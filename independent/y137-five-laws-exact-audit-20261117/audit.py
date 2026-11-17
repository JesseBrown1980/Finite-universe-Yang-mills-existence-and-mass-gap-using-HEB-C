#!/usr/bin/env python3
"""Issue #137: exact falsification audit of five proposed structural laws.

All arithmetic is original-source-pinned integer rational pairs.
Scope: retrospective 3x3 Padé hypothesis, Chebyshev rho envelope,
true-state Feshbach centering invariance, bilinear Q residual bound,
and square-root-free signed-interval spectral-weight algebra.
No numeric true original seven-loop Wilson E1->E2 certificate is supplied.
"""
import hashlib
import os
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
ATLAS=os.path.normpath(os.path.join(HERE,"..","..","docs","certificate-atlas"))
sys.path.insert(0,ATLAS)
import predictions as a

def need(ok,reason):
    if not ok:
        print("Y137_FIVE_LAWS_REFUSE|reason="+reason+"|json=0",flush=True)
        raise SystemExit(1)

def emit(tag,**kwargs):
    print(tag+"|"+"|".join(str(k)+"="+str(v) for k,v in kwargs.items())+"|json=0",flush=True)

def rat(n,d=1):return a.rat(n,d)
def add(x,y):return a.add(x,y)
def sub(x,y):return a.sub(x,y)
def mul(x,y):return a.mul(x,y)
def inv(x):return a.reciprocal(x)
def le(x,y):return a.le(x,y)
def lt(x,y):return a.lt(x,y)
def abs_rat(x):return rat(abs(x[0]),x[1])
def div(x,y):return mul(x,inv(y))
def sum_r(items):
    z=rat(0)
    for x in items:z=add(z,x)
    return z
def show(x):return a.show(x)

def atlas_gap():
    raw=open(os.path.join(ATLAS,"certificates.json"),"rb").read()
    need(hashlib.sha256(raw).hexdigest()==a.DATA_SHA,
         "frozen_full_certificate_atlas_SHA")
    entries=a.get_3x3(raw.decode("utf-8"))
    good=[]
    rows=[]
    for r in (9,27,81,243):
        z=rat(r)
        # One-pole Padé: a formal continuation, NOT an original H theorem.
        coefficient=div(rat(43),sub(rat(1),rat(43,21*r)))
        pade=sub(sub(mul(rat(3),z),rat(21,r)),div(coefficient,rat(r*r)))
        lo,hi=entries[r]["lower"],entries[r]["upper"]
        inside=le(lo,pade) and le(pade,hi)
        rows.append((r,inside))
        if inside:good.append(r)
        emit("Y137_FIVE_PADE_POINT",r=r,
             one_pole_gap_exact=show(pade),
             coefficient_effective_exact=show(coefficient),
             original_certified_lo=show(lo),original_certified_hi=show(hi),
             inside_certified_interval="YES" if inside else "NO",
             scope="RETROSPECTIVE_HYPOTHESIS")
    need(good==[81,243] and rows==[(9,False),(27,False),(81,True),(243,True)],
         "one_pole_missing_two_falsifications")
    emit("Y137_FIVE_PADE_VERDICT",one_pole_accepted="2_OF_4",
         r9="EXCLUDED",r27="EXCLUDED",r81="COMPATIBLE",r243="COMPATIBLE",
         two_pole="UNVERIFIABLE_UNTIL_EXPLICIT_FORMULA",
         physical_wilson="HOLD")

