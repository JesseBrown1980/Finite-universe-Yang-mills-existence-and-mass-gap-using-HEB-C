#!/usr/bin/env python3
"""Issue 137: true flat-projector x original Wilson source contraction.

Independent second lane of parallel research: consume frozen *original*
64-entry signed 8x8 Wilson effective-matrix rational intervals from hosted
#273, the accepted #184 exact eight-flat null eigendirection angle bounds
for the #180 original two flat directions, the certified physical Stage E
energy windows (subsets of the older #184 brackets), the exact original
B*B=72I and ||O||<=14. No new large Q source enumeration needed.

We compute a strict phase-aligned lower bound on the true unnormalized
flat component transition |<x2,M(E2,E1)x1>|. All terms use exact
integers, outward-rounded square roots, and deflation by the individual
flat sample directions before bounding high-angle contamination.

For original flat unit samples v1,v2 and true flat unit eigenvectors
x_i=c_i*v_i+h_i, ||h_i||<=s_i, h_i perpendicular to v_i:

|<x2,M x1>| >= c1*c2 |<v2,M v1>|
   -s1 ||(I-Pv1)M* v2|| -s2 ||(I-Pv2)M v1||
   -s1*s2 ||M|| .

The two deflated action norms are from source matrix Mhat, inflated by
a rigorous full 8x8 interval-error Frobenius norm. The formula applies
to the true full-Q M only because the Q/source intervals cover both
physical energy windows. A positive final strict integer margin would
be a candidate, pending independent mathematical acceptance and actual
full physical W normalization; otherwise truthful HOLD.

The projected physical first Wilson weight never auto-promotes.
"""
import hashlib
import os
from math import isqrt

HERE=os.path.dirname(os.path.abspath(__file__))
INDEP=os.path.dirname(HERE)
MATRIX=os.path.join(HERE,"INPUT-ORIGINAL-O8-64.hbp")
CENTERED=os.path.join(INDEP,"y137-centered-schur-transfer-20261113",
                      "RESULT-CENTERED-PROJECTOR.hbp")
SAMPLE=os.path.join(INDEP,"y137-q-dual-weight-20261113",
                    "RESULT-WILSON-Q-DUAL.hbp")
BGRAM=os.path.join(INDEP,"y137-fullstate-Q-normalization-20261113",
                   "RESULT-FULL-W-NORM.hbp")
U=1000000000000
T=1000000000000
B=1000000000
WF=(1,3,2,3,3,2,2,2)
V1=(1000000000,997935625,996905915,38054797,37920545,2788116,51160,51160)
V2=(111045317,-38181375,-112233220,1000000000,979217930,216249666,4169404,4169404)
PIN_CENTERED="3a147c8a750dae490882702307f8ec795a3c1f51"
PIN_SAMPLE="40762ceb865829156e4765b720f52d39a8be9b6f"
PIN_BGRAM="48c02e1e80112e5d758b403f41d07079d9fcb064"
E1_LO,E1_HI=69909429421,69909586556
E2_LO,E2_HI=69949264147,69949433884
FLOOR=94068200000
ORIGINAL_HASH="91bfe5e9758ab5a8ca90ad4d5a1e828a016996f8d58661370e8949b02f533426"
INTERVAL_HASH="39c2dedf8c108939beadbb0098ec1e0f501106de43e36c44daf11e0e0a316622"

def need(ok,label):
    if not ok:
        print("Y137_FLAT_CONTRACTION_REFUSE|reason="+label+"|json=0",flush=True)
        raise SystemExit(1)

def emit(tag,**kwargs):
    print(tag+"|"+"|".join(str(k)+"="+str(v) for k,v in kwargs.items())+
          "|json=0",flush=True)

def blob(path):
    b=open(path,"rb").read()
    return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+bytes((0,))+b).hexdigest()

def ceildiv(a,b):
    need(a>=0 and b>0,"ceildiv_positive_domain")
    return (a+b-1)//b

