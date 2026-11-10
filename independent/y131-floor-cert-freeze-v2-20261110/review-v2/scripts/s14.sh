set -u
W=/mnt/c/tmp/opus55/floor-v2-verify/wincheck
rm -rf $W; mkdir -p $W
cd /root/floor-v2-verify/clone
git archive cfc57befadcb61fb36b992af841941adaecd3fd0 | tar -x -C $W
du -sh $W | cut -f1
git diff --stat e74d8a46 cfc57befadcb61fb36b992af841941adaecd3fd0 -- native/scripts/FLOAT-EVIDENCE.txt | tail -1; echo "fe_diff_done"
ls $W/native/scripts/no_float_gate.py
