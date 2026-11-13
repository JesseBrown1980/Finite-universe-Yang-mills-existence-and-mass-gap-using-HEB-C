# MAP: Umeno's certificate ingredients against the finite S3 3x4 work (floor lane, mapping)

Written 2026-11-09 by the MAPPING lane of the floor workflow. Scope: the periodic 3x4 S3 lattice,
`H/J_E = 72 I - T + r M` on the 2,177,317,873 gauge orbits, weights W, flats P (8 orbits, M = 0), Q = nonflat.
Target of the floor lane: a rigorous lower bound gamma on `lambda_min(QHQ)` at r = 9 (the conditional value is
94.070673 from #131; any gamma >= 80 is useful). No continuum, 4D, SU(N) or Clay claim.

Tags: MEASURED (r-independent counts, or excluded r only), DERIVED (proved here, to be reviewed), REPORTED (from a
paper, PR or another lane), CONJECTURE, OPEN.

**Rule compliance.** Nothing r-dependent was computed at r = 9. The only r = 9 number in this file is the trivial
analytic bound 9m. Smoke runs were made at r = 10.5, 12, 14 and 20 only (section 8). No repository was written, nothing
was posted, and scratchpad/refute155/ was not read.

**Sources read in full.** `umeno/G1A_v1.txt` (preprint, 12 October 2026, 30 pp.), `umeno/G1A_v2.txt` (Version 2,
20 October 2026, 42 pp., DOI 10.5281/zenodo.23313815), `umeno/G1B.txt` (one, two and three cubes, 25 October 2026,
17 pp.). `G1D.txt` (single-cube multiplets) is outside this task and was not read beyond its abstract. Pointers below
are `v1 pP LNNN`, `v2 pP LNNN`, `G1B pP LNNN`: printed page number and line number in those text files.

S3 sources: #134 `docs/FINITE_S3_FIRST_GAP_AND_TERNARY_SCHUR.md`; #146
`independent/NOTE-UNCONDITIONAL-3X4-S3-FIRST-GAP-20261108.md`; #136 `independent/FINITE_S3_3X4_R9_FIRST_GAP_20261108.md`;
#131 `native/ym/results/3x4_stream/perron/PERRON-BOUND.md` (all on origin/main 6a7fc74); #143
`independent/FINITE_3X4_S3_FIRST_GAP_LARGE_R_20261108.md`; #155 branch pr155 (`independent/y137_k3_sector_isolation.py`
header only); the cloud seat's #137 design `ym137/final/NOTE-R9-WILSON-FESHBACH-AMPLITUDE-20261109.md`, and the
structure of `ym137/engine/rs/src/main.rs` and `ym137/scout/`.

---

## 0. Summary

1. **The two problems are dual (DERIVED).** Umeno works in the electric (spin-network) basis, where the electric
   operator is diagonal and the Wilson term is a bounded hopping with `0 <= V <= 18`. We work in the magnetic
   (configuration) basis, where `rM` is diagonal and the electric part `L = 72 - T` is a bounded hopping with
   `0 <= L <= 144`. Every basis-free step (the complete-output Gram identity, Schur inertia with a floor, response
   witnesses, the local cluster bound of G1B) carries over with the roles swapped. The dictionary is in section 1.
