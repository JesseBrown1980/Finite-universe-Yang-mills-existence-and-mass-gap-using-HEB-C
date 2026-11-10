#!/bin/bash
set -u
R=/tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/floor
W=$R/work
T="python3 -I -B /mnt/c/tmp/opus55/floor-freeze-verify/scripts/fztrace.py"
O=/tmp/opus55ffv/trace
mkdir -p $O
S=$W/verify_opus55/smoke/cert_m7_r12_1_f4-3-2-1.txt
P=$W/verify_opus55/plants_m6
run() { name=$1; shift; FZ_OUT=$O/$name.fz /usr/bin/time -f "%e s %M kB" $T "$@" > $O/$name.out 2> $O/$name.time; echo "$name rc=$? $(tail -1 $O/$name.time) | $(grep -E '^VERDICT|^LINT_RESULT|^PEAK_RSS|RESULT' $O/$name.out | tail -1 | cut -c1-120)"; cat $O/$name.fz | tail -3; }
run cg_smoke $W/design/py/cert_gate.py $S
run cg_m6_honest $W/design/py/cert_gate.py $P/cert_m6_r21_2_f4-3-2-1.txt
run cg_m6_P4a $W/design/py/cert_gate.py $P/cert_m6_r21_2_P4a_gamma_overstated_by_1e-4.txt
run cg_m6_P5b $W/design/py/cert_gate.py $P/cert_m6_r21_2_P5b_misrouted_two_step_target.txt
run cg_rowsonly_m7 $W/design/py/cert_gate.py --rows-only $W/verify_opus55/smoke/core_keys_m7.bin 7
run iv_smoke $W/design/py/indep_verify.py $S
run iv_m6 $W/design/py/indep_verify.py $P/cert_m6_r21_2_f4-3-2-1.txt
run cv_m6 $W/critic/class_verify.py $P/cert_m6_r21_2_f4-3-2-1.txt
run ov_m6 $W/critic/orbit_verify.py $P/cert_m6_r21_2_f4-3-2-1.txt
run lint $R/final/tools/lint_hbp.py $R/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp $R
run peak $W/design/peak_rss.py $W/design/rs/target/release/floorcert selftest
