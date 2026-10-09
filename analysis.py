#!/usr/bin/env python3
"""
analysis.py - Reproduce the project's results from the score files on disk.

    python3 analysis.py                       # everything
    python3 analysis.py --score P1_minimal    # use one prompt instead of the consensus
    python3 analysis.py --csv results.csv     # also save every regression as a row
    python3 analysis.py --extra clean=clean_fable.csv --extra blind=blind_fable.csv
                                              # add any score file to parts B, C and E
    python3 analysis.py --corpus all          # old corpus incl. non-policy notices
    python3 analysis.py --corpus strict       # scheduled + unscheduled rate cuts only
    python3 analysis.py --drop-framework      # leave out the two framework
                                              # announcements (FRAMEWORK below;
                                              # a no-op unless --corpus all)

CORPUS (corpus_types.csv, one row per statement, hand-checked 2026-10-03):
  scheduled           post-meeting statement of a scheduled meeting (212)
  unscheduled_rate    unscheduled funds-rate change (7)
  unscheduled_policy  unscheduled FOMC stance/purchase decision, no rate
                      change: 2007-08-17, 2020-03-23 (2)
  notice              liquidity, swap-line, technical or framework notice (7)
  --corpus policy (default) drops the notices, strict also drops
  unscheduled_policy, all keeps everything (the pre-2026-10-03 behaviour).
  Statements are dropped BEFORE dScore pairs are formed, so the next
  statement is differenced against the previous policy statement.
  A statement on a non-trading day (2020-03-15, a Sunday) gets the next
  trading day's d2/d10 (close-to-close from the last trading day before it).

No API calls, stdlib only (the OLS, HC1 and Newey-West code is below).

PART I - RECOGNITION WHILE SCORING (stored replies, no API)
  Share of scoring replies per file that name a date: "<Month> [day,] <year>"
  or "<year> statement/meeting/decision"; and the share whose named month and
  year are the statement's own. On blinded and paraphrased text the date is
  not in the input, so a correct one came from the model. A lower bound:
  replies were stored cut at 300 characters, and most prompts ask for the
  number only. Fable's full-corpus file is also split by prompt.

PART J - FABLE vs GEMINI (review section 4.5)
  Hold meetings to 2023-12, both dScores standardised (z) on the common
  meetings. (1) Joint regression y = a + bF zF + bG zG, NW t. (2) Paired gap
  in per-sd betas from the two separate regressions, bF - bG, with the part G
  moving-block bootstrap (block 4, 2000 draws, seed 1).

PART K - CHECKS OF THE REVIEW'S CLAIMS (Fable, hold, statements to 2023-12)
  (1) Placebo days: d2/d10 measured k trading days from the statement day
      (k = -30..-1, +1..+30; yields.csv close-to-close changes), same
      regression; how often |t| reaches the real one, and the placebo 95th
      percentile of |t|. (2) Influence: leave-one-out range of the NW t, and
      greedily dropping the meeting whose removal lowers t most, 5 times.
  (3) GPT-4 coarseness: distinct score values, share at -1, share of hold
      dScores exactly 0, ZLB (2009-01..2015-11) statements at -1.

PART L - FABLE'S CUTOFF AND RELIABILITY ON TEXT IT MAY NOT KNOW
  (if probe_post.csv and fable_post5.csv exist; 2026-10-08, $0.47 + ~$0.4)
  Dating probe on the blinded 2024-26 statements, by half-year, with
  Fable's stated confidence. Then the five-prompt spread (sd across prompts
  per statement) on the 7 latest statements, scored with all five prompts,
  split into ones Fable dates confidently and exactly (known) and the rest
  (probably after its cutoff), against the spread on the 171 pre-2024
  statements with all five prompts.

PART M - HUMAN LABELS (if human_labels.csv has labels; HUMAN_LABELS.md)
  40 randomly drawn (seed 7) pre-2024 hold-meeting pairs, labelled by hand
  H / S / D (new statement more hawkish / same / more dovish than the
  previous one). For each model: how often the sign of its dScore matches
  the label on the H and D pairs, and the rank correlation between dScore
  and the label coded +1 / 0 / -1. A validity check that markets and
  training-data memory cannot touch.

PART N - PUBLISHED HUMAN LABELS (if tdw_labels.csv exists; tdw_match.py)
  Shah, Paturi & Chava (2023) hand-labelled FOMC sentences, matched word for
  word to sentences in our statements (hawkish +1, neutral 0, dovish -1).
  Per statement with at least 2 matched sentences: the mean label. Then the
  correlation of each model's score LEVEL with it (all and hold meetings),
  and of dScore with the change in the mean label. The matched sentences
  are a few repeated, partly boilerplate sentences per statement and differ
  between neighbours, so the change test mostly measures which sentences
  happen to be labelled; only the level test is informative.

PRIMARY SPECIFICATION (frozen 2026-10-03, printed last as part P)
  y = MPS (Bauer-Swanson), x = Fable consensus dScore (prompt fixed
  effects), --corpus policy, hold meetings, no control, Newey-West SE,
  statements to 2023-12. Every other regression is secondary. Part P gives
  the primary row, the Holm and Bonferroni adjusted p over the family of
  Fable's 12 part-B regressions (MPS, MPS_ORTH, d2, d10 x all / all +
  change_bp / hold), the total number of regressions printed, and the
  primary on the 2003+ sample that d2/d10 have (review m6).
  The primary is only "primary" with the defaults (--corpus policy,
  --dscore demeaned, --score consensus); part P says so when they differ.

PART A - RELIABILITY (report.py's logic, one table across all score files)
  ICC of raw levels, ICC after removing the rate decision, ICC on hold
  meetings, and the drop; the same table with Krippendorff's alpha (interval).
  Plus Fable test-retest from cells scored twice.
  Then a three-way variance decomposition (statement x prompt x model) on the
  fully crossed 2015-19 block (CROSSED files: 41 statements x 5 prompts x 4
  models), on levels and on meeting-to-meeting changes, raw and standardised
  within model. Random-effects ANOVA, one score per cell, so the three-way
  interaction is not separable from noise ("resid"); negative variance
  estimates are set to 0 before taking shares.

PART B - VALIDITY: do meeting-to-meeting score changes predict the market?
  y  = MPS, MPS_ORTH (Bauer-Swanson, to 2023-12), d2, d10 (bp, statement day,
       daily close-to-close), t2, t10 (bp, 30-minute window around the
       release: surprises.csv TNOTE02/TNOTE10 x 100, to 2023-12)
  x  = dScore = consensus score at this statement minus the previous statement's
  with and without change_bp as a control; all meetings and hold meetings only.
  Fable and Gemini are run on the same statement pairs so they are comparable.
  SEs: OLS, HC1, Newey-West (Bartlett kernel, lag in meetings).

  If scores_dict.csv exists (dictionary.py), the word-count baseline is run
  alongside as "dict".

PART C - POST-CUTOFF CHECK
  Same dScore vs d2/d10 regressions on 2024+ statements, where no surprise
  series exists and training-data contamination is least likely.

PART D - POWER: how many post-cutoff meetings would it take?
  Takes Fable's pre-2024 R2 as the true effect and asks how many meetings a
  test at 5% (two-sided) needs for 80% power, what power the post-2024 sample
  has now, and how many years of meetings the gap represents. The pre-2024 R2
  is a winner's-curse estimate (we are looking at it because it was
  significant), so the true requirement is, if anything, larger.

PART E - RECOGNITION (if probe_fable.csv exists; built by probe.py)
  How well Fable dates the blinded statements (exact month, within 1 / 3 / 12
  months, exact year, and on the 2009-01..2015-11 zero-lower-bound statements
  where the rate level gives no clue). Then the hold-meeting regressions split
  by whether the statement was dated to the exact month ("recognised").
  A split with fewer than 8 meetings is not run.
  Text-similarity baseline (no memory, no API; review section 5): each
  blinded pre-2024 statement is matched to its most similar OTHER blinded
  statement (TF-IDF over words and word pairs, cosine) and given that
  statement's date. A generous baseline - it sees every other statement with
  its true date. It cannot name the exact meeting (the neighbour is another
  meeting); "brackets" counts statements whose two nearest neighbours are the
  meetings just before and after it, i.e. where a reader who knows the
  sequence could pin down the exact meeting.

PART F - DOES dScore ADD ANYTHING TO YIELDS BEYOND MPS?
  d2 / d10 on MPS (plus change_bp on all meetings), then the same with dScore
  added, pre-2024. Reports base R2, R2 with dScore, the gain, and dScore's
  beta and t.

PART G - PAIRED BETA GAPS (only if an --extra is labelled "clean")
  For every other --extra, hold meetings: beta(clean) - beta(other) on the
  same meetings, with a moving-block bootstrap (block 4, 2000 draws, seed 1)
  for its standard error and 95% interval. Answers "did blinding/paraphrasing
  weaken the signal by more than noise would?".

PART H - BEFORE vs AFTER A MODEL'S TRAINING CUTOFF (--cutoff LABEL=DATE)
  For an --extra model with a known training cutoff (e.g. gpt4=2021-09-30
  for openai/gpt-4), the same dScore regressions on statements up to the
  cutoff (the model may have memorised them) and after it (it cannot have).
  MPS exists only to 2023-12, so the post-cutoff MPS rows are short; d2 and
  d10 run to the end of the corpus. Fable, on the same post-cutoff
  statements, is shown for comparison (it may know them).
"""

