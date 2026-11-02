# Independent review of the 3×4 Perron bound

This page is for someone who wants to check this work or break it. A counterexample or a failed step is as useful as a
confirmation. Please post either on
[PR #79](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/79).

**Where it stands:** three reviewers have read the argument and accept it, with the lift conditional on a row check. An
outside seat replayed the row rebuild on GitHub Actions from the public data: 2,564 of 2,564 sampled rows match the definition
of H, including the tightest row, and the store's merkle recomputed from the download matches. A local run matched 4,264 of
4,264 rows, with at least 88 from every one of the 34 sectors. The same outside seat then re-ran the certificate on another
machine, [run 41444444894](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41444444894): the same 93.061051, row and M, with row sums, the key table and W-self-adjointness passing on
all rows, and 385,827 exact weighted pairs. Open: a checker written by someone else, and a registered rule. The derivation is in
[`PERRON-BOUND.md`](PERRON-BOUND.md), and the measured rows are in [`PERRON-RESULT.hbp`](PERRON-RESULT.hbp).

## 1. What is being claimed

The model is S₃ lattice gauge theory on a periodic 3×4 lattice with 24 links: H = J_E·E + J_B·M on gauge-invariant
states, with E summing over the three transpositions on every link, M = Σ_p (2 − χ(U_p)), and r = J_B/J_E. "Gap" here means
**E₉ − E₈, the gap above the eight flat states**, on this one finite lattice.

| Step | Claim | Status |
|---|---|---|
| C1 | On the store's Sx+Sy+ rows at r = 9, the published `d` gives min_h (H′d)_h / d_h = t_cert, in exact integers, rounded down | MEASURED by two separately written checkers, one author, and re-run on another machine by an outside seat |
| C2 | E₈ of the Sx+Sy+ sector, which has 7 flat states, is ≥ t_cert | Follows from C1 by interlacing and Barta, given that the rows are H |
| C3 | E₉ of the whole gauge-invariant space, all momenta and symmetry sectors, is ≥ t_cert | DERIVED. Three reviewers accept the argument. Counted by separate code on 2×2 and 2×3. 2,564 3×4 rows rebuilt on another machine have the row structure it uses |
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

Every tool recomputes the store's payload merkle, `ec03c5f8…`. The name `t_cert_milli` is the `t_milli` used across the
tools: at JE = 1000 it counts 10⁻⁶ J_E, so 93061051 means 93.061051 J_E. `d` is one little-endian i64 per row, and every
checker works in exact integers (i128 in Rust, Python integers), rounding the ratio down.

**Better still, write your own check.** It is short, and it is the strongest test of C1:

- The store is one stream across the sector files: a 4096-byte header block holding one text line, then the rows in
  index order, then zero padding. The header line gives `n`, `rooms` and `payload_bytes`.
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

   Your own version would be a stronger test. `passA.bin` has 16 bytes per row, in row order, with key as u64, weight as u32
   and magnetic number as u32, little-endian. A key holds the base-6 digits of the gauge-fixed links, least over the orbit,
   and the digits name the permutations 012, 021, 102, 120, 201, 210 in that order. The builder is
   [`ymroom.rs`](../../../crates/torusl/src/bin/ymroom.rs).
2. **Interlacing in a non-orthonormal basis.** The rows are W-self-adjoint, with W the orbit weights. Check that removing
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
[`REPLAY-41444444894-VERIFY-3X4-PAIRS.hbp`](REPLAY-41444444894-VERIFY-3X4-PAIRS.hbp). The tools have one author, so a checker written by
someone else is still open.

| Reviewer | Point | Status |
|---|---|---|
| 1, 2, 3 | Interlacing, Barta and the W^(1/2) cancellation hold | Accepted on reading |
| 1, 3 | The lift is valid when the sector is the exact symmetry reduction | Accepted in principle. Attack 1 is open |
| 1, 2, 3 | Rebuild sampled 3×4 rows from `passA.bin` with separate code | **Matched on 3×4:** 2,564 and then 5,556 rows on another machine, and 4,264 locally, across all 34 sectors |
| 2 | Another seat's pass over the 45.5M rows | Done: run 41444444894 read all 45.5M rows with `check_d_strict.py`, with the same value, row and M |
| 1 | The builder's aggregate symmetry checksum needs an exact check on pairs, preferably all of them | `verify_sample_rows.py --pairs` checks every pair the rebuilt rows touch, exactly. `check_d_strict.py --self-adjoint` tests all pairs by a random bilinear form drawn from SHA-256. Both ran on 3×4 in run 41444444894: 385,827 exact pairs, and `W_self_adjoint=PASS` |
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

The registered rule, [`GAP-VERDICT-RULE-3X4.md`](../GAP-VERDICT-RULE-3X4.md), stays in force, and the Perron route is a draft:
[`PERRON-RULE-DRAFT.md`](PERRON-RULE-DRAFT.md).
