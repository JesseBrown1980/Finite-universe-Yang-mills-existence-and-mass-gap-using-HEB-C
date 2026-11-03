#!/usr/bin/env python3
# Every kept output of copy-runs/ against its named rows, through run_cases.py's own masked, wanted_rows and chosen as they now stand, so a change of mask is read on what already ran.
# It names each row holding a field that ends in keys, the form the keys mask once erased. Exits 1 if a kept output differs. usage: recheck_kept_outputs.py   Integer only, json=0.
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import run_cases  # noqa: E402

kept = same = compared = with_keys = 0
for line in open(os.path.join(HERE, "PREDICTION.hbp"), encoding="utf-8"):
    tag, spec = run_cases.fields(line)
    if tag != "EXPECT":
        continue
    path = os.path.join(HERE, "copy-runs", spec["case"] + ".out")
    if not os.path.exists(path):
        print("NOT_KEPT|case=%s|json=0" % spec["case"])
        continue
    kept += 1
    text = open(path, encoding="utf-8", errors="replace", newline="").read().replace("\r", "")
    rows = run_cases.masked(text)
    note = spec.get("note")
    if note:
        rows = [r for r in rows if not r.startswith(note)]
    want = run_cases.chosen(run_cases.wanted_rows(spec, "/nowhere"), spec)
    got = run_cases.chosen(rows, spec)
    compared += len(want)
    ok = bool(want) and got == want
    same += 1 if ok else 0
    fields_ending_in_keys = sum(1 for r in got if re.search(r"\w_keys=", r))
    with_keys += fields_ending_in_keys
    if fields_ending_in_keys or not ok:
        print("KEPT_OUTPUT|case=%s|rows=%d|rows_same=%d|rows_with_a_field_ending_in_keys=%d|json=0" % (spec["case"], len(want), 1 if ok else 0, fields_ending_in_keys))
print("KEPT_OUTPUTS_DONE|kept_outputs=%d|rows_same=%d|rows_compared=%d|rows_with_a_field_ending_in_keys=%d|json=0" % (kept, same, compared, with_keys))
sys.exit(0 if kept and same == kept else 1)
