# Issue #137: full-3×4 finite S₃ interacting summed-Wilson-winding first-state test

**Status: PRE-ENGINE PREDICTIONS FROZEN, first-excitation weight OPEN.** The 34-row [prediction](PREDICT-S3-3X4-R9-WILSON-SUM-FIRST-WEIGHT-20261108.hbp) was committed at `b2185df95f44d80a6e526c6c455e5f2e7b22deb8` before writing any new experimental program or generating any new numerical overlap. Its Git blob is `4764015294cbb20975d1576c5923768075ef20b7`. Predictions specify 12 accessible named falsifiers; some require a future full spectral engine. Nobody has measured or certified a positive first-state Wilson-sum weight at `r=9`.

## Precise physical model and observable

Use the **complete** 2,177,317,873-orbit gauge-invariant Hilbert space of the periodic spatial 3×4 finite-`S3` gauge Hamiltonian `H/J_E=E+9M`; do not substitute the old 45,508,080-row symmetry-compressed store or the eight-flat Schur core for the complete Hilbert space. Inner products use the *orbit-weighted* physical metric `W`. The unconditional strictly positive first gap in merged #146 is distinct from the sharper `E1,E2` location in merged #136, which still explicitly relies on #131's pinned whole-nonflat Perron source.

Define the standard two-dimensional `S3` character by `chi(g)=#fixed_points(g)-1`; values `2,0,-1` on identity, transpositions and three-cycles. On each raw configuration sum exactly the four oriented horizontal length-three noncontractible Wilson loops, one for each y-row, and exactly the three vertical length-four loops, one for each x-column:

`O_sum(U)=sum_{y=0}^{3} chi(W_x(y)) + sum_{x=0}^{2} chi(W_y(x))`.

This is an integer-valued *diagonal multiplication operator*, conjugation/gauge invariant and translation zero-momentum. Its pointwise range lies in `[-7,14]`. It must never be silently replaced by the flat-projected **electric shift** from #144 or by `chi(a)+chi(b)` without the physical sums/multiplicities.

## Correct spectral target and proof obligation

Let `psi0` be the unique, W-normalized interacting ground vector. Let `lambda_first` denote the smallest spectral value strictly above the vacuum, and let `Pfirst` project onto its **entire eigenspace**, whether or not that eigenvalue is degenerate. Define `v=(O_sum-<psi0,O_sum psi0>_W)psi0`, which satisfies `<psi0,v>_W=0`. The required strictly positive spectral weight is

`weight_first=<v,Pfirst v>_W=||Pfirst v||_W^2 > 0.`

An explicit positive *rational* lower bound, not positive variance, positive flat-sector matrix rank, a Ritz overlap, or non-forbidden symmetry, is the acceptance condition. The E3..E8 contamination and all higher states must be rigorously enclosed; if an E2 degeneracy occurs, certify it and use its full projector.

### An independently checkable rational filter lower bound

One possible independent route uses a rational polynomial (or a rigorously bounded rational functional calculus approximation) `F=f(H)`. After certifying an isolated first-excitation interval and the rest of the *full* spectrum, prove `|f(lambda)|<=a` on the first-eigenspace and `|f(lambda)|<=b` on its complement, where `a>b>=0` are **rational**. Let `L` be a certified lower rational bound for `||Fv||_W^2` and `U` a certified upper rational bound for `||v||_W^2`. Then from orthogonality of the spectral components,

`L <= ||Fv||^2 <= a^2*weight_first + b^2*(U-weight_first)`,

hence the exact rational conclusion

`weight_first >= (L-b^2*U)/(a^2-b^2)`.

This is **strictly positive only if `L > b^2 U`**. It provides a falsifiable, integer-arithmetic proof target without numerical square roots. Upper and lower bounds must include all projection, ground-vector and spectral-filter errors. A filter `f` that is large in other low eigenmodes fails the test; an unverified spectral count fails it too. The spectral isolation input must be proved at the actual `r=9` model, not inferred from the large-`r` #144 theorem. The source-conditional #136 windows alone do not replace a separate certified E3 boundary and E2 multiplicity check.

A distinct route may use the exact weighted 8-flat Feshbach/Schur map and a certified lift of the Wilson transition to the full Hilbert space. The leading `C1` eigenvectors have disjoint support and *any diagonal flat character has zero leading off-diagonal matrix element*. The full `r=9` question is therefore sensitive to higher-order mixing and nonflat contributions; never promote the leading zero to an exact dark-channel theorem.

## Verification and falsifiers

- **Preflight:** independently construct all six S₃ elements, closed ordered holonomies, local gauge conjugations, x/y translations, eight commuting-holonomy flat classes, their weighted normalization and the leading selection-rule zero. The first controls must actually mutate character values, winding completeness, and W weights, and reject by named reason.
- **Spectral engine:** exact-rational or integer-only first-level isolation with an explicit E3 boundary, whole-space weighted ground residual, E1 leakage suppression, and a nonzero lower weight. All twelve prediction-frozen faults are to be physically executed when their input is available, with named refusals.
- **Outside seat:** independently reconstruct both the operator and the strict positive lower bound by a second method, and pin the source, receipts and falsifier logs by SHA-256.
- **Fail-safe:** if the candidate stays dark or positivity is not certified, report `HOLD` and keep #137 open. It is legitimate to test an alternative *explicitly named* gauge-invariant operator after a separate prediction freeze, but never relabel #144's dual electric shift as the Wilson-summed observable.

No modification to prior #131/#136/#143/#146 certificates, no new physical-continuum claim and no work on the QNN blind ensemble.
