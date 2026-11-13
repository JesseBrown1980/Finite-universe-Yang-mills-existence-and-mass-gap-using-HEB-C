#!/bin/bash
# third correction round: rehearsals of the launcher and of the checker at excluded r. Nothing here passes r = 9 or an
# r within 1 of 9 to any program, and --launch-r9 is never passed.
#   d_reh.sh prep     export of the staged file set (the checkout the checker runs in), scratch clone for the frozen build
#   d_reh.sh small    namespace entries, the base run K, the lowered-limit stop PQ, the checker cases on K
#   d_reh.sh three    A1 A2 A3 (three steps each, one per decision) and the checker on each
#   d_reh.sh frozen   FB1 FB2 FB3 FB5 in the scratch clone and the checker on FB1
#   d_reh.sh full     D13 (full size, fallback to m0 13) and the checker on it
set -u
W=/root/floor-v3; R=/root/floor-v2/repo; V=independent/y131-floor-cert-freeze-v2-20261110
P=$R/$V; O=$W/rehd; EXP=$W/export1; EXPV=$EXP/$V; SCR=$W/scratch
C3=78c89c312a265fe4090071fc1abdc7d6eb102e7e
L=final/tools/run_floor.sh
SMALL=(--test-r 12 --test-m0 7 --test-f '1;4,3,2,1' --test-g0 100/1)
ST1=$(cut -d' ' -f1 $O/STAGE1.sha256)
[ "$(sha256sum $P/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp | cut -d' ' -f1)" = "$ST1" ] || { echo "record is not the stage-1 record"; exit 1; }
cd /
run() { # name launcher-folder args... ; one launcher run, stdout and exit code kept
  local n=$1 f=$2; shift 2
  rm -rf $O/$n $O/$n.stdout $O/$n.exit
  bash $f/$L "$@" --test-out $O/$n > $O/$n.stdout 2>&1; echo $? > $O/$n.exit
  echo "$n exit=$(cat $O/$n.exit) $(tail -1 $O/$n.stdout | cut -d'|' -f1-4,7-9 | cut -c1-230)"
}
chk() { # name checkout receipt [more arguments] ; one checker run
  local n=$1 co=$2 rc=$3; shift 3
  rm -f $O/$n.stdout $O/$n.exit $O/$n.recheck.hbp*
  ( cd $co && python3 -I -B final/tools/recheck_floor.py receipt=$rc out=$O/$n.recheck.hbp "$@" ) > $O/$n.stdout 2>&1; echo $? > $O/$n.exit
  echo "$n exit=$(cat $O/$n.exit) $(tail -1 $O/$n.stdout | cut -d'|' -f1-3 | cut -c1-60) $(tail -1 $O/$n.stdout | grep -o 'reasons=.*' | cut -c1-200)"
}
resh() { ( cd $1 && sha256sum FLOOR-RUN-RECEIPT.hbp > FLOOR-RUN-RECEIPT.hbp.sha256 ); }
copyK() { rm -rf $O/cd/$1; mkdir -p $O/cd; cp -a $O/K $O/cd/$1; }
direct() { # name folder prefix... ; stage 2 entered without stage 1
  local n=$1 f=$2; shift 2
  rm -rf $O/$n $O/$n.stdout $O/$n.exit
  "$@" /usr/bin/bash --noprofile --norc -c "$(cat $f/$L)" run_floor.sh "${SMALL[@]}" --test-out $O/$n > $O/$n.stdout 2>&1; echo $? > $O/$n.exit
}
note() { echo "$2" > $O/$1.note.txt; echo "$1 $2"; }

case "$1" in
prep)
  cd $R; git add -A -- $V ':!'$V/work/design/rs/target
  rm -rf $EXP; mkdir -p $EXP; git checkout-index -a --prefix=$EXP/
  ( cd $EXPV && sha256sum final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp final/tools/recheck_floor.py | cut -c1-80 )
  rm -rf $SCR; git clone -q $R $SCR; cd $SCR; git checkout -q -b scratch-stage1 $C3
  cp -a $EXPV/. $SCR/$V/; git add -A -- $V
  git commit -q -m "scratch: stage-1 state of the third correction round, for the frozen-build rehearsal only (no part of the branch)"
  echo "scratch commit $(git rev-parse HEAD) status_lines=$(git status --porcelain --untracked-files=no | wc -l)"
  ;;
