# Final-head verification 6 of the floor freeze v2 (commit c8dbcdbf)

Verifier seat: opus55, second seat of ACER-CLAUDE-FABLE5 (pid 8467a937cba309f7), model claude-opus-5-5, 2026-11-12.
This is a regression run with the verification-5 scripts. No new attack was designed in this pass. The scripts in
`scripts/` are the verification-5 scripts with paths, commit hashes, record hash, unit names and output folder changed.
Their comment lines were also changed by the same `sed`. One of those comments in `negctl5.py` (line 254) now reads
"controls added in verification 6"; those controls were added in verification 5. Small read-only helpers were added:
`s0_state.sh`, `s1_diff.sh`, `s2_diff.sh`, `c_show.sh`, `w_done.sh`, `e_exp0.sh`, `*_start.sh`, `stage_raw.sh`, `b_reasons.sh`.
Gate A also compares `final/tools/floor_eval.py`, as the brief asks.

Lane: WSL2 Ubuntu as root. Fresh clone `/root/floor-v6-verify/repoE` at c8dbcdbf990114292313cbc410a745a14ba0b778
(parent 3c41ea2d), equal to `git ls-remote` of the branch, 0 local changes. Attack clone `repoD`. The checker
always ran from `exp0`, a `git archive` export of c8dbcdbf. r values used: 12, 14 and 21/2. `--launch-r9` was never
passed. The only r = 9 contact was `final/tools/freeze_args_controls.sh` exactly as written: 11 controls, 11 refused.
At the end `findmnt -t nsfs` printed nothing, and the host mount table had 0 floor-run entries.

## Verdict

**NOT PASS.** No HIGH or MEDIUM finding. Gate C fails its stated criterion (every control ends ACCEPT=NO): six
controls end ACCEPT=YES. All six are LOW, have the same results as in verification 5, and fall under openings that rows
139 and 144 disclose. The gate D checker pass did not finish: the WSL distribution restarted during the third
certificate (init start 15:07:54 local). Per the brief I did not retry it.

| Gate | Result |
|---|---|
| A integrity | PASS (MEASURED) |
| B launcher | PASS (MEASURED): B2, B5, B6b, B7 refused; every earlier refusal holds; FZA 11/11; honest runs pass. B3 LOW, still open (row 144 `open`) |
| C checker | Criterion not met: N03, X02b, X04b, X07b, X08, X11b end ACCEPT=YES (LOW, disclosed). X15, X15t, X15a, X02c refused with a verdict line |
| D full size | Launcher PASS (MEASURED). Checker NOT COMPLETED (2 of 3 certificates rechecked PASS, then the distribution restarted) |

## A. Integrity: PASS

- `sha256sum -c FREEZE-PIN.sha256`: exit 0, 857/857 OK. Regenerating it from `git ls-files` of the folder (minus the two FREEZE-PIN files) gives 0 differing lines.
- Record sha256 9f1076dd…f99c, named in FREEZE-PIN.txt, NOTE and CHANGES.
- Record rows match the files:
  - row 114: run_floor.sh ae114b64…
  - row 115: floor_eval.py f92f404f…
  - row 131: recheck_floor.py 36526aa2…

  All three hashes also appear in NOTE and CHANGES.
- Byte-identical to 3c41ea2d:
  - the 16 PREDICT rows (16/16)
  - main.rs, gate_required.sh, cert_gate.py, indep_verify.py, peak_rss.py
  - floor_eval.py, Cargo.toml, Cargo.lock, freeze_args_controls.sh

  Changed or new rows: 114, 131, 142-146.
- Files changed outside the folder: 0. CR bytes in changed files: 0.
- `no_float_gate.py`: exit 0, `failed=0`.
- The pin-free build (1.81, `--locked`) gives 9533e7e9…, equal to row 016.
- `cargo +1.81 clippy --release -- -D warnings`: exit 0, clippy 0.1.81.
  - The `$TC/cargo clippy` line in `b_build.sh` again resolved clippy 1.96 and failed. That is the same harness artefact as in verification 5, not the owning gate.

## B. Launcher: PASS

| Case | Exit | Last line / reason |
|---|---|---|
| B0 frozen build, clean | 2 | CERTIFICATE=PASS UNRESOLVED, freeze_commit=c8dbcdbf, frozen binary 027b0515… |
| B1 nsenter into a process-held namespace | 4 | NOT_STARTED `mount_namespace_is_held_by_another_process` |
| B2 nsenter into a namespace held by an nsfs bind mount | 4 | NOT_STARTED `mount_namespace_reference_outside_a_member_process` (was PASS in v5) |
| B3 nsenter by the launcher pid, leaving before the close | 2 | CERTIFICATE=PASS (LOW, still open, row 144 `open`) |
| B3b same, staying past the close | 1 | `close=another_process_sits_in_the_mount_namespace` |
| B4 untracked rs/.cargo/config.toml | 1 | `cargo_configuration_file_in_the_Rust_folder_or_above_it` |
| B4b .cargo/config.toml at the repository root | 1 | `cargo_configuration_file_in_the_Rust_folder_or_above_it` |
| B5 untracked workspace Cargo.toml above the crate | 1 | `cargo_manifest_naming_a_workspace_above_the_Rust_folder` (was PASS in v5) |
| B6 tracked .md outside the folder modified | 1 | `tracked_files_differ_from_the_commit` |
| B6b same, hidden by assume-unchanged | 1 | `index_marks_a_file_assume_unchanged_or_skip_worktree` (was PASS in v5) |
| B7 descendant commit adds a workspace root | 1 | `checkout_head_is_not_the_freeze_commit` (was PASS in v5) |
| B8 FZA, 11 freeze-argument controls on the B0 binary | 0 | 11 of 11 refused, numerical output lines 0, run directory 0 |