import argparse
import collections
import csv
import datetime
import math
import os
import random
import statistics

from pilot import PROMPTS, parse_score
from report import icc, residualise

FABLE = "scores_fable.csv"
GEMINI = "full_gemini.csv"
DICT = "scores_dict.csv"
BLOCK_FILES = ["changes.csv", "changes_claude.csv", "changes_openai.csv",
               "changes_frontier.csv", "changes_2004.csv"]
CROSSED = ["changes.csv", "changes_claude.csv", "changes_openai.csv",
           "changes_frontier.csv"]
POST_CUTOFF = "2024-01-01"
# Statements on longer-run goals and strategy, not post-meeting policy
# statements. With --drop-framework they are removed from the corpus before
# dScore is formed, so the next meeting is differenced against the meeting
# before the announcement.
FRAMEWORK = ("2020-08-27", "2025-08-22")
PROBE = "probe_fable.csv"
CORPUS_TYPES = "corpus_types.csv"
CORPUS_DROP = {"policy": {"notice"}, "strict": {"notice", "unscheduled_policy"}, "all": set()}


# --- data --------------------------------------------------------------------

# Score-parsing audit (review m2). Replies were stored cut at 300 characters
# before 2026-10-03. A reply shorter than that is complete, so it is re-parsed
# with pilot.parse_score (strict since 2026-10-03) and the row is dropped if
# that fails or disagrees with the stored score ("-0.", "0."). Longer replies
# cannot be re-parsed; one was found wrong by hand: its full reply was cut
# off after "1.75%", parsed as 1.0 and flipped to -1.0 (the other run of the
# same cell says -0.2 -> +0.2, the other prompts +0.10 to +0.15).
PARSE_ERRORS = {("2002-03-19", "P4_reversed", "fable_p1.csv")}
FLIP = {p["name"]: p["flip"] for p in PROMPTS}
DROPPED = collections.defaultdict(list)     # path -> [(date, prompt, score, reply)]


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
            raw = r.get("raw_reply") or ""
            bad = (r["date"], r["prompt"], r.get("source")) in PARSE_ERRORS
            if not bad and r["prompt"] in FLIP and len(raw) < 300:
                v = parse_score(raw, FLIP[r["prompt"]])
                bad = v is None or abs(v - s) > 1e-9
            if bad:
                if (r["date"], r["prompt"], s, raw) not in DROPPED[path]:
                    DROPPED[path].append((r["date"], r["prompt"], s, raw))
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
        # 30-minute changes in the 2y/10y Treasury note yield around the
        # release (Bauer-Swanson, percentage points; x100 = bp, same sign as
        # d2/d10: yields up = positive). Checked 2026-10-03 against the daily
        # d2/d10 on 2003-23 statements: corr 0.65 / 0.66, slope 1.05 / 1.23.
        for k, out in (("TNOTE02", "t2"), ("TNOTE10", "t10")):
            if r[k]:
                market[r["date"]][out] = 100 * float(r[k])
    days = []
    for r in csv.DictReader(open("yields.csv")):
        days.append(r["date"])
        for k in ("d2", "d10"):
            if r[k]:
                market[r["date"]][k] = float(r[k])
    # A statement released on a non-trading day takes the next trading day's
    # close-to-close change, which spans the release.
    for d in statements:
        if days[0] < d <= days[-1] and "d2" not in market[d]:
            nxt = min((x for x in days if x > d), default=None)
            gap = nxt and (datetime.date.fromisoformat(nxt) - datetime.date.fromisoformat(d)).days
            if nxt and nxt not in statements and gap <= 3:
                for k in ("d2", "d10"):
                    if k in market[nxt]:
                        market[d][k] = market[nxt][k]
    return statements, policy, market


def corpus_filter(statements, corpus):
    """Drop the statement types --corpus excludes (see CORPUS in the docstring)."""
    types = {r["date"]: r["type"] for r in csv.DictReader(open(CORPUS_TYPES))}
    missing = [d for d in statements if d not in types]
    if missing:
        raise SystemExit(f"{CORPUS_TYPES} has no type for {missing}")
    drop = CORPUS_DROP[corpus]
    return [d for d in statements if types[d] not in drop], \
        [d for d in statements if types[d] in drop]


def changes(score, statements):
    """dScore between consecutive corpus statements; a pair is dropped if either side is unscored."""
    out = {}
    for prev, cur in zip(statements, statements[1:]):
        if prev in score and cur in score:
            out[cur] = score[cur] - score[prev]
    return out


DSCORE = "demeaned"  # --dscore; how the consensus copes with missing prompts


def dscores(scores, statements, how):
    """dScore from {date: {prompt: score}} between consecutive corpus statements.

    One prompt (how = its name): the plain change. Consensus (review m1: from
    2020 many Fable statements have 1-3 prompts, so 54 pairs differenced
    averages over DIFFERENT prompt sets and picked up prompt level offsets):
      demeaned (default) - prompt fixed effects: each prompt's mean offset
          from the 5-prompt average, estimated on statements that have every
          prompt, is subtracted before averaging. Statements with all prompts
          are unchanged (the offsets sum to 0); no pair is lost.
      matched - mean over prompts scored at BOTH statements of the per-prompt
          change; a pair with no common prompt is dropped (22 Fable pairs,
          most of them 2024+).
      raw - change in the mean over whatever prompts each has (pre-2026-10-03).
    """
    if how != "consensus":
        return changes(series(scores, how), statements)
    if DSCORE == "matched":
        out = {}
        for prev, cur in zip(statements, statements[1:]):
            common = set(scores.get(prev, {})) & set(scores.get(cur, {}))
            if common:
                out[cur] = statistics.mean(scores[cur][p] - scores[prev][p] for p in common)
        return out
    if DSCORE == "demeaned":
        prompts = sorted({p for v in scores.values() for p in v})
        full = [v for v in scores.values() if len(v) == len(prompts)]
        off = {p: statistics.mean(v[p] - statistics.mean(v.values()) for v in full)
               for p in prompts} if len(full) >= 10 else {p: 0.0 for p in prompts}
        scores = {d: {p: x - off[p] for p, x in v.items()} for d, v in scores.items()}
    return changes(series(scores, "consensus"), statements)


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

def kripp_alpha(M):
    """Krippendorff's alpha, interval metric. M: one row per statement, one
    value per prompt (None = missing); rows with under 2 values are skipped."""
    units = [[x for x in r if x is not None] for r in M]
    units = [u for u in units if len(u) >= 2]
    vals = [x for u in units for x in u]
    n = len(vals)

    def ssd(xs):    # sum over ordered pairs i != j of (xi - xj)^2
        return 2 * (len(xs) * sum(x * x for x in xs) - sum(xs) ** 2)
    do = sum(ssd(u) / (len(u) - 1) for u in units) / n
    de = ssd(vals) / (n * (n - 1))
    return 1 - do / de if de else float("nan")


