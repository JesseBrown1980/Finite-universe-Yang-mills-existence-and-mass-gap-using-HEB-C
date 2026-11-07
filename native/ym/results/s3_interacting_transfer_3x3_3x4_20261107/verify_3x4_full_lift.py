#!/usr/bin/env python3
"""Exact conditional 3x4 S3 whole-space Perron lift and winding selection.

No new 2.17B-state eigenanalysis; verifies pinned existing sector-vector
certificate and source's explicit orbit-lift, then derives full low-eight
zero-momentum placement and exact O_alt E1 darkness for r>=9.
Original source verdict OPEN is deliberately preserved.
Predictions frozen before this code at commit 5c3daf5f832c6494dffd16927e018314abc7d8b9.
Integer-only, HBP receipts, source SHA-1 blob pins.
"""
from hashlib import sha1, sha256
from itertools import product
from pathlib import Path
import sys

CONTROLS=("wrong_tcert","fake_gap_verdict","wrong_flat_bound",
          "wrong_alt_parity","wrong_full_rebuild")
red=""
if len(sys.argv)>2 or (len(sys.argv)==2 and
        (not sys.argv[1].startswith("sabotage=")
        or sys.argv[1][9:] not in CONTROLS)):
    print("usage: verify_3x4_full_lift.py [sabotage=NAME]")
    sys.exit(2)
if len(sys.argv)==2:
    red=sys.argv[1][9:]


def check(condition,label):
    if not condition:
        print("FAILED|check="+label+"|json=0")
        sys.exit(1)


def emit(label,**fields):
    print(label+"|"+"|".join(str(k)+"="+str(v) for k,v in fields.items())
          +"|json=0",flush=True)


def getfile(root,path,expected):
    raw=root.joinpath(*path).read_bytes()
    blob=b"blob "+str(len(raw)).encode("ascii")+bytes((0,))+raw
    check(sha1(blob).hexdigest()==expected,
          "source_git_blob_"+path[-1])
    return raw,raw.decode("utf-8").splitlines()


def one(lines,prefix):
    found=[r for r in lines if r.startswith(prefix)]
    check(len(found)==1,"one_source_row_"+prefix.split("|")[0])
    return found[0]


def field(row,name):
    found=[x[len(name)+1:] for x in row.split("|")
           if x.startswith(name+"=")]
    check(len(found)==1,"source_field_"+name)
    return found[0]


def gate_perron(root):
    folder=("native","ym","results","3x4_stream","perron")
    raw,lines=getfile(root,folder+("PERRON-RESULT.hbp",),
                      "cbd428014a4d440732a5c0a541ed57a9041becee")
    _,md=getfile(root,folder+("PERRON-BOUND.md",),
                 "53378d4ee68dc88766873713285e3a34465a9d90")
    text="\n".join(md)
    check("## 2. From the sector to the whole space" in text
          and "Lift d from the sector" in text
          and "whole gauge-invariant space, all momenta" in text
          and "the same minimum bounds" in text,
          "original_orbit_lift_proof_present")
    result=one(lines,"PERRON_RESULT|")
    check(field(result,"gap_verdict")=="OPEN",
          "original_gap_verdict_must_remain_OPEN")
    if red=="fake_gap_verdict":
        check(field(result,"gap_verdict")=="PASS",
              "RED_fake_gap_verdict")
    check(field(result,"best_t_cert_milli")=="94070673"
          and field(result,"both_checkers_agree")=="1",
          "two_checker_top_value")
    sector=one(lines,"RESULT_P0|")
    check(field(sector,"n")=="45508080"
          and field(sector,"flat_states")=="7"
          and field(sector,"flat_diag_max")=="72"
          and field(sector,"flat_flat_couplings")=="0"
          and field(sector,"merkle")=="PASS",
          "sector_operator_layout")
    flat=one(lines,"RESULT_WHOLE_FLATS|")
    check(field(flat,"flat_states")=="8"
          and field(flat,"flat_diag_max")=="72"
          and field(flat,"flat_flat_couplings")=="0",
          "original_eight_full_flat")
    top=one(lines,"RESULT_PERRON_3x4_TOP|")
    correct=int(field(top,"t_cert_milli"))
    if red=="wrong_tcert":
        check(correct==94070674,"RED_wrong_tcert")
    check(correct==94070673 and
          field(top,"min_row")=="45507968" and
          field(top,"min_mag")=="3" and
          field(top,"perroncert_check")=="94070673" and
          field(top,"check_d_strict")=="94070673" and
          field(top,"outside_go_checker")=="94070673" and
          field(top,"merkle")=="PASS",
          "original_three_checker_top_bound")
    rebuild=one(lines,"RESULT_FULLREBUILD|")
    if red=="wrong_full_rebuild":
        check(field(rebuild,"canonical_key_mismatch")=="1",
              "RED_wrong_full_rebuild")
    check(field(rebuild,"rows_rebuilt")=="45508080"
          and field(rebuild,"rows_read")=="45508080"
          and all(field(rebuild,k)=="0" for k in (
              "canonical_key_mismatch","weight_mismatch",
              "M_mismatch","entries_mismatch"))
          and field(rebuild,"merkle")=="PASS",
          "original_full_sector_row_rebuild")
    # Check two prior independently written small whole-space replays.
    small=[x for x in lines if x.startswith("RESULT_LIFT|")]
    check(len(small)==2
          and any("lattice=2x2|" in x for x in small)
          and any("lattice=2x3|" in x for x in small),
          "original_small_volume_lift_crosschecks")
    gap=one(lines,"RESULT_GAP_ARITHMETIC_TOP|")
    check(field(gap,"verdict")=="OPEN"
          and field(gap,"all_r_ge_9")==
               "t_cert-72+3(r-9)=22.070673+3(r-9)",
          "original_global_gap_scope")
    emit("PER3X4_SOURCE",symmetry_sector="Sx+Sy+",
         sector_orbits=45508080,flat_in_sector=7,
         flat_full_orbits=8,full_gauge_orbits=2177317873,
         original_tcert_milli=94070673,
         checker_perron="PASS",checker_strict="PASS",
         outside_go_replay="PASS",rebuild_rows=45508080,
         original_gap_verdict="OPEN",
         original_hbp_sha256=sha256(raw).hexdigest())
    return correct


