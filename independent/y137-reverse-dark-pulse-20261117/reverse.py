#!/usr/bin/env python3
"""#137 outside-in reverse test of the 'dark original Wilson' endpoint.

This is a SOURCE-AUTHENTICATED EXPLORATORY diagnostic, not a theorem.
Take the actual original S3 centered O2=2O-7I 8flat matrix trial from
PR282 and real signed mu3 four-moment E2 Schur center from PR234.
Construct the exact nearest direction to historic v2 with *zero*
Wilson amplitude against the historic E1 witness v1 under that FIXED
centered source matrix. Walk that dark endpoint inward to v2.
Independently move the dark vector towards the SOURCE RECENTERED E2
Schur-null witness as a center "pulse". Measure normalized Wilson
amplitude, original-source E2 angle displacement and exact Schur
residual at every point with only integer arithmetic.

The true Wilson matrix and physical E1 state differ from these source
trial inputs within certified uncertainties. Hence excluding the
SOURCE-DARK endpoint alone is NOT a full Wilson spectral-weight proof.
"""
import hashlib
import os
import sys
from math import isqrt

HERE=os.path.dirname(os.path.abspath(__file__))
INDEP=os.path.dirname(HERE)
sys.path.insert(0,os.path.join(INDEP,"y137-four-moment-fullstate-20261116"))
import four_moment_transfer as e
Q=e.exact.Ratio

UNIT=1000000000000
DEN=1000000000
N=8
WF=(1,3,2,3,3,2,2,2)
SOURCE=os.path.join(HERE,"INPUT-CENTERED-O8-64.hbp")
SOURCE_GIT_BLOB="61b9d1359f5cae2d19c3b4827ee942ca7dd085ea"
SOURCE_RUN="44120602178"
SOURCE_JOB="134170606705"
FLOOR_NUM=94068200000
ORIGINAL_SINE2=9197961975
MATCHED_E2_SINE=5047836049
MATCHED_E2_FULL_DISTANCE=4761738647
D=e.ra.D
E2_LO,E2_HI=e.EXPECTED_WINDOWS[1]

def need(cond,reason):
    if not cond:
        print("Y137_REVERSE_REFUSE|reason="+reason+"|json=0",flush=True)
        raise SystemExit(1)

def emit(tag,**items):
    print(tag+"|"+"|".join(str(k)+"="+str(v) for k,v in items.items())+"|json=0",flush=True)

def ceildiv(a,b):
    need(a>=0 and b>0,"integer_outward_ceil_domain")
    return (a+b-1)//b

def sqrtup(num,den):
    need(num>=0 and den>0,"nonnegative_sqrt_ratio")
    x=ceildiv(num*UNIT*UNIT,den)
    y=isqrt(x)
    return y if y*y==x else y+1

def sqrtlow(num,den):
    need(num>=0 and den>0,"nonnegative_sqrt_ratio")
    return isqrt(num*UNIT*UNIT//den)

def gcdblob(path):
    b=open(path,"rb").read()
    return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+bytes((0,))+b).hexdigest()

def parse(line):
    parts=line.split("|")
    result={}
    for p in parts[1:]:
        k,sep,v=p.partition("=")
        need(bool(sep) and k not in result,"bad_source_receipt_field")
        result[k]=v
    need(result.get("json")=="0","bad_hbp_terminal")
    return result

def original_centered_matrix():
    need(gcdblob(SOURCE)==SOURCE_GIT_BLOB,
         "original_source_O2_64_receipt_SHA")
    rows=open(SOURCE,encoding="ascii").read().splitlines()
    need(len(rows)==68,"original_centered_O8_total_rows")
    hdr=parse(rows[0]);scope=parse(rows[1]);mat=parse(rows[2])
    need(hdr["pr"]=="282" and hdr["run"]==SOURCE_RUN
         and hdr["job"]==SOURCE_JOB
         and scope["integer_observable"]=="TWO_ORIGINAL_O_MINUS_SEVEN_I"
         and scope["rational_mu"]=="7/2"
         and mat["source_entries"]=="64_OF_64"
         and mat["full_original_Q_shell4_residuals"]=="INCLUDED"
         and mat["original_E1_window"]=="69909429421:69909586556"
         and mat["original_E2_window"]=="69949264147:69949433884",
         "original_QOQ_scope_or_true_E_window")
    A=[[0]*N for _ in range(N)]
    R=[[0]*N for _ in range(N)]; seen=set()
    for row in rows[3:67]:
        need(row.startswith("Y137_O8_ENTRY|"),
             "original_O2_matrix_missing_entry")
        x=parse(row);i,j=int(x["i"]),int(x["j"])
        need(0<=i<N and 0<=j<N and (i,j) not in seen
             and int(x["den"])==2*UNIT*UNIT,
             "original_O2_source_denominator")
        seen.add((i,j))
        A[i][j]=int(x["approx_signed_num"])
        radius=int(x["Q_residual_radius_num"])+int(x["energy_band_radius_num"])
        need(radius>=0 and
             int(x["lower_signed_num"])==A[i][j]-radius and
             int(x["upper_signed_num"])==A[i][j]+radius,
             "original_full_Q_centered_interval_invalid")
        R[i][j]=radius
    need(len(seen)==64,"source_64_entries_missing")
    result=parse(rows[67])
    need(result["entire_true_original_Oeff_8x8"]==
         "64_CENTERED_RATIONAL_ENTRY_INTERVALS"
         and result["true_normalized_first_Wilson_weight"]=="HOLD",
         "wrong_source_true_Wilson_scope")
    return A,R

