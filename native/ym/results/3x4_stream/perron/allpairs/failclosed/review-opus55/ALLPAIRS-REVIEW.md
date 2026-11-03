# Second-seat review of `allpairs`

**Reviewed:** commit `8faadb07748417e713e95723f01d83e0ad80b93f`, with `native/ym/crates/evolvers/src/bin/allpairs.rs` `f4ea7e85…`, `native/ym/crates/torusl/src/roomio.rs` `67ccd428…`, `segio.rs` `e9253ea2…`, `sha.rs` `d5ff5195…`, and the recorded executable `c68f25b4…`.
**Date:** 2026-11-03. **Authorized by:** OP-JESSE. **Reviewer:** Claude Opus 5.5 (`claude-opus-5-5`), second seat of ACER-CLAUDE-FABLE5.
Claims carry MEASURED, NAMED or CONJECTURE. Each tool run has its prediction beside its outcome in [`REVIEW.hbp`](REVIEW.hbp), with timestamps this seat wrote, and a `NOTE` row names the read-only lookups.

## Verdicts

**Overall: FAIL.** Items 2 and 5 fail. Item 2 fails on fail-closed behavior: a store can reach `verdict=PASS` and exit 0 with no rows read, or with a count gate that could not read its field. Item 5 fails on wording: some statements go further than their receipts.

**The recorded 3×4 numbers stand.** No defect below changes them. MEASURED: a separate reader, in one pass over the store, counted the same rows, entries, diagonal and pairs, cut the same four windows, and found the upper and lower triples equal by two separate tests. That pass ran on the author's machine from the author's files. A replay on another machine is OPEN.

| # | Scope item | Verdict | Basis |
|---|---|---|---|
| 1 | Window partitioning, pair coverage, exactly-once counting | **PASS** | 1,345 store-and-cap runs against a brute-force check, 0 disagreements. The four recorded 3×4 windows reproduced row for row |
| 2 | Integer overflow, malformed input, fail-closed behavior | **FAIL** | No overflow found, and 74 of 74 named cases as predicted, which include the failures here. Defects D1 to D4 and D8: `n=0` passes with `merkle=PASS` and no merkle computed, an unreadable count field passes, padding is unread, memory grows with padding |
| 3 | Unpaired edges and equality mismatches | **PASS** | All 180,352 bits of the 2×2 rows flipped, merkle repaired: only the 3,376 bits of `mag`, which this test leaves unread and `fullrebuild` reads, exit 0. One fault on each of 2,396 entries at 7 caps: each reported exactly. 220,000 random stores: counters exact whenever columns ascend, 0 false passes of the pair property. Defect D7 is one wrong counter on rows the column gate already fails |
| 4 | Independent verification of the reported pair count | **PASS** | Own reader: 1,632,625,631 upper, 1,632,625,631 lower, both fingerprints equal, on this machine. Replay on another machine: OPEN |
| 5 | Recorded results support exactly the claims | **FAIL** | Every printed number is reproduced or supported by a receipt. Seven statements go further than their receipts, and "predicted in writing first" for the 3×4 run is INCONCLUSIVE from the public record |

## Scope of this review

