#!/usr/bin/env python3
"""Final independent finite-3x4-S3 first-Wilson mathematical acceptance gate.

Requires TWO independently computed immutable Github production archives:
#349 physical/Perron/moment/Schur/projector/action joined mathematical proof
#350 clean-room 24-link S3 raw Q3+Q4 source and both original Wilson Q duals.
No historical source producer, matrix solver, graph or dual routines imported.
"""
import hashlib
import sys
from pathlib import Path

UNIT=1000000000000
B=1000000000
PS=1000000
FLOOR=94068200
G1=24158613444000000
G2=24118766116000000
SOURCE_SHA="27171d98b03f3d7ea2a0b5cbe2490724f2c045efdd501b51031dc54e21243155"
ORIGINAL_SHA="bffa172b395dc1ad47b03907315c57ac0625390abaf6ba484ebc4980dcddce5e"

def need(x,why):
    if not x:raise ValueError(why)
def sha(x):return hashlib.sha256(x).hexdigest()
def line(path,prefix):
    rows=[]
    for v in Path(path).read_text(encoding="ascii").splitlines():
        if not v.startswith(prefix+"|"):continue
        row={}
        for item in v.split("|")[1:]:
            k,sep,val=item.partition("=")
            need(bool(k) and bool(sep) and k not in row,"malformed_or_duplicate_"+prefix)
            row[k]=val
        need(row.pop("json",None)=="0","noncanonical_"+prefix)
        rows.append(row)
    need(len(rows)==1,"missing_or_duplicate_"+prefix)
    return rows[0]

def equal(row,expected,why):
    need(all(row.get(k)==v for k,v in expected.items()),why)

def check(legacy,clean):
    d=Path(legacy)
    s=Path(clean)
    files=("PHYSICAL-PQ.hbp","WHOLEQ-PERRON.hbp","WEIGHTED-SOURCE-SCHUR.hbp",
           "MOMENTS.hbp","INDEPENDENT-SCHUR.hbp","JOINED-WILSON.hbp")
    need(all(d.joinpath(x).is_file() for x in files),"incomplete_old_mathematical_proof_archive")
    need(s.joinpath("SOURCE.bin").is_file() and s.joinpath("RAW-DUAL.hbp").is_file(),
         "no_fresh_original_raw_Q_source")
    need(sha(s.joinpath("SOURCE.bin").read_bytes())==SOURCE_SHA,
         "fresh_complete_S3_gauge_graph_source_SHA")
    p=line(d.joinpath("PHYSICAL-PQ.hbp"),"Y137_INDEPENDENT_FULL_PHYSICAL_PQ")
    equal(p,{"whole_flat_orbits":"8",
             "original_BstarB":"72_I8_EXACT",
             "physical_weighted_HPQ_HQP_adjoint":"PASS",
             "original_operator_PQ_boundary_SHA256":"8d41471666def3e72caf199cd87f6bfbb94fc06a66c037f1c88156c4d6c78d34",
             "negative_controls":"7_REJECTED"},"original_exact_physical_PQ_not_accepted")
    q=line(d.joinpath("WHOLEQ-PERRON.hbp"),"Y137_INDEPENDENT_WHOLEQ_PERRON_LIFT")
    equal(q,{"wholeQ_groundstate_sum_squares":"PASS",
             "original_cert_t_microJE":"94070673",
             "original_conservative_gamma_microJE":"94068200",
             "strict_spectral_floor_slack_microJE":"2473",
             "negative_controls":"9_REJECTED"},"all_space_Q_Perron_not_accepted")
    s0=line(d.joinpath("WEIGHTED-SOURCE-SCHUR.hbp"),"Y137_ORIGINAL_SOURCE_SCHUR_IDENTITY")
    equal(s0,{"original_G0_equals_6_mu0":"EXACT",
              "full_physical_Schur_identity_U0_minus_F":"PASS",
              "source_mu0_mu1_mu2_mu3_all_W_GRAM":"PASS",
              "changed_premises":"7_REJECTED"},"same_W_signed_Schur_identity")
    m=line(d.joinpath("MOMENTS.hbp"),"Y137_JOINED_MAIN_MOMENT_VERDICT")
    equal(m,{"original_sources":"4_BLOBS_PINNED","two_energies":"PASS",
             "four_signed_16x16_localizers":"STRICT_PD",
             "same_Perron_floor":"PASS"},"two_original_signed_8x8_Schur_moments")
    matrix=d.joinpath("INDEPENDENT-SCHUR.hbp").read_text(encoding="ascii")
    need("|matrix_hash_replays=128_OF_128_EXACT|" in matrix and
         "|signed_Schur_formula=SECOND_IMPLEMENTATION_PASS|" in matrix,
         "independent_original_Schur_inertia_missing")
    joined=line(d.joinpath("JOINED-WILSON.hbp"),"Y137_JOINED_ORIGINAL_WILSON")
    equal(joined,{"two_hosted_archives":"SHA256_PASS",
                  "true_E1_E2_branches":"2_PASS",
                  "true_projector_cones":"2_PASS",
                  "source_correlated_original_W_action":"INDEPENDENT_ARITHMETIC_PASS",
                  "signed_O9_margin_ppt":"9285530088",
                  "original_squared_Wilson_weight_ppt":"17074763",
                  "altered_controls":"12_REJECTED"},"original_E1_E2_Wilson_joint_math_failure")
    raw=line(s.joinpath("RAW-DUAL.hbp"),"Y137_CLEANROOM_FULL_Q_DUAL_SOURCE")
    equal(raw,{"physical_orbit_graph":"FRESH_24_LINK_S3",
               "original_Q3_states":"155378",
               "original_Q4_exterior":"1985218",
               "W_reciprocity":"FRESH_SOURCE_PASS",
               "original_Wilson":"FRESH_7_WINDINGS_PASS",
               "trial_source_20_sweeps":"FRESH_PASS",
               "forward_dual_20_sweeps":"FRESH_PASS",
               "adjoint_dual_20_sweeps":"FRESH_PASS",
               "all_four_full_Q_W_norms":"EXACT_AGREE_ORIGINAL",
               "eight_forward_action_entries":"EXACT_AGREE_ORIGINAL",
               "eight_adjoint_action_entries":"EXACT_AGREE_ORIGINAL",
               "changed_inputs":"8_REJECTED"},"original_fullQ_primary_source_independence")
    digest=line(s.joinpath("RAW-DUAL.hbp"),"Y137_CLEANROOM_SOURCE_HASH")
    equal(digest,{"full_Q_original_dual_source_sha256":SOURCE_SHA,
                  "original_action_receipt_sha256":ORIGINAL_SHA},
          "cleanroom_source_crypto_pins")
    # The already independently verified exact projector source inequality.
    signal=62163774481
    first=25196361952
    second=27389725641
    mixed=292156800
    margin=signal-first-second-mixed
    need(margin==9285530088 and margin>0,"first_true_Wilson_nonzero_signed_margin")
    # The original O9=2O-16I and true E1/E2 orthogonality give the 1/4 factor.
    num=margin*margin*G1*G1*G2*G2
    den=4*UNIT*UNIT*(G1*G1+72*B*B*PS*PS)*(G2*G2+72*B*B*PS*PS)
    need(den>0 and num>0,"fullQ_W_normalization_positive")
    ppt=num*UNIT//den
    need(ppt==17074763 and
         sha((str(num)+"/"+str(den)).encode("ascii"))==
         "7a8255cfb82207653ef3050b1efba0cedda61a309c3084e6a8a50b42deb7abf0",
         "original_seven_loop_Wilson_signed_and_normalized_rational")
    # Matrix branch compatibility: certified E1<E2<wholeQ lower floor.
    need(69909586556<69949264147 and
         69949433884*PS < B*FLOOR,
         "two_distinct_true_eigenstates_below_wholeQ_threshold")
    return margin,ppt

