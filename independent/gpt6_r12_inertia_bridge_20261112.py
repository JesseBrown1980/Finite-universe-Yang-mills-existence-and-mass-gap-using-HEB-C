#!/usr/bin/env python3
"""Independent r12 invariant-sector counting audit; fixed Schur threshold.

Reconstruct symmetric class-weighted K from immutable canonical 2880 rows,
the independently SHA-pinned R-block witness and the frozen cutoff-9 weight.
Uses exact reduced integer pairs, dyadic outward rounding and a strict
fraction-free Bareiss LDL sign count with *checked* exact division.
No floating arithmetic, JSON, unauthorized r9 run, or gap claim outside
the 48-symmetry invariant sector.
"""
from collections import defaultdict
from hashlib import sha256
from math import lcm
from pathlib import Path
from sys import argv
from independent.seat_integer_ratio import IntegerRatio as Rat

CASES={
    "10455/100":(4,73,1,"wit-m9-f6543-t104.55-L4.txt"),
    "10470/100":(4,73,2,"wit-m9-f6543-t104.7-L4.txt"),
    "110/1":(3,3,3,"wit-m9-f6543-t110-L3.txt"),
}
ROW_SHA="865dae9216a87a0ed1caa0594c1273eb36f9785c6b4984815384a254ff670d78"
DYADIC=1<<80

def filehash(path):
    return sha256(Path(path).read_bytes()).hexdigest()

def reciproc(x):
    assert x.num
    return Rat(x.den,x.num)

def chooseword(word, cutoff, magnetic):
    assert magnetic>cutoff, ("tail class mistakenly entered core",magnetic,cutoff)
    return word[min(magnetic-cutoff,len(word))-1]

def load_pinned(folder,leaf):
    manifest=folder.joinpath("SHA256SUMS")
    assert manifest.is_file()
    for item in manifest.read_text(encoding="ascii").splitlines():
        digest,name=item.split(None,1)
        name=name.strip(" *")
        assert name and "/" not in name and ".." not in name
        p=folder.joinpath(name)
        assert p.is_file() and filehash(p)==digest,("pinned source corrupt",name)
    rowpath=folder.joinpath("rows.txt")
    assert filehash(rowpath)==ROW_SHA
    weight={}
    for ln in folder.joinpath("weights.txt").read_text(encoding="ascii").splitlines():
        if not ln.strip():continue
        k,w=map(int,ln.split())
        assert k not in weight and w>0
        weight[k]=w
    leafweight={}
    for ln in leaf.read_text(encoding="ascii").splitlines():
        if not ln.startswith("LEAF|"):continue
        a=dict(z.split("=",1) for z in ln.split("|") if "=" in z)
        k,w=int(a["key"]),int(a["w"])
        assert k not in leafweight and w>0
        leafweight[k]=w
    assert len(weight)==len(leafweight)==2880
    assert weight==leafweight,"cutoff9 weights do not match independently stored leaves"
    return rowpath.read_text(encoding="ascii").splitlines(),weight,filehash(manifest)

def load_witness(path,keys):
    g={}
    for ln in path.read_text(encoding="ascii").splitlines():
        if not ln.strip():continue
        k,v=map(int,ln.split())
        assert k not in g and v>0
        g[k]=v
    assert set(g)==set(keys),"witness is not exactly the R block"
    return g

def load_G(lines,weight,t):
    core={};mag={};last=None
    r=12
    cutoff=9
    word=(6,5,4,3)
    cache={}
    tail_signatures=0
    for ln in lines:
        cells=ln.split()
        if not cells:continue
        typ=cells[0]
        if typ=="floorcert-rows-v1":continue
        if typ=="C":
            a=int(cells[1]);M=int(cells[2])
            assert a not in core
            mag[a]=M
            last=a
            row=defaultdict(lambda:Rat(0))
            row[a]=Rat(72+r*M)-t
            for c in cells[4:]:
                b,n=map(int,c.split(":"))
                row[b]=row[b]-n
            core[a]=row
        elif typ=="T":
            assert last is not None
            m=int(cells[1])
            hist=tuple(map(int,cells[2].split(",")))
            assert len(hist)==9
            sig=(m,hist)
            if sig not in cache:
                fm=chooseword(word,cutoff,m)
                lhs=Rat(fm)*(Rat(72+r*m)-t)
                rhs=sum((amount*chooseword(word,cutoff,m+j-4)
                         for j,amount in enumerate(hist) if amount),0)
                denom=lhs-rhs
                assert denom>0,("bad tail denominator",m)
                cache[sig]=Rat(fm)*reciproc(denom)
            w=cache[sig]
            for b in cells[3:]:
                j=int(b)
                core[last][j]=core[last][j]-w
            tail_signatures+=1
        elif typ=="END":
            pass
        else:raise AssertionError(("unrecognized canonical record",typ))
    assert len(core)==2880 and list(core)==sorted(core)
    assert set(weight)==set(core)
    assert sum(x==3 for x in mag.values())==3
    offdiag=0
    for a,row in core.items():
        for b,c in row.items():
            assert b in core
            if a!=b:
                assert c<=0,("offdiag sign",a,b)
                assert weight[a]*c==weight[b]*core[b].get(a,Rat(0)),(
                    "weighted Hermiticity",a,b)
                offdiag+=1
    return core,mag,offdiag,len(cache),tail_signatures

