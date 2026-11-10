# FC assembly seat: builds PREDICTION-FINITE-CONTINUOUS-20261109.hbp from the three lane row files,
# adds blindness and pre-freeze provenance, makes every falsifier explicit, then lints the result.
# String processing and sha256 only; no arithmetic on measured data. Run: python3 -I -B fc_assemble.py <fc-tests dir>
# Fix seat edits (2026-11-09): blindness recodes F1/F2, source FC1-S11, verdict-rule and value-label edits, PF annotations,
# extra lint. Each change is listed with its reason in final/CHANGES.txt; edited rows carry a fix= field.
# Refix seat edits (after verify round 2): see the rfx()/FOV2 block and CHANGES.txt section VERIFY-ROUND; notes carry "R3:".
# Refix seat round 3 (after verify round 4): see the rfx5() block and CHANGES.txt section VERIFY-ROUND-4; notes carry "R5:".
import sys
import hashlib
import re

B = sys.argv[1]
FINAL = B + "/final"
OUTNAME = "PREDICTION-FINITE-CONTINUOUS-20261109.hbp"
SCR = "/tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/fc-tests"


def h16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def parse(path):
    rows = []
    for line in open(path):
        line = line.rstrip("\n")
        if not line:
            continue
        f = line.split("|")
        kv = []
        for x in f[1:]:
            k, v = x.split("=", 1)
            kv.append((k, v))
        rows.append((f[0], kv))
    return rows


L1 = parse(B + "/T1/ROWS.hbp")
L2 = parse(B + "/T2/ROWS.hbp")
L3 = parse(B + "/T3/ROWS.hbp")

# ------------------------------------------------------------------ blindness and provenance (assembly judgement)
# blind: 1 = no pre-freeze computation or prior report gives the measured value on any instance in scope;
# partial = some instances were computed pre-freeze or reported before; 0 = the value was already known (control);
# weak = computed pre-freeze by a tool that is exact on one side of the quantity; na = not scored.
BL = {}


def bl(ids, blind, pf="none", known="none"):
    for i in ids.split():
        BL[i] = (blind, pf, known)


bl("T1-A1", "partial", "PF-T1-1,PF-T1-3", "S1_flatcomp_ground_space_dim_on_2x2,2x3,2x4,2x5,3x3")
bl("T1-A2", "partial", "PF-T1-1,PF-T1-3")
bl("T1-A3", "partial", "PF-T1-3", "S1_flatcomp_on_2x2,2x3,2x4,2x5,3x3")
bl("T1-A4 T1-A5", "partial", "PF-T1-3", "S2_on_3x4")
bl("T1-B1 T1-B5 T1-B6 T1-B7 T1-B10 T1-B11", "partial", "PF-T1-3", "S2_on_3x4")
bl("T1-B2", "partial", "PF-T1-1,PF-T1-2,PF-T1-3", "S2_on_3x4")
bl("T1-B3 T1-B4", "partial", "PF-T1-1", "S2_CA_CB_blocks_on_3x4")
bl("T1-B-2x2", "0", "PF-T1-3")
bl("T1-B-2x3 T1-B-2x4 T1-B-2x5 T1-B-2x6 T1-B-3x3 T1-B-3x5 T1-B-4x5 T1-B8", "1")
bl("T1-B-4x4", "1", "PF-T1-2")
bl("T1-B-3x4", "0", "none", "S2_#143_C1=(3/2)Gamma_V_and_3/r^2")
bl("T1-B9", "partial", "PF-T1-3")
bl("T1-C1 T1-C3 T1-C5", "partial", "PF-T1-3")
bl("T1-C4", "partial", "PF-T1-1,PF-T1-3")
bl("T1-C2 T1-C6 T1-X1 T1-X2 T1-X3", "1")
bl("T1-C-2x3 T1-C-2x4 T1-C-2x5 T1-C-2x6", "1", "PF-T1-1")
bl("T1-C-2x2", "0", "PF-T1-3")
bl("T1-O1", "na")
bl("T2-A-Z3 T2-A-Z4 T2-A-Z6 T2-A-Q8 T2-A-DIC3 T2-A-DIC4 T2-A-DIC6 T2-A-2T T2-A-2O T2-A-2I T2-A-RULE", "0", "PF-T2-1",
   "S6_Transfer_1_table_(Q8,Dic3,Dic4,2T,2O_lattice-measured_there;2I_from_its_formula)")
bl("T2-B-SMALL T2-B-X-CYCLIC T2-C-GAP T2-C-UP-CYCLIC", "0", "PF-T2-1")
bl("T2-B-IDENTITY T2-B-SIGN T2-B-ENVELOPE T2-C-SU2", "1")
bl("T2-B-X-Q8 T2-B-X-DIC3 T2-B-X-DIC4 T2-B-X-DIC6 T2-B-X-2T T2-B-X-2O T2-B-X-2I T2-B-DIC-SPLIT T2-B-LAW-TRANSFER "
   "T2-B-LAW-HEATKERNEL T2-B-LAW-T T2-C-ENVELOPE-NUM T2-C-DOWN1-UNIVERSAL T2-C-10-Z4 T2-C-10-Z6 T2-C-10-Q8 "
   "T2-C-10-DIC3 T2-C-10-DIC4 T2-C-10-DIC6 T2-C-10-2T T2-C-10-2O T2-C-10-2I T2-C-50-Z4 T2-C-50-Z6 T2-C-50-T3PLUS "
   "T2-C-PEAK-Z3 T2-C-PEAK-Z4Z6 T2-C-PEAK-Q8 T2-C-PEAK-DIC3 T2-C-PEAK-DIC4 T2-C-PEAK-DIC6 T2-C-PEAK-2T T2-C-PEAK-2O "
   "T2-C-PEAK-2I T2-C-FREEZE-LAW T2-C-PEAK-PRODUCT T2-C-FINGERPRINT T2-C-SHAPE", "1", "PF-T2-2")
bl("T2-C-10-Z3 T2-C-50-Z3", "weak", "PF-T2-2")
bl("T2-C-4D-LIT", "na")
bl("T3-A01 T3-A02 T3-A03 T3-A04 T3-A05 T3-A06 T3-A07 T3-A08 T3-A09 T3-A10 T3-A11 T3-A12 T3-A25 T3-B01 T3-B06",
   "partial", "PF-T3-1,PF-T3-2")
bl("T3-A13 T3-A14", "0", "PF-T3-1,PF-T3-2")
bl("T3-A15 T3-A16 T3-A17 T3-A18 T3-A19 T3-A20 T3-A21 T3-A22 T3-A23 T3-A24", "1", "PF-T3-2")
bl("T3-B02 T3-B03 T3-B05", "1", "PF-T3-2")
bl("T3-B04", "0", "PF-T2-1", "S6_t(2I)=11")
bl("T3-C01 T3-C08 T3-C11 T3-C12 T3-C14 T3-C15", "1")
bl("T3-C02 T3-C03", "partial", "PF-T3-1")
bl("T3-C02-k01 T3-C02-k02", "0", "PF-T3-1")
bl("T3-C02-k03 T3-C02-k04 T3-C02-k05 T3-C02-k06 T3-C02-k07 T3-C02-k08 T3-C02-k09 T3-C02-k10 T3-C02-k11 T3-C02-k12",
   "1", "PF-T3-2")
bl("T3-C04 T3-C05 T3-C06 T3-C07 T3-C09 T3-C10 T3-C13", "1", "PF-T3-1,PF-T3-2")
bl("T3-C16", "na")

# ------------------------------------------------------------------ fix seat: blindness recodes (review findings F1, F2)
# F1: the finite repository's own records at 6a7fc747 (source FC1-S11) held measured values for several FC1 rows.
# F2: PF-T2-2 evaluated every quantity it touches approximately before the freeze, so those rows are weak, not blind.
FIX = {}


def fixbl(ids, blind, pf, known, why):
    for i in ids.split():
        BL[i] = (blind, pf, known)
        FIX.setdefault(i, []).append(why)


K11_FLAT = "S11_zgap2:second-order_flat_operator_with_lowest_splitting_sqrt14-sqrt6_on_2x2,exactly_3_on_2x3,exactly_4_on_2x4,exactly_scalar_on_3x3"
K11_RITZ = "S11_ritz:the_eight_3x3_Ritz_levels_at_r=27_and_E1-E0,E7-E6_at_r=9,27,81_(trial-space_values,full_gap_NOT_CERTIFIED)"
fixbl("T1-B1", "partial", "PF-T1-3",
      "S2_on_3x4;" + K11_FLAT + ";S11_2xL:E2-E1_intervals_on_2x2,2x3,2x4,3x3_(r=9..243);S11_ritz:(9/8)(sqrt14-sqrt6)/r^2_on_3x3;"
      "S11_ladder:r(E1-E0)->sqrt14-sqrt6_on_2x2", "known_before_freeze_filled_from_FC1-S11_(F1)")
fixbl("T1-B5 T1-B6 T1-B7", "partial", "PF-T1-3", "S2_on_3x4;" + K11_RITZ,
      "known_before_freeze_extended_with_the_3x3_Ritz_levels_of_FC1-S11_(F1,same_records)")
fixbl("T1-B-2x2", "0", "PF-T1-3",
      "S11_zgap2:lowest_flat_splitting_sqrt14-sqrt6_on_2x2;S11_ladder:r(E1-E0)->sqrt14-sqrt6;S11_2xL:E2-E1_intervals_on_2x2_at_r=9,27,81,243",
      "known_before_freeze_filled_from_FC1-S11_(F1)")
fixbl("T1-B-2x3", "0", "none",
      "S11_zgap2:lowest_flat_splitting_exactly_3_on_2x3;S11_2xL:E2-E1_intervals_on_2x3_at_r=9,27,81,243_('close_to_L/r')",
      "blind_recoded_1->0_(control):value_already_in_FC1-S11_(F1)")
fixbl("T1-B-2x4", "0", "none",
      "S11_zgap2:lowest_flat_splitting_exactly_4_on_2x4;S11_2xL:E2-E1_intervals_on_2x4_at_r=9,27,81,243_('close_to_L/r')",
      "blind_recoded_1->0_(control):value_already_in_FC1-S11_(F1)")
fixbl("T1-B-3x3", "partial", "none",
      "S11_ritz:formula_(9/8)(sqrt14-sqrt6)/r^2_printed_beside_Ritz_ratios_1.09693,1.00924,1.00098_at_r=9,27,81_(trial-space,full_gap_NOT_CERTIFIED);"
      "S11_zgap2:flat_second-order_operator_exactly_scalar_on_3x3;S11_2xL:E2-E1_intervals_on_3x3_at_r=9,27,81;"
      "not_in_the_records:an_exact_r^-2_series_coefficient_on_3x3", "blind_recoded_1->partial:formula_and_uncertified_values_in_FC1-S11_(F1)")
fixbl("T1-B8", "partial", "none",
      "S11_2xL:E2-E1_intervals_on_2x2,2x3,2x4_and_'close_to_L/r';S11_zgap2:flat_splitting_3_on_2x3_and_4_on_2x4;blind_only_on_2x5,2x6",
      "blind_recoded_1->partial:2x3_and_2x4_already_in_FC1-S11_(F1)")
fixbl("T1-B11", "partial", "PF-T1-3", "S2_on_3x4;" + K11_FLAT, "known_before_freeze_extended_from_FC1-S11_(F1)")
fixbl("T1-C1", "partial", "PF-T1-3",
      "S11_zgap2:E9-E8=3r-c_L/r+O(r^-2)_on_2x2,2x3,2x4,3x3,3x4,4x4;S11_2xL:E9-E8_intervals_on_2x2,2x3,2x4,3x3_at_r=9..243;"
      "S11_README:E9-E8_on_2x5_at_r=9", "known_before_freeze_filled_from_FC1-S11_(F1)")
fixbl("T1-C2", "partial", "none", "S11_zgap2:c_L=21_exactly_on_3x3,3x4,4x4_(charpoly_(x-84)^3);blind_only_on_3x5,4x5",
      "blind_recoded_1->partial:3x3,3x4,4x4_already_in_FC1-S11_(F1)")
fixbl("T1-C-2x3", "0", "PF-T1-1", "S11_zgap2:c_L=69/2_exactly_on_2x3;S11_2xL:E9-E8_intervals_on_2x3_at_r=9..243",
      "blind_recoded_1->0_(control):value_already_in_FC1-S11_(F1)")
fixbl("T1-C-2x4", "0", "PF-T1-1", "S11_zgap2:c_L=73/2_exactly_on_2x4;S11_2xL:E9-E8_intervals_on_2x4_at_r=9..243",
      "blind_recoded_1->0_(control):value_already_in_FC1-S11_(F1)")
fixbl("T1-C-2x2", "0", "PF-T1-3", "S11_zgap2:c_L=36.762472..._(irrational)_on_2x2;S11_2xL:E9-E8_intervals_on_2x2_at_r=9..243",
      "known_before_freeze_filled_from_FC1-S11_(F1)")
fixbl("T1-C3", "partial", "PF-T1-3", "S11_zgap2:E9-E8_to_order_1/r_on_2x2,2x3,2x4,3x3,3x4,4x4;E9_itself_not_printed_there",
      "known_before_freeze_filled_from_FC1-S11_(F1)")
fixbl("T1-C4", "partial", "PF-T1-1,PF-T1-3",
      "S11_zgap2:3_orbits_per_plaquette_at_M=3_and_first-order_shift_0_(d1=0)_on_every_lattice;"
      "charpoly_(x-84)^3_of_the_reduced_second-order_operator_on_3x3,3x4,4x4", "known_before_freeze_filled_from_FC1-S11_(F1)")
fixbl("T1-C5", "partial", "PF-T1-3",
      "S11_zgap2:reduced_second-order_operator_(x-84)^3_on_3x3,3x4,4x4_(threefold_E9);the_2xL_and_2x2_simplicity_is_not_in_the_records",
      "known_before_freeze_filled_from_FC1-S11_(F1)")
