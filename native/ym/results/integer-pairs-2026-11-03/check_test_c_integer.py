#!/usr/bin/env python3
# test_c.py and its integer copy, each run in a temporary folder as replay.py runs the original, so the recorded file stays as it is.
# The two differ in one comment line and the interval line, and each must write the recorded RESULT.hbp. A timestamp moved by one second must stop the copy.
# Path.write_text writes CRLF on Windows, so the comparison drops carriage returns. usage: check_test_c_integer.py   Integer only, json=0.
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(HERE, "..", "z-one-matrix-20261030", "curve_ABC", "C")


def read(name):
    with open(os.path.join(C, name), "rb") as f:
        return f.read()


def run_in_temp(script, evidence):
    """Returns (exit, the RESULT.hbp the script wrote, or empty bytes)."""
    with tempfile.TemporaryDirectory(prefix="test_c_") as tmp:
        shutil.copyfile(os.path.join(C, script), os.path.join(tmp, script))
        with open(os.path.join(tmp, "EVIDENCE.hbp"), "wb") as f:
            f.write(evidence)
        code = subprocess.run([sys.executable, "-I", "-B", "-X", "utf8", os.path.join(tmp, script)], capture_output=True).returncode
        written = os.path.join(tmp, "RESULT.hbp")
        if not os.path.exists(written):
            return code, b""
        with open(written, "rb") as f:
            return code, f.read().replace(b"\r", b"")


original, copy = read("test_c.py").split(b"\n"), read("test_c_integer.py").split(b"\n")
comments = [line for line in copy if line.startswith(b"# Integer copy of test_c.py")]
copy_lines = [line for line in copy if line not in comments]
same_length = len(original) == len(copy_lines)
differing = [(a, b) for a, b in zip(original, copy_lines) if a != b]
only_the_interval = len(differing) == 1 and b"total_seconds" in differing[0][0] and b".days*86400+(t1-t0).seconds" in differing[0][1]
print("TEST_C_COPY|comment_lines_added=%d|lines_differing=%d|the_interval_line_alone=%d|json=0" % (len(comments), len(differing), 1 if same_length and only_the_interval else 0))

evidence, recorded = read("EVIDENCE.hbp"), read("RESULT.hbp")
bad = 0 if same_length and only_the_interval and len(comments) == 1 else 1
for script in ("test_c.py", "test_c_integer.py"):
    code, written = run_in_temp(script, evidence)
    same = 1 if code == 0 and written == recorded else 0
    bad += 1 - same
    print("TEST_C_RUN|script=%s|exit=%d|result_same_as_recorded=%d|json=0" % (script, code, same))

# The later commit's timestamp moved by one second: the integer interval reads 3328, and the file's own assert stops it.
moved, count = re.subn(rb"(role=first_committed_verses_in_reviewed_history\|[^\n]*created_utc=2026-08-02T01:50:)26Z", rb"\g<1>27Z", evidence)
code, written = run_in_temp("test_c_integer.py", moved)
stopped = 1 if count == 1 and code != 0 and not written else 0
bad += 1 - stopped
print("TEST_C_CONTROL|timestamp_moved_one_second=%d|the_copy_stopped=%d|json=0" % (count, stopped))
sys.exit(1 if bad else 0)
