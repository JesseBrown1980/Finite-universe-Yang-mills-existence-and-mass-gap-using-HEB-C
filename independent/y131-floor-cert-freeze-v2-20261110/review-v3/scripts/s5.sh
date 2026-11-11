D=/root/floor-v2-final/head/independent/y131-floor-cert-freeze-v2-20261110
cat $D/review-v2/rehearsal-v2b/reh_b.sh
echo ====; cat $D/review-v2/rehearsal-v2b/RCHECK.txt $D/review-v2/rehearsal-v2b/LIMCHECK.txt
for n in D1 DX D3; do echo "=== $n"; grep -E '^(START|DECISION|STEP|PREREQ|INJECTED|NOTE\|rerun)' $D/review-v2/rehearsal-v2b/$n.stdout.txt | cut -c1-400; tail -1 $D/review-v2/rehearsal-v2b/$n.stdout.txt | cut -c1-700; done
