#!/usr/bin/env python3
"""Independent arithmetic receipt replay for signed-µ3 E1 matched flat direction."""
import hashlib
import sys

U=1000000000000
ORIGINAL_V1=(1000000000,997935625,996905915,38054797,37920545,2788116,51160,51160)
TARGET=2000000000


def need(p,msg):
    if not p:raise ValueError(msg)


def parse(raw):
    out={}
    for line in raw.splitlines():
        key=line.split("|",1)[0]
        need(key.startswith("Y137_E1_MATCHED_"),"unknown_row")
        z={}
        for part in line.split("|")[1:]:
            k,sep,v=part.partition("=")
            need(sep and k and k not in z,"bad_field")
            z[k]=v
        need(z.pop("json",None)=="0","HBP_end")
        out.setdefault(key,[]).append(z)
    for name,count in (("TOY",1),("POINT",6),("VECTOR",1),("VERDICT",1)):
        need(len(out.get("Y137_E1_MATCHED_"+name,[]))==count,
             "missing_"+name)
    return out


def integer(x):
    n=int(x)
    need(str(n)==x,"noncanonical_int")
    return n


def vector(x):
    v=tuple(integer(z) for z in x.split(","))
    need(len(v)==8,"bad_E1_vector")
    return v


def verify(raw):
    out=parse(raw)
    toy=out["Y137_E1_MATCHED_TOY"][0]
    need(toy=={"integer_only":"PASS",
               "moving_witness_requires_new_Wilson_source":"PASS",
               "first_Wilson_weight":"HOLD"},"toy")
    points=out["Y137_E1_MATCHED_POINT"]
    cells=[]
    for k,row in enumerate(points):
        need(integer(row["k"])==k and integer(row["den"])==4,
             "ordered_E1_candidates")
        sine=integer(row["matched_W_flat_sine_per_trillion"])
        dist=integer(row["matched_full_state_distance_per_trillion"])
        movement=integer(row["source_original_v1_delta_per_trillion"])
        spread=integer(row["source_Q_norm_spread_per_trillion"])
        total=integer(row["transported_original_full_distance_per_trillion"])
        residual=integer(row["source_fourth_moment_residual_per_trillion"])
        action=integer(row["source_fourth_moment_action_per_trillion"])
        need(0<sine<U and dist>0 and movement>=0 and spread>=0 and
             total>=dist and residual>=0 and action>=0,
             "E1_physical_error_nonnegative")
        need(integer(row["original_fixed_Wilson_source_valid"])==int(k==0) and
             integer(row["new_source_specific_Wilson_required"])==int(k!=0) and
             integer(row["E1_diagnostic_target_reached"])==int(sine<TARGET),
             "source_reuse_prohibited")
        cells.append((sine,dist,k,movement))
        if k==4:
            need(movement==949209145 and total==3235251105,
                 "original_StageE_E1_source_regression")
    best=min(cells)
    result=out["Y137_E1_MATCHED_VERDICT"][0]
    need(result["source"]=="ORIGINAL_HOSTED_SIGNED_MU3_FOUR_MOMENT" and
         integer(result["original_fixed_E1_distance_per_trillion"])==3235251105 and
         integer(result["best_matched_fraction_num"])==best[2] and
         integer(result["best_matched_fraction_den"])==4 and
         integer(result["best_matched_distance_per_trillion"])==best[1] and
         integer(result["best_matched_flat_sine_per_trillion"])==best[0] and
         integer(result["sufficient_E1_diagnostic_target_per_trillion"])==TARGET and
         result["E1_diagnostic_target"]==
           ("CANDIDATE_NEEDS_NEW_MATCHED_WILSON_SOURCE" if best[0]<TARGET else "HOLD") and
         result["original_fixed_Wilson_dual_not_reused"]=="PASS" and
         result["actual_original_first_Wilson_weight"]=="HOLD" and
         result["issue_137"]=="OPEN","source_Wilson_verdict")
    vs=out["Y137_E1_MATCHED_VECTOR"][0]
    a=vector(vs["source_E1_original_v1"])
    b=vector(vs["source_E1_recentered_v1"])
    c=vector(vs["source_E1_best_v1"])
    k=best[2]
    need(a==ORIGINAL_V1 and all(c[i]==(4-k)*a[i]+k*b[i] for i in range(8)),
         "E1_exact_source_vector_combination")
    rawv=",".join(str(x) for x in c)
    need(vs["source_E1_best_v1_sha256"]==
         hashlib.sha256(rawv.encode("ascii")).hexdigest() and
         integer(vs["source_matched_fraction_num"])==k and
         integer(vs["source_matched_fraction_den"])==4 and
         vs["true_E1_projector_moved"]=="SOURCE_CONDITIONAL" and
         vs["original_Wilson_rebuild"]=="REQUIRED" and
         vs["actual_original_first_Wilson_weight"]=="HOLD",
         "E1_best_source_vector_SHA")
    return best[0],k,rawv


def tests(raw):
    sine,k,v=verify(raw)
    for a,b in (
        ("|original_fixed_Wilson_dual_not_reused=PASS|",
         "|original_fixed_Wilson_dual_not_reused=FAIL|"),
        ("|sufficient_E1_diagnostic_target_per_trillion=2000000000|",
         "|sufficient_E1_diagnostic_target_per_trillion=0|"),
        ("|source_E1_best_v1_sha256=","|source_E1_best_v1_sha256=bad"),
        ("|actual_original_first_Wilson_weight=HOLD|",
         "|actual_original_first_Wilson_weight=PASS|"),
        ("|source_matched_fraction_den=4|","|source_matched_fraction_den=3|"),
        ("|new_source_specific_Wilson_required=1|",
         "|new_source_specific_Wilson_required=0|"),
    ):
        alt=raw.replace(a,b,1)
        need(alt!=raw,"missing_negative_fixture")
        try:verify(alt)
        except ValueError:pass
        else:raise AssertionError("accepted_forged_E1_source")
    print("Y137_E1_REPLAY|source=STAGEE_SIGNED_MU3|"
          "best_k="+str(k)+"|E1_sine="+str(sine)+
          "|best_vector_SHA256="+hashlib.sha256(v.encode("ascii")).hexdigest()+
          "|tamper=6_REJECTED|original_Wilson_weight=HOLD|json=0")


if __name__=="__main__":
    need(len(sys.argv)==2,"usage_HBP")
    with open(sys.argv[1],encoding="ascii") as f:tests(f.read())
