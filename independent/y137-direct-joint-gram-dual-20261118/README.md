# Issue #137 — original first Wilson weight: direct same-Q Gram-shifted dual residual

Research draft, November 18, 2026. Follows the authenticated full-Q common-geometry study [PR #308](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/308). Target is the original **first-excitation seven-loop Wilson spectral weight**, while maintaining the original periodic 3×4 S3 Hamiltonian, physical 8-flat weighting, and all source-conditional true E1/E2 energy brackets.

## Why this changes the calculation

The earlier source matrix boxes for the centered integer Wilson O2=2O−7I and the original unshifted O independently contain Q inverse/truncation errors. Constructing M_O2-c G21 from separate independent radii loses covariance, even though G21=I+B-sharp R2 R1 B shares precisely the same two Q resolvents as the full-Q Wilson effective operator.

For **true orthogonal** first and second eigenstates, the original Wilson amplitude satisfies
  <psi2,O psi1> = <psi2,(O-8I)psi1>
               = (1/2)<psi2,(2O-16I)psi1>.
Here c=9 relative to O2, because (2O−7I)−9I=2O−16I; at the effective 8-flat level the physical identity dressing is the exact two-energy Gram G21.

The previous nominal source Grammian minimizer cstar≈8.878892572, so c=9 is a small-rational candidate. Its shifted Q multiplication has **exact** original range [−30,+12] and operator cap 30.

## New real source-specific dual

This script is a mechanically scoped extension of the authentic original full-Q signed dual algorithm used by source PR #281, but applies **the single physical observable O9=2O−16I everywhere on P and Q** rather than subtracting separately bounded effective matrices.

It reconstructs the exact original source with all 155,378 K3 Q orbits and 1,985,218 shell-4 exterior residual targets; freezes both physical true-energy upper endpoints E1_hi and E2_hi, the same frozen eight-flat witnesses, original detailed-balance weights, and exact B-star-B=72I.

At fixed flat witnesses, it solves both original-Q directional dual equations for **O9**, independently checks the two full-shell4 residuals, evaluates the signed direct dual center, separately upper-bounds both directional errors and their quadratic cross term, and bounds true-energy drift over the whole accepted E1/E2 windows. The frozen trial-state overlap is **nonzero** and the exact shift formula
  <t2,O9 t1> = 2<t2,O t1>−16<t2,t1>
is asserted directly, so trial-state nonorthogonality is retained rather than hidden.

## Strict interpretation

A positive certified true-energy **fixed-flat** source amplitude for O9 is meaningful but **not yet an E1→E2 eigenstate Wilson certificate**. The true spectral weight additionally needs a jointly certified rotated E1 projector action and E2 projector, with the same Q source. The previous independent E1/E2 angle budgets remain too wide even if nominal O9 action improves. No strict true weight claim arises from source-level positivity alone.

The independent standalone integer verifier checks the signed dual center vs error/drift, original source scope, exact shifted normalized fixed-flat weight formula, explicit nonzero trial overlap, hashes, true-window metadata, six altered-receipt refusals, and fail-closed Wilson HOLD status. The physical Q residuals are built by the original source algorithm; a fully separate Q-graph rebuild remains a future independent review.

## Reproduction

    python3 -I -B independent/y137-direct-joint-gram-dual-20261118/joint_dual.py toy
    python3 -I -B independent/y137-direct-joint-gram-dual-20261118/joint_dual.py real > ALL.hbp
    grep -E '^Y137_(DUAL_WINDOW_TOY|DUAL_WINDOW_SOURCE|DUAL_WINDOW_SIGNED|JOINT_DUAL_AUDIT|JOINT_DUAL_VERDICT)\|' ALL.hbp > RESULT.hbp
    python3 -I -B independent/y137-direct-joint-gram-dual-20261118/verify.py RESULT.hbp

Scientific status remains: source-conditional finite S3 first gap PASS, original E1→E2 Wilson spectral weight HOLD, 4D continuum Yang–Mills OPEN.
