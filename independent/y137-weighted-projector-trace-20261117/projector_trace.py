#!/usr/bin/env python3
"""Issue #137 independent weighted projector-trace positivity verifier.

Actual original physical Wilson O is multiplication, with centered
integer O2=2O-7I. The flat effective matrix is not in Euclidean
coordinates: the archived signed HBP A_ij is a Wflat *bilinear* form.
To use the proposed trace test, K=Wflat^-1 A/T^2,
K^sharp=Wflat^-1 K^T Wflat, and P_i=v_i (v_i^T Wflat)/||v_i||_W^2.

The identity tr(P2 K P1 K^sharp)=|<v2,Kv1>_W|^2 for flat-unit
rank-one projections is checked by two independent exact integer
paths, both on a nonnormal three-dimensional toy and the ACTUAL
8x8 original centered S3 source matrix from #282.

True physical P_i are unknown. Their source-conditional Stage E flat
angle cones and the original source-specific #281 dual amplitude
give an interval lower on sqrt of the trace, with directional
rather than isotropic errors. A negative strict margin is HOLD.

The original unshifted and centered source matrix difference is also
used to reconstruct the exact shared-trial two-energy overlap Gram:
  Ghat = (2*Mhat_unshifted-Mhat_O2)/7.
This exact algebraic source correlation is checked under matching
original 8x8 inverse hashes; an entrywise interval bounds true G.
The exact true physical eigenstate orthogonality implies
<x2,Gtrue(E2,E1)x1>_W=0, with G=I+B*R2R1B.
The initial Gram check tests consistency, not an assumed improvement.
"""
import os
import sys
from math import gcd,isqrt

HERE=os.path.dirname(os.path.abspath(__file__))
INDEP=os.path.dirname(HERE)
sys.path.insert(0,os.path.join(INDEP,"y137-centered-source-flat-join-20261117"))
import centered_join as joined
stage_e=joined.stage_e
old=joined.old
T=1000000000000
B=1000000000
U=1000000000000
N=8
WF=old.WF
ORIGINAL_WEIGHTS=(1,3,2,3,3,2,2,2)

def need(ok,reason):
    if not ok:
        print("Y137_PROJECTOR_TRACE_REFUSE|reason="+reason+"|json=0",flush=True)
        raise SystemExit(1)

def emit(tag,**items):
    print(tag+"|"+"|".join(str(k)+"="+str(v) for k,v in items.items())+
          "|json=0",flush=True)

def r(n,d=1):
    need(d!=0,"zero_rational_denominator")
    if d<0:n,d=-n,-d
    q=gcd(abs(n),d)
    return n//q,d//q

def add(x,y):return r(x[0]*y[1]+x[1]*y[0],x[1]*y[1])
def mul(x,y):return r(x[0]*y[0],x[1]*y[1])

def mm(X,Y):
    n=len(X);need(n>0 and n==len(Y),"matrix_dim")
    return [[sumrat(mul(X[i][k],Y[k][j]) for k in range(n))
             for j in range(n)] for i in range(n)]

def sumrat(values):
    z=r(0)
    for v in values:z=add(z,v)
    return z

def trace(X):return sumrat(X[i][i] for i in range(len(X)))

def weighted_projector(v,weights):
    n=sum(weights[i]*v[i]*v[i] for i in range(len(v)))
    need(n>0,"weighted_flat_norm_positive")
    return [[r(v[i]*weights[j]*v[j],n) for j in range(len(v))]
            for i in range(len(v))]

def operator_from_raw(A,weights,scale):
    n=len(A)
    return [[r(A[i][j],weights[i]*scale) for j in range(n)]
            for i in range(n)]

def adjoint_from_raw(A,weights,scale):
    n=len(A)
    return [[r(A[j][i],weights[i]*scale) for j in range(n)]
            for i in range(n)]

def raw_amplitude(A,v1,v2):
    return sum(v2[i]*A[i][j]*v1[j]
               for i in range(len(v2)) for j in range(len(v1)))

def trace_two_routes(A,weights,v1,v2,scale):
    n1=sum(weights[i]*v1[i]*v1[i] for i in range(len(v1)))
    n2=sum(weights[i]*v2[i]*v2[i] for i in range(len(v2)))
    need(n1>0 and n2>0,"flat_source_norm")
    P1=weighted_projector(v1,weights)
    P2=weighted_projector(v2,weights)
    K=operator_from_raw(A,weights,scale)
    Ks=adjoint_from_raw(A,weights,scale)
    product=trace(mm(mm(mm(P2,K),P1),Ks))
    amp=raw_amplitude(A,v1,v2)
    scalar=r(amp*amp,scale*scale*n1*n2)
    need(product==scalar,"source_weighted_trace_not_scalar_overlap")
    return product,amp,n1,n2

