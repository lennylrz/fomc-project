#!/usr/bin/env python3
"""
dictionary.py - A word-count stance score: the no-LLM baseline. No API, stdlib.

    python3 dictionary.py                     # writes scores_dict.csv
    python3 dictionary.py --show 2013-12-18   # print the matches for one statement

Why: if counting words predicts yield moves about as well as Fable, the
finding is "the text carries the signal and Gemini misses it", not "Fable
understands something". A dictionary cannot have memorised market reactions,
so it is also a contamination-free reference point.

Method (in the spirit of Apel & Blix Grimaldi 2012, but a simplified list
written for this project, not their published one): find each TOPIC word and
look for DIRECTION words within WINDOW words on either side, in the same
sentence.
    inflation topics  (inflation, prices, wages, ...)     up = hawkish
    activity topics   (growth, spending, employment, ...) up = hawkish
    slack topics      (unemployment, slack, ...)          up = dovish
    policy topics     (federal funds rate, target, ...)   up = hawkish
Plus a few words that carry stance on their own (accommodative, firming).
score = (hawkish - dovish) / (hawkish + dovish), in [-1, +1]; 0 if no matches.
Vote sentences are skipped. Negation is ignored.

Output uses the score-file format (date, prompt, score, model, ...), so
analysis.py reads it like any model's scores.
"""

import argparse
import csv
import os
import re

OUT = "scores_dict.csv"
MODEL = "dictionary/abg-style-v1"
WINDOW = 5

# (topic, sign of "up", stems). Stems match the start of lower-case tokens.
# Policy uses "target"/"funds", not "rate", which would catch "unemployment rate".
TOPICS = [
    ("inflation", +1, ["inflation", "price", "cost", "wage", "compensation"]),
    ("slack", -1, ["unemployment", "slack", "underutiliz", "joblessness"]),
    ("activity", +1, ["growth", "economy", "activity", "demand", "spending",
                      "investment", "output", "production", "employment", "job",
                      "hiring", "recovery", "expansion", "labor"]),
    ("policy", +1, ["target", "funds"]),
]
UP = ["increas", "rise", "rising", "rose", "risen", "higher", "high", "elevat",
      "strong", "strength", "accelerat", "upward", "heighten", "pick", "solid",
      "robust", "raise", "firm", "tighten", "above"]
DOWN = ["decreas", "declin", "fall", "fell", "lower", "low", "subdued", "moderat",
        "weak", "slow", "downward", "muted", "contain", "eas", "soft", "cut",
        "reduc", "below", "diminish", "damp", "restrain"]
# Words that carry stance without a topic.
STANDALONE = {"accommodat": -1, "stimul": -1, "firming": +1, "tightening": +1,
              "vigilan": +1, "patient": -1}


def starts(tok, stems):
    return any(tok.startswith(s) for s in stems)


def matches(text):
    """Yield (sign, topic_word, direction_word, sentence) for every match."""
    for par in text.split("\n\n"):
        for sent in re.split(r"(?<=[a-z0-9%)][.!?])\s+(?=[A-Z])", par):
            if sent.startswith("Voting"):
                continue
            toks = re.findall(r"[a-z]+", sent.lower())
            for i, t in enumerate(toks):
                for s, stem in STANDALONE.items():
                    if t.startswith(s):
                        yield stem, t, "", sent
                topic = next((tp for tp in TOPICS if starts(t, tp[2])), None)
                if topic is None:
                    continue
                win = toks[max(0, i - WINDOW):i] + toks[i + 1:i + 1 + WINDOW]
                up = sum(starts(w, UP) for w in win)
                down = sum(starts(w, DOWN) for w in win)
                if up != down:
                    d = 1 if up > down else -1
                    word = next(w for w in win if starts(w, UP if d > 0 else DOWN))
                    yield topic[1] * d, t, word, sent


def score(text):
    h = d = 0
    for s, *_ in matches(text):
        h += s > 0
        d += s < 0
    return ((h - d) / (h + d) if h + d else 0.0), h, d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="statements", help="statement folder")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--show", metavar="DATE")
    a = ap.parse_args()

    if a.show:
        text = open(os.path.join(a.src, f"{a.show}.txt")).read()
        for s, t, w, _ in matches(text):
            print(f"  {'+' if s > 0 else '-'}  {t:<16} {w}")
        print("  score = %.3f  (hawkish %d, dovish %d)" % score(text))
        return

    dates = sorted(f[:-4] for f in os.listdir(a.src) if f.endswith(".txt"))
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "prompt", "score", "model",
                                          "temperature", "raw_reply"])
        w.writeheader()
        for d in dates:
            sc, h, dv = score(open(os.path.join(a.src, f"{d}.txt")).read())
            w.writerow({"date": d, "prompt": "DICT", "score": round(sc, 4),
                        "model": MODEL, "temperature": "",
                        "raw_reply": f"hawkish={h} dovish={dv}"})
    print(f"Wrote {len(dates)} dictionary scores to {a.out}")


if __name__ == "__main__":
    main()
