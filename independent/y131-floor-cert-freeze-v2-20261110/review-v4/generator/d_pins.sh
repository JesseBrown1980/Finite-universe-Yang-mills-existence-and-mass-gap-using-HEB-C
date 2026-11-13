#!/bin/bash
# third correction round: regenerate FREEZE-PIN.sha256 / FREEZE-PIN.txt of the v2 folder from the staged set, then run the checks.
set -u
R=/root/floor-v2/repo; W=/root/floor-v3
V=independent/y131-floor-cert-freeze-v2-20261110
P=$R/$V
C3=78c89c312a265fe4090071fc1abdc7d6eb102e7e
cd $R
git add -- $V ':!'$V/work/design/rs/target
cd $P
git ls-files . | grep -v '^FREEZE-PIN' | LC_ALL=C sort | xargs -d '\n' sha256sum > FREEZE-PIN.sha256
PS=$(sha256sum final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp | cut -d' ' -f1)
N=$(grep -c . FREEZE-PIN.sha256)
# lines 1-7 of the file committed at 78c89c31 are kept, with the record hash of line 4 replaced; the two lines that
# follow carried a stray leading letter n in that commit and are written again without it
git show $C3:$V/FREEZE-PIN.txt | sed -n '1,7p' | sed "4s/: [0-9a-f]\{64\}\.\$/: $PS./" > FREEZE-PIN.txt
printf '%s\n' \
"Third correction round: one commit on top of $C3 (reviewer acceptance review of 2026-11-11, HOLD with four gates; launcher and evaluator changed, checker final/tools/recheck_floor.py added, record rows 131-136, review-v4/). $(tail -1 review-v4/ROW-COMPARE-78C89C31.hbp | tr '|' ' ')." \
"A CERTIFICATE=PASS line of the launcher is accepted only after the checker of record row 131 ends ACCEPT=YES in a second environment (rows 125 and 133); the remaining risk of the launching host is disclosed in row 127." \
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
( cd $R && python3 -I -X utf8 native/scripts/no_float_gate.py . ) > $W/nofloat_final_d.txt 2>&1; echo "nofloat_rc=$?"; tail -1 $W/nofloat_final_d.txt | cut -c1-300
