# Version 2 revision of the prediction record. Exact-string edits of the v1 text, new DISCLOSE rows 110-114, new END counts.
import hashlib, os, re, sys
R = "/root/floor-v2/repo/independent/"
V1 = R + "y131-floor-cert-freeze-20261110/"
V2 = R + "y131-floor-cert-freeze-v2-20261110/"
NAME = "final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp"
s = open(V1 + NAME, "rb").read().decode("utf-8")
assert hashlib.sha256(s.encode()).hexdigest() == "d06ff237f55a762e7c50087d98a757ed366e749f6a736c9c1793f495efd84041"

def sha(rel):
    return hashlib.sha256(open(V2 + rel, "rb").read()).hexdigest()
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:90])
    s = s.replace(old, new)

MAIN, BIN, GATE, RSCAN = sha("work/design/rs/src/main.rs"), sha("work/design/rs/target/release/floorcert"), sha("work/design/gate_required.sh"), sha("final/tools/r_scan.sh")
MAIN1 = "7824ed780aa7f15ef5da8b94e44826e1be218734e8313578845effb33ad68900"
BIN1 = "0432b8265b88921e0070592cd996571497511e33584ce5fedc281a28bd358709"
GATE1 = "13a92ab7562dc8a3e155d883988cadc87764bc59815c59c99a916089f50bf484"
RSCAN1 = "9ea61588095137270ba0ba37000d9cd70d4cac9b4c6bb119396af5efa2fb0d24"
assert sha("work/design/rs/Cargo.toml").startswith("63026f70") and sha("work/design/rs/Cargo.lock").startswith("964f252c")
V1C = "e74d8a46e86034096fd9c9231c87f594f17a93bf"
P1 = "d06ff237f55a762e7c50087d98a757ed366e749f6a736c9c1793f495efd84041"

# measured values read from the receipts
g = open(V2 + "review-v1/regression-v2/honest_m11_r21_2_gate.txt").read()
MEM2 = re.search(r"MEM\|(\d+)kB", g).group(1)
assert "GATE_REQUIRED|PASS" in g
p2 = open(V2 + "review-v1/regression-v2/part2.log").read()
assert "gate11_rc=0" in p2 and "rowhash11_rc=0 dir_exists=1" in p2 and "RUN11_exists_before=0" in p2
PK_RH = re.search(r"PEAK_RSS\|kB=(\d+)\|exit=0\|wall_ms=(\d+)", open(V2 + "review-v1/regression-v2/e1_m11_rowhash_absent_dir.txt").read()).group(1)
PK_W = re.search(r"PEAK_RSS\|kB=(\d+)\|exit=0", open(V2 + "review-v1/regression-v2/honest_m11_r21_2_writer.txt").read()).group(1)
e3 = open(V2 + "review-v1/E3-PROVENANCE.hbp").read().strip().split("\n")[-1]
E3 = dict(x.split("=") for x in e3.split("|")[1:])

# ---- header
rep("Paths are relative to scratchpad/floor/ unless they start with ../.",
    "Paths are relative to the package root (the folder that holds final/ and work/, at any absolute location; in version 1 it was scratchpad/floor/) unless they start with ../.")
rep("this file is authoritative.\n",
    "this file is authoritative.\n"
    "# VERSION 2 (2026-11-10, local build seat, Claude Opus 5.5). This file follows an operational review of version 1, the freeze commit " + V1C + " (prediction sha256 " + P1 + "), which stays unchanged as the historical prediction-first record. Version 2 carries the blind history of version 1 and adds none: the near-9 critic run of row 093 stays disclosed, and rows 110-114 disclose the review, its errata E1-E5 and everything run for version 2.\n"
    "# Version 2 changes rows 001 003 006 007 008 009 010 013 016 020 070 and adds rows 110-118; rows 006 007 008 keep every version 1 byte and gain one v2_launch field; the other 98 rows are byte-identical to version 1 (review-v1/ROW-COMPARE-V1-V2.hbp). Every PREDICT row keeps its value, met_if, not_met_if and falsifier; row 070 changes one memory figure in its basis field. No r = 9 value and no value at r within 1 of 9 was computed for version 2.\n")

# ---- row 001
rep("(row_108)|met_if=the_m0_11_step_is_run_first",
    "(row_108)|v2_dir_sequence=MEASURED_2026-11-10_with_the_v2_binary_of_row_016:_rowhash_with_an_absent_--dir_exits_0,_creates_the_directory_and_writes_the_keys_file_(m0_7_and_m0_11),_and_cert_then_reuses_that_directory_with_KEYS:loaded_and_no_writer_ENUM_line_(row_112);_the_v1_binary_exits_101_on_an_absent_--dir_(erratum_E1,_row_110);_how_the_dry-run_of_row_108_obtained_its_directory_is_open,_its_files_are_absent_from_the_v1_commit_(row_113)|met_if=the_m0_11_step_is_run_first")
