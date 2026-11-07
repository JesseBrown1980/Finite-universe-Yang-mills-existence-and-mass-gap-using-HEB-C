#!/usr/bin/env python3
"""Exact two-dimensional full S3 2x2 winding parity and first-weight verifier.
No float, no JSON, no external numerical packages. Permutation matrix comes
from independent/gpt6_2x2_from_permutations.py and its fixed SHA256.
The C++ verifier counts parity-resolved eigenvalues separately.
"""
from collections import Counter
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import runpy
import sys

HERE=Path(__file__).resolve()
ROOT=HERE.parents[4]
source=ROOT.joinpath("independent/gpt6_2x2_from_permutations.py")
if len(sys.argv)!=2:raise SystemExit("usage: exact_selection_2x2.py MATRIX_OUTPUT_DIR")
args=sys.argv
try:
    sys.argv=[str(source)]
    with redirect_stdout(StringIO()):
        model=runpy.run_path(str(source))
finally:
    sys.argv=args

keys=model["keys"]; electric=model["rows"]; weights=model["W"]
magnetic=model["mag"]; pos=model["pos"];fixed=model["fixed"]
expand=model["expand"];decode=model["decode"];number=model["number"]
mul=model["multiply"];chi=model["chi"]

assert len(keys)==1393 and sum(weights.values())==7776
W=[weights[k] for k in keys]
H=[]
for i,row in enumerate(electric):
    r=row.copy()
    r[i]=r.get(i,0)+magnetic[i]
    H.append({j:v for j,v in r.items() if v})

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
    S.append(pos[number(fixed(swap(u)))])
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
     swap_commutes_with_H="EXACT",winding_plus_even="EXACT",
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
z=u
for _ in range(230):z=mv(z)
response=dot(u,z)
# If the winding sum were dark to E1, its even spectral support,
# apart from ground leakage ≤1e-80, would start above E3≥13.6.
# All H eigenvalues are in [0,60] by positive Laplacian+M and Gershgorin.
# Use the strictly conservative upper bound K_1≤60-13.24=1169/25.
# The rest of the even excited spectrum satisfies K≤60-13.6=1160/25.
numerator=25**230*response*10**80-nu*(1160**230*10**80+25**230*60**230)
denominator=nu*10**80*(1169**230-1160**230)
assert denominator>0 and numerator>0
emit("SELECTION_FIRST_WEIGHT",parity="EVEN",K_power=230,
     Perron_steps=850,ground_angle_sq_lt="1e-80",
     first_relative_spectral_weight_lower_gt_zero="EXACT",
     independent_spectral_counts="REQUIRED_IN_GMP_JOB",
     witness_numerator_sha256=hashlib.sha256(str(numerator).encode()).hexdigest(),
     witness_denominator_sha256=hashlib.sha256(str(denominator).encode()).hexdigest())
emit("SELECTION_READY",conditional_on_inertia="E0_E1_EVEN_E2_ODD",
     first_gap_winding_plus="NONZERO_CERTIFIED_WHEN_GMP_COUNTS_PASS",
     winding_minus_first_gap="ZERO_EXACT",continuum="OPEN")
