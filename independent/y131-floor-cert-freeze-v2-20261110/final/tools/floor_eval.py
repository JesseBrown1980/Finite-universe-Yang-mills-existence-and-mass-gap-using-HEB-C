#!/usr/bin/env python3
# floor_eval.py -- evaluator used by final/tools/run_floor.sh (version 2 freeze, third correction round).
# Integer and exact-rational arithmetic only. Reads logs and certificates, never computes a spectrum.
# Subcommands: rcheck, pins, limit, prereq, step, opfail, decide, final.  Arguments are key=value words.
# The final line separates three things: CERTIFICATE (PASS only when every REQUIRED gate, the verifier and the
# closing pin check held and at least one certificate was accepted), DECISION (ABOVE, BELOW or UNRESOLVED, from
# accepted bounds only) and PREDICTION (CONFIRMED for ABOVE, FALSIFIED for BELOW, UNRESOLVED otherwise).
# The launcher reads this file once, hashes those bytes against row 115 and runs them from memory (python3 -I -B -c);
# it does the same with peak_rss.py (row 103) and with its own text (row 114) and hands the three hashes over as
# evsha= peaksha= drvsha=. Its copies of gate_required.sh, cert_gate.py and indep_verify.py sit in a private tmpfs
# (argument tools=DIR). step and final compare the three hashes with rows 115 103 114 and hash the three copies
# against rows 020 019 021; step accepts a certificate only with the launcher's INVOKE record of that verifier call
# (exit 0, log hash, tools at their hashes after the call, argv naming the private gate driver).
# A completed process at or over the memory limit of row 011 gives status FAIL with RESOURCE_LIMIT_EXCEEDED and no
# fallback (rows 122 123): subcommand limit applies that at the third step before the row 007 prerequisite is read,
# subcommand opfail before a crash or a time limit may count as an operational failure, and step to every command
# of a step. limkb=N lowers the limit in test mode only.
# Exit of final: 0 CERTIFICATE=PASS with ABOVE, 3 PASS with BELOW, 2 PASS with UNRESOLVED, 1 every CERTIFICATE=FAIL.
# The receipt names its run directory (RUN_DIRECTORY row); the certificate paths of its RECHECK rows are relative to
# that directory, and its VERDICT_FIELDS row carries the upper bound from the verifier's Ritz values alone, which is
# the value the second-environment checker final/tools/recheck_floor.py (row 131) must reproduce (row 133).
import sys
import re
import os
import hashlib

LIM_KB = 2097152
MIL = 1000000
G0 = (94070673, 1000000)
CAP = (94070936, 1000000)
PRED_NAME = "PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp"
# row 034 names a file of the #137 package outside this folder; a byte copy is carried here and is used when the
# literal path is absent. Either source must hash to the value of row 034.
CARRIED_034 = "final/link/PREDICT-S3-3X4-R9-WILSON-FESHBACH-AMPLITUDE-20261109.hbp"
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
TOOLS = [("020", "gate_required.sh"), ("019", "py/cert_gate.py"), ("021", "py/indep_verify.py")]
MEMTOOLS = [("103", "peaksha", "peak_rss.py"), ("115", "evsha", "floor_eval.py"), ("114", "drvsha", "run_floor.sh")]
RLE = "RESOURCE_LIMIT_EXCEEDED"
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


def tools_check(R, a):
    """The private copies the launcher executes, hashed against the PIN rows, and the hashes of the bytes the
    launcher runs from memory (the peak wrapper, this evaluator, the launcher itself) against theirs."""
    bad = []
    for rid, rel in TOOLS:
        p = os.path.join(a["tools"], rel)
        if rid not in R or not os.path.isfile(p) or sha(p) != R[rid][1].get("value"):
            bad.append("row_%s:private_copy_%s_differs_from_pin" % (rid, rel.replace("/", "_")))
    for rid, key, nm in MEMTOOLS:
        if rid not in R or len(a.get(key, "")) != 64 or a.get(key) != R[rid][1].get("value"):
            bad.append("row_%s:in_memory_%s_differs_from_pin" % (rid, nm))
    return bad


