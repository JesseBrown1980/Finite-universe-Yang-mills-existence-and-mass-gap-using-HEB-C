# Fourth correction round: makes run_floor_e.sh and floor_eval_e.py from the files committed at 5eecb540.
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
s = rep(s, "(version 2 freeze, third correction round).", "(version 2 freeze, fourth correction round).")
s = rep(s, "# and for process 1, or the run stops with NOT_STARTED. Only then does the run log say that the namespace is private.\n",
        "# and for process 1, or the run stops with NOT_STARTED. Only then does the run log say that the namespace is private.\n"
        "# EXCLUSIVE (row 139). No other process may sit in that mount namespace: at the start of stage 2, after the mounts and\n"
        "# at the close the launcher lists every process whose mount namespace is its own; one that is neither this shell nor\n"
        "# a child of it stops the run (NOT_STARTED before the first command, CERTIFICATE=FAIL at the close). An entry made\n"
        "# through a namespace that another process holds (nsenter) is refused by this check.\n"
        "# BUILD (row 139). Cargo runs with CARGO_HOME set to an empty directory on the launcher's tmpfs; a cargo\n"
        "# configuration file in the Rust folder or in any directory above it, and any untracked file in the Rust folder\n"
        "# outside target/, stop the run. With a frozen build the tracked files of the whole repository must be unchanged.\n"
        "# PUBLISH. Before its final line the launcher prints PUBLISH|receipt_sha256=...; that value is to be made public at\n"
        "# once, and the checker of row 131 requires it for the r9 receipt (row 138).\n")
# stage 2: the namespace must hold this shell alone
s = rep(s, "/usr/bin/grep -Eq ' (shared|master|propagate_from):[0-9]+ ' /proc/self/mountinfo; [ $? -eq 1 ] || early_stop namespace mount_namespace_holds_a_shared_or_slave_mount\n",
        "/usr/bin/grep -Eq ' (shared|master|propagate_from):[0-9]+ ' /proc/self/mountinfo; [ $? -eq 1 ] || early_stop namespace mount_namespace_holds_a_shared_or_slave_mount\n"
        "ns_others() { # the pids, other than this shell and its own children, whose mount namespace is this one (row 139)\n"
        "  local p q\n"
        "  for p in /proc/[0-9]*; do\n"
        "    p=${p#/proc/}\n"
        "    [ \"$p\" = \"$$\" ] && continue\n"
        "    [ \"$(/usr/bin/readlink \"/proc/$p/ns/mnt\" 2>/dev/null)\" = \"$NS_SELF\" ] || continue\n"
        "    q=$(/usr/bin/sed -n 's/^PPid:[[:space:]]*//p' \"/proc/$p/status\" 2>/dev/null)\n"
        "    [ \"$q\" = \"$$\" ] && continue\n"
        "    echo \"$p\"\n"
        "  done\n"
        "}\n"
        "[ -z \"$(ns_others)\" ] || early_stop namespace mount_namespace_is_held_by_another_process\n")
s = rep(s, "[ \"$(/usr/bin/readlink /proc/self/ns/mnt 2>/dev/null)\" = \"$NS_SELF\" ] || NSBAD=${NSBAD:-mount_namespace_id_changed}\n",
        "[ \"$(/usr/bin/readlink /proc/self/ns/mnt 2>/dev/null)\" = \"$NS_SELF\" ] || NSBAD=${NSBAD:-mount_namespace_id_changed}\n"
        "[ -z \"$(ns_others)\" ] || NSBAD=${NSBAD:-mount_namespace_is_held_by_another_process}\n")
s = rep(s, "shared_or_slave_mounts=0|both_tmpfs_mounts=", "shared_or_slave_mounts=0|other_processes_in_this_namespace=0|both_tmpfs_mounts=")
# freeze commit block: the tracked files of the whole repository
s = rep(s, "  [ -z \"$(\"$GIT\" status --porcelain --untracked-files=no -- . 2>/dev/null)\" ] || prelude_stop FAIL tracked_files_differ_from_the_commit\n",
        "  [ -z \"$(\"$GIT\" status --porcelain --untracked-files=no 2>/dev/null)\" ] || prelude_stop FAIL tracked_files_differ_from_the_commit\n")
# builds: no cargo configuration, an empty CARGO_HOME, no untracked file in the Rust folder
s = rep(s, "if [ ! -f \"$PINFREE\" ]; then\n",
        "# ---- the build environment (row 139): nothing but the pinned source, Cargo.toml and Cargo.lock reaches cargo\n"
        "CGD=\"$ROOT/work/design/rs\"\n"
        "while :; do\n"
        "  { [ -e \"$CGD/.cargo/config.toml\" ] || [ -e \"$CGD/.cargo/config\" ] || [ -L \"$CGD/.cargo\" ]; } && prelude_stop FAIL cargo_configuration_file_in_the_Rust_folder_or_above_it\n"
        "  [ \"$CGD\" = / ] && break\n"
        "  CGD=$(dirname \"$CGD\")\n"
        "done\n"
        "if [ -n \"$TOP\" ]; then\n"
        "  [ -z \"$(\"$GIT\" -C \"$ROOT\" ls-files --others -- work/design/rs 2>/dev/null | grep -v '^work/design/rs/target/')\" ] || prelude_stop FAIL untracked_file_in_the_Rust_folder\n"
        "fi\n"
        "CH=\"$TMPDIR/cargo-home\"; mkdir -m 700 \"$CH\" || prelude_stop UNRESOLVED cannot_create_the_empty_cargo_home\n"
        "say \"NOTE|build_environment=CARGO_HOME_is_an_empty_directory_on_the_launcher_tmpfs|cargo_configuration_files_in_the_Rust_folder_or_above=0|untracked_files_in_the_Rust_folder_outside_target=$([ -n \"$TOP\" ] && echo 0 || echo NOT_CHECKED_no_git_checkout)|json=0\"\n"
        "if [ ! -f \"$PINFREE\" ]; then\n")