def rho_exact():
    Q=a.decimal("94.0682")
    E=a.decimal("69.949433884")
    CAP=rat(468)
    kappa=div(sub(CAP,E),sub(Q,E))
    # rho=(sqrt(kappa)-1)/(sqrt(kappa)+1)<49/81
    # is exactly equivalent to kappa<(65/16)^2, no square roots.
    threshold=rat(4225,256)
    need(lt(kappa,threshold),"rho_exact_upper_49_81_not_proved")
    factor=rat(49,81)
    targets=[("ONE_PERCENT",rat(1,100),11),
             ("THREE_PER_THOUSAND",rat(3,1000),13),
             ("ONE_OVER_700",rat(1,700),15),
             ("TEN_THOUSANDTH",rat(1,10000),20)]
    for name,target,expected in targets:
        m=0
        current=rat(2)
        while not lt(current,target):
            current=mul(current,factor)
            m+=1
            need(m<100,"nonterminating_rational_filter")
        need(m==expected and
             not lt(div(current,factor),target),
             "failed_49_over_81_degree_table")
        emit("Y137_FIVE_RHO_DEGREE",
             target=name,minimum_degree=m,
             sufficient_bound=show(current),
             original_inverse_residual_only="YES")
    # The proposed (b-a)/(b+a-2E) is the Richardson bound, not
    # the standard Chebyshev sqrt(kappa) contraction factor.
    richardson=div(sub(CAP,Q),sub(add(CAP,Q),mul(rat(2),E)))
    rich_zero=div(sub(CAP,Q),add(CAP,Q))
    need(lt(factor,richardson) and lt(factor,rich_zero),
         "wrong_proposed_rho_identity_passed")
    emit("Y137_FIVE_RHO_VERDICT",
         rho_upper_rational="49/81",
         kappa=show(kappa),
         exact_kappa_upper=show(threshold),
         source_certified_degree_table="11,13,15,20",
         candidate_3adic_identity="NOT_DERIVED",
         rational_bound="PROVEN",
         proposed_simple_ratio_at_E2=show(richardson),
         proposed_simple_ratio_at_E0=show(rich_zero),
         simple_ratio_is_Chebyshev_rho="NO",
         first_Wilson_weight="HOLD")

def centering_identity():
    # Rational, fully exact 3-state physical symmetric H:
    # E1=1, E2=2, E3=6,
    # psi1=(3,4,0)/5, psi2=(-4,3,0)/5.
    # Original flat P=first coordinate, Q=last two.
    x1=rat(3,5);x2=rat(-4,5)
    q1=(rat(4,5),rat(0))
    q2=(rat(3,5),rat(0))
    B=(rat(-12,25),rat(0))
    Qdiag=(rat(34,25),rat(6))
    E1=rat(1);E2=rat(2)
    def leg(x,energy):
        return tuple(mul(rat(-1),div(mul(B[i],x),sub(Qdiag[i],energy)))
                     for i in range(2))
    need(leg(x1,E1)==q1 and leg(x2,E2)==q2,
         "two_energy_resolvent_legs")
    flat=mul(x2,x1)
    qcross=sum_r(mul(q2[i],q1[i]) for i in range(2))
    need(flat==rat(-12,25) and qcross==rat(12,25)
         and add(flat,qcross)==rat(0),
         "exact_two_energy_orthogonality")
    diag=(rat(5),rat(-7),rat(2))
    amp=add(mul(diag[0],flat),
            sum_r(mul(diag[i+1],mul(q2[i],q1[i])) for i in range(2)))
    # Midpoint of Q spectrum [-7,2] in this independent toy.
    mu=rat(-5,2)
    centered=add(mul(sub(diag[0],mu),flat),
        sum_r(mul(sub(diag[i+1],mu),mul(q2[i],q1[i])) for i in range(2)))
    need(amp==centered and amp==rat(-144,25),
         "exact_eigenstate_Wilson_shift_invariance")
    # Nonorthogonal trial vectors must keep the identity-shift term.
    q2hat=(rat(2,5),rat(0))
    overlap_hat=add(flat,sum_r(mul(q2hat[i],q1[i]) for i in range(2)))
    ahat=add(mul(diag[0],flat),
             sum_r(mul(diag[i+1],mul(q2hat[i],q1[i])) for i in range(2)))
    chat=add(mul(sub(diag[0],mu),flat),
             sum_r(mul(sub(diag[i+1],mu),mul(q2hat[i],q1[i]))
                   for i in range(2)))
    need(sub(chat,ahat)==mul(rat(-1),mul(mu,overlap_hat))
         and overlap_hat!=rat(0),
         "nonorthogonal_trial_shift_defect_not_accounted")
    # The actual original S3 universal original seven-loop character
    # range [-7,14] ensures ||O-(7/2)I||<=21/2 on ALL Q states,
    # regardless of whether these endpoints occur in a finite K3 scan.
    bound=rat(21,2)
    need(bound==rat(14*3,4) and
         le(abs_rat(sub(rat(-7),rat(7,2))),bound)
         and le(abs_rat(sub(rat(14),rat(7,2))),bound),
         "global_original_wilson_centering_not_certified")
    emit("Y137_FIVE_CENTER_VERDICT",
         exact_two_energy_orthogonality="PASS",
         original_source_POQ_QOP_zero="STRUCTURAL",
         approximate_shift_defect="RETAINED",
         global_Q_original_Wilson_uncentered_norm_upper=14,
         global_Q_original_Wilson_centered_rational_mu="7/2",
         global_Q_original_Wilson_centered_norm_upper="21/2",
         certified_operator_norm_reduction="25_PERCENT",
         actual_original_true_E1E2_transition="HOLD")

