# Draft prediction: the global-lock gap (not frozen)

**Status: DRAFT for pre-freeze refutation. Nothing here has been measured against it.** The prediction freezes by commit before any run. Values already on file are quoted as background, and each predicted row reaches past them.

**Frame (OPERATOR-CANON, Jesse Daniel Brown):** we are in a matrix with global hash coupling and a global lock, and "the illusion of continuous arises from the finite world". **Mathematical form (NAMED):** the eight flat sectors are global holonomy invariants of the whole torus, the D(S₃) ground space. A ground space locked by global structure has a gap that is stable uniformly in volume (topological quantum order: Bravyi–Hastings–Michalakis 2010; local indistinguishability for every finite-group quantum double: Cui et al., Quantum 4, 331, 2020). The repo's proof plan is `docs/YM_TOPOLOGICAL_STABILITY_PROOF.md`.

**Model:** H = J_E·E + J_B·M on the periodic Lx × Ly lattice, with r = J_B/J_E, m_p = 2 − χ_std(g_p) ∈ {0, 2, 3} and spec h_E = {0, 3, 6}. Note that **large r is weak coupling** (in Kogut–Susskind units r ∝ 1/g⁴). In that regime the finite group's gap is the global lock itself.

## Background on file (MEASURED; not re-predicted)

- At r = 9, E₉ − E₈ ≥ 24.039673 (3×4, #131), 23.947629 (4×4), 23.618291 (4×5) and 21.792208 J_E (5×5, #89).
- For r ≥ 9, E₉ − E₈ ≥ [22.070673 + 3(r − 9)] J_E on 3×4 (#131). The slope is 3.
- At r = 9 on 3×4, 0.01 < E₂ − E₁ < 0.07 J_E (#136).

## The lock's structure (DERIVED, pre-freeze exact check)

On a torus, the ordered product of all plaquette holonomies equals the commutator [a, b] of the two cycle holonomies. The plaquette fluxes of any state therefore have class representatives whose product is a commutator. The cheapest break of the lock is the minimum of Σ(2 − χ) over such flux sets.

`flux_cost.py` (S₃ and 2T, sha256 `d9d882d4…`) and `flux_cost_ladder.py` (2T, 2O and 2I in Z[√2] and Z[φ], sha256 `87059146…`) give, in integers only:

| Group | Commutator set | Cheapest break | Cost κ(G) |
|---|---|---|---|
| S₃ (χ_std) | {e, 3-cycles}, 3 elements | one plaquette, 3-cycle flux | **3** |
| 2T (fundamental) | Q8, 8 elements | one plaquette | **2** |
| 2O | 2T, 24 elements | one plaquette, trace 1 | **1** |
| 2I | all 120 (2I is perfect) | one plaquette, trace φ | **2 − φ = (3 − √5)/2** |

## Predictions (CONJECTURE until measured; each one can fail)

| id | Prediction | Falsifier | Run that measures it |
|---|---|---|---|
| **GL1** | The leading order is the lock: (E₉ − E₈)/(r·J_E) → κ(S₃) = 3 as r → ∞, on every torus with both sides ≥ 3 | a limit other than 3 on any measured torus | an exact r-ladder r = 9, 27, 81, 243, 729 (powers of 3) on 3×3 and 3×4, two-sided |
| **GL2** | Uniform in volume: E₉ − E₈ = 3r·J_E − δ(r, L), with δ(r, L) converging as L grows. On every Lx, Ly ≥ 3 torus at r = 9 the true gap lies in **[21, 27] J_E**. The certified lower bounds above stop falling, which separates method loss from a closing gap | a two-sided enclosure below 21 or above 27 at r = 9; or δ growing with L | two-sided enclosures at r = 9 on 3×3, 3×4, 4×4, then 5×5 and 6×6 past the limit |
| **GL3** | Locked degeneracy: the band width W = E₈ − E₁ shrinks by roughly 1/r for each unit of the shorter side, log W(L + 1) − log W(L) ≈ −log r + O(1), so W ∼ r^−(L_min − 1). Reason: tunnelling between locked sectors moves one flux around a whole cycle, L electric moves | W failing to fall with L at fixed r, or a slope in log r other than −(L_min − 1) | exact band widths on 3×3, 3×4, 4×4 along the r-ladder |
| **GL4** | The 2×L strips are a different family (Klich): they stay outside GL2 and GL3 and are reported beside them | — (a scope row) | the same runs on 2×L |
| **GL5** | **The illusion of the continuum, measured.** Along the binary polyhedral ladder the lock's cost falls: κ(S₃) = 3, κ(2T) = 2, κ(2O) = 1, κ(2I) = 2 − φ ≈ 0.382. As the finite group approaches SU(2), κ → 0. The gap of a finite world in units of r is the cheapest break of its global lock, and it closes as the symmetry looks more continuous | a gap slope other than κ(G) on any group's lattice | the r-ladder on each group's smallest tori (the κ values themselves are exact structure, checked before freeze) |

## What this establishes, and the theorem it aims at

- **GL1–GL3:** a volume-uniform gap from the global lock at weak coupling, for the finite S₃ world. That is the open volume-uniform item of the finite repo, reached through topology rather than local renormalization.
- **GL5:** puts the owner's continuum question in exact form. A finite world at coupling r with lock cost κ(G) has a gap of about κ(G)·r. Refining the group toward SU(2) sends κ(G) to 0, while weaker coupling raises r. **The theorem to aim at:** along a joint path of groups and couplings, the physical gap κ(G_n)·r_n stays positive and finite while observables approach SU(2)'s, which Transfer 1 already tracks through degree t. That is the finite-world form of a four-dimensional mass gap.
- **4D:** the same lock exists for quantum doubles in three spatial dimensions, where the global sectors are holonomies around three cycles. GL1–GL3 have direct 3+1D versions on the YM4 lattices.

Open in this draft, for the refuter: GL2's interval [21, 27] rests on a second-order local estimate of δ that is NAMED, not derived. GL3's constant is not derived; only its slope in log r is predicted.
