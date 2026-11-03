# Second-seat review of the hardened `allpairs`, part three

**Reviewed:** commit `9c2c7e67e29e0b2450010bd43c3391638e6670eb`, branch `ym-3x4-allpairs-hardened`: `allpairs.rs` `3323d06e…`, new `torusl/src/roomscan.rs` `b8880f4b…`, `roomio.rs` `67ccd428…` unchanged; the recorded executable `4f64f605…`, normal hash `71fff11a…`; the controls, judge and recipe under `allpairs/hardened/`, and the corrected `failclosed/reproduce_pin_run.sh`.
**Date:** 2026-11-03. **Reviewer:** Claude Opus 5.5 (`claude-opus-5-5`), second seat of ACER-CLAUDE-FABLE5, on OP-JESSE's scope.
Claims carry MEASURED, NAMED or CONJECTURE. Parts one and two stay as reported: [`ALLPAIRS-REVIEW.md`](ALLPAIRS-REVIEW.md) `b77f78ec…`, [`ALLPAIRS-REVIEW-DIFF.md`](ALLPAIRS-REVIEW-DIFF.md) `a86808fb…`. Predictions sit beside outcomes in [`REVIEW.hbp`](REVIEW.hbp), after byte 121,766, and [`REVIEW-part2-as-reported.hbp`](REVIEW-part2-as-reported.hbp) `59183b12…` is that prefix.

## Verdicts

**Overall: FAIL, on one race in the tool and one recipe path.** D3 to D7 close. D8 closes on every path with no writer on the store: exit 0 came 0 times in 32,768 bit flips and 0 times in 77,520 byte changes. A writer toggling the header block during a run reached exit 0 with `store_identity=PASS` on a changed payload, 524 times in 2,000, on a copy. A three-line fix took that to 0 in 2,000. On 3×4 the judge pins `payload_merkle` and the recipe hashes the sectors, so this race leaves the 3×4 evidence as it stood.

| # | Question | Verdict | Basis |
|---|---|---|---|
| 1 | Does each of D3 to D8 close, on every path? | **FAIL, on D8 alone** | D3, D4, D5, D6, D7: PASS. D8: PASS with no writer, FAIL with one (H1). Exit 0 with bytes past `stream_bytes` is the source header's stated scope, and the judge and manifest pin those bytes on 3×4 |
| 2 | Does the diff add a defect? | **FAIL, on H1** | H1 sits in the new identity gate. H2 (a quadratic walk), H3 (the memory sentence) and H4 (offset unprinted) are minor. The D7 accounting is right on both sides, exact in 22,500 fuzz cases and 39,180 sweep runs |
| 3 | Does the trust root hold? | **FAIL on H1, holds on every read with no writer** | It binds four blocks, hence their merkles and payloads. It leaves the executable, rows = H, the bytes past the stream and the offset to the reader |
| 4 | Are the new judge and recipe sound? | **FAIL, on R9 alone** | R1, R2, R4 closed. R3 moved and stays fail-closed. R5 narrowed. A good Windows run cannot finish the recipe (R9). The judge is sound for what it compares |

**Scope.** This part is a review with measured runs on small stores, on the author's machine, with a Windows build and a WSL Linux build. It read the 3×4 store's bytes zero times, and it did not read the 3×4 run the coordinator is making. A replay on another machine stays OPEN. The reviewer's model is the one the author's seat reports, so independence here is a separate session and separate code, and an independent model reading this diff stays OPEN. SHA-256 is taken as collision-resistant throughout (NAMED).

## Question 1. D3 to D8

Own build first. MEASURED: `cargo +1.81 clippy --release --all-targets --locked -- -D warnings` exit 0, 38 of 38 tests, and the normal hash of the build from `git archive` equals the recorded `71fff11a…`, 24 differing bytes, `.text` equal.

| Defect | Status | Measured |
|---|---|---|
| D3 padding unread | **Closes** | A stray byte first, middle and last in the padding, on chunk edges and off them: `padding_nonzero=1`, `padding=FAIL`, exit 2. A row after the last: exit 2. In fuzz half the tables trust the block itself, so padding decides alone: 22,500 cases, 0 disagreements |
| D4 memory grows with padding | **Closes** | 256 MiB of padding: 423.6 MB on both older tools, 5.2 MB here, stopped by `check_sizes`. `rooms=` claiming 2 GiB of zeros, which passes `check_sizes`: 196 MiB working set |
| D5 cap label | **Closes** | `cap_requested=0`, `cap_entries=1`. `cap_requested=18446744073709551615`, `cap_entries=4000000000` |
| D6 store unnamed | **Closes** | The row prints the computed merkle, the block hash and the executable's hash. Two stores, one row: 0. Four rows labelled 3×4 with the other four gates at PASS: exit 2, seven fields named |
| D7 masked by a doubled lookup | **Closes** | Table in question 2, at four caps on two builds |
| D8 header under no hash | **Closes with no writer, stays open with one** | Below |

