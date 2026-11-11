#!/bin/bash
# Second correction round: the verifier's attacks (scripts/attacks.sh of the final-head verification) run again.
#   T1 T2 T3 T4 T5 T7a T7b T7c T8 : against the launcher of this round (a byte copy of the freeze folder, no git data).
#   XK XT1 XT2 XT3 XT4            : the same commands against the launcher of 3b91d1a0 (the exploits as found).
#   N1 N2                          : a root process that enters the launcher's mount namespace and rewrites a tool there.
# Paths are this seat's; the commands are the verifier's. Test mode at excluded r only.
set -u
P=${PKG:-/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110}
B=/root/floor-v2/atkc; PK=$B/tpkg; OP=$B/oldpkg; RU=/root/floor-v2/rehc; S=/mnt/c/tmp/opus55/floor-v2
C2=3b91d1a047d7485693c754ece8c7c18f43fbf326
V=independent/y131-floor-cert-freeze-v2-20261110
mkdir -p $B/tmp $RU; export TMPDIR=$B/tmp
REL=work/design/gate_required.sh
BASE=(--test-r 12 --test-m0 7 --test-f '1;4,3,2,1' --test-g0 100/1)
newpkg() { rm -rf $PK; mkdir -p $PK; tar -C $P --exclude=./work/design/rs/target --exclude=./work/run9 -cf - . | tar -C $PK -xf -
  mkdir -p $PK/work/design/rs/target/release; cp -p $P/work/design/rs/target/release/floorcert $PK/work/design/rs/target/release/; }
oldpkg() { rm -rf $OP $B/old; mkdir -p $OP $B/old; git -C /root/floor-v2/repo archive $C2 $V | tar -x -C $B/old
  tar -C $B/old/$V -cf - . | tar -C $OP -xf -; mkdir -p $OP/work/design/rs/target/release; cp -p $P/work/design/rs/target/release/floorcert $OP/work/design/rs/target/release/; }
fin() { echo "== $1 rc=$(cat $RU/$1.rc) :: $(grep '^FLOOR_RUN|' $RU/$1.stdout.txt | tail -1 | sed 's/|HASHES=.*//' | cut -c1-420)"
  local n=0; [ -f $RU/$1.fakecalls ] && n=$(grep -c . $RU/$1.fakecalls)
  echo "ATTACK|case=$1|launcher_sha16=$(sha256sum $2/final/tools/run_floor.sh | cut -c1-16)|fake_calls=$n|$3|json=0" | tee $RU/$1.attack.txt
  grep -h '^INTEGRITY' $RU/$1.stdout.txt | head -2 | cut -c1-200; return 0; }
