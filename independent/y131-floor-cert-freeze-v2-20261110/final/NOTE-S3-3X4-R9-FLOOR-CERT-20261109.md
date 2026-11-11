# NOTE: frozen prediction for the r = 9 floor certificate on the periodic 3x4 S3 lattice (floor lane, PREDICTION seat)

## VERSION 2 notice (2026-11-10, local build seat)

This folder is version 2 of the freeze. Version 1 is commit `e74d8a46e86034096fd9c9231c87f594f17a93bf`, folder
`independent/y131-floor-cert-freeze-20261110`, kept unchanged as the historical prediction-first record. Version 2 follows
an operational review of version 1 (verifier report under `review-v1/`, verdict HOLD, errata E1-E5) and carries the blind
history of version 1, including the disclosed near-9 critic run of row 093. It claims no new blind history.

The version 2 record is `PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp` with sha256
`adf784483eb89746c95ca17ea0589888da41d2bd2b7f221915d2b2332da23ec7`, 122 rows. Rows 110-122 disclose the review and everything run
for version 2 and pin the launcher. Rows 001, 003, 006, 007, 008, 009, 010, 013, 016, 020 and 070 are revised (006, 007
and 008 keep every version 1 byte and gain one field naming the launcher); the other 98 rows are byte-identical to
version 1 (`review-v1/ROW-COMPARE-V1-V2.hbp`). Every PREDICT row keeps its value, met_if, not_met_if and falsifier.

New hashes: `main.rs` `f173b6833b194a0bab6cab6d0ef30b125993aa70f306050397247ed03e464bc6`, pin-free binary
`9533e7e902ff565641b34d3bdd0c693ffa0b37baa08575283e00429e2c7fa74f`, `gate_required.sh`
`0064ca4654aa8725f2040f8b50b01e95a521966eada0ac75ffdf2ee63b98849c`, `r_scan.sh`
`a666deb720747de4b6e56f104eb477930afde6f0fefcae7a14145a32b6a4b46f`.

The r = 9 run is launched by one command, `bash final/tools/run_floor.sh --launch-r9` (sha256
`123aee3576084a06a259c188d7be423c387d71add70005d35526d18ece5f1286`, with the evaluator `final/tools/floor_eval.py`
`7f135eeee03a6fd8fb0594070ac1c94c76f1448b04f59a199f0e21390536ef06`). It checks the pins, builds the frozen binary, runs rowhash and
cert at m0 = 11, runs the required gate on every certificate, decides rows 006 and 007 in exact rational arithmetic on
verifier-accepted certificates, and ends with one line
`FLOOR_RUN|CERTIFICATE=PASS or FAIL|PREDICTION=CONFIRMED or FALSIFIED or UNRESOLVED|DECISION=ABOVE or BELOW or UNRESOLVED|GAMMA=|UPPER_BOUND=|...|HASHES=`
and a hash-listed receipt. CERTIFICATE says whether the gates and the integrity checks held; PREDICTION says whether
lambda_min(QHQ) >= g0 was confirmed or falsified. A falsified prediction reads CERTIFICATE=PASS, PREDICTION=FALSIFIED,
DECISION=BELOW, exit code 3. An integrity or gate failure reads CERTIFICATE=FAIL with GAMMA=NONE and UPPER_BOUND=NONE.
Record rows 114-117 define it and list its rehearsals at excluded r. The r = 9 mode has never been run; the r = 9
run is on HOLD until this freeze passes review.

Correction round (same day, one commit on top of the first version 2 commit `cfc57befadcb61fb36b992af841941adaecd3fd0`):
the reviewer's rulings and the findings of the separate verifier seat (`review-v2/`) are applied to the launcher and the
evaluator. The Rust source, the binary hash and the 16 PREDICT rows are byte-identical to that commit
(`review-v2/ROW-COMPARE-CFC57BEF.hbp`). Record row 119 lists each finding and its change, row 120 and
`review-v2/MODIFIED-ROWS-V1-V2.hbp` account for the 11 modified rows field by field, row 121 puts the two readings of
rows 006 and 011 at 2 GB before the reviewer, and row 122 records the reviewer's ruling on them: a process that completes
at or over 2 GiB (2,097,152 KiB) gives CERTIFICATE=FAIL with reason RESOURCE_LIMIT_EXCEEDED and no fallback; a timeout or
a crash may trigger fallback only when the applicable REQUIRED gates have not failed. The launcher runs private, hashed,
read-only copies of the gate driver, the verifier, the peak wrapper and the evaluator, and a certificate is accepted only
with the record of a verifier invocation that exited 0 (row 122). `review-v2/rehearsal-v2b/` holds the swap of the gate
driver as found against the first version 2 commit (X1) and its rejection by this launcher (Y1, Y1b, P1).

