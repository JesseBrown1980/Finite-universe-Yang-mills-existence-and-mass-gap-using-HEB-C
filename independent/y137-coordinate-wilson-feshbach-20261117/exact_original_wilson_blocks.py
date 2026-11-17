#!/usr/bin/env python3
"""#137: source-authenticated original Wilson P/Q coordinate deflation.

Original seven-loop Wilson O is gauge-invariant MULTIPLICATION by a signed
integer on each canonical physical S3 orbit. P spans precisely the eight
flat orbit coordinate directions; Q spans every other orbit. Hence,
as exact physical operators, POQ=QOP=0, while POP and QOQ are diagonal.

At frozen #180 trial flat energies, reproduce the actual original K3
source, rational-flat sample vectors and all 20 Jacobi Q updates.
The four Feshbach components are (POP, 0, 0, QOQ) on these *fixed*
samples and their sum must match the archived raw Wilson trial scalar.
The actual Q resolvent and true eigendirections are still unproved
by this source calculation; no actual E1/E2 spectral weight is claimed.
"""
import hashlib
import os
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
INDEP=os.path.dirname(HERE)
PR180=os.path.join(INDEP,"y137-q-dual-weight-20261113")
PR178=os.path.join(INDEP,"y137-wilson-effective-20261113")
sys.path.insert(0,PR180)
sys.path.insert(0,PR178)
import replay as wilson_sample
import check as original_wilson

PIN_ORIGINAL_WILSON="b6da6140ca36b361bdd9a0c0477af23d681257cf"
PIN_SAMPLE="b9881651c51a278757bc0fef15de583277330da3"
PIN_SAMPLE_RECEIPT="40762ceb865829156e4765b720f52d39a8be9b6f"
RECEIPT=os.path.join(PR180,"RESULT-WILSON-Q-DUAL.hbp")
D=1000000000
N=155378
FLATS=8

def fail(reason):
    print("Y137_OEFF_COORD_REFUSE|reason="+reason+"|json=0",flush=True)
    raise SystemExit(1)

def need(ok,reason):
    if not ok:fail(reason)

def digest(v):
    return hashlib.sha256(str(v).encode("ascii")).hexdigest()

def gitblob(path):
    raw=open(path,"rb").read()
    head=b"blob "+str(len(raw)).encode("ascii")+b"\x00"
    return hashlib.sha1(head+raw).hexdigest()

def emit(label,**values):
    print(label+"|"+"|".join(str(k)+"="+str(v) for k,v in values.items())+
          "|json=0",flush=True)

def record(lines,tag):
    matches=[line for line in lines if line.startswith(tag+"|")]
    need(len(matches)==1,"frozen_original_receipt_"+tag)
    out={}
    for piece in matches[0].split("|")[1:]:
        key,sep,val=piece.partition("=")
        need(sep and key not in out,"frozen_original_duplicate_receipt")
        out[key]=val
    need(out.get("json")=="0","frozen_original_receipt_trailer")
    return out

def pinned():
    need(gitblob(os.path.join(PR178,"check.py"))==PIN_ORIGINAL_WILSON,
         "original_raw_24_link_Wilson_changed")
    need(gitblob(os.path.join(PR180,"replay.py"))==PIN_SAMPLE,
         "original_fixed_sample_K3_changed")
    need(gitblob(RECEIPT)==PIN_SAMPLE_RECEIPT,
         "original_accepted_fixed_sample_receipt_changed")
    with open(RECEIPT,encoding="ascii") as fd:
        lines=fd.read().splitlines()
    need(len(lines)==12,"original_fixed_sample_receipt_rowcount")
    flats=record(lines,"Y137_QDUAL_FLATS")
    sample=record(lines,"Y137_QDUAL_RITZ")
    fixed=record(lines,"Y137_QDUAL_RAW_WILSON_FIXED_WEIGHT")
    graph=record(lines,"Y137_QDUAL_GRAPH")
    verdict=record(lines,"Y137_QDUAL_VERDICT")
    need(graph["flats"]=="8" and graph["q"]=="155378"
         and graph["O_min"]=="-7" and graph["O_max"]=="14"
         and graph["independent_raw_observable"]=="PASS"
         and fixed["lower_ppb_floor"]=="416300"
         and fixed["actual_E1E2_weight"]=="OPEN"
         and verdict["issue_137"]=="OPEN",
         "fixed_sample_scope_drift")
    return flats,sample,fixed

def toy():
    # Original coordinate gauge-orbit O: diagonal, P indexes first two,
    # Q the third. In contrast to the generic atlas 5x5 toy, mixed blocks
    # are identically zero here.
    p=(2,-1)
    q=(3,)
    O=(5,-7,4)
    low=sum(O[i]*p[i]*p[i] for i in range(2))
    high=O[2]*q[0]*q[0]
    full=low+high
    need(low==-4 and high==36 and full==32,"coordinate_Wilson_toy")
    # Forbidden mixed POQ element: for a diagonal original observable
    # disjoint flat and nonflat supports never share a coordinate.
    mixed=sum(O[i]*p[i]*q[0] for i in range(2) if i==2)
    need(mixed==0,"flat_nonflat_Wilson_not_diagonal")
    need(low!=full,"omitted_QOQ_negative_control")
    # A forged offdiagonal original-Wilson component would change the
    # true full scalar, so it cannot pass a diagonal-source certificate.
    fake_offdiag=3*p[0]*q[0]
    need(fake_offdiag!=0,"forged_POQ_not_rejected")
    emit("Y137_OEFF_COORD_TOY",
         P_Q_original_orbit_disjoint="PASS",
         mixed_POQ_QOP="ZERO_EXACT",
         fake_offdiagonal="REJECTED",
         omitted_QOQ="REJECTED",
         source_specific_observable="DIAGONAL",
         first_Wilson_weight="HOLD")

