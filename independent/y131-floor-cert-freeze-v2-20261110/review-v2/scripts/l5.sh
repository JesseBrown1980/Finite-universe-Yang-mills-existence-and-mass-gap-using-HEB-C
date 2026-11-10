# L5: a time limit in one launcher run kills an unrelated process that is also named floorcert
set -u
export PATH="$HOME/.cargo/bin:$PATH"
PK=/root/floor-v2-verify/clone/independent/y131-floor-cert-freeze-v2-20261110
R=/root/floor-v2-verify/reh
mkdir -p /root/floor-v2-verify/bystander; cp /bin/sleep /root/floor-v2-verify/bystander/floorcert
/root/floor-v2-verify/bystander/floorcert 900 & BP=$!
echo "bystander pid=$BP name=$(cat /proc/$BP/comm) alive=$(kill -0 $BP 2>/dev/null && echo 1 || echo 0)"
rm -rf $R/L5
bash $PK/final/tools/run_floor.sh --test-r 12 --test-m0 7 --test-f '1;4,3,2,1' --test-g0 100/1 --test-hang 1:cert --test-out $R/L5 > $R/L5.stdout 2>&1; rc=$?
wait $BP 2>/dev/null; bs=$?
echo "launcher rc=$rc ; bystander wait status=$bs (137 = SIGKILL)"
grep -E '^(INJECTED|INVOKE|STEP|DECISION)' $R/L5.stdout | sed -E 's/\|argv=.*//' | cut -c1-200
tail -1 $R/L5.stdout | sed -E 's/\|scope=.*(accepted_certificates=[0-9]+).*(\|stop=[^|]*).*/|\1\2/'
