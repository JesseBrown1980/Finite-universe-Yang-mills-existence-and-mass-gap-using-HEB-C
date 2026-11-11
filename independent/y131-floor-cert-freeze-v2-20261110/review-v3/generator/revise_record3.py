# Second correction round of the version 2 record (one commit on top of 3b91d1a0).
# Base text: the record as committed at 3b91d1a0, read from git. Every row 001-113 and 116-122 is kept byte for byte.
# Changes: one header line added; rows 114 and 115 get the new hashes and role text; rows 123-130 are appended;
# the END counts are updated. STAGE=1 writes row 129 as PENDING (the state the rehearsals run with); STAGE=2 fills it.
import hashlib, os, re, subprocess, sys
REPO = "/root/floor-v2/repo"
VREL = "independent/y131-floor-cert-freeze-v2-20261110/"
V2 = REPO + "/" + VREL
NAME = "final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp"
C1 = "cfc57befadcb61fb36b992af841941adaecd3fd0"
C2 = "3b91d1a047d7485693c754ece8c7c18f43fbf326"
STAGE = os.environ.get("STAGE", "1")
RACE = "8e460e45e434d81f9663387e9a13a60594d0cdd5d869296ea40ed4478b790752"
O = "/root/floor-v2/rehc/"
r3 = "review-v3/"
RH = r3 + "rehearsal-v2c/"

def old(rel):
    return subprocess.run(["git", "-C", REPO, "show", C2 + ":" + VREL + rel], stdout=subprocess.PIPE, check=True).stdout
def sha(rel):
    return hashlib.sha256(open(V2 + rel, "rb").read()).hexdigest()
def files(rels):
    return ",".join("%s@%s" % (r, sha(r)[:16]) for r in rels)
def U(t):
    t = " ".join(t.split()).replace(" ", "_")
    assert "|" not in t and all(32 < ord(c) < 127 for c in t), t[:80]
    return t

s = old(NAME).decode("ascii")
REC2 = hashlib.sha256(s.encode()).hexdigest()
DRV2 = hashlib.sha256(old("final/tools/run_floor.sh")).hexdigest()
EVL2 = hashlib.sha256(old("final/tools/floor_eval.py")).hexdigest()
assert REC2.startswith("adf78448") and DRV2.startswith("123aee35") and EVL2.startswith("7f135eee")
for rel in ["work/design/rs/src/main.rs", "work/design/gate_required.sh", "work/design/py/cert_gate.py", "work/design/py/indep_verify.py", "work/design/peak_rss.py"]:
    assert hashlib.sha256(old(rel)).hexdigest() == sha(rel), rel
DRV, EVL = sha("final/tools/run_floor.sh"), sha("final/tools/floor_eval.py")
assert DRV != DRV2 and EVL != EVL2
lines = s.split("\n")
assert lines[-1] == "" and lines[-2].startswith("PREDICTION_END|rows=122|")

def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)

# ---- header: one line added after the line of the first correction round
h11 = [l for l in lines if l.startswith("# CORRECTION ROUND (2026-11-10, same seat)")]
assert len(h11) == 1
rep(h11[0] + "\n", h11[0] + "\n" +
    "# SECOND CORRECTION ROUND (2026-11-10, same seat): one commit on top of " + C2 + ". It follows the final-head verification of that commit (HOLD; copied under review-v3/) and the reviewer's two rulings on it. Only the launcher and its evaluator change (rows 114 115, new hashes) and rows 123-130 are added: the launcher runs in an emptied environment with a fixed PATH and absolute program paths, executes the bytes it hashed, applies the 2097152 kB limit to every completed REQUIRED process including the prerequisite of row 007, and gives every CERTIFICATE=FAIL an exit code that no PASS shares. Rows 001-113 and 116-122 are byte-identical to that commit; where a field of rows 116 and 122 is superseded, rows 123-128 say so beside it. A PASS line of the launcher is accepted only after the second-environment recheck of row 125. Execution at r = 9 stays on HOLD.\n")