# ---- row 003
rep("quantity=vector_and_outer_stopping_rule|value=FIX-1_code_unchanged|",
    "quantity=vector_and_outer_stopping_rule|value=FIX-1_rule_unchanged_in_the_v2_source_of_row_013|")
rep("(no_code_change_after_FIX-1)|tag=REQUIRED|",
    "(no_code_change_after_FIX-1)|v2=the_v2_source_of_row_013_rewrites_the_22_clippy_1.81_findings_and_makes_rowhash_create_its_--dir_(row_111);_the_rule_of_this_row_and_the_solver's_integer_results_are_the_FIX-1_ones:_every_certificate_of_the_v2_regression_is_byte-identical_to_its_FIX-1_pin_(row_112)|tag=REQUIRED|")
# ---- row 009
rep("(absolute_paths_under_scratchpad/floor/;_work/run9/target_does_not_exist_before_this_build)",
    "(CARGO_TARGET_DIR_is_given_as_the_absolute_path_of_work/run9/target_under_the_package_root,_wherever_the_package_root_is;_work/run9/target_does_not_exist_before_this_build)")
# ---- row 010
rep("quantity=layout_and_pin_check|value=the_FIX-1_paths|rule=gate_required.sh_hard-codes_D=scratchpad/floor/work/design_and_pins_py/cert_gate.py_by_sha256;_the_r9_run_therefore_uses_byte-identical_files_at_those_paths;",
    "quantity=layout_and_pin_check|value=the_package-relative_paths|rule=gate_required.sh_(v2,_row_020)_takes_D_from_its_own_location,_work/design_under_the_package_root_at_any_absolute_location,_and_pins_py/cert_gate.py_by_sha256;_the_r9_run_therefore_uses_byte-identical_files_at_the_pinned_relative_paths;")
# ---- row 013
rep("value=" + MAIN1 + "|role=floorcert_source_FIX-1|",
    "value=" + MAIN + "|role=floorcert_source_V2_(the_FIX-1_solver;_rowhash_creates_its_--dir;_the_22_clippy_1.81_findings_rewritten,_row_111)|v1_value=" + MAIN1 + "|")
# ---- row 016
rep("path=work/design/rs/target/release/floorcert|value=" + BIN1 + "|", "path=work/design/rs/target/release/floorcert|value=" + BIN + "|v1_value=" + BIN1 + "|")
# ---- row 020
rep("value=" + GATE1 + "|role=required-gate_driver_pins_row_019|",
    "value=" + GATE + "|role=required-gate_driver_pins_row_019;_v2:_D_is_the_directory_that_holds_the_script|v1_value=" + GATE1 + "|")
# ---- row 070 (basis field only)
rep("verifier_MEM_403336kB_at_m0_11_and_733_MB_at_m0_12_(FIX-1)",
    "verifier_MEM_403696kB_at_m0_11_(the_pinned_FIX-1_receipt_of_row_030;_version_1_wrote_403336kB_here,_the_figure_row_105_reports_for_the_f_6,5,4,3_file,_erratum_E4)_and_733_MB_at_m0_12_(FIX-1)")

# ---- launcher fields (added scope): rows 001 006 007 008 keep their bytes and gain one field before tag=
DRV, EVL = sha("final/tools/run_floor.sh"), sha("final/tools/floor_eval.py")
def addfield(rid, text):
    global s
    ls = s.split("\n")
    hit = [i for i, l in enumerate(ls) if re.match(r"^[A-Z_]+\|id=" + rid + r"\|", l)]
    assert len(hit) == 1 and ls[hit[0]].count("|tag=") == 1 and " " not in text
    ls[hit[0]] = ls[hit[0]].replace("|tag=", "|v2_launch=" + text + "|tag=")
    s = "\n".join(ls)
addfield("001", "the_run_is_launched_by_the_single_command_bash_final/tools/run_floor.sh_(rows_114_115_116);_the_commands_of_this_row_are_what_that_launcher_executes_at_m0_11,_with_FB=work/run9/target/release/floorcert,_RUN11=work/run9/RUN11,_PRED=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp_and_logs_under_work/run9/log,_all_relative_to_the_package_root;_work/run9_is_absent_before_the_launch")
addfield("006", "run_floor.sh_evaluates_run_iff_and_not_run_if_of_this_row_after_the_m0_11_step_in_exact_rational_arithmetic_on_verifier-accepted_certificates_only,_prints_a_DECISION_line_with_G_max,_g0_and_U_all,_and_then_executes_the_commands_of_this_row_at_m0_12_in_work/run9/RUN12_or_stops_(row_116)")
addfield("007", "run_floor.sh_evaluates_this_row_after_the_m0_12_step_the_same_way,_runs_the_prerequisite_lines_(1)_(2)_(3)_in_work/run9/RUN13_before_the_m0_13_cert_command,_stops_with_the_comparison_OPEN_when_the_prerequisite_is_unmet,_and_stops_after_m0_13_(row_116)")
addfield("008", "run_floor.sh_ends_with_FLOOR_RUN:result=FAIL,_no_gamma_and_zero_accepted_certificates_on_any_REQUIRED_failure;_it_reads_the_one_rerun_of_this_row_as_one_rerun_for_the_whole_run,_after_a_crash_(nonzero_exit_with_no_refusal_line),_with_identical_arguments,_both_attempts_logged;_a_refusal_or_a_time_limit_gets_no_rerun_(row_116)")

