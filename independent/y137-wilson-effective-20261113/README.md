# Issue #137 — exact Wilson-sum operator and effective Feshbach witness

Status: full-space observable algebra and small exact Schur control only. The actual positive E1-to-E2 spectral weight on the 3×4 finite S3 model at r=9 is still OPEN.

The [prediction](PREDICTION.hbp) was committed before the [replay code](check.py). The old amplitude-bearing files are not imported or changed here.

## Full 24-link observable

Let chi(g) = number of fixed points of the defining three-letter permutation minus one. This is the faithful S3 two-dimensional character, with values -1, 0, 2. The raw diagonal operator is the sum of four horizontal length-3 winding characters, one for each y, and three vertical length-4 winding characters, one for each x. Each closed path transforms by conjugation under arbitrary local gauge transformations; torus translation permutes the paths and shifts basepoints by conjugation. Reflection x -> -x sends oriented horizontal cycles to inverse cycles and leaves chi unchanged. These identities establish exact gauge invariance, zero-momentum translation invariance and reflection-even parity **for every raw configuration**, not only the test fixtures.

The independent Python code reconstructs S3 from all permutations, tests 52 deterministic raw configurations, 3,744 local gauge moves, 624 translations, 52 reflections, all 18 commuting holonomy pairs and their eight simultaneous-conjugacy classes. Negative controls reject a gauge-variant single link and a translation-variant single row. The pointwise exact range is [-7, 14], so the shifted observable O-7/2 has full weighted-Hilbert-space operator norm <=21/2. The shift does not change any transition between orthogonal eigenstates.

## Exact rank-eight Feshbach identity

Conjugate the orbit Hamiltonian by W^(1/2) and write the self-adjoint blocks:

    H = [[ A, B^T ], [ B, D ]]

Here P consists of the eight flat orbits and Q is the nonflat complement. Given the established Q floor gamma=94.0682 J_E and E_i<gamma, let R_i=(D-E_i I)^(-1). For an exact eigenpair let x_i be its P coordinate. Its Q coordinate is y_i=-R_i B x_i, and x_i solves

    [A-E_i I-B^T R_i B]x_i=0.

For an orbit-diagonal Wilson observable, the **exact full-space** unnormalized transition is

    a = x_2^T O_P x_1 + x_2^T B^T R_2 O_Q R_1 B x_1.

Its normalized squared weight is a^2/(N_1 N_2), where N_i=x_i^T x_i + x_i^T B^T R_i^2 B x_i. In raw orbit coordinates these formulas must use W-adjoints. A P-only transition omits a potentially significant Q term.

For rational approximate Q vectors yhat_i at exact fixed (E_i,x_i), define r_i=Bx_i+(D-E_i I)yhat_i and epsilon_i=||r_i||/(gamma-E_i). Then ||y_i-yhat_i||<=epsilon_i. The error in the computed Q cross term is bounded by ||O_Q|| times

    ||yhat_2|| epsilon_1 + ||yhat_1|| epsilon_2 + epsilon_1 epsilon_2.

Use outward rational enclosures on all squared norms. This argument **does not yet bound the eight-flat exact eigenprojector directions or unknown exact energy parameters**. Those enclosures are indispensable for an actual positive spectral-weight certificate.

## Cancellation-sensitive control

The 3×3 integer example in the test has H rows (11,-16,-11), (-16,38,16), (-11,16,11), eigenvalues 0,6,54 and exact eigenvectors (1,0,1), (1,1,-1), (-1,2,1). The two-dimensional P block couples to scalar Q with B=(-11,16), D=11. With O=diag(2,-1,4), the exact P term is +2, the Q term is -4, the full amplitude is -2, and normalized spectral weight is **2/3**. O=I is a dark control with exact zero transition. A corrupted B, an omitted Q term and an underestimated residual error are also rejected.

These are mathematical and implementation checks, not Yang-Mills output values. They are a prerequisite for the next K3 full-space computation.

## Next exact acceptance route

Independently reconstruct O at all K3 orbit states and required exterior; verify W weighting. At E1 and E2 windows, calculate the effective 8×8 Schur matrices and their energy dependence using rational Q solves and residuals bounded by the accepted gamma. Then enclose both true eight-flat eigenprojectors and the exact O-effective transition, with explicit phase-independent error bounds and full normalizations. Freeze the predicted sign before evaluating the transition; an independent matrix builder and planted faults must reproduce or reject it. Keep issue #137 OPEN until the normalized weight is rigorously bounded below by a positive rational number.

Sources: [merged clean K3 PR #177](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/177), [lift-free inertia PR #176](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/176), [archived insufficient trial-error budget](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/issues/137#issuecomment-6860478452).
