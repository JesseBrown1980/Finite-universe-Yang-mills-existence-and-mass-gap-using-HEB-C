#!/usr/bin/env python3
"""
Runs the cases named in a rows file, and compares each case's printed rows with what it must reproduce, clock fields masked.

EXPECT|case=ID|copy=SCRIPT|args=ARGS|against=FILE|exit=N|json=0 runs SCRIPT and compares its standard output with FILE.
  prefixes=A,B  compares only the rows starting with one of these, on both sides.
  segment=K     takes the Kth block of FILE, blocks ending at an exit= line.
  first=N       takes the first N rows of FILE.
  also=GOT WANT also compares these two files byte for byte.
  note=PREFIX   copies the first row starting with PREFIX into the result row, and leaves it out of the comparison.
  hosted=1      marks a case that needs no local binary or store, so CI replays it.
  timeout=SECS  the most it may take, 3600 unless given.
ORIGINAL|case=ID|script=SCRIPT|args=ARGS|json=0 runs an original and keeps its standard output as a baseline.

In a path or argument, $WT is this repository, $P its Perron folder, $RO the second seat's vector review, $R the second seat's
local folder C:/tmp/opus55/ym-two-sided, $HERE this folder and $RUN the run folder given below.

usage: run_cases.py ROWS RUN_DIR LOG KEEP_DIR [CASE ...]     With no CASE, every case. --hosted in place of CASE takes the hosted=1 ones.
Appends one RUN row per case to LOG, keeps each case's output in KEEP_DIR, and exits 1 if any case missed or no case ran. A case with
no rows to compare is a miss. Integer only, json=0.
"""
import hashlib
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
P = os.path.join(WT, "native", "ym", "results", "3x4_stream", "perron")
MASKS = ((re.compile(r"secs_wall=\d+(\.\d+)?"), "secs_wall=MASKED"), (re.compile(r"\bsecs=\d+(\.\d+)?"), "secs=MASKED"), (re.compile(r"\bkeys=[^|]*"), "keys=MASKED"), (re.compile(r"^WROTE[|][^|]*"), "WROTE|MASKED"))


def fields(row):
    parts = row.rstrip("\r\n").split("|")
    return parts[0], dict(p.split("=", 1) for p in parts[1:] if "=" in p)


def expand(text, run_dir):
    for name, value in (("$WT", WT), ("$HERE", HERE), ("$RUN", run_dir), ("$RO", os.path.join(P, "vector", "review-opus55")), ("$P", P), ("$R", "C:/tmp/opus55/ym-two-sided")):
        text = text.replace(name, value.replace("\\", "/"))
    return text


def masked(text):
    rows = []
    for line in text.replace("\r", "").split("\n"):
        for pattern, put in MASKS:
            line = pattern.sub(put, line)
        rows.append(line)
    while rows and not rows[-1]:
        rows.pop()
    return rows


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def wanted_rows(spec, run_dir):
    text = open(expand(spec["against"], run_dir), encoding="utf-8", newline="").read()
    rows = masked(text)
    if "segment" in spec:
        blocks, block = [], []
        for row in rows:
            if row.startswith("exit="):
                blocks.append(block)
                block = []
            else:
                block.append(row)
        rows = blocks[int(spec["segment"]) - 1]
    rows = [r for r in rows if not r.startswith(("EXIT=", "exit="))]
    return rows[:int(spec["first"])] if "first" in spec else rows


def chosen(rows, spec):
    if "prefixes" in spec:
        heads = tuple(spec["prefixes"].split(","))
        return [r for r in rows if r.startswith(heads)]
    return rows


def run_one(tag, spec, run_dir, log, keep_dir):
    case = spec["case"]
    script = expand(spec.get("copy", spec.get("script")), run_dir)
    args = expand(spec.get("args", ""), run_dir).split()
    out_path = os.path.join(run_dir, case + ".out")
    err_path = os.path.join(run_dir, case + ".err")
    os.makedirs(run_dir, exist_ok=True)
    work = os.path.join(run_dir, "cwd-" + case)
    os.makedirs(work, exist_ok=True)
    limit = int(spec.get("timeout", "3600"))
    t0 = time.monotonic_ns()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    with open(out_path, "wb") as out, open(err_path, "wb") as err:
        try:
            code = subprocess.run([sys.executable, "-I", "-B", "-X", "utf8", script] + args, stdout=out, stderr=err, cwd=work, env=env, timeout=limit).returncode
        except subprocess.TimeoutExpired:
            code = "timeout"
    secs = (time.monotonic_ns() - t0) // 10**9
    text = open(out_path, encoding="utf-8", errors="replace", newline="").read().replace("\r", "")
    os.makedirs(keep_dir, exist_ok=True)
    with open(os.path.join(keep_dir, case + ".out"), "w", encoding="utf-8", newline="\n") as kept:
        kept.write(text)
    rel = os.path.relpath(script, WT).replace("\\", "/") if script.startswith(WT.replace("\\", "/")) else script
    row = "RUN|kind=%s|case=%s|script=%s|script_sha256=%s|args=%s|exit=%s|wall_secs=%d|stderr_bytes=%d|rows=%d" % (tag, case, rel, sha(script), spec.get("args", ""), code, secs, os.path.getsize(err_path), len(masked(text)))
    miss = 0
    if tag == "EXPECT":
        rows = masked(text)
        note = spec.get("note")
        if note:
            found = [r for r in rows if r.startswith(note)]
            rows = [r for r in rows if not r.startswith(note)]
            row += "|note=%s" % (found[0].replace("|", ";") if found else "none")
        want = chosen(wanted_rows(spec, run_dir), spec)
        got = chosen(rows, spec)
        same = 1 if want and got == want else 0
        first = next((i + 1 for i, (a, b) in enumerate(zip(got, want)) if a != b), min(len(got), len(want)) + 1) if not same else 0
        exit_ok = 1 if str(code) == spec["exit"] else 0
        row += "|expect_exit=%s|exit_as_predicted=%d|compared_rows=%d|rows_same=%d" % (spec["exit"], exit_ok, len(want), same)
        if first:
            row += "|first_differing_row=%d" % first
        if "also" in spec:
            a, b = expand(spec["also"], run_dir).split()
            bytes_same = 1 if os.path.exists(a) and sha(a) == sha(b) else 0
            row += "|bytes_same=%d|bytes_sha256=%s" % (bytes_same, sha(b))
            miss += 1 - bytes_same
        miss += (1 - same) + (1 - exit_ok)
        row += "|result=%s" % ("MET" if not miss else "MISS")
    row += "|at=%s|json=0" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(row, flush=True)
    with open(log, "a", encoding="utf-8", newline="\n") as f:
        f.write(row + "\n")
    return miss


def main(argv):
    rows_file, run_dir, log, keep_dir = argv[:4]
    names = argv[4:]
    hosted = names == ["--hosted"]
    misses = 0
    ran = 0
    for line in open(rows_file, encoding="utf-8"):
        tag, spec = fields(line)
        if tag not in ("EXPECT", "ORIGINAL") or "case" not in spec:
            continue
        if hosted and spec.get("hosted") != "1":
            continue
        if names and not hosted and spec["case"] not in names:
            continue
        misses += run_one(tag, spec, run_dir, log, keep_dir)
        ran += 1
    print("RUN_CASES_DONE|file=%s|ran=%d|missed=%d|json=0" % (os.path.basename(rows_file), ran, misses), flush=True)
    return 1 if misses or not ran else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