def sqrtceil(n):
    need(n>=0,"sqrt_of_negative")
    v=isqrt(n)
    return v if v*v==n else v+1

def sqrt_upper_scaled(num,den):
    need(num>=0 and den>0,"sqrt_ratio_domain")
    return sqrtceil(ceildiv(num*U*U,den))

def wnorm(v):
    return sum(WF[i]*v[i]*v[i] for i in range(8))

def parse(line):
    cells=line.split("|")
    res={}
    for s in cells[1:]:
        key,sep,val=s.partition("=")
        need(sep and key not in res,"malformed_or_repeated_receipt_field")
        res[key]=val
    need(res.get("json")=="0","missing_receipt_end")
    return res

def find(rows,tag):
    a=[parse(v) for v in rows if v.startswith(tag+"|")]
    need(len(a)>0,"missing_"+tag)
    return a

def freeze():
    need(blob(CENTERED)==PIN_CENTERED and blob(SAMPLE)==PIN_SAMPLE
         and blob(BGRAM)==PIN_BGRAM,"accepted_source_blob_drift")
    c=open(CENTERED,encoding="ascii").read().splitlines()
    s=open(SAMPLE,encoding="ascii").read().splitlines()
    b=open(BGRAM,encoding="ascii").read().splitlines()
    vrec=find(s,"Y137_QDUAL_FLATS")[0]
    need(tuple(int(x) for x in vrec["v1"].split(","))==V1
         and tuple(int(x) for x in vrec["v2"].split(","))==V2
         and vrec["sector"]=="even",
         "original_W_flat_samples_not_matched")
    grec=find(b,"Y137_FULLN_GRAM")[0]
    need(grec["BstarB_exact_72_identity"]=="1"
         and grec["wf"]==",".join(str(w) for w in WF)
         and grec["min_integer_PSD_K"]=="72",
         "exact_B_isometry_not_accepted")
    sr=find(c,"Y137_CENTER_POINT")
    need(len(sr)==2,"two_certified_original_flat_angles")
    s1=int(sr[0]["selected_sin_upper_per_trillion"])
    s2=int(sr[1]["selected_sin_upper_per_trillion"])
    need(sr[0]["sample_num"]=="69909875505"
         and sr[1]["sample_num"]=="69949729820",
         "wrong_accepted_original_null_branch")
    # Check the original null angle certificates are for windows strictly
    # wider than the later accepted Stage E actual energy windows.
    need(int(sr[0]["E_lo_num"])<E1_LO
         and int(sr[0]["E_hi_num"])>E1_HI
         and int(sr[1]["E_lo_num"])<E2_LO
         and int(sr[1]["E_hi_num"])>E2_HI,
         "physical_energy_interval_not_within_projector_source")
    need(0<s1<U and 0<s2<U,"flat_null_sin_bound_nontrivial")
    cv=find(c,"Y137_CENTER_VERDICT")[0]
    need(cv["null_branch_identified"]=="2"
         and cv["nonvacuous"]=="2",
         "original_schur_null_branch_not_certified")

    rows=open(MATRIX,encoding="ascii").read().splitlines()
    need(len(rows)==67,"hosted_original_O8_receipt_rowcount")
    source=parse(rows[0])
    need(rows[0].startswith("Y137_FLAT_CONTRACTION_SOURCE|")
         and source["original_64_source_sha256"]==ORIGINAL_HASH
         and source["original_64_interval_sha256"]==INTERVAL_HASH
         and source["hosted_run"]=="44106643165"
         and source["hosted_job"]=="134120671522",
         "original_hosted_Wilson_receipt_source_pin")
    meta=find(rows,"Y137_O8_MATRIX")[0]
    need(meta["source_matrix_SHA256"]==ORIGINAL_HASH
         and meta["interval_matrix_SHA256"]==INTERVAL_HASH
         and meta["source_entries"]=="64_OF_64"
         and meta["full_original_Q_shell4_residuals"]=="INCLUDED"
         and meta["BstarB_exact_72"]=="PASS"
         and meta["original_P_Q_wilson_mixed"]=="ZERO_EXACT"
         and meta["original_E1_window"]==str(E1_LO)+":"+str(E1_HI)
         and meta["original_E2_window"]==str(E2_LO)+":"+str(E2_HI),
         "actual_original_Wilson_matrix_scope_mismatch")
    vals=find(rows,"Y137_O8_ENTRY")
    need(len(vals)==64,"missing_exact_8x8_matrix_entries")
    A=[[0]*8 for _ in range(8)]
    R=[[0]*8 for _ in range(8)]
    used=set()
    for f in vals:
        i,j=int(f["i"]),int(f["j"])
        need(i in range(8) and j in range(8) and (i,j) not in used
             and int(f["den"])==T*T,"wrong_matrix_entry")
        used.add((i,j))
        v=int(f["approx_signed_num"])
        lo=int(f["lower_signed_num"])
        hi=int(f["upper_signed_num"])
        rad=int(f["Q_residual_radius_num"])+int(f["energy_band_radius_num"])
        need(rad>=0 and lo==v-rad and hi==v+rad,
             "original_8x8_matrix_interval_forgery")
        A[i][j]=v
        R[i][j]=rad
    verdict=find(rows,"Y137_O8_VERDICT")[0]
    need(verdict["entire_true_original_Oeff_8x8"]=="64_RATIONAL_ENTRY_INTERVALS"
         and verdict["true_normalized_first_Wilson_weight"]=="HOLD",
         "hosted_eight_flat_interval_scope")
    return A,R,s1,s2

