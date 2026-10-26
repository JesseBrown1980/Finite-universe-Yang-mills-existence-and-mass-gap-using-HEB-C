# Stage 2G — Conservative rational E0 / E1 / excitation-gap certificates for the periodic S3 torus

**Scope:** the *already built* 1,393-dimensional, eight-link, four-face finite S3 gauge-invariant Hamiltonian in native/src/torus2.rs. Rust 1.81, safe standard library, integer-only arithmetic, no JSON or floats. This stage does not introduce another Hamiltonian.

**Independent issue:** [Issue #2](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/issues/2) remains open for *tight* independent low-energy enclosures. This stage establishes conservative, mathematically proven intervals with a reproducible integer witness.

## What is certified

For H=JE HE + JB HB on the 1,393-element orbit-value basis, the inner product is

    <f,g>_w = sum_i w_i f_i g_i,

with exact positive Gauss orbit weights w_i in {1,2,3,6}. The real HE satisfies w_i HE_ij = w_j HE_ji, its off-diagonal entries are nonpositive, and its graph is connected. The electric-only physical gap is exactly 6, as established in the preceding Stage 2C report using the product of S3 transposition Laplacians and the Gauss constraint.

**Rational enclosures (denominator 1,000,000; all four bounds inclusive):**

| (JE,JB) | E0 | E1 | E1−E0 |
|---|---|---|---|
| (1,1) | [7.634198,7.634199] | [8.305233,13.528686] | **[0.671034,5.894488]** |
| (3,5) | [36.699227,36.699228] | [37.043817,53.523267] | **[0.344589,16.824040]** |

These are conservative **true eigenvalue bounds**, not estimates obtained by labeling a floating-point Lanczos or Ritz result rigorous. In particular, the lower bounds prove a quantitative, strictly positive finite-volume gap at both couplings. The E1 intervals are fairly broad; no claim is made that they are tight, or that the finite S3 result solves 4D Yang–Mills.

## Exact mathematical proof

### Positive witness and the ground energy

Choose any strictly positive vector v. The algorithm constructs one using 256 rounds of purely integer normalized iteration on the entrywise nonnegative matrix

    M = (1+max_i H_ii) I − H.

Each component is rounded to the nearest positive integer with a maximum fixed scale of 10^12; no floating-point convergence assumption enters the proof. In fact *any* positive v with the checks below passing is a valid witness.

Set

    ell = min_i (H v)_i/v_i,
    u   = max_i (H v)_i/v_i.

By the Collatz–Wielandt comparison for an irreducible stoquastic weighted-self-adjoint matrix,

    ell <= E0 <= u.

The verifier recomputes H from source and performs the inequalities using exact i128 arithmetic, rounding ell downward and u upward to denominator 1,000,000.

### First excitation lower bound

Write each f_i=v_i*g_i. For the exact electric generator HE with zero row sum, the *identity*

    <f,H f>_w
      = sum_i w_i v_i^2 * ((H v)_i/v_i) * g_i^2
      + JE/2 sum_{i,j} w_i*(-HE_ij)*v_i*v_j*(g_i−g_j)^2

holds with no approximation. The diagonal contribution is at least ell times the squared norm.

The Laplacian in the second term is symmetric in the measure m_i=w_i*v_i^2. Its edge conductances are bounded below by vmin^2 times the pure-electric edge conductances, while weighted variances in m are bounded above by vmax^2 times those in w. The already proven electric Poincare inequality therefore yields a first nonzero transformed Laplacian eigenvalue of at least

    delta = 6*JE*(vmin/vmax)^2.

By the min–max principle,

    E1 >= ell + delta,
    E1−E0 >= delta − (u−ell).

The program floors delta and uses the outward-rounded ell/u values. A nonpositive final certified lower gap causes a hard failure.

### First excitation upper bound

The native spanning-tree representative has x0=y0=identity, x2=q[0] and y1=q[2]. Form an integer second trial vector

    z_i = v_i * (chi_standard(q_i[0]) − chi_standard(q_i[2])).

The algorithm **recomputes and checks both equalities exactly**:

    <v,z>_w = 0
    <v,H z>_w = 0.

The 2D Ritz compression of H to span(v,z) is therefore diagonal. The verified Rayleigh upper bound for v is below the Rayleigh quotient of z, so Courant–Fischer gives

    E1 <= <z,H z>_w / <z,z>_w.

This ratio is rounded **upward** with integer division. Consequently the certified gap upper bound is E1_upper − E0_lower.

The use of this specific trial vector gives a reliable upper bound, but does *not* prove that z is an exact excited eigenstate.

## Software replay and provenance

The native command builds the actual torus operator, constructs and checks its positive integer trial vector and Wilson difference, and writes:

- run.hbp — source-committed denominator, exact E0/E1/gap bounds, parameters, witness SHA and the original torus anchor SHA
- index.hbi — exact byte offsets, row digest and chained HASH
- run.anchor — SHA-256 commitments to the evidence bytes
- run.measure — plain text with rigorous=1, tight=0 and source hashes

The verifier does not trust a stored measurement: it reconstructs the Hamiltonian and *recomputes both integer witnesses and all receipts*, rejecting altered bytes. The anchor must be externally pinned for independent authorship/time provenance; SHA hashes alone do not prove independent physical measurements.

Reproduction (from native/):

    cargo +1.81.0 test --all-targets --offline --locked
    cargo +1.81.0 clippy --all-targets --offline --locked -- -D warnings
    cargo +1.81.0 build --release --offline --locked
    target/release/hebc torus2-bounds 1 1 bound-1-1
    target/release/hebc torus2-bounds-verify 1 1 bound-1-1
    target/release/hebc torus2-bounds 3 5 bound-3-5
    target/release/hebc torus2-bounds-verify 3 5 bound-3-5

Compare each receipt byte-for-byte across repeated runs. Corrupt a recorded HBP or HBI byte and verify that the replay fails.

## Remaining Issue #2 requirements

The current certified lower gap bounds, although positive, are much smaller than the actual spectral gaps appear to be. A tighter fully audited interval for E1 requires an additional independently verified method (for example exact inertia/Sturm counting in the weighted sparse basis, or a validated interval factorization), plus independent low-energy residual checks. The present coarse Poincare certificate is a *first rigorous quantitative stage*, not the final requested tight eigensolver.

The model is a finite, two-dimensional S3 lattice gauge theory with a finite Hilbert space. There is no established continuum or infinite-volume lower bound, no compact-simple-Lie-group continuum construction, and no Clay Millennium Prize theorem here.
