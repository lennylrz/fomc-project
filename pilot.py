#!/usr/bin/env python3
"""
pilot.py - Score ONE FOMC statement five different ways, three times each.

The point of this script is not to produce results. It is to let you SEE the
problem the whole project is about, with your own eyes, in about two minutes.

You will get 15 numbers back. Every one of them is an answer to the same
question about the same piece of text. If they disagree, you have just
observed the thing your paper is about.

--------------------------------------------------------------------------
SETUP (do this once)
--------------------------------------------------------------------------

1. Put this file next to your unzipped corpus, so the folder looks like:

       fomc-project/
           pilot.py                 <- this file
           statements/              <- from fomc_corpus.zip
           fomc_statements.csv      <- from fomc_corpus.zip

2. Tell your computer your API key. In a terminal, in that folder:

       Mac / Linux:
           export OPENROUTER_API_KEY="paste-your-key-here"

       Windows PowerShell:
           $env:OPENROUTER_API_KEY="paste-your-key-here"

   This lasts until you close the terminal. That is deliberate: the key
   never gets written into a file you might accidentally push to GitHub.

3. Find a model ID that currently works:

       python3 pilot.py --list-models

   That prints the models available to you. Copy one ID.

--------------------------------------------------------------------------
RUN IT
--------------------------------------------------------------------------

       python3 pilot.py --model "openai/gpt-4o-mini"

Optional:
       --date 2013-12-18     which statement to score (default below)
       --runs 3              how many times to repeat each prompt
       --temperature 0.0     0.0 = "be as repeatable as possible"

Cost: roughly one penny.
"""

import argparse
import os
import re
import statistics
import sys

from openrouter import add_api_args, chat, key_from_args, request

# 2013-12-18 is chosen on purpose. At that meeting the Fed announced it would
# start reducing bond purchases (a hawkish action) while simultaneously
# strengthening its promise to keep rates low for a long time (a dovish
# signal). It is genuinely ambiguous, so it is exactly where a scoring
# instrument should struggle. If the AI is going to wobble anywhere, here.
DEFAULT_DATE = "2013-12-18"


# ---------------------------------------------------------------------------
# THE FIVE PROMPTS
#
# These all ask the same question. A human reading any of them would give
# roughly the same answer. That is the whole point: if the AI is a good
# instrument, the wording should not matter.
#
# "flip": prompt 4 deliberately reverses the direction of the scale. We flip
# its answer back in code so all five numbers are comparable. This tests
# whether the model actually reasons about the text, or just pattern-matches
# on where "hawkish" sits in the sentence.
# ---------------------------------------------------------------------------

PROMPTS = [
    {
        "name": "P1_minimal",
        "flip": False,
        "text": (
            "Score the monetary policy stance of the following FOMC statement "
            "on a scale from -1 to +1, where -1 is dovish and +1 is hawkish.\n\n"
            "Reply with only the number.\n\n"
            "STATEMENT:\n{statement}"
        ),
    },
    {
        "name": "P2_defined",
        "flip": False,
        "text": (
            "Below is a statement from the Federal Open Market Committee.\n\n"
            "A hawkish stance leans toward tighter policy and higher interest "
            "rates, typically motivated by concern about inflation. A dovish "
            "stance leans toward looser policy and lower interest rates, "
            "typically motivated by concern about growth and employment.\n\n"
            "Rate the stance on a continuous scale from -1 (maximally dovish) "
            "to +1 (maximally hawkish). Reply with only the number.\n\n"
            "STATEMENT:\n{statement}"
        ),
    },
    {
        "name": "P3_analyst",
        "flip": False,
        "text": (
            "You are a fixed income analyst. Read the FOMC statement below and "
            "tell me how hawkish it is, as a single number between -1 (dovish) "
            "and +1 (hawkish).\n\n"
            "Respond with the number and nothing else.\n\n"
            "STATEMENT:\n{statement}"
        ),
    },
    {
        "name": "P4_reversed",
        "flip": True,  # scale is inverted, we flip the sign afterwards
        "text": (
            "Assess the policy stance expressed in this FOMC statement.\n\n"
            "Use a scale from -1 to +1 where +1 means strongly DOVISH and -1 "
            "means strongly HAWKISH.\n\n"
            "Output only the numeric value.\n\n"
            "STATEMENT:\n{statement}"
        ),
    },
    {
        "name": "P5_reason_first",
        "flip": False,
        "text": (
            "Read the FOMC statement below. Briefly note the main hawkish "
            "elements and the main dovish elements. Then give an overall "
            "stance score from -1 (dovish) to +1 (hawkish).\n\n"
            "End your reply with a line in exactly this format:\n"
            "SCORE: <number>\n\n"
            "STATEMENT:\n{statement}"
        ),
    },
]


