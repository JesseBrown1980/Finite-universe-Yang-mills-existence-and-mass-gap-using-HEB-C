#!/bin/bash
set -u
R=/tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/floor
if [ -e "$R" ]; then echo "EXISTS $R"; ls -la "$R"; exit 1; fi
mkdir -p "$R"
cp -r /mnt/c/tmp/opus55/floor-freeze-verify/repo/independent/y131-floor-cert-freeze-20261110/work "$R/work"
cp -r /mnt/c/tmp/opus55/floor-freeze-verify/repo/independent/y131-floor-cert-freeze-20261110/final "$R/final"
cp /mnt/c/tmp/opus55/floor-freeze-verify/repo/independent/y131-floor-cert-freeze-20261110/FREEZE-PIN.sha256 "$R/"
cd "$R" && sha256sum -c FREEZE-PIN.sha256 | grep -c ': OK'
mkdir -p "$R/work/design/rs/target/release"
cp /tmp/opus55ffv/tgt1/release/floorcert "$R/work/design/rs/target/release/floorcert"
sha256sum "$R/work/design/rs/target/release/floorcert"
nproc; free -m | head -2; df -h /tmp | tail -1
