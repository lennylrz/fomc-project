#!/usr/bin/env python3
"""
openrouter.py - The one place that talks to the OpenRouter API. Stdlib only.

Every scorer imports from here, so a fix (retries, error handling, how the key
is supplied) lands in all of them at once.

Key handling
    Normally the key comes from the OPENROUTER_API_KEY environment variable
    and is sent as an Authorization header. Where a proxy injects the
    credential instead (Claude Code on the web), pass --injected-key: no
    header is sent and the proxy adds it.

Replies
    chat() returns (reply_text, error_string); exactly one is None. Errors are
    kept as text so they can go into the CSV. Two are special:
      OUT_OF_CREDIT ...    HTTP 402, stop the run - retrying will not help
      EMPTY_REPLY ...      the model answered with no content. Reasoning models
                           (Fable) can spend the whole max_tokens budget
                           thinking; raise --max-tokens.
      TRUNCATED ...        the reply hit max_tokens part-way (since 2026-10-03;
                           before, such replies were parsed and could give a
                           wrong score); raise --max-tokens.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = "https://openrouter.ai/api/v1"
RETRY_CODES = (429, 500, 502, 503, 529)


def add_api_args(ap, max_tokens=100):
    """The API options every scorer shares."""
    ap.add_argument("--injected-key", action="store_true",
                    help="no OPENROUTER_API_KEY needed: a proxy adds the "
                         "Authorization header (e.g. Claude Code on the web)")
    ap.add_argument("--max-tokens", type=int, default=max_tokens,
                    help=f"reply budget (default {max_tokens}); raise it if rows "
                         "fail with EMPTY_REPLY finish_reason=length")


def get_key(required=True):
    """OPENROUTER_API_KEY from the environment. With required=False, returns
    None when it is unset (proxy-injected credential)."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key and required:
        sys.exit(
            "No API key found.\n"
            "Set it first:  export OPENROUTER_API_KEY=\"your-key\"\n"
            "(PowerShell:   $env:OPENROUTER_API_KEY=\"your-key\")\n"
            "If a proxy injects the key for you, pass --injected-key instead."
        )
    return key or None


def key_from_args(args):
    return get_key(required=not getattr(args, "injected_key", False))


def request(key, path, body=None, timeout=180):
    """GET (body None) or POST JSON to BASE + path. Returns the parsed JSON;
    raises urllib.error.HTTPError and friends to the caller."""
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def chat(key, model, text, temperature=0.0, max_tokens=None, tries=4, info=None):
    """One user message, one reply. Returns (reply_text, error_string).
    max_tokens=None leaves the model's default (OpenRouter then reserves
    credit for the model maximum, which caused the 402s in run_all.py).
    Pass a dict as info to get the call's cost in dollars in info["cost"]
    (the account usage figure lags by minutes, so this is what budgets use)."""
    body = {"model": model,
            "messages": [{"role": "user", "content": text}],
            "temperature": temperature,
            "usage": {"include": True}}
    if max_tokens:
        body["max_tokens"] = max_tokens
    last = "exhausted"
    for attempt in range(tries):
        try:
            resp = request(key, "/chat/completions", body)
            if info is not None:
                info["cost"] = info.get("cost", 0.0) + float(
                    (resp.get("usage") or {}).get("cost") or 0.0)
            if "error" in resp:
                return None, f"body_error: {str(resp['error'])[:200]}"
            ch = resp["choices"][0]
            content = ch["message"].get("content")
            if not content:
                return None, f"EMPTY_REPLY finish_reason={ch.get('finish_reason')}"
            if ch.get("finish_reason") == "length":
                return None, f"TRUNCATED finish_reason=length: ...{content[-80:]}"
            return content, None
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "ignore")[:200]
            if e.code == 402:
                return None, f"OUT_OF_CREDIT: {detail}"
            last = f"HTTP {e.code}: {detail}"
            if e.code in RETRY_CODES and attempt < tries - 1:
                time.sleep(2 ** attempt + 2)
                continue
            return None, last
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:150]}"
            if attempt < tries - 1:
                time.sleep(2 ** attempt)
    return None, last