def reliability_row(label, scores, actions, order):
    prompts = sorted({p for v in scores.values() for p in v})
    dates = sorted(d for d in scores if len(scores[d]) == len(prompts) and d in actions)
    if len(dates) < 10 or len(prompts) < 2:
        return None
    act = [actions[d] for d in dates]
    levels = [[scores[d][p] for p in prompts] for d in dates]
    cols = [residualise([scores[d][p] for d in dates], act)[0] for p in prompts]
    resid = [[c[i] for c in cols] for i in range(len(dates))]
    holds = [levels[i] for i, a in enumerate(act) if a == 0]
    # changes only between statements that are adjacent in the corpus, not
    # across a gap left by a statement without all prompts (review m1)
    pos = {d: i for i, d in enumerate(order)}
    ch = [[levels[i][j] - levels[i - 1][j] for j in range(len(prompts))]
          for i in range(1, len(dates)) if pos[dates[i]] - pos[dates[i - 1]] == 1]
    raw, res = icc(levels), icc(resid)
    return {"a_raw": kripp_alpha(levels), "a_resid": kripp_alpha(resid),
            "a_hold": kripp_alpha(holds) if len(holds) >= 10 else float("nan"),
            "a_chg": kripp_alpha(ch),
            "label": label, "n": len(dates), "k": len(prompts),
            "window": f"{dates[0][:7]}..{dates[-1][:7]}", "raw": raw, "resid": res,
            "hold": icc(holds) if len(holds) >= 10 else float("nan"),
            "chg": icc(ch), "drop": 100 * (1 - res / raw) if raw else float("nan")}


def part_a(policy, keep):
    order = sorted(keep)
    print("=" * 78)
    print("A. RELIABILITY  (ICC(3,1) across prompts; statements with all prompts only)")
    print("=" * 78)
    actions = {d: (v > 0) - (v < 0) for d, v in policy.items() if d in keep}
    rows = []
    for path in BLOCK_FILES + [GEMINI, FABLE]:
        cells, model = load_cells(path)
        r = reliability_row(f"{model.split('/')[-1]} [{path}]", collapse(cells), actions, order)
        if r:
            rows.append(r)
    print(f"\n  {'model [file]':<44}{'n':>4}  {'window':<16}{'raw':>6}{'resid':>7}"
          f"{'hold':>7}{'chg':>7}{'drop':>7}")
    for r in rows:
        print(f"  {r['label'][:43]:<44}{r['n']:>4}  {r['window']:<16}{r['raw']:>6.3f}"
              f"{r['resid']:>7.3f}{r['hold']:>7.3f}{r['chg']:>7.3f}{r['drop']:>6.0f}%")
    print("\n  raw = levels; resid = after regressing out hike/hold/cut; hold = no-change")
    print("  meetings only; chg = meeting-to-meeting changes; drop = 1 - resid/raw.")
    print("\n  Same table, Krippendorff's alpha (interval metric) instead of ICC(3,1):")
    print(f"\n  {'model [file]':<44}{'n':>4}  {'window':<16}{'raw':>6}{'resid':>7}"
          f"{'hold':>7}{'chg':>7}{'drop':>7}")
    for r in rows:
        drop = 100 * (1 - r["a_resid"] / r["a_raw"]) if r["a_raw"] else float("nan")
        print(f"  {r['label'][:43]:<44}{r['n']:>4}  {r['window']:<16}{r['a_raw']:>6.3f}"
              f"{r['a_resid']:>7.3f}{r['a_hold']:>7.3f}{r['a_chg']:>7.3f}{drop:>6.0f}%")
    print("  Alpha also penalises consistent prompt offsets (ICC(3,1) does not), so")
    print("  it is at or below ICC when prompts differ in level.")

    cells, _ = load_cells(FABLE)
    pairs = [v[:2] for ps in cells.values() for v in ps.values() if len(v) > 1]
    if len(pairs) > 2:
        a, b = zip(*pairs)
        mad = statistics.mean(abs(x - y) for x, y in pairs)
        print(f"\n  Fable test-retest: {len(pairs)} cells scored in two runs, r = "
              f"{statistics.correlation(a, b):.3f}, mean |diff| = {mad:.3f}, "
              f"{sum(x != y for x, y in pairs)} differ")
    part_a_crossed(keep)


def variance3(Y):
    """Random-effects three-way ANOVA, one observation per cell. Y[i][j][l]:
    statement i, prompt j, model l. Returns variance-component shares (%)."""
    n, k, m = len(Y), len(Y[0]), len(Y[0][0])
    I, J, L = range(n), range(k), range(m)
    g = statistics.mean(Y[i][j][l] for i in I for j in J for l in L)
    s_ = [statistics.mean(Y[i][j][l] for j in J for l in L) for i in I]
    p_ = [statistics.mean(Y[i][j][l] for i in I for l in L) for j in J]
    m_ = [statistics.mean(Y[i][j][l] for i in I for j in J) for l in L]
    sp = [[statistics.mean(Y[i][j][l] for l in L) for j in J] for i in I]
    sm = [[statistics.mean(Y[i][j][l] for j in J) for l in L] for i in I]
    pm = [[statistics.mean(Y[i][j][l] for i in I) for l in L] for j in J]
    ss = {"S": k * m * sum((a - g) ** 2 for a in s_),
          "P": n * m * sum((a - g) ** 2 for a in p_),
          "M": n * k * sum((a - g) ** 2 for a in m_),
          "SP": m * sum((sp[i][j] - s_[i] - p_[j] + g) ** 2 for i in I for j in J),
          "SM": k * sum((sm[i][l] - s_[i] - m_[l] + g) ** 2 for i in I for l in L),
          "PM": n * sum((pm[j][l] - p_[j] - m_[l] + g) ** 2 for j in J for l in L)}
    sst = sum((Y[i][j][l] - g) ** 2 for i in I for j in J for l in L)
    ss["E"] = sst - sum(ss.values())
    df = {"S": n - 1, "P": k - 1, "M": m - 1, "SP": (n - 1) * (k - 1),
          "SM": (n - 1) * (m - 1), "PM": (k - 1) * (m - 1),
          "E": (n - 1) * (k - 1) * (m - 1)}
    ms = {e: ss[e] / df[e] if df[e] else 0.0 for e in ss}
    v = {"E": ms["E"],
         "SP": (ms["SP"] - ms["E"]) / m, "SM": (ms["SM"] - ms["E"]) / k,
         "PM": (ms["PM"] - ms["E"]) / n}
    v["S"] = (ms["S"] - ms["SP"] - ms["SM"] + ms["E"]) / (k * m)
    v["P"] = (ms["P"] - ms["SP"] - ms["PM"] + ms["E"]) / (n * m)
    v["M"] = (ms["M"] - ms["SM"] - ms["PM"] + ms["E"]) / (n * k)
    v = {e: max(x, 0.0) for e, x in v.items()}
    tot = sum(v.values())
    return {e: 100 * x / tot for e, x in v.items()}, n


