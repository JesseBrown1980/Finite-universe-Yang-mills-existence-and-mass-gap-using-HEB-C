# Copies each rehearsal's stdout, receipt and side files of the second correction round into review-v3/rehearsal-v2c and writes
# /root/floor-v2/rehc/SUMMARY.txt (one entry per run: name, arguments, exit code, fields of the final line).
import hashlib, os, re, shutil, subprocess, sys
O = "/root/floor-v2/rehc/"
P = "/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/"
D = P + "review-v3/rehearsal-v2c/"
T = "/mnt/c/tmp/opus55/floor-v2/"
os.makedirs(D, exist_ok=True)
NEW16 = hashlib.sha256(open(P + "final/tools/run_floor.sh", "rb").read()).hexdigest()[:16]
OLD16 = "123aee3576084a06"
keep = ("CERTIFICATE", "PREDICTION", "DECISION", "GAMMA", "UPPER_BOUND", "certificate_reason", "stage", "reason", "state_row_012",
        "steps_run", "steps_ok", "operational_failures", "accepted_certificates", "verification_records", "stop", "rule", "closing_pin_check", "private_tools_check", "certificate_commands_run",
        "result", "comparison", "gamma_cert", "U_all")
out = []
for n in sys.argv[1:]:
    txt = open(O + n + ".stdout.txt").read().replace("\r", "")
    open(D + n + ".stdout.txt", "w", newline="\n").write(txt)
    rc = O + n + "/FLOOR-RUN-RECEIPT.hbp"
    if os.path.exists(rc):
        shutil.copyfile(rc, D + n + ".FLOOR-RUN-RECEIPT.hbp")
    for side in (".bystander.txt", ".attack.txt", ".race.txt"):
        if os.path.exists(O + n + side):
            open(D + n + side, "w", newline="\n").write(open(O + n + side).read().replace("\r", ""))
    pc = O + n + "/log/pincheck_closing.txt"
    if (n.startswith("EV") or n in ("Y1", "Y1b")) and os.path.exists(pc):
        shutil.copyfile(pc, D + n + ".pincheck_closing.txt")
    lines = txt.split("\n")
    fr = [l for l in lines if l.startswith("FLOOR_RUN|")]
    assert len(fr) == 1 and [l for l in lines if l][-1] == fr[0], (n, len(fr))
    f = dict(x.split("=", 1) for x in fr[0].split("|")[1:] if "=" in x)
    code = open(O + n + ".rc").read().strip()
    # exit codes of this round (row 128); the X entries ran the launcher of 3b91d1a0 with its own codes
    if not n.startswith("X"):
        want = {"PASS": {"CONFIRMED": "0", "FALSIFIED": "3", "UNRESOLVED": "2"}.get(f.get("PREDICTION"), "?"),
                "FAIL": "4" if f.get("certificate_reason") == "NOT_STARTED" else "1"}[f["CERTIFICATE"]]
        assert code == want, (n, code, want, fr[0][:200])
    args = open(O + n + ".args").read().strip().replace(O, "OUT/").replace("/root/floor-v2/", "")
    s = n + ":" + args + ":exit=" + code + "," + ",".join("%s=%s" % (k, f[k]) for k in keep if k in f)
    rtx = open(rc).read().split("\n") if os.path.exists(rc) else []
    acc = [l for l in rtx if l.startswith("ACCEPTED|")]
    if acc: s += ",receipt_accepted_per_step=" + "/".join(re.search(r"m0=(\d+)", x).group(1) + ":" + re.search(r"count=(\d+)", x).group(1) for x in acc)
    rk = [l for l in rtx if l.startswith("RECHECK|")]
    if rtx and not n.startswith("X"): s += ",receipt_recheck_rows=%d" % len(rk)
    dec = [l for l in lines if l.startswith("DECISION|")]
    st = [l for l in lines + rtx if l.startswith("STEP|") and ("resource_limit=EXCEEDED" in l or "no_valid_verification_record" in l or "fallback=PROHIBITED" in l)]
    if st:
        x = st[0]; m = re.search(r"\|m0=(\d+)", x)
        s += ",step_line=m0_" + (m.group(1) if m else "NA") + ("_resource_limit_EXCEEDED" if "resource_limit=EXCEEDED" in x else "") + ("_fallback_PROHIBITED" if "fallback=PROHIBITED" in x else "") + ("_no_valid_verification_record" if "no_valid_verification_record" in x else "")
    lm = [l for l in lines if l.startswith("LIMIT|") and "status=EXCEEDED" in l]
    if lm: s += ",limit_line=m0_" + re.search(r"\|m0=(\d+)", lm[0]).group(1) + "_EXCEEDED_before_the_prerequisite_outcome"
    if dec: s += ",decisions=" + "/".join(re.search(r"(?:decision|state)=([A-Z]+)", x).group(1) + ">" + re.search(r"next=(\w+)", x).group(1) for x in dec)
    inv = [l for l in lines if l.startswith("INVOKE|") and "time_limit_hit=1" in l]
    if inv: s += ",time_limit_hit=" + "/".join(re.search(r"kind=(\w+)", x).group(1) + "_rc" + re.search(r"\|rc=(\d+)", x).group(1) + "_own_process_group" + re.search(r"own_process_group=(\d)", x).group(1) for x in inv)
    rr = [l for l in lines if l.startswith("NOTE|rerun_once")]
    s += ",reruns=%d" % len(rr) if (rr or inv) else ""
    tp = [l for l in lines if l.startswith("TOOLPATH|")]
    if n in ("K0", "AB", "T1"): s += ",toolpath_lines=%d,run_directory_absolute=%d" % (len(tp), 1 if any(l.startswith("RUN|") and "|out=/" in l for l in lines) or any("run_directory=/" in l for l in lines) else 0)
    b = O + n + ".bystander.txt"
    if os.path.exists(b):
        s += ",bystander_named_floorcert_alive_after=" + re.search(r"alive_after=(\d)", open(b).read()).group(1)
    a = O + n + ".attack.txt"
    if os.path.exists(a):
        at = open(a).read()
        l16 = re.search(r"launcher_sha16=(\w+)", at).group(1)
        s += ",launcher=" + {NEW16: "row_114", OLD16: "the_launcher_of_3b91d1a0"}.get(l16, "the_file_changed_by_this_run")
        m = re.search(r"file=([^|]+)", at)
        if m: s += ",changed_while_running=" + m.group(1)
        m = re.search(r"fake_gate_calls=(\d+)", at)
        if m: s += ",replaced_gate_calls=" + m.group(1)
        m = re.search(r"\|fake_calls=(\d+)", at)
        if m: s += ",planted_program_calls=" + m.group(1)
        for k in ("what", "write_into_the_private_directory_exit", "nsenter_exit", "swaps", "target_seen"):
            m = re.search(r"\|" + k + r"=([^|\n]+)", at)
            if m: s += "," + k + "=" + m.group(1)
    ig = [l for l in lines if l.startswith("INTEGRITY|")]
    if ig: s += ",integrity_line=1"
    assert " " not in s and "|" not in s, s
    assert not re.search(r"(?<![0-9a-f])[0-9a-f]{16}(?![0-9a-f])", s), s
    out.append(s)
def side(name, label, fn):
    if os.path.exists(O + name):
        shutil.copyfile(O + name, D + name)
        rl = [l for l in open(O + name).read().split("\n") if l]
        out.append(label + fn(rl))
side("RCHECK.txt", "RC:floor_eval.py_rcheck_called_directly:", lambda rl: ",".join(re.search(r"r=([^|]*)", l).group(1) + ">exit" + re.search(r"exit=(\d+)", l).group(1) for l in rl))
side("LIMCHECK.txt", "LIM:floor_eval.py_opfail_called_directly_with_a_lowered_limit:", lambda rl: "/".join(re.search(r"args=([^|]*)", l).group(1).replace(",", "+") + ">exit" + re.search(r"exit=(\d+)", l).group(1) for l in rl))
for k in ("reh_c.sh", "reh_sum_c.py", "c_atk.sh"):
    open(D + k, "w", newline="\n").write(open(T + k).read().replace("\r", ""))
for l in out: assert " " not in l and "|" not in l, l
open(O + "SUMMARY.txt", "w", newline="\n").write("\n".join(out) + "\n")
print("\n".join(out))
