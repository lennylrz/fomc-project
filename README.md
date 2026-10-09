# FOMC statement stance scoring with LLMs

**Paper:** [*Reliable, Recognised, and Hard to Validate: An Audit of LLM Stance Scores for FOMC
Statements*](paper/paper.pdf) (Lenny Lorenz, 2026). Every number in it is rebuilt from the files in
this repository by `sh paper/run_all.sh`, without API calls (see `paper/README.md`).

Scores every FOMC post-meeting statement (2000–2026) for hawkish/dovish stance
using LLMs via OpenRouter, with five differently-worded prompts, then asks:

1. **Reliability** – do prompts/models agree (ICC), and does that agreement
   survive when you look at meeting-to-meeting *changes* or strip out the rate
   decision?
2. **Validity** – do score changes line up with market reactions (Bauer-Swanson
   monetary policy surprises, 2y/10y Treasury yield moves)?

## Corpus definition
The analysis corpus is **every scheduled post-meeting statement plus unscheduled
FOMC policy decisions** (`--corpus policy`, the default in `analysis.py`).
`corpus_types.csv` types each of the 228 files in `statements/` by hand:

| type | n | kept by `policy` |
|---|---|---|
| `scheduled` | 212 | yes |
| `unscheduled_rate` (2001-01-03, 2001-04-18, 2001-09-17, 2008-01-22, 2008-10-08, 2020-03-03, 2020-03-15) | 7 | yes |
| `unscheduled_policy` (2007-08-17 risk statement, 2020-03-23 open-ended purchases) | 2 | yes (`--corpus strict` drops them) |
| `notice` (2007-08-10, 2008-03-11, 2010-05-09, 2019-10-11, 2020-03-31, 2020-08-27, 2025-08-22: liquidity, swap-line, technical and framework notices) | 7 | no |

Notices are removed *before* dScore pairs are formed, so the next statement is
differenced against the previous policy statement. `--corpus all` restores the
pre-2026-10-03 corpus. A statement on a non-trading day (2020-03-15, a Sunday)
takes the next trading day's yield change.

Date fix: the Fed's page for the June 27-28, 2007 statement is `.../20070618a.htm`,
so the URL-derived date was wrong. `fetch_fomc.DATE_FIXES` maps it to 2007-06-28,
and `fix_dates.py` applies the mapping to every file on disk (done 2026-10-03).

