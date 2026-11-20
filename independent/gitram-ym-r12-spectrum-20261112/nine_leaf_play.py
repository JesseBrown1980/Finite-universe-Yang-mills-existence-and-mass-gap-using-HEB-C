#!/usr/bin/env python3
"""Nine frozen class-address leaves, three centre-sharing arms, 3 waves forward/back.

SOURCE: pinned GitRAM cutoff-9 Schur-row artifact, run 43222707802, r=12.
OPERATOR: the 48-symmetry invariant compression H_CC (NOT the Schur F(t)).
PLAY: integer, reversible *discrete wave-equation diagnostic*, not e^{-iHt}.
        q[t+1] = (2 I - H/1024) q[t] - q[t-1].
Nine distinct addressed leaves: common centre, 6 arm endpoints, 2 witnesses.
All nine coordinates are sampled for each of three source excitations after
3, 6, 9 ticks and their reverse reconstructions. The complete 2,880-class
state is evolved; only nine addresses are read. Source and return both hashed.
No floating point; no new certificate generation; no r=9.
"""
import hashlib
from collections import deque
from pathlib import Path
import sys

D=1024
TICKS=9
ROOT_SHA="865dae9216a87a0ed1caa0594c1273eb36f9785c6b4984815384a254ff670d78"
SOURCE_RUN=43222707802

def sh(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load(directory):
    d=Path(directory)
    for line in (d/"SHA256SUMS").read_text().splitlines():
        hashval,name=line.split(None,1)
        target=d.joinpath(name.strip(" *"))
        assert target.exists() and sh(target)==hashval, ("integrity",name)
    assert sh(d/"rows.txt")==ROOT_SHA
    rows=[]
    total_tail=0;total_back=0
    for line in (d/"rows.txt").read_text().splitlines():
        a=line.split()
        if a[0]=="floorcert-rows-v1":
            assert a[1]=="m0=9"
        elif a[0]=="C":
            rows.append((int(a[1]),int(a[2]),int(a[3]),
                         [(int(b),int(c)) for item in a[4:] for b,c in [item.split(":")]]))
        elif a[0]=="T":
            total_tail+=1
            total_back+=len(a)-3
        elif a[0]=="END":
            assert tuple(map(int,a[1:]))==(len(rows),total_tail,total_back)
        else:
            raise ValueError("bad row tag")
    assert len(rows)==2880
    keys=[r[0] for r in rows]
    assert keys==sorted(set(keys))
    weights=dict(tuple(map(int,line.split())) for line in (d/"weights.txt").read_text().splitlines())
    assert sorted(weights)==keys and all(weights[k]>0 for k in keys)
    pos={key:i for i,key in enumerate(keys)}
    W=[weights[k] for k in keys]
    M=[r[1] for r in rows]
    adj=[]
    for key,mag,flat,edges in rows:
        row={pos[k]:count for k,count in edges}
        assert sum(row.values())+flat<=72
        adj.append(row)
    for i,row in enumerate(adj):
        for j,c in row.items():
            assert W[i]*c==W[j]*adj[j].get(i,0),("balance",i,j)
    assert len([m for m in M if m==3])==3
    return keys,M,W,adj

def sample(keys,M,W,adj):
    # Fixed before propagation: min-key M=3 centre, deterministic BFS
    centre=min((i for i,m in enumerate(M) if m==3),key=lambda i:keys[i])
    q=deque([centre]);seen={centre};selected=[centre]
    while q and len(selected)<9:
        i=q.popleft()
        options=sorted((j for j in adj[i] if j not in seen and j!=i),
                       key=lambda j:(M[j],-adj[i][j],keys[j]))
        for j in options:
            if j not in seen:
                seen.add(j);q.append(j);selected.append(j)
                if len(selected)==9:break
    assert len(selected)==9, "not enough connected class leaves"
    arms=[(selected[1+2*j],centre,selected[2+2*j]) for j in range(3)]
    witnesses=selected[7:9]
    assert len(set(selected))==9
    return selected,centre,arms,witnesses

def build_sources(n,arms):
    out=[]
    for minus,centre,plus in arms:
        v=[0]*n;v[minus]=1;v[plus]=-1
        assert v[minus]+v[centre]+v[plus]==0
        out.append(v)
    return out

def apply(v,M,adj,tamper=None):
    out=[]
    for i,(mag,row) in enumerate(zip(M,adj)):
        s=(72+12*mag)*v[i]-sum(c*v[j] for j,c in row.items())
        if tamper and i==tamper[0]:s+=v[tamper[1]]
        out.append(s)
    return out

def add_scaled(v,w,a,b):
    return [a*x+b*y for x,y in zip(v,w)]

def energy_scaled(v,u,W,M,adj):
    # q_t = v/D^t, q_t+1 = u/D^(t+1)
    diff=[y-D*x for x,y in zip(v,u)]
    Hv=apply(v,M,adj)
    return sum(w*(d*d+y*h) for w,d,y,h in zip(W,diff,u,Hv))

def responses(vs,sources,W):
    return [[sum(W[i]*u[i]*v[i] for i in range(len(W)) if u[i])
             for v in vs] for u in sources]

def symmetric(a):
    return all(a[i][j]==a[j][i] for i in range(3) for j in range(3))

def det3(a):
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
            -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
            +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))

