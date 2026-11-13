#!/bin/bash
# freeze_args_controls.sh -- refusal controls of the freeze arguments (row 134). No spectrum is computed.
#   bash final/tools/freeze_args_controls.sh FROZEN_BINARY PINFREE_BINARY COMPILED_COMMIT COMPILED_PREDICTION_SHA256
# FROZEN_BINARY is a floorcert built with FLOORCERT_FREEZE_COMMIT=COMPILED_COMMIT and
# FLOORCERT_PREDICTION_SHA256=COMPILED_PREDICTION_SHA256 (the binary of a --test-frozen-build rehearsal, target/release/
# floorcert in its run directory). PINFREE_BINARY is the binary of row 016.
# The writer and the verifier read the freeze arguments at r = 9 only. Each command below hands them r = 9 together
# with one freeze argument that is absent or wrong BY CONSTRUCTION, so the program must print its refusal and stop
# before any computation that depends on r: in main.rs the function r_policy runs in cert before the rows are built
# and every refusal in it ends the process; in cert_gate.py the r9_frozen_mode gate ends the process the same way.
# The one argument set that would be accepted (the compiled commit, the compiled hash and a prediction file with that
# hash) is never formed here: no command passes a readable prediction file that hashes to COMPILED_PREDICTION_SHA256.
# This script refuses to start if such a file is among its own inputs. So no r = 9 calculation can start.
# Read in the two sources (2026-11-11): cert() of main.rs makes the S3 and lattice tables (no r in them), then calls
# r_policy for every r, and only then build(), which enumerates and builds rows; cert_gate.py makes the same kind of
# tables at the top of the file, reads the header, reaches the r9_frozen_mode gate and only later enumerates.
# Second barrier: every command names m0 = 13 and runs under a 5 second limit. At m0 = 13 the enumeration alone takes
# minutes, so a command that did not refuse would be ended long before any value that depends on r exists.
# The suite stops at the first control that is not refused as expected and does not try again.
# Every control prints its argument list, its exit code and every line the program wrote (stdout and stderr).
# The accepted path itself (the FREEZE line and what follows) stays unexercised until the r = 9 run.
# Last line: FREEZE_ARGS_CONTROLS|controls=N|refused=N|...   Exit 0 when every control was refused as expected, else 1.
set -u
[ $# -eq 4 ] || { echo "FREEZE_ARGS_CONTROLS|not_started=four_arguments_needed|json=0"; exit 4; }
FB=$1; PF=$2; SC=$3; SP=$4
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P); ROOT=$(cd "$HERE/../.." && pwd -P)
VER="$ROOT/work/design/py/cert_gate.py"
echo "$SC" | grep -Eq '^[0-9a-f]{40}$' && echo "$SP" | grep -Eq '^[0-9a-f]{64}$' || { echo "FREEZE_ARGS_CONTROLS|not_started=commit_or_hash_malformed|json=0"; exit 4; }
[ -x "$FB" ] && [ -x "$PF" ] && [ -f "$VER" ] || { echo "FREEZE_ARGS_CONTROLS|not_started=a_binary_or_the_verifier_is_absent|json=0"; exit 4; }
T=$(mktemp -d) || exit 4
trap 'rm -rf "$T"' EXIT
ZC=0000000000000000000000000000000000000000
ZP=0000000000000000000000000000000000000000000000000000000000000000
[ "$SC" != "$ZC" ] && [ "$SP" != "$ZP" ] || { echo "FREEZE_ARGS_CONTROLS|not_started=compiled_values_are_zeros|json=0"; exit 4; }
# the only prediction files used: one that does not exist, and an empty file (sha256 e3b0c442..., never a 64-hex pin of a record)
NOFILE="$T/absent-prediction-file"; EMPTY="$T/empty"; : > "$EMPTY"
[ ! -e "$NOFILE" ] && [ ! -s "$EMPTY" ] || exit 4
[ "$(sha256sum "$EMPTY" | cut -d' ' -f1)" != "$SP" ] || { echo "FREEZE_ARGS_CONTROLS|not_started=the_empty_file_has_the_compiled_hash|json=0"; exit 4; }
N=0; OKN=0; FZ=0; STOPPED=0
ctl() { # name expected-exit expected-words program args...
  local nm=$1 we=$2 ww=$3; shift 3
  local out rc first ok=0
  [ $STOPPED -eq 0 ] || return 0
  echo "ARGV|name=$nm|$(printf '%s ' "$@" | sed "s#$T#TMP#g" | tr '|' ':')|json=0"
  out=$(timeout -k 1 5 "$@" 2>&1); rc=$?
  printf '%s
' "$out" | sed "s#$T#TMP#g" | while IFS= read -r l; do echo "OUT|name=$nm|$(printf '%s' "$l" | tr '|' ':')"; done
  first=$(printf '%s\n' "$out" | grep -E '^REFUSE\||^VERDICT\|REFUSE' | head -1)
  printf '%s\n' "$out" | grep -q '^FREEZE|' && FZ=$((FZ+1))
  N=$((N+1))
  if [ $rc -eq "$we" ] && printf '%s\n' "$out" | grep -Fq -- "$ww" && ! printf '%s\n' "$out" | grep -Eq '^FREEZE\||^CERT\||^ROWHASH\||^ENUM\|'; then ok=1; OKN=$((OKN+1)); fi
  echo "CONTROL|name=$nm|exit=$rc|expected_exit=$we|refused_as_expected=$ok|lines=$(printf '%s\n' "$out" | grep -c .)|first_refusal=$(printf '%s' "$first" | tr ' |' '_:' | cut -c1-200)|json=0"
  [ $ok -eq 1 ] || { STOPPED=1; echo "SUITE_STOPPED|at=$nm|reason=the_control_was_not_refused_as_expected|no_retry=1|json=0"; }
}
W=(cert --m0 13 --r 9 --f 1 --threads 1 --dir "$T/RUNX")
ctl W0_pin_free_binary 3 "not the frozen binary" "$PF" "${W[@]}" --freeze-commit "$SC" --prediction "$NOFILE" --prediction-sha256 "$SP"
ctl W1_no_freeze_argument 3 "differs from the pins compiled" "$FB" "${W[@]}"
ctl W2_wrong_commit 3 "differs from the pins compiled" "$FB" "${W[@]}" --freeze-commit "$ZC" --prediction "$NOFILE" --prediction-sha256 "$SP"
ctl W3_wrong_prediction_hash 3 "differs from the pins compiled" "$FB" "${W[@]}" --freeze-commit "$SC" --prediction "$NOFILE" --prediction-sha256 "$ZP"
ctl W4_prediction_file_absent 3 "prediction file unreadable" "$FB" "${W[@]}" --freeze-commit "$SC" --prediction "$NOFILE" --prediction-sha256 "$SP"
ctl W5_prediction_file_with_another_hash 3 "does not hash to the frozen prediction sha256" "$FB" "${W[@]}" --freeze-commit "$SC" --prediction "$EMPTY" --prediction-sha256 "$SP"
# the verifier: a certificate header at r = 9 with no row, written here; it is no certificate of anything
HD="# floorcert certificate: m0=13 r=9/1 t=1/1 f=1 cap=1/1 rowhash=$ZP keyshash=$ZP"
printf '%s freeze=%s pred=%s\n' "$HD" "$SC" "$SP" > "$T/h1.txt"
printf '%s freeze=%s pred=%s\n' "$HD" "$SC" "$ZP" > "$T/h2.txt"
V=(python3 -I -B "$VER")
ctl V1_no_freeze_argument 1 "r = 9 needs --freeze-commit" "${V[@]}" "$T/h1.txt"
ctl V2_prediction_file_absent 1 "prediction file unreadable" "${V[@]}" "$T/h1.txt" --freeze-commit "$SC" --prediction "$NOFILE" --prediction-sha256 "$SP"
ctl V3_prediction_file_with_another_hash 1 "must agree" "${V[@]}" "$T/h1.txt" --freeze-commit "$SC" --prediction "$EMPTY" --prediction-sha256 "$SP"
ctl V4_wrong_commit_and_a_file_with_another_hash 1 "must agree" "${V[@]}" "$T/h1.txt" --freeze-commit "$ZC" --prediction "$EMPTY" --prediction-sha256 "$SP"
ctl V5_header_with_another_prediction_and_a_file_with_another_hash 1 "must agree" "${V[@]}" "$T/h2.txt" --freeze-commit "$SC" --prediction "$EMPTY" --prediction-sha256 "$SP"
[ -e "$T/RUNX" ] && RX=1 || RX=0
echo "FREEZE_ARGS_CONTROLS|controls_planned=11|suite_stopped_early=$STOPPED|controls=$N|refused=$OKN|numerical_output_lines=0_(no_CERT_ROWHASH_ENUM_or_FREEZE_line_in_any_refused_control)|accepted_certificates=0|freeze_lines_printed=$FZ|run_directory_created=$RX|frozen_binary_sha256=$(sha256sum "$FB" | cut -d' ' -f1)|compiled_commit=$SC|compiled_prediction_sha256=$SP|accepted_argument_set_formed=0|json=0"
[ $OKN -eq 11 ] && [ $N -eq 11 ] && [ $STOPPED -eq 0 ] && [ $FZ -eq 0 ] && [ $RX -eq 0 ] && exit 0
exit 1
