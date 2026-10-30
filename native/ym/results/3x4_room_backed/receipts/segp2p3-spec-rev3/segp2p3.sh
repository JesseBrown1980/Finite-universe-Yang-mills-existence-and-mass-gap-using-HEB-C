#!/bin/bash
# Segmented-store P2/P3, frozen procedure (SEGP2P3-SPEC revision 3). NOT TO BE RUN WITHOUT OPERATOR APPROVAL.
# Usage: segp2p3.sh <ANCHOR>   ANCHOR = the operator-approved pre-registration seal (64 hex), taken
# from the execution authorization, never from the bundle. The run proceeds only if the recomputed
# bundle seal equals it; the verdict module checks the same equality again, independently.
# Evidence rows -> $L (HBP, json=0). Verdicts derived only by segp2p3_verdict.py from those rows.
# Never deletes anything outside $W; never writes to the operator's checkout or to any room store
# other than the ones it creates under $W.
set -u
ANCHOR=${1:-}
[[ $ANCHOR =~ ^[0-9a-f]{64}$ ]] || { echo "SEGP2P3_ABORT|reason=anchor_missing_or_malformed|json=0"; exit 2; }
SPEC=D:/ym-3x4-room-run/segp2p3-spec; W=D:/ym-3x4-room-run/segp2p3; L=$W/SEGP2P3.hbp
B=C:/Users/acer/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/native/ym/target/release
declare -A EXE=([shellschur]=29b6b55078796ad223b31373f063196a7b3a24a5f2396496b129b96c36542dd3 [roomschur]=a8007c1545a2d8827964fad71a761c1a38744671173bf393f0517e1297434eff [ymroom]=a0bc359d88aca652e5b4ec9e192741d8a1c8c501658e7fd0e33055b410c12cc8 [ymsec]=9fa8232d917892df9c0b071903f258849d40dcd477f984a438fab6a561168607)
declare -A SEGLEN=([G1]=40000000 [G2]=1048583)
JE=1000; JB=9000; FDIG=12; TOL=1000; MAXSWEEP=4000; K=8; BUDGET=12884901888
THR="60000000:101:2 72000000:1137:16 90000000:2940:40"
sha() { sha256sum "$1" | cut -c1-64; }
row() { echo "$1|json=0" >> $L; }
ok_exe() { local b; for b in shellschur roomschur ymroom ymsec; do [ "$(sha $B/$b.exe)" = "${EXE[$b]}" ] || return 1; done; }
# logical store bytes of a segmented store: files in index order, first N bytes
segcat() { local d=$1 n=$2 c=$3 i; for i in $(seq 1 $c); do cat "$d/sector-$(printf %03d $i).rooms"; done | head -c $n; }
# every segment present, exactly seglen bytes, and fully readable (0/1); a read failure is never a MISMATCH
segread() { local d=$1 c=$2 s=$3 i f; for i in $(seq 1 $c); do f=$d/sector-$(printf %03d $i).rooms; [ -f $f ] && [ "$(stat -c%s $f)" = "$s" ] && cat $f > /dev/null || { echo 0; return; }; done; echo 1; }
# verdict rows (CR stripped) appended after evidence; sidecar written with the bare file name
verdict() { python -I $SPEC/segp2p3_verdict.py $L $W $SPEC $ANCHOR | tr -d '\r' > $W/verdict.tmp; cat $W/verdict.tmp >> $L; (cd $W && sha256sum SEGP2P3.hbp | sed 's/  / */' > SEGP2P3.hbp.sha256); }
total() { tr -d '\r' < $1 | tail -1; }