def build_K(G,mag,weight,witness,max_m):
    L=[a for a in G if mag[a]<=max_m]
    R=[a for a in G if mag[a]>max_m]
    assert len(L) in (3,73)
    rset=set(R)
    g=load_witness(witness,R)
    lindex={x:i for i,x in enumerate(L)}
    n=len(L)
    k=[[Rat(0) for _ in range(n)] for _ in range(n)]
    for a in L:
        i=lindex[a]
        for b,c in G[a].items():
            if b in lindex:
                k[i][lindex[b]]=k[i][lindex[b]]+weight[a]*c
    mins=None
    ceil_excess_count=0
    for a in R:
        da=sum((x*g[b] for b,x in G[a].items() if b in rset),Rat(0))
        assert da>0,("not positive R witness",a,str(da))
        if mins is None or da<mins:mins=da
        assert weight[a]>0
        cn=g[a]*da.den
        cd=weight[a]*da.num
        assert cn>0 and cd>0
        up=(cn*DYADIC+cd-1)//cd
        coeff=Rat(up,DYADIC)
        assert coeff*Rat(cd)>=cn
        assert (up-1)*cd<cn*DYADIC
        ceil_excess_count+=int(up*cd>cn*DYADIC)
        bridges=[]
        for b,c in G[a].items():
            if b in lindex:
                bridges.append((lindex[b],weight[a]*c))
        for i,bi in bridges:
            for j,bj in bridges:
                k[i][j]=k[i][j]-bi*bj*coeff
    assert mins is not None and mins>0
    for i in range(n):
        for j in range(i):
            assert k[i][j]==k[j][i],("K asymmetric",i,j)
    return k,len(L),len(R),mins,ceil_excess_count

def inertia_strict_bareiss(K):
    n=len(K)
    den=1
    for row in K:
        for x in row:den=lcm(den,x.den)
    a=[[x.num*(den//x.den) for x in row] for row in K]
    prev=1
    signs=[1]
    exact_divisions=0
    pivots=[]
    for k in range(n):
        piv=a[k][k]
        assert piv!=0,("zero leading minor",k)
        pivots.append(piv)
        signs.append(1 if piv>0 else -1)
        for i in range(k+1,n):
            ak_i=a[i][k]
            for j in range(i,n):
                numer=a[i][j]*piv-ak_i*a[k][j]
                assert numer%prev==0,("Bareiss noninteger division",k,i,j)
                a[i][j]=numer//prev
                a[j][i]=a[i][j]
                exact_divisions+=1
        prev=piv
    negative=sum(signs[i]!=signs[i-1] for i in range(1,len(signs)))
    return negative,n-negative,exact_divisions,max(abs(x).bit_length() for x in pivots),den.bit_length()

def run(folder,leaf,witness,threshold,out):
    assert threshold in CASES
    Mmax,nsmall,expected,wname=CASES[threshold]
    assert witness.name==wname
    nums=list(map(int,threshold.split("/")))
    assert len(nums)==2 and nums[0]>0 and nums[1]>0
    t=Rat(*nums)
    assert t<Rat(144),"tail cap exceeded"
    lines,W,source_hash=load_pinned(folder,leaf)
    G,M,offdiag,uniq,tailcount=load_G(lines,W,t)
    K,L,R,min_d,round_count=build_K(G,M,W,witness,Mmax)
    assert L==nsmall and L+R==2880
    neg,pos,checks,maxpivot,denbits=inertia_strict_bareiss(K)
    assert neg==expected,("precommitted inertia falsified",threshold,neg,expected)
    lines=[
        "COUNT_AUDIT|schema=GPT6-R12-INDEPENDENT-V1|threshold=%s|r=12|source_sha256=%s|source_manifest=%s|json=0"%
        (threshold,ROW_SHA,source_hash),
        "MATRIX|classes=2880|low_dim=%d|high_dim=%d|offdiag_validated=%d|reciprocal_all_pass=1|tail_signatures=%d|tail_records=%d|json=0"%
        (L,R,offdiag,uniq,tailcount),
        "WITNESS|name=%s|sha256=%s|min_Rblock_d_num=%d|min_Rblock_d_den=%d|positive=YES|up_rounding_cases=%d|json=0"%
        (wname,filehash(witness),min_d.num,min_d.den,round_count),
        "INERTIA|negative=%d|positive=%d|expected_negative=%d|bareiss_exact_divisions=%d|max_minor_bits=%d|scale_denominator_bits=%d|json=0"%
        (neg,pos,expected,checks,maxpivot,denbits),
        "LIMIT|N_lt_t_of_symmetric_sector_at_most=%d|full_111906_orbit_symmetry_sectors=NOT_TESTED|tail_coverage_hand_bridge=ASSUMED|r9=HOLD|json=0"%neg,
        "COUNTING_R12_INDEPENDENT_PASS|threshold=%s|negative=%d|r=12|r9=HOLD|json=0"%(threshold,neg),
    ]
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text("\n".join(lines)+"\n",encoding="ascii")
    out.with_name(out.name+".sha256").write_text(
        filehash(out)+"  "+out.name+"\n",encoding="ascii")
    print("\n".join(lines))

if __name__=="__main__":
    if len(argv)!=6:
        raise SystemExit("python -B -m independent.gpt6_r12_inertia_bridge_20261112 ORIGINAL_FOLDER LEAF_HBP WITNESS_FILE THRESHOLD OUT_HBP")
    run(Path(argv[1]),Path(argv[2]),Path(argv[3]),argv[4],Path(argv[5]))
