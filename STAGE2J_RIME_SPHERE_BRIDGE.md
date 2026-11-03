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

### Cross-language checking: what is independent and what is shared

**Independent:**
- **NTT arithmetic.** Rust's `ntt`/`intt` were written separately; Python
  imports the original. Over 200 random full-field vectors Rust `ntt` matched
  the original with 0 mismatches, and 20,000 full-field round trips passed
  (review 5643283114).
- **Carrier decoding.** `rime_sphere_carrier.py --decode` validates by a
  different technique from Rust: one strict whole-document regex grammar,
  where Rust re-renders and compares. It inverts with the original `intt`.
  CI runs it on every Rust-written carrier and on all adversarial fixtures.
- **The original's own controls.** `--compare-original` checks the original
  script's printed C3 table and C4 random line against the bridge's counts.

**Shared by construction, so not independent evidence:**
- p, N = 27, and the "smallest primitive root" rule that fixes w. Both
  halves would agree on a wrong choice; `bank()`'s order check
  (w²⁷ = 1, w⁹ ≠ 1) mitigates this.
- Block partitioning, the "first k" C3 address and the C4 random vector,
  all copied from the original's conventions.
- The carrier specification. Byte-identical carriers prove the two encoders
  agree with each other, not that the format is right.
- Authorship. One author (Claude) wrote both decoders and both encoders.
  Independent verification still requires a reviewer who wrote neither.
- Labels and C5 exist only in Rust.

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

### Evidence categories

The measure line carries five categories, verbatim:
`theorem=… | tested=… | integrity=… | provenance=NOT_AUTHENTICATED | observed=…`.

**Theorems — hold for every input by mathematics:**

| | why it must hold |
|---|---|
| C1 identity | 27 divides p−1 = 1,000,080, so a primitive 27th root w exists, and 27 is invertible mod p; the NTT is a bijection on Z/p²⁷ |
| C3 at k = 27 | is C1 |
| C4 wrong root, byte 0 always survives | inverse index 0 is N⁻¹·ΣXₖ, which contains no power of the root |
| C5 label rows = 1 when any full blocks exist; 0 otherwise | `bt(k)` depends only on position k; files shorter than 27 bytes have no complete block and therefore no label rows |
| C5 labels-only bound, **given no side information** | a deterministic decoder whose *only* input is the label row must emit one fixed block, so it is exact on at most the most-repeated block's count. The condition matters: a decoder that also knows the block index can reconstruct the default input `(i*7)%251` from position alone, with no coefficients |

**Tested software properties — shown by tests and fixtures, not by proof:**

| | evidence |
|---|---|
| C2 carrier round trip | depends on the serializer and parser, not on mathematics; unit tests plus every CI round trip in both decoders |
| canonical encoding | `render(parse(t)) == t` (Rust) and a full-match grammar (Python); fixtures for `+`, leading zeros, uppercase hex, CRLF, unknown and duplicate fields, row order, split tail, trailing data |
| bank validation | p, g and w must equal the supported bank exactly, and every coefficient must be < p; fixtures for altered g, p and w, and for c+p under an inflated p |
| malformed carriers fail closed | 19 fixtures run as bounded subprocesses (`ulimit -v` 2 GiB, `timeout` 30 s) through both decoders: exit exactly 1 with `FAIL\|reason=`, never a panic (101), abort (134) or silent accept |

`result=PASS` gates on the theorems plus C2.

**Integrity versus provenance:**

- **Integrity (what the SHA-256 receipts give):** modification is detected
  *relative to trusted input bytes or a trusted `carrier_sha` / anchor
  obtained out of band*. `verify` regenerates everything from input bytes
  the verifier must already hold.
- **Provenance: not authenticated.** Receipts are unsigned, and the chain is
  one record with `prev = 0…0`. Anyone with the public tool can produce a
  fully self-consistent evidence directory for any file. The tamper tests
  show modification detection, not who produced the evidence. Origin
  attestation would need a signing layer (for example the pending ed25519
  signatures), not more hashing.

**Observations — measured on this input, reported, never required:**

| | measured | why it is not universal |
|---|---|---|
| C3 fails for k < 27 | 0 bytes, 0 blocks | a constant block has X = (27c, 0, …, 0) and recovers from one coefficient; tested in `c3_fraction_failure_is_observed_not_universal`, and the bridge still PASSes on it |
| C4 random address | 0 / 2,700 | chance matches are possible on other inputs |
| C4 wrong root, bytes other than 0 | 0 here | on `README.md`: 1,006 / 12,285 = the 455 guaranteed byte-zeros + 551 coincidental matches. Decode still fails closed on the bank check |
| C5 labels-only maximum | 2 / 500 blocks | equals this input's most-repeated block; an input of one repeated block would give its full count |

### Review 5643283114 repairs

Evidence first: commit `60db99e` adds the fixtures and regression tests and
records them failing (14 of 19 regressions, including rc=134 and rc=101).
The fixes follow, and each commit message records the runner output at
that point (14 → 8 → 0).

### Kept in CI

- all Rust tests (64 existing + 11 bridge), Clippy `-D warnings`, release build, on Rust 1.81.0
- original source blobs checked; original script run unmodified, with its C1 line **and** its C3/C4 output compared to the bridge
- cross-language `cmp` of carrier and cross-check line; the Python decoder decodes every Rust carrier
- adversarial fixtures regenerated from the original NTT with no diff allowed, then run against both decoders
- bit-exact replay, and receipt + carrier modification detection (integrity only, see above)
- real-file round trip: `README.md` through the bridge and back, `cmp` exact in both decoders
- boundary cases: empty and tail-only (<27 bytes) inputs round-trip byte-exact in both decoders

## Cost, stated

Each coefficient lives in Z/1000081 and needs 20 bits; a 27-byte block (216
bits) is carried in 540 bits — `carry_ratio=5/2`. The information-theoretic
floor for a uniform element of Z/1000081 is 27·log₂(1000081) ≈ 538.2 bits, so
the 20-bit packing wastes under 0.4%. **No compression is claimed**
(`compression_claimed=0`). **Important:** `carry_ratio=5/2` refers only to hypothetical packed 20-bit coefficient storage, *not* the actual serialized `carrier.rime` file size. The current carrier stores coefficients as newline-delimited decimal strings with header and hashing metadata, and is materially larger. The `serialized_carrier_bytes` measure reports that actual size; compare it directly to the source file's byte length. Small inputs can have very high overhead. The alternative, carrying only a reference to a
verified source bank, is cheaper to transmit but recovers nothing when the
bank is absent — the original C4 "missing bank" control.

## Scope

This stage is a verified transport and receipt layer around the original sphere
transform. It makes no claim about Yang–Mills, the mass gap, or physical
mechanism, and does not change any Stage 2G–2I result.