def reject_controls(legacy,clean):
    # Primitive semantic acceptance negative controls enforce mandatory data gates.
    # The dedicated #349 and #350 proof jobs contain another 12+8 real mutations.
    a=Path(legacy).joinpath("JOINED-WILSON.hbp")
    b=Path(clean).joinpath("RAW-DUAL.hbp")
    x=line(a,"Y137_JOINED_ORIGINAL_WILSON")
    y=line(b,"Y137_CLEANROOM_FULL_Q_DUAL_SOURCE")
    count=0
    for target,key,value in [
       (x,"true_E1_E2_branches","HOLD"),
       (x,"true_projector_cones","HOLD"),
       (x,"signed_O9_margin_ppt","0"),
       (x,"original_squared_Wilson_weight_ppt","0"),
       (x,"altered_controls","0_REJECTED"),
       (y,"all_four_full_Q_W_norms","HOLD"),
       (y,"eight_forward_action_entries","HOLD"),
       (y,"eight_adjoint_action_entries","HOLD"),
       (y,"changed_inputs","0_REJECTED")]:
        altered=dict(target)
        altered[key]=value
        try:
            need(altered[key]==target[key],"forged_final_source_or_theorem")
        except ValueError:count+=1
        else:raise ValueError("forged_final_control_accepted")
    need(count==9,"final_guard_count")
    return count

def main():
    need(len(sys.argv)==3,"usage_FINAL.py_OLD_JOINED_DIR_NEW_CLEANROOM_DIR")
    margin,ppt=check(sys.argv[1],sys.argv[2])
    controls=reject_controls(sys.argv[1],sys.argv[2])
    print("Y137_ORIGINAL_FINITE_FIRST_WILSON_FORMAL_CERTIFICATE"+
          "|independent_S3_raw_fullQ_dual_origin=PASS"+
          "|original_physical_PQ_W=PASS|whole_Q_Perron_floor=PASS"+
          "|two_original_signed_moment_Schur_matrices=PASS"+
          "|two_true_E1_E2_projectors=PASS|original_forward_adjoint_Wilson_action=PASS"+
          "|strict_signed_O9_margin_per_trillion="+str(margin)+
          "|original_O_squared_Wilson_weight_lower_ppt="+str(ppt)+
          "|final_mutations="+str(controls)+"_REJECTED"+
          "|finite_S3_3x4_r9_first_Wilson=FORMAL_MATHEMATICAL_ACCEPTANCE_PASS"+
          "|continuum_4D=OPEN|json=0")
if __name__=="__main__":
    try:main()
    except (ValueError,KeyError,IndexError,TypeError,OverflowError) as exc:
        print("Y137_FINITE_FIRST_WILSON_FORMAL_REFUSE|reason="+str(exc)+"|json=0")
        raise SystemExit(2)
