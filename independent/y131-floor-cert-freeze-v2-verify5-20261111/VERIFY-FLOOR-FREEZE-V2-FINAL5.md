# Final-head verification 5 of the floor freeze v2 (commit 3c41ea2d)

Verifier seat: opus55, second seat of ACER-CLAUDE-FABLE5 (pid 8467a937cba309f7), model claude-opus-5-5, 2026-11-11.
Lane: WSL2 Ubuntu as root on the acer machine. Fresh clone from GitHub at `/root/floor-v5-verify/repoC`, checked out at
3c41ea2d9dd01de0ffcd547a7e7d417baa2ca6c0 (parent 5eecb540). Attack clones `repoD` (local clone of repoC). Checker runs
always from `exp0`, a `git archive` export of 3c41ea2d. Scripts in `scripts/`, raw row files in `raw/`.
Same physical host as the build seat: separate directories, not a second environment.
r values used: 12, 14, 21/2 only. The only r = 9 contact was `final/tools/freeze_args_controls.sh` exactly as written (11 controls, 11 refused).
`--launch-r9` was never passed. Hot-path rows: `VERIFY-FLOOR-FREEZE-V2-FINAL5.hbp`.

## Verdict

**FAIL.** Gate C has one HIGH finding; gate B has two MEDIUM findings. HOLD stays in force.

| Gate | Result |
|---|---|
| A integrity | PASS (MEASURED) |
| B launcher | FAIL: MEDIUM B2, MEDIUM B5/B7; LOW B3, B6b |
| C checker | FAIL: HIGH X15; LOW X04b, X08, X06d/X07b/X11b, N03, X02b, X02c |
| D full size | PASS (MEASURED): launcher exit 0 ABOVE; checker ACCEPT=YES ABOVE with the published hash, same G and U |

## A. Integrity: PASS

- HEAD 3c41ea2d, equal to `git ls-remote` of the branch; tracked changes 0.
- `sha256sum -c FREEZE-PIN.sha256`: exit 0, 721/721 OK. Regenerated from `git ls-files` of the folder (minus the two FREEZE-PIN files): 0 differing lines.
- Record sha256 561e36b4…cc96e, named in FREEZE-PIN.txt, NOTE and CHANGES.
- Rows 114, 115 and 131 equal the files: run_floor.sh 52036319…, floor_eval.py f92f404f…, recheck_floor.py e28ea393…. These three values also appear in NOTE and CHANGES.
- Byte-identical to 5eecb540: the 16 PREDICT rows (16/16), main.rs, gate_required.sh, cert_gate.py, indep_verify.py, peak_rss.py, Cargo.toml, Cargo.lock, freeze_args_controls.sh. Changed or new rows: 114, 115, 131, 137-141.
- Files changed outside the folder: 0. CR bytes in changed files: 0.
- `python3 -I -X utf8 native/scripts/no_float_gate.py .`: exit 0, `failed=0`.
- Pin-free build (cargo 1.81, `--locked`): 9533e7e9…, equal to row 016. `cargo +1.81 clippy --release -- -D warnings`: exit 0, clippy 0.1.81.
  - My first clippy call was `$TC/cargo clippy`. It resolved `cargo-clippy` from `~/.cargo/bin` (clippy 1.96) and failed with 4 lints. That is a harness error of this seat, not the owning gate.

## B. Launcher: FAIL

