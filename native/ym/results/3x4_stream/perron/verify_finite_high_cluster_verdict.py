#!/usr/bin/env python3
"""Audit and register an ACCEPTED finite 3x4 S3 high-cluster Perron gap.

Reads historical certificates, original rule and original proof by exact
pinned Git blob SHA-1; no source files or previous receipts are edited.
No new 2.177B-state eigenproblem or independently hosted 45.5M-row run.
The ACCEPT verdict is finite E9-E8 conditional on the original recorded
computational certificates and orbit-lift theorem. E2-E1 remains OPEN.

Twelve predictions frozen before executable at commit
6ef0da44f761e150318cb5f047f40eb04ea23d10.
"""
from hashlib import sha1,sha256
from pathlib import Path
import sys

faults=("false_top_bound","fake_original_PASS","wrong_ball_upper",
        "false_full_rebuild","false_pairs_PASS","false_lift",
        "wrong_gap_arithmetic")
fault=""
if len(sys.argv)>2 or (len(sys.argv)==2 and
    (not sys.argv[1].startswith("sabotage=") or sys.argv[1][9:] not in faults)):
    print("usage: verify_perron_finite_verdict.py [sabotage=CONTROL]")
    sys.exit(2)
if len(sys.argv)==2:
    fault=sys.argv[1][9:]

def gate(condition,label):
    if not condition:
        print("FAILED|check="+label+"|json=0")
        sys.exit(1)

def emit(name,**kwargs):
    print(name+"|"+"|".join(key+"="+str(value) for key,value in kwargs.items())
          +"|json=0",flush=True)

def read_pinned(root,path,blob):
    raw=root.joinpath(*path).read_bytes()
    b=b"blob "+str(len(raw)).encode("ascii")+bytes((0,))+raw
    gate(sha1(b).hexdigest()==blob,"source_blob_"+path[-1])
    return raw,raw.decode("utf-8").splitlines()

def only(lines,prefix):
    matches=[row for row in lines if row.startswith(prefix)]
    gate(len(matches)==1,"unique_original_"+prefix.split("|")[0])
    return matches[0]

def val(row,key):
    found=[z[len(key)+1:] for z in row.split("|")
           if z.startswith(key+"=")]
    gate(len(found)==1,"unique_field_"+key)
    return found[0]

def equal(row,key,expected):
    gate(val(row,key)==expected,"field_"+key)

