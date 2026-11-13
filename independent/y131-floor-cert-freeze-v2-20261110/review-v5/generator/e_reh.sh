#!/bin/bash
# fourth correction round: rehearsals of the launcher and of the checker at excluded r. Nothing here computes at r = 9
# or within 1 of it, and --launch-r9 is never passed. The only contact with r = 9 is final/tools/freeze_args_controls.sh
# (eleven refusal controls, row 134), run once in the frozen phase.
#   e_reh.sh prep | small | three | frozen | full
set -u
W=/root/floor-v5; R=/root/floor-v2/repo; V=independent/y131-floor-cert-freeze-v2-20261110
P=$R/$V; O=$W/rehe; EXP=$W/export1; EXPV=$EXP/$V; SCR=$W/scratch
C4=5eecb540431a1b5665605f68ed81bc701719dcd1
L=final/tools/run_floor.sh
RC=FLOOR-RUN-RECEIPT.hbp
SMALL=(--test-r 12 --test-m0 7 --test-f '1;4,3,2,1' --test-g0 100/1)
ST1=$(cut -d' ' -f1 $O/STAGE1.sha256)
[ "$(sha256sum $P/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp | cut -d' ' -f1)" = "$ST1" ] || { echo "record is not the stage-1 record"; exit 1; }
cd /
run() { # name launcher-folder args...
  local n=$1 f=$2; shift 2
  rm -rf $O/$n $O/$n.stdout $O/$n.exit
  bash $f/$L "$@" --test-out $O/$n > $O/$n.stdout 2>&1; echo $? > $O/$n.exit
  echo "$n exit=$(cat $O/$n.exit) $(tail -1 $O/$n.stdout | cut -d'|' -f1-4,7-9 | cut -c1-230)"
}
chk() { # name checkout receipt [more arguments]
  local n=$1 co=$2 rc=$3; shift 3
  rm -f $O/$n.stdout $O/$n.exit $O/$n.recheck.hbp*
  ( cd $co && python3 -I -B final/tools/recheck_floor.py receipt=$rc out=$O/$n.recheck.hbp "$@" ) > $O/$n.stdout 2>&1; echo $? > $O/$n.exit
  echo "$n exit=$(cat $O/$n.exit) $(tail -1 $O/$n.stdout | cut -d'|' -f1-3 | cut -c1-60) $(tail -1 $O/$n.stdout | grep -o 'reasons=.*' | cut -c1-220)"
}
resh() { ( cd $1 && sha256sum $RC > $RC.sha256 ); }
cpy() { rm -rf $O/cd/$2; mkdir -p $O/cd; cp -a $O/$1 $O/cd/$2; }   # source-run case-name
direct() { # name folder prefix... ; stage 2 entered without stage 1
  local n=$1 f=$2; shift 2
  rm -rf $O/$n $O/$n.stdout $O/$n.exit
  "$@" /usr/bin/bash --noprofile --norc -c "$(cat $f/$L)" run_floor.sh "${SMALL[@]}" --test-out $O/$n > $O/$n.stdout 2>&1; echo $? > $O/$n.exit
}
note() { echo "$2" > $O/$1.note.txt; echo "$1 $2"; }
hostm() { grep -c floor-run /proc/self/mountinfo; }
E2=(env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2)

case "$1" in
prep)
  cd $R; git add -A -- $V ':!'$V/work/design/rs/target
  rm -rf $EXP; mkdir -p $EXP; git checkout-index -a --prefix=$EXP/
  ( cd $EXPV && sha256sum final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp final/tools/recheck_floor.py | cut -c1-80 )
  rm -rf $SCR; git clone -q $R $SCR; cd $SCR; git checkout -q -b scratch-stage1 $C4
  cp -a $EXPV/. $SCR/$V/; git add -A -- $V
  git commit -q -m "scratch: stage-1 state of the fourth correction round, for the frozen-build rehearsal only (no part of the branch)"
  echo "scratch commit $(git rev-parse HEAD) status_lines=$(git status --porcelain --untracked-files=no | wc -l)"
  ;;
