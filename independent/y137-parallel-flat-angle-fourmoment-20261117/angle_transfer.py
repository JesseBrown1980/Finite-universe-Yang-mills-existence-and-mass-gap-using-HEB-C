#!/usr/bin/env python3
"""#137 independent Stage-E full-state to W-flat projector angle transfer.

Stage E (PR234) source-conditionally certifies FULL normalized state
distances from actual E1/E2 eigenstates to the ORIGINAL exact-Q-resolvent
dressed fixed flat sample vectors of PR180. For true normalized ψ and
fixed normalized Φ, if ||ψ-Φ||<=d then
||Pψ-PΦ||<=d and
||Pψ/||Pψ||-PΦ/||PΦ||||<=d/sqrt(||Pψ|| ||PΦ||).

Here B*B=72I and QHQ>=γ, so for either full normalized exact
Schur eigenstate or exact-Q-dressed fixed flat sample of energy z,
||P state|| >= (1+72/(γ-z)^2)^(-1/2).
Thus sin(angle flats) <= d * sqrt(1+72/gap_min^2). Entirely exact
positive rationals with integer outward rounding.

This improves the earlier PR184 W-flat 0.108/0.253 sine ceilings
CONDITIONALLY on accepted Stage E 4th signed moment and its receipt.
It then reruns the frozen PR275 original Wilson 64-entry contraction.
No claim of first Wilson spectral weight without a strict margin.
"""
import os
import sys
from math import isqrt

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
INDEP=os.path.join(ROOT,"independent")
sys.path.insert(0,os.path.join(INDEP,"y137-parallel-flat-projector-contraction-20261117"))
import flat_wilson_gate as old
DATA=os.path.join(HERE,"INPUT-PR234-STAGE-E.hbp")
RECEIPT_BLOB="daf746ca35e44005406be18a872b38a3257e83ff"
U=1000000000000
B=1000000000
PS=1000000
FLOOR=94068200
SAMPLE_Z=(69909875505,69949729820)
PHYSICAL_UP=(69909586556,69949433884)
STAGE_E_PER_TRILLION=(3235251105,8676646901)
STAGE_E_MOVED=(949209145,3693022069)

def need(ok,reason):
    if not ok:
        print("Y137_FLAT_FOURMOMENT_REFUSE|reason="+reason+"|json=0",flush=True)
        raise SystemExit(1)

def emit(tag,**fields):
    print(tag+"|"+"|".join(str(k)+"="+str(v) for k,v in fields.items())+
          "|json=0",flush=True)

def ceildiv(a,b):
    need(a>=0 and b>0,"exact_positive_ceil_domain")
    return (a+b-1)//b

def sqrtceil(a):
    need(a>=0,"negative_square_root")
    k=isqrt(a)
    return k if k*k==a else k+1

def parse(rows,tag):
    found=[old.parse(row) for row in rows if row.startswith(tag+"|")]
    need(len(found)==1,"missing_or_multiple_"+tag)
    return found[0]

def source():
    need(old.blob(DATA)==RECEIPT_BLOB,
         "Stage_E_four_moment_accepted_receipt_sha_changed")
    rows=open(DATA,encoding="ascii").read().splitlines()
    frozen=parse(rows,"Y137_E_PROVENANCE")
    need(frozen["run_id"]=="43933360655"
         and frozen["status"]=="SCOPED_NUMERICAL_PASS_WILSON_HOLD",
         "unaccepted_original_four_moment")
    c=parse(rows,"Y137_E_CELL") if False else None
    candidates=[old.parse(v) for v in rows if v.startswith("Y137_E_CELL|")]
    need(len(candidates)==4,"Stage_E_cell_count")
    moved=[v for v in candidates if v["case"]=="CENTRE_MOVED"]
    need(len(moved)==1,"Stage_E_moved_source_not_unique")
    selected=moved[0]
    need(int(selected["four_E1_error"])==STAGE_E_PER_TRILLION[0]
         and int(selected["four_E2_error"])==STAGE_E_PER_TRILLION[1]
         and int(selected["four_E1_moved_distance"])==STAGE_E_MOVED[0]
         and int(selected["four_E2_moved_distance"])==STAGE_E_MOVED[1],
         "four_moment_full_state_error_regression")
    verdict=parse(rows,"Y137_E_VERDICT")
    need(verdict["best_case"]=="CENTRE_MOVED"
         and verdict["actual_four_moment_combined_per_trillion"]=="11911898006"
         and verdict["sufficient_gate"]=="0"
         and verdict["first_Wilson_weight"]=="HOLD",
         "Stage_E_Wilson_scope_drift")
    need(sum(STAGE_E_PER_TRILLION)==11911898006
         and all(x>y for x,y in zip(STAGE_E_PER_TRILLION,STAGE_E_MOVED)),
         "four_moment_source_error_accounting")
    return STAGE_E_PER_TRILLION

