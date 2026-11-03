#!/bin/bash
# The fitted trial vectors of the attack: two controls first, then the four main rows. Predicted at vector/attack/HYBRID-ATTACK-PREDICTION.hbp, row ATTACK_UPPER2_PREDICTION. Below normal priority, 3 threads.
export MSYS_NO_PATHCONV=1
cd C:/tmp/ym-hybrid-attack || exit 9
X=./hybridcheck.exe
L=UPPER-RUNS.hbp
run() { local tag=$1; shift; local t0=$(date +%s); "$X" "$@" > "upper.$tag" 2> "uppererr.$tag"; local c=$?; printf 'RUN|tag=%s|exit=%d|wall_secs=%d|at=%s|json=0\n' "$tag" "$c" "$(( $(date +%s) - t0 ))" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$L"; cat "upper.$tag" "uppererr.$tag" >> "$L"; }
run c3x3_full upper 3 3 9 27 in/hyb_3x3_full.hybrid 200 3 psi-3x3-full.psi
run c3x4_m14 upper 3 4 9 14 in/hyb_3x4_r9_m14.hybrid 200 3 psi-3x4-m14.psi
run m4x4_r9 upper 4 4 9 14 in/hyb_4x4_r9_m14.hybrid 200 3 psi-4x4-r9-m14.psi
run m4x4_r6 upper 4 4 6 14 in/hyb_4x4_r6_m14.hybrid 200 3 psi-4x4-r6-m14.psi
run m4x5_r9 upper 4 5 9 13 in/hyb_4x5_r9_m13.hybrid 200 3 psi-4x5-r9-m13.psi
run m5x5_r9 upper 5 5 9 11 in/hyb_5x5_r9_m11.hybrid 200 3 psi-5x5-r9-m11.psi
printf 'UPPER_DONE|at=%s|json=0\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$L"
