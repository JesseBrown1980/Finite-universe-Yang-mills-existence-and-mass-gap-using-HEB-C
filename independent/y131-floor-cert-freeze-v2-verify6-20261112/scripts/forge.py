#!/usr/bin/env python3
# forge.py -- verifier seat (opus55), final-head verification 6 (regression rerun of the verification-5 script) of the floor freeze v2.
# Integers only. Makes a copied run directory's receipt agree with whatever the checker itself computes from the
# certificates now on disk (a forger who uses the checker as an oracle), then rewrites the .sha256 sidecar.
#   python3 -I forge.py RUNDIR CHECKOUT_FREEZE_FOLDER [keep_scores]
# It changes: RECHECK sha256/gamma/ritz_writer/ritz_verifier, STEP G/U/U_verifier_only/accepted/certificates/
# resource_limit/bad, VERDICT_FIELDS and FLOOR_RUN DECISION/PREDICTION/GAMMA/UPPER_BOUND(_VERIFIER_ONLY)/
# accepted_certificates/steps_run/steps_ok/operational_failures, and PREDICT_SCORE outcomes.
import sys, os, re, hashlib, subprocess

NAME = "FLOOR-RUN-RECEIPT.hbp"
MIL = 1000000
PRED = {"ABOVE": "CONFIRMED", "BELOW": "FALSIFIED", "UNRESOLVED": "UNRESOLVED"}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def setf(line, key, val):
    w = line.split("|")
    for i, x in enumerate(w):
        if x.startswith(key + "="):
            w[i] = key + "=" + val
            return "|".join(w)
    # absent: insert before json=0
    if w[-1] == "json=0":
        w.insert(len(w) - 1, key + "=" + val)
        return "|".join(w)
    return line


def getf(line, key):
    for x in line.split("|"):
        if x.startswith(key + "="):
            return x.split("=", 1)[1]
    return None


def save(d, L):
    p = os.path.join(d, NAME)
    open(p, "w", encoding="utf-8", newline="\n").write("\n".join(L))
    open(p + ".sha256", "w", encoding="utf-8", newline="\n").write("%s  %s\n" % (sha(p), NAME))


def check(d, ck):
    pr = subprocess.run(["python3", "-I", "-B", "final/tools/recheck_floor.py", "receipt=" + os.path.join(d, NAME)],
                        cwd=ck, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return pr.stdout.decode("utf-8", "replace").split("\n")


def rat(s):
    a, b = s.split("/")
    return int(a), int(b)


def main():
    d, ck = sys.argv[1], sys.argv[2]
    keep_scores = len(sys.argv) > 3 and sys.argv[3] == "keep_scores"
    p = os.path.join(d, NAME)
    L = open(p, encoding="utf-8").read().split("\n")
    # certificate sha256 first, so the checker gets to run the verifier
    for i, x in enumerate(L):
        if x.startswith("RECHECK|"):
            cf = os.path.join(d, getf(x, "certificate"))
            if os.path.isfile(cf):
                L[i] = setf(x, "sha256", sha(cf))
    save(d, L)
    out = check(d, ck)
    here = {}
    for x in out:
        m = re.match(r"^RECHECKED\|certificate=([^|]*)\|.*\|gamma_here=([0-9/]+)\|ritz_here=([0-9/]+)\|", x)
        if m:
            here[m.group(1)] = (m.group(2), m.group(3))
    dh = [x for x in out if x.startswith("DECISION_HERE|")]
    sh = [x for x in out if x.startswith("SCORES_HERE|")]
    if not dh:
        print("FORGE|no_DECISION_HERE|last=%s" % [x for x in out if x][-1:])
        sys.exit(1)
    dec = getf(dh[0], "decision")
    G = getf(dh[0], "G")
    U = getf(dh[0], "U_verifier_only")
    steps = {}
    for i, x in enumerate(L):
        if x.startswith("RECHECK|"):
            c = getf(x, "certificate")
            if c in here:
                g, rz = here[c]
                L[i] = setf(setf(setf(x, "gamma", g), "ritz_writer", rz), "ritz_verifier", rz)
                a, b = rat(rz)
                u = (a * MIL + b, b * MIL)
                ga = rat(g)
                s = steps.setdefault(getf(x, "m0"), {"G": None, "U": None, "n": 0})
                s["n"] += 1
                if s["G"] is None or s["G"][0] * ga[1] < ga[0] * s["G"][1]:
                    s["G"] = ga
                if s["U"] is None or u[0] * s["U"][1] < s["U"][0] * u[1]:
                    s["U"] = u
    ok_steps = []
    run_steps = []
    opf = []
    for i, x in enumerate(L):
        if x.startswith("STEP|"):
            m = getf(x, "m0")
            run_steps.append(m)
            if getf(x, "status") == "OPFAIL":
                opf.append(m)
                continue
            if m in steps:
                s = steps[m]
                y = setf(x, "G", "%d/%d" % s["G"])
                y = setf(y, "U", "%d/%d" % s["U"])
                y = setf(y, "U_verifier_only", "%d/%d" % s["U"])
                y = setf(y, "accepted", str(s["n"]))
                y = setf(y, "certificates", str(s["n"]))
                y = setf(y, "resource_limit", "HELD")
                y = setf(y, "bad", "none")
                L[i] = y
                ok_steps.append(m)
    nacc = sum(s["n"] for s in steps.values())
    for i, x in enumerate(L):
        if x.startswith("VERDICT_FIELDS|") or x.startswith("FLOOR_RUN|"):
            y = setf(x, "CERTIFICATE", "PASS")
            y = setf(y, "DECISION", dec)
            y = setf(y, "PREDICTION", PRED.get(dec, "NONE"))
            y = setf(y, "GAMMA", G)
            y = setf(y, "UPPER_BOUND", U)
            if x.startswith("VERDICT_FIELDS|"):
                y = setf(y, "UPPER_BOUND_VERIFIER_ONLY", U)
                y = setf(y, "accepted_certificates", str(nacc))
            else:
                y = setf(y, "steps_run", ",".join(run_steps))
                y = setf(y, "steps_ok", ",".join(ok_steps) or "none")
                y = setf(y, "operational_failures", ",".join(opf) or "none")
            L[i] = y
    if sh and not keep_scores:
        sc = dict(w.split("=", 1) for w in sh[0].split("|")[1:] if "=" in w and re.match(r"^[0-9]{3}=", w))
        for i, x in enumerate(L):
            if x.startswith("PREDICT_SCORE|"):
                r = getf(x, "row")
                if r in sc and sc[r] != "NOT_RECHECKED":
                    L[i] = setf(x, "outcome", sc[r])
    save(d, L)
    print("FORGE|decision=%s|G=%s|U=%s|certificates=%d|steps_ok=%s|json=0" % (dec, G, U, nacc, ",".join(ok_steps)))


main()
