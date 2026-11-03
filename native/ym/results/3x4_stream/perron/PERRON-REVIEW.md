# Independent review of the 3×4 Perron bound

This page is for someone who wants to check this work or break it. A counterexample or a failed step is as useful as a
confirmation. Please post either on
[PR #79](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/79).

**Where it stands, November 3:** the bound stands at **94.070673 J_E**, certified by the author's two checkers on `x3-c.bin`, with λ₁(H′) ≤ 94.070936 from the same store ([`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md)). An outside seat's Go checker, written separately from this page's formats,
prints the same value, row and M on `x3-c.bin` and on two other vectors, as predicted in writing beforehand ([run 41509351749](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41509351749)). A second seat tried to refute the new work and refuted no printed bound ([`REVIEW-OPUS55.md`](REVIEW-OPUS55.md)). A second seat's `fullrebuild` recomputed all 45,508,080 rows from the rules, with 0 mismatches and merkle PASS, as predicted in writing first ([`FULLREBUILD-3x4.out`](FULLREBUILD-3x4.out)). `allpairs` compared every off-diagonal pair exactly: 1,632,625,631 pairs with w_h z_hj = w_j z_jh, 0 mismatches, with a prediction row time-stamped before the start, which reached git after the run ([`allpairs/ALLPAIRS-3x4.out`](allpairs/ALLPAIRS-3x4.out)). Faults on small fixtures with every hash repaired reach the row-sum and self-adjoint gates of all three checkers ([`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md), section 5). Earlier the same day:
three reviewers have read the argument and accept it, with the lift conditional on a row check. An
outside seat replayed the row rebuild on GitHub Actions from the public data: 2,564 of 2,564 sampled rows match the definition
of H, including the tightest row, and the store's merkle recomputed from the download matches. A local run matched 4,264 of
4,264 rows, with at least 88 from every one of the 34 sectors. The same outside seat then re-ran the certificate on another
machine, [run 41444444894](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41444444894): the same 93.061051, row and M, with row sums, the key table and W-self-adjointness passing on
all rows, and 385,827 exact weighted pairs. Open: a registered rule and the operator's word on a verdict, then uniformity in volume and the continuum limit, since each result here is a statement about one finite lattice. The derivation is in
[`PERRON-BOUND.md`](PERRON-BOUND.md), and the measured rows are in [`PERRON-RESULT.hbp`](PERRON-RESULT.hbp).

**A correction beside that, November 3:** `allpairs`, the exact pair test, let `OPEN` through on its two count gates. The recorded 3×4 line prints `PASS` on both, and that executable stays pinned at commit `8faadb0`, `c68f25b4…`. The corrected executable is `d78f263f…`, source `5ab04b18…`, and section 4 has the finding, with 124 of 124 header-control outcomes as predicted. A full 3×4 run with the corrected executable, rebuilt from the source pinned at `0fd24d3`, `cdb22218…`, printed the same rows apart from `secs=`, with 31 of 31 of the operator's requirements met.

**A second seat's review of `allpairs`, November 3: FAIL overall**, on fail-closed behavior and on wording, with PASS on window partitioning, on unpaired edges and on the pair count, which its own reader confirmed on this machine. The recorded 3×4 numbers stand. D1 and D2 are closed in the corrected executable, and D3 to D8 stayed open in it: [`allpairs/failclosed/review-opus55/ALLPAIRS-REVIEW.md`](allpairs/failclosed/review-opus55/ALLPAIRS-REVIEW.md) and [`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md), section 5. **The fixes, later on November 3:** D3 to D8, and the findings of the review's later parts, are fixed in two steps, each with controls and a full 3×4 run. The final tool, source `adcacfc5…`, executable `b0682e72…`, exits 0 in 2,880 s and meets every predicted field, in the same section. It ran on the same model as this seat, on this seat's machine. A replay on another machine is open.

## 1. What is being claimed

The model is S₃ lattice gauge theory on a periodic 3×4 lattice with 24 links: H = J_E·E + J_B·M on gauge-invariant
states, with E summing over the three transpositions on every link, M = Σ_p (2 − χ(U_p)), and r = J_B/J_E. "Gap" here means
**E₉ − E₈, the gap above the eight flat states**, on this one finite lattice.

| Step | Claim | Status |
|---|---|---|
| C1 | On the store's Sx+Sy+ rows at r = 9, the published `d` gives min_h (H′d)_h / d_h = t_cert, in exact integers, rounded down | MEASURED by two separately written checkers, one author, re-run on another machine by an outside seat, and printed by that seat's own Go checker on the vector at the top |
| C2 | E₈ of the Sx+Sy+ sector, which has 7 flat states, is ≥ t_cert | Follows from C1 by interlacing and Barta. That the rows are H is MEASURED on all 45,508,080 by `fullrebuild` |
| C3 | E₉ of the whole gauge-invariant space, all momenta and symmetry sectors, is ≥ t_cert | DERIVED. Three reviewers accept the argument. Counted by separate code on 2×2 and 2×3. 2,564 3×4 rows rebuilt on another machine have the row structure it uses, and `fullrebuild` matches all 45,508,080 on this seat's machine |
| C4 | E₈ ≤ 72 J_E for every r, and E₈ ≤ 70.031 J_E at r = 9 | MEASURED (flat states, then a count on a whole-space ball), plus min-max |
| C5 | E₉ − E₈ ≥ t_cert − 72 + 3(r − 9) J_E for every r ≥ 9, and ≥ t_cert − 70.031 J_E at r = 9 | Follows from C1, C3 and C4, with M ≥ 3 MEASURED |

## 2. Repeat the arithmetic

You need about 28 GB of disk and 2 GB of RAM. Everything is public, with open downloads.

```
HF=https://huggingface.co/datasets/Jessedbrown/ym-3x4-room-store/resolve
STORE=$HF/160726aaaf87386090b2b0b9ecf2815ca2634009
PERRON=$HF/d2630edf882f3d9fa125f25680fd9b6a04c98d31/perron

curl -fsSL -O $STORE/SECTORS-341-374.sha256
echo "9213927b3b60cfbeae8efef10730e8c7df2ad52f56159017b048539377886ce3  SECTORS-341-374.sha256" | sha256sum -c
for i in $(seq 341 374); do curl -fsSL -O $STORE/sector-$i.rooms; done
sha256sum -c SECTORS-341-374.sha256

curl -fsSL -O $PERRON/d93000000.bin
curl -fsSL -O $PERRON/passA.bin
echo "956b73bc6f4ec5712184eb52f67d8e0adab467c1ea843ba257126278368210da  d93000000.bin" | sha256sum -c
echo "eefd7752031cf6e1cbfd53dd47128805d1a98bb41de0a9e269222d0e2c6e3cbc  passA.bin" | sha256sum -c
```

The top vector is at `$HF/29723023f37ade227af51e1b92a4a4d55d4bb3f8/perron/top/x3-c.bin`, SHA-256 `f5c5428db1fc5d91d2ab891689f0dac7263dc26c8f9b60a2db82728f6ea0dcd1`.

**With Python alone**, using only the standard library. This also checks every row's structure:

```
python3 -I native/ym/results/3x4_stream/perron/check_d_strict.py 341:34:800000000:./sector- d93000000.bin 1000 9000 \
  --passa passA.bin --self-adjoint 27 \
  --expect-d-sha256 956b73bc6f4ec5712184eb52f67d8e0adab467c1ea843ba257126278368210da
```

Any failed condition prints one `CHECK_D_FAIL` row and exits 2, with no value. Its controls are in
[`STRICT-CONTROLS.hbp`](STRICT-CONTROLS.hbp), and it took 2,038 s on a hosted runner (section 4). The first local 3×4 row came from
the older [`check_d_stream.py`](check_d_stream.py), in 1,863 s under `python -I`. That older file relies on `assert`, which `python -O`
removes: under `-O`, a changed byte printed `merkle=PASS`. Use `check_d_strict.py` for new checks.

**With the Rust tool**, about 10 minutes:

```
(cd native/ym && cargo +1.81.0 build --release --offline --locked -p evolvers --bin perroncert)
native/ym/target/release/perroncert check seg:341:34:800000000:./sector- 0 1000 9000 d93000000.bin
```

| `d` file | SHA-256 | `t_cert` (J_E) | Tightest row | M |
|---|---|---|---|---|
| `d93000000.bin` | `956b73bc…` | 93.061051 | 44,742,735 | 3 |
| `top/x3-b.bin` | `637fe9e2…` | 94.065384 | 44,742,735 | 3 |
| `top/x3-c.bin` | `f5c5428d…` | **94.070673** | 45,507,968 | 3 |

Every tool recomputes the store's payload merkle, `ec03c5f8…`. The name `t_cert_milli` is the `t_milli` used across the
tools: at JE = 1000 it counts 10⁻⁶ J_E, so 93061051 means 93.061051 J_E. `d` is one little-endian i64 per row, and every
checker works in exact integers (i128 in Rust, Python integers), rounding the ratio down.

**Better still, write your own check.** It is short, and it is the strongest test of C1:

- The store is one stream across the sector files, `stream_bytes` long: a 4096-byte header block holding one text line then zeros, then
  `payload_bytes`. The header line gives `n`, `rooms`, `payload_bytes`, `stream_bytes` and `payload_merkle`. The rows take exactly
  8·`rooms` bytes, in index order, with `rooms` = `n` + `entries`. The rest of the payload is zero padding up to a 1 MiB boundary of the
  stream (742,160 bytes on 3×4), and the merkle covers it. **Correction, November 2:** this line read "the rows in index order, then zero
  padding". A separately written checker stopped on that wording. Sector 374 continues past `stream_bytes` with the room store's other
  bytes (349,114,368 bytes, most of them non-zero). The sector SHA-256 covers them, and they lie outside the stream and the merkle.
- A row is an 8-byte header (`w:u32, mag:u16, cnt:u16`), then `cnt` 8-byte entries (`j:u32, z:i32`), little-endian.
- `d` must be 0 on flat rows (`mag = 0`) and positive on every other row.
- For a non-flat row h, with JE = 1000 and JB = 9000, the ratio is
  `(1000·JB·mag·d[h] + 1000·JE·Σ z·d[j]) // d[h]`, in units of 10⁻⁶ J_E. `t_cert` is the minimum over those rows.
- Every entry with j ≠ h must have z ≤ 0. Flat columns contribute 0, because d is 0 there.

## 3. Where to attack it

These are the steps most likely to fail, in the order I would test them.

1. **Are the store's rows really H?** C1 speaks about the rows in the store, and a matching hash proves the bytes are
   unchanged. So far `ymroom text` matched the older builder `ymsec` byte for byte on 2×3, 2×4 and 3×3, the weights in
   `passA.bin` sum to exactly 6¹³, and sector balls read from the store give the same levels as `ball`'s whole-space
   matrices, to 6 decimals at K = 3.

   [`verify_sample_rows.py`](verify_sample_rows.py), separately written, rebuilds each row's weight, M and entries from
   permutations of three objects and compares them with the store. It takes every flat row, a sample at each magnetic number,
   a sample from each sector file, a uniform sample and any rows you name, and it reports the count for every sector. It
   matched every row on 2×2 (211) and 2×3 (2,646), and 2,250 sampled rows on 3×3 across three sector files, and its 14 damage
   controls all exit 2 ([`VERIFY-CONTROLS.hbp`](VERIFY-CONTROLS.hbp)). `--pairs` also checks w_h·z_hj = w_j·z_jh exactly, on every
   pair the rebuilt rows touch. **On 3×4, an outside replay on GitHub Actions matched 2,564 of 2,564 rows (section 4), and a local
   run matched 4,264 of 4,264, with at least 88 rows from every one of the 34 sectors ([`VERIFY34.hbp`](VERIFY34.hbp)). To repeat it:**

   ```
   python3 -I native/ym/results/3x4_stream/perron/verify_sample_rows.py 3 4 341:34:800000000:./sector- passA.bin --rows 44742735 --pairs
   ```

   **All rows:** [`second-seat/fullrebuild.rs`](second-seat/fullrebuild.rs) recomputes every row from the rules and compares it with the store: 45,508,080 rows, 0 mismatches, merkle PASS, in 7,870 s on 6 threads ([`FULLREBUILD-3x4.out`](FULLREBUILD-3x4.out)).
   To repeat it, build it with `rustc +1.81.0 -O` and run:

   ```
   fullrebuild 341:34:800000000:./sector- passA.bin 3 4 6
   ```

   **All pairs:** [`allpairs`](../../../crates/evolvers/src/bin/allpairs.rs) compares w_h·z_hj with w_j·z_jh on all 1,632,625,631 off-diagonal pairs: 0 mismatches, merkle PASS on each of 4 passes, in 2,704 s with a 3.5 GiB window ([`allpairs/ALLPAIRS-3x4.out`](allpairs/ALLPAIRS-3x4.out)). To repeat it, from `native/ym`, with the sectors there:

   ```
   cargo +1.81.0 build --locked --release -p evolvers --bin allpairs
   target/release/allpairs seg:341:34:800000000:./sector- 0 470000000
   ```

   Built from `main`, that is the corrected executable, source `5ab04b18…`. The source of the recorded run is at `git show 8faadb0:native/ym/crates/evolvers/src/bin/allpairs.rs`, `f4ea7e85…`. [`allpairs/failclosed/reproduce_pin_run.sh`](allpairs/failclosed/reproduce_pin_run.sh) builds it, runs it and judges its rows against the original run. On Windows a build's file hash carries link stamps, and [`allpairs/failclosed/pe_normal_hash.py`](allpairs/failclosed/pe_normal_hash.py) gives a hash with them zeroed.

   Your own version would be a stronger test. `passA.bin` has 16 bytes per row, in row order, with key as u64, weight as u32
   and magnetic number as u32, little-endian. A key holds the base-6 digits of the gauge-fixed links, least over the orbit,
   and the digits name the permutations 012, 021, 102, 120, 201, 210 in that order. The builder is
   [`ymroom.rs`](../../../crates/torusl/src/bin/ymroom.rs).
2. **Interlacing in a non-orthonormal basis.** The rows are W-self-adjoint, with W the stored weights, measured on every pair by `allpairs`, and `fullrebuild` matches those weights to the orbit weights. Check that removing
   the flat rows and columns is a principal compression after the W^(1/2) similarity.
3. **Barta for that matrix.** H′ = s − N with N ≥ 0 entrywise, and the bound uses ρ(N) ≤ max_h (Nd)_h / d_h. Check that
   it survives the same similarity.
4. **The lift to the whole space (C3).** This is the least tested step. Check the identity in `PERRON-BOUND.md`,
   section 2, especially moves that return to the same symmetry orbit and rows with non-trivial stabilizers. It has
   been counted by separate code on 2×2 and 2×3 (`SMALL-*.hbp`).
5. **The flat states.** The claim is exactly 8 flat gauge orbits in the whole space and 7 rows in this sector. The 7
   weights are 1, 3, 2, 3, 3, 2, 4, which sum to 18, the number of commuting pairs in S₃. A reflection swaps the classes of
   (c, c) and (c, c⁻¹), which gives the row of weight 4.
6. **The upper side (C4).** E₈ ≤ 70.031 rests on one `shellschur` count on a whole-space ball of 155,386 states, and on
   Rayleigh–Ritz for that ball.
7. **Monotonicity in r.** "For every r ≥ 9" needs M ≥ 0 on every row and M ≥ 3 on non-flat rows, with the flat bound on E₈
   holding for every r.

**What would refute it directly:** any vector with Rayleigh quotient below t_cert on H′, a row where the check gives a
smaller ratio, a positive off-diagonal entry, or a ninth whole-space level below t_cert. The K = 5 sector ball's eighth
level, 94.122 J_E, sits above t_cert, as it must.

## 4. Reviews received so far

Three reviews reached this seat through the operator on November 2, 2026. Their full text is attached:
[`REVIEW-1-full.md`](REVIEW-1-full.md) with its summary [`REVIEW-1.md`](REVIEW-1.md), [`REVIEW-2.md`](REVIEW-2.md) and
[`REVIEW-3.md`](REVIEW-3.md). They read the argument and the code at
`155acdd`, and the data went public after that. Reviewers 1 and 2 hold merge of the 3×4 result until the open items below
close.

**An outside replay matched.** A separate seat ran the row rebuild on GitHub Actions, [run 41441400030](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41441400030), on a fresh
runner. All 34 sector files and the key table matched their SHA-256 after download, and the tool at `2a2e2d4` was pinned by hash:

```
VERIFY_ROWS|L=3x4|n=45508080|rows_rebuilt=2564|seed=27|named_rows=44742735|matched=2564|merkle=PASS|pass_secs=95|secs=175
```

The sample covers every magnetic number from 3 to 36, including all 3 rows at M = 3 and 52 of the 420 rows at M = 36. The receipt
is [`REPLAY-41441400030-VERIFY-3X4.hbp`](REPLAY-41441400030-VERIFY-3X4.hbp).

**The outside re-run of the certificate matched.** The same seat ran both tools at `d8c82ae`, pinned by hash, on the public files
with the vector's hash enforced, [run 41444444894](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41444444894):

```
CHECK_D_STRICT|n=45508080|d_sha256=956b73bc…|flats=7|flat_diag=72|flat_flat_couplings=0|t_cert_milli=93061051|min_row=44742735|min_mag=3|min_nonflat_M=3|max_M=36|positive_offdiag=0|bad_d=0|row_sums_zero=PASS|passa_w_and_M=PASS|W_self_adjoint=PASS|merkle=PASS|secs=2038
VERIFY_ROWS|L=3x4|n=45508080|rows_rebuilt=5556|named_rows=44742735|sectors=34|sectors_with_rows=34|min_rows_in_a_sector=126|matched=5556|weighted_pairs_exact=385827|merkle=PASS|secs=329
```

The receipts are [`REPLAY-41444444894-CHECK-3X4-STRICT.hbp`](REPLAY-41444444894-CHECK-3X4-STRICT.hbp) and
[`REPLAY-41444444894-VERIFY-3X4-PAIRS.hbp`](REPLAY-41444444894-VERIFY-3X4-PAIRS.hbp). These two tools have one author.

**A checker written by someone else matched.** The outside seat wrote its own in Go from this page's formats. [run 41509351749](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41509351749) fetched the public files without a token, each pinned by SHA-256, and printed:

```
PASS merkle=PASS sector_hashes=PASS vector_hashes=PASS row_sums_zero=PASS W_self_adjoint=PASS
control t_cert_milli=93061051 min_row=44742735 min_mag=3
blind t_cert_milli=94070673 min_row=45507968 min_mag=3
flat_rows=7 min_nonzero_mag=3 max_mag=36 weighted_residual=0
```

That is the third of three replays. The others gave 93718415 and 94065384 on `d93700000-pass5.bin` and `x3-b.bin`. All four values, rows and M were predicted in writing before the first checker step. Its log, artifact and source are in
[`outside-go-41509351749/`](outside-go-41509351749/), and [`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md), section 5, has its scope: a self-adjoint test on x, y in −3..3, fault controls in that run that stop at the merkle and at positivity, and fixture controls that reach its row-sum and self-adjoint gates.

| Reviewer | Point | Status |
|---|---|---|
| 1, 2, 3 | Interlacing, Barta and the W^(1/2) cancellation hold | Accepted on reading |
| 1, 3 | The lift is valid when the sector is the exact symmetry reduction | Accepted in principle. Attack 1, the rows, is measured on all rows by `fullrebuild` |
| 1, 2, 3 | Rebuild sampled 3×4 rows from `passA.bin` with separate code | **Matched on 3×4:** 2,564 and then 5,556 rows on another machine, and 4,264 locally, across all 34 sectors, then all 45,508,080 rows by `fullrebuild` |
| 2 | Another seat's pass over the 45.5M rows | Done: run 41444444894 read all 45.5M rows with `check_d_strict.py`, with the same value, row and M |
| 1 | The builder's aggregate symmetry checksum needs an exact check on pairs, preferably all of them | `verify_sample_rows.py --pairs` checks every pair the rebuilt rows touch, exactly. `check_d_strict.py --self-adjoint` tests all pairs by a random bilinear form drawn from SHA-256. Both ran on 3×4 in run 41444444894: 385,827 exact pairs, and `W_self_adjoint=PASS`. All of them: `allpairs`, 1,632,625,631 pairs, 0 mismatches |
| Second seat | Refutation of the new tools and the two-sided claims: 8 of 8 claims survived, with 8 findings in wording, labels, provenance and out-of-range input | [`REVIEW-OPUS55.md`](REVIEW-OPUS55.md), and what changed in [`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md), section 6 |
| Outside seat | Its own Go checker from this page's formats | It stopped first on a wrong line of this page, corrected in section 2. Then [run 41509351749](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41509351749) printed the predicted value, row and M on all four vectors. On fixtures with every hash repaired, [run 41575947849](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41575947849), it reported all 211 row-sum faults and 1,071 of 1,198 single-pair faults, with 127 passing its form, each as predicted. Open on it: an exact pair test in its own code |
| Outside seat, November 3 | Its decisions on the remaining gates, as written: "Wider self-adjointness test": "APPROVE". "Negative controls that reach row-sum and symmetry validation": "APPROVE". "Full row reconstruction evidence": "ACCEPT the recorded result". "Finite-lattice Perron bound": "ACCEPT as independently reproduced computational evidence". "New formal gap-verdict rule": "HOLD pending final rule review and operator approval". "Continuum Yang–Mills claim": "Not certified" | Both tests are done, the first by the exact test it recommended, and the second on isolated fixtures it recommended. The rule stays a draft |
| Review relayed by the operator, November 3, second round | Its decisions, as written: "Accept exhaustive-pair result as recorded computational evidence": "YES". "Accept the reported finite-lattice Perron certificate": "YES, with its stated assumptions". "Register a final 3×4 gap-rule verdict": "HOLD". "Approve the new formal gap-verdict rule": "HOLD". "Claim a continuum Yang–Mills mass-gap solution": "NOT CERTIFIED". Its finding, as written: "the final success condition currently allows `header_entries=OPEN` or `whole_space_count=OPEN`. Requiring both to equal `PASS` would make those gates fully fail-closed. The recorded 3×4 run already passed both gates, so this does not invalidate its result." | Confirmed by reading and by measurement. The original executable, `c68f25b4…`, source `f4ea7e85…` at commit `8faadb0`, reached exit 0 on all 22 header cases with a count gate at `OPEN`. The corrected executable, `d78f263f…`, source `5ab04b18…`, exits 2 on all 26 such cases, with 124 of 124 outcomes as predicted: [`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md), section 5 |
| The operator, November 3 | His decisions, as written: "Create and test fix PR": "APPROVED". "Opus 5.5 adversarial review": "APPROVED". "Merge the future fix PR": "Requires separate authorization". "Formal 3×4 gap verdict": "HOLD". "Register gap-verdict rule": "HOLD". "Continuum mass-gap claim": "NOT CERTIFIED". And: "The original 3×4 result remains valid as recorded because both count gates printed `PASS`." | The fix and its controls are in section 5 of [`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md). The verdict, the rule and the continuum claim stay as he wrote them |
| The operator, November 3, on the 3×4 run | His word, as written: "YES — APPROVED. Run the full 3×4 `allpairs` verification using the corrected executable from PR #84, pinned at `0fd24d3`." And: "Fail closed: Any unexpected result must be recorded as a failure, not corrected or discarded silently." | Done on this seat's machine: exit 0, 31 of 31 requirements met, and all 5 rows the same as the original's apart from `secs=`, in [`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md), section 5. Recorded as a failure of byte reproducibility: three Windows builds of one source gave three file hashes, which differ only in link stamps |
| Decision relayed by the operator, November 3, on the fixes | As written: "Decision — Fix D3–D8: APPROVED". "YES. Fix all six remaining defects." | Done on this branch: [`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md), section 5 |
| The operator, November 3, on another full run | His word, as written: "I say yes to both", to a further full 3×4 run on the final `allpairs` and to an attack on the hybrid certificate of PR #89 | The 3×4 run: exit 0, every predicted field met, in the same section |
| Second seat, November 3, parts two and three on `allpairs` | Its verdicts, as written: "**Overall: FAIL, on the repeat recipe alone.**" "**Overall: FAIL, on one race in the tool and one recipe path.** D3 to D7 close." | Each finding has a row in [`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md), section 5. Open: a reading of the change that came after them |
| Outside seat, November 3, on the fixes. It signs as GPT-6, and the operator names it chatgpt astra 6 | Its verdict, as written: "**SOURCE-REVIEW VERDICT: PASS on the six D3–D8 mitigation paths inspected. EXECUTION VERDICT: INCONCLUSIVE pending dedicated hostile-store controls and a hardened full 3×4 replay.**" It also diagnosed the hosted memory row and reported the syntax error at `31a71db` | The controls and full runs it asked for are in the same section. Its review and comments are on [PR #85](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/85) |
| Second seat, November 3, on `allpairs` | Its verdicts, as written: "**Overall: FAIL.** Items 2 and 5 fail." "**The recorded 3×4 numbers stand.** No defect below changes them." Item 1, windows, PASS. Item 2, overflow, malformed input and fail-closed behavior, FAIL. Item 3, unpaired edges and mismatches, PASS. Item 4, the pair count, PASS. Item 5, the claims, FAIL | D1 and D2 closed in the corrected executable, by [`repro.py`](allpairs/failclosed/review-opus55/attack/repro.py) rerun on both. D3 to D8 open, with their fixes waiting for the operator's word. C1, C2, C3, C6 and C7 corrected in these docs, C4 in the source, and C5 open with D4. The order of the 3×4 prediction now reads as its time stamps and git show it: [`allpairs/failclosed/review-opus55/ALLPAIRS-REVIEW.md`](allpairs/failclosed/review-opus55/ALLPAIRS-REVIEW.md) and [`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md), section 5 |
| 1 | Run negative controls: wrong merkle, swapped `d`, mutated row | Done: [`STRICT-CONTROLS.hbp`](STRICT-CONTROLS.hbp), 18 of 18, and [`VERIFY-CONTROLS.hbp`](VERIFY-CONTROLS.hbp), 14 of 14 |
| 1 | `check_d_stream.py` should fail closed, and `assert` vanishes under `python -O` | Confirmed by measurement: a changed byte printed `merkle=PASS` under `-O`. Fixed in `check_d_strict.py`. The recorded runs used `-I`, so their rows stand |
| 2 | Put the 3×4 run and the location of `d` in the PR | Done: rows here, data on Hugging Face |
| 2 | Match the rule text to the run | Done. The vector for 93 J_E was solved from d = 0, and the warm start at 93.7 J_E starts from it |
| 2 | Say plainly that this is E₉ − E₈ | Done |
| 2 | State the scale of `t_cert_milli` | Done here and in the receipts, and `check_d_strict.py` prints the exact fraction. `perroncert` stays pinned during the warm start |
| 2 | The lift separates the sector claim from the whole-space claim | Accepted. The sector claim is the 8th level of that sector, which has 7 flat states |
| 3 | The bound on E₈ must be the 8th root | Confirmed: the count is 8 levels below 70.031 on a whole-space ball |
| 3 | The store must cover the top magnetic shell | MEASURED: the weights sum to exactly 6¹³, and M runs up to 36 |
| 3 | `d` must be an integer, with exact arithmetic | Confirmed, see section 2 |
| 3 | E₉ − E₈ gains at least 3(r − 9) J_E, since M ≥ 3 on non-flat rows | Accepted, added as C5. M ≥ 3 is MEASURED from `passA.bin` |

## 5. Data on Hugging Face

Dataset: <https://huggingface.co/datasets/Jessedbrown/ym-3x4-room-store>. Paths and hashes are in the `RESULT_HF` rows
of [`PERRON-RESULT.hbp`](PERRON-RESULT.hbp).

| Path | Size | What it is |
|---|---|---|
| `sector-341.rooms` … `sector-374.rooms` | 34 × 800,000,000 B | The 3×4 store |
| `perron/d93000000.bin` | 364,064,640 B | The certificate vector at solve threshold 93 J_E |
| `perron/passA.bin` | 728,129,280 B | Key, weight and magnetic number of every row, for attack 1 |
| `perron/balls/` | up to 80 MB | The ball matrices behind C4 and the sector levels |
| `perron/top/x3-c.bin` | 364,064,640 B | The top vector, 94.070673 J_E |
| `perron/top/x3-b.bin` | 364,064,640 B | The vector at 94.065384 J_E |
| `perron/top/d94058000-hosted.bin`, `d93950000-conv.bin` | 364,064,640 B each | The solved vectors x3-c is made from, with `perron/start/d93700000-pass5.bin` |

The registered rule, [`GAP-VERDICT-RULE-3X4.md`](../GAP-VERDICT-RULE-3X4.md), stays in force, and the Perron route is a draft:
[`PERRON-RULE-DRAFT.md`](PERRON-RULE-DRAFT.md).
