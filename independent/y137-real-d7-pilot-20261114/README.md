# #137 degree-7 REAL periodic-3x4-S3 full-Q source pilot

**This is a real-operator pilot, not a completed degree-7 moment certificate.**

Objective: independently enumerate complete raw 24-link × 3-transposition
electric moves under the gauge-orbit canonicalizer, construct an exact
full-Q operator action on an 8-column source, and test how far a
degree-7 paired-moment calculation can run under a finite hosted budget.

The source used first is the **Y=0** Schur trial residual,
R0=-QHP, not the accepted 20-Jacobi-step K3 residual used for
the current Wilson transition. The Y=0 residual lives on the
first 264 nonflat orbits, so its first two full Q moments can
be computed without constructing all 2,177,317,873 orbits.

The raw source uses the **actual** 3×4 periodic S3 group constants,
the complete 72 electric move action, all eight flat states and
exact orbit weights. It reconstructs R0 from Q-to-flat couplings,
independently enumerates all 72 raw moves for every nonzero active
source, applies Q after generating the complete move list (flat
destinations are projected out), and checks reverse weighted
adjacency and a separately evaluated row-action on selected target
states.

The source-driven Q operator is

    (QH Q v)_x = (72 + 9m_x) v_x - Σ_(y in Q) T_xy v_y,

with W_x T_xy = W_y T_yx. Iterate V_j=(QHQ)^j R0,
including all reached target indices and their coefficients;
no radius cut is used in any accepted moment.

Two full operator passes produce

    mu0 = R0*W R0,
    mu1 = R0*W V1,
    mu2 = V1*W V1,
    mu3 = V1*W V2.

These are **four exact 8×8 full-Q moment matrices** per sample
after a polynomial shift by z: A_int=10^9 QHQ - z I.
The pilot emits their entire integer entries, SHA-256s,
the 72-move totals, the source/target frontier sizes, W
adjoint controls and a real-source proof scope row. The shift
is evaluated exactly through the binomial identities, so the
same two expensive source passes serve both original energy
samples.

This is distinct from the accepted #191 degree-16 norm-bound proof,
which does not compute a real corrected Schur center. The accepted
K3 residual R_K3 already has shell4 support on 1,985,218 orbits,
and its degree-7 run needs a distributed/bounded-memory whole-Q
streaming representation plus independent complete-move checker.

Resource limits are explicit in source, and the verdict must remain
HOLD if higher passes cannot fit. No 14-moment degree-7 center, E1/E2
state transfer or Wilson spectral weight can be concluded from four
moments of Y=0.

### Proposed next run gates

After first two passes certify (1) a complete source and index;
(2) exact closure of **each operator application**, not global closure
of an unexpanded ball; (3) all 72 moves per source, W balance,
independent raw transitions and selected direct row applications;
(4) W pairing equality and shifted polynomial identities.

To promote a full n=7 source certificate, independently certify all
14 moments of **the accepted K3 trial** (not the Y=0 pilot),
applying the complete Q operator seven times, with no unresolved
exterior destinations. Recompute the corrected 8x8 Schur center
from these moments and verify the normalized Wilson sign bound.