argstr() { local s="" x; for x in "$@"; do s="${s:+${s}_}$x"; done; echo "$s" > $RU/$N.args; }
waitline() { local i=0; while [ $i -lt 30000 ] && ! grep -qE "$2" "$1" 2>/dev/null; do i=$((i+1)); sleep 0.01; done; }
privdir() { sed -n 's/^NOTE|binary=.*|private_directory=\([^|]*\)|.*/\1/p' $1 | head -1; }
for c in "$@"; do
 N=$c; root=$PK; ctl=K0
 case $c in X*) root=$OP; ctl=XK; [ -d $OP/final ] || oldpkg;; *) newpkg;; esac
 rm -rf $RU/$c $RU/$c.*
 case $c in
 XK) argstr "${BASE[@]}"; bash $root/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/$c > $RU/$c.stdout.txt 2>&1; echo $? > $RU/$c.rc; fin $c $root what=control_run_of_the_launcher_of_3b91d1a0;;
 T1|XT1)
   FH=$B/fh; rm -rf $FH; mkdir -p $FH/.cargo/bin; ln -s /root/.cargo/bin/rustup $FH/.cargo/bin/rustc; ln -s /root/.cargo/bin/rustup $FH/.cargo/bin/cargo
   printf '%s\n' '#!/bin/bash' 'case "$3" in */py/cert_gate.py) if [ "$4" != "--rows-only" ]; then echo "$4" >> '"$RU/$c"'.fakecalls; grep -v "^GATE_REQUIRED|" "'"$RU/$ctl"'/log/m7_gate_$(basename "$4").txt"; exit 0; fi;; esac' 'exec /usr/bin/python3 "$@"' > $FH/.cargo/bin/python3
   chmod +x $FH/.cargo/bin/python3
   argstr HOME=FAKEHOME_with_.cargo/bin/python3_a_fake_verifier PATH=FAKEHOME/.cargo/bin:PATH "${BASE[@]}"
   PATH="$FH/.cargo/bin:$PATH" HOME=$FH RUSTUP_HOME=/root/.rustup CARGO_HOME=/root/.cargo bash $root/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/$c > $RU/$c.stdout.txt 2>&1; echo $? > $RU/$c.rc
   fin $c $root what=T1_a_program_named_python3_in_HOME/.cargo/bin_that_replays_a_verifier_log;;
 T2|XT2)
   printf '%s\n' 'case "$0" in */gate_required.sh) echo "$1" >> '"$RU/$c"'.fakecalls; cat "'"$RU/$ctl"'/log/m7_gate_$(basename "$1").txt"; exit 0;; esac' > $B/tmp/evil_bashenv.sh
   argstr BASH_ENV=FILE_that_replays_a_gate_log_when_the_gate_driver_starts "${BASE[@]}"
   PATH="/root/.cargo/bin:$PATH" BASH_ENV=$B/tmp/evil_bashenv.sh bash $root/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/$c > $RU/$c.stdout.txt 2>&1; echo $? > $RU/$c.rc
   fin $c $root what=T2_BASH_ENV_names_a_file_that_replays_a_gate_log;;
 T2b)
   printf '%s\n' 'case "$0" in */gate_required.sh) echo "$1" >> '"$RU/$c"'.fakecalls; cat "'"$RU/$ctl"'/log/m7_gate_$(basename "$1").txt"; exit 0;; esac' > $B/tmp/evil_bashenv.sh
   argstr the_second_stage_started_directly_with_BASH_ENV_in_its_environment "${BASE[@]}"
   BASH_ENV=$B/tmp/evil_bashenv.sh FLOOR_STAGE=2 FLOOR_ROOT=$root PATH=/usr/bin:/bin LANG=C /usr/bin/bash --noprofile --norc -c "$(cat $root/final/tools/run_floor.sh)" run_floor.sh "${BASE[@]}" --test-out $RU/$c > $RU/$c.stdout.txt 2>&1; echo $? > $RU/$c.rc
   fin $c $root what=T2b_stage_2_entered_directly_with_BASH_ENV_set;;
 T3|XT3)
   printf '%s\n' '#!/bin/bash' "mv -f $B/tmp/$c.genuine \"\$0\"" "echo \"\$1\" >> $RU/$c.fakecalls" "cat \"$RU/$ctl/log/m7_gate_\$(basename \"\$1\").txt\"; exit 0" > $B/tmp/$c.fake; chmod 555 $B/tmp/$c.fake
   argstr "${BASE[@]}" with_race.py_swapping_the_private_gate_driver_between_its_hash_and_its_start
   PATH="/root/.cargo/bin:$PATH" bash $root/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/$c > $RU/$c.stdout.txt 2>&1 & lp=$!
   timeout 600 python3 -I -B $S/race_v.py $RU/$c/log/run.log '^INVOKE\|.*\|kind=cert\|' gate_required.sh $B/tmp/$c.fake $B/tmp/$c.genuine gate > $RU/$c.race.txt 2>&1
   wait $lp; echo $? > $RU/$c.rc; tail -1 $RU/$c.race.txt | cut -c1-200
   fin $c $root "what=T3_swap_of_the_private_gate_driver_after_its_hash|race=$(tail -1 $RU/$c.race.txt | tr '|' ':' | tr ' ' '_' | cut -c1-120)";;
 T4|XT4)
   printf '%s\n' 'import os, sys' "os.rename('$B/tmp/$c.genuine', sys.argv[0])" "open('$RU/$c.fakecalls','a').write(' '.join(sys.argv[1:3])+'\n')" 'print("FLOOR_RUN|CERTIFICATE=PASS|PREDICTION=CONFIRMED|DECISION=ABOVE|GAMMA=1000000/1|UPPER_BOUND=1000001/1|certificate_reason=FABRICATED_BY_A_SWAPPED_PRIVATE_EVALUATOR_COPY|json=0")' 'sys.exit(0)' > $B/tmp/$c.fake
   argstr "${BASE[@]}" with_race.py_swapping_the_private_evaluator_copy_before_the_final_call
   PATH="/root/.cargo/bin:$PATH" bash $root/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/$c > $RU/$c.stdout.txt 2>&1 & lp=$!
   timeout 600 python3 -I -B $S/race_v.py $RU/$c/log/run.log '^TOOL_CLOSING\|private_copy=floor_eval.py\|' floor_eval.py $B/tmp/$c.fake $B/tmp/$c.genuine now > $RU/$c.race.txt 2>&1
   wait $lp; echo $? > $RU/$c.rc; tail -1 $RU/$c.race.txt | cut -c1-200
   fin $c $root "what=T4_swap_of_the_private_evaluator_copy_before_the_final_line|race=$(tail -1 $RU/$c.race.txt | tr '|' ':' | tr ' ' '_' | cut -c1-120)";;
 T5)
   argstr "${BASE[@]}" with_cert_gate.py_of_the_tree_and_of_the_private_directory_replaced_after_the_binary_line
   bash $root/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/$c > $RU/$c.stdout.txt 2>&1 & lp=$!
   waitline $RU/$c/log/run.log '^NOTE\|binary='; pd=$(privdir $RU/$c/log/run.log)
   printf '%s\n' '#!/usr/bin/env python3' 'print("ROWHASH|x|sha256=0|")' > $PK/work/design/py/cert_gate.py; chmod u+w $pd/py/cert_gate.py 2>/dev/null; cp $PK/work/design/py/cert_gate.py $pd/py/cert_gate.py 2>/dev/null; w=$?
   wait $lp; echo $? > $RU/$c.rc; fin $c $root "what=T5_tree_file_and_private_copy_of_cert_gate.py_replaced|write_into_the_private_directory_exit=$w";;
 T7a) argstr "${BASE[@]}" run_directory_already_holds_a_finished_run; cp -a $RU/K0 $RU/$c
   bash $root/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/$c > $RU/$c.stdout.txt 2>&1; echo $? > $RU/$c.rc; fin $c $root what=T7a_existing_run_directory;;
 T7b) argstr "${BASE[@]}" run_directory_is_a_symbolic_link_to_work/run9; ln -s $PK/work/run9 $RU/$c
   bash $root/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/$c > $RU/$c.stdout.txt 2>&1; echo $? > $RU/$c.rc; rm -f $RU/$c
   fin $c $root "what=T7b_symbolic_link_to_work/run9|work_run9_exists=$([ -e $PK/work/run9 ] && echo 1 || echo 0)";;
 T7c) argstr "${BASE[@]}" run_directory_is_a_symbolic_link_to_a_finished_run; ln -s $RU/K0 $RU/$c
   bash $root/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/$c > $RU/$c.stdout.txt 2>&1; echo $? > $RU/$c.rc; rm -f $RU/$c; fin $c $root what=T7c_symbolic_link_to_a_finished_run;;
 T8)
   argstr "${BASE[@]}" with_one_line_appended_to_the_private_record_copy_after_the_binary_line
   bash $root/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/$c > $RU/$c.stdout.txt 2>&1 & lp=$!
   waitline $RU/$c/log/run.log '^NOTE\|binary='; pd=$(privdir $RU/$c/log/run.log)
   ( echo "# x" >> $pd/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp ) 2>/dev/null; w=$?
   wait $lp; echo $? > $RU/$c.rc; fin $c $root "what=T8_append_to_the_private_record_copy|write_into_the_private_directory_exit=$w";;
 N1|N2)
   tgt=gate_required.sh; [ $c = N2 ] && tgt=PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
   argstr "${BASE[@]}" with_a_root_process_entering_the_mount_namespace_by_nsenter,_remounting_the_tool_tmpfs_writable_and_appending_one_line_to_$tgt
   bash $root/final/tools/run_floor.sh "${BASE[@]}" --test-out $RU/$c > $RU/$c.stdout.txt 2>&1 & lp=$!
   waitline $RU/$c/log/run.log '^NOTE\|binary='; pd=$(privdir $RU/$c/log/run.log)
   lpid=$(sed -n 's/^NOTE|environment=.*|launcher_pid=\([0-9]*\)|.*/\1/p' $RU/$c/log/run.log | head -1)
   nsenter -t $lpid -m -- /usr/bin/bash --noprofile --norc -c "mount -o remount,rw $pd && echo '# x' >> $pd/$tgt" 2> $RU/$c.nsenter.txt; w=$?
   wait $lp; echo $? > $RU/$c.rc; fin $c $root "what=${c}_nsenter_into_the_launcher_namespace_and_append_to_$tgt|nsenter_exit=$w";;
 *) echo "unknown $c";;
 esac
done
echo "leftover_mounts=$(grep -c floor-run /proc/mounts)"