s = rep(s, "  (cd work/design/rs && RUSTC=\"$RUSTC\" \"$CARGO\" build --release --locked -j1) > \"$LOG/build_pinfree.txt\" 2>&1 \\\n",
        "  (cd work/design/rs && CARGO_HOME=\"$CH\" RUSTC=\"$RUSTC\" \"$CARGO\" build --release --locked -j1) > \"$LOG/build_pinfree.txt\" 2>&1 \\\n")
s = rep(s, "  (cd work/design/rs && RUSTC=\"$RUSTC\" CARGO_TARGET_DIR=\"$OUT/target\"", "  (cd work/design/rs && CARGO_HOME=\"$CH\" RUSTC=\"$RUSTC\" CARGO_TARGET_DIR=\"$OUT/target\"")
# closing: the namespace once more, the protocol handed to the evaluator, the PUBLISH line
s = rep(s, "# again inside the evaluator before it prints\nguard || integrity_stop\n",
        "# again inside the evaluator before it prints\nguard || integrity_stop\n"
        "if [ -n \"$(ns_others)\" ]; then STOP=FAIL_another_process_sits_in_the_mount_namespace_at_the_close; say \"NOTE|close=another_process_sits_in_the_mount_namespace|json=0\"; fi\n")
s = rep(s, "allowed=\"${#STEPS[@]}\" mode=\"$MODE\" r=\"$R\" stop=\"$STOP\" \\\n",
        "allowed=\"${#STEPS[@]}\" plan=\"$(IFS=,; echo \"${STEPS[*]}\")\" fspec=\"$FSPEC\" mode=\"$MODE\" r=\"$R\" stop=\"$STOP\" \\\n")
s = rep(s, "printf '%s\\n' \"$FIN\"\nexit \"$XC\"\n",
        "echo \"PUBLISH|receipt_sha256=$(\"$SHA\" \"$OUT/FLOOR-RUN-RECEIPT.hbp\" | cut -d' ' -f1)|receipt=$OUT/FLOOR-RUN-RECEIPT.hbp|make_this_value_public_now=the_checker_of_row_131_requires_it_for_the_r9_receipt_(row_138)|json=0\"\n"
        "printf '%s\\n' \"$FIN\"\nexit \"$XC\"\n")
assert "\t" not in s
open(D + "/run_floor_e.sh", "w", encoding="ascii", newline="").write(s)

# ------------------------------------------------------------------ evaluator
e = load("floor_eval.py")
assert "\r" not in e
e = rep(e, "(version 2 freeze, third correction round).", "(version 2 freeze, fourth correction round).")
e = rep(e, "    o.append(\"RUN_DIRECTORY|path=%s|holds=this_receipt_its_sha256_file_and_the_RUN_folders|certificate_paths_of_the_RECHECK_rows=relative_to_this_directory|json=0\"\n"
           "             % os.path.realpath(out))\n",
        "    o.append(\"RUN_DIRECTORY|path=%s|holds=this_receipt_its_sha256_file_and_the_RUN_folders|certificate_paths_of_the_RECHECK_rows=relative_to_this_directory|json=0\"\n"
        "             % os.path.realpath(out))\n"
        "    # the protocol this run was started with (row 138): the checker holds the frozen one as constants and reads this\n"
        "    # row for a rehearsal only\n"
        "    o.append(\"PROTOCOL|mode=%s|r=%s|m0_steps=%s|f=%s|g0=%s|allowed=%s|json=0\"\n"
        "             % (a[\"mode\"], a[\"r\"], a.get(\"plan\", \"NONE\"), a.get(\"fspec\", \"NONE\"), rs(g0), a[\"allowed\"]))\n")
e = rep(e, "(\" commit=%s\" % a.get(\"commit\", \"NONE\")) if a[\"mode\"] == \"r9\" else \"\"",
        "(\" commit=%s receipt_sha256=THE_VALUE_OF_THE_PUBLISH_LINE\" % a.get(\"commit\", \"NONE\")) if a[\"mode\"] == \"r9\" else \"\"")
e = rep(e, "RECHECK_RULE|rows=125_133|", "RECHECK_RULE|rows=125_133_138|")
assert "\t" not in e
open(D + "/floor_eval_e.py", "w", encoding="ascii", newline="").write(e)
print("patched")
