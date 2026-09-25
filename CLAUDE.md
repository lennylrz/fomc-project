# Project notes for Claude

See README.md for layout. Status as of 2026-09-25:

- Original thesis (LLM stance reliability collapses for changes / after removing
  the rate decision) holds for cheap models (haiku-3, gpt-4o-mini, gemini-2.5-flash:
  32–45% ICC drop) but not for claude-fable-5.1 (3% drop). That is why the project stalled.
- Live lead, "reliable != valid": Fable meeting-to-meeting score changes predict
  MPS and 2y/10y yield moves on hold meetings (t≈2.2–2.9, R²≈5%); Gemini's do not
  (t≈0) despite 0.95 level correlation. Fragile: fades against MPS_ORTH (t≈1) and
  ~0 correlation on 2024–26 statements (n≈14) → possible training-data contamination.
- No analysis script yet reproduces the regressions; that is the next task
  (consolidate Fable scores into one file, write analysis.py).
- Next: contamination test (post-cutoff statements, date-stripped text),
  dictionary/FinBERT baselines, a second frontier model, Newey-West SEs.

Conventions: API key only via OPENROUTER_API_KEY env var, never in files.
Scripts use stdlib only (urllib/csv); keep it that way for the scorers.
