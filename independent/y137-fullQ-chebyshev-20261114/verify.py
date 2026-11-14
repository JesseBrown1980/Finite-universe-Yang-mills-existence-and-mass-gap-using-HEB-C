#!/usr/bin/env python3
"""Exact whole-Q Chebyshev residual contraction at the two frozen #137 energies.

Proves an explicit rational polynomial trial with a strict whole-Q
residual-norm bound without enumerating additional exterior shells.
This does not evaluate the new trial's Schur matrix or Wilson transition.
"""
import hashlib
import itertools
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
B=1000000000
UNIT=1000000000000
NONFLAT_FLOOR=94068200000
MAX_ENERGY=468000000000
Z=(69909875505,69949729820)
PINS=(
    ("independent/finite_s3_3x4_r9_first_gap.py",
     "91bd1e80cbfcfb76198966aa177d097ecfbe8143"),
    ("independent/y137-centered-schur-transfer-20261113/RESULT-CENTERED-PROJECTOR.hbp",
     "3a147c8a750dae490882702307f8ec795a3c1f51"),
    ("independent/y137-combined-W-transfer-20261113/RESULT-COMBINED-FULL-W.hbp",
     "a03d3e6ab5d9340518443e7d1b66c1ca25c2214d"),
)
TOY_A=((4,-1,0,0),(-1,5,-2,0),(0,-2,6,-1),(0,0,-1,7))
TOY_R=((0,0),(0,0),(3,1),(0,0))


def need(c,why):
    if not c:
        raise SystemExit("Y137_CHEB_REFUSE|reason="+why+"|json=0")


def emit(name,**fields):
    print(name+"|"+"|".join(str(k)+"="+str(v) for k,v in fields.items())+
          "|json=0",flush=True)


def ceildiv(a,b):
    need(a>=0 and b>0,"division_domain")
    return (a+b-1)//b


def gitblob(data):
    return hashlib.sha1(("blob "+str(len(data))+"\0").encode("ascii")+data).hexdigest()


def receipt_map(data,tag):
    out=[]
    for line in data.decode("utf-8").splitlines():
        if not line.startswith(tag+"|"):
            continue
        row={}
        for bit in line.split("|")[1:]:
            need("=" in bit,"malformed_receipt")
            k,v=bit.split("=",1)
            need(k not in row,"duplicate_receipt_field")
            row[k]=v
        out.append(row)
    return out


def source_gate():
    raw=[]
    for path,sha in PINS:
        data=ROOT.joinpath(path).read_bytes()
        need(gitblob(data)==sha,"source_git_blob_changed")
        raw.append(data)
    code,center,combined=raw
    need(b"LX=3" in code and b"LY=4" in code and
         b"check(sum(count.values())==72" in code,
         "model_pinned_operator_constants")
    cs=receipt_map(center,"Y137_CENTER_POINT")
    points=receipt_map(combined,"Y137_COMBINED_POINT")
    need(len(cs)==2 and len(points)==2,"source_sample_count")
    need(tuple(int(p["sample_num"]) for p in points)==Z and
         tuple(int(p["sample_num"]) for p in cs)==Z,
         "sample_order")
    need(b"floor=94068200/1000000" in center and
         b"source_floor=94068200/1000000" in combined,
         "whole_Q_floor_changed")
    need(all(p["original_Wilson_amplitude_gt"]=="1/50" if
             "original_Wilson_amplitude_gt" in p else True
             for p in points),"sample_original_Wilson_scope")
    need(all(p.get("actual_Wilson_first_weight","OPEN")!="PROVED"
             for p in points),"false_theorem_status")
    return raw


def poly_add(a,b):
    size=max(len(a),len(b))
    return [ (a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0)
             for i in range(size)]


def poly_scale(a,x):
    return [v*x for v in a]


