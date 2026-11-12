#!/usr/bin/env python3
"""Exact r12 Gauss-Seidel order audit: 9 immutable certificate cells.

Reads SHA-pinned (cutoff 7,8,9) rows and original immutable certs, plus
published S leaf residuals on main. Computes exact Spearman rankings of
the forward/backward weighted coupling from the actual Schur comparison
matrix (not graph position or physical time). Reconstructs the writer's
E-scaled integer FMat and replays one fixed eight-sweep inverse solve
in both directions from the SAME v, t, initial x and shift. The
last-sweep error identity includes integer-division remainder.

For further-convergence sensitivity, continues to 24 sweeps, from
the same x initialized at the start. Does not rerun the writer's
outer inverse iteration, prove mixing, or prove a continuum mass gap.
No floating point, Fraction, JSON, or r9 execution.
"""
from hashlib import sha256
from math import isqrt
from pathlib import Path
import sys
from independent.seat_integer_ratio import IntegerRatio as Rat

E=1<<20
R=12
DT=10000
WORDS=("1","6,5,4,3","8,7,6,5,4")

def h(path):
    return sha256(Path(path).read_bytes()).hexdigest()

def trunc(a,b):
    assert b>0
    return a//b if a>=0 else -( (-a)//b )

def chk(folder):
    manifest=folder/"SHA256SUMS"
    assert manifest.is_file()
    for line in manifest.read_text(encoding="ascii").splitlines():
        digest, name=line.split(None,1)
        name=name.strip(" *")
        assert name and "/" not in name and ".." not in name
        assert h(folder/name)==digest,("source checksum mismatch",name)

def rows_read(folder,m0):
    lines=(folder/"rows.txt").read_text(encoding="ascii").splitlines()
    assert lines[0]=="floorcert-rows-v1 m0=%d"%m0
    rows=[]
    for line in lines[1:]:
        z=line.split()
        if not z:continue
        if z[0]=="C":
            key,mag,nflat=map(int,z[1:4])
            rows.append([key,mag,nflat,[(int(a),int(b)) for a,b in (x.split(":") for x in z[4:])],[]])
        elif z[0]=="T":
            m=int(z[1]); hist=tuple(map(int,z[2].split(",")))
            assert len(hist)==9
            rows[-1][4].append((m,hist,tuple(map(int,z[3:]))))
        elif z[0]=="END":
            assert tuple(map(int,z[1:]))==(len(rows),sum(len(x[4]) for x in rows),sum(len(t[2]) for x in rows for t in x[4]))
        else:raise AssertionError("unrecognized tag")
    assert [x[0] for x in rows]==sorted({x[0] for x in rows})
    assert all(x[2]+sum(v for _,v in x[3])+len(x[4])==72 for x in rows)
    return rows,h(folder/"rows.txt")

def cert_read(path,m0,rhash,rows):
    lines=path.read_text(encoding="ascii").splitlines()
    assert lines[0].startswith("# floorcert certificate: ")
    f=dict(t.split("=",1) for t in lines[0].split() if "=" in t)
    assert f["rowhash"]==rhash and int(f["m0"])==m0 and f["r"]=="12/1"
    assert int(f["t"].split("/")[1])==DT
    w=tuple(map(int,f["f"].split(",")))
    t=int(f["t"].split("/")[0])
    assert t>0 and all(x>0 for x in w)
    vv={}
    for line in lines[1:]:
        z=line.split()
        if not z:continue
        a,mag,vi=map(int,z)
        assert a not in vv and vi>0
        vv[a]=(mag,vi)
    assert len(vv)==len(rows)
    assert all(vv[x[0]][0]==x[1] for x in rows)
    return w,t,vv

def leaves_read(path,rows,vv):
    vals={}
    for line in path.read_text(encoding="ascii").splitlines():
        if not line:continue
        assert line.startswith("LEAF|")
        f=dict(s.split("=",1) for s in line.split("|") if "=" in s)
        key=int(f["key"])
        assert key not in vals
        vals[key]=(int(f["M"]),int(f["v"]),int(f["slack"]))
    assert len(vals)==len(rows)
    assert all(vals[x[0]][0]==x[1] and vals[x[0]][1]==vv[x[0]][1] for x in rows)
    return vals

