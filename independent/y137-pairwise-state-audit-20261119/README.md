# Original #137 256-partition exhaustive pairwise physical-state audit

This independent **cross-block pairwise-state audit** rechecks the original
20,738,636-state signed third-moment graph's **139,517,148 new unordered**
cross-block pairs represented in the 256 immutable original C-stage binary
partitions. Each pair has two opposing directed weighted-flux records,
totaling **279,034,296 directed records** and **837,222,984 positive
weighted-flux units**. The original production archives are not modified.

The audit source is [pair_audit.rs](pair_audit.rs), compiled with Rust 1.81,
without dependencies, unsafe code, floating-point arithmetic, or imports from
the original Stage C Rust generator.

## Exhaustive identity gate

1. Download the original archive
   [hosted run #43873674889](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43873674889),
   [original 256 binary partitions](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43873674889/artifacts/14228504695),
   alongside its original SHA256 manifest and graph receipts.
2. Verify the whole 256-file manifest against the separately pinned manifest
   SHA256 \`dda57b417ecb0bd0dd51842013981ef483ede7ddc509066786ce861ef277c027\`
   and **all 256 binary SHA256 hashes** before reading any binary pair.
3. Independently parse every 18-byte physical pair state record, enforce
   canonical positive address ordering, nonzero weighted signed flux,
   each of 256 partition hash-routing rules, and exactly **two**
   opposing records per unordered pair.
4. Recompute, from raw binary bytes, the complete per-part exact directed,
   unordered-pair and positive-flux counts and FNV64 digests; compare with
   the separately frozen original graph receipt.
5. Independently generate 16 evenly spaced pair endpoint challenges per
   partition (**4,096 actual pair endpoints sets**, i.e. **8,192 physical
   endpoints examined**). Rebuild all 72 raw electric moves at each endpoint,
   derive the six-permutation S3 gauge orbit and weight, verify magnetic
   number nonflatness, and compare **both** reciprocal multiplicities to the
   archived weighted flux \`w_i c_ij = w_j c_ji\`. The sample is deterministic,
   not an independent proof that every archived pair matches its physical
   72-move graph.
6. Require an exact full summary of **139,517,148 pairs**, **279,034,296
   directed records**, all 256 digests, and all 4,096 selected original
   S3 weighted endpoint challenges. Source-free strict Rust toy rejects
   seven distinct forged pair/partition conditions.

## Complete all-orbit pairwise reciprocity theorem

[Exact root-fixed gauge-orbit reciprocity theorem](ORBIT-RECIPROCITY-THEOREM.md)
proves `w_i*c_ij=w_j*c_ji` for **every** physical 3×4 `S3`
electric pair by counting `6^11*w_i` full-link representatives and
bijectively reversing each labeled involutive transposition move.
It includes the entire `Q5↔Q5` principal graph and
supported-to-flat transitions, independently of the numeric C-stage
cross-block partitions. The original stored Q5-principal graph
can be accepted from this **DERIVED** mathematical identity only
together with faithful complete physical-state/72-move reconstruction;
a second numerical exhaustive Q5-principal stored-pair audit is
a distinct OPEN review option.

## Crucial scientific scope

These 256 partitions represent the **new** original C-stage cross-block
pairs; the **Q5↔Q5 principal** contribution was calculated in the distinct
original B5 production and is **not** contained in these partitions. This
audit deliberately preserves a separate \`Q5_Q5_principal=SEPARATE_FULL_GATE\`
label. Full 20,738,636-state source regeneration and independent exact
third-moment 8×8 Dirichlet calculation also remain open, as recorded in
[Dirichlet draft #325](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/325).

The original finite first Wilson squared-weight lower
\`17,074,763/10^12\` is a SOURCE-CONDITIONAL positive candidate with
**FORMAL HOLD**, not a completed independent mathematical certification.
The four-dimensional continuum Yang–Mills problem remains OPEN.

This draft is a new read-only independent code path. No Hamiltonian, original
source archive, existing Perron store, physical source checker, or no-float
scanner is changed. Inspect hosted workflow
\`.github/workflows/y137-pairwise-state-audit.yml\` before marking
production all-pair acceptance.
