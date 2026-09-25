#!/usr/bin/env python3
"""
finish_fable.py - Score ONLY the statements still missing, with ONE prompt.

Why this exists: the full runner scores every statement with all five prompts.
You already have most statements, and Fable's five prompts correlate with their
own average at 0.98-0.996, so for the yield regression a single prompt is
worth the same as all five. This fills the gap and stops.

It reads every *.csv in the folder that looks like a score file, works out
which statements already have a Fable score, and scores only what is absent.

    cd ~/Desktop/"Quant Project"/fomc-project
    export OPENROUTER_API_KEY="your-key"
    python3 finish_fable.py

    --model        default anthropic/claude-fable-5.1
    --prompt       which prompt to use (default P1_minimal)
    --all-dates    include post-2023 statements too (they have no surprise
                   data, so they are excluded by default)
    --dry-run      show what it would do and the cost, without spending

Safe to interrupt and re-run. Stops immediately if credit runs out.
"""

import argparse
import csv
import glob
import json
import os
import time
import urllib.error
import urllib.request

from pilot import PROMPTS, parse_score, get_key

API_URL = "https://openrouter.ai/api/v1/chat/completions"
# Bauer-Swanson surprises end here, so later statements cannot enter the
# main regression.
SURPRISE_END = "2023-12-31"


def existing_fable_dates(model):
    """Any statement with at least one usable score from this model."""
    have = set()
    for path in glob.glob("*.csv"):
        try:
            with open(path) as f:
                rd = csv.DictReader(f)
                if not rd.fieldnames or "score" not in rd.fieldnames:
                    continue
                for r in rd:
                    if (r.get("model") == model
                            and r.get("score") not in (None, "", "None")):
                        have.add(r["date"])
        except Exception:
            continue
    return have


def ask(key, model, text, max_tokens=100, tries=4):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": text}],
        "temperature": 0.0,
        "max_tokens": max_tokens,
    }).encode()
    for attempt in range(tries):
        try:
            req = urllib.request.Request(
                API_URL, data=body,
                headers={"Authorization": f"Bearer {key}",
                         "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=180) as r:
                resp = json.load(r)
            if "error" in resp:
                return None, str(resp["error"])[:200]
            return resp["choices"][0]["message"]["content"], None
        except urllib.error.HTTPError as e:
            d = e.read().decode("utf-8", "ignore")[:200]
            if e.code == 402:
                return None, f"OUT_OF_CREDIT: {d}"
            if e.code in (429, 500, 502, 503, 529) and attempt < tries - 1:
                time.sleep(2 ** attempt + 2)
                continue
            return None, f"HTTP {e.code}: {d}"
        except Exception as e:
            if attempt < tries - 1:
                time.sleep(2 ** attempt)
                continue
            return None, f"{type(e).__name__}: {e}"
    return None, "exhausted"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="anthropic/claude-fable-5.1")
    ap.add_argument("--prompt", default="P1_minimal")
    ap.add_argument("--out", default="fable_fill.csv")
    ap.add_argument("--all-dates", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    prompt = next((p for p in PROMPTS if p["name"] == args.prompt), None)
    if prompt is None:
        raise SystemExit(f"No prompt called {args.prompt}. "
                         f"Options: {[p['name'] for p in PROMPTS]}")

    dates = sorted(f[:-4] for f in os.listdir("statements") if f.endswith(".txt"))
    if not args.all_dates:
        dates = [d for d in dates if d <= SURPRISE_END]

    have = existing_fable_dates(args.model)
    todo = [d for d in dates if d not in have]

    print(f"\nModel:            {args.model}")
    print(f"Prompt:           {args.prompt}")
    print(f"Candidates:       {len(dates)}"
          f"{'' if args.all_dates else '  (to 2023 only; surprises end there)'}")
    print(f"Already scored:   {len(have & set(dates))}")
    print(f"To score now:     {len(todo)} calls  (~${0.02*len(todo):.2f} at "
          f"recent Fable rates)")
    if todo:
        print(f"Range:            {todo[0]} to {todo[-1]}")

    if args.dry_run or not todo:
        print("\nDry run - nothing spent.\n" if args.dry_run else "\nNothing to do.\n")
        return

    key = get_key()
    new = not os.path.exists(args.out)
    f = open(args.out, "a", newline="")
    w = csv.DictWriter(f, fieldnames=["date", "prompt", "score", "model",
                                      "temperature", "raw_reply", "error"])
    if new:
        w.writeheader(); f.flush()

    ok = fail = 0
    print()
    for i, d in enumerate(todo, 1):
        text = open(os.path.join("statements", f"{d}.txt")).read().strip()
        reply, err = ask(key, args.model, prompt["text"].format(statement=text))
        score = parse_score(reply, prompt["flip"]) if reply else None
        w.writerow({"date": d, "prompt": args.prompt, "score": score,
                    "model": args.model, "temperature": 0.0,
                    "raw_reply": (reply or "").replace("\n", " ")[:300],
                    "error": err or ""})
        f.flush()
        if score is None:
            fail += 1
            if err and "OUT_OF_CREDIT" in err:
                print(f"\n  Out of credit at {i}/{len(todo)}. "
                      f"Add a little and re-run - it resumes here.\n")
                break
        else:
            ok += 1
        if i % 10 == 0:
            print(f"  {i}/{len(todo)}   scored {ok}   failed {fail}")
        time.sleep(0.3)
    f.close()
    print(f"\n{ok} scored, {fail} failed. Saved to {args.out}\n")


if __name__ == "__main__":
    main()