def part_a_crossed(keep):
    tabs, models = [], []
    for path in CROSSED:
        cells, model = load_cells(path)
        tabs.append(collapse(cells))
        models.append(model.split("/")[-1])
    prompts = sorted({p for t in tabs for v in t.values() for p in v})
    dates = sorted(d for d in tabs[0] if d in keep
                   and all(d in t and all(p in t[d] for p in prompts) for t in tabs))
    if len(dates) < 10:
        return
    lev = [[[t[d][p] for t in tabs] for p in prompts] for d in dates]
    chg = [[[lev[i][j][l] - lev[i - 1][j][l] for l in range(len(tabs))]
            for j in range(len(prompts))] for i in range(1, len(dates))]

    def standardise(Y):
        out = [[row[:] for row in plane] for plane in Y]
        for l in range(len(tabs)):
            col = [Y[i][j][l] for i in range(len(Y)) for j in range(len(prompts))]
            mu, sd = statistics.mean(col), statistics.pstdev(col)
            for i in range(len(Y)):
                for j in range(len(prompts)):
                    out[i][j][l] = (Y[i][j][l] - mu) / sd if sd else 0.0
        return out

    print(f"\n  Three-way variance decomposition, {len(dates)} statements "
          f"({dates[0][:7]}..{dates[-1][:7]}) x {len(prompts)} prompts x "
          f"{len(tabs)} models")
    print(f"  models: {', '.join(models)}")
    keys = [("S", "stmt"), ("P", "prompt"), ("M", "model"), ("SP", "SxP"),
            ("SM", "SxM"), ("PM", "PxM"), ("E", "resid")]
    print(f"\n  {'data':<24}{'n':>4}" + "".join(f"{lab:>8}" for _, lab in keys))
    for lab, Y in (("levels, raw", lev), ("levels, std in model", standardise(lev)),
                   ("changes, raw", chg), ("changes, std in model", standardise(chg))):
        sh, n = variance3(Y)
        print(f"  {lab:<24}{n:>4}" + "".join(f"{sh[e]:>7.1f}%" for e, _ in keys))
    print("\n  Shares of total variance. stmt = agreed statement differences (signal);")
    print("  SxM = models disagree about which statements are hawkish; SxP = prompts")
    print("  disagree; resid = statement x prompt x model interaction plus noise.")
    print("  std in model: each model's scores z-scored over all its cells first,")
    print("  which removes scale differences (the model share is then 0 by design).")


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
    print(f"\n  {'y':<9}{'sample':<10}{'control':<11}{'model':<8}{'n':>4}{'beta':>9}"
          f"{'t_ols':>7}{'t_hc1':>7}{'t_nw':>7}{'p_nw':>7}{'R2':>7}")
    last = None
    for r in rows:
        key = (r["y"], r["sample"], r["control"])
        if last and key[:2] != last[:2]:
            print()
        last = key
        print(f"  {r['y']:<9}{r['sample']:<10}{r['control']:<11}{r['model']:<8}{r['n']:>4}"
              f"{r['beta']:>9.3f}{r['t_ols']:>7.2f}{r['t_hc1']:>7.2f}{r['t_nw']:>7.2f}"
              f"{r['p_nw']:>7.3f}{r['r2']:>7.3f}")


def part_bc(statements, policy, market, how, out, extra=()):
    models = {}
    for label, path in (("fable", FABLE), ("gemini", GEMINI), ("dict", DICT), *extra):
        if label == "dict" and not os.path.exists(path):
            continue
        cells, _ = load_cells(path)
        # --score applies to the full-corpus LLM files; the dictionary and
        # --extra files are used as they are (mean over whatever prompts they hold).
        models[label] = dscores(collapse(cells), statements,
                                 how if label in ("fable", "gemini") else "consensus")
    common = sorted(set(models["fable"]) & set(models["gemini"]))

    print("\n" + "=" * 78)
    print(f"B. VALIDITY: market move on dScore ({how}), statements to 2023-12")
    print("=" * 78)
    pre = [d for d in common if d < POST_CUTOFF]
    for label in models:
        both = [d for d in pre if d in models[label]]
        print(f"  {label}: {len(both)} dScore pairs before {POST_CUTOFF}; "
              f"sd(dScore) = {statistics.pstdev(models[label][d] for d in both):.3f}")
    names = list(models)
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            both = [d for d in pre if d in models[x] and d in models[y]]
            r = statistics.correlation([models[x][d] for d in both], [models[y][d] for d in both])
            print(f"  corr({x} dScore, {y} dScore) = {r:.3f}")
    rows = []
    for label in models:
        run_specs(label, models[label], policy, market, pre,
                  ("MPS", "MPS_ORTH", "d2", "d10", "t2", "t10"), ("all", "hold"), rows)
    order = {m: i for i, m in enumerate(models)}
    rows.sort(key=lambda r: (["MPS", "MPS_ORTH", "d2", "d10", "t2", "t10"].index(r["y"]),
                             r["sample"], r["control"], order[r["model"]]))
    print_rows(rows)
    print("\n  beta: market units (MPS in pct pts, d2/d10/t2/t10 in bp) per 1.0 of dScore.")
    print("  t2/t10 = 30-minute intraday yield changes; not in part P's frozen family.")
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
    rows.sort(key=lambda r: (r["y"], r["sample"], r["control"], order[r["model"]]))
    print_rows(rows)
    print("\n  Too few points for Newey-West here; lag set to 0 (t_nw = t_hc1).")
    for r in rows:
        r["part"] = "C"
    out.extend(rows)
    return sorted(d for d in models["fable"] if d >= POST_CUTOFF)


def part_d(policy, post, out):
    print("\n" + "=" * 78)
    print("D. POWER: post-cutoff meetings needed to detect Fable's pre-2024 effect")
    print("=" * 78)
    z = statistics.NormalDist()
    za, zb = z.inv_cdf(0.975), z.inv_cdf(0.80)
    years = (int(post[-1][:4]) - int(POST_CUTOFF[:4])) + int(post[-1][5:7]) / 12 if post else 0
    print(f"\n  {'y':<5}{'sample':<7}{'R2 pre':>8}{'n for 80%':>11}{'n now':>7}"
          f"{'power now':>11}{'per year':>10}{'years more':>12}")
    for r in out:
        if r["part"] != "B" or r["model"] != "fable" or r["control"] != "-" \
                or r["y"] not in ("d2", "d10"):
            continue
        f2 = r["r2"] / (1 - r["r2"])
        need = math.ceil((za + zb) ** 2 / f2) + 2
        now = sum(1 for d in post if r["sample"] == "all" or policy[d] == 0)
        power = z.cdf(math.sqrt(now * f2) - za)
        rate = now / years if years else float("nan")
        more = max(need - now, 0) / rate if rate else float("nan")
        print(f"  {r['y']:<5}{r['sample']:<7}{r['r2']:>8.3f}{need:>11}{now:>7}"
              f"{power:>10.0%}{rate:>10.1f}{more:>12.0f}")
    print("\n  n for 80%: meetings needed if the pre-2024 R2 were the truth (normal")
    print("  approximation). per year: post-cutoff dScore pairs per year so far.")
    print("  Waiting for new statements cannot settle contamination in any useful")
    print("  time frame; the blinded re-score (blind.py) is the test that can.")


# --- part E ---------------------------------------------------------------------

def load_probe(path=PROBE):
    """{date: err_months} from probe.py output; the last answered row per date wins."""
    out = {}
    for r in csv.DictReader(open(path)):
        if r["err_months"] not in ("", None):
            out[r["date"]] = int(r["err_months"])
    return out


def nn_dating(folder="statements_blind"):
    """Text-similarity dating baseline; returns {date: (nearest, months off,
    nearest is adjacent, two nearest bracket it)} for pre-2024 statements."""
    import re
    dates = sorted(f[:-4] for f in os.listdir(folder) if f.endswith(".txt") and f[:-4] < POST_CUTOFF)
    docs = {}
    for d in dates:
        w = re.findall(r"[a-z0-9]+(?:[-/.][0-9a-z]+)*", open(os.path.join(folder, d + ".txt")).read().lower())
        docs[d] = collections.Counter(w + [a + " " + b for a, b in zip(w, w[1:])])
    df = collections.Counter(t for c in docs.values() for t in c)
    vec = {}
    for d, c in docs.items():
        v = {t: (1 + math.log(k)) * math.log(len(docs) / df[t]) for t, k in c.items()}
        z = math.sqrt(sum(x * x for x in v.values())) or 1.0
        vec[d] = {t: x / z for t, x in v.items()}

    def cos(a, b):
        a, b = (a, b) if len(a) <= len(b) else (b, a)
        return sum(x * b.get(t, 0.0) for t, x in a.items())

    def mon(d):
        return int(d[:4]) * 12 + int(d[5:7])
    out = {}
    for i, d in enumerate(dates):
        sims = sorted(((cos(vec[d], vec[e]), e) for e in dates if e != d), reverse=True)
        adj = {x for x in (dates[i - 1] if i else None,
                           dates[i + 1] if i + 1 < len(dates) else None) if x}
        nn = sims[0][1]
        out[d] = (nn, abs(mon(nn) - mon(d)), nn in adj,
                  {sims[0][1], sims[1][1]} == adj if len(adj) == 2 else nn in adj)
    return out


