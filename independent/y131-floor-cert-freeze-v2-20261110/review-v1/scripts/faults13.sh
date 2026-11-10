#!/bin/bash
set -u
R=/tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/floor
D=$R/work/design
O=$R/work/verify_opus55/faults
mkdir -p $O
S=$R/work/verify_opus55/smoke/cert_m7_r12_1_f4-3-2-1.txt
python3 -I -B /mnt/c/tmp/opus55/floor-freeze-verify/scripts/make_faults.py $S $O
for f in F1_one_v_doubled F2_t_above_ritz F3_v_swapped_lowM; do
  bash $D/gate_required.sh $O/$f.txt > $O/$f.gate.txt 2>&1; echo "$f rc=$? $(grep '^VERDICT' $O/$f.gate.txt | cut -c1-240)"; grep '^GATE|row_check\|^RITZ' $O/$f.gate.txt | cut -c1-200; tail -1 $O/$f.gate.txt | cut -c1-40
done
