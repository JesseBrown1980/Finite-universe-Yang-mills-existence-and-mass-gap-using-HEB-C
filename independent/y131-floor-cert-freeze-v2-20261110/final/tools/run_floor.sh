#!/bin/bash
# run_floor.sh -- single launcher of the frozen floor-certificate run (version 2 freeze).
#   default:  bash final/tools/run_floor.sh [--freeze-commit C]
#             r = 9, m0 = 11, then 12 and 13 only under rows 006 and 007 of the prediction record.
#   rehearsal: bash final/tools/run_floor.sh --test-r R --test-m0 a,b,c --test-f WORDS --test-g0 N/D --test-out DIR
#             [--test-plant IDX:UB] [--test-crash IDX:KIND] [--test-hang IDX:KIND] [--test-census]
#             R must lie more than 1 away from 9; the binary's own r policy stays in force.
# Every path is derived from this file's location. One heavy process at a time. No retry beyond row 008:
# one rerun with identical arguments after a crash, for the whole run, both attempts logged.
# Exit: 0 PASS, 1 FAIL, 2 UNRESOLVED. The last line printed is FLOOR_RUN|result=...
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT" || exit 2
[ -d "$HOME/.cargo/bin" ] && export PATH="$HOME/.cargo/bin:$PATH"
PREDREL=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
PEAK=work/design/peak_rss.py
GATE=work/design/gate_required.sh
VERIFIER=work/design/py/cert_gate.py
PINFREE=work/design/rs/target/release/floorcert
LIMIT=21600
Y137_COMMIT=5e70e9dc02d6ed32fe9a94d03a2c3a77587ff9af
Y137_PATH=independent/y137-amplitude-freeze-20261109/PREDICT-S3-3X4-R9-WILSON-FESHBACH-AMPLITUDE-20261109.hbp
RUSTC_PIN="rustc 1.81.0 (eeb90cda1 2024-09-04)"
CARGO_PIN="cargo 1.81.0 (2dbb1af80 2024-08-20)"
MODE=r9; R=9; STEPS=(11 12 13); FSPEC='1;8,7,6,5,4;6,5,4,3'; G0=94070673/1000000; OUT=work/run9
C=""; T_R=""; T_PLANT=""; T_CRASH=""; T_HANG=""; CENSUS=0; T_ANY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --freeze-commit) C="$2"; shift 2;;
    --test-r) T_R="$2"; shift 2;;
    --test-m0) IFS=, read -r -a STEPS <<< "$2"; T_ANY=1; shift 2;;
    --test-f) FSPEC="$2"; T_ANY=1; shift 2;;
    --test-g0) G0="$2"; T_ANY=1; shift 2;;
    --test-out) OUT="$2"; T_ANY=1; shift 2;;
    --test-plant) T_PLANT="$2"; T_ANY=1; shift 2;;
    --test-crash) T_CRASH="$2"; T_ANY=1; shift 2;;
    --test-hang) T_HANG="$2"; T_ANY=1; shift 2;;
    --test-census) CENSUS=1; T_ANY=1; shift;;
    *) echo "FLOOR_RUN|result=UNRESOLVED|stage=arguments|reason=unknown_argument|steps_run=none|accepted_certificates=0|json=0"; exit 2;;
  esac