# ---- new rows
def files(rels):
    return ",".join("%s@%s" % (r, sha(r)[:16]) for r in rels)
rv = "review-v1/"
ver_files = [rv + x for x in ["VERIFY-FLOOR-FREEZE.hbp", "VERIFY-FLOOR-FREEZE.hbp.sha256", "VERIFY-FLOOR-FREEZE.md", "VERIFY-FLOOR-FREEZE.md.sha256", "lint_committed.out", "nofloat_gate.out"]]
ver_files += sorted(rv + "scripts/" + x for x in os.listdir(V2 + rv + "scripts"))
rg = rv + "regression-v2/"
reg_files = sorted(rg + x for x in os.listdir(V2 + rg))
src_files = [rg + x for x in ["clippy_v1_source_22_errors.txt", "clippy_v2.txt", "build_v2.txt", "repro_build.log", "patch_main.py", "fix_scripts.py", "build.sh", "revise_record.py", "compare.py", "e3d.py", "notes.py"]]
run_files = [x for x in reg_files if x not in src_files]
HV = sha(rv + "VERIFY-FLOOR-FREEZE.hbp"); MV = sha(rv + "VERIFY-FLOOR-FREEZE.md")

rows = []
rows.append("DISCLOSE|id=110|sec=version_2|quantity=v2_follows_an_operational_review_of_v1|value=version_2_of_the_freeze_e74d8a46"
 "|statement=this_file_is_version_2;_version_1_is_commit_" + V1C + "_on_branch_cloud-seat-floor-cert-freeze-20261110,_folder_independent/y131-floor-cert-freeze-20261110,_prediction_sha256_" + P1 + ",_kept_unchanged_as_the_historical_prediction-first_record;_version_2_was_written_after_the_local_verifier_seat_read_and_reran_version_1_(verdict_HOLD,_report_sha256_" + HV + "_and_" + MV + ",_copied_under_review-v1/);_version_2_carries_the_blind_history_of_version_1_and_claims_no_new_one;_the_near-9_critic_run_of_row_093_stays_disclosed;_the_verifier_seat_and_this_build_seat_ran_r-dependent_code_only_at_the_excluded_r_12_and_21/2"
 "|errata=E1_rows_001_006_007:_the_v1_rowhash_exits_101_on_an_absent_--dir,_repaired_in_the_source_(rows_013_111_112);_E2_rows_009_010_096:_gate_required.sh_and_r_scan.sh_held_one_absolute_scratch_path,_repaired_(rows_020_111);_E3_rows_085-109:_286_files=_entries_and_6_complete=_folders_are_absent_from_the_v1_commit,_listed_with_provenance_(row_113);_E4_row_070:_memory_figure,_corrected;_E5:_cargo_+1.81_clippy_-D_warnings_gave_22_errors_on_the_v1_source,_repaired_(row_111)"
 "|authorization=owner-relayed_reviewer_instruction_of_2026-11-10:_create_a_version_2_freeze_before_any_measurement,_preserve_e74d8a46_unchanged,_repair_E1-E5,_confirm_the_predicted_rows_and_rerun_the_verifier_before_any_calculation;_no_r9_run_before_the_corrected_freeze_passes"
 "|copy_note=review-v1/nofloat_gate.out_is_the_verifier's_file_with_its_one_CR_byte_removed_(original_sha256_815f0b5815a3bf692627d904a89fe5709b61ae1dc1a2d763a5d63e640d714ead);_the_other_named_files_are_byte_copies"
 "|left_out=the_verifier's_scripts/fztrace.py_(sha256_c8eea8eed03637590784f04d8502706cbcabc87e31521a5a12db424513610d02,_its_run-time_float_tracer)_and_scripts/fz_control.py_(sha256_2cb8fa1da7d0a424d4ba5a18ab0482cce3dce60580e9f3fce77a0fb3695344a5,_the_tracer's_positive_control)_stay_outside_this_commit:_they_test_for_float_values_by_design,_the_no-float_gate_reports_10_and_3_findings_in_them,_and_native/scripts/FLOAT-EVIDENCE.txt_stays_unchanged;_they_are_in_the_verifier's_folder_C:/tmp/opus55/floor-freeze-verify/scripts_on_the_owner's_machine"
 "|files=" + files(ver_files) +
 "|tag=REPORTED|met_if=every_file_named_in_files=_hashes_to_its_fingerprint_and_git_diff_e74d8a46_over_independent/y131-floor-cert-freeze-20261110_is_empty_at_the_v2_commit|not_met_if=a_named_file_differs_or_the_v1_folder_differs_from_e74d8a46|falsifier=a_nonempty_git_diff_of_the_v1_folder_against_e74d8a46_or_a_sha256sum_of_a_named_file_that_differs|json=0")