Attempts at exit 0, MEASURED, each predicted first:

| Attempt, on the real 2×2 stream | Result |
|---|---|
| Each of the 32,768 bits of the block, real `TRUSTED` table | exit 0: **0**, exit 1: 1,388, exit 2: 31,380. Equals the hosted `HARDENING_FULL_BLOCK` row |
| Each line byte to each other value, 77,520 changes | exit 0: **0**, exit 1: 44,940, exit 2: 32,580 |
| One pair changed on both sides, merkle repaired | exit 2, `identity_differs=payload_merkle` |
| The same pair under the trusted block | exit 1, merkle mismatch |
| Same rows under `L=1x4`, and rows ×6 under `L=1x5` | exit 2, `store_identity=OPEN` |
| 64 nonzero bytes past `stream_bytes` | **exit 0**, `bytes_after_stream=64` |
| Same stream cut at another sector length | **exit 0**, `bytes_after_stream=768` |
| Junk before the stream, with OFFSET set | **exit 0**, and the row says nothing of the offset (H4) |
| **A writer toggling the merkle field during the run** | **exit 0, 524 of 2,000**, printed merkle `d7e7410a…`, table `b7c5847b…` (H1) |

The three streams at exit 0 with no writer are byte for byte a trusted stream. Line 16 of the source states that bytes past the stream stay unread. On 3×4 a zero rule there would fail the real store, which holds 347,747,335 nonzero bytes past its stream (part one). The judge pins their count, 349,114,368, and the manifest pins the bytes.

The named reruns, MEASURED:

```
REPRO_DONE|cases_differing_from_f4ea7e85=16|json=0                                       recorded and own build; C2 twice, C5_cap_one, D6_clean, C_clean, C_changed_byte_unrepaired stay as measured
BRUTE_DONE|failed=0|json=0                                                               1,304, 32 and 9 caps on 2x2, 2x3, 3x3: 0 disagreements
ROWCAP_DONE|not_met=0|json=0                                                             9 store and cap pairs at n = 2^20 + 6; the executable before the cap shows one window
GATE_ATTACK_DONE|cases=69|runs=276|not_met=0|exit0_with_open_or_fail=0|exit0_with_no_rows=0|json=0   only clean exits 0; the 5 gates all counted
BLOCKFLIP_DONE|…|clean_exit=Ok(0)|flips=32768|exit0=0|exit1=1388|exit2=31380|panics=0|…   the fuzz headerflip, widened from 2,912 bits to the whole block
```

The harness on the new contract shares no code with the tool: its own SHA-256, parser, sizes rule, gates, identity and pair accounting by hash map. On every row, dirty ones included, it compares verdict, exit class, each gate, identity, both cap labels, six counters at two caps, `pairs_clean`, and the windows rule with rows out of order. The last two and the gate rows joined as the run went on, so the first 13,500 cases have fewer compares, and rows `fuzz_hard_*` in `REVIEW.hbp` name each. 22,500 cases, exit 0: 3,230, exit 1: 6,592, exit 2: 12,678, 3,776 with repeats or disorder: **0 disagreements, 0 panics**. It can turn red: on 18 faulted copies of the tool it went red on 12, then on 16 once widened to compare each gate and `pairs_clean` and to generate `rooms=` below `n` and padding of 1 MiB or more. The two left change no verdict and no exit: the `lower_repeated` clause, which `found` and `answered` both equal to `upper` already imply, and the short-store check, where the read error stops the run anyway ([`mutate-tool.hbp`](hard/out/mutate-tool.hbp), [`mutate-green.hbp`](hard/out/mutate-green.hbp)). The author's 38 unit tests catch 16 of the 18. They miss that same `lower_repeated` clause, and the 1 MiB stream-multiple rule, which the harness catches.

## Question 2. Does the diff add a defect?

MEASURED, on the recorded executable and this seat's build:

