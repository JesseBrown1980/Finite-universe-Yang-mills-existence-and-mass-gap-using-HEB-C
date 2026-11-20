#!/usr/bin/env python3
"""Conditional interval-valid E1/E2 W-projector angle diagnostic, exact fractions.

Authentic pinned historical Stage D sources are read by the fixed producer modules,
and source_sample selects the exact matched E1/E2 original witnesses. This script
computes a directional PSD interval bound, with the identity derivative removed
from the *projected residual* but included in compressed separation. No original
Wilson result is promoted. All branch and source provenance gates remain distinct.
"""
import json
import os
import sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import source_sample as s
import check_projector as c
e=s.e
WEIGHTS=[F(w) for w in e.WF]

def interval(i,auth):
    sample=s.certificate(i,auth)
    z=e.ra.ROWS[i][0]
    v=[F(int(x)) for x in sample["source_matched_direction"].split(",")]
    assert len(v)==8 and any(v)
    sourceU,m0,m1,m2=e.source.accepted_old_moments(i)
    m3=e.exact.F(auth[z])
    L,U=e.exact.bracket4(sourceU,m0,m1,m2,m3,e.FLOOR-z,468000000000-z)
    assert e.exact.pd(e.exact.sub(U,L))
    # Historical Source's Schur bilinear uses denominator
    # D = DEN * UNIT^2, as in recentred_angle.angle.
    scale=F(e.ra.D)
    low=[[s.as_fraction(x)/scale for x in row] for row in L]
    high=[[s.as_fraction(x)/scale for x in row] for row in U]
    T=s.midpoint(low,high)
    width=c.diff(high,low)
    n=sum((WEIGHTS[j]*v[j]*v[j] for j in range(8)),F(0))
    assert n>0
    Tv=[sum((T[j][k]*v[k]/WEIGHTS[j] for k in range(8)),F(0)) for j in range(8)]
    av=sum((WEIGHTS[j]*v[j]*Tv[j] for j in range(8)),F(0))/n
    rsq=sum((WEIGHTS[j]*(Tv[j]-av*v[j])**2 for j in range(8)),F(0))/n
    residual=s.ceilrootfrac(rsq)
    # ||A|| <= ||A||_F for A = W^(-1) width.
    width_frob_sq=sum((width[j][k]**2/(WEIGHTS[j]*WEIGHTS[k])
                       for j in range(8) for k in range(8)),F(0))
    width_frob=s.ceilrootfrac(width_frob_sq)
    # Exact eight-dimensional Loewner spectral-norm upper: A <= w W.
    # The added 10^-12 ensures *strict* PD even at an exact eigenvalue.
    def width_cert(t):
        return c.pd([[((t*WEIGHTS[j] if j==k else F(0))-width[j][k])
                       for k in range(8)] for j in range(8)])
    high_width=width_frob+F(1,10**12)
    c.need(width_cert(high_width),"weighted_width_spectral_initial_upper")
    low_width=F(0)
    for _ in range(14):
        trial=(low_width+high_width)/2
        if width_cert(trial):
            high_width=trial
        else:
            low_width=trial
    width_norm=high_width
    c.need(width_cert(width_norm) and width_norm<=width_frob+F(1,10**12),
           "weighted_width_spectral_final_upper")
    # -width/2 <= S(z)-T <= width/2.
    # E=(width)^(1/2) K (width)^(1/2)/2, ||K||<=1.
    # Hence ||E u|| <= 1/2 sqrt(||width|| <u,width u>).
    width_ray=sum((v[j]*width[j][k]*v[k] for j in range(8)
                   for k in range(8)),F(0))/n
    assert width_ray>=0
    directional_error=s.ceilrootfrac(width_norm*width_ray)/2
    windows=e.three_moment_windows()
    a,b=windows[i]
    assert a<=b<e.FLOOR
    den=F(e.DEN)
    shift=max(abs(z-a),abs(z-b))/den
    gamma=F(e.FLOOR)/den
    energy_hi=F(max(z,b))/den
    assert energy_hi<gamma
    B2=F(72)
    q_deriv=B2/(gamma-energy_hi)**2
    # For the *same matched* flat witness u, R(t) <= R(z) for t<=z
    # in the commuting positive spectral calculus. The frozen original
    # Q-norm for the historical witness transports to u via ||RB||.
    c.need(b<=z,"directional_Q_monotonicity_requires_below_sample")
    old_v=list(e.ra.ROWS[i][3])
    moved_v=[int(t) for t in v]
    dist=e.flat_distance(old_v,moved_v)
    spread=e.ra.ceil_div(e.fw.B_NORM_UP*dist*e.DEN,
                         e.UNIT*(e.FLOOR-z))
    Q_upper=F(e.fw.Q_NORMS[i][1]+spread,e.UNIT)
    B_upper=F(e.fw.B_NORM_UP,e.UNIT)
    qder_directional=B_upper*Q_upper/(gamma-F(z)/den)
    c.need(qder_directional<=q_deriv,
           "directional_derivative_not_below_global")
    # Since S'(t)=-I-B*R(t)^2B, the -I term vanishes under the
    # transverse projector. ||B*R(t)^2 B u|| <= ||B|| ||R(t) B u||/
    # (gamma-t), with both terms bounded uniformly for t<=z.
    rho=residual+directional_error+qder_directional*shift
    delta_error=width_norm/2+(1+q_deriv)*shift
    pivot=max(range(8),key=lambda j:abs(WEIGHTS[j]*v[j]))
    assert v[pivot]
    columns=[]
    for j in range(8):
        if j==pivot:continue
        q=[F(0)]*8
        q[j]=F(1)
        q[pivot]=-WEIGHTS[j]*v[j]/(WEIGHTS[pivot]*v[pivot])
        columns.append(q)
    B=c.transpose(columns)
    G=[[sum((WEIGHTS[t]*B[t][j]*B[t][k] for t in range(8)),F(0))
        for k in range(7)] for j in range(7)]
    assert c.pd(G)
    K=[[sum((B[t][j]*T[t][u]*B[u][k] for t in range(8)
               for u in range(8)),F(0)) for k in range(7)] for j in range(7)]
    KK=c.mul(c.mul(K,c.inverse(G)),K)
    def cert(d):
        return c.pd(c.diff(KK,c.scaled(G,d*d)))
    candidate=F(1)
    while candidate>F(1,2**40) and not cert(candidate):
        candidate/=2
    d0=candidate if cert(candidate) else F(0)
    # The historical first pass used a coarse power-of-two lower. Preserve
    # it as a regression and improve using 12 exact rational bisections.
    coarse=d0
    if coarse>0:
        lower, upper=coarse, 2*coarse
        assert cert(lower) and not cert(upper), "failed strict singular bracket"
        for _ in range(12):
            middle=(lower+upper)/2
            if cert(middle):
                lower=middle
            else:
                upper=middle
        d0=lower
        assert d0>=coarse and cert(d0) and not cert(upper)
    delta=d0-delta_error
    target=F((2362700330,5047836049)[i],10**12)
    verified=(delta>0 and rho*rho*(1-target*target)<=target*target*delta*delta)
    return {
        "sample_num":z,"interval_lo":str(F(a)/den),
        "interval_hi":str(F(b)/den),"source_selected_k":sample["selected_fraction_num"],
        "source_weight_metric":",".join(map(str,e.WF)),
        "physical_S_denominator":str(scale),
        "residual_mid_upper":str(residual),
        "width_frobenius_upper":str(width_frob),
        "width_spectral_upper":str(width_norm),
        "exact_width_spectral_bisection_steps":14,
        "directional_width_error_upper":str(directional_error),
        "source_moved_flat_distance_per_trillion":str(dist),
        "source_Q_norm_upper":str(Q_upper),
        "directional_Q_derivative_upper":str(qder_directional),
        "projected_Q_drift_upper":str(qder_directional*shift),
        "global_Q_drift_comparison":str(q_deriv*shift),
        "full_schur_drift_upper":str((1+q_deriv)*shift),
        "sample_coarse_power2_singular_lower":str(coarse),
        "sample_compressed_singular_lower":str(d0),
        "exact_singular_bisection_steps":12,
        "interval_compressed_singular_lower":str(delta),
        "interval_projected_residual_upper":str(rho),
        "target_sine":str(target),
        "conditional_interval_angle":"PASS" if verified else "HOLD",
        "source":"PINNED_HISTORICAL_PREMISES",
        "endpoint_branch_identity":"INDEPENDENT_REVIEW_OPEN",
        "Wilson_true_first_weight":"FORMAL_HOLD",
        "continuum_4D":"OPEN"}

def main():
    # The type compatibility with historical exact-rational Stage D is tested
    # in source_sample's hosted run.
    with open(e.source.MU3_FILE,encoding="ascii") as h:
        auth=e.source.parse_pinned_mu3(h.read())
    for i in range(2):
        out=interval(i,auth)
        print("Y137_SCHUR_INTERVAL_DIRECTIONAL|"+json.dumps(out,sort_keys=True),flush=True)
if __name__=="__main__":main()
