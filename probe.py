#!/usr/bin/env python3
"""
probe.py - Recognition probe: can the model date a blinded FOMC statement?

    python3 probe.py --injected-key --end 2023-12-31 --budget 4
    python3 probe.py --dry-run

Shows the model each statement from statements_blind/ (months, years, names
and named events removed; see blind.py) and asks for the year and month of
the meeting, plus a confidence. If the model dates a blinded statement to the
right meeting, it can recognise it, and could in principle recall the market
reaction rather than read the text. analysis.py part E splits the hold-meeting
regressions by whether each statement was dated correctly.

Caveat: dating needs no memorised statement. Rate levels plus general macro
history ("2 percent objective", "asset purchases", "5-1/4 percent") place many
statements within a year or two. Exact-month dating is the stronger sign of
recognition.

Output (probe_fable.csv): date, guess_year, guess_month, confidence,
err_months (guess minus truth, in months), model, raw_reply, error.
Resumes like score_set.py: dates already answered are skipped.
    --model, --src (default statements_blind), --start/--end, --workers,
    --budget (hard stop in dollars, from the per-call cost OpenRouter returns),
    --sample N (only N evenly spaced statements, e.g. for the paraphrases:
      python3 probe.py --src statements_para --out probe_para.csv --sample 30),
    --dry-run, --injected-key, --max-tokens (default 1000)
"""

import argparse
import csv
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from openrouter import add_api_args, chat, key_from_args

FIELDS = ["date", "guess_year", "guess_month", "confidence", "err_months",
          "model", "raw_reply", "error"]
COST_PER_CALL = 0.012

PROMPT = """Below is a statement released by the Federal Open Market Committee after one
of its meetings{reworded}. Month names, years, member names and named events have been
replaced by placeholders such as [month], [year+1] or [event]; [year+N] means
N years after the year of the meeting itself.

Using anything you know, identify the meeting at which this statement was
released. Give your single best guess even if unsure.

End your reply with exactly one line in this format:
ANSWER: YEAR=YYYY MONTH=MM CONFIDENCE=low|medium|high

Statement:
{statement}"""

ANSWER_RE = re.compile(r"YEAR\s*=\s*(\d{4})\s+MONTH\s*=\s*(\d{1,2})"
                       r"(?:\s+CONFIDENCE\s*=\s*(low|medium|high))?", re.I)


def parse(reply):
    m = None
    for m in ANSWER_RE.finditer(reply or ""):
        pass                                  # keep the last match
    if not m or not 1 <= int(m.group(2)) <= 12:
        return None
    return int(m.group(1)), int(m.group(2)), (m.group(3) or "").lower()


def err_months(date, year, month):
    return (year * 12 + month) - (int(date[:4]) * 12 + int(date[5:7]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="statements_blind")
    ap.add_argument("--out", default="probe_fable.csv")
    ap.add_argument("--model", default="anthropic/claude-fable-5.1")
    ap.add_argument("--start", default="0000")
    ap.add_argument("--end", default="9999")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--budget", type=float, default=5.0)
    ap.add_argument("--sample", type=int, default=0,
                    help="probe only N statements, evenly spaced over the window")
    ap.add_argument("--dry-run", action="store_true")
    add_api_args(ap, max_tokens=1000)
    args = ap.parse_args()

    dates = sorted(f[:-4] for f in os.listdir(args.src)
                   if f.endswith(".txt") and args.start <= f[:-4] <= args.end)
    if args.sample and args.sample < len(dates):
        dates = [dates[i * len(dates) // args.sample] for i in range(args.sample)]
    have = set()
    if os.path.exists(args.out):
        have = {r["date"] for r in csv.DictReader(open(args.out)) if r["guess_year"]}
    todo = [d for d in dates if d not in have]
    print(f"\nSource:   {args.src}   ->   {args.out}")
    print(f"Model:    {args.model}   max_tokens {args.max_tokens}")
    print(f"Window:   {len(dates)} statements, {len(have & set(dates))} already answered")
    print(f"To probe: {len(todo)}  (~${COST_PER_CALL * len(todo):.2f}; "
          f"hard stop at ${args.budget:.2f} spent)")
    if args.dry_run or not todo:
        print("\nDry run - nothing spent.\n" if args.dry_run else "\nNothing to do.\n")
        return

    # the paraphrase probe says the text may be reworded; the blinded probe
    # (probe_fable.csv) was run without that clause
    reworded = "" if os.path.basename(args.src.rstrip("/")) == "statements_blind" \
        else " (it may have been reworded)"
    key = key_from_args(args)
    new = not os.path.exists(args.out)
    f = open(args.out, "a", newline="")
    w = csv.DictWriter(f, fieldnames=FIELDS)
    if new:
        w.writeheader()
        f.flush()
    lock, stop = threading.Lock(), threading.Event()
    stats = {"done": 0, "failed": 0, "cost": 0.0}

    def work(d):
        if stop.is_set():
            return
        text = open(os.path.join(args.src, f"{d}.txt")).read().strip()
        info = {}
        reply, err = chat(key, args.model, PROMPT.format(statement=text, reworded=reworded), 0.0,
                          args.max_tokens, info=info)
        got = parse(reply)
        if reply and not got:
            err = "UNPARSED"
        row = {"date": d, "model": args.model, "error": err or "",
               "raw_reply": (reply or "").replace("\n", " "),
               "guess_year": "", "guess_month": "", "confidence": "", "err_months": ""}
        if got:
            row.update(guess_year=got[0], guess_month=got[1], confidence=got[2],
                       err_months=err_months(d, got[0], got[1]))
        with lock:
            w.writerow(row)
            f.flush()
            stats["done"] += 1
            stats["failed"] += got is None
            stats["cost"] += info.get("cost", 0.0)
            if err and err.startswith("OUT_OF_CREDIT"):
                stop.set()
                print(f"  OUT OF CREDIT - stopping. {err[:150]}")
            if stats["cost"] >= args.budget and not stop.is_set():
                stop.set()
                print(f"  Budget ${args.budget:.2f} reached - stopping.")
            if stats["done"] % 25 == 0:
                print(f"  {stats['done']}/{len(todo)}  failed {stats['failed']}  "
                      f"spent ${stats['cost']:.2f}")

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, todo))
    f.close()
    print(f"\n{stats['done'] - stats['failed']} answered, {stats['failed']} failed in "
          f"{(time.time() - t0) / 60:.1f} min; this run spent ${stats['cost']:.2f}. "
          f"Saved to {args.out}\n")


if __name__ == "__main__":
    main()