| Code | Attack | Result |
|---|---|---|
| `roomscan::scan` | 14 stores: rows ending on the 64 MiB chunk, on a 16 MiB leaf, one room either side, at the stream's end; the largest rows straddling a chunk; a stray byte at each padding end; a tail | 14 of 14, every count equal to a Python reader's |
| `check_sizes` | `payload_bytes` at 2^64−1, `rooms × 8` overflowing and past the payload, no `rooms=`, no `stream_bytes=`, stream off the 1 MiB multiple, padding of 1 MiB or more, `n` above `rooms`, short file, offset at 2^64−1 | Each exit 1, with no panic. Padding just under 1 MiB passes |
| `identity_gate` | 11 named stores | As predicted. It hashes the second read (H1) |
| `differing_fields` | 900 empty parts, 300 new keys, bad UTF-8, control bytes, a line filling the block | Exit 2, no panic. 900 empty parts print an empty `identity_differs=`, with `store_identity=FAIL` |
| `padding_gate`, `header_rooms` | Faulted copies | `rows_fill_rooms` and `header_rooms` state one fact, so each covers the other |
| Answered bitset, sort on admission | Fuzz, 844 reversed-row runs, descending columns | Exact at every cap. The sort is stable and keeps windows as the rule says |
| Equal-column walk in `answer` | `k` equal columns on both sides of a pair | Right counters, quadratic time (H2) |
| `store_bytes` | Sectors of another length, too few sectors, short file | `bytes_after_stream` right, exit 1 on the short ones |
| `own_hash` | Both builds, and a copy under another name | Names the file's hash each time. It is the tool's own statement (question 3) |

**D7, when columns repeat.** Every counter as predicted, at the default cap and caps 1, 7, 100, on both builds:

| Store | `upper_without_lower` | `lower_repeated` | `value_mismatch` | `columns_not_ascending` |
|---|---:|---:|---:|---:|
| Part one's D7 store: lower doubled, a partner deleted | 1 | 1 | 0 | 1 |
| Lower side repeated alone | 0 | 1 | 0 | 1 |
| Upper side repeated alone | 1 | 0 | 0 | 1 |
| Both sides repeated, same values | 0 | 0 | 0 | 2 |
| Both sides repeated, values crossed | 0 | 0 | 2 | 2 |

The k-th lower entry answers the k-th upper entry, in stored order, at every cap: `cap_variant_counters=0`. The sweep repeats a column on one side and on both at each of 2,396 off-diagonal entries, at caps 1, 13, 100 and 470,000,000: 39,180 runs in all, `bad=0`. Each store above exits 2.

**Memory against the source header's formula** (8 bytes per upper entry, 1 bit per upper entry, 8 per window row, plus buffers, counted here as four 64 MiB chunks). MEASURED, peak working set and sampled private bytes, in MiB:

| Store | Cap | Working set | Private | Formula |
|---|---|---:|---:|---:|
| `rooms=` claims 2 GiB of zeros, 2 rows | default | 196 | **2,261** | 256 |
| 2^26 rows of no entries | default | **838** | **1,615** | 768 |
| Same | 1,000 | 198 | 207 | 264 |
| 67,042,305 upper entries | default | 619 | 698 | 775 |
| Same | 2^24 | 312 | 323 | 386 |
| 16,711,425 upper entries, descending, so every row sorts | default | 229 | 292 | 385 |
| Real 3×3 | default | 199 | 307 | 317 |
| Real 3×3 | 1,000,000 | 189 | 193 | 266 |

The formula holds for the working set, to within 9% at 2^26 rows, where `off` doubles. Private bytes run above it by the reservation, `min(cap, payload / 8) × 8` bytes on the first pass, whatever the rows hold (H3). All of it stays bounded by the cap. On 3×4: 3,586 MiB reserved, 56 of bitset, at most about 220 for 14,413,893 rows with growth, at most 256 of buffers, about 4.0 GiB in all, which matches the recipe's "about 4 GiB" (CONJECTURE, computed, since that run is not this seat's to read). At the default cap the formula's own ceiling is about 7.3 GiB, for a store of 470 million rows and 470 million upper entries, and the 2^26 row scales to about 8 GiB of working set there (CONJECTURE). The recipe's 4 GiB is for the true store.

## Question 3. The trust root

