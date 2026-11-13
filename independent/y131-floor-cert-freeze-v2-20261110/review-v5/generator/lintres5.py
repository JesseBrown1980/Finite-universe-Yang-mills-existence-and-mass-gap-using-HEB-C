# Fourth correction round. Writes final/tools/lint_result.txt of the v2 folder: the real result of the unchanged lint tool on the exported staged set.
import re, collections
W = "/root/floor-v5/"
P = "/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/"
L = [l for l in open(W + "lint_export.txt").read().split("\n") if l]
T = [l for l in open(W + "lint_tree.txt").read().split("\n") if l]
head = [l for l in L if l.startswith("LINT|")]
res = [l for l in L if l.startswith("LINT_RESULT|")]
err = [l for l in L if l.startswith("ERROR|")]
assert len(head) == 1 and len(res) == 1 and res[0] == "LINT_RESULT|errors=%d" % len(err), (len(head), res, len(err))
c = collections.Counter(); other = []
for l in err:
    if "no such file" in l: c["files_entry_names_a_file_absent_from_the_commit"] += 1
    elif "is not an existing top-level work/ dir" in l: c["complete_names_a_seat_folder_absent_from_the_commit"] += 1
    elif "named file is" in l and "row says" in l and ("final/tools/floor_eval.py" in l or "final/tools/run_floor.sh" in l): c["row_116_gives_the_fingerprints_the_launcher_and_the_evaluator_had_at_3b91d1a0"] += 1
    elif "named file is" in l and "row says" in l: c["historical_row_gives_the_version_1_fingerprint_of_a_file_repaired_in_version_2"] += 1
    elif "PIN path unreadable work/design/rs/target/release/floorcert" in l: c["row_016_binary_is_rebuilt_and_stays_out_of_the_commit"] += 1
    elif "PIN path unreadable ../ym137" in l: c["row_034_path_lies_outside_this_folder"] += 1
    else: c["other"] += 1; other.append(l)
why = {
 "files_entry_names_a_file_absent_from_the_commit": "rows 085-109 name files of the seat folders (critic, verify, refix runs) that version 1 never committed; review-v1/E3-PROVENANCE.hbp lists each with its provenance; none was recreated",
 "complete_names_a_seat_folder_absent_from_the_commit": "the complete= fields of the same rows name those folders",
 "historical_row_gives_the_version_1_fingerprint_of_a_file_repaired_in_version_2": "rows 085-109 are kept byte-identical and state the fingerprints the files had when those rows were written; main.rs, gate_required.sh and r_scan.sh carry the version 2 repairs (rows 013 020 113)",
 "row_034_path_lies_outside_this_folder": "the pinned amplitude record is at commit 5e70e9dc02d6ed32fe9a94d03a2c3a77587ff9af; a byte copy is carried at final/link/ and the pin checks of run_floor.sh read that copy; the lint tool reads the literal path only",
 "row_016_binary_is_rebuilt_and_stays_out_of_the_commit": "the pin-free binary is built from the pinned source (row 016); the build tree, where it exists, gives one error fewer",
 "row_116_gives_the_fingerprints_the_launcher_and_the_evaluator_had_at_3b91d1a0": "row 116 is kept byte-identical to 3b91d1a0 and names run_floor.sh and floor_eval.py as they were when it was written; the later correction rounds change both (rows 114 115 124 130 136 141)",
 "other": "see the lines below"}
o = [head[0], res[0],
     "# Real result of final/tools/lint_hbp.py (unchanged, sha256 in the LINT line) on the version 2 record, run on an export of the staged file set, 2026-11-11 (fourth correction round). The build tree gives: " + [l for l in T if l.startswith("LINT_RESULT|")][0] + "."]
for k, v in sorted(c.items(), key=lambda x: -x[1]):
    o.append("LINT_CLASS|errors=%d|class=%s|why=%s" % (v, k, why[k]))
o.append("# Version 1 printed errors=0 in the seat's scratch tree; on the version 1 commit the same tool gives errors=294 (review-v1/lint_committed.out). The tool was left as it is.")
o.append("# Every ERROR line follows.")
o += err
open(P + "final/tools/lint_result.txt", "w", newline="\n").write("\n".join(o) + "\n")
print("\n".join(o[:8])[:1800]); print("other:", other[:5])
