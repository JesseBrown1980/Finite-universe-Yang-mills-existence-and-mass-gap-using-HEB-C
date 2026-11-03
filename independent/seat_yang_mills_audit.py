#!/usr/bin/env python3
"""Independent finite S3 torus orbit/operator audit (no third-party packages).

Inputs: ONLY published mathematical model geometry and S3 permutation action.
Does not invoke Rust, its orbit enumeration, or its certificate verifier.
The expected fingerprint is used exclusively as a final comparison.
Run: python3 seat_yang_mills_audit.py
"""
from itertools import permutations
from collections import Counter, deque
from hashlib import sha256
from math import prod

G=list(permutations(range(3)))
assert len(G)==6 and G[0]==(0,1,2)
ids={p:i for i,p in enumerate(G)}
M=[[ids[tuple(g[h[x]] for x in range(3))] for h in G] for g in G]
INV=[next(y for y in range(6) if M[x][y]==0 and M[y][x]==0) for x in range(6)]
def op(a,b):return M[a][b]
def conj(a,b):return op(op(a,b),INV[a])
def enc(q):return sum(x*(6**j) for j,x in enumerate(q))
def dec(k):return tuple((k//(6**j))%6 for j in range(5))
def orbit(q):return {tuple(conj(g,x) for x in q) for g in range(6)}
def can(q):return min(orbit(q),key=enc)

# Independent Burnside check: (1/6) sum over g of |centralizer(g)|^5.
cent=[sum(op(g,h)==op(h,g) for h in range(6)) for g in range(6)]
burnside=sum(c**5 for c in cent)//6
assert sum(c**5 for c in cent)%6==0

# Classify orbits by a direct mathematical group-action orbit partition,
# rather than using the Rust canonical(decode(k)) histogram loop.
unseen=set(range(6**5)); classes=[]
while unseen:
    q=dec(min(unseen))
    members={enc(x) for x in orbit(q)}
    assert members.issubset(unseen)
    unseen.difference_update(members)
    classes.append((min(members),len(members)))
classes.sort()
keys=[k for k,w in classes]
weights=[w for k,w in classes]
idx={k:i for i,k in enumerate(keys)}
assert burnside==1393==len(keys)
assert sum(weights)==7776
assert set(weights).issubset({1,2,3,6})

# Actual 2x2 periodic graph, with eight directed links (x 0:4, y 4:8).
# Compute gauge-fix tree vertex frames by traversal of three tree edges.
edges=((0,2),(1,3),(2,0),(3,1),(0,1),(1,0),(2,3),(3,2))
tree=(0,1,4); free=(2,3,5,6,7)
def fix(U):
    v={0:0}
    for _ in range(3):
        for e in tree:
            a,b=edges[e]
            if a in v and b not in v:v[b]=op(v[a],U[e])
            if b in v and a not in v:v[a]=op(v[b],INV[U[e]])
    assert len(v)==4
    return tuple(op(op(v[edges[e][0]],U[e]),INV[v[edges[e][1]]]) for e in free)
def rep(q):
    U=[0]*8
    for e,g in zip(free,q):U[e]=g
    return U

def char(g):return 2 if g==0 else (-1 if g in (3,4) else 0)
def vertex(x,y):return ((x%2)*2+(y%2))
def magnetic(U):
    accum=0
    for x in range(2):
        for y in range(2):
            a=vertex(x,y);right=vertex(x+1,y);above=vertex(x,y+1)
            p=op(op(op(U[a],U[4+right]),INV[U[above]]),INV[U[4+a]])
            accum+=2-char(p)
    return accum

def transform(U,site,g):
    ret=[]
    for val,(a,b) in zip(U,edges):
        if site==a:val=op(g,val)
        if site==b:val=op(val,INV[g])
        ret.append(val)
    return ret

TRANS=(1,2,5) # the three odd elements (transpositions) of S3
rowmaps=[];mag=[]; nnz=0; flat=0
for i,key in enumerate(keys):
    U=rep(dec(key))
    assert enc(can(fix(U)))==key
    m=magnetic(U); mag.append(m)
    if m==0:flat+=1
    # independent full local gauge invariance check on each representative
    for site in range(4):
        for g in range(6):
            Up=transform(U,site,g)
            assert enc(can(fix(Up)))==key
            assert magnetic(Up)==m
    row=Counter({i:24})
    for e in range(8):
        for t in TRANS:
            Up=U.copy();Up[e]=op(t,Up[e])
            j=idx[enc(can(fix(Up)))]
            row[j]-=1
    row={j:z for j,z in row.items() if z}
    assert sum(row.values())==0
    assert all((z<0 if j!=i else True) for j,z in row.items())
    nnz+=len(row)
    rowmaps.append(row)
assert flat==8
assert nnz==32385
for i,row in enumerate(rowmaps):
    for j,z in row.items():
        assert weights[i]*z==weights[j]*rowmaps[j].get(i,0)

# Connectivity, pure-electric Wilson mode (lambda 6) and flat count.
seen={0};queue=deque([0])
while queue:
    i=queue.popleft()
    for j,z in rowmaps[i].items():
        if i!=j and z<0 and j not in seen:
            seen.add(j);queue.append(j)
assert len(seen)==1393
wilson=[char(op(rep(dec(k))[0],rep(dec(k))[2])) for k in keys]
assert sum(weights[i]*wilson[i] for i in range(len(keys)))==0
assert all(sum(z*wilson[j] for j,z in row.items())==6*wilson[i] for i,row in enumerate(rowmaps))

# Serialize the mathematically reconstructed operator per the published
# byte-order contract, then compare digest against the native result.
data=bytearray(b'HEBC-S3-TORUS2-1393-V1')
for i,key in enumerate(keys):
    data.extend(int(key).to_bytes(8,'little'))
    data.extend(int(weights[i]).to_bytes(8,'little'))
    data.extend(bytes(dec(key)))
    data.extend(int(mag[i]).to_bytes(8,'little',signed=True))
    data.extend(len(rowmaps[i]).to_bytes(8,'little'))
    for j,z in sorted(rowmaps[i].items()):
        data.extend(int(j).to_bytes(8,'little'))
        data.extend(int(z).to_bytes(8,'little',signed=True))
operator_sha=sha256(data).hexdigest()
expected='b6c608f50f81f3bf48fb0203b48e0e3bfc867037dc1d0a96633aa80b962137f3'
assert operator_sha==expected, (operator_sha, expected)

print('HEBC-SEAT-AUDIT|result=PASS|model=finite_periodic_2x2_S3|method=permutation_group_and_burnside|json=0')
print('HEBC-SEAT-AUDIT|burnside_orbits=%d|orbit_weights_sum=%d|nnz=%d|flat_orbits=%d|connected=1|gauge_samples=%d|json=0' % (burnside,sum(weights),nnz,flat,len(keys)*4*6))
print('HEBC-SEAT-AUDIT|electric_W_selfadjoint=PASS|row_sum_zero=PASS|wilson_gap6_eigenmode=PASS|json=0')
print('HEBC-SEAT-AUDIT|native_operator_sha_match=PASS|operator_sha=%s|json=0' % operator_sha)
print('HEBC-SEAT-AUDIT|scope=FINITE_S3_ONLY|continuum_YM_proven=0|independent_physical_attestation=0|json=0')

# Separate exact-arithmetic Collatz/Poincare witness replay.
# This is a check of Stage 2G's mathematical *method*, not a logically
# independent inequality or continuum theorem. Python integers do not overflow.
def apply(je,jb,v):
    return [je*sum(z*v[j] for j,z in row.items()) + jb*mag[i]*v[i]
            for i,row in enumerate(rowmaps)]
for je,jb in [(1,1),(3,5)]:
    largest=max(je*rowmaps[i].get(i,0)+jb*mag[i] for i in range(len(keys)))
    shift=largest+1
    scale=10**12
    v=[scale]*len(keys)
    for iteration in range(256):
        hv=apply(je,jb,v)
        mv=[shift*vi-hi for vi,hi in zip(v,hv)]
        assert min(mv)>0
        m=max(mv)
        v=[(x*scale+m//2)//m for x in mv]
        assert min(v)>0
    hv=apply(je,jb,v)
    den=10**6
    lo=min(h*den//x for h,x in zip(hv,v))
    up=max(-((-h*den)//x) for h,x in zip(hv,v))
    delta=6*je*min(v)**2*den//max(v)**2
    gap_lower=delta-(up-lo)
    assert gap_lower>0
    expected={(1,1):(7634198,7634199),(3,5):(36699227,36699228)}[(je,jb)]
    assert (lo,up)==expected,((je,jb),lo,up,expected)
    print(f'HEBC-SEAT-AUDIT|JE={je}|JB={jb}|E0=[{lo},{up}]/{den}|positive_gap_lower_by_Poincare={gap_lower}/{den}|method=COLLATZ_POINCARE_REPLAY|json=0')
print('HEBC-SEAT-AUDIT|NOTE=rank_one_cholesky_E1_intervals_NOT_independently_reproved|json=0')
