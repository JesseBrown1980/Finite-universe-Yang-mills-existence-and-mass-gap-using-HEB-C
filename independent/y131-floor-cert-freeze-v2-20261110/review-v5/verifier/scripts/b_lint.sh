set -u
V=/root/floor-v4-verify; cd $V/repoB
F=independent/y131-floor-cert-freeze-v2-20261110
rm -rf $V/exp0; mkdir -p $V/exp0; git archive 5eecb540431a1b5665605f68ed81bc701719dcd1 | tar -x -C $V/exp0
L=$V/scripts_lint; mkdir -p $L
for t in exp0 repoB; do
  ( cd $V/$t/$F && python3 -I -B final/tools/lint_hbp.py final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp . > $V/lint_$t.txt 2>&1; echo "lint_$t exit=$? $(grep '^LINT_RESULT' $V/lint_$t.txt) errors_lines=$(grep -c '^ERROR' $V/lint_$t.txt)" )
done
grep '^ERROR' $V/repoB/$F/final/tools/lint_result.txt | sort > $V/lint_committed_err.txt
grep '^ERROR' $V/lint_exp0.txt | sort > $V/lint_exp0_err.txt
grep '^ERROR' $V/lint_repoB.txt | sort > $V/lint_repoB_err.txt
echo "committed_vs_export_diff=$(diff $V/lint_committed_err.txt $V/lint_exp0_err.txt | grep -c '^[<>]')"
diff $V/lint_committed_err.txt $V/lint_exp0_err.txt | head
echo "export_vs_buildtree_diff:"; diff $V/lint_exp0_err.txt $V/lint_repoB_err.txt | head
grep '^LINT|' $V/lint_exp0.txt | cut -c1-300
