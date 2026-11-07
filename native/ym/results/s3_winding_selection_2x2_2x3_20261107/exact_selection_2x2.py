#!/usr/bin/env python3
"""Exact two-dimensional full S3 2x2 winding parity and first-weight verifier.
No float, no JSON, no external numerical packages. Permutation matrix comes
from independent/gpt6_2x2_from_permutations.py and its fixed SHA256.
The C++ verifier counts parity-resolved eigenvalues separately.
"""
from collections import Counter
from itertools import permutations, product
from pathlib import Path
import hashlib
import sys
sys.set_int_max_str_digits(0)
if len(sys.argv)!=2:raise SystemExit("usage: exact_selection_2x2.py MATRIX_OUTPUT_DIR")
args=sys.argv
P=tuple(permutations(range(3)))
IX={p:i for i,p in enumerate(P)}
C=tuple(tuple(IX[tuple(P[a][P[b][k]] for k in range(3))]
              for b in range(6)) for a in range(6))
INV=tuple(next(b for b in range(6) if C[a][b]==C[b][a]==0) for a in range(6))
TRANS=tuple(i for i in range(6) if C[i][i]==0 and i)
EDGE=((0,2),(1,3),(2,0),(3,1),(0,1),(1,0),(2,3),(3,2))
TREE=(0,1,4);FREE=(2,3,5,6,7)
def mul(*values):
    z=0
    for value in values:z=C[z][value]
    return z
