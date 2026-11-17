#!/usr/bin/env python3
"""#137: direct spectral-projector Wilson positivity by a signed first moment.

If E1<E2<E3, L3<=E3, ||psi1||=1, w=O psi1, then
 A=<w,(L3-H)w>-(L3-E1)|<psi1,w>|^2
  =(L3-E2)||P2 w||^2+sum_{n>=3}(L3-En)||Pn w||^2.
Therefore A>0 implies the TRUE Wilson first-excitation weight is positive.
No E2 approximate eigenvector is required. An explicit lower bound on
A with ground-state and source errors is still necessary.

The real command is an EXACT physical first-moment diagnostic for the
ORIGINAL #180 fixed K3 trial ground sample, not the exact psi1. No
new physical projector or positive Wilson weight is claimed from it.
"""
import hashlib
import os
import sys
from math import isqrt

HERE=os.path.dirname(os.path.abspath(__file__))
INDEP=os.path.dirname(HERE)
sys.path.insert(0,os.path.join(INDEP,"y137-q-dual-weight-20261113"))
# Original pinned k3_common.py deliberately refuses command-line arguments at
# import time. Keep that unchanged and present its expected no-argument import
# context, then restore Stage N's toy/real command arguments for our own main.
_STAGE_N_ARGV=sys.argv[:]
try:
    sys.argv=sys.argv[:1]
    import replay as previous
finally:
    sys.argv=_STAGE_N_ARGV

D=1000000000
E3_LO_NUM=69968699300
E1_LO_NUM=69909429421
E1_HI_NUM=69909586556
E2_LO_NUM=69949264147
E2_HI_NUM=69949433884
SHARE_SHA="b9881651c51a278757bc0fef15de583277330da3"

def need(ok,reason):
    if not ok:
        print("Y137_N_REFUSE|reason="+reason+"|json=0",flush=True)
        raise SystemExit(1)

def emit(label,**values):
    print(label+"|"+"|".join(str(k)+"="+str(v) for k,v in values.items())+
         "|json=0",flush=True)

def sha(v):
    return hashlib.sha256(str(v).encode("ascii")).hexdigest()

def H_moment(ball,p,q):
    """Original W-form <(p,q),H(p,q)> for supported K3 Q trial.

    This uses the genuine original-s3 electric rows; no compression to
    an eight-flat-only operator and no omission of P-Q couplings.
    Diagonal entries incorporate exterior edges as in source #180.
    """
    wf,wq=ball["wf"],ball["wq"]
    n=ball["n"]
    need(len(p)==8 and len(q)==n,"bad_original_physical_trial_shape")
    norm=previous.dot_w(p,p,wf)+previous.dot_w(q,q,wq)
    diag=72*previous.dot_w(p,p,wf)
    pq=0
    qq=0
    for i in range(n):
        diag+=wq[i]*ball["dbase"][i]*q[i]*q[i]
        adj=sum(ball["oc"][h]*q[ball["oj"][h]]
                for h in range(ball["rs"][i],ball["rs"][i+1]))
        qq+=wq[i]*q[i]*adj
        c=ball["C"][i]
        if c is not None:
            pq+=wq[i]*q[i]*sum(c[j]*p[j] for j in range(8))
    energy=diag-qq-2*pq
    need(norm>0 and 0<=energy<=468*norm,
         "full_original_physical_H_moment_operator_ceiling")
    return norm,energy,diag,pq,qq

def toy():
    # H=diag(1,2,5), L3=4, psi1=(1,0,0).
    # Test a visible excitation, an exterior-only dark excitation and
    # a pure ground-channel observable with leakage subtraction.
    e=(1,0,0)
    def proof(w):
        norm=sum(x*x for x in w)
        energy=sum(v*x*x for v,x in zip((1,2,5),w))
        ground=w[0]*w[0]
        return 4*norm-energy-(4-1)*ground
    need(proof((0,1,0))==2,"first_excitation_toy_positive")
    need(proof((0,0,1))==-1,"higher_state_contamination_negative_control")
    need(proof((1,0,0))==0,"ground_leakage_subtraction_control")
    need(E1_HI_NUM<E2_LO_NUM<E2_HI_NUM<E3_LO_NUM,
         "source_conditional_eigenvalue_order")
    emit("Y137_N_TOY",one_sided_projector_identity="PASS",
         positive_visible_E2="PASS",
         negative_high_sector="REJECTED",
         ground_leakage="SUBTRACTED_EXACT",
         actual_full_Wilson_weight="HOLD")

