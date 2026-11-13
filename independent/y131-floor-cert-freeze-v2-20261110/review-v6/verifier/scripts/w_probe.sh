V=/root/floor-v5-verify; P=$V/wprobe; rm -rf $P; mkdir -p $P; cp $V/out/G/D3/RUN7/cert_*.txt $P/
CK=$V/exp0/independent/y131-floor-cert-freeze-v2-20261110
python3 -I /mnt/c/tmp/opus55/floor-v2-verify5/scripts/weaken.py $P/cert_m7_r14_1_f4-3-2-1.txt vfrom $P/cert_m7_r14_1_f1.txt 1022056/10000
cd $CK && bash --noprofile --norc work/design/gate_required.sh $P/cert_m7_r14_1_f4-3-2-1.txt > $P/g.txt 2>&1; echo "gate_exit=$?"; grep -E '^(VERDICT|RITZ|GATE_REQUIRED|GATE\|row_check|MEM)' $P/g.txt | cut -c1-220
