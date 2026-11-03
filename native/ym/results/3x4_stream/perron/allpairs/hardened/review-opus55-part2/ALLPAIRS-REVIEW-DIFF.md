# Second-seat review of the corrected `allpairs`, part two

**Reviewed:** commit `0fd24d31e3abad7c2745a2c3ffa917663418621a`, `allpairs.rs` `5ab04b18…`; the executable that ran on 3×4, `cdb22218…`; the receipts under `native/ym/results/3x4_stream/perron/allpairs/failclosed/` at `fead9ede58cc08d214c396afa70094f0cf2da7a5`, and `PERRON-TWO-SIDED.md` section 5 there.
**Date:** 2026-11-03. **Reviewer:** Claude Opus 5.5 (`claude-opus-5-5`), second seat of ACER-CLAUDE-FABLE5, on OP-JESSE's scope, unblinded for this part.
Claims carry MEASURED, NAMED or CONJECTURE. Part one stays as reported: [`ALLPAIRS-REVIEW.md`](ALLPAIRS-REVIEW.md) `b77f78ec…`. Predictions sit beside outcomes in [`REVIEW.hbp`](REVIEW.hbp), after byte 108,785, and [`REVIEW-part1-as-reported.hbp`](REVIEW-part1-as-reported.hbp) `f19ead4b…` holds the ledger as first reported.

## Verdicts

**Overall: FAIL, on the repeat recipe alone.** The corrected tool closes D1 and D2, and the 3×4 receipts hold. The recipe exits 0 when its judge fails, and it never hashes the sectors.

| # | Question | Verdict | Basis |
|---|---|---|---|
| 1 | Does the diff close D1 and D2 on every path? | **PASS** | 276 runs of 69 attack cases and 83,000 fuzz cases: exit 0 with a gate at OPEN or FAIL, 0 times; exit 0 with no rows read, 0 times. By reading, `real_main` has one path to `Ok(true)`, through `verdict`, and `n = 0` stops before any pass |
| 2 | Does the diff add a defect? | **PASS** | None found in `check_header`, `repeated_key`, `number`, `codes`, `verdict` or the `n = 0` stop. `repro.py` differs on exactly the 6 D1 and D2 rows. Brute-force windows and the replayed controls are unchanged. D3 to D8 stay open, with D8 at 1,592 of 2,912 flipped header bits at exit 0 |
| 3 | Do the receipts support the claims? | **FAIL, on the recipe** | Receipts: 30 of 31 cross-checks equal, and the 31st is one row added after the commit. Judge: sound for what it compares, 136 of 136 one-field faults caught. Recipe: R1 to R3 below |

**Scope.** Ran on the author's machine, from the author's files, with a Windows build and a WSL Linux build. This part read the 3×4 store's bytes zero times. A replay on another machine stays OPEN. The reviewer's model is the one the author's seat reports, so independence here is a separate session and separate code.

## Question 1. D1 and D2: PASS

NAMED, from reading: `allpairs.rs` at `0fd24d3` reaches `Ok(true)` only through `verdict`, which needs `Gate::Pass` on both gates. `run` returns `Err` on `n = 0` before any allocation or pass, and any `n ≥ 1` must read n rows and compare the merkle.

MEASURED, each predicted first:

```
GATE_ATTACK_DONE|cases=69|runs=276|not_met=0|exit0_with_open_or_fail=0|exit0_with_no_rows=0|json=0
FUZZ_DONE|seed=20261105|cases=40000|tool_exit1=14314|tool_exit2=20097|tool_exit0=5589|pass_clean_all_gates=4631|pass_with_n0=0|pass_with_entries_open=0|pass_with_count_open=0|pass_with_nonzero_padding=958|false_pass_main_property=0|disagree_verdict=0|disagree_exit_class=0|disagree_counters_on_ascending_rows=0|cap_variant_counters_on_non_ascending_rows=120|masked_unpaired_on_non_ascending_rows=732|panics=0|secs=119|json=0
FUZZ_DONE|seed=20261106|cases=40000|tool_exit1=14157|tool_exit2=20257|tool_exit0=5586|pass_clean_all_gates=4642|pass_with_n0=0|pass_with_entries_open=0|pass_with_count_open=0|pass_with_nonzero_padding=944|false_pass_main_property=0|disagree_verdict=0|disagree_exit_class=0|disagree_counters_on_ascending_rows=0|cap_variant_counters_on_non_ascending_rows=126|masked_unpaired_on_non_ascending_rows=681|panics=0|secs=120|json=0
```

