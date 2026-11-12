V=/root/floor-v6-verify; rm -rf $V/exp0; mkdir -p $V/exp0; git -C $V/repoE archive c8dbcdbf990114292313cbc410a745a14ba0b778 | tar -x -C $V/exp0; echo "exp0_files=$(find $V/exp0 -type f | wc -l)"
