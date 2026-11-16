#!/usr/bin/env python3
"""Exact accepted-K3 degree-2 Schur bracket from ONLY real mu0,mu1,mu2.

For spectrum g<=X<=h:
 (X-g)(X-h)^2>=0 and (h-X)(X-g)^2>=0
 imply rigorous 8x8 Loewner matrices L3 <= mu3 <= H3.
The actual degree-2 Chebyshev corrected Schur center is affine in mu3.
Take its certified lower and upper matrix substitutions, then include
the full-Q residual contraction d^4/(g*K2^2) mu0.
Uses accepted historical integer source units: NO extra factor 1e9.
Does not claim an exact mu3 or the degree-11 Wilson weight.
"""
import hashlib
import os
from itertools import combinations

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
CACHE=os.path.join(ROOT,"independent",
                   "y137-shell4-diagonal-cache-20261114",
                   "RESULT-MAGNETIC-CACHE.hbp")
MU1=os.path.join(ROOT,"independent",
                 "y137-real-Q-moment-20261114","RESULT-MU1.hbp")
MU2=os.path.join(ROOT,"independent",
                 "y137-d11-shell5-spill-20261114","RESULT-MU2.hbp")
N1=os.path.join(ROOT,"independent",
                "y137-real-Q-moment-20261114","RESULT-N1.hbp")
BLOBS={
 "source":"6454216973b8e59d65174c7cadc4f22c7dcf0354",
 "mu1":"86abf9611f8b9df5e03e796e81f513cba826c085",
 "mu2":"31de869725d0e760e650365d4c386b4b2fd722e6",
 "n1":"6021f9e24532132fa52bc8ffa5477ef08e7430c8",
}
Z=(69909875505,69949729820)
N=8
B=1000000000


def need(cond,reason):
    if not cond:
        print("Y137_N2_ENVELOPE_REFUSE|reason="+reason+"|json=0",flush=True)
        raise SystemExit(1)


def emit(label,**entries):
    print(label+"|"+"|".join(str(k)+"="+str(v)
                           for k,v in entries.items())+"|json=0",flush=True)


def blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\x00"+data).hexdigest()


def read(path,pin,tag):
    raw=open(path,"rb").read()
    need(blob(raw)==BLOBS[pin],"immutable_"+pin+"_source_changed")
    lines=[]
    for line in raw.decode("utf-8").splitlines():
        if not line.startswith(tag+"|"):
            continue
        d={}
        for p in line.split("|")[1:]:
            need("=" in p,"malformed_source_row")
            k,v=p.split("=",1)
            need(k not in d,"duplicate_source_field")
            d[k]=v
        lines.append(d)
    need(len(lines)==2,"wrong_frozen_sample_count_"+pin)
    return lines


def matrix(text):
    m=[[int(x) for x in row.split(",")] for row in text.split(";")]
    need(len(m)==N and all(len(row)==N for row in m),"8x8_shape")
    return m


def encode(m):
    return ";".join(",".join(str(x) for x in row) for row in m)


def sha(m):
    return hashlib.sha256("|".join(str(x) for row in m for x in row)
                          .encode("ascii")).hexdigest()


def add(a,b):
    return [[a[i][j]+b[i][j] for j in range(N)] for i in range(N)]


def scale(a,n):
    return [[n*x for x in row] for row in a]


def sub(a,b):
    return add(a,scale(b,-1))


