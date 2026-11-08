#!/usr/bin/env python3
"""Finite 3x4 S3 true first gap at JB/JE=9, integer Feshbach certificate.

Build the 8 magnetic-flat gauge orbits, every orbit through two electric
moves (8042 total), and EVERY one-step exterior residual target (147344).
Four deterministic integer Jacobi steps generate a trial Q-resolvent on K2.
The exactly recomputed full-space residual and the previously accepted
94.070673 JE nonflat Perron floor sandwich the complete 8x8 Schur matrix.
All computations in this file are integer-only; no floating point, SciPy,
fractions, matrix-store download, JSON or undocumented spectral reduction.

This new certificate remains CONDITIONAL on the original 3x4 Perron source's
full-space positive-vector lift and archived whole-store verification.
"""
from collections import Counter
from hashlib import sha1,sha256
from itertools import permutations
from pathlib import Path
import sys

SCALE=1000000000
STEPS=4
PERRON_SCALE=1000000
LEVELS=((6989,0,0),(6992,1,1),(6993,1,1),(6996,6,2))
FAULTS=("wrong_flat_census","wrong_first_shell","omit_exterior",
        "wrong_source_floor","wrong_inertia","wrong_gram_weight",
        "ritz_floor_94121950","ritz_floor_96756025",
        "drop_exterior_edge","omit_residual_coupling","schur_sign_flip")
fault=""
if len(sys.argv)>2 or (len(sys.argv)==2 and
    (not sys.argv[1].startswith("sabotage=") or sys.argv[1][9:] not in FAULTS)):
    raise SystemExit("usage: finite_s3_3x4_r9_first_gap.py [sabotage=NAME]")
if len(sys.argv)==2:fault=sys.argv[1][9:]

def check(t,label):
    if not t:
        print("FAILED|check="+label+"|json=0",flush=True)
        raise SystemExit(1)
def emit(label,**fields):
    print(label+"|"+"|".join(str(k)+"="+str(v) for k,v in fields.items())
          +"|json=0",flush=True)

G=tuple(permutations(range(3)))
INDEX={a:i for i,a in enumerate(G)}
MUL=tuple(tuple(INDEX[tuple(G[a][G[b][i]] for i in range(3))]
                for b in range(6)) for a in range(6))
INV=tuple(next(b for b in range(6) if MUL[a][b]==MUL[b][a]==0)
          for a in range(6))
TRANS=tuple(i for i in range(1,6) if MUL[i][i]==0)
CHAR=tuple(sum(int(G[a][j]==j) for j in range(3))-1 for a in range(6))
CONJ=tuple(tuple(MUL[MUL[g][a]][INV[g]] for a in range(6))
           for g in range(6))
LX=3
LY=4
V=LX*LY
def pos(x,y):
    return (x%LX)*LY+(y%LY)

TREE=[(pos(0,y),pos(0,y+1),V+pos(0,y)) for y in range(LY-1)]
TREE += [(pos(x,y),pos(x+1,y),pos(x,y))
         for y in range(LY) for x in range(LX-1)]
TREE_IDS={k for u,v,k in TREE}
KEPT=tuple(k for k in range(2*V) if k not in TREE_IDS)
check(len(KEPT)==13 and len(TREE)==11 and len(TRANS)==3,
      "S3_tree_and_electric_generators")

def from_key(key):
    U=[0]*(2*V)
    for k,a in zip(KEPT,key):
        U[k]=a
    return U

def canonical(U):
    h=[0]*V
    for u,v,k in TREE:
        h[v]=MUL[h[u]][U[k]]
    z=[0]*(2*V)
    for x in range(LX):
        for y in range(LY):
            s=pos(x,y)
            z[s]=MUL[MUL[h[s]][U[s]]][INV[h[pos(x+1,y)]]]
            z[V+s]=MUL[MUL[h[s]][U[V+s]]][INV[h[pos(x,y+1)]]]
    check(all(z[k]==0 for k in TREE_IDS),"canonical_tree")
    key=tuple(z[k] for k in KEPT)
    return min(tuple(CONJ[g][a] for a in key) for g in range(6))

def weight(key):
    return len({tuple(CONJ[g][a] for a in key) for g in range(6)})

