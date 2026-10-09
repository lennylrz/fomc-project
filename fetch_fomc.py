#!/usr/bin/env python3
"""
fetch_fomc.py - Build the FOMC post-meeting statement corpus, 2000-present.

The Federal Reserve has used three different URL schemes over this period:
    2000-2005   /boarddocs/press/{general,monetary}/YYYY/YYYYMMDD/[default.htm]
    2006-2013   /newsevents/press/monetary/YYYYMMDDa.htm
    2014-       /newsevents/pressreleases/monetaryYYYYMMDDa.htm

Rather than hard-code these, we scrape each year's FOMC calendar page and follow
every anchor whose visible text is exactly "Statement". This is stable across
all three eras.

Output:
    statements/YYYY-MM-DD.txt   one plain-text statement per meeting
    fomc_statements.csv         date, url, n_words, n_chars, text

Usage:
    python3 fetch_fomc.py --start 2000 --end 2026 --out ./corpus
    python3 fetch_fomc.py --reclean .     # re-apply text cleaning, no fetching
"""

import argparse
import csv
import html
import os
import re
import sys
import time
import urllib.error
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (academic research; FOMC text corpus)"}
BASE = "https://www.federalreserve.gov"
CALENDAR_CURRENT = f"{BASE}/monetarypolicy/fomccalendars.htm"
CALENDAR_HISTORICAL = f"{BASE}/monetarypolicy/fomchistorical{{year}}.htm"

# Matches <a href="...">Statement</a>, allowing attributes and whitespace.
ANCHOR_RE = re.compile(r'<a[^>]*href="([^"]+)"[^>]*>\s*([^<]{0,60}?)\s*</a>', re.I)
DATE_RE = re.compile(r"(20\d{2})(\d{2})(\d{2})")
STATEMENT_URL_RE = re.compile(r"/pressreleases/monetary20\d{6}a\.htm$", re.I)
# The date is read from the URL, which is wrong for one statement: the Fed's
# page for the June 27-28, 2007 statement is .../monetary/20070618a.htm. The
# text ("growth appears to have been moderate during the first half of this
# year") and surprises.csv (MPS on 2007-06-28) both place it on 2007-06-28.
# fix_dates.py applies this mapping to every corpus and score file on disk.
DATE_FIXES = {"2007-06-18": "2007-06-28"}


