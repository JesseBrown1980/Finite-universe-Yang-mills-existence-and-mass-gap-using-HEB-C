#!/usr/bin/env python3
# recheck_floor.py -- second-environment checker of a floor run receipt (rows 125, 131 and 133 of the prediction record).
# Integer and exact-rational arithmetic only. It computes no spectrum: it runs the pinned gate driver on certificates.
#
#   python3 -I -B final/tools/recheck_floor.py receipt=RUN_DIRECTORY/FLOOR-RUN-RECEIPT.hbp [commit=C] [out=FILE]
#
# Run it inside the freeze folder of a clean checkout of the freeze commit, in an environment other than the one that
# launched the run. RUN_DIRECTORY is the directory that holds the receipt, copied whole (the receipt, its .sha256 file
# and the RUN folders). commit=C (40 hex) is required for a receipt of the frozen r = 9 run and is given by the person
# who runs this checker; it is compared with the receipt and handed to the verifier.
#
# What it does, in this order:
#  1. hashes the record, gate_required.sh, cert_gate.py, indep_verify.py and this file in the checkout against the
#     PIN rows 020 019 021 131 of the checkout's own record, and the record against the receipt;
#  2. hashes the receipt against its .sha256 file;
#  3. for every RECHECK row: takes the certificate path relative to the directory that holds the receipt; refuses a
#     path of another shape, a path that leaves that directory, a symbolic link, a missing file and a file whose
#     sha256 differs from the row; refuses a certificate file in a RUN folder that no RECHECK row names;
#  4. runs  bash --noprofile --norc work/design/gate_required.sh CERTIFICATE [freeze options]  on each one, in an
#     emptied environment, and requires GATE_REQUIRED|PASS with the certificate hash, the row hash and the verifier
#     hash of row 019, exit 0, and one VERDICT|PASS line at the receipt's r and the row's m0;
#  5. takes gamma and the Ritz value from that output of its own verifier call and from nothing else: G is the largest
#     gamma, U is the smallest Ritz value plus 1/1000000; no number of the receipt enters G or U;
#  6. decides: g0 <= G gives ABOVE, U < g0 gives BELOW, both give a contradiction, otherwise UNRESOLVED; g0 is the
#     constant of the record for the frozen run and the rehearsal's own g0 for a test-mode receipt;
#  7. only then reads the receipt's VERDICT_FIELDS row and final line and compares: CERTIFICATE must read PASS, and
#     DECISION, PREDICTION, GAMMA and UPPER_BOUND_VERIFIER_ONLY must equal what this checker found, and the per-row
#     gamma and verifier Ritz value must equal the RECHECK rows. The receipt's UPPER_BOUND, which by row 012 may rest
#     on the writer's Ritz value, must equal the value that the writer Ritz values of the RECHECK rows give together
#     with this checker's own verifier values. Any difference blocks acceptance.
# NEVER AN INPUT of G, U or the decision of this checker: the receipt's GAMMA, UPPER_BOUND,
# UPPER_BOUND_VERIFIER_ONLY, DECISION, PREDICTION, and the gamma, ritz_writer and ritz_verifier fields of its RECHECK
# rows. They are read after DECISION_HERE is printed, for comparison only. The fields of a RECHECK row used before
# that are its certificate path, its sha256, its m0 and its rowhash.
# Last line: RECHECK_VERDICT|ACCEPT=YES or NO|...   Exit: 0 ACCEPT=YES; 1 ACCEPT=NO; 4 the check could not start.
import sys
import re
import os
import hashlib
import subprocess

MIL = 1000000
LIM_KB = 2097152
G0_R9 = (94070673, 1000000)
PRED_REL = "final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp"
GATE_REL = "work/design/gate_required.sh"
PINNED = [("020", GATE_REL), ("019", "work/design/py/cert_gate.py"), ("021", "work/design/py/indep_verify.py"),
          ("131", "final/tools/recheck_floor.py")]