- **Directed attacks** (`diff/attack_gates.py`, output [`diff/out/attack-gates.hbp`](diff/out/attack-gates.hbp), recorded executable and this seat's build, default cap and cap 1): written forms of `entries=`, `nl=` and `L=` with spaces, CR, NUL, full-width digits, hex, a second `=`; look-alike keys; gates only after the newline; five spellings of `n = 0`; `n` at 2³²−1, 2³², 2⁶⁴−1 and 2⁶⁴; repeats in read and unread fields. All 59 that should fail do, with the same exit on all four runs. A zero-sided lattice over weights summing to 6 reads OPEN, exit 2 ([`diff/out/small-cases.hbp`](diff/out/small-cases.hbp)).
- **The 10 cases at exit 0, each with rows read and both gates at PASS:** the clean store, `entries=` moved, fields reversed, a CR on the unread last field, a contradiction after the newline, look-alike keys left unread, repeated parts with no `=`, `L=1x4` on 2×2, bad UTF-8 in `sector=`, and every weight times 6 under `L=1x5|nl=10`. The last two are D8 and D6, still open: the gate reads V and the header is under no hash.
- **The harness** is the corrected source with `main` renamed, plus an oracle holding the new contract in its own code ([`diff/harness_tail.rs`](diff/harness_tail.rs)). The generator adds repeated keys, other written numbers, look-alike keys, relabels and zero-row forms, on half of all stores.
- **Reproducers on the corrected tool** ([`diff/out/repro-pin.hbp`](diff/out/repro-pin.hbp)): `D1_header_only_n0` and `D1_changed_byte_unrepaired_n0` give exit 1, `reason=n is 0, so there are no rows to read and no merkle to compute`. The four D2 rows give exit 2 with the gate printed at OPEN.

## Question 2. New defects: PASS

MEASURED, each predicted first unless named:

| Check | Result | Output |
|---|---|---|
| `attack/repro.py` on `cdb22218…`, on this seat's build, and on the Linux build | 6 of 21 rows differ, the D1 and D2 rows. All C, D3, D5, D6, D7 and D8 rows as at `f4ea7e85…`. Windows and Linux rows identical apart from `secs` | [`repro-pin.hbp`](diff/out/repro-pin.hbp), [`repro-linux.hbp`](diff/out/repro-linux.hbp) |
| `attack/brute_windows.py` on `cdb22218…` | 1,345 store-and-cap runs, 0 disagreements | [`brute-windows-pin.hbp`](diff/out/brute-windows-pin.hbp) |
| The author's 40 `allpairs` control runs on `cdb22218…` | 72 of 72 rows of the original `CONTROLS.hbp` identical apart from `secs` | [`replay-controls-pin.hbp`](diff/out/replay-controls-pin.hbp) |
| The author's header controls, rerun | Byte-identical to the committed `HEADER-CONTROLS-PIN.hbp`, `175f14d2…` | [`header-rerun/`](diff/out/header-rerun/HEADER-CONTROLS.hbp) |
| Unit tests and gate at `0fd24d3` | 19 of 19. `cargo +1.81 clippy --release --all-targets --locked -- -D warnings` exits 0 | [`REVIEW.hbp`](REVIEW.hbp) |
| Own build from a `git archive` | Normal hash `953fa422…`, equal to `cdb22218…` and `d78f263f…`. 24 bytes differ, the PE stamps and the PDB GUID. No machine path in the file | [`pe-normal.hbp`](diff/out/pe-normal.hbp) |

**Would the tests turn red?** MEASURED, a fault in a copy of the tool ([`diff/out/mutate-tool.hbp`](diff/out/mutate-tool.hbp)): the old rule fails 2 unit tests, no header check 1, an empty store allowed 1, lenient numbers 4, as `PERRON-TWO-SIDED.md` states. Five more faults each fail at least 1 test. The harness reports 8 of 9. Its one miss, the zero-side check, is a gap in this seat's generator, and the direct case above covers it.

**D8 on the corrected tool.** Rows unchanged, 2×2 header line plus 64 bytes after it:

| Field | Bit flips | Exit 0, original | Exit 0, corrected |
|---|---|---|---|
| `L`, `nl`, `entries` | 192 | 171 | **0** |
| `n`, `payload_bytes`, `payload_merkle`, `w_self_adjoint`, magic, newline | 1,096 | 0 | 0 |
| `sector` | 112 | 104 | 104 |
| `rooms` | 88 | 88 | 80 |
| `stream_bytes`, `chunk`, `keys_sha256`, `json` | 912 | 896 | 896 |
| Zeros after the newline | 512 | 512 | 512 |
| **Total** | **2,912** | **1,771** | **1,592** |

Every byte of the line, changed to each of the other 255 values: 34,296 of 76,500 exit 0, all in `sector`, `rooms`, `stream_bytes`, `chunk`, `keys_sha256` and `json`, plus one in `w_self_adjoint`: its trailing `|` turned into the newline, which only cuts `json=0` ([`diff/out/headerbytes-pin.err`](diff/out/headerbytes-pin.err)). `L`, `nl`, `entries`, `n`, `payload_bytes` and `payload_merkle` have 0.

## Question 3. Receipts, judge, recipe: FAIL, on the recipe

**Receipts: supported.** MEASURED, `diff/receipts_check2.py`, output [`diff/out/receipts-check2.hbp`](diff/out/receipts-check2.hbp):

- The run: `ALLPAIRS-3x4-PIN.out` `b53b281a…` equals the file on `D:`. Rows normalised, `609bc96f…` on both runs. Standard error 0 bytes. `cdb22218…` and `5ab04b18…` hold today.
- The judgement: rerun here, `PIN-COMPARE.hbp` matches row for row, and Python's CRLF output reproduces the logged `e74b77b6…`, as `PIN_COMPARE_LINE_ENDINGS` says. `COMPARE-CONTROLS.hbp` reruns the same, 22 cases.
- The controls: the normalised hash `0305a593…` holds on `CONTROLS.hbp`, `CONTROLS-REPEAT.hbp` and `CONTROLS-PIN.hbp`. Local, pin and hosted header rows are equal apart from tool hashes. 35 `RESULT_FILE` rows and the sidecar match.
- Hosted run 41604837594: success, head `bf24a2c4…`, whose `allpairs.rs` blob is the pin's, artifact digest `ea99c7d1…` as recorded.
- `d78f263f…` and `cdb22218…` differ by 24 bytes, as recorded ([`diff/out/build-bytes.hbp`](diff/out/build-bytes.hbp)). The third build, `9bc0675a…`, stayed out of reach under `D:/ym-3x4-room-run/p0-ball`, so its 20 bytes are NAMED.
- The one miss: `RUN.hbp` on `D:` holds one row more than the committed `PIN-RUN.hbp`, a `REPRO_RERUN` row dated after the commit. The first 9 rows are the same.

A witness from part one, by chance: at 09:05:10Z `Get-Process` showed this executable's path running at below-normal priority with a peak working set of 4,038,279,168 bytes, inside the recorded run, 08:54:17Z to 09:39:22Z. This seat's reader recomputed the merkle and all 34 sector hashes against the public manifest from 09:05:50Z to about 09:15:37Z, so the store held the public bytes during that run. Its file hash at that moment went unmeasured.

**The judge is sound for what it compares.** MEASURED ([`diff/out/judge-attack.hbp`](diff/out/judge-attack.hbp)): 136 of 136 one-field faults across all 5 rows caught, and row edits, a BOM, odd `secs` forms, a nonzero exit and stderr all caught. A non-numeric field stops it with a Python traceback and exit 1, fail-closed with no `PIN_COMPARE_DONE` row. Its content is one test: the output equals `ALLPAIRS-3x4.out` apart from `secs`, plus exit 0 and empty stderr. `pairs_arithmetic` (`compare_pin_run.py:54`) compares constants and cannot fail at run time, and the other named rows follow from row identity. "31 of 31" is 31 rows of that one result.

**What the judge and the recipe cannot show.** MEASURED in the same file:

- That a run happened: a copy of the original output passes, also with `secs` invented.
- Which executable ran: no row names it.
- Which store: D6 is open, and the recipe hashes no sector.
- Beyond the stored rows: `fullrebuild` owns that.
- On a machine short of 4 GiB, a smaller cap changes `passes` and `cap_entries`, so the judge refuses it.

**Would the recipe work on another machine?** MEASURED from fresh public clones at `fead9ed`, with an empty sectors folder so the store stayed unread. On Linux (WSL, Rust 1.81.0) every step before the run works, and the file hash of the build, `389881ac…`, **equals the hosted Linux build's in `hosted/TOOLS.txt`**, across two environments. On Windows with `core.autocrlf=false` the same steps work and the normal hash matches. With this machine's default `core.autocrlf=true` it stops at its first hash. The run and the judge's PASS branch on real sectors: NOT_MEASURED, reason BUDGET, as the brief allows no 3×4 pass.

## Findings

Each new, each with no effect on the recorded numbers.

| # | Where | Finding | Reproducer | Fix |
|---|---|---|---|---|
| R1 | `reproduce_pin_run.sh:10,28` | **Exit 0 on a failed judgement.** `set -eu` with no `pipefail`, and `tee` ends the script. Tool exit 1, `PIN_COMPARE_DONE\|failed=28`, `RECIPE_EXIT=0`, on Windows and Linux. A step that cannot turn red | Run it with an empty sectors folder ([`recipe-fresh.log`](diff/out/recipe-fresh.log), [`recipe-linux.log`](diff/out/recipe-linux.log)) | `set -euo pipefail`. MEASURED: exit 1 with that one change |
| R2 | The whole of `reproduce_pin_run.sh` | **The sectors are never hashed.** With D6 open, a store with one pair changed on both sides and its merkle repaired prints the same rows, measured on 2×2, so the judge would pass it (NAMED on 3×4) | Read the script. The manifest is in the repo, `native/ym/results/3x4_room_backed/receipts/hf-store/SECTORS-341-374.sha256` | `sha256sum -c` that manifest in `SECTORS_DIR`, and record `sha256sum "$X"` and `rustc -V` in `OUT_DIR` |
| R3 | `reproduce_pin_run.sh:21` | **A default Git for Windows clone stops at the first hash.** The working copy holds CRLF: `allpairs.rs: FAILED`, exit 1, fail-closed | `git clone` with `core.autocrlf=true` ([`recipe-fresh-autocrlf-true.log`](diff/out/recipe-fresh-autocrlf-true.log)) | Hash `git show "$PIN:$S"` |
| R4 | `compare_pin_run.py:12`, `reproduce_pin_run.sh:28` | **`ORIGINAL` carries no hash.** The same change in both files passes for `flats`, `flat_w`, `flat_w_sum` and `cap_entries`, which hold no constant | `same_fault_in_both_files_*` rows in `judge-attack.hbp` | Compare with `609bc96f…` inside the judge |
| R5 | `reproduce_pin_run.sh:19-20` | **"Everything the build reads must match the pin" is wider than its check.** Cargo also reads `native/ym/backend/Cargo.toml` and `native/Cargo.toml`: a build fails without the second, and a changed line in either passes this check | Append a comment to either, run the recipe | Add both paths, or narrow the sentence |
| R6 | `PERRON-TWO-SIDED.md:259`, "A replay compares the source hash and that normal hash" | **Windows only.** `pe_normal_hash.py` on the Linux build prints `not a PE file`, exit 1. On Linux the file hash itself reproduced, `389881ac…`. On Windows the normal hash keeps the Rich header and linker 14.42, so another toolset could differ with the same source (CONJECTURE) | Run it on an ELF | "On Linux compare the file hash, `389881ac…`. On Windows compare the normal hash, and a difference there means the toolchain differs, or the source" |
| R7 | `PERRON-TWO-SIDED.md:238-239` | **Hosted runs sit under a Windows executable.** "What ran on it" lists run 41604837594 beside `d78f263f…`. That run built its own Linux files, `389881ac…` and `376cce17…` | `hosted/TOOLS.txt` | Name the Linux builds there |
| R8 | `compare_pin_run.py:2`, `PERRON-TWO-SIDED.md:268`, "written while the run was going" | **INCONCLUSIVE.** The judge first reaches git in `fead9ed`, 09:50:39Z, after the run's end at 09:39:22Z, and no row dates its writing | `git log` on that path | Same fix as the prediction rows: push before the run. Its soundness is measured above and needs no order |

## Open

| Item | Status |
|---|---|
| Replay of the corrected `allpairs` on another machine, with the judge's PASS branch on real sectors | OPEN |
| R1 to R8, and D3 to D8 | OPEN, the author's call |
| An independent model reading this diff | OPEN |

## Deviations and this part's errors

- **The two instructions on `REVIEW.hbp`.** "Leave those two files as they are" and "new rows appended to `REVIEW.hbp`" meet here as an append after byte 108,785, with the first bytes still hashing to `f19ead4b…` and a frozen copy beside it. `HASHES.sha256` stays as it stood, and [`HASHES-DIFF.sha256`](HASHES-DIFF.sha256) covers this part.
- **Predictions that missed, kept in `REVIEW.hbp`:** a fresh clone passing its source checks (it stopped on CRLF, now R3); `D:` `RUN.hbp` equal to the committed file (one later row); 0 exits in `w_self_adjoint` under byte changes (1); the harness red on all 9 tool faults (8).
- **First tries that did not run:** an export without `native/Cargo.toml` failed to load the workspace (now R5), and `$PATH` inside `wsl bash -lc` died on a parenthesis.
- **Temporary files.** This part set `TMP`, `TEMP` and `TMPDIR` into `diff/tmp`. In part one the unit tests wrote and removed their temporary stores under the system temp folder, outside the review folder.
- **Seen, unread:** `origin/ym-3x4-allpairs-failclosed` has moved to `4f8605b`. This review covers `fead9ed`.

## Files

Under `diff/`: `attack_gates.py`, `judge_attack.py`, `receipts_check2.py`, `mutate_tool.py`, `small_cases.py`, `patch_harness_new_contract.py`, `harness_tail.rs`, `recipe_linux.sh`, `repro_linux.sh`, `replay_controls_pin.py`, and `out/`. Executables in `bin/`: `allpairs-pin-own.exe`, `fuzz-pin.exe`. Hashes in [`HASHES-DIFF.sha256`](HASHES-DIFF.sha256).
