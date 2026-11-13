# One-time patch of revise_record.py: launcher rows (added scope). Run once; it refuses a second run.
p = "/mnt/c/tmp/opus55/floor-v2/revise_record.py"
s = open(p, newline="").read().replace("\r\n", "\n")
assert "v2_launch" not in s
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)
rep("Version 2 changes rows 001 003 009 010 013 016 020 070 and adds rows 110-114; the other 101 rows are byte-identical",
    "Version 2 changes rows 001 003 006 007 008 009 010 013 016 020 070 and adds rows 110-118; rows 006 007 008 keep every version 1 byte and gain one v2_launch field; the other 98 rows are byte-identical")
rep("# ---- new rows\n", '''# ---- launcher fields (added scope): rows 001 006 007 008 keep their bytes and gain one field before tag=
DRV, EVL = sha("final/tools/run_floor.sh"), sha("final/tools/floor_eval.py")
def addfield(rid, text):
    global s
    ls = s.split("\\n")
    hit = [i for i, l in enumerate(ls) if re.match(r"^[A-Z_]+\\|id=" + rid + r"\\|", l)]
    assert len(hit) == 1 and ls[hit[0]].count("|tag=") == 1 and " " not in text
    ls[hit[0]] = ls[hit[0]].replace("|tag=", "|v2_launch=" + text + "|tag=")
    s = "\\n".join(ls)
addfield("001", "the_run_is_launched_by_the_single_command_bash_final/tools/run_floor.sh_(rows_114_115_116);_the_commands_of_this_row_are_what_that_launcher_executes_at_m0_11,_with_FB=work/run9/target/release/floorcert,_RUN11=work/run9/RUN11,_PRED=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp_and_logs_under_work/run9/log,_all_relative_to_the_package_root;_work/run9_is_absent_before_the_launch")
addfield("006", "run_floor.sh_evaluates_run_iff_and_not_run_if_of_this_row_after_the_m0_11_step_in_exact_rational_arithmetic_on_verifier-accepted_certificates_only,_prints_a_DECISION_line_with_G_max,_g0_and_U_all,_and_then_executes_the_commands_of_this_row_at_m0_12_in_work/run9/RUN12_or_stops_(row_116)")
addfield("007", "run_floor.sh_evaluates_this_row_after_the_m0_12_step_the_same_way,_runs_the_prerequisite_lines_(1)_(2)_(3)_in_work/run9/RUN13_before_the_m0_13_cert_command,_stops_with_the_comparison_OPEN_when_the_prerequisite_is_unmet,_and_stops_after_m0_13_(row_116)")
addfield("008", "run_floor.sh_ends_with_FLOOR_RUN:result=FAIL,_no_gamma_and_zero_accepted_certificates_on_any_REQUIRED_failure;_it_reads_the_one_rerun_of_this_row_as_one_rerun_for_the_whole_run,_after_a_crash_(nonzero_exit_with_no_refusal_line),_with_identical_arguments,_both_attempts_logged;_a_refusal_or_a_time_limit_gets_no_rerun_(row_116)")

# ---- new rows
''')
rep('rows.append("DISCLOSE|id=114|', 'exec(open("/mnt/c/tmp/opus55/floor-v2/rev_rows.py").read())\nrows.append("DISCLOSE|id=118|')
rep("value=8_rows_revised_and_5_rows_added", "value=11_rows_revised_and_9_rows_added")
rep("revises_rows_001_(v2_dir_sequence_field_added)", "revises_rows_001_(v2_dir_sequence_and_v2_launch_fields_added)_006_007_008_(one_v2_launch_field_added_to_each,_every_version_1_byte_kept)")
rep("adds_rows_110-114_and", "adds_rows_110-118_and")
rep("the_other_101_rows_are_byte-identical;_rows_006_and_007_keep_their_bytes_because_their_commands_refer_to_row_001_and_hold_as_written_with_the_v2_binary;",
    "the_other_98_rows_are_byte-identical;_the_commands_of_rows_006_and_007_refer_to_row_001_and_hold_as_written_with_the_v2_binary;_rows_006_007_008_gain_the_field_that_names_the_launcher,_as_the_owner-relayed_added_scope_asks;")
rep("shows_101_rows_with_same_bytes_1_and_the_8_named_rows_with_same_bytes_0", "shows_98_rows_with_same_bytes_1_and_the_11_named_rows_with_same_bytes_0")
rep("outside_001_003_009_010_013_016_020_070|json=0", "outside_001_003_006_007_008_009_010_013_016_020_070|json=0")
rep("rows=114|FREEZE=12|PIN=23|", "rows=118|FREEZE=12|PIN=25|")
rep("DISCLOSE=29|DERIVED=2|CONJECTURE=15|REPORTED=37|OPEN=2|REQUIRED_TAG=58|", "DISCLOSE=31|DERIVED=2|CONJECTURE=15|REPORTED=39|OPEN=2|REQUIRED_TAG=60|")
open(p, "w", newline="\n").write(s)
print("patched")