# ---- rows 114 and 115: new value and role
PINTAIL = "|tag=REQUIRED|basis=MEASURED|met_if=sha256sum_at_run_time_equals_value|not_met_if=differs|falsifier=the_logged_pin_check_line_for_this_path_showing_another_hash|json=0"
l114 = [l for l in lines if l.startswith("PIN|id=114|")][0]; l115 = [l for l in lines if l.startswith("PIN|id=115|")][0]
rep(l114, "PIN|id=114|sec=launcher|quantity=sha256|path=final/tools/run_floor.sh|value=" + DRV + "|role=" + U("""
 single launcher of the r9 run (row 116, as amended by rows 123-128): two stages; stage 1 reads this file once and starts those bytes
 under env -i with PATH /usr/bin:/bin, LANG C and a mount namespace of its own; stage 2 hashes its own text against this row, resolves
 python3, bash, sha256sum, timeout, setsid and git once to absolute paths in system directories and cargo and rustc to the 1.81 toolchain
 binaries, logs each path with its sha256 and calls them by those paths; it reads the record and the tools of rows 019 020 021 103 115
 once into memory, hashes those bytes against the frozen values and runs those bytes (row 124); a hash guard before and after every
 command; pin checks, frozen build, rowhash and cert under the peak wrapper, gate_required.sh on every certificate, the memory limit of
 rows 011 and 123, the decision of rows 006 007 012, the final FLOOR_RUN line printed from the evaluator's captured output, and the
 receipt with the RECHECK rows of row 125; bash; it computes no spectrum""") + PINTAIL)
rep(l115, "PIN|id=115|sec=launcher|quantity=sha256|path=final/tools/floor_eval.py|value=" + EVL + "|role=" + U("""
 evaluator run by row 114 from the bytes it hashed in memory (python3 -I -B -c): reads logs and certificates, checks the PIN path rows
 (the files of rows 019 020 103 and the executed tool files again at every step, and every PIN path row and the executed tool files in a
 closing check), accepts a certificate only with the launcher's record of a verifier invocation that exited 0 with the tools at their
 hashes after the call, applies the memory limit of row 011 to every completed measured process before any fallback and before the
 prerequisite of row 007 is read (rows 122 123), evaluates rows 006 007 012 in exact rational arithmetic, scores rows 058-073 and writes
 the receipt with the verdict fields and one RECHECK row per accepted certificate (row 125); integers and integer pairs only""") + PINTAIL)

rows = []
def disclose(i, quantity, value, fields, met, notmet, fals):
    rows.append("DISCLOSE|id=%s|sec=version_2|quantity=%s|value=%s" % (i, quantity, U(value)) + "".join("|%s=%s" % (k, v if k == "files" or k == "runs" else U(v)) for k, v in fields) +
                "|tag=REPORTED|met_if=%s|not_met_if=%s|falsifier=%s|json=0" % (U(met), U(notmet), U(fals)))

# ---- verifier material of the final-head verification (copied by c_install.sh)
vf = [r3 + x for x in ["VERIFY-FLOOR-FREEZE-V2-FINAL.hbp", "VERIFY-FLOOR-FREEZE-V2-FINAL.hbp.sha256", "VERIFY-FLOOR-FREEZE-V2-FINAL.md", "VERIFY-FLOOR-FREEZE-V2-FINAL.md.sha256"]]
vf += sorted(r3 + "verifier-out/" + x for x in os.listdir(V2 + r3 + "verifier-out"))
vf += sorted(r3 + "scripts/" + x for x in os.listdir(V2 + r3 + "scripts") if x != "race.py")
HV3 = sha(r3 + "VERIFY-FLOOR-FREEZE-V2-FINAL.hbp"); MV3 = sha(r3 + "VERIFY-FLOOR-FREEZE-V2-FINAL.md")

