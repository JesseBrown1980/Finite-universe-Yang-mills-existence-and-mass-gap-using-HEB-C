# live fault injections in test mode at r = 12 on my own clone; each restores the clone afterwards
set -u
export PATH="$HOME/.cargo/bin:$PATH"
CL=/root/floor-v2-verify/clone
PK=$CL/independent/y131-floor-cert-freeze-v2-20261110
REL=independent/y131-floor-cert-freeze-v2-20261110
R=/root/floor-v2-verify/reh
FB=$PK/work/design/rs/target/release/floorcert
L="bash $PK/final/tools/run_floor.sh --test-r 12 --test-f 1;4,3,2,1 --test-g0 100/1"
IFS_SAVE=$IFS
restore() { git -C $CL checkout -q -- $REL; git -C $CL status --short -- $REL | grep -v '^??' ; }
waitfor() { # file pattern
  local i=0; while [ $i -lt 6000 ]; do grep -qE "$2" "$1" 2>/dev/null && return 0; sleep 0.05; i=$((i+1)); done; echo "WAIT_TIMEOUT $1"; return 1; }
show() { # name
  echo "== $1 rc=$2"; grep -E '^(DECISION|STEP|INJECTED|NOTE\|rerun|INVOKE)' $R/$1.stdout | sed -E 's/\|argv=.*//' | cut -c1-200
  tail -1 $R/$1.stdout | sed -E 's/\|scope=.*(accepted_certificates=[0-9]+).*(\|stop=[^|]*).*/|\1\2/'
  grep -E '^ACCEPTED' $R/$1/FLOOR-RUN-RECEIPT.hbp 2>/dev/null | tr '\n' ' '; echo; }
go() { # name m0list [extra] -> runs launcher in background, sets LP
  local n=$1 m=$2; shift 2; rm -rf $R/$n; $L --test-m0 $m "$@" --test-out $R/$n > $R/$n.stdout 2>&1 & LP=$!; }
pre_gate_sha() { sha256sum $PK/work/design/gate_required.sh | cut -c1-16; }

# L1 replay gate: gate_required.sh replaced after the pin check by a script that replays A2's genuine logs
go L1 7; waitfor $R/L1/log/run.log '^NOTE\|binary=' 
cat > $PK/work/design/gate_required.sh <<'FAKE'
#!/bin/bash
cat "/root/floor-v2-verify/reh/A2/log/m7_gate_$(basename "$1").txt"; exit 0
FAKE
echo "L1 gate_required.sh during run sha16=$(pre_gate_sha) (row 020 0064ca4654aa8725)"
wait $LP; rc=$?; ngate=$(grep -c 'cert_gate' $R/L1/log/*gate*_a1.txt 2>/dev/null | head -1); show L1 $rc; restore
grep -h '^MEM' $R/L1/log/m7_gate_*.txt | head -2

# L1b gate script exits 0 printing nothing
go L1b 7; waitfor $R/L1b/log/run.log '^NOTE\|binary='
printf '#!/bin/bash\nexit 0\n' > $PK/work/design/gate_required.sh
wait $LP; show L1b $?; restore

# L2 verifier replaced after the pin check
go L2 7; waitfor $R/L2/log/run.log '^NOTE\|binary='
echo "# edited" >> $PK/work/design/py/cert_gate.py
wait $LP; show L2 $?; restore

# L3 pinned file altered before launch (row 024 NOTE.md)
echo " " >> $PK/work/design/NOTE.md
go L3 7; wait $LP; show L3 $?; grep 'ok=0' $R/L3/log/pincheck_1.txt | cut -c1-120; restore

# L7 certificate corrupted after the writer, before its gate
go L7 7; waitfor $R/L7/log/m7_cert_a1.txt '^PEAK_RSS'
echo "# appended" >> $R/L7/RUN7/cert_m7_r12_1_f4-3-2-1.txt
wait $LP; show L7 $?; grep -h '^GATE_REQUIRED' $R/L7/log/m7_gate_cert_m7_r12_1_f4-3-2-1.txt.txt | cut -c1-80

# L4 writer killed in both attempts (only one step allowed)
go L4 7; waitfor $R/L4/log/run.log 'INVOKE\|seq=1\|'
i=0; while ! pkill -KILL -x floorcert 2>/dev/null; do sleep 0.05; i=$((i+1)); [ $i -gt 2000 ] && break; done
waitfor $R/L4/log/run.log 'rerun_once'; i=0; while ! pkill -KILL -x floorcert 2>/dev/null; do sleep 0.05; i=$((i+1)); [ $i -gt 2000 ] && break; done
wait $LP; show L4 $?

# L6 one rerun for the whole run: injected rowhash crash consumes it, then the cert is killed once
rm -rf $R/L6; $L --test-m0 7 --test-crash 1:rowhash --test-out $R/L6 > $R/L6.stdout 2>&1 & LP=$!
waitfor $R/L6/log/run.log 'kind=rowhash\|attempt=2'; i=0; while ! pkill -KILL -x floorcert 2>/dev/null; do sleep 0.05; i=$((i+1)); [ $i -gt 2000 ] && break; done
wait $LP; show L6 $?

# L8 binary replaced between steps (row 018)
go L8 7,8 --test-g0 1045/10; waitfor $R/L8/log/run.log 'DECISION\|after_m0=7'
cp $FB /root/floor-v2-verify/fb.bak; printf 'x' >> $FB
wait $LP; show L8 $?; cp /root/floor-v2-verify/fb.bak $FB; sha256sum $FB | cut -c1-16