## Data
| File | Contents |
|---|---|
| `statements/`, `fomc_statements.csv` | Statement corpus (built by `fetch_fomc.py`; trailing page links stripped 2026-09-25; 2007-06-18 renamed 2007-06-28) |
| `corpus_types.csv` | Hand classification of every statement (see Corpus definition) |
| `statements_blind/`, `blind_log.csv` | Same statements with votes, names, months, years and named events removed (built by `blind.py`) |
| `policy_actions.csv`, `policy_by_statement.csv` | Fed funds target changes by meeting |
| `surprises.csv` | Bauer-Swanson MPS / MPS_ORTH surprises and 30-minute 2y/10y Treasury yield changes TNOTE02/TNOTE10 (percentage points; `analysis.py` uses them x100 as `t2`/`t10` in bp), to 2023-12 |
| `yields.csv` | Daily 2y/10y yields (levels, percent) and close-to-close changes `d2`/`d10` in bp (2003–2026). Source: **FRED DGS2/DGS10** (H.15 constant maturity). Verified 2026-10-08: identical to `fred_DGS2.csv`/`fred_DGS10.csv` (FRED downloads, 2021-10..2026-10) on all 1229 overlapping days. |
| `fred_DGS2.csv`, `fred_DGS10.csv` | FRED downloads used to verify `yields.csv` |
| `tdw_labels.csv` | Human hawkish/dovish sentence labels from Shah, Paturi & Chava (2023), "Trillion Dollar Words" (CC BY-NC 4.0), matched word for word to sentences in our statements (`tdw_match.py`); analysis.py part N |
| `grid.csv` | 23 spaced statements x 5 prompts (Gemini) |
| `changes*.csv` | Consecutive 2015–19 (and 2004–07) blocks, per model |
| `full_gemini.csv` | Full corpus, 5 prompts, gemini-2.5-flash |
| `scores_fable.csv` | Full corpus, claude-fable-5.1, all runs merged (built by `consolidate.py`; use this) |
| `full_fable.csv`, `fable_p1.csv`, `fable_fill.csv` | Raw Fable runs that feed `scores_fable.csv` (`full_fable.csv` contains FAILED rows) |
| `scores_dict.csv` | Word-count stance score, the no-LLM baseline (built by `dictionary.py`) |
| `clean_fable.csv`, `blind_fable.csv` | Fable P1_minimal re-score of the 206 pre-2024 statements, original vs blinded text (`score_set.py`) |
| `statements_para/`, `para_log.csv` | Blinded statements paraphrased by gemini-2.5-flash, with fidelity checks (`paraphrase.py`) |
| `para_fable.csv` | Fable P1_minimal scores of the paraphrases (`score_set.py`) |
| `gpt4_p1.csv` | openai/gpt-4 (training cutoff 2021-09) P1_minimal scores, all 228 statements; analysis.py part H splits at the cutoff |
| `HUMAN_LABELS.md`, `human_labels.csv` | 40 hold-meeting pairs to label by hand (H/S/D); analysis.py part M compares every model with the labels |
| `probe_post.csv` | Dating probe on the blinded 2024-26 statements (Fable's effective cutoff; analysis.py part L) |
| `fable_post5.csv` | Fable, all five prompts, 2025-10-29..2026-07-29 (merged into `scores_fable.csv`; part L) |
| `probe_fable.csv`, `probe_para.csv` | Recognition probe: Fable's guess of the meeting date for each blinded statement / a 30-statement sample of paraphrases (`probe.py`) |

## Data sources and credits
- FOMC statements: Board of Governors of the Federal Reserve System press releases.
- Monetary policy surprises (`surprises.csv`): Bauer, M. D. and Swanson, E. T. (2023), "A Reassessment
  of Monetary Policy Surprises and High-Frequency Identification", *NBER Macroeconomics Annual* 37.
- Treasury yields: FRED series DGS2 and DGS10 (Federal Reserve H.15).
- Human sentence labels (`tdw_labels.csv`): Shah, A., Paturi, S. and Chava, S. (2023), "Trillion
  Dollar Words", ACL 2023, github.com/gtfintechlab/fomc-hawkish-dovish, licensed CC BY-NC 4.0.

## Scripts
- `openrouter.py` – the one OpenRouter client every scorer uses (key handling, retries, `OUT_OF_CREDIT` / `EMPTY_REPLY` errors)
- `pilot.py` – the five prompts, score parsing (strict since 2026-10-03: the reply must end in a number in [-1, 1]), one-statement demo. Scorers store the full reply (before 2026-10-03 replies were cut at 300 characters); `openrouter.chat` returns a `TRUNCATED` error when a reply hits `max_tokens`
- `grid.py`, `changes.py` – prompt agreement and levels-vs-changes reliability
- `run_all2.py` – resumable parallel full-corpus scorer, all five prompts
- `finish_fable.py` – fill missing statements with a single prompt
- `report.py` – reliability report across score files
- `consolidate.py` – merge the Fable runs into `scores_fable.csv` (drops failures, keeps repeat runs tagged by source)
- `analysis.py` – reproduces all results. Defaults: `--corpus policy`, `--dscore demeaned` (consensus dScore with prompt fixed effects; `matched` = common prompts only, `raw` = old), `--score consensus`. Part P states the **frozen primary specification** (MPS on Fable dScore, hold meetings, Newey-West) with Holm/Bonferroni p over Fable's 12 part-B tests; everything else is secondary. Parts: (A) reliability table and the three-way statement x prompt x model variance decomposition; (B) market regressions (MPS, MPS_ORTH, d2, d10 on dScore; hold subsample; OLS/HC1/Newey-West) for Fable, Gemini, the dictionary and any `--extra` file; (C) post-2024 check; (D) power of the post-2024 test; (E) recognition-probe accuracy and the recognised/not split; (F) yields on MPS with and without dScore; (G) paired bootstrap of beta gaps against an `--extra` labelled `clean`. (H) before vs after an `--extra` model's training cutoff (`--cutoff gpt4=2021-09-30`); (I) recognition while scoring: share of stored replies that name the statement's month and year, per file and prompt; (J) Fable vs Gemini joint regression and paired per-sd beta gap; (M) agreement with the human labels; (N) agreement with published human sentence labels; (L) Fable's cutoff from the 2024-26 dating probe and its prompt spread on statements it may not know; (K) placebo days, influence (leave-one-out, greedy drop of 5), GPT-4 coarseness; (P) primary specification and multiple testing; then a parse audit listing stored scores that are dropped. `--drop-framework` is a no-op unless `--corpus all`
- `tdw_match.py` – match the Trillion Dollar Words labelled sentences to our statements (needs a clone of github.com/gtfintechlab/fomc-hawkish-dovish; no API)
- `fix_dates.py` – apply `fetch_fomc.DATE_FIXES` to statement files and every corpus-keyed CSV (idempotent, no API)
- `score_set.py` – score one folder of statements with one prompt into one file (resumable, hard `--budget`)
- `probe.py` – recognition probe: ask the model for the meeting date of each blinded (or paraphrased) statement
- `paraphrase.py` – rewrite each blinded statement with a cheaper model (new wording, levels only as changes), with automatic fidelity checks
- `dictionary.py` – word-count baseline score (no API)
- `blind.py` – build `statements_blind/` for the contamination test (no API)
- `fetch_fomc.py` – build the corpus; `--reclean .` re-applies the text cleaning without fetching
- `diagnose.py` – OpenRouter credit / rate-limit / empty-reply diagnostics

## Running
```bash
python3 consolidate.py          # rebuild scores_fable.csv (no API)
python3 dictionary.py           # rebuild scores_dict.csv (no API)
python3 blind.py                # rebuild statements_blind/ (no API)
python3 analysis.py             # all tables; --score P1_minimal, --csv out.csv,
                                # --corpus all|strict, --dscore matched|raw
python3 analysis.py --extra clean=clean_fable.csv --extra blind=blind_fable.csv \
                    --extra para=para_fable.csv   # contamination tests (parts B, E, F, G)

# Scoring scripts need a key, either
export OPENROUTER_API_KEY="your-key"
python3 finish_fable.py --all-dates --dry-run
# or, where a proxy injects the key (Claude Code on the web), add --injected-key.
# Fable is a reasoning model: if rows fail with EMPTY_REPLY, raise --max-tokens.
```
