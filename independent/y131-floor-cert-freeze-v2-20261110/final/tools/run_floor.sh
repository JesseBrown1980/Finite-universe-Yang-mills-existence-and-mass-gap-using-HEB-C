#!/bin/bash
# run_floor.sh -- single launcher of the frozen floor-certificate run (version 2 freeze, fifth correction round).
#   frozen run: bash final/tools/run_floor.sh --launch-r9 [--freeze-commit C]
#               r = 9, m0 = 11, then 12 and 13 only under rows 006 and 007 of the prediction record.
#               The token --launch-r9 is the only way into this mode; no other argument set reaches r = 9.
#   rehearsal:  bash final/tools/run_floor.sh --test-r R --test-m0 a,b,c --test-f WORDS --test-g0 N/D --test-out DIR
#               [--test-plant IDX:UB] [--test-crash LIST] [--test-hang LIST] [--test-hang-hard LIST]
#               [--test-vexc IDX] [--test-census] [--test-limit-kb N] [--test-git-check]
#               [--test-frozen-build [--freeze-commit C]]
#               --test-frozen-build runs the freeze-commit lookup, the frozen build with the two compiled pins and
#               pin check 2 exactly as the frozen run does, and then runs the rehearsal with that binary at R.
#               (LIST is IDX:KIND[,IDX:KIND...]; KIND is rowhash, cert, rowsonly or gate)
#               R must lie more than 1 away from 9; the binary's own r policy stays in force.
# TWO STAGES. Stage 1 (the file as called) reads this file once into memory and replaces itself by
#   /usr/bin/env -i PATH=/usr/bin:/bin LANG=C ... /usr/bin/unshare -m --propagation private
#   /usr/bin/bash --noprofile --norc -c "<the bytes read>" run_floor.sh <arguments>
# so stage 2 runs the bytes that were read, with an empty environment, a fixed PATH of system directories and a
# mount namespace of its own. Stage 2 hashes its own text (BASH_EXECUTION_STRING) against row 114.
# NAMESPACE (row 132). Stage 2 starts no work unless the mount namespace of its own process differs from the mount
# namespace of its parent process and from that of process 1 and holds no shared or slave mount; entered directly,
# without stage 1, it stops with NOT_STARTED (exit 4) before it mounts or writes anything. After the two tmpfs
# mounts it reads the mount tables: both mounts must be listed for this process and absent for the parent process
# and for process 1, or the run stops with NOT_STARTED. Only then does the run log say that the namespace is private.
# EXCLUSIVE (row 139). No other process may sit in that mount namespace: at the start of stage 2, after the mounts and
# at the close the launcher lists every process whose mount namespace is its own; one that is neither this shell nor
# a child of it stops the run (NOT_STARTED before the first command, CERTIFICATE=FAIL at the close). An entry made
# through a namespace that another process holds (nsenter) is refused by this check.
# REFERENCES (row 144). At the same three points the launcher reads every mount table it can read and the open
# descriptors of every process: a bind mount or a descriptor that names this mount namespace, or one that names a
# mount namespace with no member process, stops the run. An entry through a namespace that a bound file keeps alive
# with no process in it is refused by this check.
# BUILD (row 139). Cargo runs with CARGO_HOME set to an empty directory on the launcher's tmpfs; a cargo
# configuration file in the Rust folder or in any directory above it, and any untracked file in the Rust folder
# outside target/, stop the run. With a frozen build the tracked files of the whole repository must be unchanged.
# A Cargo.toml that names a workspace in any directory above the Rust folder stops the run (row 144). With a frozen
# build the checkout must be at the freeze commit (HEAD equal to C) and the index may mark no file assume-unchanged
# or skip-worktree.
# PUBLISH. Before its final line the launcher prints PUBLISH|receipt_sha256=...; that value is to be made public at
# once, and the checker of row 131 requires it for the r9 receipt (row 138).
# Stage 1 first refuses a caller environment that carries BASH_ENV, ENV, an LD_ name, a PYTHON name or an exported
# shell function (NOT_STARTED, exit 4); stage 2 stops unless its environment holds the whitelisted names only.
# TOOLS. python3, bash, sha256sum, timeout, setsid and git are resolved once under the fixed PATH to absolute paths,
# logged with their SHA-256 (TOOLPATH lines) and called by those paths; cargo and rustc 1.81 are the toolchain
# binaries under HOME (HOME from the password database), called by absolute path and logged the same way.
# HASHED BYTES. The prediction record, gate_required.sh, cert_gate.py, indep_verify.py, peak_rss.py and the
# evaluator are each read once into memory and hashed there against the frozen SHA-256 values. peak_rss.py and the
# evaluator run from memory (python3 -I -B -c). gate_required.sh, cert_gate.py, indep_verify.py, the record and the
# binary are written from those bytes into a tmpfs mounted at <run directory>/tmp inside the private mount namespace
# (TMPDIR; the tools sit in a second tmpfs under it, read-only once written; a process outside the namespace has
# neither in its own mount table; root reads them through /proc/PID/root, row 144); the tmpfs files and the files in the tree are hashed
# before and after every command and at the close. A certificate counts only with a logged verifier invocation that
# exited 0 with the tools still at their hashes after the call (row 122, row 124).
# A completed measured process at or over 2097152 kB gives CERTIFICATE=FAIL, RESOURCE_LIMIT_EXCEEDED, and no fallback;
# this includes the rowhash and the rows-only verifier of the row 007 prerequisite, checked before the prerequisite
# outcome is read (row 123).
# One heavy process at a time. No retry beyond row 008: one rerun with identical arguments after a crash, for the
# whole run, both attempts logged; a time limit gets none.
# The last line printed is FLOOR_RUN|CERTIFICATE=PASS or FAIL|PREDICTION=CONFIRMED or FALSIFIED or UNRESOLVED|
# DECISION=ABOVE or BELOW or UNRESOLVED|GAMMA=|UPPER_BOUND=|...|HASHES= ; this launcher prints it from the output of
# the evaluator it ran from memory, and derives the exit code from that line.
# Exit: 0 CERTIFICATE=PASS and PREDICTION=CONFIRMED; 3 CERTIFICATE=PASS and PREDICTION=FALSIFIED;
#       2 CERTIFICATE=PASS and PREDICTION=UNRESOLVED; 1 CERTIFICATE=FAIL after the run started (every reason);
#       4 CERTIFICATE=FAIL with certificate_reason=NOT_STARTED (refused arguments or a refused prelude).
# ACCEPTANCE (row 125): a PASS line of this launcher is accepted only after a second, independent environment has
# run final/tools/recheck_floor.py (row 131) on the receipt: it runs gate_required.sh on every certificate of the
# RECHECK rows, takes the upper bound from its own verifier output alone and must reproduce the decision (row 133).
set -u
{
NOBOUND="PREDICTION=UNRESOLVED|DECISION=UNRESOLVED|GAMMA=NONE|UPPER_BOUND=NONE"
early_stop() { # stage reason ; nothing has run
  echo "FLOOR_RUN|CERTIFICATE=FAIL|$NOBOUND|certificate_reason=NOT_STARTED|stage=$1|reason=$2|steps_run=none|accepted_certificates=0|certificate_commands_run=0|HASHES=NONE|json=0"
  exit 4
}
if [ "${FLOOR_STAGE:-}" != 2 ] || [ -z "${BASH_EXECUTION_STRING:-}" ]; then
  # ---- stage 1: read this file once, then run exactly those bytes in an empty environment and a private mount namespace
  # a caller environment that carries a shell start file, a loader setting, a python setting or an exported function is refused
  for v in $(compgen -e); do
    case "$v" in BASH_ENV|ENV|LD_*|PYTHON*|BASHOPTS|SHELLOPTS|PS4|IFS|POSIXLY_CORRECT|BASH_COMPAT|BASH_XTRACEFD|BASH_LOADABLES_PATH|EXECIGNORE|GLOBIGNORE|CDPATH) early_stop entry "caller_environment_sets_$v";; esac
  done
  [ "$(declare -F)" = "declare -f early_stop" ] || early_stop entry caller_environment_carries_shell_functions
  [ -n "${BASH_SOURCE[0]:-}" ] || early_stop entry launcher_file_path_unknown
  SELF=$(/usr/bin/realpath -e -- "${BASH_SOURCE[0]}" 2>/dev/null) || early_stop entry launcher_file_path_unknown
  SRC=$(/usr/bin/cat -- "$SELF") || early_stop entry cannot_read_the_launcher
  SROOT=$(/usr/bin/realpath -e -- "${SELF%/*}/../.." 2>/dev/null) || early_stop entry freeze_folder_not_found
  /usr/bin/env -i PATH=/usr/bin:/bin /usr/bin/unshare -m --propagation private /usr/bin/true 2>/dev/null \
    || early_stop entry cannot_create_a_private_mount_namespace
  exec /usr/bin/env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2 FLOOR_ROOT="$SROOT" \
    /usr/bin/unshare -m --propagation private /usr/bin/bash --noprofile --norc -c "$SRC" run_floor.sh "$@"
  early_stop entry cannot_start_the_second_stage
