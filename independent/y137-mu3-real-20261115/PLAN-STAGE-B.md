# Stage B: pinned production plan, 2026-11-16

Local Codex resumes Claude's work at 42bbf383d45ab208434f519b1987adc2564195b2.
The separate cloud GPT-6 accepted Stage A. Wilson-weight certification remains HOLD.

Before the first full Q5 calculation, commit and push this plan, PREDICTION-STAGE-B.hbp,
and SOURCES-STAGE-B.hbp. The source receipt is copied verbatim from the accepted
RESULT-V1-ALL.hbp; source identity is its SHA256, exact length and target count,
not an artifact filename. Immutable download run: 43615270310, all eight groups.
Frozen energy numerators: 69909875505 and 69949729820; denominator b=1000000000.

1. Verify every downloaded group against the eight frozen fingerprints. Parse every
   record strictly (13-byte header, valid orbit weight, two bounded 82-bit x 8 packed
   vectors). Preserve group and bucket counts and require ascending addresses inside
   each of the 64 buckets. Never binary-search an entire group as if globally sorted.
2. Construct a global canonical-address index; require exactly 18,598,040 distinct
   addresses before accumulating any quadratic term. Check canonical form and orbit
   weight against the independent Rust rule during the complete row pass.
3. Enumerate all 72 moves of each state, totaling 1,339,058,880 raw moves. Compute
   both energies' ordered-row Q5 contribution and the Q5 second-moment regression.
   Account for self loops explicitly. Keep group-to-group move counts.
4. Partition directed Q5 edges on disk by their unordered endpoint pair. Sort each
   partition and require the two independently enumerated directions to exist and
   satisfy W_i*c_ij=W_j*c_ji for every distinct pair. Compute a separate paired-edge
   matrix, including each genuine self loop once. Require exact matrix agreement.
5. Retain off-Q5 source/destination/multiplicity records for Stage C. These are
   unclassified boundary destinations until the independent K3/Q4 source index is
   restored; never label every missing Q5 address as Q6.
6. Use the existing 320-bit arithmetic with checked signed overflow and enforced
   production bounds. Check amplitude lanes, coefficients, row sums and total term
   counts. Test near the declared 2^304 bound and the signed 320-bit boundary with
   Python's exact integers; planted malformed-source and edge faults must fail.
7. Benchmark a representative join-and-accumulate workload before giving a full
   runtime estimate. Record elapsed time, memory/disk requirements, source hashes,
   executable hash and exact toolchain. Emit HBP/HBI/SHA receipts first.

Matrices must name their scale: mu2_six=6*V1^T*W*V1 and
mu3_six=6*V1^T*W*X*V1, with V1=b*(stored Q5 vector) and
X diagonal b*(72+9*m)-z and off-diagonal -b*c_ij.

Signed-source authentication remains a separate Stage C gate. Exact agreement of
row and pair aggregation does not authenticate a shared source sign. The complete
K3/Q4 terms, their cross terms, source-reconstruction controls and Stage D full-state
error test remain required. Stage B claims only a Q5 principal contribution.
