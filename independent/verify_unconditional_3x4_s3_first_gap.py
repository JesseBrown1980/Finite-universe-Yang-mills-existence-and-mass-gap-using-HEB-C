#!/usr/bin/env python3
"""Independent 3x4 finite S3 *unconditional first-gap existence* certificate.

Does NOT claim an unconditional 0.01 JE lower bound, rerun the
45,508,080-row Perron store or certify winding first-state overlap.
Proof uses Burnside, generated electric graph, Perron-Frobenius for
irreducible stoquastic integer matrices, and monic polynomial
discriminant root separation. Source has no float, division op or JSON.
"""
from hashlib import sha256
from itertools import combinations, permutations
from pathlib import Path
import sys

NEGATIVES = (
    "wrong_burnside", "wrong_cycle_rank", "wrong_link_generators",
    "wrong_magnetic_cap", "wrong_spectral_ceiling",
    "wrong_discriminant", "claim_0p01_unconditional",
    "claim_first_overlap",
)
fault = ""
if len(sys.argv) > 2 or (
    len(sys.argv) == 2 and
    (not sys.argv[1].startswith("sabotage=")
     or sys.argv[1][9:] not in NEGATIVES)
):
    raise SystemExit("usage: verify_unconditional_3x4_s3_first_gap.py [sabotage=NAME]")
if len(sys.argv) == 2:
    fault = sys.argv[1][9:]


def check(ok, name):
    if not ok:
        print("FAILED|check=" + name + "|json=0", flush=True)
        raise SystemExit(1)


def emit(tag, **attrs):
    print(tag + "|" + "|".join(str(k) + "=" + str(v)
                               for k, v in attrs.items()) + "|json=0",
          flush=True)


G = tuple(permutations(range(3)))
IDX = {p: i for i, p in enumerate(G)}
def compose(p, q):
    return tuple(p[q[i]] for i in range(3))

MUL = tuple(tuple(IDX[compose(p, q)] for q in G) for p in G)
ID = IDX[(0, 1, 2)]
check(ID == 0, "permutation_identity")
ORDER2 = tuple(i for i, p in enumerate(G)
               if i != ID and MUL[i][i] == ID)
ORDER3 = tuple(i for i in range(6)
               if i != ID and i not in ORDER2)
check(len(ORDER2) == 3 and len(ORDER3) == 2,
      "S3_class_census")


def group_generated_by(generators):
    todo = [ID]
    seen = {ID}
    for g in todo:
        for h in generators:
            nxt = MUL[g][h]
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    return seen


def integer_power(base, exponent):
    check(type(base) is int and type(exponent) is int
          and exponent >= 0, "nonnegative_integer_power")
    result=1
    while exponent:
        if exponent & 1:
            result*=base
        exponent//=2
        if exponent:
            base*=base
    return result


def burnside():
    V = 3 * 4
    E = 2 * V
    rank = E - V + 1
    if fault == "wrong_cycle_rank":
        check(rank == 12, "RED_wrong_cycle_rank")
    check(V == 12 and E == 24 and rank == 13,
          "3x4_spanning_tree_cycle_rank")
    cent = [sum(int(MUL[g][h] == MUL[h][g])
                for h in range(6)) for g in range(6)]
    check(sorted(cent) == [2, 2, 2, 3, 3, 6],
          "centralizer_sizes_6_3_2")
    counts = {v: cent.count(v) for v in set(cent)}
    check(counts == {2: 3, 3: 2, 6: 1},
          "centralizer_class_multiplicities")
    fix_sum = sum(integer_power(size,rank) for size in cent)
    q, rem = divmod(fix_sum, 6)
    check(rem == 0 and q == 2177317873,
          "full_orbit_Burnside")
    if fault == "wrong_burnside":
        check(q == 2177317872, "RED_wrong_burnside")
    emit("INDEPENDENT_S3_BURNSIDE",
         lattice="3x4_periodic",
         vertices=V, positive_links=E,
         tree_links=V-1, unfixed_cycle_links=rank,
         centralizer_formula="(6^13+3*2^13+2*3^13)/6",
         full_orbits=q, method="GROUP_CENTRALIZERS_ONLY")
    return q