small)
  rm -f $O/NS0.exit; ( while [ ! -e $O/NS0.exit ]; do grep -c floor-run /proc/1/mountinfo; sleep 0.2; done ) > $O/NS0.samples 2>/dev/null &
  run NS0 $P "${SMALL[@]}"; wait
  note NS0 "HOST_MOUNT_TABLE|during_the_run=samples_$(grep -c . $O/NS0.samples)_of_/proc/1/mountinfo_every_0.2_s|largest_count_of_floor-run_entries=$(sort -n $O/NS0.samples | tail -1)|after_the_run=$(hostm)|json=0"
  direct NS1 $P "${E2[@]}" FLOOR_ROOT=$P
  note NS1 "DIRECT_ENTRY|exit=$(cat $O/NS1.exit)|run_directory_exists=$([ -e $O/NS1 ] && echo 1 || echo 0)|floor-run_entries_in_the_host_mount_table=$(hostm)|json=0"
  direct NS2 $P "${E2[@]}" FLOOR_ROOT=$P /usr/bin/unshare -m --propagation shared
  note NS2 "DIRECT_ENTRY_SHARED|exit=$(cat $O/NS2.exit)|run_directory_exists=$([ -e $O/NS2 ] && echo 1 || echo 0)|floor-run_entries_in_the_host_mount_table=$(hostm)|json=0"
  rm -rf $O/NS3 $O/NS3.stdout $O/NS3.exit
  /usr/bin/unshare -m --propagation private /usr/bin/bash --noprofile --norc -c "env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2 FLOOR_ROOT=$P /usr/bin/bash --noprofile --norc -c \"\$(cat $P/$L)\" run_floor.sh --test-r 12 --test-m0 7 --test-f '1;4,3,2,1' --test-g0 100/1 --test-out $O/NS3; e=\$?; exit \$e" > $O/NS3.stdout 2>&1; echo $? > $O/NS3.exit
  note NS3 "DIRECT_ENTRY_PARENT_IN_THE_SAME_NAMESPACE|exit=$(cat $O/NS3.exit)|run_directory_exists=$([ -e $O/NS3 ] && echo 1 || echo 0)|json=0"
  # NS4: stage 2 entered through a private namespace that another process holds (the verifier's C4), on this launcher
  /usr/bin/unshare -m --propagation private /usr/bin/sleep 600 & HP=$!; sleep 1
  direct NS4 $P /usr/bin/nsenter -t $HP -m "${E2[@]}" FLOOR_ROOT=$P
  note NS4 "ENTRY_THROUGH_A_HELD_NAMESPACE|exit=$(cat $O/NS4.exit)|run_directory_exists=$([ -e $O/NS4 ] && echo 1 || echo 0)|floor-run_mounts_in_the_held_namespace=$(grep -c floor-run /proc/$HP/mountinfo)|json=0"
  # XNS4: the same entry against the launcher of 5eecb540, from an export of that commit (the finding as found)
  rm -rf $W/exp5e; mkdir -p $W/exp5e; git -C $R archive $C4 | tar -x -C $W/exp5e
  mkdir -p $W/exp5e/$V/work/design/rs/target/release; cp $P/work/design/rs/target/release/floorcert $W/exp5e/$V/work/design/rs/target/release/
  rm -rf $O/XNS4 $O/XNS4.stdout $O/XNS4.exit
  /usr/bin/nsenter -t $HP -m "${E2[@]}" FLOOR_ROOT=$W/exp5e/$V /usr/bin/bash --noprofile --norc -c "$(cat $W/exp5e/$V/$L)" run_floor.sh --test-r 12 --test-m0 7 --test-f '1' --test-g0 100/1 --test-out $O/XNS4 > $O/XNS4.stdout 2>&1; echo $? > $O/XNS4.exit
  note XNS4 "ENTRY_THROUGH_A_HELD_NAMESPACE_5EECB540|exit=$(cat $O/XNS4.exit)|launcher_sha256=$(sha256sum $W/exp5e/$V/$L | cut -d' ' -f1)|floor-run_mounts_left_in_the_held_namespace=$(grep -c floor-run /proc/$HP/mountinfo)|json=0"
  kill $HP 2>/dev/null; wait $HP 2>/dev/null
  echo "host mounts after the holder ended: $(hostm)"
  run K $P "${SMALL[@]}"
  run U1 $P --test-r 12 --test-m0 7 --test-f '1' --test-g0 100/1
  run PQ $P --test-r 12 --test-m0 6,7,9 --test-f '1;4,3,2,1' --test-g0 1045/10 --test-limit-kb 23000
  run FB5 $P "${SMALL[@]}" --freeze-commit $C4
  chk RK $EXPV $O/K/$RC
  chk RU1 $EXPV $O/U1/$RC
  KS=$(sha256sum $O/K/$RC | cut -d' ' -f1)
  chk RKP $EXPV $O/K/$RC receipt_sha256=$KS
  chk N22 $EXPV $O/K/$RC receipt_sha256=0000000000000000000000000000000000000000000000000000000000000000
  chk N16 $EXPV $O/PQ/$RC
  chk N18 $EXPV $O/K/$RC commit=$C4
  c=RUN7/cert_m7_r12_1_f1.txt
  cpy K N1; rm $O/cd/N1/$c; chk N1 $EXPV $O/cd/N1/$RC
  cpy K N2; printf 'x\n' >> $O/cd/N2/$c; chk N2 $EXPV $O/cd/N2/$RC
  cpy K N3; d=$O/cd/N3; o=$(sha256sum $d/$c | cut -d' ' -f1); sed -i '2s/ [0-9]*$/ 1/' $d/$c; n=$(sha256sum $d/$c | cut -d' ' -f1); sed -i "s/$o/$n/g" $d/$RC; resh $d; chk N3 $EXPV $d/$RC
  cpy K N4; d=$O/cd/N4; sed -i "s#|certificate=$c|#|certificate=RUN7/../$c|#" $d/$RC; resh $d; chk N4 $EXPV $d/$RC
  cpy K N5; d=$O/cd/N5; sed -i "s#|certificate=$c|#|certificate=$O/K/$c|#" $d/$RC; resh $d; chk N5 $EXPV $d/$RC
  cpy K N6; d=$O/cd/N6; mv $d/$c $O/cd/N6.real.txt; ln -s $O/cd/N6.real.txt $d/$c; chk N6 $EXPV $d/$RC
  cpy K N7; d=$O/cd/N7; rm -rf $O/cd/N7.RUN7; mv $d/RUN7 $O/cd/N7.RUN7; ln -s $O/cd/N7.RUN7 $d/RUN7; chk N7 $EXPV $d/$RC
  cpy K N8; d=$O/cd/N8; sed -i 's/|PREDICTION=CONFIRMED|DECISION=ABOVE|/|PREDICTION=UNRESOLVED|DECISION=UNRESOLVED|/' $d/$RC; resh $d; chk N8 $EXPV $d/$RC
  cpy K N9; d=$O/cd/N9; sed -i 's/|UPPER_BOUND_VERIFIER_ONLY=10/|UPPER_BOUND_VERIFIER_ONLY=11/' $d/$RC; resh $d; chk N9 $EXPV $d/$RC
  cpy K N10; d=$O/cd/N10; sed -i 's#|GAMMA=1042273/#|GAMMA=1042274/#' $d/$RC; resh $d; chk N10 $EXPV $d/$RC
  cpy K N11; d=$O/cd/N11; cp $d/$c $d/RUN7/cert_m7_r12_1_f9.txt; chk N11 $EXPV $d/$RC
  cpy K N12; d=$O/cd/N12; sed -i 's/|PREDICTION=CONFIRMED|DECISION=ABOVE|/|PREDICTION=UNRESOLVED|DECISION=UNRESOLVED|/' $d/$RC; chk N12 $EXPV $d/$RC
  cpy K N13; d=$O/cd/N13; grep -v "^RECHECK|m0=7|certificate=$c|" $d/$RC > $d/x; mv $d/x $d/$RC; resh $d; chk N13 $EXPV $d/$RC
  rm -rf $W/export2; cp -a $EXP $W/export2; echo '# changed' >> $W/export2/$V/work/design/gate_required.sh; chk N14 $W/export2/$V $O/K/$RC
  cpy K N15; d=$O/cd/N15; sed -i 's#|ritz_verifier=104854117/#|ritz_verifier=104854118/#' $d/$RC; resh $d; chk N15 $EXPV $d/$RC
  cpy K N17; d=$O/cd/N17; sed -i 's#|g0=100/1|accepted_certificates#|g0=105/1|accepted_certificates#' $d/$RC; resh $d; chk N17 $EXPV $d/$RC
  cpy K N19; d=$O/cd/N19; sed -i 's/|UPPER_BOUND=10/|UPPER_BOUND=11/' $d/$RC; resh $d; chk N19 $EXPV $d/$RC
  # the verifier's classes, on this checker
  cpy K N20; d=$O/cd/N20; sed -i 's#|ritz_writer=113469933/#|ritz_writer=113469934/#' $d/$RC; resh $d; chk N20 $EXPV $d/$RC            # a non-minimal writer value (its N12)
  cpy K P4; d=$O/cd/P4; sed -i '0,/|outcome=NOT_MET|/s//|outcome=MET|/' $d/$RC; resh $d; chk P4 $EXPV $d/$RC                           # a score changed (its X02)
  cpy K P5; d=$O/cd/P5; sed -i 's/^\(VERDICT_FIELDS|.*\)|json=0$/\1|DECISION=UNRESOLVED|json=0/; s/^\(FLOOR_RUN|.*\)|json=0$/\1|DECISION=UNRESOLVED|json=0/' $d/$RC; resh $d; chk P5 $EXPV $d/$RC   # a repeated field (its X01)
  cpy K P6; d=$O/cd/P6; sed -i 's/^\(STEP|m0=7|.*\)|resource_limit=HELD|/\1|resource_limit=EXCEEDED|/' $d/$RC; resh $d; chk P6 $EXPV $d/$RC   # its X03
  cpy K P7; d=$O/cd/P7; mv $d/$c $d/RUN7/cert_m7_r12_1_f2.txt; sed -i "s#|certificate=$c|#|certificate=RUN7/cert_m7_r12_1_f2.txt|#" $d/$RC; resh $d; chk P7 $EXPV $d/$RC   # a renamed certificate (its X05)
  cpy K P11; d=$O/cd/P11; grep -v '^PROTOCOL|' $d/$RC > $d/x; mv $d/x $d/$RC; resh $d; chk P11 $EXPV $d/$RC
  # a foreign certificate decides (its X07): U1 ran f = 1 alone and is UNRESOLVED; the f = 4,3,2,1 certificate of K is added
  cpy U1 P2; d=$O/cd/P2; cp $O/K/RUN7/cert_m7_r12_1_f4-3-2-1.txt $d/RUN7/; grep '^RECHECK|m0=7|certificate=RUN7/cert_m7_r12_1_f4-3-2-1.txt|' $O/K/$RC > $d/row
  sed -i "/^RECHECK|m0=7|certificate=RUN7\/cert_m7_r12_1_f1.txt|/r $d/row" $d/$RC; rm $d/row
  sed -i 's/|PREDICTION=UNRESOLVED|DECISION=UNRESOLVED|GAMMA=804069\/10000|UPPER_BOUND=113469934000000\/1000000000000|/|PREDICTION=CONFIRMED|DECISION=ABOVE|GAMMA=1042273\/10000|UPPER_BOUND=104854118000000\/1000000000000|/; s/|accepted_certificates=1|/|accepted_certificates=2|/' $d/$RC; resh $d; chk P2 $EXPV $d/$RC
  ;;
