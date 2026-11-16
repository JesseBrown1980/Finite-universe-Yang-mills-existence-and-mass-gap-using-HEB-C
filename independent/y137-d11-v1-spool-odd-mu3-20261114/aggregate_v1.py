#!/usr/bin/env python3
"""Exact 8-way acceptance of archived-K3 shell5 V1 reconstruction receipts.

Each source group independently replays eight immutable original mu2
source shards and matches the old per-group Q5 Gram at E1/E2. This
aggregate accepts only all eight disjoint target-key groups and exact
historic 18,598,040-target / 125,426,880-edge census.
"""
import os
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
RECEIPTS=os.environ.get("Y137_D11_V1_RECEIPTS",
                        os.path.join(ROOT,"build","y137-d11-v1-receipts"))
FROZEN_TARGETS=(435324,4439918,988399,2812763,822474,3973928,1612450,3512784)
FROZEN_RECORDS=(2992176,30151243,6519696,19062775,5514324,26783294,10607220,23796152)
Z=(69909875505,69949729820)


def need(ok,why):
    if not ok:
        print("Y137_D11_V1_ALL_REFUSE|reason="+why+"|json=0",flush=True)
        raise SystemExit(1)


def emit(label,**kwargs):
    print(label+"|"+"|".join(str(k)+"="+str(v)
                            for k,v in kwargs.items())+"|json=0",flush=True)


def read_group(group):
    path=os.path.join(RECEIPTS,"RESULT-V1-GROUP"+str(group)+".hbp")
    need(os.path.isfile(path),"missing_group_"+str(group))
    points=[]
    head=[]
    buckets=[]
    for line in open(path,encoding="utf-8"):
        parts=line.strip().split("|")
        if not parts or not parts[0].startswith("Y137_D11_V1_"):
            continue
        dic={}
        for item in parts[1:]:
            need("=" in item,"bad_field")
            k,v=item.split("=",1)
            need(k not in dic,"duplicate_field")
            dic[k]=v
        if parts[0]=="Y137_D11_V1_VERDICT":
            head.append(dic)
        if parts[0]=="Y137_D11_V1_POINT":
            points.append(dic)
        if parts[0]=="Y137_D11_V1_BUCKET":
            buckets.append(dic)
    need(len(head)==1 and len(points)==2 and len(buckets)==8,
         "wrong_group_receipt_shape")
    v=head[0]
    need(int(v["group"])==group and
         int(v["total_Q4_edge_records"])==FROZEN_RECORDS[group] and
         int(v["exact_shell5_targets"])==FROZEN_TARGETS[group],
         "source_census_changed")
    need(v["all_target_Grams_match_original_mu2"]=="PASS" and
         int(v["original_mu2_run"])==43606393196 and
         int(v["degree11_total_outward_passes"])==10 and
         v["real_mu3"]=="NOT_COMPUTED" and
         v["actual_first_Wilson_weight"]=="HOLD",
         "wrong_source_scope")
    h=v["output_sha256"]
    need(len(h)==64 and all(c in "0123456789abcdef" for c in h),
         "invalid_sha256")
    seen={}
    for p in points:
        z=int(p["sample_num"])
        need(z in Z and z not in seen and int(p["group"])==group and
             p["exact_spooled_shell5_mu2_gram"]=="MATCHES_ACCEPTED",
             "wrong_sample_or_source_Gram")
        seen[z]=p["inherited_mu2_Q5_sha256"]
    need(set(seen)==set(Z),"missing_sample")
    for b in buckets:
        need(int(b["group"])==group and
             int(b["bucket"])%8==group and
             b["W_target_merge"]=="PASS",
             "bucket_group_missing_or_not_merged")
    need(len(set(int(b["bucket"]) for b in buckets))==8,
         "duplicate_bucket")
    need(sum(int(b["edge_records"]) for b in buckets)==
         FROZEN_RECORDS[group] and
         sum(int(b["destinations"]) for b in buckets)==
         FROZEN_TARGETS[group],"bucket_sums_not_frozen")
    return v,seen


def main():
    target_total=0
    record_total=0
    byte_total=0
    for group in range(8):
        v,seen=read_group(group)
        target_total+=int(v["exact_shell5_targets"])
        record_total+=int(v["total_Q4_edge_records"])
        byte_total+=int(v["output_bytes"])
        emit("Y137_D11_V1_ALL_GROUP",group=group,
             targets=FROZEN_TARGETS[group],
             records=FROZEN_RECORDS[group],
             bytes=v["output_bytes"],
             sha256=v["output_sha256"],
             sample_E1_sha256=seen[Z[0]],
             sample_E2_sha256=seen[Z[1]],
             target_Gram_replay="PASS")
    need(target_total==18598040 and record_total==125426880,
         "final_complete_Q5_census")
    emit("Y137_D11_V1_ALL_VERDICT",
         original_exact_mu2_run=43606393196,
         completed_destination_groups=8,
         complete_Q5_support_targets=target_total,
         complete_Q4_to_Q5_edge_records=record_total,
         spooled_V1_over_b_bytes=byte_total,
         both_sample_Q5_Grams_reproduced_exactly=1,
         source_record_hashes_verified_per_group=1,
         remaining_outward_operator_passes=9,
         terminal_odd_degree11_saves_final_pass=1,
         raw_Q5_72_move_source_review="NOT_COMPLETED",
         real_mu3="NOT_COMPUTED",
         degree11_center="HOLD",
         first_Wilson_weight="HOLD",issue_137="OPEN")


if __name__=="__main__":
    need(len(sys.argv)==1,"unexpected_arguments")
    main()
