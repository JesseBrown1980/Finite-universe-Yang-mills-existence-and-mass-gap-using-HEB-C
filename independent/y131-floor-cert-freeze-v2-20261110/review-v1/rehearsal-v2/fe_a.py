#!/usr/bin/env python3
# floor_eval.py -- evaluator used by final/tools/run_floor.sh (version 2 freeze).
# Integer and exact-rational arithmetic only. Reads logs and certificates, never computes a spectrum.
# Subcommands: rcheck, pins, prereq, step, decide, final.  Arguments are key=value words.
import sys
import re
import os
import hashlib

LIM_KB = 2097152
MIL = 1000000
G0 = (94070673, 1000000)
CAP = (94070936, 1000000)
PRED_NAME = "PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp"
# census pins restated from rows 043 044 045 047 051 055 (checked against the row text by need()).
CENSUS = {
    11: {"orbits": 1608786, "classes": 34920, "weight": 9635688, "edges": 725464,
         "rebuilt": 69840, "moves": 127681200, "conf": 1773350, "rh": "028", "kh": "025"},
    12: {"orbits": 2983071, "classes": 65025, "weight": 17816850, "edges": 1610000,
         "rebuilt": 130050, "moves": 219048552, "conf": 3042341, "rh": "029", "kh": "026"},
    13: {"classes": 89301, "rebuilt": 178602, "kh": "027"},
}
NEED = [("043", ["1608786", "34920", "9635688"]), ("047", ["725464", "1610000"]),
        ("051", ["69840", "130050", "178602"]), ("055", ["127681200", "219048552", "1773350", "3042341"]),
        ("073", ["94070673/1000000"]), ("065", ["94070936/1000000"]), ("007", ["89301"])]
WGATES = ["s3_link_table", "local_delta_vs_full_M", "link_multiset_table", "symmetry_image_rows",
          "core_census_vs_closed_form", "class_detailed_balance"]
VGATES = ["r_policy", "class_bijection", "keys_hash", "positivity_f", "positivity_v", "tail_cap_claim",
          "t_below_tail_cap", "row_check", "row_hash"]


def die(msg):
    print("EVAL_ERROR|" + msg)
    sys.exit(2)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def pow10(n):
    p = 1
    for _ in range(n):
        p = p * 10
    return p


def rat(s):
    s = s.strip()
    if not re.match(r"^[0-9]+([./][0-9]+)?$", s):
        die("not a non-negative rational: " + s)
    if "/" in s:
        a, b = s.split("/")
        if int(b) == 0:
            die("zero denominator: " + s)
        return (int(a), int(b))
    if "." in s:
        a, b = s.split(".")
        return (int(a + b), pow10(len(b)))
    return (int(s), 1)


def lt(a, b):
    return a[0] * b[1] < b[0] * a[1]


def le(a, b):
    return a[0] * b[1] <= b[0] * a[1]


def eq(a, b):
    return a[0] * b[1] == b[0] * a[1]


def add(a, b):
    return (a[0] * b[1] + b[0] * a[1], a[1] * b[1])


def sub(a, b):
    return (a[0] * b[1] - b[0] * a[1], a[1] * b[1])


def rs(a):
    if a is None:
        return "NONE"
    return "%d/%d" % (a[0], a[1])


def rmin(xs):
    m = None
    for x in xs:
        if m is None or lt(x, m):
            m = x
    return m


def rmax(xs):
    m = None
    for x in xs:
        if m is None or lt(m, x):
            m = x
    return m


def lines(path):
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read().split("\n")


def fld(line):
    d = {}
    for w in line.split("|"):
        if "=" in w:
            k, v = w.split("=", 1)
            if k not in d:
                d[k] = v
    return d


def pick(ls, prefix):
    return [x for x in ls if x.startswith(prefix)]


def rows(pred):
    out = {}
    for l in lines(pred):
        m = re.match(r"^([A-Z_]+)\|id=([0-9]{3})\|", l)
        if m:
            out[m.group(2)] = (m.group(1), fld(l), l)
    if not out:
        die("no rows in " + pred)
    return out