def part_e(statements, policy, market, how, out, extra=()):
    if not os.path.exists(PROBE):
        return
    err = load_probe()
    print("\n" + "=" * 78)
    print(f"E. RECOGNITION: can Fable date the blinded statement? ({PROBE})")
    print("=" * 78)
    n = len(err)
    zlb = [e for d, e in err.items() if "2009-01" <= d <= "2015-11"]
    print(f"\n  {n} statements answered, {err and min(err)} to {err and max(err)}")
    for lab, k in (("exact month", 0), ("within 1 month", 1), ("within 3 months", 3),
                   ("within 12 months", 12)):
        c = sum(abs(e) <= k for e in err.values())
        print(f"  {lab:<18}{c:>4} / {n}  ({c / n:.1%})")
    yr = sum(abs(e) < 12 and (int(d[:4]) * 12 + int(d[5:7]) + e - 1) // 12 == int(d[:4])
             for d, e in err.items())
    print(f"  {'exact year':<18}{yr:>4} / {n}")
    print(f"  {'ZLB 2009-15 exact':<18}{sum(e == 0 for e in zlb):>4} / {len(zlb)}"
          "  (same 0-1/4 rate at every meeting)")
    if os.path.isdir("statements_blind"):
        nn = nn_dating()
        z = {d: v for d, v in nn.items() if "2009-01" <= d <= "2015-11"}
        print(f"\n  Text-similarity baseline (nearest other blinded statement, TF-IDF; no memory):")
        print(f"  {'':<22}{'all':>9}{'ZLB':>9}   Fable (all / ZLB)")
        for lab, f, fab in (("within 1 month", lambda v: v[1] <= 1, (1, None)),
                            ("within 3 months", lambda v: v[1] <= 3, (3, None)),
                            ("nearest = adjacent", lambda v: v[2], None),
                            ("2 nearest bracket it", lambda v: v[3], (0, 0))):
            fa = (f"   {sum(abs(e) <= fab[0] for e in err.values())} / "
                  f"{sum(abs(e) <= fab[0] for e in zlb)}" if fab else "")
            print(f"  {lab:<22}{sum(map(f, nn.values())):>5}/{len(nn):<3}"
                  f"{sum(map(f, z.values())):>5}/{len(z):<3}{fa}")
        print("  bracket = the exact meeting is recoverable from the text sequence; the")
        print("  Fable column on that row is its exact-month count.")

    rows = []
    for label, path in (("fable", FABLE), *extra):
        cells, _ = load_cells(path)
        dsc = dscores(collapse(cells), statements,
                      how if label == "fable" else "consensus")
        for grp, keep in (("recog", lambda e: e == 0), ("not", lambda e: e != 0)):
            sub = {d: v for d, v in dsc.items() if d in err and keep(err[d])}
            tmp = []
            run_specs(label, sub, policy, market,
                      sorted(d for d in sub if d < POST_CUTOFF),
                      ("MPS", "d2", "d10"), ("hold",), tmp)
            for r in tmp:
                r["sample"] = grp
            rows.extend(tmp)
    held = [d for d in err if d < POST_CUTOFF and policy.get(d) == 0]
    rows.sort(key=lambda r: (["MPS", "d2", "d10"].index(r["y"]), r["sample"]))
    print(f"\n  hold meetings probed: {len(held)}; dated to the exact month: "
          f"{sum(err[d] == 0 for d in held)}; not: {sum(err[d] != 0 for d in held)}")
    print_rows(rows)
    print("\n  recog = statement dated to the exact month; not = any miss.")
    print("  Groups with fewer than 8 meetings are not run (no row).")
    for r in rows:
        r["part"] = "E"
    out.extend(rows)


# --- parts F and G -------------------------------------------------------------

def load_dscores(statements, how, extra):
    out = {}
    for label, path in (("fable", FABLE), ("gemini", GEMINI), *extra):
        cells, _ = load_cells(path)
        out[label] = dscores(collapse(cells), statements,
                              how if label in ("fable", "gemini") else "consensus")
    return out


def part_f(statements, policy, market, how, out, extra=()):
    print("\n" + "=" * 78)
    print("F. YIELDS ON MPS, WITH AND WITHOUT dScore (statements to 2023-12)")
    print("=" * 78)
    ds = load_dscores(statements, how, extra)
    print(f"\n  {'y':<5}{'sample':<7}{'controls':<15}{'model':<8}{'n':>4}{'R2 base':>9}"
          f"{'R2 +dS':>8}{'gain pp':>9}{'beta dS':>9}{'t_nw':>7}{'p_nw':>7}")
    for tgt in ("d2", "d10"):
        for sample in ("all", "hold"):
            for label, dsc in ds.items():
                use = [d for d in statements if d < POST_CUTOFF and d in dsc
                       and tgt in market[d] and "MPS" in market[d]
                       and (sample == "all" or policy[d] == 0)]
                y = [market[d][tgt] for d in use]
                base = [[1.0, market[d]["MPS"]] + ([float(policy[d])] if sample == "all" else [])
                        for d in use]
                full = [r + [dsc[d]] for r, d in zip(base, use)]
                lag = nw_lag(len(use))
                r0, r1 = ols(y, base, lag), ols(y, full, lag)
                t = r1["b"][-1] / r1["se"]["nw"][-1]
                p = t_pvalue(t, r1["df"])
                ctrl = "MPS+change_bp" if sample == "all" else "MPS"
                print(f"  {tgt:<5}{sample:<7}{ctrl:<15}{label:<8}{len(use):>4}{r0['r2']:>9.3f}"
                      f"{r1['r2']:>8.3f}{100 * (r1['r2'] - r0['r2']):>9.2f}"
                      f"{r1['b'][-1]:>9.3f}{t:>7.2f}{p:>7.3f}")
                out.append({"part": "F", "model": label, "y": tgt, "sample": sample,
                            "control": ctrl, "n": len(use), "beta": r1["b"][-1],
                            "t_nw": t, "p_nw": p, "nw_lag": lag, "r2": r1["r2"],
                            "first": use[0], "last": use[-1]})
        print()
    print("  gain pp = R2 with dScore minus R2 without, in percentage points.")


def part_g(statements, policy, market, how, extra):
    labels = [lab for lab, _ in extra]
    if "clean" not in labels or len(labels) < 2:
        return
    ds = load_dscores(statements, how, extra)
    print("\n" + "=" * 78)
    print("G. PAIRED BETA GAPS vs clean, hold meetings, statements to 2023-12")
    print("=" * 78)
    print(f"\n  {'y':<5}{'other':<8}{'n':>4}{'b clean':>9}{'b other':>9}{'gap':>8}"
          f"{'boot se':>9}{'z':>6}{'  95% interval':<20}")
    for tgt in ("MPS", "d2", "d10"):
        for other in labels:
            if other == "clean":
                continue
            a, b = ds["clean"], ds[other]
            use = [d for d in statements if d < POST_CUTOFF and d in a and d in b
                   and tgt in market[d] and policy[d] == 0]
            n, L = len(use), 4

            def gap(idx):
                y = [market[use[i]][tgt] for i in idx]
                ba = ols(y, [[1.0, a[use[i]]] for i in idx], 0)["b"][1]
                bb = ols(y, [[1.0, b[use[i]]] for i in idx], 0)["b"][1]
                return ba, bb

            ba, bb = gap(range(n))
            rng = random.Random(1)
            draws = []
            for _ in range(2000):
                idx = []
                while len(idx) < n:
                    st = rng.randrange(n - L + 1)
                    idx.extend(range(st, st + L))
                x, z = gap(idx[:n])
                draws.append(x - z)
            draws.sort()
            se = statistics.stdev(draws)
            print(f"  {tgt:<5}{other:<8}{n:>4}{ba:>9.3f}{bb:>9.3f}{ba - bb:>8.3f}{se:>9.3f}"
                  f"{(ba - bb) / se:>6.2f}  [{draws[50]:.3f}, {draws[1949]:.3f}]")
    print("\n  gap = beta(clean) - beta(other) on the same meetings; moving-block")
    print("  bootstrap over meetings in time order (block 4, 2000 draws, seed 1).")


