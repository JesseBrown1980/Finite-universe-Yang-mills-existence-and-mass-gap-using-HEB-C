#!/usr/bin/env python3
"""Exact-rational retrospective atlas tests. No new physical Wilson claim."""
import hashlib
import json
import sys
from fractions import Fraction
from math import isqrt
from pathlib import Path

F=Fraction

def need(ok,name):
    if not ok:
        raise SystemExit("ATLAS_EXACT_REFUSE|check="+name+"|json=0")

def row(tag,**vals):
    return tag+"|"+"|".join(k+"="+str(v) for k,v in vals.items())+"|json=0"

def gram(M,u,v):
    return sum((u[i]*M[i][j]*v[j] for i in range(len(u)) for j in range(len(v))),F(0))

def feshbach_toy():
    # A separate exact symmetric 5x5 toy, P dimension 2, Q dimension 3.
    A=[F(9),F(11),F(13)]
    B=[[F(2),F(-1)],[F(0),F(1)],[F(-2),F(3)]]
    O=[[F(t) for t in x] for x in (
      (2,1,2,0,1),(1,3,-1,1,0),(2,-1,4,1,-2),
      (0,1,1,5,2),(1,0,-2,2,6))]
    p1,p2=[F(1),F(2)],[F(-1),F(1)]
    e1,e2=F(1),F(2)
    q1=[-sum((B[i][j]*p1[j] for j in range(2)),F(0))*F(1,A[i]-e1) for i in range(3)]
    q2=[-sum((B[i][j]*p2[j] for j in range(2)),F(0))*F(1,A[i]-e2) for i in range(3)]
    actual=gram(O,p2+q2,p1+q1)
    pp=gram([x[:2] for x in O[:2]],p2,p1)
    pq=sum((p2[i]*O[i][j+2]*q1[j] for i in range(2) for j in range(3)),F(0))
    qp=sum((q2[j]*O[j+2][i]*p1[i] for j in range(3) for i in range(2)),F(0))
    qq=sum((q2[i]*O[i+2][j+2]*q1[j] for i in range(3) for j in range(3)),F(0))
    effective=pp+pq+qp+qq
    need(actual==effective,"Feshbach_observable_exact")
    need(actual!=effective-qq,"omit_QOQ_negative_control")
    for p,q,e in ((p1,q1,e1),(p2,q2,e2)):
        norm=sum((x*x for x in p),F(0))
        for i in range(3):
            bp=sum((B[i][j]*p[j] for j in range(2)),F(0))
            norm+=bp*bp*F(1,(A[i]-e)*(A[i]-e))
        need(norm==sum((x*x for x in p+q),F(0)),"Feshbach_normalization_identity")
    return actual,qq