fi
# ---- stage 2: the environment holds the names set by stage 1 and by bash itself, and nothing else
for v in $(compgen -e); do
  case "$v" in PATH|LANG|FLOOR_STAGE|FLOOR_ROOT|PWD|OLDPWD|SHLVL|_) ;; *) early_stop environment "environment_carries_$v";; esac
done
[ "$PATH" = /usr/bin:/bin ] && [ "$LANG" = C ] || early_stop environment path_or_lang_differs_from_the_fixed_values
# ---- the mount namespace (row 132): this process must sit in a mount namespace other than that of its parent
# process and of process 1, with no shared or slave mount in it; a direct entry into stage 2 stops here
NS_SELF=$(/usr/bin/readlink /proc/self/ns/mnt 2>/dev/null) || NS_SELF=""
NS_PARENT=$(/usr/bin/readlink "/proc/$PPID/ns/mnt" 2>/dev/null) || NS_PARENT=""
NS_INIT=$(/usr/bin/readlink /proc/1/ns/mnt 2>/dev/null) || NS_INIT=""
for v in "$NS_SELF" "$NS_PARENT" "$NS_INIT"; do
  case "$v" in mnt:\[[0-9]*\]) ;; *) early_stop namespace a_mount_namespace_id_cannot_be_read;; esac
done
[ "$NS_SELF" != "$NS_PARENT" ] && [ "$NS_SELF" != "$NS_INIT" ] || early_stop namespace second_stage_entered_outside_a_private_mount_namespace
/usr/bin/grep -Eq ' (shared|master|propagate_from):[0-9]+ ' /proc/self/mountinfo; [ $? -eq 1 ] || early_stop namespace mount_namespace_holds_a_shared_or_slave_mount
ns_others() { # the pids, other than this shell and its own children, whose mount namespace is this one (row 139)
  local p q
  for p in /proc/[0-9]*; do
    p=${p#/proc/}
    [ "$p" = "$$" ] && continue
    [ "$(/usr/bin/readlink "/proc/$p/ns/mnt" 2>/dev/null)" = "$NS_SELF" ] || continue
    q=$(/usr/bin/sed -n 's/^PPid:[[:space:]]*//p' "/proc/$p/status" 2>/dev/null)
    [ "$q" = "$$" ] && continue
    echo "$p"
  done
}
[ -z "$(ns_others)" ] || early_stop namespace mount_namespace_is_held_by_another_process
ns_refs() { # mount namespace references that are no member process (row 144): nsfs bind mounts of every readable mount
  # table and open descriptors of every process; printed when one names this namespace or a namespace without a member
  local m="" x
  for x in /proc/[0-9]*/ns/mnt; do m="$m $(/usr/bin/readlink "$x" 2>/dev/null) "; done
  { /usr/bin/cat /proc/[0-9]*/mountinfo 2>/dev/null | /usr/bin/sed -n 's/^[0-9]* [0-9]* [0-9:]* \(mnt:\[[0-9]*\]\) .* - nsfs .*$/\1/p'
    /usr/bin/find /proc/[0-9]*/fd -maxdepth 1 -lname 'mnt:*' -printf '%l\n' 2>/dev/null
  } | while read -r x; do
    if [ "$x" = "$NS_SELF" ]; then echo "$x"; else case "$m" in *" $x "*) ;; *) echo "$x";; esac; fi
  done
}
[ -z "$(ns_refs)" ] || early_stop namespace mount_namespace_reference_outside_a_member_process
unset BASH_ENV ENV CDPATH GLOBIGNORE
ROOT="$FLOOR_ROOT"; HERE="$ROOT/final/tools"
cd "$ROOT" || early_stop environment cannot_enter_the_freeze_folder
HOME=$(getent passwd "$(id -u)" | cut -d: -f6); export HOME
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
MODE=none; R=9; STEPS=(11 12 13); FSPEC='1;8,7,6,5,4;6,5,4,3'; G0=94070673/1000000; OUT="$ROOT/work/run9"
C=""; T_R=""; T_PLANT=""; T_CRASH=""; T_HANG=""; T_HARD=""; T_VEXC=""; T_LIM=""; CENSUS=0; T_ANY=0; LAUNCH=0; T_GIT=0; T_FB=0
arg_stop() { early_stop arguments "$1"; }
while [ $# -gt 0 ]; do
  case "$1" in
    --launch-r9) LAUNCH=1; shift; continue;;
    --test-census) CENSUS=1; T_ANY=1; shift; continue;;
    --test-git-check) T_GIT=1; T_ANY=1; shift; continue;;
    --test-frozen-build) T_FB=1; T_ANY=1; shift; continue;;
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
  [ -z "$C" ] || [ $T_FB -eq 1 ] || arg_stop freeze_commit_belongs_to_launch_r9_or_test_frozen_build
  MODE=test; R="$T_R"
