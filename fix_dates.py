#!/usr/bin/env python3
"""
fix_dates.py - Apply fetch_fomc.DATE_FIXES to the files already on disk.

    python3 fix_dates.py            # rewrite in place (idempotent)
    python3 fix_dates.py --dry-run  # only report what would change

Renames statements*/<old>.txt to <new>.txt and rewrites the "date" column of
every corpus-keyed CSV (corpus, policy, score, probe and log files). Market
files (yields.csv, surprises.csv, policy_actions.csv) are keyed by calendar
day, not by statement, and are left alone. No API calls.
"""

import argparse
import csv
import glob
import os

from fetch_fomc import DATE_FIXES

MARKET = {"yields.csv", "surprises.csv", "policy_actions.csv"}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    for folder in sorted(glob.glob("statements*")):
        for old, new in DATE_FIXES.items():
            src, dst = os.path.join(folder, old + ".txt"), os.path.join(folder, new + ".txt")
            if os.path.exists(src):
                if os.path.exists(dst):
                    raise SystemExit(f"{dst} exists already; not overwriting")
                print(f"  rename {src} -> {dst}")
                if not a.dry_run:
                    os.rename(src, dst)
    for path in sorted(glob.glob("*.csv")):
        if path in MARKET:
            continue
        with open(path, newline="") as f:
            rd = csv.DictReader(f)
            fields, rows = rd.fieldnames, list(rd)
        if not fields or "date" not in fields:
            continue
        n = 0
        for r in rows:
            if r["date"] in DATE_FIXES:
                r["date"] = DATE_FIXES[r["date"]]
                n += 1
        if n:
            print(f"  {path}: {n} rows")
            if not a.dry_run:
                rows.sort(key=lambda r: r["date"]) if path == "fomc_statements.csv" else None
                with open(path, "w", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=fields)
                    w.writeheader()
                    w.writerows(rows)


if __name__ == "__main__":
    main()
