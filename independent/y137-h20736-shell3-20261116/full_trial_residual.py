#!/usr/bin/env python3
"""Exact whole-H residuals of two actual 20,736-dimensional rational Ritz witnesses.

Physical support: 8 flat, 8,034 original K2-Q, 147,344 K3 shell3,
and all touched original S3 shell4 gauge-orbit targets. No floating-point.

The source is authenticated by original 144 code and current 20,736 sparse
SHA receipts. Both new rational Ritz witnesses were certified by the
separate two_trial_ritz.py minmax algorithm. Physical W norm and
D*H-z applied amplitude are independently checked against xT G x and
xT(D K-zG)x from the EXACT sparse projected Hamiltonian.

No eigenstate-distance or Wilson spectral weight positivity is inferred.
"""
import hashlib
import os
import sys
from math import isqrt

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0,HERE)
import two_trial_ritz as tw

DEN=tw.D
UNIT=1000000000000


def need(x,msg):
    if not x:
        print("Y137_H20736_FULL_REFUSE|reason="+msg+"|json=0",flush=True)
        raise SystemExit(1)


def emit(label,**kwargs):
    print(label+"|"+"|".join(str(k)+"="+str(v) for k,v in kwargs.items())
          +"|json=0",flush=True)


def digest(v):
    return hashlib.sha256(",".join(str(x) for x in v)
                          .encode("ascii")).hexdigest()


def old_source():
    sys.path.insert(0,os.path.join(ROOT,"independent",
                                    "y137-h144-nested-20261116"))
    sys.path.insert(0,os.path.join(ROOT,"independent",
                                    "y137-12x12-krylov-20261116"))
    import nested_ritz as n
    G12,K12=n.load_h12()
    ball,states,cols,actions=n.sources()
    old132,score=n.select(ball,cols,actions)
    # Regenerated 144 leading block must still be the real immutable one.
    G,K=n.expanded_matrices(ball,cols,actions,old132,G12,K12)
    need(len(G)==144 and len(K)==144,"frozen_144_principal_missing")
    return ball,states,cols,old132


def physical_amplitudes(ball,cols,old132,newindices,trial):
    x=trial
    p=x[:8]
    q2=[sum(cols[a][i]*x[8+a] for a in range(4))
        for i in range(ball["n"])]
    for k,i in enumerate(old132):
        q2[i]+=x[12+k]
    q3=x[144:]
    need(len(p)==8 and len(q2)==8034
         and len(q3)==len(newindices)==20592,
         "wrong_exact_20k_physical_trial_support")
    return p,q2,q3


def inner_products(p,q2,q3,ball,indices):
    wf,wq,we=ball["wf"],ball["wq"],ball["eW"]
    norm=sum(wf[i]*v*v for i,v in enumerate(p))
    norm+=sum(wq[i]*v*v for i,v in enumerate(q2))
    norm+=sum(we[f]*v*v for f,v in zip(indices,q3))
    need(norm>0,"nonpositive_full_state_norm")
    return norm


