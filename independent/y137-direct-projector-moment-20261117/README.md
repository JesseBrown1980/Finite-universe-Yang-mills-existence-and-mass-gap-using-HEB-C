# Issue #137 — Stage N direct first-excitation Wilson projector moment

**Research draft, 2026-11-17.** A separate direct observable-specific route, stacked on the original seven-loop source PR #180. It leaves the accepted Stage E finite full-physical first-gap proof and K5-inclusive Stage L physical source unchanged. The full Wilson spectral-weight claim remains **HOLD** until true spectral-projector errors are controlled.

## The exact one-sided theorem

For the original finite weighted-Hilbert Hamiltonian H with simple E1<E2<E3 and original physical seven-winding summed Wilson observable O, let psi1 be a **normalized exact** ground eigenstate. Fix a source-certified number L3 with E2<L3<=E3, and set w=O psi1. Define the original-W weighted signed moment

    A = <w,(L3-H)w>_W
        - (L3-E1) * |<psi1,w>_W|^2.

Expanding the exact physical spectral projectors yields

    A = (L3-E2) * |<psi2,O psi1>_W|²
        + sum_{n>=3} (L3-En)*||Pn O psi1||_W².

The high-energy summands are all <=0. Therefore a **strict rational lower bound A>0 proves positive original Wilson E1->E2 spectral weight**, without an independent approximation of psi2. More quantitatively, if A>=a>0 and E2>=E2_lo, then

    |<psi2,O psi1>_W|² >= a/(L3-E2_lo) > 0.

Any implementation must include the ground leakage term, even if the Wilson observable has been shifted by a scalar identity; such a shift does not change the exact E1->E2 channel. E3_LO=69.968699300 is inherited from the accepted whole-physical source-conditional spectral isolation; E2_lo=69.949264147.

## First actual numerical screening (not an eigenprojector certificate)

The new script imports the original PR #180 source-pinned 155,378-dimensional K3 nonflat source, independently built seven-loop Wilson observable and exact fixed-sample trial phi at 69.909875505. It takes the *source-normalized, phi-orthogonal* centered Wilson state

    v(x) = [N*O(x)-<phi,O phi>_W] * phi(x),
    N=<phi,phi>_W.

It calculates its entire original physical H first moment exactly from the 8-flat plus full K3 Q physical source, including original P-Q weighted couplings and all physical diagonal/electric actions. Its signed trial-source proxy is

    M_trial = E3_LO * <v,v>_W - <v,Hv>_W.

The code verifies original seven-loop source weights, physical H positive/468 ceilings, exact trial centering and scalar-shift invariance, and source-frozen PR #180 receipt SHA, and outputs the sign of M_trial with signed integer SHA plus exact rational ratio. This is a **trial-only diagnostic**: phi is not the exact psi1; no valid true-ground projector or E1 spectral moment positivity follows from the sign alone. A negative sign rejects this *unfiltered fixed-trial one-sided moment* as the direct sufficient test without refuting the Wilson E1->E2 channel; a positive sign identifies a promising candidate for an actual source-certified ground-state transfer.

The exact 3-state spectral toys verify the sufficient inequality, ground leakage cancellation, and rejection of a purely high-state transition. Source/CI policy remains strict integer only and refuses changed original PR #180 sources.

## Subsequent acceptance required

1. Compute a rigorous enclosure of A for the **true** psi1, using full physical source moments of the fixed ground trial plus certified original source-dependent projector/ground errors. Bound the ground channel separately; this is not covered by centering a trial phi alone.
2. If M_trial is nonpositive, attempt a **rational spectral filter or direct 8-flat Feshbach projector/resolvent** so high-energy contamination can be bounded without a global 14 times generic state-error penalty. Only claim improvement when a signed actual source interval excludes zero.
3. Independently rebuild the exact original-W O H O weighted source and compare the hosted integer receipt. Keep Wilson HOLD until a strictly positive actual A lower bound and independently reviewed exact inequality are accepted.

The source-conditional finite first gap is already enclosed as 0.039677591<(E2-E1)/J_E<0.040004463 by the earlier Stage E whole-physical Schur result. Stage N addresses a different mathematical obligation: Wilson first-excitation visibility. Four-dimensional continuum Yang–Mills remains OPEN.

Run:

    python3 -I -B independent/y137-direct-projector-moment-20261117/wilson_moment.py toy
    python3 -I -B independent/y137-direct-projector-moment-20261117/wilson_moment.py real
