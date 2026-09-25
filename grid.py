#!/usr/bin/env python3
"""
grid.py - Score a spread of FOMC statements with all five prompts, then test
whether the prompts agree about WHICH statements are more hawkish.

The pilot showed five prompts give different numbers for one statement. This
asks the harder question: do they at least agree on the ORDERING?

If prompt A and prompt B always rank statements the same way, their
disagreement is just a difference of scale, and no regression would notice.
If they rank them differently, they genuinely disagree about the world, and
your conclusions depend on which prompt you happened to write.

--------------------------------------------------------------------------
RUN IT
--------------------------------------------------------------------------

    cd ~/Desktop/"Quant Project"/fomc-project
    export OPENROUTER_API_KEY="your-key"
    python3 grid.py --model "google/gemini-2.5-flash"

Options:
    --n 23              how many statements to score (evenly spaced in time)
    --runs 1            repeats per prompt (pilot showed 1 is enough)
    --temperature 0.0
    --out grid.csv      where the raw scores are saved

Roughly 115 calls, ~3 minutes, about a penny.
"""

import argparse
import csv
import json
import math
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.request

from pilot import PROMPTS, ask, parse_score, get_key  # reuse the pilot's code


# ---------------------------------------------------------------------------
# Two ways of comparing prompts
# ---------------------------------------------------------------------------

def pearson(xs, ys):
    """
    Ordinary correlation. Answers: do these two move up and down together?
    +1 = perfectly in step, 0 = unrelated, -1 = perfect opposites.
    """
    n = len(xs)
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den if den else float("nan")


def ranks(vals):
    """Convert values to rank positions, sharing ranks for ties."""
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    r = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(xs, ys):
    """
    Correlation of the RANKS rather than the values. This is the one that
    matters here: it ignores differences of scale and asks only whether the
    two prompts put the statements in the same order.
    """
    return pearson(ranks(xs), ranks(ys))


def pct_disagree(xs, ys):
    """
    Take every possible pair of statements. For each pair, ask each prompt
    which of the two was more hawkish. What share of the time do they give
    opposite answers?

    This is the most concrete number in the whole script. "Two reasonable
    prompts disagree about which statement was more hawkish X% of the time."
    """
    n, disc, total = len(xs), 0, 0
    for i in range(n):
        for j in range(i + 1, n):
            a, b = xs[i] - xs[j], ys[i] - ys[j]
            if a == 0 or b == 0:
                continue  # a tie is not a disagreement
            total += 1
            if (a > 0) != (b > 0):
                disc += 1
    return 100 * disc / total if total else float("nan")


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--n", type=int, default=23)
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--out", default="grid.csv")
    args = ap.parse_args()

    key = get_key()

    # Pick statements evenly spaced through time so every policy regime is
    # represented: the 2004 hiking cycle, 2008, the zero-rate years, 2022.
    all_dates = sorted(
        f[:-4] for f in os.listdir("statements") if f.endswith(".txt")
    )
    step = max(1, len(all_dates) // args.n)
    dates = all_dates[::step][: args.n]

    print(f"\nModel:       {args.model}")
    print(f"Statements:  {len(dates)}  ({dates[0]} to {dates[-1]})")
    print(f"Calls:       {len(dates) * len(PROMPTS) * args.runs}")
    print("-" * 70)

    rows = []
    scores = {p["name"]: {} for p in PROMPTS}

    for n, date in enumerate(dates, 1):
        statement = open(os.path.join("statements", f"{date}.txt")).read().strip()
        line = []
        for p in PROMPTS:
            vals = []
            for run in range(args.runs):
                reply = ask(
                    key, args.model,
                    p["text"].format(statement=statement),
                    args.temperature,
                )
                s = parse_score(reply, p["flip"])
                vals.append(s)
                rows.append({
                    "date": date, "prompt": p["name"], "run": run,
                    "score": s, "model": args.model,
                    "temperature": args.temperature,
                    "raw_reply": reply.replace("\n", " ")[:300],
                })
                time.sleep(0.2)
            good = [v for v in vals if v is not None]
            val = statistics.mean(good) if good else None
            scores[p["name"]][date] = val
            line.append(f"{val:+.2f}" if val is not None else "  ?? ")
        print(f"{n:>3}. {date}   " + "  ".join(line))

    # Save everything. This file is your actual data.
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # ---- comparisons ------------------------------------------------------
    names = [p["name"] for p in PROMPTS]
    usable = [d for d in dates if all(scores[n][d] is not None for n in names)]
    if len(usable) < 5:
        sys.exit("\nToo many failed scores to compare. Check grid.csv.")

    print("-" * 70)
    print("LEVELS  (are the prompts on the same scale?)\n")
    for n in names:
        v = [scores[n][d] for d in usable]
        print(f"  {n:<16} mean {statistics.mean(v):+.3f}   "
              f"sd {statistics.pstdev(v):.3f}   "
              f"range {min(v):+.2f} to {max(v):+.2f}")

    print("\nAGREEMENT BETWEEN PROMPTS\n")
    print(f"  {'pair':<34}{'correl':>8}{'rank':>8}{'disagree':>10}")
    worst = None
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = [scores[names[i]][d] for d in usable]
            b = [scores[names[j]][d] for d in usable]
            r, rho, dis = pearson(a, b), spearman(a, b), pct_disagree(a, b)
            label = f"{names[i]} vs {names[j]}"
            print(f"  {label:<34}{r:>8.2f}{rho:>8.2f}{dis:>9.0f}%")
            if worst is None or rho < worst[0]:
                worst = (rho, names[i], names[j])

    print("\n  'correl'   do the numbers move together")
    print("  'rank'     do the prompts put statements in the same ORDER")
    print("  'disagree' share of statement pairs where the two prompts")
    print("             disagree about which one was more hawkish")

    # Show concrete flips for the worst-agreeing pair.
    _, pa, pb = worst
    print(f"\nWHERE {pa} AND {pb} DISAGREE (worst-agreeing pair)\n")
    shown = 0
    for i in range(len(usable)):
        for j in range(i + 1, len(usable)):
            da, db = usable[i], usable[j]
            a1, a2 = scores[pa][da], scores[pa][db]
            b1, b2 = scores[pb][da], scores[pb][db]
            if a1 == a2 or b1 == b2:
                continue
            if (a1 > a2) != (b1 > b2):
                winner_a = da if a1 > a2 else db
                winner_b = da if b1 > b2 else db
                print(f"  {da} ({a1:+.2f}/{b1:+.2f})  vs  {db} ({a2:+.2f}/{b2:+.2f})")
                print(f"      {pa} says {winner_a} is more hawkish; "
                      f"{pb} says {winner_b}")
                shown += 1
            if shown >= 5:
                break
        if shown >= 5:
            break
    if shown == 0:
        print("  None. These two prompts agree on ordering everywhere.")

    print(f"\nRaw scores saved to {args.out}")


if __name__ == "__main__":
    main()
