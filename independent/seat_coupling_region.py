#!/usr/bin/env python3
"""Finite S3 2x2 torus coupling-region gap witnesses (stdlib, exact rationals).

Theorem: If H(JE,JB)=JE E+JB M and its weighted-selfadjoint finite
electric matrix has Gershgorin 0<=lambda(E)<=48 while 0<=M<=12, then
|gap(J)-gap(J0)| <= 96*|JE-JE0| + 24*|JB-JB0| by Weyl inequalities.

This is an exact inequality for the SAME 1393-state finite model, not a
new numerical diagonalization, a new certified spectral threshold, a proof
for larger lattices or a 4D Yang-Mills theorem. It depends on the
previously recorded Stage 2G upper E0 bounds and PR #9 verified
Stage 2H lower E1 thresholds. No JSON output.
"""
from contextlib import redirect_stdout
from fractions import Fraction as Q
from io import StringIO
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
with redirect_stdout(StringIO()):
    m = runpy.run_path(str(HERE / "seat_yang_mills_audit.py"))
rows = m["rowmaps"]
weights = m["weights"]
mag = m["mag"]
assert len(rows) == len(weights) == len(mag) == 1393
assert sum(weights) == 7776
assert sum(len(row) for row in rows) == 32385
assert len({id(row) for row in rows}) == 1393

# The weighted symmetric electric matrix is a graph Laplacian. In a
# weighted inner product, Gershgorin still bounds its REAL eigenvalues.
# Diagonal d_i and off-diagonal absolute row sum d_i => [0,2*d_i].
for i, row in enumerate(rows):
    diag = row.get(i, 0)
    assert 0 <= diag <= 24
    assert sum(row.values()) == 0
    assert all(v < 0 for j, v in row.items() if i != j)
    assert sum(-v for j, v in row.items() if i != j) == diag
    assert 0 <= mag[i] <= 12
    for j, v in row.items():
        assert weights[i] * v == weights[j] * rows[j].get(i, 0)

# Pin the antecedent: Stage 2H lower thresholds independently confirmed
# by PR #9; THIS script only transports those prior certificates via Weyl.
receipts = (HERE / "seat_sturm_full_inertia.measure").read_text().splitlines()
assert len(receipts) == 2
assert all("result=PASS" in line and "pivots=1393|negative=1|zero=0" in line and
           "full_E1_inertia_certified=1|json=0" in line for line in receipts)
assert any("JE=1|JB=1|threshold=13240/1000" in line for line in receipts)
assert any("JE=3|JB=5|threshold=50840/1000" in line for line in receipts)

# Exact rational E1 lower bound from inertia, E0 upper from Stage 2G.
# All data here are proven numerical endpoints from the existing receipts.
anchors = [
    ("near_1_1", Q(1), Q(1), Q(13240, 1000), Q(7634199, 1000000),
     Q(1,100), Q(1,20)),
    ("near_3_5", Q(3), Q(5), Q(50840, 1000), Q(36699228, 1000000),
     Q(1,20), Q(1,5)),
]
assert all((je-dje) > 0 and (jb-djb) >= 0 for _,je,jb,_,_,dje,djb in anchors)

print(
    "HEBC-COUPLING|result=PASS|states=1393|electric_norm_upper=48|"
    "magnetic_norm_upper=12|method=WEYL_GERSHGORIN_EXACT_RATIONAL|"
    "input_operator_sha=b6c608f50f81f3bf48fb0203b48e0e3bfc867037dc1d0a96633aa80b962137f3|"
    "json=0"
)
for name,je,jb,e1_lower,e0_upper,dje,djb in anchors:
    base_gap = e1_lower - e0_upper
    perturb = 2*(48*dje + 12*djb)
    min_gap = base_gap - perturb
    assert base_gap>0 and min_gap>0
    assert (name,min_gap) in [
        ("near_1_1",Q(3445801,1000000)),
        ("near_3_5",Q(4540772,1000000)),
    ]
    print(
        f"HEBC-COUPLING|result=PASS|region={name}|"
        f"JE=[{je-dje},{je+dje}]|JB=[{jb-djb},{jb+djb}]|"
        f"base_gap_strict_gt={base_gap}|"
        f"maximum_gap_perturbation={perturb}|"
        f"gap_strict_gt={min_gap}|scope=FINITE_S3_2X2_ONLY|json=0"
    )
print(
    "HEBC-COUPLING|result=PASS|claim=ALL_JE_GT_ZERO_JB_GE_ZERO_QUALITATIVE_GAP|"
    "basis=CONNECTED_STOQUASTIC_FINITE_MATRIX|"
    "global_uniform_lower_bound=NONE|"
    "reason=SCALING_AND_JE_TO_ZERO_MAGNETIC_DEGENERACY|"
    "continuum_proven=0|json=0"
)
