#!/usr/bin/env python3
"""
score_set.py - Score a folder of statements with one prompt, into one file.

For re-scoring a chosen text version, e.g. the blinded-vs-clean contamination
test:

    python3 score_set.py --src statements_blind --out blind_fable.csv --end 2023-12-31
    python3 score_set.py --src statements       --out clean_fable.csv --end 2023-12-31

    --model        default anthropic/claude-fable-5.1
    --prompt       default P1_minimal
    --start/--end  date window (inclusive)
    --workers      parallel requests (default 4)
    --budget       stop once this run has spent this many dollars (default 10),
                   summed from the cost OpenRouter reports for each call
    --dry-run      show the job and a cost estimate, spend nothing
    plus --injected-key and --max-tokens (default 1000 here: Fable reasons
    before answering, and 100 left 3 of 7 replies empty)

Resumes: dates already scored in --out are skipped, so re-running fills gaps.
Output has the score-file columns plus error, so analysis.py can read it.
"""

import argparse
import csv
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from openrouter import add_api_args, chat, key_from_args
from pilot import PROMPTS, parse_score

FIELDS = ["date", "prompt", "score", "model", "temperature", "raw_reply", "error"]
COST_PER_CALL = 0.012   # estimate for the dry run; Fable P1 costs ~$0.005-0.012


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="anthropic/claude-fable-5.1")
    ap.add_argument("--prompt", default="P1_minimal")
    ap.add_argument("--start", default="0000")
    ap.add_argument("--end", default="9999")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--budget", type=float, default=10.0)
    ap.add_argument("--dry-run", action="store_true")
    add_api_args(ap, max_tokens=1000)
    args = ap.parse_args()

    prompt = next((p for p in PROMPTS if p["name"] == args.prompt), None)
    if prompt is None:
        raise SystemExit(f"No prompt called {args.prompt}.")
    dates = sorted(f[:-4] for f in os.listdir(args.src)
                   if f.endswith(".txt") and args.start <= f[:-4] <= args.end)
    have = set()
    if os.path.exists(args.out):
        for r in csv.DictReader(open(args.out)):
            if r["score"] not in ("", "None") and r["prompt"] == args.prompt:
                have.add(r["date"])
    todo = [d for d in dates if d not in have]

    print(f"\nSource:   {args.src}   ->   {args.out}")
    print(f"Model:    {args.model}   prompt {args.prompt}   max_tokens {args.max_tokens}")
    print(f"Window:   {len(dates)} statements, {len(have & set(dates))} already scored")
    print(f"To score: {len(todo)}  (~${COST_PER_CALL * len(todo):.2f}; "
          f"hard stop at ${args.budget:.2f} spent)")
    if args.dry_run or not todo:
        print("\nDry run - nothing spent.\n" if args.dry_run else "\nNothing to do.\n")
        return

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
        reply, err = chat(key, args.model, prompt["text"].format(statement=text),
                          0.0, args.max_tokens, info=info)
        score = parse_score(reply, prompt["flip"]) if reply else None
        with lock:
            w.writerow({"date": d, "prompt": args.prompt, "score": score,
                        "model": args.model, "temperature": 0.0,
                        "raw_reply": (reply or "").replace("\n", " "),
                        "error": err or ""})
            f.flush()
            stats["done"] += 1
            stats["failed"] += score is None
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
    print(f"\n{stats['done'] - stats['failed']} scored, {stats['failed']} failed in "
          f"{(time.time() - t0) / 60:.1f} min; this run spent "
          f"${stats['cost']:.2f}. Saved to {args.out}\n")


if __name__ == "__main__":
    main()
