#!/bin/bash
# Play certificate: address files + manifests, played vs stored matrices, and the
# end-to-end inertia gate (the same shellschur on both, identical counts,
# ambiguous=0), plus fail-closed negative controls. Integer-only, json=0.
# usage: scripts/play_certificate.sh BIN_DIR WORK CASE...    CASE = LX:LY:SX:SY:CLASSES:T1,T2
set -u
B=$1; W=$2; shift 2
mkdir -p $W; fails=0
P=$B/ymplay; Y=$B/ymsec; S=$B/shellschur
strip(){ tr '|' '\n' | grep -v -e '^matrix=' -e '^ms=' | paste -sd'|'; }
for c in "$@"; do
  IFS=: read -r lx ly sx sy m ts <<< "$c"; id="${lx}x${ly}_${sx}_${sy}"
  st=$($Y $lx $ly $sx $sy $W/$id.stored.m | grep -o 'sector_states=[0-9]*' | cut -d= -f2)
  parts=""; for r in $(seq 0 $((m-1))); do $P keys $lx $ly $sx $sy $r $m $W/$id.k$r.bin > /dev/null || fails=1; parts="$parts $W/$id.k$r.bin"; done
  $P merge $W/$id.addr $parts > /dev/null || fails=1
  $P manifest $lx $ly $sx $sy $W/$id.addr $st $W/$id.manifest > /dev/null || fails=1
  $P matrix $lx $ly $sx $sy $W/$id.addr $W/$id.manifest $W/$id.played.m > /dev/null || fails=1
  same=0; cmp -s $W/$id.played.m $W/$id.stored.m && same=1
  echo "PLAY_MATRIX|case=$id|stored_states=$st|classes=$m|manifest_sha256=$(grep -o 'sha256=[0-9a-f]*' $W/$id.manifest | head -1 | cut -d= -f2)|byte_identical=$same|json=0"
  [ $same = 1 ] || fails=1
  for t in ${ts//,/ }; do
    a=$($S $W/$id.played.m 1000 9000 $t -1 12 1000 4000 | grep '^SHELL_SCHUR|' | strip)
    b=$($S $W/$id.stored.m 1000 9000 $t -1 12 1000 4000 | grep '^SHELL_SCHUR|' | strip)
    ok=0; [ -n "$a" ] && [ "$a" = "$b" ] && echo "$a" | grep -q '|ambiguous=0|result=PASS|' && ok=1
    n=$(echo "$a" | grep -o 'negative=[0-9]*' | head -1)
    echo "PLAY_INERTIA|case=$id|t_milli=$t|played_${n}|stored_$(echo "$b" | grep -o 'negative=[0-9]*' | head -1)|identical_record=$ok|json=0"
    [ $ok = 1 ] || fails=1
  done
  rm -f $W/$id.*.m
done
# negative controls on the first case: every one must exit 2
IFS=: read -r lx ly sx sy m ts <<< "$1"; id="${lx}x${ly}_${sx}_${sy}"
neg(){ label=$1; shift; "$@" > $W/neg.out 2>&1; e=$?; ok=0; [ $e = 2 ] && ok=1; echo "PLAY_CONTROL|case=$label|exit=$e|fail_closed=$ok|json=0"; [ $ok = 1 ] || fails=1; }
: > $W/empty.addr; neg empty_file $P matrix $lx $ly $sx $sy $W/empty.addr $W/$id.manifest $W/x.m
head -c -8 $W/$id.addr > $W/short.addr; neg minus_8_bytes $P matrix $lx $ly $sx $sy $W/short.addr $W/$id.manifest $W/x.m
if [ $m -gt 1 ]; then $P merge $W/missing.addr $(ls $W/$id.k*.bin | tail -n +2) > /dev/null; neg missing_residue_class $P matrix $lx $ly $sx $sy $W/missing.addr $W/$id.manifest $W/x.m; fi
neg wrong_scope $P matrix $lx $ly $sx $((-sy)) $W/$id.addr $W/$id.manifest $W/x.m
sed 's/|states=\([0-9]*\)|/|states=9\1|/' $W/$id.manifest > $W/wrongcount.manifest; neg wrong_expected_count $P matrix $lx $ly $sx $sy $W/$id.addr $W/wrongcount.manifest $W/x.m
neg manifest_refuses_wrong_count $P manifest $lx $ly $sx $sy $W/$id.addr 1 $W/x.manifest
sed 's/|sha256=[0-9a-f]*|/|sha256=0000000000000000000000000000000000000000000000000000000000000000|/' $W/$id.manifest > $W/wrongdigest.manifest; neg wrong_digest $P matrix $lx $ly $sx $sy $W/$id.addr $W/wrongdigest.manifest $W/x.m
python3 -c "import sys; b=bytearray(open(sys.argv[1],'rb').read()); b[8]^=1; open(sys.argv[2],'wb').write(b)" $W/$id.addr $W/flip.addr
cmp -s $W/$id.addr $W/flip.addr && { echo "PLAY_CONTROL|case=flipped_byte|error=file_unchanged|json=0"; fails=1; }
neg flipped_byte $P matrix $lx $ly $sx $sy $W/flip.addr $W/$id.manifest $W/x.m
neg row_out_of_range $P row $lx $ly $sx $sy $W/$id.addr $W/$id.manifest 999999999
echo "PLAY_CERTIFICATE|cases=$#|result=$([ $fails = 0 ] && echo PASS || echo FAIL)|json=0"
exit $fails
