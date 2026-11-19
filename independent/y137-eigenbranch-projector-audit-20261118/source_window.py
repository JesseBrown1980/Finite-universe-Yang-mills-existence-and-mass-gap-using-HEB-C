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
    width_norm=s.ceilrootfrac(width_frob_sq)
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
    # Since S'(E)=-I-B*R(E)^2B, its -I term annihilates
    # under the witness-transverse projector; not under compression.
    rho=residual+directional_error+q_deriv*shift
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
    delta=d0-delta_error
    target=F((2362700330,5047836049)[i],10**12)
    verified=(delta>0 and rho*rho*(1-target*target)<=target*target*delta*delta)
    return {
        "sample_num":z,"interval_lo":str(F(a)/den),
        "interval_hi":str(F(b)/den),"source_selected_k":sample["selected_fraction_num"],
        "source_weight_metric":",".join(map(str,e.WF)),
        "physical_S_denominator":str(scale),
        "residual_mid_upper":str(residual),
        "width_frobenius_upper":str(width_norm),
        "directional_width_error_upper":str(directional_error),
        "projected_Q_drift_upper":str(q_deriv*shift),
        "full_schur_drift_upper":str((1+q_deriv)*shift),
        "sample_compressed_singular_lower":str(d0),
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
