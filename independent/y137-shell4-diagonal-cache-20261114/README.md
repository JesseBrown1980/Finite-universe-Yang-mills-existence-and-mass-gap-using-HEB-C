# #137: hash-addressed shell-4 diagonal Schur source / instant fixed-trial inertia

**Status:** NEW SOURCE RUN + INDEPENDENT REPLAY PENDING. Issue #137 remains OPEN.

This layer is based on the reviewed complete shell4 boundary-resolvent source
from draft #189 and on the second-seat review's exact per-magnetic refinement.
The original #189 matrices and receipts remain unchanged. The review's independent
plain breadth-first 1,985,218-orbit recount is cited, not imported.

## 1. New exact upper bound by *individual* magnetic cost

The gauge-orbit Hamiltonian is H = 72 I - T + 9 M. In the true
orbit-size W inner product, T is self-adjoint and has norm <= 72
because it restricts the raw 72-regular symmetric move graph.
For the shell4 principal compression of A=QHQ-z:

    A44 <= D4,
    (D4)_{ii} = 144+9 m_i-z,

since 72I+T44 is positive semidefinite. D4 is diagonal,
positive on the tested energy interval, and *m_i* is the actual
magnetic cost of that orbit. No shell5 state is silently removed:
the variational correction V=D4^-1 R4 is supported on shell4, and
its full Q quadratic form uses A44 exactly.

For the accepted K3 frozen eight-column trial Y and full Q residual R,

    S(z) <= U(Y - V)
         <= U(Y) - R4*D4^-1 R4
         <= U(Y) - R4*R4/hmax,

where hmax=144+9*16-z. The rigorous old lower bound

    S(z) >= U(Y) - R*R/gamma, gamma=94.0682-z,

is preserved. No assumption about the unknown shell5 resolvent is made.
This improves the source *upper* Schur matrix, though the remaining
source *lower* residual may still be much too large for the Wilson gate.

At frozen trial energy z0, the new 8x8 source matrix is exactly

    S_upper(z0) <= U0 - (1/6)*sum_m G_m/h_m,
    h_m = (144+9m)*10^9 - z0_num,

in the source's common units. Here G_m is the exact
weighted shell4 residual Gram for all shell4 states of magnetic
cost m. In formula above division by h_m includes the source b
scale; the source output is explicitly tagged with the common
integer denominator product_m(h_m).

Both Gram and Schur-width PSD are checked by all 255 integer principal
minors. The checker also requires that the new magnetic refinement is
positive semidefinite relative to the older uniform hmax bound.

**Floor rather than ceiling**: a positive lower credit from an exact
matrix improvement is always rounded DOWN. The complementary ceiling
is reported only for diagnostic display. This corrects the ambiguous
gain ceiling label in draft #189.

## 2. Exact polynomial cache for arbitrary z at a frozen Y(z0)

For a frozen trial Y0 with original sample z0, define

    H_ij = sum_{q in K3} w_q Y0(q,i)Y0(q,j),
    J_ij = sum_{q in K3} w_q (s0(q,i)Y0(q,j)+Y0(q,i)s0(q,j)),

where s0 is the source's exact Q residual at z0, and all
quantities use the original integer conventions (no floats).

For delta = z_num - z0_num,

    U(z) = U0 - delta*(scale^2 diag(wflat) + H),
    G(z) = G0 - 6*delta*J + 6*delta^2*H,
    G_m(z) = G_m(z0).

The last identity holds because Y0 has zero shell4 support, so
the complete shell4 exterior residual is independent of z.
These are exact polynomial identities for the **same frozen trial**,
not an extrapolation of a newly reoptimized Jacobi trial.
The source performs a direct independent-in-program evaluation at
z0+1 and must reproduce both polynomial predictions entry by entry.

The first expensive calculation emits compact, immutable eight-by-eight
matrices U0, G0, H, J, and G_m. The SHA-256 matrix hashes remain
pinned to the historical accepted #189 source.

The independent graph-free quick replayer reads only these values,
derives U(z), G(z), the m-conditioned Schur upper, the whole-Q
Schur lower, and exact symmetric inertia at each of 13 pre-sealed
energy thresholds. It separately implements matrix determinant,
all-255-minor PSD, and inertia by integer congruence. It computes
the intersection of the two valid frozen-trial count enclosures.

This changes the cost of a further fixed-trial threshold from
a K3 rebuild and millions of shell4 states to a handful of exact
8x8 integer operations. It does **not** make the SHA a mathematical
answer; it uses a SHA to ensure the mathematical coefficients are
the ones actually verified.

## 3. Acceptance gates and remaining theorem work

- Frozen source pins, energy probes and W orbit metric
- Actual complete 1,985,218-orbit shell4 magnetic census
- G_m>=0 for every populated magnetic bucket
- Sum_m G_m + G_inner = original accepted full-Q G, exactly
- Separate complete exterior-edge direction check for both samples
- Stronger diagonal Schur PSD sandwich, stronger than hmax
- Exact z0+1 trial-polynomial check without Jacobi rerun
- Independent graph-free integer verifier with altered-byte rejection
- Clear separation from a *new trial that includes shell4*. To reach
  the >100-fold improvement objective, an actual shell4-extended trial
  and a rigorously bounded new shell5 residual remain critical.

The first-excitation Wilson spectral weight stays **HOLD** until the
complete normalized full-Q signed Wilson overlap has a rational
strictly positive bound. These finite S3 results imply no continuum
SU(2) or infinite-volume theorem.
