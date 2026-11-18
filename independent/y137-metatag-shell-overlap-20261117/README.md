# Issue #137 — gauge-invariant metatag residual-cloud overlap (finite S3 pilot)

**Date:** November 17, 2026. **Status:** exact arithmetic structural test PASS, new original-model spectral bound SOURCE-CONDITIONAL, original first-excitation Wilson weight HOLD, continuum 4D OPEN. This is an independent research draft, not a modification or acceptance of the prior whole-space spectrum.

## Original physical Hamiltonian

Original periodic 3×4 lattice, S3 link group, 24 oriented positive links, 12 plaquettes, electric generator of 72 left-transposition moves, magnetic ratio r=9. The original gauge-invariant physical Hilbert space has 2,177,317,873 orbits and eight flat sectors. Original source-conditional signed four-moment (Stage E; see issue #137, draft PR #234) whole-space energy bands give

- E1/JE in (69.909429421, 69.909586556)
- E2/JE in (69.949264147, 69.949433884)
- therefore the original first physical excitation gap Δ/JE > 0.039677591 (strict).

The original full-Q Perron source condition is QHQ >= 94.070673 JE (conservative 94.0682 used in several downstream source calculations); the original store and its claimed full-orbit lift are NOT recomputed here. The original signed Wilson seven-loop observable is the sum of four horizontal length-3 plus three vertical length-4 S3-character winding terms.

## New **proposed** shell-overlap rule

The physically meaningful local inputs are the original S3 gauge-invariant plaquette excitations m_p(U) = 2 − chi(U_p), which belong to {0,2,3}. Use a spatial nearest-plaquette-pair graph (12 plaquettes, 24 x/y positive-direction pairs, periodic) and define

    W(U) = [sum_{<p,q>} min(m_p(U),m_q(U))]/72
    H_alpha = H_original + alpha*JE*diag[W(U)]

This is a **hypothetical new interaction**, not part of the previously accepted Hamiltonian. It is a minimal, finite, nonlinear density-overlap model inspired by the user's residual-shell/metatagging concept; it is not a unique or established physical law.

The model is explicitly gauge and translation invariant (plaquette holonomy is conjugated by gauge transformations, chi is a class function, and the 24 pair set permutes under lattice translations). Every term is between 0 and 3, so 0<=W<=1 *globally on all physical orbits*; no large-state enumeration is needed to prove that. On all magnetic-flat states every m_p=0, so W=0. Therefore the new operator V is a diagonal nonnegative multiplication operator, 0<=V<=alpha*JE*I, PVP=PVQ=QVP=0 for the original eight-flat coordinate projector P, and Q(H+V)Q>=QHQ. Thus the source-conditional full-Q compression floor and flat-to-Q coupling B=QHP remain valid at this structural level.

**Exact min-max perturbation certificate:** for all n, E_n(H)<=E_n(H+V)<=E_n(H)+alpha*JE. Consequently

    Δ_new > (0.039677591 - alpha)*JE.

For a general extra self-adjoint interaction (e.g. an exchange coupling, not necessarily positive), with ||V||<=alpha*JE, only Δ_new >(0.039677591 - 2alpha)*JE follows by this argument.

| alpha/JE | diagonal V>=0: strict new gap lower in JE | arbitrary signed ||V||<=alpha: strict new gap lower in JE |
|---|---:|---:|
| 1/64 | 0.024052591 PASS | 0.008427591 PASS |
| 1/32 | 0.008427591 PASS | -0.022822409 (bound exhausted) |
| 1/16 | -0.022822409 (bound exhausted) | -0.085322409 (bound exhausted) |

Negative results here mean the **old certificate no longer proves positivity by this inequality**, not that an actual spectral gap closes. For this diagonal V, the original connected offdiagonal transition graph persists, so a Perron–Frobenius uniqueness argument still gives an abstract strict positive finite gap even when the quantitative perturbation budget is exhausted.

The original exact first/second physical energy windows shift upward by at most alpha, *not* necessarily in lockstep; the original Wilson multiplication operator is unchanged, and POQ=QOP=0 still holds in the coordinate P/Q split. The full-Q resolvent, true eigenvectors, source-action duals, and original first-excitation Wilson spectral weight of H_alpha require a new calculation if alpha != 0. No positive original or modified Wilson first-weight claim is made.

## Exact two-cell quantum coupling control (separate toy)

For an illustrative two-cell exchange Hamiltonian J w sigma_x in the one-excitation subspace, choose the exact Cayley unitary with t=1/2. Acting on |10> gives

    |psi> = (3/5)|10> - i(4/5)|01>.

Norm squared 9/25+16/25=1, concurrence 2*(3/5)*(4/5)=24/25. Zero overlap gives the identity and zero entanglement. This is a **toy assumed extra interaction**, not a consequence of the S3 plaquette multiplication term. It neither establishes physical electron tunneling nor produces a Wilson first-excitation certificate.

## Hash integrity and scope

The pilot constructs a spanning-tree gauge fixing to the original 13 independent post-tree S3 links, quotients residual global conjugation by minimizing over six group elements, and computes SHA256 on the canonical orbit key. Gauge-transforming raw link bytes changes the raw hash but **preserves the physical canonical-orbit hash**. A physically changed link can change the canonical-orbit hash. SHA is an identity/integrity check, not a nonlocal quantum interaction law.

256 exact fixtures, 1536 local gauge transformations, 768 translations, the flat-zero test, positive random overlaps, Wilson symmetry checks, hash negative controls, and exact two-cell normalized amplitudes run with integer-only Python and SHA256. There are no floating-point values, Division/Decimal/Fraction or GPU dependencies. Run:

    python3 -I -B independent/y137-metatag-shell-overlap-20261117/pilot.py

CI additionally runs strict integer and repository no-float gates and checks frozen key receipt lines. `RESULT.hbp` is the output of the local exact executable. The hosted job recomputes its own `RESULT.hbp` and both SHA256 receipts; no snapshots are substituted for computation.

## Literature scope

The user supplied [*Equation of State for Finite-Density Black Holes: Addressing the Singularity Problem with a Discrete Spacetime Framework (v2-unity)*](https://www.researchgate.net/publication/387666716_Equation_of_State_for_Finite-Density_Black_Holes_Addressing_the_Singularity_Problem_with_a_Discrete_Spacetime_Framework_v2-unity) as conceptual guidance. The exact linked publication returned an access/rate-limit error when inspected on Nov 17, 2026. **No equation or numerical claim is attributed to this unread source**. Only the broader, explicitly stated bounded-density hypothesis is used here. This is a 2D *spatial* finite lattice gauge experiment; it does not model a black-hole core, pressure equation of state, or Einstein dynamics. A genuine spherical 3D finite-cell extension and stress/pressure balance would be a separate experiment.

## Scientific interpretation and next gate

1. PASS: one source-compatible gauge-invariant residual-overlap potential exists with exact finite spectral robustness budget and preservation of accepted Q-floor structure.
2. PASS (toy): a separate coherent two-cell exchange rule exhibits exact entanglement for nonzero overlap.
3. HOLD: whether residual-shell data improve the original first-excitation Wilson spectral weight or narrow the full-Q source-action uncertainty in draft PR #287.
4. HOLD: whether a coupling constructed from physical residual shells reproduces measured tunneling, confinement or finite-density black-hole physics.
5. Retain original Yang–Mills source pins, do not merge this proposed interaction into the original Hamiltonian or rename the old gap certificate as a theorem about changed physics without explicit perturbation assumptions.