disclose("123", "v2_memory_limit_on_every_completed_REQUIRED_process", "reviewer ruling of 2026-11-10, strict reading", [
 ("ruling", """the reviewer confirmed the strict reading: the 2 GiB limit applies to every completed REQUIRED process, including the
  --rows-only prerequisite verifier of row 007; a peak at or over 2097152 KiB gives CERTIFICATE=FAIL with REASON RESOURCE_LIMIT_EXCEEDED;
  never a missing prerequisite, UNRESOLVED, or fallback"""),
 ("launcher_reading", """the measured processes are the rowhash command (PEAK_RSS line of the peak wrapper), the cert command (PEAK_RSS
  line), every verifier call of gate_required.sh (MEM line) and, at the third step, the rows-only verifier of the prerequisite (MEM
  line); at the third step the launcher calls the evaluator's subcommand limit after the rows-only verifier and before the prerequisite
  outcome is read: a completed rowhash or rows-only verifier at or over the limit prints LIMIT:status=EXCEEDED, the DECISION line reads
  next=STOP, no cert command runs at that step and the final line reads CERTIFICATE=FAIL with certificate_reason=RESOURCE_LIMIT_EXCEEDED,
  no bound and exit 1; the same check applies at every step to rowhash, cert and verifier calls as rows 116 and 122 state"""),
 ("supersedes", """the last sentence of the launcher_reading field of row 122 (at the prerequisite of row 007 a verifier MEM at or over
  the limit leaves m0 13 unrun, as that row says) is superseded by this row: that case is CERTIFICATE=FAIL with RESOURCE_LIMIT_EXCEEDED;
  row 122 is kept byte-identical beside this row; row 007 keeps its text: its run-iff clause (c) describes when m0 13 runs, and with the
  ruling a peak at or over the limit ends the run before that clause is read"""),
 ("found_by", """the final-head verification of """ + C2 + """ (case PQ: with a lowered limit of 23000 kB the rows-only verifier and
  the rowhash of the third step completed over the limit and the run of that commit ended with an accepted bound from the earlier
  steps); the same command on this launcher is the rehearsal PQ of row 129, with PQ0 as its control without the lowered limit"""),
 ("exercised", "MEASURED in test mode with a lowered limit (--test-limit-kb; rehearsals PQ, R1, R2, R3 of row 129); no rehearsal reaches 2097152 kB")],
 "the rehearsal PQ of row 129 ends CERTIFICATE=FAIL with certificate_reason=RESOURCE_LIMIT_EXCEEDED, exit 1 and 0 accepted certificates",
 "a run with a completed rowhash, cert, verifier or rows-only verifier process at or over the limit that prints a bound, advances to a later step, or exits with a code other than 1",
 "a receipt of the pinned launcher with a logged PEAK_RSS or MEM at or over the limit in force and a nonzero accepted certificate count")

