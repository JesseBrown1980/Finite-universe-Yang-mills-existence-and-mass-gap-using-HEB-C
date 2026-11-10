# Version 2 notices in the NOTE and CHANGES.txt, repro_build.txt. Run after revise_record.py and compare.py.
import hashlib
V2 = "/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/"
def sha(rel): return hashlib.sha256(open(V2 + rel, "rb").read()).hexdigest()
REC = "final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp"
P2 = sha(REC); MAIN = sha("work/design/rs/src/main.rs"); BIN = sha("work/design/rs/target/release/floorcert")
GATE = sha("work/design/gate_required.sh"); RSCAN = sha("final/tools/r_scan.sh")
DRV = sha("final/tools/run_floor.sh"); EVL = sha("final/tools/floor_eval.py")
cmp_end = open(V2 + "review-v1/ROW-COMPARE-V1-V2.hbp").read().strip().split("\n")[-1]
e3_end = open(V2 + "review-v1/E3-PROVENANCE.hbp").read().strip().split("\n")[-1]

n = "final/NOTE-S3-3X4-R9-FLOOR-CERT-20261109.md"
s = open(V2 + n, encoding="utf-8", newline="").read()
head, rest = s.split("\n", 1)
notice = (
"\n## VERSION 2 notice (2026-11-10, local build seat)\n\n"
"This folder is version 2 of the freeze. Version 1 is commit `e74d8a46e86034096fd9c9231c87f594f17a93bf`, folder\n"
"`independent/y131-floor-cert-freeze-20261110`, kept unchanged as the historical prediction-first record. Version 2 follows\n"
"an operational review of version 1 (verifier report under `review-v1/`, verdict HOLD, errata E1-E5) and carries the blind\n"
"history of version 1, including the disclosed near-9 critic run of row 093. It claims no new blind history.\n\n"
"The version 2 record is `PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp` with sha256\n"
"`" + P2 + "`, 118 rows. Rows 110-118 disclose the review and everything run\n"
"for version 2 and pin the launcher. Rows 001, 003, 006, 007, 008, 009, 010, 013, 016, 020 and 070 are revised (006, 007\n"
"and 008 keep every version 1 byte and gain one field naming the launcher); the other 98 rows are byte-identical to\n"
"version 1 (`review-v1/ROW-COMPARE-V1-V2.hbp`). Every PREDICT row keeps its value, met_if, not_met_if and falsifier.\n\n"
"New hashes: `main.rs` `" + MAIN + "`, pin-free binary\n"
"`" + BIN + "`, `gate_required.sh`\n"
"`" + GATE + "`, `r_scan.sh`\n"
"`" + RSCAN + "`.\n\n"
"The r = 9 run is launched by one command, `bash final/tools/run_floor.sh` (sha256\n"
"`" + DRV + "`, with the evaluator `final/tools/floor_eval.py`\n"
"`" + EVL + "`). It checks the pins, builds the frozen binary, runs rowhash and\n"
"cert at m0 = 11, runs the required gate on every certificate, decides rows 006 and 007 in exact rational arithmetic on\n"
"verifier-accepted certificates, and ends with one `FLOOR_RUN|result=PASS|FAIL|UNRESOLVED` line and a hash-listed receipt.\n"
"Record rows 114-117 define it and list its rehearsals at excluded r. The default mode has never been run; the r = 9\n"
"run is on HOLD until this freeze passes review.\n\n"
"The text below this notice is the version 1 note, unchanged. Where it gives the version 1 record hash, the version 1\n"
"hashes of `main.rs`, the binary, `gate_required.sh` or `r_scan.sh`, the absolute scratch paths, or the row count 109, the\n"
"version 2 record and this notice give the current values. `work/design/NOTE.md` and `work/map/MAP.md` are the pinned\n"
"version 1 files, unchanged.\n")
assert "VERSION 2 notice" not in s
open(V2 + n, "w", encoding="utf-8", newline="").write(head + "\n" + notice + rest)