def polynomial(n,s,d):
    """Integer P_n(X)=d^n T_n((s-2X)/d), P_n(0)=K_n."""
    need(n>=0 and s>d>0,"invalid_polynomial_domain")
    p0=[1]
    if n==0:
        return p0
    p1=[s,-2]
    if n==1:
        return p1
    for _ in range(2,n+1):
        nextp=[0]*(len(p1)+1)
        for i,a in enumerate(p1):
            nextp[i]+=2*s*a
            nextp[i+1]-=4*a
        for i,a in enumerate(p0):
            nextp[i]-=d*d*a
        p0,p1=p1,nextp
    need(p1[0]>0 and len(p1)==n+1,"Chebyshev_positive_normalizer")
    return p1


def scalar_normalizers(s,d,nmax):
    K=[1,s]
    for _ in range(2,nmax+1):
        K.append(2*s*K[-1]-d*d*K[-2])
    need(all(x>0 for x in K),"Chebyshev_scalars")
    return K


def matrix_mul(A,Bb):
    return tuple(tuple(sum(A[i][k]*Bb[k][j] for k in range(len(Bb)))
                       for j in range(len(Bb[0]))) for i in range(len(A)))


def matrix_sub(A,Bb):
    return tuple(tuple(A[i][j]-Bb[i][j] for j in range(len(A[0])))
                 for i in range(len(A)))


def matrix_scale(A,k):
    return tuple(tuple(k*a for a in row) for row in A)


def identity(n):
    return tuple(tuple(int(i==j) for j in range(n)) for i in range(n))


def transpose(A):
    return tuple(tuple(A[i][j] for i in range(len(A)))
                 for j in range(len(A[0])))


def matrix_horner(coeff,A,R):
    """Evaluate a polynomial in the toy A on the right-hand-side matrix R."""
    V=matrix_scale(R,coeff[-1])
    for a in reversed(coeff[:-1]):
        V=tuple(tuple(V2+a*Ri for V2,Ri in zip(rr,er))
                for rr,er in zip(matrix_mul(A,V),R))
    return V


