# Issue #137 — Worker 1 B4 whole-Q5 weighted electric reverse check

**Dependencies:** draft PR #198's immutable Stage B prediction at `fe7bbd3`; independently accepted B1/B2 source-identity gate (#208); full 18,598,040-row/1,339,058,880-move B3 census (#209), [hosted 43836790446](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43836790446).

**Frozen B4 prediction:** `weighted_reverse_edge_mismatches=0`. Here `W=6×w` and `w` is the stored orbit weight in `{1,2,3,6}`. The universal factor six cancels from the reciprocity equation `w_i c_ij = w_j c_ji`. Every real on-Q5 directed edge is tested, including edges whose endpoints are in different source groups/buckets.

## Independent implementation: `rust/src/bin/b4_reverse.rs`

1. Read all eight original binary archives from accepted run `43615270310`, SHA-check their bytes against the frozen manifest, then build a global `address -> orbit weight` lookup of 18,598,040 unique addresses. The Rust 1.81 enumerator independently reconstructs each source's canonical S3 address, orbit weight, magnetic number, and all **72** electric moves per row.
2. Preserve exact raw multiplicity `c_ij`, while distinguishing source-to-Q5 and outside-Q5 moves. Outside-Q5 transitions are *not* assigned to Q6; their per-group counts and exact FNV digest are reproduced against the frozen B3 result.
3. For `i != j` with both endpoints Q5, form an 18-byte record `[min(i,j):u64, max(i,j):u64, signed(w_i*c_ij):i16]`, with a positive sign for the smaller source and negative for the larger. Each weighted flux is bounded by `6*72=432`.
4. Deterministically partition all on-Q5 records into **256 temporary files**, using a hash of their *unordered* endpoint pair (so both directions land in exactly the same file). Each partition is independently read and sorted by its endpoint pair. For every pair there must be **exactly two records**, one positive and one negative, with zero signed sum. Missing reverse, extra reverse, wrong sign or wrong weighted multiplicity refuses.
5. Assert the original B3 measured `raw_moves=1,339,058,880`, `Q5_raw_moves=125,005,512`, `outside_Q5_raw_moves=1,214,053,368`, `Q5_directed_records=124,955,592`, and zero actual self loops. Each group-specific Q5 move count and exterior FNV must reproduce the independently committed B3 receipt.
6. Use Rust 1.81 strict clippy; four exact negative controls on synthetic balanced/unbalanced pairs; source SHA-256, source executable hash, pinned GitHub SHA, runtime and per-partition hash receipts. Temporary pairs may be reproduced from immutable source files and are excluded from the uploaded compact receipt.

**Expected if B4 prediction holds:** exactly `62,477,796` verified undirected Q5 pairs, all reverse fluxes matching, `weighted_reverse_edge_mismatches=0`. This count follows from the previously measured B3 **124,955,592 per-row distinct directed records**, each supposed to have one reverse, and is independent of the source-weight test itself.

**Scope:** This gate authenticates the transition graph's W-balanced Q5 principal block and prepares the signed `mu3` edge form. No real `mu3` numerical matrix is calculated in this gate. Stage B7 checked 320-bit accumulation, B5 paired/row matrix agreement, B6 16 original Gram hashes and B8 planted signed-source errors remain pending. The real Q4/K3 source signs and mixed terms belong to Stage C; Wilson normalization belongs to Stage D. Issue #137 OPEN, Wilson weight HOLD.
