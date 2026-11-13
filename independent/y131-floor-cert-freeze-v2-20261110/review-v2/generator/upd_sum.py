import io
T="C:/tmp/opus55/floor-v2/"
s=io.open(T+"reh_sum_b.bak1",encoding="utf-8",newline="").read().replace("\r\n","\n")
def rep(a,b):
    global s
    assert s.count(a)==1,(s.count(a),a[:60]); s=s.replace(a,b)
rep('"steps_run", "steps_ok", "operational_failures", "accepted_certificates", "stop", "closing_pin_check", "certificate_commands_run")',
    '"steps_run", "steps_ok", "operational_failures", "accepted_certificates", "verification_records", "stop", "rule", "closing_pin_check", "private_tools_check", "certificate_commands_run",\n        "result", "comparison", "gamma_cert", "U_all")')
rep(r'''    if n.startswith("EV") and os.path.exists(pc):''', r'''    if (n.startswith("EV") or n in ("Y1", "Y1b", "P1")) and os.path.exists(pc):''')
rep(r'''    if dec: s += ",decisions="''', r'''    st = [l for l in lines + (open(rc).read().split("\n") if os.path.exists(rc) else []) if l.startswith("STEP|") and ("resource_limit=EXCEEDED" in l or "no_valid_verification_record" in l or "fallback=PROHIBITED" in l)]
    if st:
        x = st[0]; m = re.search(r"\|m0=(\d+)", x)
        s += ",step_line=m0_" + (m.group(1) if m else "NA") + ("_resource_limit_EXCEEDED" if "resource_limit=EXCEEDED" in x else "") + ("_fallback_PROHIBITED" if "fallback=PROHIBITED" in x else "") + ("_no_valid_verification_record" if "no_valid_verification_record" in x else "")
    if dec: s += ",decisions="''')
rep(r'''re.search(r"decision=([A-Z]+)", x).group(1) + ">"''', r'''re.search(r"(?:decision|state)=([A-Z]+)", x).group(1) + ">"''')
rep(r'''        s += ",changed_while_running=" + re.search(r"file=([^|]+)", open(a).read()).group(1)''',
    r'''        at = open(a).read()
        s += ",changed_while_running=" + re.search(r"file=([^|]+)", at).group(1) + ",launcher=" + {"123aee3576084a06": "row_114", "7de05245684805b8": "the_launcher_of_the_first_version_2_commit"}.get(re.search(r"launcher_sha16=(\w+)", at).group(1), "the_file_changed_by_this_run") + ",replaced_gate_calls=" + re.search(r"fake_gate_calls=(\d+)", at).group(1)''')
rep(r'''for k in ("reh_b.sh", "reh_sum_b.py"):''', r'''if os.path.exists(O + "LIMCHECK.txt"):
    shutil.copyfile(O + "LIMCHECK.txt", D + "LIMCHECK.txt")
    rl = [l for l in open(O + "LIMCHECK.txt").read().split("\n") if l]
    out.append("LIM:floor_eval.py_opfail_called_directly_with_a_lowered_limit:" + "/".join(re.search(r"args=([^|]*)", l).group(1).replace(",", "+") + ">exit" + re.search(r"exit=(\d+)", l).group(1) for l in rl))
for k in ("reh_b.sh", "reh_sum_b.py"):''')
io.open(T+"reh_sum_b.py","w",encoding="utf-8",newline="\n").write(s)
print("ok")
