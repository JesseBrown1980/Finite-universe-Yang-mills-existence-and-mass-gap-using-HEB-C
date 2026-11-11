D=/root/floor-v2-final/head/independent/y131-floor-cert-freeze-v2-20261110/review-v2/rehearsal-v2b
for n in R1 R2 R3 A1 C2 C4; do echo "== $n"; grep -E '^(STEP|DECISION|BYST)' $D/$n.stdout.txt | grep -oE '^(STEP\|m0=[0-9]+\|status=[A-Z]+)|writer_peak_kB=[0-9]+|verifier_mem_max_kB=[0-9]+|resource_limit=[A-Z]+|next=[A-Z]+|bad=[^|]{0,160}' | tr '\n' ' '; echo; tail -1 $D/$n.stdout.txt | cut -c1-260; grep -h 'elapsed' $D/$n.FLOOR-RUN-RECEIPT.hbp | grep -oE 'm0=[0-9]+\|kind=[a-z]+|elapsed_s=[0-9]+' | tr '\n' ' '; echo; done
cat $D/C2.bystander.txt $D/C4.bystander.txt
grep -n 'PREREQ\|rowsonly' /root/floor-v2-final/head/independent/y131-floor-cert-freeze-v2-20261110/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp | cut -c1-120