def determinant(a):
    n=len(a)
    need(n>0 and all(len(row)==n for row in a),"square_determinant")
    t=[row[:] for row in a]
    sign=1
    prev=1
    for k in range(n-1):
        if t[k][k]==0:
            swap=next((i for i in range(k+1,n) if t[i][k]),None)
            if swap is None:
                return 0
            t[k],t[swap]=t[swap],t[k]
            sign=-sign
        piv=t[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                x=piv*t[i][j]-t[i][k]*t[k][j]
                need(x%prev==0,"Bareiss_fraction_free_fault")
                t[i][j]=x//prev
        for i in range(k+1,n):
            t[i][k]=0
        prev=piv
    return sign*t[-1][-1]


def psd(a):
    need(all(a[i][j]==a[j][i] for i in range(N)
             for j in range(N)),"nonsymmetric_Loewner_matrix")
    for degree in range(1,N+1):
        for ix in combinations(range(N),degree):
            if determinant([[a[i][j] for j in ix] for i in ix])<0:
                return False
    return True


def inertia(a):
    need(all(a[i][j]==a[j][i] for i in range(N)
             for j in range(N)),"nonsymmetric_inertia_matrix")
    old=1
    negative=0
    for n in range(1,N+1):
        q=determinant([row[:n] for row in a[:n]])
        need(q!=0,"zero_leading_minor_independent_inertia_HOLD")
        negative+=int((q<0)!=(old<0))
        old=q
    return negative


def linear(a,b,fa,fb):
    return add(scale(a,fa),scale(b,fb))


def certify(sample,mu1_src,mu2_src,n1_src,index):
    z=Z[index]
    need(int(sample["sample_num"])==z and
         int(mu1_src["sample_num"])==z and
         int(mu2_src["sample_num"])==z and
         int(n1_src["sample_num"])==z,"sample_energy_alignment")
    U0=matrix(sample["U0"])
    G=matrix(sample["G0"])
    need(sha(U0)==sample["U_sha256"] and
         sha(G)==sample["G_sha256"],"historical_U_G_hash")
    need(all(x%6==0 for row in G for x in row),
         "accepted_W_metric_divisibility")
    M0=[[x//6 for x in row] for row in G]
    M1=matrix(mu1_src["exact_mu1_8x8"])
    M2=matrix(mu2_src["actual_K3_mu2_8x8"])
    need(sha(M0)==mu1_src["wholeQ_mu0_sha256"]==
         mu2_src["actual_K3_mu0_sha256"] and
         sha(M1)==mu1_src["wholeQ_mu1_sha256"]==
         mu2_src["actual_K3_mu1_sha256"] and
         sha(M2)==mu2_src["actual_K3_mu2_sha256"],
         "frozen_three_real_moment_hashes")
    g=94068200000-z
    h=468000000000-z
    need(g>0 and h>g,"accepted_global_Q_spectrum")
    s=g+h
    d=h-g
    localizers=(
        sub(M1,scale(M0,g)),
        sub(scale(M0,h),M1),
        sub(M2,scale(M1,g)),
        sub(scale(M1,h),M2),
        sub(sub(scale(M1,s),M2),scale(M0,g*h)),
    )
    need(all(psd(L) for L in localizers),
         "real_moment_global_spectral_localizer")
    # Positivity of (X-g)(X-h)^2 and (h-X)(X-g)^2
    # gives rigorous source-conditional lower and upper mu3 matrices.
    L3=add(sub(scale(M2,2*h+g),
               scale(M1,h*h+2*g*h)),scale(M0,g*h*h))
    H3=add(sub(scale(M2,h+2*g),
               scale(M1,g*g+2*g*h)),scale(M0,g*g*h))
    mu3spread=sub(H3,L3)
    need(mu3spread==scale(localizers[4],d) and
         psd(mu3spread),"polynomial_mu3_envelope_algebra")
    # P2(X)=2(s-2X)^2-d^2 = K-8sX+8X^2.
    K=2*s*s-d*d
    need(K>d*d and K>0,"Chebyshev_degree2_normalizer")
    c0=16*K*s
    c1=-(64*s*s+16*K)
    c2=128*s
    c3=-64
    Cknown=add(add(scale(M0,c0),scale(M1,c1)),scale(M2,c2))
    base=sub(scale(U0,K*K),Cknown)
    # U2=U0-(Cknown-64*mu3)/K^2; monotone in unknown mu3.
    U2lo=add(base,scale(L3,-c3))
    U2hi=add(base,scale(H3,-c3))
    S2lo=sub(scale(U2lo,g),scale(M0,d*d*d*d))
    S2hi=U2hi
    need(psd(sub(S2hi,U2lo)) and
         psd(sub(scale(S2hi,g),S2lo)),
         "valid_source_degree2_Schur_interval")
    # The outer residual bound is (d^2/K)^2 mu0, with no extra b.
    need(sub(scale(U2lo,g),S2lo)==scale(M0,d*d*d*d),
         "wrong_fullQ_residual_squared_scale")
    oldlower=sub(scale(U0,g),M0)
    need(psd(sub(scale(U0,K*K),S2hi)) and
         psd(sub(S2lo,scale(oldlower,K*K))),
         "degree2_not_nested_in_original_accepted_bracket")
    N1u=matrix(n1_src["new_upper_numerator_8x8"])
    N1l=matrix(n1_src["new_lower_numerator_8x8"])
    need(int(n1_src["new_upper_denom"])==s*s and
         int(n1_src["new_lower_denom"])==g*s*s,
         "degree1_normalization_drift")
    low_versus_n1=sub(scale(S2lo,s*s),scale(N1l,K*K))
    need(psd(low_versus_n1),
         "degree2_lower_not_better_than_corrected_degree1")
    n1upper_dominates_n2=psd(
        sub(scale(N1u,K*K),scale(S2hi,s*s)))
    n2upper_dominates_n1=psd(
        sub(scale(S2hi,s*s),scale(N1u,K*K)))
    target=index+1
    oldcount=inertia(U0)
    negs=[oldcount,inertia(oldlower),inertia(N1u),inertia(N1l),
          inertia(S2hi),inertia(S2lo)]
    need(all(n==target for n in negs),
         "accepted_inertia_1_2_not_preserved")
    # Planted historical HIGH fault: another b on source moments.
    badupper=add(sub(scale(U0,K*K),
                     scale(Cknown,B)),scale(H3,64*B))
    need(not psd(sub(scale(badupper,g),
                     scale(oldlower,K*K))),
         "extra_1e9_source_unit_fault_not_refused")
    need(c3==-64,"Chebyshev_polynomial_sign")
    emit("Y137_N2_ENVELOPE_POINT",
         sample_num=z,den=B,
         degree=2,source_units="ACCEPTED_INTEGER_NO_EXTRA_B",
         mu3_exact="NOT_COMPUTED",
         mu3_lower_sha256=sha(L3),
         mu3_upper_sha256=sha(H3),
         mu3_lower_8x8=encode(L3),
         mu3_upper_8x8=encode(H3),
         Cheb_K2_num=K,
         residual_norm_contraction_num=d*d,
         residual_norm_contraction_den=K,
         fullQ_residual_Gram_contraction_num=d*d*d*d,
         fullQ_residual_Gram_contraction_den=K*K,
         source_Schur_upper_numerator=encode(S2hi),
         source_Schur_upper_den=K*K,
         source_Schur_upper_sha256=sha(S2hi),
         source_Schur_lower_numerator=encode(S2lo),
         source_Schur_lower_den=g*K*K,
         source_Schur_lower_sha256=sha(S2lo),
         original_accepted_bracket_nesting="PASS",
         lower_bound_improves_degree1="PASS",
         upper_bound_degree1_comparable=int(
             n1upper_dominates_n2 or n2upper_dominates_n1),
         accepted_inertia=target,
         degree2_upper_inertia=negs[-2],
         degree2_lower_inertia=negs[-1],
         billion_scale_fault="REFUSED",
         true_degree11_Schur="HOLD",Wilson_weight="HOLD")
    return (z,sha(S2hi),sha(S2lo))


def main():
    S=read(CACHE,"source","Y137_CACHE_POINT")
    M1=read(MU1,"mu1","Y137_MU1_COMPLETE_POINT")
    M2=read(MU2,"mu2","Y137_D11_MU2_POINT")
    N1ROWS=read(N1,"n1","Y137_N1_POINT")
    results=[]
    for i in range(2):
        results.append(certify(S[i],M1[i],M2[i],N1ROWS[i],i))
    need(len(results)==2,"no_complete_original_energy_samples")
    emit("Y137_N2_ENVELOPE_VERDICT",
         accepted_real_moment_orders="0,1,2",
         actual_mu3="NOT_COMPUTED",
         spectral_mu3_polynomial_bounds="PASS",
         exact_degree2_Schur_8x8_sandwich="PASS",
         both_original_energy_inertia="1,2",
         original_Schur_nesting="PASS",
         lower_improves_n1="PASS",
         planted_billion_source_unit_error="REFUSED",
         degree11_real_moments_remaining=19,
         full_source_72_move_independence="PENDING",
         actual_first_Wilson_weight="HOLD",issue_137="OPEN")


if __name__=="__main__":
    main()