def real():
    toy()
    need(previous.k.SCRIPT_SHA=="f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff",
                  "original_K3_graph_SHA_drift")
    ball,obs=previous.build()
    source=previous.mod.threshold_ball(previous.A1,previous.DEN,
                 previous.ITER,previous.SCALE,ball,previous.FLOOR)
    flat=previous.even_trial(source["U"],[1,2,3,4,5,6,7])
    t=previous.trial(ball,previous.A1,flat)
    p,q=t["p"],t["q"]
    n0,k0,_,_,_=H_moment(ball,p,q)
    need(n0==t["norm"],"original_trial_Gram")
    omin=min(obs);omax=max(obs)
    need(omin>=-7 and omax<=14,"original_Wilson_observable_bounds")
    expectation=sum(ball["wf"][j]*obs[j]*p[j]*p[j] for j in range(8))
    expectation+=sum(ball["wq"][i]*obs[i+8]*q[i]*q[i]
                     for i in range(ball["n"]))
    # q_center=(N*O-<phi,O phi>)*phi, exactly phi-orthogonal.
    pp=[(n0*obs[i]-expectation)*p[i] for i in range(8)]
    qq=[(n0*obs[i+8]-expectation)*q[i]
        for i in range(ball["n"])]
    s0,s1,di,pq,qqterm=H_moment(ball,pp,qq)
    need(sum(ball["wf"][j]*p[j]*pp[j] for j in range(8))+
         sum(ball["wq"][i]*q[i]*qq[i] for i in range(ball["n"]))==0,
         "centered_sample_ground_orthogonality")
    # Adding any scalar c*I to O leaves this centered sample EXACTLY
    # unchanged. In particular this test is invariant under O->O-7/2.
    need(all(((obs[i]+3)*n0-(expectation+3*n0))*p[i]==pp[i]
             for i in range(8)),"scalar_shift_invariance_flat")
    need(all(((obs[i+8]+3)*n0-(expectation+3*n0))*q[i]==qq[i]
             for i in range(ball["n"])),"scalar_shift_invariance_Q")
    margin=E3_LO_NUM*s0-D*s1
    # This is the exact fixed-sample moment, NOT a bound for w=O psi1.
    # A negative margin says this particular unfiltered sample cannot
    # satisfy the direct one-moment sufficient test as written.
    emit("Y137_N_REAL",
         original_K3_source="AUTHENTICATED_BY_PR180",
         original_S3_Wilson="SEVEN_LOOP_RAW_24_LINK",
         source_trial_energy_num=previous.A1,
         actual_ground_energy_interval="69909429421_TO_69909586556",
         third_physical_energy_floor_num=E3_LO_NUM,
         source_flat_dimension=8,
         source_Q_dimension=ball["n"],
         centered_W_norm_SHA256=sha(s0),
         centered_H_energy_SHA256=sha(s1),
         centered_flatQ_coupling_SHA256=sha(pq),
         exact_signed_moment_SHA256=sha(margin),
         exact_signed_moment_sign=(margin>0)-(margin<0),
         centered_moment_per_unit_norm_num=margin,
         centered_moment_per_unit_norm_den=D*s0,
         centered_moment_ppm_floor=margin*1000000//(D*s0),
         unfiltered_sample_one_sided_test="POSITIVE" if margin>0 else "NOT_POSITIVE",
         ground_projector_error="NOT_BOUNDED_FOR_THIS_SAMPLE",
         first_E2_projector="NOT_CERTIFIED",
         actual_Wilson_weight="HOLD")
    emit("Y137_N_VERDICT",
         original_physical_O_H_O_moment="EXACT_FIXED_SAMPLE",
         eigenvector_transfer="NOT_COMPUTED",
         actual_first_Wilson_weight="HOLD",
         required_followup="OBSERVABLE_SPECIFIC_PROJECTOR_OR_FILTER",
         issue_137="OPEN")

if __name__=="__main__":
    args=sys.argv[1:]
    if args==["toy"]:toy()
    elif args==["real"]:real()
    else:need(False,"usage_toy_or_real")