elif [ $T_ANY -ne 0 ]; then
  arg_stop test_options_need_test_r
else
  arg_stop no_mode_given_use_launch_r9_or_test_r
fi
LIMARG=(); [ -n "$T_LIM" ] && LIMARG=("limkb=$T_LIM")
LOG=""; SEQ=0; RERUNS=1; STOP=DECIDED; RUNSTEPS=""; FB=""; FBSHA=NONE; RC=0; TIMEDOUT=0; CLS=ok
BADFILE=""; BADWANT=""; PRIV=""; P=NONE
has() { case ",$1," in *",$2,"*) return 0;; esac; return 1; } # list item
say() { echo "$1"; [ -n "$LOG" ] && echo "$1" >> "$LOG/run.log"; return 0; }
prelude_stop() { # class reason ; class FAIL = integrity or REQUIRED failure (exit 1), UNRESOLVED = not started (exit 4)
  local cr=NOT_STARTED; [ "$1" = FAIL ] && cr=REQUIRED_OR_INTEGRITY_FAILURE_ROW_008
  say "FLOOR_RUN|CERTIFICATE=FAIL|$NOBOUND|certificate_reason=$cr|stage=prelude|reason=$2|r=$R|steps_run=none|accepted_certificates=0|certificate_commands_run=0|HASHES=NONE|json=0"
  [ "$1" = FAIL ] && exit 1; exit 4
}
# ---- the programs this launcher calls: resolved once under the fixed PATH, logged with their hashes, called by path
TOOLLINES=()
SHA=$(command -v sha256sum) && SHA=$(realpath -e -- "$SHA") || prelude_stop UNRESOLVED program_sha256sum_not_found
resolve() { # name -> RES: the absolute path of a program in a system directory
  RES=$(command -v "$1") && RES=$(realpath -e -- "$RES") || prelude_stop UNRESOLVED "program_$1_not_found"
  case "$RES" in /usr/*|/bin/*|/sbin/*) ;; *) prelude_stop UNRESOLVED "program_$1_lies_outside_the_system_directories";; esac
  TOOLLINES+=("TOOLPATH|name=$1|path=$RES|sha256=$("$SHA" "$RES" | cut -d' ' -f1)|found_under=PATH_/usr/bin:/bin|json=0")
}
resolve sha256sum
resolve python3; PY="$RES"
resolve bash; BASHX="$RES"
resolve timeout; TIMEOUT="$RES"
resolve setsid; SETSID="$RES"
resolve git; GIT="$RES"
TC="$HOME/.rustup/toolchains/1.81-x86_64-unknown-linux-gnu/bin"; CARGO="$TC/cargo"; RUSTC="$TC/rustc"
for x in "$CARGO" "$RUSTC"; do
  TOOLLINES+=("TOOLPATH|name=${x##*/}|path=$x|sha256=$("$SHA" "$x" 2>/dev/null | cut -d' ' -f1)|found_under=the_1.81_toolchain_directory_of_HOME_(password_database)|json=0")
