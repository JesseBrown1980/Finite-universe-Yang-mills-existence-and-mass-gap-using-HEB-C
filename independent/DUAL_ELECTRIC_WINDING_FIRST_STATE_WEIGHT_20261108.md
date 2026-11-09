# A first-excitation-visible dual electric winding observable in finite S3 (strong r)

November 8, 2026. New **post-exploration mathematical prediction**, submitted for independent review. Not a conventional Wilson traced winding, a collider observable, or a four-dimensional continuum result.

## Exact operator, including the original full gauge Hilbert space

Let H=J_E(E+rM) be the finite periodic spatial 3×4 gauge-invariant S3 Hamiltonian. Let P be the W-orthogonal projector onto its **eight** magnetic-flat gauge-orbit basis states, labeled by commuting torus holonomy pairs [a,b] modulo simultaneous conjugation, and Q=I−P. The raw orbit weights are (1,3,2,3,3,2,2,2), totaling 18.

Define a **nonlocal electric x-cycle shift** T_x acting on *flat orbit class functions* by

    (T_x f)([a,b]) =
         sum_{t in S3-transpositions : (t a)b=b(t a)} f([t a,b]).

Extend it by zero to the full nonflat physical subspace:

    O_dual := P T_x P.

The transposition conjugacy class is invariant under simultaneous gauge conjugation, so this is an unambiguously defined operator on physical gauge-orbit functions. Every flat class is invariant under lattice translations up to gauge, hence O_dual has zero translation momentum. The exact orbit-weighted detailed-balance identity makes it self-adjoint in the physical W inner product, and row sums at most 3 give ||O_dual||<=3. It is **NOT** multiplication by the ordinary horizontal winding character χ(W_x), and is explicitly a nonlocal, flat-projected dual electric operator; do not relabel it a standard local Wilson observable.

## New exact flat-state matrix element

The independently audited three-move Schur coefficient C1 from merged #143 equals (3/2) T_y, where T_y is the same transposition class-sum acting on the **second** holonomy b. In the eight-class order (e,e),(e,t),(e,c),(t,e),(t,t),(c,e),(c,c),(c,c^-1), the two largest C1 eigenvalues are 9/2 and 3/2, with W-orthogonal rational eigenvectors

    g0 = (1,1,1,0,0,0,0,0)
    g1 = (0,0,0,1,1,0,0,0).

Both have W-norm² 6. The exact new electric x-cycle operator obeys

    <g1,T_x g0>_W = 6,

so its normalized transition matrix element is **exactly 1**. In contrast, *every multiplicative/diagonal* function of the flat holonomies has zero matrix element between g0 and g1 at this order, because the supports are disjoint. This is an important distinction for selecting an observable.

## Rigorous all-nonflat remainder and full eigenvector control

The complete nonflat compression satisfies M_Q>=3I and ||A_Q||<=72. The independently checked, store-free all-states Schur remainder from #143 is

    eta(r) = 5184/(3r−72)^3 + 373248/[(3r)^2 (3r−72)].

The ideal eight-state effective Hamiltonian is K=(72−18/r)I−C1/r². Its two top C1 eigenvalues correspond to the **first two full energy levels** for r>=100000, by the eight-low-state separation and ||Schur_error||<=eta. The nearest ideal eigenvalue separations are

    gap_g=3/r²,     gap_e=(3/2)/r².

For a normalized exact full eigenvector psi_j with normalized P projection v_j, the Schur identity gives ||(K−E_j)v_j||<=eta(r). Elementary spectral projection in the W Hilbert space gives, after phase choice,

    ||v_j − g_j/||g_j||_W||_W <= 2 eta/(gap_j−eta).

Hence the triangle inequality and ||T_x||<=3 yield the strict lower bound

    |<v_e,T_x v_g>_W|
       >= 1 − 6[eta/(3/r²−eta)+eta/((3/2)/r²−eta)].

The exact Q-resolvent and ||B||²=72 also imply ||Q psi_j|| <=sqrt(72)/(3r−72)||P psi_j||. For normalized psi_j, the product of the two projected norms is >=1/(1+q), with q=72/(3r−72)^2.

At r=100000, an independently combined **integer-rational** evaluation (no floating-point approximation) establishes

    6[eta/(3/r²−eta)+eta/((3/2)/r²−eta)] < 93/100,
    q < 1/1000,
    (7/100)/(1001/1000)=70/1001 > 1/16.

Because r² eta(r) and q decrease for r>24, these inequalities hold for every r>=100000. Therefore the **true, full finite-Hilbert-space first-excitation spectral weight** of the explicitly defined O_dual obeys

    |<psi_2,O_dual psi_1>_W|² > 1/256   for all r>=100000.

This bound accounts for all omitted nonflat states; it does not rely on the old massive 3×4 Perron vector or on a truncated Ritz overlap. It also proves the first level is isolated in this regime by the same spectral gaps and remainder.

## Provenance and scope

The executable pure-integer checker constructs all 18 commuting holonomy pairs and eight classes from S3 permutations, independently computes the weighted T_x and T_y matrices, their normalized top-mode overlap, the complete rational bound at r=100000 and its uniform monotonicity argument. Four deliberately perturbed cases change actual transposition count, orbit weights, matrix edges and the candidate first eigenvector; they must all be rejected. Hosted HBP replay is required before scientific promotion.

**What this does NOT resolve:** the original #137 asks whether the conventional translation-zero **summed Wilson winding character** detects the first excited state at r=9. It remains OPEN. Our new O_dual is intentionally different and the rigorous bound begins only at r>=100000. Further work must either certify the ordinary O_sum at r=9 or explicitly identify another gauge-invariant operator with a certified r=9 first-state spectral weight. No finite fixed-lattice theorem here proves a gap uniform in physical spacing/volume, confinement, or 4D continuous SU2 Yang–Mills existence.
