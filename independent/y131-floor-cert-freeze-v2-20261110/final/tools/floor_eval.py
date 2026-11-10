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


# ------------------------------------------------------------------ step: every gate of one m0 step
def peak(ls, bad, what):
    pk = pick(ls, "PEAK_RSS|")
    if len(pk) != 1:
        bad.append("row_011:%s_has_%d_PEAK_RSS_lines" % (what, len(pk)))
        return 0
    f = fld(pk[0])
    if f.get("exit") != "0":
        bad.append("row_011:%s_exit_%s" % (what, f.get("exit")))
    kb = int(f.get("kB", "0")) if f.get("kB", "").isdigit() else LIM_KB
    if kb >= LIM_KB:
        bad.append("row_011:%s_PEAK_RSS_not_under_2GB" % what)
    return kb


def gates(ls, names, bad, what):
    seen = {}
    for x in pick(ls, "GATE|"):
        w = x.split("|")
        if len(w) < 3 or w[2] != "PASS":
            bad.append("%s_gate_%s_is_%s" % (what, w[1] if len(w) > 1 else "?", w[2] if len(w) > 2 else "?"))
        else:
            seen[w[1]] = x
    for x in ls:
        if x.startswith("REFUSE|") or x.startswith("VERDICT|REFUSE"):
            bad.append("%s_prints_refusal" % what)
    for nm in names:
        if nm not in seen:
            bad.append("%s_gate_%s_absent" % (what, nm))
    return seen


def count_is(seen, gate, key, want, bad, row):
    if want is None or gate not in seen:
        return
    got = fld(seen[gate]).get(key)
    if got != str(want):
        bad.append("row_%s:%s_%s_is_%s_pin_%d" % (row, gate, key, got, want))