def get(url, retries=3, pause=0.4):
    """Fetch a URL as text, with retries. Returns None on persistent failure."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read().decode("utf-8", "ignore")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            if attempt == retries - 1:
                print(f"    FAILED {url}: {e}", file=sys.stderr)
                return None
            time.sleep(pause * (2 ** attempt))
    return None


def statement_links(page_html):
    """Return absolute URLs of every anchor whose text is exactly 'Statement'."""
    out = []
    for href, text in ANCHOR_RE.findall(page_html):
        # Historical calendars label the link "Statement". The current calendar
        # labels it "HTML" beneath a Statement heading, so fall back to the
        # canonical statement URL pattern. The trailing "a" distinguishes the
        # statement from the implementation note ("a1") and other releases.
        is_statement = text.strip().lower() == "statement" or STATEMENT_URL_RE.search(
            href
        )
        if not is_statement:
            continue
        if href.startswith("http"):
            url = href
        elif href.startswith("/"):
            url = BASE + href
        else:
            continue
        # Directory-style links (2000-2004) need default.htm appended.
        if url.endswith("/"):
            url += "default.htm"
        out.append(url)
    return out


def extract_text(page_html):
    """
    Pull the statement body out of a Fed press-release page.

    Strategy: strip script/style, drop everything before the release date line,
    convert to plain text, then keep the block of paragraphs that constitutes
    the statement. Fed pages are simple enough that paragraph extraction on
    <p> tags is reliable across all three eras.
    """
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", page_html)
    h = re.sub(r"(?s)<!--.*?-->", " ", h)

    # Isolate the main content region where one exists (post-2011 templates).
    m = re.search(r'(?is)<div[^>]*id="article"[^>]*>(.*?)</div>\s*</div>', h)
    if m:
        h = m.group(1)

    # Pre-2006 pages are HTML 3.2 and leave <p> tags unclosed, so we cannot
    # rely on <p>...</p> pairs. Convert every paragraph or line-break boundary
    # into an explicit delimiter, then strip remaining markup.
    h = re.sub(r"(?is)</?(p|br|div|tr|li|h[1-6])[^>]*>", "\u0001", h)
    h = re.sub(r"(?is)<[^>]+>", " ", h)
    h = html.unescape(h)

    cleaned = []
    for chunk in h.split("\u0001"):
        t = re.sub(r"\s+", " ", chunk).strip()
        if t:
            cleaned.append(t)

    # Drop boilerplate paragraphs that are not part of the statement itself.
    drop = re.compile(
        r"(?i)^(last update|for (immediate )?release|release date|share$|"
        r"frb:|federal reserve (board|issues)|implementation note|"
        r"for media inquiries|home \| |return to top|"
        r"board of governors of the federal reserve system\b.*|"
        r"\d{4}? ?(federal reserve|20th street))"
    )
    cleaned = [p for p in cleaned if not drop.match(p) and len(p) > 25]
    return strip_related("\n\n".join(cleaned).strip())


# Many pages end with page furniture that is not part of the statement:
#   2000-2005   "2003 Monetary policy Home | News and events"
#   2008-2022   links to companion releases ("Statement Regarding Purchases
#               of ...", "Swiss National Bank (68 KB PDF)", "Frequently Asked
#               Questions") and, in 2011-09-21, the start of the FAQ text.
# Two rules: cut from the first companion-release heading on (never the first
# paragraph: 2019-10-11 is titled "Statement Regarding Monetary Policy
# Implementation"), then drop trailing paragraphs that read like link titles
# (under 16 words, no closing punctuation).
RELATED = re.compile(
    r"^(Statement Regarding |Frequently Asked Questions|FAQs:|"
    r"Maturity Extension Program and Reinvestment Policy$|"
    r"Information on (Related )?Actions|Statements by Other Central Banks)"
)


def strip_related(text):
    paras = text.split("\n\n")
    for i, p in enumerate(paras[1:], 1):
        if RELATED.match(p):
            paras = paras[:i]
            break
    while (len(paras) > 1 and len(paras[-1].split()) < 16
           and not paras[-1].rstrip().endswith((".", ":", '."', ".\u201d"))):
        paras.pop()
    return "\n\n".join(paras).strip()


def reclean(folder):
    """Apply strip_related to an existing corpus without refetching."""
    txt_dir = os.path.join(folder, "statements")
    changed = []
    for name in sorted(os.listdir(txt_dir)):
        if not name.endswith(".txt"):
            continue
        path = os.path.join(txt_dir, name)
        old = open(path).read()
        new = strip_related(old)
        if new != old:
            with open(path, "w") as f:
                f.write(new)
            changed.append((name[:-4], len(old.split()), len(new.split())))
    csv_path = os.path.join(folder, "fomc_statements.csv")
    if os.path.exists(csv_path):
        rows = list(csv.DictReader(open(csv_path, newline="")))
        for r in rows:
            r["text"] = strip_related(r["text"])
            r["n_words"], r["n_chars"] = len(r["text"].split()), len(r["text"])
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["date", "url", "n_words", "n_chars", "text"])
            w.writeheader()
            w.writerows(rows)
    for d, a, b in changed:
        print(f"  {d}: {a} -> {b} words")
    print(f"Cleaned {len(changed)} statements in {txt_dir}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=2000)
    ap.add_argument("--end", type=int, default=2026)
    ap.add_argument("--out", default="./corpus")
    ap.add_argument("--reclean", metavar="DIR",
                    help="strip trailing related-release links from an existing "
                         "corpus in DIR (no fetching), e.g. --reclean .")
    args = ap.parse_args()
    if args.reclean:
        reclean(args.reclean)
        return

    txt_dir = os.path.join(args.out, "statements")
    os.makedirs(txt_dir, exist_ok=True)

    # Collect candidate statement URLs from every calendar page in range.
    urls = set()
    cur = get(CALENDAR_CURRENT)
    if cur:
        urls.update(statement_links(cur))

    for year in range(args.start, args.end + 1):
        page = get(CALENDAR_HISTORICAL.format(year=year))
        if page:
            urls.update(statement_links(page))
        time.sleep(0.3)

    # Keep only URLs carrying a parseable date inside the requested window.
    dated = {}
    for u in urls:
        m = DATE_RE.search(u)
        if not m:
            continue
        y, mo, d = m.groups()
        if not (args.start <= int(y) <= args.end):
            continue
        date = f"{y}-{mo}-{d}"
        dated[DATE_FIXES.get(date, date)] = u

    print(f"Found {len(dated)} statement URLs for {args.start}-{args.end}.")

    rows = []
    for i, (date, url) in enumerate(sorted(dated.items()), 1):
        page = get(url)
        if page is None:
            continue
        text = extract_text(page)
        if len(text) < 200:
            print(f"    SHORT  {date}  ({len(text)} chars) -> flag for manual check")
        with open(os.path.join(txt_dir, f"{date}.txt"), "w") as f:
            f.write(text)
        rows.append(
            {
                "date": date,
                "url": url,
                "n_words": len(text.split()),
                "n_chars": len(text),
                "text": text,
            }
        )
        if i % 25 == 0:
            print(f"    {i}/{len(dated)} fetched")
        time.sleep(0.25)

    csv_path = os.path.join(args.out, "fomc_statements.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "url", "n_words", "n_chars", "text"])
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: r["date"]))

    print(f"\nWrote {len(rows)} statements to {csv_path}")
    if rows:
        wc = sorted(r["n_words"] for r in rows)
        print(
            f"Word count: min {wc[0]}, median {wc[len(wc)//2]}, max {wc[-1]}"
        )


if __name__ == "__main__":
    main()
