#!/usr/bin/env python3
"""Issue #137 first actual K3->shell4 boundary-resolvent source certificate.

A completed full-Q shell5 *norm* bound follows from the exact 72-move
weighted adjacency contraction, not an enumerated truncation at shell4.
All source measurements are exact integers and retain a HOLD on Wilson weight.
"""
import hashlib
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INDEP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(INDEP, "y137-liftfree-k3-20261113"))
import k3_common as source

m = source.mod
c = m.c
B = 1000000000
SCALE = 1000000000000
UNIT = 1000000000000
STEPS = 20
PS = 1000000
FLOOR = 94068200
FROZEN = (
    (69909875505, 69908500000, 69909875505,
     (1000000000,997935625,996905915,38054797,37920545,2788116,51160,51160),
     "0752df3c1941c67316cc6834795182fdaccdaba0ca5fc711221e7217d0dbaa1c",
     "83efba692ef3a8451a68049ee996451877ac4d646ae2f357fc0b604b48db0b0f"),
    (69949729820, 69948100000, 69949729820,
     (111045317,-38181375,-112233220,1000000000,979217930,216249666,4169404,4169404),
     "9229dfad058157d80287cb1ab188c1034bdbb16394dec045b540890d8bb05109",
     "e42df65b4b269095177fc609d06b4576917901c598f8ebd477eaa58b61b90d8d")
)
WF = (1,3,2,3,3,2,2,2)


def fail(reason):
    print("Y137_BDRY_REFUSE|reason=" + reason + "|json=0", flush=True)
    raise SystemExit(1)


def need(condition, reason):
    if not condition:
        fail(reason)


def divup(n,d):
    need(n >= 0 and d > 0, "invalid_quotient")
    return (n + d - 1) // d


def emit(name, **fields):
    print(name+"|"+"|".join(str(k)+"="+str(v) for k,v in fields.items())+"|json=0", flush=True)


def encode(M):
    return ";".join(",".join(str(val) for val in row) for row in M)


def quad(M, v):
    return sum(v[i] * M[i][j] * v[j] for i in range(8) for j in range(8))


def psd(M):
    # Every one of the 255 nonempty principal minors, no floating arithmetic.
    for q in range(1,9):
        for ids in itertools.combinations(range(8), q):
            H = [[M[i][j] for j in ids] for i in ids]
            if c.det(H) < 0:
                return False
    return True


def sha(mtx):
    return hashlib.sha256("|".join(str(a) for r in mtx for a in r).encode("ascii")).hexdigest()


def build():
    w, mag, adj, q_flat, outer = c.graph()
    states, flats, sizes = m.rebuild_states()
    need(sizes == [8, 264, 7770] and len(states) == 8042, "K2_census")
    where = {key:i for i,key in enumerate(states)}
    ball2 = m.ball_from_checker(w, mag, adj, q_flat, outer)
    ball, ex = m.build_k3(states, where, w, mag, adj, outer, ball2["C"])
    need((ball["n"], ball["nf"], len(ball["oj"])) ==
         (155378, 1985218, 1356528), "K3_census")
    need(tuple(ball["wf"]) == WF, "flat_weight_metric")
    return ball, ex


def shell4_magnetic(ex, ball):
    histogram = [0]*37
    for encoded in ex["code4"]:
        value = c.magnetic(c.from_key(m.decode(encoded)))
        need(0 <= value <= 36, "magnetic_value")
        histogram[value] += 1
    need(sum(histogram) == ball["nf"], "shell4_magnetic_census")
    present = [i for i,v in enumerate(histogram) if v]
    emit("Y137_BDRY_SHELL4", counted=sum(histogram), min_m=present[0],
         max_m=present[-1],
         histogram=",".join(str(x) for x in histogram),
         weighted_72_outgoing_electric_moves="MODEL_EXACT",
         next_shell="COVERED_BY_GLOBAL_NORM_NOT_ENUMERATED")
    return present[-1]


def inner_gram(ball, a, Y):
    # Independently reconstruct all 8x8 K3-interior residual products,
    # then subtract from source G to isolate exact shell4 Gram.
    n = ball["n"]
    need(len(Y) == n, "trial_shape")
    result = [[0]*8 for _ in range(8)]
    rs,oj,oc,C = ball["rs"],ball["oj"],ball["oc"],ball["C"]
    for i in range(n):
        t = [0]*8
        for p in range(rs[i],rs[i+1]):
            yp = Y[oj[p]]
            cc = oc[p]
            for k in range(8):
                t[k] += cc*yp[k]
        ci = C[i]
        di = B*ball["dbase"][i]-a
        yi=Y[i]
        res=[di*yi[k]-B*(t[k]+(SCALE*ci[k] if ci is not None else 0))
             for k in range(8)]
        fac=6*ball["wq"][i]
        for p in range(8):
            if res[p]:
                for q in range(p,8):
                    result[p][q]+=fac*res[p]*res[q]
    for p in range(8):
        for q in range(p):
            result[p][q] = result[q][p]
    return result


