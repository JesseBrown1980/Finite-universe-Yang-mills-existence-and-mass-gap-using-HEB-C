#!/bin/bash
# run_floor.sh -- single launcher of the frozen floor-certificate run (version 2 freeze, correction round).
#   frozen run: bash final/tools/run_floor.sh --launch-r9 [--freeze-commit C]
#               r = 9, m0 = 11, then 12 and 13 only under rows 006 and 007 of the prediction record.
#               The token --launch-r9 is the only way into this mode; no other argument set reaches r = 9.
#   rehearsal:  bash final/tools/run_floor.sh --test-r R --test-m0 a,b,c --test-f WORDS --test-g0 N/D --test-out DIR
#               [--test-plant IDX:UB] [--test-crash LIST] [--test-hang LIST] [--test-hang-hard LIST]
#               [--test-vexc IDX] [--test-census] [--test-limit-kb N]
#               (LIST is IDX:KIND[,IDX:KIND...]; KIND is rowhash, cert, rowsonly or gate)
#               R must lie more than 1 away from 9; the binary's own r policy stays in force.
# Every path is derived from this file's location. One heavy process at a time. No retry beyond row 008:
# one rerun with identical arguments after a crash, for the whole run, both attempts logged; a time limit gets none.
# ISOLATED TOOLS: gate_required.sh, cert_gate.py, indep_verify.py, peak_rss.py, the evaluator, the prediction record
# and the binary are copied into a fresh private directory (mktemp -d, mode 700); the copies are hashed against the
# frozen SHA-256 values and made read-only, and only the copies are executed. The copies and the files in the tree
# are hashed again before every invocation and at the close. This file is read to its end before its first command.
# A certificate counts only with a logged verifier invocation that exited 0 (row 122).
# A completed process at or over 2097152 kB gives CERTIFICATE=FAIL, RESOURCE_LIMIT_EXCEEDED, and no fallback (row 122).
# The last line printed is FLOOR_RUN|CERTIFICATE=PASS or FAIL|PREDICTION=CONFIRMED or FALSIFIED or UNRESOLVED|
# DECISION=ABOVE or BELOW or UNRESOLVED|GAMMA=|UPPER_BOUND=|...|HASHES=
# Exit: 0 CERTIFICATE=PASS and PREDICTION=CONFIRMED; 3 CERTIFICATE=PASS and PREDICTION=FALSIFIED;
#       2 nothing decided (UNRESOLVED, or no accepted certificate for an operational reason, or not started);
#       1 CERTIFICATE=FAIL after a REQUIRED, resource-limit or integrity failure (rows 008 011).
set -u
{
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT" || exit 2
[ -d "$HOME/.cargo/bin" ] && export PATH="$HOME/.cargo/bin:$PATH"
PREDREL=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
PEAK=work/design/peak_rss.py
GATE=work/design/gate_required.sh
VERIFIER=work/design/py/cert_gate.py
INDEP=work/design/py/indep_verify.py
PINFREE=work/design/rs/target/release/floorcert
LIMIT=21600
KILLAFTER=30
RUSTC_PIN="rustc 1.81.0 (eeb90cda1 2024-09-04)"
CARGO_PIN="cargo 1.81.0 (2dbb1af80 2024-08-20)"
NOBOUND="PREDICTION=UNRESOLVED|DECISION=UNRESOLVED|GAMMA=NONE|UPPER_BOUND=NONE"
MODE=none; R=9; STEPS=(11 12 13); FSPEC='1;8,7,6,5,4;6,5,4,3'; G0=94070673/1000000; OUT=work/run9
C=""; T_R=""; T_PLANT=""; T_CRASH=""; T_HANG=""; T_HARD=""; T_VEXC=""; T_LIM=""; CENSUS=0; T_ANY=0; LAUNCH=0
arg_stop() { # reason ; nothing has run
  echo "FLOOR_RUN|CERTIFICATE=FAIL|$NOBOUND|certificate_reason=NOT_STARTED|stage=arguments|reason=$1|steps_run=none|accepted_certificates=0|certificate_commands_run=0|HASHES=NONE|json=0"
  exit 2
}
while [ $# -gt 0 ]; do
  case "$1" in
    --launch-r9) LAUNCH=1; shift; continue;;
    --test-census) CENSUS=1; T_ANY=1; shift; continue;;
    --freeze-commit|--test-r|--test-m0|--test-f|--test-g0|--test-out|--test-plant|--test-crash|--test-hang|--test-hang-hard|--test-vexc|--test-limit-kb) ;;
    *) arg_stop unknown_argument;;
  esac
  [ $# -ge 2 ] && [ -n "$2" ] || arg_stop "option_${1#--}_needs_a_value"
  case "$1" in
    --freeze-commit) C="$2";;
    --test-r) T_R="$2"; T_ANY=1;;
    --test-m0) IFS=, read -r -a STEPS <<< "$2"; T_ANY=1;;
    --test-f) FSPEC="$2"; T_ANY=1;;
    --test-g0) G0="$2"; T_ANY=1;;
    --test-out) OUT="$2"; T_ANY=1;;
    --test-plant) T_PLANT="$2"; T_ANY=1;;
    --test-crash) T_CRASH="$2"; T_ANY=1;;
    --test-hang) T_HANG="$2"; T_ANY=1;;
    --test-hang-hard) T_HARD="$2"; T_ANY=1;;
    --test-vexc) T_VEXC="$2"; T_ANY=1;;
    --test-limit-kb) T_LIM="$2"; T_ANY=1; case "$2" in *[!0-9]*) arg_stop test_limit_kb_takes_digits;; esac;;
  esac
  shift 2
