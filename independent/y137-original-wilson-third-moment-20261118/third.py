#!/usr/bin/env python3
"""Original S3 Wilson third moment with exhaustive K4 electric action.

Modes:
  bounds: exact source m0,m1,m2, K4 magnetic, certified E4 interval.
  full: same plus all 72 raw K4 moves per supported orbit, exact m3.
No float arithmetic, no removed exterior shell, and no true-eigenvector claim.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INDEP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(INDEP, "y137-prl-original-wilson-filter-20261118"))
_ARGV = sys.argv[:]
try:
    sys.argv = sys.argv[:1]
    import moment_filter as prior
finally:
    sys.argv = _ARGV

old = prior.stage_n.previous
mod = old.mod
c = mod.c
WILSON_M2_SHA = "393954283e19f17cecaae35947088d9338c9d81f7dea7d271be9fd46c39487b6"
SOURCE_K3_SHA = "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff"
CAP = 468
ELEC_CAP = 144


def need(condition, reason):
    if not condition:
        print("Y137_M3_REFUSE|reason=" + reason + "|json=0", flush=True)
        raise SystemExit(1)


def emit(label, **fields):
    print(label + "|" + "|".join(str(k) + "=" + str(v) for k,v in fields.items()) +
          "|json=0", flush=True)


def digest(value):
    return hashlib.sha256(str(value).encode("ascii")).hexdigest()


def toy():
    # Original weighted self-adjoint block structure in a 3-coordinate toy.
    H = ((2, -1, 0), (-1, 3, -1), (0, -1, 5))
    v = (0, 1, 0)
    h = tuple(sum(row[j]*v[j] for j in range(3)) for row in H)
    m1 = sum(v[i]*h[i] for i in range(3))
    m2 = sum(z*z for z in h)
    m3 = sum(h[i]*sum(H[i][j]*h[j] for j in range(3))
             for i in range(3))
    core = 35
    cross = 6
    exterior = 5
    need(h == (-1,3,-1) and (m1,m2,m3)==(3,11,46) and
         core + cross + exterior == m3,
         "three_coordinate_original_H_toy")
    need(0 <= exterior <= 144*h[2]*h[2] and 3*46 >= 11*11,
         "toy_electric_and_Hankel")
    # Crossing sign is essential: H_Q4=-1 contributes -2 hQ*h4.
    need(cross == -2*h[1]*h[2], "wrong_Q_K4_cross_sign")
    need(core-cross+exterior != m3, "negative_cross_control")
    emit("Y137_M3_TOY", physical_H_cube="PASS",
         cross_edge_sign="PASS", nonnegative_electric="PASS",
         planted_wrong_cross="REJECTED", first_Wilson_weight="HOLD")


def source_ball():
    need(old.k.SCRIPT_SHA == SOURCE_K3_SHA, "original_K3_script_sha")
    need(c.MUL == old.observed.MUL and c.CHAR == old.observed.CHAR,
         "independent_S3_rule_and_Wilson")
    w,m,adj,qflat,outer=c.graph()
    states,flat,sizes=mod.rebuild_states()
    need(len(states)==8042 and sizes==[8,264,7770],"original_K2_census")
    where={key:i for i,key in enumerate(states)}
    C2=mod.ball_from_checker(w,m,adj,qflat,outer)["C"]
    ball,extra=mod.build_k3(states,where,w,m,adj,outer,C2)
    need(ball["n"]==155378 and ball["nf"]==1985218 and
         len(extra["code4"])==ball["nf"] and
         len(extra["s4"])==ball["nf"],"original_K3_K4_census")
    keys=states+extra["ext_keys"]
    need(len(keys)==155386,"original_Wilson_keys")
    obs=[old.obs_from_checker(k) for k in keys]
    need(min(obs)>=-7 and max(obs)<=14 and obs[6]==obs[7],
         "original_character_observable")
    for j in range(8):
        a,b=flat[states[j]]
        need(obs[j]==4*c.CHAR[a]+3*c.CHAR[b],
             "original_flat_seven_loop")
    old.emit("Y137_QDUAL_GRAPH",flats=8,q=ball["n"],shell4=ball["nf"],
             O_min=min(obs),O_max=max(obs),
             independent_raw_observable="PASS")
    return ball,extra,obs


def trial_source(ball,obs):
    source=mod.threshold_ball(old.A1,old.DEN,old.ITER,old.SCALE,
                              ball,old.FLOOR)
    flat=old.even_trial(source["U"],[1,2,3,4,5,6,7])
    trial=old.trial(ball,old.A1,flat)
    p,q=trial["p"],trial["q"]
    wf,wq=ball["wf"],ball["wq"]
    n0=old.dot_w(p,p,wf)+old.dot_w(q,q,wq)
    need(n0==trial["norm"] and n0>0,"original_trial_W_norm")
    mean=sum(wf[j]*obs[j]*p[j]*p[j] for j in range(8))
    mean+=sum(wq[i]*obs[8+i]*q[i]*q[i] for i in range(ball["n"]))
    pp=[(n0*obs[j]-mean)*p[j] for j in range(8)]
    qq=[(n0*obs[8+i]-mean)*q[i] for i in range(ball["n"])]
    need(old.dot_w(pp,p,wf)+old.dot_w(qq,q,wq)==0,
         "original_W_centered_observable")
    m0,m1,_,_,_=prior.stage_n.H_moment(ball,pp,qq)
    hp,hq,h4norm=prior.original_H_action(ball,pp,qq)
    return pp,qq,hp,hq,m0,m1,h4norm


def third_moment(mode):
    ball,extra,obs=source_ball()
    pp,qq,hp,hq,m0,m1,shell4norm=trial_source(ball,obs)
    m2=shell4norm+old.dot_w(hp,hp,ball["wf"])+old.dot_w(hq,hq,ball["wq"])
    need(digest(m2)==WILSON_M2_SHA,"previous_accepted_original_m2_sha")
    prior.checks(m0,m1,m2,CAP)
    # Reconstruct H v on every shell4 orbit, from sealed weighted K3->K4 arcs.
    n4=ball["nf"]
    h4=[0]*n4
    cross4=0
    rebuilt_shell4norm=0
    mag4=0
    num_nonzero=0
    es,esrc,ewc,eW=ball["es"],ball["esrc"],ball["ewc"],ball["eW"]
    codes=extra["code4"]
    for f in range(n4):
        acc_q=sum(ewc[k]*qq[esrc[k]] for k in range(es[f],es[f+1]))
        w=eW[f]
        need(acc_q%w==0,"source_K3_K4_weighted_integrality")
        value=-(acc_q//w)
        h4[f]=value
        rebuilt_shell4norm+=w*value*value
        if value:
            num_nonzero+=1
            key=mod.decode(codes[f])
            magnetic=c.magnetic(c.from_key(key))
            need(0<=magnetic<=36,"S3_12_plaquette_magnetic_bound")
            mag4+=9*magnetic*w*value*value
    need(rebuilt_shell4norm==shell4norm,"original_m2_shell4_exact_replay")
    for f,amp in enumerate(h4):
        if amp:
            acc_h=sum(ewc[k]*hq[esrc[k]] for k in range(es[f],es[f+1]))
            cross4-=2*amp*acc_h
    # H_QQ from Stage N's independently validated original source action.
    _,core,_,_,_=prior.stage_n.H_moment(ball,hp,hq)
    base=core+cross4+mag4
    # The electric 72I-adjacency on the full gauge-invariant Hilbert space
    # is PSD and <=144I; so is its K4 principal compression.
    lower=max(base,0,(m2*m2+m1-1)//m1)
    upper=min(base+ELEC_CAP*shell4norm,CAP*m2)
    need(0<=lower<=upper and lower*m1>=m2*m2,
         "third_moment_source_bounded_interval")
    emit("Y137_M3_SOURCE", original_Wilson="SEVEN_LOOP_24_LINK",
         flat_K3="8_AND_155378", shell4=n4,
         shell4_nonzero=num_nonzero,
         original_m2_sha256=WILSON_M2_SHA,
         original_K3_sha256=SOURCE_K3_SHA,
         field="FULL_ORIGINAL_S3_r9",
         first_Wilson_weight="HOLD")
    emit("Y137_M3_BOUNDS", m0_sha256=digest(m0),m1_sha256=digest(m1),
         m2_sha256=digest(m2),shell4_norm2_sha256=digest(shell4norm),
         m3_core_sha256=digest(core),
         cross4_sha256=digest(cross4),mag4_sha256=digest(mag4),
         shell4_norm2=shell4norm,
         core=core,cross=cross4,magnetic=mag4,
         lower=lower,upper=upper,
         electric_Ceiling=ELEC_CAP,
         all_K4_magnetic="EXACT",
         all_K4_electric="BOUNDED" if mode=="bounds" else "RUNNING")
    if mode=="bounds":
        emit("Y137_M3_VERDICT", source="K3_K4_PHYSICAL",
             physical_m3="RATIONAL_INTERVAL", full_K4_E="BOUNDED_PSD_144",
             first_Wilson_weight="HOLD")
        return
    need(mode=="full","unknown_mode")
    # Resolve the entire K4-K4 electric quadratic. Since Hv has zero
    # coefficients beyond K4, links to K5 contribute zero to this moment.
    # K3-K4 crossings have already been included as cross4 above.
    electric4=0
    counted=0
    s4=extra["s4"]
    for f,amp in enumerate(h4):
        if not amp:
            continue
        key=mod.decode(codes[f])
        off=0
        for dst,cc in c.neighbors(key).items():
            idx=s4.get(mod.code(dst))
            if idx is not None:
                off+=cc*h4[idx]
        electric4+=eW[f]*amp*(72*amp-off)
        counted+=1
        if counted%50000==0:
            emit("Y137_M3_PROGRESS", checked_nonzero=counted,
                 total_nonzero=num_nonzero)
    need(0<=electric4<=ELEC_CAP*shell4norm,
         "electric_K4_source_operator_PSD_and_ceiling")
    m3=base+electric4
    need(lower<=m3<=upper and 0<=m3<=CAP*m2 and m1*m3>=m2*m2,
         "exact_original_third_H_moment_spectrum")
    T1=CAP*m0-m1
    T2=CAP*CAP*m0-2*CAP*m1+m2
    T3=CAP*CAP*CAP*m0-3*CAP*CAP*m1+3*CAP*m2-m3
    need(0<=T3<=CAP*T2 and T1*T3>=T2*T2,
         "filtered_third_moment_Cauchy")
    emit("Y137_M3_EXACT", m3=m3,m3_sha256=digest(m3),
         electric4=electric4,electric4_sha256=digest(electric4),
         full_K4_nonzero=counted,
         third_T_sha256=digest(T3),
         exact_H3="PASS", first_Wilson_weight="HOLD")
    emit("Y137_M3_VERDICT", source="K3_K4_PHYSICAL",
         physical_m3="EXACT", full_K4_E="EXHAUSTIVE_NONZERO_72_MOVES",
         first_Wilson_weight="HOLD")


if __name__=="__main__":
    if sys.argv[1:]==["toy"]:
        toy()
    elif sys.argv[1:] in (["bounds"],["full"]):
        toy()
        third_moment(sys.argv[1])
    else:
        need(False,"usage_toy_bounds_full")
