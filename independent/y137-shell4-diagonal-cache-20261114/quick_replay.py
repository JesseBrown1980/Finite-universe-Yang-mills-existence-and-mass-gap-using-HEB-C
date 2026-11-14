#!/usr/bin/env python3
"""Hash-verified, graph-free 8x8 Schur inertia replays at frozen-trial energy offsets.

Uses only the archived exact magnetic-bucket Grams and first two moments.
A SHA is an address; the new energy result follows polynomial identities.
"""
import hashlib
import itertools
import os

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
RESULT=os.path.join(HERE,"RESULT-MAGNETIC-CACHE.hbp")
PRED=os.path.join(HERE,"PREDICTION.hbp")
B=1000000000
PS=1000000
FLOOR=94068200
SCALE=1000000000000
UNIT=1000000000000
WF=(1,3,2,3,3,2,2,2)
SAMPLES=(69909875505,69949729820)


def require(cond,msg):
    if not cond:
        raise SystemExit("Y137_QUICK_REFUSE|reason="+msg+"|json=0")


def rowparse(line):
    arr=line.split("|")
    fields={}
    for item in arr[1:]:
        require("=" in item,"malformed_field")
        name,value=item.split("=",1)
        require(name not in fields,"duplicate_field")
        fields[name]=value
    return arr[0],fields


def parse(path):
    text=open(path,"rb").read().decode("utf-8")
    return [rowparse(line) for line in text.splitlines()
            if line.strip() and not line.startswith("#")]


def matrix(code):
    A=[[int(a) for a in line.split(",")] for line in code.split(";")]
    require(len(A)==8 and all(len(row)==8 for row in A),"wrong_matrix_shape")
    require(all(A[i][j]==A[j][i] for i in range(8) for j in range(8)),
            "nonsymmetric_matrix")
    return A


