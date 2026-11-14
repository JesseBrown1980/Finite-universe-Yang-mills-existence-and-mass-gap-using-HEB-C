# Issue #137 — real accepted-K3 complete-Q moments and first corrected Schur certificate

**Finite periodic 3×4 S₃, r=9.** Original Wilson first-excitation spectral
weight **HOLD**. Draft PR #193. The source-conditional full-Q spectral
floor is 94.0682 J_E at the original two frozen energy samples.

## Actual moment data

The accepted 20-Jacobi-step K3 trial's full residual R is supported
on 155,378 nonflat K3 inner orbits plus exactly 1,985,218 shell4
orbits. The original exact 8×8 Gram from #190 is G=6 R*W R.
\`moment0.py\` pins that historical artifact, checks its exact U/G SHA,
rebuilds magnetic Gram pieces, proves PSD and derives
\`mu0=G/6\` for each frozen sample.

The first **new** accepted-K3 moment is
\`mu1 = R*W X R\`, where \`X=b(QHQ-zI)\`, \`b=10^9\`.
The complete eight-shard [hosted calculation](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43594920941)
**PASS** traversed all 1,985,218 shell4 source rows, each with
exactly 72 electric moves (**142,935,696 raw moves**). Every
shell5 exit was classified, and all K3 reverse edges were verified.
It recomputed the complete inner+outer source Gram entry by entry,
checked exact W symmetry, and certified all 255 principal minors
of the lower and upper global spectral localizers for both samples.

All eight source receipts are sealed in
\`RESULT-MU1-SHARD-EVIDENCE.hbp\`, and both exact 8×8 full-Q
\`mu1\` matrices are in \`RESULT-MU1.hbp\`.

## A real corrected Schur centre from only two moments

The separate \`replay_n1.py\` performs independent graph-free assembly
from those archived shards, verifies all source SHA pins and real W
normalization, and uses an exact **integer-pair rational LDL** proof,
independent from the original Bareiss determinant method.
Its [first successful hosted run](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43598177160)
passed including strict integer/no-float audits.

For either sample, write

    g = 94068200000-z_num,
    h = 468000000000-z_num,
    s = g+h,  d = h-g.

The accepted source-conditional full-Q bound is
\`g I <= X <= h I\`. The exact degree-1 Chebyshev corrected trial is

    Y1 = Y - (2b/s) R,

with complete residual \`R1 = (I - 2X/s)R\`. Both its centre and
its improved two-sided Schur bracket can be calculated exactly from
\`mu0\` and \`mu1\`:

    U1 = U - (4b/s²)(s mu0 - mu1),

    U1 - (b/g)(d/s)² mu0 <= S(z) <= U1.

Relative to the older bounds \`U-(b/g)mu0 <= S(z) <= U\`,
the **upper** improvement is the PSD matrix

    Delta_upper = (4b/s²)(s mu0 - mu1) >= 0,

and the **lower** improvement is the PSD matrix

    Delta_lower = (4b/s²)(mu1 - g mu0) >= 0.

Both improvement matrices have strictly positive traces in both
original samples. \`RESULT-N1.hbp\` archives exact rational
numerator matrices, denominators and SHA-256 values of the corrected
full 8×8 upper and lower Schur bounds. Its dedicated workflow
requires exact byte-for-byte recomputation.

This **degree-1** result is a real corrected source with rigorous
whole-Q residual control, and avoids a further graph traversal once
mu0/mu1 have been computed.

## Holds and next gates

1. Independent second-seat raw-transition source audit for shell4
   adjacency and K3 reverse links; all source calculations currently
   use the original canonicalization code, so self-consistent
   truncation/source faults must be tested independently.
2. Complete-Q moments \`mu2..mu13\` for the accepted K3 residual.
   Degree-7 centre requires 14 exact 8×8 matrices **per energy sample**,
   complete Q projection at each pass, and no missing shell5 onward.
3. Recompute certified E1/E2 directions and fully normalized Wilson
   transition spectral weight from the improved real Schur source.
   Issue #137 remains **OPEN**, actual Wilson first weight **HOLD**.

Separate degree-7 real-source pilot #192 runs on the simpler
\`Y=0\` source; it does not substitute for the accepted K3 trial.
Keep the two source identities separate and retain all historical
source pins and original verified results.
