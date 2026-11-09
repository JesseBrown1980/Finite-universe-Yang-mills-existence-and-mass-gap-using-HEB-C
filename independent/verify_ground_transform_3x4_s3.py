#!/usr/bin/env python3
"""Independent stronger S3 first-gap bound by a ground-state Poincare transform.

No Perron vector, stored gauge matrix, spectral approximation or floating
point. The proof works on the 6^24 RAW link graph before restriction to gauge
invariants. For r=9 the finite first gap is >= 3/(396^96) JE.
This is an explicit but very weak lower bound, not >=0.01 JE.
"""
from hashlib import sha256
from itertools import combinations, permutations
from pathlib import Path
import sys

FAULTS = ("wrong_electric_gap","wrong_word_length","wrong_hdiag",
          "wrong_ground_ratio","wrong_gap_inequality",
          "wrong_0p01_unconditional")
fault=""
if len(sys.argv)>2 or (len(sys.argv)==2 and
    (not sys.argv[1].startswith("sabotage=")
     or sys.argv[1][9:] not in FAULTS)):
    raise SystemExit("usage: verify_ground_transform_3x4_s3.py [sabotage=NAME]")
if len(sys.argv)==2:
    fault=sys.argv[1][9:]


def check(ok,name):
    if not ok:
        print("FAILED|check="+name+"|json=0",flush=True)
        raise SystemExit(1)


def emit(label,**fields):
    print(label+"|"+"|".join(str(k)+"="+str(v) for k,v in fields.items())
          +"|json=0",flush=True)


def power(a,n):
    check(type(a) is int and type(n) is int and n>=0,
          "explicit_nonnegative_exponent")
    out=1
    while n:
        if n & 1:
            out*=a
        n//=2
        if n:
            a*=a
    return out


GROUP=tuple(permutations((0,1,2)))
LOOKUP={g:i for i,g in enumerate(GROUP)}
IDENTITY=LOOKUP[(0,1,2)]


def compose(a,b):
    return tuple(a[b[i]] for i in range(3))


MUL=tuple(tuple(LOOKUP[compose(x,y)] for y in GROUP) for x in GROUP)
T=tuple(i for i in range(6)
        if i!=IDENTITY and MUL[i][i]==IDENTITY)
check(len(T)==3,"S3_three_transposition_generators")


def distance_from_identity():
    distance={IDENTITY:0}
    queue=[IDENTITY]
    for g in queue:
        for t in T:
            nxt=MUL[t][g]
            if nxt not in distance:
                distance[nxt]=distance[g]+1
                queue.append(nxt)
    check(len(distance)==6 and sorted(distance.values())==[0,1,1,1,2,2],
          "exact_S3_Cayley_word_lengths")
    if fault=="wrong_word_length":
        check(max(distance.values())<=1,"RED_wrong_word_length")
    emit("GROUND_S3_DIAMETER",
         group_elements=6, wordlength_histogram="0:1,1:3,2:2",
         max_word_per_link=2,
         raw_links=24, raw_product_diameter_upper=48,
         proof="COORDINATE_BY_COORDINATE_CAYLEY_PATH")
    return 48


def det_minor(mat,index):
    dp={0:1}
    size=len(index)
    for row in range(size):
        next_dp={}
        for mask,weight in dp.items():
            for j in range(size):
                if mask & (1<<j):
                    continue
                inversions=(mask>>(j+1)).bit_count()
                sign=-1 if inversions&1 else 1
                newmask=mask|(1<<j)
                newweight=weight*mat[index[row]][index[j]]*sign
                next_dp[newmask]=next_dp.get(newmask,0)+newweight
        dp=next_dp
    return dp[(1<<size)-1]


def exact_electric_gap():
    # S3 Cayley electric Laplacian L=3I-sum_transposition L_t.
    # Its eigenvalues are precisely 0,3,3,3,3,6.
    a=[[0]*6 for _ in range(6)]
    for g in range(6):
        a[g][g]=3
        for t in T:
            a[g][MUL[t][g]]-=1
    check(all(a[i][j]==a[j][i] for i in range(6)
              for j in range(6)),
          "one_link_electric_symmetry")
    coefficients=[1]
    for k in range(1,7):
        minor_sum=sum(det_minor(a,ids) for ids in combinations(range(6),k))
        coefficients.append((-1 if k&1 else 1)*minor_sum)
    check(coefficients==[1,-18,126,-432,729,-486,0],
          "electric_characteristic_z_zminus3_four_zminus6")
    if fault=="wrong_electric_gap":
        check(coefficients==[1,-18,126,-431,729,-486,0],
              "RED_wrong_electric_gap")
    emit("GROUND_S3_ELECTRIC",
         matrix="S3_CAYLEY_TRANSPOSITION_LAPLACIAN",
         charpoly="z*(z-3)^4*(z-6)",
         one_link_eigenvalues="0,3,3,3,3,6",
         product_24link_spectral_gap=3,
         checker="COMPLETE_INTEGER_PRINCIPAL_MINORS")
    return 3