def budget(prompt, max_tokens):
    """Reply budget for one prompt: the reasoning prompt needs room to write."""
    return max(max_tokens, 1000) if prompt["name"] == "P5_reason_first" else max_tokens


def list_models(key):
    """Print available model IDs so you never have to guess one."""
    data = request(key, "/models", timeout=60)
    ids = sorted(m["id"] for m in data.get("data", []))
    print(f"{len(ids)} models available. Some good cheap starting points:\n")
    for want in ("gpt", "claude", "gemini", "llama", "mistral", "qwen"):
        hits = [i for i in ids if want in i.lower()][:4]
        for h in hits:
            print("   ", h)
    print("\nFull list: https://openrouter.ai/models")


def ask(key, model, prompt_text, temperature, max_tokens=None):
    """Send one prompt to one model. Return the raw text reply; stop the
    program on any error (grid.py and changes.py rely on this)."""
    reply, err = chat(key, model, prompt_text, temperature, max_tokens)
    if err:
        sys.exit(f"\nAPI error: {err}\n\nTry --list-models.")
    return reply


NUM = r"[+-]?(?:\d+\.\d+|\.\d+|\d+)"


def parse_score(reply, flip):
    """
    Pull the score out of whatever the model said, or return None.

    Models do not always obey "reply with only the number". They say
    "Score: 0.6" or "+0.60" or write three sentences first. So we look for an
    explicit SCORE: line, and otherwise take the number the reply ENDS with.

    Stricter since 2026-10-03 (review m2): the old version took the last
    number anywhere and clipped it to [-1, 1], so a reply cut off after
    "rates unchanged at 1.75%" became 1.0 (and -1.0 after the P4 flip), and a
    truncated "-0." became 0.0. Now a reply that does not end in a number, a
    number with a dangling point ("0."), or a value outside [-1, 1] gives None.
    """
    text = reply.strip()
    m = re.search(r"SCORE:\s*(" + NUM + r")(?![\d.]*\d)", text, re.I)
    if not m:
        m = re.search(r"(?<![\d.])(" + NUM + r")[\s*.)\]]*$", text)
        if m and "." not in m.group(1) and text.endswith(m.group(1) + "."):
            return None        # "0." / "-1." - cut off before the decimals
    if not m:
        return None
    val = float(m.group(1))
    if not -1.0 <= val <= 1.0:
        return None
    return -val if flip else val


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", help="e.g. openai/gpt-4o-mini")
    ap.add_argument("--date", default=DEFAULT_DATE)
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--list-models", action="store_true")
    add_api_args(ap)
    args = ap.parse_args()

    key = key_from_args(args)

    if args.list_models:
        list_models(key)
        return
    if not args.model:
        sys.exit("Pick a model:  python3 pilot.py --model \"openai/gpt-4o-mini\"\n"
                 "See options:   python3 pilot.py --list-models")

    # Load the one statement we are testing.
    path = os.path.join("statements", f"{args.date}.txt")
    if not os.path.exists(path):
        sys.exit(f"Cannot find {path}. Run this from your fomc-project folder.")
    statement = open(path).read().strip()

    print(f"\nStatement:   {args.date}  ({len(statement.split())} words)")
    print(f"Model:       {args.model}")
    print(f"Temperature: {args.temperature}   Runs per prompt: {args.runs}")
    print("-" * 58)

    results = {}
    for p in PROMPTS:
        scores = []
        for _ in range(args.runs):
            reply = ask(
                key,
                args.model,
                p["text"].format(statement=statement),
                args.temperature,
                budget(p, args.max_tokens),
            )
            scores.append(parse_score(reply, p["flip"]))
        results[p["name"]] = scores
        shown = "  ".join(f"{s:+.2f}" if s is not None else " ??? " for s in scores)
        print(f"{p['name']:<16} {shown}")

    # ---- summary ----------------------------------------------------------
    flat = [s for v in results.values() for s in v if s is not None]
    if not flat:
        sys.exit("\nNo scores parsed. Print a raw reply to see what came back.")

    print("-" * 58)
    print(f"All 15 scores range from {min(flat):+.2f} to {max(flat):+.2f}"
          f"   (spread {max(flat) - min(flat):.2f})")

    within = [
        statistics.pstdev(v)
        for v in results.values()
        if len([s for s in v if s is not None]) > 1
    ]
    means = [statistics.mean([s for s in v if s is not None]) for v in results.values()]

    print(f"Same prompt, repeated:      average wobble = {statistics.mean(within):.3f}")
    print(f"Different prompts:          wobble         = {statistics.pstdev(means):.3f}")
    print()
    print("If the second number is much bigger than the first, then HOW YOU ASK")
    print("matters more than random chance. That is the finding this whole")
    print("project is built on.")


if __name__ == "__main__":
    main()