def check_translation_pi():
    # The character χ(Wx(y)) is a local-gauge invariant traced closed
    # winding. Its *list* transforms by cyclic relabeling under Ty.
    # Enumerate all 3^4 possible character-value patterns, not a
    # sampling of full lattice configurations.
    symbols=(2,0,-1)
    cases=0
    for x in product(symbols,repeat=4):
        xp=tuple(x[(i+1)%4] for i in range(4))
        odd=x[0]-x[1]+x[2]-x[3]
        oddp=xp[0]-xp[1]+xp[2]-xp[3]
        even=sum(x)
        evenp=sum(xp)
        if red=="wrong_alt_parity" and cases==1:
            check(oddp==odd and odd!=0,"RED_wrong_alt_parity")
        check(oddp==-odd and evenp==even,
              "universal_y_translation_operator_parity")
        cases+=1
    check(cases==81,"all_character_patterns")
    emit("PER3X4_WINDING_SYMMETRY",
         value_patterns=81,local_gauge_invariance="TRACED_CLOSED_WINDING",
         unit_y_translation_Oalt_eigenvalue="-1",
         unit_y_translation_Osum_eigenvalue="+1",
         every_character_pattern="CHECKED_EXACTLY")


def global_theorem(bound):
    # Certified source gives E9^full(9)>= bound/1e6, via positive G-orbit
    # vector on H'_whole and Cauchy interlacing. This is *not* just
    # an Sx+Sy+ principal-block lower bound: positivity permits lifting.
    #
    # The eight magnetic-flat trial basis states have zero momentum
    # (independently verified in verify_flat_transfer.py), and
    # P_flat H(r) P_flat=72 I_8 for all r, so E8^T(r)<=72.
    # Since H(r)-H(9)=(r-9)M>=0 for r>=9, the full E9 cannot fall.
    # 72 < 94.070673, so all lowest eight states must be in T.
    flat=72*1000000
    if red=="wrong_flat_bound":
        check(flat==71*1000000,"RED_wrong_flat_bound")
    check(flat<bound and bound==94070673,
          "spectral_gap_separates_low_T_octet")
    emit("PER3X4_GLOBAL_T_THEOREM",
         lattice="3x4",couplings="r_ge_9",
         E9_full_lower_at_r9="[94.070673,+inf)",
         E8_T_upper_all_r="72.000000",
         source="POSITIVE_VECTOR_POINTWISE_WHOLE_ORBIT_LIFT",
         minmax="E8_T_LE_72",
         magnetic_monotonicity="E9_FULL_NONDECREASING",
         low_eight_all_zero_momentum="CONDITIONAL_ON_ORIGINAL_PERRON_CERT",
         original_verdict="OPEN")
    emit("PER3X4_GLOBAL_SELECTION",lattice="3x4",r_range="r_ge_9",
         interacting_ground_momentum="ZERO",
         interacting_first_excitation_momentum="ZERO",
         alternating_winding_momentum="PI",
         alternating_winding_E1_weight="ZERO_EXACT_IF_LIFT_VALID",
         summed_winding_E1_weight="OPEN",
         nonflat_mixing="DOES_NOT_BREAK_TRANSLATION_SELECTION",
         full_E1_gap_value="OPEN")


def main():
    root=Path(__file__).resolve().parents[4]
    pred=root.joinpath("native","ym","results",
       "s3_interacting_transfer_3x3_3x4_20261107",
       "PREDICTION-3X4-LIFT.hbp").read_bytes()
    check(sum(int(x.startswith(b"PREDICT|id=")) for x in pred.splitlines())
          ==10,"frozen_ten_prediction_rows")
    emit("PER3X4_BEGIN",prediction_sha256=sha256(pred).hexdigest(),
         source_status="ORIGINAL_GAP_VERDICT_OPEN",
         new_full_space_inertia="NOT_RUN")
    bound=gate_perron(root)
    check_translation_pi()
    global_theorem(bound)
    emit("PER3X4_VERIFY",status="PASS_CONDITIONAL",
         low_eight_translation_zero="SOURCE_CONDITIONAL",
         first_E1_alternating_winding_overlap="EXACT_ZERO_CONDITIONAL",
         first_E1_summed_winding_overlap="OPEN",
         original_gap_verdict="OPEN",
         actual_global_first_gap_size="OPEN",
         spatial_4D_SU2="NOT_PROVED")


if __name__=="__main__":
    main()