Refused as claimed:
- B1 (C4 rebuilt; a holder process in a private namespace, then `nsenter -t HOLDER -m`): exit 4, `reason=mount_namespace_is_held_by_another_process`, no run directory.
- B3b (nsenter by the launcher's own pid, staying past the close): exit 1, `close=another_process_sits_in_the_mount_namespace`.
- B4 (E4 rebuilt; untracked `work/design/rs/.cargo/config.toml`, frozen build) and B4b (the same file at the repository root): exit 1, `cargo_configuration_file_in_the_Rust_folder_or_above_it`.
- B6 (E3b rebuilt; tracked .md outside the folder modified): exit 1, `tracked_files_differ_from_the_commit`.
- B8 FZA on the B0 frozen binary (62dd2f6b…): exit 0, 11/11 refused; W0-W5 exit 3, V1-V5 exit 1; no FREEZE, CERT, ROWHASH or ENUM line; no run directory.

**MEDIUM B2. The C4 fix is bypassed by a namespace that no process holds.** The namespace is kept alive by a bind mount of its nsfs file:

    mount --bind nsd nsd; mount --make-private nsd; touch nsd/mnt; unshare --mount=nsd/mnt --propagation private true
    env -i PATH=/usr/bin:/bin LANG=C FLOOR_STAGE=2 FLOOR_ROOT=$FD nsenter --mount=nsd/mnt bash --noprofile --norc -c "$SRC" run_floor.sh --test-r 12 ...

- Result: exit 2, CERTIFICATE=PASS, and the run log says `other_processes_in_this_namespace=0`.
- Afterwards the held namespace still had both floor-run tmpfs mounts. Re-entering it listed `PREDICT-…hbp, floorcert, gate_required.sh, py`.
- Why: `ns_others` lists processes only. A bind-mounted `/proc/PID/ns/mnt` reference is not a process. Stage 1 is skipped and FLOOR_ROOT is chosen by the caller.
- This is the same exposure as C4 (needs root), now with the record of row 139 claiming it is closed.
- Fix: refuse a direct stage-2 entry outright. For example, stage 1 can pass a one-time token through an inherited file descriptor that stage 2 requires. Or check `/proc/self/mountinfo` of the parent of `unshare`, or require stage 2's parent process to be the unshare of stage 1.

**MEDIUM B5 / B7. The E4 fix is bypassed by a workspace root above the crate.**
- B5 setup:
  - an untracked `work/design/Cargo.toml` with `[workspace] members=["rs"]` and `[profile.release] opt-level=2, overflow-checks=false`;
  - a copy of Cargo.lock beside it.
- B5 result: the frozen build ran with them. Cargo printed "profiles for the non root package will be ignored". The frozen binary was 3590c544…, not B0's 62dd2f6b…. The run gave exit 2, CERTIFICATE=PASS.
- Why it is not caught:
  - the walk-up looks only for `.cargo/config*`;
  - the untracked check covers `work/design/rs` only;
  - the whole-repository status uses `--untracked-files=no`.
- B7 committed the same two files as a local descendant commit a324ebd of 3c41ea2d, so they were tracked. The launcher took freeze commit 3c41ea2d from `git log -- PREDREL` and found the status clean. The frozen binary was again 3590c544…, and the run gave CERTIFICATE=PASS.
  - The launcher never requires HEAD to equal the freeze commit. "The tracked files of the whole repository must be unchanged" is checked relative to HEAD, not to C.
- Soundness of certificates is unaffected: the verifier is independent of the writer. What is broken is the row-139 claim that only the pinned source, Cargo.toml and Cargo.lock reach cargo.
- Fixes:
  - require `git rev-parse HEAD` = C;
  - refuse any `Cargo.toml` in any directory above `rs`;
  - run `git ls-files --others` over the whole repository;
  - or build from a `git archive C` export into the tmpfs.

**LOW B3.** A root `nsenter -t <launcher pid> -m` after the start and after-mount checks, leaving before the close, is not detected. The run gave exit 2, PASS, and the entering process listed the private tools.
- Separately, without entering, `ls /proc/<launcher pid>/root/<run>/tmp/tools` and `sha256sum` of `gate_required.sh` from the host succeeded during the documented D13 run (MEASURED, `scripts/b_procroot.sh`).
- This contradicts the launcher header ("a process outside the namespace sees neither"). It is inside the root windows (4) and (6) of row 127.

**LOW B6b.** The modification of B6, hidden with `git update-index --assume-unchanged`, gives status 0 lines and exit 2, PASS. No effect on the build was measured (the file is not read by cargo). It shows that git status is not a tamper check.

## C. Checker: FAIL

Genuine receipts, all ACCEPT=YES with the launcher's own decision:

| Receipt | Run | Launcher | Checker |
|---|---|---|---|
| D1 | r = 14, m0 = 7 | ABOVE | YES |
| D1 with published hash | r = 14, m0 = 7 | ABOVE | YES |
| D2 | m0 = 7, 8 | BELOW at m0 = 8 | YES |
| D2 with published hash | m0 = 7, 8 | BELOW at m0 = 8 | YES |
| D3 | m0 = 7 | BELOW | YES |
| D4 | f = 1 | UNRESOLVED | YES |
| U2 | m0 = 7, 8 | UNRESOLVED | YES |
| H1 | m0 = 7 OPFAIL by injected hang, then m0 = 8 | BELOW | YES |

Rebuilt forgeries from verification 4, now refused (ACCEPT=NO, exit 1):

| Control | Refusal reason |
|---|---|
| X02, all scores set to MET | `PREDICT_SCORE_rows_differ…` |
| X03, STEP set to EXCEEDED | `STEP_row_m0_7_does_not_read_2_accepted,_resource_limit_HELD,_bad_none` |
| X04, minimal handwritten | `rehearsal_receipt_has_0_PROTOCOL_rows` |
| X05 | header differs from file name |
| X06, m0 = 8 certificates removed | `step_m0_8_carries_the_f_words_[none]…` |
| X07, foreign f word | `step_m0_7_carries_the_f_words_[1 ; 4,3,2,1]_and_the_protocol_calls_for_[1]` |
| X01, duplicate verdict keys | `a_verdict_row_repeats_a_field` |
| N12 | `RECHECK_row_m0_7_f_1_differs_in_gamma_or_a_Ritz_value` |

All of N01, N02, N04-N11, N13-N18, N20, N21, N23-N27 were also refused.

New forgeries, refused:

| Control | Refusal reason |
|---|---|
| X06b, step 8 dropped | UNRESOLVED with a step that did not run |
| X06c, step 8 marked OPFAIL | UNRESOLVED with a step that did not run |
| X09, a step after ABOVE | `a_step_follows_m0_7,_where_the_result_was_already_ABOVE` |
| X10, UNRESOLVED with step 8 removed | refused |
| X11, PROTOCOL g0 only | `g0_of_the_receipt_differs_from_the_protocol` |
| X14, RECHECK rows swapped | refused |
| X01s, X01r, X01e (duplicate fields in STEP, RECHECK, RECEIPT) | refused |
| X01p (duplicate PROTOCOL field) | refused |
| X13, X13b (wrong or malformed receipt_sha256) | `receipt_differs_from_the_published_receipt_sha256` |
| X04c (handwritten receipt checked against the D1 published hash) | refused |
| X08p (X08 checked against L1's published hash) | refused |
| X12, X12b, X12c (test receipt presented as r9) | refused before any gate ran (`gates_run=0`) |

**HIGH X15. A falsification is turned into an accepted UNRESOLVED with weaker but valid certificates.** This contradicts row 139 (d), "a host … cannot turn it into an accepted one", and the reading of ACCEPT=YES in row 138.
- D3 was BELOW (FALSIFIED) at r = 14, m0 = 7, g0 = 112: U = 111239467/10^6 from the f = 4,3,2,1 certificate.
- I replaced the class vector of that certificate with the vector of the f = 1 certificate and set `t=1022056/10000` (`scripts/weaken.py … vfrom …`).
- The pinned verifier passes it: `VERDICT|PASS`, Ritz 121.307597. Both the Rayleigh quotient of any positive vector and any smaller t are valid bounds.
- `scripts/forge.py` then rewrote the receipt fields from the checker's own output.
- Checker: exit 0, `ACCEPT=YES|DECISION=UNRESOLVED`, G 1022056/10000, U 121307598000000/10^12, reasons none. X15t (t = 100/1) gave the same result.
- Why it works:
  - the checker accepts UNRESOLVED whenever all steps are complete;
  - an upper bound is only as good as the vector the certificate brings, so a host can always raise U above g0;
  - a lower bound is only as good as the t it claims, so a host can always lower G under g0.
- At r = 9 the same move needs the host to also produce weakened m0 = 12 and 13 certificates with a frozen binary. Row 008 forbids those r = 9 invocations, but nothing in the receipt can show them (CONJECTURE for r = 9; MEASURED at r = 14).
- The published hash does not help, because the host publishes after it rewrites.
- ABOVE→BELOW and BELOW→ABOVE stay impossible: the verifier is sound.
- Fix direction:
  - the checker reruns the frozen writer and compares certificate bytes (provenance);
  - or UNRESOLVED is never accepted, and only ABOVE or BELOW stand on certificates;
  - or the checker computes its own canonical U and G.

LOW, disclosed or rehearsal-only (each ends ACCEPT=YES):
- X04b: a handwritten receipt that contains only the rows the checker reads, around D1's certificates (no published hash). With the published hash it is refused (X04c).
- X08: run L1 failed with RESOURCE_LIMIT_EXCEEDED (`--test-limit-kb 5000`) and left its certificates on disk. Dressed in D1's PASS receipt, it is accepted. With L1's published hash it is refused (X08p). Covered by row 139 (a).
- X06d, X07b, X11b: hiding BELOW by setting PROTOCOL m0_steps=7, splicing a foreign f word after rewriting PROTOCOL f, and changing g0 consistently. All are accepted, because a rehearsal's protocol is self-declared. At r9 the protocol is constants (by inspection, lines 285-293). Rehearsal acceptances therefore cannot be used as evidence that the checker detects protocol rewrites.
- N03: certificate bytes substituted with the sha256 updated; accepted (row 139 (c)).
- X02b: PREDICT 068 and 070 outcomes changed; accepted (NOT_RECHECKED by design).
- X02c: a PREDICT_SCORE row without `row=` gives a Python TypeError at line 553 (`sorted(srec)` with a None key). Exit 1 with no RECHECK_VERDICT line. It fails closed, but the last line is not the documented one.
- By inspection:
  - in r9 mode the PROTOCOL row's duplicate-key flag is not checked (lines 309-312). There is no effect, since the protocol is constants;
  - `commit=` is not bound to the checkout the checker runs in.

## D. Full-size reproduction

**PASS (MEASURED).** The launch, from the fresh clone (`scripts/d_full.sh`, systemd unit), ran from 2026-11-11T23:19:45Z to 2026-11-12T01:42:54Z:

    env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh --test-r 21/2 --test-m0 11,12,13 --test-f '1;8,7,6,5,4;6,5,4,3' --test-census --test-hang 1:cert,2:cert --test-g0 99372/1000 --test-out /root/floor-v5-verify/out/D13

- m0 = 11 and m0 = 12: OPFAIL by the injected cert time limit (`bad=cert_command_timeout`).
- m0 = 13: the row 007 prerequisite held.
  - Keys sha256 b67d54ab…, equal to row 027.
  - The rows-only verifier ran for 2181 s.
  - The LIMIT line read HELD.
- Peaks: rowhash 443,216 kB, writer 1,172,028 kB, verifier MEM 796,372 kB.
- The three certificates:

| f word | gamma | Ritz |
|---|---|---|
| 1 | 993720/10000 | 99.376500 |
| 8,7,6,5,4 | 993718/10000 | 99.376429 |
| 6,5,4,3 | 993718/10000 | 99.376425 |

- Launcher: exit 0, `CERTIFICATE=PASS|PREDICTION=CONFIRMED|DECISION=ABOVE|GAMMA=993720/10000|UPPER_BOUND=99376426000000/1000000000000`, `steps_ok=13`, `operational_failures=11,12`. These are the same G and U as verification 4 and the build seat's D13.
- PUBLISH receipt_sha256 was 1535caf8292ba00cc949c8dc329282ec505ddafcdb6760f8a373c3cec10325fd.
- Host mount table: 9,175 samples, floor-run entries 0.
- Checker pass: the run directory was copied whole without tmp/ or target/, and the checker ran from the `exp0` export with `receipt_sha256=` set to the published value. It ran from 01:42:52Z to 02:56:59Z, about 74 minutes.
  - Result: exit 0, `RECHECK_VERDICT|ACCEPT=YES|DECISION=ABOVE|PREDICTION=CONFIRMED|GAMMA=993720/10000|UPPER_BOUND_VERIFIER_ONLY=99376426000000/1000000000000`.
  - It reported `steps=11:NONE,12:NONE,13:OK`, 3 certificates rechecked with the same gamma and Ritz values, and verifier MEM max 796,972 kB.

## Not tested

- Any r9-mode receipt end to end: forbidden, since it needs r = 9 certificates.
- The accepted freeze-argument path.
- A second physical environment.
- X15 at r = 9: the r = 9 analogue stays CONJECTURE.
- Window (4) of row 127 in its tool-swap form: I did not remount or exchange a tool.
- B2 combined with a tool exchange.
