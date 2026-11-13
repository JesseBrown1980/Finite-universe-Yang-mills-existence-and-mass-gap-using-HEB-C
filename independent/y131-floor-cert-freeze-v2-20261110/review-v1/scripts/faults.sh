#!/bin/bash
set -u
R=/tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/floor
D=$R/work/design
O=$R/work/verify_opus55/faults
mkdir -p $O
S=$R/work/verify_opus55/smoke/cert_m7_r12_1_f4-3-2-1.txt
python3 -I -B /mnt/c/tmp/opus55/floor-freeze-verify/scripts/make_faults.py $S $O
for f in F1_one_v_doubled F2_t_above_ritz F3_v_swapped_lowM; do
  bash $D/gate_required.sh $O/$f.txt > $O/$f.gate.txt 2>&1; echo "$f rc=$? $(grep '^VERDICT' $O/$f.gate.txt | cut -c1-220)"; tail -1 $O/$f.gate.txt | cut -c1-60
done
# F4: tampered verifier at the pinned path: the two-step Schur term dropped (rhs never grows)
cp $D/py/cert_gate.py $O/cert_gate.orig.py
sed 's/rhs += -(-(sk \* rdtd \* rdtd \* fk) \/\/ N)/rhs += 0/' $O/cert_gate.orig.py > $O/cert_gate.tampered.py
diff $O/cert_gate.orig.py $O/cert_gate.tampered.py | head -4
cp $O/cert_gate.tampered.py $D/py/cert_gate.py
bash $D/gate_required.sh $O/F2_t_above_ritz.txt > $O/F4_gate_with_tampered_verifier.txt 2>&1; echo "F4 gate_required rc=$? $(cut -c1-160 $O/F4_gate_with_tampered_verifier.txt | head -1)"
python3 -I -B $O/cert_gate.tampered.py $O/F2_t_above_ritz.txt > $O/F4_tampered_direct.txt 2>&1; echo "F4 tampered verifier run directly rc=$? $(grep '^VERDICT' $O/F4_tampered_direct.txt | cut -c1-160)"
cp $O/cert_gate.orig.py $D/py/cert_gate.py
sha256sum $D/py/cert_gate.py
