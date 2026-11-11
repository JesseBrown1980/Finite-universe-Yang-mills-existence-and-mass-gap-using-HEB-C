# Third correction round of the version 2 record (one commit on top of 78c89c31).
# Base text: the record as committed at 78c89c31, read from git. Every row 001-113 and 116-130 is kept byte for byte.
# Changes: one header line added; rows 114 and 115 get the new hashes and role text; rows 131-136 are appended;
# the END counts are updated. STAGE=1 writes row 135 as PENDING (the state the rehearsals run with); STAGE=2 fills it.
import hashlib, os, re, subprocess, sys
REPO = os.environ.get("REPO", "/root/floor-v2/repo")
VREL = "independent/y131-floor-cert-freeze-v2-20261110/"
V2 = REPO + "/" + VREL
NAME = "final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp"
C3 = "78c89c312a265fe4090071fc1abdc7d6eb102e7e"
V3C = "1ebdb200d76d08f424e6f73ad8f17058f16a5ff0"
STAGE = os.environ.get("STAGE", "1")
O = "/root/floor-v3/rehd/"
r4 = "review-v4/"
RH = r4 + "rehearsal-v2d/"

def old(rel):
    return subprocess.run(["git", "-C", REPO, "show", C3 + ":" + VREL + rel], stdout=subprocess.PIPE, check=True).stdout
def sha(rel):
    return hashlib.sha256(open(V2 + rel, "rb").read()).hexdigest()
def files(rels):
    return ",".join("%s@%s" % (r, sha(r)[:16]) for r in rels)
def U(t):
    t = " ".join(t.split()).replace(" ", "_")
    assert "|" not in t and all(32 < ord(c) < 127 for c in t), t[:80]
    return t

s = old(NAME).decode("ascii")
REC3 = hashlib.sha256(s.encode()).hexdigest()
DRV3 = hashlib.sha256(old("final/tools/run_floor.sh")).hexdigest()
EVL3 = hashlib.sha256(old("final/tools/floor_eval.py")).hexdigest()
assert REC3.startswith("41ced0bb") and DRV3.startswith("8d1f01cf") and EVL3.startswith("c237a54a")
for rel in ["work/design/rs/src/main.rs", "work/design/gate_required.sh", "work/design/py/cert_gate.py", "work/design/py/indep_verify.py", "work/design/peak_rss.py"]:
    assert hashlib.sha256(old(rel)).hexdigest() == sha(rel), rel
DRV, EVL, CHK = sha("final/tools/run_floor.sh"), sha("final/tools/floor_eval.py"), sha("final/tools/recheck_floor.py")
assert DRV != DRV3 and EVL != EVL3
lines = s.split("\n")
assert lines[-1] == "" and lines[-2].startswith("PREDICTION_END|rows=130|")

def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)

# ---- header: one line added after the line of the second correction round
h = [l for l in lines if l.startswith("# SECOND CORRECTION ROUND (2026-11-10, same seat)")]
assert len(h) == 1
rep(h[0] + "\n", h[0] + "\n" +
    "# THIRD CORRECTION ROUND (2026-11-11, same seat): one commit on top of " + C3 + ". It follows the reviewer's acceptance review of 2026-11-11 (HOLD; copied under review-v4/) and the third final-head verification of that commit (commit " + V3C + "). The launcher and its evaluator change (rows 114 115, new hashes), a second-environment checker is added and pinned (row 131), and rows 132-136 are added: stage 2 of the launcher starts only inside a mount namespace of its own and checks that by its effect; the checker recomputes every accepted certificate, takes the upper bound from its own verifier output alone and must reproduce the decision; the receipt anchors every certificate path to its run directory; the frozen build can be rehearsed at an excluded r. Rows 001-113 and 116-130 are byte-identical to that commit; where a field of rows 125 and 128 is superseded, rows 133 and 134 say so beside it. Execution at r = 9 stays on HOLD.\n")

