#!/usr/bin/env python3
# recheck_floor.py -- second-environment checker of a floor run receipt (rows 125, 131, 133, 138 and 143 of the record).
# Fifth correction round. Integer and exact-rational arithmetic only. It computes no spectrum: it runs the pinned
# gate driver on certificates and replays the frozen protocol on what that driver prints.
#
#   python3 -I -B final/tools/recheck_floor.py receipt=RUN_DIRECTORY/FLOOR-RUN-RECEIPT.hbp
#                                              [commit=C] [receipt_sha256=H] [out=FILE]
#
# Run it inside the freeze folder of a clean checkout of the freeze commit, in an environment other than the one that
# launched the run. RUN_DIRECTORY is the directory that holds the receipt, copied whole. For a receipt of the frozen
# r = 9 run, commit=C (40 hex) and receipt_sha256=H (64 hex) are both required; they are given by the person who runs
# this checker, H being the value the launcher printed in its PUBLISH line at the end of the run and that was made
# public then. A receipt rewritten after that publication no longer hashes to H.
#
# WHAT IS ACCEPTED. ACCEPT=YES says three things at once: (1) every certificate the protocol calls for is present and
# passes the pinned verifier here; (2) the list of certificates is exactly the one the frozen protocol produces, no
# more and no fewer: the steps in their order, each completed step with every frozen f word once, no step after a
# decision; (3) the decision, the bounds, the per-step
# values and the prediction scores this checker computes from its own verifier output equal the ones in the receipt.
# A result that is ABOVE or BELOW stands on certificates verified here. An UNRESOLVED result is NEVER accepted by this
# checker (row 143): certificates that do not decide cannot show that no certificate decides, because a valid
# certificate can be replaced by a weaker valid one (a smaller t, another positive vector). The checks are still run
# and printed for an UNRESOLVED receipt; the last line is ACCEPT=NO and the reading belongs to the reviewer.
#
# THE PROTOCOL. For the frozen run it is the constant below (rows 001 006 007 012): r = 9, steps m0 = 11, 12, 13,
# f words 1 ; 8,7,6,5,4 ; 6,5,4,3 at every step, g0 = 94070673/1000000. For a rehearsal it is read from the PROTOCOL
# row of the receipt, which a rehearsal receipt states for itself: a rehearsal acceptance is no acceptance of a result.
#
# NEVER AN INPUT of G, U, the decision or the scores of this checker: the receipt's GAMMA, UPPER_BOUND,
# UPPER_BOUND_VERIFIER_ONLY, DECISION, PREDICTION, its STEP values, its PREDICT_SCORE rows and the gamma, ritz_writer
# and ritz_verifier fields of its RECHECK rows. They are read after DECISION_HERE is printed, for comparison only.
# Read before that point: the mode and r, the PROTOCOL row of a rehearsal, the status word of each STEP row (OK or
# OPFAIL), and of each RECHECK row its path, sha256, m0 and rowhash.
#
# NOT RECHECKED HERE, stated in the output: the writer's peak memory (a value of the launching host), PREDICT rows
# 068 and 070 (they read writer-side values), and that a certificate was written by the frozen binary and not by
# another program; a certificate is accepted on what the verifier proves from its rows.
# Last line: RECHECK_VERDICT|ACCEPT=YES or NO|...   Exit: 0 ACCEPT=YES; 1 ACCEPT=NO; 4 the check could not start.
import sys
import re
import os
import hashlib
import subprocess

MIL = 1000000
LIM_KB = 2097152
G0_R9 = (94070673, 1000000)
CAP = (94070936, 1000000)
STEPS_R9 = [11, 12, 13]
FWORDS_R9 = ["1", "8,7,6,5,4", "6,5,4,3"]
PRED_REL = "final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp"
GATE_REL = "work/design/gate_required.sh"
PINNED = [("020", GATE_REL), ("019", "work/design/py/cert_gate.py"), ("021", "work/design/py/indep_verify.py"),
          ("131", "final/tools/recheck_floor.py")]
PRED_OF = {"ABOVE": "CONFIRMED", "BELOW": "FALSIFIED", "UNRESOLVED": "UNRESOLVED"}
NOT_RECHECKED = ("068", "070")
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
    s = (s or "").strip()
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


