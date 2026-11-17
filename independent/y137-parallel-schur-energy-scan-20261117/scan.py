#!/usr/bin/env python3
"""Issue #137 — two simultaneous source-authenticated full Schur energy trials.

Track E2: seven fixed fractional thresholds in the accepted full physical
E2 interval. Track BOTH: 3 each in the accepted E1/E2 intervals.
Every threshold evaluates ORIGINAL 8-flat source P and full Q via actual
S3 155378 K3, complete exterior shell4 1985218, full Gram positivity,
and nonflat gamma>=94.0682. Exact 8x8 Schur lower/upper inertia counts
either tighten the physical true-energy interval or remain inconclusive.

Then recompute the already accepted Stage E four-moment true *full-state*
distance for the tighter physical energy windows without modifying the
historical source or its original fixed flat Wilson sample directions.
Convert to exact Wflat sine with B†B=72I for the joined #278 sufficient gate.

No numerical gain, missing inertia bracket, or nonpositive signed
Wilson-transfer margin is explicitly HOLD. All arithmetic integer-only.
"""
import hashlib
import os
import sys
from math import isqrt
HERE=os.path.dirname(os.path.abspath(__file__))
INDEP=os.path.dirname(HERE)
for p in ("y137-q-dual-weight-20261113","y137-four-moment-fullstate-20261116",
          "y137-radau-recentred-angle-20261114"):
    sys.path.insert(0,os.path.join(INDEP,p))
oldargs=sys.argv[:]
try:
    sys.argv=sys.argv[:1]
    import replay as orig
finally:
    sys.argv=oldargs
import four_moment_transfer as e
D=1000000000
S=e.UNIT
QFLOOR=94068200
PS=1000000
WF=(1,3,2,3,3,2,2,2)
BASE=((69909429421,69909586556),(69949264147,69949433884))
BASE_ERROR=(3235251105,8676646901)
JOIN_E2_TARGET=1608523803
JOINT_SCALE_TARGET=309746069093
ORIGINAL_BLOB="b9881651c51a278757bc0fef15de583277330da3"
ORIGINAL_WILSON_BLOB="b6da6140ca36b361bdd9a0c0477af23d681257cf"

def need(ok,why):
    if not ok:
        print("Y137_SCHUR_SCAN_REFUSE|reason="+why+"|json=0",flush=True)
        raise SystemExit(1)

def emit(tag,**fields):
    print(tag+"|"+"|".join(str(k)+"="+str(v) for k,v in fields.items())+"|json=0",flush=True)

def gitblob(path):
    raw=open(path,"rb").read()
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+bytes((0,))+raw).hexdigest()

def ceildiv(a,b):
    need(a>=0 and b>0,"nonpositive_ceiling")
    return (a+b-1)//b

def sqrtceil(n):
    need(n>=0,"negative_square_root")
    k=isqrt(n)
    return k if k*k==n else k+1

