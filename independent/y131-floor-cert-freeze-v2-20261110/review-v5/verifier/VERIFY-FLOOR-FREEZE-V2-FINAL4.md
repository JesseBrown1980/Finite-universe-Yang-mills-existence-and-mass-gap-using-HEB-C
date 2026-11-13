# Final-head verification 4 of the floor freeze v2 (commit 5eecb540)

Verifier seat: opus55, second seat of ACER-CLAUDE-FABLE5 (pid 8467a937cba309f7), model claude-opus-5-5, 2026-11-11.
Host and lane: the acer machine, WSL2 Ubuntu as root, scripts in `C:/tmp/opus55/floor-v2-verify4/`, work tree `/root/floor-v4-verify`.
Toolchain: rustc 1.81.0 (eeb90cda1), cargo 1.81.0, clippy 0.1.81, python 3.12.
This is the same machine the build seat used. My clones and exports are separate directories, but they do not count as a second environment.
Every r used here was 12, 14 or 21/2. The only contact with r = 9 was `freeze_args_controls.sh` exactly as written: 11 controls, 11 refused.
The hot-path rows are in `VERIFY-FLOOR-FREEZE-V2-FINAL4.hbp` (sha256 in its sidecar).

## Verdict

**FAIL against item D (gates 2 and 3, the checker).** HOLD stays in force.
- Items A, B, E and F: PASS.
- Item C: PASS for the documented entries. One MEDIUM finding: an nsenter entry into a held namespace runs.
- Item D: the checker reproduces honest decisions exactly. It also gives ACCEPT=YES to receipts whose decision differs from the run that produced the certificates.

| Item | Result |
|---|---|
| A integrity | MEASURED_PASS. HEAD 5eecb540, tree clean, 611/611 pins OK, record 908373eb. Rows 001-113 and 116-130 match 78c89c31 byte for byte (128/128), and so do the 16 PREDICT rows. The five tool files are unchanged. |
| B toolchain | MEASURED_PASS. The pin-free binary built in two clones is 9533e7e9… on both, equal to row 016. `cargo +1.81 clippy --release -- -D warnings` exits 0. The no-float gate exits 0 (failed=0). Lint gives 301 errors on the export, 300 on the build tree, and its error lines are identical to `lint_result.txt`. |
| C namespace | MEASURED_PASS, with one MEDIUM finding (see below). |
| D checker | MEASURED_FAIL. HIGH findings below. |
| E frozen build | MEASURED_PASS, with one MEDIUM finding (see below). |
| F full size | MEASURED_PASS. Figures below; the checker verdict is in the F section. |

## C: namespace (gate 1)

