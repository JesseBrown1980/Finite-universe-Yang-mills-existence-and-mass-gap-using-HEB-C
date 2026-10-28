#!/usr/bin/env bash
# Clean-root control for the stage B generator's sidecar fix. Run from the root of a
# fresh clone. Regenerates the 2x5 r=9 workflow with the fixed generator and requires:
#   (1) the only change from the committed original is the stage A sidecar line;
#   (2) that line names the sidecar that exists and it verifies the receipt;
#   (3) the generator refuses the legacy <stem>.hbp.sha256 name.
# The tree is restored afterwards. json=0
set -uo pipefail
A=native/ym/results/2x5_stage_a; O=.github/workflows/hebc-ym-2x5-stage-b-r9.yml
test -z "$(git status --porcelain)" || { echo "GEN_CONTROL|result=FAIL|reason=tree_not_clean|json=0"; exit 2; }
python3 native/ym/python/stage_b_workflow.py $A/HEBC-YM-2X5-STAGE-A.hbp $A/HEBC-YM-2X5-STAGE-A.sha256 2 5 9,15,27,45,81 9 $A/cores_r9.txt $O 300 40 > /dev/null; g=$?
d=$(git diff -U0 $O | grep -c '^[-+] ')
old=$(git diff -U0 $O | grep '^- ' | grep -c 'sha256sum -c $(basename native/ym/results/2x5_stage_a/HEBC-YM-2X5-STAGE-A.hbp).sha256')
new=$(git diff -U0 $O | grep '^+ ' | grep -c 'sha256sum -c HEBC-YM-2X5-STAGE-A.sha256)')
line=$(grep -o '(cd $(dirname [^)]*) && sha256sum -c [^)]*)' $O)
bash -c "$line" > /dev/null 2>&1; s=$?
t=$(mktemp -d); cp $A/HEBC-YM-2X5-STAGE-A.hbp $t/x.hbp; cp $A/HEBC-YM-2X5-STAGE-A.sha256 $t/x.hbp.sha256
python3 native/ym/python/stage_b_workflow.py $t/x.hbp $t/x.hbp.sha256 2 5 9,15,27,45,81 9 $A/cores_r9.txt $t/y.yml 300 40 > $t/legacy.txt; l=$?
lr=$(grep -c 'reason=sidecar_not_stem_sha256' $t/legacy.txt)
git checkout -q $O
echo "GEN_CONTROL|head=$(git rev-parse HEAD)|generate_rc=$g|diff_lines=$d|old_line=$old|new_line=$new|sidecar_verify_rc=$s|legacy_rc=$l|legacy_refused=$lr|json=0"
if [ $g = 0 ] && [ $d = 2 ] && [ $old = 1 ] && [ $new = 1 ] && [ $s = 0 ] && [ $l = 2 ] && [ $lr = 1 ] && [ -z "$(git status --porcelain)" ]; then
  echo "GEN_CONTROL_RESULT|result=PASS|json=0"
else
  echo "GEN_CONTROL_RESULT|result=FAIL|json=0"; exit 2
fi