**What it binds.** MEASURED: `check_trusted_table.py` `failed=0` on the three stores and the 3×4 block, and the hosted run's copy reads the same. Its four hashes equal part one's block hashes. A row needs the exact line and the hash of all 4,096 bytes, so a block one bit away fails, and that block's merkle binds every payload byte on every pass. The judge holds the 3×4 values a second time, `65dd63a8…` and `ec03c5f8…`, equal to the table's.

**Where "bind" stops.** Line 58 says these two values "bind every field of the header and every payload byte". `run_tool` takes the merkle from one read of the block (line 568) and the identity from another (line 569), and `check_header` compares `n` and `payload_bytes` between them, leaving the merkle uncompared. H1 is that gap.

**What it leaves to the reader.**

- **The executable.** The table is inside the tool, so the tool's word covers its own table. MEASURED: the pinned source with one table row edited, rebuilt, exits 0 with `store_identity=PASS` on the changed store, where the recorded executable exits 2. Its `exe_sha256` reads `713601a1…`, so the output names it, by its own statement. The reader's check is to hash the file and compare a build of the pinned source: file hash on Linux, `0f3fbbfd…` from this seat's WSL build and from the hosted build; normal hash on Windows, `71fff11a…` from the recorded file, this seat's build and a fresh clone.
- **That the rows are H.** `keys_sha256` is a label here. `fullrebuild` is the check, and it stays a separate run: the 49 small-store controls rerun here keep it red on `mag` and `sym2`.
- **Bytes past the stream, and the offset.** The first counted, the second unprinted, as above.
- **How a store reached `check_trusted_table.py`.** It prints `source=rebuilt_from_the_rules_by_ymroom` for any `--store`. MEASURED: the edited source with the changed store given as 2×2 exits 0 under that label. The workflow's rebuild is what gives the row its weight (R12).

**What else belongs in it.** No more rows. Two neighbours would carry weight: the one comparison that makes "bind" true (H1), and the source's hash as a constant in the recipe, as `reproduce_pin_run.sh` has it, since that hash is what anchors the table (R10). The manifest hash is already a constant in the recipe, and a printed `offset=` closes H4.

## Question 4. The judge and the recipe

| Part two | Now | Measured |
|---|---|---|
| R1 exit 0 on a failed judgement | **Closed** | `set -euo pipefail`. Patched to the 2×2 store on Linux: judge `failed=19`, recipe exit 1, no `REPRODUCE_DONE`. On Windows too, once R9 is corrected in a copy |
| R2 sectors unhashed | **Closed** | Empty folder: 34 `FAILED` rows, exit 1, before any build. A manifest with one line added: exit 2 |
| R3 CRLF in a default clone | **Moved, still fail-closed** | The pin recipe stops at once, exit 2. The hardened recipe passes `git diff` and the manifest (LF under `.gitattributes`), would hash all 27.2 GB, then cargo refuses `vendor/num-bigint/src/biguint/power.rs`, exit 101 (R11) |
| R4 original unpinned | **Closed** | `b0b17220…` inside the judge. The same fault in both files is refused |
| R5 pathspec narrower than the build | **Narrowed** | A one-line edit of `allpairs.rs`: exit 2. `backend`, `Cargo.lock`, `vendor` and `.cargo` are now covered. What remains is R10 |

**The judge.** MEASURED: its own test, 184 cases, 182 faults, `failed=0`. It checks every gate, both hashes, every count, the four windows and all original fields, with `ORIGINAL` pinned. This seat's 29 further cases find it reads fields, with the last repeat winning: `|value_mismatch=5|value_mismatch=0|`, an added field, reversed fields, CRLF, no final newline and `secs=abc` all exit 0, and the reverse order of a repeat exits 1. It prints `normalised_sha256` and compares it with nothing (R13). Any forger can already write good rows, which its header says, so this adds strictness and leaves soundness as it stood.

**What they still cannot show:**

- That a run happened. A copy of good rows passes, as the judge says itself.
- That the printing process was the pinned build, past the hash of the file named by `--exe`. `exe_sha256` is the tool's own statement, and the judge passes any file the output names.
- That the rows are H, or anything beyond W-self-adjointness of this stored matrix.
- The judge's PASS branch on a real 3×4 output, in this seat's hands. Here it ran on the author's synthetic good output and red on 2×2.
- Another machine.

**The new controls.** MEASURED on the three recorded executables: `run_hardening_controls.py` `failed=0`, with prediction hash `84ef31ea…`, the same on this run, the recorded run and hosted. Commit time 10:37:22Z stands before the recorded output's 10:40:40Z (timestamps, NAMED). `run_controls_hardened.py`, on copies: 49 controls, `failed=0`, 72 rows the same on the original's keys and 9 changed in `verdict` alone, as it predicts.

