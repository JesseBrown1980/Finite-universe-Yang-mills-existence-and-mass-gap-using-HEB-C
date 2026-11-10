#!/bin/bash
set -u
export PATH=$HOME/.cargo/bin:$PATH
R=/root/floor-v2/repo
P=$R/independent/y131-floor-cert-freeze-v2-20261110
W=/root/floor-v2
# 1. pin-free rebuild in a separate target dir
rm -rf $W/repro_target
cd $P/work/design/rs
env -u FLOORCERT_FREEZE_COMMIT -u FLOORCERT_PREDICTION_SHA256 CARGO_TARGET_DIR=$W/repro_target cargo +1.81 build --release --locked -j1 > $W/repro_build.log 2>&1; echo "repro_rc=$?"
echo "rebuilt=$(sha256sum $W/repro_target/release/floorcert | cut -d' ' -f1)"
echo "pinned=$(sha256sum target/release/floorcert | cut -d' ' -f1)"
rustc +1.81 --version; cargo +1.81 --version
grep -c warning $W/repro_build.log
# 2. tamper test on a copy of work/design (the script takes D from its own location)
rm -rf $W/tamper; mkdir -p $W/tamper/design/py
cp $P/work/design/gate_required.sh $W/tamper/design/; cp $P/work/design/py/*.py $W/tamper/design/py/
C=$W/reg/smoke/cert_m7_r12_1_f4-3-2-1.txt
bash $W/tamper/design/gate_required.sh $C > $W/tamper/untampered.txt 2>&1; echo "copy_untampered_rc=$? $(tail -1 $W/tamper/untampered.txt | cut -c1-80)"
sed -i 's/rhs += -(-(sk \* rdtd \* rdtd \* fk) \/\/ N)/rhs += 0/' $W/tamper/design/py/cert_gate.py
echo "tampered_sha=$(sha256sum $W/tamper/design/py/cert_gate.py | cut -d' ' -f1)"
bash $W/tamper/design/gate_required.sh $C > $W/tamper/tampered.txt 2>&1; echo "copy_tampered_rc=$?"; cat $W/tamper/tampered.txt | cut -c1-400
echo "package_cert_gate_sha=$(sha256sum $P/work/design/py/cert_gate.py | cut -d' ' -f1)"
# 3. ../ym137 pin of row 034: is the file in the #137 freeze branch
cd $R
for ref in refs/remotes/github/cloud-seat-137-amplitude-freeze-20261109; do
  git ls-tree -r --name-only $ref | grep -F 'PREDICT-S3-3X4-R9-WILSON-FESHBACH-AMPLITUDE-20261109.hbp' | while read f; do echo "$ref $f $(git cat-file blob $ref:$f | sha256sum | cut -d' ' -f1)"; done
  git rev-parse $ref
done
# 4. NOTE/CHANGES mentions
cd $P
grep -n 'scratchpad\|7824ed78\|0432b826\|13a92ab7\|9ea61588\|403336' final/NOTE-S3-3X4-R9-FLOOR-CERT-20261109.md final/CHANGES.txt work/design/NOTE.md work/map/MAP.md | cut -c1-220
python3 /mnt/c/tmp/opus55/floor-v2/rows.py 105 | grep -o '.\{300\}403336.\{200\}'
ls -la $W/reg/smoke $W/reg/RUN11 | head -30