def choose_cutoffs(track,level):
    lo,hi=BASE[level]
    span=hi-lo
    pieces=8 if track=="E2_ONLY" else 4
    return tuple(lo+span*j//pieces for j in range(1,pieces))

def tighten(lo,hi,a,lower_count,upper_count,level):
    # The exact nonflat floor ensures inertia of the 8x8 physical
    # Feshbach Schur equals whole-physical count for a<gamma.
    # The true count N(a) satisfies N_upper<=N<=N_lower.
    k=level+1
    need(0<=upper_count<=lower_count<=8,
         "invalid_original_inertia_order")
    if lower_count==upper_count==k-1:
        return max(lo,a),hi,"LOWER"
    if lower_count==upper_count==k:
        return lo,min(hi,a),"UPPER"
    return lo,hi,"INCONCLUSIVE"

def toy():
    lo,hi=10,30
    lo,hi,part=tighten(lo,hi,20,1,1,1)
    need((lo,hi,part)==(20,30,"LOWER"),"source_inertia_toy_lower")
    lo,hi,part=tighten(lo,hi,25,2,2,1)
    need((lo,hi,part)==(20,25,"UPPER"),"source_inertia_toy_upper")
    lo,hi,part=tighten(lo,hi,22,2,1,1)
    need((lo,hi,part)==(20,25,"INCONCLUSIVE"),"source_inertia_toy_hold")
    emit("Y137_SCHUR_SCAN_TOY",exact_8flat_count_logic="PASS",
         inconclusive_source="HOLD",outward_integer="PASS",
         actual_first_Wilson_weight="HOLD")

def source_auth():
    need(gitblob(os.path.join(INDEP,"y137-q-dual-weight-20261113","replay.py"))==
         ORIGINAL_BLOB,"source_original_K3_changed")
    need(gitblob(os.path.join(INDEP,"y137-wilson-effective-20261113","check.py"))==
         ORIGINAL_WILSON_BLOB,"source_original_Wilson_changed")
    need(orig.k.SCRIPT_SHA==
         "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff",
         "source_original_gauge_S3_changed")
    need(e.three_moment_windows()==BASE,
         "source_conditional_original_stage_E_windows_drift")
    need(e.ra.ROWS[1][3]==
         (111045317,-38181375,-112233220,1000000000,979217930,216249666,4169404,4169404),
         "original_second_flat_W_vector_changed")

def refined_four_moment(windows):
    with open(e.source.MU3_FILE,encoding="ascii") as f:
        auth=e.source.parse_pinned_mu3(f.read())
    refs=[]
    for i,z in enumerate(e.source.FROZEN):
        u,m0,m1,m2=e.source.accepted_old_moments(i)
        m3=e.exact.F(auth[z])
        lo,hi=e.exact.bracket4(u,m0,m1,m2,m3,e.FLOOR-z,468000000000-z)
        refs.append(e.all_refs(lo,hi))
    result=[e.cell(refs[i],windows,i,"CENTRE",True) for i in range(2)]
    errors=[x["error"] for x in result]
    need(errors[0]>0 and errors[1]>0 and
         errors[0]<S and errors[1]<S,
         "four_moment_numerical_transfer_not_certified")
    # Convert to conservative normalized W-flat sine error bound.
    # The projection's W-flat mass >=(1+72/gap²)^(-1/2).
    flat=[]
    for i in range(2):
        sample=e.source.FROZEN[i]
        energy=max(sample,windows[i][1])
        gap=D*QFLOOR-energy*PS
        need(gap>0,"whole_nonflat_floor_invalid")
        factor=sqrtceil(ceildiv(S*S*(gap*gap+72*D*D*PS*PS),gap*gap))
        flat.append(ceildiv(errors[i]*factor,S))
    return errors,flat

def main(track):
    need(track in ("E2_ONLY","BOTH"),"unknown_parallel_track")
    toy()
    source_auth()
    ball,obs=orig.build()
    need(ball["n"]==155378 and ball["nf"]==1985218 and
         tuple(ball["wf"])==WF and min(obs)==-7 and max(obs)==14,
         "original_24_link_S3_full_K3_and_shell4_source")
    scan_levels=(1,) if track=="E2_ONLY" else (0,1)
    bracket=[list(w) for w in BASE]
    counts=[0,0]
    changed=[0,0]
    emit("Y137_SCHUR_SCAN_SOURCE",
         track=track,source_full_physical="ORIGINAL_3x4_S3_FESHBACH",
         Q_coordinates=ball["n"],shell4=ball["nf"],
         exact_P_dimension=8,original_Wilson="SEVEN_LOOP_SOURCE_PIN",
         original_E1_window=str(BASE[0]),original_E2_window=str(BASE[1]))
    for level in scan_levels:
        for a in choose_cutoffs(track,level):
            # Exactly 20 Jacobi inverse steps, original fixed S3
            # 8-column source with independent full exterior residual.
            x=orig.mod.threshold_ball(a,D,orig.ITER,orig.SCALE,
                                     ball,QFLOOR)
            nlo,nhi=x["nlo"],x["nhi"]
            lo,hi,dec=tighten(bracket[level][0],bracket[level][1],
                              a,nlo,nhi,level)
            bracket[level]=[lo,hi]
            counts[level]+=1
            if dec!="INCONCLUSIVE":changed[level]+=1
            need(BASE[level][0]<=lo<hi<=BASE[level][1],
                 "inertia_window_not_nesting")
            emit("Y137_SCHUR_SCAN_POINT",
                 track=track,level=level+1,threshold_num=a,
                 full_physical_count_min=nhi,full_physical_count_max=nlo,
                 validated_side=dec,new_lower_num=lo,new_upper_num=hi,
                 original_U_sha256=x["hu"],original_G_sha256=x["hg"],
                 original_L_sha256=x["hl"],
                 all_Q_exterior="INCLUDED")
    windows=tuple(tuple(pair) for pair in bracket)
    errors,angles=refined_four_moment(windows)
    emit("Y137_SCHUR_SCAN_TRANSFER",
         track=track,original_E1_window=str(BASE[0]),
         original_E2_window=str(BASE[1]),
         tightened_E1_window=str(windows[0]),
         tightened_E2_window=str(windows[1]),
         E1_count_points=counts[0],E2_count_points=counts[1],
         E1_accepted_splits=changed[0],E2_accepted_splits=changed[1],
         Stage_E_four_moment_E1_error_per_trillion=errors[0],
         Stage_E_four_moment_E2_error_per_trillion=errors[1],
         E1_flat_sine_per_trillion=angles[0],
         E2_flat_sine_per_trillion=angles[1],
         strict_E2_only_sufficient=int(angles[0]<=3429010525
                                      and angles[1]<JOIN_E2_TARGET),
         strict_joint_scale_sufficient=int(angles[0]*S<3429010525*JOINT_SCALE_TARGET
                                         and angles[1]*S<9197961975*JOINT_SCALE_TARGET))
    emit("Y137_SCHUR_SCAN_VERDICT",
         track=track,source_original_8x8_inertia="VALIDATED_EXACT",
         physical_E2_angular_target="PASS_CONDITIONAL" if
             angles[1]<JOIN_E2_TARGET else "HOLD",
         original_Wilson_first_excitation_weight="HOLD",
         source_3x4_physical_gap="ALREADY_CONDITIONALLY_ACCEPTED",
         issue_137="OPEN")

if __name__=="__main__":
    if sys.argv[1:]==["toy"]:toy()
    elif len(sys.argv)==2:main(sys.argv[1])
    else:need(False,"usage_toy_E2_ONLY_or_BOTH")
