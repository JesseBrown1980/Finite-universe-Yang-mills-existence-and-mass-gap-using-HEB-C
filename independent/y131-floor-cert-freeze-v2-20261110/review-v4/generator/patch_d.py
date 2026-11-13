# Third correction round: makes run_floor_d.sh and floor_eval_d.py from the files committed at 78c89c31.
# Every replacement must match exactly once.
import sys
D = sys.argv[1]
SRC = sys.argv[2]


def load(n):
    return open(SRC + "/" + n, "r", encoding="ascii", newline="").read()


def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:90])
    return s.replace(a, b)


# ------------------------------------------------------------------ launcher
s = load("run_floor.sh")
assert "\r" not in s
s = rep(s, "(version 2 freeze, second correction round).", "(version 2 freeze, third correction round).")
s = rep(s, "#               [--test-vexc IDX] [--test-census] [--test-limit-kb N] [--test-git-check]\n",
        "#               [--test-vexc IDX] [--test-census] [--test-limit-kb N] [--test-git-check]\n"
        "#               [--test-frozen-build [--freeze-commit C]]\n"
        "#               --test-frozen-build runs the freeze-commit lookup, the frozen build with the two compiled pins and\n"
        "#               pin check 2 exactly as the frozen run does, and then runs the rehearsal with that binary at R.\n")
s = rep(s, "# mount namespace of its own. Stage 2 hashes its own text (BASH_EXECUTION_STRING) against row 114.\n",
        "# mount namespace of its own. Stage 2 hashes its own text (BASH_EXECUTION_STRING) against row 114.\n"
        "# NAMESPACE (row 132). Stage 2 starts no work unless the mount namespace of its own process differs from the mount\n"
        "# namespace of its parent process and from that of process 1 and holds no shared or slave mount; entered directly,\n"
        "# without stage 1, it stops with NOT_STARTED (exit 4) before it mounts or writes anything. After the two tmpfs\n"
        "# mounts it reads the mount tables: both mounts must be listed for this process and absent for the parent process\n"
        "# and for process 1, or the run stops with NOT_STARTED. Only then does the run log say that the namespace is private.\n")
s = rep(s, "# run gate_required.sh on each published certificate (the RECHECK rows of the receipt give the command).\n",
        "# run final/tools/recheck_floor.py (row 131) on the receipt: it runs gate_required.sh on every certificate of the\n"
        "# RECHECK rows, takes the upper bound from its own verifier output alone and must reproduce the decision (row 133).\n")
# stage 2 namespace check, before anything else runs
s = rep(s, "[ \"$PATH\" = /usr/bin:/bin ] && [ \"$LANG\" = C ] || early_stop environment path_or_lang_differs_from_the_fixed_values\n",
        "[ \"$PATH\" = /usr/bin:/bin ] && [ \"$LANG\" = C ] || early_stop environment path_or_lang_differs_from_the_fixed_values\n"
        "# ---- the mount namespace (row 132): this process must sit in a mount namespace other than that of its parent\n"
        "# process and of process 1, with no shared or slave mount in it; a direct entry into stage 2 stops here\n"
        "NS_SELF=$(/usr/bin/readlink /proc/self/ns/mnt 2>/dev/null) || NS_SELF=\"\"\n"
        "NS_PARENT=$(/usr/bin/readlink \"/proc/$PPID/ns/mnt\" 2>/dev/null) || NS_PARENT=\"\"\n"
        "NS_INIT=$(/usr/bin/readlink /proc/1/ns/mnt 2>/dev/null) || NS_INIT=\"\"\n"
        "for v in \"$NS_SELF\" \"$NS_PARENT\" \"$NS_INIT\"; do\n"
        "  case \"$v\" in mnt:\\[[0-9]*\\]) ;; *) early_stop namespace a_mount_namespace_id_cannot_be_read;; esac\n"
        "done\n"
        "[ \"$NS_SELF\" != \"$NS_PARENT\" ] && [ \"$NS_SELF\" != \"$NS_INIT\" ] || early_stop namespace second_stage_entered_outside_a_private_mount_namespace\n"
        "/usr/bin/grep -Eq ' (shared|master|propagate_from):[0-9]+ ' /proc/self/mountinfo; [ $? -eq 1 ] || early_stop namespace mount_namespace_holds_a_shared_or_slave_mount\n")
