set -u
export PATH="$HOME/.cargo/bin:$PATH"
B=/root/floor-v2-final; PK=$B/pkg; OP=$B/oldpkg; RU=$B/runs; S=/mnt/c/tmp/opus55/floor-v2-final/scripts
export TMPDIR=$B/tmp
REL=work/design/gate_required.sh
BASE=(--test-r 12 --test-m0 7 --test-f '1;4,3,2,1' --test-g0 100/1)
fin() {
  echo "== $1 rc=$2 :: $(grep '^FLOOR_RUN|' $RU/$1.stdout | tail -1 | sed -E 's/\|HASHES=.*//' | grep -oE '^FLOOR_RUN\|CERTIFICATE=[A-Z]+\|PREDICTION=[A-Z]+\|DECISION=[A-Z]+\|GAMMA=[^|]*\|UPPER_BOUND=[^|]*\|certificate_reason=[^|]*|stage=[^|]*|reason=[^|]*|accepted_certificates=[0-9]+|stop=[^|]*|result=[A-Z]+|comparison=[A-Z_0-9]+' | tr '\n' ' ')"
  [ -f $RU/$1.fakecalls ] && echo "   fake_calls=$(grep -c . $RU/$1.fakecalls)"
  grep -h '^INTEGRITY' $RU/$1.stdout | head -2 | cut -c1-200
  return 0
}
run() { local n=$1 root=$2; shift 2; rm -rf $RU/$n $RU/$n.*; bash $root/final/tools/run_floor.sh "$@" --test-out $RU/$n > $RU/$n.stdout 2>&1; local rc=$?; fin $n $rc; }
waitline() { local i=0; while [ $i -lt 30000 ] && ! grep -qE "$2" "$1" 2>/dev/null; do i=$((i+1)); sleep 0.01; done; }
restore() { cp -p $B/head/independent/y131-floor-cert-freeze-v2-20261110/$1 $PK/$1; }
replay_gate() { printf '%s\n' '#!/bin/bash' "echo \"\$1\" >> $RU/$1.fakecalls" "cat \"$RU/$2/log/m7_gate_\$(basename \"\$1\").txt\"; exit 0"; }
privdir() { sed -n 's/^NOTE|binary=.*|private_directory=\([^|]*\)|.*/\1/p' $1 | head -1; }
for c in "$@"; do case $c in
 K0) run K0 $PK "${BASE[@]}";;
 X0) run X0 $OP "${BASE[@]}";;
 X1|Y1)
   root=$PK; ctl=K0; [ $c = X1 ] && { root=$OP; ctl=X0; }
   rm -rf $RU/$c $RU/$c.*; bash $root/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/$c > $RU/$c.stdout 2>&1 & lp=$!
   waitline $RU/$c/log/run.log '^NOTE\|binary='; cp -p $root/$REL $B/tmp/gate.save; replay_gate $c $ctl > $root/$REL
   wait $lp; rc=$?; cp -p $B/tmp/gate.save $root/$REL; fin $c $rc
   echo "   tree_gate_restored_sha16=$(sha256sum $root/$REL | cut -c1-16)";;
 T1)
   FH=$B/fh; rm -rf $FH; mkdir -p $FH/.cargo/bin; ln -s /root/.cargo/bin/rustup $FH/.cargo/bin/rustc; ln -s /root/.cargo/bin/rustup $FH/.cargo/bin/cargo
   printf '%s\n' '#!/bin/bash' 'case "$3" in */py/cert_gate.py) if [ "$4" != "--rows-only" ]; then echo "$4" >> '"$RU"'/T1.fakecalls; grep -v "^GATE_REQUIRED|" "'"$RU"'/K0/log/m7_gate_$(basename "$4").txt"; exit 0; fi;; esac' 'exec /usr/bin/python3 "$@"' > $FH/.cargo/bin/python3
   chmod +x $FH/.cargo/bin/python3
   rm -rf $RU/T1 $RU/T1.*; HOME=$FH RUSTUP_HOME=/root/.rustup CARGO_HOME=/root/.cargo bash $PK/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/T1 > $RU/T1.stdout 2>&1; fin T1 $?;;
 T2)
   printf '%s\n' 'case "$0" in */gate_required.sh) echo "$1" >> '"$RU"'/T2.fakecalls; cat "'"$RU"'/K0/log/m7_gate_$(basename "$1").txt"; exit 0;; esac' > $B/tmp/evil_bashenv.sh
   rm -rf $RU/T2 $RU/T2.*; BASH_ENV=$B/tmp/evil_bashenv.sh bash $PK/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/T2 > $RU/T2.stdout 2>&1; fin T2 $?;;
 T3)
   printf '%s\n' '#!/bin/bash' "mv -f $B/tmp/T3.genuine \"\$0\"" "echo \"\$1\" >> $RU/T3.fakecalls" "cat \"$RU/K0/log/m7_gate_\$(basename \"\$1\").txt\"; exit 0" > $B/tmp/T3.fake; chmod 555 $B/tmp/T3.fake
   rm -rf $RU/T3 $RU/T3.*; bash $PK/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/T3 > $RU/T3.stdout 2>&1 & lp=$!
   python3 -I -B $S/race.py $RU/T3/log/run.log '^INVOKE\|.*\|kind=cert\|' gate_required.sh $B/tmp/T3.fake $B/tmp/T3.genuine gate > $RU/T3.race 2>&1
   wait $lp; rc=$?; cat $RU/T3.race; fin T3 $rc
   grep -c '^TOOL_CLOSING' $RU/T3/log/run.log; grep '^TOOL_CLOSING|private_copy=gate' $RU/T3/log/run.log | cut -c1-200;;
 T4)
   printf '%s\n' 'import os, sys' "os.rename('$B/tmp/T4.genuine', sys.argv[0])" "open('$RU/T4.fakecalls','a').write(' '.join(sys.argv[1:3])+'\n')" 'print("FLOOR_RUN|CERTIFICATE=PASS|PREDICTION=CONFIRMED|DECISION=ABOVE|GAMMA=1000000/1|UPPER_BOUND=1000001/1|certificate_reason=FABRICATED_BY_A_SWAPPED_PRIVATE_EVALUATOR_COPY|json=0")' 'sys.exit(0)' > $B/tmp/T4.fake
   rm -rf $RU/T4 $RU/T4.*; bash $PK/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/T4 > $RU/T4.stdout 2>&1 & lp=$!
   python3 -I -B $S/race.py $RU/T4/log/run.log '^TOOL_CLOSING\|private_copy=floor_eval.py\|' floor_eval.py $B/tmp/T4.fake $B/tmp/T4.genuine now > $RU/T4.race 2>&1
   wait $lp; rc=$?; cat $RU/T4.race; fin T4 $rc; grep '^TOOL_CLOSING|private_copy=floor_eval' $RU/T4/log/run.log | cut -c1-200; ls $RU/T4/;;
 T5)
   rm -rf $RU/T5 $RU/T5.*; bash $PK/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/T5 > $RU/T5.stdout 2>&1 & lp=$!
   waitline $RU/T5/log/run.log '^NOTE\|binary='; pd=$(privdir $RU/T5/log/run.log)
   printf '%s\n' '#!/usr/bin/env python3' 'print("ROWHASH|x|sha256=0|")' > $PK/work/design/py/cert_gate.py; chmod u+w $pd/py/cert_gate.py; cp $PK/work/design/py/cert_gate.py $pd/py/cert_gate.py
   wait $lp; rc=$?; restore work/design/py/cert_gate.py; fin T5 $rc;;
 T7a) rm -rf $RU/T7a $RU/T7a.*; cp -a $RU/K0 $RU/T7a; bash $PK/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/T7a > $RU/T7a.stdout 2>&1; fin T7a $?;;
 T7b) rm -rf $RU/T7b $RU/T7b.*; ln -s $PK/work/run9 $RU/T7b; bash $PK/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/T7b > $RU/T7b.stdout 2>&1; fin T7b $?
   ls -ld $PK/work/run9 2>&1 | cut -c1-120; tail -2 $RU/T7b.stdout | cut -c1-200; rm -f $RU/T7b;;
 T7c) rm -f $RU/T7c; ln -s $RU/K0 $RU/T7c; bash $PK/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/T7c > $RU/T7c.stdout 2>&1; fin T7c $?; rm -f $RU/T7c;;
 T8)
   rm -rf $RU/T8 $RU/T8.*; bash $PK/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/T8 > $RU/T8.stdout 2>&1 & lp=$!
   waitline $RU/T8/log/run.log '^NOTE\|binary='; pd=$(privdir $RU/T8/log/run.log)
   echo "# x" >> $pd/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp; wait $lp; fin T8 $?;;
 TO1)
   mkdir -p $B/byst; cp /bin/sleep $B/byst/floorcert; $B/byst/floorcert 900 & bp=$!; sleep 0.3
   rm -rf $RU/TO1 $RU/TO1.*; bash $PK/final/tools/run_floor.sh --test-r 12 --test-m0 7,8 --test-f 4,3,2,1 --test-g0 100/1 --test-hang-hard 1:cert --test-out $RU/TO1 > $RU/TO1.stdout 2>&1; rc=$?; fin TO1 $rc
   echo "BYSTANDER alive=$(kill -0 $bp 2>/dev/null && echo 1 || echo 0) comm=$(cat /proc/$bp/comm 2>/dev/null)"; kill $bp; wait $bp 2>/dev/null
   echo "LEFTOVER sleep20=$(pgrep -fc '^sleep 20$') trapTERM=$(pgrep -fc 'trap .. TERM') private_tools=$(pgrep -fc 'floor-run-tools')"
   grep -E '^(INVOKE|NOTE\|rerun)' $RU/TO1/log/run.log | grep -oE 'm0=[0-9]+\|kind=[a-z]+\|attempt=[0-9]\|rc=[0-9]+|time_limit_hit=[01]|own_process_group=[01]|rerun_once[^|]*' | tr '\n' ' '; echo;;
 TO2)
   rm -rf $RU/TO2 $RU/TO2.*; bash $PK/final/tools/run_floor.sh --test-r 12 --test-m0 7 --test-f 4,3,2,1 --test-g0 100/1 --test-hang 1:rowhash --test-out $RU/TO2 > $RU/TO2.stdout 2>&1; fin TO2 $?
   grep -E '^(INVOKE|NOTE\|rerun)' $RU/TO2/log/run.log | grep -oE 'm0=[0-9]+\|kind=[a-z]+\|attempt=[0-9]\|rc=[0-9]+|time_limit_hit=[01]|rerun_once[^|]*' | tr '\n' ' '; echo;;
 PQ)
   run PQ $PK --test-r 12 --test-m0 6,7,9 --test-f '1;4,3,2,1' --test-g0 1045/10 --test-limit-kb 23000
   grep -E '^(STEP|PREREQ|DECISION)' $RU/PQ.stdout | grep -oE '^(STEP|PREREQ|DECISION)\|[a-z_]*m0=[0-9]+|status=[A-Z]+|writer_peak_kB=[0-9]+|verifier_mem_max_kB=[0-9]+|resource_limit=[A-Z]+|next=[A-Z]+|bad=[^|]*' | tr '\n' ' '; echo
   grep -h '^PEAK_RSS\|^MEM' $RU/PQ/log/m9_rowhash.txt $RU/PQ/log/m9_rowsonly.txt;;
 R1) run R1 $PK --test-r 12 --test-m0 7,8 --test-f 4,3,2,1 --test-g0 1045/10 --test-limit-kb 5000; grep -oE 'steps_run=[^|]*' $RU/R1.stdout | tail -1;;
 BND)
   fl=$(grep '^FLOOR_RUN|' $RU/K0.stdout | tail -1); G=$(echo "$fl" | sed -n 's/.*|GAMMA=\([0-9/]*\)|.*/\1/p'); U=$(echo "$fl" | sed -n 's/.*|UPPER_BOUND=\([0-9/]*\)|.*/\1/p')
   echo "K0 G=$G U=$U"; Gn=${G%/*}; Gd=${G#*/}; Un=${U%/*}; Ud=${U#*/}
   run BA $PK --test-r 12 --test-m0 7 --test-f '1;4,3,2,1' --test-g0 $G
   run BAm $PK --test-r 12 --test-m0 7 --test-f '1;4,3,2,1' --test-g0 $((Gn*10+1))/$((Gd*10))
   run BU $PK --test-r 12 --test-m0 7 --test-f '1;4,3,2,1' --test-g0 $U
   run BUp $PK --test-r 12 --test-m0 7 --test-f '1;4,3,2,1' --test-g0 $((Un*10+1))/$((Ud*10));;
esac; done
echo DONE