fixbl("T1-C-2x5", "1", "PF-T1-1",
      "S11_README:one_certified_E9-E8_interval_on_2x5_at_r=9_only;a_single_finite-r_value_does_not_fix_the_limit,so_the_row_stays_blind",
      "known_before_freeze_filled_from_FC1-S11_(fix-seat_extension_of_F1);blind_unchanged")
fixbl("T1-O1", "na", "none",
      "S11:finite-r_values_on_2x2,2x3,2x4,3x3_(r=9..243),2x5_(r=9),3x3_Ritz_levels_(r=9,27,81)_and_the_2x2_ladder_are_in_the_records",
      "known_before_freeze_filled_from_FC1-S11_(fix-seat_extension_of_F1);row_stays_OPEN_and_UNSCORED")
TOOLROWS = ("T2-B-X-Q8 T2-B-X-DIC3 T2-B-X-DIC4 T2-B-X-DIC6 T2-B-X-2T T2-B-X-2O T2-B-X-2I T2-B-DIC-SPLIT T2-B-LAW-TRANSFER "
            "T2-B-LAW-HEATKERNEL T2-B-LAW-T T2-C-ENVELOPE-NUM T2-C-DOWN1-UNIVERSAL T2-C-10-Z4 T2-C-10-Z6 T2-C-10-Q8 "
            "T2-C-10-DIC3 T2-C-10-DIC4 T2-C-10-DIC6 T2-C-10-2T T2-C-10-2O T2-C-10-2I T2-C-50-Z4 T2-C-50-Z6 T2-C-50-T3PLUS "
            "T2-C-PEAK-Z3 T2-C-PEAK-Z4Z6 T2-C-PEAK-Q8 T2-C-PEAK-DIC3 T2-C-PEAK-DIC4 T2-C-PEAK-DIC6 T2-C-PEAK-2T T2-C-PEAK-2O "
            "T2-C-PEAK-2I T2-C-FREEZE-LAW T2-C-PEAK-PRODUCT T2-C-FINGERPRINT T2-C-SHAPE")
KTOOL = "approximate:the_PF-T2-2_tool_value_of_this_quantity_(truncated_tools_S,D,L;not_exact)"
fixbl(TOOLROWS, "weak", "PF-T2-2", KTOOL,
      "blind_recoded_1->weak:PF-T2-2_evaluated_this_quantity_approximately_before_the_freeze;MET_checks_the_tool_and_its_truncation_(F2)")
fixbl("T2-C-10-Z3 T2-C-50-Z3", "weak", "PF-T2-2", KTOOL, "known_before_freeze_filled_(was_none),as_for_the_other_PF-T2-2_rows_(F2)")

# ------------------------------------------------------------------ refix seat (after verify round 2): FINDINGS-VERIFY-R2.json, items V1..V18
# Each change keeps the earlier fix note and appends its own (prefix "R3:"). No predicted number changes.
RFX = set()


def rfx(ids, why, blind=None, pf=None, known=None, add=None, sub=None):
    for i in ids.split():
        b, p, k = BL[i]
        if sub:
            if sub[0] not in k:
                raise SystemExit("refix_known_anchor_missing:" + i)
            k = k.replace(sub[0], sub[1])
        if known is not None:
            k = known
        if add:
            k = add if k == "none" else k + ";" + add
        BL[i] = (blind or b, pf or p, k)
        FIX.setdefault(i, []).append("R3:" + why)
        RFX.add(i)


FR = "a_finite-r_record_of_a_limit_quantity_does_not_fix_the_limit,but_it_is_an_approximate_evaluation,so_the_row_is_partial,not_blind"
# V6 (blocking): PF-T3-1 computed the k=1,2 values of seven case-(ii) rows before the freeze.
for lid, what in (("T3-C04", "torus_1x2_P2_k1=3:16,k2=1:16"), ("T3-C05", "torus_2x2_P4_k1=37:768,k2=3:256"),
                  ("T3-C06", "cube_surface_S2_P6_k1=-1:64,k2=43:15360"), ("T3-C07", "f3D_k1,f3D_k2_(c4,c6)"),
                  ("T3-C09", "f3D_k1,f3D_k2_(this_row_is_their_beta-derivative)"), ("T3-C10", "psi6_ratio_1,psi6_ratio_2"),
                  ("T3-C13", "ham_c4_k1=-16:81,k2=70:1053")):
    rfx(lid, "blind_recoded_1->partial:PF-T3-1_printed_the_k=1,2_values_before_the_freeze_(V6)", blind="partial",
        known="PF-T3-1:k=1,2_values_via_the_derived_formula_(small_checks.out:" + what + ");blind_only_on_k=3..12")
# V7, V12 (blocking): the 2x5 stage-B certificate at r=9.
K2X5 = "S11_2x5B:certified_r=9_intervals_on_2x5"
rfx("T1-B-2x5", "blind_recoded_1->partial:certified_r=9_E2-E1_interval_on_2x5_in_S11_2x5B_(V7,V12)", blind="partial",
    known=K2X5 + ":first_splitting_E2_minus_E1_in=[0.571455,0.571507];" + FR)
rfx("T1-C-2x5", "blind_recoded_1->partial;citation_corrected_from_the_README_bound_to_the_certificate_(V7,V12)", blind="partial",
    known=K2X5 + ":gap_E9_minus_E8_in=[22.613640,22.615366];S11_README:only_the_bound_E9-E8>=21.778_for_r>=9;" + FR)
rfx("T1-B8", "known_before_freeze_extended:2x5_has_a_certified_r=9_point_(V12)",
    sub=("blind_only_on_2x5,2x6", K2X5 + ":E2-E1_in=[0.571455,0.571507],E8-E1_in=[1.712531,1.712569];"
                                  "the_limit_is_unmeasured_on_2x5_and_2x6;2x5_has_this_one_certified_r=9_point"))
rfx("T1-C1", "known_before_freeze_citation_corrected:the_2x5_r=9_interval_is_in_S11_2x5B,not_in_the_README_(V7)",
    sub=("S11_README:E9-E8_on_2x5_at_r=9", K2X5 + ":E9-E8_in=[22.613640,22.615366];S11_README:E9-E8>=21.778_on_2x5_for_r>=9"))
rfx("T1-O1", "known_before_freeze:2x5_record_named_(V12)", sub=("2x5_(r=9)", "2x5_(r=9,S11_2x5B)"))
# V13 (blocking): zgap2 RESULT.hbp prints E9's 1/r coefficient on six tori; review-opus55 holds r=9 bounds on E9.
rfx("T1-C3", "known_before_freeze_rewritten:the_1/r_coefficient_of_E9_is_in_ZGAP_C_on_six_tori;r=9_bounds_added_(V13)",
    known="S11_zgap2R:ZGAP_C_lambda_min_H3_micro=minus_the_row's_1/r_coefficient_on_2x2_([39.020815,39.020816]),2x3_(39),2x4_(42.5),3x3_(34.5),"
          "3x4_(39),4x4_(45);S11_rev55:E9_upper_bounds_at_r=9_(Ritz,trial-space,upper_only)_on_3x4_(94.087786,m16),4x4_(117.575598,m15),"
          "4x5_(140.955674,m12);claimed_E9_lower_bounds_at_r=9_on_4x4,4x5_(exact_4x4_r9,exact_4x5_r9);complete-model_Ritz_value_on_3x3_at_r=9_(ritz_3x3_r9);"
          "S11_2x5B:E9_in=[81.778000,81.779715]_on_2x5_at_r=9;the_1/r_coefficient_is_unknown_only_on_2x5,2x6,3x5,4x5")
rfx("T1-C2", "known_before_freeze_extended_with_the_4x5_r=9_bounds_on_E9_(V13)",
    add="S11_rev55:4x5_at_r=9:E9_upper_bound_140.955674_(ritz_4x5_r9_m12.bound,trial-space)_and_a_claimed_lower_bound_(exact_4x5_r9);" + FR)
# V14 (blocking): the D(S3) S-matrix was opened in a record (PR #154) before this file.
rfx("T1-X1", "blind_recoded_1->partial:the_spectral_part_of_met_if_is_fixed_by_FC1-S12_and_S2_(V14)", blind="partial",
    known="FC1-S12:6S_of_D(S3)_in_ICONIC-RELATIONSHIP-20261109.hbp_MODULAR_S_(row_e:triv=1,1,2,2,2,2,3,3;row_t:chi0=3,-3,0,0,0,0,3,-3);"
          "with_spec(Gamma_V)_from_S2_and_PF-T1-1,the_spectral_comparison_in_met_if_is_a_control;"
          "unmeasured:only_the_operator-level_identification_(Gamma_V_acting_as_the_closed_D_ribbon_operator,its_eigenvectors)")
# V15, V16 (minor): further zgap2 and review-opus55 content.
rfx("T1-B10", "known_before_freeze_extended_(V15)",
    add="S11_zgap2R:H0_top=-13.5,-18,-24_and_K0_scalar=1_on_3x3,3x4,4x4_(vacuum_second_order_=-(3LxLy/2)I);"
        "S11_rev55:E8_upper_bounds_at_r=9_on_3x3,3x4,4x4,4x5_(e8_*_9.out)")
rfx("T1-B11", "known_before_freeze_extended_(V15)",
    add="S11_zgap2R:H0_top=-2.258343_(2x2,=-(6-sqrt14)),-4.5_(2x3),-6_(2x4):the_top_eigenvalue_of_these_blocks")
rfx("T1-A1", "known_before_freeze_extended_(V16)", add="S11_rev55:flats_4x4,flats_4x5:classes=8_on_4x4,4x5")
rfx("T1-A2", "known_before_freeze_filled_(was_none)_(V16)",
    add="S11_rev55:flats_4x4,flats_4x5:pairs=18,classes=8;lowm_4x4_r9,lowm_4x5_r9:weights_sum=18")
rfx("T1-A5", "known_before_freeze_extended_(V16)",
    add="S11_rev55:flats_4x4,flats_4x5:moves=1728,2160,moves_not_to_M4=0;lowm_4x4_r9,lowm_4x5_r9:M=3_is_the_lowest_nonflat_M_present_(M<=14,M<=12_models)")
rfx("T1-C4", "known_before_freeze_extended_(V16)", add="S11_zgap2R:ZGAP_SIZE_m3_orbits=3LxLy_on_2x2,2x3,2x4,3x3,3x4,4x4")
# V17 (minor): the large-beta series of P_SU2 was computed exactly before the freeze.
rfx("T2-C-SU2", "blind_recoded_1->partial;prefreeze_filled:PF-T2-2_(ASYM.hbp_SU2_LARGE_BETA)_and_PF-A-2_(T2_C_SU2_P_series)_printed_these_rationals_(V17)",
    blind="partial", pf="PF-T2-2,PF-A-2",
    known="exact_pre-freeze_value:PF-T2-2_and_PF-A-2_print_c_0..5=1,-3:2,3:8,3:8,63:128,27:32;FC2-S13:4D@dfe0859b_d3_atom.py_builds_the_same_I2/I1_coefficients_"
          "(script_only,output_not_recorded);referee_question:recode_to_0_if_these_exact_coefficients_fix_the_met_if")
# V18 (minor): formula analogs in Iconic, no SU(2)_k value.
rfx("T3-C02 T3-C03", "known_before_freeze_filled_(was_none):formula_analog_named_(V18)",
    add="formula_analog:FC2-S6_TRANSFER-THEOREM_(finite_G:iota/(2^(t+1)(t+1)!)_per_plaquette,iota/(t+1)!_on_the_pillow);no_SU(2)_k_value_there;"
        "su2-ladder_GAUGE_FIRST_BREAK_2O_and_2I_match_FC3-36_and_FC3-38_in_magnitude_but_are_different_objects")

# ------------------------------------------------------------------ refix seat round 2 (after verify round 3): items W1..W9 of CHANGES.txt VERIFY-ROUND-3
# Same rules as rfx(); notes are prefixed "R4:". pre= puts text in front of the existing known_before_freeze. No predicted number changes.
RFX4 = set()


def rfx4(ids, why, blind=None, pf=None, known=None, add=None, sub=None, pre=None):
    for i in ids.split():
        b, p, k = BL[i]
        if sub:
            if sub[0] not in k:
                raise SystemExit("refix4_known_anchor_missing:" + i)
            k = k.replace(sub[0], sub[1])
        if known is not None:
            k = known
        if add:
            k = add if k == "none" else k + ";" + add
        if pre:
            k = pre if k == "none" else pre + ";" + k
        BL[i] = (blind or b, pf or p, k)
        FIX.setdefault(i, []).append("R4:" + why)
        RFX4.add(i)


# W1 (minor): FC1-38's known_before_freeze names PF-T1-1, so its prefreeze field lists it.
rfx4("T1-X1", "prefreeze_none->PF-T1-1:known_before_freeze_already_named_it_(W1)", pf="PF-T1-1")
# W2 (minor): PF-T3-1 checked the pillow identity and printed the k=1,2 first-difference powers of every complex it evaluated.
rfx4("T3-C01", "blind_recoded_1->partial;prefreeze_none->PF-T3-1:PF-T3-1_checked_the_pillow_sum_and_printed_the_k=1,2_first_differences_(W2)",
     blind="partial", pf="PF-T3-1",
     known="PF-T3-1:k=1,2_(small_checks.out:pillow_eq_a0_of_2beta_1,pillow_eq_a0_of_2beta_2;first-difference_powers_of_the_pillow,"
           "the_1x2_and_2x2_tori,the_open_cube_and_f3D_at_k=1,2);blind_only_on_k=3..12")
rfx4("T3-C15", "blind_recoded_1->partial;prefreeze_none->PF-T3-1:the_k=1,2_case_labels_can_be_read_off_the_printed_first-difference_powers_(W2)",
     blind="partial", pf="PF-T3-1",
     known="PF-T3-1:k=1,2_(small_checks.out:first-difference_powers_k1_2D_free_first_break,k2_2D_free_first_break,pillow_k1/k2_first_diff,"
           "torus_1x2_P2,torus_2x2_P4,cube_surface_S2_P6,f3D_k1,f3D_k2);blind_only_on_k=3..12")