def direct_residual(z,p,q2,q3,ball,keys,index,where,selected):
    """Full H source residual in the actual canonical orbit basis."""
    wf,wq,we=ball["wf"],ball["wq"],ball["eW"]
    rs,oj,oc,C=ball["rs"],ball["oj"],ball["oc"],ball["C"]
    es,esrc,ewc=ball["es"],ball["esrc"],ball["ewc"]
    selmap={f:t for t,f in enumerate(selected)}
    import finite_s3_3x4_r9_first_gap as c

    # K2 weighted flux entering each shell3 target from the q2 amplitudes.
    shell3flux=[0]*len(keys)
    for f in range(len(keys)):
        total=0
        for ptr in range(es[f],es[f+1]):
            total+=int(ewc[ptr])*q2[int(esrc[ptr])]
        shell3flux[f]=total

    rp=[(DEN*72-z)*p[k] for k in range(8)]
    rq2=[]
    for i in range(ball["n"]):
        ci=C[i]
        if ci is not None and q2[i]:
            for k in range(8):
                if ci[k]:
                    r=DEN*wq[i]*ci[k]*q2[i]
                    need(r%wf[k]==0,"flat_Q_metric_not_divisible")
                    rp[k]-=r//wf[k]
        val=(DEN*ball["dbase"][i]-z)*q2[i]
        for e in range(rs[i],rs[i+1]):
            val-=DEN*oc[e]*q2[oj[e]]
        if ci is not None:
            val-=DEN*sum(ci[k]*p[k] for k in range(8))
        rq2.append(val)

    # New shell3 source action: each original canonical shell3 orbit is
    # separately re-enumerated with its true 72 original electric moves.
    rs3=[0]*len(selected)
    flux_unselected=[0]*len(keys)
    shell4={}
    used_shell3=0
    shell4_events=0
    for t,f in enumerate(selected):
        key=keys[f]
        wi=we[f]
        moves=c.neighbors(key)
        need(sum(moves.values())==72,"shell3_72_move_violation")
        selfc=moves.get(key,0)
        mag=c.magnetic(c.from_key(key))
        diagonal=72+9*mag-selfc
        need(diagonal>=72,"negative_magnetic_diagonal")
        s=0
        for dst,count in moves.items():
            if dst==key:
                continue
            known=where.get(dst)
            if known is not None:
                need(known>=8,"shell3_touches_flat")
                i=known-8
                # Source action on old K2 rows: H_i,f=-c_i,f, with
                # wq_i*c_i,f = wi*c_f,i by the original source pairing.
                numer=wi*count
                need(numer%wq[i]==0,
                     "shell3_to_K2_reverse_not_integer")
                rq2[i]-=DEN*(numer//wq[i])*q3[t]
                s+=count*q2[i]
                continue
            g=index.get(dst)
            if g is not None:
                other=selmap.get(g)
                if other is not None:
                    s+=count*q3[other]
                else:
                    flux_unselected[g]+=wi*count*q3[t]
                    used_shell3+=count
            else:
                shell4[dst]=shell4.get(dst,0)+wi*count*q3[t]
                shell4_events+=count
        need(shell3flux[f]%wi==0,
             "K2_shell3_weighted_flux_not_divisible")
        # K2 neighbor terms have already been accumulated into s above;
        # independently compare their physical reverse action exactly.
        q_back=shell3flux[f]//wi
        s_back=sum(count*q2[where[dst]-8] for dst,count in moves.items()
                   if dst in where)
        need(q_back==s_back,"K2_shell3_reverse_amplitude_disagreement")
        rs3[t]=(DEN*diagonal-z)*q3[t]-DEN*s

    # Physical residual on all orbit states outside selected trial space.
    outside3=0
    shell3_nonzero=0
    for f in range(len(keys)):
        if f in selmap:
            continue
        flux=shell3flux[f]+flux_unselected[f]
        if flux:
            shell3_nonzero+=1
            wt=we[f]
            need(wt in (1,2,3,6),"bad_unselected_shell3_weight")
            outside3+=(6//wt)*flux*flux

    outside4=0
    shell4_nonzero=0
    for dest,flux in shell4.items():
        if flux:
            wt=c.weight(dest)
            need(wt in (1,2,3,6),"bad_actual_shell4_orbit_weight")
            outside4+=(6//wt)*flux*flux
            shell4_nonzero+=1
    inside=6*sum(wf[k]*v*v for k,v in enumerate(rp))
    inside+=6*sum(wq[i]*v*v for i,v in enumerate(rq2))
    inside+=6*sum(we[f]*v*v for f,v in zip(selected,rs3))
    total=inside+DEN*DEN*(outside3+outside4)
    need(total>=0,"negative_exact_whole_H_norm")
    norm=inner_products(p,q2,q3,ball,selected)
    return total,6*DEN*DEN*norm,(rp,rq2,rs3),(
        shell3_nonzero,shell4_nonzero,len(shell4),
        used_shell3,shell4_events,inside.bit_length(),
        outside3.bit_length(),outside4.bit_length())


def original_sparse_expectation(x,entries,z):
    """Independent Galerkin replay of normalized 20k physical quadratic."""
    G=0
    Q=0
    for tag,i,j,v in entries:
        a=x[i]*x[j]
        if i!=j:
            a*=2
        if tag=="G":
            G+=v*a
        else:
            Q+=v*a*DEN
    need(G>0,"nonpositive_sparse_G")
    return G,Q-z*G


def upper_sqrt_per_trillion(a,b):
    need(a>=0 and b>0,"negative_residual_or_zero_norm")
    quotient=(a*UNIT*UNIT)//b
    u=isqrt(quotient)
    if u*u*b < a*UNIT*UNIT:
        u+=1
    return u


def main():
    entries,digest0=tw.source()
    seeds=tw.original_144_trials()
    trials=tw.augmented(seeds,entries)
    ball,states,cols,old132=old_source()
    sys.path.insert(0,os.path.join(ROOT,"independent",
                                   "y137-12x12-krylov-20261116"))
    import exact_krylov_12 as h12
    h12.source_module()
    import sparse_h20736 as h
    keys,index,where=h.canonical_shell3(states,ball)
    chosen=[f for strong,total,f in h.source_score(ball,cols)]
    need(len(chosen)==20592 and len(set(chosen))==20592,
         "original_H20736_selection_not_recreated")
    emit("Y137_H20736_FULL_SOURCE",
         sparse_SHA256=digest0,physical_K2=8034,
         physical_K3_shell3=147344,
         additional_new_basis=20592,
         original_144_sources="FROZEN",
         arithmetic="INTEGER_ONLY",
         Wilson_weight="HOLD")
    for level,(z,x) in enumerate(trials,1):
        p,q2,q3=physical_amplitudes(ball,cols,old132,chosen,x)
        total,den,rs,census=direct_residual(
            z,p,q2,q3,ball,keys,index,where,chosen)
        oldnorm,oldquadratic=original_sparse_expectation(x,entries,z)
        norm=inner_products(p,q2,q3,ball,chosen)
        need(norm==oldnorm,"full_physical_W_norm_not_equal_sparse_Gram")
        rp,rq2,rs3=rs
        physical_quad=sum(ball["wf"][k]*p[k]*rp[k] for k in range(8))
        physical_quad+=sum(ball["wq"][i]*q2[i]*rq2[i]
                           for i in range(ball["n"]))
        physical_quad+=sum(ball["eW"][f]*q3[t]*rs3[t]
                           for t,f in enumerate(chosen))
        need(physical_quad==oldquadratic,
             "full_H_action_not_equal_sparse_projected_quadratic")
        rounded=upper_sqrt_per_trillion(total,den)
        emit("Y137_H20736_FULL_RESIDUAL",level=level,
             seed_144_z_num=z,denominator=DEN,
             full_trial_norm_bits=norm.bit_length(),
             residual_numerator_bits=total.bit_length(),
             source_shell3_outside_nonzero=census[0],
             source_shell4_nonzero=census[1],
             shell4_distinct_touched=census[2],
             shell3_boundary_move_events=census[3],
             shell4_boundary_move_events=census[4],
             interior_residual_square_bits=census[5],
             shell3_outside_flux_square_bits=census[6],
             shell4_outside_flux_square_bits=census[7],
             residual_upper_per_trillion=rounded,
             norm_G_in_full_physical_metric="EXACT",
             H_quadratic_full_vs_projected="EXACT",
             source_full_support="8_FLATS_K2_K3_UNSELECTED_K3_SHELL4",
             true_eigenspace_error="NOT_CERTIFIED",
             Wilson_weight="HOLD")
    emit("Y137_H20736_FULL_VERDICT",
         full_trials="2_OF_2_EXACT_W_RESIDUAL",
         residual_support="ALL_ONE_STEP_FROM_TRIAL_SOURCE",
         weighted_exterior_metric="SIX_OVER_ORBIT_WEIGHT",
         Ritz_projection="ACCEPTED_2D_TRIAL_UPPER",
         true_eigenstate_angle="HOLD",
         first_excitation_Wilson_weight="HOLD",
         issue_137="OPEN")


if __name__=="__main__":
    if sys.argv[1:]==["real"]:
        main()
    else:
        need(False,"use_real")