# ---- rows 114 and 115: new value and role
PINTAIL = "|tag=REQUIRED|basis=MEASURED|met_if=sha256sum_at_run_time_equals_value|not_met_if=differs|falsifier=the_logged_pin_check_line_for_this_path_showing_another_hash|json=0"
l114 = [l for l in lines if l.startswith("PIN|id=114|")][0]; l115 = [l for l in lines if l.startswith("PIN|id=115|")][0]
rep(l114, "PIN|id=114|sec=launcher|quantity=sha256|path=final/tools/run_floor.sh|value=" + DRV + "|role=" + U("""
 single launcher of the r9 run (row 116, as amended by rows 123-128 and 132-134): two stages; stage 1 reads this file once and starts
 those bytes under env -i with PATH /usr/bin:/bin, LANG C and a mount namespace of its own; stage 2 first requires that its mount
 namespace differs from that of its parent process and of process 1 and holds no shared or slave mount, and after its two tmpfs mounts
 that both are absent from the mount tables of the parent process and of process 1 (row 132); it hashes its own text against this row,
 resolves python3, bash, sha256sum, timeout, setsid and git once to absolute paths in system directories and cargo and rustc to the 1.81
 toolchain binaries, logs each path with its sha256 and calls them by those paths; it reads the record and the tools of rows 019 020 021
 103 115 once into memory, hashes those bytes against the frozen values and runs those bytes (row 124); a hash guard before and after
 every command; pin checks, frozen build, rowhash and cert under the peak wrapper, gate_required.sh on every certificate, the memory
 limit of rows 011 and 123, the decision of rows 006 007 012, the final FLOOR_RUN line printed from the evaluator's captured output, and
 the receipt with the RUN_DIRECTORY row and the RECHECK rows of rows 125 and 133; --test-frozen-build rehearses the freeze-commit
 lookup, the frozen build and pin check 2 at an excluded r (row 134); bash; it computes no spectrum""") + PINTAIL)
rep(l115, "PIN|id=115|sec=launcher|quantity=sha256|path=final/tools/floor_eval.py|value=" + EVL + "|role=" + U("""
 evaluator run by row 114 from the bytes it hashed in memory (python3 -I -B -c): reads logs and certificates, checks the PIN path rows
 (the files of rows 019 020 103 and the executed tool files again at every step, and every PIN path row and the executed tool files in a
 closing check), accepts a certificate only with the launcher's record of a verifier invocation that exited 0 with the tools at their
 hashes after the call, applies the memory limit of row 011 to every completed measured process before any fallback and before the
 prerequisite of row 007 is read (rows 122 123), evaluates rows 006 007 012 in exact rational arithmetic, scores rows 058-073 and writes
 the receipt with the verdict fields (among them the upper bound from the verifier's Ritz values alone), the RUN_DIRECTORY row and one
 RECHECK row per accepted certificate, each path relative to the run directory (rows 125 133); integers and integer pairs only""") + PINTAIL)

rows = []
def disclose(i, quantity, value, fields, met, notmet, fals):
    rows.append("DISCLOSE|id=%s|sec=version_2|quantity=%s|value=%s" % (i, quantity, U(value)) + "".join("|%s=%s" % (k, v if k == "files" or k == "runs" else U(v)) for k, v in fields) +
                "|tag=REPORTED|met_if=%s|not_met_if=%s|falsifier=%s|json=0" % (U(met), U(notmet), U(fals)))

rows.append("PIN|id=131|sec=launcher|quantity=sha256|path=final/tools/recheck_floor.py|value=" + CHK + "|role=" + U("""
 second-environment checker of a floor run receipt (rows 125 133): run inside the freeze folder of a clean checkout of the freeze commit
 by python3 -I -B final/tools/recheck_floor.py receipt=RUN_DIRECTORY/FLOOR-RUN-RECEIPT.hbp (with commit=C for the r9 receipt); it hashes
 the record, gate_required.sh, cert_gate.py, indep_verify.py and itself against rows 020 019 021 and this row, hashes the receipt
 against its sha256 file, anchors every certificate path of the RECHECK rows to the directory that holds the receipt, runs
 gate_required.sh on every one in an emptied environment, takes gamma and the Ritz value from that output alone, decides ABOVE, BELOW or
 UNRESOLVED and only then compares with the VERDICT_FIELDS row and the final line of the receipt; last line RECHECK_VERDICT with
 ACCEPT=YES or NO; exit 0, 1 or 4; integers and integer pairs only; it computes no spectrum""") + PINTAIL)