# W3 (minor): FC3-33 and FC3-46 are partial because of PF-T3-1; their known field now says so first.
rfx4("T3-C02", "known_before_freeze_prefixed_with_the_PF-T3-1_values_(W3)",
     pre="PF-T3-1:k=1,2_values_(small_checks.out:k1_2D_free_first_break_-1:384,next_11:46080;k2_2D_free_first_break_-1:46080,next_11:5160960);"
         "blind_only_on_k=3..12")
rfx4("T3-C03", "known_before_freeze_prefixed_with_the_PF-T3-1_values_(W3)",
     pre="PF-T3-1:k=1,2_values_(small_checks.out:pillow_eq_a0_of_2beta_1,pillow_eq_a0_of_2beta_2;pillow_k1_first_diff_-1:24,pillow_k2_first_diff_-1:720);"
         "blind_only_on_k=3..12")
# W6, W7 (blocking): The-matrix-law-essentials (source FC1-S13) gives the exact large-r limits of FC1-16, 17, 18, 20, 21.
M13 = "FC1-S13:"
X13 = "_(exact,from_an_integer_characteristic_polynomial_with_Sturm_isolation;present_at_28345a6)"
rfx4("T1-B-2x5", "blind_recoded_partial->0_(control):exact_limit_5_in_FC1-S13_(W7)", blind="0",
     known=M13 + "flat_law.hbp_L=2x5_gap_coeff_in=[4.999999999,5.000000000]" + X13 + ";README_'exactly_3,4,5,6_x_J_E^2/J_B'_(2x3..2x6);"
           "S11_2x5B:certified_r=9_E2_minus_E1_in=[0.571455,0.571507]")
rfx4("T1-B-2x6", "blind_recoded_1->0_(control):exact_limit_6_in_FC1-S13_(W6)", blind="0",
     known=M13 + "flat_law.hbp_L=2x6_gap_coeff_in=[5.999999999,6.000000000]" + X13 + ";kappa_spectrum_27,21,18,15,9;"
           "README_'exactly_3,4,5,6_x_J_E^2/J_B'_(2x3..2x6)")
rfx4("T1-B-3x3", "blind_recoded_partial->0_(control):exact_limit_in_FC1-S13_(W7)", blind="0",
     known=M13 + "flat_law3.hbp_L=3x3_second_order_degenerate=1,gap_coeff3_in=[1.453688599,1.453688599]" + X13 + ";"
           "README:16*H3_has_charpoly_x^4(x^4-6480x^2+8817984),roots_+-18sqrt14,+-18sqrt6,0_(x4),gap_(9/8)(sqrt14-sqrt6)_J_E^3/J_B^2;"
           "S11_ritz:formula_(9/8)(sqrt14-sqrt6)/r^2_beside_Ritz_ratios_1.09693,1.00924,1.00098_at_r=9,27,81_(trial-space);"
           "S11_zgap2:flat_second-order_operator_exactly_scalar_on_3x3;S11_2xL:E2-E1_intervals_on_3x3_at_r=9,27,81")
rfx4("T1-B-3x5", "blind_recoded_1->0_(control):exact_limit_15/4_in_FC1-S13_(W6)", blind="0",
     known=M13 + "flat_law3.hbp_L=3x5_second_order_degenerate=1,gap_coeff3_in=[3.749999999,3.750000000]" + X13 + ";"
           "H3_eig_+-5.625,+-1.875,0;README_'exactly_3_and_15/4_x_J_E^3/J_B^2'_(3x4,3x5)")
rfx4("T1-B-4x4", "blind_recoded_1->0_(control):exact_limit_in_FC1-S13_(W6)", blind="0",
     known=M13 + "flat_law4.hbp_L=4x4_gap_coeff4_in=[1.615209554,1.615209554]_(exact,from_the_integer_charpoly_of_Y_with_Sturm_isolation;"
           "blob_identical_at_28345a6_and_e9eb988);Y_eig_in=14000.748500304,13999.133290749,13996.071428571,13993.009566392,13991.394356837;README_'(5/4)(sqrt14-sqrt6)_J_E^4/J_B^3'_(4x4)")
rfx4("T1-B-4x5", "known_before_freeze_filled_(was_none):FC1-S13_has_only_second-order_degeneracy_on_4x5;blind_unchanged_(W6)",
     known=M13 + "flat_law.hbp_L=4x5_second_order_degenerate=1_only;no_third-_or_fourth-order_value_on_4x5_in_these_records")
rfx4("T1-B-2x2", "known_before_freeze_extended_with_FC1-S13_(W6,same_records)",
     add=M13 + "flat_law.hbp_L=2x2_gap_coeff_in=[1.292167643,1.292167643];README_'(sqrt14-sqrt6)_J_E^2/J_B'")
rfx4("T1-B-2x3", "known_before_freeze_extended_with_FC1-S13_(W6,same_records)",
     add=M13 + "flat_law.hbp_L=2x3_gap_coeff_in=[2.999999999,3.000000000];second_order.hbp_t23,t32_gap_coeff_in=[2.999999999,3.000000000]")
rfx4("T1-B-2x4", "known_before_freeze_extended_with_FC1-S13_(W6,same_records)",
     add=M13 + "flat_law.hbp_L=2x4_gap_coeff_in=[3.999999999,4.000000000]")
rfx4("T1-B-3x4", "known_before_freeze_extended_with_FC1-S13_(W6,same_records)",
     add=M13 + "flat_law3.hbp_L=3x4_gap_coeff3_in=[2.999999999,3.000000000];README_'exactly_3_and_15/4'")
# W8 (minor): further FC1-S13 instances in partial rows; codes unchanged.
FV13 = "flat_law.hbp_flat_vacua=8_on_all_10_tori_and_5x5_(2x2..3x3_at_28345a6,the_rest_at_8a28b50)"
RQ13 = "referee_question:recode_to_0_if_this_record_fixes_the_met_if_on_every_torus"
rfx4("T1-A1", "known_before_freeze_extended_with_FC1-S13;referee_question_added_(W8)", add=M13 + FV13 + ";" + RQ13)
rfx4("T1-A3", "known_before_freeze_extended_with_FC1-S13;referee_question_added_(W8)",
     add=M13 + FV13 + ";the_zero_space_of_M_on_gauge-invariant_states_is_the_span_of_these_vacua;" + RQ13)
rfx4("T1-A4", "known_before_freeze_extended_with_FC1-S13;referee_question_added_(W8)",
     add=M13 + "flat_law.hbp_flat_to_flat=0_and_PEP_diag=6LxLy_(24,36,48,60,72,54,72,90,96,120)_on_all_10_tori;the_off-diagonal_of_PEP_is_printed_only_on_2x3_"
               "(second_order.hbp_PEP_offdiag_nonzero=0);" + RQ13)
rfx4("T1-A5", "known_before_freeze_extended_with_FC1-S13_(W8)",
     add=M13 + "flat_law.hbp_flat_to_flat=0_and_intermediate_M=4_on_all_10_tori_(the_first_shell);the_minimum_nonflat_M=3_is_not_in_FC1-S13")
rfx4("T1-B1", "known_before_freeze_extended_with_FC1-S13_(W8)",
     add=M13 + "first_splitting_at_2nd_order_on_2x2..2x6_(k=1),3rd_on_3x3,3x4,3x5_(k=2),4th_on_4x4_(k=3);on_4x5_only_second_order_degenerate_(k>=2);"
               "blind_only_on_4x5_(k=3_against_k>3)")
rfx4("T1-B2", "known_before_freeze_extended_with_FC1-S13_(W8,same_records)",
     add=M13 + "spectra_of_the_leading_8x8_operator_on_2x2..2x6,3x3,3x4,3x5,4x4;the_count-form_matrix_C_is_not_printed;blind_on_4x5_and_on_the_count_form")
rfx4("T1-B3", "known_before_freeze_extended_with_FC1-S13_(W8)",
     add=M13 + "kappa_spectra_on_2x3..2x6_and_H3_eig_on_3x4,3x5_have_the_shape_of_spec(Gamma_V)=(3,1,0,-1,-3);the_count-form_entries_are_not_printed")
P13 = "2x2..2x6_(kappa_spectra_and_charpolys),3x3,3x4,3x5_(H3_eig),4x4_(Y_eig:(5/4)sqrt14,(5/4)sqrt6)"
rfx4("T1-B5", "known_before_freeze_extended_with_FC1-S13_(W8)", add=M13 + "the_leading_8-level_pattern_on_" + P13 + ";blind_only_on_4x5")
rfx4("T1-B6", "known_before_freeze_extended_with_FC1-S13_(W8)",
     add=M13 + "the_ratio_follows_from_the_printed_spectra_on_" + P13 + "_(1/2_on_rectangles,(sqrt21+3)/4_on_squares);blind_only_on_4x5")
rfx4("T1-B7", "known_before_freeze_extended_with_FC1-S13_(W8)",
     add=M13 + "degeneracy_and_symmetry_follow_from_the_printed_spectra_on_" + P13 + ";multiplicities_are_printed_on_2x2..2x6,3x3_(README),4x4_(charpoly_Y),"
               "only_the_distinct_values_on_3x4,3x5;blind_only_on_4x5")
rfx4("T1-B8", "known_before_freeze_corrected_and_extended_with_FC1-S13_(W8)",
     sub=("the_limit_is_unmeasured_on_2x5_and_2x6;2x5_has_this_one_certified_r=9_point",
          M13 + "E2-E1=L/r_and_E8-E1=3L/r_exactly_on_2x2..2x6_(gap_coeff_in_and_kappa_spectra);3x4,3x5:E2-E1=3,15/4_(the_3xL_law_at_L=4,5);"
                "blind_only_on_the_general-L_law_(2xL_with_L>=7,3xL_with_L>=6)"))
rfx4("T1-B10", "known_before_freeze_extended_with_FC1-S13_(W8)",
     add=M13 + "second-order_kappa=3LxLy/2_scalar_on_3x3,3x4,3x5,4x4,4x5_(13.5,18,22.5,24,30);on_2x2..2x6_the_kappa_spectra_and_charpolys_are_printed_"
               "(the_mean_is_their_trace,which_is_not_printed)")
rfx4("T1-B11", "known_before_freeze_extended_with_FC1-S13_(W8)",
     add=M13 + "PEP_diag=6LxLy_and_flat_to_flat=0_on_all_10_tori;spectra_of_the_second_block_on_all_10:scalar_3LxLy/2_for_Lmin>=3,"
               "3L+(L/2)(3,1,0,-1,-3)_on_2xL_(27,21,18,15,9_on_2x6),6+(sqrt14,sqrt6,0,-sqrt6,-sqrt14)_on_2x2;the_operator_form_(Gamma_V)_is_not_printed")
# W9 (minor): Iconic MEASURE-LADDER.hbp (source FC2-S14) holds the exact small-beta series of ln z_G - ln z_SU2; it fixes only the small-beta region.
L14 = ("FC2-S14:MEASURE-LADDER.hbp_GAUGE_DIFF_holds_ln_z_G-ln_z_SU2_as_exact_rationals_through_beta^30_for_all_ten_groups;"
       "its_beta-derivative_is_the_small-beta_series_of_P_G-P_SU2")
rfx4("T2-B-SIGN T2-B-ENVELOPE", "known_before_freeze_filled_(was_none):FC2-S14_named;blind_unchanged_(W9)",
     known=L14 + ";it_fixes_only_the_small-beta_region_(the_FC2-15_content),not_every_beta>0;"
                 "referee_question:recode_to_partial_if_a_30-term_series_counts_as_an_approximate_evaluation")
rfx4("T2-B-SMALL", "known_before_freeze_filled_(was_none):FC2-S14_gives_this_leading_form_(W9)",
     known=L14 + ";e.g._Dic2:1:192_at_beta^4,so_P_G-P_SU2=beta^3:48+..._and_delta_G=beta^2:12+..._with_P_SU2=beta:4+...")
rfx4("T2-B-IDENTITY", "known_before_freeze_filled_(was_none):FC2-S14_named_(W9,same_record);blind_unchanged",
     known="FC2-S14:MEASURE-LADDER.hbp_GAUGE_F_and_SU2_GAUGE_F_hold_the_Taylor_series_of_ln_z_through_beta^30;the_identity_can_be_compared_with_them_"
           "only_to_that_order;referee_question:recode_to_partial_if_a_30-term_series_counts_as_an_approximate_evaluation")

# ------------------------------------------------------------------ refix seat round 3 (after verify round 4): items X1..X7 of CHANGES.txt VERIFY-ROUND-4
# Same rules as rfx4(); notes are prefixed "R5:". Rule: a previously established result found later recodes the row to control (0); the prediction never changes.
RFX5 = set()


def rfx5(ids, why, blind=None, pf=None, known=None, add=None, sub=None, pre=None):
    for i in ids.split():
        b, p, k = BL[i]
        if sub:
            if sub[0] not in k:
                raise SystemExit("refix5_known_anchor_missing:" + i)
            k = k.replace(sub[0], sub[1])
        if known is not None:
            k = known
        if add:
            k = add if k == "none" else k + ";" + add
        if pre:
            k = pre if k == "none" else pre + ";" + k
        BL[i] = (blind or b, pf or p, k)
        FIX.setdefault(i, []).append("R5:" + why)
        RFX5.add(i)


