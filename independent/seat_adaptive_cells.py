#!/usr/bin/env python3
"""Exact coupling-ratio cell verifier and CONDITIONAL large-r planning.

Works only with the original finite 1393-state S3 2x2 torus. Existing
stage-2G E0, stage-2H/PR9 E1, and PR11 PEP receipts are antecedents.
No new eigenvalue solves, no fake successful coverage of 2<r<10000.
All numeric state uses exact integer-pair arithmetic. No Fraction, JSON or floating-point.
"""
from contextlib import redirect_stdout
from seat_integer_ratio import IntegerRatio as Q, selftest as integer_ratio_selftest
from io import StringIO
from pathlib import Path
import runpy

assert integer_ratio_selftest()
HERE=Path(__file__).resolve().parent
with redirect_stdout(StringIO()):
    model=runpy.run_path(str(HERE/"seat_yang_mills_audit.py"))
rows=model["rowmaps"]
weights=model["weights"]
potential=model["mag"]
assert len(rows)==len(weights)==len(potential)==1393
assert sum(weights)==7776 and sum(len(row) for row in rows)==32385
assert all(0<=x<=12 for x in potential)
assert sum(w*m for w,m in zip(weights,potential))==8*sum(weights)
flat=[i for i,x in enumerate(potential) if x==0]
assert len(flat)==8
assert all(rows[i].get(j,0)==(24 if i==j else 0)
           for i in flat for j in flat)
for i,row in enumerate(rows):
    d=row.get(i,0)
    assert 0<=d<=24 and sum(row.values())==0
    assert all(v<0 for j,v in row.items() if j!=i)
    for j,v in row.items():
        assert weights[i]*v==weights[j]*rows[j].get(i,0)
assert min(x for x in potential if x>0)==3

sturm=(HERE/"seat_sturm_full_inertia.measure").read_text().splitlines()
assert len(sturm)==2
assert all("result=PASS" in s and "pivots=1393|negative=1|zero=0" in s
           and "full_E1_inertia_certified=1|json=0" in s for s in sturm)
assert any("JE=1|JB=1|threshold=13240/1000" in s for s in sturm)
assert any("JE=3|JB=5|threshold=50840/1000" in s for s in sturm)
magnetic=(HERE/"seat_magnetic_endpoint.measure").read_text()
assert "PEP=24I8|first_order_gap=0" in magnetic
assert "second_order_charpoly=(x+6)^4*" in magnetic

# Absolute energy endpoints in the electric chart h(r)=E+rM.
# Exact lower E1 and upper E0 at r=0,1,5/3. Stage 2H lower E1
# inequalities are strict, but we weaken them to nonstrict for safe
# cell comparisons. Stage 2G upper E0 bounds remain nonstrict.
anchors=(
    (Q(0),Q(0),Q(6)),
    (Q(1),Q(7634199,10**6),Q(13240,1000)),
    (Q(5,3),Q(36699228,3*10**6),Q(50840,3000)),
)

def e1_lower(r):
    """By E1 monotonicity and 12-Lipschitz in r."""
    assert r>=0
    return max(e1-12*max(a-r,Q(0)) for a,_,e1 in anchors)

def e0_upper(r):
    """Min-max trials + anchors + 12-Lipschitz (rigorous)."""
    assert r>=0
    return min([8*r,Q(24)]+
               [e0+12*max(r-a,Q(0)) for a,e0,_ in anchors])

def slope_bound_at(r):
    """For low-lying E0,E1 at r>8, bound dE/dr.

    By min-max, E1(r)<=24: P is 8-dimensional and PEP=24 I.
    Q(E+rM-lambda)Q >=(3r-24)I for lambda<=24, since E>=0.
    ||QEP||^2<120 by PR11 B=-PEQ M_Q^-1 QEP and M_Q<=12.
    Therefore ||Qpsi||^2<=120/(3r-24)^2 and
    <psi,M psi><=12||Qpsi||^2<=1440/(3r-24)^2.
    """
    assert r>8
    return Q(1440)/(3*r-24)**2

def energy_drift(a,b):
    """Upper bound for individual E0/E1 rise for 8<a<=b.

    Integral of 1440/(3r-24)^2 across an interval; no floats.
    """
    assert 8<a<=b
    return 480*(Q(1)/(3*a-24)-Q(1)/(3*b-24))

nodes=(Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1),Q(5,3),Q(2))
margins=(Q(4),Q(2),Q(31,25),Q(2605801,10**6),
         Q(251731,250000),Q(71,75))
print("HEBC-CELLS|result=PASS|dim=1393|graph_E_PSD=1|M_PSD=1|flat=8|PEP=24I8|electric_chart=E+rM|json=0")
for i,(a,b) in enumerate(zip(nodes,nodes[1:])):
    lo=e1_lower(a)
    up=e0_upper(b)
    margin=lo-up
    assert margin==margins[i] and margin>0
    print(f"HEBC-CELLS|result=PASS|cell={i}|r=[{a},{b}]|E1_left_ge={lo}|E0_right_le={up}|gap_ge={margin}*JE|finite_S3_only=1|json=0")

# The remainder 2<r<10000 lacks sharp certified endpoint anchors.
# This script deliberately does NOT claim that monotone-cell cover is done.
# An exact global positive graph bound is already available in PR12.
assert e1_lower(Q(100))<=e0_upper(Q(100))
assert e1_lower(Q(10000))<=e0_upper(Q(10000))
print("HEBC-CELLS|result=OPEN|interval_r=(2,10000)|needs=new_E0_E1_endpoint_certificates|all_ratio_positive_fallback=PR12_GRAPH_BOUND|json=0")

# CONDITIONAL geometric planning lemma: IF a future independent inertia
# certificate provides g(a)>=1/a at a>8, choose width h=(1/2a)/L(a).
# Since E0'(r)<=L(a) throughout [a,a+h], the raw monotone cell
# E1(a)-E0(a+h)>=g(a)-L(a)h>=1/(2a)>0.
# This DOES NOT assert g(a)>=1/a at either illustrative knot.
for r in (Q(100),Q(10000)):
    L=slope_bound_at(r)
    h=Q(1,2)/r/L
    assert energy_drift(r,r+h)<Q(1,2)/r
    print(f"HEBC-CELLS|result=CONDITIONAL_ONLY|r={r}|slope_le={L}|if_anchor_gap_ge=1/{r}|width_le={h}|then_cell_gap_gt={Q(1,2)/r}*JE|anchor_certified=0|json=0")
print("HEBC-CELLS|result=PASS|method=MONOTONE_CELL_AND_LOW_ENERGY_DERIVATIVE|claim=R_0_TO_2_VERIFIED|r_2_to_10000_sharp_cells=OPEN|continuum_YM_proven=0|json=0")
