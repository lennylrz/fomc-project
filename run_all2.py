#!/usr/bin/env python3
"""
run_all2.py - Full-corpus scorer, all five prompts. Replaced run_all.py
(removed; it is in git history), which had two bugs:

BUG 1 (the one that broke the Fable run): max_tokens was never set, so every
request defaulted to the model's maximum output length. OpenRouter reserves
credit for the maximum before accepting a request, so once the balance fell
below that reservation every call was rejected with HTTP 402 - even though the
actual replies are a few tokens long. Now capped: --max-tokens (default 100),
and at least 1000 for P5_reason_first.

BUG 2: failures were written as "FAILED" with the error discarded, so there was
no way to tell a rate limit from an out-of-credit from a bad model name. The
error text now goes into the CSV.

    export OPENROUTER_API_KEY="your-key"
    python3 run_all2.py --model "anthropic/claude-fable-5.1" --out full_fable.csv

Resumes automatically: already-scored cells are skipped, so re-running the same
command only fills gaps. Safe to interrupt.

    --workers 4        parallel requests
    --yes              skip confirmation
    --max-tokens 100   reply budget; raise it if rows fail with EMPTY_REPLY
    --injected-key     no OPENROUTER_API_KEY; a proxy adds the credential
"""

import argparse
import csv
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from openrouter import add_api_args, chat, key_from_args
from pilot import PROMPTS, budget, parse_score

_lock = threading.Lock()
_stats = {"done": 0, "failed": 0}


def load_existing(path):
    if not os.path.exists(path):
        return set()
    have = set()
    with open(path) as f:
        for r in csv.DictReader(f):
            if r.get("score") not in (None, "", "None"):
                have.add((r["date"], r["prompt"]))
    return have


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--start", default="2000-01-01")
    ap.add_argument("--end", default="2026-12-31")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--yes", action="store_true")
    add_api_args(ap)   # P5_reason_first always gets at least 1000
    args = ap.parse_args()

    key = key_from_args(args)
    dates = sorted(f[:-4] for f in os.listdir("statements")
                   if f.endswith(".txt") and args.start <= f[:-4] <= args.end)
    texts = {d: open(os.path.join("statements", f"{d}.txt")).read().strip()
             for d in dates}

    have = load_existing(args.out)
    jobs = [(d, p) for d in dates for p in PROMPTS if (d, p["name"]) not in have]

    print(f"\nModel:        {args.model}")
    print(f"Statements:   {len(dates)}")
    print(f"Already have: {len(have)}")
    print(f"To run:       {len(jobs)} calls")
    if not jobs:
        print("\nComplete - nothing to do.")
        return
    if not args.yes and input("\nProceed? [y/N] ").strip().lower() not in ("y", "yes"):
        return

    new = not os.path.exists(args.out)
    f = open(args.out, "a", newline="")
    cols = ["date", "prompt", "score", "model", "temperature", "raw_reply", "error"]
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
    if new:
        w.writeheader(); f.flush()

    total, t0 = len(jobs), time.time()
    stop = threading.Event()

    def work(job):
        if stop.is_set():
            return
        date, p = job
        reply, err = chat(key, args.model,
                          p["text"].format(statement=texts[date]),
                          args.temperature, budget(p, args.max_tokens), tries=5)
        score = parse_score(reply, p["flip"]) if reply else None
        with _lock:
            w.writerow({"date": date, "prompt": p["name"], "score": score,
                        "model": args.model, "temperature": args.temperature,
                        "raw_reply": (reply or "").replace("\n", " "),
                        "error": err or ""})
            f.flush()
            _stats["done"] += 1
            if score is None:
                _stats["failed"] += 1
                # Out of credit: stop immediately rather than burn through
                # hundreds of doomed requests.
                if err and err.startswith("OUT_OF_CREDIT"):
                    if not stop.is_set():
                        print(f"\n  OUT OF CREDIT - stopping.\n  {err[:180]}")
                    stop.set()
            if _stats["done"] % 25 == 0 or _stats["done"] == total:
                el = time.time() - t0
                rate = _stats["done"] / el if el else 0
                print(f"  {_stats['done']}/{total} ({100*_stats['done']/total:.0f}%)  "
                      f"{rate:.1f}/s  eta {(total-_stats['done'])/rate/60 if rate else 0:.1f}m  "
                      f"failed {_stats['failed']}")

    print()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(as_completed([ex.submit(work, j) for j in jobs]))
    f.close()

    ok = total - _stats["failed"]
    print(f"\n{ok} scored, {_stats['failed']} failed, "
          f"{(time.time()-t0)/60:.1f} min. Saved to {args.out}")
    if _stats["failed"]:
        print("Failure reasons are in the 'error' column. Re-run to retry.")


if __name__ == "__main__":
    main()
