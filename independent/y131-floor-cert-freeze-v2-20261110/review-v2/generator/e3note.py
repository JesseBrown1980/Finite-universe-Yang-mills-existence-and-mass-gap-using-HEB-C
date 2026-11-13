import sys
p = sys.argv[1]
ls = open(p, encoding="utf-8", newline="").read().split("\n")
assert ls[-1] == "" and ls[-2].startswith("E3_END|") and "\r" not in "".join(ls)
note = ("E3_NOTE|id=F8|sha16=8221ac66be71558c|source=finding_8_of_the_version_2_verifier_(review-v2/VERIFY-FLOOR-FREEZE-V2.hbp)"
        "|statement=a_file_with_this_fingerprint,_the_5_bytes_DONE_and_one_line_feed,_is_in_the_local_repository_history_at_reviews/opus55-gl159-refute-20261110/indep/BATCH_DONE_of_commit_2e4e8cb;"
        "_the_two_absent_paths_that_carry_this_fingerprint,_work/verify1_1/v2/repro2.done_and_work/verify1_1/v2/shape3_m11/done,_keep_provenance=not_established_and_content_reproduced=0:"
        "_the_match_is_one_of_content_only,_a_5-byte_marker_at_another_path_written_by_another_seat,_and_the_history_of_the_two_named_files_stays_open;_the_counts_of_the_E3_END_line_are_unchanged"
        "|added=correction_round_2026-11-10|json=0")
ls.insert(len(ls) - 2, note)
open(p, "w", encoding="utf-8", newline="\n").write("\n".join(ls))
