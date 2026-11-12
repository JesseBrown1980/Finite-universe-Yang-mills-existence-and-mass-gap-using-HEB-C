#!/bin/bash
# 243 leaves = 27 weight words x cutoffs 7, 8, 9 x rehearsal couplings 21/2, 12, 14 (3x4 S3 lattice).
# Certificates are written by the pin-free floorcert binary (its own r policy refuses anything within 1 of 9);
# leaves are extracted by the scratch copy of the pinned verifier, which also re-verifies every certificate.
# Nothing at r = 9. --launch-r9 does not exist here.
BIN=/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/work/design/rs/target/release/floorcert
W=/root/ymleaf; X=$W/X; D=/mnt/c/tmp/opus55/ym-residual-rooms/data243
WORDS='1;3,2,1;4,3,2;4,3,2,1;5,4,3,2;6,5,4,3;7,6,5,4;8,7,6,5;9,8,7,6;10,9,8,7;11,10,9,8;12,11,10,9;5,4,3,2,1;6,5,4,3,2;7,6,5,4,3;8,7,6,5,4;9,8,7,6,5;10,9,8,7,6;11,10,9,8,7;12,11,10,9,8;6,5,4,3,2,1;7,6,5,4,3,2;8,7,6,5,4,3;9,8,7,6,5,4;10,9,8,7,6,5;11,10,9,8,7,6;12,11,10,9,8,7'
mkdir -p $X $D
sha256sum $BIN | cut -c1-64
for m in 7 8 9; do
  mkdir -p $X/m$m
  ( cd $X/m$m && $BIN cert --m0 $m --r 21/2,12,14 --f "$WORDS" --write-cert --threads 4 --dir $X/m$m > $X/m$m.cert.log 2>&1 ); echo "m0=$m cert_exit=$? certificates=$(ls $X/m$m/cert_*.txt 2>/dev/null | wc -l)"
done
one() { c=$1; b=X_$(basename $c .txt); python3 -I -B /root/ymleaf/cert_gate_leaf.py $c > /root/ymleaf/X/$b.out 2>&1; grep '^LEAF|' /root/ymleaf/X/$b.out > /root/ymleaf/X/$b.leaf.hbp; echo "$b $(grep -c . /root/ymleaf/X/$b.leaf.hbp) $(tail -1 /root/ymleaf/X/$b.out | cut -c1-58)"; }
export -f one
ls $X/m7/cert_*.txt $X/m8/cert_*.txt $X/m9/cert_*.txt | xargs -P 5 -I{} bash -c 'one {}' > $X/leaves.log 2>&1
cp $X/X_*.leaf.hbp $D/
for m in 7 8 9; do for c in $X/m$m/cert_*.txt; do head -1 $c > $D/XH_$(basename $c .txt).header.txt; done; done
echo "leaves=$(ls $D/X_*.leaf.hbp | wc -l) pass=$(grep -c 'VERDICT|PASS' $X/leaves.log) refuse=$(grep -c 'REFUSE' $X/leaves.log)"
echo done > $W/expand243.done