def verify_directional_exterior(ball,Y,a,v,G4):
    # Direct weighted edge traversal independent of matrix subtraction.
    # Per-target edge sums, including every shell4 target, no omissions.
    vals=[sum(Y[i][j]*v[j] for j in range(8)) for i in range(ball["n"])]
    es,src,wc,w=ball["es"],ball["esrc"],ball["ewc"],ball["eW"]
    total=0
    dropped=0
    altered=0
    for f in range(ball["nf"]):
        first=es[f]
        acc=0
        for p in range(first,es[f+1]):
            acc+=wc[p]*vals[src[p]]
        fac=6//w[f]
        total+=fac*acc*acc
        if not dropped and es[f+1]>first:
            changed=acc-wc[first]*vals[src[first]]
            difference=fac*(changed*changed-acc*acc)
            if difference:
                altered += difference
                dropped=1
    direct=B*B*total
    expected=quad(G4,v)
    need(expected>0 and direct == expected, "exterior_Gram_crosscheck")
    need(dropped==1 and altered!=0, "deleted_boundary_edge_negative_control")
    return direct


def inspect(ball, z, lo, hi, v, uhash, ghash, mmax):
    need(lo < z <= hi and hi < B*FLOOR//PS, "energy_window")
    result=m.threshold_ball(z,B,STEPS,SCALE,ball,FLOOR,keep_y=True)
    U,G,Y=result["U"],result["G"],result["Y"]
    need((result["hu"],result["hg"])==(uhash,ghash), "frozen_U_G_hash")
    inner=inner_gram(ball,z,Y)
    exterior=[[G[p][q]-inner[p][q] for q in range(8)] for p in range(8)]
    need(psd(inner) and psd(exterior), "Gram_decomposition_PSD")
    observed=verify_directional_exterior(ball,Y,z,v,exterior)
    total=quad(G,v)
    need(0 < observed<=total, "directional_split")
    # A_Q=D_Q-z >= gamma I. On vectors V supported on shell4:
    # A <= (144+9*mmax-z)I since T_44 is a compression of the
    # weighted-symmetric nonnegative 72-regular electric adjacency.
    # Thus U(Y - R4/hmax) <= U(Y)-G4/(6*hmax) in source units.
    hmax=(144+9*mmax)*B-z
    gamma=B*FLOOR-z*PS
    need(gamma>0 and PS*hmax>gamma, "resolvent_or_operator_floor")
    # New exact matrix lower-width numerator:
    # Lambda'=PS*G/(6*gamma)-G4/(6*hmax).
    width=[[PS*hmax*G[p][q]-gamma*exterior[p][q]
            for q in range(8)] for p in range(8)]
    need(psd(width), "new_full_Q_Loewner_width")
    rnorm=sum(WF[i]*v[i]*v[i] for i in range(8))
    improvement=divup(observed*UNIT,6*hmax*B*SCALE*SCALE*rnorm)
    need(improvement>0, "nontrivial_outer_source_improvement")
    share=observed*UNIT//total
    emit("Y137_BDRY_POINT", sample_num=z, den=B, E_lo_num=lo,E_hi_num=hi,
         U_sha256=uhash,G_sha256=ghash,
         Q_shell4_magnetic_max=mmax,
         corrected_schur_upper_den=6*hmax,
         old_schur_lower_gram_denom_num=6*gamma,
         old_schur_lower_gram_denom_weight=PS,
         outer_fraction_floor_per_trillion=share,
         shell4_directional_Gram=observed,
         complete_directional_Gram=total,
         new_upper_Rayleigh_improvement_ceil_per_trillion=improvement,
         G_inner=encode(inner),G_shell4=encode(exterior),
         U_source=encode(U),G_source=encode(G),
         fullQ_width_all_255_PSD=1,
         shell4_G_all_255_PSD=1,
         deleted_edge_negative_control="PASS",
         next_shell5="COVERED_BY_WEIGHTED_72_OPERATOR_NORM",
         actual_E1E2_Wilson_weight="HOLD")
    return improvement


def main():
    pred=open(os.path.join(HERE,"PREDICTION.hbp"),"rb").read()
    need(b"PREHOST_SOURCE_INPUTS_FROZEN" in pred, "input_freeze")
    need(source.SCRIPT_SHA ==
         "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff",
         "source_checker_pin")
    need(source.NEW_G==FLOOR and source.PS==PS, "source_floor_pin")
    emit("Y137_BDRY_FREEZE", status="PASS", old_source="PR180_PR182_PR186_PR187",
         source_floor="94068200/1000000",
         hypothesis="STRICT_SCHUR_UPPER_REDUCTION",
         shell5_omission="PROHIBITED")
    ball,ex=build()
    mx=shell4_magnetic(ex,ball)
    changes=[inspect(ball,*row,mx) for row in FROZEN]
    need(all(changes), "no_improvement")
    emit("Y137_BDRY_VERDICT", samples=2, all_exact_integers=1,
         actual_shell4_edges_reused=1,
         shell5_cost="RIGOROUS_GLOBAL_BOUND_72",
         source_schur_upper="STRICTLY_IMPROVED_ALONG_TWO_FROZEN_VECTORS",
         actual_E1E2_Wilson_spectral_weight="HOLD",
         next="INDEPENDENT_SOURCE_REPLAY_THEN_NEW_INERTIA_BRACKETS")


if __name__=="__main__":
    main()
