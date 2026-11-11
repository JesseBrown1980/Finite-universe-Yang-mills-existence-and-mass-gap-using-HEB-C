# Fourth correction round of the version 2 record (one commit on top of 5eecb540).
# Base text: the record as committed at 5eecb540, read from git. Every row 001-113, 116-130 and 132-136 is kept byte
# for byte. Changes: one header line added; rows 114, 115 and 131 get the new hashes and role text; rows 137-141 are
# appended; the END counts are updated. STAGE=1 writes row 140 as PENDING; STAGE=2 fills it.
import hashlib, os, re, subprocess, sys
REPO = os.environ.get("REPO", "/root/floor-v2/repo")
VREL = "independent/y131-floor-cert-freeze-v2-20261110/"
V2 = REPO + "/" + VREL
NAME = "final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp"
C4 = "5eecb540431a1b5665605f68ed81bc701719dcd1"
V4C = "e925e0bafac0ef0ad6bbf10212ed6faef04b6103"
STAGE = os.environ.get("STAGE", "1")
O = "/root/floor-v5/rehe/"
r5 = "review-v5/"
RH = r5 + "rehearsal-v2e/"

def old(rel):
    return subprocess.run(["git", "-C", REPO, "show", C4 + ":" + VREL + rel], stdout=subprocess.PIPE, check=True).stdout
def sha(rel):
    return hashlib.sha256(open(V2 + rel, "rb").read()).hexdigest()
def files(rels):
    return ",".join("%s@%s" % (r, sha(r)[:16]) for r in rels)
def U(t):
    t = " ".join(t.split()).replace(" ", "_")
    assert "|" not in t and all(32 < ord(c) < 127 for c in t), t[:80]
    return t

s = old(NAME).decode("ascii")
REC4 = hashlib.sha256(s.encode()).hexdigest()
DRV4 = hashlib.sha256(old("final/tools/run_floor.sh")).hexdigest()
EVL4 = hashlib.sha256(old("final/tools/floor_eval.py")).hexdigest()
CHK4 = hashlib.sha256(old("final/tools/recheck_floor.py")).hexdigest()
assert REC4.startswith("908373eb") and DRV4.startswith("1d069f79") and EVL4.startswith("00cb6334") and CHK4.startswith("19b4baf6")
for rel in ["work/design/rs/src/main.rs", "work/design/gate_required.sh", "work/design/py/cert_gate.py", "work/design/py/indep_verify.py", "work/design/peak_rss.py", "final/tools/freeze_args_controls.sh"]:
    assert hashlib.sha256(old(rel)).hexdigest() == sha(rel), rel
DRV, EVL, CHK = sha("final/tools/run_floor.sh"), sha("final/tools/floor_eval.py"), sha("final/tools/recheck_floor.py")
assert DRV != DRV4 and EVL != EVL4 and CHK != CHK4
lines = s.split("\n")
assert lines[-1] == "" and lines[-2].startswith("PREDICTION_END|rows=136|")

def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)

h = [l for l in lines if l.startswith("# THIRD CORRECTION ROUND (2026-11-11, same seat)")]
assert len(h) == 1
rep(h[0] + "\n", h[0] + "\n" +
    "# FOURTH CORRECTION ROUND (2026-11-11, same seat): one commit on top of " + C4 + ". It follows the fourth final-head verification of that commit (commit " + V4C + ", verdict FAIL on the checker; copied under review-v5/). The verifier obtained ACCEPT=YES from the checker of that commit on rewritten receipts whose decision the run had not reached. The checker is rewritten to replay the frozen protocol (row 131, new hash; row 138), the launcher refuses a mount namespace that another process holds and a build that a cargo configuration file or an untracked file could reach (rows 114 115, new hashes; row 139), and rows 137-141 are added. Rows 001-113, 116-130 and 132-136 are byte-identical to that commit; where a field of rows 127 and 133 is superseded, rows 137 and 138 say so beside it. Execution at r = 9 stays on HOLD.\n")

PINTAIL = "|tag=REQUIRED|basis=MEASURED|met_if=sha256sum_at_run_time_equals_value|not_met_if=differs|falsifier=the_logged_pin_check_line_for_this_path_showing_another_hash|json=0"
def setpin(i, path, val, role):
    l = [x for x in s.split("\n") if x.startswith("PIN|id=%s|" % i)]
    assert len(l) == 1
    m = re.match(r"^(PIN\|id=%s\|sec=launcher\|quantity=sha256\|path=%s\|value=)[0-9a-f]{64}\|role=([^|]*)(\|.*)$" % (i, re.escape(path)), l[0])
    assert m and m.group(3) == PINTAIL, l[0][:120]
    rep(l[0], m.group(1) + val + "|role=" + (role if role.startswith("second-environment") else m.group(2) + ";_" + role) + PINTAIL)