disclose("124", "v2_controlled_environment_and_execution_of_the_hashed_bytes", "findings T1 T2 T3 T4 of the final-head verification", [
 ("found", """the verifier seat obtained CERTIFICATE=PASS lines from the launcher of """ + C2 + """ (sha256 """ + DRV2 + """) with no
  genuine verification, four ways: T1 a program named python3 in a directory ahead of the system directories in PATH (the launcher
  put HOME/.cargo/bin first); T2 the variable BASH_ENV naming a file that bash reads when the gate driver starts; T3 a swap of the
  private copy of gate_required.sh between its hash check and its start; T4 a swap of the private copy of the evaluator before the
  final call; report sha256 """ + HV3 + """ and """ + MV3 + """, copied with its scripts and outputs under """ + r3 + """; the same
  commands run by this seat against an export of that commit are the entries XK XT1 XT2 XT3 XT4 of row 129"""),
 ("path", """stage 2 runs with PATH /usr/bin:/bin and nothing else; python3, bash, sha256sum, timeout, setsid and git are resolved
  once under that PATH, made canonical (realpath) and required to lie in a system directory; cargo and rustc are the files
  HOME/.rustup/toolchains/1.81-x86_64-unknown-linux-gnu/bin/cargo and rustc with HOME taken from the password database, and the
  frozen build runs that cargo with RUSTC set to that rustc; every one of these is logged in a TOOLPATH line with its path and
  sha256 and is called by that path; no directory of the caller's PATH is searched"""),
 ("environment", """stage 1 refuses a caller environment that carries BASH_ENV, ENV, any LD_ name, any PYTHON name or an exported
  shell function (certificate_reason NOT_STARTED, exit 4), then replaces itself by /usr/bin/env -i with PATH, LANG=C and two
  variables of its own; stage 2 stops unless its environment holds exactly those names and the ones bash sets itself; HOME is set
  from the password database and TMPDIR to a tmpfs inside the run directory; every bash child runs with --noprofile --norc and
  every python child with -I -B"""),
 ("hashed_bytes", """stage 1 reads the launcher file once and starts those bytes (bash -c); stage 2 hashes the text it is running
  against row 114; the record, gate_required.sh, cert_gate.py, indep_verify.py, peak_rss.py and floor_eval.py are each read once
  into memory and hashed there against P and rows 020 019 021 103 115; peak_rss.py and floor_eval.py are executed from those
  bytes (python3 -I -B -c), so no file of theirs exists to be exchanged; the launcher prints the final line itself from the
  evaluator's captured output and derives the exit code from that line, compared with the evaluator's exit code"""),
 ("gate_driver", """gate_required.sh is pinned (row 020) and finds cert_gate.py and indep_verify.py in the py folder beside its own
  path; the launcher therefore writes gate_required.sh, py/cert_gate.py, py/indep_verify.py, the record and the binary from the
  hashed bytes into a tmpfs that it mounts inside its own mount namespace (unshare -m, private propagation) and remounts read-only
  once written; a process outside that namespace has no path to these files; they are hashed before and after every command, the
  INVOKE line of every command carries private_tools_after=HELD, and the evaluator accepts a certificate only with that field in
  the record of its verifier call and only when the verifier sha256 that the gate driver printed is row 019"""),
 ("supersedes", """in row 116 the statement part on the private directory made by mktemp -d and the NAMED sentence at the end of
  readings_for_a_human_check, and in row 122 the isolated_copies and argv_note fields, describe the launcher of """ + C2[:8] + """
  and are superseded by this row; the executed argv now reads PYTHON -I -B -c MEMORY:peak_rss.py@SHA256 TOOLS/floorcert ... and
  BASH --noprofile --norc TOOLS/gate_required.sh CERT ..., with PYTHON and BASH the absolute paths of the TOOLPATH lines and TOOLS
  the read-only tmpfs; rows 116 and 122 are kept byte-identical beside this row"""),
 ("outcome_on_this_launcher", """MEASURED, row 129: T1 the planted python3 is never called (0 calls) and the run is the genuine
  one; T2 stops with NOT_STARTED, exit 4, nothing run; T3 and T4 the swap program finds no file to exchange (the tools exist only
  inside the namespace, and the evaluator has no file) and the run is the genuine one; T5 the write into the tool tmpfs fails and
  the changed file of the tree ends the run at the next guard; T8 the write into the tool tmpfs fails and the run is the genuine one; L1 (the tree file replaced by a replaying gate driver)
  ends CERTIFICATE=FAIL at the next guard with 0 fake calls; N1 N2 a root process that enters the namespace and rewrites a tool
  ends CERTIFICATE=FAIL at the after-call guard"""),
 ("files", files(vf))],
 "the entries T1 T2 T3 T4 Y1 of row 129 show 0 calls of a planted program and no CERTIFICATE=PASS line that rests on one, and XT1 XT2 XT3 XT4 show the findings on the launcher of " + C2,
 "a run of the pinned launcher in which a planted program, a start file named by the environment or an exchanged tool file is executed and the run ends CERTIFICATE=PASS",
 "a log of the pinned launcher with a CERTIFICATE=PASS final line and a call of a program or tool file whose sha256 is absent from the TOOLPATH and TOOL lines of that run")

