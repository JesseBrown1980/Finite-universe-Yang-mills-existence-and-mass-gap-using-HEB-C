#!/bin/bash
# Pass B rebuild into the 300G Host8 store, sectors 341..374 (operator direction 2026-10-28: "D inside the 300 gigabyte store").
R=/d/ym-3x4-room-run/d300; S=/d/ASOLARIA-HOST8-ROOMS-300G; Y=/c/Users/acer/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/native/ym/target/release/ymroom.exe
L=$R/LEDGER.hbp
SEAL0=$(sha256sum $S/ROOMS-MAKE.hbp | cut -c1-64)
echo "LEDGER|run=ym-3x4-room-backed-d300|seat=ACER-CLAUDE-FABLE5|pid=8467a937cba309f7|date=$(date -Iseconds)|operator_direction=D_inside_300G_store;overwrite_sectors_keep_seal|json=0" > $L
echo "OVERWRITE|store=D:/ASOLARIA-HOST8-ROOMS-300G|sectors=341..374|count=34|seglen=800000000|capacity=27200000000|seal=ROOMS-MAKE.hbp|seal_sha256=$SEAL0|seal_touched=0|regenerate=host8rooms.exe_make_seed16=518bbb472a9db786(stub=mix(word^seed))|json=0" >> $L
for k in $(seq 341 374); do echo "PRIOR|sector=$k|sha256=$(sha256sum $S/sector-$k.rooms | cut -c1-64)|json=0" >> $L; done
echo "PRIOR_DONE|t=$(date -Iseconds)|json=0" >> $L
for k in $(seq 341 374); do attrib.exe -R "D:\ASOLARIA-HOST8-ROOMS-300G\sector-$k.rooms"; done
WORKERS=8 MSYS_NO_PATHCONV=1 $Y build 3 4 D:/ym-3x4-room-run/passA.bin D:/asolaria-rooms-1m-50000000/stubs.hbi "seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-" 0 > $R/BUILD.hbp 2> $R/build.err &
BP=$!
sleep 20; powershell.exe -NoProfile -File 'D:\ym-3x4-room-run\d300\peakmem.ps1' &
wait $BP; EC=$?
wait
echo "BUILD_EXIT|exit=$EC|t=$(date -Iseconds)|json=0" >> $L
for k in $(seq 341 374); do attrib.exe +R "D:\ASOLARIA-HOST8-ROOMS-300G\sector-$k.rooms"; done
SEAL1=$(sha256sum $S/ROOMS-MAKE.hbp | cut -c1-64)
echo "SEAL_CHECK|before=$SEAL0|after=$SEAL1|unchanged=$([ "$SEAL0" = "$SEAL1" ] && echo 1 || echo 0)|json=0" >> $L
cat $R/BUILD.hbp; tail -3 $L