done
# ---- the hashed bytes: each file read once into memory and hashed there (rows 019 020 021 103 114 115)
msha() { printf '%s\n' "$1" | "$SHA" | cut -d' ' -f1; }
PRED_SRC=$(cat -- "$PREDREL" 2>/dev/null) || prelude_stop UNRESOLVED cannot_read_the_prediction_record
P=$(msha "$PRED_SRC")
pinval() { printf '%s\n' "$PRED_SRC" | grep -E "^PIN\|id=$1\|" | sed -n 's/.*|value=\([0-9a-f]\{64\}\)|.*/\1/p'; }
DRVSHA=$(msha "$BASH_EXECUTION_STRING")
[ "$DRVSHA" = "$(pinval 114)" ] || prelude_stop FAIL pinned_file_differs_run_floor.sh
MSRC=("$GATE" "$VERIFIER" "$INDEP" "$PEAK" "$HERE/floor_eval.py")
MROW=(020 019 021 103 115)
MTXT=(); MSHA=(); MWANT=()
for i in "${!MSRC[@]}"; do
  x=$(cat -- "${MSRC[$i]}" 2>/dev/null) || prelude_stop FAIL "pinned_file_differs_${MSRC[$i]##*/}"
  MTXT[$i]="$x"; MSHA[$i]=$(msha "$x"); MWANT[$i]=$(pinval "${MROW[$i]}")
  [ ${#MWANT[$i]} -eq 64 ] && [ "${MSHA[$i]}" = "${MWANT[$i]}" ] || prelude_stop FAIL "pinned_file_differs_${MSRC[$i]##*/}"
done
PEAKSHA="${MSHA[3]}"; EVSHA="${MSHA[4]}"
PEAKCMD=("$PY" -I -B -c "${MTXT[3]}")
PEAKDISP="$PY -I -B -c MEMORY:peak_rss.py@$PEAKSHA"
EVAL=("$PY" -I -B -c "${MTXT[4]}")
# the files of the tree stay under watch as well: a change after this point stops the run
GF=("$PREDREL" "$HERE/run_floor.sh" "$HERE/floor_eval.py" "$GATE" "$VERIFIER" "$INDEP" "$PEAK")
GW=("$P" "$DRVSHA" "$EVSHA" "${MSHA[0]}" "${MSHA[1]}" "${MSHA[2]}" "$PEAKSHA")
guard() { # 0 when every file of GF still has the hash of GW; else BADFILE and BADWANT name the first that differs
  local i got
  for i in "${!GF[@]}"; do
    got=$("$SHA" "${GF[$i]}" 2>/dev/null | cut -d' ' -f1)
    if [ ${#GW[$i]} -ne 64 ] || [ "$got" != "${GW[$i]}" ]; then BADFILE="${GF[$i]}"; BADWANT="${GW[$i]:-NO_PIN_ROW}"; return 1; fi
  done
  return 0
}
hashes_of_out() {
  ( cd "$OUT" 2>/dev/null && find . -type f ! -name 'FLOOR-RUN-RECEIPT.hbp*' ! -path './target/*' ! -path './tmp/*' | LC_ALL=C sort | while read -r f; do
      printf '%s@%s,' "${f#./}" "$("$SHA" "$f" | cut -d' ' -f1)"; done ) | sed 's/,$//'
}
integrity_stop() { # a pinned file or a private copy differs: no evaluator call, no accepted bound, CERTIFICATE=FAIL
  local got fin m rc="$OUT/FLOOR-RUN-RECEIPT.hbp" nm="${BADFILE#"$ROOT"/}"
  [ -n "$PRIV" ] && nm="${nm/#"$PRIV"/PRIVATE_COPY}"
  got=$("$SHA" "$BADFILE" 2>/dev/null | cut -d' ' -f1)
  [ -n "$LOG" ] || prelude_stop FAIL "pinned_file_differs_${BADFILE##*/}"
  say "INTEGRITY|file=$nm|want=$BADWANT|got=${got:-ABSENT}|json=0"
  fin="FLOOR_RUN|CERTIFICATE=FAIL|$NOBOUND|certificate_reason=REQUIRED_OR_INTEGRITY_FAILURE_ROW_008|stage=integrity|reason=pinned_file_changed_${BADFILE##*/}|r=$R|steps_run=${RUNSTEPS:-none}|accepted_certificates=0|prediction_sha256=$P|binary_sha256=$FBSHA|HASHES=$(hashes_of_out)|json=0"
  {
    echo "# floor run receipt written by final/tools/run_floor.sh after an integrity stop; pipe rows; json=0"
    echo "RECEIPT|scope=INTEGRITY_STOP|r=$R|mode=$MODE|json=0"
    echo "INTEGRITY|file=$nm|want=$BADWANT|got=${got:-ABSENT}|json=0"
    for m in "${STEPS[@]}"; do [ -e "$LOG/m${m}_rowhash_a1.txt" ] && echo "ACCEPTED|m0=$m|count=0|json=0"; done
    grep -E '^(INVOKE|INJECTED|NOTE|DECISION|TOOL)' "$LOG/run.log"
    echo "$fin"
  } > "$rc"
  ( cd "$OUT" && "$SHA" FLOOR-RUN-RECEIPT.hbp > FLOOR-RUN-RECEIPT.hbp.sha256 )
  echo "$fin"; exit 1
}
guard || integrity_stop
# ---- the run directory: an absolute, canonical path; in test mode it lies outside the repository and the freeze folder
TOP=$("$GIT" -C "$ROOT" rev-parse --show-toplevel 2>/dev/null) || TOP=""
if [ "$MODE" = test ]; then
  "${EVAL[@]}" rcheck r="$R" || prelude_stop UNRESOLVED test_r_refused_within_1_of_9
  case "$OUT" in /*) ;; *) prelude_stop UNRESOLVED test_out_must_be_an_absolute_path;; esac
  [ -L "$OUT" ] && prelude_stop UNRESOLVED run_directory_already_exists
  OUT=$(realpath -m -- "$OUT") || prelude_stop UNRESOLVED test_out_cannot_be_resolved
  case "$OUT/" in "$ROOT"/*) prelude_stop UNRESOLVED test_out_must_lie_outside_the_freeze_folder;; esac
  [ -n "$TOP" ] && case "$OUT/" in "$TOP"/*) prelude_stop UNRESOLVED test_out_must_lie_outside_the_repository;; esac
  [ ${#STEPS[@]} -ge 1 ] && [ ${#STEPS[@]} -le 3 ] || prelude_stop UNRESOLVED test_m0_takes_1_to_3_steps
else
  OUT=$(realpath -m -- "$OUT") || prelude_stop UNRESOLVED run_directory_cannot_be_resolved
  case "$OUT" in "$ROOT"/work/run9) ;; *) prelude_stop UNRESOLVED run_directory_resolves_outside_work_run9;; esac
fi
git_contact() { # the checkout as git reports it: readable, no dubious ownership, no file-mode difference
  local e a b rest
  e=$("$GIT" -C "$ROOT" rev-parse --show-toplevel 2>&1) || {
    case "$e" in *dubious*) prelude_stop UNRESOLVED git_reports_dubious_ownership_of_this_checkout;; esac
    prelude_stop UNRESOLVED git_cannot_read_this_checkout
  }
  while read -r a b rest; do
    [ -n "$a" ] || continue
    a="${a#:}"
    [ "$a" != "$b" ] && [ "$a" != 000000 ] && [ "$b" != 000000 ] && prelude_stop UNRESOLVED git_reports_filemode_differences
  done < <("$GIT" -C "$ROOT" -c core.filemode=true diff --raw -- . 2>/dev/null)
  return 0
}
FZ=0; { [ "$MODE" = r9 ] || [ $T_FB -eq 1 ]; } && FZ=1
if [ $FZ -eq 1 ] || [ $T_GIT -eq 1 ]; then git_contact; fi
{ [ -e "$OUT" ] || [ -L "$OUT" ]; } && prelude_stop UNRESOLVED run_directory_already_exists
mkdir -p "$OUT/log" "$OUT/tmp" || prelude_stop UNRESOLVED cannot_create_run_directory
# ---- TMPDIR: a tmpfs inside the run directory, mounted in this launcher's private mount namespace; the tools get a
# tmpfs of their own inside it, set read-only once the last file is written
mount -t tmpfs -o mode=700,size=256m floor-run-tmp "$OUT/tmp" 2>/dev/null || prelude_stop UNRESOLVED cannot_mount_the_private_tmpfs
export TMPDIR="$OUT/tmp"
PRIV="$TMPDIR/tools"
mkdir -m 700 "$PRIV" && mount -t tmpfs -o mode=700,size=256m floor-run-tools "$PRIV" 2>/dev/null && mkdir -m 700 "$PRIV/py"   || prelude_stop UNRESOLVED cannot_create_the_private_tool_directory
# ---- the namespace once more, by its effect (row 132): both mounts are in this process's mount table and in
# neither the parent's nor that of process 1; a mount that shows outside is taken down and the run does not start
ns_seen() { /usr/bin/grep -Fq " $2 " "$1" 2>/dev/null; } # mount table, mount point ; 0 listed, 1 absent, 2 unreadable
NSBAD=""
for x in "$OUT/tmp" "$PRIV"; do
  ns_seen /proc/self/mountinfo "$x"; [ $? -eq 0 ] || NSBAD=mount_absent_from_the_mount_table_of_this_process
  ns_seen "/proc/$PPID/mountinfo" "$x"; [ $? -eq 1 ] || NSBAD=${NSBAD:-private_tmpfs_listed_or_unreadable_in_the_mount_table_of_the_parent_process}
  ns_seen /proc/1/mountinfo "$x"; [ $? -eq 1 ] || NSBAD=${NSBAD:-private_tmpfs_listed_or_unreadable_in_the_mount_table_of_process_1}
done
[ "$(/usr/bin/readlink /proc/self/ns/mnt 2>/dev/null)" = "$NS_SELF" ] || NSBAD=${NSBAD:-mount_namespace_id_changed}
[ -z "$(ns_others)" ] || NSBAD=${NSBAD:-mount_namespace_is_held_by_another_process}
[ -z "$(ns_refs)" ] || NSBAD=${NSBAD:-mount_namespace_reference_outside_a_member_process}
if [ -n "$NSBAD" ]; then umount "$PRIV" 2>/dev/null; umount "$OUT/tmp" 2>/dev/null; prelude_stop UNRESOLVED "$NSBAD"; fi
TDST=("$PRIV/gate_required.sh" "$PRIV/py/cert_gate.py" "$PRIV/py/indep_verify.py")
for i in 0 1 2; do
  printf '%s\n' "${MTXT[$i]}" > "${TDST[$i]}" || prelude_stop UNRESOLVED cannot_write_a_tool_into_the_private_directory
  GF+=("${TDST[$i]}"); GW+=("${MSHA[$i]}")
done
PPRED="$PRIV/${PREDREL##*/}"
printf '%s\n' "$PRED_SRC" > "$PPRED" || prelude_stop UNRESOLVED cannot_write_a_tool_into_the_private_directory
GF+=("$PPRED"); GW+=("$P")
guard || integrity_stop
GATE="$PRIV/gate_required.sh"; VERIFIER="$PRIV/py/cert_gate.py"
LOG="$OUT/log"
say "START|mode=$MODE|r=$R|m0_steps=${STEPS[*]}|f=$FSPEC|g0=$G0|prediction_sha256=$P|driver_sha256=$DRVSHA|run_directory=$OUT|json=0"
say "NOTE|environment=env_-i_with_PATH=/usr/bin:/bin_LANG=C_HOME=${HOME}_TMPDIR=<run_directory>/tmp|mount_namespace=private_CHECKED_(row_132)|namespace_of_this_process=$NS_SELF|namespace_of_the_parent_process=$NS_PARENT|namespace_of_process_1=$NS_INIT|shared_or_slave_mounts=0|other_processes_in_this_namespace=0|references_to_this_namespace_outside_member_processes=0|mount_namespaces_without_a_member_process=0|both_tmpfs_mounts=listed_here_and_absent_from_the_mount_tables_of_the_parent_process_and_of_process_1|tmpdir=tmpfs_mounted_in_that_namespace|private_tools=a_second_tmpfs_read-only_after_the_last_write|launcher_pid=$$|children=bash_--noprofile_--norc_and_python3_-I_-B|json=0"
for x in "${TOOLLINES[@]}"; do say "$x"; done
for i in 0 1 2; do
  say "TOOL|private_copy=${TDST[$i]#"$PRIV"/}|written_from=memory|source=${MSRC[$i]}|sha256=$("$SHA" "${TDST[$i]}" | cut -d' ' -f1)|pin=${MROW[$i]}|want=${MWANT[$i]}|json=0"
done
say "TOOL|in_memory=peak_rss.py|runs_as=python3_-I_-B_-c|source=${MSRC[3]}|sha256=$PEAKSHA|pin=103|want=${MWANT[3]}|json=0"
say "TOOL|in_memory=floor_eval.py|runs_as=python3_-I_-B_-c|source=final/tools/floor_eval.py|sha256=$EVSHA|pin=115|want=${MWANT[4]}|json=0"
say "TOOL|in_memory=run_floor.sh|runs_as=bash_--noprofile_--norc_-c|source=final/tools/run_floor.sh|sha256=$DRVSHA|pin=114|want=$(pinval 114)|json=0"
say "TOOL|private_copy=${PPRED#"$PRIV"/}|written_from=memory|source=$PREDREL|sha256=$("$SHA" "$PPRED" | cut -d' ' -f1)|pin=record|want=$P|json=0"
# ---- freeze commit (frozen run, and a rehearsal with --test-frozen-build): the commit that carries the prediction
# record, checked by blob hash
if [ $FZ -eq 1 ]; then
  [ -n "$C" ] || C=$("$GIT" log -1 --format=%H -- "$PREDREL" 2>/dev/null)
  echo "$C" | grep -Eq '^[0-9a-f]{40}$' || prelude_stop UNRESOLVED freeze_commit_not_found
  PFX=$("$GIT" rev-parse --show-prefix 2>/dev/null)
  BL=$("$GIT" show "$C:$PFX$PREDREL" 2>/dev/null | "$SHA" | cut -d' ' -f1)
  [ "$BL" = "$P" ] || prelude_stop FAIL prediction_record_differs_from_the_freeze_commit
  [ -z "$("$GIT" status --porcelain --untracked-files=no 2>/dev/null)" ] || prelude_stop FAIL tracked_files_differ_from_the_commit
  [ "$("$GIT" rev-parse HEAD 2>/dev/null)" = "$C" ] || prelude_stop FAIL checkout_head_is_not_the_freeze_commit
  [ -z "$("$GIT" -C "$TOP" ls-files -v 2>/dev/null | grep '^[a-zS] ')" ] || prelude_stop FAIL index_marks_a_file_assume_unchanged_or_skip_worktree
  say "NOTE|freeze_commit=$C|prediction_blob_sha256=$BL|head_equals_the_freeze_commit=1|files_marked_assume_unchanged_or_skip_worktree=0|json=0"
fi
# ---- toolchain (row 017) and the pin-free binary of row 016
RV=$("$RUSTC" --version 2>&1); CV=$("$CARGO" --version 2>&1)
say "NOTE|rustc=$RV|cargo=$CV|json=0"
[ "$RV" = "$RUSTC_PIN" ] && [ "$CV" = "$CARGO_PIN" ] || prelude_stop FAIL toolchain_differs_from_row_017
# ---- the build environment (row 139): nothing but the pinned source, Cargo.toml and Cargo.lock reaches cargo
CGD="$ROOT/work/design/rs"
while :; do
  { [ -e "$CGD/.cargo/config.toml" ] || [ -e "$CGD/.cargo/config" ] || [ -L "$CGD/.cargo" ]; } && prelude_stop FAIL cargo_configuration_file_in_the_Rust_folder_or_above_it
  [ "$CGD" != "$ROOT/work/design/rs" ] && [ -e "$CGD/Cargo.toml" ] && grep -q workspace "$CGD/Cargo.toml" 2>/dev/null && prelude_stop FAIL cargo_manifest_naming_a_workspace_above_the_Rust_folder
  [ "$CGD" = / ] && break
  CGD=$(dirname "$CGD")
done
if [ -n "$TOP" ]; then
  [ -z "$("$GIT" -C "$ROOT" ls-files --others -- work/design/rs 2>/dev/null | grep -v '^work/design/rs/target/')" ] || prelude_stop FAIL untracked_file_in_the_Rust_folder
fi
CH="$TMPDIR/cargo-home"; mkdir -m 700 "$CH" || prelude_stop UNRESOLVED cannot_create_the_empty_cargo_home
say "NOTE|build_environment=CARGO_HOME_is_an_empty_directory_on_the_launcher_tmpfs|cargo_configuration_files_in_the_Rust_folder_or_above=0|cargo_manifests_naming_a_workspace_above_the_Rust_folder=0|untracked_files_in_the_Rust_folder_outside_target=$([ -n "$TOP" ] && echo 0 || echo NOT_CHECKED_no_git_checkout)|json=0"
if [ ! -f "$PINFREE" ]; then
  (cd work/design/rs && CARGO_HOME="$CH" RUSTC="$RUSTC" "$CARGO" build --release --locked -j1) > "$LOG/build_pinfree.txt" 2>&1 \
    || prelude_stop UNRESOLVED pin_free_build_failed
fi
guard || integrity_stop
"${EVAL[@]}" pins root="$ROOT" pred="$PPRED" tag=1 > "$LOG/pincheck_1.txt" 2>&1 || { tail -1 "$LOG/pincheck_1.txt"; prelude_stop FAIL pin_check_1_mismatch_row_010; }
say "$(tail -1 "$LOG/pincheck_1.txt")"
if [ $FZ -eq 1 ]; then
  FB="$OUT/target/release/floorcert"
  (cd work/design/rs && CARGO_HOME="$CH" RUSTC="$RUSTC" CARGO_TARGET_DIR="$OUT/target" FLOORCERT_FREEZE_COMMIT="$C" FLOORCERT_PREDICTION_SHA256="$P" "$CARGO" build --release --locked -j1) > "$LOG/build_frozen.txt" 2>&1 || prelude_stop UNRESOLVED frozen_build_failed
  [ -f "$FB" ] || prelude_stop UNRESOLVED frozen_binary_absent
  guard || integrity_stop
  "${EVAL[@]}" pins root="$ROOT" pred="$PPRED" tag=2 > "$LOG/pincheck_2.txt" 2>&1 || { tail -1 "$LOG/pincheck_2.txt"; prelude_stop FAIL pin_check_2_mismatch_row_010; }
  say "$(tail -1 "$LOG/pincheck_2.txt")"
  if [ "$MODE" = r9 ]; then
    FREEZE_ARGS=(--freeze-commit "$C" --prediction "$PREDREL" --prediction-sha256 "$P")
  else
    # a rehearsal: the binary carries the two pins and runs at the excluded R, where it takes no freeze argument
    FREEZE_ARGS=()
    say "NOTE|frozen_build_rehearsal=1|freeze_commit=$C|compiled_prediction_sha256=$P|build_log=log/build_frozen.txt|pin_check_2=HELD|r=$R|json=0"
  fi
else
  FB="$PINFREE"; C=NONE; FREEZE_ARGS=()
fi
# ---- the binary: one private copy, and that copy is the program every writer command runs
XB="$PRIV/floorcert"
cp "$FB" "$XB" && chmod -R a-w "$PRIV" && mount -o remount,ro "$PRIV" 2>/dev/null   || prelude_stop UNRESOLVED cannot_copy_the_binary_into_the_private_directory
FBSHA=$("$SHA" "$XB" | cut -d' ' -f1)
if [ $FZ -eq 1 ]; then
  [ "$FBSHA" != "$(pinval 016)" ] || prelude_stop FAIL frozen_build_gave_the_pin_free_binary_of_row_016
else
  [ "$FBSHA" = "$(pinval 016)" ] || prelude_stop FAIL binary_copy_differs_from_row_016
fi
GF+=("$FB" "$XB"); GW+=("$FBSHA" "$FBSHA")
guard || integrity_stop
say "TOOL|private_copy=floorcert|source=$FB|sha256=$FBSHA|pin=$([ $FZ -eq 1 ] && echo frozen_build_of_row_009 || echo 016)|want=$FBSHA|json=0"
say "NOTE|binary=$FB|binary_sha256=$FBSHA|executed_copy=PRIVATE_COPY/floorcert|private_directory=$PRIV|json=0"

run_cmd() { # kind m0 attempt limit killafter logfile prefix argv... ; prefix peak = under peak_rss.py from memory
  local kind=$1 m=$2 att=$3 lim=$4 ka=$5 lf=$6 pre=$7 t0 t1 cpid pg n disp; shift 7
  guard || integrity_stop
  SEQ=$((SEQ+1)); t0=$(date +%s)
  if [ "$pre" = peak ]; then
    disp="$PEAKDISP $*"
    "$SETSID" "$TIMEOUT" -k "$ka" "$lim" "${PEAKCMD[@]}" "$@" > "$lf" 2>&1 &
  else
    disp="$*"
    "$SETSID" "$TIMEOUT" -k "$ka" "$lim" "$@" > "$lf" 2>&1 &
  fi
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
  # the tools once more after the call: the bytes that ran are the bytes that were hashed
  guard || integrity_stop
  say "INVOKE|seq=$SEQ|m0=$m|kind=$kind|attempt=$att|rc=$RC|limit_s=$lim|elapsed_s=$((t1-t0))|time_limit_hit=$TIMEDOUT|own_process_group=$([ "$pg" = "$cpid" ] && echo 1 || echo 0)|private_tools_after=HELD|log=${lf#"$OUT"/}|log_sha256=$("$SHA" "$lf" | cut -d' ' -f1)|argv=$disp|json=0"
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
do_cmd() { # kind m0 idx logbase prefix argv... ; one rerun after a crash while the run still has its rerun; none after a time limit
  local kind=$1 m=$2 idx=$3 lb=$4 pre=$5; shift 5
  local att=1 lf
  while :; do
    lf="$LOG/${lb}_a${att}.txt"
    if [ $att -eq 1 ] && has "$T_CRASH" "$idx:$kind"; then
      say "INJECTED|m0=$m|kind=$kind|what=crash_by_signal_in_place_of_the_first_attempt|json=0"
      run_cmd "$kind" "$m" $att "$LIMIT" "$KILLAFTER" "$lf" peak "$BASHX" --noprofile --norc -c 'kill -SEGV $$'
    elif [ $att -eq 1 ] && [ "$kind" = gate ] && has "$T_VEXC" "$idx"; then
      say "INJECTED|m0=$m|kind=$kind|what=the_output_of_gate_required.sh_for_a_verifier_that_ended_with_an_exception_(exit_1,_no_verdict_line)_in_place_of_the_first_attempt|json=0"
      run_cmd "$kind" "$m" $att "$LIMIT" "$KILLAFTER" "$lf" plain "$BASHX" --noprofile --norc -c 'echo "Traceback (most recent call last):"; echo "GATE_REQUIRED|REFUSE|cert=INJECTED|cert_sha256=INJECTED|verifier_exit=1|header_rowhash=|verifier_rowhash=|"; exit 1'
    elif has "$T_HANG" "$idx:$kind"; then
      say "INJECTED|m0=$m|kind=$kind|what=sleep_20_under_a_2_second_limit_in_place_of_the_command|json=0"
      run_cmd "$kind" "$m" $att 2 "$KILLAFTER" "$lf" plain sleep 20
    elif has "$T_HARD" "$idx:$kind"; then
      say "INJECTED|m0=$m|kind=$kind|what=a_command_that_ignores_TERM_under_a_2_second_limit_with_KILL_3_seconds_later|json=0"
      run_cmd "$kind" "$m" $att 2 3 "$lf" plain "$BASHX" --noprofile --norc -c 'trap "" TERM; sleep 20'
    else
      run_cmd "$kind" "$m" $att "$LIMIT" "$KILLAFTER" "$lf" "$pre" "$@"
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
  say "NOTE|before_m0=$m|binary_sha256=$("$SHA" "$XB" | cut -d' ' -f1)|json=0"
  do_cmd rowhash "$m" "$idx" "m${m}_rowhash" peak "$XB" rowhash --m0 "$m" --threads 2 --dir "$RUN"
  case $CLS in
    refuse) stub "$m" FAIL rowhash_command_refused; return 0;;
    crash|timeout) aside rowhash "$m" final; opfail "$m" "rowhash_command_$CLS"; return 0;;
  esac
  if [ "$idx" -eq 3 ]; then # row 007 prerequisite
    "$SHA" "$RUN/core_keys_m$m.bin" > "$LOG/m${m}_keysha.txt" 2>&1
    do_cmd rowsonly "$m" "$idx" "m${m}_rowsonly" plain "$PY" -I -B "$VERIFIER" --rows-only "$RUN/core_keys_m$m.bin" "$m"
    # row 123: the memory limit first, over the rowhash and the rows-only verifier, before the prerequisite outcome is read
    guard || integrity_stop
    x=$("${EVAL[@]}" limit out="$OUT" m0="$m" mode="$MODE" "${LIMARG[@]}"); b=$?; say "$x"
    if [ $b -ne 0 ]; then [ -f "$LOG/m${m}_step.hbp" ] || stub "$m" FAIL memory_limit_check_gave_no_result; return 0; fi
    [ "$CLS" = ok ] || { STOP="PREREQUISITE_NOT_MET_row_007_verifier_$CLS"; return 1; }
    guard || integrity_stop
    x=$("${EVAL[@]}" prereq out="$OUT" pred="$PPRED" m0="$m" mode="$MODE" "${LIMARG[@]}"); b=$?; say "$x|json=0"
    [ $b -eq 0 ] || { STOP=PREREQUISITE_NOT_MET_row_007; return 1; }
  fi
  ls -1 "$RUN" > "$LOG/m${m}_dir_after_rowhash.txt"
  local extra=()
  [ "$T_PLANT" != "" ] && [ "${T_PLANT%%:*}" = "$idx" ] && { extra=(--plant all --ub "${T_PLANT#*:}"); say "INJECTED|m0=$m|kind=cert|what=plant_all_files_written_beside_the_honest_certificate|json=0"; }
  do_cmd cert "$m" "$idx" "m${m}_cert" peak "$XB" cert --m0 "$m" --r "$R" --f "$FSPEC" --write-cert --threads 2 --dir "$RUN" "${FREEZE_ARGS[@]}" "${extra[@]}"
  case $CLS in
    refuse) stub "$m" FAIL cert_command_refused; return 0;;
    crash|timeout) aside cert "$m" final; opfail "$m" "cert_command_$CLS"; return 0;;
  esac
  for x in "$RUN"/cert_*.txt; do
    [ -e "$x" ] || continue
    b=$(basename "$x")
    do_cmd gate "$m" "$idx" "m${m}_gate_$b" plain "$BASHX" --noprofile --norc "$GATE" "$x" "${FREEZE_ARGS[@]}"
    # a verifier that ended without a verdict (exception, kill) or ran into the time limit: operational, rows 006 (b) and
    # 007 (b); the certificates of this step are set aside and none of them counts (row 126)
    case $CLS in crash|timeout) aside gate "$m" final; opfail "$m" "verifier_$CLS"; return 0;; esac
  done
  guard || integrity_stop
  "${EVAL[@]}" step root="$ROOT" tools="$PRIV" pred="$PPRED" out="$OUT" m0="$m" r="$R" fspec="$FSPEC" mode="$MODE" census="$CENSUS" commit="$C" psha="$P" fbsha="$FBSHA" \
    py="$PY" bash="$BASHX" peaksha="$PEAKSHA" evsha="$EVSHA" drvsha="$DRVSHA" "${LIMARG[@]}" | tee -a "$LOG/run.log"
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
if [ -n "$(ns_others)" ]; then STOP=FAIL_another_process_sits_in_the_mount_namespace_at_the_close; say "NOTE|close=another_process_sits_in_the_mount_namespace|json=0"; fi
if [ -n "$(ns_refs)" ]; then STOP=FAIL_a_mount_namespace_reference_outside_a_member_process_at_the_close; say "NOTE|close=mount_namespace_reference_outside_a_member_process|json=0"; fi
for i in 0 1 2; do
  say "TOOL_CLOSING|private_copy=${TDST[$i]#"$PRIV"/}|sha256=$("$SHA" "${TDST[$i]}" | cut -d' ' -f1)|want=${MWANT[$i]}|json=0"
