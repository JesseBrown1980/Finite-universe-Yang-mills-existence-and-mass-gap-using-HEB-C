#!/usr/bin/env python3
"""Exact integer nontrivial-symmetry Ritz/Haynsworth test on 111906 core.

Data are separately generated SHA-256-pinned full S3 gauge-orbit core
matrix and D3xD4 orbit classification for the two seed states.
Because the seed is the difference of two states in the SAME lattice
symmetry orbit with equal weight, its group average is zero. Since
H and the magnetic cutoff commute with D3xD4, polynomial(H) seed
stays orthogonal to the trivial (symmetry-invariant) subspace.

Let B=180I-H_core; mu[k]=<v,B**k v>_W. The exact symmetric
Gram/threshold matrices on span(v,Bv,...,B**K v) are
Gram[i,j]=mu[i+j]
Q_t[i,j]=(180*d-t_num)*mu[i+j]-d*mu[i+j+1].
Its negative inertia gives a rigorous LOWER BOUND on the count of
FULL non-flat nontrivial-sector eigenvalues below t (zero-extended
trial vectors, no omitted-tail artifacts in their Rayleigh form).

Every step and Bareiss division uses integers. This is a FOLLOW-UP
after an exploratory local run; it is NOT a blind prediction.
"""
from hashlib import sha256
from pathlib import Path
from struct import unpack_from
from sys import argv

BINARY_SHA="74c0d38850790c2fff38a6680bf36d3701aeb63b998bd4d7be778539ddd82aec"
PLUS_KEY=2613485090
MINUS_KEY=2628605549
SYM_CLASS=2613485090
SHIFT=180
K=25

def parse_graph(path):
    data=path.read_bytes()
    assert sha256(data).hexdigest()==BINARY_SHA
    tag=b"S3R12CORE111906"
    assert data.startswith(tag)
    pos=len(tag)
    n=unpack_from("<I",data,pos)[0];pos+=4
    assert n==111906
    keys=[];mag=[];weight=[];edges=[];directed=0
    for a in range(n):
        key=unpack_from("<Q",data,pos)[0];pos+=8
        m,w,flat,tail=data[pos:pos+4];pos+=4
        count=unpack_from("<H",data,pos)[0];pos+=2
        assert (not keys or keys[-1]<key) and 3<=m<=9 and 1<=w<=6 and count<=72
        e=[];sumc=0;last=-1
        for j in range(count):
            b=unpack_from("<I",data,pos)[0];pos+=4
            c=data[pos];pos+=1
            assert last<b<n and 1<=c<=72
            e.append((b,c))
            sumc+=c;last=b
        assert sumc+flat+tail==72
        keys.append(key);mag.append(m);weight.append(w);edges.append(e)
        directed+=count
    assert pos==len(data) and directed==1818336
    return keys,mag,weight,edges,directed

def check_class(path):
    lines=path.read_text(encoding="ascii").splitlines()
    found={}
    for line in lines:
        if not line.startswith("M3_ORBIT_CLASS|"):continue
        f=dict(t.split("=",1) for t in line.split("|")[1:] if "=" in t)
        key=int(f["key"])
        assert key not in found
        found[key]=(int(f["class_key"]),int(f["gauge_weight"]))
    assert len(found)==36
    assert found[PLUS_KEY]==found[MINUS_KEY]==(SYM_CLASS,6)
    return sha256(path.read_bytes()).hexdigest()

def moments(keys,mag,weights,edges):
    idx={key:i for i,key in enumerate(keys)}
    a,b=idx[PLUS_KEY],idx[MINUS_KEY]
    assert a!=b and mag[a]==mag[b]==3 and weights[a]==weights[b]==6
    v=[0]*len(keys)
    v[a]=1
    v[b]=-1
    diag=[SHIFT-(72+12*m) for m in mag]
    # Moments through 2K+1 require 2K+1 matrix applications.
    mu=[]
    support=[]
    for power in range(2*K+2):
        mu.append(6*(v[a]-v[b]))
        if power in (0,8,25,2*K+1):
            support.append((power,sum(int(z!=0) for z in v)))
        if power==2*K+1:break
        nxt=[0]*len(keys)
        for i,row in enumerate(edges):
            t=diag[i]*v[i]
            for j,c in row:
                t+=c*v[j]
            nxt[i]=t
        v=nxt
    assert mu[0]==12
    assert len(mu)==2*K+2
    return mu,support

