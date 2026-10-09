#!/usr/bin/env python3
"""
paraphrase.py - Rewrite each blinded statement in new words, for the
contamination test. A different, cheaper model does the rewriting.

    python3 paraphrase.py --injected-key --end 2023-12-31 --budget 1
    python3 paraphrase.py --show 2013-12-18      # original vs paraphrase

Input statements_blind/ (blind.py), output statements_para/<date>.txt and
para_log.csv (date, model, words in/out, share of the paraphrase's 4-word
sequences that also occur in the blinded original, digits left, error).

The rewrite keeps the economic content (decision, direction and size of any
change, assessment of growth / labour market / inflation, risks, forward
guidance, dissents and their direction) and removes what lets a model look
the statement up: the wording and sentence order, and absolute levels of the
policy rate and of asset purchases (changes are kept: "raised the target by
a quarter point", "left the rate unchanged").

Resumes: dates with a file in statements_para/ are skipped.
"""

import argparse
import csv
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor

from openrouter import add_api_args, chat, key_from_args

SRC, OUT, LOG = "statements_blind", "statements_para", "para_log.csv"
FIELDS = ["date", "model", "change_bp", "words_in", "words_out", "overlap4", "digits",
          "flags", "tries", "error"]

PROMPT = """Rewrite the following central bank policy statement so that a reader who
knows the original by heart could not recognise it, while an economist would
draw exactly the same conclusions from it.

Rules:
- Keep ALL of the economic content: the policy decision, the direction and
  size of any change, the assessment of growth, the labour market, inflation
  and financial conditions, the balance of risks, any guidance about future
  policy (including numerical thresholds in that guidance), and any dissents
  with the direction the dissenter preferred.
- Change the structure: start with the decision, then the economic
  assessment, then the outlook and risks, then guidance, then dissents. Write
  in plain prose in your own words, as different central bank staff would.
  Do not reuse any phrase of four or more words from the original, and do
  not follow its sentence order.
- Do NOT state absolute levels of the policy interest rate, its target range,
  the discount rate, or the size of asset holdings or purchase programmes.
  State them only relative to the previous meeting: "raised its policy rate
  by a quarter of a percentage point", "kept its policy rate unchanged",
  "cut the monthly pace of its Treasury and mortgage bond purchases by $5
  billion each". The 2 percent inflation objective may be kept.
- Keep placeholders such as [month], [year+1], [member], [event] as they are,
  and do not add any dates, names or events.
- Add NOTHING that is not in the original. If the original says nothing about
  the labour market, inflation, risks, guidance or dissents, neither do you;
  do not mention a 2 percent objective unless the original does. A short
  original gives a short rewrite.
- Do not add interpretation, commentary or a hawkish/dovish label; do not
  make the tone stronger or weaker than the original.
- About two thirds of the original length. Output only the rewritten text.

Fact to use for the decision (from the official record, do not contradict
it): {decision}

Statement:
{statement}"""


def decision(bp):
    if bp == 0:
        return "the federal funds rate target was left unchanged at this meeting."
    word = "raised" if bp > 0 else "lowered"
    return (f"the federal funds rate target was {word} by {abs(bp)} basis points "
            f"({abs(bp) / 100:g} percentage point) at this meeting.")


KEEP = {"2 percent", "2-1/2 percent", "6-1/2 percent"}
LEVEL_RE = re.compile(r"\b(\d+(-\d/\d)?|\d\.\d+)( to \d+(-\d/\d)?)? percent\b")


def problems(orig, para):
    """Automatic fidelity checks; an empty list means none found."""
    out = []
    lo, lp = orig.lower(), para.lower()
    if len(para.split()) > 1.2 * len(orig.split()) + 10:
        out.append("longer")
    if any(w in lp for w in ("dissent", "preferred", "opposed", "voted against")) and \
            not any(w in lo for w in ("dissent", "preferred", "voting against", "opposed")):
        out.append("added_dissent")
    if "2 percent" in lp and "2 percent" not in lo:
        out.append("added_2pct")
    # any "N percent" other than the inflation objective and the 2012-14
    # guidance thresholds (6-1/2 unemployment, 2-1/2 projected inflation)
    lv = sorted({m.group(0) for m in LEVEL_RE.finditer(para)} - KEEP)
    if lv:
        out.append("level:" + "|".join(lv).replace(" ", "_"))
    return out


def ngrams(text, n=4):
    w = re.findall(r"[a-z]+", text.lower())
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def overlap(orig, para):
    p = ngrams(para)
    return len(p & ngrams(orig)) / len(p) if p else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="google/gemini-2.5-flash")
    ap.add_argument("--start", default="0000")
    ap.add_argument("--end", default="9999")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--budget", type=float, default=1.0)
    ap.add_argument("--show", metavar="DATE")
    add_api_args(ap, max_tokens=6000)
    args = ap.parse_args()

    if args.show:
        for d in (SRC, OUT):
            print(f"\n--- {d}/{args.show}.txt ---\n")
            print(open(os.path.join(d, f"{args.show}.txt")).read())
        return

    policy = {r["date"]: int(r["change_bp"]) for r in csv.DictReader(open("policy_by_statement.csv"))}
    os.makedirs(OUT, exist_ok=True)
    dates = sorted(f[:-4] for f in os.listdir(SRC)
                   if f.endswith(".txt") and args.start <= f[:-4] <= args.end)
    todo = [d for d in dates if not os.path.exists(os.path.join(OUT, f"{d}.txt"))]
    print(f"\n{len(dates)} statements, {len(todo)} to paraphrase with {args.model}")
    if not todo:
        return
    key = key_from_args(args)
    new = not os.path.exists(LOG)
    f = open(LOG, "a", newline="")
    w = csv.DictWriter(f, fieldnames=FIELDS)
    if new:
        w.writeheader()
    lock = threading.Lock()
    stats = {"done": 0, "cost": 0.0}

    def work(d):
        if stats["cost"] >= args.budget:
            return
        orig = open(os.path.join(SRC, f"{d}.txt")).read().strip()
        info, flags = {}, []
        text = PROMPT.format(statement=orig, decision=decision(policy[d]))
        for tries in (1, 2):                  # one retry, warmer, if a check fails
            reply, err = chat(key, args.model, text, 0.0 if tries == 1 else 0.7,
                              args.max_tokens, info=info)
            flags = problems(orig, reply) if reply else []
            if reply and not flags:
                break
        row = {"date": d, "model": args.model, "change_bp": policy[d], "tries": tries,
               "words_in": len(orig.split()), "flags": " ".join(flags), "error": err or ""}
        if reply:
            reply = reply.strip()
            with open(os.path.join(OUT, f"{d}.txt"), "w") as g:
                g.write(reply + "\n")
            row.update(words_out=len(reply.split()), overlap4=f"{overlap(orig, reply):.3f}",
                       digits=" ".join(re.findall(r"\d[\d,./-]*", reply)))
        with lock:
            w.writerow(row)
            f.flush()
            stats["done"] += 1
            stats["cost"] += info.get("cost", 0.0)
            if stats["done"] % 25 == 0:
                print(f"  {stats['done']}/{len(todo)}  spent ${stats['cost']:.3f}")

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, todo))
    f.close()
    print(f"\n{stats['done']} done, spent ${stats['cost']:.3f}. Log: {LOG}\n")


if __name__ == "__main__":
    main()
