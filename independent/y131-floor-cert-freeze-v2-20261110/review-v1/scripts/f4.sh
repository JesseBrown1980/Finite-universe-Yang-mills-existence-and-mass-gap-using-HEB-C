#!/bin/bash
set -u
R=/tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/floor
D=$R/work/design
O=$R/work/verify_opus55/faults
cp $D/py/cert_gate.py $O/cert_gate.orig.py
sed 's/rhs += -(-(sk \* rdtd \* rdtd \* fk) \/\/ N)/rhs += 0/' $O/cert_gate.orig.py > $O/cert_gate.tampered.py
diff $O/cert_gate.orig.py $O/cert_gate.tampered.py
cp $O/cert_gate.tampered.py $D/py/cert_gate.py
bash $D/gate_required.sh $O/F2_t_above_ritz.txt > $O/F4_gate.txt 2>&1; echo "F4 gate_required rc=$? $(head -1 $O/F4_gate.txt | cut -c1-200)"
cp $O/cert_gate.orig.py $D/py/cert_gate.py
sha256sum $D/py/cert_gate.py
python3 -I -B $O/cert_gate.tampered.py $O/F2_t_above_ritz.txt > $O/F4_direct.txt 2>&1; echo "tampered direct rc=$? $(grep '^VERDICT' $O/F4_direct.txt | cut -c1-200)"