def sub(a, b):
    return (a[0] * b[1] - b[0] * a[1], a[1] * b[1])


def rs(a):
    return "NONE" if a is None else "%d/%d" % (a[0], a[1])


def rmax(xs):
    m = None
    for x in xs:
        if m is None or lt(m, x):
            m = x
    return m


def rmin(xs):
    m = None
    for x in xs:
        if m is None or lt(x, m):
            m = x
    return m


def fld(line):
    """Fields of a pipe row; DUP is set when a key occurs twice."""
    d = {}
    dup = False
    for w in line.split("|"):
        if "=" in w:
            k, v = w.split("=", 1)
            if k in d:
                dup = True
            else:
                d[k] = v
    d["\0dup"] = dup
    return d


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read().split("\n")


def state_of(G, U, g0):
    above = G is not None and le(g0, G)
    below = U is not None and lt(U, g0)
    if above and below:
        return "CONTRADICTION"
    if above:
        return "ABOVE"
    if below:
        return "BELOW"
    return "UNDECIDED"


def score(S, g0, G, U):
    """PREDICT rows 058-073 from this checker's own step values, by their met_if words; S is the list of steps in run
    order, each None (not completed) or a dict with G, U and the per-certificate gammas and tail caps. Rows 068 and
    070 read writer-side values and are returned as NOT_RECHECKED."""
    def b(x):
        return "MET" if x else "NOT_MET"
    P = {}
    s1 = S[0] if len(S) > 0 else None
    s2 = S[1] if len(S) > 1 else None
    s3 = S[2] if len(S) > 2 else None
    gam = [g for s in S if s for g in s["gam"]]
    NV = "NO_GATED_VALUE"
    P["058"] = b(le((80, 1), s1["G"])) if s1 else "NOT_MET"
    P["059"] = b(le((935000, 10000), s1["G"])) if s1 else NV
    P["060"] = b(le(g0, s1["U"]) and le(s1["U"], (9413, 100))) if s1 else NV
    P["061"] = b(le(sub(s1["U"], s1["G"]), (3, 10))) if s1 else NV
    P["062"] = b(le(sub(s2["U"], s2["G"]), (1, 10))) if s2 else "NOT_EVALUATED"
    P["063"] = b(le(sub(s3["U"], s3["G"]), (1, 20))) if s3 else "NOT_EVALUATED"
    P["064"] = b(le(sub(rmin([U, CAP]), s1["G"]), (3, 10))) if s1 else NV
    P["065"] = b(all(le(x, CAP) for x in gam)) if gam else NV
    P["066"] = b(lt(rmax(gam), g0)) if gam else NV
    if s1 and len(s1["gam"]) >= 3:
        P["067"] = b(lt(s1["gam"][0], rmax(s1["gam"][1:])))
    else:
        P["067"] = NV
    P["068"] = "NOT_RECHECKED"
    P["069"] = b(le(sub(s1["G"], (1, 1000)), s2["G"])) if (s1 and s2) else "NOT_EVALUATED"
    P["070"] = "NOT_RECHECKED"
    P["071"] = b(le(G, (9410, 100)) and le((9407, 100), U)) if (G and U) else NV
    st = state_of(G, U, g0)
    P["072"] = "OPEN_BRANCH_" + ("BELOW_FALSIFIED_H4" if st == "BELOW" else st) if G else NV
    P["073"] = b(le(g0, U)) if U else NV
    return P


