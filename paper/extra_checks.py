#!/usr/bin/env python3
"""
paper/extra_checks.py - Exploratory checks the 2026-10-03 review asked for
that analysis.py does not print, plus the data behind the paper's figures.
No API calls, stdlib only; reuses analysis.py's loaders and OLS.

    python3 paper/extra_checks.py            # from the repo root or paper/

All checks: Fable consensus dScore (prompt fixed effects), --corpus policy,
hold meetings, statements to 2023-12, Newey-West SE with analysis.py's lag
rule. They are secondary and exploratory and count towards the regression
total the paper reports.

  (1) subperiods   primary spec on 2000-07, 2008-15, 2016-23 (review 4.4)
  (2) levels       MPS on the score LEVEL instead of its change (review 4.6)
  (3) lags         primary + previous policy statement's MPS; primary +
                   lagged dScore (review 4.6)
  (4) decomposition  MPS on the paraphrase (or blinded) dScore and on the
                   part paraphrasing (blinding) removed, clean - para, in one
                   regression (review section 5)
  (5) LSAP days    Fable dScore and yield moves on 2009-03-18 and 2013-09-18
                   (review 4.4), descriptive
Writes paper/runs/extra.csv (regressions), paper/runs/extra.txt (log) and
paper/runs/scatter.csv (hold-meeting MPS and Fable dScore, for figure 3).
"""

import csv
import math
import os
import random
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

import analysis as A  # noqa: E402

OUT = os.path.join("paper", "runs")


def reg(y, X):
    r = A.ols(y, X, A.nw_lag(len(y)))
    return r


def row(label, y_name, use, r, i=1):
    t = r["b"][i] / r["se"]["nw"][i]
    return {"check": label, "y": y_name, "n": r["n"], "beta": r["b"][i], "t_nw": t,
            "p_nw": A.t_pvalue(t, r["df"]), "r2": r["r2"], "first": use[0], "last": use[-1]}