done
LOG=""; SEQ=0; RERUNS=1; STOP=DECIDED; RUNSTEPS=""; FBSHA=NONE; P=NONE
EVAL=(python3 -I -B "$HERE/floor_eval.py")
say() { echo "$1"; [ -n "$LOG" ] && echo "$1" >> "$LOG/run.log"; return 0; }
prelude_stop() { # result reason
  say "FLOOR_RUN|result=$1|stage=prelude|reason=$2|r=$R|steps_run=none|accepted_certificates=0|certificate_commands_run=0|json=0"
  [ "$1" = FAIL ] && exit 1; exit 2
}
if [ -n "$T_R" ]; then
  MODE=test; R="$T_R"
  "${EVAL[@]}" rcheck r="$R" || prelude_stop UNRESOLVED test_r_refused_within_1_of_9
  case "$OUT" in /*) ;; *) prelude_stop UNRESOLVED test_out_must_be_an_absolute_path;; esac
  case "$OUT" in "$ROOT"/*) prelude_stop UNRESOLVED test_out_must_lie_outside_the_freeze_folder;; esac
  [ ${#STEPS[@]} -ge 1 ] && [ ${#STEPS[@]} -le 3 ] || prelude_stop UNRESOLVED test_m0_takes_1_to_3_steps
elif [ $T_ANY -ne 0 ]; then
  prelude_stop UNRESOLVED test_options_need_test_r
fi
[ -e "$OUT" ] && prelude_stop UNRESOLVED run_directory_already_exists
mkdir -p "$OUT/log" || prelude_stop UNRESOLVED cannot_create_run_directory
LOG="$OUT/log"
P=$(sha256sum "$PREDREL" | cut -d' ' -f1)
DRVSHA=$(sha256sum "$HERE/run_floor.sh" | cut -d' ' -f1)
say "START|mode=$MODE|r=$R|m0_steps=${STEPS[*]}|f=$FSPEC|g0=$G0|prediction_sha256=$P|driver_sha256=$DRVSHA|json=0"
# ---- freeze commit (default mode): the commit that carries the prediction record, checked by blob hash
if [ "$MODE" = r9 ]; then
  [ -n "$C" ] || C=$(git log -1 --format=%H -- "$PREDREL" 2>/dev/null)
  echo "$C" | grep -Eq '^[0-9a-f]{40}$' || prelude_stop UNRESOLVED freeze_commit_not_found
  PFX=$(git rev-parse --show-prefix 2>/dev/null)
  BL=$(git show "$C:$PFX$PREDREL" 2>/dev/null | sha256sum | cut -d' ' -f1)
  [ "$BL" = "$P" ] || prelude_stop FAIL prediction_record_differs_from_the_freeze_commit
  [ -z "$(git status --porcelain --untracked-files=no -- . 2>/dev/null)" ] || prelude_stop FAIL tracked_files_differ_from_the_commit
  say "NOTE|freeze_commit=$C|prediction_blob_sha256=$BL|json=0"
fi
# ---- row 034 lives outside this folder: read it from its own commit when the literal path is absent
ALT="$LOG/row034_from_git.hbp"
if [ ! -f "../ym137/final/$(basename "$Y137_PATH")" ]; then
  git show "$Y137_COMMIT:$Y137_PATH" > "$ALT" 2>/dev/null || rm -f "$ALT"
fi
# ---- toolchain (row 017) and the pin-free binary of row 016
RV=$(rustc +1.81 --version 2>&1); CV=$(cargo +1.81 --version 2>&1)
say "NOTE|rustc=$RV|cargo=$CV|json=0"
[ "$RV" = "$RUSTC_PIN" ] && [ "$CV" = "$CARGO_PIN" ] || prelude_stop FAIL toolchain_differs_from_row_017
if [ ! -f "$PINFREE" ]; then
  (cd work/design/rs && env -u FLOORCERT_FREEZE_COMMIT -u FLOORCERT_PREDICTION_SHA256 cargo +1.81 build --release --locked -j1) > "$LOG/build_pinfree.txt" 2>&1 \
    || prelude_stop UNRESOLVED pin_free_build_failed
fi
"${EVAL[@]}" pins root="$ROOT" pred="$PREDREL" alt034="$ALT" tag=1 > "$LOG/pincheck_1.txt" 2>&1 || { tail -1 "$LOG/pincheck_1.txt"; prelude_stop FAIL pin_check_1_mismatch_row_010; }
say "$(tail -1 "$LOG/pincheck_1.txt")"
if [ "$MODE" = r9 ]; then
  FB=work/run9/target/release/floorcert
  (cd work/design/rs && CARGO_TARGET_DIR="$ROOT/work/run9/target" FLOORCERT_FREEZE_COMMIT="$C" FLOORCERT_PREDICTION_SHA256="$P" cargo +1.81 build --release --locked -j1) > "$LOG/build_frozen.txt" 2>&1 || prelude_stop UNRESOLVED frozen_build_failed
  [ -f "$FB" ] || prelude_stop UNRESOLVED frozen_binary_absent
  "${EVAL[@]}" pins root="$ROOT" pred="$PREDREL" alt034="$ALT" tag=2 > "$LOG/pincheck_2.txt" 2>&1 || { tail -1 "$LOG/pincheck_2.txt"; prelude_stop FAIL pin_check_2_mismatch_row_010; }
  say "$(tail -1 "$LOG/pincheck_2.txt")"
  FREEZE_ARGS=(--freeze-commit "$C" --prediction "$PREDREL" --prediction-sha256 "$P")
else
  FB="$PINFREE"; C=NONE; FREEZE_ARGS=()
fi
FBSHA=$(sha256sum "$FB" | cut -d' ' -f1)
say "NOTE|binary=$FB|binary_sha256=$FBSHA|json=0"

run_cmd() { # kind m0 attempt limit logfile argv...
  local kind=$1 m=$2 att=$3 lim=$4 lf=$5; shift 5
  SEQ=$((SEQ+1))
  timeout -k 30 "$lim" "$@" > "$lf" 2>&1; RC=$?
  [ $RC -eq 124 ] && pkill -KILL -x floorcert
  say "INVOKE|seq=$SEQ|m0=$m|kind=$kind|attempt=$att|rc=$RC|limit_s=$lim|log=${lf#"$OUT"/}|log_sha256=$(sha256sum "$lf" | cut -d' ' -f1)|argv=$*|json=0"
}
classify() { # logfile -> CLS in ok refuse timeout crash
  local pat='^REFUSE\||^VERDICT\|REFUSE|^GATE\|[^|]*\|FAIL|^GATE_REQUIRED\|REFUSE\|verifier sha256|^GATE_REQUIRED\|REFUSE\|.*\|verifier_exit=1\|'
  if grep -Eq "$pat" "$1"; then CLS=refuse
  elif [ $RC -eq 0 ]; then CLS=ok
  elif [ $RC -eq 124 ]; then CLS=timeout
  else CLS=crash; fi
}
aside() { # kind m0 attempt : keep the remains of a failed attempt out of the run directory
  local d="$OUT/aside/m$2_$1_a$3"; mkdir -p "$d"
  if [ "$1" = rowhash ]; then [ -e "$OUT/RUN$2" ] && mv "$OUT/RUN$2" "$d/"
  elif [ "$1" = cert ]; then for x in "$OUT/RUN$2"/cert_*.txt; do [ -e "$x" ] && mv "$x" "$d/"; done; fi
  return 0
}
do_cmd() { # kind m0 idx logbase argv... ; one rerun after a crash while the run still has its rerun
  local kind=$1 m=$2 idx=$3 lb=$4; shift 4
  local att=1 lf
  while :; do
    lf="$LOG/${lb}_a${att}.txt"
    if [ $att -eq 1 ] && [ "$T_CRASH" = "$idx:$kind" ]; then
      say "INJECTED|m0=$m|kind=$kind|what=crash_by_signal_in_place_of_the_first_attempt|json=0"
      run_cmd "$kind" "$m" $att "$LIMIT" "$lf" python3 -I -B "$PEAK" bash -c 'kill -SEGV $$'
    elif [ "$T_HANG" = "$idx:$kind" ]; then
      say "INJECTED|m0=$m|kind=$kind|what=sleep_20_under_a_2_second_limit_in_place_of_the_command|json=0"
      run_cmd "$kind" "$m" $att 2 "$lf" sleep 20
    else
      run_cmd "$kind" "$m" $att "$LIMIT" "$lf" "$@"
    fi
    classify "$lf"
    if [ "$CLS" = crash ] && [ $RERUNS -gt 0 ]; then
      RERUNS=0; say "NOTE|rerun_once_with_identical_arguments=row_008|m0=$m|kind=$kind|first_rc=$RC|json=0"
      aside "$kind" "$m" $att; att=2; continue
    fi
    break
  done
  cp "$lf" "$LOG/${lb}.txt"
}
stub() { echo "STEP|m0=$1|status=$2|accepted=0|certificates=0|bad=$3|json=0" > "$LOG/m$1_step.hbp"; say "STEP|m0=$1|status=$2|accepted=0|bad=$3|json=0"; }

step() { # idx m0 ; return 0 when a step file exists, 1 when the run stops without one
  local idx=$1 m=$2 RUN="$OUT/RUN$2" h x b
  [ -e "$RUN" ] && { STOP=FAIL_run_directory_exists_before_rowhash_row_001; return 1; }
  h=$(sha256sum "$FB" | cut -d' ' -f1); say "NOTE|before_m0=$m|binary_sha256=$h|json=0"
  [ "$h" = "$FBSHA" ] || { STOP=FAIL_binary_changed_row_018; return 1; }
  do_cmd rowhash "$m" "$idx" "m${m}_rowhash" python3 -I -B "$PEAK" "$FB" rowhash --m0 "$m" --threads 2 --dir "$RUN"
  case $CLS in
    refuse) stub "$m" FAIL rowhash_command_refused; return 0;;
    crash|timeout) aside rowhash "$m" final; stub "$m" OPFAIL "rowhash_command_$CLS"; return 0;;
  esac
  if [ "$idx" -eq 3 ]; then # row 007 prerequisite
    sha256sum "$RUN/core_keys_m$m.bin" > "$LOG/m${m}_keysha.txt" 2>&1
    do_cmd rowsonly "$m" "$idx" "m${m}_rowsonly" python3 -I -B "$VERIFIER" --rows-only "$RUN/core_keys_m$m.bin" "$m"
    [ "$CLS" = ok ] || { STOP="PREREQUISITE_NOT_MET_row_007_verifier_$CLS"; return 1; }
    x=$("${EVAL[@]}" prereq out="$OUT" pred="$PREDREL" m0="$m"); b=$?; say "$x|json=0"
    [ $b -eq 0 ] || { STOP=PREREQUISITE_NOT_MET_row_007; return 1; }
  fi
  ls -1 "$RUN" > "$LOG/m${m}_dir_after_rowhash.txt"
  local extra=()
  [ "$T_PLANT" != "" ] && [ "${T_PLANT%%:*}" = "$idx" ] && { extra=(--plant all --ub "${T_PLANT#*:}"); say "INJECTED|m0=$m|kind=cert|what=plant_all_files_written_beside_the_honest_certificate|json=0"; }
  do_cmd cert "$m" "$idx" "m${m}_cert" python3 -I -B "$PEAK" "$FB" cert --m0 "$m" --r "$R" --f "$FSPEC" --write-cert --threads 2 --dir "$RUN" "${FREEZE_ARGS[@]}" "${extra[@]}"
  case $CLS in
    refuse) stub "$m" FAIL cert_command_refused; return 0;;
    crash|timeout) aside cert "$m" final; stub "$m" OPFAIL "cert_command_$CLS"; return 0;;
  esac
  for x in "$RUN"/cert_*.txt; do
    [ -e "$x" ] || continue
    b=$(basename "$x")
    do_cmd gate "$m" "$idx" "m${m}_gate_$b" bash "$GATE" "$x" "${FREEZE_ARGS[@]}"
    case $CLS in crash|timeout) STOP="GATE_OPERATIONAL_FAILURE_m0_${m}_$CLS"; return 1;; esac
  done
  "${EVAL[@]}" step pred="$PREDREL" out="$OUT" m0="$m" r="$R" fspec="$FSPEC" mode="$MODE" census="$CENSUS" commit="$C" psha="$P" fbsha="$FBSHA" | tee -a "$LOG/run.log"
  [ -f "$LOG/m${m}_step.hbp" ] || { STOP=EVALUATOR_FAILED_m0_$m; return 1; }
  return 0
}

idx=0
for m in "${STEPS[@]}"; do
  idx=$((idx+1))
  step "$idx" "$m" || break
  RUNSTEPS="${RUNSTEPS:+$RUNSTEPS,}$m"
  D=$("${EVAL[@]}" decide out="$OUT" steps="$RUNSTEPS" g0="$G0" allowed="${#STEPS[@]}") || { STOP=EVALUATOR_FAILED_decide; break; }
  say "$(echo "$D" | grep '^DECISION|')"
  [ "$(echo "$D" | grep '^NEXT|')" = "NEXT|ADVANCE" ] || break
done
"${EVAL[@]}" final out="$OUT" pred="$PREDREL" steps="$RUNSTEPS" g0="$G0" allowed="${#STEPS[@]}" mode="$MODE" r="$R" stop="$STOP" \
  commit="$C" fbsha="$FBSHA" drvsha="$DRVSHA" receipt="$OUT/FLOOR-RUN-RECEIPT.hbp"
exit $?
