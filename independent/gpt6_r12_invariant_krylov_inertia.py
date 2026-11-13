#!/usr/bin/env python3
"""Independent exact full-core invariant Krylov, then orthogonal sector sum.

All numbers exact integers. The seed is the sum of the 12 equal-weight
M3 gauge-orbit basis states in ONE complete D3xD4 orbit, hence invariant.
B=180I-H_CC preserves the invariant subspace. Gram and Q inertia are
computed from moments, with checked exact Bareiss divisions.

The separate nontrivial signed-orbit-difference seed is orthogonal to
this invariant subspace; its hosted receipt supplies disjoint negative
directions. Full-space lower bound on N_<t follows by block orthogonality.
These are upper/existence Ritz counts only; not whole-spectrum lower
enclosures or a proof of a first mass gap.
"""
from pathlib import Path
from hashlib import sha256
from sys import argv
from independent.gpt6_r12_nontrivial_krylov_inertia import (
    parse_graph, exact_inertia_symmetric, BINARY_SHA, SHIFT
)
K=30
CLASS=2613485090

def load_seed_class(source,keys,mags,W):
    member={}
    for line in source.read_text(encoding="ascii").splitlines():
        if not line.startswith("M3_ORBIT_CLASS|"):continue
        p=dict(x.split("=",1) for x in line.split("|")[1:] if "=" in x)
        key=int(p["key"])
        assert key not in member
        member[key]=(int(p["class_key"]),int(p["gauge_weight"]))
    assert len(member)==36
    selected=[key for key,value in member.items() if value[0]==CLASS]
    assert len(selected)==12
    lookup={key:i for i,key in enumerate(keys)}
    idx=sorted(lookup[key] for key in selected)
    assert all(mags[i]==3 and W[i]==6 for i in idx)
    assert all(member[key]==(CLASS,6) for key in selected)
    return idx,sha256(source.read_bytes()).hexdigest()

def moments(mags,W,adj,indices):
    diag=[SHIFT-(72+12*m) for m in mags]
    v=[0]*len(mags)
    for i in indices:v[i]=1
    mu=[]
    support=[]
    for power in range(2*K+2):
        mu.append(sum(W[i]*v[i] for i in indices))
        if power in (0,8,25,2*K+1):
            support.append((power,sum(int(x!=0) for x in v)))
        if power==2*K+1:break
        nxt=[0]*len(mags)
        for i,row in enumerate(adj):
            t=diag[i]*v[i]
            for j,c in row:
                t+=c*v[j]
            nxt[i]=t
        v=nxt
    assert mu[0]==72
    return mu,support

def verify_nontrivial_receipt(path):
    lines=path.read_text(encoding="ascii").splitlines()
    assert any(x.startswith("KRYLOV_NONTRIV_R12_REPLAY_PASS|dimension=26|negative_below1055_over10=2|r9=HOLD|") for x in lines)
    t={}
    for line in lines:
        if not line.startswith("KRYLOV_INERTIA|"):continue
        p=dict(x.split("=",1) for x in line.split("|")[1:] if "=" in x)
        t[p["threshold"]]=int(p["negative"])
    assert t["1055/10"]==2 and t["110/1"]==4
    assert any(BINARY_SHA in x for x in lines if x.startswith("KRYLOV_SOURCE|"))
    return t,sha256(path.read_bytes()).hexdigest()

def run(core,orbit_source,nontrivial_source,destination):
    keys,mags,W,adj,edge_count=parse_graph(core)
    idx,group_sha=load_seed_class(orbit_source,keys,mags,W)
    nontriv,nontriv_sha=verify_nontrivial_receipt(nontrivial_source)
    mu,support=moments(mags,W,adj,idx)
    n=K+1
    gram=[[mu[i+j] for j in range(n)] for i in range(n)]
    gneg,gdiv,gbits,gsigns=exact_inertia_symmetric(gram)
    assert gneg==0 and all(s==1 for s in gsigns)
    lines=[
        "INV_KRYLOV_SOURCE|schema=GPT6-TRIVIAL-R12-EXACT-V1|core_sha256=%s|M3_group_sha256=%s|nontriv_receipt_sha256=%s|states=%d|core_edges=%d|r=12|m0=9|json=0"%
        (BINARY_SHA,group_sha,nontriv_sha,len(keys),edge_count),
        "INV_SEED|class_key=%d|weight_each=6|group_orbit_size=%d|symmetry_invariant=YES|json=0"%
        (CLASS,len(idx)),
        "INV_GRAM|dimension=%d|negative=%d|positive_definite=PASS|bareiss_exact_divisions=%d|max_minor_bits=%d|json=0"%
        (n,gneg,gdiv,gbits)
    ]
    for power,nn in support:
        lines.append("INV_SUPPORT|power=%d|states=%d|json=0"%(power,nn))
    thresholds=[
        (10451,100,1),
        (10468,100,2),
        (10485,100,3),
        (1055,10,3),
        (110,1,3),
    ]
    verified={}
    for top,den,expected in thresholds:
        q=[[(SHIFT*den-top)*mu[i+j]-den*mu[i+j+1] for j in range(n)] for i in range(n)]
        neg,div,bits,signs=exact_inertia_symmetric(q)
        assert neg==expected,("invariant seeded count falsified",top,den,neg,expected)
        key="%d/%d"%(top,den)
        verified[key]=neg
        lines.append("INV_KRYLOV_INERTIA|threshold=%s|dimension=%d|negative=%d|bareiss_exact_divisions=%d|max_minor_bits=%d|json=0"%
                     (key,n,neg,div,bits))
    five=verified["1055/10"]+nontriv["1055/10"]
    seven=verified["110/1"]+nontriv["110/1"]
    assert five==5 and seven==7
    lines += [
        "ORTHOGONAL_COUNT|threshold=1055/10|trivial_negative=%d|nontrivial_negative=%d|full_nonflat_below_at_least=%d|json=0"%
        (verified["1055/10"],nontriv["1055/10"],five),
        "ORTHOGONAL_COUNT|threshold=110/1|trivial_negative=%d|nontrivial_negative=%d|full_nonflat_below_at_least=%d|json=0"%
        (verified["110/1"],nontriv["110/1"],seven),
        "THEOREM|finite_nonflat_full_spectrum_has_at_least_five_eigenvalues_below_1055/10_and_seven_below_110|independent_exact_variational=YES|source_symmetry_covariance_required=YES|json=0",
        "LIMIT|incomplete_sector_lower_bounds=1|no_first_gap_or_continuum_claim=1|r9=HOLD|json=0",
        "INV_KRYLOV_R12_REPLAY_PASS|dimension=%d|trivial_below10485=3|full_below1055=5|full_below110=7|r9=HOLD|json=0"%n,
    ]
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text("\n".join(lines)+"\n",encoding="ascii")
    destination.with_name(destination.name+".sha256").write_text(
        sha256(destination.read_bytes()).hexdigest()+"  "+destination.name+"\n",encoding="ascii")
    print("\n".join(lines))

if __name__=="__main__":
    assert len(argv)==5
    run(*(Path(a) for a in argv[1:]))