# X1 (minor): FC1-23. FC1-S13 gives the law on 2x3..2x6, not on 2x2; the met_if scores only 2x3..2x6, all exact in FC1-S13, so the row is a control.
rfx5("T1-B8", "known_before_freeze_corrected_(2x2..2x6->2x3..2x6);blind_recoded_partial->0_(control):the_met_if_scores_only_2x3..2x6,all_exact_in_FC1-S13_(X1)",
     blind="0",
     sub=("E2-E1=L/r_and_E8-E1=3L/r_exactly_on_2x2..2x6_(gap_coeff_in_and_kappa_spectra);3x4,3x5:E2-E1=3,15/4_(the_3xL_law_at_L=4,5);"
          "blind_only_on_the_general-L_law_(2xL_with_L>=7,3xL_with_L>=6)",
          "E2-E1=L/r_and_E8-E1=3L/r_exactly_on_2x3..2x6_(gap_coeff_in_and_kappa_spectra;on_2x2_the_record_gives_gap_coeff_1.292167643=sqrt14-sqrt6,not_L=2);"
          "3x4,3x5:E2-E1=3,15/4_(the_3xL_law_at_L=4,5);the_met_if_(2x3..2x6)_is_fully_known_before_the_freeze;"
          "the_general-L_law_(2xL_with_L>=7,3xL_with_L>=6)_is_in_the_scope_but_not_scored"))
# X4 (blocking): FC2-12. The 4D repository (source FC2-S15) states, proves and MEASURED the character expansion; averaging over G is one linear step.
rfx5("T2-B-IDENTITY", "blind_recoded_1->0_(control):FC2-S15_proves_and_MEASURED_the_character_expansion;the_referee_question_is_withdrawn_(X4)",
     blind="0",
     known="FC2-S15:PREDICTION-YM4-02c.hbp_line_8_YM4_02C_CHARACTER_exp(beta*cos_theta)=sum_n(n+1)*l_n(beta)*chi_n(theta),l_n=2*I_(n+1)(beta)/beta;"
           "line_34_YM4_02C_RESULT_CHARACTER_tag=MEASURED,met=1,105_identities_through_beta^20_at_traces_2,1,0,-1,-2,0_failures;"
           "lines_9,35_YM4_02C_BALLOT_E[(Tr_U)^m*chi_n]_and_its_quadrature_checks_for_Q8,2T,2O,2I;"
           "LEMMA-0004-REFLECTION-TRANSFER.md_lines_170-180_(statement_and_proof),319;"
           "averaging_over_G_with_tr_g=2cos_theta_and_E_G[chi_n]=d_n_gives_this_row's_identity_in_one_linear_step;"
           "the_traces_checked_are_every_trace_that_occurs_in_Z3,Z4,Z6,Q8,Dic3,2T;"
           "FC2-S14:MEASURE-LADDER.hbp_GAUGE_F_and_SU2_GAUGE_F_hold_the_Taylor_series_of_ln_z_through_beta^30")
# X5 (minor): FC3-47, FC3-48. The 2D-torus rule for a finite G in FC2-S15 is a formula analog; no SU(2)_k value at k=3..12, so the codes stand.
A15 = ("formula_analog:FC2-S15_LEMMA-0004_line_183_'The_rule_on_a_two-dimensional_torus'_Z=sum_rho_c_rho^F*d_rho^(-F)_with_F=LT,and_line_321;"
       "PREDICTION-YM4-02c.hbp_line_37_YM4_02C_RESULT_TORUS_2D_(MEASURED):Q8_2x2=69425/16,Q8_3x2=16917185/64,2T_2x2=1572881/648;"
       "finite_G_only,no_SU(2)_k_value_at_k=3..12;code_unchanged")
rfx5("T3-C04 T3-C05", "known_before_freeze_extended_with_the_FC2-S15_formula_analog;blind_unchanged_(X5)", add=A15)
# X6 (minor): FC1-01, FC1-03. Finite-Universe-SU-N-solved (source FC1-S14) states the S3 flat-vacuum count for every periodic torus.
A14 = ("FC1-S14:FINITE_GROUP_LAWS.md_line_57_N_flat=sum_[g]k(C(g)),lines_69-79_periodic_flat_vacua_S3=8,"
       "'the_flat-vacuum_count_of_every_periodic_S3_torus_in_The-matrix-law-essentials',enumerated_directly;further_support_for_the_referee_question")
rfx5("T1-A1 T1-A3", "known_before_freeze_extended_with_FC1-S14;code_and_referee_question_unchanged_(X6)", add=A14)

# ------------------------------------------------------------------ assembly edits (each one leaves an asm= note)
OV = {
    "T1-A5": {"falsifier": "a_first-shell_state_with_M_other_than_4,or_a_nonflat_configuration_with_M<3,on_any_of_the_10_tori"},
    "T1-B3": {"falsifier": "any_count-form_entry_of_the_measured_Gamma_V,or_its_charpoly,different_from_the_value"},
    "T1-B4": {"falsifier": "any_count-form_entry_of_the_measured_Gamma_H,or_the_charpoly_of_Gamma_H_or_Gamma_V+Gamma_H,different_from_the_value"},
    "T1-B7": {"falsifier": "r^(Lmin-1)*(E6-E3)_has_a_nonzero_limit,or_r^(Lmin-1)*(E1+E8-E2-E7)_has_a_nonzero_limit"},
    "T1-B9": {"falsifier": "a_sector-resolved_measurement_puts_E2_in_the_swap-even_sector,or_F7-F8_off_mu=0"},
    "T1-C3": {"falsifier": "lim_r*(3r+6LxLy-E9)_differs_from_the_stated_coefficient_beyond_the_FC1-00_tolerance_on_any_torus"},
    "T1-X1": {"falsifier": "an_opened_D(S3)_S-matrix_gives_a_W_x_spectrum_other_than_(3,1,0,0,0,0,-1,-3)_or_a_W_x+W_y_spectrum_other_than_(sqrt14,sqrt6,0,0,0,0,-sqrt6,-sqrt14)"},
    "T1-X2": {"falsifier": "the_E9,E10,E11_triplet_splits_at_an_order_other_than_r^-(Lmin-1),or_lim_(E11-E10)/(E10-E9)_outside_[0.99,1.01]"},
    "T1-X3": {"reach": "low:_the_crossing_sits_at_L~10-40_for_r=4-6;exact_diagonalization_of_2xL_is_infeasible_there;needs_a_non-perturbative_method_with_certified_error"},
    "T1-O1": {"met_if": "UNSCORED_(OPEN_row:no_value_is_predicted;measured_values_are_recorded_as_data_only)",
              "not_met_if": "UNSCORED", "falsifier": "none_by_design_(not_a_prediction)"},
    "T3-A12": {"value_edit": ("replace", "C_n/2", "C_(n/2)"),
               "asm": "value_edited:notation_C_n/2_written_as_C_(n/2)_(Catalan_number_of_n/2);meaning_unchanged"},
    "T3-B03": {"met_if": "for_N=1..13:the_measured_nu_(N-1)_(from_independent_fusion_iteration)_matches_the_SU(2)_trace_moments_through_degree_2N-1_and_misses_degree_2N_by_exactly_1,and_the_(N+1)x(N+1)_Hankel_determinant_of_the_SU(2)_moments_is_nonzero",
               "not_met_if": "any_of_these_fails",
               "falsifier": "a_zero_SU(2)_moment_Hankel_determinant_for_some_N<=13_(an_N-atom_law_could_then_match_through_2N),or_nu_(N-1)_missing_a_moment_below_degree_2N"},
    "T3-B04": {"met_if": "all_of_C2,Z3,Z4,Z6,Q8,Dic3,Dic4,Dic6,2T,2O,2I_satisfy_t(G)<=2N_G-2,and_t(G)<=2N_G-3_when_-1_is_in_G,with_measured_t(G)_and_N_G",
               "falsifier": "one_of_those_eleven_groups_with_t(G)>2N_G-2,or_with_-1_in_G_and_t(G)>2N_G-3"},
    "T3-C10": {"value_edit": ("append", "; domain: b_j/b_0=O(beta^2) for every j>=1"),
               "asm": "value_edited:domain_condition_added.The_lane_proof_uses_'other_labels_enter_only_at_beta^12',which_needs_b_j/b_0=O(beta^2)_for_j>=1_(true_for_every_Wilson-like_weight,a_j/a_0=O(beta^(2j))).If_b_1/b_0~s*beta,spin-1_surfaces_add_d_1^-4*s^6_and_d_1^-6*s^6_at_beta^6_and_the_ratio_is_no_longer_d_1/2^2.Numbers_unchanged"},
    "T3-C11": {"falsifier": "the_implemented_variant_gives_a_beta^6_coefficient_of_f3_other_than_-sin^2(pi/(k+2))/3072_for_some_k,or_a_2D_thermodynamic_f_that_differs_from_SU(2)_at_some_order<=12"},
    "T3-C13": {"reach": "needs_an_implementation_of_the_Zache_et_al._point-split_plaquette_operator;two_clusters_(one_plaquette;two_plaquettes_sharing_an_original_link)_suffice_for_lambda^4"},
    "T3-C14": {"reach": "needs_a_4D_Oeckl_state_sum_with_the_ribbon_structure;the_assembly_seat_rates_it_hard"},
    "T3-C15": {"falsifier": "a_case_(i)_complex_whose_measured_first_difference_depends_on_d_1/2,or_a_case_(ii)_complex_whose_first_difference_does_not"},
    "T3-C16": {"met_if": "UNSCORED_(OPEN_row)", "not_met_if": "UNSCORED", "falsifier": "none_by_design_(not_a_prediction)"},
}
for k in ("T1-A5", "T1-B3", "T1-B4", "T1-B7", "T1-B9", "T1-C3", "T1-X1", "T1-X2"):
    OV[k]["asm"] = "falsifier_made_explicit_(lane_falsifier_was_'as_not_met');prediction_unchanged"
OV["T3-B04"]["asm"] = "verdict_rule_and_falsifier_made_concrete_(lane_text:'no_finite_subgroup_violates'/'such_a_subgroup');prediction_unchanged"
OV["T3-C11"]["asm"] = "falsifier_replaced_(lane_falsifier_was_self-referential:'impossible_by_C10');prediction_unchanged"
OV["T3-C15"]["asm"] = "falsifier_made_explicit_(lane_falsifier_was_'same');prediction_unchanged"
OV["T3-B03"]["asm"] = "verdict_rule_and_falsifier_made_concrete_(lane_text:'no_counterexample'/'such_a_law');prediction_unchanged"
for k in ("T1-O1", "T3-C16"):
    OV[k]["asm"] = "OPEN_row:verdict_set_to_UNSCORED"
OV["T1-X3"]["asm"] = "reachability_flag_added"
OV["T3-C13"]["asm"] = "reachability_note_added"
OV["T3-C14"]["asm"] = "reachability_flag_added"

# ------------------------------------------------------------------ fix seat: verdict-rule and value-label edits (each leaves a fix= note)
FOV = {
    "T1-C1": {"met_if": "per_protocol:the_exact_large-r_series_coefficient_of_r_in_E9-E8_equals_3_on_every_torus,with_no_Lx,Ly_dependence_at_that_order;"
                        "certified_values_(abs((E9-E8)/(3r)-1)<=2e-3_at_r=1000)_count_only_where_certification_is_feasible",
              "not_met_if": "on_any_torus_the_coefficient_of_r_in_E9-E8_differs_from_3_or_depends_on_Lx,Ly",
              "fix": "met_if_and_not_met_if_replaced:the_lane_rule_needed_certified_values_at_r=1000_on_every_torus,infeasible_beyond_2x3;prediction_unchanged"},
    "T2-C-FREEZE-LAW": {"value_edit": ("replace", ";measured:law_ratios", ";tool_D_K4:law_ratios"),
                        "fix": "value_edited:label_'measured:'_replaced_by_'tool_D_K4:'_(the_ratios_are_D-tool_values_from_PF-T2-2,4_defects,not_measurements);"
                               "numbers_unchanged;the_MET_windows_were_set_around_these_tool_ratios"},
    "T3-C16": {"value_edit": ("replace", "unknown; inside the class it is impossible because",
                              "unknown; inside the class, for plaquette weights with b_j/b_0=O(beta^2) for every j>=1 (the domain of FC3-53), it is impossible because"),
               "fix": "value_edited:the_FC3-53_domain_condition_added_to_the_impossibility_claim_(with_b_1/b_0~s*beta_spin-1_surfaces_enter_at_beta^6_and_the_argument_fails);"
                      "row_stays_OPEN_and_UNSCORED"},
}

# refix seat (after verify round 2): verdict-rule, quantity and value-notation edits; each leaves an "R3:" fix note
D53 = "b_j/b_0=O(beta^2) for every j>=1"
FOV2 = {
    "T1-B5": {"quantity_edit": ("(lim_r^(Lmin-1)*(E_i-Ebar)/scale)",
                                "(lim_r^(Lmin-1)*(E_i-Ebar),which_is_the_value:shape*s;the_normalized_limit_is_this_divided_by_s)"),
              "fix": "R3:quantity_edited:'/scale'_removed_from_the_limit,because_the_value_already_carries_the_scale_s_(V2);value_and_numbers_unchanged"},
    "T1-X3": {"met_if": "scored_only_by_the_referee_(no_mechanical_tolerance_is_stated):the_measured_crossing_L*(r)_for_two_values_of_r_follows_1.5r^2_within_O(r)",
              "fix": "R3:met_if_marked_referee-scored_(V4);the_row_stays_NOT_RUN_unless_a_certified_non-perturbative_method_exists;prediction_unchanged"},
    "T2-C-GAP": {"value_edit": (";1-sqrt2:2;", ";(2-sqrt2):2;"), "value_edit2": (";1-sqrt3:2;", ";(2-sqrt3):2;"),
                 "fix": "R3:value_edited:Delta1_notation_'1-sqrt2:2','1-sqrt3:2'_written_'(2-sqrt2):2','(2-sqrt3):2'_(num:den_format,FC2-00);numbers_unchanged_(V3)"},
    "T3-C10": {"quantity_edit": ("for any plaquette coefficients b_j with b_1/2/b_0=r1 beta+..., r1 nonzero",
                                 "for plaquette coefficients b_j with b_1/2/b_0=r1 beta+..., r1 nonzero, and " + D53 + " (the domain)"),
               "met_if": "measured ratio equals the value for at least two different weight choices, both with " + D53,
               "not_met_if": "for weights with " + D53 + ", the ratio depends on the weight or differs from the value",
               "falsifier": "Psi6=4 for some finite k, with a weight in the domain " + D53,
               "fix": "R3:quantity_edited_and_verdict_rules_restricted_to_the_domain_" + D53.replace(" ", "_") + "_(V1);numbers_unchanged"},
}

