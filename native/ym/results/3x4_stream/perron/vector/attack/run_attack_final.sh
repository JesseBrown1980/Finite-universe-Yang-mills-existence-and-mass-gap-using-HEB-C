#!/bin/bash
# The controls, the sabotages and the four main rows of the attack on the hybrid certificate. Each row's prediction is at vector/attack/HYBRID-ATTACK-PREDICTION.hbp. Below normal priority, 3 threads.
export MSYS_NO_PATHCONV=1
cd C:/tmp/ym-hybrid-attack || exit 9
X=./hybridcheck.exe
L=ATTACK-RUNS-FINAL-BUILD.hbp
run() { local tag=$1; shift; local t0=$(date +%s); "$X" "$@" > "final.$tag" 2> "finalerr.$tag"; local c=$?; printf 'RUN|tag=%s|exit=%d|wall_secs=%d|at=%s|json=0\n' "$tag" "$c" "$(( $(date +%s) - t0 ))" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$L"; cat "final.$tag" "finalerr.$tag" >> "$L"; }
printf 'ATTACK_EXTRA_PREDICTION|at=%s|file=tmp/hyb_3x3_full.hybrid|cut=27|every_orbit_exact=1|cert_micro=76443824|rows_past_cut=0|configs_at_most_cut=60466158|json=0\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$L"
run c3x3_m13 check 3 3 9 13 in/hyb_3x3_r9_m13.hybrid in/local-3x3.hbp 76359153 3
run c3x3_full check 3 3 9 27 in/hyb_3x3_full.hybrid in/local-3x3.hbp 76443824 3
run c3x4_m14 check 3 4 9 14 in/hyb_3x4_r9_m14.hybrid in/local-3x4.hbp 94011545 3
run red_4x4_m12 check 4 4 9 12 in/hyb_4x4_r9_m12.hybrid in/local-4x4.hbp 117345755 3
run red_3x4_m12 check 3 4 9 12 in/hyb_3x4_m12.hybrid in/local-3x4.hbp 93829570 3
run t_claim check 4 4 9 10 in/hyb_4x4_r9_m10.hybrid in/local-4x4.hbp 115534180 3
run t_lower_one check 4 4 9 10 in/hyb_4x4_r9_m10.hybrid in/local-4x4.hbp 115534179 3 sabotage=lower_one
run t_drop_one check 4 4 9 10 in/hyb_4x4_r9_m10.hybrid in/local-4x4.hbp 115534179 3 sabotage=drop_one
run t_wrong_m check 4 4 9 10 in/hyb_4x4_r9_m10.hybrid in/local-4x4.hbp 115534179 3 sabotage=wrong_m
run t_nonzero_flat check 4 4 9 10 in/hyb_4x4_r9_m10.hybrid in/local-4x4.hbp 115534179 3 sabotage=nonzero_flat
run m4x4_r9 check 4 4 9 14 in/hyb_4x4_r9_m14.hybrid in/local-4x4.hbp 117453728 3
run m4x4_r6 check 4 4 6 14 in/hyb_4x4_r6_m14.hybrid in/local-4x4.hbp 103521056 3
run m4x5_r9 check 4 5 9 13 in/hyb_4x5_r9_m13.hybrid in/local-4x5.hbp 140546984 3
run m5x5_r9 check 5 5 9 11 in/hyb_5x5_r9_m11.hybrid in/local-5x5.hbp 168020667 3
printf 'ATTACK_DONE|at=%s|json=0\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$L"
T=C:/tmp/ym-vector-target/release
C=D:/ym-3x4-room-run/p0-ball/c33
for row in "13 in/hyb_3x3_r9_m13.hybrid d-3x3-m13.bin" "27 in/hyb_3x3_full.hybrid d-3x3-full.bin"; do
  set -- $row
  ./hybridcheck.exe write $C/p33.bin 3 3 "$1" "$2" "final-$3" >> "$L"
  "$T/perroncert.exe" check $C/dev33.bin 0 1000 9000 "final-$3" 2>&1 | sed "s/^/STORE_CHECK|cut=$1|/" >> "$L"
done
printf 'FINAL_BUILD_DONE|at=%s|hybridcheck_sha256=%s|json=0\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(sha256sum hybridcheck.exe | cut -c1-64)" >> "$L"
