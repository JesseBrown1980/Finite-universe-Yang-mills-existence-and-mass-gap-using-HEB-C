#!/usr/bin/env python3
"""Finite 3x4 S3 actual first-gap at r=100000, rational-only independent check.

Analytic commuting-pair path count; no sector store and no floating point.
Post-exploration result: no claim that predictions preceded computation.
"""
from fractions import Fraction as F
from itertools import permutations
from sys import argv

CONTROLS = {
    "missing_transposition", "wrong_orbit_census", "wrong_pair_amplitude",
    "wrong_cross_class", "wrong_eigenvalues", "wrong_flat_norm",
    "wrong_magnetic_min", "omit_remainder", "claim_r9", "wrong_gap_rounding",
}
fault = ""
if len(argv) > 2 or (len(argv) == 2 and not argv[1].startswith("sabotage=")):
    raise SystemExit("usage: finite_3x4_s3_highr_check.py [sabotage=NAME]")
if len(argv) == 2:
    fault = argv[1][9:]
    if fault not in CONTROLS:
        raise SystemExit("unknown sabotage")

def check(statement, label):
    if not statement:
        print("FAIL|" + label + "|json=0")
        raise SystemExit(1)

def emit(label, **fields):
    print(label + "|" + "|".join(str(k) + "=" + str(v)
          for k, v in fields.items()) + "|json=0")

group = tuple(permutations(range(3)))
ids = {g: i for i, g in enumerate(group)}
def mul(a, b):
    return ids[tuple(group[a][group[b][i]] for i in range(3))]
inverses = tuple(next(b for b in range(6) if mul(a,b)==mul(b,a)==0)
                 for a in range(6))
transpositions = tuple(i for i in range(1,6) if mul(i,i)==0)
if fault == "missing_transposition":
    transpositions = transpositions[:-1]
check(len(transpositions)==3, "transposition_census")
def conjugate(g,a):
    return mul(mul(g,a),inverses[g])

pairs = [(a,b) for a in range(6) for b in range(6)
         if mul(a,b)==mul(b,a)]
reps=[]
class_of={}
for a,b in pairs:
    if (a,b) in class_of:
        continue
    index = len(reps)
    orbit = {(conjugate(g,a),conjugate(g,b)) for g in range(6)}
    reps.append((a,b))
    for x in orbit:
        class_of[x] = index
if fault=="wrong_orbit_census":
    pairs=pairs[:-1]
check(len(pairs)==18 and len(reps)==8 and len(class_of)==18,
      "eight_flat_conjugacy_orbits")

# Three-step bridge: 4 transverse positions * 3! orderings / (4*4).
# Classification can independently be checked with exhaustive
# first-shell gauge-fixed enumerator in the accompanying local audit.
bridge = F(4*6,4*4)
if fault=="wrong_pair_amplitude":
    bridge = F(4*6,4*3)
check(bridge==F(3,2), "three_move_coefficient")
C=[[F(0) for _ in range(8)] for _ in range(8)]
for i,(a,b) in enumerate(reps):
    for t in transpositions:
        bt=mul(t,b)
        if mul(a,bt)==mul(bt,a):
            C[i][class_of[(a,bt)]]+=bridge
if fault=="wrong_cross_class":
    C[0][3]+=bridge
expected=[[F(0) for _ in range(8)] for _ in range(8)]
for i,j,val in ((0,1,F(9,2)),(1,0,F(3,2)),(1,2,F(3)),
                (2,1,F(9,2)),(3,4,F(3,2)),(4,3,F(3,2))):
    expected[i][j]=val
check(C==expected, "exact_first_nontrivial_8x8")

# Explicit eight independent rational eigenvectors, no eigensolver.
eigen=[]
for mu,v in ((F(9,2),(1,1,1)),(F(-9,2),(-1,1,-1)),
             (F(0),(-2,0,1))):
    eigen.append((mu,tuple(map(F,v))+(F(0),)*5))
for mu,v in ((F(3,2),(1,1)),(F(-3,2),(1,-1))):
    eigen.append((mu,(F(0),)*3+tuple(map(F,v))+(F(0),)*3))
for j in (5,6,7):
    eigen.append((F(0),tuple(F(int(k==j)) for k in range(8))))
check(all(all(sum(C[i][j]*v[j] for j in range(8))==mu*v[i]
              for i in range(8)) for mu,v in eigen),
      "independent_exact_eigenvectors")
mu1,mu2=F(9,2),F(3,2)
if fault=="wrong_eigenvalues":
    mu2=mu1
check(mu1-mu2==3, "first_vs_second_coefficient")

emit("FINITE34_CLASSES", gauge_group="S3", spatial_lattice="3x4",
     flat_orbits=8, commuting_pairs=18, positive_links=24)
emit("FINITE34_SCHUR", flat_energy=72, BBstar=72, C0="18I8",
     C1_spectrum="9/2,3/2,0,0,0,0,-3/2,-9/2")

# The analytic condition M_Q>=3 follows from Z2 sign parity of
# plaquettes on a periodic 2-torus; every transposition plaquette
# contributes 2 and appears in even count, a 3cycle contributes 3.
r=100000
m_min=3
flat_norm=72
if fault=="wrong_flat_norm":
    flat_norm=71
if fault=="wrong_magnetic_min":
    m_min=2
check(m_min==3 and flat_norm==72, "global_norm_and_parity")
d=m_min*r
check(d>72, "positive_resolvent")
eta=F(72**2,(d-72)**3)+F(72**3,d*d*(d-72))
if fault=="omit_remainder":
    eta=F(0)
check(eta>0 and eta==F(72**2,(d-72)**3)+F(72**3,d*d*(d-72)),
      "nonzero_schur_remainder")
tau1=F(72)-F(18,r)-mu1/F(r*r)
tau2=F(72)-F(18,r)-mu2/F(r*r)
lower=tau2-tau1-2*eta
upper=tau2-tau1+2*eta
if fault=="claim_r9":
    check(3*9>72, "invalid_r9_expansion")
check(lower>0 and upper>lower, "strict_first_gap")
scale=10**15
def floor_scaled(x):
    z=x*scale
    return z.numerator//z.denominator
def ceil_scaled(x):
    z=-x*scale
    return -(z.numerator//z.denominator)
low,high=floor_scaled(lower),ceil_scaled(upper)
if fault=="wrong_gap_rounding":
    low+=1
check(F(low,scale)<=lower and upper<=F(high,scale),
      "outward_exact_rational")
check((low,high)==(271961,328039), "replay_values")

r0=10000
d0=3*r0
eta0=F(72**2,(d0-72)**3)+F(72**3,d0*d0*(d0-72))
check(F(3,r0*r0)>2*eta0, "uniform_r_ge_10000")
# For r>24, r^2 eta(r) is decreasing by inspection of each term.
emit("FINITE34_GAP", r=r, J_E="units", lower=f"{low}/{scale}",
     upper=f"{high}/{scale}", all_r_ge_10000="POSITIVE")
emit("FINITE34_REMAINDER", numerator=eta.numerator, denominator=eta.denominator,
     min_nonflat_M=3, large_store="NOT_USED")
emit("FINITE34_SCOPE", first_gap="FINITE_S3_ONLY", first_gap_r9="OPEN",
     E1_winding_overlap="OPEN", continuum_SU2_4D="OPEN")
