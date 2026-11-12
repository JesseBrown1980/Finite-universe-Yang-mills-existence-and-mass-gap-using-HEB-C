set -u
V=/root/floor-v6-verify; cd $V/repoE
F=independent/y131-floor-cert-freeze-v2-20261110; R=$F/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
OLD=3c41ea2d9dd01de0ffcd547a7e7d417baa2ca6c0; NEW=c8dbcdbf990114292313cbc410a745a14ba0b778
echo "HEAD=$(git rev-parse HEAD) tracked_changes=$(git status --porcelain --untracked-files=no | wc -l) untracked=$(git status --porcelain | wc -l)"
echo "remote_branch=$(git ls-remote origin refs/heads/local-opus55-floor-cert-freeze-v2-20261110)"
( cd $F && sha256sum -c FREEZE-PIN.sha256 > $V/pincheck.txt 2>&1; echo "pin_c_exit=$? lines=$(wc -l < FREEZE-PIN.sha256) ok=$(grep -c ': OK$' $V/pincheck.txt) notok=$(grep -vc ': OK$' $V/pincheck.txt)" )
# regenerate FREEZE-PIN: list of files in it vs tracked files of the folder
( cd $F && cut -c67- FREEZE-PIN.sha256 | sort > $V/pin_list.txt; git ls-files . | sort > $V/tracked_list.txt; echo "pin_files=$(wc -l < $V/pin_list.txt) tracked_files_in_folder=$(wc -l < $V/tracked_list.txt)"; comm -3 $V/pin_list.txt $V/tracked_list.txt | head -20 )
( cd $F && git ls-files . | grep -v '^FREEZE-PIN' | LC_ALL=C sort | xargs sha256sum > $V/pin_regen.txt; LC_ALL=C sort -k2 FREEZE-PIN.sha256 > $V/pin_sorted.txt; LC_ALL=C sort -k2 $V/pin_regen.txt > $V/pin_regen_sorted.txt; echo "regen_vs_committed_difflines=$(diff $V/pin_sorted.txt $V/pin_regen_sorted.txt | grep -c '^[<>]')"; diff $V/pin_sorted.txt $V/pin_regen_sorted.txt | head )
echo "FREEZE-PIN.sha256 sidecar: $(cat $F/FREEZE-PIN.txt | head -0)"; ls $F/FREEZE-PIN*; grep -c . $F/FREEZE-PIN.sha256
RS=$(sha256sum $R | cut -d' ' -f1); echo "record_sha=$RS"
for f in $F/FREEZE-PIN.txt $F/final/NOTE-S3-3X4-R9-FLOOR-CERT-20261109.md $F/final/CHANGES.txt; do echo "record_hash_mentions $f: $(grep -c $RS $f)"; grep -o '[0-9a-f]\{64\}' $f | sort -u > $V/h_$(basename $f).txt; done
# tool hashes in record pin rows vs files
python3 -I - $R $F <<'PY'
import sys,re,hashlib,os
rec,F=sys.argv[1],sys.argv[2]
for l in open(rec,encoding='utf-8').read().split('\n'):
    m=re.match(r'^PIN\|id=([0-9]{3})\|',l)
    if not m: continue
    d=dict(w.split('=',1) for w in l.split('|') if '=' in w)
    p=d.get('path',''); v=d.get('value','')
    fp=os.path.join(F,p)
    got=hashlib.sha256(open(fp,'rb').read()).hexdigest() if os.path.isfile(fp) else 'ABSENT'
    print("PIN|id=%s|path=%s|want=%s|got=%s|ok=%d"%(m.group(1),p,v[:16],got[:16],1 if got==v else 0))
PY
# hashes named in NOTE/CHANGES for the tools
for t in final/tools/run_floor.sh final/tools/floor_eval.py final/tools/recheck_floor.py final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp; do s=$(sha256sum $F/$t | cut -d' ' -f1); echo "TOOLHASH|$t|$s|in_NOTE=$(grep -c $s $F/final/NOTE-S3-3X4-R9-FLOOR-CERT-20261109.md)|in_CHANGES=$(grep -c $s $F/final/CHANGES.txt)|in_FREEZEPINTXT=$(grep -c $s $F/FREEZE-PIN.txt)|in_record=$(grep -c $s $R)"; done
# all 64-hex in NOTE/CHANGES that look like tool hashes: list them with whether they match any tracked file
for f in $F/final/NOTE-S3-3X4-R9-FLOOR-CERT-20261109.md $F/final/CHANGES.txt; do for h in $(grep -o '[0-9a-f]\{64\}' $f | sort -u); do m=$(grep -l "^$h " $F/FREEZE-PIN.sha256 >/dev/null && grep "^$h " $F/FREEZE-PIN.sha256 | head -1 | cut -c67-); echo "HEX|$(basename $f)|$h|matches_pin_file=${m:-none}"; done; done
# byte-identity to OLD
for f in work/design/rs/src/main.rs work/design/gate_required.sh work/design/py/cert_gate.py work/design/py/indep_verify.py work/design/peak_rss.py work/design/rs/Cargo.lock work/design/rs/Cargo.toml final/tools/freeze_args_controls.sh final/tools/floor_eval.py; do
  a=$(git show $NEW:$F/$f | sha256sum | cut -d' ' -f1); b=$(git show $OLD:$F/$f | sha256sum | cut -d' ' -f1); echo "FILECMP|$f|same=$([ $a = $b ] && echo 1 || echo 0)|$a"
done
git show $OLD:$R > $V/rec_old.hbp
python3 -I - $R $V/rec_old.hbp <<'PY'
import sys,re
def rows(p):
    d={}; dup=0
    for l in open(p,'rb').read().split(b'\n'):
        m=re.match(rb'^([A-Z_]+)\|id=([0-9]{3})\|',l)
        if m:
            k=m.group(2).decode()
            if k in d: dup+=1
            d[k]=(m.group(1).decode(),l)
    return d,dup
a,da=rows(sys.argv[1]); b,db=rows(sys.argv[2])
pa=sorted(k for k in a if a[k][0]=='PREDICT'); pb=sorted(k for k in b if b[k][0]=='PREDICT')
print("PREDICT|now=%d|old=%d|same=%d|ids=%s"%(len(pa),len(pb),sum(1 for k in pa if k in b and a[k][1]==b[k][1]),"_".join(pa)))
ch=[k for k in sorted(set(a)|set(b)) if a.get(k,(0,None))[1]!=b.get(k,(0,None))[1]]
print("ROWCMP|rows_now=%d|rows_old=%d|dup=%d,%d|changed_or_new=%s"%(len(a),len(b),da,db,"_".join(ch)))
PY
echo "files_changed_outside_folder=$(git diff --name-only $OLD $NEW | grep -vc "^$F/")"
echo "CR introduced:"; git diff --name-only $OLD $NEW | while read f; do n=$(git show $NEW:"$f" | tr -cd '\r' | wc -c); o=$(git show $OLD:"$f" 2>/dev/null | tr -cd '\r' | wc -c); [ "$n" != 0 ] && echo "CR|$f|new=$n|old=$o"; done; echo "CR_scan_done"
python3 -I -X utf8 native/scripts/no_float_gate.py . > $V/nofloat.txt 2>&1; echo "nofloat_exit=$?"; tail -3 $V/nofloat.txt
