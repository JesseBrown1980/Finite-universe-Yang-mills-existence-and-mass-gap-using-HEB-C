# Fifth correction round of the version 2 record (one commit on top of 3c41ea2d).
# Base text: the record as committed at 3c41ea2d, read from git. Every row 001-113, 115-130 and 132-141 is kept byte
# for byte. Changes: one header line added; rows 114 and 131 get the new hashes and role text; rows 142-146 are
# appended; the END counts are updated. STAGE=1 writes row 145 as PENDING; STAGE=2 fills it.
import hashlib, os, re, subprocess, sys
REPO = os.environ.get("REPO", "/root/floor-v2/repo")
VREL = "independent/y131-floor-cert-freeze-v2-20261110/"
V2 = REPO + "/" + VREL
NAME = "final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp"
C5 = "3c41ea2d9dd01de0ffcd547a7e7d417baa2ca6c0"
V5C = "c27abc8268eb7b03128c8cde91c0e7f2cfead42b"
STAGE = os.environ.get("STAGE", "1")
O = "/root/floor-v6/rehf/"
r6 = "review-v6/"
RH = r6 + "rehearsal-v2f/"

def old(rel):
    return subprocess.run(["git", "-C", REPO, "show", C5 + ":" + VREL + rel], stdout=subprocess.PIPE, check=True).stdout
def sha(rel):
    return hashlib.sha256(open(V2 + rel, "rb").read()).hexdigest()
def files(rels):
    return ",".join("%s@%s" % (r, sha(r)[:16]) for r in rels)
def U(t):
    t = " ".join(t.split()).replace(" ", "_")
    assert "|" not in t and all(32 < ord(c) < 127 for c in t), t[:80]
    return t

s = old(NAME).decode("ascii")
REC5 = hashlib.sha256(s.encode()).hexdigest()
DRV5 = hashlib.sha256(old("final/tools/run_floor.sh")).hexdigest()
EVL5 = hashlib.sha256(old("final/tools/floor_eval.py")).hexdigest()
CHK5 = hashlib.sha256(old("final/tools/recheck_floor.py")).hexdigest()
assert REC5.startswith("561e36b4") and DRV5.startswith("52036319") and EVL5.startswith("f92f404f") and CHK5.startswith("e28ea393")
for rel in ["work/design/rs/src/main.rs", "work/design/gate_required.sh", "work/design/py/cert_gate.py", "work/design/py/indep_verify.py", "work/design/peak_rss.py", "final/tools/freeze_args_controls.sh", "final/tools/floor_eval.py"]:
    assert hashlib.sha256(old(rel)).hexdigest() == sha(rel), rel
DRV, EVL, CHK = sha("final/tools/run_floor.sh"), sha("final/tools/floor_eval.py"), sha("final/tools/recheck_floor.py")
assert DRV != DRV5 and EVL == EVL5 and CHK != CHK5
lines = s.split("\n")
assert lines[-1] == "" and lines[-2].startswith("PREDICTION_END|rows=141|")

def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)

h = [l for l in lines if l.startswith("# FOURTH CORRECTION ROUND (2026-11-11, same seat)")]
assert len(h) == 1
rep(h[0] + "\n", h[0] + "\n" +
    "# FIFTH CORRECTION ROUND (2026-11-12, same seat): one commit on top of " + C5 + ". It follows the fifth final-head verification of that commit (commit " + V5C + ", verdict FAIL: one high finding on the checker, two medium findings on the launcher; copied under review-v6/). The verifier turned a falsified rehearsal result into an accepted UNRESOLVED one with weaker valid certificates; it entered stage 2 through a mount namespace that a bound file kept alive with no process in it; and it changed the frozen binary with a workspace manifest above the Rust folder. The checker now never accepts an UNRESOLVED result (row 131, new hash; row 143), the launcher refuses those two entries and requires the checkout to be at the freeze commit (row 114, new hash; row 144), and rows 142-146 are added. Rows 001-113, 115-130 and 132-141 are byte-identical to that commit; where a field of rows 138 and 139 is superseded, rows 143 and 144 say so beside it. Execution at r = 9 stays on HOLD.\n")

