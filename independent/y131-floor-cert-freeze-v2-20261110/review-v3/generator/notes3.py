# Second correction round: additions to the NOTE and to CHANGES.txt. Base text: the two files as committed at 3b91d1a0 (read from git),
# kept byte for byte; one paragraph is inserted in the notice of the NOTE and one section is appended to CHANGES.txt.
import hashlib, subprocess
REPO = "/root/floor-v2/repo"; VREL = "independent/y131-floor-cert-freeze-v2-20261110/"; V2 = REPO + "/" + VREL
C2 = "3b91d1a047d7485693c754ece8c7c18f43fbf326"
def old(rel): return subprocess.run(["git", "-C", REPO, "show", C2 + ":" + VREL + rel], stdout=subprocess.PIPE, check=True).stdout.decode("utf-8")
def sha(rel): return hashlib.sha256(open(V2 + rel, "rb").read()).hexdigest()
P3 = sha("final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp"); DRV = sha("final/tools/run_floor.sh"); EVL = sha("final/tools/floor_eval.py")
cmp_end = open(V2 + "review-v3/ROW-COMPARE-3B91D1A0.hbp").read().strip().split("\n")[-1]
n = "final/NOTE-S3-3X4-R9-FLOOR-CERT-20261109.md"
s = old(n)
mark = "The text below this notice is the version 1 note, unchanged."
assert s.count(mark) == 1 and "Second correction round" not in s
add = (
"Second correction round (same day, one commit on top of `" + C2 + "`): the final-head verification of\n"
"that commit returned HOLD (`review-v3/VERIFY-FLOOR-FREEZE-V2-FINAL.md`). The verifier seat obtained CERTIFICATE=PASS lines\n"
"from the launcher of that commit with no genuine verification, four ways: a program named `python3` placed ahead of the\n"
"system directories in PATH (T1), the variable BASH_ENV (T2), and a swap of the private copy of the gate driver (T3) or of\n"
"the evaluator (T4) between its hash check and its start. The launcher and the evaluator are changed; the Rust source, the\n"
"binary hash, `gate_required.sh`, `cert_gate.py`, `indep_verify.py`, `peak_rss.py` and the 16 PREDICT rows are\n"
"byte-identical (`review-v3/ROW-COMPARE-3B91D1A0.hbp`). The record now has 130 rows and sha256\n"
"`" + P3 + "`; the launcher is\n"
"`" + DRV + "` and the evaluator\n"
"`" + EVL + "`. The record hash, the launcher hash, the evaluator hash and the\n"
"row count given earlier in this notice are those of `3b91d1a0`.\n"
"One file of the verifier material stays out of the commit: the race program of the swap attacks (race.py, sha256 8e460e45e434d81f9663387e9a13a60594d0cdd5d869296ea40ed4478b790752) imports ctypes, an import the no-float gate lists; it stays out of the commit and is named by that hash in row 129.\n\n"
"What changed (record rows 123-130): the launcher starts itself again under `env -i` with PATH `/usr/bin:/bin` in a mount\n"
"namespace of its own, resolves every program once to an absolute path and logs it with its sha256, reads each tool once,\n"
"hashes those bytes and runs those bytes (the peak wrapper and the evaluator from memory, the gate driver and the verifier\n"
"from a read-only tmpfs inside the namespace), and prints the final line itself from the evaluator's captured output\n"
"(row 124). The 2 GiB limit applies to every completed REQUIRED process including the rows-only prerequisite verifier of\n"
"row 007, by the reviewer's ruling: at or over 2,097,152 KiB the run ends CERTIFICATE=FAIL, RESOURCE_LIMIT_EXCEEDED\n"
"(row 123). Exit codes: 0 PASS and CONFIRMED, 3 PASS and FALSIFIED, 2 PASS and UNRESOLVED, 1 every CERTIFICATE=FAIL of a\n"
"started run, 4 NOT_STARTED (row 128).\n\n"
"Remaining risk, disclosed (row 127): the r = 9 run is one run as root on one machine. A concurrent root process on that\n"
"machine is outside what a launcher can exclude: it can act before the environment is cleared, change a system program or\n"
"library, enter the launcher's mount namespace, or exchange a file and restore it between two hash checks. The control is\n"
"row 125: a CERTIFICATE=PASS line is the launcher's own statement, and the result is accepted only after a second,\n"
"independent environment has rerun `gate_required.sh` on every certificate listed in the RECHECK rows of the receipt, from\n"
"a clean checkout of the freeze commit, and recomputed the verdict fields. The receipt prints the exact command.\n\n")
s = s.replace(mark, add + mark)
open(V2 + n, "w", encoding="utf-8", newline="").write(s)

