# Fourth correction round: additions to the NOTE and to CHANGES.txt. Base text: the two files as committed at 5eecb540 (read from git),
# kept byte for byte; one paragraph is inserted in the notice of the NOTE and one section is appended to CHANGES.txt.
import hashlib, subprocess
REPO = "/root/floor-v2/repo"; VREL = "independent/y131-floor-cert-freeze-v2-20261110/"; V2 = REPO + "/" + VREL
C4 = "5eecb540431a1b5665605f68ed81bc701719dcd1"
def old(rel): return subprocess.run(["git", "-C", REPO, "show", C4 + ":" + VREL + rel], stdout=subprocess.PIPE, check=True).stdout.decode("utf-8")
def sha(rel): return hashlib.sha256(open(V2 + rel, "rb").read()).hexdigest()
P5 = sha("final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp"); DRV = sha("final/tools/run_floor.sh"); EVL = sha("final/tools/floor_eval.py"); CHK = sha("final/tools/recheck_floor.py")
cmp_end = open(V2 + "review-v5/ROW-COMPARE-5EECB540.hbp").read().strip().split("\n")[-1]
n = "final/NOTE-S3-3X4-R9-FLOOR-CERT-20261109.md"
s = old(n)
mark = "The text below this notice is the version 1 note, unchanged."
assert s.count(mark) == 1 and "Fourth correction round" not in s
add = (
"Fourth correction round (2026-11-11, one commit on top of `" + C4 + "`): the fourth final-head\n"
"verification of that commit returned FAIL on the checker (`review-v5/verifier/VERIFY-FLOOR-FREEZE-V2-FINAL4.md`). The\n"
"launcher, the frozen build and a full-size run to m0 = 13 were reproduced from a fresh clone. The checker accepted\n"
"rewritten receipts whose decision the run had not reached: a falsification hidden by removing a step's certificates, a\n"
"result decided by a certificate from another run, a failed run rewritten as a pass. The record now has 141 rows and sha256\n"
"`" + P5 + "`; the launcher is\n"
"`" + DRV + "`, the evaluator\n"
"`" + EVL + "` and the checker\n"
"`" + CHK + "`. The hashes and the row count given earlier in this notice are\n"
"those of the earlier commits. The Rust source, the binary hash, `gate_required.sh`, `cert_gate.py`, `indep_verify.py`,\n"
"`peak_rss.py` and the 16 PREDICT rows are byte-identical (`review-v5/ROW-COMPARE-5EECB540.hbp`).\n\n"
"What changed (record rows 137-141):\n\n"
"- The checker replays the frozen protocol (row 138). It holds r = 9, the steps 11, 12, 13, the three f words and g0 as\n"
"  constants. ACCEPT=YES needs every certificate the protocol calls for, no certificate beside them, no step after a\n"
"  decision, and its own decision, bounds, per-step values and scores equal to the receipt's. An UNRESOLVED result with a\n"
"  step that did not complete is left to the reviewer: the checker ends ACCEPT=NO.\n"
"- The receipt hash is published (row 138). The launcher prints `PUBLISH|receipt_sha256=...` before its final line, and the\n"
"  checker needs that value for the r = 9 receipt: `python3 -I -B final/tools/recheck_floor.py\n"
"  receipt=RUN_DIRECTORY/FLOOR-RUN-RECEIPT.hbp commit=C receipt_sha256=H`.\n"
"- The launcher's mount namespace must hold the launcher alone (row 139): another process in it stops the run at the\n"
"  start, after the mounts, or at the close.\n"
"- The build takes nothing but the pinned files (row 139): an empty CARGO_HOME, no cargo configuration file in the Rust\n"
"  folder or above it, no untracked file in the Rust folder, and with a frozen build an unchanged repository.\n\n"
"What stays open is listed in row 139: the writer's peak memory and PREDICT rows 068 and 070 are values of the launching\n"
"host; a certificate is accepted on what the verifier proves, whoever wrote it; a root process can still enter the\n"
"namespace between two checks. The rehearsals of this round are in row 140 and under `review-v5/rehearsal-v2e/`. Nothing\n"
"was computed at r = 9 or within 1 of it. The r = 9 run stays on HOLD until an independent verification of this commit\n"
"passes.\n\n")
s = s.replace(mark, add + mark)
open(V2 + n, "w", encoding="utf-8", newline="").write(s)

c = "final/CHANGES.txt"
s = old(c)
assert "FOURTH CORRECTION ROUND" not in s and s.endswith("\n")
s += (
"- FOURTH CORRECTION ROUND (2026-11-11, one commit on top of " + C4 + "; fourth final-head verification FAIL on the checker, review-v5/; record rows 137-141).\n"
"  The record hash, the tool hashes and the row count in the lines above are those of the earlier commits.\n"
"  Found by the verifier seat on the checker of 5eecb540: ACCEPT=YES on rewritten receipts (a step's certificates removed to hide BELOW; a certificate of another\n"
"  f word added to reach ABOVE; a failed run rewritten as PASS; a hand-written receipt; scores changed), and four smaller acceptances (row 137).\n"
"  Checker: rewritten to replay the frozen protocol from constants, to require exactly the protocol's certificates, to refuse a step after a decision and an\n"
"  UNRESOLVED result with an uncompleted step, to recompute the scores other than 068 and 070, to compare the verifier memory with the limit, and to require the\n"
"  published receipt hash for the r9 receipt (row 138 beside rows 127 and 133).\n"
"  Launcher: the mount namespace must hold the launcher alone (finding C4); empty CARGO_HOME, no cargo configuration file, no untracked file in the Rust folder\n"
"  (finding E4); the whole repository unchanged for a frozen build (finding E3b); a PUBLISH line with the receipt sha256 (row 139).\n"
"  Evaluator: one PROTOCOL row in the receipt.\n"
"  Launcher " + DRV + ", evaluator " + EVL + ", checker " + CHK + ".\n"
"  main.rs, the binary hash, gate_required.sh, cert_gate.py, indep_verify.py, peak_rss.py, freeze_args_controls.sh and the 16 PREDICT rows are unchanged.\n"
"- Record after the fourth correction round: " + P5 + ", 141 rows. " + cmp_end + "\n"
"- Nothing was computed at r = 9 or at any r within 1 of 9. The r = 9 run stays on HOLD.\n")
open(V2 + c, "w", encoding="utf-8", newline="").write(s)
print("P5", P5); print(cmp_end)
