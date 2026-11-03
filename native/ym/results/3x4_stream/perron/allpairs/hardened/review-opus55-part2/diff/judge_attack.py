# Attacks compare_pin_run.py with faults the author's test file leaves out. Every field of every row in turn, row edits, and a tampered ORIGINAL beside a tampered output.
# usage: judge_attack.py JUDGE ORIGINAL_OUT PIN_OUT OUT_HBP   Integer only, json=0.
import os, re, subprocess, sys

JUDGE, ORIG, PIN, OUT = sys.argv[1:5]
work = os.path.dirname(os.path.abspath(OUT)) + "/judge"
os.makedirs(work, exist_ok=True)
orig = open(ORIG, "rb").read().decode()
pin = open(PIN, "rb").read().decode()
lines = orig.splitlines(True)
log = open(OUT, "w", encoding="utf-8", newline="\n")
bad = 0


def judge(new_text, orig_text=orig, code="0", err=b"", extra=True):
    op, np, ep = work + "/orig", work + "/new", work + "/err"
    open(op, "wb").write(orig_text.encode())
    open(np, "wb").write(new_text.encode())
    open(ep, "wb").write(err)
    a = [sys.executable, "-I", "-X", "utf8", JUDGE, op, np] + ([code, ep] if extra else [])
    r = subprocess.run(a, capture_output=True, text=True)
    rows = r.stdout.splitlines()
    done = bool(rows) and rows[-1].startswith("PIN_COMPARE_DONE|")
    failed = int(rows[-1].split("failed=")[1].split("|")[0]) if done else -1
    return r.returncode, failed, done


def expect(name, want_pass, *a, **k):
    global bad
    code, failed, done = judge(*a, **k)
    ok = (code == 0 and failed == 0) if want_pass else code != 0
    bad += 0 if ok else 1
    log.write("JUDGE_CASE|case=%s|should_pass=%d|exit=%d|failed=%d|done_row=%d|met=%d|json=0\n" % (name, int(want_pass), code, failed, int(done), int(ok)))
    log.flush()


expect("pin_run_as_committed", True, pin)
expect("original_copied_as_the_run", True, orig)
expect("original_copied_with_secs_invented", True, re.sub(r"\|secs=[0-9]+\|", "|secs=1|", orig))
expect("crlf_output", True, orig.replace("\n", "\r\n"))
# Every value of every row, one at a time, except secs and json.
tried = caught = 0
for li, ln in enumerate(lines):
    parts = ln.rstrip("\n").split("|")
    for pi, part in enumerate(parts):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        if k in ("secs", "json"):
            continue
        for nv in (v + "1", "0" if v != "0" else "1"):
            np = list(parts)
            np[pi] = k + "=" + nv
            text = "".join(lines[:li]) + "|".join(np) + "\n" + "".join(lines[li + 1:])
            code, failed, done = judge(text)
            tried += 1
            caught += code != 0
log.write("JUDGE_EVERY_FIELD|variants=%d|caught=%d|json=0\n" % (tried, caught))
bad += tried - caught
# Rows.
expect("row_deleted_last", False, "".join(lines[:-1]))
expect("row_duplicated", False, orig + lines[-1])
expect("pass_rows_swapped", False, lines[1] + lines[0] + "".join(lines[2:]))
expect("no_final_newline", False, orig.rstrip("\n"))
expect("extra_blank_line", False, orig + "\n")
expect("extra_unknown_row", False, orig + "NOTE|x=1|json=0\n")
expect("bom_at_the_start", False, "﻿" + orig)
expect("secs_removed", False, orig.replace("|secs=2704|", "|"))
expect("secs_word", False, orig.replace("|secs=2704|", "|secs=abc|"))
expect("secs_negative", False, orig.replace("|secs=2704|", "|secs=-1|"))
expect("extra_secs_field", False, orig.replace("|secs=2704|", "|secs=2704|secs=1|"))
expect("merkle_value_appended", False, orig.replace("|merkle=PASS|verdict", "|merkle=PASS|x=1|verdict"))
expect("number_is_a_word", False, orig.replace("|n=45508080|", "|n=abc|"))
expect("pass_row_lost_a_key", False, orig.replace("rows_from=0|", "", 1))
expect("exit_code_absent_from_args_but_output_clean", True, orig, extra=False)
expect("exit_1", False, orig, code="1")
expect("exit_0_with_space", False, orig, code="0 ")
expect("stderr_one_byte", False, orig, err=b"x")
# The ORIGINAL is read from its path with no hash. A fault made in both files, in a field the judge holds no constant for.
for name, a, b in [("flats", "|flats=7|", "|flats=8|"), ("flat_w", "|flat_w=1,3,2,3,3,2,4|", "|flat_w=4,3,2,3,3,2,1|"), ("flat_w_sum", "|flat_w_sum=18|", "|flat_w_sum=19|"), ("cap", "|cap_entries=470000000|", "|cap_entries=1|")]:
    t = orig.replace(a, b)
    expect("same_fault_in_both_files_" + name, True, t, orig_text=t)
expect("same_fault_in_both_files_pairs", False, orig.replace("|pairs=1632625631|", "|pairs=1632625630|"), orig_text=orig.replace("|pairs=1632625631|", "|pairs=1632625630|"))
for f in ("orig", "new", "err"):
    os.remove(work + "/" + f)
os.rmdir(work)
log.write("JUDGE_ATTACK_DONE|not_met=%d|json=0\n" % bad)
log.close()
print("JUDGE_ATTACK_DONE|tried_every_field=%d|caught=%d|not_met=%d|json=0" % (tried, caught, bad))
sys.exit(1 if bad else 0)
