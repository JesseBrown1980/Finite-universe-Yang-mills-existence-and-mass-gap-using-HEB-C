#!/bin/bash
# Fail-closed controls for collect.py with synthetic records (verdict behaviour
# only; no physical results). Exit 0 only if every case gives its required verdict.
set -u
COL=$(cd "$(dirname "$0")" && pwd)/collect.py
D=$(mktemp -d); trap 'rm -rf $D' EXIT; cd $D
C=0ed8b129e5e52cf67d3a42dcd5a490082ef8720d19c6b8071e978c3a4a8c532e; SC=2x2:9:1393:7776:8
EX=23746649:8,46576000:8,90123457:616
mk(){ printf 'INDEP_RUN|code_sha256=%s|command=x|seed=1|json=0\nINDEP_BUILD|L=2x2|gauge_orbits=1393|burnside=1393|weight_sum=7776|six_pow_free=7776|free_links=5|tree_links=3|flat_states=8|WA_symmetric=PASS|json=0\nINDEP_COUNT|L=2x2|r=%s|t_milli=%s|N=%s|seed=1|hadamard_bits=1|primes_31bit=2|reshuffle_retries=0|result=%s|json=0\n' "${5:-$C}" "${4:-9}" $1 $2 $3; }
fails=0
case_(){ want=$1; shift; label=$1; shift; python3 $COL --code $C --scope $SC $EX "$@" > out.txt; e=$?
  if [ $e = $want ]; then echo "COLLECT_CONTROL|case=$label|exit=$e|PASS|json=0"; else echo "COLLECT_CONTROL|case=$label|exit=$e|want=$want|FAIL|json=0"; fails=1; fi; }
mk 23746649 8 COMPUTED > a; mk 46576000 8 COMPUTED > b; mk 90123457 616 COMPUTED > c
case_ 0 clean a b c
mk 90123457 617 COMPUTED > c2; case_ 1 numeric_mismatch a b c2
{ mk 23746649 8 INCONCLUSIVE; mk 23746649 8 COMPUTED | tail -1; } > d; case_ 2 duplicate_hides_inconclusive d b c
cp a a2; case_ 2 duplicate_threshold a a2 b c
mk 23746649 8 COMPUTED 10 > r10; case_ 2 out_of_scope_r r10 b c
sed 's/|hadamard_bits=1//' a > nh; case_ 2 missing_field nh b c
mk 23746649 8 COMPUTED 9 deadbeef > bad; case_ 2 unpinned_code_hash bad b c
case_ 2 missing_threshold a b
sed 's/flat_states=8/flat_states=7/' a > fl; case_ 2 wrong_structure fl b c
case_ 2 missing_file a b nofile
sed 's/N=8|/N=8x|/' a > mal; case_ 2 malformed_number mal b c
mk 23746649 8 INCONCLUSIVE > inc; case_ 2 inconclusive_count inc b c
exit $fails
