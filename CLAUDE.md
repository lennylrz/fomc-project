# Project notes for Claude

See README.md for layout. Status as of 2026-09-25:

- Original thesis (LLM stance reliability collapses for changes / after removing
  the rate decision) holds for cheap models (haiku-3, gpt-4o-mini, gemini-2.5-flash:
  32–45% ICC drop) but not for claude-fable-5.1 (3% drop). That is why the project stalled.
- Live lead, "reliable != valid": Fable meeting-to-meeting score changes predict
  MPS and 2y/10y yield moves on hold meetings (t≈2.2–2.9, R²≈5%); Gemini's do not
  (t≈0) despite 0.95 level correlation. Fragile: fades against MPS_ORTH (t≈1) and
  ~0 correlation on 2024–26 statements (n≈14) → possible training-data contamination.
- Reproducible now: `consolidate.py` -> `scores_fable.csv`; `analysis.py` prints
  everything (stdlib OLS/HC1/Newey-West). Hold meetings, NW t: MPS 2.41, d2 2.29,
  d10 2.71 (Gemini ≈0); MPS_ORTH 0.82. Effect weaker with P1_minimal only
  (`--score P1_minimal`: MPS 2.20, d2 1.74, d10 1.99). Post-2024: only 10 dScore
  pairs, nothing significant for either model.
- Fable is missing 7 statements from 2024+ (2024-01-31, 2024-05-01, 2024-09-18,
  2025-01-29, 2025-06-18, 2026-06-17, 2026-07-29): score them first
  (`finish_fable.py --all-dates`) before the contamination test.
- Next: contamination test (post-cutoff statements, date-stripped text),
  dictionary/FinBERT baselines, a second frontier model.

Conventions: API key only via OPENROUTER_API_KEY env var, never in files.
Scripts use stdlib only (urllib/csv); keep it that way for the scorers.
