# Copies each correction-round rehearsal's stdout, receipt and side files into review-v2/rehearsal-v2b and writes
# /root/floor-v2/rehb/SUMMARY.txt (one entry per run: name, arguments, exit code, fields of the final line).
import os, re, shutil, sys
O = "/root/floor-v2/rehb/"
D = "/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/review-v2/rehearsal-v2b/"
T = "/mnt/c/tmp/opus55/floor-v2/"
os.makedirs(D, exist_ok=True)
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
    for side in (".bystander.txt", ".attack.txt"):
        if os.path.exists(O + n + side):
            shutil.copyfile(O + n + side, D + n + side)
    pc = O + n + "/log/pincheck_closing.txt"
    if (n.startswith("EV") or n in ("Y1", "Y1b", "P1")) and os.path.exists(pc):
        shutil.copyfile(pc, D + n + ".pincheck_closing.txt")
    lines = txt.split("\n")
    fr = [l for l in lines if l.startswith("FLOOR_RUN|")]
    assert len(fr) == 1 and [l for l in lines if l][-1] == fr[0], (n, len(fr))
    f = dict(x.split("=", 1) for x in fr[0].split("|")[1:] if "=" in x)
    args = open(O + n + ".args").read().strip().replace(O, "OUT/").replace("/root/floor-v2/", "")
    s = n + ":" + args + ":exit=" + open(O + n + ".rc").read().strip() + "," + ",".join("%s=%s" % (k, f[k]) for k in keep if k in f)
    acc = [l for l in (open(rc).read().split("\n") if os.path.exists(rc) else []) if l.startswith("ACCEPTED|")]
    if acc: s += ",receipt_accepted_per_step=" + "/".join(re.search(r"m0=(\d+)", x).group(1) + ":" + re.search(r"count=(\d+)", x).group(1) for x in acc)
    dec = [l for l in lines if l.startswith("DECISION|")]
    st = [l for l in lines + (open(rc).read().split("\n") if os.path.exists(rc) else []) if l.startswith("STEP|") and ("resource_limit=EXCEEDED" in l or "no_valid_verification_record" in l or "fallback=PROHIBITED" in l)]
    if st:
        x = st[0]; m = re.search(r"\|m0=(\d+)", x)
        s += ",step_line=m0_" + (m.group(1) if m else "NA") + ("_resource_limit_EXCEEDED" if "resource_limit=EXCEEDED" in x else "") + ("_fallback_PROHIBITED" if "fallback=PROHIBITED" in x else "") + ("_no_valid_verification_record" if "no_valid_verification_record" in x else "")
    if dec: s += ",decisions=" + "/".join(re.search(r"(?:decision|state)=([A-Z]+)", x).group(1) + ">" + re.search(r"next=(\w+)", x).group(1) for x in dec)
    inv = [l for l in lines if l.startswith("INVOKE|") and "time_limit_hit=1" in l]
    if inv: s += ",time_limit_hit=" + "/".join(re.search(r"kind=(\w+)", x).group(1) + "_rc" + re.search(r"\|rc=(\d+)", x).group(1) + "_own_process_group" + re.search(r"own_process_group=(\d)", x).group(1) for x in inv)
    rr = [l for l in lines if l.startswith("NOTE|rerun_once")]
    s += ",reruns=%d" % len(rr) if (rr or inv) else ""
    b = O + n + ".bystander.txt"
    if os.path.exists(b):
        s += ",bystander_named_floorcert_alive_after=" + re.search(r"alive_after=(\d)", open(b).read()).group(1)
    a = O + n + ".attack.txt"
    if os.path.exists(a):
        at = open(a).read()
        s += ",changed_while_running=" + re.search(r"file=([^|]+)", at).group(1) + ",launcher=" + {"123aee3576084a06": "row_114", "7de05245684805b8": "the_launcher_of_the_first_version_2_commit"}.get(re.search(r"launcher_sha16=(\w+)", at).group(1), "the_file_changed_by_this_run") + ",replaced_gate_calls=" + re.search(r"fake_gate_calls=(\d+)", at).group(1)
    ig = [l for l in lines if l.startswith("INTEGRITY|")]
    if ig: s += ",integrity_line=1"
    assert " " not in s and "|" not in s, s
    out.append(s)
if os.path.exists(O + "RCHECK.txt"):
    shutil.copyfile(O + "RCHECK.txt", D + "RCHECK.txt")
    rl = [l for l in open(O + "RCHECK.txt").read().split("\n") if l]
    out.append("RC:floor_eval.py_rcheck_called_directly:" + ",".join(re.search(r"r=([^|]*)", l).group(1) + ">exit" + re.search(r"exit=(\d+)", l).group(1) for l in rl))
if os.path.exists(O + "LIMCHECK.txt"):
    shutil.copyfile(O + "LIMCHECK.txt", D + "LIMCHECK.txt")
    rl = [l for l in open(O + "LIMCHECK.txt").read().split("\n") if l]
    out.append("LIM:floor_eval.py_opfail_called_directly_with_a_lowered_limit:" + "/".join(re.search(r"args=([^|]*)", l).group(1).replace(",", "+") + ">exit" + re.search(r"exit=(\d+)", l).group(1) for l in rl))
for k in ("reh_b.sh", "reh_sum_b.py"):
    open(D + k, "w", newline="\n").write(open(T + k).read().replace("\r", ""))
open(O + "SUMMARY.txt", "w", newline="\n").write("\n".join(out) + "\n")
print("\n".join(out))