# --- part H -----------------------------------------------------------------------

def part_h(statements, policy, market, how, extra, cutoffs, out):
    if not cutoffs:
        return
    ds = load_dscores(statements, how, extra)
    for label, cut in cutoffs:
        print("\n" + "=" * 78)
        print(f"H. {label}: before vs after its training cutoff {cut}")
        print("=" * 78)
        rows = []
        for win, keep in (("pre", lambda d: d <= cut), ("post", lambda d: d > cut)):
            for lab in (label, "fable"):
                if lab == "fable" and win == "pre":
                    continue
                sub = {d: v for d, v in ds[lab].items() if keep(d) and d in ds[label]}
                tmp = []
                run_specs(lab, sub, policy, market, sorted(sub),
                          ("MPS", "d2", "d10"), ("all", "hold"), tmp,
                          lag=None if win == "pre" else 0)
                for r in tmp:
                    r["sample"] = r["sample"] + "-" + win
                rows.extend(tmp)
        rows.sort(key=lambda r: (["MPS", "d2", "d10"].index(r["y"]), r["sample"].split("-")[1] == "post",
                                 r["sample"], r["control"], r["model"] != label))
        print_rows(rows)
        print(f"\n  pre = statements up to {cut}; post = after it (NW lag 0 there: few")
        print("  points, t_nw = t_hc1). Rows need 8+ meetings.")
        for r in rows:
            r["part"] = "H"
        out.extend(rows)


MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august",
          "september", "october", "november", "december"]
DATE_MENTION = __import__("re").compile(
    r"\b(January|February|March|April|May|June|July|August|September|October|November"
    r"|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)\.?\s+(?:\d{1,2}(?:-\d{1,2})?,?\s+)?"
    r"((?:19|20)\d\d)\b|\b((?:19|20)\d\d)\s+(?:FOMC\s+)?(?:statement|meeting|decision)",
    __import__("re").I)
RECOG_FILES = [("fable", FABLE, "original"), ("clean", "clean_fable.csv", "original"),
               ("blind", "blind_fable.csv", "blinded"), ("para", "para_fable.csv", "paraphrased"),
               ("gemini", GEMINI, "original"), ("gpt4", "gpt4_p1.csv", "original")]


def mentions(reply, date):
    """(names any date, names this statement's month and year)."""
    hit = own = False
    for m in DATE_MENTION.finditer(reply):
        hit = True
        if m.group(1):
            mon = next(i for i, x in enumerate(MONTHS, 1) if x.startswith(m.group(1).lower()[:3]))
            own = own or (int(m.group(2)) == int(date[:4]) and mon == int(date[5:7]))
    return hit, own


def part_i():
    print("\n" + "=" * 78)
    print("I. RECOGNITION WHILE SCORING: replies that name the statement's date")
    print("=" * 78)
    print(f"\n  {'file':<20}{'text':<13}{'prompt':<17}{'replies':>8}{'name date':>11}"
          f"{'%':>6}{'own m+y':>9}{'%':>6}")
    examples = []
    for label, path, text in RECOG_FILES:
        if not os.path.exists(path):
            continue
        rows = [r for r in csv.DictReader(open(path)) if r.get("raw_reply")]
        groups = [("all", rows)]
        if label == "fable":
            groups += [(p, [r for r in rows if r["prompt"] == p]) for p in sorted(FLIP)]
        for g, rs in groups:
            if not rs:
                continue
            hits = [mentions(r["raw_reply"], r["date"]) for r in rs]
            h, o = sum(x for x, _ in hits), sum(y for _, y in hits)
            print(f"  {path:<20}{text:<13}{g:<17}{len(rs):>8}{h:>11}{100 * h / len(rs):>6.1f}"
                  f"{o:>9}{100 * o / len(rs):>6.1f}")
        for r in rows:
            if label in ("blind", "para") and mentions(r["raw_reply"], r["date"])[1]:
                examples.append((label, r["date"], r["raw_reply"]))
    print("\n  Examples (blinded/paraphrased input, own month and year named):")
    for label, d, raw in examples[:4]:
        m = DATE_MENTION.search(raw)
        lo = max(0, m.start() - 60)
        print(f"    {label} {d}: ...{raw[lo:m.end() + 40]}...")
    print("\n  own m+y = the reply names the statement's own month and year.")


def part_j(statements, policy, market, how, out):
    ds = load_dscores(statements, how, ())
    F, G = ds["fable"], ds["gemini"]
    print("\n" + "=" * 78)
    print("J. FABLE vs GEMINI, hold meetings, statements to 2023-12, dScores in sd units")
    print("=" * 78)
    print(f"\n  {'y':<5}{'n':>4}{'joint bF':>10}{'t_nw':>7}{'joint bG':>10}{'t_nw':>7}"
          f"{'   sep bF':>10}{'sep bG':>8}{'gap':>8}{'boot se':>9}{'z':>6}  95% interval")
    for tgt in ("MPS", "d2", "d10", "t2", "t10"):
        use = [d for d in statements if d < POST_CUTOFF and d in F and d in G
               and tgt in market[d] and policy[d] == 0]
        n = len(use)

        def z(v):
            mu, sd = statistics.mean(v), statistics.pstdev(v)
            return [(x - mu) / sd for x in v]
        zf, zg = z([F[d] for d in use]), z([G[d] for d in use])
        y = [market[d][tgt] for d in use]
        j = ols(y, [[1.0, a, b] for a, b in zip(zf, zg)], nw_lag(n))
        tf, tg = (j["b"][i] / j["se"]["nw"][i] for i in (1, 2))

        def gap(idx):
            yy = [y[i] for i in idx]
            return (ols(yy, [[1.0, zf[i]] for i in idx], 0)["b"][1]
                    - ols(yy, [[1.0, zg[i]] for i in idx], 0)["b"][1])
        bf = ols(y, [[1.0, a] for a in zf], 0)["b"][1]
        bg = ols(y, [[1.0, b] for b in zg], 0)["b"][1]
        rng, L, draws = random.Random(1), 4, []
        for _ in range(2000):
            idx = []
            while len(idx) < n:
                st = rng.randrange(n - L + 1)
                idx.extend(range(st, st + L))
            draws.append(gap(idx[:n]))
        draws.sort()
        se = statistics.stdev(draws)
        print(f"  {tgt:<5}{n:>4}{j['b'][1]:>10.3f}{tf:>7.2f}{j['b'][2]:>10.3f}{tg:>7.2f}"
              f"{bf:>10.3f}{bg:>8.3f}{bf - bg:>8.3f}{se:>9.3f}{(bf - bg) / se:>6.2f}"
              f"  [{draws[50]:.3f}, {draws[1949]:.3f}]")
        for lab, b, t in (("fable|gemini", j["b"][1], tf), ("gemini|fable", j["b"][2], tg)):
            out.append({"part": "J", "model": lab, "y": tgt, "sample": "hold", "control": "joint",
                        "n": n, "beta": b, "t_nw": t, "p_nw": t_pvalue(t, j["df"]),
                        "nw_lag": j["lag"], "r2": j["r2"], "first": use[0], "last": use[-1]})
    print("\n  joint: both z-scored dScores in one regression (NW t). sep: per-sd betas")
    print("  from separate regressions; gap = sep bF - sep bG, block bootstrap as in G.")
    print("  MPS in pct pts, yields in bp, per 1 sd of dScore.")