def rank(x):
    ids=sorted(range(len(x)),key=lambda j:x[j])
    result=[0]*len(x)
    i=0
    while i<len(ids):
        j=i
        while j+1<len(ids) and x[ids[j+1]]==x[ids[i]]:
            j+=1
        for k in range(i,j+1):
            result[ids[k]]=i+j
        i=j+1
    return result

def spear(x,y):
    a=rank(x);b=rank(y);n=len(a)
    sa=sum(a);sb=sum(b)
    top=n*sum(u*v for u,v in zip(a,b))-sa*sb
    da=n*sum(u*u for u in a)-sa*sa
    db=n*sum(v*v for v in b)-sb*sb
    if not da or not db:return 0
    scaled=isqrt(top*top*1000000//(da*db))
    return scaled if top>=0 else -scaled

def f_at(word,m,m0):
    assert m>m0
    return word[min(m-m0,len(word))-1]

def matrix(rows,m0,word,tn,vals):
    # Core entries, including any self edge, then tail Schur contribution.
    # Reproduce Rust's E-scaled coefficient truncation and independent
    # exact rational weights for the rank-correlation diagnostic.
    index={x[0]:i for i,x in enumerate(rows)}
    assert len(index)==len(rows)
    v=[vals[x[0]][1] for x in rows]
    diagonal=[]
    all_w=[]
    forward=[]
    backward=[]
    for a,row in enumerate(rows):
        key,mag,flat,core,tails=row
        diagonal.append(E*(72*DT+R*DT*mag-tn)//DT)
        ws={}
        exact={}
        for j,c in core:
            jj=index[j]
            ws[jj]=ws.get(jj,0)+E*c
            exact[jj]=exact.get(jj,Rat(0))+c
        for m,hist,back in tails:
            fk=f_at(word,m,m0)
            sf=sum(cnt*f_at(word,m+k-4,m0) for k,cnt in enumerate(hist) if cnt)
            n=((72*DT+R*DT*m-tn)*fk - DT*sf)
            assert n>0
            scaled=E*DT*fk//n
            precise=Rat(DT*fk,n)
            for j in back:
                jj=index[j]
                ws[jj]=ws.get(jj,0)+scaled
                exact[jj]=exact.get(jj,Rat(0))+precise
        all_w.append(sorted(ws.items()))
        uf=Rat(0);ub=Rat(0)
        for jj,c in exact.items():
            if jj>a:uf+=c*v[jj]
            elif jj<a:ub+=c*v[jj]
        forward.append(uf/v[a])
        backward.append(ub/v[a])
    assert len(diagonal)==len(v) and all(diagonal[i]>0 for i in range(len(v)))
    return diagonal,all_w,v,forward,backward

def solve(diag,ww,v,reverse,steps):
    n=len(v)
    # This is the actual Rust gs_eigen source's starting x and shift,
    # using the FMat at the certificate's recorded t.
    ratios=[]
    selfw=[]
    for i in range(n):
        selfco=sum(w for j,w in ww[i] if j==i)
        selfw.append(selfco)
        action=diag[i]*v[i]-sum(w*v[j] for j,w in ww[i])
        ratios.append(trunc(action,v[i]))
    lo=min(ratios);hi=max(ratios)
    margin=min(20*E,max(E//50,(hi-lo)//4))
    sigma=lo-margin
    den=[diag[i]-selfw[i]-sigma for i in range(n)]
    assert all(z>0 for z in den), "inverse problem diagonal invalid"
    x=[trunc(vi*E,margin) for vi in v]
    order=range(n-1,-1,-1) if reverse else range(n)
    last_before=[];last_rem=[]
    out={}
    for t in range(1,steps+1):
        old=x[:]
        remainder=[0]*n
        for i in order:
            numerator=E*v[i]+sum(w*x[j] for j,w in ww[i] if j!=i)
            x[i]=trunc(numerator,den[i])
            remainder[i]=numerator-den[i]*x[i]
            assert 0<=remainder[i]<den[i]
        if t in (8,24):
            # Exact residual of the final inverse equation,
            # compared to the omitted FUTURE-neighbour changes.
            mismatches=0;nonzero=0;raw=0;remsum=0;future_mass=0
            for i in range(n):
                lhs=den[i]*x[i]-E*v[i]-sum(w*x[j] for j,w in ww[i] if j!=i)
                future=sum(w*(x[j]-old[j]) for j,w in ww[i]
                           if (j<i if reverse else j>i))
                predicted=-remainder[i]-future
                if lhs!=predicted:mismatches+=1
                nonzero+=int(future!=0)
                raw+=abs(lhs)
                remsum+=remainder[i]
                future_mass+=abs(future)
            assert mismatches==0, ("GS last-sweep exact identity",mismatches)
            digest=sha256((",".join(map(str,x))+"\n").encode("ascii")).hexdigest()
            out[t]=(digest,raw,future_mass,remsum,nonzero,mismatches)
    return out

def audit(folder,m0,leafdir):
    chk(folder)
    rows,rhash=rows_read(folder,m0)
    output=[]
    for wordtxt in WORDS:
        stem=wordtxt.replace(",","-")
        cert=folder/("cert_m%d_r12_1_f%s.txt"%(m0,stem))
        leaf=leafdir/("S_cert_m%d_r12_1_f%s.leaf.hbp"%(m0,stem))
        assert cert.is_file() and leaf.is_file()
        word,t,vals=cert_read(cert,m0,rhash,rows)
        vl=leaves_read(leaf,rows,vals)
        d,w,v,uf,ub=matrix(rows,m0,word,t,vals)
        q=[Rat(vl[x[0]][2],vl[x[0]][1]) for x in rows]
        corr=spear(q,uf);bcorr=spear(q,ub)
        assert corr>0, ("frozen positive cutoff7 forward prediction",m0,wordtxt,corr)
        print("FROZEN_RESIDUAL|m0=%d|f=%s|rows=%d|forward_rank_milli=%d|backward_rank_milli=%d|certificate_sha256=%s|leaf_sha256=%s|json=0"%(m0,wordtxt,len(rows),corr,bcorr,h(cert),h(leaf)))
        output.append((m0,wordtxt,corr,bcorr))
        fw=solve(d,w,v,False,24)
        rv=solve(d,w,v,True,24)
        assert fw[8][0]!=rv[8][0], "reverse and forward unexpectedly identical"
        for direction,data in (("forward",fw),("reverse",rv)):
            for sweeps,(digest,residual,future,remainder,active,bad) in data.items():
                print("GS_EXACT|m0=%d|f=%s|direction=%s|inner_sweeps=%d|vector_sha256=%s|residual_abs_sum=%d|future_term_abs_sum=%d|integer_remainder_sum=%d|affected_rows=%d|identity_mismatches=%d|json=0"%(m0,wordtxt,direction,sweeps,digest,residual,future,remainder,active,bad))
            print("CONVERGENCE|m0=%d|f=%s|direction=%s|sweeps_8_abs=%d|sweeps_24_abs=%d|reduction=%s|json=0"%(m0,wordtxt,direction,data[8][1],data[24][1],"YES" if data[24][1]<data[8][1] else "NO"))
    assert len(output)==3
    print("GS_CUTOFF_PASS|m0=%d|words=3|forward_backward=PASS|replay_8_and_24=PASS|r=12|r9=HOLD|json=0"%m0)

if __name__=="__main__":
    if len(sys.argv)!=4:raise SystemExit("usage: python -B independent/gpt6_gs_sweep_order_20261112.py ARTIFACT_DIR M0 LEAVES_DIR")
    audit(Path(sys.argv[1]),int(sys.argv[2]),Path(sys.argv[3]))