s = rep(s, "    case \"$v\" in BASH_ENV|ENV|LD_*|PYTHON*) early_stop entry \"caller_environment_sets_$v\";; esac\n",
        "    case \"$v\" in BASH_ENV|ENV|LD_*|PYTHON*|BASHOPTS|SHELLOPTS|PS4|IFS|POSIXLY_CORRECT|BASH_COMPAT|BASH_XTRACEFD|BASH_LOADABLES_PATH|EXECIGNORE|GLOBIGNORE|CDPATH) early_stop entry \"caller_environment_sets_$v\";; esac\n")
s = rep(s, "C=\"\"; T_R=\"\"; T_PLANT=\"\"; T_CRASH=\"\"; T_HANG=\"\"; T_HARD=\"\"; T_VEXC=\"\"; T_LIM=\"\"; CENSUS=0; T_ANY=0; LAUNCH=0; T_GIT=0\n",
        "C=\"\"; T_R=\"\"; T_PLANT=\"\"; T_CRASH=\"\"; T_HANG=\"\"; T_HARD=\"\"; T_VEXC=\"\"; T_LIM=\"\"; CENSUS=0; T_ANY=0; LAUNCH=0; T_GIT=0; T_FB=0\n")
s = rep(s, "    --test-git-check) T_GIT=1; T_ANY=1; shift; continue;;\n",
        "    --test-git-check) T_GIT=1; T_ANY=1; shift; continue;;\n"
        "    --test-frozen-build) T_FB=1; T_ANY=1; shift; continue;;\n")
s = rep(s, "  [ -z \"$C\" ] || arg_stop freeze_commit_belongs_to_launch_r9\n",
        "  [ -z \"$C\" ] || [ $T_FB -eq 1 ] || arg_stop freeze_commit_belongs_to_launch_r9_or_test_frozen_build\n")
s = rep(s, "if [ \"$MODE\" = r9 ] || [ $T_GIT -eq 1 ]; then git_contact; fi\n",
        "FZ=0; { [ \"$MODE\" = r9 ] || [ $T_FB -eq 1 ]; } && FZ=1\n"
        "if [ $FZ -eq 1 ] || [ $T_GIT -eq 1 ]; then git_contact; fi\n")
s = rep(s, "mkdir -m 700 \"$PRIV\" && mount -t tmpfs -o mode=700,size=256m floor-run-tools \"$PRIV\" 2>/dev/null && mkdir -m 700 \"$PRIV/py\"   || prelude_stop UNRESOLVED cannot_create_the_private_tool_directory\n",
        "mkdir -m 700 \"$PRIV\" && mount -t tmpfs -o mode=700,size=256m floor-run-tools \"$PRIV\" 2>/dev/null && mkdir -m 700 \"$PRIV/py\"   || prelude_stop UNRESOLVED cannot_create_the_private_tool_directory\n"
        "# ---- the namespace once more, by its effect (row 132): both mounts are in this process's mount table and in\n"
        "# neither the parent's nor that of process 1; a mount that shows outside is taken down and the run does not start\n"
        "ns_seen() { /usr/bin/grep -Fq \" $2 \" \"$1\" 2>/dev/null; } # mount table, mount point ; 0 listed, 1 absent, 2 unreadable\n"
        "NSBAD=\"\"\n"
        "for x in \"$OUT/tmp\" \"$PRIV\"; do\n"
        "  ns_seen /proc/self/mountinfo \"$x\"; [ $? -eq 0 ] || NSBAD=mount_absent_from_the_mount_table_of_this_process\n"
        "  ns_seen \"/proc/$PPID/mountinfo\" \"$x\"; [ $? -eq 1 ] || NSBAD=${NSBAD:-private_tmpfs_listed_or_unreadable_in_the_mount_table_of_the_parent_process}\n"
        "  ns_seen /proc/1/mountinfo \"$x\"; [ $? -eq 1 ] || NSBAD=${NSBAD:-private_tmpfs_listed_or_unreadable_in_the_mount_table_of_process_1}\n"
        "done\n"
        "[ \"$(/usr/bin/readlink /proc/self/ns/mnt 2>/dev/null)\" = \"$NS_SELF\" ] || NSBAD=${NSBAD:-mount_namespace_id_changed}\n"
        "if [ -n \"$NSBAD\" ]; then umount \"$PRIV\" 2>/dev/null; umount \"$OUT/tmp\" 2>/dev/null; prelude_stop UNRESOLVED \"$NSBAD\"; fi\n")