**One control is red on hosted Linux at this commit (C1).** The hosted `HARDENING-CONTROLS.hbp` ends `failed=1`, on `HARDENING_MEMORY|tool=hardened|peak_bytes=613576704`, and its step exits 1. The same case reads 5,210,112 on Windows. The rows compared agree across this seat's Windows run, the recorded Windows run and hosted: all 279 `HARDENING_CASE` rows, `fa70da79…` from each, and the sweep rows, `72ef943a…`.

## Findings

Each new, and none moves a recorded number.

| # | Where | Finding | Reproducer | Fix |
|---|---|---|---|---|
| **H1** | `allpairs.rs:568-570`, `446-457`, `58` | **Two reads of the block: merkle from one, identity from the other.** MEASURED on a copy, with a writer toggling the merkle field: exit 0, `verdict=PASS`, `store_identity=PASS`, 524 of 2,000, printing the changed store's merkle. With no writer: exit 1 and exit 2 | [`hard/race.py`](hard/race.py), [`race.hbp`](hard/out/race.hbp) | Compare `payload_merkle=`, `L=`, `sector=` of the line with `hdr` in `check_header`, or parse `Hdr` from the one block. [`hard/fix/patch.py`](hard/fix/patch.py): exit 0 in 0 of 2,000, 38 tests, clippy 0, all 42 named attack rows unchanged |
| H2 | `allpairs.rs:280,287` | **The equal-column walk is quadratic.** `k = 65,534` on both sides: 3,697 ms for 1 MiB of store, 37 ms for the same row size with distinct columns; 8 such pairs 30,256 ms. Verdict FAIL, counters exact. A 26.85 GB store of 25,600 such pairs would take about 26 hours, against 45 minutes for the real one (CONJECTURE, scaled) | [`quadratic.hbp`](hard/out/quadratic.hbp) | Upper bound by `partition_point`, and a cursor per run |
| H3 | `allpairs.rs:9-10` | **The memory sentence leaves out the reservation and `Vec` growth.** Table above | [`memory.hbp`](hard/out/memory.hbp) | One clause |
| H4 | `allpairs.rs:595` | **The row omits OFFSET and DEV.** A junk prefix passes in silence | `T3` in [`attack-new.hbp`](hard/out/attack-new.hbp) | Print `offset=` |
| **R9** | `reproduce_hardened_run.sh:34` | **A good Windows run cannot finish.** In Git Bash `[ -e allpairs ]` is true when `allpairs.exe` exists, so `X` keeps no suffix, and native Python cannot open it for `--exe`: a traceback and exit 1, after the whole run. Fail-closed | [`recipes-win3.hbp`](hard/out/recipes-win3.hbp), [`small-lf-2.log`](hard/out/recipes/small-lf-2.log) | Test `$X.exe` first. Measured in a copy: the judge reaches its last row |
| R10 | `reproduce_hardened_run.sh:13,25-26,35` | **The source hash and the build hash are printed, and compared with nothing; PIN is a parameter.** MEASURED: this recipe in a checkout of `0fd24d3` with that PIN reaches the sector check. An untracked file inside the pathspec, and `native/.cargo/config.toml` above it, pass `git diff`, and the second changes the Linux build to `ddd9b09a…`, printed in `build.txt`. The pin recipe does hold its source hash | [`recipes-win.hbp`](hard/out/recipes-win.hbp), [`recipes-linux.hbp`](hard/out/recipes-linux.hbp) | Constants for `allpairs.rs` and `roomscan.rs`; `git status --porcelain --ignored` on the build paths; add `native/.cargo` and `.cargo`; compare `build.txt` on Linux with the hosted hash |
| R11 | `reproduce_hardened_run.sh:10`, order of steps | **A default clone learns late, and the advised clone form does not last.** The original output's hash is checked only by the judge, after the run; cargo stops after the sectors are hashed. `git -c core.autocrlf=false clone` leaves `core.autocrlf=true` in force, and a later checkout puts 1,430 CR bytes back in `allpairs.rs`. `git clone -c core.autocrlf=false` keeps it: 0 | [`recipes-win2.hbp`](hard/out/recipes-win2.hbp), [`recipes-win4.hbp`](hard/out/recipes-win4.hbp) | Check `ALLPAIRS-3x4.out` first, as the pin recipe does; advise `git clone -c`, in both recipes |
| R12 | `check_trusted_table.py:40,43` | **The `source=` label is a constant.** | Question 3 | `source=given`, with the workflow saying where the store came from |
| R13 | `compare_hardened_run.py:29,109` | **The judge reads a last-wins dict and compares no row as text.** | [`attack-judge.hbp`](hard/out/attack-judge.hbp) | Pin the normalised hash with `secs` and `exe_sha256` blanked |
| C1 | `run_hardening_controls.py:350` | **On Linux `ru_maxrss` reads the Python parent.** Same tool, same store: 11,685,888 B from a small parent, 745,820,160 B from one holding 700 MiB, and still that after it frees them. A false red | [`maxrss.hbp`](hard/out/maxrss.hbp) | A small helper between them: 11,550,720 B, measured |