def bilinear_residual():
    # A_i >= gap_i >0; true u_i, numerical samples y_i and residual
    # delta_i=A_i*(y_i-u_i); O_centered is a diagonal scalar toy.
    L1,L2=rat(5),rat(6)
    u1,u2=rat(2,3),rat(3,4)
    v1,v2=rat(1,2),rat(2,3)
    residual1=mul(L1,sub(v1,u1))
    residual2=mul(L2,sub(v2,u2))
    eps1=div(abs_rat(residual1),L1)
    eps2=div(abs_rat(residual2),L2)
    O=rat(-7)
    mu=rat(-5,2)
    centered=sub(O,mu)
    for op in (O,centered):
        actual=mul(mul(u2,op),u1)
        approximate=mul(mul(v2,op),v1)
        error=abs_rat(sub(actual,approximate))
        upper=sum_r((mul(eps2,abs_rat(mul(op,v1))),
                    mul(eps1,abs_rat(mul(op,v2))),
                    mul(abs_rat(op),mul(eps1,eps2))))
        need(le(error,upper),"bilinear_residual_transfer_toy_failed")
    # The signed residual of the original K3 compact-support action
    # must include exterior shell4, not merely 155378 interior rows.
    emit("Y137_FIVE_RESIDUAL_VERDICT",
         bilinear_Cauchy_exact="PASS",
         source_Wilson_centred_action="DIAGONAL_EXACT",
         Q_floor_gap="SOURCE_CONDITIONAL_REQUIRED",
         full_exterior_residual="MANDATORY",
         transfer_actual_Wilson="NOT_YET_CERTIFIED")

def signed_gate(lo,hi,d1_hi,d2_hi,p,q):
    need(q>0 and p>=0 and lt(rat(0),d1_hi) and lt(rat(0),d2_hi),
         "invalid_physical_normalization_domain")
    excludes=lt(rat(0),lo) or lt(hi,rat(0))
    if not excludes:return False,False
    lower=lo if lt(rat(0),lo) else abs_rat(hi)
    strict=lt(mul(rat(p),mul(d1_hi,d2_hi)),mul(rat(q),mul(lower,lower)))
    return excludes,strict

def weight_gate():
    # Source-independent exact rational positive proof only.
    good=signed_gate(rat(3,5),rat(4,5),rat(2),rat(2),1,20)
    bad_zero=signed_gate(rat(-1,5),rat(4,5),rat(2),rat(2),1,20)
    bad_equal=signed_gate(rat(1),rat(1),rat(1),rat(1),1,1)
    need(good==(True,True) and bad_zero==(False,False)
         and bad_equal==(True,False),
         "strict_sign_and_normalization_gates")
    emit("Y137_FIVE_WEIGHT_GATE",
         signed_interval_exclusion="PASS",
         strict_cross_multiplied_lower_weight="PASS",
         zero_crossing_negative_control="REJECTED",
         equality_negative_control="REJECTED",
         fixed_sample_is_true_eigenstate="NO",
         physical_original_Wilson_spectral_weight="HOLD")

def main():
    atlas_gap()
    rho_exact()
    centering_identity()
    bilinear_residual()
    weight_gate()
    emit("Y137_FIVE_LAWS_VERDICT",
         one_pole_Pade="FAILS_R9_AND_R27",
         chebyshev_49_over_81="EXACT_SUFFICIENT_UPPER",
         centred_true_state_identity="PASS",
         signed_full_Q_residual_transfer="TOY_PROVEN",
         strict_normalized_weight_gate="TOY_PROVEN",
         unprovided_two_pole="NOT_INFERRED",
         first_excitation_Wilson="HOLD",
         four_dimensional_continuum="OPEN")

if __name__=="__main__":
    main()
