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
    return "\n\n".join(cleaned).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=2000)
    ap.add_argument("--end", type=int, default=2026)
    ap.add_argument("--out", default="./corpus")
    args = ap.parse_args()

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
        dated[f"{y}-{mo}-{d}"] = u

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
