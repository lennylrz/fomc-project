#!/usr/bin/env python3
"""
report.py - Read one or more score files and produce the project's results.

    python3 report.py changes.csv
    python3 report.py changes.csv changes_model2.csv     (compare models)

Needs policy_by_statement.csv in the same folder: the Fed's own record of
which meetings raised, held, or cut rates, matched to statement dates.

WHAT IT REPORTS

  1. Reliability of the raw scores.
     "If I pick one prompt at random, how well does it track the truth?"

  2. How much of the score is just the rate decision.
     The rate decision is public the instant it's announced. Any part of the
     score explained by it carries no new information.

  3. Reliability of what's left after the rate decision is removed.
     This is the number that matters. It describes the only part of the
     score that could tell you something markets didn't already know.

  4. The same thing computed only on meetings where rates did not change,
     where the words are the sole news. A second route to the same answer.

  5. How often prompts disagree on direction between meetings.
"""

import collections
import csv
import statistics
import sys


# --- reliability -----------------------------------------------------------
# Everything below is a two-way ANOVA on a table with one row per statement
# and one column per prompt. It splits the variation three ways: real
# differences between statements (signal), consistent bias of one prompt
# versus another, and unexplained residual (noise).

def _anova(M):
    n, k = len(M), len(M[0])
    flat = [x for r in M for x in r]
    gm = statistics.mean(flat)
    rm = [statistics.mean(r) for r in M]
    cm = [statistics.mean(M[i][j] for i in range(n)) for j in range(k)]
    sst = sum((x - gm) ** 2 for x in flat)
    ssr = k * sum((a - gm) ** 2 for a in rm)
    ssc = n * sum((a - gm) ** 2 for a in cm)
    return n, k, ssr / (n - 1), ssc / (k - 1), (sst - ssr - ssc) / ((n - 1) * (k - 1))


def icc(M):
    """ICC(3,1). 0 = useless, 1 = perfect. Above 0.75 is usually called good."""
    n, k, msr, msc, mse = _anova(M)
    den = msr + (k - 1) * mse
    return (msr - mse) / den if den else float("nan")


def variance_share(M):
    n, k, msr, msc, mse = _anova(M)
    vs, vp, ve = max(0, (msr - mse) / k), max(0, (msc - mse) / n), mse
    t = vs + vp + ve
    return {"statement": 100 * vs / t, "prompt": 100 * vp / t, "residual": 100 * ve / t}


def residualise(y, x):
    """Strip out the part of y that a simple regression on x explains."""
    mx, my = statistics.mean(x), statistics.mean(y)
    denom = sum((a - mx) ** 2 for a in x)
    b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / denom if denom else 0.0
    return [c - (my + b * (a - mx)) for a, c in zip(x, y)], b


def r_squared(y, x):
    res, _ = residualise(y, x)
    my = statistics.mean(y)
    sst = sum((c - my) ** 2 for c in y)
    return 1 - sum(r * r for r in res) / sst if sst else float("nan")


# --- report ----------------------------------------------------------------

