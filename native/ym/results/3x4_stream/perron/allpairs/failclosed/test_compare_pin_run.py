# Tests compare_pin_run.py on copies of the original run's output. A damaged copy must exit 1 with failed above 0. A copy that differs only in
# secs= must exit 0. Exits 1 if any case differs from that. Integer only, json=0.
# usage: test_compare_pin_run.py ALLPAIRS-3x4.out OUT_FILE
import os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "compare_pin_run.py")
ORIG = sys.argv[1]
text = open(ORIG, "rb").read().decode()
lines = text.splitlines(True)


def sub(a, b):
    if a not in text:
        raise SystemExit("no match: " + a)
    return text.replace(a, b, 1)


# name, output text, exit code given, stderr text, should it pass
CASES = [
    ("same_file", text, "0", "", True),
    ("only_secs_differ", re.sub(r"\|secs=[0-9]+\|", "|secs=999|", text), "0", "", True),
    ("value_mismatch", sub("|value_mismatch=0|lower_without_upper=0|upper_without_lower=0|columns", "|value_mismatch=1|lower_without_upper=0|upper_without_lower=0|columns"), "0", "", False),
    ("lower_unpaired", sub("|lower_without_upper=0|upper_without_lower=0|columns", "|lower_without_upper=1|upper_without_lower=0|columns"), "0", "", False),
    ("upper_unpaired", sub("|upper_without_lower=0|columns", "|upper_without_lower=2|columns"), "0", "", False),
    ("header_entries_open", sub("header_entries=PASS", "header_entries=OPEN"), "0", "", False),
    ("header_entries_fail", sub("header_entries=PASS", "header_entries=FAIL"), "0", "", False),
    ("whole_space_count_open", sub("whole_space_count=PASS", "whole_space_count=OPEN"), "0", "", False),
    ("whole_space_count_fail", sub("whole_space_count=PASS", "whole_space_count=FAIL"), "0", "", False),
    ("verdict_fail", sub("|verdict=PASS|", "|verdict=FAIL|"), "0", "", False),
    ("one_pass_row_gone", "".join(x for x in lines if not x.startswith("ALLPAIRS_PASS|pass=2")), "0", "", False),
    ("one_pass_merkle_open", sub("|merkle=PASS|secs=", "|merkle=OPEN|secs="), "0", "", False),
    ("pairs_one_short", sub("|pairs=1632625631|", "|pairs=1632625630|"), "0", "", False),
    ("rows_one_short", sub("|rows_read=45508080|", "|rows_read=45508079|"), "0", "", False),
    ("row_sum_counter", sub("|row_sum_nonzero=0|", "|row_sum_nonzero=3|"), "0", "", False),
    ("zero_weight_counter", sub("|zero_weight=0|", "|zero_weight=1|"), "0", "", False),
    ("window_moved", sub("|rows_to=9065182|", "|rows_to=9065183|"), "0", "", False),
    ("a_detail_row", text + "ALLPAIRS_BAD|kind=value_mismatch|i=1|h=2|json=0\n", "0", "", False),
    ("no_final_row", "".join(x for x in lines if x.startswith("ALLPAIRS_PASS|")), "0", "", False),
    ("empty_output", "", "0", "", False),
    ("exit_code_2", text, "2", "", False),
    ("stderr_not_empty", text, "0", "x\n", False),
]
tmp = tempfile.mkdtemp(prefix="compare-")
out = open(sys.argv[2], "w", encoding="utf-8", newline="\n")
fails = 0
for name, body, code, err, should_pass in CASES:
    op, ep = os.path.join(tmp, "out"), os.path.join(tmp, "err")
    open(op, "wb").write(body.encode())
    open(ep, "wb").write(err.encode())
    r = subprocess.run([sys.executable, "-I", "-X", "utf8", TOOL, ORIG, op, code, ep], capture_output=True, text=True)
    rows = r.stdout.splitlines()
    failed = int(rows[-1].split("|failed=")[1].split("|")[0]) if rows and rows[-1].startswith("PIN_COMPARE_DONE|") else -1
    ok = (r.returncode == 0 and failed == 0) if should_pass else (r.returncode == 1 and failed > 0)
    fails += 0 if ok else 1
    out.write("COMPARE_CONTROL|case=%s|should_pass=%d|exit=%d|failed=%d|met=%d|json=0\n" % (name, 1 if should_pass else 0, r.returncode, failed, 1 if ok else 0))
os.remove(op)
os.remove(ep)
os.rmdir(tmp)
out.write("COMPARE_CONTROLS_DONE|cases=%d|faults=%d|failed=%d|json=0\n" % (len(CASES), sum(1 for c in CASES if not c[4]), fails))
out.close()
print("COMPARE_CONTROLS_DONE|cases=%d|faults=%d|failed=%d|json=0" % (len(CASES), sum(1 for c in CASES if not c[4]), fails))
sys.exit(1 if fails else 0)