def cmd_step(a):
    m = int(a["m0"])
    r = rat(a["r"])
    out = a["out"]
    lg = out + "/log"
    run = out + "/RUN%d" % m
    mode = a["mode"]
    R = rows(a["pred"])
    need(R)
    C = CENSUS.get(m, {}) if mode == "r9" or a.get("census") == "1" else {}
    bad = []
    crows = []
    fwords = a["fspec"].split(";")
    rh = lines(lg + "/m%d_rowhash.txt" % m)
    ce = lines(lg + "/m%d_cert.txt" % m)
    pk_r = peak(rh, bad, "rowhash")
    pk_c = peak(ce, bad, "cert")
    seen = gates(rh, [], bad, "rowhash")
    seen2 = gates(ce, [], bad, "cert")
    both = dict(seen)
    both.update(seen2)
    for nm in WGATES:
        if nm not in both:
            bad.append("row_055:writer_gate_%s_absent" % nm)
    for s in (seen, seen2):
        count_is(s, "class_detailed_balance", "edges", C.get("edges"), bad, "047")
        count_is(s, "symmetry_image_rows", "rows_rebuilt", C.get("rebuilt"), bad, "051")
        count_is(s, "symmetry_image_rows", "classes", C.get("classes"), bad, "051")
        count_is(s, "local_delta_vs_full_M", "moves_checked", C.get("moves"), bad, "055")
        count_is(s, "link_multiset_table", "configurations_checked", C.get("conf"), bad, "055")
    ro = pick(rh, "ROWHASH_ONLY|")
    rowhash = keyshash = ""
    if len(ro) != 1:
        bad.append("rowhash_step_line_absent")
    else:
        f = fld(ro[0])
        rowhash = f.get("sha256", "")
        keyshash = f.get("keyshash", "")
        if f.get("m0") != str(m) or len(rowhash) != 64 or len(keyshash) != 64:
            bad.append("rowhash_step_line_malformed")
    rh_pin = R[C["rh"]][1]["value"] if "rh" in C else None
    kh_pin = R[C["kh"]][1]["value"] if "kh" in C else None
    if rh_pin and rowhash != rh_pin:
        bad.append("row_%s:rowhash_differs_from_pin" % C["rh"])
    if kh_pin and keyshash != kh_pin:
        bad.append("row_%s:keyshash_differs_from_pin" % C["kh"])
    kf = run + "/core_keys_m%d.bin" % m
    if not os.path.isfile(kf) or sha(kf) != keyshash:
        bad.append("keys_file_sha256_differs_from_KEYSHASH")
    for x in pick(ce, "ROWHASH|"):
        if fld(x).get("sha256") != rowhash:
            bad.append("cert_command_rowhash_differs_from_rowhash_step")
    for x in pick(ce, "KEYSHASH|"):
        if fld(x).get("sha256") != keyshash:
            bad.append("cert_command_keyshash_differs_from_rowhash_step")
    if not pick(ce, "ROWHASH|") or not pick(ce, "KEYSHASH|") or not pick(ce, "KEYS|loaded="):
        bad.append("cert_command_did_not_reuse_the_rowhash_directory")
    for x in pick(ce, "TAIL|"):
        if fld(x).get("gate_observed_ge_layer") != "PASS":
            bad.append("row_050:tail_gate_not_PASS")
    fbsha = a.get("fbsha", "")
    if mode == "r9":
        fz = pick(ce, "FREEZE|")
        if not fz:
            bad.append("row_009:writer_FREEZE_line_absent")
        for x in fz:
            f = fld(x)
            if f.get("commit") != a["commit"] or f.get("prediction_sha256") != a["psha"] or f.get("binary_sha256") != fbsha:
                bad.append("row_018:writer_FREEZE_line_differs")
    # directory content: rowhash files plus the certificates the writer lists (row 001)
    before = set(x for x in lines(lg + "/m%d_dir_after_rowhash.txt" % m) if x)
    wrote = {}
    for x in pick(ce, "WROTE|"):
        w = x.split("|")
        wrote[os.path.basename(w[1])] = fld(x).get("sha256", "")
    now = set(os.listdir(run)) if os.path.isdir(run) else set()
    extra = sorted(now - before - set(wrote))
    if extra:
        bad.append("row_001:directory_holds_%d_files_not_listed_by_WROTE" % len(extra))
    cl = pick(ce, "CERT|")
    if len(cl) != len(fwords) or len(wrote) != len(fwords):
        bad.append("row_002:%d_CERT_lines_%d_WROTE_lines_for_%d_f_words" % (len(cl), len(wrote), len(fwords)))
    vsha_pin = R["019"][1]["value"]
    mem_max = 0
    for i, x in enumerate(cl):
        cb = []
        f = fld(x)
        fw = f.get("f", "")
        if i < len(fwords) and fw != fwords[i]:
            cb.append("row_002:f_word_order")
        base = "cert_m%d_r%d_%d_f%s.txt" % (m, r[0], r[1], fw.replace(",", "-"))
        path = run + "/" + base
        gm = re.match(r"^([0-9]+)/([0-9]+)=", f.get("gamma", ""))
        g_w = (int(gm.group(1)), int(gm.group(2))) if gm else None
        row = {"f": fw, "file": base, "sha": "ABSENT", "gamma": None, "rw": None, "rv": None,
               "cap": f.get("tail_cap", ""), "next": f.get("next_t_refused", ""), "gate": "MISSING"}
        if g_w is None or f.get("row_check") != "PASS" or not f.get("next_t_refused", "").startswith("gate="):
            cb.append("row_046:writer_CERT_line")
        if f.get("r") != "%d/%d" % r or f.get("m0") != str(m) or f.get("rowhash") != rowhash:
            cb.append("writer_CERT_line_r_m0_rowhash")
        if base not in wrote or not os.path.isfile(path):
            cb.append("certificate_file_absent")
        else:
            row["sha"] = sha(path)
            if row["sha"] != wrote[base]:
                cb.append("certificate_sha256_differs_from_WROTE")
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                head = fh.readline().rstrip("\n")
            hd = {}
            for w in head.split(" "):
                if "=" in w:
                    k, v = w.split("=", 1)
                    hd[k] = v
            if hd.get("m0") != str(m) or hd.get("r") != "%d/%d" % r or hd.get("f") != fw:
                cb.append("header_m0_r_f")
            if hd.get("rowhash") != rowhash or hd.get("keyshash") != keyshash:
                cb.append("header_rowhash_keyshash")
            if mode == "r9" and (hd.get("freeze") != a["commit"] or hd.get("pred") != a["psha"]):
                cb.append("row_009:header_freeze_pred")
            g = lines(lg + "/m%d_gate_%s.txt" % (m, base))
            vs = gates(g, VGATES, cb, "verifier")
            gr = pick(g, "GATE_REQUIRED|")
            vd = pick(g, "VERDICT|PASS|")
            if len(gr) != 1 or not gr[0].startswith("GATE_REQUIRED|PASS|") or len(vd) != 1:
                cb.append("row_053:GATE_REQUIRED_not_PASS")
                row["gate"] = "REFUSE" if gr else "MISSING"
            else:
                row["gate"] = "PASS"
                gf = fld(gr[0])
                if gf.get("cert_sha256") != row["sha"] or gf.get("rowhash") != rowhash or gf.get("verifier_sha256") != vsha_pin:
                    cb.append("row_053:GATE_REQUIRED_fields")
                vm = re.match(r"^VERDICT\|PASS\|lambda_min\(QHQ\) >= ([0-9]+)/([0-9]+) at r = ([0-9]+)/([0-9]+) \(m0 = ([0-9]+)\)\|", vd[0])
                if not vm:
                    cb.append("VERDICT_line_unreadable")
                else:
                    g_v = (int(vm.group(1)), int(vm.group(2)))
                    if not eq((int(vm.group(3)), int(vm.group(4))), r) or int(vm.group(5)) != m:
                        cb.append("VERDICT_r_m0")
                    g_h = rat(hd["t"]) if re.match(r"^[0-9]+/[0-9]+$", hd.get("t", "")) else None
                    if g_h is None or g_w is None or not eq(g_v, g_h) or not eq(g_v, g_w):
                        cb.append("row_005:gamma_three_way_mismatch")
                    else:
                        row["gamma"] = g_v
                    if fld(vd[0]).get("min_slack") != f.get("min_slack") or fld(vs.get("row_check", "")).get("min_slack") != f.get("min_slack"):
                        cb.append("row_054:min_slack_differs")
                rz = pick(g, "RITZ_CLASS_VECTOR|")
                if len(rz) == 1 and re.match(r"^[0-9]+\.[0-9]{6}$", rz[0].split("|")[1]) and re.match(r"^[0-9]+\.[0-9]{6}$", f.get("ritz_upper", "")):
                    row["rv"] = rat(rz[0].split("|")[1])
                    row["rw"] = rat(f["ritz_upper"])
                    if row["gamma"] is not None and not le(row["gamma"], add(rmin([row["rv"], row["rw"]]), (1, MIL))):
                        cb.append("row_052:gamma_above_Ritz_upper")
                else:
                    cb.append("row_052:Ritz_lines")
                mems = pick(g, "MEM|")
                if not mems:
                    cb.append("row_011:verifier_MEM_absent")
                for y in mems:
                    mm = re.match(r"^MEM\|([0-9]+)kB", y)
                    kb = int(mm.group(1)) if mm else LIM_KB
                    mem_max = max(mem_max, kb)
                    if kb >= LIM_KB:
                        cb.append("row_011:verifier_MEM_not_under_2GB")
                for y in pick(g, "KEYSHASH|"):
                    if fld(y).get("sha256") != keyshash:
                        cb.append("row_056:verifier_keyshash")
                en = pick(g, "ENUM|")
                if "orbits" in C:
                    ef = fld(en[0]) if en else {}
                    if ef.get("orbits") != str(C["orbits"]) or ef.get("classes") != str(C["classes"]) or ef.get("weight") != str(C["weight"]):
                        cb.append("row_043_044:verifier_ENUM_differs_from_pin")
                if mode == "r9":
                    vf = pick(g, "FREEZE|")
                    ff = fld(vf[0]) if vf else {}
                    if ff.get("commit") != a["commit"] or ff.get("prediction_sha256") != a["psha"] or ff.get("verifier_sha256") != vsha_pin:
                        cb.append("row_009:verifier_FREEZE_line")
        row["bad"] = cb
        bad.extend("f_%s:%s" % (fw.replace(",", "-"), y) for y in cb)
        crows.append(row)
    ok = not bad
    acc = [c for c in crows if ok]
    G = rmax([c["gamma"] for c in acc])
    U = rmin([add(rmin([c["rv"], c["rw"]]), (1, MIL)) for c in acc])
    Uv = rmin([add(c["rv"], (1, MIL)) for c in acc])
    o = ["STEP|m0=%d|status=%s|accepted=%d|certificates=%d|G=%s|U=%s|U_verifier_only=%s|writer_peak_kB=%d|verifier_mem_max_kB=%d|rowhash=%s|keyshash=%s|rowhash_pin=%s|bad=%s|json=0"
         % (m, "OK" if ok else "FAIL", len(acc), len(crows), rs(G), rs(U), rs(Uv), max(pk_r, pk_c), mem_max,
            rowhash or "NONE", keyshash or "NONE", ("row_" + C["rh"]) if "rh" in C else "three_way_equality_only", ";".join(bad) or "none")]
    for c in crows:
        o.append("CERTROW|m0=%d|f=%s|file=%s|sha256=%s|accepted=%d|gate=%s|gamma=%s|ritz_writer=%s|ritz_verifier=%s|tail_cap=%s|next_t_refused=%s|bad=%s|json=0"
                 % (m, c["f"], c["file"], c["sha"], 1 if ok else 0, c["gate"], rs(c["gamma"]), rs(c["rw"]), rs(c["rv"]), c["cap"], c["next"], ";".join(c["bad"]) or "none"))
    for e in extra:
        g = lines(lg + "/m%d_gate_%s.txt" % (m, e))
        gr = pick(g, "GATE_REQUIRED|")
        o.append("CERTROW|m0=%d|f=UNLISTED|file=%s|sha256=%s|accepted=0|gate=%s|gamma=NONE|bad=not_listed_by_WROTE|json=0"
                 % (m, e, sha(run + "/" + e), gr[0].split("|")[1] if gr else "NOT_A_CERTIFICATE"))
    with open(lg + "/m%d_step.hbp" % m, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(o) + "\n")
    print("\n".join(o))
    sys.exit(0 if ok else 1)