def det(A):
    n=len(A)
    if n==0:
        return 1
    M=[row[:] for row in A]
    d=1
    sign=1
    for k in range(n-1):
        if M[k][k]==0:
            w=next((i for i in range(k+1,n) if M[i][k]),None)
            if w is None:
                return 0
            M[k],M[w]=M[w],M[k]
            sign=-sign
        pivot=M[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                num=pivot*M[i][j]-M[i][k]*M[k][j]
                require(num%d==0,"noninteger_Bareiss")
                M[i][j]=num//d
        for i in range(k+1,n):
            M[i][k]=0
        d=pivot
    return sign*M[-1][-1]


def psd(A):
    for mask in range(1,256):
        idx=[k for k in range(8) if mask&(1<<k)]
        small=[[A[i][j] for j in idx] for i in idx]
        if det(small)<0:
            return False
    return True


def inertia(A):
    """Count negative eigenvalues by exact leading principal minors.

    This is the Sylvester sign-variation rule for a symmetric matrix when
    every leading minor is nonzero. A zero minor is explicitly a HOLD,
    requiring an independent 2x2-pivot inertia route; it is not guessed.
    """
    require(len(A)==8 and all(len(r)==8 for r in A),
            "inertia_matrix_shape")
    require(all(A[i][j]==A[j][i] for i in range(8) for j in range(8)),
            "inertia_matrix_symmetry")
    neg=0
    prev=1
    for k in range(1,9):
        nxt=det([r[:k] for r in A[:k]])
        require(nxt!=0,"zero_leading_minor_requires_independent_inertia")
        if (prev<0)!=(nxt<0):
            neg+=1
        prev=nxt
    return neg,0

def build_bucket_map(raw):
    d={}
    for entry in raw.split("~"):
        name,mat=entry.split(":",1)
        q=int(name)
        require(q not in d and 4<=q<=16,"duplicate_or_bad_magnetic_bucket")
        d[q]=matrix(mat)
    require(16 in d and d,"missing_outer_magnetic_bucket")
    return d


def compute_at(r,z):
    U0=matrix(r["U0"])
    G0=matrix(r["G0"])
    H=matrix(r["Y_Gram"])
    J=matrix(r["G_linear"])
    z0=int(r["sample_num"])
    delta=z-z0
    U=[[U0[i][j]-delta*(H[i][j]+
        (SCALE*SCALE*WF[i] if i==j else 0))
        for j in range(8)] for i in range(8)]
    G=[[G0[i][j]-6*delta*J[i][j]+6*delta*delta*H[i][j]
        for j in range(8)] for i in range(8)]
    gamma=B*FLOOR-z*PS
    require(gamma>0 and psd(G),"resolvent_or_trial_residual")
    buckets=build_bucket_map(r["shell4_magnetic_gram"])
    denom=1
    for mm in buckets:
        denom*=(144+9*mm)*B-z
    numerator=[[sum(A[i][j]*(denom//((144+9*mm)*B-z))
                     for mm,A in buckets.items())
                for j in range(8)] for i in range(8)]
    if z==z0:
        require(denom==int(r["common_magnetic_den"]) and
                numerator==matrix(r["magnetic_weighted_num"]),
                "source_point_diagonal_cache_mismatch")
    width=[[PS*denom*G[i][j]-gamma*numerator[i][j]
           for j in range(8)] for i in range(8)]
    require(psd(width),"fullQ_width_PSD")
    # PSD matrix inequalities guarantee the exact inertia enclosure.
    Uupper=[[6*denom*U[i][j]-numerator[i][j]
             for j in range(8)] for i in range(8)]
    Llower=[[6*gamma*U[i][j]-PS*G[i][j]
             for j in range(8)] for i in range(8)]
    upperneg,upperzero=inertia(Uupper)
    lowerneg,lowerzero=inertia(Llower)
    require(upperneg <= lowerneg,"Schur_inertia_inconsistent")
    return upperneg,lowerneg,upperzero,lowerzero


def emit(label,**fields):
    print(label+"|"+"|".join(k+"="+str(v) for k,v in fields.items())+"|json=0",
          flush=True)


def main():
    pred=parse(PRED)
    require(pred[0][0]=="Y137_CACHE_PREHOST_FREEZE" and
            pred[0][1]["status"]=="PREHOST_FREEZE","prehost_pin_missing")
    grid=[int(i) for i in pred[3][1]["z_num"].split(",")]
    require(len(grid)==13 and len(set(grid))==13,"frozen_grid_size")
    blob=open(os.path.join(HERE,"source_cache.py"),"rb").read()
    calculated=hashlib.sha1(("blob "+str(len(blob))+"\0").encode()+blob).hexdigest()
    require(calculated==pred[0][1]["source_script_git_blob"],"source_script_modified")
    rec=parse(RESULT)
    require([x[0] for x in rec]==["Y137_CACHE_FREEZE","Y137_CACHE_SHELL4",
            "Y137_CACHE_POINT","Y137_CACHE_POINT","Y137_CACHE_VERDICT"],
            "not_exactly_two_source_samples")
    require(int(rec[1][1]["orbits"])==1985218,"source_shell4_census")
    require(rec[-1][1]["actual_first_Wilson_spectral_weight"]=="HOLD",
            "proof_scope_violation")
    points=[rec[2][1],rec[3][1]]
    require(tuple(int(x["sample_num"]) for x in points)==SAMPLES,
            "frozen_sample_mismatch")
    for i,r in enumerate(points):
        pin=pred[1+i][1]
        for key in ("U_sha256","G_sha256"):
            require(pin[key]==r[key],"historical_source_pin")
        for key,matkey in (("U_sha256","U0"),("G_sha256","G0")):
            values=matrix(r[matkey])
            digest=hashlib.sha256("|".join(str(n) for row in values for n in row)
                                  .encode("ascii")).hexdigest()
            require(digest==r[key],"raw_matrix_source_sha")
        sample_result=compute_at(r,int(r["sample_num"]))
        emit("Y137_QUICK_SOURCE",sample_num=r["sample_num"],
             source_U_sha=r["U_sha256"],source_G_sha=r["G_sha256"],
             new_gain_floor_per_trillion=r["upper_source_gain_floor_per_trillion"],
             sample_negative_inertia_lower=sample_result[0],
             sample_negative_inertia_upper=sample_result[1])
    for z in grid:
        bounds=[compute_at(r,z) for r in points]
        low=max(b[0] for b in bounds)
        high=min(b[1] for b in bounds)
        require(low<=high,"two_frozen_trials_inconsistent")
        emit("Y137_QUICK_GRID",z_num=z,den=B,
             negative_count_lower=low,negative_count_upper=high,
             two_trial_bounds="INTERSECTION",
             input_graph_rebuilt=0,
             true_spectral_weight="HOLD")
    emit("Y137_QUICK_VERDICT",precomputed_shell4_graph_reused=1,
         source_records=2,energy_thresholds=len(grid),
         integer_inertia_8x8="EXACT",
         actual_Wilson_first_spectral_weight="HOLD")


if __name__=="__main__":
    main()
