#!/bin/bash
# scratch variant of the writer: sweep order and inner count switchable by environment; r = 12 only
export PATH=/root/.cargo/bin:$PATH
SRC=/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/work/design/rs
W=/root/ymleaf/gsvar
rm -rf $W; mkdir -p $W; cp -r $SRC/src $SRC/Cargo.toml $W/; [ -f $SRC/Cargo.lock ] && cp $SRC/Cargo.lock $W/
python3 -I - <<'PY'
p="/root/ymleaf/gsvar/src/main.rs"; s=open(p).read()
a="    let inner = 8usize;\n"; assert s.count(a)==1
s=s.replace(a,"    let inner: usize = std::env::var(\"GS_INNER\").ok().and_then(|x| x.parse().ok()).unwrap_or(8);\n    let rev = std::env::var(\"GS_ORDER\").map(|x| x == \"rev\").unwrap_or(false);\n    let order: Vec<usize> = if rev { (0..n).rev().collect() } else { (0..n).collect() };\n")
a="        for _ in 0..inner {\n            for a in 0..n {\n"; assert s.count(a)==1
s=s.replace(a,"        for _ in 0..inner {\n            for &a in order.iter() {\n")
open(p,"w").write(s)
PY
cd $W && cargo +1.81 build --release 2>&1 | tail -2
BIN=$W/target/release/floorcert; ls -l $BIN | cut -c1-80
run() { tag=$1; ord=$2; inn=$3; m=$4; d=$W/$tag; mkdir -p $d; ( cd $d && GS_ORDER=$ord GS_INNER=$inn $BIN cert --m0 $m --r 12 --f "6,5,4,3" --write-cert --threads 4 --dir $d > $d/log.txt 2>&1 ); c=$(ls $d/cert_*.txt 2>/dev/null | head -1); [ -f "$c" ] || { echo "$tag NO_CERT $(tail -1 $d/log.txt | cut -c1-150)"; return; }
  python3 -I -B /root/ymleaf/cert_gate_leaf.py $c > $d/gate.out 2>&1; grep '^LEAF|' $d/gate.out > /mnt/c/tmp/opus55/ym-residual-rooms/data/V22_${tag}.leaf.hbp; head -1 $c > /mnt/c/tmp/opus55/ym-residual-rooms/data/V22_${tag}.header.txt; echo "$tag leaves=$(grep -c . /mnt/c/tmp/opus55/ym-residual-rooms/data/V22_${tag}.leaf.hbp) $(tail -1 $d/gate.out | cut -c1-90)"; }
for m in 7 8 9; do run fwd8_m$m fwd 8 $m; run rev8_m$m rev 8 $m; run fwd64_m$m fwd 64 $m; done
echo done > $W/done
