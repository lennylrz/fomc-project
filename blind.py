#!/usr/bin/env python3
"""
blind.py - Make a copy of every statement with the identifying details removed,
for the contamination test. No API calls, stdlib only.

    python3 blind.py                 # writes statements_blind/ and blind_log.csv
    python3 blind.py --show 2013-12-18

The question the blinded text answers: does Fable score a statement well
because it reads it, or because it recognises it and remembers what followed?
If the dScore -> yield relationship survives blinding, it is reading.

What is changed (everything else is left word for word):
  votes     "Voting for ..." sentences are dropped (the roster dates the
            statement to within a year or two), as is the 2025+ "approved the
            following statement for release by a 9 - 3 vote" line. "Voting
            against ..." sentences are kept, with names removed, because a
            dissent is stance information.
  names     every FOMC member named in any vote sentence, anywhere in the
            corpus, becomes "[member]".
  dates     month names become "[month]"; years become relative to the
            statement's own year, so date-based guidance keeps its meaning:
            "at least through mid-2015" in 2012 -> "through mid-[year+3]".
  events    named one-off events become "[event]" / "[country]" / "[region]"
            (the coronavirus, the invasion of Ukraine by Russia, hurricanes,
            the Middle East conflict, ...).

What is NOT removed, and still identifies a statement to a model that has read
it: rate levels ("5-3/4 percent"), distinctive phrasing, the era's standard
paragraph layout. The date-stripped test therefore removes the easy cues, not
all of them; a paraphrased version is the stronger test.

blind_log.csv has one row per statement with the counts of each replacement.
The script also prints capitalised words that remain, for a manual check.
"""

import argparse
import collections
import csv
import os
import re

SRC, OUT, LOG = "statements", "statements_blind", "blind_log.csv"

MONTHS = ("January February March April May June July August September "
          "October November December").split()
MONTH_RE = re.compile(r"\b(" + "|".join(MONTHS) + r")\b")
YEAR_RE = re.compile(r"\b(19[89]\d|20[0-4]\d)\b")

# Named one-off events. Order matters: longer phrases first.
EVENTS = [
    (r"the invasion of Ukraine by Russia", "the invasion of [country] by [country]"),
    (r"Russia's (war against|invasion of) Ukraine", r"[country]'s \1 [country]"),
    (r"\b(Ukraine|Russia|Iraq|Japan)\b", "[country]"),
    (r"\bthe Middle East\b", "[region]"),
    (r"\b(COVID-19|COVID|coronavirus)\b", "[event]"),
    (r"\bHurricanes? (Katrina|Rita|Wilma|Harvey|Irma|Maria|Ian)"
     r"(,? (and|or) (Katrina|Rita|Wilma|Harvey|Irma|Maria|Ian))?", "[event]"),
    (r"\b(Katrina|Rita|Wilma|Harvey|Irma|Maria)\b", "[event]"),
]
EVENTS = [(re.compile(p), r) for p, r in EVENTS]

VOTE_FOR = re.compile(r"^Voting for\b")
VOTE_COUNT = re.compile(r"^The Federal Open Market Committee approved the "
                        r"following statement for release by")
TITLES = re.compile(r",? (Chairman|Chair|Vice Chairman|Vice Chair|Jr\.?)$")


def sentences(par):
    """Split a paragraph into sentences without breaking on initials
    ("Ben S. Bernanke") or "Jr."."""
    return re.split(r"(?<=[a-z0-9%)][.!?])\s+(?=[A-Z\"“])", par)


def collect_names(texts):
    """Every person named in a vote sentence: full names and surnames."""
    full = set()
    for text in texts:
        for par in text.split("\n\n"):
            if not par.startswith("Voting"):
                continue
            for s in sentences(par):
                if not s.startswith("Voting"):
                    continue
                m = re.search(r"\bw(?:ere|as)\b:?|:", s)
                if not m:
                    continue
                body = s[m.end():].split(", who ")[0]
                for part in re.split(r";|\band\b|, (?=[A-Z][a-z]+ [A-Z])", body):
                    name = TITLES.sub("", part.strip(" .,:"))
                    name = TITLES.sub("", name)
                    if re.fullmatch(r"[A-Z][a-zA-Z.'\- ]+ [A-Z][a-zA-Z'\-]+", name):
                        full.add(name)
    surnames = {n.split()[-1] for n in full}
    return full, surnames


def year_word(y, base):
    d = y - base
    return "[this year]" if d == 0 else f"[year{d:+d}]"


def blind(date, text, name_re):
    base = int(date[:4])
    n = collections.Counter()
    kept = []
    for par in text.split("\n\n"):
        out = []
        for s in sentences(par):
            if VOTE_FOR.match(s) or VOTE_COUNT.match(s):
                n["vote_sentences"] += 1
                continue
            out.append(s)
        if out:
            kept.append(" ".join(out))
    t = "\n\n".join(kept)

    def sub(regex, repl, text, key):
        text, k = regex.subn(repl, text)
        n[key] += k
        return text

    t = sub(name_re, "[member]", t, "names")
    for rx, repl in EVENTS:
        t = sub(rx, repl, t, "events")
    t = sub(MONTH_RE, "[month]", t, "months")
    t, k = YEAR_RE.subn(lambda m: year_word(int(m.group()), base), t)
    n["years"] += k
    return t, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", metavar="DATE", help="print one statement, original and blinded")
    args = ap.parse_args()

    dates = sorted(f[:-4] for f in os.listdir(SRC) if f.endswith(".txt"))
    texts = {d: open(os.path.join(SRC, f"{d}.txt")).read().strip() for d in dates}
    full, surnames = collect_names(texts.values())
    # Titles plus surname ("Chair Powell", "Mr. Hoenig") and full names first,
    # then bare surnames.
    alts = sorted(full, key=len, reverse=True) + sorted(surnames)
    name_re = re.compile(
        r"(?:\b(?:Chairman|Chair|Governor|President|Mr\.|Ms\.|Mrs\.) )?\b(?:"
        + "|".join(re.escape(a) for a in alts) + r")\b(?:,? Jr\.)?")

    if args.show:
        t, n = blind(args.show, texts[args.show], name_re)
        print(texts[args.show], "\n\n" + "-" * 70 + "\n")
        print(t, "\n\n", dict(n))
        return

    os.makedirs(OUT, exist_ok=True)
    keys = ["vote_sentences", "names", "months", "years", "events"]
    rows, left = [], collections.Counter()
    for d in dates:
        t, n = blind(d, texts[d], name_re)
        with open(os.path.join(OUT, f"{d}.txt"), "w") as f:
            f.write(t)
        rows.append({"date": d, "words_before": len(texts[d].split()),
                     "words_after": len(t.split()), **{k: n[k] for k in keys}})
        # Capitalised words that are not at the start of a sentence.
        for w in re.findall(r"(?<=[a-z,;] )[A-Z][a-z]+(?:'s)?", t):
            left[w] += 1

    with open(LOG, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "words_before", "words_after"] + keys)
        w.writeheader()
        w.writerows(rows)

    tot = {k: sum(r[k] for r in rows) for k in keys}
    print(f"Blinded {len(rows)} statements -> {OUT}/  (log: {LOG})")
    print(f"  {len(full)} member names found; replacements: "
          + ", ".join(f"{k} {v}" for k, v in tot.items()))
    print("\nCapitalised words left mid-sentence (check none identify a date):")
    print("  " + ", ".join(f"{w} {c}" for w, c in left.most_common(60)))


if __name__ == "__main__":
    main()
