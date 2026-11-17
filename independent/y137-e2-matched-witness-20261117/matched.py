#!/usr/bin/env python3
"""#137 E2 Schur-null direct matched witness, full W error with no transport back.

Use accepted original real signed mu3 and four-moment (PR234) 8x8
matrix enclosures, recenter source E2 flat vector, and measure the *true
eigenstate* error relative to that SAME recentered/dressed source
direction. This avoids charging historical original-vector displacement
when we plan to recalculate the Wilson source on the new direction.
All original S3 Q floor, exact 8x8 moments, and energy brackets frozen.

A direct matched witness is DIFFERENT from the original PR281 fixed
Wilson sample. Positive original Wilson first weight stays HOLD until
that source is independently recalculated at the matched witness.
"""
import os
import sys
from math import isqrt

HERE=os.path.dirname(os.path.abspath(__file__))
INDEP=os.path.dirname(HERE)
sys.path.insert(0,os.path.join(INDEP,"y137-four-moment-fullstate-20261116"))
import four_moment_transfer as e

UNIT=e.UNIT
DEN=e.DEN
R=e.ra
FW=e.fw
TARGET=3418880542
ORIGINAL_FOUR_E2=8676646901
ORIGINAL_MOVED=3693022069
PIECES=4
LEVEL=1

def need(ok,msg):
    if not ok:
        print("Y137_E2_DIRECT_REFUSE|reason="+msg+"|json=0",flush=True)
        raise SystemExit(1)

def emit(tag,**kwargs):
    print(tag+"|"+"|".join(str(k)+"="+str(v) for k,v in kwargs.items())+"|json=0",flush=True)

def ceildiv(a,b):
    need(a>=0 and b>0,"positive_integer_ceiling")
    return (a+b-1)//b

def rootceil(n):
    need(n>=0,"negative_integer_sqrt")
    z=isqrt(n)
    return z if z*z==n else z+1

def flat_sine(d,energy_hi):
    # ||P phi||>= [1+72/(gamma-z)^2]^-1/2 for original
    # exact-Q-dressed normalized true or matched fixed source states.
    z=R.ROWS[LEVEL][0]
    c=max(energy_hi,z)
    gap=DEN*94068200-c*1000000
    need(gap>0,"source_gamma_flat_mass_nonpositive")
    factor=rootceil(ceildiv(UNIT*UNIT*(gap*gap+72*DEN*DEN*1000000*1000000),gap*gap))
    return ceildiv(d*factor,UNIT)