Refused with exit 4, no run directory and no floor-run mount on the host:
- direct entry with no unshare (C1, output byte-identical to the build seat's NS1);
- unshare with shared, slave or unchanged propagation (C2, byte-identical to NS2);
- a parent shell in the same private namespace (C3);
- FLOOR_STAGE and BASH_EXECUTION_STRING faked in the caller's environment (C6);
- `bash -c` started without stage 1 (C7);
- BASH_ENV set (C9);
- an extra environment name on direct entry (C10);
- a run directory that is a symlink, or one that resolves into the repository (C8).

The normal run C0 sampled the host mount table every 0.1 s: 379 samples, never a floor-run entry. The full-size run F sampled it every 1 s: 8,271 samples, also none.

**MEDIUM (C4).** A direct stage-2 entry with `nsenter -t HOLDER -m` into a private namespace held by another process is not refused:
- it ran to CERTIFICATE=PASS (exit 2) and printed `mount_namespace=private_CHECKED`;
- while it ran, the private tools (floorcert, gate_required.sh and the record copy) could be listed from outside through `/proc/HOLDER/root`;
- both tmpfs mounts stayed alive in the holder's namespace after the run.

The check compares namespace ids with the parent process and with process 1, so it cannot see who else holds the namespace. This needs root (window (4) of row 127).

**LOW (C5).** A nested private namespace without stage 1 also runs. It is isolated, but it skips the stage-1 checks, and FLOOR_ROOT is chosen by the caller.

## D: checker (gates 2 and 3)

By inspection of `recheck_floor.py`:
- G comes from its own VERDICT line (lines 293-299, 326-328) and U from its own RITZ_CLASS_VECTOR line (lines 300-301, 329-332).
- The decision is made at lines 351-362.
- The receipt's GAMMA, UPPER_BOUND, UPPER_BOUND_VERIFIER_ONLY, DECISION and PREDICTION are compared only after that, at lines 367-394.
- Each RECHECK row is run once. Duplicate and unlisted rows are refused.

LOW notes from the same reading:
- VERDICT_FIELDS is read at lines 334-338, before the decision, and gives g0 in test mode. The row-133 sentence saying it is read only afterwards is therefore inexact.
- The verifier's MEM value is printed but never blocks; there is no check against 2,097,152 kB.

Honest receipts, rerun from a clean export:

| Run | r and m0 | Launcher decision | Checker |
|---|---|---|---|
| D1 | r = 14, m0 = 7 | ABOVE, G 1109058/10000, U 111239467000000/10^12 | ACCEPT=YES, same G and U |
| D2 | r = 14, m0 = 7 then 8 | BELOW, G 1109962/10000, U 111041467000000/10^12 | ACCEPT=YES, same G and U |
| D3 | r = 14, m0 = 7 | BELOW | ACCEPT=YES, same |
| D4 | r = 14, m0 = 7 | UNRESOLVED, G 1022056/10000, U 121307598000000/10^12 | ACCEPT=YES, same |
| E1 | r = 12, m0 = 7 | UNRESOLVED | ACCEPT=YES, same |

My own controls on these receipts: 29 tampered receipts were refused with exit 1 or 4 (D_NEG_REFUSED in the .hbp), and the unmodified copy N00 gave ACCEPT=YES as expected.

The checker gave a wrong ACCEPT=YES in these controls (the sidecar was rewritten each time; it is a plain sha256 that anyone can recompute):
- **HIGH X06: a falsification is hidden.** D2 was BELOW at m0 = 8. I removed both m0 = 8 certificates and their rows. Result: ACCEPT=YES, DECISION=UNRESOLVED, even though the m0 = 8 STEP and DECISION rows saying BELOW are still in the receipt.
- **HIGH X07: a certificate the run never produced decides the result.** D4 ran f = 1 and was UNRESOLVED. I added the f = 4,3,2,1 certificate from D1. Result: ACCEPT=YES, ABOVE, CONFIRMED.
- **HIGH X08: a failed run is accepted.** A run the launcher failed with RESOURCE_LIMIT_EXCEEDED (CERTIFICATE=FAIL, no RECHECK rows) was rewritten as a PASS receipt. Result: ACCEPT=YES, ABOVE.
- **HIGH X04: a hand-written receipt is accepted.** Eight hand-written rows around real certificates gave ACCEPT=YES.
- **HIGH X02: the 16 prediction scores are not checked.** All 16 PREDICT_SCORE outcomes set to MET gave ACCEPT=YES.
- MEDIUM:
  - N03: certificate bytes substituted, with the sha256 updated; it still verifies, ACCEPT=YES.
  - N12: a non-minimal ritz_writer value altered; ACCEPT=YES.
  - X01: duplicate keys; a BELOW receipt carrying a trailing DECISION=ABOVE gave ACCEPT=YES.
  - X03: STEP rows changed to resource_limit=EXCEEDED; ACCEPT=YES.
- LOW, X05: the file name's f word differs from the certificate header; ACCEPT=YES.

What the controls show:
- ACCEPT=YES certifies that the listed certificates verify and imply decision D.
- It does not certify that the frozen protocol produced D: the m0 steps 11/12/13, the three frozen f words, the fallback rules of rows 006/007, the memory limit, or the scores.
- At r = 9 the same gap is open to anyone holding a frozen binary. Any 40-hex commit can be compiled in with the record hash.
- This contradicts the control of row 127 ("a false acceptance on the launching host does not survive that rerun") and the reviewer's gate 2 requirement to "independently reproduce ABOVE, BELOW or UNRESOLVED".

Suggested fix for r9 mode:
- Require m0 to be in {11, 12, 13} in order, with exactly the three frozen f words per step, each matching both the certificate header and the file name.
- Recompute the step sequence of rows 006/007 and the PREDICT_SCORE rows from the checker's own values.
- Check the verifier's MEM against the limit.
- Publish the receipt sha256 out of band at the end of the run.

## E: frozen build (gate 4a)

By inspection:
- In main.rs, `cert()` builds the r-independent tables, then calls `r_policy` for every r, then `build()`; every refusal exits the process.
- In cert_gate.py, the `r9_frozen_mode` gate (lines 194-209) comes before enumeration (line 215 onward).
- So every refusal comes before enumeration, row construction and certificate generation.

E1 (`--test-frozen-build`, r = 12):
- found freeze commit 5eecb540 with blob 908373eb;
- pin checks 1 and 2 both gave 22 rows, 0 bad;
- frozen binary 7461f0fcef67faceff8ea3fa45b94be76e83f216c17c4ba93946d5a6961457ce, which is not the row-016 binary;
- the same bytes came out of a second clone;
- ended CERTIFICATE=PASS with exit 2, and the checker gave ACCEPT=YES.

This binary is compiled with the real commit and record hash, so it should be the production r9 binary (NAMED). It is still on disk at `/root/floor-v4-verify/out/E/E1/target/release/floorcert`.

Refusals:
- wrong commit (78c89c31, or a bogus value): exit 1, prediction_record_differs_from_the_freeze_commit;
- a modified tracked file inside the freeze folder: exit 1, tracked_files_differ_from_the_commit;
- `--freeze-commit` without `--test-frozen-build`: exit 4.

FZA on the E1 binary:
- 11 controls, 11 refused;
- W0-W5 exited 3 and V1-V5 exited 1;
- no FREEZE, CERT, ROWHASH or ENUM line, and no run directory.

**MEDIUM (E4).** An untracked `work/design/rs/.cargo/config.toml` changed the frozen binary to 29201c13…. The run still ended CERTIFICATE=PASS, because the check uses `git status --untracked-files=no` and the frozen binary has no expected hash.

**LOW (E3b).** A modified tracked file outside the freeze folder is not refused. The status check is scoped to the folder, and the crate reads nothing outside it.

## F: full-size fallback (gate 4b)

The run was the same as the build seat's D13 except for g0: r = 21/2, `--test-m0 11,12,13 --test-f '1;8,7,6,5,4;6,5,4,3' --test-census --test-hang 1:cert,2:cert --test-g0 99372/1000`.

I set g0 to exactly the expected G. The le boundary therefore gives ABOVE, where the build seat's g0 = 9938/100 gave BELOW.

- Prerequisite at m0 = 13: keys sha256 b67d54ab…, equal to row 027. The rows-only verifier passed with MEM 786,936 kB, and PREREQ status was PASS.
- LIMIT line: HELD, limit_kB=2097152.
- Writer: peak 1,172,012 kB on the cert step (442,976 kB on rowhash).
- Verifier: MEM max 796,712 kB.
- The three certificates at m0 = 13:

| f word | gamma | Ritz |
|---|---|---|
| 1 | 993720/10000 | 99.376500 |
| 8,7,6,5,4 | 993718/10000 | 99.376429 |
| 6,5,4,3 | 993718/10000 | 99.376425 |

- Launcher: exit 0, CERTIFICATE=PASS, ABOVE, GAMMA 993720/10000, UPPER_BOUND 99376426000000/10^12. These are the same G and U as the build seat's D13.
- Host mount table: 8,271 samples, floor-run entries 0.
- The clock stepped back during the run (elapsed_s=-4 at the m0 = 11 cert step). The build seat reported the same.
- Checker verdict on this receipt: exit 0, ACCEPT=YES, DECISION=ABOVE, G 993720/10000, U_verifier_only 99376426000000/10^12, 3 certificates rechecked, checker verifier MEM max 797,136 kB, receipt sha256 59b2c7832cef563d…. The checker took about 75 minutes.

## G: how honest rows 132-135 are

Reproduced: NS0-NS3 (NS1 and NS2 byte for byte), FB1-FB3, FB5, FZA 11/11, the RK/RA/RFB1/RD13-class acceptances, and the N1-N21-class refusals.

Omitted from those rows:
- the nsenter entry C4;
- the checker's lack of protocol binding (X02-X08, N03, N12);
- the untracked cargo config E4.

The claim of row 133 and the row-127 control, that a false acceptance does not survive the recheck, fails under X06, X07 and X08.

## NOT_MEASURED

- XNS: the launcher of 78c89c31 was not run.
- A second environment in the proper sense: same host.
- Any r = 9 computation: prohibited.
- The accepted freeze-argument path: unexercised by design.
