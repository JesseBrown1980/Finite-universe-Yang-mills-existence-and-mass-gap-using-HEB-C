V=/root/floor-v6-verify
bash /mnt/c/tmp/opus55/floor-v2-verify6/scripts/e_exp0.sh > $V/exp0.txt 2>&1
bash /mnt/c/tmp/opus55/floor-v2-verify6/scripts/b_build.sh > $V/b_build.out 2>&1
bash /mnt/c/tmp/opus55/floor-v2-verify6/scripts/b_clippy.sh > $V/b_clippy.out 2>&1
touch $V/a_run.done