def toy():
    w=(1,2,3)
    A=[[5,-1,2],[3,4,7],[-5,2,6]]
    a=(2,1,0)
    b=(1,0,1)
    value,amp,n1,n2=trace_two_routes(A,w,a,b,11)
    need(value[0]>0 and value[1]>0 and amp!=0,
         "weighted_rankone_trace_nonnormal_toy")
    K=operator_from_raw(A,w,11)
    wrong=[[K[j][i] for j in range(3)] for i in range(3)]
    wrongT=trace(mm(mm(mm(weighted_projector(b,w),K),
                         weighted_projector(a,w)),wrong))
    need(wrongT!=value,"Euclidean_transpose_looks_like_W_adjoint")
    need(isqrt(15)==3 and old.ceildiv(7,3)==3,
         "integer_root_toy")
    emit("Y137_PROJECTOR_TRACE_TOY",
         nonnormal_weighted_3x3="PASS",
         W_adjoint_required="PASS",
         Euclidean_transpose_negative_control="REJECTED",
         exact_rank_one_trace="PASS",
         actual_first_Wilson_weight="HOLD")

def original_gram(A2,R2,A0,R0):
    meta=old.find(open(old.MATRIX,encoding="ascii").read().splitlines(),
                  "Y137_O8_MATRIX")[0]
    cm=old.parse(open(joined.CENTERED,encoding="ascii").read().splitlines()[2])
    for field in ("original_Q_trial_1_U_sha256",
                  "original_Q_trial_2_U_sha256",
                  "original_Q_trial_1_G_sha256",
                  "original_Q_trial_2_G_sha256"):
        need(meta[field]==cm[field],"unshifted_centered_Q_trials_differ")
    # This exact source subtraction reconstructs the shared truncated
    # two-energy Gram source from the two multiplication observables.
    G=[[0]*N for _ in range(N)]
    E=[[0]*N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            n=2*A0[i][j]-A2[i][j]
            need(n%7==0,"source_midpoint_shift_Gram_not_exact")
            G[i][j]=n//7
            E[i][j]=old.ceildiv(2*R0[i][j]+R2[i][j],7)
    return G,E

def actual():
    toy()
    ppb=joined.dual_input()
    A,R,s1,s2,f1,f2=joined.source_data()
    A0,R0,a1,a2=old.freeze()
    need(WF==ORIGINAL_WEIGHTS and len(A)==N and len(R)==N,
         "original_source_8_weighted_flat_dimension")
    v1,v2=old.V1,old.V2
    tr,amp,n1,n2=trace_two_routes(A,WF,v1,v2,T*T)
    need(tr[0]>0,"positive_source_central_trace")
    # Source whole-Q raw original centered matrix interval, 64
    # independent worst-case entries: default box loses correlations.
    signed_box=sum(abs(v2[i]*v1[j])*R[i][j]
                   for i in range(N) for j in range(N))
    box_zero=int(abs(amp)<=signed_box)
    Gram,Gradius=original_gram(A,R,A0,R0)
    baseg=raw_amplitude(Gram,v1,v2)
    Eg=sum(abs(v2[i]*v1[j])*Gradius[i][j]
           for i in range(N) for j in range(N))
    need(Eg>=0,"signed_two_energy_Gram_interval")
    # Source-conditional physical Gnorm <= 1+72/(gamma2*gamma1).
    g1=old.FLOOR-old.E1_HI
    g2=old.FLOOR-old.E2_HI
    need(g1>0 and g2>0,"original_Q_floor")
    Gnorm=U+old.ceildiv(72*B*B*U,g1*g2)
    g_sample_floor=max(0,abs(baseg)-Eg)
    # Each exact true projector must satisfy <x2,Gtrue x1>=0.
    # Approx sample may be nonorthogonal, bounded by both angle cones.
    geometric_cap=old.ceildiv((s1+s2)*Gnorm,U)
    geometric_cap+=old.ceildiv(s1*s2*Gnorm,U*U)
    c1=isqrt(U*U-s1*s1)
    c2=isqrt(U*U-s2*s2)
    # Lower bound for possible |<v2,G v1>| from full 8x8
    # source entries is normalized by sqrt(n1 n2) ROUND DOWN.
    nf=old.sqrtceil(n1*n2)
    gram_lower=old.ceildiv(g_sample_floor*U,T*T*nf) if g_sample_floor else 0
    # Since nf is upward, ceil may still overstate the lower bound.
    # Use floor for conservative source lower instead.
    gram_lower=(g_sample_floor*U)//(T*T*nf)
    admissible=old.ceildiv(geometric_cap*U*U,c1*c2)
    need(gram_lower<=admissible,
         "source_projector_orthogonality_contradiction")
    # Conditional trace source signal is the fully original centered
    # *integer O2* fixed-direction squared normalized source weight.
    # Translate full normalized source to flat-normalized absolute amp.
    sample_amplitude=isqrt(ppb*U*U//1000000000)
    need(sample_amplitude>0 and 0<s1<U and 0<s2<U,
         "conditional_spectral_source_outside_scope")
    # Deflated source-specific action norms and interval inflation,
    # independently recomputed in Wflat bilinear coordinates.
    row=[sum(A[i][j]*v1[j] for j in range(N)) for i in range(N)]
    col=[sum(A[i][j]*v2[i] for i in range(N)) for j in range(N)]
    def_forward=n2*sum((6//WF[i])*row[i]*row[i]
                      for i in range(N))-6*amp*amp
    def_adjoint=n1*sum((6//WF[j])*col[j]*col[j]
                      for j in range(N))-6*amp*amp
    den=6*n1*n2*T*T*T*T
    need(def_forward>=0 and def_adjoint>=0,"deflation_PSD")
    forward=old.sqrt_upper_scaled(def_forward,den)
    adjoint=old.sqrt_upper_scaled(def_adjoint,den)
    eraw=sum((36//(WF[i]*WF[j]))*R[i][j]*R[i][j]
             for i in range(N) for j in range(N))
    err=old.sqrt_upper_scaled(eraw,36*T*T*T*T)
    op=21*U+old.ceildiv(21*72*B*B*U,g1*g2)
    # Sharpen previously accepted two-sided scalar triangular bound
    # by retaining phase cosines on BOTH linear projector terms.
    pos_signal=sample_amplitude*c1*c2//(U*U)
    term1=old.ceildiv(c2*s1*(adjoint+err),U*U)
    term2=old.ceildiv(c1*s2*(forward+err),U*U)
    term3=old.ceildiv(s1*s2*op,U*U)
    contam=term1+term2+term3
    signed=pos_signal-contam
    trace_lo=(max(0,signed)*max(0,signed))//U
    trace_hi=old.ceildiv(op*op,U)
    need(0<=trace_lo<=trace_hi and trace_hi>0,
         "rank_one_true_projector_trace_interval")
    emit("Y137_PROJECTOR_TRACE_SOURCE",
         original_O="TWICE_SEVEN_LOOP_CENTERED_O2",
         source_Q_8x8="PR282_HOSTED_TRUE_ENERGY_INTERVALS",
         directional_dual="PR281_SOURCE_CORRELATED",
         true_flat_sines="STAGE_E_PR277_SOURCE_CONDITIONAL",
         flat_metric="1,3,2,3,3,2,2,2",
         weighted_adjoint="EXACT",
         true_projector_rank="ONE_EACH",
         two_energy_Gram_center="EXACT_2_ORIGINAL_MINUS_CENTERED_DIV_7",
         same_Q_trial_U_G_hashes="4_OF_4_PASS")
    emit("Y137_PROJECTOR_TRACE_GRAM",
         source_signed_Gram_sample_sha256=old.blob(old.MATRIX),
         source_Gram_abs_lower_per_trillion=gram_lower,
         exact_orthogonality_sample_cap_per_trillion=admissible,
         original_truncated_Gram_asymmetry_max_num=
            max(abs(Gram[i][j]-Gram[j][i]) for i in range(N) for j in range(N)),
         two_energy_true_eigenstate_orthogonality="FEASIBLE",
         full_Q_source_Gram_error="ENTRYWISE_CONSERVATIVE")
    emit("Y137_PROJECTOR_TRACE_BOUNDS",
         original_centered_source_matrix_trace_num_digits=len(str(tr[0])),
         original_centered_source_matrix_trace_den_digits=len(str(tr[1])),
         old_entrywise_sample_amplitude_interval_contains_zero=box_zero,
         original_source_dual_fixed_trace_floor_ppb=ppb,
         angular_signal_lower_per_trillion=pos_signal,
         projector_first_linear_per_trillion=term1,
         projector_second_linear_per_trillion=term2,
         projector_quadratic_per_trillion=term3,
         angular_contamination_upper_per_trillion=contam,
         strict_signed_amplitude_margin_per_trillion=signed,
         true_projector_trace_lower_per_trillion=trace_lo,
         true_projector_trace_upper_per_trillion=trace_hi)
    emit("Y137_PROJECTOR_TRACE_VERDICT",
         exact_weighted_trace_identity="PASS",
         physical_orthogonality_metric="CERTIFIED_SOURCE_COMPATIBLE",
         joint_original_E1E2_source="SAME_CENTERED_SOURCE",
         first_excitation_original_Wilson_projector_trace=
             "CANDIDATE_REQUIRES_REVIEW" if signed>0 else "HOLD",
         quantitative_normalized_original_Wilson_weight="NOT_CERTIFIED",
         issue_137="OPEN")

if __name__=="__main__":
    if sys.argv[1:]==["toy"]:toy()
    elif sys.argv[1:]==["real"]:actual()
    else:need(False,"usage_toy_or_real")