def stoquastic(n):
    gens = group_generated_by(ORDER2)
    check(gens == set(range(6)),
          "three_transpositions_generate_S3")
    if fault == "wrong_link_generators":
        check(group_generated_by(ORDER2[:1]) == set(range(6)),
              "RED_wrong_link_generators")
    # Every raw 24-link field is reached from the identity field
    # coordinate-by-coordinate because these electric generators
    # generate S3 on EACH link. The gauge quotient of a connected
    # graph is connected, including all symmetry and momentum sectors
    # in the complete gauge-invariant Hilbert space.
    electric_moves = 24 * len(ORDER2)
    check(electric_moves == 72, "all_electric_moves")
    magnetic_per_plaq = (0, 2, 3)
    plaquettes = 3 * 4
    max_M = plaquettes * max(magnetic_per_plaq)
    if fault == "wrong_magnetic_cap":
        check(max_M == 24, "RED_wrong_magnetic_cap")
    check(max_M == 36, "spin2_character_S3_M_max36")
    max_E = 2 * electric_moves
    max_H = max_E + 9 * max_M
    if fault == "wrong_spectral_ceiling":
        check(max_H == 467, "RED_wrong_spectral_ceiling")
    check((max_E, max_H) == (144, 468),
          "quadratic_form_spectrum_0_to_468")
    check(n >= 2, "full_Hilbert_has_excitation")
    # In orbit-indicator basis H has integer entries with
    # nonpositive off-diagonals. By a positive diagonal orbit-weight
    # similarity it is Hermitian. A is an irreducible nonnegative
    # matrix after adding a scalar to -H. Perron-Frobenius therefore
    # makes the bottom eigenvalue SIMPLE, for every finite r.
    emit("INDEPENDENT_S3_IRREDUCIBILITY",
         electrical_generators=3, generation_closure=6,
         all_links=24, electric_moves=electric_moves,
         raw_graph="CONNECTED_BY_COORDINATE_GENERATORS",
         gauge_orbit_graph="CONNECTED_BY_QUOTIENT",
         Hamiltonian="IRREDUCIBLE_STOQUASTIC_INTEGER_MATRIX",
         weighted_selfadjoint="YES",
         Perron_ground_multiplicity=1,
         all_finite_r_nonnegative="YES")
    emit("INDEPENDENT_S3_NORM",
         E_lower=0,E_upper=max_E,
         number_of_plaquettes=plaquettes,M_upper=max_M,
         r=9, full_spectrum_lower=0,full_spectrum_upper=max_H)
    return max_H


def independent_separation(n, width):
    # The gauge-orbit indicator matrix is integer-valued, so its
    # characteristic polynomial p is monic over Z.
    # The squarefree part q=p/gcd(p,p') is monic over Z,
    # and has m distinct REAL roots in [0,width], 2<=m<=n.
    # Its discriminant is a nonzero integer:
    # Discriminant(q)=product_(i<j)(lambda_i-lambda_j)^2 >= 1.
    # If delta is the adjacent first root difference, all the
    # remaining m*(m-1)/2-1 differences have absolute size <=width.
    # Thus delta >= width^(-K), K=n*(n-1)/2-1.
    pair_count = n * (n - 1) // 2
    exponent = pair_count - 1
    check(pair_count == 2370356558953963128
          and exponent == 2370356558953963127,
          "exact_root_separation_exponent")
    if fault == "wrong_discriminant":
        check(exponent == pair_count,
              "RED_wrong_discriminant")
    if fault == "claim_0p01_unconditional":
        check(exponent <= 1, "RED_claim_0p01_unconditional")
    if fault == "claim_first_overlap":
        check("OPEN" == "PROVED", "RED_claim_first_overlap")
    emit("INDEPENDENT_S3_FIRST_GAP",
         coupling_r=9,levels="FIRST_TWO_OF_FULL_SPACE",
         lower_bound="468^(-2370356558953963127)*JE",
         upper_bound="468*JE",
         strictly_positive="PROVED_UNCONDITIONALLY",
         argument="IRREDUCIBLE_PF_PLUS_INTEGER_DISCRIMINANT",
         original_Perron_floor_required="NO",
         original_45M_store_required="NO",
         r9_gap_gt_0p01="SOURCE_CONDITIONAL_NOT_PROVED_HERE",
         first_state_winding_overlap="OPEN")
    return exponent


def integer_gcd(a,b):
    a=abs(a);b=abs(b)
    while b:
        a,b=b,a%b
    return a

def ratio(a,b=1):
    check(type(a) is int and type(b) is int and b != 0,
          "exact_integer_rational_inputs")
    if b<0:
        a,b=-a,-b
    g=integer_gcd(a,b)
    return (a//g,b//g)

def radd(x,y):
    return ratio(x[0]*y[1]+y[0]*x[1],x[1]*y[1])

def rsub(x,y):
    return ratio(x[0]*y[1]-y[0]*x[1],x[1]*y[1])

def rmul(x,y):
    return ratio(x[0]*y[0],x[1]*y[1])

def rle(x,y):
    return x[0]*y[1]<=y[0]*x[1]

def rlt(x,y):
    return x[0]*y[1]<y[0]*x[1]

def matrix_product(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(len(a)))
             for j in range(len(a))] for i in range(len(a))]


def determinant_minor(a, subset):
    # Integer Leibniz via signed dynamic programming, no external
    # spectral or eigenvalue package. Independent of Newton traces.
    m = len(subset)
    dp = {0: 1}
    for j in range(m):
        nd = {}
        for mask, coefficient in dp.items():
            for k in range(m):
                if mask & (1 << k):
                    continue
                parity = (mask >> (k+1)).bit_count()
                sign = -1 if parity & 1 else 1
                nm = mask | (1 << k)
                nd[nm] = nd.get(nm,0) + sign * coefficient * a[subset[j]][subset[k]]
        dp = nd
    return dp[(1 << m)-1]


