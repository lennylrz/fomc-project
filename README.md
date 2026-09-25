# FOMC statement stance scoring with LLMs

Scores every FOMC post-meeting statement (2000–2026) for hawkish/dovish stance
using LLMs via OpenRouter, with five differently-worded prompts, then asks:

1. **Reliability** – do prompts/models agree (ICC), and does that agreement
   survive when you look at meeting-to-meeting *changes* or strip out the rate
   decision?
2. **Validity** – do score changes line up with market reactions (Bauer-Swanson
   monetary policy surprises, 2y/10y Treasury yield moves)?

## Data
| File | Contents |
|---|---|
| `statements/`, `fomc_statements.csv` | Statement corpus (built by `fetch_fomc.py`) |
| `policy_actions.csv`, `policy_by_statement.csv` | Fed funds target changes by meeting |
| `surprises.csv` | Bauer-Swanson MPS / MPS_ORTH surprises (to 2023-12) |
| `yields.csv` | Daily 2y/10y yields and changes in bp (2003–2026) |
| `grid.csv` | 23 spaced statements x 5 prompts (Gemini) |
| `changes*.csv` | Consecutive 2015–19 (and 2004–07) blocks, per model |
| `full_gemini.csv` | Full corpus, 5 prompts, gemini-2.5-flash |
| `full_fable.csv`, `fable_p1.csv`, `fable_fill.csv` | Full corpus, claude-fable-5.1 (split across runs; `full_fable.csv` contains FAILED rows) |

## Scripts
- `pilot.py` – the five prompts, score parsing, one-statement demo
- `grid.py`, `changes.py` – prompt agreement and levels-vs-changes reliability
- `run_all2.py` – resumable parallel full-corpus scorer (`run_all.py` is the older, buggy version)
- `finish_fable.py` – fill missing statements with a single prompt
- `report.py` – reliability report across score files
- `diagnose.py` – OpenRouter credit / rate-limit diagnostics

## Running
```bash
export OPENROUTER_API_KEY="your-key"
python3 report.py changes.csv changes_frontier.csv
```