SCOPE3 = {"T3-B02": "k=5,6", "T3-B03": "every_probability_law_with_N_atoms", "T3-B04": "finite_subgroups_of_SU(2)",
          "T3-B05": "k=5_against_2I", "T3-B06": "SU(2)_k_k=1..12_and_finite_subgroups", "T3-C08": "k->infinity",
          "T3-C13": "Hamiltonian_qKS,k=1..12", "T3-C14": "D=4,k=1..12", "T3-C16": "SU(2)_k_3D_theories_outside_the_Oeckl_class",
          "T3-C03": "pillow,k=1..12", "T3-C04": "1x2_periodic_torus,k=1..12", "T3-C05": "2x2_periodic_torus,k=1..12",
          "T3-C06": "open_cube,k=1..12", "T3-C07": "3D_cubic_lattice,k=1..12", "T3-C09": "3D_cubic_lattice,k=1..12",
          "T3-C02": "2D_free_boundary,k=1..12", "T3-C11": "3D_cubic_lattice_variant_transport,k=1..12"}
PART1 = {"A": "a", "B": "b", "C": "c"}
PART1X = {"T1-X1": "b", "T1-X2": "c", "T1-X3": "c", "T1-O1": "all"}

preds = {"FC1": [], "FC2": [], "FC3": []}
defs = {}
srcvals = {}
srcquant = {}


def emit(test, lane_id, kv, kind):
    d = dict(kv)
    core = {}
    extras = []
    if test == "FC1":
        core["scope"] = d["torus"]
        core["part"] = PART1X.get(lane_id, PART1.get(lane_id[3], "all"))
        core["value"] = d["value"]
        core["met_if"], core["not_met_if"] = d.get("met_if", ""), d.get("not_met_if", "")
        skip = {"id", "torus", "quantity", "value", "tag", "met_if", "not_met_if", "falsifier", "json"}
    elif test == "FC2":
        core["scope"] = d["group"]
        core["part"] = d["part"]
        core["value"] = d["predicted"]
        core["met_if"], core["not_met_if"] = d["met_if"], d["not_met_if"]
        skip = {"id", "group", "part", "quantity", "predicted", "tag", "met_if", "not_met_if", "falsifier", "json"}
    else:
        core["part"] = d.get("part", "c")
        core["met_if"], core["not_met_if"] = d.get("met", ""), d.get("not_met", "")
        skip = {"id", "part", "quantity", "predicted", "tag", "met", "not_met", "falsifier", "json"}
        if kind == "TABLE":
            core["scope"] = "k=%s" % d["k"]
            core["quantity"] = "M_n(k) at k=%s for n=0..30 (one line of the predicted table; canonical text in fields k,n,M)" % d["k"]
            core["value"] = "the 31 values in field M"
        elif kind == "GAUGE_FIRST_BREAK":
            core["scope"] = "2D_free_boundary,k=%s" % d["k"]
            core["quantity"] = "ln Z_k - ln Z_SU2 per plaquette on the 2D free-boundary lattice (case (i)): last zero order, first and next nonzero coefficients"
            core["value"] = "zero through beta^%s; beta^%s: %s; beta^%s: %s" % (
                d["zero_through_beta_power"], d["first_nonzero_power"], d["value"], d["next_power"], d["next_value"])
            skip = skip | {"value"}
            extras.append(("first_value", d["value"]))
        else:
            core["scope"] = SCOPE3.get(lane_id, "SU(2)_k,k=1..12")
            core["value"] = d["predicted"]
    if "quantity" not in core:
        core["quantity"] = d["quantity"]
    core["tag"] = d["tag"]
    core["falsifier"] = d.get("falsifier", "")
    srcvals[lane_id] = core["value"]
    ov = OV.get(lane_id, {})
    for k, v in ov.items():
        if k in ("falsifier", "met_if", "not_met_if"):
            core[k] = v
        if k == "value_edit":
            core["value"] = core["value"].replace(v[1], v[2]) if v[0] == "replace" else core["value"] + v[1]
    fv = FOV.get(lane_id, {})
    for k, v in fv.items():
        if k in ("falsifier", "met_if", "not_met_if"):
            core[k] = v
        if k == "value_edit":
            if v[1] not in core["value"]:
                raise SystemExit("fix_value_edit_anchor_missing:" + lane_id)
            core["value"] = core["value"].replace(v[1], v[2])
    srcquant[lane_id] = core["quantity"]
    fv2 = FOV2.get(lane_id, {})
    for k, v in fv2.items():
        if k in ("falsifier", "met_if", "not_met_if"):
            core[k] = v
        if k in ("value_edit", "value_edit2", "quantity_edit"):
            fld = "quantity" if k == "quantity_edit" else "value"
            if v[0] not in core[fld]:
                raise SystemExit("refix_edit_anchor_missing:%s:%s" % (lane_id, k))
            core[fld] = core[fld].replace(v[0], v[1])
    if fv2:
        RFX.add(lane_id)
    fixnote = FIX.get(lane_id, []) + ([fv["fix"]] if "fix" in fv else []) + ([fv2["fix"]] if "fix" in fv2 else [])
    for k, v in kv:
        if k not in skip:
            extras.append((k, v))
    blind, pf, known = BL[lane_id]
    fields = [("id", None), ("src", lane_id), ("test", test), ("part", core["part"]), ("scope", core["scope"]),
              ("quantity", core["quantity"]), ("value", core["value"]), ("tag", core["tag"]), ("blind", blind),
              ("prefreeze", pf), ("known_before_freeze", known), ("met_if", core["met_if"]),
              ("not_met_if", core["not_met_if"]), ("falsifier", core["falsifier"])]
    if "reach" in ov:
        fields.append(("reach", ov["reach"]))
    if "asm" in ov:
        fields.append(("asm", ov["asm"]))
    if fixnote:
        fields.append(("fix", ";".join(fixnote)))
    fields += extras
    preds[test].append(fields)


for typ, kv in L1:
    if typ == "PREDICT":
        emit("FC1", dict(kv)["id"], kv, typ)
    elif typ == "T1_CONV":
        defs["FC1"] = kv
for typ, kv in L2:
    if typ == "T2ROW":
        emit("FC2", dict(kv)["id"], kv, typ)
    elif typ == "T2_DEF":
        defs["FC2"] = kv
for typ, kv in L3:
    d = dict(kv)
    if typ in ("ROW", "TABLE", "GAUGE_FIRST_BREAK"):
        if d["id"] == "T3-C00":
            defs["FC3"] = kv
        else:
            emit("FC3", d["id"], kv, typ)
T3SRC = [kv for typ, kv in L3 if typ == "SOURCE"]


def row(typ, fields):
    return typ + "|" + "|".join("%s=%s" % (k, v) for k, v in fields) + "|json=0"


out = []
lane_h = ";".join("%s:%s" % (p, h16(B + "/" + p)) for p in
                  ("T1/NOTE.md", "T1/ROWS.hbp", "T2/NOTE.md", "T2/ROWS.hbp", "T3/NOTE.md", "T3/ROWS.hbp", "T3/T3_TABLE.txt"))
out.append(row("FC_PREDICTION_HEAD", [
    ("schema", "FC_PREDICTION_V1"), ("date", "2026-11-09"), ("seat", "cloud"), ("role", "assembly"),
    ("file", OUTNAME), ("note", "NOTE-FINITE-CONTINUOUS-20261109.md"),
    ("measured_values", "0"), ("measurement_status", "NOT_RUN"), ("written_before_any_measurement", "1"),
    ("tests", "FC1:universal_against_non-universal_on_ten_finite_S3_tori_(flat_band,its_first_splitting,the_gap;2xL_contrast)"
              ";FC2:where_the_break_sits_for_ten_finite_subgroups_of_SU(2)_(design_degree,2D_crossover_beta_x,turnover)"
              ";FC3:SU(2)_k_past_the_degree-11_ceiling_and_the_q-deformed_lattice_caveat"),
    ("lanes", "T1->FC1,T2->FC2,T3->FC3"), ("lane_files_sha256_16", lane_h),
    ("tags", "MEASURED,DERIVED,REPORTED,CONJECTURE,OPEN"), ("verdicts", "MET,NOT_MET,NOT_RUN,UNSCORED_(OPEN_rows)"),
    ("blind_codes", "1=nothing_computed_or_reported_before_the_freeze_gives_the_measured_value_on_any_instance_in_scope;"
                    "partial=some_instances_known_(pre-freeze_computation_or_prior_record);"
                    "0=control,value_known_before_the_freeze_(pre-freeze_computation_or_prior_record);"
                    "weak=an_approximate_pre-freeze_evaluation_of_the_measured_quantity_exists_(PF-T2-2_tools),so_MET_checks_the_tool_and_its_truncation;"
                    "na=not_a_blind_test:OPEN_rows_are_UNSCORED;the_REPORTED_literature_row_FC2-60_is_scored_by_the_referee_from_its_sources;"
                    "finite-r_rule:one_certified_or_trial-space_finite-r_record_of_a_limit_quantity_makes_the_row_partial,not_blind;"
                    "pre-freeze_rule:a_row_whose_prefreeze_run_printed_its_value_on_an_instance_in_scope_is_not_blind"),
    ("blind_search_scope", "the_finite_repository_holds_many_earlier_records;a_blind_code_states_what_the_searches_listed_in_the_SOURCE_rows_(FC1-S11,FC1-S12,FC1-S13,FC1-S14,FC2-S13,FC2-S14,FC2-S15),"
                           "in_search_rounds_and_in_the_NOTE_found_up_to_search_cutoff,not_a_guarantee;"
                           "searched:finite-universe-yang-mills-existence-and-mass-gap-using-heb-c_(main_6a7fc747,pr154,all_324_refs),The-matrix-law-essentials_(main_e9eb988),Iconic-3-space_(main_5886d99),"
                           "yang-mills-4-dimensional-continum-proof_(main_830fd3fd,docs/_included;dfe0859b),gguf-files-operating-as-trained-quantum-neural-network-models_(main_98ef58a),"
                           "Finite-Universe-SU-N-solved_(main_e6d36326),continuum-Clay-variation_(main_7cba1987)"),
    ("search_rounds", "four:(1)_the_review_after_assembly_(2026-11-09;finite_repository_records_at_6a7fc747;found_FC1-S11);"
                      "(2)_verify_round_2_(fc-tests/verify-hunter;git_ls-remote_2026-11-09T21:57Z:finite_main_6a7fc747_324_refs,Iconic_main_5886d99_23_refs,4D_main_830fd3fd_92_refs;"
                      "found_the_FC1-S11_labels_zgap2R,2x5B,rev55,FC1-S12,FC2-S13);"
                      "(3)_verify_round_3_(fc-tests/verify-hunter3-1;git_ls-remote_2026-11-10T00:35Z:the_same_three,The-matrix-law-essentials_main_e9eb988_22_refs,"
                      "gguf-files-operating-as-trained-quantum-neural-network-models_main_98ef58a_48_refs;found_FC1-S13,FC2-S14);"
                      "(4)_verify_round_4_(fc-tests/verify-hunter3-2;git_ls-remote_2026-11-10T01:04Z_of_the_same_five,refs_unchanged_except_one_qnn_WIP_branch;"
                      "mirror_clones_of_those_five_and_of_Finite-Universe-SU-N-solved_(54_refs)_and_continuum-Clay-variation_(10_refs);"
                      "every_object_read,unreachable_ones_included;also_the_local_finite,4D,qnn,finite-reversible_and_analysis-of-cubes_repositories;found_FC1-S14,FC2-S15)"),
    ("search_cutoff", "2026-11-10T11:30Z;the_last_search_(round_4)_read_refs_as_of_2026-11-10T01:04Z;"
                      "refs_that_moved_or_appeared_after_round_4_were_not_searched_(git_ls-remote_2026-11-10T14:35Z,refix-r4/out/lsremote-*.txt):"
                      "4D_main_830fd3fd->2616622d_(new_commits_2026-11-10T13:04Z..14:05Z;the_FC2-S15_blobs_unchanged),4D_branch_local-opus55-ym4-06a-global-lock-20261110=pull/47_(2a2f598,2026-11-10T13:50Z),4D_pull/45/merge,"
                      "finite_branches_local-opus55-global-lock-20261110_(26756c9,2026-11-10T12:23Z)_and_measure-global-lock-20261110_(b3eeca0,2026-11-10T13:06Z)_with_pull/158,159,"
                      "qnn_cloud-seat-stripe-reader-20261109=pull/18_(cc01837->bfd93f4,2026-11-10T02:27Z,before_the_cutoff,not_searched)_and_pull/18/merge"),
    ("late_record_rule", "a_previously_established_result_found_after_the_freeze,or_after_the_search_cutoff,reclassifies_the_affected_row_as_control_(blind=0)_and_never_changes_its_prediction_"
                         "(value,quantity,tag,scope,met_if,not_met_if,falsifier)"),
    ("prior_records", "FC1-S11:the_finite_repository's_own_records_held_measured_values_for_some_FC1_rows_before_this_file;those_rows_are_controls_or_partial;"
                      "FC1-S12_(PR_#154)_held_the_D(S3)_S-matrix;FC1-S13_(The-matrix-law-essentials)_held_exact_large-r_limits_on_nine_tori;"
                      "FC2-S13_holds_a_script_for_the_P_SU2_series;FC2-S14_(Iconic_MEASURE-LADDER)_holds_the_exact_small-beta_series_of_ln_z_G-ln_z_SU2"),
    ("fix_seat", "review_findings_applied_after_assembly;each_change_and_its_reason_in_final/CHANGES.txt;edited_rows_carry_a_fix_field"),
    ("refix_seat", "verify-round-2_findings_(FINDINGS-VERIFY-R2.json,18)_applied;fix_notes_prefixed_R3:;CHANGES.txt_section_VERIFY-ROUND;previous_package_kept_in_final/superseded-r3-1/;"
                   "round_2_(after_verify_round_3,9_findings):fix_notes_prefixed_R4:;CHANGES.txt_section_VERIFY-ROUND-3;previous_package_kept_in_final/superseded-r3-2/;"
                   "round_3_(after_verify_round_4,FINDINGS-VERIFY-R4.json,7_items):fix_notes_prefixed_R5:;CHANGES.txt_section_VERIFY-ROUND-4;previous_package_kept_in_final/superseded-r3-3/"),
    ("row_fields", "id,src(lane_row),test,part,scope,quantity,value,tag,blind,prefreeze,known_before_freeze,met_if,not_met_if,falsifier[,reach][,asm][,fix],lane_extras"),
    ("value_fidelity", "value,quantity,tag,met_if,not_met_if_and_lane_extras_copied_verbatim_from_the_lane_row_except_where_an_asm_or_fix_field_says_otherwise"),
    ("integer_only_scripts", "1"), ("repo_writes", "0"), ("github_posts", "0"),
    ("frame", "the_owner's_frame_is_stated_in_NOTE_section_1_and_is_not_a_claim_of_any_row")]))