def need(R):
    for rid, words in NEED:
        if rid not in R:
            die("row %s missing" % rid)
        for w in words:
            if w not in R[rid][2]:
                die("row %s does not carry %s" % (rid, w))


def args(av):
    d = {}
    for w in av:
        if "=" not in w:
            die("argument without = : " + w)
        k, v = w.split("=", 1)
        d[k] = v
    return d


# ------------------------------------------------------------------ rcheck: test-mode r stays away from 9
def cmd_rcheck(a):
    r = rat(a["r"])
    near = le((8, 1), r) and le(r, (10, 1))
    print("RCHECK|r=%s|within_1_of_9=%d" % (rs(r), 1 if near else 0))
    sys.exit(1 if near else 0)


# ------------------------------------------------------------------ pins: every PIN row that names a path
def cmd_pins(a):
    R = rows(a["pred"])
    need(R)
    root = a["root"]
    bad = 0
    n = 0
    for rid in sorted(R):
        kind, f, _ = R[rid]
        if kind != "PIN" or "path" not in f:
            continue
        n += 1
        p = os.path.join(root, f["path"])
        src = "tree"
        if not os.path.isfile(p) and rid == "034" and a.get("alt034") and os.path.isfile(a["alt034"]):
            p = a["alt034"]
            src = "git_object"
        got = sha(p) if os.path.isfile(p) else "ABSENT"
        ok = 1 if got == f["value"] else 0
        bad += 1 - ok
        print("PINCHECK|id=%s|path=%s|source=%s|want=%s|got=%s|ok=%d" % (rid, f["path"], src, f["value"], got, ok))
    print("PINCHECK_RESULT|tag=%s|prediction_sha256=%s|rows=%d|bad=%d" % (a.get("tag", "1"), sha(a["pred"]), n, bad))
    sys.exit(1 if bad else 0)


# ------------------------------------------------------------------ prereq: row 007 prerequisite (third step)
def cmd_prereq(a):
    m = int(a["m0"])
    lg = a["out"] + "/log"
    R = rows(a["pred"])
    bad = []
    rh = pick(lines(lg + "/m%d_rowhash.txt" % m), "ROWHASH_ONLY|")
    ro = lines(lg + "/m%d_rowsonly.txt" % m)
    vd = pick(ro, "VERDICT|ROWS_ONLY|")
    mem = pick(ro, "MEM|")
    keys = a["out"] + "/RUN%d/core_keys_m%d.bin" % (m, m)
    ks = sha(keys) if os.path.isfile(keys) else "ABSENT"
    if m in CENSUS:
        want = R[CENSUS[m]["kh"]][1]["value"]
        if ks != want:
            bad.append("keys_sha256_differs_from_row_%s" % CENSUS[m]["kh"])
        pin = "row_" + CENSUS[m]["kh"]
    else:
        pin = "NOT_PINNED_AT_THIS_M0"
    if len(rh) != 1 or len(vd) != 1:
        bad.append("rowhash_lines_missing")
    else:
        w = fld(rh[0])
        v = fld(vd[0])
        if w.get("sha256") != v.get("rowhash") or len(w.get("sha256", "")) != 64:
            bad.append("writer_and_verifier_rowhash_differ")
        if w.get("keyshash") != ks or v.get("keyshash") != ks:
            bad.append("keyshash_differs_from_file")
    if len(mem) < 1:
        bad.append("verifier_MEM_line_missing")
    else:
        for x in mem:
            mm = re.match(r"^MEM\|([0-9]+)kB", x)
            if not mm or int(mm.group(1)) >= LIM_KB:
                bad.append("verifier_MEM_not_under_2GB")
    print("PREREQ|m0=%d|keys_sha256=%s|keys_pin=%s|status=%s|bad=%s" % (m, ks, pin, "FAIL" if bad else "PASS", ",".join(bad) or "none"))
    sys.exit(1 if bad else 0)