# ---- step 0: preconditions -------------------------------------------------------------
[ -e $W ] && { echo "SEGP2P3_ABORT|reason=run_dir_exists|json=0"; exit 3; }
mkdir -p $W; cd $W || exit 3
pre=1
(cd $SPEC && sha256sum -c --quiet SHA256SUMS) || pre=0
SEAL=$(cat $SPEC/SHA256SUMS $SPEC/SEGP2P3-SPEC.hbi | sha256sum | cut -c1-64)
[ "$SEAL" = "$ANCHOR" ] || pre=0
[ "$(tr -d '\r\n' < $SPEC/SEGP2P3.seal)" = "$ANCHOR" ] || pre=0
ok_exe || pre=0
tasklist.exe | grep -qiE 'shellschur|roomschur|ymroom|ymsec|cargo|rustc' && pre=0
free=$(df -B1 --output=avail /d | tail -1); [ "$free" -ge 20000000000 ] || pre=0
row "PRECONDITIONS|ok=$pre|seal=$SEAL|anchor=$ANCHOR|free_bytes_D=$free|t=$(date -Iseconds)"
[ $pre = 1 ] || { verdict; exit 4; }

# ---- step 1: synthetic controls (comparator equivalence, verdict logic) -------------------
python -I $SPEC/code/schur_record_compare_stream_controls.py --v1-file $SPEC/code/schur_record_compare_v1_9f60d56.py > $W/comparator-controls.hbp
cc=FAIL; [ "$(total $W/comparator-controls.hbp)" = 'STREAM_EQUIV_TOTAL|cases=60|ok=60|result=PASS|json=0' ] && cc=PASS
row "CONTROL_TOTAL|kind=comparator|line=$(total $W/comparator-controls.hbp | tr '|' ';')|file=comparator-controls.hbp|file_sha256=$(sha $W/comparator-controls.hbp)"
python -I $SPEC/segp2p3_verdict_controls.py > $W/verdict-controls.hbp
vc=FAIL; [ "$(total $W/verdict-controls.hbp)" = 'SEGP2P3_CONTROLS_TOTAL|cases=40|ok=40|result=PASS|json=0' ] && vc=PASS
row "CONTROL_TOTAL|kind=verdict|line=$(total $W/verdict-controls.hbp | tr '|' ';')|file=verdict-controls.hbp|file_sha256=$(sha $W/verdict-controls.hbp)"