def magnetic(U):
    s=0
    for x in range(LX):
        for y in range(LY):
            i=pos(x,y);right=pos(x+1,y);up=pos(x,y+1)
            p=MUL[MUL[MUL[U[i]][U[V+right]]][INV[U[up]]]][INV[U[V+i]]]
            s+=2-CHAR[p]
    return s

def neighbors(key):
    U=from_key(key)
    count=Counter()
    for k in range(2*V):
        old=U[k]
        for t in TRANS:
            U[k]=MUL[t][old]
            count[canonical(U)]+=1
        U[k]=old
    check(sum(count.values())==72,"electric_72_moves")
    return count

def source_floor():
    path=Path(__file__).resolve().parents[1] / (
         "native/ym/results/3x4_stream/perron/PERRON-RESULT.hbp")
    raw=path.read_bytes()
    git_blob=b"blob "+str(len(raw)).encode()+bytes((0,))+raw
    check(sha1(git_blob).hexdigest()=="cbd428014a4d440732a5c0a541ed57a9041becee",
          "historical_Perron_Git_blob_pin")
    lines=raw.decode("utf-8").splitlines()
    tops=[s for s in lines if s.startswith("RESULT_PERRON_3x4_TOP|")]
    check(len(tops)==1 and "t_cert_milli=94070673|" in tops[0]
          and "outside_go_checker=94070673|" in tops[0]
          and "min_row=45507968|" in tops[0],
          "original_Perron_floor_three_checkers")
    check(any("gap_verdict=OPEN|" in s for s in lines)
          and any(s.startswith("RESULT_KEY_TABLE|") for s in lines),
          "historical_verdict_and_whole_census_retained")
    entries=dict(item.split("=",1) for item in tops[0].split("|")[1:] if "=" in item)
    source_num=int(entries["t_cert_milli"])
    check(source_num==int(entries["perroncert_check"])
          ==int(entries["check_d_strict"])
          ==int(entries["outside_go_checker"])==94070673,
          "pinned_matching_numerical_compression_floor")
    # PERRON-BOUND.md section 2 bounds lambda_min(QHQ), NOT merely E9.
    return "PINNED_CONDITIONAL_WHOLE_ORBIT_LIFT",source_num

def graph():
    flat={}
    for a in range(6):
        for b in range(6):
            if MUL[a][b]!=MUL[b][a]:continue
            U=[0]*(2*V)
            for y in range(LY):U[pos(LX-1,y)]=a
            for x in range(LX):U[V+pos(x,LY-1)]=b
            check(magnetic(U)==0,"flat_commuting_torus")
            flat[canonical(U)]=(a,b)
    if fault=="wrong_flat_census":
        flat.pop(next(iter(flat)))
    check(len(flat)==8 and sum(weight(k) for k in flat)==18,
          "all_eight_flat_orbits")
    layers=[sorted(flat)]
    seen=set(layers[0])
    for _ in range(2):
        new=set()
        for key in layers[-1]:
            new.update(neighbors(key))
        new.difference_update(seen)
        seen.update(new)
        layers.append(sorted(new))
    if fault=="wrong_first_shell":
        layers[1].pop()
    check(len(layers[1])==264 and len(layers[2])==7770,
          "complete_two_move_gauge_orbits")
    states=[key for layer in layers for key in layer]
    where={k:i for i,k in enumerate(states)}
    w=[weight(k) for k in states]
    m=[magnetic(from_key(k)) for k in states]
    check(len(states)==8042 and m[:8]==[0]*8
          and set(m[8:272])=={4},"flat_and_first_shell_potential")
    # Build all Q-Q, Q-P and Q->outside transitions from the
    # actual canonical S3 Hamiltonian definition, not an Sx+Sy+ proxy.
    adj=[]
    q_flat=[]
    outside={}
    first=[neighbors(k) for k in layers[0]]
    for i,key in enumerate(states):
        near=neighbors(key)
        ins=[]
        toflat=[0]*8
        for dst,c in near.items():
            j=where.get(dst)
            if j is None:
                check(i>=8,"flat_to_outside_forbidden")
                outside.setdefault(dst,[]).append((i-8,w[i]*c))
            elif j<8:
                check(i>=8,"flat_to_flat_forbidden")
                toflat[j]+=c
            else:
                if i>=8:ins.append((j-8,c))
        if i>=8:
            adj.append(ins)
            q_flat.append(toflat)
    if fault=="omit_exterior":
        outside.pop(next(iter(outside)))
    check(len(outside)==147344,"complete_one_step_residual_support")
    for i, row in enumerate(adj):
        for j,c in row:
            check(w[8+i]*c==w[8+j]*dict(adj[j]).get(i,0),
                  "weighted_Q_Q_electric_adjoint")
    # Independent P-Q detailed-balance identity.
    for i,row in enumerate(q_flat):
        for j,c in enumerate(row):
            check(w[8+i]*c==w[j]*first[j].get(states[8+i],0),
                  "weighted_P_Q_electric_adjoint")
    outer=[(weight(k),edges) for k,edges in outside.items()]
    check(all(W in (1,2,3,6) for W,_ in outer),"outer_orbit_weights")
    # Mutate an actual exterior electric coefficient without changing census.
    if fault=="drop_exterior_edge":
        W,edges=outer[0]
        outer[0]=(W,edges[1:])
    # Burnside count of simultaneous conjugacy classes of S3^13.
    full_dim=(6**13+3*2**13+2*3**13)//6
    nflat=len(layers[0]); nfirst=len(layers[1]); nsecond=len(layers[2])
    census_count=len(states); nouter=len(outer)
    flat_weight=sum(weight(k) for k in flat)
    check(full_dim==2177317873 and census_count==nflat+nfirst+nsecond
          and flat_weight==18,"computed_full_and_flat_census")
    emit("S3_3X4_CENSUS",flat=nflat,shell1=nfirst,shell2=nsecond,
         total_K2=census_count,exterior_residual_states=nouter,
         flat_raw_commuting=flat_weight,orbit_dimension_full=full_dim)
    return w,m,adj,q_flat,outer