def main():
    statements, policy, market = A.load_market()
    statements, _ = A.corpus_filter(statements, "policy")
    pre = [d for d in statements if d < A.POST_CUTOFF]
    cells, _ = A.load_cells(A.FABLE)
    scores = A.collapse(cells)
    F = A.dscores(scores, statements, "consensus")
    hold = [d for d in pre if d in F and policy[d] == 0 and "MPS" in market[d]]
    rows, log = [], []

    # (1) subperiods
    for lo, hi in (("2000", "2007"), ("2008", "2015"), ("2016", "2023")):
        use = [d for d in hold if lo <= d[:4] <= hi]
        r = reg([market[d]["MPS"] for d in use], [[1.0, F[d]] for d in use])
        rows.append(row(f"subperiod {lo}-{hi}", "MPS", use, r))

    # (2) score level (prompt-demeaned consensus, as dScore is built from)
    prompts = sorted({p for v in scores.values() for p in v})
    full = [v for v in scores.values() if len(v) == len(prompts)]
    off = {p: statistics.mean(v[p] - statistics.mean(v.values()) for v in full) for p in prompts}
    level = {d: statistics.mean(x - off[p] for p, x in v.items()) for d, v in scores.items()}
    use = [d for d in hold if d in level]
    r = reg([market[d]["MPS"] for d in use], [[1.0, level[d]] for d in use])
    rows.append(row("score level instead of dScore", "MPS", use, r))

    # (3) lagged controls: previous POLICY statement (corpus order)
    prev = dict(zip(statements[1:], statements[:-1]))
    use = [d for d in hold if "MPS" in market.get(prev[d], {})]
    r = reg([market[d]["MPS"] for d in use],
            [[1.0, F[d], market[prev[d]]["MPS"]] for d in use])
    rows.append(row("primary + previous statement's MPS", "MPS", use, r))
    use = [d for d in hold if prev[d] in F]
    r = reg([market[d]["MPS"] for d in use], [[1.0, F[d], F[prev[d]]] for d in use])
    rows.append(row("primary + lagged dScore", "MPS", use, r))

    # (4) decomposition of the clean single-prompt dScore
    ex = {}
    for lab, path in (("clean", "clean_fable.csv"), ("blind", "blind_fable.csv"),
                      ("para", "para_fable.csv")):
        c, _ = A.load_cells(path)
        ex[lab] = A.dscores(A.collapse(c), statements, "consensus")
    for other in ("para", "blind"):
        use = [d for d in hold if d in ex["clean"] and d in ex[other]]
        y = [market[d]["MPS"] for d in use]
        X = [[1.0, ex[other][d], ex["clean"][d] - ex[other][d]] for d in use]
        r = reg(y, X)
        rows.append(row(f"decomposition: {other} dScore", "MPS", use, r, 1))
        rows.append(row(f"decomposition: clean - {other}", "MPS", use, r, 2))
        sd_o = statistics.pstdev(ex[other][d] for d in use)
        sd_r = statistics.pstdev(ex["clean"][d] - ex[other][d] for d in use)
        log.append(f"  sd({other} dScore) {sd_o:.3f}, sd(clean - {other}) {sd_r:.3f}, n {len(use)}")

    # (5) the two largest LSAP hold days
    for d in ("2009-03-18", "2013-09-18"):
        m = market[d]
        log.append(f"  {d}: Fable dScore {F.get(d, float('nan')):+.3f}, d10 {m.get('d10', float('nan')):+.0f} bp,"
                   f" d2 {m.get('d2', float('nan')):+.0f} bp, MPS {m.get('MPS', float('nan')):+.3f}")

    # (6) reliability "resid" with separate hike and cut dummies instead of
    # the linear -1/0/+1 code (review m7), crossed 2015-19 block
    from report import icc
    keep = set(statements)
    order = sorted(keep)
    log.append("")
    log.append("  ICC resid, 2015-19 block: linear code vs hike/cut dummies")
    for path in A.CROSSED:
        sc = A.collapse(A.load_cells(path)[0])
        prompts = sorted({p for v in sc.values() for p in v})
        dates = [d for d in order if d in sc and len(sc[d]) == len(prompts)]
        act = [(policy[d] > 0) - (policy[d] < 0) for d in dates]
        cols = []
        for p in prompts:
            y = [sc[d][p] for d in dates]
            X = [[1.0, float(a == 1), float(a == -1)] for a in act]
            k = 3
            XtX = A._inv([[sum(r[i] * r[j] for r in X) for j in range(k)] for i in range(k)])
            Xty = [sum(r[i] * v for r, v in zip(X, y)) for i in range(k)]
            b = [sum(XtX[i][j] * Xty[j] for j in range(k)) for i in range(k)]
            cols.append([v - sum(bi * xi for bi, xi in zip(b, r)) for r, v in zip(X, y)])
        resid_d = icc([[c[i] for c in cols] for i in range(len(dates))])
        lin = [A.residualise([sc[d][p] for d in dates], act)[0] for p in prompts]
        resid_l = icc([[c[i] for c in lin] for i in range(len(dates))])
        raw = icc([[sc[d][p] for p in prompts] for d in dates])
        hikes, cuts = sum(a == 1 for a in act), sum(a == -1 for a in act)
        log.append(f"  {path:<22} n {len(dates)} (hikes {hikes}, cuts {cuts})  raw {raw:.3f}  "
                   f"resid linear {resid_l:.3f}  resid dummies {resid_d:.3f}  "
                   f"drop {100 * (1 - resid_l / raw):.0f}% / {100 * (1 - resid_d / raw):.0f}%")

    # (7) predictable part of MPS: MPS - MPS_ORTH on dScore, and MPS on the same meetings
    common = [d for d in hold if "MPS_ORTH" in market[d]]
    y_pred = [market[d]["MPS"] - market[d]["MPS_ORTH"] for d in common]
    r = reg(y_pred, [[1.0, F[d]] for d in common])
    rows.append(row("predictable part (MPS - MPS_ORTH)", "MPSp", common, r))
    r = reg([market[d]["MPS"] for d in common], [[1.0, F[d]] for d in common])
    rows.append(row("MPS on the same meetings", "MPS", common, r))

    # (8) primary: winsorised, Spearman, permutation
    x = [F[d] for d in hold]
    y = [market[d]["MPS"] for d in hold]

    def wins(v, lo=0.025, hi=0.975):
        s_ = sorted(v)
        a, b = s_[int(lo * (len(v) - 1))], s_[int(round(hi * (len(v) - 1)))]
        return [min(max(t, a), b) for t in v]
    r = reg(wins(y), [[1.0, t] for t in wins(x)])
    rows.append(row("primary, x and y winsorised 2.5/97.5%", "MPS", hold, r))

    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        rk = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                rk[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return rk
    rho = statistics.correlation(ranks(x), ranks(y))
    real_b = A.ols(y, [[1.0, t] for t in x], 0)["b"][1]
    rng = random.Random(1)
    perm = 0
    for _ in range(2000):
        xs = x[:]
        rng.shuffle(xs)
        perm += abs(A.ols(y, [[1.0, t] for t in xs], 0)["b"][1]) >= abs(real_b)
    log.append("")
    log.append(f"  primary Spearman rho {rho:.3f}; permutation p (2000 shuffles of dScore, seed 1) {perm / 2000:.3f}")

    # (9) greedy drop of 5, and a benchmark: the same drop applied to data
    # simulated from the fitted line with resampled residuals (fat tails kept)
    lag = A.nw_lag(len(hold))

    def tnw(xv, yv):
        n = len(xv)
        mx, my = statistics.fmean(xv), statistics.fmean(yv)
        sxx = sum((t - mx) ** 2 for t in xv)
        b = sum((t - mx) * (u - my) for t, u in zip(xv, yv)) / sxx
        h = [(t - mx) * (u - my - b * (t - mx)) for t, u in zip(xv, yv)]
        S = sum(v * v for v in h)
        L = A.nw_lag(n) if lag is None else A.nw_lag(n)
        for l_ in range(1, L + 1):
            w = 1 - l_ / (L + 1)
            S += 2 * w * sum(h[t] * h[t - l_] for t in range(l_, n))
        return b / math.sqrt(S / sxx ** 2 * n / (n - 2))

    def greedy(xv, yv, k=5):
        idx = list(range(len(xv)))
        path = []
        for _ in range(k):
            best = min(idx, key=lambda i: tnw([xv[j] for j in idx if j != i], [yv[j] for j in idx if j != i]))
            idx.remove(best)
            path.append((best, tnw([xv[j] for j in idx], [yv[j] for j in idx])))
        return path
    t_full = tnw(x, y)
    path = greedy(x, y)
    dropped = [hold[i] for i, _ in path]
    log.append(f"  greedy drop (fast NW, check vs part K): full t {t_full:.2f} -> "
               + " -> ".join(f"{t:.2f}" for _, t in path) + "; dropped " + ", ".join(dropped))
    fit = A.ols(y, [[1.0, t] for t in x], 0)["b"]
    res = [u - fit[0] - fit[1] * t for t, u in zip(x, y)]
    rng = random.Random(2)
    sims = []
    for _ in range(200):
        ys = [fit[0] + fit[1] * t + rng.choice(res) for t in x]
        sims.append((tnw(x, ys), greedy(x, ys)[-1][1]))
    sims.sort(key=lambda v: v[1])
    full_med = statistics.median(v[0] for v in sims)
    after_med = statistics.median(v[1] for v in sims)
    share = sum(v[1] <= path[-1][1] for v in sims) / len(sims)
    log.append(f"  benchmark (200 simulations, true slope = estimate, resampled residuals, seed 2):"
               f" median full t {full_med:.2f}, median t after greedy drop of 5 {after_med:.2f},"
               f" share at or below the actual {path[-1][1]:.2f}: {share:.2f}")

    # (10) Fable vs Gemini without the five most influential meetings
    G = A.dscores(A.collapse(A.load_cells(A.GEMINI)[0]), statements, "consensus")
    log.append("")
    log.append("  Fable vs Gemini without " + ", ".join(dropped))
    for tgt in ("MPS", "d2", "d10", "t2", "t10"):
        use = [d for d in pre if d in F and d in G and tgt in market[d] and policy[d] == 0
               and d not in dropped]
        n = len(use)

        def z(v):
            mu, sd = statistics.mean(v), statistics.pstdev(v)
            return [(t - mu) / sd for t in v]
        zf, zg = z([F[d] for d in use]), z([G[d] for d in use])
        yy = [market[d][tgt] for d in use]
        j = A.ols(yy, [[1.0, a, b] for a, b in zip(zf, zg)], A.nw_lag(n))
        tf, tg = (j["b"][i] / j["se"]["nw"][i] for i in (1, 2))

        def gap(idx):
            ys = [yy[i] for i in idx]
            return (A.ols(ys, [[1.0, zf[i]] for i in idx], 0)["b"][1]
                    - A.ols(ys, [[1.0, zg[i]] for i in idx], 0)["b"][1])
        g0 = gap(range(n))
        rng, L, draws = random.Random(1), 4, []
        for _ in range(2000):
            idx = []
            while len(idx) < n:
                st = rng.randrange(n - L + 1)
                idx.extend(range(st, st + L))
            draws.append(gap(idx[:n]))
        draws.sort()
        se = statistics.stdev(draws)
        log.append(f"  J-drop5 {tgt:<4} n {n}  joint t Fable {tf:.2f} Gemini {tg:.2f}  gap z {g0 / se:.2f}"
                   f"  [{draws[50]:.3f}, {draws[1949]:.3f}]")

    # (11) unprompted naming at the five influential meetings vs other hold meetings
    reps = [r for r in csv.DictReader(open(A.FABLE)) if r.get("raw_reply")]
    def rate(ds):
        rs = [r for r in reps if r["date"] in ds]
        return sum(A.mentions(r["raw_reply"], r["date"])[1] for r in rs), len(rs)
    a1, n1 = rate(set(dropped))
    a2, n2 = rate(set(hold) - set(dropped))
    log.append(f"  naming own month+year (scores_fable replies): influential 5 {a1}/{n1}, other hold {a2}/{n2}")

    os.makedirs(OUT, exist_ok=True)
    fields = ["check", "y", "n", "beta", "t_nw", "p_nw", "r2", "first", "last"]
    with open(os.path.join(OUT, "extra.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(OUT, "scatter.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "dscore", "mps"])
        for d in hold:
            w.writerow([d, f"{F[d]:.4f}", f"{market[d]['MPS']:.4f}"])
    lines = [f"  {r['check']:<40}{r['y']:<5}{r['n']:>4}{r['beta']:>9.3f}{r['t_nw']:>7.2f}"
             f"{r['p_nw']:>7.3f}  {r['first']}..{r['last']}" for r in rows]
    text = "\n".join(["Exploratory checks (Fable, hold, policy corpus, NW)",
                      f"  {'check':<40}{'y':<5}{'n':>4}{'beta':>9}{'t_nw':>7}{'p_nw':>7}"]
                     + lines + [""] + log + [f"\n  {len(rows)} regression coefficients"])
    open(os.path.join(OUT, "extra.txt"), "w").write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
