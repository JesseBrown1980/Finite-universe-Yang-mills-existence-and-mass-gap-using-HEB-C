A=/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-v2-20261110/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
python3 -I /mnt/c/tmp/opus55/floor-v2-verify/scripts/rows.py $A 070 basis
grep '^PREDICTION_END' $A
python3 -I - $A <<'PY'
import re,sys,collections
c=collections.Counter(); t=collections.Counter()
for l in open(sys.argv[1]):
    m=re.match(r'^([A-Z_]+)\|id=',l)
    if m:
        c[m.group(1)]+=1
        tg=re.search(r'\|tag=([A-Z_]+)\|',l); t[tg.group(1) if tg else 'NONE']+=1
print(dict(c),dict(t))
PY
python3 -I /mnt/c/tmp/opus55/floor-v2-verify/scripts/rows.py $A 110,111,112,113,114,115,116,117,118 | cut -c1-2500