# ------------------------------------------------------------------ decide / final
def load_steps(out, steps):
    S = []
    for m in steps:
        ls = lines(out + "/log/m%d_step.hbp" % m)
        st = pick(ls, "STEP|")
        if len(st) != 1:
            die("step file of m0 %d unreadable" % m)
        f = fld(st[0])
        d = {"m": m, "status": f["status"], "G": None, "U": None, "Uv": None, "certs": [], "line": st[0],
             "pk": int(f.get("writer_peak_kB", "0")), "mem": int(f.get("verifier_mem_max_kB", "0"))}
        if f["status"] == "OK":
            d["G"] = rat(f["G"])
            d["U"] = rat(f["U"])
            d["Uv"] = rat(f["U_verifier_only"])
        d["certs"] = [fld(x) for x in pick(ls, "CERTROW|")]
        d["raw"] = [x for x in ls if x]
        S.append(d)
    return S


def state_of(G, U, g0):
    above = G is not None and le(g0, G)
    below = U is not None and lt(U, g0)
    if above and below:
        return "CONTRADICTION"
    if above:
        return "ABOVE"
    if below:
        return "BELOW_FALSIFIED_H4"
    return "UNDECIDED"


def decide(S, g0, allowed):
    ok = [s for s in S if s["status"] == "OK"]
    G = rmax([s["G"] for s in ok])
    U = rmin([s["U"] for s in ok])
    Uv = rmin([s["Uv"] for s in ok])
    last = S[-1]
    more = len(S) < allowed
    n = len(S)
    rule = "row_006" if n == 1 else ("row_007" if n == 2 else "row_007_after_13_stop")
    if any(s["status"] == "FAIL" for s in S):
        return ("FAIL", "STOP", "row_008", G, U, Uv)
    if not ok:
        return ("NO_CERTIFICATE_OPERATIONAL", "ADVANCE" if more else "STOP", rule + "(b)", G, U, Uv)
    st = state_of(G, U, g0)
    sv = state_of(G, Uv, g0)
    if st == "CONTRADICTION" or sv == "CONTRADICTION":
        return ("CONTRADICTION", "STOP", "row_052", G, U, Uv)
    if st != sv:
        return ("HUMAN_READING_NEEDED_U_DEFINITION", "STOP", "header_U(m)", G, U, Uv)
    if last["status"] == "OPFAIL":
        if st == "UNDECIDED" and more:
            return (st, "ADVANCE", rule + "(b)", G, U, Uv)
        return (st, "STOP", rule + "_not_run_if" if st != "UNDECIDED" else rule + "_last_step", G, U, Uv)
    if st == "UNDECIDED" and more:
        return (st, "ADVANCE", rule + "(a)", G, U, Uv)
    return (st, "STOP", (rule + "_not_run_if") if st != "UNDECIDED" else "last_allowed_step", G, U, Uv)


