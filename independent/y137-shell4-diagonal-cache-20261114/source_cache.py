#!/usr/bin/env python3
"""Generate exact m-conditioned shell4 Gram cache and fixed-trial energy polynomials.

One costly graph pass is followed by millisecond-scale rational 8x8 replays.
Source model remains the K3 builder; independent input/census review is separate.
All certified gain numerators round DOWN, never up.
"""
import hashlib
import os
import sys
from array import array

HERE=os.path.dirname(os.path.abspath(__file__))
PARENT=os.path.dirname(HERE)
sys.path.insert(0,os.path.join(PARENT,"y137-shell4-resolvent-domination-20261113"))
import source as old
m=old.m
B=old.B
SCALE=old.SCALE
PS=old.PS
UNIT=old.UNIT


def need(t,reason):
    old.need(t,reason)


def enc(A):
    return old.encode(A)


def gram_add(out,v,w,fac):
    for i in range(8):
        vi=v[i]
        for j in range(i,8):
            out[i][j]+=fac*vi*w[j]


def sym(A):
    for i in range(8):
        for j in range(i):
            A[i][j]=A[j][i]
    return A


def mag_list(ex,ball):
    mvals=array("b")
    hist=[0]*37
    digest=hashlib.sha256()
    for key in ex["code4"]:
        x=m.c.magnetic(m.c.from_key(m.decode(key)))
        need(0<=x<=36,"magnetic_out_of_range")
        hist[x]+=1
        mvals.append(x)
        digest.update(bytes((x,)))
    need(len(mvals)==1985218 and min(mvals)==4 and max(mvals)==16,"shell4_census")
    old.emit("Y137_CACHE_SHELL4",orbits=len(mvals),minimum_m=4,maximum_m=16,
             magnetic_bytes_sha256=digest.hexdigest(),
             histogram=",".join(str(x) for x in hist))
    return mvals,hist


def moments(ball,z,Y):
    """H=sum w YY*, J=sum w(sY*+Ys*) in source's exact orbit metric."""
    H=[[0]*8 for _ in range(8)]
    J=[[0]*8 for _ in range(8)]
    n=ball["n"]
    rs,oi,oc,src=ball["rs"],ball["oj"],ball["oc"],ball["C"]
    for i in range(n):
        row=Y[i]
        t=[0]*8
        for e in range(rs[i],rs[i+1]):
            y=Y[oi[e]]
            coupling=oc[e]
            for k in range(8):
                t[k]+=coupling*y[k]
        c=src[i]
        s=[(B*ball["dbase"][i]-z)*row[k]
           -B*(t[k]+(SCALE*c[k] if c is not None else 0)) for k in range(8)]
        w=ball["wq"][i]
        for p in range(8):
            yp=row[p]
            sp=s[p]
            for q in range(p,8):
                H[p][q]+=w*yp*row[q]
                J[p][q]+=w*(sp*row[q]+yp*s[q])
    return sym(H),sym(J)


def per_magnetic_grams(ball,mvals,Y):
    """Exact packed edge grouping; 8x8 Gram per cost, one traversal of all edges."""
    lo,hi=m.entry_range(Y)
    need(lo>=0 and hi>0,"packed_nonnegative")
    maxS=ball["maxwc"]*hi
    bits=max((6*ball["nf"]*maxS*maxS).bit_length(),hi.bit_length())+1
    mask=(1<<bits)-1
    sh=[i*bits for i in range(8)]
    packed=m.pack(Y,bits)
    acc=[[0]*8 for _ in range(37)]
    es,src,wc,wt=ball["es"],ball["esrc"],ball["ewc"],ball["eW"]
    for f in range(ball["nf"]):
        S=0
        for e in range(es[f],es[f+1]):
            S+=wc[e]*packed[src[e]]
        if not S:
            continue
        factor=6//wt[f]
        a=acc[mvals[f]]
        for p in range(8):
            s=(S>>sh[p])&mask
            if s:
                a[p]+=factor*s*S
    matrices=[]
    for bucket in acc:
        G=[[0]*8 for _ in range(8)]
        for p in range(8):
            for q in range(p,8):
                G[p][q]=B*B*((bucket[p]>>sh[q])&mask)
        matrices.append(sym(G))
    return matrices


def mat_add(A,B):
    return [[A[i][j]+B[i][j] for j in range(8)] for i in range(8)]


def mat_sub(A,B):
    return [[A[i][j]-B[i][j] for j in range(8)] for i in range(8)]


def source_direct_recheck(ball,z0,U0,G0,Y,H,J,Gm):
    """Exact independent-in-program check of frozen-trial z -> z+1 formulas."""
    delta=1
    zz=z0+delta
    ud=[[0]*8 for _ in range(8)]
    gd=[[0]*8 for _ in range(8)]
    for k in range(8):
        ud[k][k]=SCALE*SCALE*ball["wf"][k]*(72*B-zz)
    rs,oi,oc,C=ball["rs"],ball["oj"],ball["oc"],ball["C"]
    for i in range(ball["n"]):
        y=Y[i]
        t=[0]*8
        for e in range(rs[i],rs[i+1]):
            rr=Y[oi[e]]
            co=oc[e]
            for k in range(8):
                t[k]+=co*rr[k]
        d=B*ball["dbase"][i]-zz
        sc=C[i]
        s=[d*y[k]-B*(t[k]+(SCALE*sc[k] if sc is not None else 0))
           for k in range(8)]
        w=ball["wq"][i]
        for p in range(8):
            for q in range(8):
                ud[p][q]+=w*y[p]*s[q]
                if sc is not None:
                    ud[p][q]-=w*B*SCALE*sc[p]*y[q]
            for q in range(p,8):
                gd[p][q]+=6*w*s[p]*s[q]
    sym(gd)
    for bucket in Gm:
        gd=mat_add(gd,bucket)
    frozenGram=[[H[i][j]+(SCALE*SCALE*ball["wf"][i] if i==j else 0)
                for j in range(8)] for i in range(8)]
    expectedU=[[U0[i][j]-delta*frozenGram[i][j] for j in range(8)]
               for i in range(8)]
    expectedG=[[G0[i][j]-6*delta*J[i][j]+6*delta*delta*H[i][j]
                for j in range(8)] for i in range(8)]
    need(ud==expectedU and gd==expectedG,"fixed_trial_polynomial_recheck")
    need(all(ud[p][q]==ud[q][p] for p in range(8) for q in range(8)),
         "offpoint_U_symmetry")


