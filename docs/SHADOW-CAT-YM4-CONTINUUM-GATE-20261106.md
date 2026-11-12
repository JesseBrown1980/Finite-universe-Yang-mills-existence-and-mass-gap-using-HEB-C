# Shadow Cats: finite S3 gauge-sector bridge to four-dimensional continuum work

**Status 2026-11-06:** navigation and precise theorem boundary. This document does **not** modify any existing 3×4 certificate, spectrum, first-gap verdict or formal HOLD. The actual exact tests and immutable predictions are in the companion [YM4 PR #34](https://github.com/JesseBrown1980/yang-mills-4-dimensional-continum-proof/pull/34). Source tests and receipts are committed in that draft branch.

## The user's Shadow Cat residual and the exact test

The intended residual is the retained **Shadow Cat** in the threefold C0/C1/C2 cyclic torus bookkeeping, **not** the numerical error between two continuum approximations. A finite test representation is `r=(C0+C1+C2) mod 3`; `r=2` admits unsigned `2/3` and balanced `-1/3` representations of the same modular class. The 27→9→3→1 block map `B_3(x)_j=sum(x_3j,x_(3j+1),x_(3j+2)) mod 3` preserves global residue `r` exactly. Periodic 27-site permutation jumps computed by repeated cubing were checked at k=0..16, including `3^16=43,046,721`. Three cyclic C0/C1/C2 rotations preserve r.

**Evidence:** [hosted PASS 42330239449](https://github.com/JesseBrown1980/yang-mills-4-dimensional-continum-proof/actions/runs/42330239449); `tests/SHADOW_CAT_RESIDUAL_RECEIPT.txt` and `tests/test_shadow_cat_residual.py` in YM4 PR #34. Nine registered Shadow Cat predictions were frozen BEFORE source code at `11fecb81`. This is an **integer ternary identity**, not an experimental signal.

## Gauge invariance of a concrete S3 candidate

The simplest attempt to interpret the signed Shadow Cat as a closed-loop `Z3` orientation chooses the normal subgroup `A3={1,a,a²}` of `S3`. However, the transposition `t` obeys `tat^-1=a^-1`. A gauge transformation therefore changes a raw orientation `r=1` into `r=2`. The **signed residue is not a gauge-invariant Wilson-loop observable in this candidate identification**.

The standard S3 character is invariant under this conjugation, but reads `χ_std(a)=χ_std(a²)=-1` and thus **loses the sign distinction**. A genuinely gauge-invariant Shadow Cat carrying extra information would need a different, specifically constructed, relational/Wilson-network observable. That construction is OPEN.

**Evidence:** 9 predictions frozen BEFORE source at `be28b595`; [hosted PASS 42330519118](https://github.com/JesseBrown1980/yang-mills-4-dimensional-continum-proof/actions/runs/42330519118) checked 1,296 two-link configurations and endpoint gauge transformations plus four falsifiers, with `tests/SHADOW_CAT_S3_GAUGE_RECEIPT.txt` and `tests/test_shadow_cat_s3_gauge.py`. The tests prove the conjugacy fact for this **candidate**, not that the full user Shadow Cat model has been physically defined in S3 or SU(2).

## Where the actual finite Yang-Mills certificate enters

This repository's 3×4 `H=J_E E+J_B M` S3 Hamiltonian has the recorded **E9−E8≥24.039673 J_E at r=9** 3×4 spectral separation. That remains exactly its own statement. The first excitation above the vacuum is `E2−E1` (for one-based rank labels when the vacuum is unique). A certified **E9−E8** cannot automatically serve as a first physical mass-gap bound.

The companion [YM4 triadic physical-gap test](https://github.com/JesseBrown1980/yang-mills-4-dimensional-continum-proof/pull/34) supplies two exact rational finite transfer families. Both admit positive finite-lattice gaps and valid power-of-three jumps, but only one has a gap bounded below in physical units as lattice spacing shrinks. A separate toy observable residual remains nonzero even while a lower **dark** excitation's physical gap tends to zero. Thus an exactly conserved Shadow Cat residue, a visible correlation residual, and a **strictly positive physical first mass gap** must remain three distinct mathematical predicates.

## Next finite-to-continuum gate (OPEN)

1. Construct an explicit **gauge-invariant** Shadow Cat candidate on this repository's 1,393-state 2×2 S3 physical basis, rather than only a mod-three label or bare holonomy orientation. Verify its matrix elements and commute/covariance properties under every local gauge transformation.
2. Test connected Euclidean two-point correlations, spectral overlaps and the true **lowest physical excitation**. Keep separate any E9/E8 cluster-separation certificate and any accidental zero overlap.
3. Construct a corresponding **continuous SU(2)** operator and quantitative three-scale blocking identities with controlled errors along the coupling trajectory `β(a)`. Establish the infinite family of lattice-spacing-uniform bounds needed for physical masses, plus continuum quantum field theory construction for the Clay target.

Neither fixed-volume S3 spectra, 3^16 permutation jumps, nor the nanoparticle toy interferometer solve these open steps. The official four-dimensional Yang–Mills existence and mass-gap theorem remains OPEN, as recorded in [YM4/PROBLEM.md](https://github.com/JesseBrown1980/yang-mills-4-dimensional-continum-proof/blob/main/PROBLEM.md).

**Code-policy:** this document adds no floating-point code or changes to the existing proof gates. Its scope is cross-repository evidence and a precise falsification boundary.