def cmd_decide(a):
    steps = [int(x) for x in a["steps"].split(",")]
    g0 = rat(a["g0"])
    S = load_steps(a["out"], steps)
    st, nxt, rule, G, U, Uv = decide(S, g0, int(a["allowed"]))
    cg = "NONE" if G is None else ("GE" if le(g0, G) else "LT")
    cu = "NONE" if U is None else ("LT" if lt(U, g0) else "GE")
    print("DECISION|after_m0=%d|state=%s|G_max=%s|G_max_vs_g0=%s|g0=%s|U_all=%s|U_all_vs_g0=%s|U_all_verifier_only=%s|inputs=verifier_accepted_certificates_only|next=%s|rule=%s|json=0"
          % (steps[-1], st, rs(G), cg, rs(g0), rs(U), cu, rs(Uv), nxt, rule))
    print("NEXT|" + nxt)


def score(S, g0, G, U):
    """PREDICT rows 058-073 by their met_if words; s1 s2 s3 are the steps in run order."""
    def ok(i):
        return len(S) > i and S[i]["status"] == "OK"

    def b(x):
        return "MET" if x else "NOT_MET"
    P = {}
    s1 = S[0] if ok(0) else None
    s2 = S[1] if ok(1) else None
    s3 = S[2] if ok(2) else None
    allc = [c for s in S if s["status"] == "OK" for c in s["certs"] if c.get("accepted") == "1"]
    gam = [rat(c["gamma"]) for c in allc]
    NV = "NO_GATED_VALUE"
    P["058"] = b(s1 and le((80, 1), s1["G"])) if s1 else "NOT_MET"
    P["059"] = b(le((935000, 10000), s1["G"])) if s1 else NV
    P["060"] = b(le(g0, s1["U"]) and le(s1["U"], (9413, 100))) if s1 else NV
    P["061"] = b(le(sub(s1["U"], s1["G"]), (3, 10))) if s1 else NV
    P["062"] = b(le(sub(s2["U"], s2["G"]), (1, 10))) if s2 else "NOT_EVALUATED"
    P["063"] = b(le(sub(s3["U"], s3["G"]), (1, 20))) if s3 else "NOT_EVALUATED"
    P["064"] = b(le(sub(rmin([U, CAP]), s1["G"]), (3, 10))) if s1 else NV
    P["065"] = b(all(le(x, CAP) for x in gam)) if gam else NV
    P["066"] = b(lt(rmax(gam), g0)) if gam else NV
    if s1 and len(s1["certs"]) >= 3:
        g = [rat(c["gamma"]) for c in s1["certs"] if c.get("accepted") == "1"]
        P["067"] = b(lt(g[0], rmax(g[1:])))
    else:
        P["067"] = NV
    if allc:
        good = True
        for c in allc:
            if c.get("next_t_refused") != "gate=row_check" or not le(rat(c["gamma"]), sub(rat(c["tail_cap"]), (10, 1))):
                good = False
        P["068"] = b(good)
    else:
        P["068"] = NV
    P["069"] = b(le(sub(s1["G"], (1, 1000)), s2["G"])) if (s1 and s2) else "NOT_EVALUATED"
    if s1:
        good = s1["pk"] < 524288 and s1["mem"] < 1048576
        if s2:
            good = good and s2["pk"] < 1048576 and s2["mem"] < 1572864
        P["070"] = b(good)
    else:
        P["070"] = NV
    P["071"] = b(le(G, (9410, 100)) and le((9407, 100), U)) if (G and U) else NV
    P["072"] = "OPEN_BRANCH_" + state_of(G, U, g0) if G else NV
    P["073"] = b(le(g0, U)) if U else NV
    return P


