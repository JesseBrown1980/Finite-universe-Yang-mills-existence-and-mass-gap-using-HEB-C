#!/bin/bash
# Second correction round: rehearsals of the pinned launcher, test mode at excluded r only. The r9 mode is never started here.
# usage: reh_c.sh NAME [NAME...]   Output: /root/floor-v2/rehc/NAME (run directory), NAME.stdout.txt, NAME.rc, NAME.args
# PKG=<folder> runs another copy of the freeze folder (development); default is the repository tree.
P=${PKG:-/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110}
O=/root/floor-v2/rehc
AT=/root/floor-v2/atkc
A=$AT/pkg
REC=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
mkdir -p $O $AT /root/floor-v2/tmp
export TMPDIR=/root/floor-v2/tmp
argstr() { local s="" x; for x in "$@"; do [ -n "$x" ] || x=EMPTY; s="${s:+${s}_}$x"; done; echo "${s:-NO_ARGUMENT}"; }
fresh() { # a byte copy of the package folder outside the repository (no git data), with the pin-free binary
  rm -rf $A; mkdir -p $A
  tar -C $P --exclude=./work/design/rs/target --exclude=./work/run9 -cf - . | tar -C $A -xf -
  mkdir -p $A/work/design/rs/target/release; cp -p $P/work/design/rs/target/release/floorcert $A/work/design/rs/target/release/
}
fin() { echo "== $1 rc=$(cat $O/$1.rc) :: $(grep '^FLOOR_RUN|' $O/$1.stdout.txt | tail -1 | sed 's/|HASHES=.*//' | cut -c1-520)"; }
one() { # NAME args... : the launcher of the tree, with a run directory
  local n=$1; shift; rm -rf $O/$n $O/$n.*
  argstr "$@" > $O/$n.args
  bash $P/final/tools/run_floor.sh --test-out $O/$n "$@" > $O/$n.stdout.txt 2>&1; echo $? > $O/$n.rc; fin $n
}
raw() { # NAME ROOT args... : exactly these arguments, no run directory given
  local n=$1 root=$2; shift 2; rm -rf $O/$n $O/$n.*
  argstr "$@" > $O/$n.args
  bash $root/final/tools/run_floor.sh "$@" > $O/$n.stdout.txt 2>&1; echo $? > $O/$n.rc; fin $n
  [ -e $root/work/run9 ] && echo "!! work/run9 exists under $root"
}
byst() { # NAME args... : the same as one, beside a process named floorcert that this script starts outside the launcher
  local n=$1 bp a0 a1; shift
  mkdir -p $AT/bystander; cp /bin/sleep $AT/bystander/floorcert
  $AT/bystander/floorcert 900 & bp=$!
  sleep 0.3; a0=0; kill -0 $bp 2>/dev/null && a0=1
  one $n "$@"
  a1=0; kill -0 $bp 2>/dev/null && a1=1
  echo "BYSTANDER|name=$(cat /proc/$bp/comm 2>/dev/null)|what=a_copy_of_sleep_named_floorcert_started_outside_the_launcher|alive_before=$a0|alive_after=$a1|leftover_sleep_20=$(pgrep -fc '^sleep 20$')|json=0" | tee $O/$n.bystander.txt
  kill $bp 2>/dev/null; wait $bp 2>/dev/null
}
atk() { # NAME RELFILE HOW args... : run on the copy; once the binary line is logged, change RELFILE of the tree copy; put it back afterwards
  local n=$1 rel=$2 how=$3 lp i tgt; shift 3; rm -rf $O/$n $O/$n.*
  fresh
  argstr "$@" > $O/$n.args
  bash $A/final/tools/run_floor.sh --test-out $O/$n "$@" > $O/$n.stdout.txt 2>&1 & lp=$!
  i=0; while [ $i -lt 3000 ] && ! grep -q '^NOTE|binary=' $O/$n/log/run.log 2>/dev/null; do i=$((i+1)); sleep 0.01; done
  tgt=$A/$rel
  case $how in
    fakegate) printf '%s\n' '#!/bin/bash' 'echo "GATE_REQUIRED|PASS|cert=$1|cert_sha256=$(sha256sum "$1" | cut -d" " -f1)|rowhash=NONE|verifier_sha256=6043d089"' > $tgt;;
    replay) # the verifier's L1: a gate driver that replays the logs of the genuine run K0 and runs no verifier
      printf '%s\n' '#!/bin/bash' "echo \"\$1\" >> $O/$n.fakecalls" "cat \"$O/K0/log/m7_gate_\$(basename \"\$1\").txt\"; exit 0" > $tgt;;
    empty) printf '%s\n' '#!/bin/bash' "echo \"\$1\" >> $O/$n.fakecalls" 'exit 0' > $tgt;;
    append) echo "# one appended line" >> $tgt;;
    byte) printf 'X' >> $tgt;;
  esac
  echo "ATTACK|file=$rel|how=$how|launcher_sha16=$(sha256sum $A/final/tools/run_floor.sh | cut -c1-16)|changed_after_the_binary_line=1|sha256_after_change=$(sha256sum $tgt 2>/dev/null | cut -d' ' -f1)|json=0" > $O/$n.attack.txt
  wait $lp; echo $? > $O/$n.rc
  i=0; [ -f $O/$n.fakecalls ] && i=$(grep -c . $O/$n.fakecalls)
  cp -p $P/$rel $A/$rel
  echo "ATTACK_END|file=$rel|put_back=1|copy_equals_repository_file=$(cmp -s $P/$rel $A/$rel && echo 1 || echo 0)|fake_gate_calls=$i|json=0" >> $O/$n.attack.txt
  fin $n; grep '^INTEGRITY|' $O/$n.stdout.txt | cut -c1-260; tail -1 $O/$n.attack.txt
}
ev() { # NAME : the evaluator called directly on a copy of the finished run LK1, with a tool directory built here
  local c=$1 TD=$AT/evtools PS FS DS ES KS PY=/usr/bin/python3.12 BX=/usr/bin/bash
  [ -f $O/LK1/FLOOR-RUN-RECEIPT.hbp ] || { echo "LK1 first"; exit 1; }
  fresh; rm -rf $O/$c $O/$c.*; cp -a $O/LK1 $O/$c; rm -f $O/$c/FLOOR-RUN-RECEIPT.hbp*
  rm -rf $TD; mkdir -p $TD/py
  cp $A/work/design/gate_required.sh $A/$REC $TD/; cp $A/work/design/py/cert_gate.py $A/work/design/py/indep_verify.py $TD/py/
  sed -i -e "s#$O/LK1/tmp/tools#$TD#g" -e "s#$O/LK1/#$O/$c/#g" $O/$c/log/run.log
  PS=$(sha256sum $A/$REC | cut -d' ' -f1); FS=$(sha256sum $A/work/design/rs/target/release/floorcert | cut -d' ' -f1); DS=$(sha256sum $A/final/tools/run_floor.sh | cut -d' ' -f1)
  ES=$(sha256sum $A/final/tools/floor_eval.py | cut -d' ' -f1); KS=$(sha256sum $A/work/design/peak_rss.py | cut -d' ' -f1)
  case $c in
    EV0) echo "evaluator_called_directly_on_a_copy_of_the_finished_run_LK1_(run_log_paths_rewritten_to_the_copy_and_to_a_tool_directory_built_for_this_call),_nothing_changed:_the_control" > $O/$c.args;;
    EV1) echo "# one appended line" >> $A/work/design/gate_required.sh; echo "as_EV0_with_work/design/gate_required.sh_of_the_tree_copy_changed" > $O/$c.args;;
    EV2) echo "# one appended line" >> $A/work/design/py/indep_verify.py; echo "as_EV0_with_work/design/py/indep_verify.py_of_the_tree_copy_changed" > $O/$c.args;;
    EV3) sed -i '/^INVOKE|.*|kind=gate|/d' $O/$c/log/run.log; echo "as_EV0_with_the_INVOKE_line_of_the_verifier_call_removed_from_the_run_log_(a_bypassed_gate)" > $O/$c.args;;
    EV4) echo "# one appended line" >> $TD/gate_required.sh; echo "as_EV0_with_the_executed_copy_of_gate_required.sh_changed" > $O/$c.args;;
    EV5) sed -i '/|kind=gate|/s/|rc=0|/|rc=1|/' $O/$c/log/run.log; echo "as_EV0_with_the_recorded_exit_code_of_the_verifier_call_set_to_1" > $O/$c.args;;
    EV6) sed -i '/|kind=gate|/s/|private_tools_after=HELD|/|/' $O/$c/log/run.log; echo "as_EV0_with_the_private_tools_after_field_removed_from_the_record_of_the_verifier_call" > $O/$c.args;;
    EV7) KS=$(printf x | sha256sum | cut -d' ' -f1); echo "as_EV0_with_another_hash_given_for_the_in-memory_peak_wrapper" > $O/$c.args;;
  esac
  ( cd $A
    $PY -I -B $A/final/tools/floor_eval.py step root=$A tools=$TD pred=$TD/${REC##*/} out=$O/$c m0=7 r=12 fspec=4,3,2,1 mode=test census=0 commit=NONE psha=$PS fbsha=$FS py=$PY bash=$BX peaksha=$KS evsha=$ES drvsha=$DS; echo "STEP_EXIT|$?"
    $PY -I -B $A/final/tools/floor_eval.py final root=$A tools=$TD out=$O/$c pred=$TD/${REC##*/} steps=7 g0=100/1 allowed=1 mode=test r=12 stop=DECIDED commit=NONE fbsha=$FS drvsha=$DS evsha=$ES peaksha=$KS predrel=$REC receipt=$O/$c/FLOOR-RUN-RECEIPT.hbp
    echo $? > $O/$c.rc ) > $O/$c.stdout.txt 2>&1
  fin $c; grep '^STEP|\|^STEP_EXIT' $O/$c.stdout.txt | cut -c1-330; grep 'ok=0' $O/$c/log/pincheck_closing.txt | cut -c1-200
}
S="--test-r 12 --test-f 4,3,2,1"
K="--test-r 12 --test-m0 7 --test-f 1;4,3,2,1 --test-g0 100/1"
for c in "$@"; do case $c in
 K0) one K0 $K;;
 A1) one A1 --test-r 12 --test-m0 7,8,9 --test-f '1;4,3,2,1' --test-g0 1045/10;;
 A2) one A2 --test-r 12 --test-m0 7,8,9 --test-f '1;4,3,2,1' --test-g0 100/1;;
 A3) one A3 --test-r 12 --test-m0 7,8,9 --test-f '1;4,3,2,1' --test-g0 110/1;;
 B1) one B1 --test-r 21/2 --test-m0 6,7 --test-f '4,3,2,1' --test-g0 95/1 --test-plant 1:993765/10000;;
 B2) one B2 --test-r 12 --test-m0 6,7 --test-f '1;4,3,2,1' --test-g0 1045/10 --test-plant 2:1048542/10000;;
 C1) one C1 $S --test-m0 7,8 --test-g0 100/1 --test-crash 1:rowhash;;
 C2) byst C2 $S --test-m0 7,8 --test-g0 100/1 --test-hang 1:cert;;
 C3) one C3 $S --test-m0 7,8 --test-g0 100/1 --test-crash 1:cert;;
 C4) byst C4 $S --test-m0 7,8 --test-g0 100/1 --test-hang-hard 1:cert;;
 C5) one C5 $S --test-m0 7 --test-g0 100/1 --test-hang 1:rowhash;;
 V1) one V1 $S --test-m0 7,8 --test-g0 100/1 --test-vexc 1;;
 V2) one V2 $S --test-m0 7,8 --test-g0 100/1 --test-crash 1:rowhash --test-vexc 1;;
 V3) one V3 $S --test-m0 7,8 --test-g0 100/1 --test-hang 1:gate;;
 V4) one V4 --test-r 12 --test-f '1;4,3,2,1' --test-m0 7,8 --test-g0 100/1 --test-crash 1:rowhash,1:gate;;
 N9) one N9 --test-r 19/2 --test-m0 7 --test-f '4,3,2,1';;
 N13) one N13 --test-r 13 --test-m0 7 --test-f '4,3,2,1' --test-g0 100/1;;
 BA) one BA $S --test-m0 7 --test-g0 1042273/10000;;
 BAm) one BAm $S --test-m0 7 --test-g0 1042273001/10000000;;
 BU) one BU $S --test-m0 7 --test-g0 104854118/1000000;;
 BUp) one BUp $S --test-m0 7 --test-g0 104854119/1000000;;
 E0) raw E0 $P;;
 E1) raw E1 $P --test-r '' --test-m0 7 --test-f 4,3,2,1 --test-g0 100/1 --test-out $O/E1;;
 E2) raw E2 $P --test-m0 7 --test-r;;
 E3) raw E3 $P --test-m0 7 --test-f 4,3,2,1;;
 E4) raw E4 $P --test-r 12 --test-m0 7 --test-g0 '' --test-out $O/E4;;
 E5) fresh; raw E5 $A --launch-r9 --test-r 12;;
 E6) fresh; raw E6 $A --test-r --launch-r9;;
 E7) raw E7 $P --test-r 12 --freeze-commit cfc57befadcb61fb36b992af841941adaecd3fd0 --test-out $O/E7;;
 E8) fresh; raw E8 $A --launch-r9 --test-census;;
 E9) raw E9 $P --bogus;;
 E10) fresh; raw E10 $A --launch-r9 --test-limit-kb 5000;;
 E11) raw E11 $P --test-r 12 --test-m0 7 --test-limit-kb 5k --test-out $O/E11;;
 E12) raw E12 $P $S --test-m0 7 --test-g0 100/1 --test-out relative/E12;;
 E13) fresh; raw E13 $A $S --test-m0 6 --test-g0 100/1 --test-out $O/../atkc/pkg/work/rehT7d; ls -d $A/work/rehT7d 2>&1 | cut -c1-80;;
 E14) raw E14 $P $S --test-m0 6 --test-g0 100/1 --test-out /root/floor-v2/repo/rehE14; ls -d /root/floor-v2/repo/rehE14 2>&1 | cut -c1-80;;
 E15) rm -rf $O/E15 $O/E15.*; argstr BASH_ENV=FILE $S --test-m0 7 --test-g0 100/1 > $O/E15.args; : > $AT/benv.sh
      BASH_ENV=$AT/benv.sh bash $P/final/tools/run_floor.sh $S --test-m0 7 --test-g0 100/1 --test-out $O/E15 > $O/E15.stdout.txt 2>&1; echo $? > $O/E15.rc; fin E15;;
 E16) rm -rf $O/E16 $O/E16.*; argstr PYTHONPATH=/x $S --test-m0 7 --test-g0 100/1 > $O/E16.args
      PYTHONPATH=/x bash $P/final/tools/run_floor.sh $S --test-m0 7 --test-g0 100/1 --test-out $O/E16 > $O/E16.stdout.txt 2>&1; echo $? > $O/E16.rc; fin E16;;
 E17) rm -rf $O/E17 $O/E17.*; argstr LD_PRELOAD=/x $S --test-m0 7 --test-g0 100/1 > $O/E17.args
      env LD_PRELOAD=/nonexistent/x.so bash $P/final/tools/run_floor.sh $S --test-m0 7 --test-g0 100/1 --test-out $O/E17 > $O/E17.stdout.txt 2>/dev/null; echo $? > $O/E17.rc; fin E17;;
 AB) # absolute run directory and tool paths: called by a relative path from another working directory, with a hostile PATH and HOME
     rm -rf $O/AB $O/AB.*; fresh; argstr cwd=/_PATH=/root/floor-v2/atkc/fakebin:PATH_HOME=/nonexistent_relative_launcher_path $K > $O/AB.args
     mkdir -p $AT/fakebin; for t in python3 sha256sum git timeout setsid cargo rustc; do printf '%s\n' '#!/bin/bash' "echo $t >> $O/AB.fakecalls" 'exit 0' > $AT/fakebin/$t; chmod +x $AT/fakebin/$t; done
     ( cd / && PATH=$AT/fakebin:$PATH HOME=/nonexistent /usr/bin/bash ${A#/}/final/tools/run_floor.sh $K --test-out $O/AB > $O/AB.stdout.txt 2>&1; echo $? > $O/AB.rc ); fin AB
     echo "fake_program_calls=$([ -f $O/AB.fakecalls ] && grep -c . $O/AB.fakecalls || echo 0)" | tee $O/AB.fake.txt
     grep '^START|' $O/AB/log/run.log | grep -o 'run_directory=[^|]*'; grep -c '^TOOLPATH|' $O/AB/log/run.log;;
 GC1) one GC1 $K --test-git-check;;
 GC2) # a clone whose files carry another mode than the commit: the checkout check refuses it
     rm -rf $AT/gc $O/GC2 $O/GC2.*; mkdir -p $AT/gc; tar -C $P --exclude=./work/design/rs/target -cf - . | tar -C $AT/gc -xf -
     mkdir -p $AT/gc/work/design/rs/target/release; cp -p $P/work/design/rs/target/release/floorcert $AT/gc/work/design/rs/target/release/
     ( cd $AT/gc && git init -q . && git -c user.name=x -c user.email=x@x add -A . ':!work/design/rs/target' && git -c user.name=x -c user.email=x@x commit -q -m x && chmod 755 final/CHANGES.txt )
     argstr $K --test-git-check on_a_scratch_git_checkout_with_one_file_mode_changed > $O/GC2.args
     bash $AT/gc/final/tools/run_floor.sh $K --test-git-check --test-out $O/GC2 > $O/GC2.stdout.txt 2>&1; echo $? > $O/GC2.rc; fin GC2;;
 GC3) # the same scratch checkout owned by another user: git reports dubious ownership
     [ -d $AT/gc/.git ] || { echo "GC2 first"; exit 1; }
     rm -rf $O/GC3 $O/GC3.*; chmod 644 $AT/gc/final/CHANGES.txt; chown -R nobody $AT/gc
     argstr $K --test-git-check on_a_scratch_git_checkout_owned_by_another_user > $O/GC3.args
     bash $AT/gc/final/tools/run_floor.sh $K --test-git-check --test-out $O/GC3 > $O/GC3.stdout.txt 2>&1; echo $? > $O/GC3.rc; fin GC3; chown -R root $AT/gc;;
 RC) : > $O/RCHECK.txt
     for r in 9 9/1 19/2 10 8 81/10 79/10 10000001/1000000 7999999/1000000 12 21/2 13 x '' -9; do
       python3 -I -B $P/final/tools/floor_eval.py rcheck r="$r" > $O/rc.tmp 2>&1; echo "RCHECK|r=${r:-EMPTY}|exit=$?|out=$(tail -1 $O/rc.tmp | tr '|' ':' | tr ' ' '_' | cut -c1-90)|json=0" >> $O/RCHECK.txt
     done; rm -f $O/rc.tmp; cat $O/RCHECK.txt;;
 LK1) fresh; raw LK1 $A $S --test-m0 7 --test-g0 100/1 --test-out $O/LK1; grep '^PINCHECK|id=034' $O/LK1/log/pincheck_1.txt | cut -c1-200;;
 LK2) fresh; rm $A/final/link/PREDICT-S3-3X4-R9-WILSON-FESHBACH-AMPLITUDE-20261109.hbp
      raw LK2 $A $S --test-m0 7 --test-g0 100/1 --test-out $O/LK2; grep '^PINCHECK|id=034' $O/LK2/log/pincheck_1.txt | cut -c1-200;;
 G1) atk G1 work/design/gate_required.sh fakegate $S --test-m0 8 --test-g0 100/1;;
 G2) atk G2 work/design/py/cert_gate.py append $S --test-m0 8 --test-g0 100/1;;
 G3) atk G3 final/tools/floor_eval.py append $S --test-m0 8 --test-g0 100/1;;
 G4) atk G4 work/design/peak_rss.py append $S --test-m0 8 --test-g0 100/1;;
 G5) atk G5 final/tools/run_floor.sh append $S --test-m0 8 --test-g0 100/1;;
 G6) atk G6 work/design/rs/target/release/floorcert byte $S --test-m0 8 --test-g0 100/1;;
 G7) atk G7 $REC append $S --test-m0 8 --test-g0 100/1;;
 G8) atk G8 work/design/py/indep_verify.py append $S --test-m0 8 --test-g0 100/1;;
 EV0|EV1|EV2|EV3|EV4|EV5|EV6|EV7) ev $c;;
 MG) fresh; rm $A/work/design/gate_required.sh; raw MG $A $S --test-m0 7 --test-g0 100/1 --test-out $O/MG;;
 Y1) atk Y1 work/design/gate_required.sh replay $K;;
 Y1b) atk Y1b work/design/gate_required.sh empty $K;;
 R1) one R1 $S --test-m0 7,8 --test-g0 1045/10 --test-limit-kb 5000;;
 R2) one R2 $S --test-m0 7,8 --test-g0 100/1 --test-limit-kb 5000 --test-hang 1:cert;;
 R3) one R3 $S --test-m0 7,8 --test-g0 1045/10 --test-limit-kb 15000;;
 PQ) one PQ --test-r 12 --test-m0 6,7,9 --test-f '1;4,3,2,1' --test-g0 1045/10 --test-limit-kb 23000
     grep -E '^(STEP|PREREQ|DECISION|LIMIT)' $O/PQ.stdout.txt | cut -c1-260; grep -h '^PEAK_RSS\|^MEM' $O/PQ/log/m9_rowhash.txt $O/PQ/log/m9_rowsonly.txt | cut -c1-160;;
 PQ0) one PQ0 --test-r 12 --test-m0 6,7,9 --test-f '1;4,3,2,1' --test-g0 1045/10
     grep -E '^(STEP|PREREQ|DECISION|LIMIT)' $O/PQ0.stdout.txt | cut -c1-260;;
 F3) one F3 $S --test-m0 7,8,9 --test-g0 100/1 --test-hang 1:cert,2:cert
     grep -E '^(STEP|PREREQ|DECISION|LIMIT)' $O/F3.stdout.txt | cut -c1-260;;
 LIM) : > $O/LIMCHECK.txt
     for spec in "mode=r9 limkb=5000" "limkb=5000" "mode=test limkb=0" "mode=test limkb=abc" "mode=test limkb=2097153"; do
       python3 -I -B $P/final/tools/floor_eval.py opfail out=$O/absent m0=7 why=x $spec > $O/rc.tmp 2>&1; x=$?; echo "LIMCHECK|args=$(echo $spec | tr ' ' ',')|exit=$x|out=$(tail -1 $O/rc.tmp | tr '|' ':' | tr ' ' '_' | cut -c1-90)|json=0" >> $O/LIMCHECK.txt
     done; rm -f $O/rc.tmp; cat $O/LIMCHECK.txt;;
 D1) one D1 --test-r 21/2 --test-m0 11 --test-g0 99/1 --test-census;;
 *) echo "unknown case $c";;
esac; done
echo "leftover_mounts=$(grep -c floor-run /proc/mounts)"