def certify(root):
    folder=("native","ym","results","3x4_stream","perron")
    raw,lines=read_pinned(root,folder+("PERRON-RESULT.hbp",),
       "cbd428014a4d440732a5c0a541ed57a9041becee")
    _,text=read_pinned(root,folder+("PERRON-BOUND.md",),
       "53378d4ee68dc88766873713285e3a34465a9d90")
    _,registered=read_pinned(root,("native","ym","results","3x4_stream",
       "GAP-VERDICT-RULE-3X4.md"),
       "42bfad8820daa8a34c9501d57f35e49447c552de")
    gate("only" in "\n".join(registered[:8]) and
         "t_milli = 60000000" in "\n".join(registered[:8]),
         "existing_60M_rule_separate")
    proof="\n".join(text)
    gate("## 2. From the sector to the whole space" in proof and
         "(H′_whole d̃)(x)" in proof and
         "the same minimum bounds" in proof and
         "Cauchy interlacing" in proof,
         "whole_space_orbit_lift_proof")
    if fault=="false_lift":
        gate("Sx+Sy+ positive vector does not lift" in proof,
             "RED_false_lift")

    original=only(lines,"PERRON_RESULT|")
    equal(original,"gap_verdict","OPEN")
    equal(original,"best_t_cert_milli","94070673")
    if fault=="fake_original_PASS":
        gate(val(original,"gap_verdict")=="PASS","RED_fake_original_PASS")

    sector=only(lines,"RESULT_P0|")
    for key,expect in (("n","45508080"),("flat_states","7"),
        ("flat_diag_max","72"),("flat_flat_couplings","0"),
        ("merkle","PASS")):
        equal(sector,key,expect)

    keys=only(lines,"RESULT_KEY_TABLE|")
    equal(keys,"sum_w","6^13=13060694016")
    equal(keys,"sum_flat_w","18=commuting_pairs_in_S3")
    equal(keys,"min_nonflat_M","3")

    flats=only(lines,"RESULT_WHOLE_FLATS|")
    for key,expect in (("flat_states","8"),("flat_diag_max","72"),
                       ("flat_flat_couplings","0")):
        equal(flats,key,expect)

    top=only(lines,"RESULT_PERRON_3x4_TOP|")
    for key,expect in (("t_cert_milli","94070673"),("min_row","45507968"),
           ("min_mag","3"),("perroncert_check","94070673"),
           ("check_d_strict","94070673"),("outside_go_checker","94070673"),
           ("merkle","PASS"),
           ("d_sha256","f5c5428db1fc5d91d2ab891689f0dac7263dc26c8f9b60a2db82728f6ea0dcd1")):
        equal(top,key,expect)
    if fault=="false_top_bound":
        gate(int(val(top,"t_cert_milli"))==94070674,"RED_false_top_bound")

    outsider=only(lines,"RESULT_OUTSIDE_GO_41509351749|")
    equal(outsider,"run","41509351749")
    for key in ("merkle","sector_hashes","vector_hashes",
                "row_sums_zero","W_self_adjoint"):
        equal(outsider,key,"PASS")

    rebuild=only(lines,"RESULT_FULLREBUILD|")
    equal(rebuild,"rows_rebuilt","45508080")
    equal(rebuild,"rows_read","45508080")
    equal(rebuild,"sectors_match_public_manifest","34/34")
    equal(rebuild,"merkle","PASS")
    for key in ("canonical_key_mismatch","weight_mismatch","M_mismatch",
                "entries_mismatch"):
        equal(rebuild,key,"0")
    if fault=="false_full_rebuild":
        gate(val(rebuild,"entries_mismatch")=="1","RED_false_full_rebuild")

    paired=only(lines,"RESULT_ALLPAIRS_PIN_3x4|")
    equal(paired,"pairs","1632625631")
    equal(paired,"passes","4")
    equal(paired,"requirements","31")
    equal(paired,"requirements_met","31")
    for key in ("header_entries","whole_space_count","merkle_each_pass",
                "verdict"):
        equal(paired,key,"PASS")
    for key in ("value_mismatch","lower_without_upper","upper_without_lower",
                "structure_counters"):
        equal(paired,key,"0")
    if fault=="false_pairs_PASS":
        gate(val(paired,"value_mismatch")=="1","RED_false_pairs_PASS")

    ball=only(lines,"RESULT_E8_WHOLE|lattice=3x4|r=9|ball_K=3|")
    equal(ball,"N_ball_at_70.031","8")
    equal(ball,"ambiguous","0")
    equal(ball,"ball_states","155386")
    if fault=="wrong_ball_upper":
        gate(val(ball,"N_ball_at_70.031")=="7","RED_wrong_ball_upper")

    reported=only(lines,"RESULT_GAP_ARITHMETIC_TOP|")
    equal(reported,"verdict","OPEN")
    equal(reported,"r9","t_cert-70.031=24.039673")
    equal(reported,"all_r_ge_9",
          "t_cert-72+3(r-9)=22.070673+3(r-9)")
    scope=only(lines,"RESULT_SCOPE|")
    equal(scope,"gap_verdict","OPEN_operators_word")
    equal(scope,"uniformity_in_volume","OPEN")
    equal(scope,"continuum_limit","OPEN")

    full_orbits=(6*6*6*6*6*6*6*6*6*6*6*6*6+
                 3*2*2*2*2*2*2*2*2*2*2*2*2*2+
                 2*3*3*3*3*3*3*3*3*3*3*3*3*3)//6
    gate(full_orbits==2177317873,"whole_gauge_orbit_Burnside")
    weighted=1
    for _ in range(13):
        weighted*=6
    gate(weighted==13060694016,"whole_gauge_fixed_weight_census")

    top_micro=int(val(top,"t_cert_milli"))
    e8_r9_micro=70031000
    flat_micro=72000000
    gap9=top_micro-e8_r9_micro
    gap_high=top_micro-flat_micro
    if fault=="wrong_gap_arithmetic":
        gate(gap9==24039674,"RED_wrong_gap_arithmetic")
    gate(gap9==24039673 and gap_high==22070673,
         "all_gap_arithmetic_exact")
    gate(e8_r9_micro<top_micro and flat_micro<top_micro,
         "strict_nonzero_finite_cluster_gap")
    emit("FINITE_PER3X4_SOURCE",
         original_HBP_SHA256=sha256(raw).hexdigest(),
         original_gap_verdict="OPEN_IMMUTABLE",
         registered_60M_rule="UNCHANGED",
         full_space_orbits=full_orbits,
         sector_orbits=45508080,
         orbit_weight_sum=weighted,
         external_replica_Go_run=41509351749)
    emit("FINITE_PER3X4_EVIDENCE",
         vector_sha256=val(top,"d_sha256"),
         tcert_micro=top_micro,min_row=45507968,magnetic_min=3,
         original_rebuild_rows=45508080,original_rebuild_mismatches=0,
         original_pair_checks=1632625631,
         original_pair_mismatches=0,original_header_gates="PASS",
         source="PINNED_ORIGINAL_RECEIPTS")
    emit("FINITE_PER3X4_VERDICT",
         status="ACCEPTED_FINITE_HIGH_CLUSTER_BOUND_FROM_PINNED_EVIDENCE",
         lattice="3x4",group="S3",JE=1,r=9,
         E9_full_lower_micro=top_micro,
         E8_full_upper_micro=e8_r9_micro,
         E9_minus_E8_lower_micro=gap9,
         first_excitation_E2_minus_E1="NOT_CERTIFIED",
         source_original_verdict="OPEN")
    emit("FINITE_PER3X4_COUPLINGS",
         range="r_GE_9",
         lower_micro_at_r9=gap_high,
         lower_micro_slope_per_unit_r=3000000,
         statement="E9_minus_E8_GE_22.070673_plus_3_times_r_minus_9",
         from="MAGNETIC_MIN_NONFLAT_M_EQUALS_3")
    emit("FINITE_PER3X4_LIMITS",
         accepts_historical_computational_evidence="YES",
         independent_entire_store_replay_another_machine="OPEN",
         external_go_exact_all_pairs="NOT_DONE",
         old_record_retained="YES",
         original_rule_60M="REMAINS_REGISTERED",
         numerical_first_gap="OPEN",
         uniform_volume="OPEN",fourD_SU2_Clay="OPEN")

def main():
    root=Path(__file__).resolve().parents[5]
    prediction=root.joinpath("native","ym","results","3x4_stream","perron",
       "PREDICT-FINITE-HIGH-CLUSTER-VERDICT-20261107.hbp").read_bytes()
    gate(sum(int(z.startswith(b"PREDICT|id="))
             for z in prediction.splitlines())==12,"predicted_twelve_rows")
    emit("FINITE_PER3X4_BEGIN",
         prediction_sha256=sha256(prediction).hexdigest(),
         verdict="FINITE_E9_MINUS_E8_ONLY",
         existing_evidence_new_fullspace_solver="NO")
    certify(root)
    emit("FINITE_PER3X4_VERIFY",status="PASS",
         new_rule_scope="FINITE_HIGH_CLUSTER_ONLY",
         original_receipt_immutable="YES",
         original_60M_rule_unmodified="YES",
         continuum_claim="NOT_CERTIFIED")

if __name__=="__main__":
    main()