rows.append("REQUIRED|id=125|sec=version_2|quantity=v2_acceptance_only_after_a_second_environment_recheck|value=" + U("reviewer ruling of 2026-11-10, bounded acceptance") +
 "|rule=" + U("""a FLOOR_RUN line with CERTIFICATE=PASS is the launcher's own statement; the result is accepted only after a second,
  independent execution environment has rechecked the published certificates, hashes and verdict without trusting that line: (a) the
  launcher ran in the controlled environment of row 124; (b) the attacks T1 T2 T3 T4 and L1 were rerun against this launcher and
  rejected with zero accepted certificates that rest on a planted program (row 129); (c) the second environment, from a clean checkout
  of the freeze commit C, checks that this file hashes to the prediction_sha256 of the receipt and that every tool hashes to rows 019
  020 021, runs gate_required.sh on every certificate listed in a RECHECK row of the receipt, and recomputes the verdict fields""") +
 "|recheck_command=" + U("""for each RECHECK row of work/run9/FLOOR-RUN-RECEIPT.hbp: sha256sum CERT equals the sha256 of the row; then
  bash work/design/gate_required.sh CERT --freeze-commit C --prediction
  final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp --prediction-sha256 P, run inside the freeze folder, with C, P and the exact
  command line printed in the RECHECK_RULE row of the receipt (a test-mode receipt prints the command without the three options); it must end with one GATE_REQUIRED:PASS line whose cert_sha256, rowhash and verifier_sha256 equal the fields of the row
  and one VERDICT:PASS line whose gamma equals the row's gamma""") +
 "|verdict_recomputation=" + U("""GAMMA is the largest gamma of the RECHECK rows; UPPER_BOUND is the smallest of ritz_writer and
  ritz_verifier over those rows plus 1/1000000; DECISION follows the decision_rule field of the final line with g0 of the header;
  the three must equal the VERDICT_FIELDS row of the receipt and the final line""") +
 "|receipt=" + U("""FLOOR-RUN-RECEIPT.hbp carries one VERDICT_FIELDS row, one RECHECK_RULE row and one RECHECK row per accepted
  certificate with m0, certificate path, sha256, gamma, ritz_writer, ritz_verifier, rowhash and verifier_sha256""") +
 "|scope=" + U("""this row governs acceptance of the r9 result by the reviewer; it adds no gate to the launcher's own CERTIFICATE
  field and changes no PREDICT row; the remaining risk of the launching host is disclosed in row 127""") +
 "|tag=REQUIRED|basis=MEASURED|met_if=" + U("the second environment's gate_required.sh ends GATE_REQUIRED:PASS on every RECHECK row and its recomputed GAMMA, UPPER_BOUND and DECISION equal the final line") +
 "|not_met_if=" + U("a RECHECK certificate that the second environment's verifier refuses, a hash that differs, a recomputed verdict field that differs, or no second-environment recheck") +
 "|falsifier=" + U("a second-environment log in which gate_required.sh on a certificate of a RECHECK row ends without GATE_REQUIRED:PASS, or prints another gamma than the row") + "|json=0")

disclose("126", "v2_verifier_crash_on_a_later_certificate_of_a_step", "finding 8 of the final-head verification", [
 ("statement", """the behaviour of the frozen rows is kept: when a verifier call of a step crashes (after the one rerun of row 008)
  or runs into the time limit, the step is operational (rows 006 (b) and 007 (b)) and counts as no certificate; this holds also
  when the verifier had already accepted an earlier certificate of the same step: every certificate of that step, the accepted
  ones included, is moved to the aside folder of the run directory, none of them is counted, none appears in an ACCEPTED or
  RECHECK row, and G and U of that step do not exist; the receipt names the step in operational_failures and the run log names
  the files set aside; a later step may still decide (rehearsal V4 of row 129: a crash of the verifier at the second certificate
  of the first step)"""),
 ("why_stated", "the verifier seat asked that this reading be visible in a row: a bound from a certificate that passed is set aside here because the step as a whole has no complete verification")],
 "the receipt of the rehearsal V4 of row 129 lists 0 accepted certificates for the step whose verifier call crashed and names that step in operational_failures",
 "a receipt that counts a certificate of a step in which a verifier call crashed or ran into the time limit",
 "a receipt of the pinned launcher with an ACCEPTED count above 0 for a step named in operational_failures")