setpin("114", "final/tools/run_floor.sh", DRV, U("""fourth correction round (row 139): the mount namespace must hold this shell alone
 (checked at the start of stage 2, after the mounts and at the close); cargo runs with an empty CARGO_HOME and the run stops on a cargo
 configuration file in the Rust folder or above it and on an untracked file in the Rust folder; with a frozen build the tracked files of
 the whole repository must be unchanged; a PUBLISH line gives the receipt sha256 before the final line"""))
setpin("115", "final/tools/floor_eval.py", EVL, U("""fourth correction round (row 138): the receipt carries one PROTOCOL row with the mode, r, the
 planned steps, the f words and g0"""))
setpin("131", "final/tools/recheck_floor.py", CHK, U("""second-environment checker of a floor run receipt (rows 125 133 138), fourth correction round: run
 inside the freeze folder of a clean checkout of the freeze commit by python3 -I -B final/tools/recheck_floor.py
 receipt=RUN_DIRECTORY/FLOOR-RUN-RECEIPT.hbp, with commit=C and receipt_sha256=H for the r9 receipt; it hashes the checkout's record and
 tools and itself against rows 020 019 021 and this row, the receipt against its sha256 file and against H; it holds the frozen protocol as
 constants (r 9, steps 11 12 13, the three f words, g0) and reads a rehearsal's protocol from its PROTOCOL row; it requires the listed steps
 to be a prefix of the plan, every completed step to carry exactly the f words of the protocol, one certificate each, with file name and
 header agreeing, and no certificate elsewhere; it runs gate_required.sh once on each in an emptied environment, takes gamma, the Ritz value
 and the verifier memory from that output alone, replays the stops and the decision, refuses a step after a decision and an UNRESOLVED
 result with a step that did not complete, recomputes the PREDICT scores other than 068 and 070, and only then compares with the STEP rows,
 the RECHECK rows, the PREDICT_SCORE rows, the VERDICT_FIELDS row and the final line; last line RECHECK_VERDICT with ACCEPT=YES or NO; exit
 0, 1 or 4; integers and integer pairs only; it computes no spectrum"""))

rows = []
def disclose(i, quantity, value, fields, met, notmet, fals):
    rows.append("DISCLOSE|id=%s|sec=version_2|quantity=%s|value=%s" % (i, quantity, U(value)) + "".join("|%s=%s" % (k, v if k == "files" or k == "runs" else U(v)) for k, v in fields) +
                "|tag=REPORTED|met_if=%s|not_met_if=%s|falsifier=%s|json=0" % (U(met), U(notmet), U(fals)))

vf = sorted(r5 + "verifier/" + x for x in os.listdir(V2 + r5 + "verifier")) + sorted(r5 + "verifier/scripts/" + x for x in os.listdir(V2 + r5 + "verifier/scripts"))
vf = [x for x in vf if os.path.isfile(V2 + x)]
HV = sha(r5 + "verifier/VERIFY-FLOOR-FREEZE-V2-FINAL4.hbp")