def exact_margin(A,R,s1,s2):
    n1,n2=wnorm(V1),wnorm(V2)
    need(n1>0 and n2>0,"bad_weighted_norm")
    normroot=sqrtceil(n1*n2)
    rows1=[sum(A[i][j]*V1[j] for j in range(8)) for i in range(8)]
    cols2=[sum(A[i][j]*V2[i] for i in range(8)) for j in range(8)]
    amplitude=sum(V2[i]*rows1[i] for i in range(8))
    need(amplitude==sum(V1[j]*cols2[j] for j in range(8)),
         "matrix_bilinear_duality")
    sample_err=sum(abs(V2[i]*V1[j])*R[i][j]
                   for i in range(8) for j in range(8))
    sample_lower=max(0,abs(amplitude)-sample_err)
    lower_sample_amp=sample_lower*U//(T*T*normroot)
    # The original O_eff source matrix is in the raw W-flat bilinear
    # coordinates, not a Euclidean 8x8 action. The W^-1 factors below
    # are obligatory; all eight original weights are 1, 2, or 3.
    # Exact deflation norm squared in original W P-coordinates.
    # A's entries represent W_P Oeff in raw integer/T^2 form.
    denom=6*n1*n2*T*T*T*T
    z1_num=n2*sum((6//WF[i])*rows1[i]*rows1[i] for i in range(8))
    z1_num-=6*amplitude*amplitude
    z2_num=n1*sum((6//WF[j])*cols2[j]*cols2[j] for j in range(8))
    z2_num-=6*amplitude*amplitude
    need(z1_num>=0 and z2_num>=0,
         "source_deflated_operator_PSD_identity")
    z1=sqrt_upper_scaled(z1_num,denom)
    z2=sqrt_upper_scaled(z2_num,denom)
    # Frobenius norm upper bound for all 64 independent signed
    # Mtrue-Mhat interval errors, including OQOQ resolvent and energy drift.
    raw=sum((36//(WF[i]*WF[j]))*R[i][j]*R[i][j]
              for i in range(8) for j in range(8))
    matrix_err=sqrt_upper_scaled(raw,36*T*T*T*T)
    gamma1=FLOOR-E1_HI
    gamma2=FLOOR-E2_HI
    need(gamma1>0 and gamma2>0,"accepted_Q_floor_energy_gap")
    # ||Oeff||_W <= 14*(1+||B||²/(gamma1*gamma2)).
    op=14*U+ceildiv(14*72*B*B*U,gamma1*gamma2)
    c1=isqrt(U*U-s1*s1)
    c2=isqrt(U*U-s2*s2)
    signal=(lower_sample_amp*c1*c2)//(U*U)
    contamination=ceildiv(s1*(z2+matrix_err),U)
    contamination+=ceildiv(s2*(z1+matrix_err),U)
    contamination+=ceildiv(s1*s2*op,U*U)
    margin=signal-contamination
    emit("Y137_FLAT_WILSON_INPUT",
         original_projector="PR184_W_FLAT_NULL_BRANCH_ACCEPTED",
         original_flat_samples="PR180_EVEN_TWO_VECTORS",
         original_Wilson_matrix="PR273_HOSTED_64_SIGNED_ENTRIES",
         physical_E1E2_windows="STAGE_E_SUBSETS_OF_PR184",
         source_BstarB="EXACT_72",
         original_Wilson_O_norm="14",
         native_w_first_norm2_sha256=hashlib.sha256(str(n1).encode("ascii")).hexdigest(),
         native_w_second_norm2_sha256=hashlib.sha256(str(n2).encode("ascii")).hexdigest(),
         flat_sine_upper1_per_trillion=s1,
         flat_sine_upper2_per_trillion=s2)
    emit("Y137_FLAT_WILSON_BENCHMARK",
         matrix_entry_exact=64,
         original_source_sample_amplitude_sign=(amplitude>0)-(amplitude<0),
         unnormalized_signed_sample_sha256=hashlib.sha256(str(amplitude).encode("ascii")).hexdigest(),
         raw_sample_err_sha256=hashlib.sha256(str(sample_err).encode("ascii")).hexdigest(),
         sample_absolute_lower_per_trillion=lower_sample_amp,
         full_8x8_interval_operator_error_per_trillion=matrix_err,
         deflated_forward_M_v1_per_trillion=z1,
         deflated_adjoint_Mstar_v2_per_trillion=z2,
         true_effective_Wilson_operator_bound_per_trillion=op,
         phase_cosine1_lower_per_trillion=c1,
         phase_cosine2_lower_per_trillion=c2)
    emit("Y137_FLAT_WILSON_GATE",
         signal_lower_per_trillion=signal,
         contamination_upper_per_trillion=contamination,
         signed_margin_per_trillion=margin,
         original_source_phase_aligned_two_flat_state_transition=
             "CANDIDATE_PENDING_INDEPENDENT_REVIEW" if margin>0 else "HOLD",
         complete_full_state_normalization="NOT_RECOMPUTED",
         physical_first_Wilson_weight="HOLD",
         issue_137="OPEN")
    return margin

def toy():
    # Single exact diagonal W-operator example: deflated actions vanish
    # when both trial vectors are exact orthogonal coordinate eigenvectors.
    A=[[5,0],[0,-7]]
    u1=(1,0)
    u2=(0,1)
    a=sum(u2[i]*A[i][j]*u1[j] for i in range(2) for j in range(2))
    z1=sum(A[i][j]*u1[j] for i in range(2) for j in range(2))
    need(a==0 and z1==5,"diagonal_Wilson_dark_toy")
    need(sqrtceil(15)==4 and isqrt(16)==4 and
         ceildiv(7,3)==3,"outward_root_toy")
    emit("Y137_FLAT_WILSON_TOY",operator="WEIGHTED_DIAGONAL",
         dark_transition="REJECTED_AS_POSITIVE",
         outward_sqrt="PASS",real_first_Wilson_weight="HOLD")

if __name__=="__main__":
    import sys
    if sys.argv[1:]==["toy"]:
        toy()
    elif sys.argv[1:]==["real"]:
        toy()
        A,R,s1,s2=freeze()
        exact_margin(A,R,s1,s2)
    else:
        need(False,"usage_toy_or_real")
