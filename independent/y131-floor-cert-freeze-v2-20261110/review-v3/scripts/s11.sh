cd /root/floor-v2/repo
rm -rf /mnt/c/tmp/opus55/floor-v2-final/winrepo; mkdir -p /mnt/c/tmp/opus55/floor-v2-final/winrepo
git archive 3b91d1a047d7485693c754ece8c7c18f43fbf326 | tar -x -C /mnt/c/tmp/opus55/floor-v2-final/winrepo
git ls-tree -r 3b91d1a0 --name-only | grep -i 'FLOAT-EVIDENCE\|no_float_gate'
for c in e74d8a46 cfc57bef 3b91d1a0; do git rev-parse $c:FLOAT-EVIDENCE.txt 2>/dev/null || git ls-tree -r $c | grep FLOAT-EVIDENCE; done
git diff --stat e74d8a46 3b91d1a0 -- FLOAT-EVIDENCE.txt native | tail -1
