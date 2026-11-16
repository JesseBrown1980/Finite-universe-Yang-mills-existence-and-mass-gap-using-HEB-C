# Accepted-K3 degree-11 μ3 bridge: persist true V1 on shell 5

The real [whole-Q μ2 run 43606393196](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43606393196) **PASS** exhaustively traversed all 1,985,218 original shell4 sources (142,935,696 electric moves), reduced 125,426,880 Q4-to-shell5 source events by target, and certified the exact 8x8 mu0/mu1/mu2 for both frozen energies using 16x16 block-Hankel and spectral-localizer controls.

This child branch reuses **those exact immutable source artifacts**, avoiding another full 142.9-million-move expansion. For each of 64 target-key buckets, it downloads and verifies all eight original shard-specific event manifests and combines all source contributions before taking a weighted outer product. It then emits a compact sorted binary spool of true original shell-5 V1=XR amplitudes for both energies; to keep the original verified unsigned packed-source convention, the spool stores **V1/b**, with the exact multiplier b=10^9 specified in its receipt.

A per-target record is \`<Q B H H>\` plus two variable-length unsigned packed eight-column values: 64-bit canonical target address, 8-bit orbit-size W, and two 16-bit byte lengths for the frozen E1/E2 V1/b vectors. The overall file has SHA-256 and exact byte/target counts. Group boundaries correspond to key mod 8; each group stores eight of the 64 radix buckets in canonical order. The original real Q5 mu2 8x8 Gram **must** be reproduced entry by entry for both samples from the newly written V1 spool; otherwise the output REFUSES. Every source artifact has a byte hash verified against its historical manifest.

**First hosted stage:** exact synthetic negative controls then just group 0 (one eighth of Q5 target-address buckets). Only after that passes should all eight groups be replayed. The metadata must say \`real_mu3=NOT_COMPUTED\` until all Q3/Q4/Q5 V1 values, every on-support raw edge and all matching weighted mixed-sign products are certified.

## Terminal odd-moment law

An independent [review of Matrix Laws PR #14](https://github.com/JesseBrown1980/The-matrix-law-essentials/pull/14#issuecomment-6879238689) confirmed that the final odd moment needs the quadratic form over its current support, saving the largest last outward operator pass. For degree 11:

    V_j = X^j R,  j=0,...,10.
    mu_(2j) = V_j*W V_j,
    mu_(2j+1) = V_j*W X V_j.

**Ten complete outward passes** yield V0..V10, and mu21 is computed from verified on-support edges without building V11. The real mu3 will use the newly archived V1 on K3+Q4+Q5, the same idea at j=1. The full Q5 source must enumerate every 72-move row and check actual self loops from the independent S3 generator. **A complete mu2 Gram alone has no information about the individual V1 target values**, so this replay spool is essential.

## Signed-packing caution

The shell5 V1/b sum in this first transition is nonnegative, so unsigned packing is valid under the original width bound. The full K3/Q4 V1 contains signed entries, and V2 onward generally does too. Higher Krylov states require **separate signed positive/negative lanes** or another independently verified bounded signed integer representation. Do not apply the original nonnegative packed-lane fast path indiscriminately.

Source review, mu3..mu21, degree11 corrected Schur and the fully normalized first-excitation Wilson spectral weight remain HOLD. This branch is a data-replay bridge rather than a new Yang–Mills theorem.
