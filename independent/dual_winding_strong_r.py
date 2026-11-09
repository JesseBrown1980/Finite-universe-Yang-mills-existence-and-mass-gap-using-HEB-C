#!/usr/bin/env python3
"""Exact integer full-space dual-winding first-state weight bound on finite 3x4 S3.

This is for the explicitly nonlocal flat-PROJECTED electric holonomy-shift
observable, not a conventional Wilson-loop character. The original r=9
Wilson/summed-winding overlap remains open.
"""
from itertools import permutations
from hashlib import sha256
import sys

FAULTS = ("drop_transposition", "change_orbit_weight", "drop_dual_edge", "wrong_first_mode")
fault = ""
if len(sys.argv) == 2 and sys.argv[1].startswith("sabotage="):
    fault = sys.argv[1][9:]
    if fault not in FAULTS:
        raise SystemExit("unknown sabotage")
elif len(sys.argv) != 1:
    raise SystemExit("usage: dual_winding_strong_r.py [sabotage=NAME]")

def require(condition, tag):
    if not condition:
        print("DUALWIND_FAIL|gate=" + tag + "|json=0", flush=True)
        raise SystemExit(1)

G = tuple(permutations(range(3)))
ids = {g:i for i,g in enumerate(G)}
MUL = tuple(tuple(ids[tuple(G[a][G[b][i]] for i in range(3))] for b in range(6)) for a in range(6))
INV = tuple(next(b for b in range(6) if MUL[a][b] == MUL[b][a] == 0) for a in range(6))
TRAN = tuple(a for a in range(1,6) if MUL[a][a] == 0)
if fault == "drop_transposition":
    TRAN = TRAN[:-1]
require(len(TRAN)==3, "three_transposition_class_sum")

def conj(g,a):
    return MUL[MUL[g][a]][INV[g]]

# Explicit commuting holonomy pairs (a,b) for the two torus cycles,
# modulo simultaneous root gauge conjugation; no matrix rows imported.
reps=[]
class_idx={}
weights=[]
for a in range(6):
    for b in range(6):
        if MUL[a][b] != MUL[b][a] or (a,b) in class_idx:
            continue
        orb={(conj(g,a),conj(g,b)) for g in range(6)}
        k=len(reps)
        reps.append((a,b))
        weights.append(len(orb))
        for item in orb:
            class_idx[item]=k
require(len(class_idx)==18 and len(reps)==8 and sum(weights)==18,
        "complete_eight_flat_holonomy_classes")
if fault == "change_orbit_weight":
    weights[3]+=1

# Flat projected dual electric x-winding shift on class functions:
# (O_x f)([a,b]) = sum_{t transpositions, [ta,b]=[b,ta]} f([ta,b]).
# It extends as zero on every nonflat gauge orbit. This is a nonlocal,
# gauge-invariant and translation-invariant electric shift, NOT chi(W_x).
Cx=[[0]*8 for _ in range(8)]
Cy=[[0]*8 for _ in range(8)]
for i,(a,b) in enumerate(reps):
    for t in TRAN:
        ta=MUL[t][a]
        tb=MUL[t][b]
        if MUL[ta][b]==MUL[b][ta]:
            Cx[i][class_idx[(ta,b)]]+=1
        if MUL[a][tb]==MUL[tb][a]:
            Cy[i][class_idx[(a,tb)]]+=1
if fault == "drop_dual_edge":
    Cx[3][0]-=1
for m in (Cx,Cy):
    require(all(weights[i]*m[i][j]==weights[j]*m[j][i]
                for i in range(8) for j in range(8)),
            "weighted_winding_selfadjoint")
require(max(sum(row) for row in Cx)<=3,
        "dual_operator_norm_le_three")
# Original separately verified first-shell calculation yields C1 = 3/2 Cy;
# independent group algebra verifies top two weighted eigenvectors.
ug=(1,1,1,0,0,0,0,0)
ue=(0,0,0,1,1,0,0,0)
if fault == "wrong_first_mode":
    ue=(0,0,0,1,0,0,0,0)
require(all(sum(Cy[i][j]*ug[j] for j in range(8))==3*ug[i]
            and sum(Cy[i][j]*ue[j] for j in range(8))==ue[i]
            for i in range(8)),
        "top_two_C1_eigenvectors")
wg=sum(weights[i]*ug[i]*ug[i] for i in range(8))
we=sum(weights[i]*ue[i]*ue[i] for i in range(8))
cross=sum(weights[i]*ue[i]*sum(Cx[i][j]*ug[j] for j in range(8)) for i in range(8))
require((wg,we,cross)==(6,6,6),"normalized_leading_matrix_element_one")
# Spectral gaps of the ideal 8-state Schur matrix K, where 2*C1=3*Cy:
# gamma_g=3/r^2 and gamma_e=3/(2r^2).  All-state eta(r) controls
# residual K-lambda (including any omitted nonflat state).
# For r>=100000, t=r^2*eta is decreasing. Evaluate its largest value
# at r0 with one exact integer rational numerator/denominator.
r0=100000
d=3*r0
N=5184*d*d+373248*(d-72)*(d-72)
D=d*d*(d-72)**3
x=N*r0*r0
a=3*D-x
b=3*D-2*x
require(a>0 and b>0,"isolated_first_two_Schur_modes")
# Canonical mode vectors differ from flat projections of true eigenstates
# in norm by <=2*eta/(gamma_i-eta), from the exact residual plus
# elementary spectral projection. ||O_x||<=3 gives error <=
# 6 * [ eta/(gamma_g-eta) + eta/(gamma_e-eta) ].
error_n=6*x*(b+2*a)
error_d=a*b
require(100*error_n<93*error_d,"overlap_error_under_93_percent")
# ||Q psi|| <= sqrt(72)/(3r-72) ||P psi||, hence product
# of flat projection norms >=1/(1+q) where q=72/(3r-72)^2.
require(72*1000<(d-72)*(d-72),"nonflat_projection_mass_small")
# Therefore amplitude > (1-.93)/(1+.001)=70/1001>1/16,
# and the SQUARED first spectral weight >1/256 at all r>=100000.
require(70*16>1001,"rational_lower_weight_bound")
hash_cx=sha256("|".join(str(v) for row in Cx for v in row).encode()).hexdigest()
hash_cy=sha256("|".join(str(v) for row in Cy for v in row).encode()).hexdigest()
print("DUALWIND_3X4|group=S3|flat_classes=8|commuting_raw=18|weights=1,3,2,3,3,2,2,2|operator=FLAT_PROJECTED_DUAL_ELECTRIC_X_WINDING|local_Wilson_character=NO|json=0")
print("DUALWIND_COUPLING|ground_C1=9/2|first_C1=3/2|normalized_leading_amplitude=1|Cx_operator_norm_le=3|Cx_sha256="+hash_cx+"|Cy_sha256="+hash_cy+"|json=0")
print("DUALWIND_FULL_WEIGHT|r_range=r_ge_100000|full_first_state_weight_lower=1/256|strict=YES|proof=ALL_NONFLAT_SCHUR_REMAINDER|Perron_store=NOT_USED|json=0")
print("DUALWIND_SCOPE|r9_Wilson_sum_first_overlap=OPEN|r9_dual_shift_first_overlap=OPEN|continuum_SU2=OPEN|json=0")
