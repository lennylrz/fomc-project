# Paper: *Reliable, Recognised, and Hard to Validate*

An audit of LLM stance scores for FOMC statements. `paper.pdf` is the compiled paper.

## Build

From the repository root (no API calls, about two minutes):

```sh
sh paper/run_all.sh
```

This runs `analysis.py` with the default settings (`results.txt`, `results.csv`) and five variants
(`paper/runs/{strict,all,matched,raw,p1}.*`), the exploratory checks (`paper/extra_checks.py` ->
`paper/runs/extra.*`, `scatter.csv`), the table builder (`paper/make_tables.py`), and `latexmk`.

Needs Python 3 (stdlib only) and a TeX Live with `pgfplots`, `booktabs`, `threeparttable`, `natbib`,
`fvextra` and `xurl` (Ubuntu: `texlive-latex-recommended texlive-latex-extra texlive-pictures
texlive-fonts-recommended latexmk`). Without a local TeX, upload `paper/` (including `tables/`,
`figures/`, `sections/` and `refs.bib`) to Overleaf and compile `paper.tex` with pdfLaTeX.

## No hand-typed numbers

`make_tables.py` writes every table (`tables/*.tex`), every figure (`figures/*.tex`, pgfplots) and
`tables/numbers.tex`, which defines `\R{key}` for each number quoted in the text. An unknown key prints
`??key??` in bold. To check a number in the text, find its key in `sections/*.tex` and look it up in
`tables/numbers.tex`; `make_tables.py` shows which output line it was parsed from.

## Files

| File | Contents |
|---|---|
| `paper.tex` | Preamble, abstract, introduction; inputs `sections/*.tex` |
| `sections/data.tex` | Sections 2-3: data and scoring design |
| `sections/reliability.tex` | Section 4 |
| `sections/recognition.tex` | Section 5 |
| `sections/validity.tex` | Section 6 |
| `sections/cannot.tex`, `sections/conclusion.tex` | Sections 7-8 |
| `sections/appendix.tex` | Prompts, corpus, parse audit, extra tables, disclosures, reproduction |
| `refs.bib` | Bibliography, checked by web search on 2026-10-09 |
| `extra_checks.py` | Exploratory robustness checks (subperiods, levels, lags, paraphrase decomposition, hike/cut dummies) |
| `make_tables.py` | Tables, figures, `numbers.tex` |
| `run_all.sh` | Full rebuild |
