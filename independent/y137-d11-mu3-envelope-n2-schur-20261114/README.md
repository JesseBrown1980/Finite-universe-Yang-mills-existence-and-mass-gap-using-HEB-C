# Accepted-K3 degree-2 Schur enclosure from exact μ0, μ1, μ2

**Source-conditional full-Q 3×4 S₃, r=9.** This is an
intermediate certificate toward the **degree-11 target**, not a
replacement for computing μ3..μ21 or the normalized Wilson weight.

The [real μ2 hosted certificate](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43606393196)
passed all eight source-shard and target groups, recovering exact
μ0, μ1, μ2 at both original frozen energies. The complete
shell5 V1 target values were [independently replayed](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43614463352)
and are preserved in downloadable source-addressed artifacts.

## Polynomial source bounds on the *unknown* μ3

Let X=b(QHQ−zI), with b=10^9, accepted source trial R and
\(\mu_k=R^*W X^kR\). The accepted spectral interval is
\(gI\preceq X\preceq hI\), where

    g=94068200000-z_num, h=468000000000-z_num.

Because both of the scalar polynomials

    (x-g)(x-h)^2 >= 0,
    (h-x)(x-g)^2 >= 0

hold for every \(x\in[g,h]\), spectral calculus implies the
exact **8×8 Loewner** envelope

    L3 <= mu3 <= H3,

where

    L3=(2h+g)mu2-(h²+2gh)mu1+g h² mu0,
    H3=(h+2g)mu2-(g²+2gh)mu1+g² h mu0.

Their width is **exactly**

    H3-L3=(h-g) [(g+h)mu1-mu2-gh mu0] >= 0.

These inequalities use the actual complete-Q moments without
claiming that μ3 has been computed. They only require the original
global spectral enclosure; strict all-minor PSD and moment SHA gates
are part of the hosted calculation.

## Degree-2 Chebyshev corrected source from bounded μ3

Set

    s=g+h, d=h-g,
    P2(X)=2(s-2X)^2-d²=K2-8s X+8X²,
    K2=2s²-d²,
    C3(X)=(K2²-P2(X)²)/X
         =16 K2 s -(64s²+16 K2)X+128s X²-64X³.

The corrected Schur center in the historical accepted integer-source
convention is

    U2=U0-[16 K2 s mu0 -(64s²+16 K2)mu1
           +128s mu2 -64mu3] / K2².

**No extra factor b is applied to source moments.** The exact
full-Q residual contraction has squared factor d^4/K2².
Since the unknown center increases with μ3 in Loewner order,
replace μ3 by L3 and H3 to get \`U2lo <= U2 <= U2hi\`.
The true Schur matrix therefore obeys

    U2lo - [d^4/(g K2²)] mu0 <= S(z) <= U2hi.

The hosted verifier proves exact source-unit multiplication,
nesting inside the original accepted bracket \`U0−mu0/g <= S <= U0\`,
negative inertia counts **1 (E1)** and **2 (E2)** at both
new lower/upper bounds, and a planted **extra 10^9** source-normalization
fault that must be rejected. It also tests that this n=2 lower bound
is Loewner-above the accepted n=1 lower bound. The n=2 upper
bound need **not** be Loewner-below the n=1 upper bound, so no claim
is made of full n=2-vs-n=1 bracket nesting.

This is a **computable exact 8×8 intermediate enclosure** from
three already verified moments with only small-integer-matrix
operations. It provides a route to further truncated-moment
polynomial bounds and helps prioritize which full-Q moment
applications are necessary for the final degree-11 certificate.
It does not establish an actual positive first Wilson weight.

## Remaining obligations

- The μ3 *value*, μ4..μ21, and the degree-11 corrected exact
  Schur center remain **HOLD**.
- The full 18,598,040-state Q5 raw electric operator still
  requires an independent completeness certificate; the successful
  128-row Q5 second-generator probe is a sample only.
- The fully normalized interacting-vacuum-to-first-excitation
  Wilson transition must pass its independent source/energy-angle
  and 1/700 positivity budget before the first spectral weight
  may be certified.

Issue #137 OPEN, source certificate draft only.