rows.append("DISCLOSE|id=111|sec=version_2|quantity=v2_source_and_script_repair|value=r-independent"
 "|statement=work/design/rs/src/main.rs_" + MAIN1 + "_to_" + MAIN + "_by_the_exact-string_edits_of_patch_main.py:_rowhash_calls_create_dir_all_on_its_--dir_before_the_keys_file_is_written;_cert_creates_no_directory_and_with_an_absent_--dir_exits_101_as_in_v1;_the_22_clippy_findings_are_rewritten_with_no_allow_attribute_anywhere:_iterator_forms_for_the_index_loops,_strip_prefix,_clamp,_the_unused_fmat_removed,_from_key_renamed_links_of_key,_a_slice_argument_for_gs_eigen,_and_the_long_argument_lists_of_dfs_fmat_x_certify_write_cert_max_t_carried_by_the_structs_Dfs_Problem_Solve_CertOut_and_one_Rat;_no_f32_f64_or_unsafe;_Cargo.toml_and_Cargo.lock_unchanged_(rows_014_015)"
 "|measured=cargo_+1.81_clippy_--release_--locked_--_-D_warnings_exit_0;_cargo_+1.81_build_--release_--locked_-j1_exit_0_with_0_warnings;_pin-free_binary_" + BIN1 + "_to_" + BIN + ";_a_pin-free_rebuild_in_a_separate_target_dir_is_byte-identical_(final/tools/repro_build.txt,_rustc_1.81.0_eeb90cda1)"
 "|scripts=work/design/gate_required.sh_" + GATE1 + "_to_" + GATE + "_and_final/tools/r_scan.sh_" + RSCAN1 + "_to_" + RSCAN + ":_each_takes_its_base_directory_from_its_own_location_(fix_scripts.py);_r_scan.sh_is_a_text_scan_(grep_of_.txt_and_.log_files_for_r_fields),_it_computes_nothing;_it_was_read_and_was_left_unrun_for_version_2,_because_10_of_its_11_listed_folders_hold_absent_files_(row_113);_final/tools/r_scan.txt_lint_controls.txt_and_lint_token_scan.txt_are_the_version_1_outputs,_unchanged"
 "|files=" + files(src_files) +
 "|tag=REPORTED|met_if=clippy_and_build_under_the_toolchain_named_in_measured=_exit_0_on_the_source_of_row_013_and_a_pin-free_rebuild_gives_the_value_of_row_016|not_met_if=a_clippy_error,_a_build_warning_or_another_binary_hash|falsifier=a_clippy_run_with_-D_warnings_under_that_toolchain_on_row_013's_source_with_a_nonzero_exit|json=0")

