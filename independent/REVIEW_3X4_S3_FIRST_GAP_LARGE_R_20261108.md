# Independent proof audit of the 3×4 strong-magnetic first gap (2026-11-08)

**Scope:** the complete periodic spatial 3×4 finite S₃ Hamiltonian, not a continuum SU(2) Yang–Mills theory. This review is a new reimplementation by GPT-6, not a different human/model seat; the alternative computation is independently coded from group multiplication rather than copied matrix rows. Original PR #132 remains available as the historical post-exploration record.

## Rebuilt exact facts

The alternative verifier constructs a **horizontal-first** spanning tree (the original has a vertical-first tree), fixes all 24 link variables down to 13 free variables modulo root conjugacy, and uses independent permutation-group multiplication to construct every flat class and its complete 72-move electric first shell. It recovers 18 raw commuting pairs, eight gauge-flat orbits, 264 distinct one-step neighbors, first-shell magnetic cost 4, and all weighted reverse edges. It obtains, *without reading the precomputed matrix*, `4C0=72I8` and `16C1` with the exact nonzero entries `(0,1)=72,(1,0)=24,(1,2)=48,(2,1)=72,(3,4)=24,(4,3)=24`. Its **integer Newton power-trace identity** yields the characteristic polynomial of `16C1`:

    z^8 - 5760 z^6 + 2985984 z^4
      = z^4(z²−72²)(z²−24²).

Thus C1 has precisely ±9/2, ±3/2 and four zeros, matching #132's rational eigenvectors independently. The top two eigenvalues are simple and separated by 3.

## Analytic complete-space estimate

The electric operator E=72I−A is nonnegative and every electric link generator is a unitary involution, so `||A||≤72`. The product of S₃ sign characters of all oriented plaquettes on a periodic torus is +1; a single transposition plaquette (cost 2) is impossible, and every 3-cycle costs 3. Hence `M_Q≥3I` on the **entire** nonflat space, with no Perron-store premise.

For the first eight full eigenvalues λ≤72, with D=rM_Q, δ=72−λ, `R=(D−A_Q+δI)^−1`, and B=PAQ, min–max and the Schur identity give `δ≤72/(3r−72)` for r>24. In the weighted physical Hilbert space `||B||²=72`, and `B D^−1 B*=18/r I`; the exact next coefficient is `C1/r²`. The two resolvent identities bound the full residual by

    eta(r)=5184/(3r−72)^3+373248/[(3r)^2(3r−72)].

This controls *all* nonflat states (not only the first shell). Uniform Weyl bounds for the strictly monotone eight Schur eigenvalue branches imply

    3/r²−2eta(r) ≤ (E2−E1)/J_E ≤ 3/r²+2eta(r).

The alternative checker combines the denominators into one integer fraction, checks positivity at r=10000 and exact outward rounding at r=100000. Since both positive terms in `r² eta(r)` decrease for r>24, the strict lower bound extends to every r≥10000. At r=100000, the outward enclosing integer endpoints are `271961/10^15` and `328039/10^15`.

**Review disposition:** mathematical and independent-implementation PASS for this strong-r finite-S₃ claim, conditional on hosted final-head CI for the copied original source and new alternative-tree checker. This proof does **not** use the original 3×4 Perron store, does not bound the first gap at r=9, does not determine winding overlap, and does not prove a mass gap uniform in lattice size, volume or continuum limit. Any protected merge must use fresh checks against main, not stale branch checks from original #132.
