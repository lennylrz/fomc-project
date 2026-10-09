#!/usr/bin/env python3
"""
consolidate.py - Merge the Fable score files into one: scores_fable.csv.

    python3 consolidate.py

The claude-fable-5.1 scores were produced over several runs:

    full_fable.csv        full-corpus run; 832 of 1653 rows are FAILED (empty score)
    fable_p1.csv          re-run of 2000-2003, all five prompts
    fable_fill.csv        single-prompt fill of the last gaps (finish_fable.py)
    changes_frontier.csv  the 2015-19 consecutive block from changes.py
    fable_post5.csv       all five prompts on 2025-10-29..2026-07-29 (2026-10-08,
                          score_set.py; for the post-cutoff reliability check)

Only rows with a usable numeric score are kept. Where the same statement and
prompt was scored in more than one run, every run is kept, tagged with its
source file, rather than silently picking one: the repeats are a free
test-retest check (temperature 0 is not fully deterministic), and
analysis.py averages them. Prompt 4's scale is already flipped back in the
`score` column of every source file.

Output columns: date, prompt, score, model, temperature, raw_reply, source
"""

import collections
import csv

SOURCES = ["full_fable.csv", "fable_p1.csv", "fable_fill.csv", "changes_frontier.csv",
           "fable_post5.csv"]
OUT = "scores_fable.csv"
MODEL = "anthropic/claude-fable-5.1"
FIELDS = ["date", "prompt", "score", "model", "temperature", "raw_reply", "source"]


def main():
    rows, dropped = [], collections.Counter()
    for path in SOURCES:
        with open(path) as f:
            for r in csv.DictReader(f):
                if r.get("model") != MODEL:
                    dropped[path, "other model"] += 1
                    continue
                try:
                    score = float(r["score"])
                except (ValueError, TypeError):
                    dropped[path, "no score"] += 1
                    continue
                rows.append({"date": r["date"], "prompt": r["prompt"], "score": score,
                             "model": r["model"], "temperature": r["temperature"],
                             "raw_reply": r["raw_reply"], "source": path})

    rows.sort(key=lambda r: (r["date"], r["prompt"], SOURCES.index(r["source"])))
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    cells = collections.defaultdict(list)
    for r in rows:
        cells[r["date"], r["prompt"]].append(r["score"])
    by_date = collections.defaultdict(set)
    for d, p in cells:
        by_date[d].add(p)
    repeats = [v for v in cells.values() if len(v) > 1]
    differ = sum(1 for v in repeats if len(set(v)) > 1)

    print(f"Wrote {OUT}: {len(rows)} rows")
    for (path, why), n in sorted(dropped.items()):
        print(f"  dropped {n:>4} from {path} ({why})")
    print(f"  {len(cells)} statement x prompt cells, {len(by_date)} statements "
          f"({min(by_date)} to {max(by_date)})")
    print("  prompts per statement: " + ", ".join(
        f"{k}: {v}" for k, v in sorted(collections.Counter(map(len, by_date.values())).items())))
    print(f"  {len(repeats)} cells scored in more than one run; {differ} of them differ")


if __name__ == "__main__":
    main()
