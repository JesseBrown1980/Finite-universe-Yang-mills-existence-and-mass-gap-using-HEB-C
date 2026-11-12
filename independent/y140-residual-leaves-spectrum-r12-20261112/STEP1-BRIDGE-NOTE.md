# Step 1: why the comparison matrix bounds the level count (hand derivation, 2026-11-12)

Status: derived by hand by this unit; GPT-6 derived the same inequality independently the same day. CONJECTURE in
the seat's triad until a third party checks the proof. Scope: the symmetry-invariant sector only (see the end).

Setting. H_Q is the Hamiltonian on the non-flat space, in a basis where every off-diagonal entry is <= 0 (each
move enters with coefficient -1) and the diagonal is 72 + r M. Split the basis into the core C (M <= m0) and the
tail T (M > m0):  H_Q - t = [[H_CC - t, B^T], [B, H_TT - t]].

1. Tail bound. For a symmetric matrix A with off-diagonal entries <= 0 and any vector f > 0,
       x^T A x = sum_k ((A f)_k / f_k) x_k^2 + (1/2) sum_{k != l} (-A_kl) f_k f_l (x_k/f_k - x_l/f_l)^2
   so A >= diag((A f)_k / f_k). Take A = H_TT - t and f = the certificate's weight word as a function of M.
   The verifier's tail-cap gate proves (A f)_k > 0 on every tail orbit for t below the cap. Hence
       H_TT - t >= D_f(t) > 0   and so   (H_TT - t)^{-1} <= D_f(t)^{-1}.
2. Schur complement. S(t) = H_CC - t - B^T (H_TT - t)^{-1} B >= H_CC - t - B^T D_f(t)^{-1} B = G(t).
   G(t) is exactly the matrix the verifier applies to the certificate vector (core counts, and for every one-step
   tail orbit the weight f_k / N_k on each move back into the core).
3. Counting. Since H_TT - t > 0, the inertia of H_Q - t is the inertia of (H_TT - t) plus that of S(t), so the
   number of levels of H_Q below t equals n_-(S(t)), and S(t) >= G(t) gives n_-(S(t)) <= n_-(G(t)).
       N_{<t}(H_Q) <= n_-(G(t)).
4. Once more inside the core. Split the core classes into L and R. G(t) has off-diagonal entries <= 0 (checked
   exactly), so for any g > 0 on R with d = G_RR g > 0:  G_RR >= diag(d/g) > 0, and the same two steps give
       n_-(G(t)) <= n_-(K(t)),  K(t) = B_LL - B_LR diag(g_a / (W_a d_a)) B_RL,  B = diag(W) G.
   Rounding the diagonal coefficient up keeps the inequality.
   K(t) is a small exact rational matrix whose inertia is counted exactly.

Consequence: if n_-(K(t)) = k then level k+1 is >= t.

Scope that must travel with every use. Everything above is applied to the 48-symmetry-class matrix, that is, to
H_Q restricted to symmetry-invariant states. The lowest level of the whole H_Q is invariant (positive vector), so
the floor is a statement about the whole space. Levels 2, 3, 4 of the invariant sector are NOT known to be
levels 2, 3, 4 of the whole space: a state that changes sign under a lattice symmetry may lie below them. The
Ritz upper bounds hold for the whole space; the lower bounds hold for the invariant sector only.
