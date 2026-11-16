# #137 Worker 1 B5 — exact 8x8 Q5 principal third moment, two archived energies

**Status before full hosted acceptance:** B5 production **PENDING**; B1/B2/B3/B4 PASS, B7 component PASS; whole-Q mu3 and Wilson spectral weight HOLD.

## Immutable inputs

- Frozen PR #198 prediction and hash manifest at `fe7bbd3c611d8977b65b6c69f06cbfcee3e20fcf`.
- Authenticated Q5 V1/b archive from GitHub Actions run `43615270310`, 18,598,040 addresses, 3,140,900,108 bytes, independently validated on PR #208, run `43834357496`.
- Complete independent 72-move Q5 electric census PR #209, hosted `43836790446`.
- Weighted reciprocity PR #210, hosted `43839051643`: 124,955,592 distinct directed Q5 records, 62,477,796 unordered reverse pairs, zero weighted mismatches; 125,005,512 Q5 raw moves (includes multiplicity).
- Checked 320-bit arithmetic PR #211, hosted `43840006670`.
- E1, E2 integer numerators `69909875505` and `69949729820`, denominator `b=1000000000`.

## Independent aggregations in `rust/src/bin/b5_moments.rs`

For each Q5 source orbit i, let q_i denote the eight archived unsigned lanes `V1_i / b`, w_i its exact global-conjugation orbit weight, and m_i the independently recomputed magnetic number. The Q5 principal matrix is:

`mu3_six(Q5) = 6 * sum_i w_i (b q_i) outer ((D_i - b c_ii) b q_i - b^2 sum_{j in Q5,j!=i} c_ij q_j)`

with `D_i = b*(72+9*m_i) - z`. Every move, including those leaving Q5, remains in the 72 of D_i. Exterior source amplitudes are zero *only in this Q5 principal-block calculation*, and the exterior flux is retained from #209/#210 for Stage C.

**Ordered-row form:** independently accumulate `T_i = (D_i-b*c_ii) q_i - b sum_{j!=i,Q5} c_ij q_j`, then all 64 entries `6*w_i*b^2*q_i[a]*T_i[b]`.

**Unordered paired-edge form:** independently form `U_i = sum_{j>i,Q5} w_i*c_ij*q_j`. Accumulate the diagonal `6*w_i*b^2*(D_i-b*c_ii)*q_i outer q_i` and the symmetric upper-edge contribution `-6*b^3*(q_i outer U_i + U_i outer q_i)`. The latter uses weighted flux `w_i*c_ij=w_j*c_ji`, separately certified by B4. Exactly one external factor 6 is applied; `U_i` already contains raw w_i. Store only the 36 upper-triangle pair entries and require equality against **all 64 ordered-row entries**, for **both** samples (128 exact entry equalities).

The two calculations use distinct source contractions (all directed rows versus once-only upper endpoint pairs); they share the independently verified original move rule and source amplitudes. Full row-vs-pair agreement is an aggregation check, not signed-source authentication.

## Integer validity and resources

The B5 contracted terms use the accepted B7 five-limb signed-320 implementation with tighter per-accumulation conditions:
- physical source `a=b*q_i < 2^112`,
- contracted row or pair component `|t| < 2^123`,
- signed complete coefficient `|c| < 2^37`,
- no more than `2^31` terms per matrix cell,
- signed 320-bit overflow refused, every partial sum checked strictly below `2^304` in magnitude.

Consequently `|partial_sum| < 2^(112+123+37+31) = 2^303 < 2^304` conservatively. Source-free controls check packed 82-bit lane boundaries, wide cancellation and rejection of oversized source, contracted term or coefficient.

The implementation builds a globally addressable index for the 18,598,040 records in memory; it does not binary-search concatenated group files. A hosted 10,000-source benchmark precedes the full pass, with `/usr/bin/time -v` memory and elapsed-time data.

### Independent review order

1. Verify Rust 1.81 `cargo clippy --locked --release --bin b5_moments -- -D warnings`, `cargo build --locked`, and source-free toy controls.
2. Verify `Cargo.lock` is tracked and reproducible, repository no-float and compiled no-float checks pass. The previous Python-AST audit invocation against the Rust file was removed after its accidental workflow failure.
3. Verify all eight source SHA-256 records; benchmark memory and time; run both actual 8x8 matrices.
4. Require exact row=pair in 128 entries and the B3/B4 census counts before any B5 PASS.
5. B6 subsequently reproduces all 16 original Q5 Gram fingerprints using `mu2_six=6 V1^T W V1`. B8 provides independent semantic corruptions.
6. Stage C authenticates signed Q4/K3 source cross terms; Stage D evaluates the actual full-state four-moment bound and Wilson-weight error against strict `1/700`.

**Do not promote the B5 Q5-principal result as the actual whole-space third moment or a standalone spectral-weight bound.** Keep issue #137 OPEN and all research PRs in draft pending independent review.
