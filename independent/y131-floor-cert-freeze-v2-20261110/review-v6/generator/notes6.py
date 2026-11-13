# Fifth correction round: additions to the NOTE and to CHANGES.txt. Base text: the two files as committed at 3c41ea2d (read from git),
# kept byte for byte; one paragraph is inserted in the notice of the NOTE and one section is appended to CHANGES.txt.
import hashlib, subprocess
REPO = "/root/floor-v2/repo"; VREL = "independent/y131-floor-cert-freeze-v2-20261110/"; V2 = REPO + "/" + VREL
C5 = "3c41ea2d9dd01de0ffcd547a7e7d417baa2ca6c0"
def old(rel): return subprocess.run(["git", "-C", REPO, "show", C5 + ":" + VREL + rel], stdout=subprocess.PIPE, check=True).stdout.decode("utf-8")
def sha(rel): return hashlib.sha256(open(V2 + rel, "rb").read()).hexdigest()
P6 = sha("final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp"); DRV = sha("final/tools/run_floor.sh"); EVL = sha("final/tools/floor_eval.py"); CHK = sha("final/tools/recheck_floor.py")
cmp_end = open(V2 + "review-v6/ROW-COMPARE-3C41EA2D.hbp").read().strip().split("\n")[-1]
n = "final/NOTE-S3-3X4-R9-FLOOR-CERT-20261109.md"
s = old(n)
mark = "The text below this notice is the version 1 note, unchanged."
assert s.count(mark) == 1 and "Fifth correction round" not in s
add = (
"Fifth correction round (2026-11-12, one commit on top of `" + C5 + "`): the fifth final-head\n"
"verification of that commit returned FAIL (`review-v6/verifier/VERIFY-FLOOR-FREEZE-V2-FINAL5.md`). Integrity and a\n"
"full-size run to m0 = 13 were reproduced from a fresh clone, and the rewritten receipts of the fourth report were\n"
"refused. Three findings stood: a falsified rehearsal result was turned into an accepted UNRESOLVED one with weaker\n"
"valid certificates (high); stage 2 was entered through a mount namespace that a bound file kept alive with no process\n"
"in it (medium); a workspace manifest above the Rust folder changed the frozen binary (medium). The record now has 146\n"
"rows and sha256 `" + P6 + "`; the launcher is\n"
"`" + DRV + "` and the checker\n"
"`" + CHK + "`; the evaluator is unchanged\n"
"(`" + EVL + "`). The hashes and the row count given earlier in this\n"
"notice are those of the earlier commits. The Rust source, the binary hash, `gate_required.sh`, `cert_gate.py`,\n"
"`indep_verify.py`, `peak_rss.py` and the 16 PREDICT rows are byte-identical (`review-v6/ROW-COMPARE-3C41EA2D.hbp`).\n\n"
"What changed (record rows 142-146):\n\n"
"- The checker never accepts an UNRESOLVED result (row 143). ACCEPT=YES is given to ABOVE and to BELOW only: each is a\n"
"  statement the certificates prove. UNRESOLVED says that no certificate of the run decides, and certificates cannot\n"
"  prove that, because a valid certificate can be replaced by a weaker valid one. An r = 9 run that ends UNRESOLVED is\n"
"  still reported UNRESOLVED by the launcher; that report is the launching host's statement.\n"
"- The launcher reads every mount table and every open descriptor at the three points of row 139 (row 144). A bind\n"
"  mount or a descriptor that names its mount namespace, or a mount namespace with no member process, stops the run.\n"
"- A `Cargo.toml` that names a workspace in a directory above the Rust folder stops the run. With a frozen build the\n"
"  checkout must be at the freeze commit, and the index may mark no file assume-unchanged or skip-worktree (row 144).\n\n"
"What stays open is listed in row 144 beside rows 127 and 139. The rehearsals of this round are in row 145 and under\n"
"`review-v6/rehearsal-v2f/`. Nothing was computed at r = 9 or within 1 of it. The r = 9 run stays on HOLD until an\n"
"independent verification of this commit passes.\n\n")
s = s.replace(mark, add + mark)
open(V2 + n, "w", encoding="utf-8", newline="").write(s)

c = "final/CHANGES.txt"
s = old(c)
assert "FIFTH CORRECTION ROUND" not in s and s.endswith("\n")
s += (
"- FIFTH CORRECTION ROUND (2026-11-12, one commit on top of " + C5 + "; fifth final-head verification FAIL, review-v6/; record rows 142-146).\n"
"  The record hash, the tool hashes and the row count in the lines above are those of the earlier commits.\n"
"  Found by the verifier seat on 3c41ea2d: X15 (high), a BELOW rehearsal result turned into an accepted UNRESOLVED one with a weaker valid certificate;\n"
"  B2 (medium), stage 2 entered through a mount namespace kept alive by a bound nsfs file with no process in it; B5 and B7 (medium), a workspace manifest\n"
"  above the Rust folder changed the frozen binary, and HEAD was not required to be the freeze commit; smaller findings in row 142.\n"
"  Checker: an UNRESOLVED result is never accepted (row 143, beside rows 138 and 139); a PREDICT_SCORE row without a row key is a reason and no Python error;\n"
"  in r9 mode the PROTOCOL row's repeated-field flag is read and commit= is compared with the HEAD of the checkout.\n"
"  Launcher: mount tables and open descriptors read at the three points of row 139; a workspace manifest above the Rust folder stops the run; with a frozen\n"
"  build HEAD must equal the freeze commit and no file may be marked assume-unchanged or skip-worktree; header wording on /proc/PID/root (row 144).\n"
"  Launcher " + DRV + ", checker " + CHK + "; evaluator unchanged (" + EVL + ").\n"
"  main.rs, the binary hash, gate_required.sh, cert_gate.py, indep_verify.py, peak_rss.py, freeze_args_controls.sh and the 16 PREDICT rows are unchanged.\n"
"- Record after the fifth correction round: " + P6 + ", 146 rows. " + cmp_end + "\n"
"- Nothing was computed at r = 9 or at any r within 1 of 9. The r = 9 run stays on HOLD.\n")
open(V2 + c, "w", encoding="utf-8", newline="").write(s)
print("P6", P6); print(cmp_end)
