#!/usr/bin/env bash
# Exact measured comparison: the same finite S3 Yang-Mills jobs, executed
# and independently re-executed via direct CLI and via the HTTP-0 backend.
# Neither 3^16 virtual addresses nor source-certificate lookups replace math.
# usage: bash native/ym/scripts/http0_full_tests.sh BIN WORK PORT SPEC
set -euo pipefail
test "$#" -eq 4 || { echo 'HTTP0_FULL|status=FAIL|reason=arity|json=0'; exit 2; }
BIN="$1"
WORK="$2"
PORT="$3"
SPEC="$4"
case "$PORT" in ''|*[!0-9]*) echo 'HTTP0_FULL|status=FAIL|reason=bad_port|json=0'; exit 2;; esac
case "$SPEC" in
    sector/2/2/1/1|sector/2/2/1/-1|sector/2/2/-1/1|sector/2/2/-1/-1|count/2/2/1/1/1/27/64000/15/10) ;;
    *) echo 'HTTP0_FULL|status=FAIL|reason=spec_not_admitted|json=0'; exit 2 ;;
esac
test -x "$BIN" || { echo 'HTTP0_FULL|status=FAIL|reason=missing_binary|json=0'; exit 2; }
mkdir -p "$WORK/cli" "$WORK/http"
SPECS=("$SPEC")
if [ "$SPEC" = "count/2/2/1/1/1/27/64000/15/10" ]; then
    SPECS=("sector/2/2/1/1" "$SPEC")
fi
EPOCH=$(date +%s)
for s in "${SPECS[@]}"; do
    "$BIN" job "$WORK/cli" "$s" > "$WORK/cli-job.out"
    grep -Fq 'result=PASS' "$WORK/cli-job.out"
    "$BIN" verify "$WORK/cli" "$s" > "$WORK/cli-verify.out"
    grep -Fq 'result=PASS' "$WORK/cli-verify.out"
done
CLI_SECS=$(( $(date +%s) - EPOCH ))
EPOCH=$(date +%s)
OUT_ID="$WORK/HTTP0.hbp" bash native/ym/scripts/http0_jobs.sh "$BIN" "$WORK/http" "$PORT" "${SPECS[@]}" > "$WORK/http0-jobs.out"
grep -q '^HTTP0_IDENTITY|.*|server_exit=0|json=0$' "$WORK/HTTP0.hbp"
HTTP_SECS=$(( $(date +%s) - EPOCH ))
for s in "${SPECS[@]}"; do
    SPEC_ID="$(printf '%s' "$s" | tr '/' '_')"
    for name in run.hbp index.hbi run.anchor; do
        cmp "$WORK/cli/shards/$SPEC_ID/$name" "$WORK/http/shards/$SPEC_ID/$name"
    done
done
# Wall seconds measured on the same hosted runner. Report, do not infer that
# HTTP-0's virtual lookup is a faster Hamiltonian solver.
echo "HTTP0_FULL|spec=$SPEC|jobs=${#SPECS[@]}|cli_secs=$CLI_SECS|http0_secs=$HTTP_SECS|canonical=BYTE_IDENTICAL|reexecution=PASS|route=PASS|scope=FINITE_2X2|result=PASS|json=0" | tee "$WORK/RESULT.hbp"
SPEC_ID="$(printf '%s' "$SPEC" | tr '/' '_')"
(cd "$WORK" && sha256sum RESULT.hbp "cli/shards/$SPEC_ID/run.hbp" "http/shards/$SPEC_ID/run.hbp" > SHA256SUMS)
