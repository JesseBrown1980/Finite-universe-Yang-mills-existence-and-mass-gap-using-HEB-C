set -u
V=/root/floor-v4-verify; FB=$V/repoB/independent/y131-floor-cert-freeze-v2-20261110; O=$V/out/E; mkdir -p $O
A="--test-r 12 --test-m0 7 --test-f 1 --test-g0 100/1"
cd $FB
env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $A --test-frozen-build --test-out $O/E1 > $O/E1.out 2>&1; echo "CASE|id=E1|exit=$?|json=0"
grep -E '^NOTE\|freeze_commit|^PINCHECK_RESULT|^NOTE\|frozen_build_rehearsal|^TOOL\|private_copy=floorcert' $O/E1.out | cut -c1-300
tail -1 $O/E1.out | cut -c1-300
echo "frozen_binary_sha=$(sha256sum $O/E1/target/release/floorcert | cut -d' ' -f1) row016=9533e7e902ff565641b34d3bdd0c693ffa0b37baa08575283e00429e2c7fa74f"
rm -rf $V/second/E1; cp -a $O/E1 $V/second/E1; rm -rf $V/second/E1/tmp $V/second/E1/target
( cd $V/exp0/independent/y131-floor-cert-freeze-v2-20261110 && python3 -I -B final/tools/recheck_floor.py receipt=$V/second/E1/FLOOR-RUN-RECEIPT.hbp > $O/E1.recheck.txt 2>&1; echo "CHECK|id=E1|exit=$?|json=0"; tail -1 $O/E1.recheck.txt | cut -c1-300 )
env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $A --test-frozen-build --freeze-commit 78c89c312a265fe4090071fc1abdc7d6eb102e7e --test-out $O/E2 > $O/E2.out 2>&1; echo "CASE|id=E2_wrong_commit_78c89c31|exit=$?|$(tail -1 $O/E2.out | cut -c1-250)"
env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $A --test-frozen-build --freeze-commit 1111111111111111111111111111111111111111 --test-out $O/E2b > $O/E2b.out 2>&1; echo "CASE|id=E2b_bogus_commit|exit=$?|$(tail -1 $O/E2b.out | cut -c1-250)"
env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $A --freeze-commit 5eecb540431a1b5665605f68ed81bc701719dcd1 --test-out $O/E2c > $O/E2c.out 2>&1; echo "CASE|id=E2c_freeze_commit_without_frozen_build|exit=$?|$(tail -1 $O/E2c.out | cut -c1-250)"
# modified tracked files: a separate clone
[ -d $V/repoC ] || git clone -q $V/repoB $V/repoC; cd $V/repoC && git checkout -q 5eecb540431a1b5665605f68ed81bc701719dcd1
FC=$V/repoC/independent/y131-floor-cert-freeze-v2-20261110
echo "x" >> $FC/review-v4/ROW-COMPARE-78C89C31.hbp
( cd $FC && env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $A --test-frozen-build --test-out $O/E3 > $O/E3.out 2>&1; echo "CASE|id=E3_tracked_file_in_freeze_folder_modified|exit=$?|$(tail -1 $O/E3.out | cut -c1-250)" )
git -C $V/repoC checkout -q -- .
F1=$(git -C $V/repoC ls-files | grep -v '^independent/y131-floor-cert-freeze-v2-20261110/' | grep -E '\.md$' | head -1); echo "outside_file=$F1"
echo "x" >> "$V/repoC/$F1"
( cd $FC && env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $A --test-frozen-build --test-out $O/E3b > $O/E3b.out 2>&1; echo "CASE|id=E3b_tracked_file_outside_freeze_folder_modified|exit=$?|$(grep -o 'NOTE|freeze_commit=[^|]*' $O/E3b.out)|$(tail -1 $O/E3b.out | cut -c1-200)" )
git -C $V/repoC checkout -q -- .; echo "repoC_status=$(git -C $V/repoC status --porcelain --untracked-files=no | wc -l)"
# E4: an untracked cargo configuration file beside the crate changes the frozen build; git status --untracked-files=no does not see it
mkdir -p $FC/work/design/rs/.cargo; printf '[profile.release]\nopt-level = 2\n' > $FC/work/design/rs/.cargo/config.toml
echo "repoC_tracked_status=$(git -C $V/repoC status --porcelain --untracked-files=no | wc -l) untracked=$(git -C $V/repoC status --porcelain | tr '\n' ' ')"
( cd $FC && env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh $A --test-frozen-build --test-out $O/E4 > $O/E4.out 2>&1; echo "CASE|id=E4_untracked_cargo_config|exit=$?|$(tail -1 $O/E4.out | cut -c1-200)" )
echo "frozen_E1=$(sha256sum $O/E1/target/release/floorcert | cut -d' ' -f1) frozen_E3b=$(sha256sum $O/E3b/target/release/floorcert 2>/dev/null | cut -d' ' -f1) frozen_E4=$(sha256sum $O/E4/target/release/floorcert 2>/dev/null | cut -d' ' -f1)"
rm -rf $FC/work/design/rs/.cargo
# E5: the eleven refusal controls on the frozen binary of E1 (the only permitted contact with r = 9)
cd $FB
bash final/tools/freeze_args_controls.sh $O/E1/target/release/floorcert $FB/work/design/rs/target/release/floorcert 5eecb540431a1b5665605f68ed81bc701719dcd1 908373ebb40979e0d8d49a1b20990fe2c65195ec338dc4424189649850be4d82 > $O/FZA.out 2>&1; echo "CASE|id=FZA|exit=$?|json=0"
grep -E '^CONTROL|^SUITE_STOPPED|^FREEZE_ARGS_CONTROLS' $O/FZA.out
echo "fza_out_lines=$(grep -c '^OUT|' $O/FZA.out) numeric_lines=$(grep -cE '^OUT\|name=[^|]*\|(FREEZE|CERT|ROWHASH|ENUM):' $O/FZA.out)"