disclose("137", "v2_findings_of_the_fourth_final_head_verification", "verdict FAIL on the checker; items A B E F pass, C passes with one medium finding", [
 ("report", """the verifier seat checked commit """ + C4 + """ from a fresh clone with its own scripts (its commit """ + V4C + """, report sha256
  """ + HV + """, copied with its scripts under """ + r5 + """verifier/); it reproduced the pins, the pin-free binary of row 016, clippy and the
  no-float gate, the namespace refusals, the frozen-build rehearsal, the eleven freeze-argument refusals and a full-size run to m0 13 with
  the same G and U as the build seat's D13, and the checker's verdict on five honest receipts"""),
 ("checker_high", """the checker of that commit (sha256 """ + CHK4 + """) gave ACCEPT=YES on rewritten receipts, each with its sha256 file
  rewritten: X06 a run that ended BELOW at its second step, with that step's certificates and rows removed, accepted as UNRESOLVED; X07 a
  run of one f word that was UNRESOLVED, with a certificate of another f word from another run added, accepted as ABOVE; X08 a run the
  launcher had failed on a lowered memory limit, rewritten as a PASS receipt; X04 a hand-written receipt of 8 rows around real certificates;
  X02 every PREDICT_SCORE outcome set to MET"""),
 ("checker_medium_low", """N03 certificate bytes substituted with the row sha256 updated, still verifying; N12 a ritz_writer value that
  was not the smallest altered; X01 a second DECISION and PREDICTION field appended to the verdict rows; X03 STEP rows set to
  resource_limit EXCEEDED; X05 a certificate file renamed to another f word; in test mode g0 was read before the decision; the verifier
  memory was printed and never compared with the limit"""),
 ("launcher", """C4 (medium): stage 2 entered by nsenter through a private mount namespace that another process held was not refused, ran
  to a PASS line, and its tools could be listed from outside through that process; C5 (low): a nested private namespace entered without
  stage 1 runs; E4 (medium): an untracked work/design/rs/.cargo/config.toml changed the frozen binary and the run still ended PASS; E3b
  (low): a modified tracked file outside the freeze folder was not refused"""),
 ("supersedes", """the control field of row 127 said that a false acceptance on the launching host does not survive the rerun of the
  verifier in a second environment; as found, a rewritten receipt did survive the checker of """ + C4[:8] + """; what the checker now binds is
  stated in row 138 and what it leaves open in row 139; row 127 is kept byte-identical beside this row"""),
 ("note", """the verifier's frozen-build rehearsal compiled a binary with the commit """ + C4 + """ and the record hash of that commit; it was
  not run at r 9; the freeze commit of this round is another commit, so that binary does not carry this round's pins"""),
 ("files", files(vf))],
 "the report named in files= lists each finding with its exit code, and the entries P5 (X01), P4 (X02), P6 (X03), P7 (X05), P1 and P1b (X06), P2 (X07) and N20 (N12) of row 140 end ACCEPT=NO on this checker",
 "a finding of that report that this row leaves out",
 "a row of the report file with severity HIGH or MEDIUM whose name is absent from this row")

rows.append("REQUIRED|id=138|sec=version_2|quantity=v2_the_checker_replays_the_frozen_protocol|value=" + U("fourth final-head verification, findings X02 X04 X06 X07 X08") +
 "|rule=" + U("""ACCEPT=YES of the checker of row 131 says three things: (1) every certificate the protocol calls for is present and passes
  the verifier of row 019 in the checker's environment; (2) the list of certificates is the one the frozen protocol produces, no more and
  no fewer: the listed steps are a prefix of 11 12 13, every completed step carries the f words 1, 8,7,6,5,4 and 6,5,4,3 once each with file
  name and certificate header agreeing in m0, r and f, no certificate file lies in a RUN folder beside them, and no step follows a step at
  which the result was already ABOVE or BELOW; (3) the decision, G, the upper bound, the per-step G and U and the PREDICT scores 058-067,
  069 and 071-073 that the checker computes from its own verifier output equal those of the receipt""") +
 "|unresolved=" + U("""an UNRESOLVED result is accepted only when all three steps completed with all their certificates; with a step that
  did not complete (an operational failure of rows 006 (b) and 007 (b), a stop at the prerequisite of row 007) the checker ends ACCEPT=NO
  and the reading belongs to the reviewer: the checker cannot tell a step that failed from a step whose certificates were removed; an
  ABOVE or BELOW result stands on certificates verified by the checker and is accepted with earlier steps not completed""") +
 "|published_hash=" + U("""the launcher prints a PUBLISH line with the sha256 of the receipt before its final line; for the r9 receipt the
  checker requires receipt_sha256=H and refuses a receipt that does not hash to it; H is made public when the run ends, so a receipt
  rewritten afterwards is refused whatever its sha256 file says""") +
 "|comparisons=" + U("""the receipt's UPPER_BOUND must equal the checker's upper bound and each row's ritz_writer the checker's Ritz value
  (the two definitions of U of row 012 have agreed in every run; where they differ the checker ends ACCEPT=NO); a repeated field in a
  verdict row, a STEP row that does not read the full accepted count with resource_limit HELD, a PREDICT_SCORE row that differs and a
  verifier memory at or over 2097152 kB each give ACCEPT=NO""") +
 "|rehearsals=" + U("""a rehearsal receipt states its own protocol in its PROTOCOL row (steps, f words, g0) and the checker replays that
  one; an acceptance of a rehearsal receipt is no acceptance of a result""") +
 "|supersedes=" + U("""in row 133 the rule field's sentence (d) and the never_an_input field's last clauses (the receipt's UPPER_BOUND
  compared with the smallest of the rows' ritz_writer values; g0 of a rehearsal read from VERDICT_FIELDS) are superseded by this row; row
  133 is kept byte-identical beside this row""") +
 "|tag=REQUIRED|basis=MEASURED|met_if=" + U("the checker of row 131, run in a second environment on the r9 receipt with commit=C and receipt_sha256=H, ends RECHECK_VERDICT with ACCEPT=YES") +
 "|not_met_if=" + U("the checker ends ACCEPT=NO, exits 4, was run without the published hash, or was not run in a second environment") +
 "|falsifier=" + U("a receipt that the pinned checker accepts and whose list of certificates differs from the list the frozen protocol produces on the certificates' own values") + "|json=0")