small)
  # NS0: the documented call, with the host mount table sampled while it runs
  rm -f $O/NS0.exit; ( while [ ! -e $O/NS0.exit ]; do grep -c floor-run /proc/1/mountinfo; sleep 0.2; done ) > $O/NS0.samples 2>/dev/null &
  run NS0 $P "${SMALL[@]}"; wait
  note NS0 "HOST_MOUNT_TABLE|during_the_run=samples_$(grep -c . $O/NS0.samples)_of_/proc/1/mountinfo_every_0.2_s|largest_count_of_floor-run_entries=$(sort -n $O/NS0.samples | tail -1)|after_the_run=$(grep -c floor-run /proc/self/mountinfo)|json=0"
  # NS1: stage 2 entered directly, in the caller's namespace
  direct NS1 $P env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2 FLOOR_ROOT=$P
  note NS1 "DIRECT_ENTRY|exit=$(cat $O/NS1.exit)|run_directory_exists=$([ -e $O/NS1 ] && echo 1 || echo 0)|floor-run_entries_in_the_host_mount_table=$(grep -c floor-run /proc/self/mountinfo)|json=0"
  # NS2: stage 2 entered directly in a new namespace whose mounts stay shared
  direct NS2 $P env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2 FLOOR_ROOT=$P /usr/bin/unshare -m --propagation shared
  note NS2 "DIRECT_ENTRY_SHARED|exit=$(cat $O/NS2.exit)|run_directory_exists=$([ -e $O/NS2 ] && echo 1 || echo 0)|floor-run_entries_in_the_host_mount_table=$(grep -c floor-run /proc/self/mountinfo)|json=0"
  # NS3: stage 2 entered directly by a parent shell that sits in the same private namespace
  rm -rf $O/NS3 $O/NS3.stdout $O/NS3.exit
  /usr/bin/unshare -m --propagation private /usr/bin/bash --noprofile --norc -c "env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2 FLOOR_ROOT=$P /usr/bin/bash --noprofile --norc -c \"\$(cat $P/$L)\" run_floor.sh --test-r 12 --test-m0 7 --test-f '1;4,3,2,1' --test-g0 100/1 --test-out $O/NS3; e=\$?; exit \$e" > $O/NS3.stdout 2>&1; echo $? > $O/NS3.exit
  note NS3 "DIRECT_ENTRY_PARENT_IN_THE_SAME_NAMESPACE|exit=$(cat $O/NS3.exit)|run_directory_exists=$([ -e $O/NS3 ] && echo 1 || echo 0)|json=0"
  # XNS: the launcher of 78c89c31 from an export of that commit, stage 2 entered directly (the finding as found)
  rm -rf $W/exp78; mkdir -p $W/exp78; git -C $R archive $C3 | tar -x -C $W/exp78
  mkdir -p $W/exp78/$V/work/design/rs/target/release; cp $P/work/design/rs/target/release/floorcert $W/exp78/$V/work/design/rs/target/release/
  rm -rf $O/XNS $O/XNS.stdout $O/XNS.exit
  env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2 FLOOR_ROOT=$W/exp78/$V /usr/bin/bash --noprofile --norc -c "$(cat $W/exp78/$V/$L)" run_floor.sh --test-r 12 --test-m0 7 --test-f '1' --test-g0 100/1 --test-out $O/XNS > $O/XNS.stdout 2>&1; echo $? > $O/XNS.exit
  note XNS "DIRECT_ENTRY_78C89C31|exit=$(cat $O/XNS.exit)|launcher_sha256=$(sha256sum $W/exp78/$V/$L | cut -d' ' -f1)|floor-run_entries_left_in_the_host_mount_table=$(grep -c floor-run /proc/self/mountinfo)|json=0"
  umount $O/XNS/tmp/tools 2>/dev/null; umount $O/XNS/tmp 2>/dev/null
  echo "host mounts after cleaning: $(grep -c floor-run /proc/self/mountinfo)"
  # K: the base run of the checker cases; PQ: the lowered-limit stop at the prerequisite
  run K $P "${SMALL[@]}"
  run PQ $P --test-r 12 --test-m0 6,7,9 --test-f '1;4,3,2,1' --test-g0 1045/10 --test-limit-kb 23000
  run FB5 $P "${SMALL[@]}" --freeze-commit $C3
  chk RK $EXPV $O/K/FLOOR-RUN-RECEIPT.hbp
  chk N16 $EXPV $O/PQ/FLOOR-RUN-RECEIPT.hbp
  chk N18 $EXPV $O/K/FLOOR-RUN-RECEIPT.hbp commit=$C3
  c=RUN7/cert_m7_r12_1_f1.txt; RC=FLOOR-RUN-RECEIPT.hbp
  copyK N1; rm $O/cd/N1/$c; chk N1 $EXPV $O/cd/N1/$RC
  copyK N2; printf 'x\n' >> $O/cd/N2/$c; chk N2 $EXPV $O/cd/N2/$RC
  copyK N3; d=$O/cd/N3; o=$(sha256sum $d/$c | cut -d' ' -f1); sed -i '2s/ [0-9]*$/ 1/' $d/$c; n=$(sha256sum $d/$c | cut -d' ' -f1); sed -i "s/$o/$n/g" $d/$RC; resh $d; chk N3 $EXPV $d/$RC
  copyK N4; d=$O/cd/N4; sed -i "s#|certificate=$c|#|certificate=RUN7/../$c|#" $d/$RC; resh $d; chk N4 $EXPV $d/$RC
  copyK N5; d=$O/cd/N5; sed -i "s#|certificate=$c|#|certificate=$O/K/$c|#" $d/$RC; resh $d; chk N5 $EXPV $d/$RC
  copyK N6; d=$O/cd/N6; mv $d/$c $O/cd/N6.real.txt; ln -s $O/cd/N6.real.txt $d/$c; chk N6 $EXPV $d/$RC
  copyK N7; d=$O/cd/N7; rm -rf $O/cd/N7.RUN7; mv $d/RUN7 $O/cd/N7.RUN7; ln -s $O/cd/N7.RUN7 $d/RUN7; chk N7 $EXPV $d/$RC
  copyK N8; d=$O/cd/N8; sed -i 's/|PREDICTION=CONFIRMED|DECISION=ABOVE|/|PREDICTION=UNRESOLVED|DECISION=UNRESOLVED|/' $d/$RC; resh $d; chk N8 $EXPV $d/$RC
  copyK N9; d=$O/cd/N9; sed -i 's/|UPPER_BOUND_VERIFIER_ONLY=10/|UPPER_BOUND_VERIFIER_ONLY=11/' $d/$RC; resh $d; chk N9 $EXPV $d/$RC
  copyK N10; d=$O/cd/N10; sed -i 's#|GAMMA=1042273/#|GAMMA=1042274/#' $d/$RC; resh $d; chk N10 $EXPV $d/$RC
  copyK N11; d=$O/cd/N11; cp $d/$c $d/RUN7/cert_m7_r12_1_f9.txt; chk N11 $EXPV $d/$RC
  copyK N12; d=$O/cd/N12; sed -i 's/|PREDICTION=CONFIRMED|DECISION=ABOVE|/|PREDICTION=UNRESOLVED|DECISION=UNRESOLVED|/' $d/$RC; chk N12 $EXPV $d/$RC
  copyK N13; d=$O/cd/N13; grep -v "^RECHECK|m0=7|certificate=$c|" $d/$RC > $d/x; mv $d/x $d/$RC; resh $d; chk N13 $EXPV $d/$RC
  rm -rf $W/export2; cp -a $EXP $W/export2; echo '# changed' >> $W/export2/$V/work/design/gate_required.sh; chk N14 $W/export2/$V $O/K/$RC
  copyK N15; d=$O/cd/N15; sed -i 's#|ritz_verifier=104854117/#|ritz_verifier=104854118/#' $d/$RC; resh $d; chk N15 $EXPV $d/$RC
  copyK N19; d=$O/cd/N19; sed -i 's/|UPPER_BOUND=10/|UPPER_BOUND=11/' $d/$RC; resh $d; chk N19 $EXPV $d/$RC
  copyK N20; d=$O/cd/N20; sed -i 's#|ritz_writer=104854117/#|ritz_writer=100000000/#' $d/$RC; resh $d; chk N20 $EXPV $d/$RC
  copyK N21; d=$O/cd/N21; sed -i 's/|UPPER_BOUND=104/|UPPER_BOUND=100/' $d/$RC; resh $d; chk N21 $EXPV $d/$RC
  copyK N17; d=$O/cd/N17; sed -i 's#|g0=100/1|accepted_certificates#|g0=105/1|accepted_certificates#' $d/$RC; resh $d; chk N17 $EXPV $d/$RC
  ;;