disclose("127", "v2_remaining_risk_of_the_launching_host", "disclosed; the control is row 125", [
 ("statement", """the r9 run is one run as root on one machine; by the reviewer's ruling the launcher closes the PATH, check-then-run
  and BASH_ENV routes (row 124) and makes no claim against an unrestricted administrator of that machine; a concurrent process with
  root rights is outside what a launcher can exclude; this row names the windows that remain"""),
 ("windows", """(1) stage 1 runs in the caller's environment until env -i: a caller environment built to alter bash itself acts
  before the launcher's first line, and the refusal of BASH_ENV, ENV, LD_, PYTHON names and exported functions is a hygiene check
  made by the shell it would alter; the documented invocation is from a clean login shell; (2) the system programs (python3 with
  its standard library, bash, sha256sum, coreutils, timeout, setsid, unshare, mount, git) and the 1.81 toolchain are recorded by
  path and sha256 of the named executable only; their libraries and the kernel are taken as they are; (3) the files of the tree
  (the record passed to the writer and to the gate driver by its relative path in the r9 mode, the Rust source during the frozen
  build, the binary) are read by path; they are hashed before and after every command, so a change that stays is caught, while a
  root process that changes one and restores it between two hash checks is unseen; (4) a root process can enter the launcher's
  mount namespace (nsenter with the launcher's process id), remount the tool tmpfs writable and exchange a tool; a change that
  stays is caught by the after-call guard (MEASURED: N1 N2 of row 129), a change restored within one command is unseen (NAMED,
  left unexercised); (5) the run directory with its logs and certificates is writable by root while the run lasts; the receipt
  gives the sha256 of every log and certificate at the close; (6) the launcher's memory and its process are open to root"""),
 ("control", """the independent rerun of the verifier on the published certificates by another seat in a second environment (row
  125): a certificate is a list of rows with a positive vector, and gate_required.sh rechecks it from the certificate file alone,
  so a false acceptance on the launching host does not survive that rerun; the result is accepted only after it"""),
 ("tags", "MEASURED: the attacks of row 129; NAMED: windows (1) (2) (3) (5) (6) and the restored exchange of (4)")],
 "the windows listed here are the ones a reader of run_floor.sh finds, and the entries N1 N2 of row 129 end CERTIFICATE=FAIL",
 "a route to a CERTIFICATE=PASS line without genuine verification that needs no root process on the launching host and is absent from this row",
 "a test-mode run of the pinned launcher, started from a clean login shell by a user process without root rights acting from outside, that ends CERTIFICATE=PASS on a certificate the verifier of row 019 refuses")

