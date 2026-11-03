#!/bin/bash
# Assembles independent/electric_spectrum_2x2.measure from one run folder, in a fixed order. No arithmetic beyond bash integers.
# The folder holds a.out b.out c.out same.out d_sectors.out d.log e.out e.done, and d_T.out d_T.errout for each T in d.log.
# usage: electric_spectrum_2x2_assemble.sh RUN_FOLDER
set -uo pipefail
R=$1
PY="python3 -I -X utf8"
S=independent/electric_spectrum_2x2.py
M=independent/electric_spectrum_2x2.measure
COSTS="0 6 12 15 18 21 24 27 30 33 36 42 48"

open_interval() {
  local low=0 c
  for c in $COSTS; do
    if [ $(( c * 1000 )) -ge "$1" ]; then echo "$low,$c"; return; fi
    low=$c
  done
  echo "$low,above"
}

{
  echo "ELECTRIC_MEASURE_HEAD|prediction_commit=2e7afedb9bbfc9d1e1113bb223b77cf845db1f38|retry_prediction_commit=4ee284590ea088f153f829ab94097389298c9255|retry2_prediction_commit=ea23e312bf8f50f8f6f11aab7aa6944d3b75441d|script=$S|lane=git_bash_windows_python_3.13|hosted_replay=.github/workflows/electric-spectrum-2x2.yml|float_used=0|json=0"
  for f in independent/gpt6_2x2_from_permutations.py independent/gpt6_sturm_sectors.py independent/gpt6_sturm_interval.py native/ym/independent/indep_verify.py; do
    echo "ELECTRIC_ENGINE|file=$f|sha256=$(sha256sum "$f" | cut -d' ' -f1)|json=0"
  done
  cat "$R/a.out" "$R/b.out" "$R/c.out" "$R/same.out" "$R/d_sectors.out"
  grep '^RUN|path=D|T=' "$R/d.log" | while IFS='|' read -r _ _ tfield rcfield secfield _; do
    T=${tfield#T=}
    rc=${rcfield#rc=}
    sec=${secfield#seconds=}
    grep '^GPT6_SECTOR|' "$R/d_$T.errout" | sed "s/^GPT6_SECTOR|/ELECTRIC_D_SECTOR|T=$T|/" || true
    if [ "$rc" = 0 ]; then
      cat "$R/d_$T.out"
    else
      done_sectors=$(grep -c '^GPT6_SECTOR|' "$R/d_$T.errout" || true)
      last=$(tail -1 "$R/d_$T.errout" | tr -d ':' | tr ' ' '_')
      if [ "$T" = 6000 ]; then place="at_eigenvalue=6"; tag=ELECTRIC_D_SINGULAR; else place="open_interval=$(open_interval "$T")"; tag=ELECTRIC_D_UNCERTIFIED; fi
      echo "$tag|T=$T|exit=$rc|sturm_rows=$(grep -c . "$R/d_$T.out" || true)|sectors_certified_before_stop=$done_sectors|stderr_last=$last|$place|json=0"
    fi
    echo "ELECTRIC_D_RUN|T=$T|exit=$rc|seconds=$sec|lane=local_below_normal|json=0"
  done
  cat "$R/e.out"
  e_rc=$(sed 's/.*|rc=\([0-9]*\)|.*/\1/' "$R/e.done")
  e_sec=$(sed 's/.*|seconds=\([0-9]*\)|.*/\1/' "$R/e.done")
  echo "ELECTRIC_E_RUN|exit=$e_rc|seconds=$e_sec|workers=3|kernel_source_blob=$(git ls-files -s native/ym/independent/minors/src/main.rs | cut -d' ' -f2)|lane=local_below_normal|json=0"
} > "$R/measure.base"

$PY $S f "$R/measure.base" | tr -d '\r' > "$R/f.out"
test "${PIPESTATUS[0]}" = 0 || { cat "$R/f.out"; exit 1; }
cat "$R/measure.base" "$R/f.out" > "$R/measure.with_f"
$PY $S predictions independent/ELECTRIC-SPECTRUM-2X2-PREDICTION.hbp independent/ELECTRIC-SPECTRUM-2X2-RETRY-PREDICTION.hbp independent/ELECTRIC-SPECTRUM-2X2-RETRY-PREDICTION-2.hbp "$R/measure.with_f" | tr -d '\r' > "$R/p.out"
test "${PIPESTATUS[0]}" = 0 || { cat "$R/p.out"; exit 1; }
cat "$R/measure.with_f" "$R/p.out" > "$M"
wc -l "$M"
echo "CR=$(tr -cd '\r' < "$M" | wc -c)"
