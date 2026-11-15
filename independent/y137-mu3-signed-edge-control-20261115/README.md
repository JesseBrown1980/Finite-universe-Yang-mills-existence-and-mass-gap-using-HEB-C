# #137 second-seat: signed mu3 edge-form control (frozen before full Q5 run)

This independent exact-integer toy tests the operator identity and the *kind of
source errors that a mu2 regression cannot detect*. It uses no original
Yang-Mills source files, so **real mu3 remains NOT COMPUTED**. First-excitation
Wilson spectral weight remains **HOLD**.

Run:

    python3 -I -B independent/y137-mu3-signed-edge-control-20261115/toy_edge_form.py

## The independent identity

For the actual accepted-K3 source support, take V1=XR in all eight columns,
the exact W orbit weights (the source convention is W_i=6*w_i), and b=10^9.
With the independently enumerated full 72 raw electric moves, write c_ij
for the multiplicity of moves from orbit i to orbit j, including genuine
self loops. Let m_i be the magnetic number and z the original frozen energy
integer. The diagonal of X before removing self moves is

    D_i = b*(72 + 9*m_i) - z.

Then the signed third moment is

    mu3 = sum_i W_i*(D_i-b*c_ii)*v_i*v_i^T
          - b*sum_{i<j} W_i*c_ij*(v_i*v_j^T+v_j*v_i^T)

over all nonzero V1 support states. This equals the original ordered-row
formula only if the entire row census is preserved and

    W_i*c_ij = W_j*c_ji

for every on-support edge pair. Outsupport neighbors contribute zero to
V1 but still count in 72 on the diagonal. Deduplicate canonical orbit
destinations with integer multiplicity before forming either bilinear.
The two formulas are independent integer aggregation paths.

## A specific sign trap when reusing the mu2 replay

The archived `full_mu2_shard.py` explicitly uses a **positive response**
on Q4 because its mu2 factors share a sign. For mu3 the signed Q4 value is

    V1_Q4 = -(D*pf - b*sum_Q4_pf + b*sum_inner_R).

The archived Q5 spool holds unsigned `V1_Q5/b` and its full contribution
requires multiplying the unpacked Q5 vector by b. The K3 signed V1
comes from the inner residual source. Restore these signs and units
**before** calculating any mixed edge product.

A single source-row sign flip preserves all entries of

    mu2 = sum_i W_i*v_i*v_i^T

but changes mu3 whenever the row couples to nonzero neighbors. Thus an
exact whole-Q mu2 replay, though required, is not a sufficient sign or
source-provenance check for the third moment.

## Reproducible planted negative controls

The standalone toy has four orbit states, weights 1,2,3,6; eight signed
source columns; 72 moves per row including nonzero genuine self loops
and off-support moves. All six unordered edge pairs obey W reciprocity.

1. Independent ordered-row and unordered-edge calculations of the
   complete 8x8 mu3 agree entry-by-entry (not just in trace).
2. Flipping one whole source vector keeps mu2 byte-identical but changes
   `mu3[0,0]` by `-844560000000000`.
3. Folding a real 0->1 move into the 0->0 self loop keeps the 72-move
   row count unchanged; W reciprocity detects the corruption.

Frozen toy results: `mu2[0,0]=407754`,
`mu3[0,0]=31666883400000000`, and sign-flipped
`mu3[0,0]=30822323400000000`.

## Required hosted real-source gate (not accomplished by this toy)

- Verify all eight archived Q5 `.v1` artifacts from #195 against their
  exact published SHA-256 receipts, counts, canonical addresses, orbit weights,
  two energy samples, and b=10^9 scaling. Verify corresponding K3 and Q4
  signed frozen sources by *their own* source hashes.
- Enumerate all 72 actual electric moves independently for each of
  18,598,040 Q5 sources using the separately authored S3 move rule.
  Assert original-row agreement, actual self loops, full orbit weight and
  magnetic number, and exact W reciprocity on each on-support pair.
- Join transitions across **all** 64 address buckets / eight groups:
  a group-local quadratic misses cross-group edges. Ensure off-support Q6
  is zero-valued and still counted in the source degree; do not infer
  an edge's destination is off-support merely because it is not in the
  current shard/group.
- Build signed K3/Q4/Q5 V1, globally deduplicated by canonical target.
  Accumulate the full two-sample 8x8 mu3 by both ordered-row and unordered
  paired-edge formulas. Require exact matrix equality.
- Replay the complete whole-Q mu2 **byte-identically** and reject the
  planted sign-flip (mu2-only acceptance is insufficient), folded-self-loop,
  omitted edge, and omitted cross-group edge controls.
- After independent raw source authentication, apply the hardened #198
  mu3 Loewner acceptance window at both frozen z values, with rational
  denominator-inclusive fingerprints and positive-definite inverse blocks.
  Carry real mu3 through the four-moment bounds and the #187 full-state
  normalization formula. Strict required error is below 1/700.

**Prediction before full source:** the exact row-vs-pair matrices will
agree if and only if the restored source/sign convention and complete
edge census are consistent. No predicted Wilson-weight PASS is filed.
The current recorded best full-state error is 0.014153976076.