def number(q):return sum(x*6**i for i,x in enumerate(q))
def decode(code):return tuple(code//6**i%6 for i in range(5))
def canonical(q):
    return min(number(tuple(mul(c,x,INV[c]) for x in q)) for c in range(6))
def expand(q):
    u=[0]*8
    for i,x in zip(FREE,q):u[i]=x
    return u
def fixed(u):
    f=[None]*4;f[0]=0
    for _ in range(3):
        for e in TREE:
            a,b=EDGE[e]
            if f[a] is not None and f[b] is None:f[b]=C[f[a]][u[e]]
            if f[b] is not None and f[a] is None:f[a]=C[f[b]][INV[u[e]]]
    assert all(x is not None for x in f)
    return canonical(tuple(mul(f[EDGE[i][0]],u[i],INV[f[EDGE[i][1]]]) for i in FREE))
def chi(x):return 2 if x==0 else 0 if x in TRANS else -1
def plaquette_energy(u):
    total=0
    for x,y in product(range(2),repeat=2):
        at=2*x+y;right=2*((x+1)%2)+y;up=2*x+(y+1)%2
        g=mul(u[at],u[4+right],INV[u[up]],INV[u[4+at]])
        total+=2-chi(g)
    return total

counts=Counter(canonical(q) for q in product(range(6),repeat=5))
keys=sorted(counts)
assert len(keys)==1393 and sum(counts.values())==7776
pos={key:i for i,key in enumerate(keys)}
W=[counts[k] for k in keys]
magnetic=[];electric=[];H=[]
for i,key in enumerate(keys):
    u=expand(decode(key))
    magnetic.append(plaquette_energy(u))
    row=Counter({i:24})
    for e in range(8):
        for t in TRANS:
            v=u.copy();v[e]=C[t][u[e]]
            row[pos[fixed(v)]]-=1
    r={j:z for j,z in row.items() if z}
    electric.append(r)
    total=r.copy()
    total[i]=total.get(i,0)+magnetic[i]
    H.append({j:z for j,z in total.items() if z})
assert sum(len(row) for row in electric)==32385
assert all(sum(row.values())==0 for row in electric)

# Independent SHA anchor for the canonical 1393-state native operator.
payload=bytearray(b"HEBC-S3-TORUS2-1393-V1")
for i,key in enumerate(keys):
    payload.extend(key.to_bytes(8,"little"))
    payload.extend(W[i].to_bytes(8,"little"))
    payload.extend(bytes(decode(key)))
    payload.extend(magnetic[i].to_bytes(8,"little",signed=True))
    payload.extend(len(electric[i]).to_bytes(8,"little"))
    for j,value in sorted(electric[i].items()):
        payload.extend(j.to_bytes(8,"little"))
        payload.extend(value.to_bytes(8,"little",signed=True))
operator_sha=hashlib.sha256(payload).hexdigest()
assert operator_sha=="b6c608f50f81f3bf48fb0203b48e0e3bfc867037dc1d0a96633aa80b962137f3"

def swap(u):
    v=[0]*8
    for x in range(2):
        for y in range(2):
            a=2*x+y;b=2*y+x
            v[b]=u[4+a];v[4+b]=u[a]
    return v

S=[];op=[];om=[]
for code in keys:
    u=expand(decode(code))
    S.append(pos[fixed(swap(u))])
    a=chi(mul(u[0],u[2]))
    b=chi(mul(u[4],u[5]))
    op.append(a+b)
    om.append(a-b)
assert all(S[S[i]]==i and W[S[i]]==W[i] for i in range(1393))
assert all(op[S[i]]==op[i] and om[S[i]]==-om[i] for i in range(1393))
assert all(H[S[i]].get(S[j],0)==z and W[i]*z==W[j]*H[j].get(i,0)
           for i,row in enumerate(H) for j,z in row.items())
assert sum(len(row) for row in electric)==32385

def project(odd):
    pairs=[];index={};w=[]
    for i in range(1393):
        j=S[i]
        if i>j or (odd and i==j):continue
        p=len(pairs)
        pairs.append((i,j))
        w.append(W[i]*(2 if i!=j else 1))
        index[i]=(p,1)
        if j!=i:index[j]=(p,-1 if odd else 1)
    rows=[]
    for i,_ in pairs:
        row=Counter()
        for j,z in H[i].items():
            if j in index:
                k,sign=index[j];row[k]+=sign*z
        rows.append({j:z for j,z in row.items() if z})
    assert all(w[i]*z==w[j]*rows[j].get(i,0)
               for i,row in enumerate(rows) for j,z in row.items())
    return w,rows

def emit(name,**fields):
    print(name+"|"+"|".join(str(k)+"="+str(v) for k,v in fields.items())+"|json=0",flush=True)

out=Path(args[1]);out.mkdir(parents=True,exist_ok=True)
dims=[]
for odd in (False,True):
    w,rows=project(odd)
    path=out.joinpath("odd.matrix" if odd else "even.matrix")
    with path.open("w") as f:
        f.write(str(len(w))+"\n")
        f.write(" ".join(map(str,w))+"\n")
        f.write(" ".join("0" for _ in w)+"\n")
        for i,row in enumerate(rows):
            for j,z in sorted(row.items()):
                if j>=i:f.write(str(i)+" "+str(j)+" "+str(z)+"\n")
    import hashlib
    emit("SELECTION_BLOCK",parity="ODD" if odd else "EVEN",
         dim=len(w),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
         weighted_self_adjoint="EXACT")
    dims.append(len(w))
assert dims==[746,647]
emit("SELECTION_GEOMETRY",full_dim=1393,even_dim=746,odd_dim=647,
     swap_commutes_with_H="EXACT",operator_sha256=operator_sha,winding_plus_even="EXACT",
     winding_minus_odd="EXACT",winding_minus_E1="ZERO_IF_E1_EVEN")

# Certify positive first-gap overlap using an exact integer response bound:
# certify separately by GMP that N_even(13.24265)=2, N_odd(13.24265)=0
# and N_even(13.6)=2, N_odd(13.6)=1, and N_even(13.24)=1.
# Ground-state Perron angle is controlled by the full gap E1>13.24.
def mv(x):
    return [60*x[i]-sum(z*x[j] for j,z in row.items()) for i,row in enumerate(H)]
def hx(x):
    return [sum(z*x[j] for j,z in row.items()) for row in H]
def dot(x,y):
    return sum(W[i]*a*b for i,(a,b) in enumerate(zip(x,y)))
v=[1]*1393
for _ in range(850):v=mv(v)
assert all(v[i]>0 and v[S[i]]==v[i] for i in range(1393))
h=hx(v);norm=dot(v,v);mean=dot(v,h)
residual=sum(W[i]*(norm*h[i]-mean*v[i])**2 for i in range(1393))
diff=1324*norm-100*mean
assert diff>0
# sin(angle(v,true_ground))² <= res*100²/(norm*diff²) < 10^-80
assert 10000*10**80*residual<norm*diff*diff
a=dot(v,[op[i]*v[i] for i in range(1393)])
u=[norm*op[i]*v[i]-a*v[i] for i in range(1393)]
assert dot(v,u)==0 and all(u[S[i]]==u[i] for i in range(1393))
nu=dot(u,u)
# phi=v/sqrt(norm); mu=<phi,O_plus phi>; centered normalized response
# u_prime=(O_plus-mu)*phi = u/norm**(3/2). Its variance is
# V=||u_prime||_W^2=nu/norm**3. Certified lower bound V>=1.
variance_den=norm**3
assert nu>=variance_den, "CENTERED_WINDING_VARIANCE_BELOW_ONE"
z=u
for _ in range(230):z=mv(z)
response=dot(u,z)
# Explicit leakage correction in the hypothetical NULL E1 overlap case:
#
# psi=true normalized ground state, phi=850-step Perron approximant,
# delta=sin(angle(psi,phi))**2 < 10**(-80) (certified above).
# Choose phases so <psi,phi>>=0. Then ||psi-phi||^2<=2*delta.
# For the gauge-invariant O_plus, ||O_plus||<=4, |mu|<=4.
#
# If <E1,O_plus psi>=0, then
# |<E1,u_prime>| = |<E1,O_plus(phi-psi)-mu*phi>|
#               <= 8*||phi-psi||, so its squared weight <=128*delta.
# The ground-state leakage of u_prime has squared weight <=delta*V,
# because <phi,u_prime>=0 and phi/psi have sin^2 angle delta.
# Since V>=1, the *normalized* total low-energy weight <=129*delta.
# All remaining even modes begin at E3>=13.6 by the independent
# 746/647-dimensional exact GMP inertia certificate.
#
# For K=60I-H, 0<=K<=60. The resulting null-case response bound:
# F=<u,K^230 u>/<u,u>
#   <=(1160/25)^230 + 129*(60^230)/(10^80).
# A *strictly positive* integer excess refutes the E1-dark hypothesis.
leakage_units=129
numerator=25**230*response*10**80-nu*(1160**230*10**80
                                     +leakage_units*25**230*60**230)
denominator=nu*10**80*(1169**230-1160**230)
assert denominator>0 and numerator>0, "FIRST_E1_OVERLAP_NULL_NOT_REFUTED"
witness=hashlib.sha256(str(numerator).encode()).hexdigest()
# Pinned independent 850-iteration/230-response recomputation, reviewed
# before this correction and unrelated to the GMP inertia implementation.
assert witness=="2d5504cbc526c07d7264b3a055f3bee5550a1cf62dc4ce869f9e6670f8d8cc3f"
emit("SELECTION_LEAKAGE",centered_variance_lower="1",
     centered_variance_exact_gate="PASS",
     normalized_ground_leakage_delta=1,
     normalized_E1_leakage_delta_upper=128,
     total_low_mode_leakage_delta_upper=leakage_units,
     corrected_excess_positive="EXACT",
     corrected_excess_sha256=witness)
emit("SELECTION_FIRST_WEIGHT",parity="EVEN",K_power=230,
     Perron_steps=850,ground_angle_sq_lt="1e-80",
     first_relative_spectral_weight_lower_gt_zero="EXACT",
     independent_spectral_counts="REQUIRED_IN_GMP_JOB",
     conservative_leakage_multiplier=leakage_units,
     witness_numerator_sha256=witness,
     witness_denominator_sha256=hashlib.sha256(str(denominator).encode()).hexdigest())
emit("SELECTION_READY",conditional_on_inertia="E0_E1_EVEN_E2_ODD",
     first_gap_winding_plus="NONZERO_CERTIFIED_WHEN_GMP_COUNTS_PASS",
     winding_minus_first_gap="ZERO_EXACT",continuum="OPEN")
