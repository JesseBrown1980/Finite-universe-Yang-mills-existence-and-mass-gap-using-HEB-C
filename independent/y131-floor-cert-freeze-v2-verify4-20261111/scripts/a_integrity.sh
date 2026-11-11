set -u
cd /root/floor-v4-verify/repoB
F=independent/y131-floor-cert-freeze-v2-20261110; R=$F/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
echo "HEAD=$(git rev-parse HEAD) status_lines=$(git status --porcelain --untracked-files=no | wc -l) untracked=$(git status --porcelain | wc -l)"
git ls-remote https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C.git refs/heads/local-opus55-floor-cert-freeze-v2-20261110
( cd $F && sha256sum -c FREEZE-PIN.sha256 > /root/floor-v4-verify/pincheck.txt 2>&1; echo "pin_c_exit=$? lines=$(wc -l < FREEZE-PIN.sha256) ok=$(grep -c ': OK$' /root/floor-v4-verify/pincheck.txt) notok=$(grep -vc ': OK$' /root/floor-v4-verify/pincheck.txt)" )
echo "record_sha=$(sha256sum $R | cut -d' ' -f1)"
grep -o '[0-9a-f]\{64\}' $F/FREEZE-PIN.txt | sort -u | grep -c "$(sha256sum $R | cut -d' ' -f1)"
git show 78c89c312a265fe4090071fc1abdc7d6eb102e7e:$R > /root/floor-v4-verify/rec_78c.hbp
echo "rec78c_sha=$(sha256sum /root/floor-v4-verify/rec_78c.hbp | cut -d' ' -f1)"
python3 -I - $R /root/floor-v4-verify/rec_78c.hbp <<'PY'
import sys,re
def rows(p):
    d={}; hdr=[]; dup=0
    for l in open(p,'rb').read().split(b'\n'):
        m=re.match(rb'^([A-Z_]+)\|id=([0-9]{3})\|',l)
        if m:
            k=m.group(2).decode()
            if k in d: dup+=1
            d[k]=(m.group(1).decode(),l)
        else: hdr.append(l)
    return d,hdr,dup
a,ha,da=rows(sys.argv[1]); b,hb,db=rows(sys.argv[2])
want=[ "%03d"%i for i in list(range(1,114))+list(range(116,131))]
same=sum(1 for k in want if k in a and k in b and a[k][1]==b[k][1])
diff=[k for k in want if not (k in a and k in b and a[k][1]==b[k][1])]
pa=[k for k in a if a[k][0]=='PREDICT']; pb=[k for k in b if b[k][0]=='PREDICT']
psame=sum(1 for k in pa if k in b and a[k][1]==b[k][1])
changed=[k for k in sorted(set(a)|set(b)) if a.get(k,(0,None))[1]!=b.get(k,(0,None))[1]]
print("ROWCMP|rows_now=%d|rows_78c=%d|dup_now=%d|dup_78c=%d|checked=%d|same=%d|diff=%s|predict_now=%d|predict_78c=%d|predict_same=%d|predict_ids=%s|all_changed_or_new=%s|header_now=%d|header_78c=%d|json=0"%(len(a),len(b),da,db,len(want),same,"_".join(diff) or "none",len(pa),len(pb),psame,"_".join(sorted(pa)),"_".join(changed),len([h for h in ha if h]),len([h for h in hb if h])))
PY
for f in work/design/rs/src/main.rs work/design/gate_required.sh work/design/py/cert_gate.py work/design/py/indep_verify.py work/design/peak_rss.py work/design/rs/Cargo.lock work/design/rs/Cargo.toml; do
  a=$(sha256sum $F/$f | cut -d' ' -f1); b=$(git show 78c89c312a265fe4090071fc1abdc7d6eb102e7e:$F/$f | sha256sum | cut -d' ' -f1); echo "FILECMP|$f|now=$a|78c=$b|same=$([ $a = $b ] && echo 1 || echo 0)"
done
git diff --stat 78c89c312a265fe4090071fc1abdc7d6eb102e7e 5eecb540431a1b5665605f68ed81bc701719dcd1 | tail -3
git diff --name-only 78c89c312a265fe4090071fc1abdc7d6eb102e7e 5eecb540431a1b5665605f68ed81bc701719dcd1 | grep -v '/review-v4/' 
for id in 114 115 131; do grep "^PIN|id=$id|" $R | sed -n 's/.*|path=\([^|]*\)|value=\([0-9a-f]*\)|.*/\1 \2/p' | while read p v; do echo "PIN$id $p want=$v got=$(sha256sum $F/$p | cut -d' ' -f1)"; done; done
# CR counts
for f in $R $F/final/tools/run_floor.sh $F/final/tools/recheck_floor.py $F/final/tools/floor_eval.py; do echo "CR $f $(tr -cd '\r' < $f | wc -c)"; done