Second correction round (same day, one commit on top of `3b91d1a047d7485693c754ece8c7c18f43fbf326`): the final-head verification of
that commit returned HOLD (`review-v3/VERIFY-FLOOR-FREEZE-V2-FINAL.md`). The verifier seat obtained CERTIFICATE=PASS lines
from the launcher of that commit with no genuine verification, four ways: a program named `python3` placed ahead of the
system directories in PATH (T1), the variable BASH_ENV (T2), and a swap of the private copy of the gate driver (T3) or of
the evaluator (T4) between its hash check and its start. The launcher and the evaluator are changed; the Rust source, the
binary hash, `gate_required.sh`, `cert_gate.py`, `indep_verify.py`, `peak_rss.py` and the 16 PREDICT rows are
byte-identical (`review-v3/ROW-COMPARE-3B91D1A0.hbp`). The record now has 130 rows and sha256
`41ced0bb2ad9b4078153f4264c46ba6c767994ecbd774c47efd6b20188bdefdc`; the launcher is
`8d1f01cfb85f19ce596baa63e245ab96298fe1c8c74db2afebaff27d387c9059` and the evaluator
`c237a54a0d1e85ee4d22230d532a86ad336535cd3feeb1087da6e4804c6e4278`. The record hash, the launcher hash, the evaluator hash and the
row count given earlier in this notice are those of `3b91d1a0`.
One file of the verifier material stays out of the commit: the race program of the swap attacks (race.py, sha256 8e460e45e434d81f9663387e9a13a60594d0cdd5d869296ea40ed4478b790752) imports ctypes, an import the no-float gate lists; it stays out of the commit and is named by that hash in row 129.

What changed (record rows 123-130): the launcher starts itself again under `env -i` with PATH `/usr/bin:/bin` in a mount
namespace of its own, resolves every program once to an absolute path and logs it with its sha256, reads each tool once,
hashes those bytes and runs those bytes (the peak wrapper and the evaluator from memory, the gate driver and the verifier
from a read-only tmpfs inside the namespace), and prints the final line itself from the evaluator's captured output
(row 124). The 2 GiB limit applies to every completed REQUIRED process including the rows-only prerequisite verifier of
row 007, by the reviewer's ruling: at or over 2,097,152 KiB the run ends CERTIFICATE=FAIL, RESOURCE_LIMIT_EXCEEDED
(row 123). Exit codes: 0 PASS and CONFIRMED, 3 PASS and FALSIFIED, 2 PASS and UNRESOLVED, 1 every CERTIFICATE=FAIL of a
started run, 4 NOT_STARTED (row 128).

Remaining risk, disclosed (row 127): the r = 9 run is one run as root on one machine. A concurrent root process on that
machine is outside what a launcher can exclude: it can act before the environment is cleared, change a system program or
library, enter the launcher's mount namespace, or exchange a file and restore it between two hash checks. The control is
row 125: a CERTIFICATE=PASS line is the launcher's own statement, and the result is accepted only after a second,
independent environment has rerun `gate_required.sh` on every certificate listed in the RECHECK rows of the receipt, from
a clean checkout of the freeze commit, and recomputed the verdict fields. The receipt prints the exact command.

Third correction round (2026-11-11, one commit on top of `78c89c312a265fe4090071fc1abdc7d6eb102e7e`): the reviewer's acceptance
review of that commit returned HOLD with four gates (`review-v4/REVIEW-ACCEPTANCE-20261111.md`). The launcher and the
evaluator are changed and a checker is added; the Rust source, the binary hash, `gate_required.sh`, `cert_gate.py`,
`indep_verify.py`, `peak_rss.py` and the 16 PREDICT rows are byte-identical (`review-v4/ROW-COMPARE-78C89C31.hbp`). The
record now has 136 rows and sha256 `908373ebb40979e0d8d49a1b20990fe2c65195ec338dc4424189649850be4d82`; the launcher is
`1d069f79638a10dbdb6c7021a6b57331200d689285b31671b81115f5474ea5ce`, the evaluator
`00cb6334ae13aeb0848423f5132c80abd5978f492ae15575a56aebb1a6b22b04` and the checker `final/tools/recheck_floor.py`
`19b4baf6e6be907a3b878d05a5c472ad4914efffd8aef0ca16a6f17c32f065ba`. The hashes and the row count given earlier in this notice are
those of the earlier commits.

What changed (record rows 131-136):

- Namespace (row 132). Stage 2 of the launcher starts only when its mount namespace differs from that of its parent
  process and of process 1 and holds no shared mount; entered directly it stops with NOT_STARTED, exit 4, before it mounts
  or writes anything. After its two tmpfs mounts it checks that both are absent from the mount tables of the parent
  process and of process 1. Only then does the run log say the namespace is private.
- Independent verdict (rows 131 and 133). Acceptance of a result needs the checker, run in a second environment from a
  clean checkout: `python3 -I -B final/tools/recheck_floor.py receipt=RUN_DIRECTORY/FLOOR-RUN-RECEIPT.hbp commit=C`. It
  reruns `gate_required.sh` on every accepted certificate, takes the upper bound from its own verifier output alone,
  decides ABOVE, BELOW or UNRESOLVED, and only then compares with the receipt. Any difference gives ACCEPT=NO.
- Certificate paths (row 133). The receipt names its run directory, and every RECHECK row gives its certificate relative
  to that directory. The checker refuses a missing file, a symbolic link, a path that leaves the directory, a file whose
  sha256 differs, and a certificate file that no row names.
- Frozen build and full-size fallback (row 134). `--test-frozen-build` rehearses the freeze-commit lookup, the frozen
  build and pin check 2 at an excluded r. A full-size rehearsal at r = 21/2 runs the fallback to m0 = 13 with its
  prerequisite and the 2 GiB limit. The freeze options of the writer and of the verifier are read at r = 9 only and stay
  unexercised until the run.

The rehearsals of this round are listed in row 135 and kept under `review-v4/rehearsal-v2d/`. Nothing was run at r = 9 or
within 1 of it. The r = 9 run stays on HOLD until the reviewer accepts this commit with evidence from an independent
environment.