three)
  run A1 $P --test-r 12 --test-m0 7,8,9 --test-f '1;4,3,2,1' --test-g0 1045/10 &
  run A2 $P --test-r 12 --test-m0 7,8,9 --test-f '1;4,3,2,1' --test-g0 100/1 &
  run A3 $P --test-r 12 --test-m0 7,8,9 --test-f '1;4,3,2,1' --test-g0 110/1 &
  wait
  for n in A1 A2 A3; do chk R$n $EXPV $O/$n/FLOOR-RUN-RECEIPT.hbp & done; wait
  ;;
frozen)
  run FB1 $SCR/$V "${SMALL[@]}" --test-frozen-build
  grep -E '^NOTE\|(frozen_build|freeze_commit)|^TOOL\|private_copy=floorcert|^PINCHECK_RESULT' $O/FB1.stdout | cut -c1-330
  run FB2 $SCR/$V "${SMALL[@]}" --test-frozen-build --freeze-commit $C3
  echo >> $SCR/$V/final/CHANGES.txt
  run FB3 $SCR/$V "${SMALL[@]}" --test-frozen-build
  git -C $SCR checkout -q -- $V/final/CHANGES.txt; echo "scratch status_lines=$(git -C $SCR status --porcelain --untracked-files=no | wc -l)"
  chk RFB1 $EXPV $O/FB1/FLOOR-RUN-RECEIPT.hbp
  bash $EXPV/final/tools/freeze_args_controls.sh $O/FB1/target/release/floorcert $P/work/design/rs/target/release/floorcert $(git -C $SCR rev-parse HEAD) $ST1 > $O/FZA.stdout 2>&1; echo $? > $O/FZA.exit
  echo "FZA exit=$(cat $O/FZA.exit) $(tail -1 $O/FZA.stdout | cut -c1-200)"
  ;;
full)
  run D13 $P --test-r 21/2 --test-m0 11,12,13 --test-f '1;8,7,6,5,4;6,5,4,3' --test-g0 9938/100 --test-census --test-hang 1:cert,2:cert
  chk RD13 $EXPV $O/D13/FLOOR-RUN-RECEIPT.hbp
  ;;
esac
echo "DONE $1"
