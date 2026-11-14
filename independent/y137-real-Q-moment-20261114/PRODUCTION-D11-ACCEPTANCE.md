# Issue #137 production target: degree-11 accepted-K3 full-Q moments

**Decision frozen 2026-11-14:** degree **11** is the production
Chebyshev corrected trial. Degree **7** is only the already authorized
lower-cost 72-move source-validation pilot in draft #192, which uses
the different Y=0 source. It is not the stopping degree for #193.

## Exact production obligation

The accepted K3 trial at each original E1/E2 frozen sample has real
source data R_z supported on K3 plus all 1,985,218 shell4 orbits.
Let b=10^9, X_z=b(QHQ-zI), W the exact orbit-size metric and

    mu_k(z) = R_z* W X_z^k R_z,      k=0,...,21.

There are **22 complete symmetric 8x8 integer moment matrices per
sample**, hence **44 sample-specific matrices** total.
The paired form is

    V_j = X^j R,
    mu_(2j)   = V_j* W V_j,
    mu_(2j+1) = V_j* W X V_j,    j=0,...,10.

The final odd moment mu21 is an **on-support W-weighted edge
quadratic form** in V10, so **10 complete outward applications**
construct V0 through V10 and supply all 22 moments. The final
V11 (largest outer frontier) is not constructed. For all earlier
odd moments the paired alternative V_j*W V_(j+1) remains available.
The full 72-move operator on each true support must be independently
verified, including diagonal and self-loop contributions. Both
frozen energies share graph geometry but retain separate R_z.
Any compression, power-of-three jump, or hash cache MUST preserve
the whole-Q operator and exact W pairing, with a proved reduction
rather than an assumed closed finite shell.

Completed and preserved in #193:

- mu0 for both frozen samples: accepted exact K3 full-Q Gram, PASS.
- mu1 for both frozen samples: all eight exhaustive shell4 shards,
  142,935,696 raw moves, exact 8x8 matrices and source checks, PASS.
- first degree-1 corrected source Schur sandwich: corrected against
  the accepted normalization and inertia, PASS. The old extra-10^9
  matrix receipt remains preserved as REJECTED.

Remaining real source moments for degree 11:

    mu3, mu4, ... , mu21: 19 8x8 matrices per frozen sample.

The exact real mu2 8x8 matrices and all raw source/target fan-in
checks passed in #194. The complete V1 target values must be kept
or exactly replayed for the next true mu3 on-support edge form:
a mu2 Gram alone loses target-specific amplitudes.

**Resources:** The first complete outward application and mu2
have now passed for both accepted-K3 samples in the descendant
[#194 run 43606393196](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43606393196).
It resolved **18,598,040 actual shell5 target states** and all
**125,426,880** Q4-to-Q5 edge records. The independent source review
is still pending. The remaining applications are the nine transitions
V1→V2 through V9→V10, with a final mu21 support-edge quadratic
form requiring no V11. At every step measure source support, complete
frontier, W-weighted spill, canonicalizer agreement, memory and disk.
If support growth makes this infeasible, record RESOURCE_HOLD and
develop a proved transfer/moment reduction, preserving degree 11. Do NOT quietly replace the
goal with degree 7 or truncate the outer frontier.

## Correct historical integer-source normalization — hard acceptance gate

Use the accepted #190 source's exact integer matrix U0 and R; **no
extra factor b=10^9** multiplies the moments when building the centre.

For each energy, define certified operator endpoints

    g = 94068200000-z_num,
    h = 468000000000-z_num,
    s = g+h,
    d = h-g.

Define exact integer polynomials

    P0(X)=1, P1(X)=s-2X,
    P_(n+1)(X)=2(s-2X) P_n(X)-d^2 P_(n-1)(X),
    K_n=P_n(0)>0.

Set n=11 and polynomial C21:

    C21(X)=(K11^2-P11(X)^2)/X = sum_(k=0)^21 c_k X^k.

The actual accepted-source corrected variational centre is

    U11 = U0 - [sum_(k=0)^21 c_k mu_k] / K11^2.

The complete Q residual is R11=P11(X)R/K11, and the resulting
source-conditional Schur bounds are

    U11 - [d^22/(g * K11^2)] mu0 <= S(z) <= U11.

The bound is the **square** of the Chebyshev norm factor
d^11/K11. Thus the residual-Gram contraction is d^22/K11^2;
there must be exactly two powers of K11 in the denominator, not 22.
Use only exact integer numerator/denominator arithmetic, with
the grouping written explicitly in code.

The global whole-Q floor and upper 468 bound remain the accepted
conditional inputs. The norm-contraction factor d^11/K11 has a
separately verified strict upper of 0.008 at both original samples
(approximately 0.00791 and 0.00794), hence a squared residual-Gram
factor less than 0.000064. This mathematical estimate does not by
itself settle the fully normalized Wilson weight or the energy-window
part of the sign-transfer budget.

**Must verify independently, in original U0 units:**
1. Exact raw 72-move row completeness for every nonzero Q source at
   each pass, all destination canonical orbit IDs resolved or explicit
   P projection, every W-weighted electric reverse edge consistent;
   sample columns independently regenerated from the raw move rule.
2. Immutable source hashes and both frozen samples, complete outgoing
   edge counts, exact 8x8 mu0/mu1 historical byte agreement,
   paired-moment identities, PSD block-Hankel Gram/localizer checks.
3. Corrected two-sided Schur bracket nested in the accepted original

       U0-mu0/g <= new_lower <= new_upper <= U0

   in the exact 8x8 Loewner order.
4. Original and new upper and lower Schur inertia counts match the
   certified E1=1 and E2=2 at the same frozen energies. An
   extra-billion-factor planted error MUST be rejected, as in #193
   corrected degree-1 run.
5. Independently recompute the exact normalized, original
   (unshifted) E1→E2 Wilson amplitude and compare source, energy,
   projector-angle and normalization errors with the <1/700
   positivity gate. Improving the source residual alone is not a
   complete positive-weight proof.

## Status

**Degree-11 real source: IN PROGRESS, NOT CERTIFIED.**
The three 8x8 mu0/mu1/mu2 matrices per sample are accepted
conditionally on the archived source and complete #194 mu2 source
fan-in; mu3..mu21 are NOT COMPUTED. The independent
full raw-transition source audit remains open.
The true first-excitation Wilson spectral weight remains HOLD,
issue #137 OPEN, #193 DRAFT. Degree-7 Y=0 pilot #192 may remain as a
separate instrument gate but is not the production destination.
