set -u
export PATH="$HOME/.cargo/bin:$PATH"
PK=/root/floor-v2-verify/clone/independent/y131-floor-cert-freeze-v2-20261110
R=/root/floor-v2-verify/reh; FB=$PK/work/design/rs/target/release/floorcert
cp $FB /root/floor-v2-verify/fb.bak
rm -rf $R/L8
bash $PK/final/tools/run_floor.sh --test-r 12 --test-m0 7,8 --test-f '1;4,3,2,1' --test-g0 1045/10 --test-out $R/L8 > $R/L8.stdout 2>&1 & LP=$!
i=0; until grep -q 'kind=cert|attempt=1' $R/L8/log/run.log 2>/dev/null; do sleep 0.05; i=$((i+1)); [ $i -gt 6000 ] && break; done
printf 'x' >> $FB; echo "append_rc=$? sha16_now=$(sha256sum $FB | cut -c1-16)"
wait $LP; echo "rc=$?"
grep -E '^(NOTE\|before|STEP|DECISION)' $R/L8.stdout | cut -c1-160; tail -1 $R/L8.stdout | sed -E 's/\|scope=.*(accepted_certificates=[0-9]+).*(\|stop=[^|]*).*/|\1\2/'
cp /root/floor-v2-verify/fb.bak $FB; sha256sum $FB | cut -c1-16