SRC = {
    "FC1": [("S1", "finite-universe-yang-mills-existence-and-mass-gap-using-heb-c@6a7fc747:docs/YM_TOPOLOGICAL_STABILITY_PROOF.md", "opened_by_lane_T1;existence_at_commit_rechecked_by_assembly"),
            ("S2", "finite-universe-yang-mills-existence-and-mass-gap-using-heb-c@cbd8b70d:independent/FINITE_3X4_S3_FIRST_GAP_LARGE_R_20261108.md_(#143)", "opened_by_lane_T1;assembly_reread_C1=CA+CB+0_and_the_3/r^2_law"),
            ("S3", "finite-universe-yang-mills-existence-and-mass-gap-using-heb-c@6a7fc747:docs/FINITE_S3_FIRST_GAP_AND_TERNARY_SCHUR.md", "opened_by_lane_T1;existence_rechecked"),
            ("S11", "finite-universe-yang-mills-existence-and-mass-gap-using-heb-c@6a7fc747:"
                    "(zgap2)native/ym/results/zgap2-2026-10-30-cloud/README.md;(2xL)native/ym/results/2xL/README.md;"
                    "(ritz)independent/SEAT_3X3_VACUUM_BLOCK_RITZ_REPORT.md_sections_A-C_and_README.md_row_'3x3_Ritz_report';"
                    "(ladder)README.md_section_'2x2_coupling_ladder:E1-E0';(README)README.md_2xL_summary_(2x5:E9-E8>=21.778_for_r>=9);"
                    "(zgap2R)native/ym/results/zgap2-2026-10-30-cloud/RESULT.hbp;"
                    "(2x5B)native/ym/results/2x5_stage_b/HEBC-YM-2X5-STAGE-B.hbp_(added_at_a853916,2026-10-27);"
                    "(rev55)native/ym/results/3x4_stream/perron/vector/review-opus55/out/_files_flats_4x4.out,flats_4x5.out,lowm_4x4_r9.out,lowm_4x5_r9.out,"
                    "exact_4x4_r9.out,exact_4x5_r9.out,ritz_3x3_r9.out,e8_3_3_9.out,e8_3_4_9.out,e8_4_4_9.out,e8_4_5_9.out,"
                    "ritz_3x4_r9_m16.bound,ritz_4x4_r9_m15.bound,ritz_4x5_r9_m12.bound_(added_at_e0466bd,2026-11-03)",
             "opened_read-only_by_the_fix_seat_after_review_finding_F1;the_repository's_own_measured_records_(exact_integer_perturbation_theory,"
             "certified_intervals,Ritz_trial-space_values),all_present_at_commit_6a7fc747,which_predates_this_file;not_cited_by_lane_T1_or_the_assembly_seat;"
             "used_only_to_set_blind_and_known_before_freeze;"
             "refix_seat_(after_verify_round_2):labels_zgap2R,2x5B,rev55_added;every_S11_file_reopened_read-only_at_6a7fc747_with_git_show_and_the_quoted_lines_confirmed;"
             "blob_sha256_16:zgap2=742cda2122b7f291,2xL=410068a6baa0a8f4,ritz=f777655ecd83d0da,README=57975a8e1da736eb,zgap2R=a0448af4e5cd8255,2x5B=6a768396264d75dd,"
             "flats_4x4=f2802ffea71ee801,flats_4x5=55073fc87cd308a3,lowm_4x4_r9=4ef74358e0bcf127,lowm_4x5_r9=db8531de4b77dd99,exact_4x4_r9=715507edfb41f958,"
             "exact_4x5_r9=8ac0f67809fd15fc,ritz_3x3_r9=846b65ee6d5d0c65,e8_3_3_9=b40433da277e4795,e8_3_4_9=4da9acd899a97843,e8_4_4_9=49132d35f81a357d,"
             "e8_4_5_9=38a1c4982cb8a3b1,ritz_3x4_r9_m16=f8b1a0663e58bbe9,ritz_4x4_r9_m15=c09de25695acbff1,ritz_4x5_r9_m12=5177bc8c46be82a5"),
            ("S12", "finite-universe-yang-mills-existence-and-mass-gap-using-heb-c@b8a2daa_(branch_pr154,PR_#154,unmerged;committed_2026-11-09_13:16_-0300):"
                    "independent/ICONIC-RELATIONSHIP-20261109.hbp_rows_MODULAR_S_and_CHECK_six_S_real_symmetric_unitary",
             "opened_read-only_by_the_refix_seat_after_verify_round_2_(git_show);blob_sha256_16_5c51b1895a1d0c2f;the_measured_6S_matrix_of_D(S3)_in_the_charge-flux_basis;"
             "used_only_to_set_FC1-38's_blind_and_known_before_freeze"),
            ("S13", "The-matrix-law-essentials@28345a6_(2026-10-25_18:42_-0300)_and_8a28b50_(2026-10-25_19:01_-0300;the_final_flat_law.hbp_and_flat_law3.hbp,"
                    "unchanged_at_main_e9eb988):data/volume/flat_law.hbp,flat_law3.hbp,flat_law4.hbp,second_order.hbp;README.md_section_'Results:_exact_weak-coupling_laws'",
             "opened_read-only_by_the_refix_seat_round_2_after_verify_round_3_(git_show_on_a_clone;git_ls-remote_main=e9eb988);not_cited_by_lane_T1_or_by_any_earlier_seat;"
             "exact_large-r_coefficients_from_integer_characteristic_polynomials_with_Sturm_root_isolation;"
             "blob_sha256_16:flat_law@28345a6=474e50f575c0473f_(stops_after_3x3_with_a_traceback),flat_law@8a28b50=e9eb988=a0e04aa9906112f6,"
             "flat_law3@28345a6=56de742aea8506cd,flat_law3@8a28b50=e9eb988=d863691b620f531d,flat_law4=c15daf95fd28ee37_(both),second_order=01b04ac14561a69e,"
             "README@28345a6=50e928f091d18182,README@e9eb988=20f8470919359e7f;used_only_to_set_blind_and_known_before_freeze",
             {"gives_exact": "T1-B-2x2 T1-B-2x3 T1-B-2x4 T1-B-2x5 T1-B-2x6 T1-B-3x3 T1-B-3x4 T1-B-3x5 T1-B-4x4 T1-B8",
              "gives_instances": "T1-A1 T1-A3 T1-A4 T1-A5 T1-B1 T1-B2 T1-B3 T1-B5 T1-B6 T1-B7 T1-B10 T1-B11",
              "names_only": "T1-B-4x5"}),
            ("S14", "Finite-Universe-SU-N-solved@e6d36326_(main;the_file_added_at_242f8a8,2026-10-31_07:50_-0300):docs/FINITE_GROUP_LAWS.md_lines_57,69-79",
             "found_by_search_round_4_(verify-hunter3-2);opened_read-only_by_the_refix_seat_round_3_(git_show_on_the_round-4_clone;git_ls-remote_main=e6d36326_at_2026-11-10T14:35Z);"
             "git_blob_80156c8d,sha256_16_ef03a375cf2d6728;outside_every_earlier_search;N_flat=sum_[g]k(C(g))_and_the_S3_count_8_for_every_periodic_torus,attributed_to_The-matrix-law-essentials;"
             "used_only_for_known_before_freeze_of_FC1-01_and_FC1-03",
             {"gives_instances": "T1-A1 T1-A3"})],
    "FC2": [("S4", "DLMF_10.29.1,10.29.2,10.32.3,10.40.1_(10.40(ii)_bounds_only_for_K_nu),10.41.3,10.41.5,10.41.7-10.41.11", "opened_by_lane_T2"),
            ("S5", "INSPIRE_records:Petcher-Weingarten_PRD22_2465_(1980)_id153202;Rebbi_PRD21_3350_(1980);Bhanot-Rebbi_PRD24_3319_(1981,SU(3)_subgroups);Bhanot-Rebbi_NPB180_469_(1981,SU(2))", "opened_by_lane_T2"),
            ("S6", "iconic-3-space@pr7(fb9990e5):proofs/transfer/TRANSFER-THEOREM.md_sections_0,2.4,3,4,7;predictions/su2-ladder/PREDICTION.hbp_on_main", "opened_by_lanes_T2,T3;assembly_reread_the_ladder_table"),
            ("S13", "yang-mills-4-dimensional-continum-proof@dfe0859b_(branch_cloud-seat-ym4-04c-evidence-20261109;2026-11-09_14:13_UTC):"
                    "reviews/ym4-04c-prediction/ym4-04c/smallfield-largefield/d3_atom.py_lines_17-42",
             "opened_read-only_by_the_refix_seat_(git_show);blob_sha256_16_245d3d6fe6a62296;script_only:it_builds_the_Hankel_coefficients_of_I_1,I_2_and_prints_I2/I1_to_6_terms;"
             "its_output_is_not_committed_and_the_script_was_not_run;used_only_for_FC2-29's_known_before_freeze"),
            ("S14", "Iconic-3-space@565b9ac_(on_main;2026-11-09_13:47_-0300):measurements/su2-ladder/MEASURE-LADDER.hbp_rows_GAUGE_DIFF,GAUGE_F_(61_groups,n=0..30)_and_SU2_GAUGE_F",
             "opened_read-only_by_the_refix_seat_round_2_(git_show);blob_sha256_16_13853c1b5013a67d_(git_blob_2ea58967a174);exact_rationals_of_ln_z_G-ln_z_SU2_through_beta^30_"
             "for_all_ten_FC2_groups_(labels_C3,C4,C6,Dic2,Dic3,Dic4,Dic6,2T,2O,2I);it_fixes_only_the_small-beta_region;used_only_for_known_before_freeze_of_FC2-12_to_FC2-15",
             {"names_only": "T2-B-IDENTITY T2-B-SIGN T2-B-ENVELOPE T2-B-SMALL"}),
            ("S15", "yang-mills-4-dimensional-continum-proof@830fd3fd_(main_at_search_round_4;an_ancestor_of_main_2616622d,where_both_blobs_are_unchanged):"
                    "docs/PREDICTION-YM4-02c.hbp_lines_8,9,34,35,37_(lines_8,9_added_at_0e9bcff,2026-11-03_18:06_-0300;result_lines_34,35,37_at_c31a033,2026-11-03_19:06_-0300);"
                    "docs/LEMMA-0004-REFLECTION-TRANSFER.md_lines_170-180,183,319,321_(the_file_added_at_c31a033)",
             "found_by_search_round_4_(verify-hunter3-2);a_raw_scan_of_search_round_2_logged_line_8_without_a_finding;opened_read-only_by_the_refix_seat_round_3_(git_show);"
             "blob_sha256_16:PREDICTION-YM4-02c.hbp=963b446a633b2485_(git_blob_b4cec322),LEMMA-0004=3d99bfa8b6dd5bd7_(git_blob_1f7dcb38);"
             "the_character_expansion_of_exp(beta*cos_theta),proved_and_MEASURED_(105_identities_through_beta^20,0_failures),and_the_2D-torus_rule_for_finite_G;"
             "used_only_for_known_before_freeze_of_FC2-12,FC3-47_and_FC3-48",
             {"gives_exact": "T2-B-IDENTITY", "names_only": "T3-C04 T3-C05"})],
}
SRC["FC3"] = [("S7", dict(kv)["ref"], dict(kv).get("opened", "local_records_read_by_lane_T3") + ";used:" + dict(kv)["used"]) for kv in T3SRC]
SRC["FC3"] = [("S%d" % (7 + i), r, o) for i, (_, r, o) in enumerate(SRC["FC3"])]

CONV = {
    "FC1": [("hamiltonian", "H/J_E=6LxLy*I-T+r*M_on_the_gauge-invariant_space_of_S3_LGT_on_the_periodic_LxLy_torus;T=sum_of_transposition_link_moves;M=sum_p(3-#fix(g_p));r=J_B/J_E"),
            ("tori", "2x2,2x3,2x4,2x5,2x6,3x3,3x4,3x5,4x4,4x5"), ("units", "J_E")] +
           [(k, v) for k, v in defs["FC1"] if k != "json"] +
           [("protocol_note", "per_protocol_in_a_row_means_this_verdict_protocol;exact_series_coefficients_are_preferred_on_every_torus_(finite-r_certification_is_infeasible_beyond_2x3)")],
    "FC2": [(k, v) for k, v in defs["FC2"] if k != "json"] +
           [("groups", "Z3,Z4,Z6,Q8=Dic2,Dic3,Dic4,Dic6,2T,2O,2I"), ("numeric_format", "decimals_as_printed;rationals_as_num:den")],
    "FC3": [("src", "T3-C00"), ("kind", "construction_C_k_(definition,not_a_prediction;not_counted)")] +
           [(("lane_" + k) if k in ("tag", "met", "not_met", "falsifier") else k, v) for k, v in defs["FC3"] if k not in ("json", "id")] +
           [("rational_format", "num:den"), ("decimal_format", "12_significant_digits"), ("f_convention", "f=ln(Z)/N_p")],
}
TYPEC = {"FC1": "CONV", "FC2": "DEF", "FC3": "DEF"}
counts = {}
idmap = {}
for test in ("FC1", "FC2", "FC3"):
    for i, fields in enumerate(preds[test]):
        idmap[dict(fields)["src"]] = "%s-%02d" % (test, i + 1)