PINTAIL = "|tag=REQUIRED|basis=MEASURED|met_if=sha256sum_at_run_time_equals_value|not_met_if=differs|falsifier=the_logged_pin_check_line_for_this_path_showing_another_hash|json=0"
def setpin(i, path, val, role):
    l = [x for x in s.split("\n") if x.startswith("PIN|id=%s|" % i)]
    assert len(l) == 1
    m = re.match(r"^(PIN\|id=%s\|sec=launcher\|quantity=sha256\|path=%s\|value=)[0-9a-f]{64}\|role=([^|]*)(\|.*)$" % (i, re.escape(path)), l[0])
    assert m and m.group(3) == PINTAIL, l[0][:120]
    rep(l[0], m.group(1) + val + "|role=" + (role if role.startswith("second-environment") else m.group(2) + ";_" + role) + PINTAIL)
setpin("114", "final/tools/run_floor.sh", DRV, U("""fifth correction round (row 144): at the three points of row 139 the launcher also reads
 every mount table and every open descriptor and stops on a reference to its mount namespace, or to a mount namespace with no member
 process, that is not a member process; the run stops on a Cargo.toml that names a workspace in a directory above the Rust folder; with a
 frozen build the checkout must be at the freeze commit and the index may mark no file assume-unchanged or skip-worktree"""))
setpin("131", "final/tools/recheck_floor.py", CHK, U("""second-environment checker of a floor run receipt (rows 125 133 138 143), fifth correction round: run
 inside the freeze folder of a clean checkout of the freeze commit by python3 -I -B final/tools/recheck_floor.py
 receipt=RUN_DIRECTORY/FLOOR-RUN-RECEIPT.hbp, with commit=C and receipt_sha256=H for the r9 receipt; it hashes the checkout's record and
 tools and itself against rows 020 019 021 and this row, the receipt against its sha256 file and against H; it holds the frozen protocol as
 constants (r 9, steps 11 12 13, the three f words, g0) and reads a rehearsal's protocol from its PROTOCOL row; it requires the listed steps
 to be a prefix of the plan, every completed step to carry exactly the f words of the protocol, one certificate each, with file name and
 header agreeing, and no certificate elsewhere; it runs gate_required.sh once on each in an emptied environment, takes gamma, the Ritz value
 and the verifier memory from that output alone, replays the stops and the decision, refuses a step after a decision, never accepts an
 UNRESOLVED result (row 143), recomputes the PREDICT scores other than 068 and 070, and only then compares with the STEP rows, the RECHECK
 rows, the PREDICT_SCORE rows, the VERDICT_FIELDS row and the final line; for the r9 receipt it compares commit=C with the HEAD of its
 checkout where git can read one; last line RECHECK_VERDICT with ACCEPT=YES or NO; exit 0, 1 or 4; integers and integer pairs only; it
 computes no spectrum"""))

rows = []
def disclose(i, quantity, value, fields, met, notmet, fals):
    rows.append("DISCLOSE|id=%s|sec=version_2|quantity=%s|value=%s" % (i, quantity, U(value)) + "".join("|%s=%s" % (k, v if k == "files" or k == "runs" else U(v)) for k, v in fields) +
                "|tag=REPORTED|met_if=%s|not_met_if=%s|falsifier=%s|json=0" % (U(met), U(notmet), U(fals)))

vf = []
for sub in ("verifier/", "verifier/scripts/", "verifier/raw/"):
    vf += sorted(r6 + sub + x for x in os.listdir(V2 + r6 + sub) if os.path.isfile(V2 + r6 + sub + x))
HV = sha(r6 + "verifier/VERIFY-FLOOR-FREEZE-V2-FINAL5.hbp")