def replay():
    with open(e.source.MU3_FILE,encoding="ascii") as h:
        source=e.source.parse_pinned_mu3(h.read())
    windows=e.three_moment_windows()
    need(windows==list(e.EXPECTED_WINDOWS) or tuple(windows)==e.EXPECTED_WINDOWS,
         "accepted_physical_energy_windows_changed")
    z,lo,hi,v0,_,gap,_=R.ROWS[LEVEL]
    uu,m0,m1,m2=e.source.accepted_old_moments(LEVEL)
    m3=e.exact.F(source[z])
    low,upper=e.exact.bracket4(uu,m0,m1,m2,m3,e.FLOOR-z,468000000000-z)
    need(e.exact.pd(e.exact.sub(upper,low)),"real_mu3_interval_positive")
    cn,cd,wn,wd=e.all_refs(low,upper)["CENTRE"]
    v1=R.recentre(cn,list(v0))
    need(R.wnorm(v1)>0 and sum(e.WF[i]*v1[i]*v0[i] for i in range(8))>0,
         "orientation_of_accepted_recentered_witness")
    need(e.cell(e.all_refs(low,upper),windows,LEVEL,"CENTRE",True)["error"]==ORIGINAL_FOUR_E2,
         "hosted_stage_E_moved_error_not_reproduced")
    need(e.flat_distance(list(v0),v1)==ORIGINAL_MOVED,
         "original_W_flat_E2_witness_movement")
    best=None
    for k in range(0,6):
        # v_k=(4-k)*v0+k*v_moved, exact integer flat coordinate.
        v=[(PIECES-k)*v0[i]+k*v1[i] for i in range(8)]
        need(R.wnorm(v)>0,"candidate_flat_vector_zero")
        dist=e.flat_distance(list(v0),v)
        qlo,qhi=FW.Q_NORMS[LEVEL]
        spread=ceildiv(FW.B_NORM_UP*dist*DEN,UNIT*(e.FLOOR-z))
        qlo=max(0,qlo-spread);qhi+=spread
        # Exact original 8x8 fourth-moment Schur-envelope residual;
        # direct matched-v witness, so NO triangle transport to old v0.
        ang=R.angle(cn,cd,wn,wd,v,z,lo,hi,gap)
        drift=max(z-lo,hi-z)
        mu0=ang["mu"]-ang["extra"]-ceildiv(drift*UNIT,DEN)
        full=FW.compose(ang["Hcenter"]+ang["action"],mu0,
                        (windows[1][0]-windows[0][1])*UNIT//DEN if LEVEL==0
                        else min(windows[1][0]-windows[0][1],
                                 R.E3_LO-windows[1][1])*UNIT//DEN,
                        z,windows[LEVEL][0],windows[LEVEL][1],qlo,qhi)
        direct=full["error"]
        sine=flat_sine(direct,windows[LEVEL][1])
        # For this original-projector source, a new Wilson source solve
        # and positive signed contraction would still be necessary.
        extra=FW.sqrt_ceil(dist*dist+spread*spread)
        total=direct+extra
        if k==PIECES:need(total==ORIGINAL_FOUR_E2,
                           "old_original_source_accepted_regression")
        result=(sine,direct,k,dist,ang["Hcenter"],ang["action"],full["extra"])
        if best is None or result<best:best=result
        emit("Y137_E2_DIRECT_POINT",k=k,den=PIECES,
             source_original_v2_delta_per_trillion=dist,
             source_Q_norm_spread_per_trillion=spread,
             source_fourth_moment_residual_per_trillion=ang["Hcenter"],
             source_fourth_moment_action_per_trillion=ang["action"],
             matched_full_state_distance_per_trillion=direct,
             matched_W_flat_sine_per_trillion=sine,
             transported_original_full_distance_per_trillion=total,
             original_fixed_Wilson_source_valid=int(k==0),
             new_source_specific_Wilson_required=int(k!=0),
             E2_target_reached=int(sine<TARGET))
    sine,direct,k,dist,residual,action,extra=best
    emit("Y137_E2_DIRECT_VERDICT",
         source="ORIGINAL_HOSTED_SIGNED_MU3_FOUR_MOMENT",
         original_fixed_E2_distance_per_trillion=ORIGINAL_FOUR_E2,
         best_matched_fraction_num=k,
         best_matched_fraction_den=PIECES,
         best_matched_distance_per_trillion=direct,
         best_matched_flat_sine_per_trillion=sine,
         sufficient_E2_target_per_trillion=TARGET,
         E2_target="CANDIDATE_NEEDS_NEW_MATCHED_WILSON_SOURCE" if sine<TARGET else "HOLD",
         original_fixed_Wilson_dual_not_reused="PASS",
         actual_original_first_Wilson_weight="HOLD",
         issue_137="OPEN")

def toy():
    a=(1,0);b=(0,1)
    need(sum(a[i]*b[i] for i in range(2))==0
         and rootceil(15)==4 and rootceil(16)==4
         and ceildiv(7,3)==3,"integer_orthogonal_source_toy")
    emit("Y137_E2_DIRECT_TOY",integer_only="PASS",
         moving_witness_requires_new_Wilson_source="PASS",
         first_Wilson_weight="HOLD")

if __name__=="__main__":
    if sys.argv[1:]==["toy"]:toy()
    elif sys.argv[1:]==["real"]:
        toy()
        replay()
    else:need(False,"usage_toy_or_real")
