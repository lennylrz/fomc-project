#!/bin/sh
# Rebuild every number, table, figure and the PDF of the paper from the stored
# score files. No API calls. Run from the repository root: sh paper/run_all.sh
set -e
X="--extra clean=clean_fable.csv --extra blind=blind_fable.csv --extra para=para_fable.csv --extra gpt4=gpt4_p1.csv --cutoff gpt4=2021-09-30"
python3 analysis.py $X --csv results.csv > results.txt
mkdir -p paper/runs
python3 analysis.py $X --corpus strict --csv paper/runs/strict.csv > paper/runs/strict.txt
python3 analysis.py $X --corpus all --csv paper/runs/all.csv > paper/runs/all.txt
python3 analysis.py $X --dscore matched --csv paper/runs/matched.csv > paper/runs/matched.txt
python3 analysis.py $X --dscore raw --csv paper/runs/raw.csv > paper/runs/raw.txt
python3 analysis.py $X --score P1_minimal --csv paper/runs/p1.csv > paper/runs/p1.txt
python3 paper/extra_checks.py > /dev/null
python3 paper/make_tables.py
cd paper && latexmk -pdf -interaction=nonstopmode paper.tex > /dev/null && echo "paper/paper.pdf built"
