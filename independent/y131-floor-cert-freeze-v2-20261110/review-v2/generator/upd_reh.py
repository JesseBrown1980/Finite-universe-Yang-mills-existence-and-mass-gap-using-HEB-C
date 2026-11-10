import io
T="C:/tmp/opus55/floor-v2/"
s=io.open(T+"reh_b.bak1",encoding="utf-8",newline="").read().replace("\r\n","\n")
def rep(a,b):
    global s
    assert s.count(a)==1,(s.count(a),a[:60]); s=s.replace(a,b)
rep("mkdir -p $O $AT\n", """OLD=$AT/oldclone
C1=cfc57befadcb61fb36b992af841941adaecd3fd0
V=independent/y131-floor-cert-freeze-v2-20261110
mkdir -p $O $AT /root/floor-v2/tmp
export TMPDIR=/root/floor-v2/tmp
oldclone() { # a clone of the local repository checked out at the first version 2 commit, with the pin-free binary of row 016
  if [ "$(git -C $OLD rev-parse HEAD 2>/dev/null)" != "$C1" ]; then
    rm -rf $OLD; git clone -q --no-hardlinks /root/floor-v2/repo $OLD && git -C $OLD checkout -q --detach $C1 || { echo "clone failed"; exit 1; }
  fi
  git -C $OLD checkout -q -- $V
  mkdir -p $OLD/$V/work/design/rs/target/release; cp -p $P/work/design/rs/target/release/floorcert $OLD/$V/work/design/rs/target/release/
}
""")
# generalized attack
a0 = s.index("atk() {"); a1 = s.index('S="--test-r 12 --test-f 4,3,2,1"')
s = s[:a0] + r'''atk() { # NAME RELFILE HOW args... : run on the copy; once the binary line is logged, change RELFILE; put it back afterwards
  local n=$1 rel=$2 how=$3 lp i root=$A tgt pd; shift 3; rm -rf $O/$n $O/$n.*
  case $n in X*) oldclone; root=$OLD/$V;; *) fresh;; esac
  argstr "$@" > $O/$n.args
  bash $root/final/tools/run_floor.sh --test-out $O/$n "$@" > $O/$n.stdout.txt 2>&1 & lp=$!
  i=0; while [ $i -lt 3000 ] && ! grep -q '^NOTE|binary=' $O/$n/log/run.log 2>/dev/null; do i=$((i+1)); sleep 0.01; done
  tgt=$root/$rel
  if [ $how = private ]; then # the copy the launcher executes, in its private directory
    pd=$(sed -n 's/^NOTE|binary=.*|private_directory=\([^|]*\)|.*/\1/p' $O/$n/log/run.log | head -1)
    tgt=$pd/gate_required.sh; chmod u+w "$tgt"
  fi
  case $how in
    fakegate) printf '%s\n' '#!/bin/bash' 'echo "GATE_REQUIRED|PASS|cert=$1|cert_sha256=$(sha256sum "$1" | cut -d" " -f1)|rowhash=NONE|verifier_sha256=6043d089"' > $tgt;;
    replay|private) # the verifier's L1: a gate driver that replays the logs of the genuine run X0 and runs no verifier
      printf '%s\n' '#!/bin/bash' "echo \"\$1\" >> $O/$n.fakecalls" "cat \"$O/X0/log/m7_gate_\$(basename \"\$1\").txt\"; exit 0" > $tgt;;
    empty) printf '%s\n' '#!/bin/bash' "echo \"\$1\" >> $O/$n.fakecalls" 'exit 0' > $tgt;;
    append) echo "# one appended line" >> $tgt;;
    byte) printf 'X' >> $tgt;;
  esac
  echo "ATTACK|file=$([ $how = private ] && echo PRIVATE_COPY/gate_required.sh || echo $rel)|how=$how|launcher_sha16=$(sha256sum $root/final/tools/run_floor.sh | cut -c1-16)|changed_after_the_binary_line=1|sha256_after_change=$(sha256sum $tgt 2>/dev/null | cut -d' ' -f1)|json=0" > $O/$n.attack.txt
  wait $lp; echo $? > $O/$n.rc
  i=0; [ -f $O/$n.fakecalls ] && i=$(grep -c . $O/$n.fakecalls)
  case $n in X*) git -C $OLD checkout -q -- $V; echo "ATTACK_END|file=$rel|put_back=1|clone_tracked_files_changed=$(git -C $OLD status --porcelain --untracked-files=no -- $V | wc -l)|fake_gate_calls=$i|json=0" >> $O/$n.attack.txt;;
    *) cp -p $P/$rel $A/$rel
       echo "ATTACK_END|file=$rel|put_back=1|copy_equals_repository_file=$(cmp -s $P/$rel $A/$rel && echo 1 || echo 0)|fake_gate_calls=$i|json=0" >> $O/$n.attack.txt;;
  esac
  fin $n; grep '^INTEGRITY|' $O/$n.stdout.txt | cut -c1-260; tail -1 $O/$n.attack.txt
}
ev() { # NAME : the evaluator called directly on a copy of the finished run LK1, from a tool directory built here
  local c=$1 TD=$AT/evtools pd PS FS DS
  [ -f $O/LK1/FLOOR-RUN-RECEIPT.hbp ] || { echo "LK1 first"; exit 1; }
  fresh; rm -rf $O/$c $O/$c.*; cp -a $O/LK1 $O/$c; rm -f $O/$c/FLOOR-RUN-RECEIPT.hbp*
  rm -rf $TD; mkdir -p $TD/py
  cp $A/work/design/gate_required.sh $A/work/design/peak_rss.py $A/final/tools/floor_eval.py $A/$REC $TD/; cp $A/work/design/py/cert_gate.py $A/work/design/py/indep_verify.py $TD/py/
  pd=$(sed -n 's/^NOTE|binary=.*|private_directory=\([^|]*\)|.*/\1/p' $O/$c/log/run.log | head -1)
  sed -i -e "s#$pd#$TD#g" -e "s#$O/LK1/#$O/$c/#g" $O/$c/log/run.log
  PS=$(sha256sum $A/$REC | cut -d' ' -f1); FS=$(sha256sum $A/work/design/rs/target/release/floorcert | cut -d' ' -f1); DS=$(sha256sum $A/final/tools/run_floor.sh | cut -d' ' -f1)
  case $c in
    EV0) echo "evaluator_called_directly_on_a_copy_of_the_finished_run_LK1_(run_log_paths_rewritten_to_the_copy_and_to_a_tool_directory_built_for_this_call),_nothing_changed:_the_control" > $O/$c.args;;
    EV1) echo "# one appended line" >> $A/work/design/gate_required.sh; echo "as_EV0_with_work/design/gate_required.sh_of_the_tree_copy_changed" > $O/$c.args;;
    EV2) echo "# one appended line" >> $A/work/design/py/indep_verify.py; echo "as_EV0_with_work/design/py/indep_verify.py_of_the_tree_copy_changed" > $O/$c.args;;
    EV3) sed -i '/^INVOKE|.*|kind=gate|/d' $O/$c/log/run.log; echo "as_EV0_with_the_INVOKE_line_of_the_verifier_call_removed_from_the_run_log_(a_bypassed_gate)" > $O/$c.args;;
    EV4) echo "# one appended line" >> $TD/gate_required.sh; echo "as_EV0_with_the_executed_copy_of_gate_required.sh_changed" > $O/$c.args;;
    EV5) sed -i '/|kind=gate|/s/|rc=0|/|rc=1|/' $O/$c/log/run.log; echo "as_EV0_with_the_recorded_exit_code_of_the_verifier_call_set_to_1" > $O/$c.args;;
  esac
  ( cd $A
    python3 -I -B $TD/floor_eval.py step root=$A tools=$TD pred=$TD/${REC##*/} out=$O/$c m0=7 r=12 fspec=4,3,2,1 mode=test census=0 commit=NONE psha=$PS fbsha=$FS; echo "STEP_EXIT|$?"
    python3 -I -B $TD/floor_eval.py final root=$A tools=$TD out=$O/$c pred=$TD/${REC##*/} steps=7 g0=100/1 allowed=1 mode=test r=12 stop=DECIDED commit=NONE fbsha=$FS drvsha=$DS receipt=$O/$c/FLOOR-RUN-RECEIPT.hbp
    echo $? > $O/$c.rc ) > $O/$c.stdout.txt 2>&1
  fin $c; grep '^STEP|\|^STEP_EXIT' $O/$c.stdout.txt | cut -c1-330; grep 'ok=0' $O/$c/log/pincheck_closing.txt | cut -c1-200
}
''' + s[a1:]
e0 = s.index(" EV1|EV2) #"); e1 = s.index(" D1) one D1")
s = s[:e0] + r''' EV0|EV1|EV2|EV3|EV4|EV5) ev $c;;
 MG) fresh; rm $A/work/design/gate_required.sh; raw MG $A $S --test-m0 7 --test-g0 100/1 --test-out $O/MG;;
 X0) oldclone; rm -rf $O/X0 $O/X0.*; argstr --test-r 12 --test-f '1;4,3,2,1' --test-g0 100/1 --test-m0 7 > $O/X0.args
     bash $OLD/$V/final/tools/run_floor.sh --test-out $O/X0 --test-r 12 --test-f '1;4,3,2,1' --test-g0 100/1 --test-m0 7 > $O/X0.stdout.txt 2>&1; echo $? > $O/X0.rc; fin X0;;
 X1) atk X1 work/design/gate_required.sh replay --test-r 12 --test-f '1;4,3,2,1' --test-g0 100/1 --test-m0 7;;
 X1b) atk X1b work/design/gate_required.sh empty --test-r 12 --test-f '1;4,3,2,1' --test-g0 100/1 --test-m0 7;;
 Y1) atk Y1 work/design/gate_required.sh replay --test-r 12 --test-f '1;4,3,2,1' --test-g0 100/1 --test-m0 7;;
 Y1b) atk Y1b work/design/gate_required.sh empty --test-r 12 --test-f '1;4,3,2,1' --test-g0 100/1 --test-m0 7;;
 P1) atk P1 work/design/gate_required.sh private --test-r 12 --test-f '1;4,3,2,1' --test-g0 100/1 --test-m0 7;;
 R1) one R1 $S --test-m0 7,8 --test-g0 1045/10 --test-limit-kb 5000;;
 R2) one R2 $S --test-m0 7,8 --test-g0 100/1 --test-limit-kb 5000 --test-hang 1:cert;;
 R3) one R3 $S --test-m0 7,8 --test-g0 1045/10 --test-limit-kb 15000;;
 E10) fresh; raw E10 $A --launch-r9 --test-limit-kb 5000;;
 E11) raw E11 $P --test-r 12 --test-m0 7 --test-limit-kb 5k --test-out $O/E11;;
 LIM) : > $O/LIMCHECK.txt
     for spec in "mode=r9 limkb=5000" "limkb=5000" "mode=test limkb=0" "mode=test limkb=abc" "mode=test limkb=2097153"; do
       python3 -I -B $P/final/tools/floor_eval.py opfail out=$O/absent m0=7 why=x $spec > $O/rc.tmp 2>&1; x=$?; echo "LIMCHECK|args=$(echo $spec | tr ' ' ',')|exit=$x|out=$(tail -1 $O/rc.tmp | tr '|' ':' | tr ' ' '_' | cut -c1-90)|json=0" >> $O/LIMCHECK.txt
     done; rm -f $O/rc.tmp; cat $O/LIMCHECK.txt;;
''' + s[e1:]
rep(" D1) one D1 --test-r 21/2 --test-m0 11 --test-g0 99/1 --test-census;;\n", """ D1) one D1 --test-r 21/2 --test-m0 11 --test-g0 99/1 --test-census;;
 DX) one DX --test-r 21/2 --test-m0 11,12 --test-f 1 --test-g0 9938/100 --test-census;;
 D3) one D3 --test-r 21/2 --test-m0 11,12,13 --test-f 1 --test-g0 9938/100 --test-census --test-hang 1:cert,2:cert;;
""")
io.open(T+"reh_b.sh","w",encoding="utf-8",newline="\n").write(s)
print("ok")
