N=/root/floor-v6-verify/neg
for i in G_D4 G_U2 X15 X15t X15a X02c X06d N03 X02b X04b X07b X08 X11b; do echo "== $i: $(tail -1 $N/$i.chk.txt | cut -c1-600)"; done
R=/root/floor-v6-verify/repoE/independent/y131-floor-cert-freeze-v2-20261110/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
grep -E '^[A-Z_]+\|id=144\|' $R | tr '|' '\n' | fold -w 300
