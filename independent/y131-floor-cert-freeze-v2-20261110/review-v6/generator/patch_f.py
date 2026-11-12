# Fifth correction round: makes run_floor_f.sh and recheck_floor_f.py from the files committed at 3c41ea2d.
# The evaluator is unchanged. Every replacement must match exactly once.
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
s = rep(s, "(version 2 freeze, fourth correction round).", "(version 2 freeze, fifth correction round).")
s = rep(s, "# through a namespace that another process holds (nsenter) is refused by this check.\n",
        "# through a namespace that another process holds (nsenter) is refused by this check.\n"
        "# REFERENCES (row 144). At the same three points the launcher reads every mount table it can read and the open\n"
        "# descriptors of every process: a bind mount or a descriptor that names this mount namespace, or one that names a\n"
        "# mount namespace with no member process, stops the run. An entry through a namespace that a bound file keeps alive\n"
        "# with no process in it is refused by this check.\n")
s = rep(s, "# outside target/, stop the run. With a frozen build the tracked files of the whole repository must be unchanged.\n",
        "# outside target/, stop the run. With a frozen build the tracked files of the whole repository must be unchanged.\n"
        "# A Cargo.toml that names a workspace in any directory above the Rust folder stops the run (row 144). With a frozen\n"
        "# build the checkout must be at the freeze commit (HEAD equal to C) and the index may mark no file assume-unchanged\n"
        "# or skip-worktree.\n")
s = rep(s, "a process outside the namespace sees\n# neither); the tmpfs files",
        "a process outside the namespace has\n# neither in its own mount table; root reads them through /proc/PID/root, row 144); the tmpfs files")
# stage 2: no reference to this namespace other than its member processes, and no namespace without a member process
s = rep(s, "[ -z \"$(ns_others)\" ] || early_stop namespace mount_namespace_is_held_by_another_process\n",
        "[ -z \"$(ns_others)\" ] || early_stop namespace mount_namespace_is_held_by_another_process\n"
        "ns_refs() { # mount namespace references that are no member process (row 144): nsfs bind mounts of every readable mount\n"
        "  # table and open descriptors of every process; printed when one names this namespace or a namespace without a member\n"
        "  local m=\"\" x\n"
        "  for x in /proc/[0-9]*/ns/mnt; do m=\"$m $(/usr/bin/readlink \"$x\" 2>/dev/null) \"; done\n"
        "  { /usr/bin/cat /proc/[0-9]*/mountinfo 2>/dev/null | /usr/bin/sed -n 's/^[0-9]* [0-9]* [0-9:]* \\(mnt:\\[[0-9]*\\]\\) .* - nsfs .*$/\\1/p'\n"
        "    /usr/bin/find /proc/[0-9]*/fd -maxdepth 1 -lname 'mnt:*' -printf '%l\\n' 2>/dev/null\n"
        "  } | while read -r x; do\n"
        "    if [ \"$x\" = \"$NS_SELF\" ]; then echo \"$x\"; else case \"$m\" in *\" $x \"*) ;; *) echo \"$x\";; esac; fi\n"
        "  done\n"
        "}\n"
        "[ -z \"$(ns_refs)\" ] || early_stop namespace mount_namespace_reference_outside_a_member_process\n")
s = rep(s, "[ -z \"$(ns_others)\" ] || NSBAD=${NSBAD:-mount_namespace_is_held_by_another_process}\n",
        "[ -z \"$(ns_others)\" ] || NSBAD=${NSBAD:-mount_namespace_is_held_by_another_process}\n"
        "[ -z \"$(ns_refs)\" ] || NSBAD=${NSBAD:-mount_namespace_reference_outside_a_member_process}\n")
s = rep(s, "|other_processes_in_this_namespace=0|both_tmpfs_mounts=",
        "|other_processes_in_this_namespace=0|references_to_this_namespace_outside_member_processes=0|mount_namespaces_without_a_member_process=0|both_tmpfs_mounts=")
# freeze commit block: the checkout is at the freeze commit and the index hides no file
s = rep(s, "  [ -z \"$(\"$GIT\" status --porcelain --untracked-files=no 2>/dev/null)\" ] || prelude_stop FAIL tracked_files_differ_from_the_commit\n"
           "  say \"NOTE|freeze_commit=$C|prediction_blob_sha256=$BL|json=0\"\n",
        "  [ -z \"$(\"$GIT\" status --porcelain --untracked-files=no 2>/dev/null)\" ] || prelude_stop FAIL tracked_files_differ_from_the_commit\n"
        "  [ \"$(\"$GIT\" rev-parse HEAD 2>/dev/null)\" = \"$C\" ] || prelude_stop FAIL checkout_head_is_not_the_freeze_commit\n"
        "  [ -z \"$(\"$GIT\" -C \"$TOP\" ls-files -v 2>/dev/null | grep '^[a-zS] ')\" ] || prelude_stop FAIL index_marks_a_file_assume_unchanged_or_skip_worktree\n"
        "  say \"NOTE|freeze_commit=$C|prediction_blob_sha256=$BL|head_equals_the_freeze_commit=1|files_marked_assume_unchanged_or_skip_worktree=0|json=0\"\n")
# builds: no manifest that names a workspace above the Rust folder
s = rep(s, "  { [ -e \"$CGD/.cargo/config.toml\" ] || [ -e \"$CGD/.cargo/config\" ] || [ -L \"$CGD/.cargo\" ]; } && prelude_stop FAIL cargo_configuration_file_in_the_Rust_folder_or_above_it\n",
        "  { [ -e \"$CGD/.cargo/config.toml\" ] || [ -e \"$CGD/.cargo/config\" ] || [ -L \"$CGD/.cargo\" ]; } && prelude_stop FAIL cargo_configuration_file_in_the_Rust_folder_or_above_it\n"
        "  [ \"$CGD\" != \"$ROOT/work/design/rs\" ] && [ -e \"$CGD/Cargo.toml\" ] && grep -q workspace \"$CGD/Cargo.toml\" 2>/dev/null && prelude_stop FAIL cargo_manifest_naming_a_workspace_above_the_Rust_folder\n")
