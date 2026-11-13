# Issue #137 — clean acceptance record for the K3 reflection-sector isolation

**Status (2026-11-13):** independently reviewed finite-model certificate, subject to the source floor and whole-orbit Hamiltonian assumptions below. The operator has explicitly confirmed completion of their human review; technical acceptance remains tied to the exact head and its CI.

**Scope:** periodic 3×4 finite `S3` lattice, `r=J_B/J_E=9`. This is the historical #155 certificate using the #131 floor `94.070673 J_E`. The accepted *lift-free* replay of its exact U/G matrices uses `94.0682 J_E` and has already merged separately as [PR #176](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/176), with an independent fraction-free 8×8 inertia recount. No new numerical thresholds are introduced here.

## Exact certificate

The **unaltered** source, receipt, and receipt digest have been carried from draft [PR #155](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/155), at head `30a08260d9827d61b37d8fbb4817513f9e487369`:

- `y137_k3_sector_isolation.py` — git blob `63bb9b9e8d3f858d586ff6a8370a38944b18af19`
- `Y137-K3-SECTOR-ISOLATION.hbp` — git blob `f4e08a31e7abc0fe13c044d02952b36bf3b2f6df`
- `Y137-K3-SECTOR-ISOLATION.hbp.sha256` — git blob `81486df4b8904f0124c2f2f59324e6135d64ab74`

The receipt's **SHA-256** is `cf91b9e4d842698d4972ac8df6ff6210bd3f439f561a354bca2954aac36716ef` (distinct from the Git blob SHA). These source and receipt bytes are unchanged; verification against the exact running environment is a CI/replay obligation.

For threshold z, counts are (even lower, even upper, odd lower, odd upper):

| z/J_E | Exact counts |
|---|---|
| 69.9567503 | (2,2,0,0) |
| 69.9686993 | (2,2,0,0) |
| 69.9689591 | (3,2,0,0) |

The old floor `94.070673` was replaced by `94.0682` in #176 and all three count tuples stayed unchanged. The derived conditional bound is `E3 >= 69.9686993 J_E`. Since `E2 < 69.9567503 J_E`, one obtains the sharper **`E3-E2 > 0.0119490 J_E`**. The independently certified even/odd decomposition places both E1 and E2 in the reflection-even sector at the tested thresholds; `E_odd >= 69.9689591 J_E`.

## Counting lemma and sector conditions

For a trial extension `psi(v)=(SCALE*v,-X*v)` of the eight flat coordinates, the exact trial form `U(v)` is evaluated with the weighted inner product. The Q-space residual Gram form `G(v)` includes every Q row in K3 and every shell-4 target. For `z < floor <= lambda_min(QHQ)`, the Feshbach/Haynsworth identity bounds the Schur complement from below using the inverse bound `(QHQ-z)^-1 <= (floor-z)^-1`. The lower witness `L=6*gamma_num*U-PS*G` therefore satisfies, in exact inertia, `n_-(U) <= N(z) <= n_-(L)`; the U min–max upper *existence* count itself is unconditional on the Q floor.

**Per-sector application requires equivariance of the trial extension.** Specifically, with `pi` the Q reflection permutation and `sigma` its action on flats, `Y[pi(i)][sigma(k)]=Y[i][k]` must hold. Starting with `Y=0`, this follows inductively from reflection invariance of the diagonal, Q-Q and Q-P couplings and entrywise Jacobi rounding. The previous independent review measured equivariance at the actual thresholds. This qualification replaces the overly broad phrase “whatever X” for arbitrary non-equivariant extensions in the source docstring; the source bytes have intentionally not been changed.

**Whole-orbit reflection lemma:** x→−x maps each horizontal link to the inverse of its reflected link, maps each vertical link to the corresponding vertical link, and preserves gauge orbits and stabilizers. It sends each plaquette holonomy to a conjugate of its inverse, preserving the real `S3` character. The electric generator's 72 transposition moves are permuted under this map. Thus the whole-space Hamiltonian commutes with the reflection, and the even/odd split is valid beyond the finite trial ball.

**Exterior weighted-balance lemma:** the electric moves are involutions and are gauge-covariant. Pairing each move with its inverse yields `|O| c(O,O') = |O'| c(O',O)`; using gauge-orbit stabilizer weights gives `w_O c(O,O') = w_O' c(O',O)`. The independent review reports a complete back-walk check for all `9,690,600` shell-4 couplings, not just the original stride-199 sample.

## Census and independent review

The K3 trial ball has **155,378 nonflat Q orbits**, or **155,386 including the eight flats**. The off-diagonal Q-Q list contains **1,356,528 ordered entries**. The complete shell-4 exterior contains **1,985,218 targets** and **9,690,600 edges**. These distinguish Q counts from full-ball counts.

The previous cloud-seat [review of #155](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/155#pullrequestreview-5832526757) reports an independent graph census, exact C++/Python U/G/L recount, exhaustive shell-4 back-walk, planted faults and an independent effective-trial check. Its conclusion was `CONFIRMED_WITH_NOTES`; no mathematical blocking finding was reported. Those independent heavy computations are **referenced evidence, not rerun by this clean PR**.

This clean branch **excludes** the old `y137-evidence-20261109/d2-feshbach-r9` amplitude-bearing logs and all `Fraction`/`pickle` historical scripts; they remain reachable only through the original draft #155 history. It also leaves `native/scripts/FLOAT-EVIDENCE.txt` untouched. Thus no new exemption or human-gated evidence-list change is requested.

## Separate open obligation

[Issue #137](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/issues/137) still requires a **positive rational lower bound** on the conventional summed seven-loop Wilson observable's full-space E1→E2 spectral weight. Historical K3 Ritz amplitudes are estimates; their existing residual enclosures are vacuous for proving positivity, as filed in the issue. This acceptance record makes **no positive-weight claim**, no continuum theorem, and no particle-mass claim.
