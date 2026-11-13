#!/bin/bash
set -u
R=/tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/floor
FB=$R/work/design/rs/target/release/floorcert
O=$R/work/verify_opus55/plants_m6
cd $R/work/design
/usr/bin/time -v $FB cert --m0 6 --r 21/2 --f '4,3,2,1' --write-cert --plant all --ub 993765/10000 --threads 2 --dir $O > $O/writer.txt 2>$O/writer.time; echo rc=$?
cd $O && for f in cert_*.txt; do echo "$(sha256sum $f | cut -c1-16) $f"; done > hashes.txt
cat hashes.txt
for f in cert_*.txt; do bash $R/work/design/gate_required.sh $O/$f > $O/$f.gate.txt 2>&1; echo "$? $(grep '^VERDICT' $O/$f.gate.txt | cut -c1-150)  $f"; done
