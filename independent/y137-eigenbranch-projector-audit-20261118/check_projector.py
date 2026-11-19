#!/usr/bin/env python3
"""Exact rational conditional projector-angle verifier; no float or numpy.
Reads an externally authenticated eight-flat Schur-envelope JSON.
Never promotes source provenance, branch identification, or Wilson status.
"""
import json
import sys
from fractions import Fraction as F

def need(ok, msg):
    if not ok: raise ValueError(msg)

def q(x):
    if isinstance(x,float): raise ValueError("float forbidden")
    return F(str(x))
def M(x): return [[q(t) for t in r] for r in x]
def transpose(A): return list(map(list,zip(*A)))
def mul(A,B):
    return [[sum((x*y for x,y in zip(r,c)),F(0)) for c in transpose(B)] for r in A]
def diff(A,B): return [[x-y for x,y in zip(r,s)] for r,s in zip(A,B)]
def scaled(A,t): return [[t*x for x in r] for r in A]
def inverse(A):
    n=len(A);T=[r[:]+[F(int(i==j)) for j in range(n)] for i,r in enumerate(A)]
    for j in range(n):
        k=next((i for i in range(j,n) if T[i][j]),None)
        if k is None:raise ValueError("singular")
        T[j],T[k]=T[k],T[j]
        v=T[j][j]; T[j]=[x/v for x in T[j]]
        for i in range(n):
            if i!=j:
                v=T[i][j];T[i]=[x-v*y for x,y in zip(T[i],T[j])]
    return [r[n:] for r in T]
def pd(A):
    A=[r[:] for r in A];n=len(A)
    if any(A[i][j]!=A[j][i] for i in range(n) for j in range(n)):return False
    for k in range(n):
        d=A[k][k]
        if d<=0:return False
        for i in range(k+1,n):
            for j in range(i,n):
                v=A[i][j]-A[i][k]*A[k][j]/d
                A[i][j]=v;A[j][i]=v
    return True
def verify(a):
    W=[q(t) for t in a["weights"]];n=len(W)
    need(n==8 and all(t>0 for t in W), 'positive_W_8')
    L,U=M(a["schur_lower"]),M(a["schur_upper"])
    need(len(L)==len(U)==n and all(len(r)==n for r in L+U), '8x8_shapes')
    need(all(L[i][j]==L[j][i] and U[i][j]==U[j][i] for i in range(n) for j in range(n)), 'W_bilinear_symmetry')
    D=diff(U,L)
    need(pd(D), 'strict_Loewner_ordering_not_certified')
    u=[q(t) for t in a["witness"]]
    need(len(u)==n, 'witness_dimension')
    nu=sum((W[i]*u[i]**2 for i in range(n)),F(0));need(nu>0, 'positive_witness_norm')
    z,gamma,b,drift=[q(a[k]) for k in ("sample_energy","gamma","upper_energy","window_drift")]
    need(z<=b<gamma and drift>=abs(b-z), 'energy_window')
    bn=q(a['coupling_norm_sq_upper']);need(bn>=0, 'coupling_cap')
    T=[[(L[i][j]+U[i][j])/(2*W[i]) for j in range(n)] for i in range(n)]
    Tu=[sum((T[i][j]*u[j] for j in range(n)),F(0)) for i in range(n)]
    alpha=sum((W[i]*u[i]*Tu[i] for i in range(n)),F(0))/nu
    rsq=sum((W[i]*(Tu[i]-alpha*u[i])**2 for i in range(n)),F(0))/nu
    wsq=sum((D[i][j]**2/(4*W[i]*W[j]) for i in range(n) for j in range(n)),F(0))
    w=q(a['envelope_norm_upper']);need(w>=0 and w*w>=wsq, 'weighted_envelope_bound')
    eta=w+(1+bn/(gamma-b)**2)*drift
    rho=q(a["projected_residual_upper"]);delta=q(a["compressed_singular_lower"])
    target=q(a["target_sine_upper"])
    need(rho>=eta and delta>0 and 0<target<1, 'positive_projector_inputs')
    need((rho-eta)**2>=rsq, 'residual_upper_failed')
    pivot=next(i for i in range(n) if u[i])
    cols=[]
    for j in range(n):
        if j==pivot:continue
        v=[F(0)]*n;v[j]=F(1)
        v[pivot]=-W[j]*u[j]/(W[pivot]*u[pivot]);cols.append(v)
    B=transpose(cols)
    G=[[sum((W[k]*B[k][i]*B[k][j] for k in range(n)),F(0))
       for j in range(n-1)] for i in range(n-1)]
    need(pd(G), 'positive_seven_dimensional_Gram')
    K=[[sum((B[k][i]*(L[k][l]+U[k][l])*B[l][j]/2
             for k in range(n) for l in range(n)),F(0))
       for j in range(n-1)] for i in range(n-1)]
    need(all(K[i][j]==K[j][i] for i in range(n-1) for j in range(n-1)), 'compressed_Schur_symmetry')
    gap=delta+eta
    need(pd(diff(mul(mul(K,inverse(G)),K),scaled(G,gap*gap))), 'compressed_singular_bound_failed')
    need(rho*rho*(1-target*target)<=target*target*delta*delta, 'target_sine_failed')
    return {"status":"CONDITIONAL_NUMERICAL_PASS","rho":str(rho),
            "delta":str(delta),"eta":str(eta),"target":str(target),
            "projector_angle":"PASS",
            "true_branch":"REQUIRES_ENDPOINT_INERTIA_PROOF",
            "full_Q_source":"REQUIRES_AUTHENTICATION",
            "first_wilson":"FORMAL_HOLD"}
def main():
    try:
        need(len(sys.argv)==2, 'usage: check_projector.py input.json')
        with open(sys.argv[1],encoding="utf-8") as h:
            a=json.load(h,parse_float=lambda _: (_ for _ in ()).throw(ValueError("float forbidden")))
        result=verify(a);code=0
    except (AssertionError,ValueError,KeyError,ZeroDivisionError,IndexError) as exc:
        result={"status":"HOLD","reason":str(exc),"first_wilson":"FORMAL_HOLD"};code=2
    print(json.dumps(result,sort_keys=True));raise SystemExit(code)
if __name__=="__main__":main()