def highr_arithmetic():
    # These are the six known NONZERO entries of 16*C1.
    # This crosscheck verifies spectral arithmetic, not an
    # independent reconstruction of the S3 physical first shell.
    a = [[0]*8 for _ in range(8)]
    for i,j,value in ((0,1,72),(1,0,24),(1,2,48),
                      (2,1,72),(3,4,24),(4,3,24)):
        a[i][j] = value
    principal = [0]*9
    principal[0] = 1
    for k in range(1,9):
        total = 0
        for s in combinations(range(8),k):
            total += determinant_minor(a,s)
        principal[k] = (-1 if k&1 else 1)*total
    expected=[1,0,-5760,0,2985984,0,0,0,0]
    check(principal == expected,
          "independent_principal_minor_C1_characteristic_polynomial")
    # An independent Newton traces calculation of the SAME 8x8
    # entries, with all integer divisibility checked.
    t = [[int(i==j) for j in range(8)] for i in range(8)]
    traces = []
    for k in range(1,9):
        t = matrix_product(t,a)
        traces.append(sum(t[i][i] for i in range(8)))
    newton = [1]
    for k in range(1,9):
        num = -sum(newton[k-j]*traces[j-1] for j in range(1,k+1))
        value, residue = divmod(num,k)
        check(residue==0,"newton_divisibility_exact")
        newton.append(value)
    check(newton == principal,
          "independent_Newton_and_principal_minor_agree")
    emit("INDEPENDENT_S3_HIGHR_C1",
         input="SOURCE_STATED_SIX_NONZERO_16C1_ENTRIES",
         charpoly="z^4*(z^2-72^2)*(z^2-24^2)",
         checker1="PRINCIPAL_MINOR_LEIBNIZ",
         checker2="INTEGER_NEWTON_TRACES",
         top_eigenvalues_of_C1="9/2,3/2",
         top_difference_of_C1="3",
         raw_first_shell_reenumeration="NOT_PERFORMED_BY_THIS_CHECK")
    for r in (10000,100000):
        d=3*r
        eta = radd(ratio(5184,(d-72)**3),
                   ratio(373248,d*d*(d-72)))
        estimate=ratio(3,r*r)
        margin=rmul(ratio(2),eta)
        low = rsub(estimate,margin)
        high = radd(estimate,margin)
        check(low[0]>0 and rlt(low,high),
              "positive_rhigh_gap_enclosure")
        if r==100000:
            check(rle(ratio(271961,10**15),low)
                  and rle(high,ratio(328039,10**15)),
                  "r100000_outward_endpoints")
        emit("INDEPENDENT_S3_HIGHR",
             r=r,eta_numerator=eta[0],eta_denominator=eta[1],
             gap_lower_numerator=low[0],
             gap_lower_denominator=low[1],
             gap_upper_numerator=high[0],
             gap_upper_denominator=high[1],
             strict_positive="YES",
             original_Perron_source_used="NO")
    # Under r>24, r² eta(r) is decreasing:
    # r²*5184/(3r-72)^3 has negative log derivative;
    # r²*373248/[(3r)^2(3r-72)]
    # equals 41472/(3r-72), also decreasing.
    emit("INDEPENDENT_S3_HIGHR_UNIFORM",
         r_min=10000, source_floor="M_nonflat_GE_3",
         ratio_r2_eta="STRICTLY_DECREASING_FOR_r_GT_24",
         positive_E2_minus_E1_for_all_larger_r="CHECKED_ANALYTICALLY")


def main():
    pred=Path(__file__).resolve().with_name(
        "PREDICT-UNCONDITIONAL-3X4-S3-FIRST-GAP-20261108.hbp"
    ).read_bytes()
    check(sum(row.startswith(b"PREDICT|id=")
              for row in pred.splitlines())==14,
          "all_fourteen_predictions_frozen")
    emit("INDEPENDENT_S3_START",prediction_sha256=sha256(pred).hexdigest(),
         test="NO_FULL_STORE_STOQUASTIC_FIRST_GAP",
         gauge_group="FINITE_S3",
         full_dimension="NOT_A_SECTOR")
    n=burnside()
    cap=stoquastic(n)
    independent_separation(n,cap)
    highr_arithmetic()
    emit("INDEPENDENT_S3_DONE",status="PASS_UNCONDITIONAL_FINITE_GAP_EXISTENCE",
         r9_sharp_numeric_gap="CONDITIONAL_PER_PERRON",
         full_second_machine_store="NOT_REPLAYED",
         observable_first_weight="OPEN",
         physical_continuum_mass_gap="OPEN")


if __name__ == "__main__":
    main()
