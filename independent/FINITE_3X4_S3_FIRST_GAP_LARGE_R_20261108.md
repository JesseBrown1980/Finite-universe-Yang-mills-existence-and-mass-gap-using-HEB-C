# Finite 3x4 S3 FIRST excitation: strong-magnetic exact Schur bound

**2026-11-08; DRAFT for independent mathematical review.** This is a new post-exploration theorem proposal. No prediction-first claim: the 8x8 coefficients were found before this note was frozen. No 27GB store was read, no previously certified large eigensystem was recomputed, and no 4D continuum SU(2) result is claimed.

## Statement (one-based energy levels)

For the full periodic 3x4 spatial S3 gauge Hamiltonian H=J_E(E+rM), r=J_B/J_E, J_E>0, let E1<=E2 be its two lowest **full physical gauge-invariant** eigenvalues. The total gauge-orbit dimension is 2,177,317,873, not the 45,508,080-row Sx+Sy+ sector. Define d=3r and

    eta(r) = 5184/(d-72)^3 + 373248/[d^2(d-72)].

The exact-rational analytic certificate claims for every r>=10000:

    0 < 3/r^2-2 eta(r) <= (E2-E1)/J_E <= 3/r^2+2 eta(r).

At r=100000, outward-rational enclosure:

    271961/10^15 <= (E2-E1)/J_E <= 328039/10^15.

The 3/r^2 leading law is a genuine first-gap asymptotic, not the earlier accepted E9-E8 high-cluster bound at r=9. This certificate does not bound E2-E1 at r=9 and does not establish the first-state overlap of any Wilson observable.

## Operator and decomposition

The S3 two-dimensional character has chi(e)=2, chi(transposition)=0, chi(3cycle)=-1. Magnetic potential M(U)=sum_{plaquettes}[2-chi(P)] is nonnegative. There are 24 positive links and 3 electric transposition moves each; E=72 I-A where A is the sum of their unitary involutive link actions, restricted to gauge-invariant functions. Thus E>=0, A is Hermitian, ||A||<=72.

P projects onto the eight flat conjugacy classes of commuting torus holonomy pairs (a,b), Q=I-P, B=PAQ. Enumerating the 18 commuting pairs and their 8 simultaneous-conjugation classes gives 8 flat orbit states. All 72 one-electric-move neighbors of any flat state are nonflat with M=4; there are 264 distinct neighboring physical orbit classes. There are no 2-move transitions between distinct flat classes. Consequently, exactly:

    P H P/J_E = 72 I_8
    B B* = 72 I_8
    B M_Q^-1 B* = 18 I_8.

### Magnetic lower bound WITHOUT the huge store

The sign homomorphism S3 -> {+1,-1} makes each transposition plaquette odd and every 3-cycle plaquette even. Each periodic-torus link appears twice with opposite orientation in the product of all plaquette signs, so the total product is +1. There can be no isolated transposition plaquette; transposition plaquettes occur in even count and cost 2 each. One nontrivial 3-cycle already costs 3. Therefore every nonflat field satisfies M>=3, without relying on the 45.5M-row original magnetic census.

## Exact 8x8 interaction coefficient

For lambda<=72, put delta=72-lambda>=0, D=r M_Q, A_Q=QAQ, and R=(D-A_Q+delta I)^-1. Schur reduction to P gives

    [ (72-lambda)I_8 - B R B* ] psi = 0.

The first two inverse powers of r give

    B D^-1 B* = 18/r I_8
    B D^-1 A_Q D^-1 B* = C1/r^2.

Two independent constructions check C1:

1. Exhaustively enumerate every first-shell physical gauge-orbit neighbor with an explicit spanning-tree gauge fixing and reconstruct weighted electric counts; 264 distinct first-shell states, M=4, exact reverse weighted-adjacency.
2. Enumerate only S3 commuting-pair conjugacy classes. All nonzero 3-move flat-to-flat bridges run along three y-direction links at a fixed one of four rows, with 3! orderings and intermediate magnetic costs 4,4, contributing 4*6/16=3/2 per valid holonomy transposition.

In a compatible eight-class order the exact C1 block structure is

    CA = ((0, 9/2, 0), (3/2, 0, 3), (0, 9/2, 0))
    CB = ((0, 3/2), (3/2, 0))
    C1 = CA direct_sum CB direct_sum zero(3).

This matrix is symmetric in the orbit-weighted inner product. Its eight exact eigenvalues are 9/2,3/2,0,0,0,0,-3/2,-9/2 (all eigenvectors can be given with rational coordinates). The top two differ by exactly 3.

## Control of EVERY nonflat state, not just the nearby shell

For d=3r>72, QHQ/J_E >=d. Every one of the lowest eight eigenvalues has lambda<=72 by min-max, while the ninth has lambda>=d by Cauchy interlacing of the nonflat principal compression. The eight low roots are therefore isolated.

At a low eigenvalue, the Schur identity and ||B||^2=72 give 0<=delta<=72/(d-72). Put R0=(D-A_Q)^-1. The resolvent identities are

    R-R0 = -delta R R0
    R0-D^-1-D^-1 A_Q D^-1 = D^-1 A_Q D^-1 A_Q R0.

Because ||R||,||R0||<=1/(d-72), ||D^-1||<=1/d, ||A_Q||<=72, and ||B||^2=72, we obtain the EXACT, all-states operator bound

    ||B R B* -18/r I_8 - C1/r^2||
       <= 72^2/(d-72)^3 + 72^3/[d^2(d-72)]
       = eta(r).

The eight Schur eigenvalue branches are monotonically decreasing in lambda. By Weyl's inequality the j-th full low eigenvalue lies within eta(r) of 72-18/r-mu_j/r^2, with mu_j sorted from largest to smallest. For the first two levels mu1=9/2 and mu2=3/2, giving the claimed 3/r^2 +/- 2 eta(r) gap bound. The function r^2 eta(r) is decreasing for r>24. A positive left bound at r=10000 (checked with exact rational arithmetic) thus applies to all larger r.

## Provenance, falsifiers, and limits

This independent seat locally executed a full first-shell S3 gauge-orbit enumeration and a second exact commuting-holonomy-only calculation, then checked all the rational bounds. Ten deliberately incorrect mathematical controls were rejected, and the two local output receipts replayed byte-for-byte. Those local scripts and receipts are supplied in the conversation artifact; the compact independent analytic verifier is filed alongside this note. An additional independently authored hosted reviewer should repeat the short-path classification and the full-space Schur indexing before acceptance. This result must remain DRAFT until those gates complete.

This proof does not use the original 3x4 Perron bound, does not compute E2-E1 at r=9, and does not establish any first-eigenstate winding spectral weight, spatial-volume-uniform bound, physical mass, continuous SU(2), or Clay mass gap. The earlier finite E9-E8 verdict and historical OPEN evidence are unchanged.