SRCLINT = ("gives_exact", "gives_instances", "names_only")
for test in ("FC1", "FC2", "FC3"):
    for srow in SRC[test]:
        sid, ref, opened = srow[:3]
        ext = srow[3] if len(srow) > 3 else {}
        out.append(row("SOURCE", [("id", "%s-%s" % (test, sid)), ("tag", "REPORTED"), ("ref", ref), ("opened", opened)] +
                       [(k, ",".join(idmap[x] for x in ext[k].split())) for k in SRCLINT if k in ext]))
    out.append(row(TYPEC[test], [("id", "%s-00" % test)] + CONV[test]))
    for i, fields in enumerate(preds[test]):
        fid = "%s-%02d" % (test, i + 1)
        fields[0] = ("id", fid)
        idmap[dict(fields)["src"]] = fid
        out.append(row("PREDICT", fields))

# ------------------------------------------------------------------ counts
allp = [dict(f) for t in ("FC1", "FC2", "FC3") for f in preds[t]]
TAGS = ("MEASURED", "DERIVED", "REPORTED", "CONJECTURE", "OPEN")
BLS = ("1", "partial", "0", "weak", "na")


def cnt(rows, key, vals):
    return ",".join("%s:%d" % (v, sum(1 for r in rows if r[key] == v)) for v in vals)


per = ";".join("%s(%d)=%s" % (t, len(preds[t]), cnt([dict(f) for f in preds[t]], "tag", TAGS)) for t in ("FC1", "FC2", "FC3"))
perbl = ";".join("%s=%s" % (t, cnt([dict(f) for f in preds[t]], "blind", BLS)) for t in ("FC1", "FC2", "FC3"))


def asm_kind(a):
    if a.startswith("value_edited"):
        return "value_notation_or_domain"
    if a.startswith("reachability"):
        return "reachability_flag_only"
    return "falsifier_or_verdict_rule_only"


AK = ("falsifier_or_verdict_rule_only", "value_notation_or_domain", "reachability_flag_only")
asm_by = ";".join("%s:%d(%s)" % (k, sum(1 for r in allp if "asm" in r and asm_kind(r["asm"]) == k),
                                 ",".join(r["id"] for r in allp if "asm" in r and asm_kind(r["asm"]) == k)) for k in AK)
out.append(row("PREDICTION_END", [
    ("prediction_rows", str(len(allp))), ("by_tag", cnt(allp, "tag", TAGS)), ("by_test", per),
    ("by_blind", cnt(allp, "blind", BLS)), ("by_blind_per_test", perbl),
    ("control_rows_blind0", ",".join(r["id"] for r in allp if r["blind"] == "0")),
    ("non_prediction_rows", "head=1,source=%d,conv_or_def=3,end=1,prefreeze=see_below" % sum(len(SRC[t]) for t in SRC)),
    ("measured_values", "0"), ("assembly_edits", str(sum(1 for r in allp if "asm" in r))), ("assembly_edits_by_kind", asm_by),
    ("fix_edits", "%d_rows_carry_fix(%s)" % (sum(1 for r in allp if "fix" in r), ",".join(r["id"] for r in allp if "fix" in r))),
    ("open_rows_unscored", ",".join(r["id"] for r in allp if r["tag"] == "OPEN")),
    ("refix_round3_rows", "%d(%s)" % (len(RFX), ",".join(sorted(idmap[i] for i in RFX)))),
    ("refix_round4_rows", "%d(%s)" % (len(RFX4), ",".join(sorted(idmap[i] for i in RFX4)))),
    ("refix_round5_rows", "%d(%s)" % (len(RFX5), ",".join(sorted(idmap[i] for i in RFX5))))]))

# ------------------------------------------------------------------ pre-freeze disclosure
PF = [
    ("PF-T1-1", "T1", "T1/s3_gamma.py", "T1/s3_gamma.out", "group-level_S3_only,no_torus:18_commuting_pairs,8_orbits,weights;Gamma_V,Gamma_H_and_charpolys;#143_CA/CB_blocks;M=3_internal_orbits_and_alpha/beta/row-pair_counts;integer-sqrt_decimals"),
    ("PF-T1-2", "T1", "T1/cycle_orderings.py", "T1/cycle_orderings.out", "combinatorics_on_the_cycle_C_m,no_torus,no_group:N_m=binom(2m-2,m-1)_for_m=2..8"),
    ("PF-T1-3", "T1", "T1/torus2x2_second_order.py", "T1/torus2x2_second_order.out", "2x2_torus_only_(allowed_smallest_case):tree-gauge_census_(18_flat,72_M3_configs;8_and_12_orbits);two-move_path_sums:flat_sector_6I+Gamma_V+Gamma_H,M3_12x12_matrix;no_Hamiltonian_built,nothing_diagonalized"),
    ("PF-T2-1", "T2", "T2/prefreeze/t2_groups.py", "T2/prefreeze/GROUPS.hbp", "exact_quaternion_closure_of_the_10_groups;moments_M_n_(n<=42);d_n_by_group_sum_and_by_Klein;t,iota,Transfer_coefficients;trace_classes;integer_Wronskian_series_W_n,D_n_(n<=30);151_checks_0_failed"),
    ("PF-T2-2", "T2", "T2/prefreeze/t2_asym.py", "T2/prefreeze/ASYM.hbp", "truncated_asymptotic_tools_S,D,L_on_a_beta_grid,crossings_by_bisection,closed-form_laws,exact_Hankel_rationals;no_exact_plaquette_curve_except_that_for_Z3_the_L_tool_is_the_full_class_sum_on_the_group_side;12_checks_0_failed"),
    ("PF-T3-1", "T3", "T3/t3_small_checks.py", "T3/small_checks.out", "the_only_SU(2)_k_fusion_enumeration:k=1,2,n<=30;series_arithmetic_of_the_derived_formulas_at_k<=2_(2D_free,pillow,1x2_and_2x2_tori,open_cube,3D_formula,Hamiltonian_RS_arithmetic,Psi6);41_checks_0_failed"),
    ("PF-T3-2", "T3", "T3/t3_closed_forms.py", "T3/closed_forms.out", "closed_form_A3_only_for_k=1..12,n=0..30_(writes_T3/T3_TABLE.txt_sha256_3c8e7da5564a106b);consistency_with_A2,A4,A6,A7;C2_rationals;2cos(pi/(k+2))_by_integer_bisection;decimals;62_checks_0_failed;no_fusion_iteration_for_k>=3"),
]
PFX = {"PF-T3-1": [("blind_k12_exempt", "FC3-54_(variant_transport:not_evaluated),FC3-55_(weak-coupling_limit:not_evaluated),FC3-57_(D=4:not_evaluated)"),
                   ("blind_k12_rule", "every_other_FC3_row_with_some_k<=2_in_scope_lists_this_run_and_is_not_blind=1_(refix_seat_round_2,W2)")],
       "PF-T2-2": [("blind_effect", "every_row_it_touches_is_blind=weak:its_tool_values_approximate_the_measured_quantity_(fix_seat,F2);"
                                    "except_FC2-29,whose_value_(the_exact_Hankel_rationals,ASYM.hbp_SU2_LARGE_BETA)_it_printed_exactly:partial_(refix_seat,V17)"),
                   ("referee_question", "did_this_run_exceed_the_brief's_smallest-case_allowance_(no_plaquette_curves_beyond_the_smallest_cases)?"
                                        "_open;the_referee_seat_records_the_answer_and_its_reason")]}
pfrows = []
for pid, lane, scr, outp, scope in PF:
    touches = ",".join(sorted(idmap[r["src"]] for r in allp if pid in r["prefreeze"].split(",")))
    pfrows.append(row("PREFREEZE", [("id", pid), ("lane", lane), ("script", SCR + "/" + scr), ("sha256_16", h16(B + "/" + scr)),
                                    ("output", SCR + "/" + outp), ("output_sha256_16", h16(B + "/" + outp)), ("run", "python3_-I_-B"),
                                    ("integer_only", "1"), ("measurement", "0"), ("scope", scope), ("touches", touches or "none")] + PFX.get(pid, [])))
pfrows.append(row("PREFREEZE", [("id", "PF-T2-3"), ("lane", "T2"), ("script", "t2_asym.py_superseded_development_runs"),
                                ("sha256_16", "fe60126fd161300c,901f3dc3bef21067"), ("output", "overwritten_by_PF-T2-2"),
                                ("output_sha256_16", "not_retained"), ("measurement", "0"),
                                ("scope", "same_tools_as_PF-T2-2;differ_only_in_defect-truncation_bookkeeping_and_reporting"), ("touches", "none_(superseded)")]))
pfrows.append(row("PREFREEZE", [("id", "PF-T3-3"), ("lane", "T3"), ("script", SCR + "/T3/t3_rowlint.py"), ("sha256_16", h16(B + "/T3/t3_rowlint.py")),
                                ("output", "stdout_only"), ("measurement", "0"), ("computational", "0_(lint_only;computes_no_row_value)"),
                                ("scope", "format_lint_of_T3/ROWS.hbp_(69_rows_0_bad;TABLE_rows_byte-equal_to_T3_TABLE.txt);first_written_one_directory_up_and_moved_into_T3_within_seconds_(lane_disclosure)"), ("touches", "none")]))
pfrows.append(row("PREFREEZE", [("id", "PF-T2-0"), ("lane", "T2"), ("script", "none_(mental_arithmetic_while_planning)"), ("measurement", "0"),
                                ("scope", "rough_orientation_at_Z3_and_Dic3_beta=4,N(T)_model_beta=5,10,2I_gap_model_beta=16-35;no_row_value_from_it_(lane_disclosure)"), ("touches", "none")]))
repro = ";".join("%s:%s" % (p, h16(FINAL + "/repro/" + p)) for p in
                 ("T1/s3_gamma.out", "T1/cycle_orderings.out", "T1/torus2x2_second_order.out", "T2/GROUPS.hbp", "T2/ASYM.hbp",
                  "T3/small_checks.out", "T3/closed_forms.out", "T3/T3_TABLE.txt"))
pfrows.append(row("PREFREEZE", [("id", "PF-A-1"), ("lane", "assembly"), ("script", "unchanged_copies_of_PF-T1-1..3,PF-T2-1..2,PF-T3-1..2_in_" + SCR + "/final/repro"),
                                ("sha256_16", "identical_to_the_lane_scripts"), ("output", SCR + "/final/repro"), ("output_sha256_16", repro),
                                ("run", "python3_-I_-B"), ("measurement", "0"),
                                ("scope", "reproduction_only:every_output_byte-identical_to_the_lane_output;no_new_quantity"), ("touches", "none_(same_as_the_reproduced_runs)")]))
pfrows.append(row("PREFREEZE", [("id", "PF-A-2"), ("lane", "assembly"), ("script", SCR + "/final/fc_arith_check.py"), ("sha256_16", h16(FINAL + "/fc_arith_check.py")),
                                ("output", SCR + "/final/arith_check.out"), ("output_sha256_16", h16(FINAL + "/arith_check.out")), ("run", "python3_-I_-B"),
                                ("integer_only", "1"), ("measurement", "0"),
                                ("scope", "arithmetic_of_derived_formulas_only:Gamma_charpolys,detailed_balance,kappa,E2-E1_per_torus,2xL_and_2x2_gap_coefficients;Molien->t,iota,coefficients;Hankel_rationals;Transfer_law_roots;freeze-law_x*;T3_table_hash_and_internal_consistency;C02_and_pillow_rationals;12-digit_case-(ii)_decimals_from_2cos(pi/(k+2))_by_bisection;Hankel_determinants_of_Catalan_moments;no_torus,no_group_closure,no_fusion_iteration,no_plaquette_curve"),
                                ("touches", ",".join(sorted(idmap[r["src"]] for r in allp if "PF-A-2" in r["prefreeze"].split(",")))
                                 + "_(its_Hankel_rationals_are_that_row's_value;refix_seat,V17);for_every_other_row_it_re-derives_printed_values_and_changes_none")]))
SUP = FINAL + "/superseded"
SUP3 = FINAL + "/superseded-r3-1"
SUP4 = FINAL + "/superseded-r3-2"
SUP5 = FINAL + "/superseded-r3-3"
R5DEV = ("dev1_script_9f75f76bcafbdf5a,HBP_df09836adfbf439c_(0_lint_errors;differs_from_the_final_in_the_PF-A-4_scope_text_and_this_list);"
         "dev2_script_d71f0b9e821d446b,HBP_6bb69063be6a0d98_(0_lint_errors;differs_from_the_final_only_in_this_list);"
         "one_lint_mutation_test_on_a_temporary_copy_(four_rows_or_fields_broken_on_purpose;4_lint_errors_as_expected;copy_deleted;output_refix-r4/out/mut.out_34841b0319b8ac53)")
R4DEV = ("dev1_script_d59cf0d757d405f1,HBP_d889e3e8f7e4ac08_(0_lint_errors;differs_from_the_final_only_in_this_list);"
         "one_lint_mutation_test_on_a_temporary_copy_(five_rows_broken_on_purpose;6_lint_errors_as_expected,one_row_caught_by_two_rules;copy_and_output_deleted)")
