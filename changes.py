#!/usr/bin/env python3
"""
changes.py - The central test of the project.

Score a block of CONSECUTIVE FOMC meetings with all five prompts, then compare:

    reliability of LEVELS   ("how hawkish was the September statement?")
    reliability of CHANGES  ("was September more hawkish than July?")

The literature reports the first and uses the second. If the second is much
worse, published reliability figures overstate the quality of the measure as
it is actually used. That is the paper.

--------------------------------------------------------------------------
RUN IT
--------------------------------------------------------------------------

    export OPENROUTER_API_KEY="your-key"
    python3 changes.py --model "google/gemini-2.5-flash"

Options:
    --start 2015-01-01     first meeting in the block
    --end   2019-12-31     last meeting in the block
    --out   changes.csv
    --resume               reuse scores already in the output file

~200 calls, about five minutes, a couple of pennies.
Results are written as they arrive, so a crash costs you nothing.
"""

import argparse
import csv
import math
import os
import statistics
import sys
import time

from openrouter import add_api_args, key_from_args
from pilot import PROMPTS, ask, budget, parse_score


# ---------------------------------------------------------------------------
# Reliability statistics
#
# Everything below is a two-way ANOVA. Think of it as a table: one row per
# statement, one column per prompt. We split the total variation in that
# table into three parts:
#
#   between statements  - real signal, the statements genuinely differ
#   between prompts     - bias, one prompt runs hotter than another
#   residual            - noise, the part nothing explains
#
# A good instrument has almost all of its variation in the first bucket.
# ---------------------------------------------------------------------------

def anova(matrix):
    """
    matrix[i][j] = score for statement i under prompt j.
    Returns the three mean squares plus table dimensions.
    """
    n = len(matrix)          # statements
    k = len(matrix[0])       # prompts
    flat = [x for row in matrix for x in row]
    gm = statistics.mean(flat)

    row_means = [statistics.mean(r) for r in matrix]
    col_means = [statistics.mean(matrix[i][j] for i in range(n)) for j in range(k)]

    ss_total = sum((x - gm) ** 2 for x in flat)
    ss_rows = k * sum((rm - gm) ** 2 for rm in row_means)
    ss_cols = n * sum((cm - gm) ** 2 for cm in col_means)
    ss_err = ss_total - ss_rows - ss_cols

    return {
        "n": n, "k": k,
        "MSR": ss_rows / (n - 1),
        "MSC": ss_cols / (k - 1),
        "MSE": ss_err / ((n - 1) * (k - 1)),
    }


def icc(matrix):
    """
    ICC(3,1) - consistency form.

    Answers: if I pick one prompt at random, how well does its score track
    the truth? Ranges 0 to 1. Roughly:
        > 0.90  excellent
        0.75-0.90  good
        0.50-0.75  moderate
        < 0.50  poor
    """
    a = anova(matrix)
    num = a["MSR"] - a["MSE"]
    den = a["MSR"] + (a["k"] - 1) * a["MSE"]
    return num / den if den else float("nan")


def variance_share(matrix):
    """Percentage of total variance attributable to each source."""
    a = anova(matrix)
    n, k = a["n"], a["k"]
    v_stmt = max(0.0, (a["MSR"] - a["MSE"]) / k)
    v_prompt = max(0.0, (a["MSC"] - a["MSE"]) / n)
    v_err = a["MSE"]
    tot = v_stmt + v_prompt + v_err
    return {
        "statement": 100 * v_stmt / tot,
        "prompt": 100 * v_prompt / tot,
        "residual": 100 * v_err / tot,
    }


def pearson(x, y):
    mx, my = statistics.mean(x), statistics.mean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    return num / den if den else float("nan")


# ---------------------------------------------------------------------------