def part_k(statements, policy, market, how, out):
    ds = load_dscores(statements, how, ())
    F = ds["fable"]
    print("\n" + "=" * 78)
    print("K. CHECKS: placebo days, influence, GPT-4 coarseness (Fable, hold, to 2023-12)")
    print("=" * 78)
    days = [r for r in csv.DictReader(open("yields.csv"))]
    pos = {r["date"]: i for i, r in enumerate(days)}
    hold = [d for d in statements if d < POST_CUTOFF and d in F and policy[d] == 0]

    def tstat(use, y):
        r = ols(y, [[1.0, F[d]] for d in use], nw_lag(len(use)))
        return r["b"][1] / r["se"]["nw"][1]
    print(f"\n  (1) placebo days  {'real t':>7}{'n days':>8}{'|t|>1.96':>10}{'|t|>=real':>11}"
          f"{'p95 |t|':>9}{'max |t|':>9}")
    for tgt, col in (("d2", "d2"), ("d10", "d10")):
        use = [d for d in hold if tgt in market[d]]
        real = tstat(use, [market[d][tgt] for d in use])
        ts = []
        for k in list(range(-30, 0)) + list(range(1, 31)):
            pu, py = [], []
            for d in use:
                i = pos.get(d)
                if i is None or not 0 <= i + k < len(days) or not days[i + k][col]:
                    continue
                pu.append(d)
                py.append(float(days[i + k][col]))
            ts.append(abs(tstat(pu, py)))
        ts.sort()
        p95 = ts[int(0.95 * len(ts)) - 1]
        print(f"  {tgt:<17}{real:>7.2f}{len(ts):>8}{sum(t > 1.96 for t in ts):>10}"
              f"{sum(t >= abs(real) for t in ts):>11}{p95:>9.2f}{ts[-1]:>9.2f}")
    print(f"\n  (2) influence     {'full t':>7}{'LOO min':>9}{'LOO max':>9}   greedy drop of 5 (t after each)")
    for tgt in ("MPS", "d2", "d10", "t2", "t10"):
        use = [d for d in hold if tgt in market[d]]
        full = tstat(use, [market[d][tgt] for d in use])
        loo = [tstat([x for x in use if x != d], [market[x][tgt] for x in use if x != d])
               for d in use]
        cur, path = use[:], []
        for _ in range(5):
            best = min(cur, key=lambda d: tstat([x for x in cur if x != d],
                                                 [market[x][tgt] for x in cur if x != d]))
            cur.remove(best)
            path.append((best, tstat(cur, [market[x][tgt] for x in cur])))
        print(f"  {tgt:<17}{full:>7.2f}{min(loo):>9.2f}{max(loo):>9.2f}   "
              + " -> ".join(f"{t:.2f}" for _, t in path))
        print(f"  {'':<17}dropped: " + ", ".join(d for d, _ in path))
    if os.path.exists("gpt4_p1.csv"):
        cells, _ = load_cells("gpt4_p1.csv")
        sc = series(collapse(cells), "consensus")
        vals = list(sc.values())
        g = dscores(collapse(cells), statements, "consensus")
        gh = [g[d] for d in g if d < POST_CUTOFF and policy[d] == 0]
        fh = [F[d] for d in F if d < POST_CUTOFF and policy[d] == 0]
        zlb = [v for d, v in sc.items() if "2009-01" <= d <= "2015-11"]
        print(f"\n  (3) GPT-4 P1: {len(vals)} scores, {len(set(vals))} distinct values, "
              f"{sum(v == -1 for v in vals)} at -1 ({100 * sum(v == -1 for v in vals) / len(vals):.0f}%)")
        print(f"      hold dScores exactly 0: GPT-4 {sum(x == 0 for x in gh)}/{len(gh)} "
              f"({100 * sum(x == 0 for x in gh) / len(gh):.0f}%), Fable "
              f"{sum(abs(x) < 1e-9 for x in fh)}/{len(fh)}; ZLB statements at -1: "
              f"{sum(v == -1 for v in zlb)}/{len(zlb)}")


def part_l():
    if not (os.path.exists("probe_post.csv") and os.path.exists("fable_post5.csv")):
        return
    print("\n" + "=" * 78)
    print("L. FABLE'S CUTOFF (2024-26 dating probe) AND PROMPT SPREAD ON UNSEEN TEXT")
    print("=" * 78)
    pr = {r["date"]: r for r in csv.DictReader(open("probe_post.csv")) if r["err_months"] != ""}
    print(f"\n  {'period':<10}{'n':>4}{'exact':>7}{'conf high':>11}   misses (err months, confidence)")
    halves = collections.defaultdict(list)
    for d, r in sorted(pr.items()):
        halves[d[:4] + ("H1" if d[5:7] <= "06" else "H2")].append((d, r))
    for h, rs in sorted(halves.items()):
        miss = [f"{d} ({r['err_months']}, {r['confidence']})" for d, r in rs if r["err_months"] != "0"]
        print(f"  {h:<10}{len(rs):>4}{sum(r['err_months'] == '0' for _, r in rs):>7}"
              f"{sum(r['confidence'] == 'high' for _, r in rs):>11}   {', '.join(miss)}")
    known = {d for d, r in pr.items() if r["err_months"] == "0" and r["confidence"] == "high"}
    post = collapse(load_cells("fable_post5.csv")[0])
    old = collapse(load_cells(FABLE)[0])
    k = len(FLIP)
    pre = sorted(statistics.pstdev(v.values()) for d, v in old.items()
                 if len(v) == k and d < POST_CUTOFF)
    print(f"\n  Spread across the {k} prompts (sd per statement); pre-2024 statements with")
    print(f"  all prompts: n {len(pre)}, median {statistics.median(pre):.3f}, "
          f"90th pct {pre[int(0.9 * len(pre))]:.3f}")
    print(f"\n  {'statement':<12}{'probe':<14}" + "".join(f"{p[:2]:>6}" for p in sorted(FLIP))
          + f"{'sd':>7}{'pctile':>8}")
    groups = collections.defaultdict(list)
    for d, v in sorted(post.items()):
        if len(v) < k:
            continue
        sd = statistics.pstdev(v.values())
        grp = "known" if d in known else "not known"
        groups[grp].append(sd)
        print(f"  {d:<12}{grp:<14}" + "".join(f"{v[p]:>6.2f}" for p in sorted(FLIP))
              + f"{sd:>7.3f}{sum(s <= sd for s in pre) / len(pre):>8.2f}")
    for g, v in groups.items():
        print(f"  mean sd, {g}: {statistics.mean(v):.3f} (n {len(v)})")
    print("\n  known = dated to the exact month with 'high' confidence. pctile = share of")
    print("  pre-2024 statements whose prompt spread is at or below this one.")


def part_m(statements, how, extra):
    if not os.path.exists("human_labels.csv"):
        return
    lab = {r["date"]: {"H": 1, "S": 0, "D": -1}[r["label"].strip().upper()]
           for r in csv.DictReader(open("human_labels.csv"))
           if r["label"].strip().upper() in ("H", "S", "D")}
    if not lab:
        return
    print("\n" + "=" * 78)
    print(f"M. HUMAN LABELS: {len(lab)} labelled pairs (H {sum(v == 1 for v in lab.values())}, "
          f"S {sum(v == 0 for v in lab.values())}, D {sum(v == -1 for v in lab.values())})")
    print("=" * 78)

    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2
            i = j + 1
        return r
    ds = load_dscores(statements, how, extra)
    if os.path.exists(DICT):
        ds["dict"] = dscores(collapse(load_cells(DICT)[0]), statements, "consensus")
    print(f"\n  {'model':<10}{'n':>4}{'sign agrees (H/D pairs)':>26}{'Spearman':>10}")
    for m, d in ds.items():
        use = [x for x in lab if x in d]
        hd = [x for x in use if lab[x]]
        agree = sum((d[x] > 0) == (lab[x] > 0) and d[x] != 0 for x in hd)
        rho = statistics.correlation(ranks([d[x] for x in use]), ranks([lab[x] for x in use])) \
            if len(use) > 2 else float("nan")
        print(f"  {m:<10}{len(use):>4}{agree:>15} / {len(hd):<10}{rho:>10.2f}")
    print("\n  sign agrees: dScore > 0 on H pairs, < 0 on D pairs (0 counts as a miss).")


