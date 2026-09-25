#!/usr/bin/env python3
"""
analysis.py - Reproduce the project's results from the score files on disk.

    python3 analysis.py                       # everything
    python3 analysis.py --score P1_minimal    # use one prompt instead of the consensus
    python3 analysis.py --csv results.csv     # also save every regression as a row

No API calls, stdlib only (the OLS, HC1 and Newey-West code is below).

PART A - RELIABILITY (report.py's logic, one table across all score files)
  ICC of raw levels, ICC after removing the rate decision, ICC on hold
  meetings, and the drop. Plus Fable test-retest from cells scored twice.

PART B - VALIDITY: do meeting-to-meeting score changes predict the market?
  y  = MPS, MPS_ORTH (Bauer-Swanson, to 2023-12), d2, d10 (bp, statement day)
  x  = dScore = consensus score at this statement minus the previous statement's
  with and without change_bp as a control; all meetings and hold meetings only.
  Fable and Gemini are run on the same statement pairs so they are comparable.
  SEs: OLS, HC1, Newey-West (Bartlett kernel, lag in meetings).

PART C - POST-CUTOFF CHECK
  Same dScore vs d2/d10 regressions on 2024+ statements, where no surprise
  series exists and training-data contamination is least likely.
"""

import argparse
import collections
import csv
import math
import statistics

from report import icc, residualise

FABLE = "scores_fable.csv"
GEMINI = "full_gemini.csv"
BLOCK_FILES = ["changes.csv", "changes_claude.csv", "changes_openai.csv",
               "changes_frontier.csv", "changes_2004.csv"]
POST_CUTOFF = "2024-01-01"


# --- data --------------------------------------------------------------------

def load_cells(path):
    """{date: {prompt: [scores...]}} - keeps repeat runs of the same cell."""
    cells = collections.defaultdict(lambda: collections.defaultdict(list))
    model = "?"
    with open(path) as f:
        for r in csv.DictReader(f):
            try:
                s = float(r["score"])
            except (ValueError, TypeError):
                continue
            cells[r["date"]][r["prompt"]].append(s)
            model = r.get("model", model)
    return cells, model


def collapse(cells):
    """Average repeat runs: {date: {prompt: score}}."""
    return {d: {p: statistics.mean(v) for p, v in ps.items()} for d, ps in cells.items()}


def series(scores, how):
    """One number per statement: mean over available prompts, or one prompt."""
    if how == "consensus":
        return {d: statistics.mean(ps.values()) for d, ps in scores.items()}
    return {d: ps[how] for d, ps in scores.items() if how in ps}


def load_market():
    statements = [r["date"] for r in csv.DictReader(open("fomc_statements.csv"))]
    policy = {r["date"]: int(r["change_bp"]) for r in csv.DictReader(open("policy_by_statement.csv"))}
    market = collections.defaultdict(dict)
    for r in csv.DictReader(open("surprises.csv")):
        for k in ("MPS", "MPS_ORTH"):
            if r[k]:
                market[r["date"]][k] = float(r[k])
    for r in csv.DictReader(open("yields.csv")):
        for k in ("d2", "d10"):
            if r[k]:
                market[r["date"]][k] = float(r[k])
    return statements, policy, market


def changes(score, statements):
    """dScore between consecutive corpus statements; a pair is dropped if either side is unscored."""
    out = {}
    for prev, cur in zip(statements, statements[1:]):
        if prev in score and cur in score:
            out[cur] = score[cur] - score[prev]
    return out


# --- regression ----------------------------------------------------------------

def _inv(A):
    n = len(A)
    M = [row[:] + [float(i == j) for j in range(n)] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-14:
            raise ValueError("singular design matrix")
        M[c], M[p] = M[p], M[c]
        piv = M[c][c]
        M[c] = [v / piv for v in M[c]]
        for r in range(n):
            if r != c and M[r][c]:
                f = M[r][c]
                M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    return [row[n:] for row in M]


def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > 1e-30 else 1e-30)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        for aa in (m * (b - m) * x / ((qam + m2) * (a + m2)),
                   -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))):
            d = 1 + aa * d
            d = 1 / (d if abs(d) > 1e-30 else 1e-30)
            c = 1 + aa / c
            c = c if abs(c) > 1e-30 else 1e-30
            h *= d * c
        if abs(d * c - 1) < 1e-12:
            break
    return h


def t_pvalue(t, df):
    """Two-sided p-value from Student's t (regularised incomplete beta)."""
    x = df / (df + t * t)
    a, b = df / 2, 0.5
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(a * math.log(x) + b * math.log(1 - x) - lbeta)
    if x < (a + 1) / (a + b + 2):
        return front * _betacf(a, b, x) / a
    return 1 - front * _betacf(b, a, 1 - x) / b


def nw_lag(n):
    return int(4 * (n / 100) ** (2 / 9))


