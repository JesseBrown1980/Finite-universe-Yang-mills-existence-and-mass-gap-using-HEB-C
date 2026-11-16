#!/usr/bin/env python3
"""Exact two-state Rayleigh--Ritz UPPER witnesses inside the H20736 sparse space.

Reconstruct original 144D rational resolvent-probe vectors at their exact
frozen Ritz upper endpoints. Add exact diagonal-Jacobi shell3 coordinates
from the stored authenticated H20736 sparse weighted generalized pencil.
Certify the *2-dimensional subspace* generalized Ritz eigenvalues by
integer 2x2 Sylvester inertia (no large sparse eigensolver required).

These are valid variational UPPER bounds for the first two eigenvalues
provided the full sparse projected source is accepted. They are NOT
full-space eigenstate residual or Wilson spectral-weight certificates.
"""
import hashlib
import os
import sys
from math import gcd

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
SPARSE=os.path.join(ROOT,"build","y137-h20736","H20736-SPARSE-UPPER.tsv")
RESULT=os.path.join(ROOT,"build","y137-h20736","RESULT-H20736.hbp")
SOURCE_BLOB="d0d9d3d14d804450a31ed8e98c01a031b9a53596"
SPARSE_SOURCE=os.path.join(HERE,"sparse_h20736.py")
D=1000000000
N=20736
BASE=144
FROZEN=((69924497998,69924497999),
        (69963565333,69963565334))


def need(ok,why):
    if not ok:
        print("Y137_H20736_TWO_REFUSE|reason="+why+"|json=0",flush=True)
        raise SystemExit(1)


def emit(label,**parts):
    print(label+"|"+"|".join(k+"="+str(v) for k,v in parts.items())
          +"|json=0",flush=True)


def gitblob(path):
    b=open(path,"rb").read()
    return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")
                        +b"\x00"+b).hexdigest()


def signed_hash(a):
    return hashlib.sha256(",".join(str(x) for x in a)
                          .encode("ascii")).hexdigest()


def source():
    need(gitblob(SPARSE_SOURCE)==SOURCE_BLOB,"source_H20736_not_frozen")
    raw=open(SPARSE,"rb").read()
    digest=hashlib.sha256(raw).hexdigest()
    lines=open(RESULT,encoding="ascii").read().splitlines()
    original=[s for s in lines if s.startswith("Y137_H20736_MATRIX|")]
    need(len(original)==1,"missing_source_sparse_hash")
    fields=dict(term.split("=",1) for term in original[0].split("|")[1:]
                if "=" in term)
    need(fields.get("sparse_TSV_sha256")==digest
         and fields.get("basis_dim")=="20736"
         and fields.get("upper_triangle_stored_nonzero")=="98704",
         "original_sparse_full_matrix_not_authenticated")
    a=[]
    prev=None
    with open(SPARSE,encoding="ascii") as fd:
        for s in fd:
            tag,i,j,v=s.strip().split("\t")
            i,j,v=int(i),int(j),int(v)
            need(tag in ("G","K") and 0<=i<=j<N and v!=0,
                 "malformed_sparse_galerkin_entry")
            item=(tag,i,j)
            need(prev is None or item>prev,"unsorted_or_duplicate_sparse_entry")
            prev=item
            a.append((tag,i,j,v))
    need(len(a)==98704,"authentic_full_matrix_entry_count")
    return a,digest


def original_144_trials():
    sys.path.insert(0,os.path.join(ROOT,"independent",
                                   "y137-h144-nested-20261116"))
    sys.path.insert(0,os.path.join(ROOT,"independent",
                                   "y137-12x12-krylov-20261116"))
    import nested_ritz as n
    import full_residual as r
    G12,K12=n.load_h12()
    ball,states,cols,actions=n.sources()
    chosen,score=n.select(ball,cols,actions)
    G,K=n.expanded_matrices(ball,cols,actions,chosen,G12,K12)
    groups=n.group_schur(ball,cols,actions,chosen)
    bracket=[n.exact_bracket(k,G12,K12,groups) for k in (1,2)]
    need(tuple(bracket)==FROZEN,"frozen_H144_Ritz_drift")
    samples=[]
    for level in (1,2):
        z=bracket[level-1][1]
        schur=r.exact_schur(z,G12,K12,groups)
        probe=0 if level==1 else 3
        core=r.solve_int_symmetric(schur,probe)
        trial=r.integer_coefficients(z,core,chosen,ball,cols,actions)
        need(len(trial)==144 and any(trial[:8]),
             "original_144_trial_not_recreated")
        samples.append((z,trial))
    return samples


def lcm(a,b):
    return a//gcd(a,b)*b


