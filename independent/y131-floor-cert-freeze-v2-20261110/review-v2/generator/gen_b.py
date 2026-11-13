# Builds revise_record2.py: the head of revise_record.py (rows 001-113, as committed at cfc57bef) with the
# correction-round edits below, followed by tail_b.py (rows 114-122).
import io
T = "/mnt/c/tmp/opus55/floor-v2/"
src = io.open(T + "revise_record.py", encoding="utf-8", newline="").read().replace("\r\n", "\n")
cut = src.index("# rows 114-117 (launcher); the text of rehearsal-v2/rev_rows.py, inlined")
h = src[:cut]
def rep(a, b):
    global h
    assert h.count(a) == 1, (h.count(a), a[:70])
    h = h.replace(a, b)
rep("# Version 2 revision of the prediction record. Exact-string edits of the v1 text, new DISCLOSE rows 110-114, new END counts.",
    "# Version 2 revision of the prediction record, correction round. Exact-string edits of the v1 text, new rows 110-122, new END counts.")
rep('''adds rows 110-118; rows 006 007 008 keep''', '''adds rows 110-122; rows 006 007 008 keep''')
rep('''was computed for version 2.\\n")''', '''was computed for version 2.\\n"
    "# CORRECTION ROUND (2026-11-10, same seat): one commit on top of the first version 2 commit cfc57befadcb61fb36b992af841941adaecd3fd0. It applies the reviewer's rulings and the findings of the separate verifier seat to the launcher and its evaluator (rows 114-117 and 119-122): the launcher runs private hashed copies of the gate and verifier tools, and a completed process at or over 2097152 kB gives CERTIFICATE=FAIL with RESOURCE_LIMIT_EXCEEDED and no fallback. The Rust source, the binary hash of row 016 and the 16 PREDICT rows are byte-identical to that commit. The launcher's last line reads FLOOR_RUN|CERTIFICATE=...|PREDICTION=...|DECISION=...|GAMMA=...|UPPER_BOUND=...|...|HASHES=...; the r = 9 mode starts only with the token --launch-r9 and stays on HOLD.\\n")''')
rep('"the_run_is_launched_by_the_single_command_bash_final/tools/run_floor.sh_(rows_114_115_116);',
    '"the_run_is_launched_by_the_single_command_bash_final/tools/run_floor.sh_--launch-r9_(rows_114_115_116);')
rep('"run_floor.sh_ends_with_FLOOR_RUN:result=FAIL,_no_gamma_and_zero_accepted_certificates_on_any_REQUIRED_failure;_it_reads_the_one_rerun_of_this_row_as_one_rerun_for_the_whole_run,_after_a_crash_(nonzero_exit_with_no_refusal_line),_with_identical_arguments,_both_attempts_logged;_a_refusal_or_a_time_limit_gets_no_rerun_(row_116)"',
    '"run_floor.sh_ends_with_FLOOR_RUN:CERTIFICATE=FAIL,_GAMMA=NONE,_UPPER_BOUND=NONE_and_zero_accepted_certificates_on_any_REQUIRED_or_integrity_failure;_it_reads_the_one_rerun_of_this_row_as_one_rerun_for_the_whole_run,_after_a_crash_(nonzero_exit_with_no_refusal_line),_with_identical_arguments,_both_attempts_logged;_a_refusal_gets_no_rerun;_a_command_ended_by_the_time_limit_(timeout_exit_124,_or_exit_137_from_the_KILL_that_follows_once_the_limit_has_elapsed)_is_a_time_limit_and_gets_no_rerun_(row_116)"')
rep('''_(sha256_equal_to_row_034's_value)"''',
    '''_(sha256_equal_to_row_034's_value);_a_byte_copy_of_it_is_carried_at_final/link/PREDICT-S3-3X4-R9-WILSON-FESHBACH-AMPLITUDE-20261109.hbp_and_the_launcher's_pin_checks_read_that_copy_when_the_literal_path_is_absent_(rows_116_119)"''')
tail = io.open(T + "tail_b.py", encoding="utf-8", newline="").read().replace("\r\n", "\n")
io.open(T + "revise_record2.py", "w", encoding="utf-8", newline="\n").write(h + tail)
print("revise_record2.py written", len(h), len(tail))