def ols(y, X, lag):
    """OLS with classical, HC1 and Newey-West SEs. X rows include the constant.
    Rows must be in time order for Newey-West."""
    n, k = len(y), len(X[0])
    XtX_inv = _inv([[sum(r[i] * r[j] for r in X) for j in range(k)] for i in range(k)])
    Xty = [sum(r[i] * v for r, v in zip(X, y)) for i in range(k)]
    b = [sum(XtX_inv[i][j] * Xty[j] for j in range(k)) for i in range(k)]
    e = [v - sum(bi * xi for bi, xi in zip(b, r)) for r, v in zip(X, y)]
    my = statistics.mean(y)
    sst = sum((v - my) ** 2 for v in y)
    r2 = 1 - sum(u * u for u in e) / sst if sst else float("nan")

    def sandwich(meat):
        A = [[sum(XtX_inv[i][a] * meat[a][c] for a in range(k)) for c in range(k)] for i in range(k)]
        return [[sum(A[i][c] * XtX_inv[c][j] for c in range(k)) for j in range(k)] for i in range(k)]

    s2 = sum(u * u for u in e) / (n - k)
    V_ols = [[s2 * v for v in row] for row in XtX_inv]
    g = [[r[i] * u for i in range(k)] for r, u in zip(X, e)]    # score contributions
    S0 = [[sum(gt[i] * gt[j] for gt in g) for j in range(k)] for i in range(k)]
    V_hc1 = [[v * n / (n - k) for v in row] for row in sandwich(S0)]
    S = [row[:] for row in S0]
    for L in range(1, lag + 1):
        w = 1 - L / (lag + 1)
        for t in range(L, n):
            for i in range(k):
                for j in range(k):
                    S[i][j] += w * (g[t][i] * g[t - L][j] + g[t - L][i] * g[t][j])
    V_nw = [[v * n / (n - k) for v in row] for row in sandwich(S)]
    return {"b": b, "r2": r2, "n": n, "df": n - k, "lag": lag,
            "se": {name: [math.sqrt(max(V[i][i], 0)) for i in range(k)]
                   for name, V in (("ols", V_ols), ("hc1", V_hc1), ("nw", V_nw))}}


# --- part A ----------------------------------------------------------------------

def reliability_row(label, scores, actions):
    prompts = sorted({p for v in scores.values() for p in v})
    dates = sorted(d for d in scores if len(scores[d]) == len(prompts) and d in actions)
    if len(dates) < 10 or len(prompts) < 2:
        return None
    act = [actions[d] for d in dates]
    levels = [[scores[d][p] for p in prompts] for d in dates]
    cols = [residualise([scores[d][p] for d in dates], act)[0] for p in prompts]
    resid = [[c[i] for c in cols] for i in range(len(dates))]
    holds = [levels[i] for i, a in enumerate(act) if a == 0]
    ch = [[levels[i][j] - levels[i - 1][j] for j in range(len(prompts))]
          for i in range(1, len(dates))]
    raw, res = icc(levels), icc(resid)
    return {"label": label, "n": len(dates), "k": len(prompts),
            "window": f"{dates[0][:7]}..{dates[-1][:7]}", "raw": raw, "resid": res,
            "hold": icc(holds) if len(holds) >= 10 else float("nan"),
            "chg": icc(ch), "drop": 100 * (1 - res / raw) if raw else float("nan")}


def part_a(policy):
    print("=" * 78)
    print("A. RELIABILITY  (ICC(3,1) across prompts; statements with all prompts only)")
    print("=" * 78)
    actions = {d: (v > 0) - (v < 0) for d, v in policy.items()}
    rows = []
    for path in BLOCK_FILES + [GEMINI, FABLE]:
        cells, model = load_cells(path)
        r = reliability_row(f"{model.split('/')[-1]} [{path}]", collapse(cells), actions)
        if r:
            rows.append(r)
    print(f"\n  {'model [file]':<44}{'n':>4}  {'window':<16}{'raw':>6}{'resid':>7}"
          f"{'hold':>7}{'chg':>7}{'drop':>7}")
    for r in rows:
        print(f"  {r['label'][:43]:<44}{r['n']:>4}  {r['window']:<16}{r['raw']:>6.3f}"
              f"{r['resid']:>7.3f}{r['hold']:>7.3f}{r['chg']:>7.3f}{r['drop']:>6.0f}%")
    print("\n  raw = levels; resid = after regressing out hike/hold/cut; hold = no-change")
    print("  meetings only; chg = meeting-to-meeting changes; drop = 1 - resid/raw.")

    cells, _ = load_cells(FABLE)
    pairs = [v[:2] for ps in cells.values() for v in ps.values() if len(v) > 1]
    if len(pairs) > 2:
        a, b = zip(*pairs)
        mad = statistics.mean(abs(x - y) for x, y in pairs)
        print(f"\n  Fable test-retest: {len(pairs)} cells scored in two runs, r = "
              f"{statistics.correlation(a, b):.3f}, mean |diff| = {mad:.3f}, "
              f"{sum(x != y for x, y in pairs)} differ")


# --- parts B and C -----------------------------------------------------------------

