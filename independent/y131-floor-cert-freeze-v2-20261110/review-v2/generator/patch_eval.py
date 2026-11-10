# Applies the second correction-round changes to final/tools/floor_eval.py by exact-string replacement:
# private tool copies checked by the evaluator, an invocation record required for every accepted certificate,
# RESOURCE_LIMIT_EXCEEDED as a certificate failure with precedence over an operational failure, a test-mode limit.
import io
P = "/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/final/tools/floor_eval.py"
s = io.open(P, encoding="utf-8", newline="").read()
assert "\r" not in s


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


rep('''# accepted bounds only) and PREDICTION (CONFIRMED for ABOVE, FALSIFIED for BELOW, UNRESOLVED otherwise).
''', '''# accepted bounds only) and PREDICTION (CONFIRMED for ABOVE, FALSIFIED for BELOW, UNRESOLVED otherwise).
# The launcher runs this file from a private directory that also holds its copies of gate_required.sh, cert_gate.py,
# indep_verify.py and peak_rss.py (argument tools=DIR); step and final hash those copies against rows 020 019 021
# 103 115, and step accepts a certificate only with the launcher's INVOKE record of that verifier call (exit 0, log
# hash, argv naming the private gate driver). A completed process at or over the memory limit of row 011 gives
# status FAIL with RESOURCE_LIMIT_EXCEEDED; subcommand opfail applies that before a crash or a time limit may count
# as an operational failure. limkb=N lowers the limit in test mode only.
''')
rep('''VGATES = ["r_policy",''', '''TOOLS = [("020", "gate_required.sh"), ("019", "py/cert_gate.py"), ("021", "py/indep_verify.py"),
         ("103", "peak_rss.py"), ("115", "floor_eval.py")]
RLE = "RESOURCE_LIMIT_EXCEEDED"
VGATES = ["r_policy",''')
rep('''# ------------------------------------------------------------------ rcheck: test-mode r stays away from 9
''', '''def tools_check(R, tools):
    """The private copies the launcher executes, hashed against the PIN rows; this file must be one of them."""
    bad = []
    for rid, rel in TOOLS:
        p = os.path.join(tools, rel)
        if rid not in R or not os.path.isfile(p) or sha(p) != R[rid][1].get("value"):
            bad.append("row_%s:private_copy_%s_differs_from_pin" % (rid, rel.replace("/", "_")))
    if os.path.realpath(sys.argv[0]) != os.path.realpath(os.path.join(tools, "floor_eval.py")):
        bad.append("row_115:evaluator_runs_outside_the_private_directory")
    return bad


def invocation(lg, m, kind, lb, want_argv):
    """True when the last INVOKE line of run.log for this log names exit 0, no time limit, a process group of its
    own, the hash of the log as it is read here and an argv that starts with want_argv."""
    hit = []
    for x in pick(lines(lg + "/run.log"), "INVOKE|"):
        f = fld(x)
        if f.get("m0") == str(m) and f.get("kind") == kind and re.match(r"^log/%s_a[12]\\.txt$" % re.escape(lb), f.get("log", "")):
            hit.append((f, x))
    final = lg + "/%s.txt" % lb
    if not hit or not os.path.isfile(final):
        return False
    f, x = hit[-1]
    am = re.search(r"\\|argv=(.*)\\|json=0$", x)
    return (f.get("rc") == "0" and f.get("time_limit_hit") == "0" and f.get("own_process_group") == "1"
            and f.get("log_sha256") == sha(final) and am is not None
            and (am.group(1) == want_argv or am.group(1).startswith(want_argv + " ")))


# ------------------------------------------------------------------ rcheck: test-mode r stays away from 9
''')
# prereq memory line
rep('''            if not mm or int(mm.group(1)) >= LIM_KB:
                bad.append("verifier_MEM_not_under_2GB")''', '''            if not mm or int(mm.group(1)) >= LIM_KB:
                bad.append("verifier_MEM_at_or_over_%dkB" % LIM_KB)''')
