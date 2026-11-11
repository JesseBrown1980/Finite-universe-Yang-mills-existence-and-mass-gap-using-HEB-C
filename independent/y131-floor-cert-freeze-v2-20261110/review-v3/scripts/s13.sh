for R in /mnt/c/tmp/opus55/floor-v2-final/winclone/independent/y131-floor-cert-freeze-v2-20261110 /root/floor-v2-final/head/independent/y131-floor-cert-freeze-v2-20261110; do
 cd $R; python3 -I -B final/tools/lint_hbp.py final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp $R > /root/floor-v2-final/lint.$(basename $(dirname $(dirname $R))).out 2>&1
 grep -E '^LINT' /root/floor-v2-final/lint.$(basename $(dirname $(dirname $R))).out | cut -c1-200
 sha256sum final/tools/lint_hbp.py | cut -c1-64
done
diff <(grep '^ERROR' /root/floor-v2-final/lint.winclone.out) <(grep '^ERROR' /mnt/c/tmp/opus55/floor-v2-final/winclone/independent/y131-floor-cert-freeze-v2-20261110/final/tools/lint_result.txt) && echo ERROR_LINES_IDENTICAL