def analyse(path, actions):
    sc = collections.defaultdict(dict)
    model = "?"
    for r in csv.DictReader(open(path)):
        try:
            sc[r["date"]][r["prompt"]] = float(r["score"])
        except (ValueError, TypeError):
            continue
        model = r.get("model", model)

    prompts = sorted({p for v in sc.values() for p in v})
    dates = sorted(d for d in sc if len(sc[d]) == len(prompts) and d in actions)
    if len(dates) < 10:
        print(f"  {path}: only {len(dates)} usable statements, skipping")
        return None

    act = [actions[d] for d in dates]
    levels = [[sc[d][p] for p in prompts] for d in dates]

    icc_raw = icc(levels)
    vshare = variance_share(levels)

    consensus = [statistics.mean(r) for r in levels]
    r2_action = r_squared(consensus, act)

    resid = [[residualise([sc[d][p] for d in dates], act)[0][i]
              for p in prompts] for i in range(len(dates))]
    icc_resid = icc(resid)

    holds = [i for i, a in enumerate(act) if a == 0]
    icc_hold = icc([levels[i] for i in holds]) if len(holds) >= 10 else float("nan")

    changes = [[levels[i][j] - levels[i - 1][j] for j in range(len(prompts))]
               for i in range(1, len(dates))]
    opposite = sum(1 for r in changes if any(v > 0 for v in r) and any(v < 0 for v in r))

    return {
        "path": path, "model": model, "n": len(dates), "k": len(prompts),
        "window": f"{dates[0]} to {dates[-1]}",
        "icc_raw": icc_raw, "icc_resid": icc_resid, "icc_hold": icc_hold,
        "r2_action": r2_action, "vshare": vshare,
        "opposite": opposite, "transitions": len(changes),
        "n_hold": len(holds),
    }


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python3 report.py changes.csv [more.csv ...]")

    actions = {}
    try:
        for r in csv.DictReader(open("policy_by_statement.csv")):
            actions[r["date"]] = int(r["change_bp"])
    except FileNotFoundError:
        sys.exit("Missing policy_by_statement.csv - it must sit in this folder.")
    # Code as -1 / 0 / +1 rather than basis points, so one large move does not
    # dominate. We are asking "which direction", not "by how much".
    actions = {d: (1 if v > 0 else (-1 if v < 0 else 0)) for d, v in actions.items()}

    results = [x for x in (analyse(p, actions) for p in sys.argv[1:]) if x]
    if not results:
        sys.exit("Nothing to report.")

    for r in results:
        print(f"\n{'='*66}")
        print(f"{r['model']}")
        print(f"{r['n']} statements x {r['k']} prompts   {r['window']}")
        print("=" * 66)

        print("\n1. RELIABILITY OF THE RAW SCORES")
        print(f"     ICC = {r['icc_raw']:.3f}")
        print("     This is the figure papers in this area report.")

        print("\n2. HOW MUCH IS JUST THE RATE DECISION?")
        print(f"     R-squared on hike / hold / cut = {r['r2_action']:.3f}")
        print(f"     {100*r['r2_action']:.0f}% of the score is explained by an announcement")
        print("     the market receives instantly and for free.")

        print("\n3. RELIABILITY OF WHAT REMAINS")
        print(f"     ICC after removing the rate decision = {r['icc_resid']:.3f}")
        print(f"     ICC on the {r['n_hold']} no-change meetings   = {r['icc_hold']:.3f}")
        print("     These describe the only informative part of the measure.")
        if r["icc_raw"] > 0:
            drop = 100 * (1 - r["icc_resid"] / r["icc_raw"])
            print(f"     Reliability falls {drop:.0f}% once the free information is removed.")

        print("\n4. WHERE THE VARIATION COMES FROM")
        for k in ("statement", "prompt", "residual"):
            print(f"     {k:<12}{r['vshare'][k]:>7.1f}%")

        print("\n5. DIRECTION DISAGREEMENT")
        print(f"     {r['opposite']} of {r['transitions']} meeting-to-meeting moves "
              f"({100*r['opposite']/r['transitions']:.0f}%) get")
        print("     strictly opposite calls from different prompts.")

    if len(results) > 1:
        print(f"\n{'='*66}")
        print("ACROSS MODELS")
        print("=" * 66)
        print(f"\n  {'model':<34}{'raw':>8}{'resid':>8}{'drop':>8}")
        for r in results:
            drop = 100 * (1 - r["icc_resid"] / r["icc_raw"])
            print(f"  {r['model'][:33]:<34}{r['icc_raw']:>8.3f}"
                  f"{r['icc_resid']:>8.3f}{drop:>7.0f}%")
        print("\n  If the drop is similar across models, this is a property of")
        print("  LLM stance scoring rather than a quirk of one model.")
    print()


if __name__ == "__main__":
    main()