Fourth correction round (2026-11-11, one commit on top of `5eecb540431a1b5665605f68ed81bc701719dcd1`): the fourth final-head
verification of that commit returned FAIL on the checker (`review-v5/verifier/VERIFY-FLOOR-FREEZE-V2-FINAL4.md`). The
launcher, the frozen build and a full-size run to m0 = 13 were reproduced from a fresh clone. The checker accepted
rewritten receipts whose decision the run had not reached: a falsification hidden by removing a step's certificates, a
result decided by a certificate from another run, a failed run rewritten as a pass. The record now has 141 rows and sha256
`561e36b40630485c9f27ee981bb1c03280c63296153fca21c3123703308cc96e`; the launcher is
`5203631998f0ff53d2bfe86dc0307405e42e5b2bd908b2aaf28beef7566ceda8`, the evaluator
`f92f404f117d6d5f20fb8c5d020797060b539d2a0784d2b1d2c851b68ac42a10` and the checker
`e28ea393ba00fb173ef0678a06959b37df17073f81ef9f48c1f5565c1e58afe4`. The hashes and the row count given earlier in this notice are
those of the earlier commits. The Rust source, the binary hash, `gate_required.sh`, `cert_gate.py`, `indep_verify.py`,
`peak_rss.py` and the 16 PREDICT rows are byte-identical (`review-v5/ROW-COMPARE-5EECB540.hbp`).

What changed (record rows 137-141):

- The checker replays the frozen protocol (row 138). It holds r = 9, the steps 11, 12, 13, the three f words and g0 as
  constants. ACCEPT=YES needs every certificate the protocol calls for, no certificate beside them, no step after a
  decision, and its own decision, bounds, per-step values and scores equal to the receipt's. An UNRESOLVED result with a
  step that did not complete is left to the reviewer: the checker ends ACCEPT=NO.
- The receipt hash is published (row 138). The launcher prints `PUBLISH|receipt_sha256=...` before its final line, and the
  checker needs that value for the r = 9 receipt: `python3 -I -B final/tools/recheck_floor.py
  receipt=RUN_DIRECTORY/FLOOR-RUN-RECEIPT.hbp commit=C receipt_sha256=H`.
- The launcher's mount namespace must hold the launcher alone (row 139): another process in it stops the run at the
  start, after the mounts, or at the close.
- The build takes nothing but the pinned files (row 139): an empty CARGO_HOME, no cargo configuration file in the Rust
  folder or above it, no untracked file in the Rust folder, and with a frozen build an unchanged repository.

What stays open is listed in row 139: the writer's peak memory and PREDICT rows 068 and 070 are values of the launching
host; a certificate is accepted on what the verifier proves, whoever wrote it; a root process can still enter the
namespace between two checks. The rehearsals of this round are in row 140 and under `review-v5/rehearsal-v2e/`. Nothing
was computed at r = 9 or within 1 of it. The r = 9 run stays on HOLD until an independent verification of this commit
passes.

The text below this notice is the version 1 note, unchanged. Where it gives the version 1 record hash, the version 1
hashes of `main.rs`, the binary, `gate_required.sh` or `r_scan.sh`, the absolute scratch paths, or the row count 109, the
version 2 record and this notice give the current values. `work/design/NOTE.md` and `work/map/MAP.md` are the pinned
version 1 files, unchanged.

Written 2026-11-09 by the PREDICTION seat of the floor workflow. This note explains the frozen record
`PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp` (sha256 `d06ff237f55a762e7c50087d98a757ed366e749f6a736c9c1793f495efd84041`,
109 rows). Where the two differ, the record wins. Row numbers below refer to the record.

The record is the file whose sha256 is compiled into the frozen binary (`FLOORCERT_PREDICTION_SHA256`). It must not be
edited after that hash is taken. This note and `CHANGES.txt` may be committed beside it. Neither is pinned by the record.

Tags: DERIVED, CONJECTURE, REPORTED, OPEN; REQUIRED for rules; basis=MEASURED for r-independent counts or excluded-r
smoke.

**Rules kept by this seat.**
* Nothing r-dependent was computed at r = 9 or within 1 of it.
* This seat's computations were: sha256 of lane files; a pin-free rebuild of the binary; a text scan for r values; and
  the record lint. None of them depends on r (row 097). The REFIX-2 seat added the wrapper test and two writer-peak
  runs at the excluded r = 21/2 (row 106). The REFIX-3 seat (2026-11-10) made text edits only, plus the lint, its
  controls and the r scan (no run of floorcert or of a verifier).
* Integers only. The lint is `python3 -I -B`, and its token scan finds no `/`, `**`, float literal or forbidden module.
* No repository or GitHub writes. `scratchpad/refute155/` was not read.
* New files: under 100 kB from the first seats; REFIX-2 added about 5 MB (three m0 = 11 and one m0 = 12 certificate
  at r = 21/2, and their key files, in `work/refix2/`).

## 1. What is frozen

The object is an unconditional, lift-free lower bound gamma_cert on lambda_min(QHQ) at r = 9. It comes from the
Schur-Collatz-Wielandt certificate (Theorem S, design NOTE section 2), checked in exact integers by the FIX-1 writer
`floorcert`. It is then rebuilt row by row by the pinned independent verifier `py/cert_gate.py`.