disclose("142", "v2_findings_of_the_fifth_final_head_verification", "verdict FAIL: integrity and the full-size run pass, the launcher has two medium findings, the checker one high finding", [
 ("report", """the verifier seat checked commit """ + C5 + """ from a fresh clone with its own scripts (its commit """ + V5C + """, report sha256
  """ + HV + """, copied with its scripts and raw outputs under """ + r6 + """verifier/); it reproduced the 721 pins, the record and tool hashes,
  the pin-free binary of row 016, clippy 1.81 and the no-float gate, the refusals NS4 FB3b FB6 of row 140 and the eleven freeze-argument
  refusals, and a full-size run to m0 13 at r 21/2 with the same G and U as the build seat's D13, accepted by the checker with the
  published hash; the rewritten receipts of its fourth report were refused, its X08 only with the published hash"""),
 ("checker_high", """X15: a rehearsal that ended BELOW at r 14 and m0 7 was given, in place of its deciding certificate, a certificate of
  the same m0, r and f word with the class vector of another certificate and a smaller t; the verifier of row 019 passes it, since any
  positive vector gives a valid upper bound and any smaller t a valid lower bound; with the receipt rewritten from the checker's own output
  the checker of that commit (sha256 """ + CHK5 + """) ended ACCEPT=YES with DECISION=UNRESOLVED; the published hash does not bind it, because
  the host publishes after it rewrites; a change from ABOVE to BELOW or from BELOW to ABOVE stays impossible"""),
 ("launcher_medium", """B2: a mount namespace kept alive by a bind mount of its nsfs file, with no process in it, entered by nsenter
  with FLOOR_STAGE=2, passed the process listing of row 139, ran to a PASS line and kept both tmpfs mounts afterwards; B5 and B7: an
  untracked or locally committed work/design/Cargo.toml that names a workspace with the Rust folder as member, with a release profile of
  its own, changed the frozen binary and the run still ended PASS; the launcher did not require the checkout to be at the freeze commit"""),
 ("low", """B3: a root process that enters by the launcher's pid between two listings and leaves is unseen, and root reads the private
  tools through /proc/PID/root during a run, against the launcher header's wording; B6b: a tracked change hidden by git update-index
  --assume-unchanged passes the status check; X04b and X08: a hand-written receipt and a failed run rewritten as PASS are accepted when no
  published hash is given, and refused with it; X06d X07b X11b: a rehearsal receipt's own PROTOCOL row can be rewritten; N03 and X02b:
  disclosed in row 139; X02c: a PREDICT_SCORE row without a row key ended the checker with a Python error and exit 1; by inspection, the
  r9 PROTOCOL row's repeated-field flag was not read and commit= was not compared with the checkout"""),
 ("supersedes", """row 139 said in its open_checker field (d) that a host cannot turn a decided result into an accepted one; as found,
  a host turned a BELOW result into an accepted UNRESOLVED one; row 143 states the rule that replaces that sentence and row 138's
  unresolved field; rows 138 and 139 are kept byte-identical beside this row"""),
 ("files", files(vf))],
 "the report named in files= lists each finding with its command and output line, and the entries X15 RU1 RA1 NS5 FB8 FB9 FB10 of row 145 end as stated there",
 "a finding of that report that this row leaves out",
 "a row of the report file with severity HIGH or MEDIUM whose name is absent from this row")

rows.append("REQUIRED|id=143|sec=version_2|quantity=v2_an_unresolved_result_is_never_accepted_by_the_checker|value=" + U("fifth final-head verification, finding X15") +
 "|rule=" + U("""the checker of row 131 ends ACCEPT=YES on a result that is ABOVE or BELOW and on no other; on an UNRESOLVED result it
  runs and prints every check of row 138 and ends ACCEPT=NO with the reason that an UNRESOLVED result is never accepted, whether or not
  all three steps completed""") +
 "|why=" + U("""ABOVE rests on a verified lower bound at or over g0 and BELOW on a verified upper bound under g0; each is a statement the
  certificates prove, and a weaker certificate cannot produce it; UNRESOLVED is the statement that no certificate of the run decides, and
  certificates cannot prove that: the verifier of row 019 passes any smaller t and the Rayleigh quotient of any positive vector, so the
  host that holds a deciding certificate can put a non-deciding one in its place; no check of the receipt or of the certificates can tell
  the two apart without redoing the writer's computation""") +
 "|standing_of_an_unresolved_receipt=" + U("""the launcher's own line and the PREDICT scoring of rows 058-073 are unchanged: an r9 run
  that ends UNRESOLVED is reported UNRESOLVED; that report is the launching host's statement and carries no acceptance of the checker;
  it would be confirmed only by a second party running the frozen protocol from the freeze commit on a host of its own, which is a new
  r9 computation outside row 008 and is the operator's and the reviewer's decision, not this seat's""") +
 "|supersedes=" + U("""the unresolved field of row 138 (an UNRESOLVED result accepted when all three steps completed) and the sentence
  (d) of the open_checker field of row 139 are superseded by this row; both rows are kept byte-identical beside it""") +
 "|tag=REQUIRED|basis=MEASURED|met_if=" + U("the checker of row 131 ends ACCEPT=NO on every receipt whose decision, computed by the checker, is UNRESOLVED (entries RU1 RA1 X15 of row 145)") +
 "|not_met_if=" + U("the pinned checker ends ACCEPT=YES with DECISION=UNRESOLVED on any receipt") +
 "|falsifier=" + U("a receipt on which the pinned checker prints RECHECK_VERDICT with ACCEPT=YES and DECISION=UNRESOLVED") + "|json=0")