def transfer(d,i):
    a=max(SAMPLE_Z[i],PHYSICAL_UP[i])
    g=B*FLOOR-a*PS
    need(g>0,"original_Q_floor_below_reference")
    # factor = sqrt(1+72*(B*PS)^2/g^2), ceiling in 1e12.
    numerator=g*g+72*B*B*PS*PS
    fac=sqrtceil(ceildiv(U*U*numerator,g*g))
    s=ceildiv(d*fac,U)
    need(0<s<U,"vacuous_projected_flat_sine")
    return s,fac,g

def toy():
    # As a proof-independent toy, projecting two full unit vectors on
    # the same nonzero coordinate subspace cannot increase their absolute
    # difference; normalization raises it by at most 1/sqrt(p1*p2).
    # p1=p2=3/5, d=3/10, so projected direction cap <= 1/2.
    d=3*U//10
    p=3
    q=5
    need(ceildiv(d*q,p)==U//2,
         "normalization_lipschitz_toy")
    need(sqrtceil(15)==4 and sqrtceil(16)==4
         and ceildiv(7,3)==3,"outward_integer_toy")
    emit("Y137_FLAT_FOURMOMENT_TOY",W_projection="CONTRACTION",
         normalized_direction="GEOMETRIC_MEAN_BOUND",
         outward_integer="PASS",first_Wilson_weight="HOLD")

def run():
    toy()
    source()
    A,R,old_s1,old_s2=old.freeze()
    a,b,c=transfer(STAGE_E_PER_TRILLION[0],0)
    d,e,f=transfer(STAGE_E_PER_TRILLION[1],1)
    need(a<old_s1 and d<old_s2,
         "new_source_conditional_angles_not_improved")
    emit("Y137_FLAT_FOURMOMENT_SOURCE",
         source="PR234_HOSTED_SIGNED_MU3_STAGED_FOUR_MOMENTS",
         original_3moment_PR184_sine1=old_s1,
         original_3moment_PR184_sine2=old_s2,
         certified_fullstate_distance1=STAGE_E_PER_TRILLION[0],
         certified_fullstate_distance2=STAGE_E_PER_TRILLION[1],
         original_fixed_sample_Z1=SAMPLE_Z[0],
         original_fixed_sample_Z2=SAMPLE_Z[1],
         true_E1_upper=PHYSICAL_UP[0],true_E2_upper=PHYSICAL_UP[1],
         original_Q_floor=FLOOR,
         original_BstarB="EXACT_72",
         norm_factor1_per_trillion=b,
         norm_factor2_per_trillion=e,
         max_Q_floor_gap1_scaled=c,max_Q_floor_gap2_scaled=f,
         four_moment_flat_sine1=a,four_moment_flat_sine2=d)
    old.exact_margin(A,R,a,d)
    emit("Y137_FLAT_FOURMOMENT_VERDICT",
         four_moment_sine_sources="SOURCE_CONDITIONAL_PR234_DRAFT",
         original_Wilson_matrix="PR273_HOSTED_PASS",
         original_QOQ_bounds="STILL_ENTRYWISE",
         actual_true_first_Wilson_weight="HOLD",issue_137="OPEN")

if __name__=="__main__":
    if sys.argv[1:]==["toy"]:toy()
    elif sys.argv[1:]==["real"]:run()
    else:need(False,"usage_toy_or_real")
