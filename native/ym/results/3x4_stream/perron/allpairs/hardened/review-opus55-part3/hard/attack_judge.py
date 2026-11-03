# Attacks compare_hardened_run.py with outputs a run could not print, or forms its field-by-field reading may not see. Builds the good output with the author's own test code.
# Each case states what this seat predicts: pass means the judge exits 0 on it. REVIEW.hbp holds this file's hash before it runs.
# usage: attack_judge.py JUDGE TEST_SCRIPT ORIGINAL_OUT TMP_DIR OUT_HBP  Integer only, json=0.
import hashlib, os, re, subprocess, sys

JUDGE, TEST, ORIG, TMP, OUT = sys.argv[1:6]
os.makedirs(TMP, exist_ok=True)
orig = open(ORIG, "rb").read().decode()
t = open(TEST, encoding="utf-8").read().replace("\r\n", "\n")
a, b = t.index("EXE_HASH ="), t.index("GOOD = good_output()")
ns = {"orig": orig}
exec(t[a:b], ns)
GOOD = ns["good_output"]()
ROWS = GOOD.splitlines(True)
FINAL = ROWS[4]
op, ep, xp = TMP + "/out", TMP + "/err", TMP + "/exe"
log = open(OUT, "w", encoding="utf-8", newline="\n")
bad = 0


def judge(body, code="0", err=b"", extra=()):
    open(op, "wb").write(body if isinstance(body, bytes) else body.encode())
    open(ep, "wb").write(err)
    r = subprocess.run([sys.executable, "-I", "-X", "utf8", JUDGE, ORIG, op, code, ep] + list(extra), capture_output=True, text=True)
    rows = r.stdout.splitlines()
    done = rows[-1] if rows else ""
    failed = done.split("|failed=")[1].split("|")[0] if done.startswith("HARDENED_COMPARE_DONE|") else "-"
    return r.returncode, failed, r.stdout, r.stderr[-120:].replace("\n", " ")


def case(name, want_pass, body, **kw):
    global bad
    code, failed, _, err = judge(body, **kw)
    ok = (code == 0) == want_pass
    bad += 0 if ok else 1
    log.write("JUDGE_ATTACK|case=%s|predicted=%s|exit=%d|failed=%s|met=%d|json=0\n" % (name, "pass" if want_pass else "fail", code, failed, int(ok)))


def final(new):
    return "".join(ROWS[:4]) + new


case("good", True, GOOD)
# A false value, followed by the true one: fields() keeps the last.
for key, false, true in (("value_mismatch", "5", "0"), ("store_identity", "FAIL", "PASS"), ("verdict", "FAIL", "PASS"), ("padding_nonzero", "9", "0"), ("payload_merkle", "0" * 64, "ec03c5f8ea5abd37ed8f80e0e9e7f00e37840a753f33a1008fbd090b18072a0b")):
    assert "|%s=%s|" % (key, true) in FINAL
    case("repeated_key_false_then_true_%s" % key, True, final(FINAL.replace("|%s=%s|" % (key, true), "|%s=%s|%s=%s|" % (key, false, key, true))))
    case("repeated_key_true_then_false_%s" % key, False, final(FINAL.replace("|%s=%s|" % (key, true), "|%s=%s|%s=%s|" % (key, true, key, false))))
case("repeated_key_in_a_pass_row", True, ROWS[0].replace("|value_mismatch=0|", "|value_mismatch=9|value_mismatch=0|") + "".join(ROWS[1:]))
case("a_field_no_tool_prints", True, final(FINAL.replace("|verdict=PASS|", "|verdict=PASS|note=edited_by_hand|")))
parts = FINAL.rstrip("\n").split("|")
case("final_row_fields_reversed", False, final("|".join([parts[0]] + parts[:0:-1]) + "\n"))
mid = parts[1:]
case("final_row_fields_rotated_json_last", True, final("|".join([parts[0]] + mid[-2:-1] + mid[:-2] + mid[-1:]) + "\n"))
case("crlf_line_ends", True, GOOD.replace("\n", "\r\n"))
case("no_final_newline", True, GOOD[:-1])
case("blank_line_at_the_end", False, GOOD + "\n")
case("byte_order_mark", False, b"\xef\xbb\xbf" + GOOD.encode())
case("secs_not_a_number", True, re.sub(r"\|secs=[0-9]+\|", "|secs=abc|", GOOD))
case("secs_negative", True, re.sub(r"\|secs=[0-9]+\|", "|secs=-5|", GOOD))
case("exe_field_gone_without_exe_option", True, final(re.sub(r"\|exe_sha256=[0-9a-z]+", "", FINAL)))
case("bad_utf8_in_an_extra_field", True, "".join(ROWS[:4]).encode() + FINAL.encode().replace(b"|verdict=PASS|", b"|x=" + bytes([255, 254]) + b"|verdict=PASS|"))
case("form_feed_inside_a_row", False, final(FINAL.replace("|verdict=PASS|", "|\x0cverdict=PASS|")))
case("exit_code_00", False, GOOD, code="00")
case("stderr_one_byte", False, GOOD, err=b"\n")
# --exe.
exe = b"any file at all"
open(xp, "wb").write(exe)
h = hashlib.sha256(exe).hexdigest()
named = re.sub(r"\|exe_sha256=[0-9a-z]+", "|exe_sha256=" + h, FINAL)
case("exe_named_is_any_file_the_output_names", True, final(named), extra=["--exe", xp])
case("exe_option_with_no_value", False, GOOD, extra=["--exe"])
# Output with a correct count but in another window order is caught by windows and by the original's rows.
case("pass_rows_swapped", False, ROWS[1] + ROWS[0] + "".join(ROWS[2:]))
# The normalised hash it prints is the same for every run that differs only in secs; it is printed, and compared with nothing.
_, _, o1, _ = judge(GOOD)
_, _, o2, _ = judge(re.sub(r"\|secs=[0-9]+\|", "|secs=7|", GOOD))
n1 = re.search(r"normalised_sha256=([0-9a-f]+)", o1).group(1)
n2 = re.search(r"normalised_sha256=([0-9a-f]+)", o2).group(1)
_, _, o3, _ = judge(final(FINAL.replace("|verdict=PASS|", "|verdict=PASS|note=edited_by_hand|")))
n3 = re.search(r"normalised_sha256=([0-9a-f]+)", o3).group(1)
log.write("JUDGE_NORMALISED|good=%s|secs_only_equal=%d|edited_row_differs=%d|judge_compares_it=0|json=0\n" % (n1, int(n1 == n2), int(n1 != n3)))
for p in (op, ep, xp):
    os.remove(p)
log.write("JUDGE_ATTACK_DONE|not_met=%d|json=0\n" % bad)
log.close()
print("JUDGE_ATTACK_DONE|not_met=%d|json=0" % bad)
sys.exit(1 if bad else 0)