def run_point(ball,mvals,row):
    z,lo,hi,v,uh,gh=row
    t=m.threshold_ball(z,B,old.STEPS,SCALE,ball,old.FLOOR,keep_y=True)
    need(t["hu"]==uh and t["hg"]==gh,"original_U_G_hash_pin")
    U,G,Y=t["U"],t["G"],t["Y"]
    H,J=moments(ball,z,Y)
    Gm=per_magnetic_grams(ball,mvals,Y)
    G4=[[sum(A[i][j] for A in Gm) for j in range(8)] for i in range(8)]
    oldinner=old.inner_gram(ball,z,Y)
    need(mat_add(oldinner,G4)==G,"full_K3_plus_shell4_residual_Gram")
    for mm,A in enumerate(Gm):
        if any(any(val for val in r) for r in A):
            need(old.psd(A),"single_cost_Gram_PSD_"+str(mm))
    need(old.psd(G4),"all_shell4_Gram_PSD")
    old.verify_directional_exterior(ball,Y,z,v,G4)
    source_direct_recheck(ball,z,U,G,Y,H,J,Gm)
    used=[i for i in range(37) if any(any(v for v in r) for r in Gm[i])]
    need(used[0]>=4 and used[-1]<=16,"magnetic_bucket_support")
    h={i:(144+9*i)*B-z for i in used}
    common=1
    for a in h.values():
        common*=a
    uppernum=[[sum(Gm[mm][i][j]*(common//h[mm]) for mm in used)
               for j in range(8)] for i in range(8)]
    uniform_h=(144+9*16)*B-z
    uniform_num=[[G4[i][j]*(common//uniform_h) for j in range(8)]
                 for i in range(8)]
    # Common is divisible by uniform_h only when m=16 is present.
    need(16 in used,"magnetic_sixteen_support")
    need(old.psd(mat_sub(uppernum,uniform_num)),
         "strict_Loewner_diagonal_improvement")
    gamma=B*old.FLOOR-z*PS
    need(gamma>0,"Q_floor_resolvent")
    width=[[PS*common*G[i][j]-gamma*uppernum[i][j]
            for j in range(8)] for i in range(8)]
    need(old.psd(width),"fullQ_diagonal_width_PSD")
    qnum=old.quad(uppernum,v)
    wnorm=sum(old.WF[i]*v[i]*v[i] for i in range(8))
    denom=6*common*B*SCALE*SCALE*wnorm
    floor_gain=qnum*UNIT//denom
    ceil_gain=old.divup(qnum*UNIT,denom)
    uniform_gain=old.quad(G4,v)*UNIT//(6*uniform_h*B*SCALE*SCALE*wnorm)
    need(floor_gain>=uniform_gain and floor_gain>0,"directional_gain_improved")
    old.emit("Y137_CACHE_POINT", sample_num=z,den=B,E_lo_num=lo,E_hi_num=hi,
             U_sha256=uh,G_sha256=gh,
             source_scale=SCALE,source_floor_num=old.FLOOR,
             magnetic_support=",".join(str(mm) for mm in used),
             common_magnetic_den=common,
             magnetic_weighted_num=enc(uppernum),
             upper_source_gain_floor_per_trillion=floor_gain,
             upper_source_gain_ceil_per_trillion=ceil_gain,
             uniform_source_gain_floor_per_trillion=uniform_gain,
             strict_gain=int(floor_gain>uniform_gain),
             all_255_minors_diagonal_width_PSD=1,
             all_255_minors_diagonal_gain_over_uniform_PSD=1,
             fixed_trial_energy_polynomial="EXACT_AT_ALL_z_BELOW_Q_FLOOR",
             U0=enc(U),G0=enc(G),Y_Gram=enc(H),G_linear=enc(J),
             shell4_magnetic_gram="~".join(str(mm)+":"+enc(Gm[mm]) for mm in used),
             first_Wilson_spectral_weight="HOLD")
    return floor_gain


def main():
    prediction=open(os.path.join(HERE,"PREDICTION.hbp"),"rb").read()
    need(b"PREHOST_FREEZE" in prediction,"freeze_missing")
    need(old.source.NEW_G==old.FLOOR,"floor_changed")
    old.emit("Y137_CACHE_FREEZE",status="PASS", model="3x4_S3_r9",
             graph_builder="SOURCE_NOT_INDEPENDENT",
             actual_Wilson_spectral_weight="HOLD")
    ball,ex=old.build()
    mag,hist=mag_list(ex,ball)
    gains=[run_point(ball,mag,row) for row in old.FROZEN]
    need(len(gains)==2 and min(gains)>0,"two_positive_refinements")
    old.emit("Y137_CACHE_VERDICT",samples=2,full_shell4_census=1985218,
             magnetic_bucket_psd="PASS",
             fixed_trial_energy_polynomial="EXACT",
             independent_second_seat_Gram_review="PENDING",
             actual_first_Wilson_spectral_weight="HOLD")


if __name__=="__main__":
    main()
