#!/usr/bin/env python3
"""Exact certified 4-vector Ritz UPPER envelope from two residual Krylov vectors.

No full 429M row enumeration and NO missing H_tt guessed. Work with exact old
two H20736 source vectors u1,u2 and exact projected residuals ti=(I-P)ri:
   ri=(D H-z_i)u_i, D=10^9.
The accepted 2x2 integer residual Gram E_num / den is strictly positive.
Hermiticity supplies EXACT K_u,t = E_num/(den D).

Prove universal original finite S3 physical H upper bound M=468:
- 24 links times 3 involutive transposition moves: electric
  L=72I-sum U_t, every U_t unitary/self-adjoint => 0<=L<=144I.
- Twelve plaquette potential terms 2-CHAR (CHAR >= -1) each <=3,
  so 0<=9*B<=9*12*3=324I.
Therefore 0<=H<=468I on full weighted gauge-invariant Hilbert space.

Choosing rescaled ti' = den*ti yields integer 4x4 UPPER pencil
    Q(z) = D K_upper - z G
    [[D K_uu-z G_uu,                     E_num],
     [E_num,          (D*468-z)*den*E_num]].
The actual 4x4 projected K is Loewner-below K_upper. Its first two
projected Ritz eigenvalues are therefore rigorously UPPER bounded by the
first two eigenvalues of this explicit four-vector upper envelope.
Exact symmetric Bareiss inertia brackets them at 10^-9 resolution.

This is a certified upper bound, NOT an exact value of K_tt nor
a true eigenstate angle or Wilson first-excitation spectral weight.
"""
import os
import sys
from hashlib import sha256
from itertools import permutations

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
RESULT=os.path.join(ROOT,"build","y137-two-residual","RESULT-TWO-RESIDUAL.hbp")
D=1000000000
ELECTRIC=24*3*2
MAGNETIC=9*12*3
CAP=ELECTRIC+MAGNETIC
ORIGINAL_2D_UPPER=((69921372133,69921372134),
                   (69960527810,69960527811))


def need(ok,why):
    if not ok:
        print("Y137_FOUR_ENVELOPE_REFUSE|reason="+why+"|json=0",
              flush=True)
        raise SystemExit(1)


def digest(v):
    return sha256(str(v).encode("ascii")).hexdigest()


def emit(tag,**d):
    print(tag+"|"+"|".join(str(k)+"="+str(v)
          for k,v in d.items())+"|json=0",flush=True)