disclose("132", "v2_stage_2_runs_only_inside_a_private_mount_namespace", "reviewer acceptance review of 2026-11-11, gate 1; verifier finding FS2", [
 ("found", """stage 2 of the launcher of """ + C3 + """ (sha256 """ + DRV3 + """) took the variable FLOOR_STAGE=2 and a bash -c text as
  proof that stage 1 had run; entered directly (env -i with the five words of stage 1 and bash -c with the file text, no unshare) it
  ran in the caller's mount namespace and left its two tmpfs mounts on the host (case FS2 of the third final-head verification, commit
  """ + V3C + """; the same entry against an export of that commit is the entry XNS of row 135)"""),
 ("change", """stage 2 reads the mount namespace id of its own process, of its parent process and of process 1 (readlink of
  /proc/self/ns/mnt, /proc/PPID/ns/mnt, /proc/1/ns/mnt) before anything else: an unreadable id, an id equal to the parent's or to that
  of process 1, or a shared, slave or propagate_from mark in /proc/self/mountinfo stops with certificate_reason NOT_STARTED, stage
  namespace, exit 4, with no mount made and no file written; unshare -m replaces itself by bash, so the parent of a stage 2 started by
  stage 1 is the caller of the launcher, outside the new namespace"""),
 ("by_effect", """after the two tmpfs mounts the launcher reads three mount tables: both mount points must be listed in
  /proc/self/mountinfo and absent from /proc/PPID/mountinfo and from /proc/1/mountinfo, and the namespace id must be unchanged; if
  not, both mounts are taken down and the run stops with NOT_STARTED; the NOTE line of the run log reads mount_namespace=private_CHECKED
  with the three ids only after these checks"""),
 ("stage_1_list", """stage 1 also refuses a caller environment that carries BASHOPTS, SHELLOPTS, PS4, IFS, POSIXLY_CORRECT, BASH_COMPAT,
  BASH_XTRACEFD, BASH_LOADABLES_PATH, EXECIGNORE, GLOBIGNORE or CDPATH, beside the names of row 124 (a low finding of the third
  final-head verification); as row 127 window (1) says, this is a hygiene check made by the shell it would alter"""),
 ("scope", """the check shows that the tmpfs files are outside the mount tables of the calling process and of process 1; a root process
  that enters the namespace on purpose stays window (4) of row 127, with row 125 and row 133 as its control"""),
 ("outcome", """MEASURED, row 135: NS1 the direct entry stops with exit 4 and leaves no mount and no run directory; NS2 a direct entry
  from a namespace whose mounts are shared stops with exit 4; NS0 the documented call runs and the host mount table holds no
  floor-run mount during or after it""")],
 "the entries NS1 and NS2 of row 135 end NOT_STARTED with exit 4 and the entry NS0 ends with the namespace NOTE and no floor-run mount in the host mount table",
 "a run of the pinned launcher whose stage 2 mounts a tmpfs that shows in the mount table of its parent process or of process 1 and that goes on to print a FLOOR_RUN line other than NOT_STARTED",
 "a log of the pinned launcher with a START line and a floor-run-tmp or floor-run-tools entry in /proc/1/mountinfo taken while that run lasted")