def moment_center():
    with open(e.source.MU3_FILE,encoding="ascii") as f:
        accepted=e.source.parse_pinned_mu3(f.read())
    windows=e.three_moment_windows()
    need(tuple(windows)==e.EXPECTED_WINDOWS,
         "original_true_physical_windows")
    z,lo,hi,v2,_,gap,_=e.ra.ROWS[1]
    u,m0,m1,m2=e.source.accepted_old_moments(1)
    m3=e.exact.F(accepted[z])
    low,high=e.exact.bracket4(u,m0,m1,m2,m3,
                               e.FLOOR-z,468000000000-z)
    need(e.exact.pd(e.exact.sub(high,low)),
         "signed_mu3_four_moment_not_nested")
    Cn,Cd,Wn,Wd=e.all_refs(low,high)["CENTRE"]
    need(all(Cn[i][j]==Cn[j][i]
             for i in range(N) for j in range(N)),
         "Schur_center_not_symmetric")
    # The CENTRE width Wn/Wd is HALF the full Loewner width.
    eps_width=sum((Q(Wn[i][i],WF[i]*Wd*D)
                   for i in range(N)),Q(0))
    need(eps_width.numerator>=0,"negative_Loewner_trace_width")
    graw=FLOOR_NUM-max(z,E2_HI)
    need(graw>0,"Q_floor_not_above_E2")
    drift=Q(max(abs(z-E2_LO),abs(z-E2_HI)),DEN)
    eps_drift=drift*(Q(1)+Q(72*DEN*DEN,graw*graw))
    eps=eps_width+eps_drift
    need(eps.numerator>0,"zero_Schur_source_uncertainty")
    vrec=e.ra.recentre(Cn,list(v2))
    need(sum(WF[i]*v2[i]*vrec[i] for i in range(N))>0,
         "center_pulse_wrong_orientation")
    # Reproduce the independent hosted PR284 E2 source-matched
    # four-moment and normalized full-W projector receipt. The
    # historical original Wilson source is NOT this recentered vector.
    moved=e.flat_distance(list(v2),vrec)
    need(moved==3693022069,"hosted_PR284_E2_direction_regression")
    qlo,qhi=e.fw.Q_NORMS[1]
    spread=ceildiv(e.fw.B_NORM_UP*moved*DEN,
                   UNIT*(e.FLOOR-z))
    qlo=max(0,qlo-spread)
    qhi+=spread
    ang=e.ra.angle(Cn,Cd,Wn,Wd,vrec,z,lo,hi,gap)
    ee=max(z-lo,hi-z)
    mu0=ang["mu"]-ang["extra"]-ceildiv(ee*UNIT,DEN)
    gap2=min(E2_LO-e.EXPECTED_WINDOWS[0][1],
             e.ra.E3_LO-E2_HI)*(UNIT//DEN)
    matched=e.fw.compose(ang["Hcenter"]+ang["action"],
                         mu0,gap2,z,E2_LO,E2_HI,qlo,qhi)
    need(matched["error"]==MATCHED_E2_FULL_DISTANCE,
         "hosted_PR284_E2_matched_physical_distance")
    factor=sqrtup(graw*graw+72*DEN*DEN,graw*graw)
    matched_flat=ceildiv(matched["error"]*factor,UNIT)
    need(matched_flat==MATCHED_E2_SINE and
         MATCHED_E2_SINE<ORIGINAL_SINE2,
         "hosted_PR284_E2_matched_Wflat_sine")
    return Cn,Cd*D,eps,eps_width,eps_drift,vrec

def wnorm(v):
    return sum(WF[i]*v[i]*v[i] for i in range(N))

def wdot(v,w):
    return sum(WF[i]*v[i]*w[i] for i in range(N))

def sigmas(A,Cn,Sden,eps,v1,v2,vrec,k,p,kind,src,original_amp):
    n1=wnorm(v1);n2=wnorm(v2)
    nv=wnorm(src)
    need(n1>0 and n2>0 and nv>0,
         "zero_source_direction")
    a=sum(src[i]*sum(A[i][j]*v1[j] for j in range(N))
          for i in range(N))
    base=abs(a)
    # True normalized source O2 amplitude is in raw W-bilinear
    # central source units, dividing by T^2.
    amplitude=sqrtlow(a*a,UNIT*UNIT*UNIT*UNIT*n1*nv)
    center=[sum(Cn[i][j]*src[j] for j in range(N))
            for i in range(N)]
    res_sq6=sum((6//WF[i])*center[i]*center[i]
                for i in range(N))
    residual_lo=sqrtlow(res_sq6,6*Sden*Sden*nv)
    residual_hi=sqrtup(res_sq6,6*Sden*Sden*nv)
    d=wdot(v2,src)
    need(d*d<=n2*nv,"weighted_angle_Cauchy")
    angle_sq_num=n2*nv-d*d
    angle_sine=sqrtup(angle_sq_num,n2*nv)
    eps_limit=ceildiv(eps.numerator*UNIT,eps.denominator)
    # If candidate's Schur center residual exceeds the complete
    # four-moment+energy drift envelope it CANNOT be actual null.
    excluded=int(residual_lo>eps_limit)
    # Else it merely remains feasible with respect to this ONE test.
    within_angle=int(angle_sine<=ORIGINAL_SINE2)
    matchnorm=wnorm(vrec)
    dm=wdot(vrec,src)
    need(dm*dm<=matchnorm*nv,"matched_center_Cauchy")
    match_sq=matchnorm*nv-dm*dm
    matched_angle_lower=sqrtlow(match_sq,matchnorm*nv)
    matched_angle_upper=sqrtup(match_sq,matchnorm*nv)
    matched_dark_excluded=int(matched_angle_lower>MATCHED_E2_SINE)
    emit("Y137_REVERSE_PATH",
         kind=kind,outside_step=k,center_pulse_step=p,
         source_fixed_O2_signed_amplitude_sign=(a>0)-(a<0),
         original_centered_source_abs_amplitude_per_trillion=amplitude,
         original_E2_source_angle_sine_up_per_trillion=angle_sine,
         source_Schur_residual_lo_per_trillion=residual_lo,
         source_Schur_residual_hi_per_trillion=residual_hi,
         complete_Schur_uncertainty_up_per_trillion=eps_limit,
         original_E2_angle_cone_feasible=within_angle,
         matched_E2_source_angle_sine_lo_per_trillion=matched_angle_lower,
         matched_E2_source_angle_sine_hi_per_trillion=matched_angle_upper,
         matched_E2_sine_certified_upper_per_trillion=MATCHED_E2_SINE,
         matched_direction_excluded_by_angle=matched_dark_excluded,
         actual_Schur_null_excluded_for_fixed_direction=excluded,
         true_O2_amplitude_certified="NO_SOURCE_MATRIX_UNCERTAINTY",
         actual_first_Wilson_weight="HOLD")
    return amplitude,residual_hi,angle_sine,excluded,matched_angle_lower,matched_dark_excluded

def main():
    A,R=original_centered_matrix()
    Cn,Sden,eps,eps_width,eps_drift,vrec=moment_center()
    v1,v2=[list(e.ra.ROWS[i][3]) for i in (0,1)]
    row=[sum(A[i][j]*v1[j] for j in range(N)) for i in range(N)]
    s=[(6//WF[i])*row[i] for i in range(N)]
    ss=wnorm(s);a=wdot(v2,s)
    need(ss>0 and a!=0,"source_central_Wilson_dark_seed")
    vd=[ss*v2[i]-a*s[i] for i in range(N)]
    need(wnorm(vd)>0 and wdot(vd,s)==0,
         "inverse_dark_endpoint_not_exact")
    need(sum(vd[i]*row[i] for i in range(N))==0,
         "inverse_dark_original_Wilson_bilinear_not_zero")
    need(wnorm(vrec)>0 and wdot(v2,vrec)>0,
         "source_recentred_E2_not_certified")
    # Here is the INVERSE-dark lower bound independent of any
    # particular path: among ALL Wflat unit directions x with
    # <x,s>_W=0, their least possible Wflat sine from vrec is
    # |<vrec,s>|/(||vrec||_W ||s||_W). Both are original source
    # integers. This tests the ENTIRE source-dark hyperplane,
    # rather than merely the one endpoint closest to old v2.
    ar=wdot(vrec,s)
    nrec=wnorm(vrec)
    need(nrec>0 and ar!=0 and ar*ar<=nrec*ss,
         "inverse_dark_hyperplane_geometry")
    closest_to_recentered=[ss*vrec[i]-ar*s[i]
                           for i in range(N)]
    need(wdot(closest_to_recentered,s)==0,
         "inverse_hyperplane_projector_not_exact")
    required_min_sine_lo=sqrtlow(ar*ar,nrec*ss)
    required_min_sine_hi=sqrtup(ar*ar,nrec*ss)
    source_dark_all_excluded=int(ar*ar*UNIT*UNIT>
                                 MATCHED_E2_SINE*MATCHED_E2_SINE*nrec*ss)
    # Inverse robustness target: quantify the greatest total source
    # perturbation eta=||K_true*x1 - Kstar*v1||_W (for unit flats)
    # which is SUFFICIENT to exclude every dark E2 vector within
    # the matched E2 cone. If:
    #   a0-eta > sine2*(||sstar||+eta)
    # then no admissible dark direction is possible. The goal is to
    # compare the REQUIRED eta against the EXISTING independent original
    # 64-entry true-energy source bound and E1 projector uncertainty.
    n1=wnorm(v1)
    source_a_lo=sqrtlow(ar*ar,36*UNIT*UNIT*UNIT*UNIT*nrec*n1)
    source_s_hi=sqrtup(ss,36*UNIT*UNIT*UNIT*UNIT*n1)
    needed=source_a_lo*UNIT-MATCHED_E2_SINE*source_s_hi
    tolerance=max(0,needed//(UNIT+MATCHED_E2_SINE))
    need(source_a_lo>0 and source_s_hi>0,
         "inverse_source_brightness_zero")
    rvec=[sum(abs(v1[j])*R[i][j] for j in range(N))
          for i in range(N)]
    source_r6=sum((6//WF[i])*rvec[i]*rvec[i] for i in range(N))
    full_Q_M_action_err=sqrtup(source_r6,
                               6*UNIT*UNIT*UNIT*UNIT*n1)
    E1_SINE=3429010525
    c1=isqrt(UNIT*UNIT-E1_SINE*E1_SINE)
    E1_chord=E1_SINE+(UNIT-c1)
    g1=FLOOR_NUM-69909586556
    g2=FLOOR_NUM-69949433884
    need(g1>0 and g2>0,"source_true_E1_E2_below_floor")
    M_op=21*UNIT+ceildiv(21*72*DEN*DEN*UNIT,g1*g2)
    E1_source_err=ceildiv(M_op*E1_chord,UNIT)
    total_eta=full_Q_M_action_err+E1_source_err
    robust_exclusion=int(total_eta<tolerance and tolerance>0)
    emit("Y137_REVERSE_ROBUST_TARGET",
         matched_E2_max_sine_per_trillion=MATCHED_E2_SINE,
         frozen_source_abs_rec_amplitude_lo_per_trillion=source_a_lo,
         frozen_source_Wilson_action_norm_hi_per_trillion=source_s_hi,
         sufficient_full_source_action_error_strict_max_per_trillion=tolerance,
         original_full_Q_true_energy_directional_box_error_per_trillion=
              full_Q_M_action_err,
         true_E1_projector_contribution_per_trillion=E1_source_err,
         certified_total_source_action_error_per_trillion=total_eta,
         original_source_rational_full_Q_all_64_entries="INCLUDED",
         exact_original_E1_sine=E1_SINE,
         true_Wilson_dark_excluded_by_this_sufficient_gate=robust_exclusion,
         actual_original_first_Wilson_weight="HOLD")
    # Reverse endpoint MUST be compared to certified matched flat
    # state angle and with FULL source K and E1 errors still open.
    emit("Y137_REVERSE_DARK_HYPERPLANE",
         closest_dark_to_recentered_sine_lo_per_trillion=required_min_sine_lo,
         closest_dark_to_recentered_sine_hi_per_trillion=required_min_sine_hi,
         certified_matched_E2_sine_ceiling_per_trillion=MATCHED_E2_SINE,
         all_dark_directions_for_fixed_original_centered_M_excluded=
              source_dark_all_excluded,
         exact_integer_strict_cross_product="PASS",
         full_true_centered_Wilson_K_errors="NOT_BOUNDED_HERE",
         true_E1_projector_error="NOT_BOUNDED_HERE",
         actual_original_first_Wilson_weight="HOLD")
    noQ=sigmas(A,Cn,Sden,eps,v1,v2,vrec,8,0,
                "DARK_ENDPOINT",vd,None)
    results=[]
    for k in range(8,-1,-1):
        v=[8*ss*v2[i]-k*a*s[i] for i in range(N)]
        res=sigmas(A,Cn,Sden,eps,v1,v2,vrec,k,0,
                   "OUTSIDE_IN",v,None)
        results.append((k,res))
    need(results[0][1][0]==0 and
         results[-1][1][2]==0,
         "outside_in_dark_to_original_endpoints")
    pulse=[]
    for p in range(0,9):
        v=[(8-p)*vd[i]+p*ss*vrec[i] for i in range(N)]
        res=sigmas(A,Cn,Sden,eps,v1,v2,vrec,8,p,
                   "CENTER_PULSE",v,None)
        pulse.append((p,res))
    need(pulse[0][1]==noQ and pulse[-1][1][0]>0,
         "center_pulse_source_negative_control")
    need(eps_width.numerator>=0 and eps_drift.numerator>0,"source_uncertainty_terms")
    emit("Y137_REVERSE_SOURCE",
         source_M="PR282_ORIGINAL_CENTERED_64_PHYSICAL_HBP",
         source_Schur="PR234_SIGNED_REAL_MU3_FOUR_MOMENT_CENTER",
         original_E1_direction="PR180_OLD_WITNESS",
         original_E2_direction="PR180_OLD_WITNESS",
         center_pulse_direction="PR234_FOUR_MOMENT_RECENTERED_E2",
         original_physical_E2_window="69949264147:69949433884",
         full_Q_floor="940682/10000",
         target_endpoint="ZERO_WILSON_SOURCE_BILINEAR",
         source_M_sqrt_bound="APPROXIMATE_ONLY",
         source_Schur_loewner_width="CERTIFIED_CONDITIONAL",
         original_E2_sine_bound_per_trillion=ORIGINAL_SINE2,
         matched_E2_sine_bound_per_trillion=MATCHED_E2_SINE,
         matched_source_PR284_hosted_replay="EXACT_PASS",
         source_uncertainty_width_up_per_trillion=
             ceildiv(eps_width.numerator*UNIT,eps_width.denominator),
         energy_drift_up_per_trillion=
             ceildiv(eps_drift.numerator*UNIT,eps_drift.denominator),
         original_source_spectral_gap="CONDITIONALLY_ACCEPTED")
    emit("Y137_REVERSE_VERDICT",
         exact_dark_source_end="PASS",
         inward_path_count=len(results),
         center_pulse_count=len(pulse),
         dark_source_excluded_by_current_Schur_only=noQ[3],
         dark_source_excluded_by_matched_E2_sine_only=noQ[5],
         dark_source_to_matched_sine_lower_per_trillion=noQ[4],
         all_source_dark_hyperplane_excluded_under_matched_E2_cone=
              source_dark_all_excluded,
         best_possible_dark_from_matched_sine_lo_per_trillion=
              required_min_sine_lo,
         independently_verified_true_wilson_M="NOT_CONSTRAINED_TO_SOURCE_CENTRE",
         true_E1_projector_angle="NOT_USED",
         global_dark_state_physical_exclusion="NOT_PROVED",
         original_first_Wilson_spectral_weight="HOLD",
         issue_137="OPEN")

def toy():
    # W=diag(1,2), Mv1=(2,1). For v2=(1,1),
    # nearest W-orthogonal dark direction is (1, -1).
    w=(1,2);src=(2,1);v=(1,1)
    ss=sum(w[i]*src[i]*src[i] for i in range(2))
    a=sum(w[i]*v[i]*src[i] for i in range(2))
    vd=[ss*v[i]-a*src[i] for i in range(2)]
    need(ss==6 and a==4
         and sum(w[i]*vd[i]*src[i] for i in range(2))==0
         and vd==[-2,2],
         "exact_weighted_inverse_dark_source_toy")
    need(sqrtup(2,4)==707106781187
         and sqrtlow(4,4)==UNIT
         and ceildiv(7,3)==3,
         "integer_root_outward_toy")
    emit("Y137_REVERSE_TOY",inverse_weighted_dark="PASS",
         exact_damping_endpoint="ZERO",
         strict_integer_square_roots="PASS",
         original_first_Wilson_weight="HOLD")

if __name__=="__main__":
    if sys.argv[1:]==["toy"]:toy()
    elif sys.argv[1:]==["real"]:
        toy()
        main()
    else:need(False,"usage_toy_or_real")