s = rep(s, "say \"NOTE|environment=env_-i_with_PATH=/usr/bin:/bin_LANG=C_HOME=${HOME}_TMPDIR=<run_directory>/tmp|mount_namespace=private_(unshare_-m)|tmpdir=tmpfs_mounted_in_that_namespace|",
        "say \"NOTE|environment=env_-i_with_PATH=/usr/bin:/bin_LANG=C_HOME=${HOME}_TMPDIR=<run_directory>/tmp|mount_namespace=private_CHECKED_(row_132)|namespace_of_this_process=$NS_SELF|namespace_of_the_parent_process=$NS_PARENT|namespace_of_process_1=$NS_INIT|shared_or_slave_mounts=0|both_tmpfs_mounts=listed_here_and_absent_from_the_mount_tables_of_the_parent_process_and_of_process_1|tmpdir=tmpfs_mounted_in_that_namespace|")
s = rep(s, "# ---- freeze commit (frozen run): the commit that carries the prediction record, checked by blob hash\nif [ \"$MODE\" = r9 ]; then\n",
        "# ---- freeze commit (frozen run, and a rehearsal with --test-frozen-build): the commit that carries the prediction\n# record, checked by blob hash\nif [ $FZ -eq 1 ]; then\n")
s = rep(s, "if [ \"$MODE\" = r9 ]; then\n  FB=\"$OUT/target/release/floorcert\"\n",
        "if [ $FZ -eq 1 ]; then\n  FB=\"$OUT/target/release/floorcert\"\n")
s = rep(s, "  FREEZE_ARGS=(--freeze-commit \"$C\" --prediction \"$PREDREL\" --prediction-sha256 \"$P\")\nelse\n",
        "  if [ \"$MODE\" = r9 ]; then\n"
        "    FREEZE_ARGS=(--freeze-commit \"$C\" --prediction \"$PREDREL\" --prediction-sha256 \"$P\")\n"
        "  else\n"
        "    # a rehearsal: the binary carries the two pins and runs at the excluded R, where it takes no freeze argument\n"
        "    FREEZE_ARGS=()\n"
        "    say \"NOTE|frozen_build_rehearsal=1|freeze_commit=$C|compiled_prediction_sha256=$P|build_log=log/build_frozen.txt|pin_check_2=HELD|r=$R|json=0\"\n"
        "  fi\nelse\n")
s = rep(s, "[ \"$MODE\" = r9 ] || [ \"$FBSHA\" = \"$(pinval 016)\" ] || prelude_stop FAIL binary_copy_differs_from_row_016\n",
        "if [ $FZ -eq 1 ]; then\n"
        "  [ \"$FBSHA\" != \"$(pinval 016)\" ] || prelude_stop FAIL frozen_build_gave_the_pin_free_binary_of_row_016\n"
        "else\n"
        "  [ \"$FBSHA\" = \"$(pinval 016)\" ] || prelude_stop FAIL binary_copy_differs_from_row_016\n"
        "fi\n")
s = rep(s, "pin=$([ \"$MODE\" = r9 ] && echo frozen_build_of_row_009 || echo 016)|want=$FBSHA|json=0\"\n",
        "pin=$([ $FZ -eq 1 ] && echo frozen_build_of_row_009 || echo 016)|want=$FBSHA|json=0\"\n")
assert "\t" not in s
open(D + "/run_floor_d.sh", "w", encoding="ascii", newline="").write(s)

# ------------------------------------------------------------------ evaluator
e = load("floor_eval.py")
assert "\r" not in e
e = rep(e, "(version 2 freeze, second correction round).", "(version 2 freeze, third correction round).")
e = rep(e, "# Exit of final: 0 CERTIFICATE=PASS with ABOVE, 3 PASS with BELOW, 2 PASS with UNRESOLVED, 1 every CERTIFICATE=FAIL.\n",
        "# Exit of final: 0 CERTIFICATE=PASS with ABOVE, 3 PASS with BELOW, 2 PASS with UNRESOLVED, 1 every CERTIFICATE=FAIL.\n"
        "# The receipt names its run directory (RUN_DIRECTORY row); the certificate paths of its RECHECK rows are relative to\n"
        "# that directory, and its VERDICT_FIELDS row carries the upper bound from the verifier's Ritz values alone, which is\n"
        "# the value the second-environment checker final/tools/recheck_floor.py (row 131) must reproduce (row 133).\n")