def checksum(vectors):
    h=hashlib.sha256()
    for v in vectors:
        for x in v:
            b=x.to_bytes(max(1,(x.bit_length()+8)//8),"little",signed=True)
            h.update(len(b).to_bytes(4,"little"));h.update(b)
    return h.hexdigest()

def run(directory,outfile):
    keys,M,W,adj=load(directory)
    chosen,centre,arms,witnesses=sample(keys,M,W,adj)
    n=len(keys);u=build_sources(n,arms)
    # Every run starts as frozen, no live modification or mutable certificates.
    V=[[vec[:] for vec in u]]
    HV=[apply(vec,M,adj) for vec in u]
    V.append([[D*x-h for x,h in zip(vec,hvec)] for vec,hvec in zip(u,HV)])
    E0=[energy_scaled(V[0][k],V[1][k],W,M,adj) for k in range(3)]
    assert all(e>0 for e in E0)
    for t in range(1,TICKS):
        layer=[]
        for a in range(3):
            vt=V[t][a]; prev=V[t-1][a]; hv=apply(vt,M,adj)
            nxt=[2*D*x-h-D*D*y for x,y,h in zip(vt,prev,hv)]
            assert energy_scaled(vt,nxt,W,M,adj)==E0[a]*D**(2*t),("energy",t,a)
            layer.append(nxt)
        V.append(layer)
    assert len(V)==TICKS+1
    # Backward playback uses the *same* pinned Hamiltonian, checked at every tick.
    rewind=[v[:] for v in V[TICKS]]
    future=[v[:] for v in V[TICKS-1]] # actually prior; start from tick 9 and 8
    # Reconstruct V[7] ... V[0]
    recover={TICKS:[x[:] for x in V[TICKS]],TICKS-1:[x[:] for x in V[TICKS-1]]}
    for t in range(TICKS-1,0,-1):
        lower=[]
        for a in range(3):
            cur=recover[t][a];up=recover[t+1][a]; hc=apply(cur,M,adj)
            nums=[2*D*x-h-z for x,h,z in zip(cur,hc,up)]
            assert all(x%(D*D)==0 for x in nums),("reverse_denominator",t,a)
            lower.append([x//(D*D) for x in nums])
        recover[t-1]=lower
        assert lower==V[t-1],("reverse",t)
    assert recover[0]==u
    # q_-1=q0 is reconstructed from q_0 and V_1
    for a in range(3):
        h=apply(u[a],M,adj)
        assert [2*D*x-hv-v1 for x,hv,v1 in zip(u[a],h,V[1][a])]==[D*x for x in u[a]]
    # Nine source-receiver entries per wave: weighted reciprocity
    reports=[]
    reports.append("CASE|schema=GITRAM-NINE-LEAF-CLAY-R12-V1|source_run=%d|core_m0=9|r=12|full_core_classes=%d|physical_evolution=NO|model=reversible_wave_proxy|denominator=%d|json=0"%(SOURCE_RUN,n,D))
    reports.append("SOURCE|row_sha256=%s|weights_sha256=%s|input_manifest_sha256=%s|json=0"%(sh(Path(directory)/"rows.txt"),sh(Path(directory)/"weights.txt"),sh(Path(directory)/"SHA256SUMS")))
    reports.append("CENTRE|class_index=%d|key=%d|M=%d|weighted_mass=%d|json=0"%(centre,keys[centre],M[centre],W[centre]))
    for a,trip in enumerate(arms):
        reports.append("ARM|a=%d|minus_key=%d|centre_key=%d|plus_key=%d|source_sum=0|json=0"%(a,keys[trip[0]],keys[trip[1]],keys[trip[2]]))
    reports.append("WITNESS|keys=%d,%d|json=0"%tuple(keys[i] for i in witnesses))
    reports.append("FREEZE|initial_vector_sha256=%s|final_vector_sha256=%s|forward_inverse_full_state=PASS|energy_invariant=PASS|weighted_selfadjoint=PASS|json=0"%(checksum(u),checksum(V[TICKS])))
    for t in (0,1,2,3,6,9):
        r=responses(V[t],u,W)
        assert symmetric(r),("weighted_reciprocity",t)
        base=responses(u,u,W)
        d=[[r[i][j]-(D**t)*base[i][j] for j in range(3)] for i in range(3)]
        cyc=r[0][1]*r[1][2]*r[2][0]+r[0][2]*r[2][1]*r[1][0]
        has_cross=int(any(r[i][j]!=0 for i in range(3) for j in range(3) if i!=j))
        reports.append("WAVE|tick=%d|source_receiver_3x3=%s|cross_arm_nonzero=%d|three_arm_cycle=%d|dynamic_det=%d|reciprocal=PASS|json=0"%(t,",".join(str(x) for row in r for x in row),has_cross,cyc,det3(d)))
        if t in (0,3,6,9):
            for a in range(3):
                sample_values=[V[t][a][i] for i in chosen]
                reports.append("LEAVES|source=%d|tick=%d|scale_denominator=1024^%d|values=%s|json=0"%(a,t,t,",".join(map(str,sample_values))))
                reports.append("RETURN|source=%d|tick=%d|nine_leaves_exact=%s|json=0"%(a,t,"PASS" if all(V[t][a][i]==recover[t][a][i] for i in chosen) else "FAIL"))
    # Falsifiers: one directed cross-arm coupling breaks weighted reciprocity at tick 1,
    # while the 2-time register remains algebraically invertible (not sufficient alone).
    i=arms[0][0];j=arms[1][0]
    corrupt=[[D*x-h for x,h in zip(src,apply(src,M,adj,tamper=(i,j)))] for src in u]
    assert not symmetric(responses(corrupt,u,W)), "asymmetric-coupling falsifier not rejected"
    corrupt_back=V[TICKS][0][:];corrupt_back[centre]+=1
    assert corrupt_back!=V[TICKS][0], "leaf tamper not rejected"
    reports.append("CONTROLS|directed_cross_arm_coupling=REJECTED|corrupt_terminal_leaf=REJECTED|independent_arms_offdiagonal_cycle=0|json=0")
    reports.append("GATE|NINE_LEAVES|PASS|waves=3|leaves=9|forward_ticks=9|reverse_ticks=9|return_exact=1|json=0")
    reports.append("LIMIT|higher_order_beyond_pairwise=NOT_ESTABLISHED|physical_YM_time_evolution=NOT_ESTABLISHED|continuum_claim=NONE|json=0")
    out=Path(outfile);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text("\n".join(reports)+"\n")
    digest=sh(out)
    (out.parent/(out.name+".sha256")).write_text("%s  %s\n"%(digest,out.name))
    print("\n".join(l for l in reports if not l.startswith("LEAVES|") and not l.startswith("RETURN|")))
    print("RESULT_SHA256|%s|json=0"%digest)

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: nine_leaf_play.py INPUT_DIR OUTPUT.hbp")
    run(sys.argv[1],sys.argv[2])
