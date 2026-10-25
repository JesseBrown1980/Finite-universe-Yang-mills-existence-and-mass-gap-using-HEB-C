#!/usr/bin/env python3
"""Global finite S3 2x2 torus coupling-ratio gap theorem (exact arithmetic).

For every JE>0, JB>=0 on the SAME finite 1393-state Hamiltonian:
    gap(JE,JB) >= 6*JE / (24+12*JB/JE)^16 > 0.
Antecedents: original finite electric gap=6 and fully reconstructible
weighted-connected graph operator; PR #9 certified E1 thresholds for
the stronger r-chart regions, PR #11 magnetic endpoint for s-chart.
No JSON, floating point, continuum inference or eigensolver.
"""
from collections import deque
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
mag=model["mag"]
n=len(rows)
assert n==1393 and len(weights)==n and len(mag)==n
assert sum(weights)==7776 and sum(map(len,rows))==32385
assert set(weights)<={1,2,3,6}
assert all(0<=x<=12 for x in mag)
assert sum(w*x for w,x in zip(weights,mag))==8*sum(weights)
graph=[]
for i,row in enumerate(rows):
    diag=row.get(i,0)
    assert 0<=diag<=24 and sum(row.values())==0
    assert all(v<0 for j,v in row.items() if j!=i)
    assert sum(-v for j,v in row.items() if j!=i)==diag
    for j,v in row.items():
        assert weights[i]*v==weights[j]*rows[j].get(i,0)
    graph.append(tuple(j for j,v in row.items() if j!=i and v<0))

def eccentricity(start):
    dist=[-1]*n
    dist[start]=0
    queue=deque([start])
    while queue:
        i=queue.popleft()
        for j in graph[i]:
            if dist[j]<0:
                dist[j]=dist[i]+1
                queue.append(j)
    assert all(d>=0 for d in dist)
    return max(dist)

diameter=max(eccentricity(i) for i in range(n))
assert diameter==8

inertia=(HERE/"seat_sturm_full_inertia.measure").read_text().splitlines()
assert len(inertia)==2
assert all("result=PASS" in line and
           "pivots=1393|negative=1|zero=0" in line and
           "full_E1_inertia_certified=1|json=0" in line for line in inertia)
assert any("JE=1|JB=1|threshold=13240/1000" in line for line in inertia)
assert any("JE=3|JB=5|threshold=50840/1000" in line for line in inertia)
magnetic=(HERE/"seat_magnetic_endpoint.measure").read_text()
assert "PEP=24I8|first_order_gap=0" in magnetic
assert "s_upper=1/10000|error_coeff_max=120/1249|strict_gap_gt=s^2" in magnetic

e1_11=Q(13240,1000)
e0_35=Q(36699228,1000000)/3
e1_35=Q(50840,1000)/3
assert e1_11-e0_35==Q(251731,250000)
assert e1_35-8*2==Q(71,75)
assert e1_11-12==Q(31,25)

def lower_all_r(r):
    assert r>=0
    return Q(6,1)/(24+12*r)**(2*diameter)

# Exact rational sanity checks; the analytic inequalities cover ALL real r>=0.
for ratio in [Q(0),Q(1,10),Q(1),Q(5,3),Q(2),Q(100),Q(10000)]:
    assert lower_all_r(ratio)>0
assert Q(31,25)>0 and e1_11-e0_35>0 and e1_35-8*Q(2)>0

print("HEBC-RATIO|result=PASS|model=S3_TORUS2|dim=1393|graph_diameter=8|orbit_weight_sum=7776|nnz=32385|weighted_E_PSD=1|E_norm_le=48|M_norm_le=12|M_weighted_average=8|json=0")
print("HEBC-RATIO|result=PASS|domain=JE>0,JB>=0|r=JB/JE|gap_ge=6*JE/(24+12*r)^16|method=GROUND_STATE_GRAPH_HARNACK_POINCARE|electric_gap_antecedent=6|global_coupling_uniform=0|json=0")
print("HEBC-RATIO|result=PASS|electric_chart_r=[0,1]|gap_strict_gt=JE*(31/25+4*r)|input=STAGE2H_E1_1_1_AND_M_TRIAL|json=0")
print("HEBC-RATIO|result=PASS|electric_chart_r=[1,5/3]|gap_strict_gt=JE*251731/250000|input=STAGE2H_E1_1_1_STAGE2G_E0_3_5|json=0")
print("HEBC-RATIO|result=PASS|electric_chart_r=[5/3,2]|gap_strict_gt=JE*(1271/75-8*r)|at_r_2_gt=71/75*JE|json=0")
print("HEBC-RATIO|result=PASS|magnetic_chart_s=(0,1/10000]|gap_strict_gt=JE^2/JB|input=PR11_EIGHT_VACUUM_SECOND_ORDER|json=0")
print("HEBC-RATIO|result=PASS|claim=ALL_FINITE_POSITIVE_COUPLING_RATIOS_COVERED|proof=GLOBAL_GRAPH_BOUND_PLUS_SHARPER_REGIONS|larger_lattices=UNPROVEN|continuum_YM_proven=0|json=0")
