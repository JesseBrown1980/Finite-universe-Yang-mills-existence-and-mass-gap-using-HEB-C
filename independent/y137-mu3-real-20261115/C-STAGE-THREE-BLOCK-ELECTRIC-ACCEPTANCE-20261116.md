# Issue #137 — complete supported cross-block electric graph certificate (2026-11-16)

**Scientific scope:** Exact, finite 3×4 S₃ K3/Q4/Q5 **source-support** electric graph. This is the operator-completeness and weighted-reverse gate needed before assembling the authentic whole-space signed third moment. It does not by itself evaluate the moment or the Wilson spectral weight.

The immutable source is the **20,738,636 distinct canonical states** accepted in #217, #219 and the unified #220, with physical signed V1=X R on K3/Q4 and original Q5 V1/b spools. The original 72-move gauge-fixed 3×4 S₃ generator (24 links × 3 transpositions), frozen canonicality and orbit weights are independently rechecked on each source state.

## Exhaustive source and transition counts

[Hosted run 43873674889](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43873674889) returned all jobs **SUCCESS**, including 256 exact sorted-pair comparisons and reauthentication of all original sources.

| Source | Rows | Actual raw electric moves | To K3 | To Q4 | To Q5 | Outside supported source | True self loops |
|---|---:|---:|---:|---:|---:|---:|---:|
| K3 | 155,378 | 11,187,216 | 1,397,544 | 9,789,408 | 0 | 264 | 0 |
| Q4 | 1,985,218 | 142,935,696 | 9,728,688 | 7,486,632 | 125,720,376 | 0 | 0 |
| Q5 | 18,598,040 | 1,339,058,880 | 0 | 125,467,392 | 125,005,512 | 1,088,585,976 | 0 |
| **Total** | **20,738,636** | **1,493,181,792** | | | | **1,088,586,240** | **0** |

These are **raw move multiplicities**, not distinct neighbor records. In particular, Q4→Q5 and Q5→Q4 raw counts need not agree because canonical S₃ orbit multiplicities differ; what must agree exactly is the *physical weighted flux* w_i c_ij = w_j c_ji on **every individual pair**.

The graph enumerator explicitly retains off-support counts, including the 264 K3-to-outside moves and all Q5-to-outside moves, in the original diagonal degree 72. No exterior destination is relabeled as a supported source without actually appearing in the authenticated global address map.

## Exact weighted-reverse certificate

The complete **Q5↔Q5 principal** graph had already been independently accepted by original Stage B4 with 62,477,796 unordered reciprocal pairs, 124,955,592 directed destination records and 125,005,512 raw Q5-on-Q5 moves.

The new Stage C full graph excludes that one already-pinned principal block and writes every other supported non-self directed transition to **256 deterministic disk partitions** with normalized unordered address pair and signed physical flux. Every partition is sorted and is accepted only if every pair has **exactly two opposite-signed records with identical weighted flux**. Missing, duplicated, unbalanced and wrong-direction records are rejected by exact comparator tests.

- New reciprocal unordered pairs: **139,517,148**
- New directed destination records: **279,034,296**
- New pair weighted positive-flux sum: **837,222,984**
- Exact weighted reverse mismatches: **0**
- Unmatched reverse records: **0**
- Genuine supported self-loop moves: **0**
- All 256 partitions exact-balanced: **PASS**

Combining the independently accepted B4 Q5↔Q5 graph and the Stage C cross-block result gives **201,994,944 supported unordered pairs**, **403,989,888 distinct directed pair records**, and **404,595,552 supported raw moves**. The difference of **605,664** between raw move multiplicity and directed destination count is retained, not dropped. Outside the supported source there are another **1,088,586,240 raw moves**; supported plus exterior recovers exactly **1,493,181,792**.

The complete result is frozen in `RESULT-WORKER1-C-EXACT-CROSS-GRAPH-20261116.hbp`, including all 256 per-part exact pair counts/digests. The 256 binary pair archives are preserved as GitHub artifact **14228504695** (5,022,649,182 bytes), and the receipt archive as artifact **14229282267**. The complete SHA-256 manifest of 256 partition files is archived with manifest SHA-256 **dda57b417ecb0bd0dd51842013981ef483ede7ddc509066786ce861ef277c027**. Original executable SHA-256 **6ae43ce7142cc619aeaf6e9fb0d9850699e99d4950da240723c8e952d1bbcdfa**; original Rust Cargo.lock SHA-256 **31f315c4d110146ba73e813439b2cdb2e8bd4aed2f5e5fd3e719c31826399150**. All source and archived result files are unmodified.

## Next exact matrix gate

At **both** frozen energies, assemble the full `mu3_six=6 V1^T W X V1` 8×8 signed matrices, preserving the original physical factor six exactly once and every diagonal contribution `D_i=b(72+9m_i)-z`. Pair contributions must use the verified weighted flux and correct source signs. Compare 128 entries by independent row-ordered operator application and weighted unordered-pair aggregation; reproduce all prior complete lower moments, B5 Q5 principal μ3 and original B6 Grams.

The independently authenticated full R envelope gives global physical **|V1|<2^112** and conditional **every row/pair absolute partial sum <2^294**. The final moment code must check signed 320-bit overflow and that strict absolute limit in production.

**Scientific disposition:** full source-support graph and weighted reciprocity PASS, whole-Q μ3 NOT_COMPUTED, first-excitation Wilson spectral weight HOLD, issue #137 OPEN, all research PRs DRAFT.
