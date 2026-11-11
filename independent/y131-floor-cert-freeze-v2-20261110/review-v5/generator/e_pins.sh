#!/bin/bash
# fourth correction round: regenerate FREEZE-PIN.sha256 / FREEZE-PIN.txt of the v2 folder from the staged set, then run the checks.
set -u
R=/root/floor-v2/repo; W=/root/floor-v5
V=independent/y131-floor-cert-freeze-v2-20261110
P=$R/$V
C3=5eecb540431a1b5665605f68ed81bc701719dcd1
cd $R
git add -- $V ':!'$V/work/design/rs/target
cd $P
git ls-files . | grep -v '^FREEZE-PIN' | LC_ALL=C sort | xargs -d '\n' sha256sum > FREEZE-PIN.sha256
PS=$(sha256sum final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp | cut -d' ' -f1)
N=$(grep -c . FREEZE-PIN.sha256)
# lines 1-8 of the file committed at 5eecb540 are kept, with the record hash of line 4 replaced
git show $C3:$V/FREEZE-PIN.txt | sed -n '1,8p' | sed "4s/: [0-9a-f]\{64\}\.\$/: $PS./" > FREEZE-PIN.txt
printf '%s\n' \
"Fourth correction round: one commit on top of $C3 (fourth final-head verification, FAIL on the checker; checker rewritten to replay the frozen protocol, launcher and evaluator changed, record rows 137-141, review-v5/). $(tail -1 review-v5/ROW-COMPARE-5EECB540.hbp | tr '|' ' ')." \
"A CERTIFICATE=PASS line of the launcher is accepted only after the checker of record row 131 ends ACCEPT=YES in a second environment, with the receipt hash of the PUBLISH line (rows 125, 133 and 138); what stays open is disclosed in rows 127 and 139." \
"Paths under work/ are the pinned files at their pinned relative paths (the floorcert binary is rebuilt, not committed). Check: sha256sum -c FREEZE-PIN.sha256 ($N files)." >> FREEZE-PIN.txt
grep -c . FREEZE-PIN.txt; sed -n '4p' FREEZE-PIN.txt | cut -c60-200
cd $R
git add -- $V ':!'$V/work/design/rs/target
echo "pinned_files=$N"
( cd $P && sha256sum -c FREEZE-PIN.sha256 | grep -vc ': OK$' ; )
echo "staged_not_in_pin:"; ( cd $P && git ls-files . | grep -v '^FREEZE-PIN' | LC_ALL=C sort | diff - <(sed 's/^[0-9a-f]*  //' FREEZE-PIN.sha256) | head -5 )
echo "unstaged_or_untracked:"; git status --porcelain -- $V | grep -v '^[AM]  ' | grep -v target | head
echo "CR files:"; git ls-files -- $V | while read f; do if grep -Iq . "$f" && grep -q $'\r' "$f"; then echo "CR $f"; fi; done | head
echo "staged outside v2:"; git diff --cached --name-only | grep -v "^$V/" | head
( cd $R && python3 -I -X utf8 native/scripts/no_float_gate.py . ) > $W/nofloat_final_e.txt 2>&1; echo "nofloat_rc=$?"; tail -1 $W/nofloat_final_e.txt | cut -c1-300