rows.append("DISCLOSE|id=112|sec=version_2|quantity=v2_regression_runs|value=r_12_and_r_21/2_and_r-independent"
 "|statement=every_floorcert_and_cert_gate.py_run_of_the_build_seat,_all_with_the_v2_pin-free_binary_" + BIN + "_and_--threads_2,_in_/root/floor-v2/reg_of_the_seat's_WSL_(outside_the_repository);_nothing_at_r_9_and_nothing_at_r_within_1_of_9;_the_binary's_own_r_policy_was_left_in_force"
 "|runs=(1)_selftest:_output_equal_to_the_FIX-1_ledger_entry_345f7197...;_(2)_rowhash_--m0_7_with_an_absent_--dir:_exit_0,_directory_created,_keys_file_equal_to_the_ledger's_core_keys_m7.bin;_(3)_cert_--m0_7_--r_12_--f_4,3,2,1_--write-cert_in_an_existing_directory:_certificate_byte-identical_to_the_ledger's_smoke_certificate_(sha256_6b0864111909134dde63be778bb986c706a6c280303ab90da14f5adc7e768823),_GATE_REQUIRED:PASS;_(4)_the_same_cert_in_the_directory_rowhash_made_in_(2):_KEYS:loaded,_the_same_certificate;_(5)_the_same_cert_with_an_absent_--dir:_exit_101_and_no_directory,_as_in_v1;_(6)_cert_--m0_6_--r_21/2_--f_4,3,2,1_--write-cert_--plant_all_--ub_993765/10000:_14_certificate_files,_14_of_14_byte-identical_to_the_ledger's_plants_m6_f4321_entries,_gate_verdicts_PASS_on_the_honest_file_and_on_P1b_(which_is_the_same_bytes)_and_REFUSE_on_the_12_others;_(7)_rowhash_--m0_11_under_peak_rss.py_with_an_absent_--dir:_exit_0,_directory_created,_rowhash_equal_to_row_028_and_keyshash_and_keys_file_equal_to_row_025,_PEAK_RSS_" + PK_RH + "kB;_(8)_cert_--m0_11_--r_21/2_--f_8,7,6,5,4_--write-cert_under_peak_rss.py_in_that_directory:_KEYS:loaded,_no_writer_ENUM_line,_certificate_byte-identical_to_the_pinned_one_(sha256_a217a469e1bb482226e0cb92a54fdb32ebd0b3ef5608892627da6ec0433effa5),_PEAK_RSS_" + PK_W + "kB;_(9)_gate_required.sh_on_that_certificate:_GATE_REQUIRED:PASS,_verifier_MEM_" + MEM2 + "kB;_(10)_tamper_test_on_a_copy_of_work/design_outside_the_package:_the_untampered_copy_passes_and_a_copy_with_one_edited_line_of_cert_gate.py_is_refused_by_the_sha256_pin_(exit_1);_the_package's_cert_gate.py_was_left_untouched"
 "|also_run=cargo_clippy_and_build_(row_111),_lint_hbp.py_on_the_version_1_text_in_the_v2_tree,_git_fetches_and_file_searches_(row_113);_none_r-dependent"
 "|files=" + files(run_files) +
 "|tag=REPORTED|met_if=a_rerun_of_these_commands_with_the_binary_of_row_016_reproduces_the_named_certificate_and_keys_hashes|not_met_if=a_certificate_or_keys_file_of_such_a_rerun_differs_from_its_FIX-1_pin|falsifier=a_v2_binary_run_at_r_12_or_r_21/2_whose_certificate_sha256_differs_from_the_work/design/out/fix1/LEDGER.txt_entry_of_the_same_name|json=0")

rows.append("DISCLOSE|id=113|sec=version_2|quantity=v2_provenance_of_the_absent_disclosed_files|value=" + E3["verified"] + "_verified_and_" + E3["not_established"] + "_not_established_of_" + E3["absent_paths"] + "_paths"
 "|statement=the_files=_fields_of_rows_085-109_name_" + E3["absent_paths"] + "_distinct_paths_(286_entries)_that_are_absent_from_the_v1_commit,_and_the_6_complete=_folders_work/critic2_verify1_0_verify1_1_refix2_verify2_0_verify2_1_are_absent;_review-v1/E3-PROVENANCE.hbp_lists_each_path_with_its_fingerprint_and_rows;_provenance=verified_(" + E3["verified"] + "_paths):_the_same_bytes_are_in_the_repository_history_at_the_path_named_there;_provenance=not_established_(" + E3["not_established"] + "_paths):_no_file_with_that_fingerprint_was_found_in_the_places_searched;_of_these,_" + E3["of_which_content_reproduced"] + "_fingerprints_were_reproduced_by_a_2026-11-10_rerun_on_this_machine_(bytes_confirmed,_history_of_the_original_file_open);_no_absent_file_was_recreated_or_back-filled"
 "|searched=every_blob_reachable_from_the_GitHub_branch_and_pull_heads_and_the_local_mirror_refs_(read-only_fetch),_and_the_file_trees_named_in_the_E3_SEARCH_lines_of_that_file;_the_cloud_seat's_scratch_machine_was_outside_reach"
 "|link_pin=the_file_of_row_034_(path_../ym137/...)_is_outside_this_folder;_the_same_bytes_are_at_independent/y137-amplitude-freeze-20261109/PREDICT-S3-3X4-R9-WILSON-FESHBACH-AMPLITUDE-20261109.hbp_of_commit_5e70e9dc02d6ed32fe9a94d03a2c3a77587ff9af_(sha256_equal_to_row_034's_value)"
 "|files=" + files([rv + "E3-PROVENANCE.hbp"]) +
 "|tag=REPORTED|met_if=every_path_marked_verified_in_review-v1/E3-PROVENANCE.hbp_has_its_sha256_at_the_named_repository_path|not_met_if=a_path_marked_verified_whose_named_blob_hashes_otherwise|falsifier=a_git_cat-file_of_a_named_blob_whose_sha256_differs_from_the_listed_one|json=0")

# rows 114-117 (launcher); the text of rehearsal-v2/rev_rows.py, inlined
# Rows 114-117 of the version 2 record (launcher). exec()'d by revise_record.py; uses its names.
PINTAIL = "|tag=REQUIRED|basis=MEASURED|met_if=sha256sum_at_run_time_equals_value|not_met_if=differs|falsifier=the_logged_pin_check_line_for_this_path_showing_another_hash|json=0"
rows.append("PIN|id=114|sec=launcher|quantity=sha256|path=final/tools/run_floor.sh|value=" + DRV +
 "|role=single_launcher_of_the_r9_run_(row_116):_pin_checks,_frozen_build,_rowhash_and_cert_under_peak_rss.py,_gate_required.sh_on_every_certificate,_the_decision_of_rows_006_007_012,_the_final_FLOOR_RUN_line_and_the_receipt;_bash;_it_computes_no_spectrum" + PINTAIL)