disclose("144", "v2_namespace_references_workspace_manifest_freeze_head_and_what_stays_open", "fifth final-head verification, findings B2 B5 B7 B6b B3 X02c", [
 ("namespace", """at the three points of row 139 (before any work, after the two tmpfs mounts, at the close) stage 2 also reads the nsfs
  entries of every mount table under /proc and the open descriptors of every process, and lists every mount namespace that has a member
  process; a bind mount or a descriptor that names the launcher's own mount namespace stops the run, and so does one that names a mount
  namespace with no member process, through which such a reference could be hidden one level away (NOT_STARTED and exit 4 before the
  first command, CERTIFICATE=FAIL at the close); the entry of finding B2 is refused by the first of these (entry NS5 of row 145; XNS5
  shows the entry as found on the launcher of """ + C5[:8] + """)"""),
 ("build", """the walk from the Rust folder to the root directory, which row 139 gave for cargo configuration files, also stops the
  run on a Cargo.toml that contains the word workspace in any directory above work/design/rs, tracked or not (entry FB8); with a frozen
  build the HEAD of the checkout must equal the freeze commit C (entry FB9) and git ls-files -v may show no file marked assume-unchanged
  or skip-worktree (entry FB10)"""),
 ("checker_small", """a PREDICT_SCORE row without a row key gives ACCEPT=NO with its reason and no Python error; in r9 mode a PROTOCOL
  row that repeats a field gives ACCEPT=NO, and commit=C is compared with the HEAD of the checkout the checker runs in where git can
  read one (an export carries none and the output line says so); these two r9 paths cannot be rehearsed, since no r9 receipt exists"""),
 ("wording", """the launcher header no longer says that a process outside the namespace sees neither tmpfs: such a process does not
  have them in its own mount table, and root reads them through /proc/PID/root while the run lasts (finding B3)"""),
 ("open", """NAMED, not closed by this round: a root process that enters by the launcher's pid, or binds or opens its namespace file,
  between two of the three readings and undoes it before the next is unseen (windows 4 and 6 of row 127); a reference held in a pid
  namespace whose /proc this launcher cannot read is unseen; a rehearsal receipt states its own protocol, so an acceptance of a rehearsal
  receipt shows nothing about protocol rewrites (the r9 protocol is the checker's constants); without receipt_sha256=H a rehearsal
  receipt rewritten whole is accepted, and the r9 receipt is refused without H; points (a) (b) (c) of row 139 stand as written""")],
 "the entries NS5 FB8 FB9 FB10 of row 145 end with exit 4 or 1 and the reasons named there",
 "a run of the pinned launcher that ends CERTIFICATE=PASS while a bind mount names its mount namespace at the start, or with a Cargo.toml naming a workspace above the Rust folder",
 "a receipt of the pinned launcher with CERTIFICATE=PASS from a run entered through a mount namespace kept alive by a bound file")

if STAGE == "2":
    rh = sorted(RH + x for x in os.listdir(V2 + RH))
    summ = open(O + "SUMMARY.txt").read().strip().replace("\n", ";_")
    assert " " not in summ and "|" not in summ
    st1 = open(O + "STAGE1.sha256").read().split()[0]
    assert hashlib.sha256(open(V2 + RH + "RECORD-AT-REHEARSAL.hbp", "rb").read()).hexdigest() == st1
    f145 = [("statement", """test-mode runs of the pinned launcher (rows 114 115) at excluded r only and runs of the pinned checker (row
      131) on their receipts, writing outside the repository in /root/floor-v6/rehf; no r9-mode run and no computation at r 9 or within 1
      of it (the entry FZA hands r 9 to the writer and the verifier in eleven refusal controls, row 134, each ended by its refusal); they
      ran with this file in its state before this row was filled (sha256 """ + st1 + """, named in each receipt and kept as """ + RH + """RECORD-AT-REHEARSAL.hbp);
      this file differs from that state in this row only; the entries FB1 to FB10 ran in a scratch clone that held that state as a commit
      of its own; XNS5 ran the launcher of """ + C5 + """ from an export of that commit; the checker entries ran in an export of the staged
      file set; X15 was built with the verifier's weaken.py and forge.py (""" + r6 + """verifier/scripts/) on the run D3"""),
            ("limits", """the checker entries ran on this machine, in an export of the staged files, a second directory and no second
      environment; D13 reached m0 13 through two injected time limits at m0 11 and 12, so its m0 11 and m0 12 cert and verifier steps did
      not run at full size in this round; FZA leaves the accepted freeze-argument path unexercised; the r9 paths of the checker (the
      constants, commit=, the published hash requirement) are not exercised by any entry; where an INVOKE line carries a negative elapsed
      time on an injected 2-second limit, the wall clock of this WSL host stepped back between two reads (NAMED) and no bound depends on
      elapsed_s"""),
            ("runs", summ), ("files", files(rh))]