three)
  run A1 $P --test-r 12 --test-m0 7,8,9 --test-f '1;4,3,2,1' --test-g0 1045/10 &
  run A2 $P --test-r 12 --test-m0 7,8,9 --test-f '1;4,3,2,1' --test-g0 100/1 &
  run A3 $P --test-r 12 --test-m0 7,8,9 --test-f '1;4,3,2,1' --test-g0 110/1 &
  run B2 $P --test-r 12 --test-m0 7,8 --test-f '1;4,3,2,1' --test-g0 1046/10 &
  wait
  for n in A1 A2 A3 B2; do chk R$n $EXPV $O/$n/$RC & done; wait
  # a falsification hidden (the verifier's X06): B2 is BELOW at m0 8; its m0 8 certificates and rows are removed and the verdict rewritten to the m0 7 state
  g7=$(grep '^STEP|m0=7|' $O/B2/$RC | sed 's/.*|G=\([0-9/]*\)|.*/\1/'); u7=$(grep '^STEP|m0=7|' $O/B2/$RC | sed 's/.*|U=\([0-9/]*\)|.*/\1/')
  forge() { # dir ; verdict rows rewritten to UNRESOLVED on the m0 7 values
    sed -i "s#^\(VERDICT_FIELDS\)|CERTIFICATE=PASS|PREDICTION=[A-Z]*|DECISION=[A-Z]*|GAMMA=[0-9/]*|UPPER_BOUND=[0-9/]*|UPPER_BOUND_VERIFIER_ONLY=[0-9/]*|#\1|CERTIFICATE=PASS|PREDICTION=UNRESOLVED|DECISION=UNRESOLVED|GAMMA=$g7|UPPER_BOUND=$u7|UPPER_BOUND_VERIFIER_ONLY=$u7|#; s#^\(FLOOR_RUN\)|CERTIFICATE=PASS|PREDICTION=[A-Z]*|DECISION=[A-Z]*|GAMMA=[0-9/]*|UPPER_BOUND=[0-9/]*|#\1|CERTIFICATE=PASS|PREDICTION=UNRESOLVED|DECISION=UNRESOLVED|GAMMA=$g7|UPPER_BOUND=$u7|#; s/|accepted_certificates=4|/|accepted_certificates=2|/" $1/$RC
  }
  cpy B2 P1; d=$O/cd/P1; rm $d/RUN8/cert_*; grep -v '^RECHECK|m0=8|\|^STEP|m0=8|\|^CERTROW|m0=8|\|^ACCEPTED|m0=8|' $d/$RC > $d/x; mv $d/x $d/$RC
  forge $d; sed -i 's/|steps_run=7,8|steps_ok=7,8|/|steps_run=7|steps_ok=7|/' $d/$RC; resh $d; chk P1 $EXPV $d/$RC
  cpy B2 P1b; d=$O/cd/P1b; rm $d/RUN8/cert_*; grep -v '^RECHECK|m0=8|\|^CERTROW|m0=8|' $d/$RC > $d/x; mv $d/x $d/$RC
  sed -i 's/^STEP|m0=8|.*/STEP|m0=8|status=OPFAIL|accepted=0|certificates=0|resource_limit=HELD|limit_kB=2097152|bad=cert_command_crash|json=0/' $d/$RC
  forge $d; sed -i 's/|steps_run=7,8|steps_ok=7,8|operational_failures=none|/|steps_run=7,8|steps_ok=7|operational_failures=8|/' $d/$RC; resh $d; chk P1b $EXPV $d/$RC
  ;;