rows.append("REQUIRED|id=133|sec=version_2|quantity=v2_second_environment_checker_and_verdict_agreement|value=" + U("reviewer acceptance review of 2026-11-11, gates 2 and 3") +
 "|rule=" + U("""the recheck of row 125 is made by the pinned checker of row 131 and by no hand procedure: a result of the launcher is
  accepted only after final/tools/recheck_floor.py, run in a second, independent environment inside the freeze folder of a clean
  checkout of the freeze commit, ends RECHECK_VERDICT with ACCEPT=YES on the receipt; the checker (a) reruns gate_required.sh on every
  certificate of a RECHECK row and requires GATE_REQUIRED:PASS and VERDICT:PASS from its own call; (b) forms G as the largest gamma and
  the upper bound as the smallest Ritz value of its own verifier calls plus 1/1000000, with no number of the receipt in either; (c)
  decides ABOVE when g0 LE G, BELOW when the upper bound LT g0, UNRESOLVED otherwise, and blocks when both hold; g0 is 94070673/1000000
  for the r9 receipt; (d) compares only then: CERTIFICATE of the receipt must read PASS and DECISION, PREDICTION, GAMMA and
  UPPER_BOUND_VERIFIER_ONLY of its VERDICT_FIELDS row must equal the checker's values; any difference gives ACCEPT=NO""") +
 "|never_an_input=" + U("""the checker forms G, its upper bound and its decision before it reads the VERDICT_FIELDS row or the final
  line; the receipt's GAMMA, UPPER_BOUND, UPPER_BOUND_VERIFIER_ONLY, DECISION and PREDICTION and the gamma, ritz_writer and
  ritz_verifier fields of the RECHECK rows enter none of the three; of a RECHECK row it uses the path, the sha256, m0 and the rowhash
  before that point; afterwards it also requires that the receipt's UPPER_BOUND equals the smallest of the rows' ritz_writer values
  and its own verifier values plus 1/1000000, so a receipt whose UPPER_BOUND was altered gives ACCEPT=NO; for a rehearsal receipt g0
  is the rehearsal's own value, read from the receipt, and for the r9 receipt it is the constant of the record""") +
 "|certificate_paths=" + U("""the receipt carries one RUN_DIRECTORY row with the absolute run directory, and every RECHECK row names its
  certificate as RUNm/cert_... with relative_to=RUN_DIRECTORY; the run directory is the directory that holds the receipt and is copied
  whole to the second environment; the checker joins each path to the directory of the receipt it was given and gives ACCEPT=NO for a
  path of another shape, a path that leaves that directory, a symbolic link, a missing file, a file whose sha256 differs from the row,
  a certificate file in a RUN folder that no RECHECK row names, and a receipt that differs from its sha256 file""") +
 "|supersedes=" + U("""in row 125 the recheck_command field (a per-certificate command typed by hand, with paths whose anchor it left
  open) and the verdict_recomputation field (UPPER_BOUND from the smaller of ritz_writer and ritz_verifier of the RECHECK rows) are
  superseded by this row; the launcher's own UPPER_BOUND field keeps the definition of row 012 and its decision is unchanged: it
  already ends UNRESOLVED when the two definitions of U give different states; row 125 is kept byte-identical beside this row""") +
 "|scope=" + U("""this row governs acceptance of the r9 result by the reviewer; it adds no gate to the launcher's own CERTIFICATE field
  and changes no PREDICT row; the checker shares no code file with the launcher or the evaluator and calls the verifier of row 019
  through the gate driver of row 020""") +
 "|tag=REQUIRED|basis=MEASURED|met_if=" + U("the checker of row 131, run in a second environment on the r9 receipt, ends RECHECK_VERDICT with ACCEPT=YES") +
 "|not_met_if=" + U("the checker ends ACCEPT=NO, exits 4, or was not run in a second environment") +
 "|falsifier=" + U("an output file of the pinned checker on the r9 receipt whose last line reads ACCEPT=NO") + "|json=0")