rep('''    kb = int(f.get("kB", "0")) if f.get("kB", "").isdigit() else LIM_KB
    if kb >= LIM_KB:
        bad.append("row_011:%s_PEAK_RSS_not_under_2GB" % what)
    return kb
''', '''    if not f.get("kB", "").isdigit():
        bad.append("row_011:%s_PEAK_RSS_unreadable" % what)
        return 0
    kb = int(f["kB"])
    if kb >= LIM_KB:
        bad.append("row_011:%s:%s_PEAK_RSS_%dkB_limit_%dkB" % (RLE, what, kb, LIM_KB))
    return kb
''')
rep('''    for rid in ("019", "020", "103"):
        pf = os.path.join(a["root"], R[rid][1]["path"])
        if not os.path.isfile(pf) or sha(pf) != R[rid][1]["value"]:
            bad.append("row_%s:file_on_disk_differs_from_pin" % rid)
''', '''    for rid in ("019", "020", "103"):
        pf = os.path.join(a["root"], R[rid][1]["path"])
        if not os.path.isfile(pf) or sha(pf) != R[rid][1]["value"]:
            bad.append("row_%s:file_on_disk_differs_from_pin" % rid)
    # the copies that were executed (private directory of the launcher), and the launcher's record of each command
    tools = a["tools"]
    bad.extend(tools_check(R, tools))
    if not invocation(lg, m, "rowhash", "m%d_rowhash" % m, "python3 -I -B %s/peak_rss.py %s/floorcert rowhash --m0 %d" % (tools, tools, m)):
        bad.append("row_008:no_valid_invocation_record_rowhash")
    if not invocation(lg, m, "cert", "m%d_cert" % m, "python3 -I -B %s/peak_rss.py %s/floorcert cert --m0 %d" % (tools, tools, m)):
        bad.append("row_008:no_valid_invocation_record_cert")
    nrec = 0
''')
rep('''                row["gate"] = "PASS"
                gf = fld(gr[0])
''', '''                row["gate"] = "PASS"
                gf = fld(gr[0])
                # an actual verifier invocation: the launcher's INVOKE record with exit 0 for exactly this log
                if invocation(lg, m, "gate", "m%d_gate_%s" % (m, base), "bash %s/gate_required.sh %s" % (tools, path)):
                    nrec += 1
                else:
                    cb.append("row_053:no_valid_verification_record")
                    row["gate"] = "NO_RECORD"
''')
rep('''                    kb = int(mm.group(1)) if mm else LIM_KB
                    mem_max = max(mem_max, kb)
                    if kb >= LIM_KB:
                        cb.append("row_011:verifier_MEM_not_under_2GB")
''', '''                    if not mm:
                        cb.append("row_011:verifier_MEM_unreadable")
                        continue
                    kb = int(mm.group(1))
                    mem_max = max(mem_max, kb)
                    if kb >= LIM_KB:
                        cb.append("row_011:%s:verifier_MEM_%dkB_limit_%dkB" % (RLE, kb, LIM_KB))
''')
rep('''    o = ["STEP|m0=%d|status=%s|accepted=%d|certificates=%d|G=%s|U=%s|U_verifier_only=%s|writer_peak_kB=%d|verifier_mem_max_kB=%d|rowhash=%s|keyshash=%s|rowhash_pin=%s|bad=%s|json=0"
         % (m, "OK" if ok else "FAIL", len(acc), len(crows), rs(G), rs(U), rs(Uv), max(pk_r, pk_c), mem_max,
''', '''    res = "EXCEEDED" if any(RLE in y for y in bad) else "HELD"
    o = ["STEP|m0=%d|status=%s|accepted=%d|certificates=%d|G=%s|U=%s|U_verifier_only=%s|writer_peak_kB=%d|verifier_mem_max_kB=%d|resource_limit=%s|limit_kB=%d|verification_records=%d|rowhash=%s|keyshash=%s|rowhash_pin=%s|bad=%s|json=0"
         % (m, "OK" if ok else "FAIL", len(acc), len(crows), rs(G), rs(U), rs(Uv), max(pk_r, pk_c), mem_max, res, LIM_KB, nrec,
''')
rep('''# ------------------------------------------------------------------ decide / final
''', '''# ------------------------------------------------------------------ opfail: a crash or a time limit inside a step
def cmd_opfail(a):
    """A command of this step crashed or ran into the time limit. Fallback is open only while no REQUIRED gate has
    failed: a process of this step that completed (exit 0, or a verifier that printed its verdict) at or over the
    memory limit makes the step FAIL with RESOURCE_LIMIT_EXCEEDED, and the run stops."""
    m = int(a["m0"])
    lg = a["out"] + "/log"
    bad = []
    for nm in sorted(os.listdir(lg)):
        if not re.match(r"^m%d_(rowhash|cert|rowsonly|gate_.*)\\.txt$" % m, nm) or re.search(r"_a[12]\\.txt$", nm):
            continue
        ls = lines(lg + "/" + nm)
        what = nm[:-4].replace("|", "_")
        for x in pick(ls, "PEAK_RSS|"):
            f = fld(x)
            if f.get("exit") == "0" and f.get("kB", "").isdigit() and int(f["kB"]) >= LIM_KB:
                bad.append("row_011:%s:%s_PEAK_RSS_%skB_limit_%dkB" % (RLE, what, f["kB"], LIM_KB))
        if pick(ls, "VERDICT|"):
            for x in pick(ls, "MEM|"):
                mm = re.match(r"^MEM\\|([0-9]+)kB", x)
                if mm and int(mm.group(1)) >= LIM_KB:
                    bad.append("row_011:%s:%s_MEM_%skB_limit_%dkB" % (RLE, what, mm.group(1), LIM_KB))
    if bad:
        st = "STEP|m0=%d|status=FAIL|accepted=0|certificates=0|resource_limit=EXCEEDED|limit_kB=%d|operational_event=%s|fallback=PROHIBITED|bad=%s|json=0" % (m, LIM_KB, a["why"], ";".join(bad))
    else:
        st = "STEP|m0=%d|status=OPFAIL|accepted=0|certificates=0|resource_limit=HELD|limit_kB=%d|bad=%s|json=0" % (m, LIM_KB, a["why"])
    with open(lg + "/m%d_step.hbp" % m, "w", encoding="utf-8", newline="\\n") as fh:
        fh.write(st + "\\n")
    print(st)


# ------------------------------------------------------------------ decide / final
''')
rep('''        d = {"m": m, "status": f["status"], "G": None, "U": None, "Uv": None, "certs": [], "line": st[0],
''', '''        d = {"m": m, "status": f["status"], "G": None, "U": None, "Uv": None, "certs": [], "line": st[0],
             "res": f.get("resource_limit", "HELD"),
''')
rep('''    if any(s["status"] == "FAIL" for s in S):
        return ("FAIL", "STOP", "row_008", G, U, Uv)
''', '''    if any(s["status"] == "FAIL" and s["res"] == "EXCEEDED" for s in S):
        return ("FAIL", "STOP", "row_011_resource_limit_exceeded_fallback_prohibited_row_122", G, U, Uv)
    if any(s["status"] == "FAIL" for s in S):
        return ("FAIL", "STOP", "row_008", G, U, Uv)
''')
rep('''    if pbad:
        stop = "FAIL_closing_pin_check_%d_rows_differ_row_010" % pbad
''', '''    if pbad:
        stop = "FAIL_closing_pin_check_%d_rows_differ_row_010" % pbad
    tb = tools_check(R, a["tools"])
    if tb:
        stop = "FAIL_private_tool_copies_" + "_".join(sorted(set(y.split(":")[0] for y in tb)))
''')
rep('''        cert, why, dec = "FAIL", "REQUIRED_OR_INTEGRITY_FAILURE_ROW_008", "UNRESOLVED"
        G = U = Uv = None
''', '''        cert, why, dec = "FAIL", "REQUIRED_OR_INTEGRITY_FAILURE_ROW_008", "UNRESOLVED"
        if any(s["status"] == "FAIL" and s["res"] == "EXCEEDED" for s in S):
            why = RLE
        G = U = Uv = None
''')
rep('''|closing_pin_check=rows_%d_bad_%d''', '''|closing_pin_check=rows_%d_bad_%d|private_tools_check=files_%d_bad_%d''')
rep(''' acc, stop, rule, pn, pbad,
''', ''' acc, stop, rule, pn, pbad, len(TOOLS), len(tb),
''')
rep('''CMDS = {"rcheck": cmd_rcheck, "pins": cmd_pins, "prereq": cmd_prereq, "step": cmd_step, "decide": cmd_decide, "final": cmd_final}
if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
    die("usage: floor_eval.py rcheck|pins|prereq|step|decide|final key=value ...")
CMDS[sys.argv[1]](args(sys.argv[2:]))
''', '''CMDS = {"rcheck": cmd_rcheck, "pins": cmd_pins, "prereq": cmd_prereq, "step": cmd_step, "opfail": cmd_opfail,
        "decide": cmd_decide, "final": cmd_final}
if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
    die("usage: floor_eval.py rcheck|pins|prereq|step|opfail|decide|final key=value ...")
ARGS = args(sys.argv[2:])
if "limkb" in ARGS:
    # a lowered memory limit exists for rehearsals only; the frozen run has the limit of row 011 and no other
    if ARGS.get("mode") != "test" or not ARGS["limkb"].isdigit() or not 1 <= int(ARGS["limkb"]) <= LIM_KB:
        die("limkb is a test-mode argument between 1 and %d" % LIM_KB)
    LIM_KB = int(ARGS["limkb"])
CMDS[sys.argv[1]](ARGS)
''')
rep('x.startswith("INJECTED|") or x.startswith("NOTE|"):', 'x.startswith("INJECTED|") or x.startswith("NOTE|") or x.startswith("TOOL"):')
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched", len(s.split("\n")))
