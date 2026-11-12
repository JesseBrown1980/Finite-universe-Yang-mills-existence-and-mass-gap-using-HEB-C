# Full gauge-orbit r=12 symmetry spectrum: certified matrix and nontrivial variational witness

Date: 2026-11-12. Parent independent basis construction: PR #169. Mathematical counting bridge: PR #168. Coupling **r=12** throughout; `m0=9` means **magnetic-number cutoff**, not coupling 9. The protected coupling-r9 run remains on HOLD.

## Exact enumeration and 15 symmetry representations

The original finite-S₃ Rust 1.81 enumerator is patched *only inside a disposable hosted checkout* so the 48 lattice translations/reflections are **not quotiented out**. The resulting basis contains **111,906 global-conjugation gauge orbits**, grouped into 2,880 D₃×D₄ symmetry orbits. All 15 real irreducible characters are accounted for: trivial dimension 2,880, nontrivial total dimension 109,026.

Those results were independently audited in PR #169; all of its required GitHub checks passed.

## Full core matrix, not merely a projected toy

[Hosted run 43271826090](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43271826090) constructed the **complete gauge-orbit principal matrix** on every magnetic-number M≤9 gauge-orbit state at coupling r=12.

* 111,906 rows, 1,818,336 distinct directed nonzero core transitions.
* Every row accounts for all **72 single-link moves**, including 264 flat-sector transitions and 6,216,840 outgoing moves to the excluded magnetic tail.
* All 1,818,336 directed reciprocal core entries independently pass `W_a T_ab=W_b T_ba` in both Rust and a separately written Python binary parser.
* The canonical binary file is 10,658,383 bytes, SHA-256 `74c0d38850790c2fff38a6680bf36d3701aeb63b998bd4d7be778539ddd82aec`; original source key SHA-256 `3cfd4f0ac9d7866e3b8a6f54d35153a50011dc2ee23feb7952f194b12cc45eb7`.

The precise matrix is `H_CC(a,b)=δ_ab(72+12M_a)-T_ab` on the full gauge-orbit basis, without symmetrizing away the nontrivial lattice representations. The binary is kept as a GitHub Actions artifact and is **not** committed as a large binary into the source repository.

**Limitation:** H_CC is a principal restriction. A lower bound for the spectrum of H_CC alone is not a full-space lower bound; omitted tail states can lower eigenvalues. The exact gap still needs a full-sector Schur lower comparison or another all-space inequality.

## First exact nontrivial representation test: M=3 alone

[Hosted run 43271139256](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43271139256) applied all 15 D₃×D₄ character projectors to the 36 gauge-orbit states with M=3. There are 33 nontrivial dimensions. **No moves stay within M=3**; all projected M=3-only trial vectors have exact Rayleigh quotient **108**.

This is a control, not a proof of absence of lower states: coupling to M=4,7 and other magnetic layers changes the spectrum.

## Exact nontrivial Krylov variational witness

[Hosted run 43273780653](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43273780653) reproduces a separate, postexploration, exact-integer Krylov result using the full verified core matrix. This was not an unobserved prediction.

The two starting gauge-orbit keys `2613485090` and `2628605549` have equal conjugacy orbit weight 6 and belong to the **same lattice-symmetry class `2613485090`**. A separate Rust group-action census verified both memberships in [run 43272369709](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43272369709).

Consequently the vector `v=δ_a−δ_b` is orthogonal to the 48-group-invariant subspace. The magnetic cutoff and exact move operator commute with lattice translations/reflections, so `(180−H_CC)^k v` stays in the sum of **nontrivial** symmetry sectors. Its zero extension is also in those sectors of the full non-flat Hamiltonian.

Define the exact moments and 26×26 quadratic form by

```
B = 180I − H_CC
mu[k] = <v, B^k v>_W
Q_t[i,j] = (180*d − n)*mu[i+j] − d*mu[i+j+1]     t=n/d
i,j = 0,...,25.
```

The Gram matrix `mu[i+j]` is **strictly positive definite**, verified by its exact Bareiss leading-principal-minor signs. For each threshold every Bareiss division is independently required to be an exact integer division. Signed inertia of the quadratic form counts the number of negative directions in this 26-dimensional trial subspace.

| Threshold t | Negative directions in exact nontrivial Krylov trial space |
| --- | ---: |
| 104.55 | 0 |
| 104.70 | 0 |
| 105.50 | **2** |
| 110.00 | **4** |

**Rigorous variational implication, for the specified finite non-flat Hamiltonian:** at least **two eigenvalues belonging to nontrivial symmetry sectors lie strictly below 105.5**. The 26-dimensional Krylov test does *not* prove that no eigenvalues lie below 104.55 or 104.70 in the much larger omitted trial directions. The negative directions are upper-bound/existence evidence only, not lower spectral enclosures.

If the previously reported three invariant-sector Ritz upper enclosures (all below 105.5) are accepted, the *complete non-flat spectrum* must have at least **five** eigenvalues below 105.5, even though the **fourth invariant-sector level** has certified lower bound 110. Thus the observed invariant-sector cluster followed by a gap to 110 **cannot** be interpreted as the complete non-flat spectrum's fourth-level gap.

This does **not** disprove a positive *first* mass gap of the finite model, and does **not** establish a first gap, lattice-size-uniform gap, weak-coupling bound, or 4D continuum Yang–Mills theorem.

## Next proof obligation

Build symmetry-resolved **lower** comparisons, beginning with the nontrivial sector that produced the Krylov witness: invertible positive tail blocks, exact group projection of all core rows and weighted coupling, rational outward-rounded Schur bounds, and integer inertia. Only then can we separate the first full-space eigenvalues with certified lower and upper enclosures.

The protected r=9 floor launch is still **HOLD**. None of these runs used coupling r=9.
