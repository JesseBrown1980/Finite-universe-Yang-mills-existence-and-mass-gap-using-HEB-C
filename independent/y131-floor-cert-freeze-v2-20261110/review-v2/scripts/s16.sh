A=/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-v2-20261110
cd /tmp 2>/dev/null || cd /root
python3 -I -B $A/final/tools/lint_hbp.py $A/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp $A > /root/floor-v2-verify/lint.out 2>&1; echo "rc=$?"
grep -E '^LINT' /root/floor-v2-verify/lint.out | cut -c1-300
grep -vE '^LINT' /root/floor-v2-verify/lint.out | sed -E 's/[=:].*//' | sort | uniq -c | head
