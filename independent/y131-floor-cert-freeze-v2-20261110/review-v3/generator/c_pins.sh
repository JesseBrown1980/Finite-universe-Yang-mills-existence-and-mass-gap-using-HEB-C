#!/bin/bash
# Regenerate FREEZE-PIN.sha256 / FREEZE-PIN.txt of the v2 folder from the staged set, then run the checks.
set -u
R=/root/floor-v2/repo
V=independent/y131-floor-cert-freeze-v2-20261110
P=$R/$V
cd $R
git add -- $V ':!'$V/work/design/rs/target
cd $P
git ls-files . | grep -v '^FREEZE-PIN' | LC_ALL=C sort | xargs -d '\n' sha256sum > FREEZE-PIN.sha256
PS=$(sha256sum final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp | cut -d' ' -f1)
N=$(grep -c . FREEZE-PIN.sha256)
printf '%s\n' \
"Floor certificate prediction (lift-free Schur-Collatz-Wielandt floor for lambda_min(QHQ), periodic 3x4 S3, r = 9): VERSION 2 of the freeze, built by the local seat, 2026-11-10." \
"Version 1 is commit e74d8a46e86034096fd9c9231c87f594f17a93bf, folder independent/y131-floor-cert-freeze-20261110, unchanged: the historical prediction-first record. Version 2 follows an operational review of version 1 (review-v1/) and carries its blind history, including the disclosed critic run at r = 90000001/10^7 (row 093). It claims no new blind history." \
"Nothing was computed at r = 9 or within 1 of it for version 2. review-v1/ROW-COMPARE-V1-V2.hbp compares the 109 rows of version 1 with version 2 row by row: $(tail -1 review-v1/ROW-COMPARE-V1-V2.hbp | tr '|' ' ')." \
"The value to compile in as FLOORCERT_PREDICTION_SHA256 is the sha256 of final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp: $PS." \
"The r = 9 run is launched by one command, bash final/tools/run_floor.sh --launch-r9, only after this freeze passes review. It is on HOLD." \
"Correction round: one commit on top of the first version 2 commit cfc57befadcb61fb36b992af841941adaecd3fd0 (reviewer rulings and verifier findings, record rows 119-122, review-v2/). $(tail -1 review-v2/ROW-COMPARE-CFC57BEF.hbp | tr '|' ' ')." \
"Second correction round: one commit on top of 3b91d1a047d7485693c754ece8c7c18f43fbf326 (final-head verification HOLD and two reviewer rulings; launcher and evaluator changed, record rows 123-130, review-v3/). $(tail -1 review-v3/ROW-COMPARE-3B91D1A0.hbp | tr '|' ' ')." \n"A CERTIFICATE=PASS line of the launcher is accepted only after the second-environment recheck of record row 125; the remaining risk of the launching host is disclosed in row 127." \n"Paths under work/ are the pinned files at their pinned relative paths (the floorcert binary is rebuilt, not committed). Check: sha256sum -c FREEZE-PIN.sha256 ($N files)." > FREEZE-PIN.txt
cd $R
git add -- $V ':!'$V/work/design/rs/target
echo "pinned_files=$N"
( cd $P && sha256sum -c FREEZE-PIN.sha256 | grep -vc ': OK$' ; )
echo "staged_not_in_pin:"; ( cd $P && git ls-files . | grep -v '^FREEZE-PIN' | LC_ALL=C sort | diff - <(sed 's/^[0-9a-f]*  //' FREEZE-PIN.sha256) | head -5 )
echo "unstaged_or_untracked:"; git status --porcelain -- $V | grep -v '^[AM]  ' | grep -v target | head
echo "CR files:"; git ls-files -- $V | while read f; do if grep -Iq . "$f" && grep -q $'\r' "$f"; then echo "CR $f"; fi; done | head
echo "v1 diff lines:"; git diff e74d8a46 -- independent/y131-floor-cert-freeze-20261110 | wc -l; git diff --cached e74d8a46 -- independent/y131-floor-cert-freeze-20261110 | wc -l
echo "staged outside v2:"; git diff --cached --name-only | grep -v "^$V/" | head
echo "float evidence diff:"; git diff --cached e74d8a46 -- native/scripts/FLOAT-EVIDENCE.txt | wc -l
( cd $R && python3 -I -X utf8 native/scripts/no_float_gate.py . ) > /root/floor-v2/nofloat_final_c.txt 2>&1; echo "nofloat_rc=$?"; tail -3 /root/floor-v2/nofloat_final_c.txt | cut -c1-300