def augmented(samples,entries):
    # Offdiagonal original 144 to new shell3 and exact selected shell3
    # Gram and diagonal Hamiltonian; the Gram cross is identically zero.
    diagH=[0]*(N-BASE)
    diagG=[0]*(N-BASE)
    links=[[] for unused in range(N-BASE)]
    for tag,i,j,v in entries:
        if i>=BASE and i==j:
            (diagG if tag=="G" else diagH)[i-BASE]=v
        elif i<BASE and j>=BASE and tag=="K":
            links[j-BASE].append((i,v))
        elif i<BASE and j>=BASE and tag=="G":
            need(False,"old_144_shell3_metric_cross_nonzero")
    need(all(x>0 for x in diagG) and all(x>0 for x in diagH),
         "missing_positive_exterior_coordinate_diagonals")
    out=[]
    for z,x in samples:
        y_rat=[]
        denom=1
        for i in range(N-BASE):
            h=diagH[i]
            g=diagG[i]
            den=D*h-z*g
            need(den>0,"new_shell3_Jacobi_not_strictly_positive")
            numer=-D*sum(v*x[k] for k,v in links[i])
            common=gcd(abs(numer),den)
            p,q=numer//common,den//common
            y_rat.append((p,q))
            denom=lcm(denom,q)
        values=[c*denom for c in x]+[p*(denom//q) for p,q in y_rat]
        scale=0
        for v in values:
            scale=gcd(scale,abs(v))
        need(scale>0,"zero_new_resolvent_trial")
        values=[c//scale for c in values]
        need(len(values)==N,"wrong_augmented_vector_len")
        out.append((z,values))
    return out


def gram_hamiltonian(xs,entries):
    W=[[0,0],[0,0]]
    K=[[0,0],[0,0]]
    for tag,i,j,value in entries:
        tar=W if tag=="G" else K
        for a in range(2):
            for b in range(a,2):
                term=xs[a][i]*xs[b][j]
                if i!=j:
                    term+=xs[a][j]*xs[b][i]
                tar[a][b]+=value*term
    for T in (W,K):
        T[1][0]=T[0][1]
    need(W[0][0]>0 and W[1][1]>0
         and W[0][0]*W[1][1]>W[0][1]*W[0][1],
         "two_new_trials_not_independent")
    return W,K


def inertia(G,K,z):
    a=D*K[0][0]-z*G[0][0]
    b=D*K[0][1]-z*G[0][1]
    d=D*K[1][1]-z*G[1][1]
    det=a*d-b*b
    need(a!=0 and det!=0,"zero_2by2_inertia_endpoint")
    count=int(a<0)+int((det<0)!=(a<0))
    return count


def bracket(G,K,level):
    lo,hi=0,72*D-1
    need(inertia(G,K,lo)<level and inertia(G,K,hi)>=level,
         "two_sample_Ritz_outside_original_spectral_window")
    while hi-lo>1:
        m=(lo+hi)//2
        if inertia(G,K,m)>=level:
            hi=m
        else:
            lo=m
    need(inertia(G,K,lo)==level-1
         and inertia(G,K,hi)==level,
         "exact_2by2_Ritz_not_bracketed")
    return lo,hi


def main():
    entries,digest=source()
    samples=original_144_trials()
    new=augmented(samples,entries)
    W,K=gram_hamiltonian([values for z,values in new],entries)
    brackets=[bracket(W,K,k) for k in (1,2)]
    emit("Y137_H20736_TWO_SOURCE",dimension=N,
         authenticated_sparse_sha256=digest,
         original_H144_two_trial_samples="EXACT_REBUILT",
         new_selected_shell3_diagonal="EXACT_JACOBI",
         two_sample_Gram="STRICT_POSITIVE",
         physical_metric="W_ORBIT",arithmetic="INTEGER_ONLY")
    for level,(z,v) in enumerate(new,1):
        emit("Y137_H20736_TWO_VECTOR",level=level,seed_Ritz_z_num=z,
             trial_length=len(v),trial_nonzero=sum(x!=0 for x in v),
             largest_signed_bit_length=max(abs(x).bit_length() for x in v),
             full_trial_SHA=signed_hash(v))
    for level,(lo,hi) in enumerate(brackets,1):
        prev_hi=FROZEN[level-1][1]
        improvement=prev_hi-hi
        need(hi<=prev_hi,"actual_new_trial_not_improving_old_144_accepted_upper")
        emit("Y137_H20736_TWO_RITZ",level=level,
             exact_lower_z_num=lo,exact_upper_z_num=hi,
             denominator=D, original_144_upper_z_num=prev_hi,
             strict_upper_improvement_z_num=improvement,
             certificate="EXACT_2D_SUBSPACE_MINMAX_UPPER")
    emit("Y137_H20736_TWO_VERDICT",
         authentic_20736_dimension="PASS",
         strict_positive_2D_Gram="PASS",
         exact_projection_of_2_new_resolvent_trials="PASS",
         original_full_20736_Ritz="NOT_COMPUTED",
         certified_two_trial_subspace_Ritz_upper="PASS",
         full_space_residual="NOT_COMPUTED",
         Wilson_weight="HOLD",issue_137="OPEN")


if __name__=="__main__":
    if sys.argv[1:]==["real"]:
        main()
    else:
        need(False,"use_real")
