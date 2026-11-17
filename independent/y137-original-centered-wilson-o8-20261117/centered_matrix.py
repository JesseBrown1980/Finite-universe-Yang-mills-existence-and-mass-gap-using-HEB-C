#!/usr/bin/env python3
"""Issue 137: original seven-loop Wilson 8x8 effective observable interval.

For the original diagonal multiplication observable and eight-flat coordinate
projector, POQ=QOP=0 exactly. For true energies E1,E2, the raw flat
coordinate matrix is M_ij=wflat_i Oflat_i delta_ij +
 <R(E2)B e_i,O_Q R(E1)B e_j>_W.

Use source-pinned full-Q K3 Jacobi trial Y, exact exterior residual Gram,
the accepted Q floor, exact B*B=72 I in Wflat, and both source-conditional
physical energy windows to enclose EACH of 64 original physical entries.
Every calculation is integer-only, including outward root/division bounds.
This does not certify true flat eigenvectors or the Wilson E1-E2 transition.
"""
import hashlib
import os
import sys
from math import isqrt

HERE=os.path.dirname(os.path.abspath(__file__))
INDEP=os.path.dirname(HERE)
PR180=os.path.join(INDEP,"y137-q-dual-weight-20261113")
sys.path.insert(0,PR180)
_saved_argv=sys.argv[:]
try:
    sys.argv=sys.argv[:1]
    import replay as source
finally:
    sys.argv=_saved_argv

B=1000000000
PS=1000000
Q_FLOOR=94068200
SCALE=source.SCALE
E1_LO,E1_HI=69909429421,69909586556
E2_LO,E2_HI=69949264147,69949433884
WFLAT=(1,3,2,3,3,2,2,2)
K=72
OMAX=21
N=155378
ORIGINAL_CHECK="b6da6140ca36b361bdd9a0c0477af23d681257cf"
ORIGINAL_REPLAY="b9881651c51a278757bc0fef15de583277330da3"
ORIGINAL_BGRAM="48c02e1e80112e5d758b403f41d07079d9fcb064"

def need(ok,why):
    if not ok:
        print("Y137_O8_REFUSE|reason="+why+"|json=0",flush=True)
        raise SystemExit(1)

def emit(tag,**items):
    print(tag+"|"+"|".join(str(k)+"="+str(v) for k,v in items.items())+"|json=0",flush=True)

def blob(path):
    v=open(path,"rb").read()
    return hashlib.sha1(b"blob "+str(len(v)).encode("ascii")+bytes((0,))+v).hexdigest()

def sha(v):
    return hashlib.sha256(str(v).encode("ascii")).hexdigest()

def ceildiv(a,b):
    need(a>=0 and b>0,"integer_ceiling_positive_arguments")
    return (a+b-1)//b

def sqrtceil(a):
    need(a>=0,"negative_square_root")
    v=isqrt(a)
    return v if v*v==a else v+1

def toy():
    p=(3,-1)
    q=(2,4)
    op=(14,-7)
    oq=(-1,2)
    flat=sum(p[i]*p[i]*op[i] for i in range(2))
    exterior=sum(q[i]*q[i]*oq[i] for i in range(2))
    need(flat==119 and exterior==28 and flat+exterior==147,
         "source_specific_two_block_toy")
    need(flat!=flat+exterior,"omitted_QOQ_control")
    # Rational shift of the entire exact physical observable, not just Q.
    normP=sum(v*v for v in p)
    normQ=sum(v*v for v in q)
    centered2=2*(flat+exterior)-7*(normP+normQ)
    need(centered2==84 and normP+normQ==30,
         "toy_exact_original_centered_Wilson_shift")
    need(sqrtceil(15)==4 and sqrtceil(16)==4 and ceildiv(7,3)==3,
         "outward_integer_sqrt_control")
    need(E1_LO<E1_HI<E2_LO<E2_HI,"physical_energy_brackets_order")
    emit("Y137_O8_TOY",diagonal_P_Q_zero="PASS",
         omitted_QOQ="REJECTED",rational_outward="PASS",
         centered_original_observable="EXACT_RATIONAL_SHIFT",
         actual_first_Wilson_weight="HOLD")

