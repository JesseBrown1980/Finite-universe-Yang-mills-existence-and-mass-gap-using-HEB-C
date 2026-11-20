#!/usr/bin/env python3
"""Source-linked frozen-sample Schur projector diagnostic.
Uses authenticated original signed-mu3 four-moment matrices from research #317.
This is a *sample-energy diagnostic*, never a certificate for true eigenprojectors.
"""
import json
import os
import sys
from fractions import Fraction as F
from math import isqrt

HERE=os.path.dirname(os.path.abspath(__file__))
INDEP=os.path.dirname(HERE)
for name in ("y137-four-moment-fullstate-20261116", "y137-independent-premise-audit-20261118"):
    sys.path.insert(0,os.path.join(INDEP,name))
sys.path.insert(0,HERE)
import four_moment_transfer as e
import check_projector as c

def ceilrootfrac(x,den=10**12):
    assert x>=0
    n=(x.numerator*den*den+x.denominator-1)//x.denominator
    v=isqrt(n)
    if v*v<n:v+=1
    return F(v,den)

def as_fraction(x):
    # Historical Stage D defines its own rational type with (n,d) fields.
    # Explicit conversion avoids silently introducing floating point.
    if isinstance(x, F):
        return x
    if hasattr(x, "numerator") and hasattr(x, "denominator"):
        return F(int(x.numerator), int(x.denominator))
    if isinstance(x, int):
        return F(x)
    raise TypeError("unsupported exact rational source: " + type(x).__name__)

def midpoint(A,B):
    return [[(as_fraction(A[i][j])+as_fraction(B[i][j]))/2
             for j in range(8)] for i in range(8)]

def certificate(i,authentic):
    z,lo,hi,v0,_,gap,_=e.ra.ROWS[i]
    U0,m0,m1,m2=e.source.accepted_old_moments(i)
    m3=e.exact.F(authentic[z])
    L,U=e.exact.bracket4(U0,m0,m1,m2,m3,e.FLOOR-z,468000000000-z)
    assert e.exact.pd(e.exact.sub(U,L))
    cn,cd,wn,wd=e.all_refs(L,U)["CENTRE"]
    v1=e.ra.recentre(cn,list(v0))
    options=[]
    windows=e.three_moment_windows()
    for k in range(6):
        v=[(4-k)*v0[j]+k*v1[j] for j in range(8)]
        ang=e.ra.angle(cn,cd,wn,wd,v,z,lo,hi,gap)
        dist=e.flat_distance(list(v0),v)
        qlo,qhi=e.fw.Q_NORMS[i]
        spread=e.ra.ceil_div(e.fw.B_NORM_UP*dist*e.DEN,e.UNIT*(e.FLOOR-z))
        qlo=max(0,qlo-spread);qhi+=spread
        drift=max(z-lo,hi-z)
        mu0=ang["mu"]-ang["extra"]-e.ra.ceil_div(drift*e.UNIT,e.DEN)
        sep=(windows[1][0]-windows[0][1])*e.UNIT//e.DEN if i==0 else min(windows[1][0]-windows[0][1],e.ra.E3_LO-windows[1][1])*e.UNIT//e.DEN
        full=e.fw.compose(ang["Hcenter"]+ang["action"],mu0,sep,z,windows[i][0],windows[i][1],qlo,qhi)
        # The published flat_sine conversion is a strictly monotone function of direct error.
        options.append((full["error"],k,v))
    _,k,v=min(options)
    # Keep basis scaling explicit. All calculations here are at the frozen z.
    T=midpoint(L,U)
    scale=max(abs(x) for row in T for x in row)
    assert scale>0
    low=[[as_fraction(x)/scale for x in row] for row in L]
    high=[[as_fraction(x)/scale for x in row] for row in U]
    T=midpoint(low,high)
    W=[F(x) for x in e.WF]
    norm=sum(W[j]*v[j]*v[j] for j in range(8))
    Tv=[sum(T[j][k]*v[k]/W[j] for k in range(8)) for j in range(8)]
    avg=sum(W[j]*v[j]*Tv[j] for j in range(8))/norm
    rsq=sum(W[j]*(Tv[j]-avg*v[j])**2 for j in range(8))/norm
    err=ceilrootfrac(rsq)
    # Outward upper bound on the weighted Frobenius operator norm of
    # (U-L)/2; never divide by an upper bound for sqrt(W_i W_j).
    envelope_sq=sum(((high[j][k]-low[j][k])/2)**2/(W[j]*W[k])
                    for j in range(8) for k in range(8))
    w=ceilrootfrac(envelope_sq)
    eta=w
    pivot=max(range(8),key=lambda j:abs(W[j]*v[j]))
    assert v[pivot]
    vectors=[]
    for j in range(8):
        if j==pivot:continue
        b=[F(0)]*8;b[j]=1;b[pivot]=-W[j]*v[j]/(W[pivot]*v[pivot]);vectors.append(b)
    B=c.transpose(vectors)
    G=[[sum(W[k]*B[k][a]*B[k][b] for k in range(8)) for b in range(7)] for a in range(7)]
    K=[[sum(B[k][a]*T[k][l]*B[l][b] for k in range(8) for l in range(8)) for b in range(7)] for a in range(7)]
    Ginv=c.inverse(G)
    KK=c.mul(c.mul(K,Ginv),K)
    def separation(d):
        return c.pd(c.diff(KK,c.scaled(G,d*d)))
    # Exact lower singular separation; search binary fractions with strict positivity.
    candidate=F(1)
    while candidate>F(1,2**30) and not separation(candidate):
        candidate/=2
    d0=candidate if separation(candidate) else F(0)
    delta=d0-eta
    target=F((2362700330,5047836049)[i],10**12)
    rho=err+eta
    # Sample only, physical energy drift is not included. Conditional algebra verdict.
    angle=("SAMPLE_PASS" if delta>0 and rho*rho*(1-target*target)<=target*target*delta*delta else "SAMPLE_HOLD")
    return {"sample_num":z,"selected_fraction_num":k,"selected_fraction_den":4,
       "sample_only":True,"true_energy_projector":"FORMAL_HOLD",
       "matrices_source":"PINNED_ORIGINAL_SIGNED_MU3", "source_matched_direction":",".join(map(str,v)),
       "residual_sqrt_upper":str(err),"envelope_upper":str(eta),
       "singular_sample_lower":str(d0),"singular_window_lower_NOT_CERTIFIED":str(delta),
       "sample_angular_verdict":angle, "target_sine":str(target),
       "original_Wilson":"FORMAL_HOLD"}

def main():
    with open(e.source.MU3_FILE,encoding="ascii") as f:
        authentic=e.source.parse_pinned_mu3(f.read())
    assert as_fraction(e.exact.Ratio(2,3))==F(2,3)
    print("Y137_RATIO_ADAPTER|original_Ratio=PASS|json=0",flush=True)
    for i in range(2):
        item=certificate(i,authentic)
        print("Y137_SCHUR_SAMPLE_DIAGNOSTIC|"+json.dumps(item,sort_keys=True),flush=True)
if __name__=="__main__":main()