disclose("128", "v2_exit_codes_run_directory_and_first_contact_checks", "second correction round", [
 ("exit_codes", """0 CERTIFICATE=PASS with PREDICTION=CONFIRMED; 3 CERTIFICATE=PASS with PREDICTION=FALSIFIED; 2 CERTIFICATE=PASS
  with PREDICTION=UNRESOLVED; 1 CERTIFICATE=FAIL after the run started, for every reason (a REQUIRED or integrity failure, the
  resource limit, and no accepted certificate for an operational reason); 4 CERTIFICATE=FAIL with certificate_reason=NOT_STARTED
  (refused arguments, a refused caller environment, a refused run directory, a refused checkout, a prelude stop before the first
  command); no FAIL shares a code with a PASS; the launcher derives the code from the final line it prints and ends with
  CERTIFICATE=FAIL and code 1 when the evaluator's own exit code differs from it"""),
 ("supersedes", """the exit_codes field of row 116 and reading (e) of its readings_for_a_human_check (exit 2 for a run with no
  accepted certificate, and for a stop before the first command) are superseded by this row: those cases now exit 1 and 4; row
  116 is kept byte-identical beside this row"""),
 ("test_out", """--test-out must be an absolute path, must be no symbolic link and must not exist; it is made canonical (realpath)
  and refused when it resolves inside the freeze folder or inside the repository that holds it (finding T7d: a path through
  another folder that led back into the freeze folder); in the r9 mode the run directory is ROOT/work/run9 with ROOT the canonical
  absolute path of the freeze folder, whatever the caller's working directory, and it is refused when it resolves elsewhere"""),
 ("first_contact", """TMPDIR is a tmpfs mounted at the tmp folder of the run directory inside the launcher's mount namespace, with
  the tool tmpfs under it; nothing is written to the system's temporary folder; in the r9 mode, before the freeze-commit lookup,
  the launcher asks git for the top level of the checkout and for file-mode differences (git -c core.filemode=true diff --raw):
  a checkout that git reports as of dubious ownership, or one whose files differ from the commit in mode, stops with NOT_STARTED
  and a reason that names the case; --test-git-check runs the same check in test mode (rehearsals GC1 GC2 GC3 of row 129); the
  absolute run directory and the absolute program paths are exercised by the rehearsal AB (called by a relative path from another
  working directory with a planted PATH and another HOME)"""),
 ("not_yet_exercised", """CONJECTURE until the r9 run, as in row 116: the freeze-commit lookup, the frozen build with the absolute
  cargo and rustc paths inside the namespace (a build with the two environment variables set to zeros was run once by hand, with
  TMPDIR on the tmpfs, and reproduced no pinned hash by design), pin check 2 and the FREEZE line checks; the m0 12 and m0 13
  full-size rehearsals DX and D3 were run on the launcher of """ + C2[:8] + """ and are kept under review-v2/rehearsal-v2b; this
  round repeats the full-size m0 11 rehearsal D1 only, since the decision arithmetic of the evaluator is unchanged""")],
 "every entry of row 129 with CERTIFICATE=FAIL shows exit 1 or 4 and every entry with CERTIFICATE=PASS shows exit 0, 2 or 3",
 "a run that ends CERTIFICATE=FAIL with exit 0, 2 or 3, or CERTIFICATE=PASS with exit 1 or 4",
 "a stdout file of row 129 whose final line and recorded exit code contradict the exit_codes field of this row")

if STAGE == "2":
    rh = sorted(RH + x for x in os.listdir(V2 + RH))
    assert not any(x.endswith("race_v.py") for x in rh) and not os.path.exists(V2 + r3 + "scripts/race.py")
    summ = open(O + "SUMMARY.txt").read().strip().replace("\n", ";_")
    assert " " not in summ and "|" not in summ
    st1 = open(O + "STAGE1.sha256").read().split()[0]
    assert hashlib.sha256(open(V2 + RH + "RECORD-AT-REHEARSAL.hbp", "rb").read()).hexdigest() == st1
    d1 = hashlib.sha256(old("review-v2/rehearsal-v2b/DX.stdout.txt")).hexdigest(); d3 = hashlib.sha256(old("review-v2/rehearsal-v2b/D3.stdout.txt")).hexdigest()
    f129 = [("statement", """test-mode runs of the pinned launcher (rows 114 115) at excluded r only, with the pin-free binary of row
      016, writing outside the repository in /root/floor-v2/rehc; no r9-mode run and nothing at r within 1 of 9; they ran with this
      file in its state before this row was filled (sha256 """ + st1 + """, named in each receipt and kept as """ + RH + """RECORD-AT-REHEARSAL.hbp);
      this file differs from that state in this row and in one entry less in files= of row 124; the entries XK XT1 XT2 XT3 XT4 ran the launcher of """ + C2 + """ from an
      export of that commit and show the verifier's findings as found; the entries T1-T8, N1 N2, Y1, Y1b, G1-G8 are attacks on this
      launcher; the row 117 rehearsals stay as the record of the launcher of """ + C2[:8] + """; its full-size runs DX (m0 11 12) and D3
      (m0 11 12 13) are not repeated: stdout sha256 """ + d1 + """ and """ + d3 + """ under review-v2/rehearsal-v2b"""),
            ("kept_outside_the_commit", """the race program of T3 T4 XT3 XT4 (race.py of the verifier seat; race_v.py of this seat is the same bytes) imports ctypes for the inotify calls, an import the no-float gate of this repository lists as a finding; the file stays out of the commit and is named here by its sha256 """ + RACE + """, at C:/tmp/opus55/floor-v2-final/scripts/race.py; attacks.sh and c_atk.sh call it by that name; its printed lines are the .race.txt files"""),
            ("runs", summ), ("files", files(rh))]