else:
    f145 = [("statement", "PENDING: stage 1 of this file, written before the rehearsals ran")]
disclose("145", "v2_launcher_and_checker_rehearsals_fifth_correction_round", "excluded r only", f145,
 "each stdout file named in files= ends with the FLOOR_RUN or RECHECK_VERDICT line whose fields are quoted in runs=",
 "a stdout file whose last line differs",
 "a named stdout file or receipt whose FLOOR_RUN or RECHECK_VERDICT fields differ from runs=")

disclose("146", "v2_record_revision_fifth_correction_round", "2 rows revised and 5 rows added", [
 ("statement", """against the record of """ + C5 + """ (sha256 """ + REC5 + """) this file adds one header line, gives rows 114 and 131 the new
  hashes of the launcher and the checker (their former values: """ + DRV5 + """ and """ + CHK5 + """) with their role text, adds rows 142-146 and
  updates the END counts; rows 001-113, 115-130 and 132-141 are byte-identical to that commit (""" + r6 + """ROW-COMPARE-3C41EA2D.hbp); the
  16 PREDICT rows, the Rust source, gate_required.sh, cert_gate.py, indep_verify.py, peak_rss.py, freeze_args_controls.sh, the evaluator
  of row 115 and the binary hash of row 016 are unchanged"""),
 ("after_this_row", """lint_hbp.py, the pin check, the no-float gate, the CR count, the row comparison and the local git commit; none
  r-dependent; this file cannot carry their outputs without changing its own sha256; no r9 run by this seat""")],
 r6 + "ROW-COMPARE-3C41EA2D.hbp regenerated from the two committed files shows rows 114 and 131 with same bytes 0 and every other row of that commit with same bytes 1",
 "another row differs, or a PREDICT row differs from " + C5,
 "a byte comparison of the two committed files showing a changed row outside 114 and 131")

end_old = "PREDICTION_END|rows=141|FREEZE=12|PIN=26|REQUIRED=26|PREDICT=16|LINK=2|STATUS=9|DISCLOSE=50|DERIVED=2|CONJECTURE=15|REPORTED=58|OPEN=2|REQUIRED_TAG=64|"
end_new = "PREDICTION_END|rows=146|FREEZE=12|PIN=26|REQUIRED=27|PREDICT=16|LINK=2|STATUS=9|DISCLOSE=54|DERIVED=2|CONJECTURE=15|REPORTED=62|OPEN=2|REQUIRED_TAG=65|"
rep(end_old, "\n".join(rows) + "\n" + end_new)
for r in rows:
    assert " " not in r and "\t" not in r, r[:60]
    for m in re.finditer(r"(?<![0-9a-f])[0-9a-f]{16}(?![0-9a-f])", re.sub(r"\|files=[^|]*", "", r)):
        raise SystemExit("bare 16-hex in row " + r[:20] + " " + m.group(0))
assert "\r" not in s and all(ord(c) < 127 for c in s)
a = {l.split("|")[1]: l for l in old(NAME).decode().split("\n") if re.match(r"^[A-Z]+\|id=\d{3}\|", l)}
b = {l.split("|")[1]: l for l in s.split("\n") if re.match(r"^[A-Z]+\|id=\d{3}\|", l)}
diff = sorted(k for k in a if a[k] != b[k])
assert diff == ["id=114", "id=131"] and len(b) == 146, (diff, len(b))
open(V2 + NAME, "wb").write(s.encode("ascii"))
print("written stage", STAGE, hashlib.sha256(s.encode()).hexdigest(), "rows", len(b), "launcher", DRV[:12], "evaluator", EVL[:12], "checker", CHK[:12])
