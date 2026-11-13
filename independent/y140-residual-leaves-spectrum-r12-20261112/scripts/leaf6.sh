#!/bin/bash
# canonical row text of the matrix at m0 = 8 and 9 (r = 12), and the header line of every three-word certificate
W=/root/ymleaf; D=/mnt/c/tmp/opus55/ym-residual-rooms/data
for m in 8 9; do
  c=$W/T$m/RUN$m/cert_m${m}_r12_1_f6-5-4-3.txt
  ROWSOUT=$W/ROWS_m$m.txt python3 -I -B $W/cert_gate_rows.py $c > $W/ROWS_m$m.out 2>&1
  echo "m0=$m $(grep '^ROWHASH' $W/ROWS_m$m.out | cut -c1-110) text_sha256=$(sha256sum $W/ROWS_m$m.txt | cut -d' ' -f1) bytes=$(stat -c %s $W/ROWS_m$m.txt)"
  cp $W/ROWS_m$m.txt $D/
done
cp $W/R_cert_m7_r12_1_f1.rows.txt $D/ROWS_m7.txt
for m in 7 8 9; do for c in $W/T$m/RUN$m/cert_*.txt; do head -1 $c > $D/H_$(basename $c .txt).header.txt; done; done
ls $D | grep -c header
