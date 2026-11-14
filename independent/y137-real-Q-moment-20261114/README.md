# Issue #137 — real accepted-K3 full-Q moments and corrected Schur source

**Finite periodic 3×4 S₃, r=9.** Draft PR #193. Actual first-excitation
summed-Wilson spectral weight: **HOLD**.

## Actual 8×8 moment matrices (accepted-K3 source)

The accepted 20-Jacobi-step K3 trial has an eight-column integer
residual R supported on the 155,378 inner nonflat K3 orbits plus all
1,985,218 shell-4 orbits. Its accepted residual Gram convention is

    G0 = 6 R* W R,              mu0 = G0/6.

For either original frozen energy, with b=10^9 and z_num=b*z,

    X = b (QHQ-z I_Q) = b QHQ - z_num I_Q,
    R = X Y - b QHP,            mu_k = R* W X^k R.

All symbols above use the **integer source convention**, including the
accepted eight-by-eight U0 matrix, and W denotes the original
orbit-size metric. U0 already incorporates its own energy scaling.
In particular, the *accepted* Schur bracket is exactly

    U0 - mu0/g <= S(z) <= U0,   g=94068200000-z_num.

The moment correction therefore **never receives another factor
b=10^9** when combined with U0.

The hosted eight-shard [complete calculation](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43594920941)
passed, exhausting 1,985,218 shell-4 rows, 72 moves each, or
142,935,696 raw moves. All shell-5 exits were counted and original
inner+outer G0 was recovered entry by entry. Both real weighted
`mu0` and `mu1` matrices at the original E1/E2 energies are archived:
`RESULT-MU0.hbp`, `RESULT-MU1.hbp`, with the complete original
eight-shard evidence in `RESULT-MU1-SHARD-EVIDENCE.hbp`.

The second-seat [review #6877824258](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/193#issuecomment-6877824258)
independently verified both moment matrices using characteristic
polynomials and exact spectral localizers. The reviewer did not rerun
the eight raw-move shards, so independent transition-source review
remains pending.

## HIGH normalization error: preserved and rejected

The previous `RESULT-N1.hbp` incorrectly used an extra b=10^9 on
all moment corrections. Its archived Schur upper bound was **negative
definite at both samples**, in contradiction with the accepted lower
Schur bracket (one/two negative eigenvalues). It has been retained
without changes as `RESULT-N1-REJECTED-1E9.hbp` for audit and
regression testing. **Its upper/lower matrices must never be used
in E1/E2 isolation or Wilson-weight calculations.**

The new `replay_n1.py` reconstructs all source matrices from eight
pinned shard receipts and applies the correct accepted convention:

    g = 94068200000-z_num,
    h = 468000000000-z_num,
    s = g+h,       d = h-g.

For n=1 the exact Chebyshev polynomial is P1(X)=s-2X.
The actual corrected trial, *with R defined in source units above*, is

    Y1 = Y - (2/s) R,
    R1 = (I - 2X/s) R,

so the corrected Schur centre and full-Q sandwich are

    U1 = U0 - (4/s²)(s mu0 - mu1),
    U1 - [d²/(g s²)] mu0 <= S(z) <= U1.

The upper and lower improvement matrices relative to the accepted
bracket are

    D_upper = (4/s²)(s mu0-mu1) >= 0,
    D_lower = (4/s²)(mu1-g mu0) >= 0.

They are checked as exact PSD matrices, **and** the corrected interval
is checked to lie inside the original accepted interval:

    U1 <= U0,
    U1 >= U0-mu0/g,
    corrected lower >= U0-mu0/g.

To guard the normalization, an independent fraction-free
leading-principal-minor inertia test requires

| Matrix | E1 negative count | E2 negative count |
|---|---:|---:|
| Accepted upper U0 | 1 | 2 |
| Accepted lower U0-mu0/g | 1 | 2 |
| Corrected U1 | 1 | 2 |
| Corrected lower | 1 | 2 |

An explicit negative control recreates the invalid extra-b upper
bound and **requires its nested-bracket and inertia gates to fail**.
Pure integer-pair rational LDL checks PSD separately; no floating
point or Python `fractions` is used.

The active corrected `RESULT-N1.hbp` holds the full new exact
numerator/denominator matrices, their SHA-256 receipts, inertia
counts, and old-billion-factor negative-control verdicts. The
dedicated hosted workflow requires byte-identical replay of it.

The squared residual-norm contraction at degree 1 is exactly
`d²/s²` (about 0.784), narrowing the original bracket width to
roughly 78.4% at both energies. This modest improvement is distinct
from any claim to have completed degree 7.

## Mandatory degree-7 source-unit rule

The [full-Q Chebyshev algebra of draft #191](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/191)
must use this same accepted integer residual convention before
consuming K3 moments. Let P_n(X) be the exact Chebyshev polynomial
and K_n=P_n(0), with

    F_(n-1)(X)=(K_n-P_n(X))/X,
    C_(2n-1)(X)=(K_n²-P_n(X)²)/X = sum c_k X^k.

In these accepted source units the exact trial and centre are

    Y_n = Y - F_(n-1)(X) R/K_n,
    U_n = U0 - (1/K_n²) sum_(k=0)^(2n-1) c_k mu_k.

**No extra b prefactor.** The previous expression with
`b/K_n²` applies only when moments and U are expressed with a
different physical (unscaled) residual convention, which must
never be mixed with the accepted K3 source files.

## Outstanding proof obligations

1. Independent second-seat audit of the actual complete 72-move
   shell-4 transition source. The current checksum and spectral
   tests establish internal consistency but cannot alone exclude
   a shared operator-construction fault.
2. Actual accepted-K3 moments `mu2..mu13` at both frozen energies.
   Degree 7 requires fourteen complete W-weighted 8×8 matrices
   per sample, including shell5 and each further frontier.
3. Recompute fully normalized E1/E2 state directions and actual
   unshifted summed-Wilson first-excitation spectral weight.

Issue #137 remains OPEN; the true first weight remains **HOLD**.
The separate degree-7 raw-move pilot #192 uses a different Y=0
residual source and cannot substitute for accepted K3 moments.