**Run (rows 001-012).**

| step | m0 | classes | when it runs (decided now) |
|---|---:|---:|---|
| 1 | 11 | 34,920 | always, first |
| 2 | 12 | 65,025 | only if step 1 leaves the comparison with g0 undecided, or step 1 failed for an operational reason |
| 3 | 13 | 89,301 | only if step 2 leaves the comparison undecided, or step 2 failed for an operational reason; and only after its r-independent row hash agrees between writer and verifier |

The notation used in the table:
* g0 = 94070673/10^6 (#131's floor).
* "Undecided" means max G < g0 <= U_all. G(m) is the best gated gamma at m0 = m. U_all is the smallest Ritz upper
  bound so far, plus 10^-6 for truncation.
* An operational failure is a crash, a process running over 6 h, or a process going over 2 GB.

The stop rules:
* A REQUIRED failure on an honest r = 9 certificate is **not** an operational failure. It stops the lane, no r = 9 gamma
  is reported, and a new freeze is needed (row 008).
* There is no step with m0 above 13.

Fixed for every step:
* **f set:** `1;8,7,6,5,4;6,5,4,3`, so three certificates per step. All three f are nonincreasing, and their r_star is
  below 9 at m0 = 10..12, so their cap at r = 9 is at least 9(m0 + 1).
* **One shell word:** the f list is passed as a single argument. Typed into a shell it is `--f '1;8,7,6,5,4;6,5,4,3'`;
  the quotes are shell syntax, not part of the argument. Unquoted, each `;` would end the command. Rows 001, 006 and
  007 say so.
* **Run directories (rows 001, 006, 007).** RUN11 must not exist before the row 001 rowhash command. That command
  creates it and writes `RUN11/core_keys_m11.bin`. The cert command then reuses the same RUN11: it loads that keys
  file (`KEYS|loaded=...` expected, and no writer ENUM line) instead of enumerating. RUN12 and RUN13 work the same
  way. The exact rowhash-then-cert sequence in one new directory was dry-run at the excluded r = 21/2, m0 = 11
  (row 108): rowhash and keyshash equal rows 028 and 025, the cert loaded the keys, and the three certificates are
  byte-identical to those of rows 105 and 106.
* **Peak memory from outside (rows 001, 011, 103).** Every r = 9 FB command (cert and rowhash) runs as
  `python3 -I -B work/design/peak_rss.py FB ...`. The wrapper execs FB with the same arguments and, after FB exits,
  appends one `PEAK_RSS|kB=...` line from `wait4` (the kernel's high-water mark). That line is the writer's peak. The
  writer's own `hwm=` fields are printed only at the ENUM and ROWS stages and are not peaks: at r = 21/2, m0 = 11 the
  ROWS field read 174,584 kB against a true peak of 440,480 kB (row 106). The verifier's MEM line is its true peak.
* **Vector and stopping rule:** the FIX-1 code, unchanged (row 003). It runs at most 10 outer steps,
  `t <- min(t + cw_lo(F(t)), cap - 10^-4)`, and stops when the step is at most 10^-4. Inside, `gs_eigen` runs at most 600
  iterations of 8 Gauss-Seidel sweeps.
* **Not adopted:** the stricter stopping rule suggested in design NOTE section 6. Changing the solver would unpin the
  source and the binary, and skip the plant suite that has already been verified (row 100).
* **Bisection:** exact, with step 10^-4, up to the largest passing t below the cap. The CERT line must report that
  gamma + 10^-4 is refused (row 004).
* **Reported value:** gamma_cert is the largest gated gamma over all steps run and all f (row 005). Every certificate is
  listed with its GATE_REQUIRED line (row 057). The GATE_REQUIRED line does not carry t, so each gated gamma is the
  tn/td of the verifier's `VERDICT|PASS|lambda_min(QHQ) >= tn/td` line, and it must equal both the header `t=` and the
  writer's CERT gamma. Any mismatch falsifies the code (row 008).

**r = 9 mode (row 009).**
* The frozen binary FB is `work/run9/target/release/floorcert`. It is built in `work/design/rs` by
  `CARGO_TARGET_DIR=work/run9/target FLOORCERT_FREEZE_COMMIT=C FLOORCERT_PREDICTION_SHA256=P cargo +1.81 build --release --locked -j1`
  (absolute paths under `scratchpad/floor/`; `work/run9/target` must not exist before the build). C is the commit that
  carries the record, and P is the record's sha256.
* FB is the only binary that rows 001, 006 and 007 run. The frozen build never writes `work/design/rs/target`, so the
  non-frozen binary pinned in row 016 (`0432b8265b88921e`) stays untouched. Checked with dummy pins:
  `refix1/targetdir_test.txt` (the dummy-pinned binary was never run and was deleted).
* The writer refuses r = 9 unless three things hold: the pins are compiled in, the arguments equal them, and the
  `--prediction` file hashes to P. It then prints `FREEZE` with its own binary sha256 and writes `freeze=` and `pred=`
  into every header.
* `cert_gate.py` refuses r = 9 unless its own three arguments agree with the header.
* Limit of the verifier's r = 9 mode (row 009). It checks only that its arguments agree with the header and that the
  `--prediction` file hashes to P. It cannot tell that C is a real commit, or that the header was written by FB: the
  critic/2 seat passed its r_policy gate with a hand-made header and a made-up C. The binding of an r = 9 certificate
  to FB rests on the writer's compiled pins, the ban on other r = 9 invocations (row 008) and the FB hash checks of
  row 018.
* The frozen binary's hash cannot be known before the freeze. It is recorded from the FREEZE line and must be the same
  in every step. `sha256sum` of FB is also logged after the build and before each r = 9 step, and must equal it
  (row 018).
* The pin-free binary is reproducible: a rebuild from the pinned sources into a separate target directory is
  byte-identical to `0432b8265b88921e` (`tools/repro_build.txt`).

**Layout (row 010).** `gate_required.sh` hard-codes the design path and pins the verifier by sha256. So the r = 9 run
uses byte-identical files at those paths. The pin check of every PIN path row (row 016 included, on the untouched
non-frozen binary) is logged twice: before the frozen build, and again after it, before the first r = 9 command.

**m0 = 13 keys file (row 007).** `FB rowhash --m0 13 --dir RUN13`, with RUN13 not existing before it, writes `RUN13/core_keys_m13.bin`. Its sha256 is logged
and must equal row 027. The verifier then reads that exact file (`cert_gate.py --rows-only RUN13/core_keys_m13.bin 13`).

**Pins (rows 013-034 and 103; full sha256 in the record).**

| item | sha256 (16 hex) |
|---|---|
| `rs/src/main.rs` | 7824ed780aa7f15e |
| `rs/Cargo.toml` / `rs/Cargo.lock` | 63026f703d730712 / 964f252c22008671 |
| `peak_rss.py` (outside peak wrapper, row 103) | 9bc36642e5ae03bf |
| binary, pin-free (rustc 1.81.0) | 0432b8265b88921e |
| `py/cert_gate.py` (REQUIRED verifier) | 6043d0897250a7c8 |
| `gate_required.sh` | 13a92ab7562dc8a3 |
| `py/indep_verify.py` (not used at r = 9) | 497d2fbb64eb14e9 |
| critic `class_verify.py` (verifier origin) / `orbit_verify.py` | 756b3a2590293c1a / 5b04b07fd484ede3 |
| design NOTE.md / MAP.md | ac7bb14d0c15e0b7 / de2e240cdaceb90e |
| core_keys m0 = 11 / 12 / 13 | e25b8b392161f6f0 / 942c2eed527aa2c3 / b67d54ab32d0c33a |
| **row hash m0 = 11** (writer = verifier) | 8369f4a981a888f4e028b155f3306371c2eacb421bed9bbc444b86e7ef862884 |
| **row hash m0 = 12** (writer = verifier rows-only) | f835b2e1ded4b7f3f38d9d7f3f8437ebfa0a6ede53783f224ebbd1e9b4b7dee7 |
| #137 package record | 0b97fa83c02e94e7 |

The m0 = 13 row hash was not computed. It is a prerequisite of step 3 (row 007). Being r-independent, it may be
computed after the freeze and before step 3's r = 9 command.

## 2. REQUIRED gates (rows 035-057)

Every r = 9 certificate must pass all of the following:
* **Census per M layer** (rows 035-045). The counts below are exact, and the verifier's cumulative ENUM line must match
  them (1,608,786 / 2,983,071 / 4,123,551 orbits for m0 = 11 / 12 / 13).

  | M | 3 | 4 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
  |---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
  | classes | 3 | 70 | 57 | 552 | 2,066 | 132 | 4,916 | 27,124 | 30,105 | 24,276 |
  | orbits | 36 | 1,320 | 990 | 23,760 | 81,180 | 4,620 | 213,840 | 1,283,040 | 1,374,285 | 1,140,480 |

  Layers 1, 2 and 5 are empty.
* **Completeness:** every row and every tail target accounts for all 72 moves, and the tail and back-move counts equal
  the pins.
* **Class detailed balance:** 725,464 edges at m0 = 11 and 1,610,000 at m0 = 12.
* **Z-sign:** core counts >= 0, and every Schur denominator > 0.
* **Positivity:** f and v are positive, in both programs.
* **Tail cap:** the writer's layer floor and observed-target floor hold. The verifier's own colouring cap must equal the
  header's, and t must be below it. The header cap must be >= 9(m0 + 1) for all three f at m0 = 11 and 12, and for
  f = 1 at m0 = 13. With f = 1 the cap is exactly 108 at m0 = 11 and 118 at m0 = 12. At m0 = 13 the verify seat
  reports (r-independent) r_star = 15/4 with gain 131/8 for 8,7,6,5,4, and r_star = 5 with gain 19 for 6,5,4,3. That is
  information only, not a gate.
* **Symmetry-image gate:** rows rebuilt = 2 x classes (69,840 / 130,050 / 178,602).
* **Link tables:** the link-table, link-multiset and local-Delta-M gates pass, with the pinned check counts.
* **Independent verifier:** `GATE_REQUIRED|PASS`. That needs VERDICT|PASS, the verifier's own row hash equal to the
  header's and to the pin, the pinned verifier sha256, and the same min slack as the writer.
* **Ritz from separate code** (row 052). The certified gamma must be at most min(verifier RITZ_CLASS_VECTOR, writer
  ritz_upper) + 10^-6. A gamma above it falsifies the code, and no gamma is reported.

Row 082 records why the row rebuild is the load-bearing gate. A Ritz check cannot catch a P1b-type fault at large m0:
P1b moved gamma only from 99.3655 to 99.3662 at r = 21/2, m0 = 11.

In the plant receipt, the P1b certificate at (m0; f) = (6; 4,3,2,1), (7; 4,3,2,1) and (7; 1) is byte-identical to the
honest file. Those three PASSes are correct, but they test nothing. The independent gate is shown to refuse the
writer-blind P1b fault only at m0 = 8 (row_check, 269 failing rows) and at m0 = 11 (row 082).

## 3. Predictions (rows 058-073; CONJECTURE unless marked)

| row | quantity | frozen value | basis |
|---|---|---|---|
| 058 | G(11) | >= 80: an unconditional lift-free floor | excluded-r smoke (best f within 0.05 of Ritz at m0 >= 9; f = 1 is not); f = 1 cap 108 at m0 = 11 |
| 059 | G(11) | >= 93.5 | design NOTE section 6 (cap margin about 14) |
| 060 | U(11) | in [94.070673, 94.13] | own Ritz exceeded the best Ritz by 0.013 at r = 21/2 |
| 061 | U(11) - G(11) | <= 0.3 | r = 21/2, m0 = 10 (margin 16.1): 0.182 with f = 1, 0.020 with the best f, 0.049 with the frozen 6,5,4,3 |
| 062 | U(12) - G(12) | <= 0.1 (central 0.01-0.03) | r = 21/2, m0 = 11 (margin 26.6): 0.024 / 0.0072 |
| 063 | U(13) - G(13) | <= 0.05 | r = 21/2 and r = 12 at m0 = 13: 0.0043 and 0.0028 |
| 064 | distance to lambda_min, min(U_all, 94.070936) - G(11) | <= 0.3 | 061 together with #131's REPORTED upper value |
| 065 | every gated gamma | <= 94.070936 (#131's REPORTED Ritz value) | consistency |
| 066 | comparison lean | gamma_cert < g0 at every step (row 012 state UNDECIDED unless U_all < g0) | see below |
| 067 | best f at m0 = 11 | a mild f, strictly above the f = 1 gamma | r = 21/2: 99.3655 against 99.3528 |
| 068 | cap binding | never: gamma <= cap - 10, and next_t_refused names row_check | cap >= 108 against lambda about 94.07 |
| 069 | near monotonicity | G(12) >= G(11) - 0.001 | excluded-r non-monotonicity <= 0.0012 (best f) |
| 070 | resources | each program against its own limit: writer PEAK_RSS < 524,288 kB at m0 = 11 and < 1,048,576 kB at m0 = 12; verifier MEM < 1,048,576 kB at m0 = 11 and < 1,572,864 kB at m0 = 12 | true peaks at r = 21/2: writer 440,480 kB (m0 = 11, three f) and 810,940 kB (m0 = 12, one f); verifier 403,336 kB and 733 MB. The old 175 / 312 MB were ROWS-stage values |
| 071 | location of lambda_min | the final bracket meets [94.07, 94.10] | NOTE section 6 fit |
| 073 | H4 consistency | U_all >= g0 | #131 REPORTED |

Rows 062, 063 and 069 are vacuous (NOT_EVALUATED, not FALSIFIED) if their step is not run.

**Why row 066 leans BELOW.** If #131's bracket is right, lambda_min lies in [94.070673, 94.070936] (REPORTED, via MAP
section 5). Reaching g0 would then need a deficit of at most about 0.00026. The smallest deficit measured at any excluded
r with m0 <= 13 is 0.0026 (r = 14, m0 = 11). So row 066 predicts that all three steps will run (rows 006-007), and that
gamma_cert stays below g0. Row 012 then scores the state UNDECIDED, unless U_all < g0 (BELOW_FALSIFIED_H4). Row 066
predicts only gamma_cert < g0, not a row 012 state.

**Comparison with #131 (row 072, OPEN, read and report).**
* If gamma_cert >= 94070673/10^6, then H4 of #137 (`lambda_min(QHQ_whole) >= g0`) holds unconditionally and lift-free,
  on this certificate alone. #131's value is confirmed as a floor without its sector-to-whole lift and without any #131
  input. #131's own certificate is not thereby audited.
* If gamma_cert < 94070673/10^6, nothing is concluded against #131, because a smaller lower bound refutes nothing. #131
  stays REPORTED and conditional on its rows R1 and R2. This lane still delivers the unconditional lift-free floor
  gamma_cert and the bracket [gamma_cert, U_all].
* If U_all < 94070673/10^6, a certified upper bound refutes #131's floor, H4 at g0 is falsified, and the falsifier of
  #137 row 138 fires.

## 4. The averaging lemma and what it changes (rows 076-079, REPORTED from the review seat)

* **Status.** The review seat proved Lemma A (verdict PASS). The side result is MAP section 6; MAP section 5 is
  Theorem F.
  * Hypotheses: W-symmetry, Z-sign, and the 48 maps acting by basis permutations.
  * Conclusion: lambda_min(sector) = lambda_min(whole), and the class quotient equals the compression to the trivial
    isotypic component.
  * Not needed: irreducibility and Perron-Frobenius.
  * Scope: the trivial character only. It says nothing about #137's odd sector.
* **#131's lift.** Lemma A removes no condition for a Collatz-Wielandt floor. It is redundant with the pointwise
  class-constant lift of PERRON-BOUND section 2. Both rest on R1 (the stored classes are complete and disjoint G-orbits)
  and R2 (each stored row aggregates the representative's 72 moves, with flats dropped), which #152 checks (REPORTED).
  What Lemma A adds is the equality, and a way to transfer non-CW sector bounds. #131 stays REPORTED and conditional.
* **#137 H4.** No #137 prediction changes. H4 is a whole-space floor. A CW bound on the class quotient yields it through
  either route, given R1 and R2. #137 rows 008 and 136 stay as frozen.
* **This lane** uses neither route. Its certificate is lift-free by construction: the core is the full orbit space
  {M <= m0}, v is constant on classes, every orbit's row equals its representative's (row 051), and the tail floor holds
  pointwise.
* **Theorem S review:** PASS. Two minor points are carried:
  * r_star needs a layer gain >= 0, which holds for the nonincreasing f that are frozen;
  * the wording of NOTE 2.4 step 2.

  Theorem F and the cluster floor 3C were not reviewed and are not used.

## 5. Link to #137 row 138 (rows 074-075)

#137 row 138 (REQUIRED in that package) names a second floor: one that is separately frozen and read and reported. This
record is that floor.
* **What is handed over:** gamma2 = gamma_cert, recorded as accepted_source_assumption_2 with this record's sha256 read
  from its freeze commit.
* **How #137 uses it:** #137 re-evaluates its floor-dependent tests at gamma2, after its final evaluation on #131's
  floor. Those rows are INFORMATIVE, never BOUND.
* **If gamma2 >= g0:** by #137 Lemma 11 (row 137), its results hold conditional on this floor alone.
* **If gamma2 < g0:** nothing carries over.
* **Upper bound:** U_all is reported too. If U_all < g0, that is the falsifier of row 138.
* **Release:** the owner rules on any release of a result conditional on gamma2.
* **Lift-free:** this floor needs no lift, because its core lies in the full orbit space.

## 6. Pre-freeze disclosure (rows 085-102 and 104-109)

Every computation in the lane, with the sha256 prefixes of its program and output, is in the record. In summary:

| seat | r values | what |
|---|---|---|
| mapping | none; 21/2, 12, 14, 20 | mhist (closed-form census); cluster floors (cluster_smoke, cluster_refine at 21/2, sanity at 20) |
| design, pre-FIX-1 | none; 21/2, 12, 14, 20 | census to M <= 18; smoke grid m0 = 4..13 and mild f; plants at 12, 21/2, 20; Python checks at 12 and 20; one run at r = 20 (m0 = 12, f = 4,3,2,1) stopped after 15 min; the rstar table went to the terminal only |
| design, FIX-1 | 12, 21/2, none | smoke at r = 12; honest m0 = 11 at 21/2; 56 plant files at 21/2; m0 = 12 row hash; second opinion at 12; one deleted dev plant trial at 21/2 |
| design, FIX-1 refusal tests | 10, 19/2, 90000001/10^7, 8 | refused while parsing, before any computation; no file written |
| critic | 21/2, 12, 20, none | class_verify at m0 = 11 (honest and P1b); orbit_verify at m0 = 6 (r = 20, terminal) and m0 = 7 (r = 12); tail sample and census (r-independent) |
| critic/2 (row 102) | 21/2, none, 9 refused | honest m0 = 11 gate at 21/2; 7 gate runs at 21/2, m0 = 6-8 (4 writer plants, 2 hand-faulted certificates, 1 honest); m0 = 9 row hash (r-independent); r = 9 and r = 41/4 refusal tests on three hand-made one-row headers. No r-dependent arithmetic ran at r = 9; cert_gate.py stopped at class_bijection after the r-independent enumeration |
| critic, **near r = 9** | **90000001/10^7** | one run, `floorcert cert --m0 4` (73 classes, default f), while testing the old guard r > 9. It printed gamma = -0.0001 with cap 0 (trivial) and a crude 73-class Rayleigh value. That value was withheld and no file holds it. It is not recorded here and cannot inform rows 058-073 (row 093). |
| review | 21/2, 12, 20 | 2x2 and 2x3 lattices only; nothing on 3x4 |
| prediction (this seat) | none | hashing, pin-free rebuild, r scan, lint |
| REFIX-1 seat (row 097) | none | text edits of the record and this note, r scan, lint and controls reruns, one dummy-pinned build into a separate target dir (never run, deleted) |
| verify seat 1, attempt 0 (row 104, `work/verify1_0/`) | 12, 14, none | pin check, lint and r-scan reruns, own r_star table (r-independent), nine hand-made controls on the r = 12 m0 = 7 smoke certificate |
| verify seat 1 (row 105, `work/verify1_1/`) | 12, 21/2, none | pin-free rebuilds (byte-identical), smoke at 12, honest m0 = 11 at 21/2 (writer peak 440,844 kB sampled), the row 001 three-f shape at 21/2 with the 6,5,4,3 file gated (PASS), m0 = 13 census, deficits read from the grid |
| records verifier seat 2, folder 0 (row 107, `work/verify2_0/`) | 20, 21, 14, none | lint, controls and r-scan reruns, pin-free rebuild (byte-identical), own r_star table (r-independent), smoke at 20, eleven gated controls on the r = 20 smoke certificates (two of them edited to r = 21, one to r = 14) |
| records verifier seat 2, folder 1 (row 108, `work/verify2_1/`) | 21/2, none | lint and r-scan reruns, pin check, name-bound check of rows 102 and 104-106, pin-free rebuild, the row 001 rowhash-then-cert sequence in one new directory at 21/2 with the f = 1 file gated (PASS) |
| records verifier seat 3 (row 109, `work/verify3_0/`) | pre-listed | the folder of the verifier that checks this file; it did not exist when the record was written, and its files are disclosed in that seat's own receipt |
| REFIX-3 seat (`refix3/`, outside `work/`) | none | text edits of the record and this note, the new lint binding and its controls, the r-scan rerun |
| REFIX-2 seat (rows 097, 106, `work/refix2/`) | 21/2, none | text edits, the new peak wrapper, the rescoped r scan, lint and controls reruns; true writer peaks at 21/2 for the m0 = 11 three-f shape and m0 = 12 one f (certificates not gated) |

The r scan (`tools/r_scan.sh OUT`, receipt `tools/r_scan.txt`) reads every .txt and .log in a fixed list of `work/`
directories (map, design, critic, critic2, review, verify1_0, verify1_1, refix2, verify2_0, verify2_1, verify3_0;
target dirs excluded; a listed directory that does not exist yet is skipped). It looks for `r=a/b` fields and for
`--r` arguments. It reads only .txt and .log files: .out, .err, .sh, .py, .rs, .md, .json and binary files are not
scanned. Those were grepped separately (row 096): r values within 1 of 9 occur in them only as the r = 9 guard
strings of the two programs, a NOTE's disclosed 90000001/10^7 sentence and future r = 9 command, and two .out copies
of the old receipt, none r-dependent. It refuses an output path under `work/` unless the name ends in `.out`, so a
seat confined to its own folder can run the exact script. It names every other `work/` directory on stderr; such a
directory needs its own DISCLOSE row before the freeze. `work/verify3_0` is pre-listed (row 109): its seat writes
scan and lint copies as .out files, so the rerun still matches. The freeze seat reruns it as its
last step, and the rerun must match the receipt byte for byte (row 096). The receipt shows:
* computation lines carry only r = 21/2, 12, 14 and 20, plus r = 21 in two verify2_0 controls (row 107);
* r = 10, 19/2, 90000001/10^7 and 8 occur only in the two FIX-1 refusal files, and in four verify-seat copies of the
  scan receipt (two in verify1_1, one each in verify2_0 and verify2_1). The file list for 10/1 also names
  verify2_0/rstar_v2.txt, where the unanchored match is the tail of `r_star=10/1`, the r-independent threshold of
  f = 4,3,2,1 at m0 = 10;
* r = 9 occurs only in the four critic/2 `r9test` files (three hand-made headers and the verifier's refusal log) and
  those four copies; r = 41/4 only in the critic/2 writer refusal log and those copies;
* the arguments `--r 9`, `--r 18/2` (9, unreduced) and `--r 21/2,9` (a mixed list) occur only in the critic/2 writer
  refusal log, each refused at r9_frozen_mode with exit 3 and no file written, and in the verify2_0 and verify2_1
  copies of the receipt; `--r 20` occurs once, in verify2_0/ctrl/PREDICTIONS.txt.

None of them holds an r-dependent value.

The only r = 9 numbers in the record (row 083) are of these kinds:
* the analytic 9(m0 + 1) and the f = 1 caps 108 and 118, built from r-independent gains, and the solver's start
  t = min(3r, cap - 1) = 27 = 3r (row 003);
* g0 and 94.070936, both REPORTED;
* CONJECTURE values extrapolated from excluded r.

## 7. Files and the lint

| file | sha256 (16 hex) |
|---|---|
| `PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp` | d06ff237f55a762e |
| `tools/lint_hbp.py` (record lint) | 609655a3c6004bdc |
| `tools/lint_result.txt` (0 errors) | 980e0d788ad11d96 |
| `tools/lint_controls.txt` (9 planted record faults, each caught with exactly one error) | 91f2685243eef147 |
| `tools/lint_token_scan.txt` (lint is integer-only) | 30eef93f67e048d7 |
| `tools/r_scan.sh` / `tools/r_scan.txt` | 9ea6158809513727 / 1e6113f86dd1a2e3 |
| `tools/repro_build.txt` | 434795bd6e546d48 |

What the lint checks:
* **Format:** LF, ASCII, no whitespace, the TYPE|key=value|...|json=0 form, sequential unique ids.
* **Fields:** id, quantity, value, tag, met_if, not_met_if and a concrete falsifier on every row; a basis on every
  CONJECTURE; rationals only (no decimals) in value, met_if, not_met_if and falsifier.
* **Tags:** allowed per row type.
* **References:** every internal row reference resolves.
* **Pins:** it recomputes the sha256 of all 19 PIN rows that have a path.
* **Fingerprints, bound by name:** every DISCLOSE row with fingerprints carries a `files=` field of `path@sha16`
  entries, and the lint checks each entry against the sha256 of that named file (307 entries). A row with
  `complete=work/<dir>` must list every file of that folder outside target/ (rows 102 and 104-108). Every other
  16-hex fingerprint in the row (308) must equal one of the row's own entries, so a fingerprint copied onto the wrong
  name, or one naming a file outside the row, is an error. The one exception is the deleted dev verifier
  4c72b3e31eb4a1f2. The `files=` entry is the name binding: the prose next to a fingerprint is descriptive.
* **Counts:** the counts in PREDICTION_END match.

Result: `LINT_RESULT|errors=0`.
