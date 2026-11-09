# Independent S3 certificate replay — HTTP-0 execution track

**Date:** November 9, 2026 · **Stage:** independent small-torus and 3×4 neighborhood verification · **Next gate:** 45,508,080-row streaming store replay.

## Executed and verified

- **New C++17 implementation:** constructs S3 directly from permutations, computes electric transpositions, magnetic plaquette costs, and canonical spanning-tree gauge representatives.
- **Complete 2×2 lattice:** 1,393 physical orbits, every electric transition and weighted-adjoint pair checked.
- **Complete 2×3 lattice:** 47,449 physical orbits, every electric transition and weighted-adjoint pair checked.
- **3×4 reconstruction:** Burnside orbit count 2,177,317,873; eight flat states; 264 distance-one states; 7,770 distance-two states; 147,344 distinct distance-three exterior targets. Recomputed all 72 moves on 8,042 interior states and checked their weighted-adjoint pairs.
- **Matrix-law controls:** independently verified the 27-ring Pascal/Frobenius identities over integers modulo 3, exact cubing jumps through exponent 3^16, and five freeze/play leaves at 0, 1, 3, 9 and 27.
- **Adversarial controls:** modified orbit weights and a modified frozen leaf are rejected.
- **Clean-runner replay:** the dedicated GitHub Actions workflow recompiles the source, executes the checks, and compares the HBP output byte-for-byte after removing variable elapsed milliseconds.

Primary evidence: `GPT6_HTTP0_INDEPENDENT_POSTEXPLORATION.hbp`.
Primary executables: `gpt6_http0_independent_s3.cpp` and `gpt6_http0_pascal_freeze.py`.

## Next gate: full 3×4 streaming reproduction

The original research store consists of 34 room segments carrying 26,850,881,536 payload bytes, a 728,129,280-byte orbit-key table, and a 364,064,640-byte Perron vector. The independent streaming run will carry out these five checks in sequence:

1. **Source integrity:** fetch the 34 segments, key table, vector and manifests; verify their lengths, hashes and identity.
2. **All-row recomputation:** reconstruct all 45,508,080 symmetry-sector rows from the S3 group rules; check every matrix coefficient, weight and magnetic cost; recalculate the Merkle root.
3. **Exact adjoint test:** check all 1,632,625,631 weighted off-diagonal pairs and complete row/edge census.
4. **Perron certificate:** independently evaluate the exact positive-vector inequalities yielding the 94.070673 J_E nonflat floor and verify the whole-orbit lift.
5. **New hosted certificate:** record source pin, executable hash, per-leaf digests, fault controls, final status, and an externally anchored HBI/HBP/SHA/SH/HASH receipt.

## HTTP-0, triadic scheduling and matrix laws

The existing HTTP-0 certificate addresses remain stable: 81 (Perron), 82 (row reconstruction) and 83 (all-pairs). The independent hosted computation will receive its own receipt chain and published locator.

Triadic checkpointing partitions 45,508,080 rows into **771 leaves** of at most `3^10=59,049` rows. Each leaf records its complete row range, consumed source bytes and exact SHA-256 checksum. Freeze/play uses verified leaves to restart or audit a run.

The Pascal/Frobenius jump identity is proved for commuting operations over characteristic 3. The current jump test verifies that algebraic setting; its application to the Yang–Mills Hamiltonian is a separate mathematical reduction gate.

## Reproduce

The repository workflow `.github/workflows/gpt6-http0-independent-replay.yml` compiles the new C++ checker on Linux, rebuilds the complete small tori and the 3×4 neighborhood, verifies exact HBP output, and tests induced failures. The 45.5-million-row replay has its own following execution stage.

**Current research standing:** completed exact finite reconstruction tests; independent full-store certificate stage scheduled by its prerequisite source availability; the sharp first-gap interval relies on the original Perron certificate pending that replay.