def invocation(lg, m, kind, lb, want_argv):
    """True when the last INVOKE line of run.log for this log names exit 0, no time limit, a process group of its
    own, the tools at their hashes after the call, the hash of the log as it is read here and an argv that starts
    with want_argv."""
    hit = []
    for x in pick(lines(lg + "/run.log"), "INVOKE|"):
        f = fld(x)
        if f.get("m0") == str(m) and f.get("kind") == kind and re.match(r"^log/%s_a[12]\.txt$" % re.escape(lb), f.get("log", "")):
            hit.append((f, x))
    final = lg + "/%s.txt" % lb
    if not hit or not os.path.isfile(final):
        return False
    f, x = hit[-1]
    am = re.search(r"\|argv=(.*)\|json=0$", x)
    return (f.get("rc") == "0" and f.get("time_limit_hit") == "0" and f.get("own_process_group") == "1"
            and f.get("private_tools_after") == "HELD" and f.get("log_sha256") == sha(final) and am is not None
            and (am.group(1) == want_argv or am.group(1).startswith(want_argv + " ")))


# ------------------------------------------------------------------ rcheck: test-mode r stays away from 9
def cmd_rcheck(a):
    r = rat(a["r"])
    near = le((8, 1), r) and le(r, (10, 1))
    print("RCHECK|r=%s|within_1_of_9=%d" % (rs(r), 1 if near else 0))
    sys.exit(1 if near else 0)


# ------------------------------------------------------------------ pins: every PIN row that names a path
def pin_scan(R, root):
    """Hash every PIN row that names a path. Returns the PINCHECK lines, the row count and the count that differ."""
    o = []
    bad = 0
    n = 0
    for rid in sorted(R):
        kind, f, _ = R[rid]
        if kind != "PIN" or "path" not in f:
            continue
        n += 1
        p = os.path.join(root, f["path"])
        src = "tree"
        if not os.path.isfile(p) and rid == "034":
            p = os.path.join(root, CARRIED_034)
            src = "carried_copy_final/link"
        got = sha(p) if os.path.isfile(p) else "ABSENT"
        ok = 1 if got == f["value"] else 0
        bad += 1 - ok
        o.append("PINCHECK|id=%s|path=%s|source=%s|want=%s|got=%s|ok=%d" % (rid, f["path"], src, f["value"], got, ok))
    return o, n, bad