disclose("139", "v2_exclusive_namespace_build_environment_and_what_stays_open", "fourth final-head verification, findings C4 E4 E3b, and the limits of the checker", [
 ("namespace", """stage 2 lists every process whose mount namespace is its own (readlink of /proc/PID/ns/mnt) and stops unless each is this
  shell or a child of it: before any work (NOT_STARTED, exit 4), again after the two tmpfs mounts, and at the close, where another process
  in the namespace gives CERTIFICATE=FAIL; an entry through a namespace that another process holds is refused by the first of these
  (entry NS4 of row 140; XNS4 shows the entry as found on the launcher of """ + C4[:8] + """)"""),
 ("build", """cargo runs with CARGO_HOME set to an empty directory on the launcher's tmpfs; the run stops with CERTIFICATE=FAIL on a
  .cargo/config.toml or .cargo/config in work/design/rs or in any directory above it, and on an untracked file in work/design/rs outside
  target/ (git ls-files --others); with a frozen build the tracked files of the whole repository, and no longer of the freeze folder alone,
  must be unchanged (entries FB3b FB6 FB7 of row 140)"""),
 ("open_checker", """NAMED, not closed by this round: (a) the writer's peak memory is a value of the launching host; the checker compares
  its own verifier memory with the limit and reports the writer's value as not rechecked; (b) PREDICT rows 068 and 070 read writer-side
  values and are reported NOT_RECHECKED; (c) a certificate is accepted on what the verifier proves from its rows, whoever wrote it: a
  frozen binary can be compiled by anyone with a 40-hex commit and the record hash, and a certificate with the frozen m0, r and f word that
  passes the verifier is a valid lower bound whatever program wrote it (finding N03); (d) a host that removes certificates before it
  publishes the receipt hash can turn a decided result into an unaccepted one, and cannot turn it into an accepted one"""),
 ("open_launcher", """NAMED: a root process that enters the namespace between two of the three listings and leaves again is unseen
  (window 4 of row 127); C5, a nested private namespace entered without stage 1, runs with the caller's FLOOR_ROOT, whose launcher file
  must still hash to row 114""")],
 "the entries NS4 FB3b FB6 FB7 of row 140 end with exit 4 or 1 and the reasons named there",
 "a run of the pinned launcher that ends CERTIFICATE=PASS with a second process in its mount namespace at the start, or with a cargo configuration file in the Rust folder",
 "a receipt of the pinned launcher with CERTIFICATE=PASS from a run entered through a namespace held by another process")

if STAGE == "2":
    rh = sorted(RH + x for x in os.listdir(V2 + RH))
    summ = open(O + "SUMMARY.txt").read().strip().replace("\n", ";_")
    assert " " not in summ and "|" not in summ
    st1 = open(O + "STAGE1.sha256").read().split()[0]
    assert hashlib.sha256(open(V2 + RH + "RECORD-AT-REHEARSAL.hbp", "rb").read()).hexdigest() == st1
    f140 = [("statement", """test-mode runs of the pinned launcher (rows 114 115) at excluded r only and runs of the pinned checker (row
      131) on their receipts, writing outside the repository in /root/floor-v5/rehe; no r9-mode run and no computation at r 9 or within 1
      of it (the entry FZA hands r 9 to the writer and the verifier in eleven refusal controls, row 134, each ended by its refusal); they
      ran with this file in its state before this row was filled (sha256 """ + st1 + """, named in each receipt and kept as """ + RH + """RECORD-AT-REHEARSAL.hbp);
      this file differs from that state in this row only; the entries FB1 FB2 FB3 FB3b FB6 FB7 ran in a scratch clone that held that state
      as a commit of its own; XNS4 ran the launcher of """ + C4 + """ from an export of that commit; the checker entries ran in an export of
      the staged file set"""),
            ("limits", """the checker entries ran on this machine, in an export of the staged files, a second directory and no second
      environment; D13 reached m0 13 through two injected time limits at m0 11 and 12, so its m0 11 and m0 12 cert and verifier steps did
      not run at full size in this round; FZA leaves the accepted freeze-argument path unexercised; the verifier's X08 and X04 rewritings
      were not rebuilt by this seat and are left to the verifier's rerun; where an INVOKE line carries a negative elapsed time on an
      injected 2-second limit, the wall clock of this WSL host stepped back between two reads (NAMED) and no bound depends on elapsed_s"""),
            ("runs", summ), ("files", files(rh))]
