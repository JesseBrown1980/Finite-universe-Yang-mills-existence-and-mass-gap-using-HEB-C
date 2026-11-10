set -u
A=/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-v2-20261110
E=$A/review-v1/E3-PROVENANCE.hbp
wc -l $E; head -c 1500 $E; echo
grep -c 'provenance=verified' $E; grep -c 'provenance=not_established' $E
grep 'provenance=verified' $E | cut -c1-600
