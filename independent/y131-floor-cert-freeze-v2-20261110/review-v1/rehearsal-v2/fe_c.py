

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