def sign(x):
    return (x>0)-(x<0)

def exact_inertia_symmetric(matrix):
    n=len(matrix)
    assert all(len(row)==n for row in matrix)
    assert all(matrix[i][j]==matrix[j][i] for i in range(n) for j in range(i))
    a=[row[:] for row in matrix]
    prev=1
    signs=[1]
    exact_divisions=0
    max_bits=0
    for k in range(n):
        pivot=a[k][k]
        assert pivot!=0,("singular leading principal minor",k)
        signs.append(sign(pivot))
        max_bits=max(max_bits,abs(pivot).bit_length())
        for i in range(k+1,n):
            p=a[i][k]
            for j in range(i,n):
                num=a[i][j]*pivot-p*a[k][j]
                assert num%prev==0,("Bareiss nonexact",k,i,j)
                a[i][j]=num//prev
                a[j][i]=a[i][j]
                exact_divisions+=1
        prev=pivot
    negative=sum(int(signs[i]!=signs[i-1]) for i in range(1,len(signs)))
    return negative,exact_divisions,max_bits,signs

def run(binary,source,output):
    source_digest=check_class(source)
    keys,mags,W,adj,directed=parse_graph(binary)
    mu,support=moments(keys,mags,W,adj)
    Ksize=K+1
    gram=[[mu[i+j] for j in range(Ksize)] for i in range(Ksize)]
    ng,divg,bg,gsigns=exact_inertia_symmetric(gram)
    assert ng==0 and all(s==1 for s in gsigns),"Krylov Gram is not positive definite"
    lines=[
        "KRYLOV_SOURCE|schema=GPT6-NONTRIV-R12-EXACT-V1|states=111906|directed_edges=%d|m0=9|r=12|binary_sha256=%s|m3_symmetry_source_sha256=%s|json=0"%
        (directed,BINARY_SHA,source_digest),
        "SEED|key_plus=%d|key_minus=%d|D3xD4_class=%d|equal_weights=6|zero_group_average=1|json=0"%
        (PLUS_KEY,MINUS_KEY,SYM_CLASS),
        "GRAM|dimension=%d|negative=%d|bareiss_exact_divisions=%d|max_leading_minor_bits=%d|positive_definite=PASS|json=0"%
        (Ksize,ng,divg,bg),
    ]
    for power,count in support:
        lines.append("KRYLOV_SUPPORT|power=%d|nonzero_states=%d|json=0"%(power,count))
    thresholds=[
        (10455,100,0),
        (10470,100,0),
        (1055,10,2),
        (110,1,4)
    ]
    for num,den,expected in thresholds:
        q=[[(SHIFT*den-num)*mu[i+j]-den*mu[i+j+1] for j in range(Ksize)]
           for i in range(Ksize)]
        neg,div,bits,signs=exact_inertia_symmetric(q)
        assert neg==expected,("frozen postexploration count not reproduced",num,den,neg,expected)
        lines.append("KRYLOV_INERTIA|threshold=%d/%d|dim=%d|negative=%d|exact_divisions=%d|max_leading_minor_bits=%d|arithmetic=INTEGER|json=0"%
                     (num,den,Ksize,neg,div,bits))
    lines += [
        "THEOREM|two_nontrivial_symmetry_eigenvalues_strictly_below=1055/10|finite_full_nonflat_H=YES|proof_type=RITZ_KRYLOV_NEGATIVE_FORM|requires_lattice_symmetry_commutation=YES|json=0",
        "LIMIT|nontrivial_sector_lower_bounds_NOT_PROVED|tail_not_needed_for_zero_extended_trial_upper_bounds|zero_group_average_source=EXACT_SYMMETRY_ORBIT|r9=HOLD|json=0",
        "KRYLOV_NONTRIV_R12_REPLAY_PASS|dimension=%d|negative_below1055_over10=2|r9=HOLD|json=0"%Ksize,
    ]
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text("\n".join(lines)+"\n",encoding="ascii")
    output.with_name(output.name+".sha256").write_text(
        sha256(output.read_bytes()).hexdigest()+"  "+output.name+"\n",encoding="ascii")
    print("\n".join(lines))

if __name__=="__main__":
    assert len(argv)==4
    run(Path(argv[1]),Path(argv[2]),Path(argv[3]))
