export PATH="$HOME/.cargo/bin:$PATH"
B=/root/floor-v2-final; export TMPDIR=$B/tmp
O=$B/runs/../pkg/work/rehT7d
rm -rf $B/pkg/work/rehT7d
bash $B/pkg/final/tools/run_floor.sh --test-r 12 --test-m0 6 --test-f 4,3,2,1 --test-g0 100/1 --test-out $O > $B/runs/T7d.stdout 2>&1 & lp=$!
i=0; while [ $i -lt 3000 ] && ! grep -q '^START' $B/pkg/work/rehT7d/log/run.log 2>/dev/null && kill -0 $lp 2>/dev/null; do i=$((i+1)); sleep 0.01; done
ls -d $B/pkg/work/rehT7d 2>&1; grep -c '^START' $B/pkg/work/rehT7d/log/run.log 2>/dev/null
wait $lp; echo "rc=$?"; tail -1 $B/runs/T7d.stdout | cut -c1-200
ls $B/pkg/work/rehT7d 2>&1 | head
cd $B/pkg && sha256sum -c FREEZE-PIN.sha256 2>/dev/null | grep -vc ': OK$'
rm -rf $B/pkg/work/rehT7d