R3DEV = ("dev1_script_3135c7d129327499,HBP_b3ef666c0c36e712_(0_lint_errors;differs_from_the_final_only_in_PF-A-4_and_PF-A-5_texts);"
         "dev2_script_cd2883d376aaa2cb,HBP_7da7d6ac48024283_(0_lint_errors;differs_from_the_final_only_in_this_list);"
         "one_lint_mutation_test_on_a_temporary_copy_(eight_blind_codes_and_one_fix_note_broken_on_purpose;9_lint_errors_as_expected;copy_and_output_deleted,not_retained)")
pfrows.append(row("PREFREEZE", [("id", "PF-A-3"), ("lane", "assembly,edited_by_the_fix_seat_and_the_refix_seat"), ("script", SCR + "/final/fc_assemble.py"), ("sha256_16", h16(__file__)),
                                ("output", SCR + "/final/" + OUTNAME), ("run", "python3_-I_-B"), ("integer_only", "1"), ("measurement", "0"),
                                ("computational", "0_(assembly_and_lint_only;computes_no_row_value)"),
                                ("scope", "string_assembly_and_lint_of_this_file;fix-seat_edits:blindness_recodes,FC1-S11,FC1-27_verdict_rule,FC2-55_and_FC3-59_value_edits,PF_annotations,extra_lint;"
                                          "refix-seat_edits:R3_recodes_and_known_before_freeze,FC1-S11_labels,FC1-S12,FC2-S13,FC1-10,FC1-40,FC2-28,FC3-53_edits,head-row_codes,PF_annotations,extra_lint;"
                                          "refix-seat_round-2_edits:R4_recodes_and_known_before_freeze,FC1-S13,FC2-S14,SOURCE_lint_fields,PF-T3-1_k<=2_fields,extra_lint;"
                                          "refix-seat_round-3_edits:R5_recodes_and_known_before_freeze,FC1-S14,FC2-S15,head-row_search_fields,extra_lint;"
                                          "the_assembly_seat's_version_is_PF-A-5(ii);the_fix_seat's_version_is_PF-A-5(iv)"), ("touches", "none")]))
pfrows.append(row("PREFREEZE", [("id", "PF-A-4"), ("lane", "assembly"), ("script", SCR + "/final/fc_float_scan.py"), ("sha256_16", h16(FINAL + "/fc_float_scan.py")),
                                ("output", SCR + "/final/float_scan.out"), ("output_sha256_16", h16(FINAL + "/float_scan.out")), ("run", "python3_-I_-B"),
                                ("integer_only", "1"), ("measurement", "0"),
                                ("computational", "0_(lint_only;neither_this_scan_nor_the_two_inline_scans_computes_a_row_value)"),
                                ("scope", "token_scan_of_all_11_scripts_(3_assembly,8_lane)_for_float_division,float_literals_and_banned_modules:0_hits_each;"
                                          "re-run_by_the_fix_seat,by_the_refix_seat_and_by_the_refix_seat_rounds_2_and_3_on_each_re-edited_fc_assemble.py_(%s_the_assembly-seat_output_%s);"
                                          "two_earlier_inline_python3_-I_-B_-c_versions_of_the_same_scan_on_the_assembly_scripts_(text_not_retained,no_fingerprint)"
                                          % ("byte-identical_to" if h16(FINAL + "/float_scan.out") == h16(SUP + "/float_scan.assembly-seat.out") else "DIFFERS_from",
                                             h16(SUP + "/float_scan.assembly-seat.out"))), ("touches", "none")]))
pfrows.append(row("PREFREEZE", [("id", "PF-A-5"), ("lane", "assembly"),
                                ("script", "superseded_runs_of_fc_assemble.py:(i)_two_development_runs,text_not_retained;"
                                           "(ii)_the_assembly_seat's_final_version,kept_as_" + SCR + "/final/superseded/fc_assemble.assembly-seat.py"),
                                ("sha256_16", "(i)_not_retained;(ii)_" + h16(SUP + "/fc_assemble.assembly-seat.py")),
                                ("output", "(i)_one_crashed_before_writing(KeyError),one_wrote_a_file_since_overwritten;"
                                           "(ii)_the_HBP_before_the_fix_seat,kept_as_" + SCR + "/final/superseded/PREDICTION-FINITE-CONTINUOUS-20261109.assembly-seat.hbp"),
                                ("output_sha256_16", "(i)_not_retained;(ii)_" + h16(SUP + "/PREDICTION-FINITE-CONTINUOUS-20261109.assembly-seat.hbp")),
                                ("measurement", "0"), ("computational", "0_(assembly_and_lint_only;computes_no_row_value)"),
                                ("scope", "same_assembly_and_lint;(i)_differ_in_FC3-00_field_names,per-row_asm_texts,value_edits_applied_programmatically;"
                                          "(ii)_differs_from_PF-A-3_only_by_the_fix-seat_edits;"
                                          "(iii)_four_fix-seat_development_runs_of_the_edited_script,text_not_retained,outputs_overwritten:"
                                          "script_sha256_16_838ffe93f207f4cf,94b50edcf368c524,d50897a18d5f5794,de8d7914b29c09af;"
                                          "HBP_sha256_16_0d6e84f12a69af26,c074579f2b7ce129,8409391fea0a6f1e,43db4f3141d120a1;"
                                          "the_second_and_third_failed_lint_(a_dropped_space_merged_two_row_ids_in_the_weak_list);"
                                          "(iv)_the_fix_seat's_final_version_(script_" + h16(SUP3 + "/fc_assemble.py") + ",HBP_" + h16(SUP3 + "/" + OUTNAME) + "),kept_in_" + SCR + "/final/superseded-r3-1/;"
                                          "(v)_refix-seat_development_runs_of_the_re-edited_script,outputs_overwritten:" + R3DEV + ";"
                                          "(vi)_the_refix_seat's_final_version_(script_" + h16(SUP4 + "/fc_assemble.py") + ",HBP_" + h16(SUP4 + "/" + OUTNAME) + "),kept_in_" + SCR + "/final/superseded-r3-2/;"
                                          "(vii)_refix-seat_round-2_development_runs_in_a_mirror_tree_(" + SCR + "/refix-r3-2/mirror),outputs_kept_there_or_overwritten:" + R4DEV + ";"
                                          "(viii)_the_refix_seat_round-2_final_version_(script_" + h16(SUP5 + "/fc_assemble.py") + ",HBP_" + h16(SUP5 + "/" + OUTNAME) + "),kept_in_" + SCR + "/final/superseded-r3-3/;"
                                          "(ix)_refix-seat_round-3_development_runs_in_a_mirror_tree_(" + SCR + "/refix-r4/mirror),outputs_kept_there_or_overwritten:" + R5DEV), ("touches", "none")]))
pfrows.append(row("PREFREEZE", [("id", "PF-A-0"), ("lane", "assembly"), ("script", "none_(hand_plausibility_arithmetic)"), ("measurement", "0"),
                                ("scope", "leading_gap-term_estimates_of_three_T2_descents_(2T,Dic4,Z6_10%)_and_by-hand_spectra_of_Gamma_V,Gamma_V+Gamma_H;no_exact_curve;no_row_value_changed"), ("touches", "none")]))
out += pfrows
text = "\n".join(out) + "\n"
open(FINAL + "/" + OUTNAME, "w").write(text)

# ------------------------------------------------------------------ lint
errs = []
lines = text.split("\n")[:-1]


def kset(scope):
    ks = set()
    for m in re.finditer(r"k=(\d+)(?:\.\.(\d+))?((?:,\d+)*)", scope):
        a = int(m.group(1))
        ks.update(range(a, int(m.group(2)) + 1) if m.group(2) else [a])
        ks.update(int(x) for x in m.group(3).split(",") if x)
    return ks



ids = set()
declared = {"PF-T1-1", "PF-T1-2", "PF-T1-3", "PF-T2-1", "PF-T2-2", "PF-T3-1", "PF-T3-2", "PF-A-2", "none"}
BADF = {"", "as_not_met", "same", "such a law", "such a subgroup", "n/a", "as not met"}
for ln in lines:
    if not ln.endswith("|json=0"):
        errs.append("no_json0:" + ln[:40])
    f = ln.split("|")
    if any("=" not in x for x in f[1:]):
        errs.append("field_without_equals:" + ln[:40])
    d = dict(x.split("=", 1) for x in f[1:])
    if "id" in d:
        if d["id"] in ids:
            errs.append("dup_id:" + d["id"])
        ids.add(d["id"])
    if f[0] == "PREDICT":
        for k in ("id", "src", "test", "part", "scope", "quantity", "value", "tag", "blind", "prefreeze", "met_if", "not_met_if", "falsifier"):
            if not d.get(k, "").strip():
                errs.append("missing_%s:%s" % (k, d.get("id")))
        if d["tag"] not in ("DERIVED", "REPORTED", "CONJECTURE", "OPEN"):
            errs.append("bad_tag:" + d["id"])
        if d["tag"] == "OPEN":
            if not (d["met_if"].startswith("UNSCORED") and d["falsifier"].startswith("none_by_design")):
                errs.append("open_row_not_unscored:" + d["id"])
        else:
            if d["falsifier"].strip().lower() in BADF or d["met_if"].strip().lower() in ("n/a", "") or d["not_met_if"].strip().lower() in ("n/a", ""):
                errs.append("verdict_or_falsifier_not_reachable:" + d["id"])
        for p in d["prefreeze"].split(","):
            if p not in declared:
                errs.append("undeclared_prefreeze:%s:%s" % (d["id"], p))
        if d["value"] != srcvals[d["src"]] and "value_edited" not in d.get("asm", "") + d.get("fix", ""):
            errs.append("value_changed_without_asm_or_fix:" + d["id"])
        if d["blind"] not in BLS:
            errs.append("bad_blind:" + d["id"])
        if d["blind"] == "0" and d["known_before_freeze"] == "none" and d["prefreeze"] == "none":
            errs.append("control_without_source:" + d["id"])
        if "PF-T2-2" in d["prefreeze"].split(",") and d["blind"] != "weak" and not d["known_before_freeze"].startswith("exact_pre-freeze_value:"):
            errs.append("tool_row_not_weak:" + d["id"])
        if d["blind"] in ("0", "partial") and d["known_before_freeze"] == "none" and d["prefreeze"] == "none":
            errs.append("known_part_unstated:" + d["id"])
        if "S11_" in d["known_before_freeze"] and d["test"] != "FC1":
            errs.append("S11_outside_FC1:" + d["id"])
        if d["known_before_freeze"].startswith("exact_pre-freeze_value:") and d["blind"] not in ("0", "partial"):
            errs.append("exact_prefreeze_value_but_blind:" + d["id"])
        if "PF-T3-1" in d["prefreeze"].split(",") and d["blind"] == "1" and min(kset(d["scope"]) or [99]) <= 2:
            errs.append("PF-T3-1_row_with_k<=2_in_scope_coded_blind:" + d["id"])
        if d["blind"] == "1" and re.search(r"(at_r=\d|_r=9|r=9_|interval)", d["known_before_freeze"]):
            errs.append("finite-r_record_but_blind:" + d["id"])
        if d["quantity"] != srcquant[d["src"]] and "quantity_edited" not in d.get("fix", ""):
            errs.append("quantity_changed_without_fix:" + d["id"])
for ln in lines:
    if re.search(r"\b(he|his|him)\b", ln, re.I):
        errs.append("pronoun:" + ln[:60])
PFRE = re.compile(r"PF-(?:T[123]|A)-\d+")
srcl = {}
k12_exempt = set()
for ln in lines:
    f = ln.split("|")
    d = dict(x.split("=", 1) for x in f[1:] if "=" in x)
    if f[0] == "SOURCE":
        for k in SRCLINT:
            for x in d.get(k, "").split(","):
                if x:
                    srcl.setdefault(x, []).append((k, d["id"]))
    if f[0] == "PREFREEZE" and d.get("id") == "PF-T3-1":
        k12_exempt = set(re.findall(r"FC3-\d+", d.get("blind_k12_exempt", "")))
for ln in lines:
    f = ln.split("|")
    if f[0] != "PREDICT":
        continue
    d = dict(x.split("=", 1) for x in f[1:])
    for p in set(PFRE.findall(d["known_before_freeze"])):
        if p not in d["prefreeze"].split(","):
            errs.append("known_names_prefreeze_run_not_listed:%s:%s" % (d["id"], p))
    for k, sid in srcl.get(d["id"], []):
        if sid not in d["known_before_freeze"]:
            errs.append("source_lists_row_but_known_does_not_cite_it:%s:%s" % (d["id"], sid))
        if k == "gives_exact" and d["blind"] != "0":
            errs.append("source_gives_exact_value_but_not_control:%s:%s" % (d["id"], sid))
        if k == "gives_instances" and d["blind"] in ("1", "weak", "na"):
            errs.append("source_lists_instance_but_blind:%s:%s" % (d["id"], sid))
    if d["test"] == "FC3" and d["blind"] == "1" and min(kset(d["scope"]) or [99]) <= 2 and d["id"] not in k12_exempt:
        errs.append("FC3_row_with_k<=2_in_scope_blind_without_PF-T3-1_exemption:" + d["id"])
for x in srcl:
    if x not in ids:
        errs.append("source_lists_unknown_row:" + x)
for x in k12_exempt:
    if x not in ids:
        errs.append("k12_exempt_unknown_row:" + x)
hd = dict(x.split("=", 1) for x in lines[0].split("|")[1:])
for k in ("search_rounds", "search_cutoff", "late_record_rule"):
    if not hd.get(k, "").strip():
        errs.append("head_row_missing_" + k)
seq_ok = all(dict(f)["id"] == "%s-%02d" % (t, i + 1) for t in preds for i, f in enumerate(preds[t]))
if not seq_ok:
    errs.append("ids_not_sequential")
print("LINT|lines=%d|predict_rows=%d|errors=%d|json=0" % (len(lines), len(allp), len(errs)))
for e in errs:
    print("ERR|" + e)
print(row("SUMMARY", [("by_tag", cnt(allp, "tag", TAGS)), ("by_test", per), ("by_blind", cnt(allp, "blind", BLS))]))