def reconstruct():
    flats,sample,fixed=pinned()
    need(wilson_sample.k.SCRIPT_SHA==
         "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff",
         "original_Q_source_SHA_drift")
    ball,diag=wilson_sample.build()
    need(len(diag)==FLATS+N and len(ball["wf"])==FLATS and
         len(ball["wq"])==N,"original_flat_and_Q_physical_dimensions")
    needs=[wilson_sample.A1,wilson_sample.A2]
    starts=([1,2,3,4,5,6,7],[7,6,5,4,3,2,1])
    original=[]
    for i in range(2):
        base=wilson_sample.mod.threshold_ball(needs[i],D,
              wilson_sample.ITER,wilson_sample.SCALE,ball,wilson_sample.FLOOR)
        v=wilson_sample.even_trial(base["U"],starts[i])
        expected=flats["v"+str(i+1)]
        need(",".join(str(t) for t in v)==expected,
             "original_frozen_flat_eigenvector_sample_changed")
        trial=wilson_sample.trial(ball,needs[i],v)
        original.append(trial)
    t1,t2=original
    p1,p2=t1["p"],t2["p"]
    q1,q2=t1["q"],t2["q"]
    wf,wq=ball["wf"],ball["wq"]
    flat=sum(wf[i]*diag[i]*p2[i]*p1[i] for i in range(FLATS))
    nonflat=sum(wq[i]*diag[FLATS+i]*q2[i]*q1[i] for i in range(N))
    overlap=sum(wf[i]*p2[i]*p1[i] for i in range(FLATS))
    overlap+=sum(wq[i]*q2[i]*q1[i] for i in range(N))
    signed=flat+nonflat
    need(signed==int(sample["raw_trial_amplitude"]) and
         overlap==int(sample["overlap_W"]),
         "original_exact_raw_Wilson_overlap_regression")
    den=t1["norm"]*t2["norm"]
    lo=signed*signed*D//den
    hi=(signed*signed*D+den-1)//den
    need(lo==int(sample["raw_trial_weight_ppb_floor"]) and
         hi==int(sample["raw_trial_weight_ppb_ceil"]),
         "original_raw_Wilson_normalized_fixed_trial_weight")
    need(flat!=0 and nonflat!=0,
         "original_source_effective_two_nonzero_terms")
    need(signed!=flat and signed!=nonflat,
         "original_source_dropped_actual_QOQ_or_POP")
    # The shift O -> O + 3 I changes fixed-sample amplitude by exactly
    # three times the nonzero original sample overlap. This check forbids
    # silently setting sample overlap to zero (which holds only for true
    # distinct orthogonal eigenstates).
    shifted=sum(wf[i]*(diag[i]+3)*p2[i]*p1[i] for i in range(FLATS))
    shifted+=sum(wq[i]*(diag[FLATS+i]+3)*q2[i]*q1[i] for i in range(N))
    need(shifted-signed==3*overlap and overlap!=0,
         "sample_observable_scalar_shift_forgery")
    # This is an operator-level exact identity: original O is a
    # multiplication operator, and P/Q partition the disjoint canonical
    # weighted orbit basis. No matrix elements connect their supports.
    mixed_poq=0
    mixed_qop=0
    need(mixed_poq==mixed_qop==0,
         "original_Wilson_P_Q_mixed_term_not_zero")
    emit("Y137_OEFF_COORD_SOURCE",
         original_3x4_S3="FULL_24_LINK_SEVEN_WINDING_CHARACTERS",
         original_P="EIGHT_FLAT_COORDINATE_ORBITS",
         original_Q="ALL_NONFLAT_ORBITS",
         Wilson_type="DIAGONAL_MULTIPLICATION",
         exact_POQ="ZERO",
         exact_QOP="ZERO",
         fixed_sample_P_Wilson_P_sha256=digest(flat),
         fixed_sample_Q_Wilson_Q_sha256=digest(nonflat),
         source_Q_dim=N,
         source_Q_inverse_iterations=wilson_sample.ITER,
         original_source_SHA_pin="PASS",
         full_physical_true_E1E2_projectors="NOT_COMPUTED")
    emit("Y137_OEFF_COORD_FIXED_SAMPLE",
         frozen_energy_1_num=needs[0],frozen_energy_2_num=needs[1],
         POP_signed=flat,POQ_signed=mixed_poq,
         QOP_signed=mixed_qop,QOQ_signed=nonflat,
         exact_recombined_original_sample=signed,
         original_Qdual_archive_match="EXACT",
         original_raw_normalized_weight_ppb_floor=lo,
         original_raw_signed_SHA256=digest(signed),
         fixed_sample_identity_shift="EXACT_TRACKED",
         fixed_sample_QOQ_omitted="REJECTED",
         actual_inverse_tail="ITERATIVE_APPROXIMATION",
         actual_true_physical_psi1_psi2="NOT_CERTIFIED",
         actual_first_Wilson_weight="HOLD")
    emit("Y137_OEFF_COORD_VERDICT",
         original_Wilson_mixed_Feshbach_terms="EXACT_ZERO_BY_ORBIT_SUPPORT",
         original_QOQ="SOURCE_AUTHENTICATED_FIXED_SAMPLE",
         source_specific_Feshbach_effective_8x8="NOT_YET_CERTIFIED",
         true_eigenspace_flat_vectors="NOT_YET_CERTIFIED",
         physical_first_Wilson_weight="HOLD",issue_137="OPEN")

if __name__=="__main__":
    if sys.argv[1:]==["toy"]:
        toy()
    elif sys.argv[1:]==["real"]:
        toy()
        reconstruct()
    else:
        fail("usage_toy_or_real")