frozen)
  run FB1 $SCR/$V "${SMALL[@]}" --test-frozen-build
  grep -E '^NOTE\|(frozen_build|freeze_commit|build_environment)|^TOOL\|private_copy=floorcert|^PINCHECK_RESULT' $O/FB1.stdout | cut -c1-300
  run FB2 $SCR/$V "${SMALL[@]}" --test-frozen-build --freeze-commit $C4
  echo >> $SCR/$V/final/CHANGES.txt
  run FB3 $SCR/$V "${SMALL[@]}" --test-frozen-build
  git -C $SCR checkout -q -- $V/final/CHANGES.txt
  echo >> $SCR/README.md
  run FB3b $SCR/$V "${SMALL[@]}" --test-frozen-build                      # a tracked file outside the freeze folder (the verifier's E3b)
  git -C $SCR checkout -q -- README.md
  mkdir -p $SCR/$V/work/design/rs/.cargo; printf '[build]\nrustflags = ["-C", "opt-level=1"]\n' > $SCR/$V/work/design/rs/.cargo/config.toml
  run FB6 $SCR/$V "${SMALL[@]}" --test-frozen-build                       # a cargo configuration file (the verifier's E4)
  rm -rf $SCR/$V/work/design/rs/.cargo
  echo x > $SCR/$V/work/design/rs/src/extra.rs
  run FB7 $SCR/$V "${SMALL[@]}" --test-frozen-build                       # an untracked file in the Rust folder
  rm -f $SCR/$V/work/design/rs/src/extra.rs
  echo "scratch status_lines=$(git -C $SCR status --porcelain --untracked-files=no | wc -l)"
  chk RFB1 $EXPV $O/FB1/$RC
  bash $EXPV/final/tools/freeze_args_controls.sh $O/FB1/target/release/floorcert $P/work/design/rs/target/release/floorcert $(git -C $SCR rev-parse HEAD) $ST1 > $O/FZA.stdout 2>&1; echo $? > $O/FZA.exit
  echo "FZA exit=$(cat $O/FZA.exit) $(tail -1 $O/FZA.stdout | cut -c1-200)"
  ;;
full)
  run D13 $P --test-r 21/2 --test-m0 11,12,13 --test-f '1;8,7,6,5,4;6,5,4,3' --test-g0 9938/100 --test-census --test-hang 1:cert,2:cert
  chk RD13 $EXPV $O/D13/$RC
  ;;
esac
echo "DONE $1"