## Open

| Item | Status |
|---|---|
| Replay of the hardened `allpairs` on another machine, with the judge's PASS branch on real sectors | OPEN |
| The 3×4 run on this commit | The coordinator's, unread here |
| H1 to H4, R9 to R13, C1 | OPEN, the author's call |
| An independent model reading this diff | OPEN |

## Deviations and this part's errors

- **Predictions that missed, kept in `REVIEW.hbp`:** the gate attack's case count (I wrote 81, the script holds 69, every exit as predicted); `final_row_fields_reversed` as judge-red (it passes, now R13); a default clone stopping at the manifest (it holds LF there, now R3 and R11); the harness red on all 18 faults (12, then 16, as above); 76,500 line-byte changes (77,520, the row said it was an estimate).
- **First tries that did not run:** `edges.py` stopped on my row builder; `attack_judge.py` stopped twice on my own case for bad UTF-8, and one `RESULT` row with an empty `not_met` came from that, marked by the `NOTE` after it; the first memory store held 2,016 MiB under a `rooms=` for 2,048, so it reported exit 1 and was rebuilt; the first patched Windows recipe ran with `MSYS_NO_PATHCONV=1` from my shell, which gave its own traceback, and the rerun without it found R9.
- **My cleanup met a running script:** removing `hard/tmp/a` stopped the named attacks on the first of the six green faults, so `D7_reviewer_store` shows as missed in its row. A `NOTE` in `REVIEW.hbp` marks it. Its harness row and `P_n_above_the_rows` stand.
- **A file I changed in my own clone:** the Windows clone's `allpairs.rs` came back with CRLF after my test edit, which is how R11's 1,430 was seen. Its build still gave normal hash `71fff11a…`.
- **Network.** Fresh clones came from the public repo, read only, and were deleted after use. `TMP` and `TEMP` on Windows and `TMPDIR` on WSL stayed in `hard/tmp`. A listing of the system temp folder by time shows none of this part's files. No write outside this folder.
- **Stores.** Every store was a copy or a new file under `hard/tmp`. `D:` was read and run from, with its hashes unchanged, and `F:` was untouched.
- **Removed:** the tool with the edited table and its source, a build that passes a changed store. [`hard/trust_demo.py`](hard/trust_demo.py) rebuilds it. `bin/allpairs-fix.exe` stays.
- **Seen, unread:** `origin/ym-3x4-allpairs-hardened` has moved to `b8ac5f6`, and `audit/allpairs-hardened-20261103` is at `fb2ef5f`. This review covers `9c2c7e6`. On `D:` this part read only `hosted-run` and `hardening-run`, the store files, `mutate_pairs.py` and the executables.

## Files

Under `hard/`: `attack_new.py`, `attack_more.py`, `make_attack_gates.py`, `attack_gates.py`, `attack_judge.py`, `edges.py`, `shapes.py`, `shape_claim.py`, `race.py`, `trust_demo.py`, `fix/patch.py`, `harness_tail.rs`, `mutate_tool.py`, `mutate_green.py`, `recipe_win.sh` to `recipe_win4.sh`, `recipe_linux.sh`, `maxrss.sh`, `maxrss2.sh`, `run_hard*.cmd`, and `out/`. Executables in `bin/`: `allpairs-hardened-own.exe`, `allpairs-fix.exe`, and `fuzz-hard.exe` to `fuzz-hard4.exe`, one for each widening of the harness; `harness_tail.rs` as it stands builds the last. Hashes in [`HASHES-HARDENED.sha256`](HASHES-HARDENED.sha256).