disclose("134", "v2_frozen_build_rehearsal_and_full_size_fallback_to_m0_13", "reviewer acceptance review of 2026-11-11, gate 4", [
 ("frozen_build", """--test-frozen-build makes a rehearsal take the three steps that only the r9 mode took before: the git contact
  check and the freeze-commit lookup with the blob hash of the record and the clean-tree check, the build with FLOORCERT_FREEZE_COMMIT
  and FLOORCERT_PREDICTION_SHA256 compiled in (absolute cargo and rustc paths, target directory inside the run directory), and pin
  check 2; the binary must differ from the pin-free binary of row 016 or the run stops; the rehearsal then runs at the excluded R with
  that binary, which takes no freeze argument away from r 9; --freeze-commit C is accepted with this option"""),
 ("build_is_not_argument_validation", """a frozen-build rehearsal shows that the binary compiles with the two pins, where it comes
  from and that the pin checks hold; it does not show that the freeze arguments work at run time, because the writer and the verifier
  read them at r 9 only"""),
 ("freeze_argument_controls", """final/tools/freeze_args_controls.sh hands r 9 to the writer and to the verifier with one freeze
  argument absent or wrong by construction and requires the refusal: for the writer the pin-free binary, no freeze argument, a wrong
  commit, a wrong prediction hash, an absent prediction file and a prediction file with another hash; for the verifier, on a header
  line with no row written by the script, no freeze argument, an absent prediction file, a file with another hash and two more with a
  wrong commit or a wrong header hash; each program ends at its refusal before any computation that depends on r; the script never
  forms the accepted argument set (it passes no readable prediction file that hashes to the compiled value) and stops unless every
  control is refused, no FREEZE line is printed and no run directory appears; entry FZA of row 135, on the binary of FB1"""),
 ("still_unexercised", """the accepted path: the writer and the verifier taking the three freeze options, their FREEZE lines and the
  checks of those lines in the evaluator stay CONJECTURE until the r9 run; apart from the eleven refusal controls of FZA, which
  compute nothing, no command of this round passes r 9 or an r within 1 of 9 to any program"""),
 ("full_size", """the entry D13 of row 135 is a full-size rehearsal at r 21/2 with the three frozen f words through the fallback of
  rows 006 (b) and 007 (b) to m0 13: the rowhash of m0 13, the logged hash of its keys file, the rows-only verifier of the
  prerequisite of row 007, the memory limit of row 123 read before the prerequisite outcome at the full 2097152 kB, the cert command
  and one verifier call per certificate; the entry PQ repeats the lowered-limit stop at the prerequisite on this launcher"""),
 ("supersedes", """the not_yet_exercised field of row 128 named the freeze-commit lookup, the frozen build inside the namespace and
  pin check 2 as CONJECTURE until the r9 run; these three are exercised by the entries FB1 FB2 FB3 of row 135 and that part of the
  field is superseded by this row; row 128 is kept byte-identical beside this row""")],
 "the entry FB1 of row 135 ends CERTIFICATE=PASS with a frozen_build_rehearsal NOTE line and a binary hash other than row 016, and the entry D13 reaches a STEP line for m0 13",
 "a rehearsal with --test-frozen-build that runs the pin-free binary, or a D13 receipt without a rowsonly INVOKE line and a LIMIT line for m0 13",
 "a receipt named in row 135 for FB1 whose TOOL line of floorcert gives the hash of row 016")

if STAGE == "2":
    rh = sorted(RH + x for x in os.listdir(V2 + RH))
    summ = open(O + "SUMMARY.txt").read().strip().replace("\n", ";_")
    assert " " not in summ and "|" not in summ
    st1 = open(O + "STAGE1.sha256").read().split()[0]
    assert hashlib.sha256(open(V2 + RH + "RECORD-AT-REHEARSAL.hbp", "rb").read()).hexdigest() == st1
    f135 = [("statement", """test-mode runs of the pinned launcher (rows 114 115) at excluded r only and runs of the pinned checker (row
      131) on their receipts, writing outside the repository in /root/floor-v3/rehd; no r9-mode run and no computation at r 9 or within
      1 of it (the entry FZA hands r 9 to the writer and the verifier in eleven refusal controls, row 134, each ended by its refusal); they
      ran with this file in its state before this row was filled (sha256 """ + st1 + """, named in each receipt and kept as """ + RH + """RECORD-AT-REHEARSAL.hbp);
      this file differs from that state in this row only; the entries FB1 FB2 FB3 ran in a scratch clone that held that state as a
      commit of its own (a frozen build needs a commit; that commit is no part of the branch); the entry XNS ran the launcher of """ + C3 + """
      from an export of that commit; the checker entries ran in an export of the staged file set; a second environment proper is the
      verifier seat's and the reviewer's (row 133)"""),
            ("clock_note", """two INVOKE lines carry a negative elapsed time, each on an injected 2-second limit: -3 s at the m0 12 cert
      step of D13 and -2 s in XNS; the launcher reads the wall clock (date +%s) before and after a command, and the clock of this WSL host
      stepped back between the two reads (NAMED: the host clock was not examined); the time-limit decision of those lines rests on the
      exit code 124 of timeout, and no bound or verdict depends on elapsed_s"""),
            ("limits", """the checker entries ran on this machine, in an export of the staged files, which is a second directory and no second
      environment; the frozen-build entries used a scratch commit; D13 reached m0 13 through two injected time limits at m0 11 and 12
      (rows 006 (b) and 007 (b)), so its m0 11 and m0 12 cert and verifier steps did not run at full size in this round; FZA shows eleven
      refusals and leaves the accepted freeze-argument path unexercised (row 134)"""),
            ("runs", summ), ("files", files(rh))]