def load_cache(path):
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            try:
                out[(r["date"], r["prompt"])] = float(r["score"])
            except (ValueError, KeyError):
                pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--start", default="2015-01-01")
    ap.add_argument("--end", default="2019-12-31")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--out", default="changes.csv")
    ap.add_argument("--resume", action="store_true")
    add_api_args(ap)
    args = ap.parse_args()

    key = key_from_args(args)
    names = [p["name"] for p in PROMPTS]

    dates = sorted(
        f[:-4] for f in os.listdir("statements")
        if f.endswith(".txt") and args.start <= f[:-4] <= args.end
    )
    if len(dates) < 8:
        sys.exit(f"Only {len(dates)} statements in that window. Widen it.")

    cache = load_cache(args.out) if args.resume else {}
    new_file = not (args.resume and os.path.exists(args.out))

    print(f"\nModel:      {args.model}")
    print(f"Window:     {dates[0]} to {dates[-1]}  ({len(dates)} consecutive meetings)")
    print(f"Calls:      {len(dates) * len(PROMPTS) - len(cache)}")
    print("-" * 72)

    f = open(args.out, "a", newline="")
    w = csv.DictWriter(
        f, fieldnames=["date", "prompt", "score", "model", "temperature", "raw_reply"]
    )
    if new_file:
        w.writeheader()

    scores = {}
    for idx, date in enumerate(dates, 1):
        text = open(os.path.join("statements", f"{date}.txt")).read().strip()
        row = []
        for p in PROMPTS:
            if (date, p["name"]) in cache:
                s = cache[(date, p["name"])]
            else:
                reply = ask(key, args.model,
                            p["text"].format(statement=text), args.temperature,
                            budget(p, args.max_tokens))
                s = parse_score(reply, p["flip"])
                w.writerow({
                    "date": date, "prompt": p["name"], "score": s,
                    "model": args.model, "temperature": args.temperature,
                    "raw_reply": reply.replace("\n", " "),
                })
                f.flush()
                time.sleep(0.2)
            scores[(date, p["name"])] = s
            row.append(s)
        shown = "  ".join(f"{v:+.2f}" if v is not None else "  ?? " for v in row)
        print(f"{idx:>3}. {date}   {shown}")
    f.close()

    # Keep only meetings scored successfully by every prompt.
    good = [d for d in dates if all(scores[(d, n)] is not None for n in names)]
    if len(good) < 8:
        sys.exit("Too many failed scores.")

    levels = [[scores[(d, n)] for n in names] for d in good]

    # Changes: prompt-by-prompt difference from one meeting to the next.
    changes = []
    for i in range(1, len(good)):
        changes.append([
            scores[(good[i], n)] - scores[(good[i - 1], n)] for n in names
        ])

    icc_lvl, icc_chg = icc(levels), icc(changes)
    vs_lvl, vs_chg = variance_share(levels), variance_share(changes)

    print("-" * 72)
    print("RELIABILITY\n")
    print(f"  Levels   (how hawkish is this statement?)      ICC = {icc_lvl:.3f}")
    print(f"  Changes  (more hawkish than last meeting?)     ICC = {icc_chg:.3f}")
    if icc_lvl > 0:
        print(f"\n  The measure the literature actually uses retains "
              f"{100*icc_chg/icc_lvl:.0f}% of the\n  reliability that gets reported.")

    print("\nWHERE THE VARIATION COMES FROM\n")
    print(f"  {'':<14}{'levels':>10}{'changes':>10}")
    for k_ in ("statement", "prompt", "residual"):
        print(f"  {k_:<14}{vs_lvl[k_]:>9.1f}%{vs_chg[k_]:>9.1f}%")

    # ---- does the classical formula predict what we observe? --------------
    consensus = [statistics.mean(r) for r in levels]
    r_auto = pearson(consensus[:-1], consensus[1:])
    predicted = (icc_lvl - r_auto) / (1 - r_auto) if r_auto < 1 else float("nan")

    print("\nIS THIS THE KNOWN MECHANISM?\n")
    print(f"  Correlation between consecutive statements   r = {r_auto:.3f}")
    print(f"  Reliability of changes the formula predicts     {predicted:.3f}")
    print(f"  Reliability of changes actually observed        {icc_chg:.3f}")
    print("\n  Formula: (rho - r) / (1 - r). Consecutive Fed statements are")
    print("  near-identical, so r is high, so differencing throws away most")
    print("  of the signal while keeping all of the noise. If the two numbers")
    print("  above are close, that is the explanation, not a coincidence.")

    # ---- the most interpretable number in the paper -----------------------
    disagree = sum(
        1 for row in changes
        if not (all(v > 0 for v in row) or all(v < 0 for v in row))
    )
    print("\nDIRECTION DISAGREEMENT\n")
    print(f"  Meeting-to-meeting transitions:            {len(changes)}")
    print("  Where the five prompts do NOT agree on")
    print(f"  whether the Fed got more or less hawkish:  {disagree}"
          f"  ({100*disagree/len(changes):.0f}%)")

    print(f"\nRaw scores saved to {args.out}")


if __name__ == "__main__":
    main()
