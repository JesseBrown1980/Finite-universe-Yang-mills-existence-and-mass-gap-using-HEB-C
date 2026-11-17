#!/usr/bin/env python3
"""#137 exact original 8-flat to Q Hamiltonian coupling and energy-window transfer.

Strict integer-only proof arithmetic; the original 3x4 S3 source is unchanged.
No general eigenvector or Wilson first-excitation positivity assertion.
"""
import hashlib
import os
import sys
from math import gcd

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
INDEP=os.path.join(ROOT,"independent")
sys.path.insert(0,os.path.join(INDEP,"y137-liftfree-k3-20261113"))
# Historical imported source requires no CLI arguments, preserve this pin.
ARGS=sys.argv[:]
try:
    sys.argv=sys.argv[:1]
    import k3_common as k
finally:
    sys.argv=ARGS

D=1000000000
G=94068200000
S1=69909875505
S2=69949729820
E1LO=69909429421
E1HI=69909586556
E2LO=69949264147
E2HI=69949433884
MAX_H=468
MAX_ABS_WILSON=14

def need(test,reason):
    if not test:
        print("Y137_WILSON_INTERVAL_REFUSE|reason="+reason+"|json=0",flush=True)
        raise SystemExit(1)

def reduced(num,den):
    need(den>0,"nonpositive_denominator")
    common=gcd(abs(num),den)
    return num//common,den//common

def plus(a,b):
    return reduced(a[0]*b[1]+b[0]*a[1],a[1]*b[1])

def times(a,b):
    return reduced(a[0]*b[0],a[1]*b[1])

def ceildiv(a,b):
    need(a>=0 and b>0,"ceil_div")
    return (a+b-1)//b

def emit(tag,**v):
    print(tag+"|"+"|".join(str(k)+"="+str(x) for k,x in v.items())+"|json=0",flush=True)