PRED_OF = {"ABOVE": "CONFIRMED", "BELOW": "FALSIFIED", "UNRESOLVED": "UNRESOLVED"}
OUT = []


def say(x):
    OUT.append(x)
    print(x)
    sys.stdout.flush()


def finish(accept, reasons, extra, outfile):
    say("RECHECK_VERDICT|ACCEPT=%s|%s|reasons=%s|json=0" % ("YES" if accept else "NO", extra, ";".join(reasons) or "none"))
    if outfile:
        with open(outfile, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(OUT) + "\n")
    sys.exit(0 if accept else 1)


def cannot(msg):
    print("RECHECK_VERDICT|ACCEPT=NO|not_started=%s|json=0" % msg)
    sys.exit(4)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def rat(s):
    """A non-negative rational written a/b, a.b or a; None when the word has another shape."""
    s = s.strip()
    if not re.match(r"^[0-9]+([./][0-9]+)?$", s):
        return None
    if "/" in s:
        a, b = s.split("/")
        if int(b) == 0:
            return None
        return (int(a), int(b))
    if "." in s:
        a, b = s.split(".")
        p = 1
        for _ in range(len(b)):
            p = p * 10
        return (int(a + b), p)
    return (int(s), 1)


def lt(a, b):
    return a[0] * b[1] < b[0] * a[1]


def le(a, b):
    return a[0] * b[1] <= b[0] * a[1]


def eq(a, b):
    return a is not None and b is not None and a[0] * b[1] == b[0] * a[1]


def rs(a):
    return "NONE" if a is None else "%d/%d" % (a[0], a[1])


def fld(line):
    d = {}
    for w in line.split("|"):
        if "=" in w:
            k, v = w.split("=", 1)
            if k not in d:
                d[k] = v
    return d


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read().split("\n")


