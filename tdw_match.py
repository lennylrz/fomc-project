#!/usr/bin/env python3
"""
tdw_match.py - Human hawkish/dovish labels for our statements, from the
"Trillion Dollar Words" dataset (Shah, Paturi & Chava 2023, ACL; CC BY-NC
4.0; github.com/gtfintechlab/fomc-hawkish-dovish).

    git clone --depth 1 https://github.com/gtfintechlab/fomc-hawkish-dovish TDW
    python3 tdw_match.py TDW            # -> tdw_labels.csv

Their 2,326 hand-labelled sentences come from FOMC minutes, speeches and
press conferences (label 0 dovish, 1 hawkish, 2 neutral). Minutes repeat the
policy statement, so some labelled sentences appear word for word in our
statements. This keeps every (statement, sentence) match, after lower-casing
and collapsing punctuation, coded hawkish +1 / neutral 0 / dovish -1.
analysis.py part N averages them per statement. Stdlib only (the .xlsx files
are read with zipfile); no API calls.
"""

import csv
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
FILES = ["training_data/test-and-training/training_data/lab-manual-combine-train-5768.xlsx",
         "training_data/test-and-training/test_data/lab-manual-combine-test-5768.xlsx"]
CODE = {"0": -1, "1": 1, "2": 0}


def read_xlsx(path):
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():     # inline strings otherwise
        shared = [("".join(t.text or "" for t in si.iter(NS + "t")))
                  for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(NS + "si")]
    rows = []
    for r in ET.fromstring(z.read("xl/worksheets/sheet1.xml")).iter(NS + "row"):
        row = {}
        for c in r.findall(NS + "c"):
            v = c.find(NS + "v")
            if c.get("t") == "inlineStr":
                val = "".join(x.text or "" for x in c.iter(NS + "t"))
            elif v is None:
                val = None
            else:
                val = shared[int(v.text)] if c.get("t") == "s" else v.text
            row[re.match(r"[A-Z]+", c.get("r")).group()] = val
        rows.append(row)
    return rows


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    labels = {}
    for f in FILES:
        rows = read_xlsx(os.path.join(sys.argv[1], f))
        head = rows[0]
        col = {v: k for k, v in head.items()}
        for r in rows[1:]:
            labels[norm(r[col["sentence"]])] = (r[col["sentence"]], CODE[str(r[col["label"]])])
    out = []
    for name in sorted(os.listdir("statements")):
        text = open(os.path.join("statements", name)).read()
        for s in re.split(r"(?<=[.!?])\s+", text):
            hit = labels.get(norm(s))
            if hit:
                out.append({"date": name[:-4], "label": hit[1], "sentence": hit[0]})
    with open("tdw_labels.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "label", "sentence"])
        w.writeheader()
        w.writerows(out)
    print(f"{len(labels)} labelled sentences; {len(out)} matches in "
          f"{len({r['date'] for r in out})} statements -> tdw_labels.csv")


if __name__ == "__main__":
    main()