def determinant(a):
    n=len(a)
    need(n>0 and all(len(row)==n for row in a),
         "fraction_free_nonsquare")
    m=[r[:] for r in a]
    previous=1
    sign=1
    for k in range(n-1):
        if not m[k][k]:
            pos=next((i for i in range(k+1,n) if m[i][k]),None)
            if pos is None:
                return 0
            m[k],m[pos]=m[pos],m[k]
            sign=-sign
        pivot=m[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                v=pivot*m[i][j]-m[i][k]*m[k][j]
                need(v%previous==0,"fraction_free_nonintegral")
                m[i][j]=v//previous
            m[i][k]=0
        previous=pivot
    return sign*m[-1][-1]


def parse(tag,rows):
    matching=[line for line in rows if line.startswith(tag+"|")]
    need(len(matching)==1,"missing_or_duplicate_record_"+tag)
    a={}
    for field in matching[0].split("|")[1:]:
        k,sep,v=field.partition("=")
        need(sep and k not in a,"invalid_record_field")
        a[k]=v
    need(a.get("json")=="0","invalid_record_terminator")
    return a


def original_exact():
    need(os.path.isfile(RESULT),"missing_full_source_H20738_matrix")
    rows=open(RESULT,encoding="ascii").read().splitlines()
    m=parse("Y137_TWO_RESIDUAL_MATRIX",rows)
    g=parse("Y137_TWO_RESIDUAL_GRAM",rows)
    v=parse("Y137_TWO_RESIDUAL_VERDICT",rows)
    den=int(m["old_Gram_det_den"])
    e11,e12,e22=(int(m[k]) for k in
                    ("E11_num","E12_num","E22_num"))
    need(den>0 and e11>0 and e22>0
         and e11*e22-e12*e12>0
         and int(m["E_determinant_num"])==e11*e22-e12*e12
         and g["rank"]=="2" and
         v["certified_nested_dimension"]=="20738"
         and v["new_H_tt_block"]=="HOLD",
         "unaccepted_rank2_residual_Gram")
    for key,val in (("11",e11),("12",e12),("22",e22)):
        need(digest(val)==g["E"+key+"_num_sha256"],
             "original_residual_Gram_sha_drift")
    g11,g12,g22=(int(m[k]) for k in
                   ("old_source_G11","old_source_G12","old_source_G22"))
    k11,k12,k22=(int(m[k]) for k in
                   ("old_source_H11","old_source_H12","old_source_H22"))
    need(g11>0 and g22>0 and g11*g22-g12*g12>0,
         "source_two_sample_Gram_not_strict")
    return den,[[e11,e12],[e12,e22]],[[g11,g12],[g12,g22]],[
        [k11,k12],[k12,k22]]


def pencil(z,den,E,G,K):
    q=[[0]*4 for ignored in range(4)]
    for i in range(2):
        for j in range(2):
            q[i][j]=D*K[i][j]-z*G[i][j]
            q[i][2+j]=E[i][j]
            q[2+j][i]=E[i][j]
            q[2+i][2+j]=(D*CAP-z)*den*E[i][j]
    need(all(q[i][j]==q[j][i] for i in range(4)
             for j in range(4)), "upper_pencil_not_symmetric")
    return q


def inertia(z,den,E,G,K):
    q=pencil(z,den,E,G,K)
    # A symmetric pencil can have an exact zero LEADING minor at a
    # non-eigenvalue. Try every symmetric row/column permutation before
    # refusing. Congruence permutations preserve Sylvester inertia.
    for order in permutations(range(4)):
        last=1
        negatives=0
        valid=True
        for size in range(1,5):
            ids=order[:size]
            d=determinant([[q[i][j] for j in ids] for i in ids])
            if d==0:
                valid=False
                break
            negatives+=int((d<0)!=(last<0))
            last=d
        if valid:
            return negatives
    need(False,"no_nondegenerate_symmetric_principal_minor_order")


def bracket(level,den,E,G,K):
    lo,hi=0,72*D-1
    need(inertia(lo,den,E,G,K)<level and
         inertia(hi,den,E,G,K)>=level,
         "first_two_upper_Ritz_outside_0_72")
    while hi-lo>1:
        z=(hi+lo)//2
        count=inertia(z,den,E,G,K)
        if count>=level:
            hi=z
        else:
            lo=z
    need(inertia(lo,den,E,G,K)==level-1
         and inertia(hi,den,E,G,K)==level,
         "final_exact_rational_inertia_mismatch")
    return lo,hi


def toy():
    need(CAP==468 and ELECTRIC==144 and MAGNETIC==324,
         "physical_operator_upper_cap_drift")
    need(determinant([[2,1],[1,3]])==5
         and determinant([[0,1],[1,0]])==-1,
         "fraction_free_inertia_toys")
    # 2 source coords, 2 new coords; known 4D diagonal eigenvalues,
    # low levels 2 and 3 in energy units.
    den=1
    E=[[1,0],[0,1]]
    G=[[1,0],[0,1]]
    K=[[2,0],[0,3]]
    # Cross terms enter via E/D, so exact bounds lie below the
    # uncoupled 2 and 3 after extending with positive-energy modes.
    x=bracket(1,den,E,G,K)
    y=bracket(2,den,E,G,K)
    need(x[1]<=2*D and y[1]<=3*D
         and x[0]>=0 and y[0]>=x[0],
         "two_old_sources_no_longer_variational_upper")
    emit("Y137_FOUR_ENVELOPE_TOY",
         H_electric_bound=ELECTRIC,
         H_magnetic_bound=MAGNETIC,
         H_total_cap=CAP,
         exact_upper_envelope_inertia="PASS",
         two_toy_Ritz_brackets="PASS",
         full_H_tt="NOT_COMPUTED",
         Wilson_weight="HOLD")


def real():
    need(CAP==468 and D==1000000000,
         "source_operator_cap_changed")
    den,E,G,K=original_exact()
    result=[bracket(k,den,E,G,K) for k in (1,2)]
    for level,(lo,hi) in enumerate(result,1):
        orig=ORIGINAL_2D_UPPER[level-1]
        need(hi<=orig[1],
             "four_envelope_upper_not_nested_below_original_2D_Ritz")
        emit("Y137_FOUR_ENVELOPE_RITZ",
             level=level,integer_lower_z_num=lo,integer_upper_z_num=hi,
             energy_den=D,original_2D_Ritz_upper_z_num=orig[1],
             certified_upper_improvement_num=orig[1]-hi,
             certificate="FOUR_VECTOR_LOEWNER_UPPER_ENVELOPE",
             original_H_tt="NOT_COMPUTED",
             true_full_state_eigenvector="NOT_CERTIFIED",
             Wilson_weight="HOLD")
    emit("Y137_FOUR_ENVELOPE_VERDICT",
         original_H_source="FINITE_S3_3X4_r9",
         electric_72_involutive_terms="BOUND_144",
         magnetic_12_plaquettes_character_range="BOUND_324",
         universal_H_Loewner_ceiling=CAP,
         two_residual_rank="EXACT_2_OF_2",
         nested_effective_dimension=20738,
         four_vector_trial="RIGOROUS_UPPER_RITZ",
         full_H_tt="NOT_COMPUTED",
         true_full_H20738_Ritz="NOT_COMPUTED",
         Wilson_first_excitation_weight="HOLD",
         issue_137="OPEN")


if __name__=="__main__":
    if sys.argv[1:]==["toy"]:
        toy()
    elif sys.argv[1:]==["real"]:
        real()
    else:
        need(False,"usage_toy_or_real")