rows.append("PIN|id=115|sec=launcher|quantity=sha256|path=final/tools/floor_eval.py|value=" + EVL +
 "|role=evaluator_called_by_row_114:_reads_logs_and_certificates,_checks_the_PIN_path_rows,_evaluates_rows_006_007_012_in_exact_rational_arithmetic,_scores_rows_058-073_and_writes_the_receipt;_integers_and_integer_pairs_only" + PINTAIL)
rows.append("DISCLOSE|id=116|sec=version_2|quantity=v2_single_launcher|value=bash_final/tools/run_floor.sh"
 "|statement=the_r9_run_is_one_command,_bash_final/tools/run_floor.sh_[--freeze-commit_C],_from_any_working_directory;_every_path_comes_from_the_script's_own_location;_in_order_it_(1)_stops_unless_work/run9_is_absent;_(2)_takes_C_as_the_last_commit_that_touched_this_file_(or_the_argument)_and_stops_unless_the_blob_of_this_file_at_C_has_the_sha256_P_of_the_file_on_disk_and_the_tracked_files_of_the_folder_equal_the_commit;_(3)_checks_the_toolchain_lines_of_row_017;_(4)_rebuilds_the_pin-free_binary_of_row_016_when_it_is_absent;_(5)_pin_check_1_over_every_PIN_row_that_names_a_path,_reading_the_file_of_row_034_from_commit_5e70e9dc02d6ed32fe9a94d03a2c3a77587ff9af_when_the_literal_path_is_absent;_(6)_the_frozen_build_of_row_009;_(7)_pin_check_2;_(8)_per_step:_sha256sum_of_FB,_the_rowhash_command,_at_the_third_step_the_prerequisite_of_row_007,_the_cert_command_of_rows_001_006_007_with_no_other_flag,_gate_required.sh_on_every_cert_file_of_the_run_directory,_then_the_evaluator;_(9)_a_DECISION_line;_(10)_the_last_line_FLOOR_RUN:result=..._and_work/run9/FLOOR-RUN-RECEIPT.hbp_with_the_sha256_of_every_certificate,_log_and_keys_file;_each_program_runs_alone_under_a_21600_second_limit;_exit_0_PASS,_1_FAIL,_2_UNRESOLVED"
 "|decision=G(m)_is_the_largest_gamma_of_the_VERDICT:PASS_lines_of_the_certificates_of_step_m_and_exists_only_when_every_check_of_the_step_passed;_U(m)_is_the_smallest_of_the_writer's_ritz_upper_and_the_verifier's_RITZ_CLASS_VECTOR_over_those_certificates_plus_1/1000000,_as_the_header_defines_it;_the_state_is_ABOVE_when_max_G_GE_g0,_BELOW_FALSIFIED_H4_when_U_all_LT_g0,_UNDECIDED_otherwise,_by_integer_cross-multiplication;_the_next_step_runs_only_when_run_iff_(a)_of_row_006_or_007_holds_(UNDECIDED)_or_(b)_holds_(the_step_produced_no_certificate_after_a_crash_or_the_time_limit);_the_launcher_also_evaluates_U_from_the_verifier's_line_alone_and_stops_with_UNRESOLVED_and_the_words_HUMAN_READING_NEEDED_when_the_two_readings_of_U_give_different_states"
 "|result=PASS:_every_step_run_passed_every_check_and_the_state_is_ABOVE_or_BELOW_FALSIFIED_H4_(the_comparison_field_says_which;_PASS_states_that_the_run_is_complete_and_gated,_the_scores_of_rows_058-073_are_listed_beside_it);_FAIL:_a_pin_mismatch,_a_refusal_line_of_the_writer_or_the_verifier,_a_REQUIRED_check_that_failed,_a_certificate_file_the_writer_did_not_list,_a_contradiction_of_row_052;_then_gamma_cert=NONE_and_the_receipt_lists_zero_accepted_certificates_for_every_step_(row_008);_UNRESOLVED:_UNDECIDED_after_the_last_allowed_step,_the_prerequisite_of_row_007_unmet,_a_verifier_process_that_crashed_twice_or_ran_into_the_time_limit,_or_a_stop_before_the_first_command"
 "|checks_per_step=PEAK_RSS_line_present_with_exit_0_and_under_2097152_kB_for_rowhash_and_cert;_every_writer_and_verifier_GATE_line_PASS_and_the_named_gates_present;_rowhash_and_keyshash_equal_to_rows_025-029_and_equal_across_rowhash_step,_cert_command,_certificate_header_and_verifier;_the_counts_of_rows_043_044_047_051_055;_one_CERT_and_one_WROTE_line_per_f_word;_file_sha256_equal_to_the_WROTE_line_and_to_GATE_REQUIRED:cert_sha256;_gamma_equal_three_ways_(row_005);_min_slack_equal_(row_054);_gamma_LE_the_Ritz_bound_plus_1/1000000_(row_052);_verifier_MEM_under_2097152_kB;_the_verifier_sha256_of_row_019;_at_r_9_the_FREEZE_lines_with_C,_P_and_the_one_FB_hash_(rows_009_018)"
 "|readings_for_a_human_check=(a)_one_rerun_for_the_whole_run,_only_after_a_crash;_(b)_a_process_that_ends_normally_with_PEAK_RSS_or_MEM_at_or_over_2_GB_is_a_REQUIRED_failure_of_row_011_(FAIL),_while_a_process_killed_by_the_kernel_or_by_the_time_limit_is_the_operational_case_of_row_006_(b);_(c)_certificates_left_by_a_cert_command_that_crashed_are_moved_to_work/run9/aside_and_count_as_none;_(d)_a_step_with_an_operational_failure_leaves_PASS_reachable_at_a_later_step_and_is_named_in_operational_failures=;_(e)_PASS_covers_both_decided_states;_(f)_with_no_gated_certificate_rows_059-073_are_scored_NO_GATED_VALUE_and_row_058_NOT_MET;_(g)_row_070_is_scored_on_the_larger_of_the_rowhash_and_cert_PEAK_RSS_of_a_step;_(h)_on_a_time_limit_the_launcher_kills_processes_named_floorcert;_(i)_m0_13_has_no_pinned_row_hash:_three-way_equality_plus_the_keys_pin_of_row_027"
 "|not_yet_exercised=CONJECTURE_until_the_r9_run:_the_freeze-commit_lookup,_the_frozen_build,_pin_check_2,_the_FREEZE_line_checks_and_the_m0_12_and_m0_13_pins_are_code_that_only_the_default_mode_reaches;_the_rehearsals_of_row_117_reach_every_other_branch_they_name;_a_stop_in_those_parts_comes_before_the_first_r9_command_and_prints_FLOOR_RUN:result=..._with_stage=prelude"
 "|test_mode=--test-r_R_with_--test-m0,_--test-f,_--test-g0,_--test-out_and_the_injections_--test-plant,_--test-crash,_--test-hang,_--test-census_runs_the_same_chain_with_the_pin-free_binary_of_row_016;_the_launcher_refuses_R_within_1_of_9_before_anything_runs_and_the_binary's_r_policy_stays_in_force;_a_test_option_without_--test-r_stops_the_launcher"
 "|authorization=owner-relayed_added_scope_of_2026-11-10:_one_command_with_automatic_verification_and_the_conditional_fallback_of_rows_006_007;_fallback_decided_only_from_certified_rational_bounds;_PASS_requires_every_applicable_certificate_gate_and_integrity_gate;_execution_at_r_9_stays_on_HOLD"
 "|files=" + files(["final/tools/run_floor.sh", "final/tools/floor_eval.py"]) +
 "|tag=REPORTED|met_if=the_two_files_hash_to_rows_114_115_and_a_test-mode_rerun_at_an_excluded_r_reproduces_the_outcomes_of_row_117|not_met_if=another_hash_or_another_outcome|falsifier=a_test-mode_run_of_the_pinned_launcher_whose_FLOOR_RUN_line_differs_in_result_from_the_row_117_entry_with_the_same_arguments|json=0")
