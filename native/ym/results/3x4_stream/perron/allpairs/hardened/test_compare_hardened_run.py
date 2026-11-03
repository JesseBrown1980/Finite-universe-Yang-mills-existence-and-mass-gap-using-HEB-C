# Tests compare_hardened_run.py before the run it will judge. It builds the output a clean run should print, from the original run's rows and the store's
# known values, then damages every field of every row, one at a time. Each damaged copy must exit 1 with failed above 0. A copy that differs only in secs must
# exit 0, and so must a copy of the good output: the judge compares rows, and a replay is what shows a run happened. Exits 1 if any case differs.
# usage: test_compare_hardened_run.py ALLPAIRS-3x4.out OUT_FILE     Integer only, json=0.
import os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "compare_hardened_run.py")
ORIG = sys.argv[1]
orig = open(ORIG, "rb").read().decode()
EXE_HASH = "e" * 64


def rep(t, a, b):
    if t.count(a) < 1:
        raise SystemExit("no match: " + a)
    return t.replace(a, b)


def good_output():
    t = orig
    t = rep(t, "|upper_without_lower=0|merkle=PASS|", "|upper_without_lower=0|lower_repeated=0|merkle=PASS|")
    t = rep(t, "|passes=4|cap_entries=470000000|", "|passes=4|cap_requested=470000000|cap_entries=470000000|")
    t = rep(t, "|upper_without_lower=0|columns_not_ascending=", "|upper_without_lower=0|lower_repeated=0|columns_not_ascending=")
    t = rep(t, "|flat_w=1,3,2,3,3,2,4|flat_w_sum=18|", "|flat_w=1,3,2,3,3,2,4|flat_w_listed=7|flat_w_sum=18|")
    t = rep(t, "|whole_space_count=PASS|merkle=PASS|verdict=PASS|", "|whole_space_count=PASS|rooms=3356267422|header_rooms=PASS|padding_bytes=742160|padding_nonzero=0|padding=PASS|bytes_after_stream=349114368|store_identity=PASS|identity_differs=-|payload_merkle=ec03c5f8ea5abd37ed8f80e0e9e7f00e37840a753f33a1008fbd090b18072a0b|header_sha256=65dd63a89d7e1a7cdd3e7876c834c6698a01081ea7a63738e305890bee9e6a21|merkle=PASS|verdict=PASS|exe_sha256=" + EXE_HASH + "|")
    return t


GOOD = good_output()
GOOD_ROWS = GOOD.splitlines(True)
tmp = tempfile.mkdtemp(prefix="judge-")
op, ep, xp = os.path.join(tmp, "out"), os.path.join(tmp, "err"), os.path.join(tmp, "orig")
fails, cases, faults = 0, 0, 0
out = open(sys.argv[2], "w", encoding="utf-8", newline="\n")


def judge(body, code="0", err="", original=None):
    open(op, "wb").write(body.encode())
    open(ep, "wb").write(err.encode())
    r = subprocess.run([sys.executable, "-I", "-X", "utf8", TOOL, original or ORIG, op, code, ep], capture_output=True, text=True)
    rows = r.stdout.splitlines()
    failed = int(rows[-1].split("|failed=")[1].split("|")[0]) if rows and rows[-1].startswith("HARDENED_COMPARE_DONE|") else -1
    return r.returncode, failed


def expect(name, should_pass, *args, **kw):
    global fails, cases, faults
    code, failed = judge(*args, **kw)
    good = (code == 0 and failed == 0) if should_pass else (code == 1 and failed != 0)
    fails += 0 if good else 1
    cases += 1
    faults += 0 if should_pass else 1
    out.write("JUDGE_CONTROL|case=%s|should_pass=%d|exit=%d|failed=%d|met=%d|json=0\n" % (name, 1 if should_pass else 0, code, failed, 1 if good else 0))


expect("good_output", True, GOOD)
expect("only_secs_differ", True, re.sub(r"\|secs=[0-9]+\|", "|secs=999|", GOOD))
# Every field of every row, one at a time. secs is the one field allowed to differ, and exe_sha256 is judged only with --exe.
for r, row in enumerate(GOOD_ROWS):
    parts = row.rstrip("\n").split("|")
    for p, part in enumerate(parts):
        if "=" not in part:
            continue
        key = part.split("=", 1)[0]
        if key in ("secs", "exe_sha256") or (key == "json"):
            continue
        for bad in ("X", "7777777"):
            broken = list(parts)
            broken[p] = key + "=" + bad
            body = list(GOOD_ROWS)
            body[r] = "|".join(broken) + "\n"
            expect("row%d_%s_%s" % (r, key, bad), False, "".join(body))
expect("original_output_lacks_every_new_field", False, orig)
expect("one_pass_row_gone", False, "".join(x for x in GOOD_ROWS if not x.startswith("ALLPAIRS_PASS|pass=2")))
expect("one_pass_row_repeated", False, GOOD_ROWS[0] + GOOD)
expect("a_detail_row", False, GOOD_ROWS[0] + "ALLPAIRS_BAD|kind=value_mismatch|i=1|h=2|json=0\n" + "".join(GOOD_ROWS[1:]))
expect("final_row_gone", False, "".join(GOOD_ROWS[:4]))
expect("final_row_first", False, GOOD_ROWS[4] + "".join(GOOD_ROWS[:4]))
expect("empty_output", False, "")
expect("exit_code_2", False, GOOD, code="2")
expect("exit_code_1", False, GOOD, code="1")
expect("stderr_not_empty", False, GOOD, err="x\n")
# A change in both files: the original's hash is pinned, so the judge refuses it.
open(xp, "wb").write(orig.replace("|flats=7|", "|flats=8|").encode())
expect("the_same_fault_in_both_files", False, GOOD.replace("|flats=7|", "|flats=8|"), original=xp)
# With --exe, the output must name that file.
open(op, "wb").write(GOOD.encode())
open(ep, "wb").write(b"")
open(xp, "wb").write(b"some executable")
r = subprocess.run([sys.executable, "-I", "-X", "utf8", TOOL, ORIG, op, "0", ep, "--exe", xp], capture_output=True, text=True)
named = r.returncode == 1
fails += 0 if named else 1
cases += 1
faults += 1
out.write("JUDGE_CONTROL|case=output_names_another_executable|should_pass=0|exit=%d|met=%d|json=0\n" % (r.returncode, 1 if named else 0))
for path in (op, ep, xp):
    os.remove(path)
os.rmdir(tmp)
out.write("JUDGE_SCOPE|a_copy_of_a_good_output_passes=1|what_shows_a_run_happened=a_replay|json=0\n")
out.write("JUDGE_CONTROLS_DONE|cases=%d|faults=%d|failed=%d|json=0\n" % (cases, faults, fails))
out.close()
print("JUDGE_CONTROLS_DONE|cases=%d|faults=%d|failed=%d|json=0" % (cases, faults, fails))
sys.exit(1 if fails else 0)
