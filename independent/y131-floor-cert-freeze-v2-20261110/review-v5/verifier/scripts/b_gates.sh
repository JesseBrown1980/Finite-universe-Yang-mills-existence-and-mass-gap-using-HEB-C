set -u
cd /root/floor-v4-verify/repoB
F=independent/y131-floor-cert-freeze-v2-20261110
python3 -I -X utf8 native/scripts/no_float_gate.py . > /root/floor-v4-verify/nofloat.txt 2>&1; echo "nofloat_exit=$?"; tail -5 /root/floor-v4-verify/nofloat.txt
head -30 $F/final/tools/lint_hbp.py | grep -i 'usage\|#' | head -12
cat $F/final/tools/lint_result.txt | head -30