e = rep(e, "    o.append(\"VERDICT_FIELDS|CERTIFICATE=%s|PREDICTION=%s|DECISION=%s|GAMMA=%s|UPPER_BOUND=%s|g0=%s|accepted_certificates=%d|json=0\"\n"
           "             % (cert, pred, dec, rs(G), rs(U), rs(g0), acc))\n",
        "    o.append(\"VERDICT_FIELDS|CERTIFICATE=%s|PREDICTION=%s|DECISION=%s|GAMMA=%s|UPPER_BOUND=%s|UPPER_BOUND_VERIFIER_ONLY=%s|g0=%s|accepted_certificates=%d|r=%s|mode=%s|json=0\"\n"
        "             % (cert, pred, dec, rs(G), rs(U), rs(Uv), rs(g0), acc, a[\"r\"], a[\"mode\"]))\n"
        "    o.append(\"RUN_DIRECTORY|path=%s|holds=this_receipt_its_sha256_file_and_the_RUN_folders|certificate_paths_of_the_RECHECK_rows=relative_to_this_directory|json=0\"\n"
        "             % os.path.realpath(out))\n")
old_rule = e[e.index("        o.append(\"RECHECK_RULE|row=125|"):e.index("        for s in S:\n            if s[\"status\"] != \"OK\":\n                continue\n            rhs = ")]
new_rule = (
    "        o.append(\"RECHECK_RULE|rows=125_133|accepted_only_after=a_second_independent_environment_ran_the_checker_of_row_131_on_this_receipt_and_it_ended_RECHECK_VERDICT:ACCEPT=YES|\"\n"
    "                 \"where=a_clean_checkout_of_the_freeze_commit,_inside_the_freeze_folder,_with_this_run_directory_copied_whole_(the_receipt,_its_sha256_file_and_the_RUN_folders)|\"\n"
    "                 \"command=python3 -I -B final/tools/recheck_floor.py receipt=RUN_DIRECTORY/FLOOR-RUN-RECEIPT.hbp%s|\"\n"
    "                 \"certificate_paths=each_RECHECK_row_names_its_certificate_relative_to_the_directory_that_holds_the_receipt_(the_run_directory);_the_checker_refuses_a_missing_file,_a_symbolic_link,_a_path_that_leaves_that_directory_and_a_file_whose_sha256_differs_from_the_row|\"\n"
    "                 \"gate_command_per_certificate=bash --noprofile --norc work/design/gate_required.sh RUN_DIRECTORY/CERTIFICATE%s|gate_driver_sha256=%s|verifier_sha256=%s|\"\n"
    "                 \"expect=last_line_GATE_REQUIRED_PASS_with_the_cert_sha256_rowhash_and_verifier_sha256_of_the_RECHECK_row,_and_VERDICT_PASS_with_the_gamma_of_the_RECHECK_row|\"\n"
    "                 \"then=GAMMA_is_the_largest_gamma_the_checker's_verifier_printed;_the_upper_bound_is_the_smallest_Ritz_value_the_checker's_verifier_printed_plus_1/1000000_and_no_value_of_this_receipt_enters_it;_DECISION_by_the_decision_rule_field_of_the_final_line;_the_three_must_equal_DECISION,_GAMMA_and_UPPER_BOUND_VERIFIER_ONLY_of_the_VERDICT_FIELDS_row;_any_difference_blocks_acceptance|json=0\"\n"
    "                 % ((\" commit=%s\" % a.get(\"commit\", \"NONE\")) if a[\"mode\"] == \"r9\" else \"\", extra, R[\"020\"][1][\"value\"], R[\"019\"][1][\"value\"]))\n")
e = rep(e, old_rule, new_rule)
e = rep(e, "                    o.append(\"RECHECK|m0=%d|certificate=RUN%d/%s|sha256=%s|gamma=%s|ritz_writer=%s|ritz_verifier=%s|rowhash=%s|verifier_sha256=%s|json=0\"\n",
        "                    o.append(\"RECHECK|m0=%d|certificate=RUN%d/%s|relative_to=RUN_DIRECTORY|sha256=%s|gamma=%s|ritz_writer=%s|ritz_verifier=%s|rowhash=%s|verifier_sha256=%s|json=0\"\n")
assert "\t" not in e
open(D + "/floor_eval_d.py", "w", encoding="ascii", newline="").write(e)
print("patched")