else:
    f140 = [("statement", "PENDING: stage 1 of this file, written before the rehearsals ran")]
disclose("140", "v2_launcher_and_checker_rehearsals_fourth_correction_round", "excluded r only", f140,
 "each stdout file named in files= ends with the FLOOR_RUN or RECHECK_VERDICT line whose fields are quoted in runs=",
 "a stdout file whose last line differs",
 "a named stdout file or receipt whose FLOOR_RUN or RECHECK_VERDICT fields differ from runs=")

disclose("141", "v2_record_revision_fourth_correction_round", "3 rows revised and 5 rows added", [
 ("statement", """against the record of """ + C4 + """ (sha256 """ + REC4 + """) this file adds one header line, gives rows 114, 115 and 131 the
  new hashes of the launcher, the evaluator and the checker (their former values: """ + DRV4 + """, """ + EVL4 + """ and """ + CHK4 + """) with their
  role text, adds rows 137-141 and updates the END counts; rows 001-113, 116-130 and 132-136 are byte-identical to that commit
  (""" + r5 + """ROW-COMPARE-5EECB540.hbp); the 16 PREDICT rows, the Rust source, gate_required.sh, cert_gate.py, indep_verify.py,
  peak_rss.py, freeze_args_controls.sh and the binary hash of row 016 are unchanged"""),
 ("after_this_row", """lint_hbp.py, the pin check, the no-float gate, the CR count, the row comparison and the local git commit; none
  r-dependent; this file cannot carry their outputs without changing its own sha256; no r9 run by this seat""")],
 r5 + "ROW-COMPARE-5EECB540.hbp regenerated from the two committed files shows rows 114 115 131 with same bytes 0 and every other row of that commit with same bytes 1",
 "another row differs, or a PREDICT row differs from " + C4,
 "a byte comparison of the two committed files showing a changed row outside 114 115 131")

end_old = "PREDICTION_END|rows=136|FREEZE=12|PIN=26|REQUIRED=25|PREDICT=16|LINK=2|STATUS=9|DISCLOSE=46|DERIVED=2|CONJECTURE=15|REPORTED=54|OPEN=2|REQUIRED_TAG=63|"
end_new = "PREDICTION_END|rows=141|FREEZE=12|PIN=26|REQUIRED=26|PREDICT=16|LINK=2|STATUS=9|DISCLOSE=50|DERIVED=2|CONJECTURE=15|REPORTED=58|OPEN=2|REQUIRED_TAG=64|"
rep(end_old, "\n".join(rows) + "\n" + end_new)
for r in rows:
    assert " " not in r and "\t" not in r, r[:60]
    for m in re.finditer(r"(?<![0-9a-f])[0-9a-f]{16}(?![0-9a-f])", re.sub(r"\|files=[^|]*", "", r)):
        raise SystemExit("bare 16-hex in row " + r[:20] + " " + m.group(0))
assert "\r" not in s and all(ord(c) < 127 for c in s)
a = {l.split("|")[1]: l for l in old(NAME).decode().split("\n") if re.match(r"^[A-Z]+\|id=\d{3}\|", l)}
b = {l.split("|")[1]: l for l in s.split("\n") if re.match(r"^[A-Z]+\|id=\d{3}\|", l)}
diff = sorted(k for k in a if a[k] != b[k])
assert diff == ["id=114", "id=115", "id=131"] and len(b) == 141, (diff, len(b))
open(V2 + NAME, "wb").write(s.encode("ascii"))
print("written stage", STAGE, hashlib.sha256(s.encode()).hexdigest(), "rows", len(b), "launcher", DRV[:12], "evaluator", EVL[:12], "checker", CHK[:12])