c = "final/CHANGES.txt"
s = old(c)
assert "SECOND CORRECTION ROUND" not in s and s.endswith("\n")
s += (
"- SECOND CORRECTION ROUND (one commit on top of " + C2 + "; final-head verification HOLD, review-v3/; record rows 123-130).\n"
"  The record hash, the launcher hash, the evaluator hash and the row count in the lines above are those of 3b91d1a0.\n"
"  Found by the verifier seat on the launcher of 3b91d1a0, each giving a CERTIFICATE=PASS line with no genuine verification: T1 a planted python3 ahead of the\n"
"  system directories in PATH; T2 BASH_ENV; T3 a swap of the private gate driver copy between hash check and start; T4 the same for the evaluator copy.\n"
"  Launcher: stage 1 refuses BASH_ENV, ENV, LD_*, PYTHON* and exported functions and starts its own bytes under env -i (PATH /usr/bin:/bin, LANG C) in a private\n"
"  mount namespace; every program is resolved once to an absolute path and logged with its sha256 (TOOLPATH lines); cargo and rustc are the 1.81 toolchain\n"
"  binaries by absolute path; each tool is read once, hashed and run from those bytes (peak_rss.py and floor_eval.py by python3 -I -B -c; gate_required.sh,\n"
"  cert_gate.py and indep_verify.py from a read-only tmpfs inside the namespace); a guard hashes them before and after every command; the launcher prints the\n"
"  final line from the evaluator's captured output. TMPDIR is a tmpfs in the run directory; the run directory is absolute; --test-out is made canonical and\n"
"  refused inside the freeze folder or the repository; the r9 mode refuses a checkout with dubious ownership or file-mode differences.\n"
"  2 GiB (reviewer ruling, strict reading): every completed REQUIRED process, including the rows-only prerequisite verifier and the m0 13 rowhash of row 007,\n"
"  at or over 2097152 kB gives CERTIFICATE=FAIL, RESOURCE_LIMIT_EXCEEDED, checked before the prerequisite outcome is read (row 123 beside row 122).\n"
"  Exit codes: 0 PASS+CONFIRMED, 3 PASS+FALSIFIED, 2 PASS+UNRESOLVED, 1 CERTIFICATE=FAIL, 4 NOT_STARTED (row 128 beside row 116).\n"
"  Kept outside the commit: the race program of the swap attacks (race.py, sha256 8e460e45e434d81f9663387e9a13a60594d0cdd5d869296ea40ed4478b790752) imports ctypes, an import the no-float gate lists; it stays out of the commit and is named by that hash in row 129.\n"
"  A verifier crash on a later certificate of a step sets the whole step aside; none of its certificates is counted (row 126).\n"
"  Disclosed residual (row 127): one run as root on one machine; a concurrent root process is outside what the launcher can exclude. Acceptance (row 125): only\n"
"  after a second environment reruns gate_required.sh on every certificate of the receipt's RECHECK rows from a clean checkout and recomputes the verdict.\n"
"  Launcher " + DRV + ", evaluator " + EVL + ".\n"
"  main.rs, the binary hash, gate_required.sh, cert_gate.py, indep_verify.py, peak_rss.py and the 16 PREDICT rows are unchanged.\n"
"- Record after the second correction round: " + P3 + ", 130 rows. " + cmp_end + "\n"
"- Nothing was computed at r = 9 or at any r within 1 of 9. No push, no pull request. The r = 9 run stays on HOLD.\n")
open(V2 + c, "w", encoding="utf-8", newline="").write(s)
print("P3", P3); print(cmp_end)