def det(A):
    n=len(A)
    if n==0:return 1
    B=[row[:] for row in A]
    last=1
    sign=1
    for k in range(n-1):
        if B[k][k]==0:
            p=next((j for j in range(k+1,n) if B[j][k]),None)
            if p is None:return 0
            B[k],B[p]=B[p],B[k]
            sign=-sign
        pivot=B[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                t=B[i][j]*pivot-B[i][k]*B[k][j]
                check(t%last==0,"integer_Bareiss_division")
                B[i][j]=t//last
        for i in range(k+1,n):B[i][k]=0
        last=pivot
    return sign*B[-1][-1]

def inertia(A):
    check(all(A[i][j]==A[j][i] for i in range(8) for j in range(8)),
          "Schur_exact_symmetry")
    neg=0
    previous=1
    for n in range(1,9):
        D=det([row[:n] for row in A[:n]])
        check(D!=0,"nonzero_Sylvester_pivots")
        neg+=int((D<0)!=(previous<0))
        previous=D
    return neg

def add_gram(G,R,w):
    check(w in (1,2,3,6),"weight_divides_six")
    fac=6//w
    if fault=="wrong_gram_weight" and w!=1:
        fac=6
    for i in range(8):
        s=fac*R[i]
        if s:
            for j in range(i,8):G[i][j]+=s*R[j]

def threshold(a,w,m,adj,q_flat,outer,source_floor_num):
    b=100
    n=len(adj)
    # Deterministic integer-only trial inverse with 4 parallel Jacobi
    # iterations; accuracy is NOT assumed, only the exact residual matters.
    diag=[b*(72+9*m[8+i]-dict(adj[i]).get(i,0))-a for i in range(n)]
    check(min(diag)>0,"positive_Q_Jacobi_diagonal")
    off=[[(j,c) for j,c in row if j!=i] for i,row in enumerate(adj)]
    F=[[-b*c for c in row] for row in q_flat]
    X=[[0]*8 for _ in range(n)]
    for _ in range(STEPS):
        Y=[]
        for i in range(n):
            s=[SCALE*F[i][k] for k in range(8)]
            for j,c in off[i]:
                y=X[j]
                for k in range(8):s[k]+=b*c*y[k]
            Y.append([v//diag[i] for v in s])
        X=Y
    Ri=[]
    for i in range(n):
        s=[SCALE*F[i][k]-diag[i]*X[i][k] for k in range(8)]
        for j,c in off[i]:
            y=X[j]
            for k in range(8):s[k]+=b*c*y[k]
        Ri.append([w[8+i]*v for v in s])
    if fault=="omit_residual_coupling":
        Ri[0][0]=0
    G=[[0]*8 for _ in range(8)]
    for i,R in enumerate(Ri):add_gram(G,R,w[8+i])
    # Because X is identically zero outside K2, this is the COMPLETE
    # exterior residual; no 2.17B inverse is approximated silently.
    for W,edges in outer:
        R=[0]*8
        for i,c in edges:
            y=X[i]
            for k in range(8):R[k]+=b*c*y[k]
        add_gram(G,R,W)
    for i in range(8):
        for j in range(i):G[i][j]=G[j][i]
    U=[[0]*8 for _ in range(8)]
    for k in range(8):
        U[k][k]=SCALE*SCALE*w[k]*(b*72-a)
    for i in range(n):
        wi=w[8+i];f=F[i];x=X[i];r=Ri[i]
        for k in range(8):
            fk=SCALE*wi*f[k]
            xk=x[k]
            for j in range(8):
                U[k][j]-=fk*x[j]+xk*r[j]
    if fault=="schur_sign_flip":
        U[0][0]=-U[0][0]
    check(all(U[i][j]==U[j][i] for i in range(8) for j in range(8)),
          "exact_symmetric_trial")
    floor_num=source_floor_num
    if fault=="wrong_source_floor":
        floor_num+=1
    if fault=="ritz_floor_94121950":
        floor_num=94121950
    if fault=="ritz_floor_96756025":
        floor_num=96756025
    gamma_num=b*floor_num-a*PERRON_SCALE
    check(gamma_num>0,"nonflat_Perron_resolvent_floor")
    L=[[6*gamma_num*U[i][j]-PERRON_SCALE*G[i][j]
         for j in range(8)] for i in range(8)]
    if fault=="wrong_inertia" and a==6993:
        L[0][0]+=SCALE*SCALE*SCALE
    nlo=inertia(L)
    nhi=inertia(U)
    hu=sha256("|".join(str(z) for row in U for z in row).encode()).hexdigest()
    hg=sha256("|".join(str(z) for row in G for z in row).encode()).hexdigest()
    hl=sha256("|".join(str(z) for row in L for z in row).encode()).hexdigest()
    emit("S3_3X4_THRESHOLD",threshold=str(a)+"/100",
         lower_inertia=nlo,upper_inertia=nhi,
         perron_floor_num=floor_num,lower_witness_sha256=hl,
         schur_trial_sha256=hu,residual_gram_sha256=hg)
    return nlo,nhi,hu,hg,hl

def main():
    check(len(sys.argv)==1 or fault in FAULTS,"recognized_cli_only")
    src,floor_num=source_floor()
    emit("S3_3X4_BEGIN",status="SOURCE_CONDITIONAL",gauge_group="S3",r=9,
         operator="FULL_GAUGE_ORBIT_HAMILTONIAN",
         source_floor=src,compression_floor_num=floor_num,
         jacobi_integer_steps=STEPS)
    w,m,adj,qflat,outer=graph()
    got=[]
    for a,lo,hi in LEVELS:
        outcome=threshold(a,w,m,adj,qflat,outer,floor_num)
        check(outcome[:2]==(lo,hi),"frozen_full_space_one_sided_counts")
        got.append(outcome[:2])
    check(got==[(0,0),(1,1),(1,1),(6,2)],"four_threshold_composition")
    emit("S3_3X4_FIRST_GAP",
         E1_interval="(6989/100,6992/100)",
         E2_interval="(6993/100,6996/100)",
         first_gap_interval="(1/100,7/100)",
         bound_basis="FULL_EIGHT_FLAT_SCHUR_AND_ONE_SIDED_INERTIA",
         status="PASS_EXACT_MATH_CONDITIONAL_SOURCE")
    emit("S3_3X4_SCOPE",original_Perron_store_rerun="NO",
         accepted_source_assumption="lambda_min_QHQ_whole_GE_94070673/1000000",
         first_state_winding_overlap="OPEN",
         spatial_SU2_continuum="NOT_PROVED")

if __name__=="__main__":main()