2. **The S3 work already has** the dual of Theorem 2.1 (#134: gap(E) = 3g), Proposition 2.2 (#134 Harnack, #146
   ground transform), Theorem 4.1 at m = 3 (#143: QHQ >= 3r), Lemma 4.2 (#136, #155 and the #137 design keep every
   one-step exterior target), Theorem 5.1 with a floor (#136, #155, #137 with P = the flats and the #131 floor on Q),
   and v2's response witnesses (6.32) and (C.4) (the residual identity of #136 and Lemma 2 of the #137 design).
   **It does not have** a floor that is itself built in Umeno's way: #131's 94.070673 is a Collatz-Wielandt bound on a
   numerically solved vector over the whole 45,508,080-row sector, plus a lift.
3. **Analytic floors for every omitted state in our basis (section 3):** (A) the dual of Theorem 4.1,
   `QHQ >= r m` on `{M >= m}`, which is 9m at r = 9; (B) the dual of Lemma 6.1, `M >= 3` on Q (#143); (C) the dual of
   G1B section 4, `H >= C(theta) + theta r M` on the full kinematic space, with C(theta) from exact single-plaquette
   (6-dim) or domino (36-dim) cluster problems; (D) v2's lower positive completion (6.27), dual form
   `Q L Q >= C A^-1 C*`. (A) and (C) are cheap and exact. MEASURED at excluded r: (C) raises the tail floor a lot
   (domino, m = 6: 96.63 at r = 10.5 and 105.63 at r = 12, against 63 and 72 for (A)). On all of Q (m = 3), (C) with
   dominoes is at most 77.52 at r = 10.5. That bound is rigorous and the floor is nondecreasing in r, so dominoes
   alone cannot certify 80 at r = 9 (DERIVED). (C) is a tail floor, not a standalone floor.
4. **The transfer that gives gamma (section 5, DERIVED):** take the core = nonflat orbits with `M < m0` in the **full**
   orbit space, the tail floor from (A) or (C) resolved layer by layer as in G1B's L1(t), and Theorem 5.1 with k = 0.
   In our basis the test matrix
   `F(t) = W(H_CC - t) - sum_eta J_eta / (d_eta - t)` is a **symmetric Z-matrix**, so a single positive vector v with
   `F(t) v >= 0`, checked in one exact integer pass (#131's Collatz-Wielandt machinery), certifies
   `lambda_min(QHQ_whole) >= t`. That bound is lift-free, needs no LDL of a large matrix, and its tail enters only
   through the analytic floor. Umeno needs exact inertia on 9 to 1205 dimensions because spin-network hopping has no
   sign structure. Our stoquastic basis replaces that with a positive-vector check, which scales to millions.
5. **Exact census (MEASURED, r-independent, new).** The orbit counts by M follow in closed form from Frobenius' formula on
   the torus and Burnside over the global conjugation (section 7). The nonflat core `M <= 11` has 1,608,786 orbits, and
   `M <= 13` has 4,123,551. Both are smaller than #131's 45.5M-row sector store. The counts give a completeness gate,
   the analogue of G1B's dynamic-program count (7).
6. **Side result (DERIVED, review needed): the sector-to-whole step for lambda_min needs no pointwise lift.** QHQ is
   stoquastic and commutes with the 48 lattice maps. A nonnegative ground vector, averaged over the group, gives a
   nonnegative invariant ground vector, so `lambda_min(QHQ_whole) = lambda_min(QHQ_sector)`. This is Umeno's
   positivity-implies-invariance argument (v1 p5 L250-254; G1B p7 L328-334), moved from the gauge group to the
   lattice symmetries (section 6).
7. **Electric-basis-only ideas (section 4):** the cycle formula of Theorem 2.1 used as a floor; the Casimir growth law
   behind Theorem 4.1 and the O(N^-2) decay of Theorems 4.5-4.6 (our M is bounded by 36, so no rate exists); the proof
   of Lemma 6.1; Proposition 6.4; the center sectors; the Haar, Fierz and epsilon machinery; the device V^2 <= 18V in
   (6.31); and the whole SC representation (Section 3).

---

## 1. Dictionary (DERIVED)

| Umeno, electric basis (G1A, G1B) | Ours, magnetic basis (3x4 S3) |
|---|---|
| basis: spin networks, all intertwiners kept (v1 p8 L433-438) | basis: gauge orbits of link configurations, weights W |
| diagonal part: `H_E = sum eps_e C2,e`, unbounded Casimirs | diagonal part: `r M`, `0 <= M <= 36` (M in {0,3,4,6,...,34,36}) |
| bounded hopping: `M_v`, `0 <= v <= 9 sum beta_p` (v1 p5 L205-219) | bounded hopping: `L = 72 - T = sum_e (3 - sum_tau R_tau)`, `0 <= L <= 144` |
| sign structure: none in general | stoquastic: every off-diagonal <= 0 (#134 step 2, #146 step 2) |
| complete cutoff P_N (edge heights <= N), or strict window `1[0,E)(T)` (G1B p4 L151-156) | strict magnetic window `1[M < m0]`; the flats are the window `M < 1` (or `M < 3`) |
| complement floor from Casimir growth plus V >= 0 (Theorem 4.1) | complement floor from M >= m0 plus L >= 0 (section 3A) |
| one Wilson multiplication changes each edge height by at most r = 1 (v1 p10 L566-574) | one link move changes M by at most 6 and changes only the 2 plaquettes on that link |
| one-step output space E_N, finite, built by Haar integration (v1 p8 L439-458) | the 72 moves of each core orbit, with integer counts and weights |
| finite tests: exact inertia (leading minors, LDL) at 9, 35, 105, 1205 dims | finite test: positive-vector certificate of a Z-matrix (CW) at any size; exact inertia only on small Feshbach blocks (7x7, 8x8) |
| natural regime: weak magnetic coupling (beta = 1/2) | natural regime: strong magnetic coupling (r = 9) |

---

## 2. Ingredient map

For each item: Umeno's statement (paraphrased; pointer to both versions), the S3 counterpart, whether the S3 work
has it, and how it transfers.

### 2.1 Theorem 2.1, finite-model operator and electric gap (v1 p5 L227-265; v2 p5 L235-270)

*Statement.* H_kin is self-adjoint, nonnegative, with compact resolvent and a unique positive ground state, which is
gauge invariant. The physical electric gap is exactly `(4/3) min_C sum_{e in C} eps_e` over genuine simple cycles (2.7).
The proof: a nonconstant spin-network support has no degree-one vertex, so it contains a cycle; every nontrivial
SU(3) irrep has Casimir >= 4/3; a fundamental Wilson loop on a shortest cycle attains the bound.

*S3 counterpart.* #134 step 1: the one-link electric class sum has eigenvalues 0, 3, 6 (trivial, standard, sign).
Supports contain a cycle, so `gap(E) = 3g`, with g = 3 the girth on 3x4. #146 uses the raw (ungauged) electric gap 3,
with characteristic polynomial `z(z-3)^4(z-6)`. Uniqueness and positivity: #134 step 2 and #146 step 2 (Perron-Frobenius).

*Has it:* YES (REPORTED).

*Transfer to the floor:* none as a floor. In our basis it says `L >= 3g (1 - Pi_const)`, and Q contains almost all of
the constant function (only 18 of 6^13 units of weight are flat), so it adds essentially nothing on Q. The *positivity
part* of the proof (unique positive ground state, hence invariant) does transfer, and gives section 6.

### 2.2 Proposition 2.2, ground-state comparison (v1 p6 L281-302; v2 p6 L286-308)

*Statement.* `gamma >= delta_E e^{-2tW} (m_t/M_t)^2 > 0` for every t > 0 (2.9). It comes from the ground-state
transform, the Poincare inequality for delta_E, and Feynman-Kac bounds on the positive vacuum. Umeno calls it a
finite-graph positivity statement with no regulator-uniform scale.

*S3 counterpart.* #134 steps 3-5: diameter <= 2k, Harnack `max psi / min psi <= B^D`, and the bound
`E2 - E1 >= 3 g J_E / B^(2D)` (9/396^52 at r = 9 and J_E = 1). #146: raw diameter 48, `g_max/g_min <= 396^48`, and
`(E2 - E1)/J_E >= 3/396^96`.

*Has it:* YES (REPORTED), in a discrete Harnack form that is stronger than Umeno's heat-kernel form.

*Transfer to the floor:* none useful; it bounds a gap and is astronomically weak.

### 2.3 Theorem 4.1, complete-cutoff estimate (v1 p9 L463-502; v2 p10-11 L558-600)

*Statement.* `Q_N H_E Q_N >= d_N Q_N` with `d_N = eps_min ((N+1)^2/4 + N + 1)` (4.3). Every omitted spin network has an
edge of height >= N+1, whatever its intertwiner multiplicity. It gives the resolvent bound (4.4) and monotone Ritz
convergence `mu_k,N` decreasing to `E_k`.

*S3 counterpart.* The dual: P_m0 = `1[M < m0]` commutes with M, and L >= 0 compresses to L >= 0. Hence
`Q_m0 H Q_m0 >= r m0` (section 3A). #143 uses the case m0 = 3 on Q: `QHQ/J_E >= d = 3r` (#143, "Control of EVERY
nonflat state"). #131 uses the same fact with Weyl's inequality: the floor grows by 3(r - 9) for r >= 9.

*Has it:* YES at m0 = 3 (REPORTED). The window version m0 > 3 is not used anywhere (DERIVED here).

*Transfer:* direct, and it is the trivial tail floor of section 5. **What does not transfer** is the growth law
`d_N ~ N^2/4`: our M is bounded by 36, and in the regime that matters the floor 9 m0 grows only linearly.

### 2.4 Lemma 4.2, complete-output Gram identity (v1 p11 L587-609; v2 p12 L679-701)

*Statement.* `K_out* K_out = A^2 + B*B` (4.11), and in non-orthonormal coordinates `R_f = X* G_out X - A_f G^-1 A_f`
(4.12). Remarks (v1 p11 L603-609): terms with the same output must be added before the Gram product, the output space
is fixed before coefficients are specialised, and no finite output space replaces the whole complement in the lower
bound.

*S3 counterpart.* #136: 147,344 exterior targets one move outside the 8,042-state trial space, each kept with its
weighted coefficient; `G = 6 R^T W_Q^-1 R`. #155: the K3 ball's exterior is shell 4 (1,985,218 orbits), and "the
exterior list holds every orbit one electric move outside it". The #137 design: exterior shell 6 with 2,465,466
classes, "accumulated by class", plus GPT-6's required complete-exterior gate (CONTEXT, audit item 4).

*Has it:* YES (REPORTED).

*Transfer:* direct, and simpler in our basis. The retained set is a union of orbits, so orthogonal projection is a
coordinate restriction, and the boundary Gram is `(B*B)_ij = w_i sum_{k in tail} c_ik c_kj` (counts of two-step
paths through the tail; DERIVED from detailed balance `w_i c_ik = w_k c_ki`). No `M - S G^-1 S` subtraction is needed.

### 2.5 Lemma 4.3 and Theorem 4.4, excess-edge sectors and local overlap (v1 p11-12 L611-668; v2 p13 L710-759)

*Statement.* The commuting projections `Q_J,N` (exactly the edges in J exceed the cutoff) are orthogonal and sum to
Q_N. A term supported on S_alpha reaches only `J ⊂ S_alpha` (4.14). Hence
`B_N* B_N <= sum_J d_J sum_{alpha: J ⊂ S_alpha} P V_alpha Q_J V_alpha P <= d_loc sum_alpha B_alpha* B_alpha` (4.15).
Cross terms are bounded, not dropped.

*S3 counterpart.* The dual locality: a move on link e changes only the classes of the two plaquettes containing e, so
the output's excited-plaquette class vector differs from the input's only on those two plaquettes. The S3 work never
needs (4.15), because it computes B*B exactly, cross terms included.

*Has it:* not as a theorem; not needed (REPORTED/DERIVED).

*Transfer:* available as an analytic shortcut (a d_loc-type bound with d_loc = 4 links per plaquette) when one wants
to bound B*B without listing the tail. The exact sparse computation is cheaper here.

### 2.6 Theorem 4.5, electric-energy-relative boundary bound (v1 p12-13 L670-727; v2 p13-14 L761-822)

*Statement.* `B_N* B_N <= kappa_N P_N H_E P_N` with
`kappa_N = d_loc / c(N - r + 1) * max_e sum_{alpha: e in S_alpha} b_alpha^2 / eps_e` (4.18)-(4.19), and kappa_N = O(N^-2).
Only input shells of height >= N - r + 1 can leave the cutoff (4.21)-(4.22).

*S3 counterpart.* The dual input-shell fact holds: only core orbits with `M >= m0 - 6` have moves leaving `{M < m0}`.
So `B = B U` with U the projector onto `{m0 - 6 <= M < m0}`, and `B*B <= ||B||^2 U`. With the Schur test, a relative
diagonal bound is `B*B <= W diag(out_i) * max_k in_k` (out_i = moves from i into the tail, in_k <= 72; DERIVED).

*Has it:* NO, and not needed (DERIVED).

*Transfer:* only the shell-localisation idea. The **O(N^-2) decay does not transfer**: it needs unbounded Casimir
growth against a bounded Wilson term. In our basis the bounded part is L, and the boundary coupling per state stays O(1).

### 2.7 Theorem 4.6, volume-uniform resolvent bound (v1 p13 L729-771; v2 p14-15 L824-874)

*Statement.* If `D_N >= delta_N`, (4.19) holds and `delta_N + zeta > kappa_N`, then
`||(H + zeta)^-1 - (A_N + zeta)^-1 P_N|| <= (1 + kappa_N/(4 zeta)) / (delta_N + zeta - kappa_N)` (4.24), through the
complementary Schur operator `S_Q >= delta_N + zeta - kappa_N` (4.26) and the identity (4.27). Uncentred, before vacuum
subtraction, and not an infrared gap bound.

*S3 counterpart.* #143's all-states resolvent identities (`R - R0 = -delta R R0`, the eta(r) bound with
`||B||^2 = 72`) are the same kind of norm-resolvent control, but for the flat block at large r.

*Has it:* the spirit of it, at r >= 10000 only (REPORTED).

*Transfer to the floor:* none needed. A floor is a lower bound, not a resolvent-norm statement.

### 2.8 Theorem 5.1, Schur inertia with a floor (v1 p14 L777-812, App. C p28 L1625-1663; v2 p15-16 L877-924, App. E p39-40 L2300-2344)

*Statement.* If `D >= d` and `t < d`, put `F_d(t) = A - tI - B*B/(d - t)` (5.3). Then `n_-(F_d(t)) <= k` implies
`E_k(H) >= t` (5.4), through the exact count `#{E_j < t} = n_-(A - t - B*(D - t)^-1 B)` (5.5). In a non-orthonormal
basis: `F_f(t) = A_f - tG - C_f/(d - t)` (5.6). Umeno notes (v1 p14 L810-812) that the generic d_N always holds and a
graph-specific improvement "must be proved for the entire complementary space".

*S3 counterpart.* #136: P = 8 flats, Q = all nonflats, floor `gamma = b (94.070673 - z)` from #131, trial
`X_int` on two shells, and `n_-(UPPER) <= N_full(z) <= n_-(LOWER)` with `LOWER = 6 gamma_num U - 10^6 G`. #155 does the
same with the K3 ball and reflection sectors. The #137 design (Lemmas 1-2, Corollary 3, Theorem I) does it in the
48-symmetry sectors at depth 5.

*Has it:* YES, with P = flats and the floor supplied by #131 (REPORTED).

*Transfer for the floor lane:* apply the theorem **one level down, inside Q**: retained = the nonflat magnetic window
`{3 <= M < m0}`, complement = `{M >= m0}`, d from section 3. Here k = 0, so the test is `F(t) >= 0`, and in our basis
F(t) is a Z-matrix (section 5). This is the step the S3 work lacks.

### 2.9 The relative estimate (5.7) (v1 p14 L820-830; v2 p16 L925-935)

*Statement.* If `B_N* B_N <= kappa_N P_N H_E P_N` and `t < d`, then
`F_rel(t) = A - tI - (kappa_N/(d - t)) P_N H_E P_N` is a valid lower test. The exact (5.3) is at least as sharp, so
(5.7) is only a cheaper alternative when the exact Gram is expensive.

*S3 counterpart.* None.

*Has it:* NO.

*Transfer:* with any relative bound `B*B <= K_rel` (for example the diagonal out-degree bound of 2.6),
`F_rel(t) = W(H_CC - t) - K_rel/(d - t)` is still a Z-matrix, so the CW certificate applies. It removes the two-step
pass over the tail at some cost in sharpness. Low priority, because the exact B*B is cheap here.

### 2.10 Proposition 5.2, scalar sufficient bound (v1 p15 L836-865; v2 p16-17 L937-969)

*Statement.* With `L(d,a,b) = (a + d - sqrt((d - a)^2 + 4b^2))/2` (5.8) and `||B_N|| <= b_N`, one gets
`gamma >= L(d_N, mu_1,N, b_N) - mu_0,N` (5.9), and `b_N <= W/2` by centring V. This is an eventual-success statement
for each fixed model.

*S3 counterpart.* #143's eta(r) uses the same norm-Schur reasoning with `||B||^2 = 72`.

*Has it:* the spirit of it, at large r (REPORTED).

*Transfer:* for the floor, `lambda_min(QHQ) >= L(r m0, a, b)` with a a lower bound on the core's lowest eigenvalue and
b = ||B||. Centring L gives `b <= 72`, the Schur test gives `b <= sqrt(max out * max in) <= 72`, and the result is
roughly `a - b^2/(r m0 - a)`. It is weak unless r m0 is large. Not recommended.

### 2.11 Lemma 6.1, graph-specific complementary floor (v1 p17-18 L1040-1065; v2 p19 L1144-1163)

*Statement.* For the two-plaquette graph, `Q T Q >= 11 Q` and `Q H(beta) Q >= 11 Q` on the whole omitted space (6.14),
against the generic d_1 = 3. The proof is a case analysis over Casimirs and singlet conditions at the trivalent
vertices, and (3, 3-bar, 8) attains 11. Then 12 - s >= 0 keeps the bound. The improvement "uses the actual graph and
Gauss constraints and is independent of the finite output-space dimension".

*S3 counterpart.* #143: on Q, M >= 3. Transposition plaquettes come in pairs by the sign homomorphism, and one 3-cycle
costs 3. That is the graph-specific improvement over the generic minimum nonzero cost 2. #131's 94.070673 is a far
stronger graph-specific floor, but it is numerical and conditional.

*Has it:* YES at the level M >= 3 (REPORTED).

*Transfer:* the next graph-specific analytic floors in our basis are section 3C (local clusters, the G1B section 4
method) and 3D (positive completion). The case-analysis proof of Lemma 6.1 itself is electric-only.

### 2.12 Version 2 additions

* **Proposition 6.4, complete electric core** (v2 p22-23 L1325-1364). The 35-dim one-step output space equals
  `Ran 1[0,18)(T)`, with `Q_Pi T Q_Pi >= 18`. A coincidence of the electric spectrum. Dual: NO. The shell-1 states
  (264, all M = 4) are not the whole `M = 4` window (1,320 orbits, section 7). The *idea* of retaining the core plus its
  one-step outputs (v2 p22 L1322-1323) transfers. It moves the floor approximation one layer out and keeps the
  Z-structure.
* **(6.27)-(6.30), positive-potential completions** (v2 p23-24 L1366-1425). From `0 <= V <= 18`:
  `C A^-1 C* <= Q_Pi V Q_Pi <= 18 - C(18 - A)^-1 C*`, with lower and upper completions H_- and H_+ (6.30). Dual
  (DERIVED): with `0 <= L <= 144`, `A = Pi L Pi` (positive definite on a proper core) and `C = Q L Pi = -T_TC`,
  `Q L Q >= C A^-1 C*` on the tail, a valid floor for every omitted state. The cost is the inverse of the core's electric
  compression. OPEN, low priority.
* **(6.31)-(6.33), actual magnetic-tail information and response witnesses** (v2 p24-25 L1427-1487).
  `B*(D - t)^-1 B <= U_X(t) = (beta^2 R_Pi - G*X - X*G + X* K X)/(d - t)` with
  `K = M2 - (d + t) M1 + d t M0`. Here M2 is bounded by `V^2 <= 18 V` without degree-8 moments. The S3 counterpart is
  #136's U, R, G construction and Lemma 2 of the #137 design (REPORTED), so the S3 work HAS it for P = flats. In our
  basis M2 = (DY)*(DY) is exact (two-step outputs), so the device `V^2 <= 18 V` (dual `L^2 <= 144 L`) is not needed.
  **Caution (DERIVED):** inside the floor lane's core, a response X breaks the Z-sign structure of F(t). Then only exact
  inertia works, which is infeasible at a million rows. Enlarge the retained window instead.
* **Proposition 6.6, extremal finite-information envelopes** (v2 p26 L1546-1576). Given only the finite blocks and
  `0 <= V <= 18`, both completions are attained, so those envelopes are sharp. Dual moral: with only the core and the
  floor `L >= 0`, the trivial tail floor cannot be beaten. Better floors need tail information: 3C, 3D, or a larger window.
* **Proposition C.1 and Appendix C** (v2 p34-37 L2002-2183). Optimised response `U_Y(t)` (C.4), nested monotone,
  electric-layer comparator U_E (C.2), direct physical columns (C.10). The S3 shells play the role of Y (REPORTED).
  The layer comparator (C.2) is exactly the G1B L1 idea below.
* **(6.37), vacuum control** (v2 p27 L1582-1594). `1 - |<Omega, w>|^2 <= (u - l0)/(l1 - l0)`. Basis-free. Relevant to
  #137's amplitude lane, not to the floor.
* **(6.33) and (6.36), affine coupling tests**: Bernstein coefficients over coupling intervals. Basis-free. For the
  floor, monotonicity in r already holds (M >= 0), and #131 adds 3(r - 9).

### 2.13 G1B (one, two and three cubes)

* **Theorem 3.1, complete-window eigenvalue count** (G1B p6 L234-263). If `K >= C + theta T` (form order),
  `d = C + theta E` and `t < d`, then `L0(t) = H - tG - R/(d - t)` (13) and the layered
  `L1(t) = H - tG - sum_{eta >= E} J_eta/(C + theta eta - t)` (14), with `J_eta = <1{eta}(T) B f_i, 1{eta}(T) B f_j>` (12),
  satisfy `L0 <= L1 <= S(t) <= H - tG` (17). Dual (DERIVED): `H >= C + theta r M`, the window `M < m0`, and the layers
  `eta = M` of the one-step outputs (`m0 <= eta <= m0 + 5`). The S3 work has the L0 form only, at P = flats.
* **Corollary 3.2, two-sided gap enclosure** (G1B p6 L265-284). Ritz and trial vectors outside the window are allowed.
  The S3 counterpart is UP being floor-free (#137 design, Remark 4.4).
* **Section 4, local lower bounds on the full kinematic space** (G1B p7 L290-334, Table 2 p7 L337-342). Clusters
  (single plaquettes, shared-edge pairs) cover each plaquette once, the electric operator is distributed with exact
  edge sums `1 - theta`, and a fraction theta is reserved (22)-(23). The key justification: the local operator is
  elliptic and has a unique positive lowest eigenfunction, so it is gauge invariant, "Hence the lowest value in the
  neutral local sector equals the unrestricted lowest value" (G1B p7 L332-333). That allows the overlapping cluster
  inequalities to be added. S3 counterpart: none. Transfer: section 3C (DERIVED, smoke-tested).
* **Section 6, window ceiling and Theorem 6.1** (G1B p9-11 L416-577). Any certificate `Delta > t - u` needs
  `t < C + theta E` (25), so `E > (u - C)/theta` is necessary (26). Theorem 6.1 shows that complete absolute windows
  grow exponentially in volume. Dual: the floor lane needs `t < d(m0)`. At fixed 3x4 volume the window stays at a few
  million orbits (section 7), so the obstruction does not bite here. It would bite on larger lattices.
* **Section 7.2, symmetry and Appendix B** (G1B p13 L685-693). Window labels need sector-resolved two-sided enclosures
  before they can be assigned to untruncated states. The same caution applies to GPT-6's conditional lemma that E2 is
  in the trivial representation (CONTEXT, audit item 2).
* **Section 8, coupling interval** (G1B p13-14 L696-737). Min-max monotonicity and a fixed trial vector. Dual: the
  monotonicity in r of #131.

---

## 3. Analytic floors for every omitted state in OUR magnetic basis

Notation: tail `T_m = {orbits with M >= m}` (all of them are nonflat for m >= 1), and D = the compression of H to `T_m`.

**A. Dual of Theorem 4.1 (DERIVED).** `L = sum_e (3 - sum_tau R_tau) >= 0` (each link term has eigenvalues 0, 3, 6), and
M commutes with the window projector, so `D >= r m`. At r = 9 this is **9m**: 27 on all of Q (m = 3), 99 at m = 11,
108 at m = 12, 126 at m = 14. It needs nothing but M on the tail, and is valid on every omitted orbit.

**B. Dual of Lemma 6.1 (REPORTED, #143).** Q has no orbit with M in {1, 2, 5}, so `Q = T_3` and floor A applies with
m = 3. (The census of section 7 confirms the zero counts at M = 1, 2, 5 and 35.)

**C. Dual of G1B section 4: local clusters (DERIVED).** Write
`H = sum_c h_c(theta) + theta r M`, where each cluster operator h_c(theta) carries part of L (the edge weights add up to
the full L) and `(1 - theta) r` times the cost of its plaquettes. Every h_c is stoquastic, irreducible (transpositions
generate S3) and commutes with its local gauge group, so its lowest eigenvalue on the full kinematic space equals the
lowest eigenvalue of its reduced holonomy operator (G1B's positivity argument). Hence `H >= C(theta) + theta r M` on the
whole space, and `D >= C(theta) + theta r m` on `T_m`, for every theta in [0, 1].

* Single plaquettes (12 clusters; each link at weight 1/2, since every link of the 3x4 torus borders two distinct
  plaquettes): on L2(S3), `h = 6 - 2A + r'(2 - chi_std)` with `(Af)(g) = sum_tau f(tau g)` and `r' = (1 - theta) r`
  (6x6 integer matrix; on class functions it is the 3x3 form `[[6,-6,0],[-6,18+6r',-12],[0,-12,12+6r']]`, Gram
  diag(1,3,2)).
* Vertical dominoes (6 clusters `(x,0)+(x,1)` and `(x,2)+(x,3)`; shared link weight 1, the 6 outer links weight 1/2):
  on L2(S3^2), `h = 12 - (3/2)(A_X + A_Y) - S + r'(cost X + cost Y)` with `(Sf)(X,Y) = sum_tau f(X tau, Y tau)`
  (36x36 integer matrix). The electric diagonal adds up to 6 x 12 = 72.
* MEASURED (excluded r, section 8): domino tail floors at m = 6 are 96.63 (r = 10.5), 105.63 (12), 117.62 (14) and
  153.63 (20), against 63, 72, 84 and 120 for floor A. At m = 3 (all of Q) the domino floor is 77.43 at r = 10.5, with
  a rigorous upper bound of 77.52 (concavity in theta plus a slope bound). At r = 12 it is 81.93.
* DERIVED: the floor is nondecreasing in r (each cluster's lowest eigenvalue is nondecreasing in r', and theta r m
  increases). So the domino-only floor on all of Q is <= 77.52 at r = 9, and **cannot by itself give gamma >= 80**.
  Its use is as a tail floor in section 5, where it lets the window be smaller. Larger clusters (3x1 rings, 251 reduced
  orbits each; 2x2 blocks do not tile 3x4) are OPEN.
* Ceiling (DERIVED): with exact clusters as large as the lattice, the method's best possible all-Q value is
  `max_theta [E0((1 - theta) r) + 3 theta r]`. Its value at r = 9 is not evaluated here (r-dependent).

**D. Dual of v2 (6.27), lower positive completion (DERIVED).** `Q L Q >= C A^-1 C*` on the tail, with `A = Pi L Pi` on
the core and `C = -T_TC`. Valid on every omitted orbit, and strongest on the tail layer adjacent to the core. It needs
the core's electric inverse (an M-matrix, so its inverse is entrywise nonnegative). OPEN.

**Not analytic floors in our basis:** Proposition 2.2 (gap-type, astronomically weak), Proposition 5.2 (needs
||B|| <= 72; weak), Theorem 2.1 (electric gap; no effect on Q).

---

## 4. Ideas that work only in an electric (spin-network) basis

1. **Theorem 2.1's cycle formula as a floor tool.** It is a statement about the spectrum of the diagonal electric
   operator. In our basis L is off-diagonal, and the bound is invisible on Q.
2. **The growth law of Theorem 4.1** (`d_N ~ N^2/4`, from Casimir growth (4.5)) and the **O(N^-2) decay of
   Theorems 4.5-4.6** (kappa_N ~ 1/c(N - r + 1)). Both need an unbounded diagonal against a bounded hopping that
   changes heights by +-r. Our diagonal M is bounded by 36 and the hopping L is bounded by 144. The dual floor exists
   (3A) but improves only linearly, and the coupling per boundary state does not decay.
3. **Excess-edge sectors (4.13) as defined**: edge-height projectors p_{e,N} that commute with the Gauss projection.
   The dual (plaquette-class locality, ΔM <= 6) holds, but the sectors are not needed, because B*B is computed exactly.
4. **The proof of Lemma 6.1** (Casimir >= 3 outside 1, 3, 3-bar; singlets at the trivalent vertices). Our analogue,
   M >= 3, has a different (sign-parity) proof.
5. **Proposition 6.4** (the output space equals an electric spectral window), **the center-sector closure P_ab**
   (v2 p23-24 L1390-1407: S3 has trivial center), the **Haar, epsilon and Fierz calculus** (App. A, v2 App. B; our
   matrix elements are integer move counts), and the **device `V^2 <= 18 V` in (6.31)** (we have exact two-step outputs).
6. **Section 3, the SC representation** (Theorem 3.1, Corollary 3.2, Propositions 3.2-3.4, the Cuntz corner, depth
   tails): it transports an already proved gap and gives no floor in either basis.

Everything else used here (Lemma 4.2, Theorem 5.1 with (5.5)-(5.6), (5.7), the response witnesses, (6.37), G1B
Theorem 3.1 and section 4) is basis-free algebra.

---

## 5. The transfer that gives gamma (DERIVED; design input for the floor lane, not a run)

**Theorem F (Schur-CW floor).** Let Cr = nonflat orbits with M < m0 (full orbit space), with tail `T_m0`. Fix theta and a
tail floor `d_eta = C(theta) + theta r eta` (or `d_eta = r eta`, theta = 1, C = 0) with `t < d_m0`. For core orbits i, j put

    F(t)_ij = w_i [ (72 + r M_i - c_ii - t) delta_ij - c_ij (1 - delta_ij) ]  -  w_i sum_{k in T_m0} c_ik c_kj / (d_{M_k} - t),

where c_ik is the number of (link, transposition) moves from i to k, and c_ii counts the moves that return to i. If some v > 0
on Cr has `(F(t) v)_i >= 0` for every i, then `lambda_min(QHQ_whole) >= t`.

*Proof.* (1) `D >= d(M)` in form order (3A or 3C), and M commutes with the tail, so `(D - t)^-1 <= diag(1/(d_{M_k} - t))`.
Hence the exact Schur complement is >= F(t) (Theorem 5.1 / G1B (16)-(17)). (2) Detailed balance gives
`B^T W_T^-1 diag(...) B = w_i sum_k c_ik c_kj/(d - t)` with nonnegative entries, so F(t) is a symmetric Z-matrix.
(3) For a symmetric Z-matrix `F = sI - N` with N >= 0, `F v >= 0` with v > 0 gives `rho(N) <= s` (Collatz-Wielandt), so
F >= 0. (4) With n_-(F) = 0 and `D - t > 0`, the Haynsworth count gives no eigenvalue of QHQ below t. QED.

*Gates that transfer from the S3 work and the papers:* the census completeness gate (per-M orbit counts of Cr equal
section 7; G1B's "membership, independence, and equality with (7) prove completeness", G1B p5 L203-205); the complete
one-step exterior with multiplicities and a hash (Lemma 4.2; GPT-6 audit item 4); detailed balance on every edge (#131
allpairs, #137 H1); the Z-sign gate (every off-diagonal of F(t) <= 0, every `d_eta - t > 0`); and the ceiling
`t < d_m0` (G1B (25)). A cross-check is available from the floor-free Ritz side (#131's two-sided bracket
`lambda_1(H') <= 94.070936`).

*Sizes (MEASURED, section 7):* the nonflat core M <= 9 has 111,906 orbits, M <= 11 has 1,608,786, and M <= 13 has
4,123,551 (in the full orbit space, lift-free). Its one-step outputs lie in `m0 <= M <= m0 + 5`. In the 48-symmetry
sector the sizes are about 48 times smaller (CONJECTURE), with section 6 replacing the lift. The trivial floor 9m0 needs
m0 >= 12 for a comfortable margin at targets near 94 (9 x 11 = 99 leaves under 5). Floor 3C allows a smaller m0.

*Reuse of the cloud seat's engine (structure read, not run):* `ym137/engine/rs/src/main.rs` has the S3 tables, the
canonical keys for the "sym", "odd" and "full" (nsym = 1) sectors, move lists with counts, 256-bit accumulators,
exterior aggregation by class with exact division by W_e, and integer Gauss-Seidel. A magnetic-window generator is
needed: the engine builds electric shells from the flats. Whether the sublevel sets `{M < m0}` are connected under moves
is OPEN, so a BFS restricted to the window must be checked against the census.

---

## 6. Sector-to-whole for lambda_min without a pointwise lift (DERIVED; review needed)

H' = QHQ on the whole nonflat space, in the W-symmetrised form, is `sI - N_sym` with N_sym >= 0 entrywise. The 48 lattice
maps act by weight-preserving permutations P_g that commute with N_sym (H2 of the #137 design; they map flats to flats).
Perron-Frobenius for nonnegative symmetric matrices (reducible or not) gives a nonnegative eigenvector u for rho(N_sym).
The average `sum_g P_g u` is nonnegative, nonzero and invariant, and it is an eigenvector for the same rho. So
`lambda_min(H'_whole) = lambda_min(H' on invariant functions) = lambda_min(h'_KL)`, the nonflat sector matrix in the
class basis. Therefore any lower bound on the sector matrix (#131's CW on its rows, rebuilt by #152) is a lower bound
on the whole nonflat space, including the non-trivial sectors V_rest that the #137 design's H4 needs. This is
Umeno's positivity-implies-invariance step (v1 p5 L250-254; G1B p7 L328-334), moved from the gauge group to the
lattice symmetries. It does not use the vector d or the pointwise identity of PERRON-BOUND section 2. It still needs
the sector rows to represent H' on invariant functions, which is what the row rebuild checks. I did not find this
argument in the documents I read.

---

## 7. Census by magnetic cost (MEASURED, r-independent, new)

Gauge-fixed configurations (13 free elements) with plaquette classes C_p: by Frobenius on the torus (Euler
characteristic 0), with per-plaquette factors `(1 + 3x^2 + 2x^3)/6`, `(1 - 3x^2 + 2x^3)/6`, `(1 - x^3)/6` for the
trivial, sign and standard characters. Burnside over the global conjugation adds the Z2 and Z3 centraliser terms:

    orbits(x)   = (1+3x^2+2x^3)^12 + (1-3x^2+2x^3)^12 + 3(1-x^3)^12 + (1+x^2)^12 + (1-x^2)^12 + (1+2x^3)^12
    weighted(x) = 6 [ (1+3x^2+2x^3)^12 + (1-3x^2+2x^3)^12 + (1-x^3)^12 ]

Checks: total 2,177,317,873 (#146's Burnside count), total weight 6^13, 8 flat orbits of total weight 18 (#131), 36
orbits at M = 3 (#131: 3 sector rows at M = 3), and zero counts at M = 1, 2, 5, 35. Script `scripts/mhist.py`, sha256
a0777988f6cc3731; full table in `mhist.txt`.

| M | orbits | cumulative orbits, M <= m (8 flats included) | cumulative weight |
|---:|---:|---:|---:|
| 0 | 8 | 8 | 18 |
| 3 | 36 | 44 | 234 |
| 4 | 1,320 | 1,364 | 7,362 |
| 6 | 990 | 2,354 | 10,926 |
| 7 | 23,760 | 26,114 | 153,486 |
| 8 | 81,180 | 107,294 | 634,626 |
| 9 | 4,620 | 111,914 | 654,426 |
| 10 | 213,840 | 325,754 | 1,937,466 |
| 11 | 1,283,040 | 1,608,794 | 9,635,706 |
| 12 | 1,374,285 | 2,983,079 | 17,816,868 |
| 13 | 1,140,480 | 4,123,559 | 24,659,748 |
| 14 | 8,981,280 | 13,104,839 | 78,547,428 |

---

## 8. Smoke runs (MEASURED, excluded r only; for the pre-freeze disclosure)

| script | sha256 (16 hex) | r | output |
|---|---|---|---|
| `scripts/mhist.py` | a0777988f6cc3731 | none (r-independent) | `mhist.txt` |
| `scripts/cluster_smoke.py` | 0d1c119f38a2875a | 10.5, 12, 14, 20 | `cluster_smoke.txt` |
| `scripts/cluster_refine.py` | df9739e6b2d87120 | 10.5 | `cluster_refine.txt` |
| `scripts/sanity_r20.py` | 1d369bf8cd407b92 | 20 | `sanity_r20.txt` |

All are Python big ints only (`python3 -I -B`), with exact Bareiss leading minors and theta on a grid of 1/50 (1/2500 in
the refinement). Floors `C(theta) + theta r m` (lower values on the grid):

| r | cluster | m = 3 | m = 4 | m = 6 | m = 8 | m = 10 | trivial r m at m = 6 |
|---|---|---:|---:|---:|---:|---:|---:|
| 10.5 | plaquette | 73.73 | 79.57 | 92.83 | 107.49 | 123.11 | 63 |
| 10.5 | domino | 77.43 | 83.41 | 96.63 | 110.98 | 126.17 | 63 |
| 12 | plaquette | 78.23 | 85.58 | 101.82 | 119.49 | 138.10 | 72 |
| 12 | domino | 81.93 | 89.41 | 105.63 | 122.98 | 141.15 | 72 |
| 14 | domino | 87.93 | 97.41 | 117.62 | 138.98 | 161.15 | 84 |
| 20 | domino | 105.93 | 121.39 | 153.63 | 186.96 | 221.15 | 120 |

Refinement (r = 10.5, domino, m = 3): grid maximum 77.431170 at theta = 1355/2500, interior maximum confirmed, and a
rigorous upper bound of 77.513076. Sanity (r = 20, theta = 0): `12 c_plaq >= 68.391` and `6 c_dom >= 69.643`, both below
the ground energy near 72 - 18/20 - 4.5/400 ≈ 71.09 (REPORTED series), and both match the second-order estimates
72 - 72/r and 72 - 45/r. For comparison, the conditional #131 floor at these r is at least 94.07 + 3(r - 9): 98.57 at
r = 10.5 and 103.07 at r = 12.

---

## 9. OPEN and cautions

* OPEN: a magnetic-window generator and the connectivity of `{M < m0}`; larger clusters (3x1 rings); the completion 3D;
  every r = 9 value other than 9m. The floor lane must freeze its own prediction before its r = 9 run.
* Caution: response witnesses inside the core destroy the Z-structure (2.12). Enlarging the window keeps it.
* Caution: a single theta must be used for all tail layers. Two operator lower bounds do not imply their pointwise maximum.
* Caution: section 6 and Theorem F are new derivations from this lane and need an independent review before use.
* REPORTED status of the inputs: #131 stays conditional on its lift. Section 6 offers a second route that still needs
  the row rebuild (#152). The #137, #155 and #136 results stay conditional on #131.