def cmd_pins(a):
    R = rows(a["pred"])
    need(R)
    o, n, bad = pin_scan(R, a["root"])
    print("\n".join(o))
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
                bad.append("verifier_MEM_at_or_over_%dkB" % LIM_KB)
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
    if not f.get("kB", "").isdigit():
        bad.append("row_011:%s_PEAK_RSS_unreadable" % what)
        return 0
    kb = int(f["kB"])
    if kb >= LIM_KB:
        bad.append("row_011:%s:%s_PEAK_RSS_%dkB_limit_%dkB" % (RLE, what, kb, LIM_KB))
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
    # the evaluator hashes the verifier, the gate driver and the peak wrapper itself (rows 019 020 103); the
    # verifier_sha256 printed by the gate driver is compared too, further down, and is not relied on alone
    for rid in ("019", "020", "103"):
        pf = os.path.join(a["root"], R[rid][1]["path"])
        if not os.path.isfile(pf) or sha(pf) != R[rid][1]["value"]:
            bad.append("row_%s:file_on_disk_differs_from_pin" % rid)
    # the copies that were executed (private directory of the launcher), and the launcher's record of each command
    tools = a["tools"]
    bad.extend(tools_check(R, a))
    pkw = "%s -I -B -c MEMORY:peak_rss.py@%s %s/floorcert" % (a["py"], a["peaksha"], tools)
    if not invocation(lg, m, "rowhash", "m%d_rowhash" % m, "%s rowhash --m0 %d" % (pkw, m)):
        bad.append("row_008:no_valid_invocation_record_rowhash")
    if not invocation(lg, m, "cert", "m%d_cert" % m, "%s cert --m0 %d" % (pkw, m)):
        bad.append("row_008:no_valid_invocation_record_cert")
    nrec = 0
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
                # an actual verifier invocation: the launcher's INVOKE record with exit 0 for exactly this log
                if invocation(lg, m, "gate", "m%d_gate_%s" % (m, base), "%s --noprofile --norc %s/gate_required.sh %s" % (a["bash"], tools, path)):
                    nrec += 1
                else:
                    cb.append("row_053:no_valid_verification_record")
                    row["gate"] = "NO_RECORD"
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
                    if not mm:
                        cb.append("row_011:verifier_MEM_unreadable")
                        continue
                    kb = int(mm.group(1))
                    mem_max = max(mem_max, kb)
                    if kb >= LIM_KB:
                        cb.append("row_011:%s:verifier_MEM_%dkB_limit_%dkB" % (RLE, kb, LIM_KB))
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
    res = "EXCEEDED" if any(RLE in y for y in bad) else "HELD"
    o = ["STEP|m0=%d|status=%s|accepted=%d|certificates=%d|G=%s|U=%s|U_verifier_only=%s|writer_peak_kB=%d|verifier_mem_max_kB=%d|resource_limit=%s|limit_kB=%d|verification_records=%d|rowhash=%s|keyshash=%s|rowhash_pin=%s|bad=%s|json=0"
         % (m, "OK" if ok else "FAIL", len(acc), len(crows), rs(G), rs(U), rs(Uv), max(pk_r, pk_c), mem_max, res, LIM_KB, nrec,
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


# ------------------------------------------------------------------ opfail: a crash or a time limit inside a step
def limit_scan(lg, m):
    """Every completed measured process of this step (a writer command with PEAK_RSS exit 0, a verifier that printed
    its verdict) at or over the memory limit, as a list of row 011 words."""
    bad = []
    for nm in sorted(os.listdir(lg)):
        if not re.match(r"^m%d_(rowhash|cert|rowsonly|gate_.*)\.txt$" % m, nm) or re.search(r"_a[12]\.txt$", nm):
            continue
        ls = lines(lg + "/" + nm)
        what = nm[:-4].replace("|", "_")
        for x in pick(ls, "PEAK_RSS|"):
            f = fld(x)
            if f.get("exit") == "0" and f.get("kB", "").isdigit() and int(f["kB"]) >= LIM_KB:
                bad.append("row_011:%s:%s_PEAK_RSS_%skB_limit_%dkB" % (RLE, what, f["kB"], LIM_KB))
        if pick(ls, "VERDICT|"):
            for x in pick(ls, "MEM|"):
                mm = re.match(r"^MEM\|([0-9]+)kB", x)
                if mm and int(mm.group(1)) >= LIM_KB:
                    bad.append("row_011:%s:%s_MEM_%skB_limit_%dkB" % (RLE, what, mm.group(1), LIM_KB))
    return bad


def cmd_limit(a):
    """Third step, after the rowhash and the rows-only verifier and before the row 007 prerequisite is read: a
    completed process at or over the limit makes the step FAIL with RESOURCE_LIMIT_EXCEEDED (row 123)."""
    m = int(a["m0"])
    lg = a["out"] + "/log"
    bad = limit_scan(lg, m)
    if not bad:
        print("LIMIT|m0=%d|status=HELD|limit_kB=%d|checked=completed_rowhash_and_rows_only_verifier_before_the_row_007_prerequisite|json=0" % (m, LIM_KB))
        sys.exit(0)
    st = "STEP|m0=%d|status=FAIL|accepted=0|certificates=0|resource_limit=EXCEEDED|limit_kB=%d|checked=before_the_row_007_prerequisite_is_read|fallback=PROHIBITED|bad=%s|json=0" % (m, LIM_KB, ";".join(bad))
    with open(lg + "/m%d_step.hbp" % m, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(st + "\n")
    print(st)
    sys.exit(1)


def cmd_opfail(a):
    """A command of this step crashed or ran into the time limit. Fallback is open only while no REQUIRED gate has
    failed: a process of this step that completed (exit 0, or a verifier that printed its verdict) at or over the
    memory limit makes the step FAIL with RESOURCE_LIMIT_EXCEEDED, and the run stops."""
    m = int(a["m0"])
    lg = a["out"] + "/log"
    bad = limit_scan(lg, m)
    if bad:
        st = "STEP|m0=%d|status=FAIL|accepted=0|certificates=0|resource_limit=EXCEEDED|limit_kB=%d|operational_event=%s|fallback=PROHIBITED|bad=%s|json=0" % (m, LIM_KB, a["why"], ";".join(bad))
    else:
        st = "STEP|m0=%d|status=OPFAIL|accepted=0|certificates=0|resource_limit=HELD|limit_kB=%d|bad=%s|json=0" % (m, LIM_KB, a["why"])
    with open(lg + "/m%d_step.hbp" % m, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(st + "\n")
    print(st)


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
             "res": f.get("resource_limit", "HELD"),
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


def decision_of(st):
    """Row 012 state word to the three-way decision. G_max >= g0: ABOVE. U_min < g0: BELOW. Otherwise UNRESOLVED."""
    if st == "ABOVE":
        return "ABOVE"
    if st == "BELOW_FALSIFIED_H4":
        return "BELOW"
    return "UNRESOLVED"


PRED_OF = {"ABOVE": "CONFIRMED", "BELOW": "FALSIFIED", "UNRESOLVED": "UNRESOLVED"}


def decide(S, g0, allowed):
    ok = [s for s in S if s["status"] == "OK"]
    G = rmax([s["G"] for s in ok])
    U = rmin([s["U"] for s in ok])
    Uv = rmin([s["Uv"] for s in ok])
    last = S[-1]
    more = len(S) < allowed
    n = len(S)
    rule = "row_006" if n == 1 else ("row_007" if n == 2 else "row_007_after_13_stop")
    if any(s["status"] == "FAIL" and s["res"] == "EXCEEDED" for s in S):
        return ("FAIL", "STOP", "row_011_resource_limit_exceeded_fallback_prohibited_rows_122_123", G, U, Uv)
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
    print("DECISION|after_m0=%d|decision=%s|state=%s|G_max=%s|G_max_vs_g0=%s|g0=%s|U_all=%s|U_all_vs_g0=%s|U_all_verifier_only=%s|inputs=verifier_accepted_certificates_only|next=%s|rule=%s|json=0"
          % (steps[-1], decision_of(st), st, rs(G), cg, rs(g0), rs(U), cu, rs(Uv), nxt, rule))
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
    # closing pin check: every PIN row that names a path, hashed again before anything is printed
    po, pn, pbad = pin_scan(R, a["root"])
    po.append("PINCHECK_RESULT|tag=closing|prediction_sha256=%s|rows=%d|bad=%d" % (sha(a["pred"]), pn, pbad))
    with open(out + "/log/pincheck_closing.txt", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(po) + "\n")
    if pbad:
        stop = "FAIL_closing_pin_check_%d_rows_differ_row_010" % pbad
    tb = tools_check(R, a)
    if tb:
        stop = "FAIL_private_tool_copies_" + "_".join(sorted(set(y.split(":")[0] for y in tb)))
    if S:
        st, nxt, rule, G, U, Uv = decide(S, g0, int(a["allowed"]))
    else:
        st, nxt, rule, G, U, Uv = ("NO_STEP", "STOP", "prelude", None, None, None)
    failed = any(s["status"] == "FAIL" for s in S) or st == "CONTRADICTION" or stop.startswith("FAIL")
    opf = [str(s["m"]) for s in S if s["status"] == "OPFAIL"]
    nacc = 0 if failed else sum(1 for s in S for c in s["certs"] if c.get("accepted") == "1" and s["status"] == "OK")
    if failed:
        # an integrity, REQUIRED-gate or verifier failure: no accepted bound is printed (row 008)
        cert, why, dec = "FAIL", "REQUIRED_OR_INTEGRITY_FAILURE_ROW_008", "UNRESOLVED"
        if any(s["status"] == "FAIL" and s["res"] == "EXCEEDED" for s in S):
            why = RLE
        G = U = Uv = None
    elif nacc == 0 or G is None or U is None:
        cert, why, dec = "FAIL", "NO_ACCEPTED_CERTIFICATE_OPERATIONAL", "UNRESOLVED"
        G = U = Uv = None
    elif stop != "DECIDED":
        cert, why, dec = "PASS", "ACCEPTED_CERTIFICATES_THEN_STOP_" + stop, "UNRESOLVED"
    else:
        cert, why, dec = "PASS", "EVERY_REQUIRED_GATE_AND_THE_CLOSING_PIN_CHECK_HELD", decision_of(st)
    pred = PRED_OF[dec]
    P = score([] if failed else S, g0, G, U) if (S and not failed) else {}
    if not P:
        for k in range(58, 74):
            P["%03d" % k] = "NO_GATED_VALUE"
        P["058"] = "NOT_MET" if S else "NO_GATED_VALUE"
    for rid in P:
        if rid not in R or R[rid][0] != "PREDICT":
            die("row %s is not a PREDICT row" % rid)
    acc = nacc
    files = []
    for dp, dn, fn in os.walk(out):
        dn.sort()
        if dp == out:
            # the build directory of the frozen binary and the launcher's tmpfs mount point stay outside the listing
            dn[:] = [d for d in dn if d not in ("target", "tmp")]
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
    fin = ("FLOOR_RUN|CERTIFICATE=%s|PREDICTION=%s|DECISION=%s|GAMMA=%s|UPPER_BOUND=%s|certificate_reason=%s|prediction_tested=lambda_min(QHQ)_GE_g0|decision_rule=G_max_GE_g0_ABOVE;U_min_LT_g0_BELOW;G_max_LT_g0_LE_U_min_UNRESOLVED|state_row_012=%s|scope=%s|r=%s|g0=%s|steps_run=%s|steps_ok=%s|operational_failures=%s|accepted_certificates=%d|stop=%s|rule=%s|closing_pin_check=rows_%d_bad_%d|private_tools_check=files_%d_bad_%d|predict_met=%s|predict_not_met=%s|predict_other=%s|freeze_commit=%s|prediction_sha256=%s|binary_sha256=%s|HASHES=%s|json=0"
           % (cert, pred, dec, rs(G), rs(U), why, st, scope, a["r"], rs(g0), ",".join(str(s["m"]) for s in S) or "none",
              ",".join(str(s["m"]) for s in S if s["status"] == "OK") or "none", ",".join(opf) or "none", acc, stop, rule, pn, pbad, len(TOOLS) + len(MEMTOOLS), len(tb),
              met, notmet, other, a.get("commit", "NONE"), sha(a["pred"]), a.get("fbsha", "NONE"), key))
    o = ["# floor run receipt written by final/tools/floor_eval.py; pipe rows; json=0",
         "RECEIPT|scope=%s|r=%s|mode=%s|driver_sha256=%s|evaluator_sha256=%s|json=0" % (scope, a["r"], a["mode"], a.get("drvsha", "NONE"), a.get("evsha", "NONE"))]
    for s in S:
        o.extend((re.sub(r"\|accepted=[0-9]+\|", "|accepted=0_ROW_008|", x) if failed else x) for x in s["raw"])
        o.append("ACCEPTED|m0=%d|count=%d|json=0" % (s["m"], 0 if failed or s["status"] != "OK" else sum(1 for c in s["certs"] if c.get("accepted") == "1")))
    for x in lines(out + "/log/run.log"):
        if x.startswith("DECISION|") or x.startswith("INVOKE|") or x.startswith("INJECTED|") or x.startswith("NOTE|") or x.startswith("TOOL"):
            o.append(x if x.endswith("json=0") else x + "|json=0")
    for k in sorted(P):
        o.append("PREDICT_SCORE|row=%s|value=%s|outcome=%s|scope=%s|json=0" % (k, R[k][1].get("value", ""), P[k], scope))
    for f in files:
        o.append("FILE|path=%s|sha256=%s|bytes=%d|json=0" % f)
    # what a second environment needs to recheck this result without relying on the line below (row 125)
    o.append("VERDICT_FIELDS|CERTIFICATE=%s|PREDICTION=%s|DECISION=%s|GAMMA=%s|UPPER_BOUND=%s|UPPER_BOUND_VERIFIER_ONLY=%s|g0=%s|accepted_certificates=%d|r=%s|mode=%s|json=0"
             % (cert, pred, dec, rs(G), rs(U), rs(Uv), rs(g0), acc, a["r"], a["mode"]))
    o.append("RUN_DIRECTORY|path=%s|holds=this_receipt_its_sha256_file_and_the_RUN_folders|certificate_paths_of_the_RECHECK_rows=relative_to_this_directory|json=0"
             % os.path.realpath(out))
    if cert == "PASS":
        extra = ""
        if a["mode"] == "r9":
            extra = " --freeze-commit %s --prediction %s --prediction-sha256 %s" % (a.get("commit", "NONE"), a.get("predrel", "final/" + PRED_NAME), sha(a["pred"]))
        o.append("RECHECK_RULE|rows=125_133|accepted_only_after=a_second_independent_environment_ran_the_checker_of_row_131_on_this_receipt_and_it_ended_RECHECK_VERDICT:ACCEPT=YES|"
                 "where=a_clean_checkout_of_the_freeze_commit,_inside_the_freeze_folder,_with_this_run_directory_copied_whole_(the_receipt,_its_sha256_file_and_the_RUN_folders)|"
                 "command=python3 -I -B final/tools/recheck_floor.py receipt=RUN_DIRECTORY/FLOOR-RUN-RECEIPT.hbp%s|"
                 "certificate_paths=each_RECHECK_row_names_its_certificate_relative_to_the_directory_that_holds_the_receipt_(the_run_directory);_the_checker_refuses_a_missing_file,_a_symbolic_link,_a_path_that_leaves_that_directory_and_a_file_whose_sha256_differs_from_the_row|"
                 "gate_command_per_certificate=bash --noprofile --norc work/design/gate_required.sh RUN_DIRECTORY/CERTIFICATE%s|gate_driver_sha256=%s|verifier_sha256=%s|"
                 "expect=last_line_GATE_REQUIRED_PASS_with_the_cert_sha256_rowhash_and_verifier_sha256_of_the_RECHECK_row,_and_VERDICT_PASS_with_the_gamma_of_the_RECHECK_row|"
                 "then=GAMMA_is_the_largest_gamma_the_checker's_verifier_printed;_the_upper_bound_is_the_smallest_Ritz_value_the_checker's_verifier_printed_plus_1/1000000_and_no_value_of_this_receipt_enters_it;_DECISION_by_the_decision_rule_field_of_the_final_line;_the_three_must_equal_DECISION,_GAMMA_and_UPPER_BOUND_VERIFIER_ONLY_of_the_VERDICT_FIELDS_row;_any_difference_blocks_acceptance|json=0"
                 % ((" commit=%s" % a.get("commit", "NONE")) if a["mode"] == "r9" else "", extra, R["020"][1]["value"], R["019"][1]["value"]))
        for s in S:
            if s["status"] != "OK":
                continue
            rhs = fld(s["line"]).get("rowhash", "NONE")
            for c in s["certs"]:
                if c.get("accepted") == "1":
                    o.append("RECHECK|m0=%d|certificate=RUN%d/%s|relative_to=RUN_DIRECTORY|sha256=%s|gamma=%s|ritz_writer=%s|ritz_verifier=%s|rowhash=%s|verifier_sha256=%s|json=0"
                             % (s["m"], s["m"], c.get("file"), c.get("sha256"), c.get("gamma"), c.get("ritz_writer"), c.get("ritz_verifier"), rhs, R["019"][1]["value"]))
    o.append(fin)
    with open(a["receipt"], "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(o) + "\n")
    with open(a["receipt"] + ".sha256", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("%s  %s\n" % (sha(a["receipt"]), os.path.basename(a["receipt"])))
    print(fin)
    if cert != "PASS":
        sys.exit(1)
    if dec == "ABOVE":
        sys.exit(0)
    if dec == "BELOW":
        sys.exit(3)
    sys.exit(2)


CMDS = {"rcheck": cmd_rcheck, "pins": cmd_pins, "limit": cmd_limit, "prereq": cmd_prereq, "step": cmd_step,
        "opfail": cmd_opfail, "decide": cmd_decide, "final": cmd_final}
if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
    die("usage: floor_eval.py rcheck|pins|limit|prereq|step|opfail|decide|final key=value ...")
ARGS = args(sys.argv[2:])
if "limkb" in ARGS:
    # a lowered memory limit exists for rehearsals only; the frozen run has the limit of row 011 and no other
    if ARGS.get("mode") != "test" or not ARGS["limkb"].isdigit() or not 1 <= int(ARGS["limkb"]) <= LIM_KB:
        die("limkb is a test-mode argument between 1 and %d" % LIM_KB)
    LIM_KB = int(ARGS["limkb"])
CMDS[sys.argv[1]](ARGS)