def pins():
    need(blob(os.path.join(INDEP,"y137-wilson-effective-20261113","check.py"))==
         ORIGINAL_CHECK,"original_24_link_Wilson_source_changed")
    need(blob(os.path.join(PR180,"replay.py"))==ORIGINAL_REPLAY,
         "original_K3_source_changed")
    receipt=os.path.join(INDEP,"y137-fullstate-Q-normalization-20261113",
                         "RESULT-FULL-W-NORM.hbp")
    need(blob(receipt)==ORIGINAL_BGRAM,"original_B_isometry_receipt_changed")
    fields=[x for x in open(receipt,encoding="ascii").read().splitlines()
            if x.startswith("Y137_FULLN_GRAM|")]
    need(len(fields)==1 and
         "BstarB_exact_72_identity=1" in fields[0] and
         "min_integer_PSD_K=72" in fields[0] and
         "P_Q_edges=264" in fields[0],
         "accepted_B_isometry_drift")
    need(source.k.SCRIPT_SHA==
         "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff",
         "original_full_Q_script_not_frozen")

def build():
    pins()
    ball,O=source.build()
    need(ball["n"]==N and tuple(ball["wf"])==WFLAT and len(O)==N+8,
         "original_physical_orbit_census_or_weights")
    need(min(O)==-7 and max(O)==14 and O[6]==O[7],
         "original_Wilson_character_or_reflection")
    gram=[[0]*8 for _ in range(8)]
    nnz=0
    for i,row in enumerate(ball["C"]):
        if row is None:continue
        w=ball["wq"][i]
        nnz+=sum(c!=0 for c in row)
        for a in range(8):
            if row[a]==0:continue
            for b in range(8):
                gram[a][b]+=w*row[a]*row[b]
    need(nnz==264 and all(gram[a][b]==(K*WFLAT[a] if a==b else 0)
                          for a in range(8) for b in range(8)),
         "original_weighted_BstarB_exact_72")
    emit("Y137_O8_SOURCE",flat=8,Q=N,shell4=ball["nf"],
         Q_floor_num=Q_FLOOR,Q_floor_den=PS,
         original_Wilson="SEVEN_LOOP_DIAGONAL_MULTIPLICATION",
         original_POQ="ZERO",original_QOP="ZERO",
         BstarB="EXACT_72_IDENTITY",P_Q_nonzero_records=nnz)
    return ball,O

