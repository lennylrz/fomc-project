#!/usr/bin/env python3
"""
diagnose.py - Find out why the Fable run keeps failing.

run_all.py threw away the error messages, which was my mistake. This makes a
handful of calls slowly and prints exactly what comes back, including the
account's credit and rate-limit status.

    python3 diagnose.py --model "anthropic/claude-fable-5.1"

Costs a fraction of a penny. Takes about 20 seconds.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

from pilot import PROMPTS, parse_score, get_key


def show(title):
    print("\n" + "=" * 62)
    print(title)
    print("=" * 62)


def check_key(key):
    """OpenRouter reports credit and rate-limit status on this endpoint."""
    show("1. ACCOUNT STATUS")
    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/key",
            headers={"Authorization": f"Bearer {key}"})
        d = json.load(urllib.request.urlopen(req, timeout=30)).get("data", {})
        for k in ("label", "usage", "limit", "limit_remaining",
                  "is_free_tier", "rate_limit"):
            if k in d:
                print(f"   {k:<18} {d[k]}")
        if d.get("limit") is not None and d.get("limit_remaining") is not None:
            if d["limit_remaining"] <= 0:
                print("\n   >>> CREDIT EXHAUSTED. This is the cause.")
        if d.get("is_free_tier"):
            print("\n   >>> Free tier. Free tiers are heavily rate limited.")
    except Exception as e:
        print(f"   could not read key status: {e}")


def one_call(key, model, text, label):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": text}],
        "temperature": 0.0,
    }).encode()
    t0 = time.time()
    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions", data=body,
            headers={"Authorization": f"Bearer {key}",
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=180) as r:
            resp = json.load(r)
        el = time.time() - t0
        if "error" in resp:
            print(f"   {label:<28} ERROR IN BODY: {str(resp['error'])[:150]}")
            return
        msg = resp["choices"][0]["message"]["content"]
        u = resp.get("usage", {})
        print(f"   {label:<28} OK  {el:4.1f}s  "
              f"in={u.get('prompt_tokens','?')} out={u.get('completion_tokens','?')}  "
              f"reply={msg.strip()[:40]!r}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")[:300]
        print(f"   {label:<28} HTTP {e.code}: {detail}")
    except Exception as e:
        print(f"   {label:<28} {type(e).__name__}: {str(e)[:150]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="anthropic/claude-fable-5.1")
    args = ap.parse_args()
    key = get_key()

    check_key(key)

    # A short early statement and a long recent one, to separate "length"
    # from "the account is out of credit or throttled".
    show("2. SINGLE CALLS, ONE AT A TIME")
    cases = []
    for d in ("2000-02-02", "2014-03-19", "2026-07-29"):
        p = os.path.join("statements", f"{d}.txt")
        if os.path.exists(p):
            t = open(p).read().strip()
            cases.append((d, t, len(t.split())))
    for d, t, w in cases:
        one_call(key, args.model,
                 PROMPTS[0]["text"].format(statement=t), f"{d} ({w} words)")
        time.sleep(2)

    show("3. FOUR CALLS IN QUICK SUCCESSION")
    print("   (if these fail while the ones above succeeded, it is rate limiting)")
    d, t, w = cases[-1]
    for i in range(4):
        one_call(key, args.model,
                 PROMPTS[0]["text"].format(statement=t), f"rapid #{i+1}")

    print("\nPaste all of this back.\n")


if __name__ == "__main__":
    main()
