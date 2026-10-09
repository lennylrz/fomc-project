#!/usr/bin/env python3
"""
diagnose.py - Check the OpenRouter account and a few live calls when a run fails.

Makes a handful of calls slowly and prints exactly what comes back, including
the account's credit and rate-limit status, and flags empty replies (a
reasoning model that used its whole max_tokens budget thinking).

    python3 diagnose.py --model "anthropic/claude-fable-5.1"

Costs a fraction of a penny. Takes about 20 seconds.
"""

import argparse
import os
import time
import urllib.error

from openrouter import add_api_args, key_from_args, request
from pilot import PROMPTS


def show(title):
    print("\n" + "=" * 62)
    print(title)
    print("=" * 62)


def check_key(key):
    """OpenRouter reports credit and rate-limit status on this endpoint."""
    show("1. ACCOUNT STATUS")
    try:
        d = request(key, "/key", timeout=30).get("data", {})
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


def one_call(key, model, text, label, max_tokens):
    body = {"model": model,
            "messages": [{"role": "user", "content": text}],
            "temperature": 0.0,
            "max_tokens": max_tokens}
    t0 = time.time()
    try:
        resp = request(key, "/chat/completions", body)
        el = time.time() - t0
        if "error" in resp:
            print(f"   {label:<28} ERROR IN BODY: {str(resp['error'])[:150]}")
            return
        ch = resp["choices"][0]
        msg = ch["message"].get("content") or ""
        u = resp.get("usage", {})
        status = "OK " if msg else f"EMPTY ({ch.get('finish_reason')})"
        print(f"   {label:<28} {status} {el:4.1f}s  "
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
    add_api_args(ap)
    args = ap.parse_args()
    key = key_from_args(args)

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
                 PROMPTS[0]["text"].format(statement=t), f"{d} ({w} words)", args.max_tokens)
        time.sleep(2)

    show("3. FOUR CALLS IN QUICK SUCCESSION")
    print("   (if these fail while the ones above succeeded, it is rate limiting)")
    d, t, w = cases[-1]
    for i in range(4):
        one_call(key, args.model,
                 PROMPTS[0]["text"].format(statement=t), f"rapid #{i+1}", args.max_tokens)

    print("\nPaste all of this back.\n")


if __name__ == "__main__":
    main()