c = "final/CHANGES.txt"
s = open(V2 + c, encoding="utf-8", newline="").read()
assert "VERSION 2 (2026-11-10" not in s
if not s.endswith("\n"): s += "\n"
s += (
"\nVERSION 2 (2026-11-10, local build seat, Claude Opus 5.5; owner-relayed reviewer authorization: version 2 freeze before any measurement)\n"
"- Version 1 (commit e74d8a46e86034096fd9c9231c87f594f17a93bf, folder independent/y131-floor-cert-freeze-20261110) stays unchanged. This folder is a copy of it\n"
"  with the repairs below. Everything above this section is the version 1 text, unchanged.\n"
"- E1: rowhash creates its --dir when it is absent (std::fs::create_dir_all at the start of rowhash_only). cert creates no directory; with an absent --dir it\n"
"  exits 101 as in version 1, and it reuses the directory rowhash made (KEYS|loaded).\n"
"- E5: the 22 errors of cargo +1.81 clippy --release --locked -- -D warnings are rewritten, with no allow attribute. Clippy exit 0, build exit 0, 0 warnings.\n"
"  main.rs " + MAIN + ". Pin-free binary " + BIN + " (a rebuild in a separate target dir is byte-identical).\n"
"- E2: work/design/gate_required.sh and final/tools/r_scan.sh take their base directory from their own location. gate_required.sh " + GATE + ",\n"
"  r_scan.sh " + RSCAN + ". r_scan.sh was left unrun: it is a text scan and 10 of its 11 folders hold absent files.\n"
"  final/tools/r_scan.txt, lint_controls.txt and lint_token_scan.txt are the version 1 outputs, unchanged. final/tools/lint_hbp.py is unchanged.\n"
"- E4: row 070's basis gives the verifier memory of the pinned FIX-1 receipt, 403696kB, and names the version 1 figure 403336kB.\n"
"- E3: review-v1/E3-PROVENANCE.hbp lists every absent files= path with its provenance. " + e3_end + "\n"
"  No absent file was recreated or back-filled.\n"
"- Regression with the version 2 binary, at the excluded r 12 and 21/2 only: selftest, the m0 7 smoke certificate, the 14 m0 6 plant certificates and the\n"
"  m0 11 certificate with its key file and row hash are byte-identical to their FIX-1 pins; the required gate passes on the honest files and refuses the\n"
"  12 distinct plants. Receipts: review-v1/regression-v2/. Record row 112.\n"
"- Launcher (added scope, owner-relayed): final/tools/run_floor.sh " + DRV + " and final/tools/floor_eval.py\n"
"  " + EVL + ". One command for the r = 9 run: pin checks, frozen build, rowhash and cert under peak_rss.py,\n"
"  gate_required.sh on every certificate, rows 006/007 decided in exact rational arithmetic from verifier-accepted certificates only, one FLOOR_RUN line,\n"
"  a receipt. Rehearsed in test mode at excluded r only (record row 117, review-v1/rehearsal-v2/). The default mode was not run. Rows 001 006 007 008 name it.\n"
"- Record: " + P2 + ", 118 rows. " + cmp_end + "\n"
"- final/tools/lint_result.txt holds the real lint result on the version 2 record, with the error count and the reason of each class.\n"
"- Nothing was computed at r = 9 or at any r within 1 of 9. No push, no pull request. The r = 9 run waits for the review of this version 2 freeze.\n")
open(V2 + c, "w", encoding="utf-8", newline="").write(s)

log = open("/root/floor-v2/repro_build.log").read()
reb = hashlib.sha256(open("/root/floor-v2/repro_target/release/floorcert", "rb").read()).hexdigest()
assert reb == BIN
open(V2 + "final/tools/repro_build.txt", "w", newline="").write(
"REPRO_BUILD|cmd=env -u FLOORCERT_FREEZE_COMMIT -u FLOORCERT_PREDICTION_SHA256 CARGO_TARGET_DIR=<separate dir> cargo +1.81 build --release --locked -j1|rustc=rustc 1.81.0 (eeb90cda1 2024-09-04)|rebuilt=" + reb + "|pinned=" + BIN + "|IDENTICAL|warnings=" + str(log.count("warning")) + "|r_dependent=NONE|version=2\n")
print("P2", P2); print(cmp_end); print(e3_end)