Honest rehearsals still pass with the new namespace and manifest checks; this host has `/Cargo.toml` without the word workspace. D1 (r = 14) gave exit 0, `CERTIFICATE=PASS|DECISION=ABOVE`, and G and U equal to verification 5. B0 and D13 also passed.
With a root `nsenter`-free read of `/proc/<launcher pid>/root/…` during D13 (`b_procroot.sh`), the private tools and `gate_required.sh` (0064ca46…) can still be read. The launcher header now discloses this (row 144 `wording`).

## C. Checker

Genuine receipts (`g_runs.sh`, r = 14):

| Control | Checker result |
|---|---|
| G_D1, G_D1_pub, G_D2, G_D2_pub, G_D3, G_H1 | ACCEPT=YES with the launcher's decision |
| G_D4, G_U2 (genuine UNRESOLVED) | ACCEPT=NO, reason `UNRESOLVED_is_never_accepted_by_this_checker_(row_143)…` (the intended change from v5) |

Forgery controls (`c_all.sh`, 59 controls):
- X15, X15t and X15a now end `RECHECK_VERDICT|ACCEPT=NO|DECISION=UNRESOLVED` with the row-143 reason. That closes the v5 HIGH.
- X02c ends `ACCEPT=NO` with `PREDICT_SCORE_row_without_a_row_key`. There is a verdict line and no traceback.
- No traceback appears in any checker output.
- X06d, ACCEPT=YES in v5, is now ACCEPT=NO through row 143.

Controls that end ACCEPT=YES (all LOW, all as in v5, all disclosed):
- N03: certificate bytes substituted with the sha256 updated (row 139 (c)).
- X02b: PREDICT 068 and 070 outcomes changed (NOT_RECHECKED by design).
- X04b: a handwritten minimal receipt checked without the published hash. With the hash (X04c) it is refused.
- X08: L1's certificates dressed in D1's receipt checked without the hash. With the hash (X08p) it is refused. Row 139 (a).
- X07b and X11b: the rehearsal protocol was rewritten consistently. The PROTOCOL row of a rehearsal is self-declared, while the r9 protocol is the checker's constants (row 144 `open`).

## D. Full-size reproduction

- Launcher (`d_full.sh`, unit floor-v6-d13): 13:48:21Z to 17:11:23Z.
  - The run took 3 h 23 min, longer than in v5, because the host was shared with other `/root/ymleaf` jobs.
  - Command: `env -i … run_floor.sh --test-r 21/2 --test-m0 11,12,13 --test-f '1;8,7,6,5,4;6,5,4,3' --test-census --test-hang 1:cert,2:cert --test-g0 99372/1000`.
  - m0 = 11 and m0 = 12: OPFAIL by the injected cert timeout.
  - m0 = 13: PREREQ keys b67d54ab… (row 027) PASS; LIMIT HELD.
  - Peaks: writer 1,172,256 kB, rowhash 443,108 kB, verifier MEM 796,380 kB.
  - Certificates at m0 = 13:

    | f word | gamma | Ritz |
    |---|---|---|
    | 1 | 993720/10000 | 99.376500 |
    | 8,7,6,5,4 | 993718/10000 | 99.376429 |
    | 6,5,4,3 | 993718/10000 | 99.376425 |

  - Exit 0, last line `CERTIFICATE=PASS|PREDICTION=CONFIRMED|DECISION=ABOVE|GAMMA=993720/10000|UPPER_BOUND=99376426000000/1000000000000`. These are the same G and U as in v4 and v5.
  - PUBLISH receipt_sha256 was 65c7e7988fd72088a089ec9369cbea16d37ef7ad4440baa44ab2267554c079bf.
  - Host mount sampler: 13,021 samples, floor-run entries 0.
- Checker (from `exp0`, with the published hash):
  - It started at 14:11 local.
  - `RECHECKED` PASS for f = 1 (gamma 993720/10000, Ritz 99376500/10^6) and for f = 8,7,6,5,4 (993718/10000, 99376429/10^6).
  - During the f = 6,5,4,3 recheck the WSL distribution restarted: PID 1 started at 15:07:54 local, and the journal holds a single boot from 15:31:25. The unit and the other jobs on the host ended with it.
  - No RECHECK_VERDICT line, no `.recheck.exit`, no `.done`. I did not cause the restart: I killed no process and ran no wsl shutdown. The cause is not measured.
  - Not retried, per the brief. Rerunning `recheck_floor.py receipt=/root/floor-v6-verify/second/D13/FLOOR-RUN-RECEIPT.hbp receipt_sha256=65c7e798… out=…` from `exp0` (about 75 min or more) settles it.

## Not run or not completed

- The D checker verdict (see above).
- Any r9-mode receipt end to end, and the accepted freeze-argument path.
- A second physical environment.
- New attacks against the row-144 changes, such as a reference in an unreadable pid namespace or a timed bind between the readings. Excluded by the brief.
