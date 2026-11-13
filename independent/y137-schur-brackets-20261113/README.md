# Issue #137 — frozen K3 energy-window probes and exact Schur envelope

This is the first source-backed numerical step after the merged [#177](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/177) and [#178](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/178). The prediction and eight exact r=9 energy points were frozen in PREDICTION.hbp at commit 7f018daa, before replay.py was written. The chosen points were informed by old **exploratory** Ritz roots, not presumed to have particular certified outcomes.

The replay uses the previously pinned, independent/finite_s3_3x4_r9_first_gap.py K2 checker and independent/y137_k3_sector_isolation.py via merged y137-liftfree-k3-20261113/k3_common.py. It rebuilds the complete K3 ball of 155,378 nonflat states, all 1,985,218 shell-4 residual targets, and their edges. At each of eight new points (69.90, 69.905, 69.908, 69.909, 69.94, 69.945, 69.948, 69.949) it computes the full integer 8×8 U and G, the lift-free lower L, and all reflection-even/odd inertia counts. It uses the independent Faddeev–LeVerrier/Descartes checker for the same exact matrices and checks all 255 nonempty principal minors of G for positive semidefiniteness.

## Exact interval meaning

In the eight flat coordinate directions, let Wp be diag(w_flat), b=10^7, T=10^12, z=a/b and gnum=b*94068200-a*10^6. The accepted source floor is gamma=94.0682 J_E, so gnum>0.

The original source builds trial vectors with P coordinates T*v and nonflat coordinates from its rounded Jacobi Y. U is exactly b times the quadratic form of (H-z), scaled by T^2 in P; G is six times the squared W-weighted full-space Q residual, including all shell-4 targets. The true Schur form in flat coordinates obeys

    [U - 10^6 G/(6 gnum)] / (b T^2) <= S_W(z) <= U / (b T^2).

Inequalities are in quadratic-form Loewner order, so G must be PSD. Normalize S by Wp^(-1/2), since raw flat coordinate vectors are not Euclidean-normalized. The uncertain, positive-semidefinite width matrix has norm bounded above by its trace,

    ||Delta|| <= (10^6/[6 gnum b T^2]) sum_k G_kk/w_flat[k].

The runner reports this upper trace bound as a **reduced rational fraction** and with an outward-rounded ceiling in parts per billion; no float or square root is needed. The matrix-inertia limits give

    n_negative(U) <= exact N(z) <= n_negative(L).

Reflection-sector counts satisfy the same inequalities. The pointwise lower and upper counts need not be monotone when their *trial vectors change with z*. The program therefore applies a valid monotonically inferred closure: N(z_i) is at least the greatest pointwise minimum at any earlier threshold and at most the least pointwise maximum at any later threshold. Only points whose count collapses to a singleton yield sharper energy bounds.

Starting intervals are taken **only from the already accepted mainline results**: 69.89 < E1 < 69.92, 69.93 < E2 < 69.9567503, E3 >=69.9686993, all conditional on the source floor. The old K3 Ritz-root estimates in superseded #155 are used for choosing a candidate grid and are not silently promoted into certified bounds.

## Actual first hosted readout (filed after the prediction)

The initial corrected-head calculation completed [GitHub run 43485090193](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43485090193), and its exact 19 reported rows were copied verbatim to [RESULT-K3-SCHUR-BRACKETS.hbp](RESULT-K3-SCHUR-BRACKETS.hbp) **after the run**. The later CI gate compares each freshly rerun row byte for byte to this receipt. The first attempted job failed before constructing the graph because the freeze parser searched for both grid fields as a single contiguous string; the next commit corrected the parser without altering the frozen grid.

| z/J_E | Certified full-H count range N(z) | Even / odd |
| --- | --- | --- |
| 69.900 | [0,0] | 0 / 0 |
| 69.905 | [0,0] | 0 / 0 |
| 69.908 | [0,0] | 0 / 0 |
| 69.909 | [0,1] | ambiguous even / 0 odd |
| 69.940 | [1,1] | 1 / 0 |
| 69.945 | [1,1] | 1 / 0 |
| 69.948 | [1,1] | 1 / 0 |
| 69.949 | [1,2] | ambiguous even / 0 odd |

Six points give exact counts; two honestly remain intervals. Every new Gram matrix passed all 255 PSD principal-minor tests and the independent characteristic-polynomial inertia check. The lift-free floor weakens the old-floor lower matrix monotonically.

By the min–max/inertia count at 69.908 and 69.948, together with the accepted mainline endpoints,

    69.908 < E1/J_E < 69.92
    69.948 < E2/J_E < 69.9567503
     0.028 < (E2-E1)/J_E < 0.0487503

These are finite-model source-conditional intervals, not just estimates of K3 Ritz levels. They improve the first gap's certified lower bound from 0.01 to **0.028 J_E**, with the original E3 lower bound unchanged.

The W-normalized Schur error **trace norm bound** from the new exact Gram at z=69.948 is at most 9,358,936 parts per billion, i.e. 0.009358936 J_E (upward rounded). This is a sound but broad bound, and it explains why the small-matrix projector computation should use anisotropic/direction-sensitive error information and a dual residual for the Wilson amplitude rather than treating that trace as an exact shift.

## What this proves and what remains

Upon hosted replay, this PR can produce genuine new **full-space finite-model eigenvalue interval information** and a source-certified numerical error width on the small Schur pencil. It does not yet compute an eight-flat null vector, the energy-dependent effective observable O_eff, its complete Q-tail transition, or the normalized full-space Wilson weight. Therefore positive Wilson-sum first-excitation weight remains OPEN on issue #137.

The following proof lane is a certified 8×8 Schur null-projector at E1/E2, using the inherited effective-gap >0.01 J_E and tightened source-certified rational brackets. Then combine independent W-correct Wilson orbit values, Q-resolvent residuals and an explicit error propagation for the complete transition. Acceptance requires a positive **rational** lower bound, not an exploratory K3 amplitude.

## Run

    python3 -I -B independent/y137-schur-brackets-20261113/replay.py

Hosted runtime includes the K3 reconstruction and all eight integer Jacobi probes. CI keeps the runner output as an artifact; no historical receipt is modified. Source hashes and the prediction blob are pinned.