def main():
    a = {}
    for w in sys.argv[1:]:
        if "=" not in w:
            cannot("argument_without_equals_sign")
        k, v = w.split("=", 1)
        a[k] = v
    for k in a:
        if k not in ("receipt", "commit", "receipt_sha256", "out"):
            cannot("unknown_argument_" + k)
    if "receipt" not in a:
        cannot("usage:_recheck_floor.py_receipt=RUN_DIRECTORY/FLOOR-RUN-RECEIPT.hbp_[commit=C]_[receipt_sha256=H]_[out=FILE]")
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

    # ---- 2. the receipt: its hash file, the hash made public at the end of the run, and the rows read before the decision
    side = rcpt + ".sha256"
    rsha = sha(rcpt)
    sw = read_lines(side)[0].split(" ")[0] if os.path.isfile(side) and not os.path.islink(side) else "ABSENT"
    pub = a.get("receipt_sha256", "")
    say("RECEIPT_HASH|sha256=%s|sha256_file=%s|equal=%d|published=%s|equal_to_published=%s|json=0"
        % (rsha, sw, 1 if rsha == sw else 0, pub or "NOT_GIVEN", ("1" if rsha == pub else "0") if pub else "NOT_GIVEN"))
    if rsha != sw:
        bad.append("receipt_differs_from_its_sha256_file")
    if pub and (not re.match(r"^[0-9a-f]{64}$", pub) or pub != rsha):
        bad.append("receipt_differs_from_the_published_receipt_sha256")
    L = [x for x in read_lines(rcpt) if x]
    head = [x for x in L if x.startswith("RECEIPT|")]
    if len(head) != 1:
        finish(False, bad + ["receipt_has_%d_RECEIPT_rows" % len(head)], "certificates_rechecked=0", outfile)
    hf = fld(head[0])
    mode = hf.get("mode", "")
    r = rat(hf.get("r", ""))
    if mode not in ("r9", "test") or r is None or hf["\0dup"]:
        finish(False, bad + ["receipt_mode_or_r_unreadable"], "certificates_rechecked=0", outfile)
    if mode == "test" and le((8, 1), r) and le(r, (10, 1)):
        finish(False, bad + ["test_mode_receipt_within_1_of_r_9_is_not_rechecked"], "certificates_rechecked=0", outfile)
    commit = a.get("commit", "")
    freeze_args = []
    prot = [x for x in L if x.startswith("PROTOCOL|")]
    if mode == "r9":
        if not eq(r, (9, 1)):
            bad.append("receipt_of_mode_r9_names_another_r")
        if not re.match(r"^[0-9a-f]{40}$", commit):
            finish(False, bad + ["a_receipt_of_the_r9_run_needs_commit=C_(40_hex)_given_by_the_person_who_runs_this_checker"], "certificates_rechecked=0", outfile)
        if not pub:
            finish(False, bad + ["a_receipt_of_the_r9_run_needs_receipt_sha256=H,_the_value_of_the_launcher's_PUBLISH_line_as_made_public_at_the_end_of_the_run"], "certificates_rechecked=0", outfile)
        freeze_args = ["--freeze-commit", commit, "--prediction", PRED_REL, "--prediction-sha256", P]
        # commit= against the checkout this checker runs in, where git can read it (an export carries no HEAD)
        try:
            chead = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.DEVNULL).stdout.decode("ascii", "replace").strip()
        except Exception:
            chead = ""
        if not re.match(r"^[0-9a-f]{40}$", chead):
            chead = "NOT_READ_no_git_checkout"
        elif chead != commit:
            bad.append("commit=_differs_from_the_HEAD_of_this_checkout")
        say("CHECKOUT_HEAD|head=%s|commit_given=%s|json=0" % (chead, commit))
        steps_plan, fwords, g0, g0src = list(STEPS_R9), list(FWORDS_R9), G0_R9, "record_constant_row_073"
    else:
        if commit:
            bad.append("commit=_belongs_to_a_receipt_of_the_r9_run")
        if len(prot) != 1 or fld(prot[0])["\0dup"]:
            finish(False, bad + ["rehearsal_receipt_has_%d_PROTOCOL_rows" % len(prot)], "certificates_rechecked=0", outfile)
        pf = fld(prot[0])
        g0 = rat(pf.get("g0", ""))
        ok_plan = re.match(r"^[0-9]{1,2}(,[0-9]{1,2}){0,2}$", pf.get("m0_steps", "")) and re.match(r"^[0-9,]+(;[0-9,]+)*$", pf.get("f", "")) and g0 is not None
        if not ok_plan:
            finish(False, bad + ["PROTOCOL_row_of_the_rehearsal_unreadable"], "certificates_rechecked=0", outfile)
        steps_plan = [int(x) for x in pf["m0_steps"].split(",")]
        fwords = pf["f"].split(";")
        g0src = "PROTOCOL_row_of_the_rehearsal_receipt"
        if len(set(steps_plan)) != len(steps_plan) or len(set(fwords)) != len(fwords) or not all(re.match(r"^[0-9]+(,[0-9]+)*$", w) for w in fwords):
            finish(False, bad + ["PROTOCOL_row_of_the_rehearsal_unreadable"], "certificates_rechecked=0", outfile)
    if mode == "r9" and len(prot) == 1:
        pf = fld(prot[0])
        if pf["\0dup"] or pf.get("m0_steps") != ",".join(str(x) for x in steps_plan) or pf.get("f") != ";".join(fwords) or not eq(rat(pf.get("g0", "")), g0):
            bad.append("PROTOCOL_row_differs_from_the_frozen_protocol")
    elif mode == "r9":
        bad.append("receipt_has_%d_PROTOCOL_rows" % len(prot))
    ptool = [fld(x).get("sha256", "") for x in L if x.startswith("TOOL|private_copy=PREDICT")]
    if ptool != [P]:
        bad.append("record_of_the_receipt_differs_from_the_record_of_this_checkout")
    if len([x for x in L if x.startswith("RUN_DIRECTORY|")]) != 1:
        bad.append("receipt_has_no_single_RUN_DIRECTORY_row")
    say("PROTOCOL_HERE|mode=%s|r=%s|m0_steps=%s|f=%s|g0=%s|source=%s|freeze_commit_given=%s|json=0"
        % (mode, rs(r), ",".join(str(x) for x in steps_plan), ";".join(fwords), rs(g0), g0src if mode == "test" else "constants_of_this_checker_(rows_001_006_007_012)", commit or "NONE"))

    # ---- 3. the steps the receipt lists: a prefix of the plan, each OK or OPFAIL (the status word is all that is read)
    srows = [x for x in L if x.startswith("STEP|")]
    listed = []
    for x in srows:
        f = fld(x)
        if f["\0dup"] or not re.match(r"^[0-9]{1,2}$", f.get("m0", "")) or f.get("status") not in ("OK", "OPFAIL"):
            bad.append("STEP_row_unreadable_or_status_other_than_OK_OPFAIL")
            continue
        listed.append((int(f["m0"]), f["status"], f))
    if [m for m, _, _ in listed] != steps_plan[:len(listed)] or not listed:
        finish(False, bad + ["steps_of_the_receipt_are_no_prefix_of_the_protocol:%s" % ",".join(str(m) for m, _, _ in listed)], "certificates_rechecked=0", outfile)

    # ---- 4. certificate paths: exactly the frozen f words at every OK step, none at an OPFAIL step, nothing unlisted
    rechecks = [x for x in L if x.startswith("RECHECK|")]
    by_step = {}
    seen = set()
    for x in rechecks:
        f = fld(x)
        rel = f.get("certificate", "")
        m = re.match(r"^RUN([0-9]{1,2})/(cert_m([0-9]{1,2})_r([0-9]+)_([0-9]+)_f([0-9-]+)\.txt)$", rel)
        why = ""
        if f["\0dup"]:
            why = "row_repeats_a_field"
        elif not m or m.group(1) != m.group(3) or f.get("m0") != m.group(1):
            why = "path_shape_refused"
        elif rel in seen:
            why = "certificate_listed_twice"
        elif f.get("relative_to") != "RUN_DIRECTORY":
            why = "row_does_not_anchor_the_path_to_the_run_directory"
        elif not eq((int(m.group(4)), int(m.group(5))), r) or "%d/%d" % r != "%s/%s" % (m.group(4), m.group(5)):
            why = "file_name_names_another_r"
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
            else:
                with open(full, "r", encoding="utf-8", errors="replace") as fh:
                    hl = fh.readline().rstrip("\n")
                hd = {}
                for w in hl.split(" "):
                    if "=" in w:
                        k, v = w.split("=", 1)
                        hd.setdefault(k, v)
                fw = hd.get("f", "")
                if not hl.startswith("# floorcert certificate:") or hd.get("m0") != m.group(1) or hd.get("r") != "%d/%d" % r or fw.replace(",", "-") != m.group(6):
                    why = "certificate_header_differs_from_its_file_name_in_m0_r_or_f"
                elif mode == "r9" and (hd.get("freeze") != commit or hd.get("pred") != P):
                    why = "certificate_header_names_another_freeze_commit_or_record"
        seen.add(rel)
        if why:
            bad.append("%s:%s" % (rel.replace("|", "_")[:80] or "EMPTY", why))
            say("RECHECKED|certificate=%s|path_check=%s|gate=NOT_RUN|json=0" % (rel[:80] or "EMPTY", why))
        else:
            by_step.setdefault(int(m.group(1)), []).append((f, rel, os.path.join(rund, rel), fw))
    unlisted = []
    for d in sorted(os.listdir(rund)):
        if re.match(r"^RUN[0-9]{1,2}$", d) and os.path.isdir(os.path.join(rund, d)):
            for n in sorted(os.listdir(os.path.join(rund, d))):
                if n.startswith("cert_") and d + "/" + n not in seen:
                    unlisted.append(d + "/" + n)
    if unlisted:
        bad.append("certificate_files_in_the_RUN_folders_that_no_RECHECK_row_names:%d" % len(unlisted))
    for mstep in by_step:
        if mstep not in [m for m, _, _ in listed]:
            bad.append("certificates_at_m0_%d,_which_is_no_listed_step" % mstep)
    todo = []
    for mstep, status, _ in listed:
        got = [c[3] for c in by_step.get(mstep, [])]
        if status == "OK" and got != fwords:
            bad.append("step_m0_%d_carries_the_f_words_[%s]_and_the_protocol_calls_for_[%s]" % (mstep, " ; ".join(got) or "none", " ; ".join(fwords)))
        if status == "OPFAIL" and got:
            bad.append("step_m0_%d_is_listed_as_not_completed_and_carries_certificates" % mstep)
        if status == "OK":
            todo.extend((mstep,) + c for c in by_step.get(mstep, []))
    say("PATHS|recheck_rows=%d|usable=%d|unlisted_certificate_files=%d|steps_listed=%s|json=0"
        % (len(rechecks), len(todo), len(unlisted), ",".join("%d:%s" % (m, s) for m, s, _ in listed)))

    # ---- 5. the verifier, run here once per certificate; gamma, Ritz value and memory from this output alone
    env = {"PATH": "/usr/bin:/bin", "LANG": "C"}
    own = {}
    mem_max = 0
    ran = 0
    for mstep, f, rel, full, fw in todo:
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
            elif not eq((int(vm.group(3)), int(vm.group(4))), r) or int(vm.group(5)) != mstep or int(vm.group(2)) == 0:
                cb.append("verdict_names_another_r_or_m0")
            else:
                g_v = (int(vm.group(1)), int(vm.group(2)))
        if len(rz) == 1 and re.match(r"^[0-9]+\.[0-9]{6}$", rz[0].split("|")[1]):
            u_v = rat(rz[0].split("|")[1])
        else:
            cb.append("verifier_Ritz_line_absent_or_unreadable")
        mems = [int(mm.group(1)) for mm in (re.match(r"^MEM\|([0-9]+)kB", y) for y in out) if mm]
        if not mems:
            cb.append("verifier_printed_no_MEM_line")
        for kb in mems:
            mem_max = max(mem_max, kb)
            if kb >= LIM_KB:
                cb.append("verifier_MEM_%dkB_at_or_over_the_limit_%dkB" % (kb, LIM_KB))
        if g_v is not None and u_v is not None and not le(g_v, (u_v[0] * MIL + u_v[1], u_v[1] * MIL)):
            cb.append("gamma_above_the_verifier_Ritz_value")
        if not cb:
            own.setdefault(mstep, []).append((fw, g_v, u_v, f))
        bad.extend("%s:%s" % (rel, y) for y in cb)
        say("RECHECKED|certificate=%s|sha256=%s|path_check=PASS|gate_exit=%d|gate=%s|gamma_here=%s|ritz_here=%s|bad=%s|json=0"
            % (rel, f["sha256"], pr.returncode, gr[0].split("|")[1] if gr else "MISSING", rs(g_v), rs(u_v), ";".join(cb) or "none"))

    # ---- 6. the protocol replayed on this checker's own values: steps, stops, decision, scores
    S = []
    opfail = []
    for mstep, status, _ in listed:
        c = own.get(mstep, [])
        if status == "OK" and len(c) == len(fwords):
            S.append({"m": mstep, "G": rmax([x[1] for x in c]), "U": rmin([(x[2][0] * MIL + x[2][1], x[2][1] * MIL) for x in c]),
                      "gam": [x[1] for x in c]})
        else:
            S.append(None)
            if status == "OPFAIL":
                opfail.append(mstep)
            else:
                bad.append("step_m0_%d_has_no_complete_set_of_verified_certificates" % mstep)
    G = U = None
    st = "UNDECIDED"
    for i, s in enumerate(S):
        done = [x for x in S[:i + 1] if x]
        G = rmax([x["G"] for x in done]) if done else None
        U = rmin([x["U"] for x in done]) if done else None
        st = state_of(G, U, g0)
        if st == "CONTRADICTION":
            bad.append("lower_bound_and_upper_bound_contradict_each_other_after_m0_%d" % listed[i][0])
            break
        if st in ("ABOVE", "BELOW") and i < len(S) - 1:
            bad.append("a_step_follows_m0_%d,_where_the_result_was_already_%s" % (listed[i][0], st))
            break
    dec = "UNRESOLVED" if st == "UNDECIDED" else ("NONE" if st == "CONTRADICTION" else st)
    complete = len(listed) == len(steps_plan) and not opfail and all(S)
    if dec == "UNRESOLVED":
        bad.append("UNRESOLVED_is_never_accepted_by_this_checker_(row_143):_certificates_that_do_not_decide_cannot_show_that_no_certificate_decides")
    if dec == "UNRESOLVED" and not complete:
        bad.append("UNRESOLVED_with_a_step_that_did_not_complete_or_did_not_run_(steps_%s_of_%s,_not_completed_%s):_this_reading_belongs_to_the_reviewer"
                   % (",".join(str(m) for m, _, _ in listed), ",".join(str(x) for x in steps_plan), ",".join(str(x) for x in opfail) or "none"))
    if G is None or U is None:
        bad.append("no_verified_certificate")
    PS = score(S, g0, G, U) if (G is not None and U is not None) else {}
    say("DECISION_HERE|decision=%s|prediction=%s|G=%s|U_verifier_only=%s|g0=%s|g0_source=%s|steps=%s|not_completed=%s|certificates=%d|verifier_mem_max_kB=%d|limit_kB=%d|inputs=the_output_of_this_checker's_own_verifier_calls_and_the_protocol|json=0"
        % (dec, PRED_OF.get(dec, "NONE"), rs(G), rs(U), rs(g0), g0src, ",".join("%d:%s" % (m, "OK" if S[i] else "NONE") for i, (m, _, _) in enumerate(listed)),
           ",".join(str(x) for x in opfail) or "none", sum(len(v) for v in own.values()), mem_max, LIM_KB))

    # ---- 7. the receipt's own values, read here for the first time and compared
    vfl = [x for x in L if x.startswith("VERDICT_FIELDS|")]
    fin = [x for x in L if x.startswith("FLOOR_RUN|")]
    if len(vfl) != 1 or len(fin) != 1 or L[-1] != fin[0]:
        finish(False, bad + ["receipt_verdict_rows_absent_or_repeated"], "certificates_rechecked=%d" % ran, outfile)
    vf = fld(vfl[0])
    ff = fld(fin[0])
    if vf["\0dup"] or ff["\0dup"]:
        bad.append("a_verdict_row_repeats_a_field")
    for k in ("CERTIFICATE", "PREDICTION", "DECISION", "GAMMA", "UPPER_BOUND"):
        if vf.get(k) != ff.get(k):
            bad.append("VERDICT_FIELDS_and_the_final_line_differ_in_%s" % k)
    if vf.get("CERTIFICATE") != "PASS":
        bad.append("receipt_does_not_read_CERTIFICATE=PASS")
    if not eq(rat(vf.get("g0", "")), g0):
        bad.append("g0_of_the_receipt_differs_from_the_protocol")
    if vf.get("accepted_certificates") != str(len(todo)) or not todo:
        bad.append("accepted_certificates_differs_from_the_certificates_the_protocol_calls_for")
    if vf.get("DECISION") != dec:
        bad.append("DECISION_differs:receipt_%s_here_%s" % (vf.get("DECISION"), dec))
    if vf.get("PREDICTION") != PRED_OF.get(dec):
        bad.append("PREDICTION_differs:receipt_%s_here_%s" % (vf.get("PREDICTION"), PRED_OF.get(dec, "NONE")))
    if not eq(G, rat(vf.get("GAMMA", ""))):
        bad.append("GAMMA_differs:receipt_%s_here_%s" % (vf.get("GAMMA"), rs(G)))
    for k in ("UPPER_BOUND_VERIFIER_ONLY", "UPPER_BOUND"):
        if not eq(U, rat(vf.get(k, ""))):
            bad.append("%s_differs:receipt_%s_here_%s" % (k, vf.get(k), rs(U)))
    if ff.get("steps_run") != ",".join(str(m) for m, _, _ in listed) or ff.get("steps_ok") != (",".join(str(m) for i, (m, _, _) in enumerate(listed) if S[i]) or "none") \
            or ff.get("operational_failures") != (",".join(str(x) for x in opfail) or "none"):
        bad.append("steps_run_steps_ok_or_operational_failures_of_the_final_line_differ")
    if mode == "r9" and ff.get("freeze_commit") != commit:
        bad.append("freeze_commit_of_the_receipt_differs_from_commit=")
    for i, (mstep, status, sf) in enumerate(listed):
        if not S[i]:
            continue
        if not eq(S[i]["G"], rat(sf.get("G", ""))) or not eq(S[i]["U"], rat(sf.get("U_verifier_only", ""))) or not eq(S[i]["U"], rat(sf.get("U", ""))):
            bad.append("STEP_row_m0_%d_differs_in_G_or_U" % mstep)
        if sf.get("accepted") != str(len(fwords)) or sf.get("certificates") != str(len(fwords)) or sf.get("resource_limit") != "HELD" or sf.get("bad") != "none":
            bad.append("STEP_row_m0_%d_does_not_read_%d_accepted,_resource_limit_HELD,_bad_none" % (mstep, len(fwords)))
        for fw, g_v, u_v, f in own[mstep]:
            if not eq(g_v, rat(f.get("gamma", ""))) or not eq(u_v, rat(f.get("ritz_verifier", ""))) or not eq(u_v, rat(f.get("ritz_writer", ""))):
                bad.append("RECHECK_row_m0_%d_f_%s_differs_in_gamma_or_a_Ritz_value" % (mstep, fw.replace(",", "-")))
    srec = {}
    for x in L:
        if x.startswith("PREDICT_SCORE|"):
            f = fld(x)
            if "row" not in f:
                bad.append("PREDICT_SCORE_row_without_a_row_key")
            if f.get("row", "NO_ROW_KEY") in srec or f["\0dup"]:
                bad.append("PREDICT_SCORE_row_repeated")
            srec[f.get("row", "NO_ROW_KEY")] = f.get("outcome")
    sdiff = [k for k in sorted(PS) if k not in NOT_RECHECKED and srec.get(k) != PS[k]]
    if PS and (sorted(srec) != sorted(PS) or sdiff):
        bad.append("PREDICT_SCORE_rows_differ_from_the_scores_computed_here:%s" % (",".join("%s_receipt_%s_here_%s" % (k, srec.get(k), PS[k]) for k in sdiff) or "row_set"))
    say("SCORES_HERE|%s|not_rechecked=068_070_(writer-side_values)|compared_after_the_decision=1|json=0"
        % "|".join("%s=%s" % (k, PS[k]) for k in sorted(PS)))
    say("RECEIPT_VERDICT|CERTIFICATE=%s|PREDICTION=%s|DECISION=%s|GAMMA=%s|UPPER_BOUND=%s|UPPER_BOUND_VERIFIER_ONLY=%s|read=after_the_decision_of_this_checker|json=0"
        % (vf.get("CERTIFICATE"), vf.get("PREDICTION"), vf.get("DECISION"), vf.get("GAMMA"), vf.get("UPPER_BOUND"), vf.get("UPPER_BOUND_VERIFIER_ONLY")))
    finish(not bad, bad, "DECISION=%s|PREDICTION=%s|GAMMA=%s|UPPER_BOUND_VERIFIER_ONLY=%s|g0=%s|mode=%s|r=%s|steps=%s|certificates_rechecked=%d|not_rechecked=writer_peak_memory,_PREDICT_068_070,_certificate_provenance|receipt_sha256=%s|record_sha256=%s"
           % (dec, PRED_OF.get(dec, "NONE"), rs(G), rs(U), rs(g0), mode, rs(r), ",".join(str(m) for m, _, _ in listed), ran, rsha, P), outfile)


main()