# ---- step 2: P2 builder identity, per lattice ----------------------------------------------
declare -A MERKLE SIZE
for LAT in 2x3 2x4 3x3; do
  LX=${LAT%x*}; LY=${LAT#*x}; D=$W/p2/$LAT; mkdir -p $D
  $B/ymsec.exe $LX $LY 1 1 $D/ymsec.txt > $D/ymsec.out 2> $D/ymsec.err; e1=$?
  $B/ymroom.exe text $LX $LY $D/ymroom.txt > $D/text.out 2> $D/text.err; e2=$?
  r=0; [ $e1 = 0 ] && [ $e2 = 0 ] && [ -s $D/ymsec.txt ] && [ -s $D/ymroom.txt ] && r=1
  row "P2_TEXT|L=$LAT|runs_ok=$r|ymsec_exit=$e1|ymroom_exit=$e2|ymsec_sha256=$(sha $D/ymsec.txt 2>/dev/null)|ymsec_bytes=$(stat -c%s $D/ymsec.txt 2>/dev/null)|ymroom_sha256=$(sha $D/ymroom.txt 2>/dev/null)|ymroom_bytes=$(stat -c%s $D/ymroom.txt 2>/dev/null)"
  $B/ymroom.exe passa $LX $LY $D/passa.bin > $D/passa.out 2> $D/passa.err
  states=$(( $(stat -c%s $D/passa.bin) / 16 ))
  for G in single G1 G2; do
    truncate -s 0 $D/keys-$G.rooms; truncate -s $((8*states)) $D/keys-$G.rooms
    if [ $G = single ]; then : > $D/single.rooms; DEV=$D/single.rooms
    else
      n=${SIZE[$LAT]}; s=${SEGLEN[$G]}; c=$(( (n + s - 1) / s + 1 )); mkdir -p $D/seg$G
      for i in $(seq 1 $c); do truncate -s $s $D/seg$G/sector-$(printf %03d $i).rooms; done
      DEV="seg:1:$c:$s:$D/seg$G/sector-"; eval "C_$G=$c"
    fi
    $B/ymroom.exe build $LX $LY $D/passa.bin $D/keys-$G.rooms "$DEV" 0 > $D/build-$G.out 2> $D/build-$G.err; e=$?
    h=$(grep '^YMROOMHDR|' $D/build-$G.out); bl=$(grep '^YMROOM_BUILD|' $D/build-$G.out)
    w=$(echo "$h" | grep -o 'w_self_adjoint=[A-Z]*' | cut -d= -f2); hr=$(echo "$bl" | grep -o 'header_readback=[A-Z]*' | cut -d= -f2)
    pm=$(echo "$h" | grep -o 'payload_merkle=[0-9a-f]*' | cut -d= -f2)
    row "P2_BUILD|L=$LAT|geom=$G|exit=$e|w_self_adjoint=$w|header_readback=$hr|hdr_sha256=$(printf '%s' "$h" | sha256sum | cut -c1-64)|payload_merkle=$pm|dev=$DEV"
    if [ $G = single ]; then SIZE[$LAT]=$(stat -c%s $D/single.rooms); MERKLE[$LAT]=$pm; row "P2_SINGLE|L=$LAT|bytes=${SIZE[$LAT]}|store_sha256=$(sha $D/single.rooms)"
    else
      n=${SIZE[$LAT]}; c=$(eval echo \$C_$G); s=${SEGLEN[$G]}
      rd=$(segread $D/seg$G $c $s); [ -s $D/single.rooms ] || rd=0; tl=$(( c * s - n )); pe=NA; tz=NA
      if [ $rd = 1 ]; then
        pe=0; segcat $D/seg$G $n $c | cmp -s - $D/single.rooms && pe=1
        tz=0; for i in $(seq 1 $c); do cat $D/seg$G/sector-$(printf %03d $i).rooms; done | tail -c $tl | cmp -s - <(head -c $tl /dev/zero) && tz=1
      fi
      row "P2_STORE|L=$LAT|geom=$G|read_ok=$rd|files=$c|seglen=$s|prefix_equal_single=$pe|tail_zero=$tz|tail_bytes=$tl"
    fi
  done
done

# ---- step 3: planted segment-integrity controls (2x3 store, control geometry G3) ------------
# 2x3 at t=60M has core 74 (CI pre-run), so ROOMSCHUR_COLS=0:1 is valid; G3 = 16411-byte prime
# segments give many boundaries. G3 is a control geometry only, not part of the P2 verdict.
G3=16411; CD=$W/ctl; mkdir -p $CD/G3; n2=${SIZE[2x3]}; c4=$(( (n2 + G3 - 1) / G3 + 1 ))
for i in $(seq 1 $c4); do truncate -s $G3 $CD/G3/sector-$(printf %03d $i).rooms; done
truncate -s $((8 * $(stat -c%s $W/p2/2x3/passa.bin) / 16)) $CD/keys-G3.rooms
$B/ymroom.exe build 2 3 $W/p2/2x3/passa.bin $CD/keys-G3.rooms "seg:1:$c4:$G3:$CD/G3/sector-" 0 > $CD/build-G3.out 2> $CD/build-G3.err; eg=$?
gp=0; segcat $CD/G3 $n2 $c4 | cmp -s - $W/p2/2x3/single.rooms && gp=1
row "SEG_CONTROL_STORE|L=2x3|geom=G3|seglen=$G3|files=$c4|build_exit=$eg|prefix_equal_single=$gp"
mid=$(( c4 / 2 )); seg=FAIL; kpass=0
kc() { # $1 case, $2 dir, $3 count -> detected (1) when exit not in {0,2}, or no cols line, or merkle != P2 2x3
  local o=$CD/$1.out; ROOMSCHUR_K=$K ROOMSCHUR_BUDGET=$BUDGET ROOMSCHUR_COLS=0:1 $B/roomschur.exe "seg:1:$3:$G3:$2/sector-" 0 $JE $JB 60000000 $FDIG $TOL $MAXSWEEP > $o 2> $CD/$1.err; local e=$?
  local m; m=$(grep '^SHELL_SCHUR_COLS|' $o | grep -o 'payload_merkle=[0-9a-f]*' | cut -d= -f2)
  local det=0; { [ $e != 0 ] && [ $e != 2 ]; } || [ -z "$m" ] || [ "$m" != "${MERKLE[2x3]}" ] && det=1
  echo "$e $det"
}
if [ $eg = 0 ] && [ $gp = 1 ] && [ $c4 -ge 6 ]; then
  for k in K0 K1 K2 K3 K4 K5; do cp -r $CD/G3 $CD/$k; done
  mv $CD/K1/sector-$(printf %03d $mid).rooms $CD/K1.removed
  printf '\xff' | dd of=$CD/K2/sector-$(printf %03d $mid).rooms bs=1 seek=$(( G3 / 2 )) conv=notrunc status=none
  mv $CD/K3/sector-$(printf %03d $mid).rooms $CD/K3/swap.tmp; mv $CD/K3/sector-$(printf %03d $((mid+1))).rooms $CD/K3/sector-$(printf %03d $mid).rooms; mv $CD/K3/swap.tmp $CD/K3/sector-$(printf %03d $((mid+1))).rooms
  truncate -s $(( G3 - 1 )) $CD/K4/sector-$(printf %03d $mid).rooms
  for k in K0 K1 K2 K3 K4 K5; do
    cnt=$c4; [ $k = K5 ] && cnt=$(( c4 - 2 ))
    set -- $(kc $k $CD/$k $cnt); want=1; [ $k = K0 ] && want=0
    g=0; [ "$2" = "$want" ] && g=1; kpass=$((kpass + g))
    row "SEG_CONTROL|case=$k|exit=$1|detected=$2|want_detected=$want|ok=$g"
  done
  [ $kpass = 6 ] && seg=PASS
else
  row "SEG_CONTROL|case=setup|ok=0|reason=G3_store_not_built_or_fewer_than_6_files"
fi

# ---- step 4: P3 runner identity (3x3, segmented store G1) ----------------------------------
D3=$W/p2/3x3; MAT=$D3/ymsec.txt; c3=$(grep '^P2_STORE|L=3x3|geom=G1|' $L | grep -o 'files=[0-9]*' | cut -d= -f2)
DEV3="seg:1:$c3:40000000:$D3/segG1/sector-"; N3=${SIZE[3x3]}; STORE3=$(grep '^P2_SINGLE|L=3x3|' $L | grep -o 'store_sha256=[0-9a-f]*' | cut -d= -f2)
MSHA=$(sha $MAT)
inputs_ok() { [ "$(sha $MAT)" = "$MSHA" ] && [ "$(segcat $D3/segG1 $N3 $c3 | sha256sum | cut -c1-64)" = "$STORE3" ]; }
chunks() { # side dir S core -> P3_CHUNKS fields
  local side=$1 d=$2 s=$3 core=$4 i pres=0 ex=1 bind="" bok=1 cok=1 rng=""
  for i in $(seq 0 $((s-1))); do
    [ "$(grep -c '^SHELL_SCHUR_COLS|' $d/c$i.out)" = 1 ] && pres=$((pres+1))
    [ "$(cat $d/c$i.exit)" = 0 ] || [ "$(cat $d/c$i.exit)" = 2 ] || ex=0
    b=$(cat $d/c$i.bind); [ -z "$bind" ] && bind=$b; [ "$b" = "$bind" ] || bok=0
    case $side in shell) [ "$b" = "INPUT_MATRIX|sha256=$MSHA|file=ymsec.txt|json=0" ] || bok=0;; room) [ "$b" = "INPUT_ROOMS|sha256=$STORE3|file=3x3_segG1_logical|json=0" ] || bok=0;; esac
    [ "$(grep '^SHELL_SCHUR_COLS|' $d/c$i.out | grep -o '|core=[0-9]*' | cut -d= -f2)" = $core ] || cok=0
    rng="$rng $(grep '^SHELL_SCHUR_COLS|' $d/c$i.out | grep -o 'cols=[0-9]*:[0-9]*' | cut -d= -f2)"
  done
  local pe=1 nxt=0 r; for r in $(echo $rng | tr ' ' '\n' | sort -t: -k1,1n); do [ "${r%:*}" = $nxt ] || pe=0; nxt=${r#*:}; done; [ $nxt = $core ] || pe=0
  local cc=$core; [ $cok = 1 ] || cc=bad
  row "P3_CHUNKS|t=$t|side=$side|S=$s|present=$pres|exits_ok=$ex|partition_exact=$pe|binding_equal=$bok|core=$cc"
}
for spec in $THR; do
  t=${spec%%:*}; rest=${spec#*:}; core=${rest%%:*}; S=${rest#*:}; P=$W/p3/t$t; mkdir -p $P/shell $P/room
  i0=1; inputs_ok || i0=0
  for i in $(seq 0 $((S-1))); do
    a=$(( i * core / S )); b=$(( (i+1) * core / S ))
    # binding lines go to .bind files: merge tools read only the tools' own chunk output
    SHELLSCHUR_COLS=$a:$b $B/shellschur.exe $MAT $JE $JB $t -1 $FDIG $TOL $MAXSWEEP > $P/shell/c$i.out 2> $P/shell/c$i.err; echo $? > $P/shell/c$i.exit
    echo "INPUT_MATRIX|sha256=$(sha $MAT)|file=ymsec.txt|json=0" > $P/shell/c$i.bind
    ROOMSCHUR_K=$K ROOMSCHUR_BUDGET=$BUDGET ROOMSCHUR_COLS=$a:$b $B/roomschur.exe "$DEV3" 0 $JE $JB $t $FDIG $TOL $MAXSWEEP > $P/room/c$i.out 2> $P/room/c$i.err; echo $? > $P/room/c$i.exit
    echo "INPUT_ROOMS|sha256=$(segcat $D3/segG1 $N3 $c3 | sha256sum | cut -c1-64)|file=3x3_segG1_logical|json=0" > $P/room/c$i.bind
  done
  chunks shell $P/shell $S $core; chunks room $P/room $S $core
  fs=$(for i in $(seq 0 $((S-1))); do printf '%s,' $P/shell/c$i.out; done); fr=$(for i in $(seq 0 $((S-1))); do printf '%s,' $P/room/c$i.out; done)
  SHELLSCHUR_MERGE=${fs%,} $B/shellschur.exe $MAT $JE $JB $t -1 $FDIG $TOL $MAXSWEEP > $P/shell/merge.out 2> $P/shell/merge.err; es=$?
  ROOMSCHUR_K=$K ROOMSCHUR_BUDGET=$BUDGET ROOMSCHUR_MERGE=${fr%,} $B/roomschur.exe "$DEV3" 0 $JE $JB $t $FDIG $TOL $MAXSWEEP > $P/room/merge.out 2> $P/room/merge.err; er=$?
  for side in shell room; do
    m=$(grep '^SHELL_SCHUR|' $P/$side/merge.out | tail -1); e=$es; [ $side = room ] && e=$er
    f() { echo "$m" | grep -o "|$1=[^|]*" | cut -d= -f2; }
    row "P3_MERGE|t=$t|side=$side|exit=$e|core=$(f core)|result=$(f result)|negative=$(f negative)|ambiguous=$(f ambiguous)"
    for i in $(seq 0 $((S-1))); do cat $P/$side/c$i.out $P/$side/c$i.bind; done > $P/$side-t$t.hbp; cat $P/$side/merge.out >> $P/$side-t$t.hbp
  done
  ms=$(grep '^SHELL_SCHUR_COLS|' $P/room-t$t.hbp | grep -o 'payload_merkle=[0-9a-f]*' | cut -d= -f2)
  nl=$(echo "$ms" | grep -c .); ae=0; [ "$(echo "$ms" | sort -u | grep -c .)" = 1 ] && ae=1
  row "P3_MERKLE|t=$t|room_lines=$nl|all_equal=$ae|merkle=$(echo "$ms" | head -1)"
  i1=1; inputs_ok || i1=0; u=0; [ $i0 = 1 ] && [ $i1 = 1 ] && u=1
  row "P3_INPUTS|t=$t|unchanged=$u|matrix_sha256=$MSHA|store_sha256=$STORE3"
  for mode in v2 v1; do
    fl=""; [ $mode = v1 ] && fl=--v1
    python -I $SPEC/code/schur_record_compare_stream.py $fl $P/shell-t$t.hbp $P/room-t$t.hbp > $P/cmp-$mode.out 2> $P/cmp-$mode.err; e=$?
    v=$(tr -d '\r' < $P/cmp-$mode.out | grep '^SCHUR_COMPARE_VERDICT|' | awk -F'|' '{print $3}')
    row "P3_CMP|t=$t|mode=$mode|verdict=$v|exit=$e|stdout_file=p3/t$t/cmp-$mode.out|stdout_sha256=$(sha $P/cmp-$mode.out)"
    tr -d '\r' < $P/cmp-$mode.out | sed "s/^/P3_CMP_STDOUT|t=$t|mode=$mode|/" >> $L
  done
done

# ---- step 5: control C-SF60 (same binary, single-file store, t=60M, S=2) ---------------------
C=$W/csf60; mkdir -p $C
for i in 0 1; do a=$(( i * 101 / 2 )); b=$(( (i+1) * 101 / 2 ))
  ROOMSCHUR_K=$K ROOMSCHUR_BUDGET=$BUDGET ROOMSCHUR_COLS=$a:$b $B/roomschur.exe $D3/single.rooms 0 $JE $JB 60000000 $FDIG $TOL $MAXSWEEP > $C/c$i.out 2> $C/c$i.err
done
ROOMSCHUR_K=$K ROOMSCHUR_BUDGET=$BUDGET ROOMSCHUR_MERGE=$C/c0.out,$C/c1.out $B/roomschur.exe $D3/single.rooms 0 $JE $JB 60000000 $FDIG $TOL $MAXSWEEP > $C/merge.out 2> $C/merge.err
cat $C/c0.out $C/c1.out $C/merge.out > $C/room-single-t60000000.hbp
python -I $SPEC/code/schur_record_compare_stream.py $C/room-single-t60000000.hbp $W/p3/t60000000/room-t60000000.hbp > $C/cmp.out; ce=$?
sc=0; cmp -s <(grep '^SCOL|' $C/room-single-t60000000.hbp) <(grep '^SCOL|' $W/p3/t60000000/room-t60000000.hbp) && sc=1
csf=FAIL; [ $ce = 0 ] && [ $sc = 1 ] && csf=PASS
cv=$(tr -d '\r' < $C/cmp.out | grep '^SCHUR_COMPARE_VERDICT|' | awk -F'|' '{print $3}')
row "CSF60|v2_exit=$ce|v2_verdict=$cv|stdout_file=csf60/cmp.out|stdout_sha256=$(sha $C/cmp.out)|scol_bytes_identical=$sc|result=$csf"
row "CONTROLS|comparator=$cc|segment=$seg|verdict=$vc|csf60=$csf"

# ---- step 6: end integrity and verdict ---------------------------------------------------
xe=1; ok_exe || xe=0
sp=1; (cd $SPEC && sha256sum -c --quiet SHA256SUMS) || sp=0
row "END_INTEGRITY|exe_unchanged=$xe|spec_unchanged=$sp|t=$(date -Iseconds)"
verdict
