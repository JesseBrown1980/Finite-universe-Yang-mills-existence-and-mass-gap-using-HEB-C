# Stage 2J — Byte-exact RIME Prism / HEB-C bridge

Third reviewable layer, alongside PR #4 (certified finite Hamiltonian, Issue #2)
and PR #5 (tested RIME/Hamiltonian symmetry constraints). This layer touches
neither; it is a data bridge around the original RIME Prism transform.

**Direction (operator, 2026-10-25):** build on the sphere, keeping its original
source, transform and controls intact. Preserve the original Python NTT and
C1–C4; add the HEB-C Rust verification and HBP/HBI receipt layer around them.

## What is retained, unchanged

| file | origin | git blob |
|---|---|---|
| `native/vendor/rime_sphere_source/rime_prism_pipeline.py` | ASOLARIA-UNIVERSE-SIMULATOR @ `3f9f42d`, `players/` | `da8e4c92dabef3702f9d3d4a743bdc5ad6e3da59` |
| `native/vendor/rime_sphere_source/rime_sphere.py` | same | `449ac82b82223349ca8fc41d8e9b005fd3beda06` |

CI checks both blobs, then runs the original script as-is and requires its own
`C1 identity ... byte-exact = True`.

## The implementation distinction this stage pins

In the original script, `bt(k)` maps each of the 27 coordinate **positions** to
a balanced-ternary RGB cell in {-1,0,1}³. Those labels are the same for every
block, so they carry no information about any block. `bt` is defined but not
called in `main()`; C1/C2 pass because the inverse runs on the full NTT
**coefficient values** in Z/1000081.

So the bridge carries the coefficients. The labels are metadata.

## What was added

- `native/scripts/rime_sphere_carrier.py` — **imports** `ntt`/`intt` and
  `primitive_root` from the vendored original (no re-implementation) and writes
  `carrier.rime` + `xcheck.measure`.
- `native/src/rime_sphere_bridge.rs` — integer-only Rust: the same bank
  (p=1000081, g=7, w=951846), `encode`/`decode` of the carrier (tail bytes kept,
  so any length is byte-exact), the controls, and HBP/HBI/anchor receipts.
- CLI: `hebc rime-sphere-bridge [dir] [input]`, `rime-sphere-verify [dir] [input]`,
  `rime-sphere-decode CARRIER OUT`.

The Rust and Python carriers and cross-check lines must be **byte-identical**
(CI `cmp`, and a unit test pins the Python carrier sha
`6121bb3ff559cf5d…`). Two languages, one transform, one answer.

## Acceptance report

Default input = the original pipeline's own fallback, `(i*7)%251`, 13,500 bytes,
500 blocks of 27. (The original banner prints "real enwik" but silently uses
this fallback when its enwik8 path is absent; the vendored file is left as-is.)

### C3: individual-byte recovery vs whole-block recovery

These are different measures and are reported separately (`c3_bytes`,
`c3_blocks`). A byte can match by chance; a block counts only if all 27 match.

| k of 27 kept | bytes recovered | whole blocks recovered |
|---|---|---|
| 3 | 0 / 13,500 | 0 / 500 |
| 9 | 0 / 13,500 | 0 / 500 |
| 18 | 0 / 13,500 | 0 / 500 |
| 24 | 0 / 13,500 | 0 / 500 |
| 26 | 0 / 13,500 | 0 / 500 |
| 27 | 13,500 / 13,500 | 500 / 500 |

### Guaranteed vs observed

**Theorems — hold for every input; the only things `result=PASS` gates on:**

| | why it must hold |
|---|---|
| C1 identity, C2 carrier round trip | 27 divides p−1 = 1,000,080, so a primitive 27th root w exists, and 27 is invertible mod p; the NTT is a bijection on Z/p²⁷ |
| C3 at k = 27 | is C1 |
| C4 wrong root, byte 0 always survives | inverse index 0 is N⁻¹·ΣXₖ, which contains no power of the root |
| C5 label rows distinct = 1 | `bt(k)` depends only on the position k, never on the block |
| C5 labels-only bound | a decoder that sees only identical labels must emit one fixed block, so it is exact on at most the most-repeated block's count |

**Observations — measured on this input, reported, never required:**

| | measured | why it is not universal |
|---|---|---|
| C3 fails for k < 27 | 0 bytes, 0 blocks | a constant block has X = (27c, 0, …, 0) and recovers from one coefficient; tested in `c3_fraction_failure_is_observed_not_universal`, and the bridge still PASSes on it |
| C4 random address | 0 / 2,700 | chance matches are possible on other inputs |
| C4 wrong root, bytes other than 0 | 0 here | on `README.md`: 1,006 / 12,285 = the 455 guaranteed byte-zeros + 551 coincidental matches. Decode still fails closed on the input sha |
| C5 labels-only maximum | 2 / 500 blocks | equals this input's most-repeated block; an input of one repeated block would give its full count |

The measure line carries this split verbatim:
`theorem=C1,C2,C3_k27,C4_wrong_root_byte0,C5_single_label_row,C5_bound_le_max_block_multiplicity|observed=C3_k_lt_27_counts,C4_random_counts,C4_wrong_root_other_bytes,C5_max_exact_value`.

### Kept in CI

- 73 Rust tests (64 existing + 9 bridge), Clippy `-D warnings`, release build — Rust 1.81.0
- original source blobs checked, original script run unmodified
- cross-language `cmp` of carrier and cross-check line, Python vs Rust
- bit-exact replay, and receipt + carrier tamper rejection
- real-file round trip: `README.md` through the bridge and back, `cmp` exact, Python and Rust carriers identical (also run locally on `STAGE2I_INDEPENDENT_VERIFIER_AND_SCALING.md`, 12,256 bytes, 25-byte tail)

## Cost, stated

Each coefficient lives in Z/1000081 and needs 20 bits; a 27-byte block (216
bits) is carried in 540 bits — `carry_ratio=5/2`. The information-theoretic
floor for a uniform element of Z/1000081 is 27·log₂(1000081) ≈ 538.2 bits, so
the 20-bit packing wastes under 0.4%. **No compression is claimed**
(`compression_claimed=0`). The alternative, carrying only a reference to a
verified source bank, is cheaper to transmit but recovers nothing when the
bank is absent — the original C4 "missing bank" control.

## Scope

This stage is a verified transport and receipt layer around the original sphere
transform. It makes no claim about Yang–Mills, the mass gap, or physical
mechanism, and does not change any Stage 2G–2I result.