if os.environ.get("STAGE") == "2":
    rh = sorted("review-v1/rehearsal-v2/" + x for x in os.listdir(V2 + "review-v1/rehearsal-v2"))
    summ = open("/root/floor-v2/reh/SUMMARY.txt").read().strip().replace("\n", ";_")
    assert " " not in summ and "|" not in summ
    st1 = open("/root/floor-v2/reh/STAGE1.sha256").read().split()[0]
    body = ("|statement=test-mode_runs_of_the_pinned_launcher_(rows_114_115)_at_excluded_r_only,_with_the_pin-free_binary_of_row_016,_outside_the_repository_in_/root/floor-v2/reh;_no_default-mode_run_and_nothing_at_r_within_1_of_9;_they_ran_with_this_file_in_its_state_before_this_row_was_filled_(sha256_" + st1 + ",_named_in_each_receipt_and_kept_as_review-v1/rehearsal-v2/RECORD-AT-REHEARSAL.hbp);_this_file_differs_from_that_state_in_this_row_and_in_the_revise_record.py_fingerprint_of_row_118_only,_because_the_generator_was_then_rewritten_without_its_exec_line_for_the_no-float_gate,_with_the_same_output_rows;_before_them_the_seat_ran_development_runs_of_the_launcher_with_the_same_arguments_against_a_provisional_copy_of_this_file_and_overwrote_their_output"
            "|runs=" + summ + "|files=" + files(rh))
