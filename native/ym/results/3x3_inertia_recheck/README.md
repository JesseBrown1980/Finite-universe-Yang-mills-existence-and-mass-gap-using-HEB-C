# 3×3 90M inertia recheck (November 1, 2026)

At `t_milli=90000000` on the 3×3 (+,+) sector, the old merge gives `negative=37`, `positive=2894` and
`ambiguous=9`. `schurcert` reads the same column enclosures and decides every column:

```
SCHURCERT|method=congruence_gershgorin|widen=1|m=2940|negative=44|positive=2896|ambiguous=0|result=PASS
```

That is 44 levels of the 3×3 (+,+) sector below 90 J_E at r = 9. It sits inside the old bounds: the
9 undecided columns split into 7 negative and 2 positive. The ambiguity came from the last step of the
old merge. It needed no new column solves and no more precision.

The rows are in [`RECHECK-RESULT.hbp`](RECHECK-RESULT.hbp), which has a `.sha256` sidecar.

## Method

The old merge eliminates a dense interval matrix. Each update treats its inputs as independent when
they are not, so widths grow far past what the column enclosures imply. `schurcert` uses each
enclosure once:

1. Take the midpoint M of the enclosures, and find a congruence X from a fixed-point elimination of M.
   X only steers. An error in it can lose decisions but cannot change a count.
2. Compute X M Xᵀ in exact integers, and bound the effect of every enclosure radius on it.
3. Apply Gershgorin to the scaled result. If every row is dominant, the result is nonsingular, so X is
   too. By Sylvester's law, S then has as many negative eigenvalues as rows with a negative centre.
4. If any row is undecided, the tool prints `result=AMBIGUOUS` and no count.

The argument and every bound are in the source header:
[`schurcert.rs`](../../crates/sturmrs/src/bin/schurcert.rs).

## Checks

| Matrix | Old merge | `schurcert` | Exact minors on the midpoint |
|---|---|---|---|
| 3×4 60M, m = 137 | 0 / 137 | 0 / 137 | 0 / 137 |
| 3×3 60M, m = 101 | 7 / 94 | 7 / 94 | 7 / 94 |
| 3×3 72M, m = 1,137 | 7 / 1,130 | 7 / 1,130 | 7 / 1,130 |
| 3×3 90M, m = 2,940 | 37 / 2,894, 9 undecided | 44 / 2,896 | see `RECHECK-RESULT.hbp` |

The last column comes from [`independent/minors`](../../independent/minors), written separately from
`schurcert` and `roomschur`. It computes the sign of every leading minor modulo primes up to the Hadamard
bound, and uses no intervals. It covers only the midpoint matrix, which is one matrix in the enclosures.

**Slack.** `SCHURCERT_WIDEN` multiplies every enclosure radius. The 90M count stays 44 / 2,896 at 100,
1,000, 3,000 and 10,000 times the radii. At 100,000 times, 7 rows are undecided and the tool gives no
count. Only `widen=1` is a certificate.

**Repeats and input.** Every result row matched between two builds of the tool at 6 and 2 workers,
apart from timing fields. The input's SHA-256, `8aa62d94…`, matches `GATE3X3-SEG`.

## Scope

- This replaces only the final inertia step. It trusts the column enclosures and does not check them.
- It is a 3×3 result. It says nothing about 3×4 at any threshold, and it is not a gap.
- It is not yet the merge step of any registered spec.
- No second seat has reviewed it.

## Reproduce

```
cd native/ym
cargo +1.81.0 build --release --offline --locked -p sturmrs --bin schurcert
WORKERS=6 target/release/schurcert <SCOL files>
```

The 3×4 60M input is in [`../3x4_stream/production-41321108365/`](../3x4_stream/production-41321108365/)
(`scol-*.out`). The 3×3 inputs are off git, at 1.6 GB for 90M. They are `roomschur-seg-t*.out` in the
`gate3x3-seg` folder recorded in `../3x4_room_backed/receipts/RAW-ARTIFACTS-OFFGIT.hbp`, with their hashes
in `RECHECK-RESULT.hbp`.

For the exact check, [`dump_mid.py`](dump_mid.py) writes the midpoint matrix in a shuffled order,
`indep-minors` reads it, and [`count_signs.py`](count_signs.py) counts the sign changes.