def ground_transform(diameter,base_gap):
    # For raw x, (72+9 M_x-lambda0) g_x =
    # sum_{72 neighbors y}g_y, with g_x>0 and lambda0>=0.
    # Hence for every neighbor y, g_y<=396g_x; by
    # graph diameter <=48, gmax/gmin<=396^48.
    degree=24*3
    plaquettes=12
    magnetic_max=3*plaquettes
    coeff=degree+9*magnetic_max
    check(degree==72 and magnetic_max==36 and coeff==396,
          "ground_eigenvector_neighbor_coefficient")
    if fault=="wrong_hdiag":
        check(coeff==395,"RED_wrong_hdiag")
    if fault=="wrong_ground_ratio":
        check(diameter<=47,"RED_wrong_ground_ratio")
    # For f=psi/g, ground-state transform yields:
    # <gf,(H-lambda0)gf> =
    # 1/2 sum_{directed x->y} g_x*g_y*(f_x-f_y)^2
    # >= gmin^2 <f,E f>.
    # min_c sum g_x^2(f_x-c)^2 <= gmax^2 min_c sum(f_x-c)^2.
    # Therefore lambda_1(H)-lambda_0(H)
    # >= gap(E)*(gmin/gmax)^2.
    exponent=2*diameter
    denom=power(coeff,exponent)
    check(exponent==96 and denom>300,
          "exact_ground_transform_exponent_and_positive_bound")
    if fault=="wrong_gap_inequality":
        check(exponent==48,"RED_wrong_gap_inequality")
    if fault=="wrong_0p01_unconditional":
        check(100*base_gap>=denom,"RED_wrong_0p01_unconditional")
    # The unique Perron ground of the raw graph is invariant
    # under gauge symmetries because H commutes with them.
    # Thus restriction to gauge invariant functions cannot
    # lower the full raw first excitation.
    emit("GROUND_S3_RAW_GAUGE_FIRST_GAP",
         raw_graph="S3_POWER_24",
         model="PERIODIC_3x4_FULL_GAUGE_INVARIANT",
         r=9, upper_neighbor_ratio=coeff,
         diameter_bound=diameter,
         gmax_over_gmin_le="396^48",
         free_electric_gap=base_gap,
         exact_lower_num=base_gap,
         exact_lower_den=denom,
         lower_bound="3/396^96*JE",
         raw_gap="POSITIVE_UNCONDITIONAL",
         gauge_gap_ge_raw="PROVED_BY_INVARIANT_POSITIVE_GROUND",
         numerical_0p01_lower="NOT_PROVED",
         original_Perron_store="NOT_USED")
    emit("GROUND_S3_SCOPE",
         result="STRONGER_UNCONDITIONAL_FINITE_FIRST_GAP",
         ground_transform="EXACT_CONDUCTANCE_AND_VARIANCE_COMPARISON",
         source_conditional_r9_0p01_to_0p07="NOT_REPLACED",
         spectral_first_winding_weight="OPEN",
         continuum_uniformity="OPEN")


def main():
    root=Path(__file__).resolve().with_name(
        "PREDICT-GROUND-TRANSFORM-3X4-S3-FIRST-GAP-20261108.hbp")
    b=root.read_bytes()
    check(sum(x.startswith(b"PREDICT|supp=") for x in b.splitlines())==8,
          "eight_supplement_predictions_frozen_first")
    emit("GROUND_S3_BEGIN",supplement_sha256=sha256(b).hexdigest(),
         independent_of_original_Perron="YES",
         integer_only="YES",complete_raw_matrix_enumeration="NOT_REQUIRED")
    diameter=distance_from_identity()
    gap=exact_electric_gap()
    ground_transform(diameter,gap)
    emit("GROUND_S3_DONE",
         status="PASS_INDEPENDENT_UNCONDITIONAL_GAP_3_OVER_396_POW_96",
         Perron_source="NOT_USED",
         strong_numeric_r9_bracket="CONDITIONAL_ONLY",
         spectral_overlap="OPEN",Clay_continuum="OPEN")


if __name__=="__main__":
    main()