def run():
    toy()
    ball,O=build()
    # Exact source integer matrix 2*(original_O - 7/2 I), with
    # physical universal norm <=21. Divide signed matrix and interval
    # numerators by TWO in the output denominator.
    O=[2*v-7 for v in O]
    need(min(O)==-21 and max(O)==21,
         "universal_source_centered_character_range")
    emit("Y137_O8_CENTERED_SOURCE",
         original_7_loop_integer_O="SOURCE_AUTHENTICATED",
         rational_mu="7/2",
         integer_observable="TWO_ORIGINAL_O_MINUS_SEVEN_I",
         centered_Q_operator_norm_upper_num=21,
         centered_Q_operator_norm_upper_den=2,
         true_E1E2_transition_shift_invariant="EXACT_ORTHOGONALITY",
         original_fixed_sample_shift_defect="MUST_BE_RETAINED")
    R1=source.mod.threshold_ball(E1_HI,B,source.ITER,SCALE,ball,
                                 Q_FLOOR,keep_y=True)
    R2=source.mod.threshold_ball(E2_HI,B,source.ITER,SCALE,ball,
                                 Q_FLOOR,keep_y=True)
    Y1,Y2=R1["Y"],R2["Y"]
    need(len(Y1)==len(Y2)==N,"Q_trial_dimension")
    gap1=(B//PS)*Q_FLOOR-E1_HI
    gap2=(B//PS)*Q_FLOOR-E2_HI
    need(gap1>0 and gap2>0,"accepted_Q_floor_below_true_energy")
    width1=E1_HI-E1_LO
    width2=E2_HI-E2_LO
    qnorm1=[0]*8
    qnorm2=[0]*8
    A=[[0]*8 for _ in range(8)]
    for idx in range(N):
        y1,y2=Y1[idx],Y2[idx]
        w=ball["wq"][idx]
        ow=w*O[8+idx]
        for i in range(8):
            ai=y2[i]
            bi=y1[i]
            qnorm1[i]+=w*bi*bi
            qnorm2[i]+=w*ai*ai
            if ai:
                for j in range(8):
                    A[i][j]+=ow*ai*y1[j]
    for i in range(8):
        A[i][i]+=SCALE*SCALE*WFLAT[i]*O[i]

    # Exact K3 source residual Gram equals 6 times original W-norm²
    # of the FULL-Q, shell4-inclusive (B H_QQ-a)Y+B*SCALE*C residual.
    # Thus ||Y_true-Yhat|| <= sqrt(G_ii/6)/(B*(gamma-E)).
    q1=[sqrtceil(v) for v in qnorm1]
    q2=[sqrtceil(v) for v in qnorm2]
    e1=[ceildiv(sqrtceil(ceildiv(R1["G"][i][i],6)),gap1)
        for i in range(8)]
    e2=[ceildiv(sqrtceil(ceildiv(R2["G"][i][i],6)),gap2)
        for i in range(8)]

    max_rad=0
    rows=[]
    for i in range(8):
        for j in range(8):
            # Q-operator approximation error on the full original Q.
            residual_radius=OMAX*(e2[i]*q1[j]+e1[j]*q2[i]+e2[i]*e1[j])
            # Resolvent identity over the complete certified TRUE E windows.
            # In Wflat-orthonormal space, ||B||²=72 and ||O||<=14.
            raw_flat_factor=sqrtceil(WFLAT[i]*WFLAT[j])
            coeff=raw_flat_factor*K*OMAX*B*B*SCALE*SCALE
            band2=ceildiv(coeff*width2,gap2*gap2*gap1)
            band1=ceildiv(coeff*width1,gap2*gap1*gap1)
            energy_radius=band1+band2
            radius=residual_radius+energy_radius
            lo,hi=A[i][j]-radius,A[i][j]+radius
            need(lo<=A[i][j]<=hi,"invalid_signed_Wilson_interval")
            rows.append((i,j,A[i][j],lo,hi,residual_radius,energy_radius))
            max_rad=max(max_rad,radius)
    # Exact reflection symmetry: original physical coordinate 6/7 pair.
    perm=list(range(8))
    perm[6],perm[7]=7,6
    need(all(A[i][j]==A[perm[i]][perm[j]]
             for i in range(8) for j in range(8)),
         "original_Wilson_source_reflection_mismatch")
    emit("Y137_O8_MATRIX",
         original_Q_trial_1_U_sha256=R1["hu"],
         original_Q_trial_2_U_sha256=R2["hu"],
         original_Q_trial_1_G_sha256=R1["hg"],
         original_Q_trial_2_G_sha256=R2["hg"],
         upper_endpoint_E1_num=E1_HI,upper_endpoint_E2_num=E2_HI,
         original_E1_window= str(E1_LO)+":"+str(E1_HI),
         original_E2_window= str(E2_LO)+":"+str(E2_HI),
         source_matrix_SHA256=sha(A),
         interval_matrix_SHA256=sha(rows),
         original_K3_Jacobi_steps=source.ITER,
         full_original_Q_shell4_residuals="INCLUDED",
         BstarB_exact_72="PASS",
         Q_Wilson_two_times_centered_operator_cap_21="PASS",
         original_P_Q_wilson_mixed="ZERO_EXACT",
         source_entries="64_OF_64")
    for i,j,a,lo,hi,er,ee in rows:
        emit("Y137_O8_ENTRY",i=i,j=j,den=2*SCALE*SCALE,
             approx_signed_num=a,lower_signed_num=lo,upper_signed_num=hi,
             Q_residual_radius_num=er,energy_band_radius_num=ee)
    emit("Y137_O8_VERDICT",
         original_true_E1E2_windows="BOTH_COVERED",
         entire_true_original_Oeff_8x8="64_CENTERED_RATIONAL_ENTRY_INTERVALS",
         max_radius_per_trillion=ceildiv(max_rad*1000000000000,2*SCALE*SCALE),
         flat_sector_eigendirections="NOT_CERTIFIED",
         true_normalized_first_Wilson_weight="HOLD",issue_137="OPEN")

if __name__=="__main__":
    if sys.argv[1:]==["toy"]:toy()
    elif sys.argv[1:]==["real"]:run()
    else:need(False,"usage_toy_or_real")