def part_n(statements, policy):
    if not os.path.exists("tdw_labels.csv"):
        return
    lab = collections.defaultdict(list)
    for r in csv.DictReader(open("tdw_labels.csv")):
        lab[r["date"]].append(int(r["label"]))
    H = {d: statistics.mean(v) for d, v in lab.items() if len(v) >= 2 and d in statements}
    print("\n" + "=" * 78)
    print(f"N. PUBLISHED HUMAN LABELS (Shah et al. 2023): {len(H)} statements with 2+ "
          f"labelled sentences ({min(H)[:4]}-{max(H)[:4]})")
    print("=" * 78)
    print(f"\n  {'model':<10}{'n':>5}{'level r':>9}{'n hold':>8}{'hold r':>8}{'n chg':>7}{'dScore r':>10}")
    for label, path in (("fable", FABLE), ("gemini", GEMINI), ("dict", DICT), ("gpt4", "gpt4_p1.csv")):
        if not os.path.exists(path):
            continue
        sc = collapse(load_cells(path)[0])
        lev = series(sc, "consensus")
        ds = dscores(sc, statements, "consensus")
        use = [d for d in H if d in lev]
        hold = [d for d in use if policy[d] == 0]
        pairs = [c for p, c in zip(statements, statements[1:]) if p in H and c in H and c in ds]
        r1 = statistics.correlation([lev[d] for d in use], [H[d] for d in use])
        r2 = statistics.correlation([lev[d] for d in hold], [H[d] for d in hold])
        prev = dict(zip(statements[1:], statements))
        r3 = statistics.correlation([ds[c] for c in pairs], [H[c] - H[prev[c]] for c in pairs])
        print(f"  {label:<10}{len(use):>5}{r1:>9.3f}{len(hold):>8}{r2:>8.3f}{len(pairs):>7}{r3:>10.3f}")
    print("\n  level r: model score vs mean human label of the statement's matched")
    print("  sentences. dScore r: uninformative by construction (see docstring).")


def holm(ps):
    """Holm step-down adjusted p-values, in the input order."""
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    adj, run = [0.0] * m, 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * ps[i]))
        adj[i] = run
    return adj


def part_p(statements, policy, market, how, rows, defaults):
    print("\n" + "=" * 78)
    print("P. PRIMARY SPECIFICATION AND MULTIPLE TESTING")
    print("=" * 78)
    if not defaults:
        print("\n  NOTE: not the frozen defaults (--corpus policy, --dscore demeaned,")
        print("  --score consensus); the 'primary' row below is not the primary.")
    fam = [r for r in rows if r["part"] == "B" and r["model"] == "fable"
           and r["y"] in ("MPS", "MPS_ORTH", "d2", "d10")]
    adj = holm([r["p_nw"] for r in fam])
    m = len(fam)
    print(f"\n  Family: Fable's {m} part-B regressions. Total regressions printed in")
    print(f"  this run: {len(rows)} (all parts, all models).")
    print(f"\n  {'y':<9}{'sample':<7}{'control':<11}{'n':>4}{'beta':>9}{'t_nw':>7}{'p_nw':>8}"
          f"{'Holm':>8}{'Bonf':>8}")
    for r, h in sorted(zip(fam, adj), key=lambda t: t[0]["p_nw"]):
        star = "  <- PRIMARY" if (r["y"], r["sample"], r["control"]) == ("MPS", "hold", "-") else ""
        print(f"  {r['y']:<9}{r['sample']:<7}{r['control']:<11}{r['n']:>4}{r['beta']:>9.3f}"
              f"{r['t_nw']:>7.2f}{r['p_nw']:>8.3f}{h:>8.3f}{min(1.0, m * r['p_nw']):>8.3f}{star}")
        r["p_holm"] = h
    cells, _ = load_cells(FABLE)
    dsc = dscores(collapse(cells), statements, how)
    tmp = []
    use = [d for d in statements if d < POST_CUTOFF and d >= "2003-01-01"]
    run_specs("fable", dsc, policy, market, use, ("MPS",), ("hold",), tmp)
    for r in tmp:
        r.update(part="P", sample="hold-2003+")
        print(f"\n  Primary on the 2003+ sample (as d2/d10): n {r['n']}, beta {r['beta']:.3f},"
              f" t_nw {r['t_nw']:.2f}, p {r['p_nw']:.3f}")
    rows.extend(tmp)
    print("\n  Holm/Bonf: adjusted for the 12 tests in the family only, not for the")
    print("  specification search that came before the freeze (corpus, sample,")
    print("  target and consensus choices were made after seeing results).")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--score", default="consensus",
                    help="'consensus' (mean of available prompts) or one prompt name, e.g. P1_minimal")
    ap.add_argument("--csv", help="write every regression to this CSV")
    ap.add_argument("--extra", action="append", default=[], metavar="LABEL=FILE",
                    help="another score file to run alongside in parts B and C")
    ap.add_argument("--cutoff", action="append", default=[], metavar="LABEL=DATE",
                    help="part H: split an --extra model's regressions at its training cutoff")
    ap.add_argument("--corpus", choices=sorted(CORPUS_DROP), default="policy",
                    help="which statements count (see CORPUS above); default policy")
    ap.add_argument("--dscore", choices=("demeaned", "matched", "raw"), default="demeaned",
                    help="consensus dScore when statements have different prompt sets "
                         "(see dscores()); raw = pre-2026-10-03 behaviour")
    ap.add_argument("--drop-framework", action="store_true",
                    help="leave out the framework announcements " + ", ".join(FRAMEWORK))
    a = ap.parse_args()
    extra = [tuple(e.split("=", 1)) for e in a.extra]
    global DSCORE
    DSCORE = a.dscore

    statements, policy, market = load_market()
    statements, dropped = corpus_filter(statements, a.corpus)
    print(f"\n  --corpus {a.corpus}: {len(statements)} statements"
          + (f"; left out: {', '.join(dropped)}" if dropped else ""))
    if a.drop_framework:
        statements = [d for d in statements if d not in FRAMEWORK]
        print(f"\n  --drop-framework: {', '.join(FRAMEWORK)} left out of parts B-E\n")
    part_a(policy, set(statements))
    rows = []
    post = part_bc(statements, policy, market, a.score, rows, extra)
    part_d(policy, post, rows)
    part_e(statements, policy, market, a.score, rows, extra)
    part_f(statements, policy, market, a.score, rows, extra)
    part_g(statements, policy, market, a.score, extra)
    part_h(statements, policy, market, a.score, extra,
           [tuple(c.split("=", 1)) for c in a.cutoff], rows)
    part_i()
    part_n(statements, policy)
    part_m(statements, a.score, extra)
    part_l()
    part_k(statements, policy, market, a.score, rows)
    part_j(statements, policy, market, a.score, rows)
    part_p(statements, policy, market, a.score, rows,
           a.corpus == "policy" and a.dscore == "demeaned" and a.score == "consensus")
    print("\n" + "=" * 78)
    print("PARSE AUDIT: stored scores dropped (see PARSE_ERRORS)")
    print("=" * 78)
    for path, bad in DROPPED.items():
        for d, p, sc, raw in bad:
            print(f"  {path:<16}{d}  {p:<16}stored {sc:+.2f}  reply {raw[:50]!r}"
                  + ("..." if len(raw) > 50 else ""))
    print("  Replies were stored cut at 300 characters until 2026-10-03, so longer")
    print(f"  ones cannot be re-parsed; they are kept unless listed in PARSE_ERRORS.")
    if a.csv:
        fields = ["part", "model", "y", "sample", "control", "n", "beta", "t_ols",
                  "t_hc1", "t_nw", "p_nw", "p_holm", "nw_lag", "r2", "first", "last"]
        with open(a.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        print(f"\nWrote {len(rows)} regressions to {a.csv}")
    print()


if __name__ == "__main__":
    main()