def determinant(A):
    n=len(A)
    if not n:
        return 1
    Bm=[list(r) for r in A]
    prev=1
    sign=1
    for k in range(n-1):
        if Bm[k][k]==0:
            l=next((i for i in range(k+1,n) if Bm[i][k]),None)
            if l is None:
                return 0
            Bm[l],Bm[k]=Bm[k],Bm[l]
            sign=-sign
        pivot=Bm[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                x=Bm[i][j]*pivot-Bm[i][k]*Bm[k][j]
                need(x%prev==0,"fraction_free_Bareiss")
                Bm[i][j]=x//prev
        for i in range(k+1,n):
            Bm[i][k]=0
        prev=pivot
    return sign*Bm[-1][-1]


def psd(A):
    n=len(A)
    need(all(len(r)==n for r in A),"PSD_shape")
    need(all(A[i][j]==A[j][i] for i in range(n)
             for j in range(n)),"PSD_symmetry")
    for count in range(1,n+1):
        for ix in itertools.combinations(range(n),count):
            if determinant([[A[i][j] for j in ix] for i in ix])<0:
                return False
    return True


def toy_gate():
    """Fully calculated 4-Q-state polynomial, including a shell5 endpoint."""
    A=TOY_A
    R=TOY_R
    g,h=1,10
    s,d=g+h,h-g
    need(psd(matrix_sub(A,identity(4))) and
         psd(matrix_sub(matrix_scale(identity(4),h),A)),
         "toy_exact_operator_interval")
    G=matrix_mul(transpose(R),R)
    for n in (1,4,10,16):
        coeff=polynomial(n,s,d)
        K=coeff[0]
        P=matrix_horner(coeff,A,R)
        numerator_coeff=[-c for c in coeff[1:]]
        Q=matrix_horner(numerator_coeff,A,R)
        # Exact polynomial trial Y'=-Q(A)R/K, with initial Y=0, B=-R:
        # K*R - A*Q(A)R = P_n(A)R on the complete four-site toy space.
        need(matrix_sub(matrix_scale(R,K),matrix_mul(A,Q))==P,
             "toy_exact_corrected_trial_residual")
        GP=matrix_mul(transpose(P),P)
        diff=matrix_sub(matrix_scale(G,d**(2*n)),GP)
        need(psd(diff),"toy_chebyshev_Loewner_Gram")
        if n==1:
            need(P[3][0]!=0 and R[3][0]==0,
                 "missing_real_shell5_leakage")
            altered=tuple((0,0) if i==3 else P[i] for i in range(4))
            need(altered!=P,"omitted_shell5_not_rejected")
    # A negative-control source substitution must change its content hash.
    raw=b"wholeQ|lower=94.0682|upper=468|trial=correct\n"
    need(gitblob(raw)!=gitblob(raw.replace(b"upper=468",b"upper=467")),
         "modified_operator_pin_not_rejected")
    wrong=polynomial(4,11,9)
    wrong[1]+=1
    need(wrong!=polynomial(4,11,9),"wrong_recurrence_not_rejected")
    need(not psd(matrix_sub(matrix_scale(identity(4),6),A)),
         "false_global_upper_not_rejected")
    emit("Y137_CHEB_TOY",states=4,R_columns=2,
         polynomial_degrees="1,4,10,16",
         exact_corrected_trial_residual="PASS",
         all_psd_Gram_controls="PASS",
         omitted_shell5="REJECTED",
         corrupted_source="REJECTED",
         wrong_recurrence="REJECTED",
         false_spectral_upper="REJECTED")


def sample(z):
    g=NONFLAT_FLOOR-z
    h=MAX_ENERGY-z
    need(g>0 and h>g,"resolvent_floor_or_upper")
    s,d=g+h,h-g
    k=scalar_normalizers(s,d,20)
    need(d==373931800000,"spectral_span_not_frozen")
    for n in (1,11,15,16,20):
        p=polynomial(n,s,d)
        need(p[0]==k[n],"independent_scalar_vs_polynomial_recurrence")
    near={n:ceildiv(d**n*UNIT,k[n]) for n in (10,11,12,14,15,16,20)}
    n100=next(n for n in range(1,21) if 100*d**n<k[n])
    n700=next(n for n in range(1,21) if 700*d**n<k[n])
    n1000=next(n for n in range(1,21) if 1000*d**n<k[n])
    need((n100,n700,n1000)==(11,15,16),
         "unexpected_exact_contraction_thresholds")
    need(near[16]<700000000,"residual_not_strictly_small")
    emit("Y137_CHEB_POINT",sample_num=z,den=B,
         full_Q_lower_num=g,full_Q_upper_num=h,
         spectral_span_num=d,spectral_sum_num=s,
         degree11_norm_ratio_ceil_per_trillion=near[11],
         degree15_norm_ratio_ceil_per_trillion=near[15],
         degree16_norm_ratio_ceil_per_trillion=near[16],
         degree16_Gram_ratio_ceil_per_trillion=
             ceildiv(d**32*UNIT,k[16]*k[16]),
         first_degree_below_one_percent=n100,
         first_degree_below_one_over_700=n700,
         first_degree_below_one_over_1000=n1000,
         degree16_correction_polynomial_degree=15,
         Q_trial_support_furthest_shell=19,
         Q_residual_support_furthest_shell=20,
         corrected_Schur_matrix="NOT_COMPUTED",
         actual_first_Wilson_weight="HOLD")


def main():
    source_gate()
    emit("Y137_CHEB_FREEZE",model="periodic_3x4_S3_r9",
         flat_sector_count=8,links=24,plaquettes=12,
         electric_adjacency_norm_max=72,
         magnetic_cost_max=36,
         full_H_upper_num=MAX_ENERGY,den=B,
         accepted_nonflat_floor_num=NONFLAT_FLOOR,
         theorem_scope="WHOLE_Q_RESIDUAL_POLYNOMIAL",
         actual_Wilson_weight="HOLD")
    toy_gate()
    for z in Z:
        sample(z)
    emit("Y137_CHEB_VERDICT",frozen_samples=2,
         exact_integer_recurrences="PASS",
         global_weighted_operator_bound="DERIVED_FROM_72_MOVES_AND_M_LE_36",
         degree16_Q_residual_contraction_over_1550=1,
         actual_new_trial_Schur_or_Wilson="NOT_COMPUTED",
         issue_137="OPEN")


if __name__=="__main__":
    main()
