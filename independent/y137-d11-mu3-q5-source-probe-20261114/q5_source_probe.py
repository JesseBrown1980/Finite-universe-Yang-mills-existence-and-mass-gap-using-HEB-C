#!/usr/bin/env python3
"""Independent REAL Q5 source-row completeness probe for next odd μ3.

Reads the exact accepted K3 V1/b group-0 spool from hosted run
43613345828. SHA and count must agree with immutable prior source.
Independently rederive 72 raw moves, gauge-fixed targets, magnetic
energy and orbit weights for 128 sampled real shell5 states. This
does NOT calculate an entire μ3 or omit source rows by pretending a
sample is the full supported operator.
"""
import hashlib
import os
import struct
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
sys.path.insert(0,os.path.join(ROOT,"independent"))
sys.path.insert(0,os.path.join(ROOT,"independent",
                              "y137-d11-shell5-spill-20261114"))
import finite_s3_3x4_r9_first_gap as original
import independent_move_rule as independent

PATH=os.environ.get("Y137_D11_Q5_SPOOL",
                    os.path.join(ROOT,"build","y137-q5-real-source","GROUP-0.v1"))
HEADER=struct.Struct("<Q B H H")
EXPECTED_SHA="3f561c26f3cf5b355ab769ae96e9da8ceaa141186fb5ecb80cc1ec4227e4c589"
EXPECTED_COUNT=435324
EXPECTED_LENGTH=72717336
WIDTH=82
COLS=8
MAX_SAMPLES=128
STEP=3000


def need(ok,why):
    if not ok:
        print("Y137_D11_MU3_Q5_REFUSE|reason="+why+"|json=0",flush=True)
        raise SystemExit(1)


def emit(name,**fields):
    print(name+"|"+"|".join(str(k)+"="+str(v)
                           for k,v in fields.items())+"|json=0",flush=True)


def unpack(value):
    need(value.bit_length()<=WIDTH*COLS,"signed_or_overflowed_Q5_lane")
    mask=(1<<WIDTH)-1
    return tuple((value>>(k*WIDTH))&mask for k in range(COLS))


def rows():
    need(os.path.getsize(PATH)==EXPECTED_LENGTH,"old_V1_spool_length")
    h=hashlib.sha256()
    count=0
    output=[]
    with open(PATH,"rb") as f:
        while True:
            header=f.read(HEADER.size)
            if not header:
                break
            need(len(header)==HEADER.size,"partial_target_header")
            code,w,n0,n1=HEADER.unpack(header)
            raw0=f.read(n0)
            raw1=f.read(n1)
            need(len(raw0)==n0 and len(raw1)==n1,
                 "truncated_target_coefficients")
            h.update(header)
            h.update(raw0)
            h.update(raw1)
            need(code%8==0 and w in (1,2,3,6),
                 "Q5_target_key_or_weight")
            if count%STEP==0 and len(output)<MAX_SAMPLES:
                p0=int.from_bytes(raw0,"little")
                p1=int.from_bytes(raw1,"little")
                output.append((code,w,unpack(p0),unpack(p1)))
            count+=1
    need(h.hexdigest()==EXPECTED_SHA and count==EXPECTED_COUNT,
         "original_accepted_V1_spool_not_reproduced")
    need(len(output)==MAX_SAMPLES,"not_enough_independent_Q5_rows")
    return output


def run():
    samples=rows()
    total_moves=0
    nontrivial_self=0
    checked_reverse=0
    # A self-consistent extra self-loop cannot be accepted as a real
    # electric move merely because row sums and W balance survive:
    # compare the original row against independent permutation gauge.
    planted_refused=False
    for i,(code,w,vec0,vec1) in enumerate(samples):
        key=original.decode(code)
        need(original.weight(key)==w,"Q5_weight_mismatch")
        near=original.neighbors(key)
        need(sum(near.values())==72,"missing_raw_move")
        try:
            independent.audit_original(
                key,near,w,original.magnetic(original.from_key(key)),
                original.KEPT,original.TRANS)
        except ValueError:
            need(False,"separate_S3_permutation_checker_disagrees")
        total_moves+=72
        nontrivial_self+=near.get(key,0)
        if i<8:
            for target,coefficient in list(near.items())[:3]:
                wt=original.weight(target)
                need(w*coefficient%wt==0,
                     "weighted_reverse_not_integer")
                reverse=w*coefficient//wt
                need(original.neighbors(target).get(key,0)==reverse,
                     "reverse_electric_row_fault")
                checked_reverse+=1
        if i==0:
            altered=near.copy()
            bad=next((x for x in altered if x!=key),None)
            need(bad is not None,"not_a_real_nonself_move")
            altered[bad]-=1
            if altered[bad]==0:
                del altered[bad]
            altered[key]=altered.get(key,0)+1
            need(sum(altered.values())==72,
                 "planted_tamper_invariant_changed")
            try:
                independent.audit_original(
                    key,altered,w,original.magnetic(original.from_key(key)),
                    original.KEPT,original.TRANS)
            except ValueError:
                planted_refused=True
        need(any(vec0) or any(vec1),"zero_Q5_row_outside_active_support")
    need(planted_refused,"folded_Q5_edge_not_detected")
    emit("Y137_D11_MU3_Q5_REAL_PROBE",
         accepted_source_run=43613345828,
         original_mu2_run=43606393196,
         fully_sha_verified_group0_Q5_targets=EXPECTED_COUNT,
         audited_Q5_source_rows=len(samples),
         independently_rebuilt_raw_moves=total_moves,
         exact_S3_canonicalization="PASS",
         original_72_moves_per_row="PASS",
         W_orbit_size_and_magnetic="PASS",
         real_reverse_electric_edges=checked_reverse,
         exact_selfloop_raw_move_count=nontrivial_self,
         planted_edge_as_selfloop="REFUSED",
         source_vectors="REAL_SIGNED_E1_E2_V1_OVER_B_SHELL5",
         whole_Q5_source_completeness="NOT_YET_TESTED",
         real_mu3="NOT_COMPUTED",
         degree11_remaining_moments=19,
         original_Wilson_weight="HOLD",issue_137="OPEN")


if __name__=="__main__":
    run()