def main():
    a = {}
    for w in sys.argv[1:]:
        if "=" not in w:
            cannot("argument_without_equals_sign")
        k, v = w.split("=", 1)
        a[k] = v
    for k in a:
        if k not in ("receipt", "commit", "out"):
            cannot("unknown_argument_" + k)
    if "receipt" not in a:
        cannot("usage:_recheck_floor.py_receipt=RUN_DIRECTORY/FLOOR-RUN-RECEIPT.hbp_[commit=C]_[out=FILE]")
    outfile = a.get("out")
    here = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))
    root = os.path.realpath(os.path.join(here, "..", ".."))
    pred = os.path.join(root, PRED_REL)
    if not os.path.isfile(pred):
        cannot("prediction_record_absent_from_this_checkout")
    rcpt = os.path.abspath(a["receipt"])
    if os.path.islink(rcpt) or not os.path.isfile(rcpt):
        cannot("receipt_absent_or_a_symbolic_link")
    rund = os.path.realpath(os.path.dirname(rcpt))
    if (rund + "/").startswith(root + "/work/design/") or (rund + "/").startswith(root + "/final/"):
        cannot("run_directory_lies_inside_the_pinned_folders_of_the_checkout")
    bad = []

    # ---- 1. the checkout: record and tools against the PIN rows of the checkout's own record
    P = sha(pred)
    pins = {}
    row073 = ""
    for l in read_lines(pred):
        m = re.match(r"^PIN\|id=([0-9]{3})\|", l)
        if m:
            f = fld(l)
            pins[m.group(1)] = (f.get("path", ""), f.get("value", ""))
        if re.match(r"^[A-Z_]+\|id=073\|", l):
            row073 = l
    say("RECHECK_START|checker=final/tools/recheck_floor.py|checkout=%s|record_sha256=%s|receipt=%s|run_directory=%s|json=0" % (root, P, rcpt, rund))
    for rid, rel in PINNED:
        p = os.path.join(root, rel)
        want = pins.get(rid, ("", ""))
        got = sha(p) if os.path.isfile(p) and not os.path.islink(p) else "ABSENT"
        ok = want[0] == rel and len(want[1]) == 64 and got == want[1]
        say("CHECKOUT_PIN|row=%s|path=%s|want=%s|got=%s|ok=%d|json=0" % (rid, rel, want[1] or "NO_PIN_ROW", got, 1 if ok else 0))
        if not ok:
            bad.append("checkout_file_differs_from_row_%s" % rid)
    if "%d/%d" % G0_R9 not in row073:
        bad.append("row_073_of_the_record_does_not_carry_g0")

    # ---- 2. the receipt: its own hash file, then the rows this checker needs; the verdict rows are read at step 7
    side = rcpt + ".sha256"
    rsha = sha(rcpt)
    sw = read_lines(side)[0].split(" ")[0] if os.path.isfile(side) and not os.path.islink(side) else "ABSENT"
    say("RECEIPT_HASH|sha256=%s|sha256_file=%s|equal=%d|json=0" % (rsha, sw, 1 if rsha == sw else 0))
    if rsha != sw:
        bad.append("receipt_differs_from_its_sha256_file")
    L = [x for x in read_lines(rcpt) if x]
    head = [x for x in L if x.startswith("RECEIPT|")]
    rechecks = [x for x in L if x.startswith("RECHECK|")]
    rdir = [x for x in L if x.startswith("RUN_DIRECTORY|")]
    ptool = [fld(x).get("sha256", "") for x in L if x.startswith("TOOL|private_copy=PREDICT")]
    if len(head) != 1:
        finish(False, bad + ["receipt_has_%d_RECEIPT_rows" % len(head)], "certificates_rechecked=0", outfile)
    hf = fld(head[0])
    mode = hf.get("mode", "")
    r = rat(hf.get("r", ""))
    if mode not in ("r9", "test") or r is None:
        finish(False, bad + ["receipt_mode_or_r_unreadable"], "certificates_rechecked=0", outfile)
    if mode == "r9" and not eq(r, (9, 1)):
        bad.append("receipt_of_mode_r9_names_another_r")
    if mode == "test" and le((8, 1), r) and le(r, (10, 1)):
        finish(False, bad + ["test_mode_receipt_within_1_of_r_9_is_not_rechecked"], "certificates_rechecked=0", outfile)
    if len(rdir) != 1:
        bad.append("receipt_has_%d_RUN_DIRECTORY_rows" % len(rdir))
    if ptool != [P]:
        bad.append("record_of_the_receipt_differs_from_the_record_of_this_checkout")
    freeze_args = []
    commit = a.get("commit", "")
    if mode == "r9":
        if not re.match(r"^[0-9a-f]{40}$", commit):
            finish(False, bad + ["a_receipt_of_the_r9_run_needs_commit=C_(40_hex)_given_by_the_person_who_runs_this_checker"], "certificates_rechecked=0", outfile)
        freeze_args = ["--freeze-commit", commit, "--prediction", PRED_REL, "--prediction-sha256", P]
    elif commit:
        bad.append("commit=_belongs_to_a_receipt_of_the_r9_run")
    say("RECEIPT_SCOPE|mode=%s|r=%s|recheck_rows=%d|freeze_commit_given=%s|json=0" % (mode, rs(r), len(rechecks), commit or "NONE"))

    # ---- 3. certificate paths: relative to the directory that holds the receipt, hashed, nothing unlisted
    todo = []
    seen = set()
    for x in rechecks:
        f = fld(x)
        rel = f.get("certificate", "")
        m = re.match(r"^RUN([0-9]{1,2})/(cert_m([0-9]{1,2})_r[0-9]+_[0-9]+_f[0-9-]+\.txt)$", rel)
        why = ""
        if not m or m.group(1) != m.group(3) or f.get("m0") != m.group(1):
            why = "path_shape_refused"
        elif rel in seen:
            why = "certificate_listed_twice"
        elif f.get("relative_to") != "RUN_DIRECTORY":
            why = "row_does_not_anchor_the_path_to_the_run_directory"
        else:
            full = os.path.join(rund, rel)
            if os.path.islink(os.path.join(rund, "RUN" + m.group(1))) or os.path.islink(full):
                why = "symbolic_link_refused"
            elif not os.path.isfile(full):
                why = "certificate_file_missing"
            elif not os.path.realpath(full).startswith(rund + "/RUN" + m.group(1) + "/"):
                why = "path_leaves_the_run_directory"
            elif not re.match(r"^[0-9a-f]{64}$", f.get("sha256", "")) or sha(full) != f["sha256"]:
                why = "certificate_sha256_differs_from_the_RECHECK_row"
        seen.add(rel)
        if why:
            bad.append("%s:%s" % (rel.replace("|", "_")[:80] or "EMPTY", why))
            say("RECHECKED|certificate=%s|path_check=%s|gate=NOT_RUN|json=0" % (rel[:80] or "EMPTY", why))
        else:
            todo.append((f, rel, os.path.join(rund, rel), int(m.group(1))))
    unlisted = []
    for d in sorted(os.listdir(rund)):
        if re.match(r"^RUN[0-9]{1,2}$", d) and os.path.isdir(os.path.join(rund, d)):
            for n in sorted(os.listdir(os.path.join(rund, d))):
                if n.startswith("cert_") and d + "/" + n not in seen:
                    unlisted.append(d + "/" + n)
    if unlisted:
        bad.append("certificate_files_in_the_RUN_folders_that_no_RECHECK_row_names:%d" % len(unlisted))
    say("PATHS|recheck_rows=%d|usable=%d|unlisted_certificate_files=%d|json=0" % (len(rechecks), len(todo), len(unlisted)))

    # ---- 4 and 5. the verifier, run here; gamma and the Ritz value from this output alone
    env = {"PATH": "/usr/bin:/bin", "LANG": "C"}
    gams = []
    ritz = []
    writer_rows = []
    mem_max = 0
    ran = 0
    for f, rel, full, m0 in todo:
        cmd = ["bash", "--noprofile", "--norc", GATE_REL, full] + freeze_args
        pr = subprocess.run(cmd, cwd=root, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        ran += 1
        out = pr.stdout.decode("utf-8", errors="replace").split("\n")
        if outfile:
            with open("%s.gate_%d_%s.txt" % (outfile, ran, os.path.basename(rel)), "w", encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(out))
        cb = []
        gr = [x for x in out if x.startswith("GATE_REQUIRED|")]
        vd = [x for x in out if x.startswith("VERDICT|")]
        rz = [x for x in out if x.startswith("RITZ_CLASS_VECTOR|")]
        g_v = None
        u_v = None
        if pr.returncode != 0 or len(gr) != 1 or not gr[0].startswith("GATE_REQUIRED|PASS|") or [x for x in out if x][-1:] != gr:
            cb.append("gate_did_not_end_GATE_REQUIRED_PASS")
        else:
            gf = fld(gr[0])
            if gf.get("cert_sha256") != f["sha256"]:
                cb.append("gate_hashed_another_certificate")
            if gf.get("verifier_sha256") != pins.get("019", ("", ""))[1]:
                cb.append("gate_ran_another_verifier")
            if gf.get("rowhash") != f.get("rowhash"):
                cb.append("rowhash_differs_from_the_RECHECK_row")
        if len(vd) != 1:
            cb.append("verdict_lines_%d" % len(vd))
        else:
            vm = re.match(r"^VERDICT\|PASS\|lambda_min\(QHQ\) >= ([0-9]+)/([0-9]+) at r = ([0-9]+)/([0-9]+) \(m0 = ([0-9]+)\)\|", vd[0])
            if not vm:
                cb.append("verdict_is_not_PASS_or_unreadable")
            elif not eq((int(vm.group(3)), int(vm.group(4))), r) or int(vm.group(5)) != m0 or int(vm.group(2)) == 0:
                cb.append("verdict_names_another_r_or_m0")
            else:
                g_v = (int(vm.group(1)), int(vm.group(2)))
        if len(rz) == 1 and re.match(r"^[0-9]+\.[0-9]{6}$", rz[0].split("|")[1]):
            u_v = rat(rz[0].split("|")[1])
        else:
            cb.append("verifier_Ritz_line_absent_or_unreadable")
        for y in out:
            mm = re.match(r"^MEM\|([0-9]+)kB", y)
            if mm:
                mem_max = max(mem_max, int(mm.group(1)))
        if g_v is not None and u_v is not None and not le(g_v, (u_v[0] * MIL + u_v[1], u_v[1] * MIL)):
            cb.append("gamma_above_the_verifier_Ritz_value")
        # the RECHECK row, compared only now that this call's own values exist
        if g_v is not None and not eq(g_v, rat(f.get("gamma", ""))):
            cb.append("gamma_differs_from_the_RECHECK_row")
        if u_v is not None and not eq(u_v, rat(f.get("ritz_verifier", ""))):
            cb.append("verifier_Ritz_value_differs_from_the_RECHECK_row")
        if not cb:
            gams.append(g_v)
            ritz.append(u_v)
            writer_rows.append((rat(f.get("ritz_writer", "")), u_v))
        bad.extend("%s:%s" % (rel, y) for y in cb)
        say("RECHECKED|certificate=%s|sha256=%s|path_check=PASS|gate_exit=%d|gate=%s|gamma_here=%s|ritz_here=%s|gamma_row=%s|ritz_verifier_row=%s|bad=%s|json=0"
            % (rel, f["sha256"], pr.returncode, gr[0].split("|")[1] if gr else "MISSING", rs(g_v), rs(u_v), f.get("gamma", ""), f.get("ritz_verifier", ""), ";".join(cb) or "none"))

    # ---- 6. the decision of this checker, from its own verifier output
    complete = bool(todo) and len(gams) == len(rechecks) and not unlisted
    G = U = None
    for x in gams:
        if G is None or lt(G, x):
            G = x
    for x in ritz:
        y = (x[0] * MIL + x[1], x[1] * MIL)
        if U is None or lt(y, U):
            U = y
    # ---- 7. the receipt's verdict rows, read here for the first time
    vfl = [x for x in L if x.startswith("VERDICT_FIELDS|")]
    fin = [x for x in L if x.startswith("FLOOR_RUN|")]
    if len(vfl) != 1 or len(fin) != 1 or L[-1] != fin[0]:
        finish(False, bad + ["receipt_verdict_rows_absent_or_repeated"], "certificates_rechecked=%d" % ran, outfile)
    vf = fld(vfl[0])
    ff = fld(fin[0])
    if mode == "r9":
        g0 = G0_R9
        g0src = "record_constant_row_073"
        if not eq(rat(vf.get("g0", "")), g0):
            bad.append("g0_of_the_receipt_differs_from_the_record")
    else:
        g0 = rat(vf.get("g0", ""))
        g0src = "rehearsal_value_of_the_receipt"
        if g0 is None:
            finish(False, bad + ["g0_of_the_rehearsal_receipt_unreadable"], "certificates_rechecked=%d" % ran, outfile)
    dec = "NONE"
    if complete and G is not None and U is not None:
        above = le(g0, G)
        below = lt(U, g0)
        if above and below:
            dec = "CONTRADICTION"
            bad.append("lower_bound_and_upper_bound_contradict_each_other")
        elif above:
            dec = "ABOVE"
        elif below:
            dec = "BELOW"
        else:
            dec = "UNRESOLVED"
    else:
        bad.append("no_complete_set_of_rechecked_certificates")
    say("DECISION_HERE|decision=%s|prediction=%s|G=%s|U_verifier_only=%s|g0=%s|g0_source=%s|certificates=%d|verifier_mem_max_kB=%d|mem_under_%d_kB=%d|inputs=the_output_of_this_checker's_own_verifier_calls|json=0"
        % (dec, PRED_OF.get(dec, "NONE"), rs(G), rs(U), rs(g0), g0src, len(gams), mem_max, LIM_KB, 1 if mem_max < LIM_KB else 0))
    for k in ("CERTIFICATE", "PREDICTION", "DECISION", "GAMMA", "UPPER_BOUND"):
        if vf.get(k) != ff.get(k):
            bad.append("VERDICT_FIELDS_and_the_final_line_differ_in_%s" % k)
    if vf.get("CERTIFICATE") != "PASS":
        bad.append("receipt_does_not_read_CERTIFICATE=PASS")
    if vf.get("accepted_certificates") != str(len(rechecks)) or not rechecks:
        bad.append("accepted_certificates_differs_from_the_number_of_RECHECK_rows")
    if vf.get("DECISION") != dec:
        bad.append("DECISION_differs:receipt_%s_here_%s" % (vf.get("DECISION"), dec))
    if vf.get("PREDICTION") != PRED_OF.get(dec):
        bad.append("PREDICTION_differs:receipt_%s_here_%s" % (vf.get("PREDICTION"), PRED_OF.get(dec, "NONE")))
    if not eq(G, rat(vf.get("GAMMA", ""))):
        bad.append("GAMMA_differs:receipt_%s_here_%s" % (vf.get("GAMMA"), rs(G)))
    if not eq(U, rat(vf.get("UPPER_BOUND_VERIFIER_ONLY", ""))):
        bad.append("UPPER_BOUND_VERIFIER_ONLY_differs:receipt_%s_here_%s" % (vf.get("UPPER_BOUND_VERIFIER_ONLY"), rs(U)))
    # the receipt's own UPPER_BOUND (row 012: the smaller of the writer's and the verifier's Ritz value, plus 1/1000000):
    # compared here with the value the RECHECK rows' writer fields give together with this checker's verifier values
    ub_want = None
    for rw_, uv_ in writer_rows:
        if rw_ is None:
            bad.append("ritz_writer_of_a_RECHECK_row_unreadable")
            continue
        z = rw_ if lt(rw_, uv_) else uv_
        z = (z[0] * MIL + z[1], z[1] * MIL)
        if ub_want is None or lt(z, ub_want):
            ub_want = z
    if not eq(ub_want, rat(vf.get("UPPER_BOUND", ""))):
        bad.append("UPPER_BOUND_of_the_receipt_differs_from_its_own_rows:receipt_%s_rows_give_%s" % (vf.get("UPPER_BOUND"), rs(ub_want)))
    if mode == "r9" and ff.get("freeze_commit") != commit:
        bad.append("freeze_commit_of_the_receipt_differs_from_commit=")
    say("RECEIPT_VERDICT|CERTIFICATE=%s|PREDICTION=%s|DECISION=%s|GAMMA=%s|UPPER_BOUND=%s|UPPER_BOUND_VERIFIER_ONLY=%s|read=after_the_decision_of_this_checker|json=0"
        % (vf.get("CERTIFICATE"), vf.get("PREDICTION"), vf.get("DECISION"), vf.get("GAMMA"), vf.get("UPPER_BOUND"), vf.get("UPPER_BOUND_VERIFIER_ONLY")))
    finish(not bad, bad, "DECISION=%s|PREDICTION=%s|GAMMA=%s|UPPER_BOUND_VERIFIER_ONLY=%s|g0=%s|mode=%s|r=%s|certificates_rechecked=%d|receipt_sha256=%s|record_sha256=%s"
           % (dec, PRED_OF.get(dec, "NONE"), rs(G), rs(U), rs(g0), mode, rs(r), ran, rsha, P), outfile)


main()
