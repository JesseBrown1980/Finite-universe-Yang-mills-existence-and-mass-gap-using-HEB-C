set -u
V=/root/floor-v4-verify; F=$V/repoB/independent/y131-floor-cert-freeze-v2-20261110; O=$V/out/C; mkdir -p $O
cd $F
SRC=$(cat final/tools/run_floor.sh)
ARGS() { echo --test-r 12 --test-m0 7 --test-f 1 --test-g0 100/1 --test-out $O/$1; }
hostcnt() { grep -c floor-run /proc/1/mountinfo; }
report() { echo "CASE|id=$1|exit=$2|run_dir_exists=$([ -e $O/$1 ] && echo 1 || echo 0)|host_floor_run_mounts=$(hostcnt)|last=$(tail -1 $O/$1.out | cut -c1-260)|json=0"; }
# C1 direct, no unshare
env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2 FLOOR_ROOT=$F /usr/bin/bash --noprofile --norc -c "$SRC" run_floor.sh $(ARGS C1) > $O/C1.out 2>&1; report C1 $?
# C2 unshare shared
env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2 FLOOR_ROOT=$F /usr/bin/unshare -m --propagation shared /usr/bin/bash --noprofile --norc -c "$SRC" run_floor.sh $(ARGS C2) > $O/C2.out 2>&1; report C2 $?
# C2s unshare slave
env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2 FLOOR_ROOT=$F /usr/bin/unshare -m --propagation slave /usr/bin/bash --noprofile --norc -c "$SRC" run_floor.sh $(ARGS C2s) > $O/C2s.out 2>&1; report C2s $?
# C2u unshare unchanged
env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2 FLOOR_ROOT=$F /usr/bin/unshare -m --propagation unchanged /usr/bin/bash --noprofile --norc -c "$SRC" run_floor.sh $(ARGS C2u) > $O/C2u.out 2>&1; report C2u $?
# C3 parent shell inside the same private namespace
export SRC F O
/usr/bin/unshare -m --propagation private /usr/bin/bash --noprofile --norc -c 'env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2 FLOOR_ROOT=$F /usr/bin/bash --noprofile --norc -c "$SRC" run_floor.sh --test-r 12 --test-m0 7 --test-f 1 --test-g0 100/1 --test-out $O/C3; echo "inner_exit=$?"' > $O/C3.out 2>&1; report C3 $?
# C6 FLOOR_STAGE=2 in a normal call (bash FILE): stage 1 must take over -- runs a real small rehearsal
FLOOR_STAGE=2 env -i PATH=/usr/bin:/bin HOME=/root FLOOR_STAGE=2 BASH_EXECUTION_STRING=x bash final/tools/run_floor.sh $(ARGS C6) > $O/C6.out 2>&1; report C6 $?
# C7 bash -c with the text but no FLOOR_STAGE (stage 1 under -c)
env -i PATH=/usr/bin:/bin /usr/bin/bash --noprofile --norc -c "$SRC" run_floor.sh $(ARGS C7) > $O/C7.out 2>&1; report C7 $?
# C9 BASH_ENV in caller env
env -i PATH=/usr/bin:/bin BASH_ENV=/dev/null bash final/tools/run_floor.sh $(ARGS C9) > $O/C9.out 2>&1; report C9 $?
# C10 extra env name in direct entry inside a private ns (should be refused by the stage 2 whitelist)
env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2 FLOOR_ROOT=$F EXTRA=1 /usr/bin/unshare -m --propagation private /usr/bin/bash --noprofile --norc -c "$SRC" run_floor.sh $(ARGS C10) > $O/C10.out 2>&1; report C10 $?
# C8 symlinked run directory, and a symlink that resolves into the repository
ln -sfn $O $V/lnkout; ln -sfn $V/repoB $V/lnkrepo; ln -sfn $O/nowhere $O/C8L
env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $(ARGS C8L) > $O/C8L.out 2>&1; echo "CASE|id=C8L_symlink_as_run_dir|exit=$?|last=$(tail -1 $O/C8L.out | cut -c1-200)|json=0"
env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh --test-r 12 --test-m0 7 --test-f 1 --test-g0 100/1 --test-out $V/lnkrepo/xrun > $O/C8R.out 2>&1; echo "CASE|id=C8R_symlink_into_repo|exit=$?|exists=$([ -e $V/repoB/xrun ] && echo 1 || echo 0)|last=$(tail -1 $O/C8R.out | cut -c1-200)|json=0"
echo "git_status_repoB=$(cd $V/repoB && git status --porcelain | tr '\n' ' ')"