else:
    f129 = [("statement", "PENDING: stage 1 of this file, written before the rehearsals ran")]
disclose("129", "v2_launcher_rehearsals_second_correction_round", "excluded r only", f129,
 "each stdout file named in files= ends with the FLOOR_RUN line whose fields are quoted in runs=",
 "a stdout file whose last line differs",
 "a named stdout file or receipt whose FLOOR_RUN fields differ from runs=")

disclose("130", "v2_record_revision_second_correction_round", "2 rows revised and 8 rows added", [
 ("statement", """against the record of """ + C2 + """ (sha256 """ + REC2 + """) this file adds one header line, gives rows 114 and 115
  the new hashes and role text of the launcher and the evaluator (their former values: """ + DRV2 + """ and """ + EVL2 + """), adds rows
  123-130 and updates the END counts; rows 001-113 and 116-122 are byte-identical to that commit (""" + r3 + """ROW-COMPARE-3B91D1A0.hbp);
  the 16 PREDICT rows, the Rust source, gate_required.sh, cert_gate.py, indep_verify.py, peak_rss.py and the binary hash of row 016
  are unchanged; fields of rows 116 and 122 that this round supersedes are named in rows 123 124 128 and left in place"""),
 ("history", """review-v2/ holds the verifier material, the generators and the rehearsals of the first correction round, kept as
  committed at """ + C2[:8] + """; """ + r3 + """ holds the final-head verification of that commit, the generators of this round and
  its rehearsals"""),
 ("after_this_row", """lint_hbp.py, the pin check, the no-float gate, the CR count, the row comparison and the local git commit; none
  r-dependent; this file cannot carry their outputs without changing its own sha256; no push and no r9 run by this seat""")],
 r3 + "ROW-COMPARE-3B91D1A0.hbp regenerated from the two committed files shows rows 001-113 and 116-122 with same bytes 1 and rows 114 115 with same bytes 0",
 "another row differs, or a PREDICT row differs from " + C2,
 "a byte comparison of the two committed files showing a changed row outside 114 and 115")

end_old = "PREDICTION_END|rows=122|FREEZE=12|PIN=25|REQUIRED=23|PREDICT=16|LINK=2|STATUS=9|DISCLOSE=35|DERIVED=2|CONJECTURE=15|REPORTED=43|OPEN=2|REQUIRED_TAG=60|"
end_new = "PREDICTION_END|rows=130|FREEZE=12|PIN=25|REQUIRED=24|PREDICT=16|LINK=2|STATUS=9|DISCLOSE=42|DERIVED=2|CONJECTURE=15|REPORTED=50|OPEN=2|REQUIRED_TAG=61|"
rep(end_old, "\n".join(rows) + "\n" + end_new)
for r in rows:
    assert " " not in r and "\t" not in r, r[:60]
    for m in re.finditer(r"(?<![0-9a-f])[0-9a-f]{16}(?![0-9a-f])", re.sub(r"\|files=[^|]*", "", r)):
        raise SystemExit("bare 16-hex in row " + r[:20] + " " + m.group(0))
assert "\r" not in s and all(ord(c) < 127 for c in s)
# rows 001-113 and 116-122 unchanged
a = {l.split("|")[1]: l for l in old(NAME).decode().split("\n") if re.match(r"^[A-Z]+\|id=\d{3}\|", l)}
b = {l.split("|")[1]: l for l in s.split("\n") if re.match(r"^[A-Z]+\|id=\d{3}\|", l)}
diff = sorted(k for k in a if a[k] != b[k])
assert diff == ["id=114", "id=115"] and len(b) == 130, (diff, len(b))
open(V2 + NAME, "wb").write(s.encode("ascii"))
print("written stage", STAGE, hashlib.sha256(s.encode()).hexdigest(), "rows", len(b), "launcher", DRV[:12], "evaluator", EVL[:12])