def main():
    path=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name("certificates.json")
    raw=path.read_bytes()
    data=json.loads(raw.decode("utf-8"),parse_float=F,parse_int=int)
    need(data["source"]["commit"]=="98c39fbaa1e6ecf9e6454062e90801f385356063","frozen_source")
    need([len(data[k]) for k in ("gap_measurements","spectral_measurements","algorithm_measurements")]==[39,15,26],"80_measurements")
    lines=[row("ATLAS_SOURCE",commit=data["source"]["commit"],data_sha256=hashlib.sha256(raw).hexdigest(),records=80)]
    gaps={int(g["r"]):g for g in data["gap_measurements"] if g["name"]=="3x3" and g["kind"]=="interval"}
    need(set(gaps)=={9,27,81,243},"all_four_3x3_intervals")
    count=0
    for rr in sorted(gaps):
        g=gaps[rr]
        lo,hi=g["lower"],g["upper"]
        f2=3*rr-F(21,rr)
        f3=f2-F(43,rr*rr)
        inside=lo<=f3<=hi
        if rr==9:need(not inside,"r9_truncated_expansion_must_fail")
        else:
            need(inside,"higher_r_interval_predicted")
            count+=int(inside)
        c3lo,c3hi=(f2-hi)*rr*rr,(f2-lo)*rr*rr
        lines.append(row("ATLAS_GAP_TEST",r=rr,kind=g["kind"],certified_lo=lo,certified_hi=hi,
          model2=f2,model3=f3,model3_inside="YES" if inside else "NO",
          inferred_c3_lo=c3lo,inferred_c3_hi=c3hi))
    need(count==3,"three_large_r_cells")
    g27=gaps[27]
    wrong=F(81)-F(21,27)-F(44,27*27)
    need(not(g27["lower"]<=wrong<=g27["upper"]),"coefficient_44_negative_control")
    nine=gaps[9]
    nine_min=(F(27)-F(21,9)-nine["upper"])*81
    common_high=max((3*rr-F(21,rr)-gaps[rr]["upper"])*rr*rr for rr in (27,81,243))
    common_low=min((3*rr-F(21,rr)-gaps[rr]["lower"])*rr*rr for rr in (27,81,243))
    need(nine_min>common_low and common_high<=common_low,"r9_coefficient_not_high_r_constant")
    lines.append(row("ATLAS_GAP_VERDICT",high_r_within=3,high_r_total=3,r9_rejected="YES",
        wrong_c3_44_rejected="YES",uniform_r9_c3_rejected="YES",
        scope="RETROSPECTIVE_INTERVAL_COMPARISON"))
    H=data["hypothesis_parameters"]
    q,e2,e3,cap=(H[k] for k in ("Q_floor","E2_upper","E3_lower","operator_upper"))
    Qgap=q-e2; egap=e3-e2
    need(Qgap>0 and egap>0,"positive_Q_and_E3_separation")
    kappa=(cap-e2)*F(1,Qgap)
    S=10**18
    floor=isqrt(kappa.numerator*S*S//kappa.denominator)
    sqlo,sqhi=F(floor,S),F(floor+1,S)
    rlo=(sqlo-1)*F(1,sqlo+1)
    rhi=(sqhi-1)*F(1,sqhi+1)
    need(0<rlo<rhi<1,"strict_Chebyshev_ratio_interval")
    for tag,tgt,expected in (
        ("ONE_PERCENT",F(1,100),11),
        ("THREE_PER_THOUSAND",F(3,1000),13),
        ("OLD_1_OVER_700",F(1,700),15),
        ("TEN_THOUSANDTH",F(1,10000),20),
    ):
        m=next(j for j in range(1,100) if 2*rhi**j < tgt)
        need(m==expected,"exact_polynomial_degree_"+tag)
        need(2*rlo**(m-1)>=tgt,"minimality_"+tag)
        lines.append(row("ATLAS_FILTER_TEST",target=tag,certified_sufficient_degree=m,
            upper_bound_at_degree=2*rhi**m,scope="THEORETICAL_INVERSE_RESIDUAL_ONLY"))
    need(Qgap*F(1,egap)>1000,"spectral_scale_ratio")
    lines.append(row("ATLAS_FILTER_VERDICT",Q_minus_E2=Qgap,E3_minus_E2=egap,
        ratio=Qgap*F(1,egap),kappa=kappa,rho_lower=rlo,rho_upper=rhi,
        Wilson_transfer="NOT_COMPUTED"))
    val,qq=feshbach_toy()
    lines.append(row("ATLAS_FESHBACH_TOY",full_transition=val,effective_transition=val,
        QOQ_term=qq,omitted_QOQ_rejected="YES",full_state_normalization="PASS",
        original_3x4_Wilson="NOT_COMPUTED"))
    lines.append(row("ATLAS_VERDICT",readme_source="PASS",retrospective_large_r="3_OF_3",
       r9="ASYMPTOTIC_MODEL_REJECTED",Chebyshev_exact="PASS",
       Feshbach_exact_toy="PASS",physical_Wilson_weight="HOLD",continuum="OPEN"))
    print("\n".join(lines))

if __name__=="__main__":
    main()