done
say "TOOL_CLOSING|in_memory=peak_rss.py|sha256=$(msha "${MTXT[3]}")|want=${MWANT[3]}|json=0"
say "TOOL_CLOSING|in_memory=floor_eval.py|sha256=$(msha "${MTXT[4]}")|want=${MWANT[4]}|json=0"
say "TOOL_CLOSING|in_memory=run_floor.sh|sha256=$(msha "$BASH_EXECUTION_STRING")|want=$(pinval 114)|json=0"
FOUT=$("${EVAL[@]}" final root="$ROOT" tools="$PRIV" out="$OUT" pred="$PPRED" steps="$RUNSTEPS" g0="$G0" allowed="${#STEPS[@]}" plan="$(IFS=,; echo "${STEPS[*]}")" fspec="$FSPEC" mode="$MODE" r="$R" stop="$STOP" \
  commit="$C" fbsha="$FBSHA" drvsha="$DRVSHA" evsha="$EVSHA" peaksha="$PEAKSHA" predrel="$PREDREL" receipt="$OUT/FLOOR-RUN-RECEIPT.hbp")
ERC=$?
guard || integrity_stop
# ---- the final line: printed here from the captured output of the evaluator that ran from memory; the exit code
# is read off that line and must agree with the evaluator's own
FIN=$(printf '%s\n' "$FOUT" | grep '^FLOOR_RUN|')
printf '%s\n' "$FOUT" | grep -v '^FLOOR_RUN|'
case "$FIN" in
  *$'\n'*) XC=bad;;
  "FLOOR_RUN|CERTIFICATE=PASS|PREDICTION=CONFIRMED|DECISION=ABOVE|"*) XC=0;;
  "FLOOR_RUN|CERTIFICATE=PASS|PREDICTION=FALSIFIED|DECISION=BELOW|"*) XC=3;;
  "FLOOR_RUN|CERTIFICATE=PASS|PREDICTION=UNRESOLVED|DECISION=UNRESOLVED|"*) XC=2;;
  "FLOOR_RUN|CERTIFICATE=FAIL|$NOBOUND|"*) XC=1;;
  *) XC=bad;;
esac
if [ "$XC" = bad ] || [ "$XC" != "$ERC" ]; then
  echo "FLOOR_RUN|CERTIFICATE=FAIL|$NOBOUND|certificate_reason=REQUIRED_OR_INTEGRITY_FAILURE_ROW_008|stage=closing|reason=evaluator_output_and_exit_code_${ERC}_do_not_form_one_final_line|r=$R|steps_run=${RUNSTEPS:-none}|accepted_certificates=0|prediction_sha256=$P|binary_sha256=$FBSHA|HASHES=$(hashes_of_out)|json=0"
  exit 1
fi
echo "PUBLISH|receipt_sha256=$("$SHA" "$OUT/FLOOR-RUN-RECEIPT.hbp" | cut -d' ' -f1)|receipt=$OUT/FLOOR-RUN-RECEIPT.hbp|make_this_value_public_now=the_checker_of_row_131_requires_it_for_the_r9_receipt_(row_138)|json=0"
printf '%s\n' "$FIN"
exit "$XC"
}
