#!/usr/bin/env python3
"""
run_all.py - Score the whole corpus, in parallel, safely resumable.

Sequential scoring of 228 statements x 5 prompts would take about 40 minutes.
This runs several requests at once and finishes in a fraction of that. It
writes every score to disk the moment it arrives, so an interruption costs you
nothing: re-run the same command and it picks up exactly where it stopped.

--------------------------------------------------------------------------
RUN IT
--------------------------------------------------------------------------

    cd ~/Desktop/"Quant Project"/fomc-project
    export OPENROUTER_API_KEY="your-key"

    python3 run_all.py --model "anthropic/claude-fable-5.1" --out full_fable.csv

It will show you the job size and estimated cost, then ask you to confirm.

Options:
    --start 2000-01-01      first statement
    --end   2026-12-31      last statement
    --workers 8             parallel requests (lower this if rate-limited)
    --temperature 0.0
    --yes                   skip the confirmation prompt

If it stops for any reason, just run the identical command again.
"""

import argparse
import csv
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

from pilot import PROMPTS, parse_score, get_key

API_URL = "https://openrouter.ai/api/v1/chat/completions"

_lock = threading.Lock()
_done = 0
_failed = 0


def ask_robust(key, model, prompt_text, temperature, tries=5):
    """
    One API call, with retries. Unlike the pilot version this never exits on
    error - a long run must survive a rate limit or a blip without losing
    everything already paid for.
    """
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": temperature,
    }).encode()
    for attempt in range(tries):
        try:
            req = urllib.request.Request(
                API_URL, data=body,
                headers={"Authorization": f"Bearer {key}",
                         "Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=180) as r:
                resp = json.load(r)
            return resp["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            # 429 = rate limited, 5xx = server trouble. Both worth waiting out.
            if e.code in (429, 500, 502, 503, 529) and attempt < tries - 1:
                time.sleep(2 ** attempt + 1)
                continue
            if attempt == tries - 1:
                return None
        except Exception:
            if attempt == tries - 1:
                return None
            time.sleep(2 ** attempt)
    return None


def load_existing(path):
    """Which (date, prompt) pairs do we already have?"""
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
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()

    key = get_key()

    dates = sorted(
        f[:-4] for f in os.listdir("statements")
        if f.endswith(".txt") and args.start <= f[:-4] <= args.end
    )
    texts = {d: open(os.path.join("statements", f"{d}.txt")).read().strip()
             for d in dates}

    have = load_existing(args.out)
    jobs = [(d, p) for d in dates for p in PROMPTS
            if (d, p["name"]) not in have]

    # Rough cost estimate. Statements average ~400 words ~ 550 tokens, plus
    # prompt overhead; output is short except for the reasoning prompt.
    avg_in = sum(len(t.split()) for t in texts.values()) / len(texts) * 1.4 + 120
    est_in = avg_in * len(jobs) / 1e6
    print(f"\nModel:       {args.model}")
    print(f"Statements:  {len(dates)}  ({dates[0]} to {dates[-1]})")
    print(f"Prompts:     {len(PROMPTS)}")
    print(f"Already done:{len(have)}")
    print(f"To run:      {len(jobs)} calls")
    print(f"Est. tokens: ~{est_in:.2f}M in, ~{0.08*len(jobs)/1e3:.2f}M out")
    print(f"Workers:     {args.workers}")

    if not jobs:
        print("\nNothing to do - this run is already complete.")
        return

    if not args.yes:
        if input("\nProceed? [y/N] ").strip().lower() not in ("y", "yes"):
            print("Cancelled.")
            return

    new_file = not os.path.exists(args.out)
    f = open(args.out, "a", newline="")
    w = csv.DictWriter(f, fieldnames=["date", "prompt", "score", "model",
                                      "temperature", "raw_reply"])
    if new_file:
        w.writeheader()
        f.flush()

    total = len(jobs)
    start_t = time.time()

    def work(job):
        global _done, _failed
        date, p = job
        reply = ask_robust(key, args.model,
                           p["text"].format(statement=texts[date]),
                           args.temperature)
        score = parse_score(reply, p["flip"]) if reply else None
        with _lock:
            w.writerow({
                "date": date, "prompt": p["name"], "score": score,
                "model": args.model, "temperature": args.temperature,
                "raw_reply": (reply or "FAILED").replace("\n", " ")[:300],
            })
            f.flush()
            _done += 1
            if score is None:
                _failed += 1
            if _done % 25 == 0 or _done == total:
                el = time.time() - start_t
                rate = _done / el if el else 0
                eta = (total - _done) / rate if rate else 0
                print(f"  {_done}/{total}  ({100*_done/total:.0f}%)  "
                      f"{rate:.1f}/s  eta {eta/60:.1f} min  failed {_failed}")

    print()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(as_completed([ex.submit(work, j) for j in jobs]))
    f.close()

    print(f"\nDone in {(time.time()-start_t)/60:.1f} min. "
          f"{total - _failed} scored, {_failed} failed.")
    if _failed:
        print("Re-run the same command to retry the failures.")
    print(f"Saved to {args.out}")


if __name__ == "__main__":
    main()