s = rep(s, "|cargo_configuration_files_in_the_Rust_folder_or_above=0|untracked_files_in_the_Rust_folder_outside_target=",
        "|cargo_configuration_files_in_the_Rust_folder_or_above=0|cargo_manifests_naming_a_workspace_above_the_Rust_folder=0|untracked_files_in_the_Rust_folder_outside_target=")
# closing: the references once more
s = rep(s, "if [ -n \"$(ns_others)\" ]; then STOP=FAIL_another_process_sits_in_the_mount_namespace_at_the_close; say \"NOTE|close=another_process_sits_in_the_mount_namespace|json=0\"; fi\n",
        "if [ -n \"$(ns_others)\" ]; then STOP=FAIL_another_process_sits_in_the_mount_namespace_at_the_close; say \"NOTE|close=another_process_sits_in_the_mount_namespace|json=0\"; fi\n"
        "if [ -n \"$(ns_refs)\" ]; then STOP=FAIL_a_mount_namespace_reference_outside_a_member_process_at_the_close; say \"NOTE|close=mount_namespace_reference_outside_a_member_process|json=0\"; fi\n")
assert "\t" not in s
open(D + "/run_floor_f.sh", "w", encoding="ascii", newline="").write(s)

# ------------------------------------------------------------------ checker
c = load("recheck_floor.py")
assert "\r" not in c
c = rep(c, "(rows 125, 131, 133 and 138 of the record).\n# Fourth correction round.", "(rows 125, 131, 133, 138 and 143 of the record).\n# Fifth correction round.")
c = rep(c, "no step after a\n# decision, and, for an UNRESOLVED result, every allowed step completed; (3) the decision, the bounds, the per-step\n",
        "no step after a\n# decision; (3) the decision, the bounds, the per-step\n")
c = rep(c, "# A result that is ABOVE or BELOW stands on certificates verified here. An UNRESOLVED result with a step that did not\n"
           "# complete (an operational failure, an early stop) is NOT accepted by this checker: nothing here can tell a step\n"
           "# that failed from a step whose certificates were removed, and that reading belongs to the reviewer.\n",
        "# A result that is ABOVE or BELOW stands on certificates verified here. An UNRESOLVED result is NEVER accepted by this\n"
        "# checker (row 143): certificates that do not decide cannot show that no certificate decides, because a valid\n"
        "# certificate can be replaced by a weaker valid one (a smaller t, another positive vector). The checks are still run\n"
        "# and printed for an UNRESOLVED receipt; the last line is ACCEPT=NO and the reading belongs to the reviewer.\n")
c = rep(c, "    if dec == \"UNRESOLVED\" and not complete:\n",
        "    if dec == \"UNRESOLVED\":\n"
        "        bad.append(\"UNRESOLVED_is_never_accepted_by_this_checker_(row_143):_certificates_that_do_not_decide_cannot_show_that_no_certificate_decides\")\n"
        "    if dec == \"UNRESOLVED\" and not complete:\n")
c = rep(c, "            if f.get(\"row\") in srec or f[\"\\0dup\"]:\n"
           "                bad.append(\"PREDICT_SCORE_row_repeated\")\n"
           "            srec[f.get(\"row\")] = f.get(\"outcome\")\n",
        "            if \"row\" not in f:\n"
        "                bad.append(\"PREDICT_SCORE_row_without_a_row_key\")\n"
        "            if f.get(\"row\", \"NO_ROW_KEY\") in srec or f[\"\\0dup\"]:\n"
        "                bad.append(\"PREDICT_SCORE_row_repeated\")\n"
        "            srec[f.get(\"row\", \"NO_ROW_KEY\")] = f.get(\"outcome\")\n")
c = rep(c, "        if pf.get(\"m0_steps\") != \",\".join(str(x) for x in steps_plan) or",
        "        if pf[\"\\0dup\"] or pf.get(\"m0_steps\") != \",\".join(str(x) for x in steps_plan) or")
c = rep(c, "        freeze_args = [\"--freeze-commit\", commit, \"--prediction\", PRED_REL, \"--prediction-sha256\", P]\n",
        "        freeze_args = [\"--freeze-commit\", commit, \"--prediction\", PRED_REL, \"--prediction-sha256\", P]\n"
        "        # commit= against the checkout this checker runs in, where git can read it (an export carries no HEAD)\n"
        "        try:\n"
        "            chead = subprocess.run([\"git\", \"-C\", root, \"rev-parse\", \"HEAD\"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,\n"
        "                                   stderr=subprocess.DEVNULL).stdout.decode(\"ascii\", \"replace\").strip()\n"
        "        except Exception:\n"
        "            chead = \"\"\n"
        "        if not re.match(r\"^[0-9a-f]{40}$\", chead):\n"
        "            chead = \"NOT_READ_no_git_checkout\"\n"
        "        elif chead != commit:\n"
        "            bad.append(\"commit=_differs_from_the_HEAD_of_this_checkout\")\n"
        "        say(\"CHECKOUT_HEAD|head=%s|commit_given=%s|json=0\" % (chead, commit))\n")
assert "\t" not in c
open(D + "/recheck_floor_f.py", "w", encoding="ascii", newline="").write(c)
print("patched")