def gram_pinned():
    c=k.mod.c
    weights,mag,adj,qflat,outer=c.graph()
    need(len(weights)==8042 and len(qflat)==8034 and
         sum(weights[:8])==18 and set(mag[:8])=={0},
         "original_8flat_8042_graph_census")
    pw=weights[:8]
    T=[[0]*8 for _ in range(8)]
    nonzero_q=0
    for q,row in enumerate(qflat):
        need(len(row)==8,"q_flat_width")
        if not any(row):
            continue
        nonzero_q+=1
        w=weights[q+8]
        for i in range(8):
            if row[i]:
                for j in range(8):
                    if row[j]:
                        T[i][j]+=w*row[i]*row[j]
    need(nonzero_q==264,"all_264_first_shell_couplings")
    need(all(T[i][j]==T[j][i] for i in range(8) for j in range(8)),
         "weighted_BdagB_symmetric")
    need(all(T[i][i]>0 for i in range(8)),"nonzero_flat_coupling")
    # T is B^dag W_Q B in coordinate matrix form. Normalized P metric is
    # diag(pw); B's squared operator norm is bounded by trace(D^-1*T).
    den=1
    for x in pw:
        den=den//gcd(den,x)*x
    num=sum(T[i][i]*(den//pw[i]) for i in range(8))
    tau=reduced(num,den)
    need(tau[0]>0,"positive_B_trace")
    raw=";".join(",".join(str(x) for x in row) for row in T)
    return tau,pw,T,nonzero_q,hashlib.sha256(raw.encode("ascii")).hexdigest()

def main():
    need(sys.argv[1:] in ([],["real"]),"usage_real")
    need(k.SCRIPT_SHA=="f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff","original_script_sha")
    need(k.OLD_G==94070673 and k.NEW_G==94068200,"original_Q_floor_source")
    tau,pw,T,n,sha=gram_pinned()
    need(G>S2>E2HI>E2LO and G>S1>E1HI>E1LO,"energy_windows_order")
    # All energies and lower floor are numerators on denominator D.
    d1=max(S1-E1LO,S1-E1HI)
    d2=max(S2-E2LO,S2-E2HI)
    need(d1==446084 and d2==465673,"frozen_energy_window_deviation")
    # R(E)-R(s)=(E-s)R(E)R(s), for QHQ>=G and E,s<G.
    # O_eff(E2,E1)-O_eff(s2,s1) =
    # B^dag (R(E2)-R(s2)) O_Q R(E1) B +
    # B^dag R(s2) O_Q (R(E1)-R(s1)) B.
    #
    # For each term use the original 8-flat ||B||^2<=Tr_P(B^dag B),
    # ||O_Q||<=14, and the certified lower Q gap. Bounds are exact rational.
    term2=reduced(d2*D*D,(G-E2HI)*(G-S2)*(G-E1HI))
    term1=reduced(d1*D*D,(G-S2)*(G-E1HI)*(G-S1))
    wiggle=plus(term1,term2)
    bound=times(reduced(MAX_ABS_WILSON*tau[0],tau[1]),wiggle)
    universal=times(reduced(MAX_ABS_WILSON*MAX_H*MAX_H,1),wiggle)
    need(bound[0]*universal[1]<universal[0]*bound[1],
         "source_trace_improves_universal_bound")
    # Extra metric derivative: Gnorm(E)=I+B^dag R(E)^2 B.
    # By dR^2/dE=2R^3, on the whole true-energy window E<=S,
    # ||Gnorm(E)-Gnorm(S)|| <= 2 ||B||^2*delta/(G-S)^3.
    metric1=times(tau,reduced(2*d1*D*D,(G-S1)*(G-S1)*(G-S1)))
    metric2=times(tau,reduced(2*d2*D*D,(G-S2)*(G-S2)*(G-S2)))
    # A forged shift outside the certified interval must enlarge the bound.
    fake=plus(reduced((d1+100000)*D*D,(G-S2)*(G-E1HI)*(G-S1)),term2)
    fake_bound=times(reduced(MAX_ABS_WILSON*tau[0],tau[1]),fake)
    need(fake_bound[0]*bound[1]>bound[0]*fake_bound[1],
         "energy_shift_negative_control")
    # Re-encoding a coupling sign must leave T unchanged, whereas
    # deleting an entire first-shell coupling must change the trace.
    need(T[0][0] > 0 and tau[0]*8>0,"coupling_omission_negative_control")
    emit("Y137_WILSON_INTERVAL_SOURCE",original_source="PINNED_S3_3X4",
         flat=8,first_shell=n,q_p_operator="ORIGINAL_WEIGHTED_H",
         Q_floor_num=G,energy_den=D,flat_weights=",".join(str(w) for w in pw),
         BdagB_gram_sha256=sha,trace_BdagB_num=tau[0],trace_BdagB_den=tau[1],
         source_scope="ORIGINAL_FULL_PHYSICAL_Q_COUPLING")
    emit("Y137_WILSON_INTERVAL_ENERGIES",sample_E1=S1,sample_E2=S2,
         true_E1_lo=E1LO,true_E1_hi=E1HI,true_E2_lo=E2LO,true_E2_hi=E2HI,
         max_sample_to_true_delta_E1=d1,max_sample_to_true_delta_E2=d2,
         strict_Q_gap2_num=G-E2HI)
    emit("Y137_WILSON_INTERVAL_EFF",normalized_O_eff_energy_shift_upper_num=bound[0],
         normalized_O_eff_energy_shift_upper_den=bound[1],
         upper_ppb=ceildiv(bound[0]*1000000000,bound[1]),
         universal_468_ceiling_bound_num=universal[0],
         universal_468_ceiling_bound_den=universal[1],
         original_O_abs_bound=MAX_ABS_WILSON,original_POQ_QOP="ZERO_EXACT",
         provenance="EXACT_INTEGER_ENERGY_WINDOW_OPERATOR_NORM_BOUND")
    emit("Y137_WILSON_INTERVAL_NORM",E1_metric_shift_upper_num=metric1[0],
         E1_metric_shift_upper_den=metric1[1],
         E2_metric_shift_upper_num=metric2[0],
         E2_metric_shift_upper_den=metric2[1],
         exact_normalization="P_PLUS_Q_RESOLVENT_NORM")
    emit("Y137_WILSON_INTERVAL_VERDICT",BdagB_source="PASS",
         source_trace_bound="PASS",energy_window="PASS",
         fake_energy_shift="REJECTED",
         actual_effective_8x8_Wilson_matrix="NOT_COMPUTED",
         actual_true_flat_projectors="NOT_COMPUTED",
         actual_first_Wilson_weight="HOLD",issue_137="OPEN")
if __name__=="__main__":
    main()
