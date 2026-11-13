#!/bin/bash
R=/tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/floor
P=/mnt/c/tmp/opus55/floor-freeze-verify/repo/independent/y131-floor-cert-freeze-20261110
mkdir -p $R && cp -r $P/work $P/final $R/
python3 -I -B $R/final/tools/lint_hbp.py $R/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp $R > /mnt/c/tmp/opus55/floor-freeze-verify/lint_committed.out 2>&1; echo lint_rc=$?
L=/mnt/c/tmp/opus55/floor-freeze-verify/lint_committed.out
grep -v LINT_RESULT $L | sed -E 's/^line [0-9]+: //' | sed -E 's/ (work|final|\.\.)\/.*//' | cut -c1-50 | sort | uniq -c | sort -rn | head
tail -1 $L
rm -rf /tmp/claude-0
