# Issue #137 — independent checker for next shell-4 / energy certificate

**Scope:** independent integer-arithmetic acceptance preflight against five immutable accepted
mainline receipts (#180, #184, #185, #186, #187). This does **not** calculate a new
2-million-orbit shell-4 correction, does **not** improve either true energy bracket, and
does **not** certify the actual first-excitation Wilson weight. The real theorem
remains **HOLD** pending an independent full-Q source measurement and review.

## Accepted evidence and checker independence

The checker imports **none of the source scripts** from #180–#187. It reads the original
receipt bytes, verifies their exact Git blob SHAs, separately reconstructs the normalized
flat/Q transfer through integer upper-rounded roots, checks both source matrix hashes,
the actual E1/E2 interval endpoints, the accepted PSD/null-branch flags, and the
original unshifted Wilson fixed-sample lower weight. It replays both accepted state
errors exactly: 44731270536 and 99359189983 in 10^-12 units, combined 144090460519.
A byte change in a pinned source fails.

This is a **second implementation of the composition arithmetic**. Independence of
future shell-4 source coefficients must additionally be established by a separately
written weighted graph builder/verifier (FABLE5/second-seat review). Matching an
accepted receipt alone is not a new independent source proof.

## Exact Krylov/Feshbach residual lemma for the next source certificate

Let A=D-z on the **entire weighted Q Hilbert space**, and assume the accepted
lower bound A >= gI > 0 (g=94.0682-z for the frozen r=9 samples).
For any current eight-column trial-Q vector Y, with residual R=A Y+B,
the symmetric variational Schur upper matrix is U(Y), and the exact Schur matrix is

    S(z) = U(Y) - R* A^-1 R.

For **any correction V** (including a finite-support shell-4 Krylov corrector),
set

    Y' = Y-V,
    R' = R-A V,
    K = R*V + V*R - V* A V,
    U(Y') = U(Y) - K.

Then the following rigorous matrix inequalities hold in the weighted flat inner product:

    U(Y') - (R'*R')/g  <=  S(z)  <=  U(Y').

Proof: expand R'*A^-1 R' and use 0 <= A^-1 <= I/g; the identities
are exact in the weighted Hermitian metric. The uncorrected certificate
uses V=0. Thus ANY reduction in the **complete** residual Gram after an
independent source correction directly strengthens the actual Schur sandwich,
with no need to compute the full Q inverse.

For a targeted shell-4 V, R' can have support on shell 3, shell 4 **and
shell 5**. The independent source verifier must rebuild ALL reached
states and weighted edges, including next-shell contributions. Omitting shell 5
is a mathematical error, even if an inner-K3 residual happens to vanish.

The checker includes a rational two-state toy example:
A = [[10,-1],[-1,5]] >= 4I, R=(10,0), V=(1,0), R'=(0,1).
The exact residual correction is 500/49, the variational correction is 10,
and the valid upper is 41/4. If shell 5 is omitted, the false upper is 10,
which is strictly below 500/49; the planted omission must be rejected.
The toy verifies the **lemma/fault control**, not the actual 3x4 S3 source.

## Exact independent budget replay

The prior exploratory issue comment #6866536747 contains slightly different last
digits on the hypothetical error ceilings; this isolated checker corrects them.
All results use 10^-12 outward ceilings. In the conservative counterfactuals
the accepted Rayleigh mu is **held fixed**:

| Hypothesis, not a new certificate | Combined bound | Numerical 1/700 gate |
| --- | ---: | --- |
| Accepted mainline | 0.144090460519 | HOLD |
| Schur source action artificially zero | 0.013162197722 | HOLD |
| Energy variation artificially zero | 0.130824656179 | HOLD |
| Divide both by 100, keeping original mu | 0.001435396879 | HOLD |
| Divide both by 101, keeping original mu | 0.001421178505 | Would pass |

If the narrowed energy bracket also independently justifies recomputing the
Rayleigh scalar term, the 100-fold counterfactual gives 0.001318722908.
**These are sensitivity tests only:** none of the stronger input hypotheses
has been certified. The original Wilson fixed-sample squared weight >0.000416300
and operator norm <=14 imply the sufficient true-state sign threshold
combined error <1/700.

## Independent source tasks before promotion

1. Freeze the K3 sample vectors/energies, exact W orbit weights, and all source
   evidence hashes. A second implementation generates the shell-4 Krylov
   correction V and the complete R' Q-residual Gram, with all shell-5 neighbors
   and electric couplings. Verify W-adjoint detailed balance and exact U'
   above. Preserve a deliberately omitted shell-5-edge falsifier.
2. Use the new 8x8 S(z) brackets to independently recount full-E1/E2
   inertia at a frozen microgrid. Check both reflection sectors and null branch,
   retaining ambiguous points as holds. Source 14-point historical grid
   stays unchanged.
3. Rerun normalized Q tails and the **unshifted original seven-loop Wilson**
   signed interval. A positive actual first-excitation spectral weight may
   be claimed only after a strictly positive rational bound for the true
   full-W normalized eigenstates and independent source verification.

Run locally:

    python3 -I -B independent/y137-shell4-krylov-verifier-20261113/verify.py

This checker is intended to be runnable in a clean hosted PR workflow. It
does not trigger or impersonate an external FABLE5/second-seat agent.