def cmd_final(a):
    out = a["out"]
    steps = [int(x) for x in a["steps"].split(",")] if a.get("steps") else []
    g0 = rat(a["g0"])
    R = rows(a["pred"])
    S = load_steps(out, steps) if steps else []
    stop = a.get("stop", "DECIDED")
    if S:
        st, nxt, rule, G, U, Uv = decide(S, g0, int(a["allowed"]))
    else:
        st, nxt, rule, G, U, Uv = ("NO_STEP", "STOP", "prelude", None, None, None)
    failed = any(s["status"] == "FAIL" for s in S) or st == "CONTRADICTION" or stop.startswith("FAIL")
    opf = [str(s["m"]) for s in S if s["status"] == "OPFAIL"]
    if failed:
        result, comp = "FAIL", "NONE_ROW_008"
        G = U = Uv = None
    elif stop != "DECIDED" or st not in ("ABOVE", "BELOW_FALSIFIED_H4"):
        result, comp = "UNRESOLVED", ("OPEN_" + stop if stop != "DECIDED" else st)
    else:
        result, comp = "PASS", st
    P = score([] if failed else S, g0, G, U) if (S and not failed) else {}
    if not P:
        for k in range(58, 74):
            P["%03d" % k] = "NO_GATED_VALUE"
        P["058"] = "NOT_MET" if S else "NO_GATED_VALUE"
    for rid in P:
        if rid not in R or R[rid][0] != "PREDICT":
            die("row %s is not a PREDICT row" % rid)
    acc = 0 if failed else sum(1 for s in S for c in s["certs"] if c.get("accepted") == "1" and s["status"] == "OK")
    files = []
    for dp, dn, fn in os.walk(out):
        dn.sort()
        if os.path.basename(dp) == "target" or "/target/" in dp + "/":
            dn[:] = []
            continue
        for n in sorted(fn):
            p = os.path.join(dp, n)
            rel = os.path.relpath(p, out)
            if rel == os.path.basename(a["receipt"]) or rel.endswith(".sha256"):
                continue
            files.append((rel, sha(p), os.path.getsize(p)))
    files.sort()
    scope = "FROZEN_R9_RUN" if a["mode"] == "r9" else "REHEARSAL_AT_EXCLUDED_R_NOT_A_SCORE"
    met = ",".join(k for k in sorted(P) if P[k] == "MET") or "none"
    notmet = ",".join(k for k in sorted(P) if P[k] == "NOT_MET") or "none"
    other = ",".join("%s:%s" % (k, P[k]) for k in sorted(P) if P[k] not in ("MET", "NOT_MET")) or "none"
    key = ",".join("%s@%s" % (f[0], f[1]) for f in files)
    fin = ("FLOOR_RUN|result=%s|comparison=%s|scope=%s|r=%s|g0=%s|gamma_cert=%s|U_all=%s|steps_run=%s|steps_ok=%s|operational_failures=%s|accepted_certificates=%d|stop=%s|rule=%s|predict_met=%s|predict_not_met=%s|predict_other=%s|freeze_commit=%s|prediction_sha256=%s|binary_sha256=%s|files=%s|json=0"
           % (result, comp, scope, a["r"], rs(g0), rs(G), rs(U), ",".join(str(s["m"]) for s in S) or "none",
              ",".join(str(s["m"]) for s in S if s["status"] == "OK") or "none", ",".join(opf) or "none", acc, stop, rule,
              met, notmet, other, a.get("commit", "NONE"), sha(a["pred"]), a.get("fbsha", "NONE"), key))
    o = ["# floor run receipt written by final/tools/floor_eval.py; pipe rows; json=0",
         "RECEIPT|scope=%s|r=%s|mode=%s|driver_sha256=%s|evaluator_sha256=%s|json=0" % (scope, a["r"], a["mode"], a.get("drvsha", "NONE"), sha(sys.argv[0]))]
    for s in S:
        o.extend((re.sub(r"\|accepted=[0-9]+\|", "|accepted=0_ROW_008|", x) if failed else x) for x in s["raw"])
        o.append("ACCEPTED|m0=%d|count=%d|json=0" % (s["m"], 0 if failed or s["status"] != "OK" else sum(1 for c in s["certs"] if c.get("accepted") == "1")))
    for x in lines(out + "/log/run.log"):
        if x.startswith("DECISION|") or x.startswith("INVOKE|") or x.startswith("INJECTED|") or x.startswith("NOTE|"):
            o.append(x if x.endswith("json=0") else x + "|json=0")
    for k in sorted(P):
        o.append("PREDICT_SCORE|row=%s|value=%s|outcome=%s|scope=%s|json=0" % (k, R[k][1].get("value", ""), P[k], scope))
    for f in files:
        o.append("FILE|path=%s|sha256=%s|bytes=%d|json=0" % f)
    o.append(fin)
    with open(a["receipt"], "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(o) + "\n")
    with open(a["receipt"] + ".sha256", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("%s  %s\n" % (sha(a["receipt"]), os.path.basename(a["receipt"])))
    print(fin)
    sys.exit(0 if result == "PASS" else (1 if result == "FAIL" else 2))


CMDS = {"rcheck": cmd_rcheck, "pins": cmd_pins, "prereq": cmd_prereq, "step": cmd_step, "decide": cmd_decide, "final": cmd_final}
if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
    die("usage: floor_eval.py rcheck|pins|prereq|step|decide|final key=value ...")
CMDS[sys.argv[1]](args(sys.argv[2:]))