def run_specs(label, dsc, policy, market, dates, targets, samples, out, lag=None):
    for tgt in targets:
        for sample in samples:
            for ctrl in (False, True):
                use = [d for d in dates if d in dsc and tgt in market[d]
                       and (sample == "all" or policy[d] == 0)]
                if len(use) < 8 or (ctrl and sample == "hold"):
                    continue
                y = [market[d][tgt] for d in use]
                X = [[1.0, dsc[d]] + ([float(policy[d])] if ctrl else []) for d in use]
                try:
                    r = ols(y, X, nw_lag(len(use)) if lag is None else lag)
                except ValueError:
                    continue
                row = {"model": label, "y": tgt, "sample": sample,
                       "control": "change_bp" if ctrl else "-", "n": r["n"],
                       "beta": r["b"][1], "r2": r["r2"], "nw_lag": r["lag"],
                       "first": use[0], "last": use[-1]}
                for se in ("ols", "hc1", "nw"):
                    row["t_" + se] = r["b"][1] / r["se"][se][1] if r["se"][se][1] else float("nan")
                row["p_nw"] = t_pvalue(row["t_nw"], r["df"])
                out.append(row)


def print_rows(rows):
    print(f"\n  {'y':<9}{'sample':<7}{'control':<11}{'model':<8}{'n':>4}{'beta':>9}"
          f"{'t_ols':>7}{'t_hc1':>7}{'t_nw':>7}{'p_nw':>7}{'R2':>7}")
    last = None
    for r in rows:
        key = (r["y"], r["sample"], r["control"])
        if last and key[:2] != last[:2]:
            print()
        last = key
        print(f"  {r['y']:<9}{r['sample']:<7}{r['control']:<11}{r['model']:<8}{r['n']:>4}"
              f"{r['beta']:>9.3f}{r['t_ols']:>7.2f}{r['t_hc1']:>7.2f}{r['t_nw']:>7.2f}"
              f"{r['p_nw']:>7.3f}{r['r2']:>7.3f}")


def part_bc(statements, policy, market, how, out):
    models = {}
    for label, path in (("fable", FABLE), ("gemini", GEMINI)):
        cells, _ = load_cells(path)
        models[label] = changes(series(collapse(cells), how), statements)
    common = sorted(set(models["fable"]) & set(models["gemini"]))

    print("\n" + "=" * 78)
    print(f"B. VALIDITY: market move on dScore ({how}), statements to 2023-12")
    print("=" * 78)
    pre = [d for d in common if d < POST_CUTOFF]
    for label in models:
        both = [d for d in pre if d in models[label]]
        print(f"  {label}: {len(both)} dScore pairs before {POST_CUTOFF}; "
              f"sd(dScore) = {statistics.pstdev(models[label][d] for d in both):.3f}")
    fs, gs = [models["fable"][d] for d in pre], [models["gemini"][d] for d in pre]
    print(f"  corr(fable dScore, gemini dScore) = {statistics.correlation(fs, gs):.3f}")
    rows = []
    for label in models:
        run_specs(label, models[label], policy, market, pre,
                  ("MPS", "MPS_ORTH", "d2", "d10"), ("all", "hold"), rows)
    rows.sort(key=lambda r: (["MPS", "MPS_ORTH", "d2", "d10"].index(r["y"]),
                             r["sample"], r["control"], r["model"]))
    print_rows(rows)
    print("\n  beta: market units (MPS in pct pts, d2/d10 in bp) per 1.0 of dScore.")
    print("  NW lag = floor(4 (n/100)^(2/9)) meetings; p_nw two-sided, Student t.")
    for r in rows:
        r["part"] = "B"
    out.extend(rows)

    print("\n" + "=" * 78)
    print(f"C. POST-CUTOFF: statements from {POST_CUTOFF} (no MPS available)")
    print("=" * 78)
    post = [d for d in common if d >= POST_CUTOFF]
    print(f"  {len(post)} dScore pairs, {post[0] if post else '-'} to {post[-1] if post else '-'}")
    rows = []
    for label in models:
        run_specs(label, models[label], policy, market, post, ("d2", "d10"),
                  ("all", "hold"), rows, lag=0)
    rows.sort(key=lambda r: (r["y"], r["sample"], r["control"], r["model"]))
    print_rows(rows)
    print("\n  Too few points for Newey-West here; lag set to 0 (t_nw = t_hc1).")
    for r in rows:
        r["part"] = "C"
    out.extend(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--score", default="consensus",
                    help="'consensus' (mean of available prompts) or one prompt name, e.g. P1_minimal")
    ap.add_argument("--csv", help="write every regression to this CSV")
    a = ap.parse_args()

    statements, policy, market = load_market()
    part_a(policy)
    rows = []
    part_bc(statements, policy, market, a.score, rows)
    if a.csv:
        fields = ["part", "model", "y", "sample", "control", "n", "beta", "t_ols",
                  "t_hc1", "t_nw", "p_nw", "nw_lag", "r2", "first", "last"]
        with open(a.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        print(f"\nWrote {len(rows)} regressions to {a.csv}")
    print()


if __name__ == "__main__":
    main()
