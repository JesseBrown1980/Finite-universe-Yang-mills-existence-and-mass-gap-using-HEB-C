# Third correction round: additions to the NOTE and to CHANGES.txt. Base text: the two files as committed at 78c89c31 (read from git),
# kept byte for byte; one paragraph is inserted in the notice of the NOTE and one section is appended to CHANGES.txt.
import hashlib, subprocess
REPO = "/root/floor-v2/repo"; VREL = "independent/y131-floor-cert-freeze-v2-20261110/"; V2 = REPO + "/" + VREL
C3 = "78c89c312a265fe4090071fc1abdc7d6eb102e7e"
def old(rel): return subprocess.run(["git", "-C", REPO, "show", C3 + ":" + VREL + rel], stdout=subprocess.PIPE, check=True).stdout.decode("utf-8")
def sha(rel): return hashlib.sha256(open(V2 + rel, "rb").read()).hexdigest()
P4 = sha("final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp"); DRV = sha("final/tools/run_floor.sh"); EVL = sha("final/tools/floor_eval.py"); CHK = sha("final/tools/recheck_floor.py")
cmp_end = open(V2 + "review-v4/ROW-COMPARE-78C89C31.hbp").read().strip().split("\n")[-1]
n = "final/NOTE-S3-3X4-R9-FLOOR-CERT-20261109.md"
s = old(n)
mark = "The text below this notice is the version 1 note, unchanged."
assert s.count(mark) == 1 and "Third correction round" not in s
add = (
"Third correction round (2026-11-11, one commit on top of `" + C3 + "`): the reviewer's acceptance\n"
"review of that commit returned HOLD with four gates (`review-v4/REVIEW-ACCEPTANCE-20261111.md`). The launcher and the\n"
"evaluator are changed and a checker is added; the Rust source, the binary hash, `gate_required.sh`, `cert_gate.py`,\n"
"`indep_verify.py`, `peak_rss.py` and the 16 PREDICT rows are byte-identical (`review-v4/ROW-COMPARE-78C89C31.hbp`). The\n"
"record now has 136 rows and sha256 `" + P4 + "`; the launcher is\n"
"`" + DRV + "`, the evaluator\n"
"`" + EVL + "` and the checker `final/tools/recheck_floor.py`\n"
"`" + CHK + "`. The hashes and the row count given earlier in this notice are\n"
"those of the earlier commits.\n\n"
"What changed (record rows 131-136):\n\n"
"- Namespace (row 132). Stage 2 of the launcher starts only when its mount namespace differs from that of its parent\n"
"  process and of process 1 and holds no shared mount; entered directly it stops with NOT_STARTED, exit 4, before it mounts\n"
"  or writes anything. After its two tmpfs mounts it checks that both are absent from the mount tables of the parent\n"
"  process and of process 1. Only then does the run log say the namespace is private.\n"
"- Independent verdict (rows 131 and 133). Acceptance of a result needs the checker, run in a second environment from a\n"
"  clean checkout: `python3 -I -B final/tools/recheck_floor.py receipt=RUN_DIRECTORY/FLOOR-RUN-RECEIPT.hbp commit=C`. It\n"
"  reruns `gate_required.sh` on every accepted certificate, takes the upper bound from its own verifier output alone,\n"
"  decides ABOVE, BELOW or UNRESOLVED, and only then compares with the receipt. Any difference gives ACCEPT=NO.\n"
"- Certificate paths (row 133). The receipt names its run directory, and every RECHECK row gives its certificate relative\n"
"  to that directory. The checker refuses a missing file, a symbolic link, a path that leaves the directory, a file whose\n"
"  sha256 differs, and a certificate file that no row names.\n"
"- Frozen build and full-size fallback (row 134). `--test-frozen-build` rehearses the freeze-commit lookup, the frozen\n"
"  build and pin check 2 at an excluded r. A full-size rehearsal at r = 21/2 runs the fallback to m0 = 13 with its\n"
"  prerequisite and the 2 GiB limit. The freeze options of the writer and of the verifier are read at r = 9 only and stay\n"
"  unexercised until the run.\n\n"
"The rehearsals of this round are listed in row 135 and kept under `review-v4/rehearsal-v2d/`. Nothing was run at r = 9 or\n"
"within 1 of it. The r = 9 run stays on HOLD until the reviewer accepts this commit with evidence from an independent\n"
"environment.\n\n")
s = s.replace(mark, add + mark)
open(V2 + n, "w", encoding="utf-8", newline="").write(s)

c = "final/CHANGES.txt"
s = old(c)
assert "THIRD CORRECTION ROUND" not in s and s.endswith("\n")
s += (
"- THIRD CORRECTION ROUND (2026-11-11, one commit on top of " + C3 + "; reviewer acceptance review HOLD, review-v4/; record rows 131-136).\n"
"  The record hash, the launcher hash, the evaluator hash and the row count in the lines above are those of the earlier commits.\n"
"  Gate 1, namespace: stage 2 could be entered directly and then mounted its tmpfs on the host. It now compares its mount namespace with that of its parent\n"
"  process and of process 1, refuses shared mounts, and after mounting checks that both tmpfs mounts are absent outside; a direct entry stops with exit 4 (row 132).\n"
"  Gate 2, independent verdict: final/tools/recheck_floor.py (row 131) reruns the gate on every accepted certificate in a second environment, takes the upper\n"
"  bound from its own verifier output alone, decides, and then compares with the receipt; any difference gives ACCEPT=NO (row 133 beside row 125).\n"
"  Gate 3, certificate paths: the receipt carries a RUN_DIRECTORY row and each RECHECK row is relative to it; the checker refuses missing, substituted,\n"
"  linked and out-of-directory files and unlisted certificate files (row 133).\n"
"  Gate 4: --test-frozen-build rehearses the freeze-commit lookup, the frozen build and pin check 2 at an excluded r; D13 is a full-size fallback to m0 13\n"
"  at r 21/2 with the prerequisite of row 007 and the 2 GiB limit (row 134 beside row 128). The freeze options of the writer and the verifier stay unexercised.\n"
"  Launcher " + DRV + ", evaluator " + EVL + ", checker " + CHK + ".\n"
"  main.rs, the binary hash, gate_required.sh, cert_gate.py, indep_verify.py, peak_rss.py and the 16 PREDICT rows are unchanged.\n"
"- Record after the third correction round: " + P4 + ", 136 rows. " + cmp_end + "\n"
"- Nothing was computed at r = 9 or at any r within 1 of 9. The r = 9 run stays on HOLD.\n")
open(V2 + c, "w", encoding="utf-8", newline="").write(s)
print("P4", P4); print(cmp_end)
