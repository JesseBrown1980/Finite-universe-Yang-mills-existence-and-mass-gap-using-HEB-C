# Builds notes2.py, lintres2.py and pins2.sh from the first-round scripts by exact-string replacement.
import io
T = "/mnt/c/tmp/opus55/floor-v2/"
def rd(n): return io.open(T + n, encoding="utf-8", newline="").read().replace("\r\n", "\n")
def wr(n, s): io.open(T + n, "w", encoding="utf-8", newline="\n").write(s)
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:70])
    return s.replace(a, b)

s = rd("notes.py")
s = rep(s, '"`, 118 rows. Rows 110-118 disclose the review and everything run\\n"', '"`, 122 rows. Rows 110-122 disclose the review and everything run\\n"')
s = rep(s, '"The r = 9 run is launched by one command, `bash final/tools/run_floor.sh` (sha256\\n"', '"The r = 9 run is launched by one command, `bash final/tools/run_floor.sh --launch-r9` (sha256\\n"')
s = rep(s, '"verifier-accepted certificates, and ends with one `FLOOR_RUN|result=PASS|FAIL|UNRESOLVED` line and a hash-listed receipt.\\n"',
 '"verifier-accepted certificates, and ends with one line\\n"\n'
 '"`FLOOR_RUN|CERTIFICATE=PASS or FAIL|PREDICTION=CONFIRMED or FALSIFIED or UNRESOLVED|DECISION=ABOVE or BELOW or UNRESOLVED|GAMMA=|UPPER_BOUND=|...|HASHES=`\\n"\n'
 '"and a hash-listed receipt. CERTIFICATE says whether the gates and the integrity checks held; PREDICTION says whether\\n"\n'
 '"lambda_min(QHQ) >= g0 was confirmed or falsified. A falsified prediction reads CERTIFICATE=PASS, PREDICTION=FALSIFIED,\\n"\n'
 '"DECISION=BELOW, exit code 3. An integrity or gate failure reads CERTIFICATE=FAIL with GAMMA=NONE and UPPER_BOUND=NONE.\\n"')
s = rep(s, '"Record rows 114-117 define it and list its rehearsals at excluded r. The default mode has never been run; the r = 9\\n"\n"run is on HOLD until this freeze passes review.\\n\\n"',
 '"Record rows 114-117 define it and list its rehearsals at excluded r. The r = 9 mode has never been run; the r = 9\\n"\n"run is on HOLD until this freeze passes review.\\n\\n"\n'
 '"Correction round (same day, one commit on top of the first version 2 commit `cfc57befadcb61fb36b992af841941adaecd3fd0`):\\n"\n'
 '"the reviewer\'s rulings and the findings of the separate verifier seat (`review-v2/`) are applied to the launcher and the\\n"\n'
 '"evaluator. The Rust source, the binary hash and the 16 PREDICT rows are byte-identical to that commit\\n"\n'
 '"(`review-v2/ROW-COMPARE-CFC57BEF.hbp`). Record row 119 lists each finding and its change, row 120 and\\n"\n'
 '"`review-v2/MODIFIED-ROWS-V1-V2.hbp` account for the 11 modified rows field by field, row 121 puts the two readings of\\n"\n'
 '"rows 006 and 011 at 2 GB before the reviewer, and row 122 records the reviewer\'s ruling on them: a process that completes\\n"\n'
 '"at or over 2 GiB (2,097,152 KiB) gives CERTIFICATE=FAIL with reason RESOURCE_LIMIT_EXCEEDED and no fallback; a timeout or\\n"\n'
 '"a crash may trigger fallback only when the applicable REQUIRED gates have not failed. The launcher runs private, hashed,\\n"\n'
 '"read-only copies of the gate driver, the verifier, the peak wrapper and the evaluator, and a certificate is accepted only\\n"\n'
 '"with the record of a verifier invocation that exited 0 (row 122). `review-v2/rehearsal-v2b/` holds the swap of the gate\\n"\n'
 '"driver as found against the first version 2 commit (X1) and its rejection by this launcher (Y1, Y1b, P1).\\n\\n"')
s = rep(s, '''"  a receipt. Rehearsed in test mode at excluded r only (record row 117, review-v1/rehearsal-v2/). The default mode was not run. Rows 001 006 007 008 name it.\\n"''',
 '''"  a receipt. Rehearsed in test mode at excluded r only (record row 117, review-v2/rehearsal-v2b/). The r = 9 mode was not run. Rows 001 006 007 008 name it.\\n"
"- CORRECTION ROUND (one commit on top of cfc57befadcb61fb36b992af841941adaecd3fd0; reviewer rulings and verifier findings, record rows 119-122):\\n"
"  final line FLOOR_RUN|CERTIFICATE=|PREDICTION=|DECISION=|GAMMA=|UPPER_BOUND=|...|HASHES= with exit codes 0 confirmed, 3 falsified, 2 undecided, 1 certificate failure;\\n"
"  every command in its own process group (setsid), a time limit ends that group only and gets no rerun; the launcher hashes every pinned program and itself\\n"
"  before every invocation, the evaluator hashes the verifier, the gate driver and the peak wrapper at every step and runs a closing pin check;\\n"
"  the launcher copies the gate driver, the verifier, the peak wrapper, the evaluator, the record and the binary into a fresh private directory, hashes the\\n"
"  copies against the frozen values and runs only the copies; a certificate needs the record of a verifier invocation with exit 0; a completed process at or\\n"
"  over 2097152 kB gives CERTIFICATE=FAIL, certificate_reason=RESOURCE_LIMIT_EXCEEDED, and no fallback (row 122);\\n"
"  the r = 9 mode needs the token --launch-r9 and an empty option value stops the launcher; a verifier process that ends with an exception or runs into the\\n"
"  time limit is an operational failure; a byte copy of the file of row 034 is carried under final/link/; review-v1/E3-PROVENANCE.hbp gains one E3_NOTE line (F8).\\n"
"  The first round's launcher rehearsals stay in review-v1/rehearsal-v2/ as history. main.rs, the binary hash, gate_required.sh and the 16 PREDICT rows are unchanged.\\n"''')
s = rep(s, '"- Record: " + P2 + ", 118 rows. "', '"- Record: " + P2 + ", 122 rows. "')
wr("notes2.py", s)

s = rd("lintres.py")
s = rep(s, '"the pinned amplitude record is at commit 5e70e9dc02d6ed32fe9a94d03a2c3a77587ff9af; run_floor.sh reads it from that git object and checks the pin"',
 '"the pinned amplitude record is at commit 5e70e9dc02d6ed32fe9a94d03a2c3a77587ff9af; a byte copy is carried at final/link/ and the pin checks of run_floor.sh read that copy; the lint tool reads the literal path only"')
wr("lintres2.py", s)

s = rd("pins.sh")
s = rep(s, '''"The r = 9 run is launched by one command, bash final/tools/run_floor.sh, only after this freeze passes review. It is on HOLD." \\''',
 '''"The r = 9 run is launched by one command, bash final/tools/run_floor.sh --launch-r9, only after this freeze passes review. It is on HOLD." \\
"Correction round: one commit on top of the first version 2 commit cfc57befadcb61fb36b992af841941adaecd3fd0 (reviewer rulings and verifier findings, record rows 119-122, review-v2/). $(tail -1 review-v2/ROW-COMPARE-CFC57BEF.hbp | tr '|' ' ')." \\''')
wr("pins2.sh", s)
print("ok")
