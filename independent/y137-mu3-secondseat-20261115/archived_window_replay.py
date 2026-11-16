#!/usr/bin/env python3
"""Separate exact replay of the real #137 8x8 mu3 moment window.

No imports from the original mu3_acceptance or moment_radau sources.
Uses its own rational Gauss-Jordan solver and PSD Schur elimination.
Pins original Git blob bytes and checks all original moment hashes.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib

ROOT=Path(__file__).resolve().parents[2]
FILES=[
 ("cache","independent/y137-shell4-diagonal-cache-20261114/RESULT-MAGNETIC-CACHE.hbp",
  "6454216973b8e59d65174c7cadc4f22c7dcf0354","Y137_CACHE_POINT"),
 ("mu1","independent/y137-real-Q-moment-20261114/RESULT-MU1.hbp",
  "86abf9611f8b9df5e03e796e81f513cba826c085","Y137_MU1_COMPLETE_POINT"),
 ("mu2","independent/y137-d11-shell5-spill-20261114/RESULT-MU2.hbp",
  "31de869725d0e760e650365d4c386b4b2fd722e6","Y137_D11_MU2_POINT"),
 ("n2","independent/y137-d11-mu3-envelope-n2-schur-20261114/RESULT-N2.hbp",
  "4ecc2b5888e55edde0f54bb670fb723a2c678e9d","Y137_N2_ENVELOPE_POINT"),
 ("acceptance","independent/y137-mu3-acceptance-20261115/RESULT-MU3-ACCEPTANCE.hbp",
  "257a7778aaab4ec7c742f0b790b24579c3b20a87","Y137_MU3_WINDOW"),
]
N=8
Z=[69909875505,69949729820]
B=1_000_000_000

def need(p,tag):
    if not p:
        raise RuntimeError("Y137_SECONDSEAT_REFUSE_"+tag)

def git_blob_sha(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()

def read(tag,path,pin,record):
    raw=(ROOT/path).read_bytes()
    need(git_blob_sha(raw)==pin,"SOURCE_BLOB_"+tag)
    rows=[]
    for s in raw.decode("utf-8").splitlines():
        if not s.startswith(record+"|"):continue
        cells={}
        for item in s.split("|")[1:]:
            need("=" in item,"MALFORMED_"+tag)
            k,v=item.split("=",1)
            need(k not in cells,"DUPLICATE_"+tag)
            cells[k]=v
        rows.append(cells)
    need(len(rows)==2,"WRONG_SAMPLES_"+tag)
    return rows

def mat(raw):
    a=[[Q(int(x)) for x in row.split(",")] for row in raw.split(";")]
    need(len(a)==N and all(len(row)==N for row in a),"MATRIX_SHAPE")
    return a

def zero(n=N):
    return [[Q(0) for _ in range(n)] for _ in range(n)]

def eye(n=N):
    m=zero(n)
    for i in range(n):m[i][i]=Q(1)
    return m

def plus(a,b):
    return [[v+w for v,w in zip(x,y)] for x,y in zip(a,b)]

def minus(a,b):
    return [[v-w for v,w in zip(x,y)] for x,y in zip(a,b)]

def times(a,s):
    return [[v*s for v in row] for row in a]

def product(a,b):
    n=len(a); r=len(b[0]); k=len(b)
    return [[sum((a[i][t]*b[t][j] for t in range(k)),Q(0))
             for j in range(r)] for i in range(n)]

def transpose(a):
    return [list(row) for row in zip(*a)]

def sym(a):
    return all(a[i][j]==a[j][i] for i in range(len(a)) for j in range(len(a)))

def inverse(a):
    n=len(a)
    w=[list(r)+list(e) for r,e in zip(a,eye(n))]
    for j in range(n):
        p=next((i for i in range(j,n) if w[i][j]),None)
        need(p is not None,"SINGULAR_INV")
        w[j],w[p]=w[p],w[j]
        mult=Q(1)/w[j][j]
        w[j]=[v*mult for v in w[j]]
        for i in range(n):
            if i==j or w[i][j]==0:continue
            c=w[i][j]
            w[i]=[v-c*t for v,t in zip(w[i],w[j])]
    v=[r[n:] for r in w]
    need(product(a,v)==eye(n),"INVERSE_IDENTITY")
    return v

def psd(a):
    # Independent rational Schur-elimination PSD proof. A zero
    # diagonal of a PSD matrix requires its entire remaining row zero.
    need(sym(a),"PSD_SYMMETRY")
    n=len(a)
    t=[list(r) for r in a]
    for k in range(n):
        p=t[k][k]
        if p<0:return False
        if p==0:
            if any(t[k][i]!=0 for i in range(k+1,n)):return False
            continue
        for i in range(k+1,n):
            for j in range(i,n):
                x=t[i][j]-t[i][k]*t[k][j]/p
                t[i][j]=t[j][i]=x
        for i in range(k+1,n):
            t[k][i]=t[i][k]=Q(0)
    return True

def pd(a):
    # This separately checks SPD using strict pivots, unlike the author's
    # 255-principal-minor determinant route.
    need(sym(a),"PD_SYMMETRY")
    n=len(a)
    t=[list(r) for r in a]
    for k in range(n):
        p=t[k][k]
        if p<=0:return False
        for i in range(k+1,n):
            for j in range(i,n):
                t[i][j]=t[j][i]=t[i][j]-t[i][k]*t[k][j]/p
    return True

def tr(a):
    return sum((a[i][i] for i in range(len(a))),Q(0))

def ratio_floor(a,b):
    need(a>=0 and b>0,"BAD_WIDTH")
    q=a*1_000_000/b
    return q.numerator//q.denominator

def old_sha(a):
    need(all(v.denominator==1 for row in a for v in row),"OLD_SOURCE_NONINTEGER")
    return hashlib.sha256("|".join(str(v.numerator) for row in a for v in row).encode("ascii")).hexdigest()

def canonical_sha(a):
    return hashlib.sha256("|".join(str(v.numerator)+"/"+str(v.denominator) for row in a for v in row).encode("ascii")).hexdigest()

def rat(i,j):
    return product(product(i,inverse(j)),transpose(i))

def check(idx,files):
    z=Z[idx]
    s,m1,m2,n2,stored=[files[x][idx] for x in ("cache","mu1","mu2","n2","acceptance")]
    need(all(int(r["sample_num"])==z for r in (s,m1,m2,n2,stored)),"MISALIGNED_ENERGIES")
    U0=mat(s["U0"])
    G0=mat(s["G0"])
    need(all(x.denominator==1 and x.numerator%6==0 for row in G0 for x in row),"G0_OVER_SIX")
    M0=times(G0,Q(1,6))
    M1=mat(m1["exact_mu1_8x8"])
    M2=mat(m2["actual_K3_mu2_8x8"])
    need(old_sha(M0)==m1["wholeQ_mu0_sha256"]==m2["actual_K3_mu0_sha256"],"MU0_SOURCE_HASH")
    need(old_sha(M1)==m1["wholeQ_mu1_sha256"]==m2["actual_K3_mu1_sha256"],"MU1_SOURCE_HASH")
    need(old_sha(M2)==m2["actual_K3_mu2_sha256"],"MU2_SOURCE_HASH")
    g=Q(94068200000-z);h=Q(468000000000-z)
    need(g>0 and h>g,"ORIGINAL_Q_SPECTRUM")
    D=minus(M1,times(M0,g));C=minus(M2,times(M1,g))
    E=minus(times(M0,h),M1);G=minus(times(M1,h),M2)
    need(pd(D) and pd(E),"HANKEL_PIVOT_PD")
    lower=plus(times(M2,g),rat(C,D))
    upper=minus(times(M2,h),rat(G,E))
    need(psd(minus(upper,lower)),"MU3_WINDOW_EMPTY")
    # Independent cubic-envelope calculation from spectral nonnegative
    # polynomials; also require the original archived integer matrices.
    l3=plus(minus(times(M2,2*h+g),times(M1,h*h+2*g*h)),times(M0,g*h*h))
    h3=plus(minus(times(M2,h+2*g),times(M1,g*g+2*g*h)),times(M0,g*g*h))
    need(l3==mat(n2["mu3_lower_8x8"]) and h3==mat(n2["mu3_upper_8x8"]),"CUBIC_ENVELOPE_SOURCE")
    need(psd(minus(lower,l3)) and psd(minus(h3,upper)),"WINDOW_NOT_NESTED")
    ratio=ratio_floor(tr(minus(upper,lower)),tr(minus(h3,l3)))
    need(ratio==int(stored["window_trace_per_million_of_197_envelope"]),"WINDOW_WIDTH_DISAGREEMENT")
    # Current upstream rational hash is numerator-only: check matching
    # physical data, then provide an unambiguous canonical hash.
    from math import lcm
    def old_to_int(a):
        d=1
        for row in a:
            for v in row:d=lcm(d,v.denominator)
        return [[v*d for v in row] for row in a]
    need(old_sha(old_to_int(lower))==stored["window_lower_integer_sha256"],"OLD_LOWER_SHA_DISAGREEMENT")
    need(old_sha(old_to_int(upper))==stored["window_upper_integer_sha256"],"OLD_UPPER_SHA_DISAGREEMENT")
    print("Y137_SECONDSEAT_ARCHIVED|sample_num="+str(z)+"|source_mu0_mu1_mu2=PINNED|window_inside_cubic=PASS|window_width_per_million="+str(ratio)+"|different_exact_psd_method=PASS|new_lower_canonical_sha256="+canonical_sha(lower)+"|new_upper_canonical_sha256="+canonical_sha(upper)+"|Wilson_weight=HOLD|json=0",flush=True)

def main():
    files={tag:read(tag,path,pin,record) for tag,path,pin,record in FILES}
    for i in range(2):check(i,files)
    print("Y137_SECONDSEAT_ARCHIVED_VERDICT|two_real_samples_independently_replayed=PASS|numerator_only_hash_collision_control=SEPARATELY_PROVEN|real_mu3=NOT_COMPUTED|Wilson_weight=HOLD|json=0",flush=True)

if __name__=="__main__":main()