else:
    body = "|statement=PENDING:_stage_1_of_this_file,_written_before_the_rehearsals_ran"
rows.append("DISCLOSE|id=117|sec=version_2|quantity=v2_launcher_rehearsals|value=excluded_r_only" + body +
 "|tag=REPORTED|met_if=each_receipt_named_in_files=_ends_with_the_FLOOR_RUN_line_quoted_in_runs=|not_met_if=a_receipt_whose_last_line_differs|falsifier=a_named_receipt_whose_FLOOR_RUN_result_differs_from_runs=|json=0")
rows.append("DISCLOSE|id=118|sec=version_2|quantity=v2_record_revision_and_closing_steps|value=11_rows_revised_and_9_rows_added"
 "|statement=against_version_1_this_file_changes_header_line_6,_adds_2_header_lines,_revises_rows_001_(v2_dir_sequence_and_v2_launch_fields_added)_006_007_008_(one_v2_launch_field_added_to_each,_every_version_1_byte_kept)_003_(value_and_a_v2_field)_009_(path_wording)_010_(value_and_rule_wording)_013_016_020_(new_hashes,_v1_value_fields)_070_(one_memory_figure_in_basis),_adds_rows_110-118_and_updates_the_PREDICTION_END_counts;_the_other_98_rows_are_byte-identical;_the_commands_of_rows_006_and_007_refer_to_row_001_and_hold_as_written_with_the_v2_binary;_rows_006_007_008_gain_the_field_that_names_the_launcher,_as_the_owner-relayed_added_scope_asks;_the_15_PREDICT_rows_other_than_070_are_byte-identical_and_row_070_keeps_its_value,_met_if,_not_met_if_and_falsifier;_review-v1/ROW-COMPARE-V1-V2.hbp_gives_the_row-by-row_comparison"
 "|history_rows=rows_085-109_are_kept_byte-identical_as_the_version_1_disclosures;_their_program_and_files=_fields_quote_the_version_1_fingerprints_of_the_binary_and_of_gate_required.sh,_so_lint_hbp.py_reports_those_entries_as_differing_from_the_v2_files,_and_reports_the_absent_files_and_folders_of_row_113;_the_lint_tool_is_unchanged_and_its_real_result_on_this_file_is_in_final/tools/lint_result.txt,_with_the_error_count_and_the_reason_of_each_class"
 "|compile_in=the_order_of_version_1_is_kept:_this_file_is_committed_first;_C_is_the_40-hex_commit_that_carries_it_and_P_is_its_sha256;_the_frozen_binary_FB_is_built_after_that_commit_(row_009)_and_its_hash_is_recorded_at_run_time_(row_018);_row_016_pins_the_pin-free_binary"
 "|after_this_row=lint_hbp.py,_the_pin_check,_the_no-float_gate,_the_CR_count,_the_row_comparison_and_the_local_git_commit;_none_r-dependent;_this_file_cannot_carry_their_outputs_without_changing_its_own_sha256;_no_push_and_no_r9_run_by_this_seat"
 "|tag=REPORTED|met_if=review-v1/ROW-COMPARE-V1-V2.hbp_regenerated_from_the_two_committed_files_shows_98_rows_with_same_bytes_1_and_the_11_named_rows_with_same_bytes_0|not_met_if=another_row_differs_or_a_PREDICT_row's_value,_met_if,_not_met_if_or_falsifier_differs_from_version_1|falsifier=a_byte_comparison_of_the_two_committed_files_showing_a_changed_row_outside_001_003_006_007_008_009_010_013_016_020_070|json=0")

end_old = "PREDICTION_END|rows=109|FREEZE=12|PIN=23|REQUIRED=23|PREDICT=16|LINK=2|STATUS=9|DISCLOSE=24|DERIVED=2|CONJECTURE=15|REPORTED=32|OPEN=2|REQUIRED_TAG=58|"
end_new = "PREDICTION_END|rows=118|FREEZE=12|PIN=25|REQUIRED=23|PREDICT=16|LINK=2|STATUS=9|DISCLOSE=31|DERIVED=2|CONJECTURE=15|REPORTED=39|OPEN=2|REQUIRED_TAG=60|"
rep(end_old, "\n".join(rows) + "\n" + end_new)
for r in rows:
    assert " " not in r and "\t" not in r, r[:60]
assert "\r" not in s and all(ord(c) < 127 for c in s)
open(V2 + NAME, "wb").write(s.encode("utf-8"))
print("written", hashlib.sha256(s.encode()).hexdigest(), "MEM2", MEM2, "PK", PK_RH, PK_W, E3)
