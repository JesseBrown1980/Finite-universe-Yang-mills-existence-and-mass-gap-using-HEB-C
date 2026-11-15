#!/bin/bash
# One hybrid point on the L_x x L_y torus: fit the vector (the second reader's ritz), build the local table,
# check the vector with the separately written program (hybridcheck), and print one POINT row.
# usage: point.sh LX LY R CUT THREADS RITZ_EXE HYBRIDCHECK_EXE LOCAL_TABLE_PY
# Integers only: energies in micro units of J_E.
LX=$1; LY=$2; R=$3; CUT=$4; T=$5; RITZ=$6; HC=$7; LT=$8
PY=python3; command -v python3 > /dev/null 2>&1 || PY=python
NL=$(( 2 * LX * LY ))
# a first guess of lambda_1(H') in micro units, 3nl - 3nl/(4r) + 3r - 21/r; it only places the targets
G=$(( 3000000 * NL - 3000000 * NL / (4 * R) + 3000000 * R - 21000000 / R ))
TARGETS=""
for off in 20000000 16000000 12000000 9000000 7000000 5500000 4500000 3500000 2800000 2200000 1700000 1300000 1000000 750000 500000 300000 150000; do
  TARGETS="$TARGETS,$(( G - off ))"
done
TARGETS=${TARGETS#,}
N=hyb_${LX}x${LY}_r${R}_m${CUT}
S0=$(date +%s)
"$RITZ" $LX $LY $R $CUT 150 $T ${N}_a none hybrid=$TARGETS hsweeps=300 > ${N}_a.out 2>&1
E1=$?
grep -E "^HYBRID\|" ${N}_a.out
# second pass: eight targets between the best target of the first pass and the next one above it
FINE=$($PY -I - ${N}_a.out <<'PY'
import sys
rows = []
for l in open(sys.argv[1]):
    if l.startswith('HYBRID|'):
        d = dict(kv.split('=', 1) for kv in l.strip().split('|')[1:] if '=' in kv)
        rows.append((int(d['target_micro']), int(d['cert_micro'])))
rows.sort()
if rows:
    i = max(range(len(rows)), key=lambda k: rows[k][1])
    lo = rows[i][0]
    hi = rows[i + 1][0] if i + 1 < len(rows) else lo + 150000
    print(','.join(str(lo + (hi - lo) * k // 9) for k in range(1, 9)))
PY
)
E1B=0
if [ -n "$FINE" ]; then
  "$RITZ" $LX $LY $R $CUT 150 $T ${N}_b none hybrid=$FINE hsweeps=300 > ${N}_b.out 2>&1
  E1B=$?
  grep -E "^HYBRID\|" ${N}_b.out
fi
BA=$(grep "^HYBRID_BEST" ${N}_a.out | sed 's/.*cert_micro=\([-0-9]*\).*/\1/')
BB=$(grep "^HYBRID_BEST" ${N}_b.out 2>/dev/null | sed 's/.*cert_micro=\([-0-9]*\).*/\1/')
BEST=${BA:-0}; VEC=${N}_a.hybrid
if [ -n "$BB" ] && [ "$BB" -gt "$BEST" ]; then BEST=$BB; VEC=${N}_b.hybrid; fi
S1=$(date +%s)
$PY -I "$LT" $LX $LY local-${LX}x${LY}.hbp > table.out 2>&1
tail -1 table.out
"$HC" check $LX $LY $R $CUT $VEC local-${LX}x${LY}.hbp $BEST $T > $N.check 2> $N.checkerr
E2=$?
cat $N.check; tail -3 $N.checkerr
S2=$(date +%s)
# E8 from above. Flat form 3nl for every torus; dressed form 3nl + 2r - sqrt(4r^2 + 3nl) for min(LX,LY) >= 4
# (VECTOR-BOUND.md). The square root is rounded down, so the dressed value is rounded up.
$PY -I - $NL $R $BEST $LX $LY $CUT $E1 $E1B $E2 $(( S1 - S0 )) $(( S2 - S1 )) <<'PY'
import sys, math
nl, r, best, lx, ly, cut, e1, e1b, e2, t1, t2 = (int(x) for x in sys.argv[1:12])
U = 10**6
root = math.isqrt((4 * r * r + 3 * nl) * U * U)
e8 = (3 * nl + 2 * r) * U - root
flat = 3 * nl * U
ok = int(e1 == 0 and e1b == 0 and e2 == 0)
print("POINT|Lx=%d|Ly=%d|r=%d|cut=%d|nl=%d|ritz_exit=%d|ritz_fine_exit=%d|hybridcheck_exit=%d|certificate_checked=%d|E9_lower_micro=%d|E8_upper_dressed_micro=%d|E8_upper_flat_micro=%d|gap_lower_dressed_micro=%d|gap_lower_flat_micro=%d|dressed_formula_needs_min_L_ge_4=%d|fit_seconds=%d|check_seconds=%d|json=0"
      % (lx, ly, r, cut, nl, e1, e1b, e2, ok, best, e8, flat, best - e8, best - flat, int(min(lx, ly) >= 4), t1, t2))
PY