done
if [ $LAUNCH -eq 1 ]; then
  [ $T_ANY -eq 0 ] || arg_stop launch_r9_takes_no_test_option
  MODE=r9
elif [ -n "$T_R" ]; then
  [ -z "$C" ] || arg_stop freeze_commit_belongs_to_launch_r9
  MODE=test; R="$T_R"
elif [ $T_ANY -ne 0 ]; then
  arg_stop test_options_need_test_r
else
  arg_stop no_mode_given_use_launch_r9_or_test_r
fi
LIMARG=(); [ -n "$T_LIM" ] && LIMARG=("limkb=$T_LIM")
LOG=""; SEQ=0; RERUNS=1; STOP=DECIDED; RUNSTEPS=""; FB=""; FBSHA=NONE; RC=0; TIMEDOUT=0; CLS=ok
BADFILE=""; BADWANT=""; PRIV=""
cleanup() { [ -n "$PRIV" ] && [ -d "$PRIV" ] && { chmod -R u+w "$PRIV" 2>/dev/null; rm -rf "$PRIV"; }; return 0; }
trap cleanup EXIT
has() { case ",$1," in *",$2,"*) return 0;; esac; return 1; } # list item
say() { echo "$1"; [ -n "$LOG" ] && echo "$1" >> "$LOG/run.log"; return 0; }
prelude_stop() { # class reason ; class FAIL = integrity or REQUIRED failure, UNRESOLVED = not started
  local cr=NOT_STARTED; [ "$1" = FAIL ] && cr=REQUIRED_OR_INTEGRITY_FAILURE_ROW_008
  say "FLOOR_RUN|CERTIFICATE=FAIL|$NOBOUND|certificate_reason=$cr|stage=prelude|reason=$2|r=$R|steps_run=none|accepted_certificates=0|certificate_commands_run=0|HASHES=NONE|json=0"
  [ "$1" = FAIL ] && exit 1; exit 2
}
# ---- the pinned hashes, read from the record by this script itself (rows 019 020 021 103 114 115)
P=$(sha256sum "$PREDREL" | cut -d' ' -f1)
pinval() { grep -E "^PIN\|id=$1\|" "$PREDREL" | sed -n 's/.*|value=\([0-9a-f]\{64\}\)|.*/\1/p'; }
GF=("$PREDREL" "$HERE/run_floor.sh" "$HERE/floor_eval.py" "$GATE" "$VERIFIER" "$INDEP" "$PEAK")
GW=("$P" "$(pinval 114)" "$(pinval 115)" "$(pinval 020)" "$(pinval 019)" "$(pinval 021)" "$(pinval 103)")
guard() { # 0 when every file of GF still has the hash of GW; else BADFILE and BADWANT name the first that differs
  local i got
  for i in "${!GF[@]}"; do
    got=$(sha256sum "${GF[$i]}" 2>/dev/null | cut -d' ' -f1)
    if [ ${#GW[$i]} -ne 64 ] || [ "$got" != "${GW[$i]}" ]; then BADFILE="${GF[$i]}"; BADWANT="${GW[$i]:-NO_PIN_ROW}"; return 1; fi
  done
  return 0
}
hashes_of_out() {
  ( cd "$OUT" 2>/dev/null && find . -type f ! -name 'FLOOR-RUN-RECEIPT.hbp*' ! -path './target/*' | LC_ALL=C sort | while read -r f; do
      printf '%s@%s,' "${f#./}" "$(sha256sum "$f" | cut -d' ' -f1)"; done ) | sed 's/,$//'
}
integrity_stop() { # a pinned file or a private copy differs: no evaluator call, no accepted bound, CERTIFICATE=FAIL
  local got fin m rc="$OUT/FLOOR-RUN-RECEIPT.hbp" nm="${BADFILE#"$ROOT"/}"
  [ -n "$PRIV" ] && nm="${nm/#"$PRIV"/PRIVATE_COPY}"
  got=$(sha256sum "$BADFILE" 2>/dev/null | cut -d' ' -f1)
  [ -n "$LOG" ] || prelude_stop FAIL "pinned_file_differs_${BADFILE##*/}"
  say "INTEGRITY|file=$nm|want=$BADWANT|got=${got:-ABSENT}|json=0"
  fin="FLOOR_RUN|CERTIFICATE=FAIL|$NOBOUND|certificate_reason=REQUIRED_OR_INTEGRITY_FAILURE_ROW_008|stage=integrity|reason=pinned_file_changed_${BADFILE##*/}|r=$R|steps_run=${RUNSTEPS:-none}|accepted_certificates=0|prediction_sha256=$P|binary_sha256=$FBSHA|HASHES=$(hashes_of_out)|json=0"
  {
    echo "# floor run receipt written by final/tools/run_floor.sh after an integrity stop; pipe rows; json=0"
    echo "RECEIPT|scope=INTEGRITY_STOP|r=$R|mode=$MODE|json=0"
    echo "INTEGRITY|file=$nm|want=$BADWANT|got=${got:-ABSENT}|json=0"
    for m in "${STEPS[@]}"; do [ -e "$LOG/m${m}_rowhash_a1.txt" ] && echo "ACCEPTED|m0=$m|count=0|json=0"; done
    grep -E '^(INVOKE|INJECTED|NOTE|DECISION|TOOL)\|' "$LOG/run.log"
    echo "$fin"
  } > "$rc"
  ( cd "$OUT" && sha256sum FLOOR-RUN-RECEIPT.hbp > FLOOR-RUN-RECEIPT.hbp.sha256 )
  echo "$fin"; exit 1
}
guard || integrity_stop
# ---- the isolated copies: a fresh private directory, each copy hashed against its frozen value, only the copies run
PRIV=$(mktemp -d "${TMPDIR:-/tmp}/floor-run-tools.XXXXXXXX") || { PRIV=""; prelude_stop UNRESOLVED cannot_create_the_private_tool_directory; }
chmod 700 "$PRIV" && mkdir "$PRIV/py" || prelude_stop UNRESOLVED cannot_create_the_private_tool_directory
TSRC=("$GATE" "$VERIFIER" "$INDEP" "$PEAK" "$HERE/floor_eval.py" "$PREDREL")
TDST=("$PRIV/gate_required.sh" "$PRIV/py/cert_gate.py" "$PRIV/py/indep_verify.py" "$PRIV/peak_rss.py" "$PRIV/floor_eval.py" "$PRIV/${PREDREL##*/}")
TWANT=("$(pinval 020)" "$(pinval 019)" "$(pinval 021)" "$(pinval 103)" "$(pinval 115)" "$P")
TROW=(020 019 021 103 115 record)
for i in "${!TSRC[@]}"; do
  cp "${TSRC[$i]}" "${TDST[$i]}" || prelude_stop UNRESOLVED cannot_copy_a_tool_into_the_private_directory
  GF+=("${TDST[$i]}"); GW+=("${TWANT[$i]}")
done
chmod -R a-w "$PRIV"; chmod u+w "$PRIV"
guard || integrity_stop
GATE="$PRIV/gate_required.sh"; VERIFIER="$PRIV/py/cert_gate.py"; PEAK="$PRIV/peak_rss.py"; PPRED="$PRIV/${PREDREL##*/}"
EVAL=(python3 -I -B "$PRIV/floor_eval.py")
if [ "$MODE" = test ]; then
  "${EVAL[@]}" rcheck r="$R" || prelude_stop UNRESOLVED test_r_refused_within_1_of_9
  case "$OUT" in /*) ;; *) prelude_stop UNRESOLVED test_out_must_be_an_absolute_path;; esac
  case "$OUT" in "$ROOT"/*) prelude_stop UNRESOLVED test_out_must_lie_outside_the_freeze_folder;; esac
  [ ${#STEPS[@]} -ge 1 ] && [ ${#STEPS[@]} -le 3 ] || prelude_stop UNRESOLVED test_m0_takes_1_to_3_steps
fi
[ -e "$OUT" ] && prelude_stop UNRESOLVED run_directory_already_exists
mkdir -p "$OUT/log" || prelude_stop UNRESOLVED cannot_create_run_directory
LOG="$OUT/log"
DRVSHA=$(sha256sum "$HERE/run_floor.sh" | cut -d' ' -f1)
say "START|mode=$MODE|r=$R|m0_steps=${STEPS[*]}|f=$FSPEC|g0=$G0|prediction_sha256=$P|driver_sha256=$DRVSHA|json=0"
for i in "${!TDST[@]}"; do
  say "TOOL|private_copy=${TDST[$i]#"$PRIV"/}|source=${TSRC[$i]#"$ROOT"/}|sha256=$(sha256sum "${TDST[$i]}" | cut -d' ' -f1)|pin=${TROW[$i]}|want=${TWANT[$i]}|json=0"
done
# ---- freeze commit (frozen run): the commit that carries the prediction record, checked by blob hash
if [ "$MODE" = r9 ]; then
  [ -n "$C" ] || C=$(git log -1 --format=%H -- "$PREDREL" 2>/dev/null)
  echo "$C" | grep -Eq '^[0-9a-f]{40}$' || prelude_stop UNRESOLVED freeze_commit_not_found
  PFX=$(git rev-parse --show-prefix 2>/dev/null)
  BL=$(git show "$C:$PFX$PREDREL" 2>/dev/null | sha256sum | cut -d' ' -f1)
  [ "$BL" = "$P" ] || prelude_stop FAIL prediction_record_differs_from_the_freeze_commit
  [ -z "$(git status --porcelain --untracked-files=no -- . 2>/dev/null)" ] || prelude_stop FAIL tracked_files_differ_from_the_commit
  say "NOTE|freeze_commit=$C|prediction_blob_sha256=$BL|json=0"
fi
# ---- toolchain (row 017) and the pin-free binary of row 016
RV=$(rustc +1.81 --version 2>&1); CV=$(cargo +1.81 --version 2>&1)
say "NOTE|rustc=$RV|cargo=$CV|json=0"
[ "$RV" = "$RUSTC_PIN" ] && [ "$CV" = "$CARGO_PIN" ] || prelude_stop FAIL toolchain_differs_from_row_017
if [ ! -f "$PINFREE" ]; then
  (cd work/design/rs && env -u FLOORCERT_FREEZE_COMMIT -u FLOORCERT_PREDICTION_SHA256 cargo +1.81 build --release --locked -j1) > "$LOG/build_pinfree.txt" 2>&1 \
    || prelude_stop UNRESOLVED pin_free_build_failed
fi
guard || integrity_stop
"${EVAL[@]}" pins root="$ROOT" pred="$PPRED" tag=1 > "$LOG/pincheck_1.txt" 2>&1 || { tail -1 "$LOG/pincheck_1.txt"; prelude_stop FAIL pin_check_1_mismatch_row_010; }
say "$(tail -1 "$LOG/pincheck_1.txt")"
if [ "$MODE" = r9 ]; then
  FB=work/run9/target/release/floorcert
  (cd work/design/rs && CARGO_TARGET_DIR="$ROOT/work/run9/target" FLOORCERT_FREEZE_COMMIT="$C" FLOORCERT_PREDICTION_SHA256="$P" cargo +1.81 build --release --locked -j1) > "$LOG/build_frozen.txt" 2>&1 || prelude_stop UNRESOLVED frozen_build_failed
  [ -f "$FB" ] || prelude_stop UNRESOLVED frozen_binary_absent
  guard || integrity_stop
  "${EVAL[@]}" pins root="$ROOT" pred="$PPRED" tag=2 > "$LOG/pincheck_2.txt" 2>&1 || { tail -1 "$LOG/pincheck_2.txt"; prelude_stop FAIL pin_check_2_mismatch_row_010; }
  say "$(tail -1 "$LOG/pincheck_2.txt")"
  FREEZE_ARGS=(--freeze-commit "$C" --prediction "$PREDREL" --prediction-sha256 "$P")
else
  FB="$PINFREE"; C=NONE; FREEZE_ARGS=()
fi
# ---- the binary: one private copy, and that copy is the program every writer command runs
XB="$PRIV/floorcert"
cp "$FB" "$XB" && chmod a-w "$XB" || prelude_stop UNRESOLVED cannot_copy_the_binary_into_the_private_directory
FBSHA=$(sha256sum "$XB" | cut -d' ' -f1)
[ "$MODE" = r9 ] || [ "$FBSHA" = "$(pinval 016)" ] || prelude_stop FAIL binary_copy_differs_from_row_016
GF+=("$FB" "$XB"); GW+=("$FBSHA" "$FBSHA")
guard || integrity_stop
say "TOOL|private_copy=floorcert|source=$FB|sha256=$FBSHA|pin=$([ "$MODE" = r9 ] && echo frozen_build_of_row_009 || echo 016)|want=$FBSHA|json=0"
say "NOTE|binary=$FB|binary_sha256=$FBSHA|executed_copy=PRIVATE_COPY/floorcert|private_directory=$PRIV|json=0"

run_cmd() { # kind m0 attempt limit killafter logfile argv... ; the command runs in a process group of its own
  local kind=$1 m=$2 att=$3 lim=$4 ka=$5 lf=$6 t0 t1 cpid pg n; shift 6
  guard || integrity_stop
  SEQ=$((SEQ+1)); t0=$(date +%s)
  setsid timeout -k "$ka" "$lim" "$@" > "$lf" 2>&1 &
  cpid=$!
  # setsid runs in place here (a background job of a script is never a group leader), so the new group id is $cpid
  pg=""; n=0
  while [ $n -lt 100 ]; do
    pg=$(ps -o pgid= -p "$cpid" 2>/dev/null | tr -d ' ')
    [ -z "$pg" ] || [ "$pg" = "$cpid" ] && break
    n=$((n+1)); sleep 0.01
  done
  wait "$cpid"; RC=$?
  t1=$(date +%s); TIMEDOUT=0
  if [ $RC -eq 124 ] || { [ $RC -eq 137 ] && [ $((t1-t0)) -ge "$lim" ]; }; then
    TIMEDOUT=1
    # the time limit ended this command: end what is left of the process group this launcher started, and only that group
    kill -KILL -- "-$cpid" 2>/dev/null
  fi
  say "INVOKE|seq=$SEQ|m0=$m|kind=$kind|attempt=$att|rc=$RC|limit_s=$lim|elapsed_s=$((t1-t0))|time_limit_hit=$TIMEDOUT|own_process_group=$([ "$pg" = "$cpid" ] && echo 1 || echo 0)|log=${lf#"$OUT"/}|log_sha256=$(sha256sum "$lf" | cut -d' ' -f1)|argv=$*|json=0"
}
classify() { # logfile -> CLS: refuse (a refusal line), timeout (the time limit), ok, crash (anything else, a verifier exception included)
  local pat='^REFUSE\||^VERDICT\|REFUSE|^GATE\|[^|]*\|FAIL|^GATE_REQUIRED\|REFUSE\|verifier sha256'
  if grep -Eq "$pat" "$1"; then CLS=refuse
  elif [ $TIMEDOUT -eq 1 ]; then CLS=timeout
  elif [ $RC -eq 0 ]; then CLS=ok
  else CLS=crash; fi
}
aside() { # kind m0 attempt : keep the remains of a failed attempt out of the run directory
  local d="$OUT/aside/m$2_$1_a$3"; mkdir -p "$d"
  if [ "$1" = rowhash ]; then [ -e "$OUT/RUN$2" ] && mv "$OUT/RUN$2" "$d/"
  else for x in "$OUT/RUN$2"/cert_*.txt; do [ -e "$x" ] && mv "$x" "$d/"; done; fi
  return 0
}
do_cmd() { # kind m0 idx logbase argv... ; one rerun after a crash while the run still has its rerun; none after a time limit
  local kind=$1 m=$2 idx=$3 lb=$4; shift 4
  local att=1 lf
  while :; do
    lf="$LOG/${lb}_a${att}.txt"
    if [ $att -eq 1 ] && has "$T_CRASH" "$idx:$kind"; then
      say "INJECTED|m0=$m|kind=$kind|what=crash_by_signal_in_place_of_the_first_attempt|json=0"
      run_cmd "$kind" "$m" $att "$LIMIT" "$KILLAFTER" "$lf" python3 -I -B "$PEAK" bash -c 'kill -SEGV $$'
    elif [ $att -eq 1 ] && [ "$kind" = gate ] && has "$T_VEXC" "$idx"; then
      say "INJECTED|m0=$m|kind=$kind|what=the_output_of_gate_required.sh_for_a_verifier_that_ended_with_an_exception_(exit_1,_no_verdict_line)_in_place_of_the_first_attempt|json=0"
      run_cmd "$kind" "$m" $att "$LIMIT" "$KILLAFTER" "$lf" bash -c 'echo "Traceback (most recent call last):"; echo "GATE_REQUIRED|REFUSE|cert=INJECTED|cert_sha256=INJECTED|verifier_exit=1|header_rowhash=|verifier_rowhash=|"; exit 1'
    elif has "$T_HANG" "$idx:$kind"; then
      say "INJECTED|m0=$m|kind=$kind|what=sleep_20_under_a_2_second_limit_in_place_of_the_command|json=0"
      run_cmd "$kind" "$m" $att 2 "$KILLAFTER" "$lf" sleep 20
    elif has "$T_HARD" "$idx:$kind"; then
      say "INJECTED|m0=$m|kind=$kind|what=a_command_that_ignores_TERM_under_a_2_second_limit_with_KILL_3_seconds_later|json=0"
      run_cmd "$kind" "$m" $att 2 3 "$lf" bash -c 'trap "" TERM; sleep 20'
    else
      run_cmd "$kind" "$m" $att "$LIMIT" "$KILLAFTER" "$lf" "$@"
    fi
    classify "$lf"
    if [ "$CLS" = crash ] && [ $RERUNS -gt 0 ]; then
      RERUNS=0; say "NOTE|rerun_once_with_identical_arguments=row_008|m0=$m|kind=$kind|first_rc=$RC|json=0"
      [ "$kind" = gate ] || aside "$kind" "$m" $att
      att=2; continue
    fi
    break
  done
  cp "$lf" "$LOG/${lb}.txt"
}
stub() { echo "STEP|m0=$1|status=$2|accepted=0|certificates=0|resource_limit=HELD|bad=$3|json=0" > "$LOG/m$1_step.hbp"; say "STEP|m0=$1|status=$2|accepted=0|bad=$3|json=0"; }
opfail() { # m0 why ; a crash or a time limit: operational only while no completed process of the step broke the memory limit (row 122)
  guard || integrity_stop
  "${EVAL[@]}" opfail out="$OUT" m0="$1" why="$2" mode="$MODE" "${LIMARG[@]}" | tee -a "$LOG/run.log"
  [ -f "$LOG/m$1_step.hbp" ] || stub "$1" FAIL evaluator_wrote_no_step_file
}

step() { # idx m0 ; return 0 when a step file exists, 1 when the run stops without one
  local idx=$1 m=$2 RUN="$OUT/RUN$2" x b
  [ -e "$RUN" ] && { STOP=FAIL_run_directory_exists_before_rowhash_row_001; return 1; }
  say "NOTE|before_m0=$m|binary_sha256=$(sha256sum "$XB" | cut -d' ' -f1)|json=0"
  do_cmd rowhash "$m" "$idx" "m${m}_rowhash" python3 -I -B "$PEAK" "$XB" rowhash --m0 "$m" --threads 2 --dir "$RUN"
  case $CLS in
    refuse) stub "$m" FAIL rowhash_command_refused; return 0;;
    crash|timeout) aside rowhash "$m" final; opfail "$m" "rowhash_command_$CLS"; return 0;;
  esac
  if [ "$idx" -eq 3 ]; then # row 007 prerequisite
    sha256sum "$RUN/core_keys_m$m.bin" > "$LOG/m${m}_keysha.txt" 2>&1
    do_cmd rowsonly "$m" "$idx" "m${m}_rowsonly" python3 -I -B "$VERIFIER" --rows-only "$RUN/core_keys_m$m.bin" "$m"
    [ "$CLS" = ok ] || { STOP="PREREQUISITE_NOT_MET_row_007_verifier_$CLS"; return 1; }
    guard || integrity_stop
    x=$("${EVAL[@]}" prereq out="$OUT" pred="$PPRED" m0="$m" mode="$MODE" "${LIMARG[@]}"); b=$?; say "$x|json=0"
    [ $b -eq 0 ] || { STOP=PREREQUISITE_NOT_MET_row_007; return 1; }
  fi
  ls -1 "$RUN" > "$LOG/m${m}_dir_after_rowhash.txt"
  local extra=()
  [ "$T_PLANT" != "" ] && [ "${T_PLANT%%:*}" = "$idx" ] && { extra=(--plant all --ub "${T_PLANT#*:}"); say "INJECTED|m0=$m|kind=cert|what=plant_all_files_written_beside_the_honest_certificate|json=0"; }
  do_cmd cert "$m" "$idx" "m${m}_cert" python3 -I -B "$PEAK" "$XB" cert --m0 "$m" --r "$R" --f "$FSPEC" --write-cert --threads 2 --dir "$RUN" "${FREEZE_ARGS[@]}" "${extra[@]}"
  case $CLS in
    refuse) stub "$m" FAIL cert_command_refused; return 0;;
    crash|timeout) aside cert "$m" final; opfail "$m" "cert_command_$CLS"; return 0;;
  esac
  for x in "$RUN"/cert_*.txt; do
    [ -e "$x" ] || continue
    b=$(basename "$x")
    do_cmd gate "$m" "$idx" "m${m}_gate_$b" bash "$GATE" "$x" "${FREEZE_ARGS[@]}"
    # a verifier that ended without a verdict (exception, kill) or ran into the time limit: operational, rows 006 (b) and 007 (b)
    case $CLS in crash|timeout) aside gate "$m" final; opfail "$m" "verifier_$CLS"; return 0;; esac
  done
  guard || integrity_stop
  "${EVAL[@]}" step root="$ROOT" tools="$PRIV" pred="$PPRED" out="$OUT" m0="$m" r="$R" fspec="$FSPEC" mode="$MODE" census="$CENSUS" commit="$C" psha="$P" fbsha="$FBSHA" "${LIMARG[@]}" | tee -a "$LOG/run.log"
  [ -f "$LOG/m${m}_step.hbp" ] || { STOP=FAIL_evaluator_wrote_no_step_file_m0_$m; return 1; }
  return 0
}

idx=0
for m in "${STEPS[@]}"; do
  idx=$((idx+1))
  step "$idx" "$m" || break
  RUNSTEPS="${RUNSTEPS:+$RUNSTEPS,}$m"
  guard || integrity_stop
  D=$("${EVAL[@]}" decide out="$OUT" steps="$RUNSTEPS" g0="$G0" allowed="${#STEPS[@]}") || { STOP=FAIL_evaluator_decide; break; }
  say "$(echo "$D" | grep '^DECISION|')"
  [ "$(echo "$D" | grep '^NEXT|')" = "NEXT|ADVANCE" ] || break
done
# ---- closing: every pinned file and every private copy once more here, and every PIN row and the private copies
# again inside the evaluator before it prints
guard || integrity_stop
for i in "${!TDST[@]}"; do
  say "TOOL_CLOSING|private_copy=${TDST[$i]#"$PRIV"/}|sha256=$(sha256sum "${TDST[$i]}" | cut -d' ' -f1)|want=${TWANT[$i]}|json=0"
done
"${EVAL[@]}" final root="$ROOT" tools="$PRIV" out="$OUT" pred="$PPRED" steps="$RUNSTEPS" g0="$G0" allowed="${#STEPS[@]}" mode="$MODE" r="$R" stop="$STOP" \
  commit="$C" fbsha="$FBSHA" drvsha="$DRVSHA" receipt="$OUT/FLOOR-RUN-RECEIPT.hbp"
exit $?
}