- **Read:** `allpairs.rs`, `roomio.rs`, `segio.rs`, `sha.rs`, the recorded results in `perron/allpairs/`, and the claims in `PERRON-TWO-SIDED.md`, `PERRON-BOUND.md`, `PERRON-REVIEW.md`, `PERRON-RESULT.hbp` and `README.md`.
- **Ran, on the author's machine (i5-8300H, Windows 11, Rust 1.81):** the recorded executable and this seat's build on damaged copies of small stores, a brute-force window check, a differential fuzz harness, exhaustive fault sweeps, and one pass of this seat's own reader over the 3×4 store, at below-normal priority, peak working set 104,914,944 bytes, 587 s. A full `allpairs` run from another build, started at the operator's direction, shared the disk during that pass, and this review uses none of its output.
- **Status of a replay:** this review is a code review, tests on copies, and one pass by a separate reader. A full replay of `allpairs` on 3×4 was outside its scope. A replay on another machine, from the public files, is OPEN.
- **Independence.** Separate here: this session, the reader, the oracle and the second algorithm, all written from the format in the sources with no code taken from `roomio`, `segio`, `sha` or `allpairs`. Shared with the author: the model (the author's seat reports Opus 5.5, so blind spots can be common to both), the machine, the disk, the files, and a brief written by the author's seat. Seen during the work: the subject line of a later commit, `55ff7c6` "allpairs: both count gates must read PASS for exit 0", from a `git log --all` run to date the receipts. Its diff stayed unread. D2 was already on this seat's list from reading the code, which others cannot check. The session's auto-loaded memory index named the run folder, the `project_ym_3x4_*` notes and the author's worktree stayed unread as briefed.
- **Left unchanged:** `D:/ASOLARIA-HOST8-ROOMS-300G`, `D:/ym-3x4-room-run`, `F:`, and the checkout's tracked files. Hashes of the small stores and the recorded executable were the same at the end, and all 34 sectors matched the public manifest during the pass. Deviations from the brief are listed at the end.

## Item 1. Window partitioning, pair coverage, exactly-once counting: PASS

NAMED, from reading the code: each pass starts where the last ended (`allpairs.rs:252-264`), and `admit` keeps rows contiguous (`:120-134`), so the windows partition 0..n. Each pass walks every row from its start (`:193-196`), so a lower entry (h, i) is answered in the one pass whose window holds i. With strictly ascending columns, which the census enforces, one lookup meets at most one upper entry, so `found == upper` is a one-to-one count.

MEASURED, each predicted first:

```
BRUTE_WINDOWS|L=2x2|caps_run=1304|disagreements=0|max_passes=188|secs=61|json=0
BRUTE_WINDOWS|L=2x3|caps_run=32|disagreements=0|max_passes=2591|secs=147|json=0
BRUTE_WINDOWS|L=3x3|caps_run=9|disagreements=0|max_passes=76|secs=111|json=0
BRUTE_DONE|failed=0|json=0
```

Command: `python3 -I -X utf8 attack/brute_windows.py <recorded allpairs.exe> out/brute-windows.hbp`. Own parser, own window rule. For each cap it compares `rows_from`, `rows_to`, `upper_stored` and `lookups` of every `ALLPAIRS_PASS` row, and the caps run 0 to 1,300 on 2×2, with exact-fit caps on 2×3 and 3×3.

On the 3×4 store, this seat's reader cut the windows from the rows and counted the lower entries landing in each, with every value equal to the recorded `ALLPAIRS_PASS` rows:

| Window | rows_from | rows_to | upper stored | lower entries landing |
|---|---|---|---|---|
| 0 | 0 | 9,065,182 | 469,999,969 | 469,999,969 |
| 1 | 9,065,182 | 19,726,083 | 469,999,992 | 469,999,992 |
| 2 | 19,726,083 | 34,139,976 | 469,999,960 | 469,999,960 |
| 3 | 34,139,976 | 45,508,080 | 222,625,710 | 222,625,710 |

Scope note, MEASURED: a window holds more than the cap when one row alone exceeds it, because the first row always enters. At cap 1 on 2×2 that gives 188 passes. The recorded maximum is 469,999,992 at cap 470,000,000.

## Item 2. Integer overflow, malformed input, fail-closed behavior: FAIL

**Integer overflow: none found.** NAMED, from reading: products are `i64` of `u32` and `i32`, at most (2³²−1)·2³¹ < 2⁶³; the row sum is `i64` over at most 65,535 entries; `sum_w` is `u128`; `ent.len()` stays below 2³² at `MAX_CAP`. `first + count` wraps in release at `segio.rs:36` and still ends at exit 1, and `off + 4096` at `roomio.rs:58` runs only after a read at `off` has succeeded. MEASURED: no `f32` or `f64` in the four source files; stored values at the extremes pass clean (`R6`); a pair equal modulo 2³² and different as integers is one mismatch (`R7`); a row summing to −2³², which is 0 modulo 2³², is one row-sum fault (`R8`).

**Malformed input.** MEASURED, 74 of 74 named cases as predicted, with the recorded executable and this seat's build printing the same line on all 48 stores. Command: `python3 -I -X utf8 attack/attacks.py H P R B C`, output [`out/attacks.log`](out/attacks.log). All 48 stores also ran at caps 0, 1, 2, 3, 7 and 100, with the same exit, verdict and counters as at the default cap, so each result below holds at those caps (`ATTACK_CAP_MATRIX=1`, output [`out/attacks-caps.log`](out/attacks-caps.log)). 25 of 25 command-line cases as predicted: bad or negative offset, bad or negative cap, missing file, directory, wrong sector length, a short run of sectors, and a wrapped sector range each give exit 1. A closed standard output gives exit 101. Sizes on and around the 16 MiB leaves and 64 MiB chunks pass, and a changed payload byte at each edge gives exit 1 ([`out/sizes.hbp`](out/sizes.hbp)). Rows of the largest count a `u16` holds, placed with the header as the last room of a chunk, starting on a chunk edge, and spanning one, pass clean, and one changed value past the edge is one mismatch, named ([`out/stars.hbp`](out/stars.hbp), [`out/stars2.hbp`](out/stars2.hbp)). A sector boundary inside a room, at sector length 4,099, passes clean.

**Fail-closed: FAIL, by D1, D2, D3, D4 and D8 below.**

## Item 3. Unpaired edges and equality mismatches: PASS

MEASURED, each predicted first:

```
SWEEP_DONE|store=D:/ym-3x4-room-run/p0-ball/small/2x2/dev.bin|n=211|pairs=1198|off_entries=2396|caps=[0, 1, 3, 13, 100, 1198, 470000000]|runs=42953|value_ok=16772|delete_ok=16772|move_ok=7932|weight_ok=1477|bad=0|secs=1459|json=0
FUZZ_DONE|seed=20261103|cases=100000|tool_exit1=19650|tool_exit2=49029|tool_exit0=31321|pass_clean_all_gates=17301|pass_with_n0=1049|pass_with_entries_open=1794|pass_with_count_open=9983|pass_with_nonzero_padding=5099|false_pass_main_property=0|disagree_verdict=0|disagree_exit_class=0|disagree_counters_on_ascending_rows=0|cap_variant_counters_on_non_ascending_rows=406|masked_unpaired_on_non_ascending_rows=2124|panics=0|secs=579|json=0
FUZZ_DONE|seed=20261104|cases=100000|tool_exit1=19660|tool_exit2=49163|tool_exit0=31177|pass_clean_all_gates=16907|pass_with_n0=1039|pass_with_entries_open=1767|pass_with_count_open=10165|pass_with_nonzero_padding=5339|false_pass_main_property=0|disagree_verdict=0|disagree_exit_class=0|disagree_counters_on_ascending_rows=0|cap_variant_counters_on_non_ascending_rows=399|masked_unpaired_on_non_ascending_rows=2158|panics=0|secs=588|json=0
```

- **The sweep** (`fuzz sweep`) runs the tool's own `run()` on the 2×2 rows. One changed value with the row sum kept gives exactly one mismatch, naming i and h, at each of 7 caps, for each of 2,396 entries. One deleted entry gives one unpaired entry on the right side. A moved column gives two unpaired. A changed weight breaks every pair of its row.
- **The fuzz** (`fuzz fuzz SEED ITERS TMP`, plus a 20,000-case run on seed 7) calls the tool's `real_main` on random stores, clean and malformed, at random caps, against an oracle with its own SHA-256, parser and hash-map pair test. The tool is an unchanged copy, with `main` renamed and the `#[path]` lines pointing into the checkout. `false_pass_main_property=0` means that among these stores, none with a wrong or unpaired value within its n rows reached exit 0.
- **Would it turn red?** MEASURED: 6 of 6 faults put into a copy of the tool make the harness report ([`out/harness-controls.hbp`](out/harness-controls.hbp)): a window forgetting its last row, an uncounted mismatch, a closing window skipping a row, dropped pair gates, a double-counted lookup, and a removed merkle compare.
- **Every bit.** Each bit of the 2×2 rows, with the merkle repaired each time and the cap rotating through 470,000,000, 100 and 13 (`fuzz bitflip`, output [`out/bitflip-2x2.err`](out/bitflip-2x2.err)), 180,352 flips, 0 panics:

  | Field | Flips | Exit 0 | Exit 1 | Exit 2 |
  |---|---|---|---|---|
  | `w` | 6,752 | 0 | 0 | 6,752 |
  | `mag` | 3,376 | 3,376 | 0 | 0 |
  | `cnt` | 3,376 | 0 | 3,356 | 20 |
  | `off_column` | 76,672 | 0 | 0 | 76,672 |
  | `off_value` | 76,672 | 0 | 0 | 76,672 |
  | `diag_column` | 6,752 | 0 | 0 | 6,752 |
  | `diag_value` | 6,752 | 0 | 0 | 6,752 |

- **Brute force on the clean stores.** Own arrays, every lower entry looked up: `BRUTE_PAIRS|L=2x2|n=211|upper=1198|found=1198|mismatch=0|lower_without_upper=0|upper_without_lower=0`, and the same zeros with `upper=36155` on 2×3 and `upper=7560012` on 3×3 ([`out/brute-windows.hbp`](out/brute-windows.hbp)).
- **Window edges.** One changed value on each side of a pair, in the last row of each window and the first row of the next: 28 of 28 on 3×3 at cap 1,000,000 and 24 of 24 on 2×3 at cap 1,000, each one mismatch, named ([`out/reader-controls.hbp`](out/reader-controls.hbp)).
- **The author's controls.** The 40 `allpairs` outcomes in `CONTROLS.hbp`, replayed with the recorded executable and the author's `mutate_pairs.py`: 72 of 72 recorded rows identical apart from `secs` ([`out/replay-controls.hbp`](out/replay-controls.hbp)).

## Item 4. Independent verification of the reported pair count: PASS

The reader is [`reader/src/main.rs`](reader/src/main.rs) `6ced3899…`, executable `147b7768…`, Rust 1.81, std only, integer only, `cargo +1.81 clippy --all-targets -- -D warnings` at exit 0, 6 of 6 tests. Its SHA-256 constants come from integer roots at start-up and pass the FIPS known answers.

Command, with the key values drawn from the OS after the reader was frozen and recorded before the run:

```
review-reader seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector- --r 66140c50092c464f8b09502b8a812647 --k0 22b50578953e554d --k1 6a05b10f78747e29 --cap 470000000 --manifest native/ym/results/3x4_room_backed/receipts/hf-store/SECTORS-341-374.sha256
```

MEASURED, exit 0, 40 of 40 predicted fields equal, and 20 of 20 fields equal to the recorded line ([`out/reader-3x4.out`](out/reader-3x4.out) `a45458a8…`, [`out/compare-3x4.hbp`](out/compare-3x4.hbp)):

```
REVIEW_READER|L=3x4|sector=Sx+Sy+|n=45508080|rows=45508080|entries=3310759342|diag=45508080|upper=1632625631|lower=1632625631|not_ascending=0|out_of_range=0|zero_z=0|positive_off=0|row_sum_nonzero=0|zero_weight=0|missing_diag=0|sum_w=13060694016|codes=13060694016|flats=7|flat_w=1,3,2,3,3,2,4|flat_rows=0,28,49,44742698,44742719,45507967,45507970|flat_off_entries=20|max_cnt=73|max_w=288|min_z=-36|max_z=72|max_abs_wz=864|used_rooms=3356267422|trailing_rooms=92770|trailing_nonzero_rooms=0|odd_bytes=0|tail_nonzero_bytes=347747335|stream_read=27200000000|merkle=ec03c5f8ea5abd37ed8f80e0e9e7f00e37840a753f33a1008fbd090b18072a0b|merkle_match=1|sectors_match=34/34|fingerprint_upper=671468cc4543adaf9ccb1a27a73355f9|fingerprint_lower=671468cc4543adaf9ccb1a27a73355f9|fingerprint_equal=1|keyed_sum61=0|buckets_nonzero=0|first_bucket=-|windows=4|cap=470000000|verdict=PASS|secs=587|float_used=0|json=0
```

The recorded line it is compared with:

```
ALLPAIRS|L=3x4|sector=Sx+Sy+|n=45508080|rows_read=45508080|entries=3310759342|header_entries=PASS|diag=45508080|pairs=1632625631|passes=4|cap_entries=470000000|value_mismatch=0|lower_without_upper=0|upper_without_lower=0|columns_not_ascending=0|column_out_of_range=0|zero_z=0|positive_offdiag=0|row_sum_nonzero=0|zero_weight=0|missing_diag=0|flats=7|flat_w=1,3,2,3,3,2,4|flat_w_sum=18|sum_w=13060694016|codes=13060694016|whole_space_count=PASS|merkle=PASS|verdict=PASS|secs=2704|json=0
```

The same pass measured what the recorded line leaves out: 92,770 rooms of padding after the last row (742,160 bytes), all zero; the payload merkle `ec03c5f8…`; all 34 sector files equal to the public manifest `9213927b…`, which binds the header block too, since sector 341 starts with it; and 347,747,335 nonzero bytes in the raw tail after the payload, the value the outside seat's Go checker reports.

### The second algorithm

Both tests run over the same pass in O(1) memory. Each compares the multiset of upper triples (h, j, w_h·z_hj), j > h, with the lower triples (j, h, w_h·z_hj), j < h. Neither uses a window.

- **Lane A, a product fingerprint.** Each triple is coded as a field element m, one to one for rows and columns below 2³¹, which the reader and its out-of-range counter hold. The test is ∏(r − m) over the upper triples = ∏(r − m) over the lower, in GF(2¹²⁷ − 1), at a random r. **False-pass rate:** two different multisets give two different polynomials of degree at most N = 1,632,625,631, which agree at no more than N points, so at most N/(2¹²⁷ − 1) ≈ 9.6 × 10⁻³⁰ for stores fixed before r is drawn. This bound assumes nothing about any hash. Measured values: `671468cc4543adaf9ccb1a27a73355f9` on both sides.
- **Lane B, a keyed sum.** Σ ± SipHash-2-4(min(h,j), max(h,j), w_h·z_hj) modulo 2⁶¹ − 1, plus the upper triples and minus the lower. **False-pass rate:** at most 9/2⁶⁴ ≈ 4.9 × 10⁻¹⁹ if SipHash-2-4 with these keys behaves as a random function, an assumption tagged NAMED. It also keeps 695 sums by leading row, to localize a failure. Measured: 0, and 0 nonzero buckets.
- **What the two would miss.** A change that keeps both sides of a pair equal, or removes both sides of a pair: `fullrebuild` owns that question, and the reader's `entries=` compare catches a removal. The diagonal, which the row sum covers, and `M`, which neither test reads. A duplicate pair present on both sides, which the column counter catches. A store built after seeing r and the keys: they are public here, so a replay should draw its own. A fault in the reader's row walk reaches both lanes alike: the controls below measure that walk.
- **Controls, MEASURED.** Both lanes reported 2,396 of 2,396 single changed values on 2×2, 211 of 211 changed weights, 71 of 71 moved columns and 52 of 52 window-edge faults on 2×3 and 3×3, and passed 70 of 70 symmetric changes as designed ([`out/reader-controls.hbp`](out/reader-controls.hbp)). Lane A's values, recomputed in Python big integers with the same r, match the reader's on 2×2, 2×3 and 3×3 ([`out/fingerprint-check.hbp`](out/fingerprint-check.hbp)). Lane B's nonzero sum on a faulted 2×2 store, recomputed in Python with the same keys, matches too, `363212212049028539` ([`out/keyed-sum-check.hbp`](out/keyed-sum-check.hbp)). The reader's windows equal the tool's on 2×3 and 3×3. A rehearsal on a store split into three sectors of a length that is no multiple of 16 MiB matched its manifest, merkle and tail count ([`out/reader-rehearsal-seg.out`](out/reader-rehearsal-seg.out)).

## Item 5. Whether the recorded results support exactly the claims: FAIL

**Supported, MEASURED or by a named receipt:** n, rows, entries, diagonal, pairs, every zero counter and the four windows, by the reader above. The recorded line, quoted at `PERRON-TWO-SIDED.md:207`, is byte-identical to `ALLPAIRS-3x4.out`. `entries = diag + 2·pairs` holds. 25 predicted fields equal the output. The 12 `RESULT_FILE` hashes for `allpairs/` and `PERRON-RESULT.sha256` match the files. `allpairs-3x4.err` is 0 bytes and `RUN.hbp` records exit 0. Source hash `f4ea7e85…` matches. At this commit, in `native/ym`, `cargo +1.81 clippy --release --all-targets --locked -- -D warnings` exits 0 and the tool's unit tests pass 11 of 11 ([`out/workspace-clippy-all-targets.log`](out/workspace-clippy-all-targets.log)). This is a local run of the gate, and hosted checks were left to their owner. A build from this commit equals the recorded executable in `.text`, `.data`, `.pdata` and `.reloc`, with 24 differing bytes in all, the PE timestamps and the PDB GUID ([`out/pe-compare.out`](out/pe-compare.out)). Flat weights equal `PASSA-CENSUS-3x4.hbp`. Hosted run 41575947849: `gh run view` gives success at head `62533d11…`, whose `allpairs.rs` and `roomio.rs` are the reviewed hashes, and the artifact digest is `9219e3a9…` as recorded. 289 of 2,401 and 127 of 1,198 recompute. "3.5 GiB" is 470,000,000 × 8 bytes, the entries alone. The recorded run has no peak-memory receipt. A concurrent `allpairs` run of another build, described to this seat as holding 3.5 GiB, showed a peak working set of 4,038,279,168 bytes. Command for these checks: `python3 -I -X utf8 attack/receipts_check.py`, output [`out/receipts-check.hbp`](out/receipts-check.hbp), which holds the line behind C1:

```
CONTROL_COMPOSITION|total=49|clean_stores=5|allpairs_rejects_a_repaired_change=23|allpairs_passes_a_repaired_change_by_scope=9|allpairs_unrepaired_byte=3|fullrebuild_outcomes=9|caps_3x3=1|json=0
```

**Beyond the receipts:**

| # | Where | Statement | MEASURED finding | Text the receipts support |
|---|---|---|---|---|
| C1 | `PERRON-TWO-SIDED.md:215`, `README.md:64`, `RESULT_ALLPAIRS_3x4` | "with a store's merkle repaired after one change: 49 of 49", "Its controls … all 49" | The 49 are 5 clean stores, 23 repaired changes rejected, 9 repaired changes passed by scope, 3 unrepaired bytes, and 9 outcomes of `fullrebuild` | "40 `allpairs` outcomes and 9 `fullrebuild` outcomes: 5 clean, 32 with a repaired change, 3 with an unrepaired byte" |
| C2 | `PERRON-TWO-SIDED.md:215` | "at large and small windows" on 2×2, 2×3 and 3×3 | 3×3 ran at one cap, 1,000,000. This review adds 9 caps on 3×3 | "2×2 and 2×3 at two caps, 3×3 at cap 1,000,000" |
| C3 | `PERRON-TWO-SIDED.md:215` | "An unrepaired byte stops it at the merkle with exit 1" | Holds for payload bytes with n ≥ 1. Header bits: 1,771 of 2,912 flips exit 0 (D8), and `n=0` skips the merkle (D1) | "An unrepaired payload byte" |
| C4 | `allpairs.rs:11-12` | "Exit 0 only when every gate holds" | An OPEN gate exits 0 (D2), and so does n = 0 (D1) | Holds after the fixes below |
| C5 | `allpairs.rs:6,11` | "Memory stays bounded", "CAP_ENTRIES bounds the upper entries one window holds" | Peak working set grows with padding (D4). The first row of a window enters above the cap | "Bounded when the padding is small and no row exceeds the cap" |
| C6 | `PERRON-TWO-SIDED.md:33` | "H′ is W-self-adjoint: … 1,632,625,631 off-diagonal pairs" | 20 of those pairs touch flat rows, which H′ removes, with `flat_flat_couplings=0` from `RESULT_P0`, so H′ holds 1,632,625,611 | "All 1,632,625,631 pairs of the stored rows, 1,632,625,611 of them in H′" |
| C7 | `PERRON-REVIEW.md:136` | "with W the orbit weights, measured on every pair by `allpairs`" | `allpairs` reads W from the rows. That W is the orbit weights comes from `fullrebuild`, `weight_mismatch=0` | "with the stored weights, measured by `allpairs`, which `fullrebuild` matches to the orbit weights" |

**INCONCLUSIVE: "as predicted in writing first", for the 3×4 run** (`README.md:64`, `PERRON-BOUND.md:111,225`, `PERRON-REVIEW.md:8`, `PERRON-TWO-SIDED.md:204`, `predicted_first=1`). MEASURED: `ALLPAIRS-RUN.hbp` first appears in git in `8faadb0`, at 04:58:34Z, after the run's recorded end at 04:45:40Z. The source reached git in `e735ae5` at 04:04:40Z, after the recorded start at 04:00:35Z. The order rests on the rows' own timestamps. The predicted values follow from the header (`n`, `entries`, and (entries − n)/2 = pairs), the cap, and the earlier `passA` census, so what the prediction could lose on is the zero counters and the window count. To settle it next time: push the prediction row before the run starts. For the fixture controls the code that computes the prediction is in `62533d11`, pushed before run 41575947849, which supports that claim. This review's own predictions carry the same limit until `REVIEW.hbp` is published.

**NOT_MEASURED, reason NOT_REACHABLE_FROM_HERE:** "An outside seat recommended this check, and the operator relayed its approval" (`PERRON-TWO-SIDED.md:203`). 2,704 s is the recorded run's own clock.

## Defects

D1, D2, D3, D5, D6, D7 and D8 have rows in [`attack/repro.py`](attack/repro.py), which needs only the public fixture and takes an absolute path to the executable:
`python3 -I -X utf8 attack/repro.py <allpairs> native/ym/results/3x4_stream/perron/allpairs/fixture-controls/fixture-2x2.rooms.gz`.
D4 uses `attack/mem_stores.py` and `attack/mem_probe.ps1`. The full header table in D8 comes from `fuzz headerflip`.
MEASURED on the recorded executable and on this seat's build: all 21 rows as listed ([`out/repro-recorded.hbp`](out/repro-recorded.hbp)). A fixed tool will differ on its D rows and must keep its C rows, so the script doubles as a regression check for a later diff.

**D1. `n=0` passes with no rows read and prints `merkle=PASS`, with no merkle computed.** `allpairs.rs:252` (no pass runs), `:217-226` (`covers` is vacuous), `:329`, `:331` (`merkle=PASS` is a literal). Reproducer, a 4096-byte file holding one line:

```
printf 'YMROOMHDR|n=0|payload_bytes=0|w_self_adjoint=PASS\n' > s.bin; truncate -s 4096 s.bin; allpairs s.bin 0; echo $?
ALLPAIRS|L=|sector=|n=0|rows_read=0|entries=0|header_entries=OPEN|diag=0|pairs=0|passes=0|cap_entries=470000000|value_mismatch=0|lower_without_upper=0|upper_without_lower=0|columns_not_ascending=0|column_out_of_range=0|zero_z=0|positive_offdiag=0|row_sum_nonzero=0|zero_weight=0|missing_diag=0|flats=0|flat_w=|flat_w_sum=0|sum_w=0|codes=-|whole_space_count=OPEN|merkle=PASS|verdict=PASS|secs=0|json=0
0
```

The 2×2 store with a changed payload byte, its merkle left stale, and `n=0`, `entries=0` and no `nl=` in the header, also exits 0. Fix: `n == 0` is an error, and print `merkle=` only from a compare that ran. **Effect on the recorded 3×4 result:** none. `n=45508080`, `passes=4`.

**D2. An unreadable count field leaves its gate OPEN, and OPEN exits 0.** `allpairs.rs:316-329`: `entries_gate != "FAIL" && count_gate != "FAIL"`. The unit test at `:584` holds the `None` for a wrong link count in place. Reproducers on the 2×2 store with the merkle repaired: every weight doubled gives exit 2 with `nl=8`, and exit 0 with `sum_w=15552|codes=-|whole_space_count=OPEN` when `nl=` is removed, set to 7, or `L=` is set to `2y2`. One pair removed gives exit 2 with `entries=2607` and exit 0 with `entries=abc`. MEASURED: every one of the 48 bit flips in `L=` and 40 in `nl=` exits 0. The line for doubled weights with `nl=` removed, exit 0:

```
ALLPAIRS|L=2x2|sector=Sx+Sy+|n=211|rows_read=211|entries=2607|header_entries=PASS|diag=211|pairs=1198|passes=1|cap_entries=470000000|value_mismatch=0|lower_without_upper=0|upper_without_lower=0|columns_not_ascending=0|column_out_of_range=0|zero_z=0|positive_offdiag=0|row_sum_nonzero=0|zero_weight=0|missing_diag=0|flats=7|flat_w=2,6,4,6,6,4,8|flat_w_sum=36|sum_w=15552|codes=-|whole_space_count=OPEN|merkle=PASS|verdict=PASS|secs=0|json=0
```

Fix: exit 0 only when both gates read PASS, with test stores given real fields. **Effect:** none. The recorded line has `header_entries=PASS` and `whole_space_count=PASS`.

**D3. Payload after the last row is hashed and never read.** `roomio.rs:96`, and nothing compares `rooms=`. The builder's format says this padding is zeros (`ymroom.rs:18-19`). Reproducers, merkle repaired: padding filled with `0xFF`, and an asymmetric row placed right after row n−1, each exit 0 with `rows_read=211`. Fix: require every byte after the last row to be zero, and compare `rooms=`. **Effect:** none. MEASURED on 3×4: 92,770 rooms, 0 nonzero.

**D4. Memory grows with that padding.** `roomio.rs:93,110`: once `h == n`, `p` stays 0, so `carry` keeps every later byte. Also `allpairs.rs:63` (`flat_w`) and `:131-132` (`w`, `off`) sit outside the cap. MEASURED, two rows plus zero padding at cap 1000, each exit 0 ([`out/mem-probes.hbp`](out/mem-probes.hbp)):

| Padding | Peak working set, bytes |
|---|---|
| 64 MiB | 138,350,592 |
| 256 MiB | 436,854,784 |
| 1,024 MiB | 1,228,926,976 |

Fix: stop keeping bytes after the last row. **Effect:** none. Padding 742,160 bytes, 7 flat rows.

**D5. `cap_entries` prints the argument, and the window uses the clamped value.** `allpairs.rs:246` against `:331`. Reproducer: cap 0 prints `cap_entries=0` with `passes=188`, the same as cap 1. Cap 18446744073709551615 prints that number and uses 4,000,000,000. **Effect:** none. 470,000,000 is in range.

**D6. The output never names the store.** `allpairs.rs:331` prints `merkle=PASS` and no value, and `ALLPAIRS-RUN.hbp` and `RESULT_ALLPAIRS_3x4` carry no merkle or manifest. MEASURED: the clean 2×2 store and a copy with one pair changed on both sides print identical lines apart from `secs`, with merkles `b7c5847b…` and a repaired one. A four-row store labelled `L=3x4|nl=24` with weights summing to 6¹³ prints `whole_space_count=PASS|header_entries=PASS|merkle=PASS|verdict=PASS` (`n=4`). Fix: print `payload_merkle=` and a hash of the header block, and add the merkle to the RESULT row. **Effect:** the recorded line alone cannot name its store. The path in `run_allpairs34.sh`, the read-only attribute and October 28 date on all 34 sector files ([`out/sector-attrs.hbp`](out/sector-attrs.hbp)), the four recorded windows, and this seat's merkle and manifest match on those bytes today tie it to `ec03c5f8…`.

**D7. `upper_without_lower` is `stored − found`, which a doubled lookup can cancel.** `allpairs.rs:200`, with `saturating_sub`, and `pairs_clean` at `:229-239`. Reproducer: in row h double the lower entry that points at row i, and delete row m's entry that points at row i, row sums kept. Row i's entry for m now has no partner, and the doubled lookup takes its place in the count. MEASURED, at caps 470,000,000, 100 and 13 ([`out/d7-found.hbp`](out/d7-found.hbp)): `stored=1198|found=1198|lookups=1198`, `value_mismatch=0|lower_without_upper=0|upper_without_lower=0` with one entry truly unpaired, and `columns_not_ascending=1|verdict=FAIL`, exit 2. By those counts `pairs_clean` is true on that store. The fuzz saw this on rows with non-ascending columns only, 4,282 times in 200,000 cases, and these counters vary with the cap there on 805 cases. The verdict stays right, carried by the column gate. Fix: a bit per stored entry, 59 MB at this cap, marks each entry answered and gives a direct count of unpaired entries. **Effect:** none. `columns_not_ascending=0`.

**D8. The header block is under no hash.** `roomio.rs:25-37` reads it, and the merkle starts at `off + 4096`. `L=` and `sector=` are printed unchecked beyond the count gate's V, and `rooms=`, `stream_bytes=`, `chunk=`, `keys_sha256=` and all bytes after the newline go unread. MEASURED, every bit of the 2×2 header line plus 64 bytes after it, rows unchanged ([`out/headerflip-2x2.err`](out/headerflip-2x2.err)): 1,771 of 2,912 flips exit 0, including all 152 in `stream_bytes`, all 88 in `rooms`, and 83 of 104 in `entries`. `n`, `payload_bytes`, `payload_merkle` and `w_self_adjoint` have 0 flips at exit 0. Fix: D2's fix closes `L`, `nl` and `entries`, and printing the header's hash (D6) covers the rest. **Effect:** none. Sector 341's hash, which covers the header block, matches the public manifest.

## Open

| Item | Status |
|---|---|
| Replay of `allpairs` on another machine from the public files | OPEN, about 2,704 s |
| This seat's reader on another machine, from the public files, with new r and keys | OPEN, 587 s here |
| An exact pair test in the outside seat's own code | OPEN, as the docs state |
| Review of any later diff of `allpairs` | OPEN. For it: `attack/repro.py` on the new executable, `attack/brute_windows.py`, and the harness reassembled from the new source plus `fuzz/harness_tail.rs` |
| Tool fixes for D1 to D8 and the wording of C1 to C7 | OPEN, the author's call |

## Deviations and this review's own errors

Kept beside the results, as MEASURED in `REVIEW.hbp`:

- **A boundary breach.** Git Bash `/tmp` is `C:/Users/acer/AppData/Local/Temp`, and four helper scripts went there: `p.py`, `p2.py`, `p3.py`, `p4.py`. Earlier files of those names may have been overwritten, which this seat cannot see: `p5.py` to `p7.py` dated November 1 sit beside them. The four are left in place, with copies in `helpers/` and hashes in `out/stray-tmp-files.sha256`. A failed command chain also ran the existing `/tmp/p5.py`, which stopped at its line 2 with an `IndexError`, and created an empty `C:/tmp/opus55/fuzz_run2.cmd`, since removed.
- **Session working directory.** The harness set it inside the author's worktree. Every command used absolute paths into the review folder and the checkout.
- **Lookups with no prediction row.** The read-only checks of git history, `gh run view`, `gh api`, sector attributes, the `RESULT_FILE` hashes and the D7 counts ran with no prediction written first. `REVIEW.hbp` names them in a `NOTE` row.
- **Failed first tries.** A reader test expected a wrong window list, the rule was right. Clippy flagged a range loop in the reader. The fuzz launcher did not start at first, and its stderr for the sweep landed in `out/.err`, renamed after the run. Two index faults in this seat's fuzz generator stopped a first long run, with 0 tool panics. A memory probe passed its arguments as one string and measured nothing, then was fixed and rerun. Each outcome is recorded beside its prediction. The raw outputs of those two failed runs were replaced by their reruns, and their rows stay in `REVIEW.hbp`. `bin/fuzz.exe` keeps the generator that panicked.

## Files

All under this folder, hashed in [`HASHES.sha256`](HASHES.sha256): `reader/` (the reader), `fuzz/` (`harness_tail.rs` and the assembled `src/main.rs`), `attack/` (`attacks.py`, `repro.py`, `brute_windows.py`, `reader_controls.py`, `replay_controls.py`, `harness_controls.py`, `stars.py`, `stars2.py`, `sizes.py`, `receipts_check.py`, `compare_3x4.py`, `fingerprint_check.py`, `keyed_sum_check.py`, `pe_sections.py`, `mem_probe.ps1`, `mem_stores.py`), `out/` (outputs), `bin/` (the executables), `REVIEW.hbp` (every prediction and outcome). The harness grew during the review: `bin/fuzz.exe` ran the sweep, `bin/fuzz2.exe` the fuzz, `bin/fuzz3.exe` the bit flips, with each hash in `REVIEW.hbp` and the changes in `helpers/`.
