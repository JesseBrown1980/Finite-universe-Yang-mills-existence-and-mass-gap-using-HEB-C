A=/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-v2-20261110
cat $A/review-v1/regression-v2/reg1.sh | head -70
echo =====
cat $A/review-v1/regression-v2/reg2.sh | head -50
V1=/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-20261110
find $V1 -name 'run_fix1.sh'