else:
    f135 = [("statement", "PENDING: stage 1 of this file, written before the rehearsals ran")]
disclose("135", "v2_launcher_and_checker_rehearsals_third_correction_round", "excluded r only", f135,
 "each stdout file named in files= ends with the FLOOR_RUN or RECHECK_VERDICT line whose fields are quoted in runs=",
 "a stdout file whose last line differs",
 "a named stdout file or receipt whose FLOOR_RUN or RECHECK_VERDICT fields differ from runs=")

disclose("136", "v2_record_revision_third_correction_round", "2 rows revised and 6 rows added", [
 ("statement", """against the record of """ + C3 + """ (sha256 """ + REC3 + """) this file adds one header line, gives rows 114 and 115
  the new hashes and role text of the launcher and the evaluator (their former values: """ + DRV3 + """ and """ + EVL3 + """), adds rows
  131-136 and updates the END counts; rows 001-113 and 116-130 are byte-identical to that commit (""" + r4 + """ROW-COMPARE-78C89C31.hbp);
  the 16 PREDICT rows, the Rust source, gate_required.sh, cert_gate.py, indep_verify.py, peak_rss.py and the binary hash of row 016
  are unchanged; fields of rows 125 and 128 that this round supersedes are named in rows 133 and 134 and left in place"""),
 ("review", """the reviewer's acceptance review of 2026-11-11 is copied as """ + r4 + """REVIEW-ACCEPTANCE-20261111.md; its four gates are
  answered by rows 132 (namespace), 133 (independent verdict and certificate paths) and 134 (frozen build and full-size fallback); the
  clean-room comparison it cites matched 189246 core classes, 34920 at m0 11, 65025 at m0 12 and 89301 at m0 13, the class counts of
  rows 043 and 007"""),
 ("after_this_row", """lint_hbp.py, the pin check, the no-float gate, the CR count, the row comparison and the local git commit; none
  r-dependent; this file cannot carry their outputs without changing its own sha256; no r9 run by this seat""")],
 r4 + "ROW-COMPARE-78C89C31.hbp regenerated from the two committed files shows rows 001-113 and 116-130 with same bytes 1 and rows 114 115 with same bytes 0",
 "another row differs, or a PREDICT row differs from " + C3,
 "a byte comparison of the two committed files showing a changed row outside 114 and 115")

end_old = "PREDICTION_END|rows=130|FREEZE=12|PIN=25|REQUIRED=24|PREDICT=16|LINK=2|STATUS=9|DISCLOSE=42|DERIVED=2|CONJECTURE=15|REPORTED=50|OPEN=2|REQUIRED_TAG=61|"
end_new = "PREDICTION_END|rows=136|FREEZE=12|PIN=26|REQUIRED=25|PREDICT=16|LINK=2|STATUS=9|DISCLOSE=46|DERIVED=2|CONJECTURE=15|REPORTED=54|OPEN=2|REQUIRED_TAG=63|"
rep(end_old, "\n".join(rows) + "\n" + end_new)
for r in rows:
    assert " " not in r and "\t" not in r, r[:60]
    for m in re.finditer(r"(?<![0-9a-f])[0-9a-f]{16}(?![0-9a-f])", re.sub(r"\|files=[^|]*", "", r)):
        raise SystemExit("bare 16-hex in row " + r[:20] + " " + m.group(0))
assert "\r" not in s and all(ord(c) < 127 for c in s)
a = {l.split("|")[1]: l for l in old(NAME).decode().split("\n") if re.match(r"^[A-Z]+\|id=\d{3}\|", l)}
b = {l.split("|")[1]: l for l in s.split("\n") if re.match(r"^[A-Z]+\|id=\d{3}\|", l)}
diff = sorted(k for k in a if a[k] != b[k])
assert diff == ["id=114", "id=115"] and len(b) == 136, (diff, len(b))
open(V2 + NAME, "wb").write(s.encode("ascii"))
print("written stage", STAGE, hashlib.sha256(s.encode()).hexdigest(), "rows", len(b), "launcher", DRV[:12], "evaluator", EVL[:12], "checker", CHK[:12])
