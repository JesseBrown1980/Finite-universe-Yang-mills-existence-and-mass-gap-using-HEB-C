#!/bin/bash
S=/mnt/c/tmp/opus55/floor-v2
T=/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/final/tools
cat $S/fe_a.py $S/fe_b.py $S/fe_c.py | tr -d '\r' > $T/floor_eval.py
tr -d '\r' < $S/run_floor.sh > $T/run_floor.sh
chmod 755 $T/run_floor.sh $T/floor_eval.py
bash -n $T/run_floor.sh; echo "bash_n=$?"
python3 -I -B -c "import ast,sys;ast.parse(open(sys.argv[1]).read());print('ast_ok')" $T/floor_eval.py
sha256sum $T/run_floor.sh $T/floor_eval.py; wc -l $T/run_floor.sh $T/floor_eval.py
ls /root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/work/
cd /root/floor-v2/repo && git add -- independent/y131-floor-cert-freeze-v2-20261110/final/tools/floor_eval.py && python3 -I -X utf8 native/scripts/no_float_gate.py . 2>&1 | tail -4
tail -2 /root/floor-v2/e3_fs_log.txt
