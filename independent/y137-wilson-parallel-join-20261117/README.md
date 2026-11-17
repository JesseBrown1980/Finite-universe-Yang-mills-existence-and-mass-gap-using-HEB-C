# Issue #137 — exact independent join of the two parallel Wilson certificates

Research draft, 2026-11-17. This lane combines two separately source-computed original 3×4 S₃ Wilson results without re-running either physical Q graph:

- **Observable lane, hosted PR #276**: two original, immutable, fixed W-flat directions, with their exact full-Q Feshbach tails at *every certified Stage E physical energy*, have strictly positive original seven-loop Wilson squared normalized source weight **>1,027,970 parts per billion**. The source result includes complete shell4 residuals, two source-specific duals, original unshifted Wilson O, energy-window drift, and exact original B†B=72I. The exact hosted receipt and provenance are frozen in `INPUT-DUAL-TRUE-WINDOW.hbp`.
- **Eigendirection lane, hosted PR #277**: original Stage E four-moment full-state transfer errors imply source-conditional W-flat true-state sines **≤0.003429010525** and **≤0.009197961975**, replacing PR #184's 0.108258863901 / 0.253465115951. They use the correct geometric mean of the normalized full-flat projection masses and original full-Q spectral floor.
- **Mixed term:** Original seven-loop O is a weighted-physical coordinate multiplication operator and eight-flat P selects coordinate supports; therefore exact POQ=QOP=0. The remaining 8×8 effective M is the accepted original source signed full-Q QOQ matrix. Hosted #273 has exact rational interval bounds on all 64 entries. Deflated action norms of `Mhat v1` and `Mhat* v2` are computed with correct W-flat reciprocals and inflated by the full matrix error Frobenius norm.

## Source-specific sufficient test

For the exact physical flat-direction normalized eigenstates `x1`, `x2`, write `xi=ci*vi+hi` with signed phase choice, `||hi||<=si`, `ci>=sqrt(1-si²)`. For true-energy effective matrix `M(E2,E1)`, let `a` be the independently source-certified lower original normalized FULL fixed-sample amplitude from PR #276. Since the full states have norms at least as large as their flat components, `a` is also a **conservative lower bound on the flat-normalized fixed-direction amplitude**. Then

    |<x2,M x1>| >= c1*c2*a
       -s1*||(I-Pv1) M* v2||
       -s2*||(I-Pv2) M v1||
       -s1*s2*||M||.

The two deflated action norms are bounded by the exact 64-entry source central matrix plus an independently certified all-entry interval Frobenius inflation. `||M||` has the accepted original full-Q bound `14*(1+72/(gamma-E2_hi)*(gamma-E1_hi))`. The verifier computes each squared/source/sine quantity with strict integer numerator and outward square root, rejects missing or forged sources, and returns signed margin with source provenance. If margin is positive, the mathematical implication for the true original first Wilson matrix element is sound **conditional on acceptance of all original Stage E and true-energy source certificates**, subject to independent proof review. The code never labels a candidate a completed spectral-weight theorem.

This is the **first exact arithmetic join of the independent true-energy original O dual and the true E1/E2 flat Schur projector estimates**, not a rerun of a toy test. If the margin is nonpositive, it quantitatively identifies the remaining source-specific uncertainty: the deflated signed action bounds or the true flat-sine estimates. The finite physical first excitation gap remains source-conditionally certified. Physical first Wilson weight HOLD until accepted strict positive margin. 4D continuum theorem OPEN.

Hosted source run: `.github/workflows/y137-original-wilson-parallel-join.yml`.
