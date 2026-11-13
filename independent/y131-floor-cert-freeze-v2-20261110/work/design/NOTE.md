# NOTE: a Schur-Collatz-Wielandt floor for lambda_min(QHQ) on the periodic 3x4 S3 lattice (floor lane, DESIGN)

Written 2026-11-09 by the DESIGN lane of the floor workflow. Model: `H/J_E = 72 I - T + r M` on the 2,177,317,873
gauge orbits of the periodic 3x4 S3 lattice, inner product weighted by the orbit sizes w, T the electric move counts
(24 links x 3 transpositions = 72 moves per state), M = sum over the 12 plaquettes of `2 - chi_std` (costs 0, 2, 3 for
the classes e, t, c), flats P (M = 0, 8 orbits), Q = nonflat. Target: a rigorous lower bound gamma on `lambda_min(QHQ)`
at r = 9. No continuum, 4D, SU(N) or Clay claim.

Tags: MEASURED (r-independent counts, or excluded r only), DERIVED (proved here; review needed), REPORTED (another PR,
lane or paper), CONJECTURE, OPEN.

**Rule compliance.** Nothing r-dependent was computed at r = 9 by this lane: since FIX-1 both the Rust writer and the
Python verifiers accept only the excluded values r in {21/2, 12, 14} and r >= 20 (nothing within 1 of r = 9; r = 10 is
refused), and r = 9 itself only in a frozen mode that was never run (section 12). Every computation used r in
{21/2, 12, 14, 20}. The FIX-1 refusal tests called the programs with r = 10, 19/2, 90000001/10000000 and 8. Each call was
refused while parsing its arguments or the header, before any computation (`out/fix1/adhoc/`).
The only r = 9 numbers in this file are the trivial analytic bound 9m (as 9(m0 + 1)), the r-independent threshold test
"r_star < 9" of section 2.6, and labelled CONJECTURE extrapolations from the excluded points, which the task asked for.
Integers only (Rust 1.81, std only, i128 with overflow checks; Python big ints, `python3 -I -B`, no float, fractions,
decimal or math). No repository writes, no GitHub posts, scratchpad/refute155/ not read. Work is under
`scratchpad/floor/work/design/` only.

**Pre-freeze disclosure (carried from the critic, FIX-1).** While testing the old guard `r > 9`, the critic ran
`floorcert cert --m0 4 --r 90000001/10000000` once (73 classes, default f = 32,16,8,4,2,1, scratch directory since
deleted). It printed gamma = -0.0001 with tail cap 0 (trivial) and a crude 73-class Rayleigh value, which the critic
withheld; no file holds it. This critic-lane exposure belongs in the floor's frozen prediction. The FIX-1 whitelist
refuses that r before any computation (`out/fix1/smoke/selftest.txt`, and section 12).

---

## 0. Summary

1. **Certificate (DERIVED, Theorem S).** Core C = nonflat orbits with `M <= m0`, tail T = `M > m0`. On the tail, a
   positive function f(M) gives the operator floor `H_TT >= diag(delta)` with
   `delta_k = 72 + r M_k - sum_{moves k -> l, l in T} f(M_l)/f(M_k)` (ground-state substitution, Lemma 1). A local count
   over plaquette colourings bounds every `delta_k` from below by an r-affine layer floor (Lemma 2), so `t < cap` makes
   `H_TT - t` positive definite on all 2.17 billion tail orbits. The Schur complement is then bounded below by the
   Z-matrix
   `F(t)_ij = (72 + r M_i - t) delta_ij - c_ij - sum_{k in T} c_ik c_kj / (delta_k - t)` on the core, and one positive
   vector v with `F(t) v >= 0` row by row, checked in exact integers, proves `lambda_min(QHQ) >= t`.
2. **It improves the requested shape.** The requested single global vector (core vector plus a tail formula
   `c lambda^(m - m0)`) needs a matching condition between the core boundary values and the formula (section 3). Theorem
   S needs none: the tail enters only through an operator floor, the scale of f drops out, and moves from the tail back
   into the core are dropped from `delta_k`, which only raises it. With `f = 1` the tail floor is exactly the trivial
   `r M >= r (m0 + 1)` (the 9m bound at r = 9). Every positive f with `r_star(f) < 9` (an r-independent number) keeps the
   tail cap at r = 9 at least `9 (m0 + 1)` and adds an r-independent gain near the boundary.
3. **Lift-free (DERIVED).** The rows are checked on one representative per 48-symmetry class, but the vector is the
   class-constant vector on the full orbit space and every orbit's row equals its representative's row exactly (H, M, w
   and the tail floor commute with the 48 lattice maps). So the bound holds on the whole nonflat space, with no
   sector-to-whole lift.
4. **Census (MEASURED, r-independent, new for the classes).** Exact enumeration of every nonflat orbit with `M <= 18`
   (3,289,814 classes) reproduces the closed-form orbit and weight counts layer by layer (table in section 4).
5. **Smoke (MEASURED, excluded r).** The certified gamma is within 0.01 of the Rayleigh-Ritz upper bound by m0 = 11 or 12
   at every excluded r (r = 21/2: `99.3721 <= lambda_min(QHQ) <= 99.3765`; r = 12: `104.4512 <= lambda_min <= 104.4541`),
   and the smallest cores that beat the Weyl-shifted #131 value are 2,748 classes (r = 21/2) and 130 classes (r = 12)
   (section 5).
6. **Proposal for r = 9 (CONJECTURE, section 6).** m0 = 11 (34,920 classes) with f in {1, (8,7,6,5,4), (6,5,4,3)}, fallback
   m0 = 12 (65,025 classes). Both are cheap: rows 82 s / 174 MB and 143 s / 311 MB on one thread, plus 2-5 min per (r, f)
   for the vector and the bisection. Conjectured outcome: gamma(9) >= 93.5 at m0 = 11 and within about 0.1 of
   lambda_min(QHQ) at m0 = 12. The excluded-r fit puts lambda_min(QHQ)(9) at 94.07-94.10, against #131's 94.070673
   (REPORTED). gamma >= 80 needs at most m0 = 10 (7,796 classes).
7. **FIX-1 (sections 8.1 and 12).** No gamma is quoted without `GATE_REQUIRED|PASS`. That line requires the pinned
   independent verifier `py/cert_gate.py`, adopted from the critic's class_verify.py, to rebuild every row of the written
   certificate file and pass it, with its own row hash equal to the writer's.
   * Honest certificate, m0 = 11, r = 21/2, f = 8,7,6,5,4: gamma = 99.3655 and Ritz 99.389579. Both the writer and
     the verifier find min slack 2,883,978,097 and row hash `8369f4a981a888f4...`. `GATE_REQUIRED|PASS`; the
     verifier took 9 min 38 s and 404 MB (`out/fix1/honest_m11/`).
   * Every planted fault, including the new misrouted-target plants P5a and P5b, was written as a faulted file and fed
     to the verifier (section 8.1).
   * The r guard is a whitelist with a frozen-only r = 9 mode.

---

## 1. Setting and the facts used

* Configurations `U in S3^24`; gauge orbits i with weight `w_i` = number of tree-gauge-fixed configurations in the orbit
  (orbit size under the residual global conjugation); `sum_i w_i = 6^13`.
* Moves: `(e, tau)`, e a link, tau one of the three transpositions, `U_e -> tau U_e`. `c_ij` = number of the 72 moves
  that take a configuration of orbit i into orbit j (independent of the configuration chosen in i: a gauge transformation
  conjugates tau into another transposition and permutes the three moves of each link). Self-moves `c_ii` are included.
* `(H f)_i = (72 + r M_i) f_i - sum_j c_ij f_j`, self-adjoint in `<f, g>_w = sum_i w_i f_i g_i` by **detailed balance**
  `w_i c_ij = w_j c_ji` (REPORTED #131 and #146; reason: each move is an involution, so the pairs (configuration, move)
  from orbit i to orbit j are in bijection with the pairs from j to i, and orbit i holds `6^11 w_i` configurations).
  MEASURED here as a gate on every core edge at the class level (`GATE|class_detailed_balance`).
* QHQ is the compression of H to Q: moves into flats are simply absent from Q's rows.
* **Lattice symmetries.** The 48 maps (12 translations times the reflections x -> -x, y -> -y) act on configurations by
  permuting links, inverting the reversed ones. They commute with gauge transformations, map plaquettes to plaquettes
  (holonomy to a conjugate or inverse, same class), so they preserve M, the flats, w and the move multiset (for a reversed
  link `(tau U)^-1 = U^-1 tau = (U^-1 tau U) U^-1`, and `U^-1 tau U` runs over the three transpositions). Hence
  `c_{gi,gj} = c_ij`. The engine's `info()` asserts the M-symmetry and orbit-stabilizer on every core class.

## 2. The certificate and its proof (DERIVED)

### 2.1 Lemma 0 (per-link move table)

A move on link e changes the holonomies of exactly the two plaquettes p, q that contain e (distinct on the 3x4 torus).
With X, Y the holonomies of p and q based at the source vertex of e, the new classes are `(class(tau X), class(tau Y))`.

*Proof.* If p traverses e forwards from its source a, `hol_p(a) = U_e R` and the move gives `tau U_e R = tau X`. If q
traverses e backwards, `hol_q(a) = S U_e^-1` and the move gives `S U_e^-1 tau^-1 = S U_e^-1 tau`, which is conjugate to
`tau S U_e^-1 = tau Y`. QED.

Running tau over the three transpositions gives the Delta M multisets, by the class pair of (p, q):

| pair | ee | et | ec | tt, X = Y (aligned) | tt, X != Y | tc | cc |
|---|---|---|---|---|---|---|---|
| Delta M | {4,4,4} | {0,3,3} | {1,1,1} | {-4,2,2} | {-1,-1,2} | {-3,0,0} | {-2,-2,-2} |

So |Delta M| <= 4 for every move (not 6). Gates: all 36 pairs (X, Y) x 3 transpositions (`GATE|s3_link_table`); the
observed multiset of every link of every core representative and every tail target equals a table entry
(`GATE|link_multiset_table`, 2.96 million configurations at m0 = 10); the local Delta M equals a full recomputation of M
for every move and every two-step move (`GATE|local_delta_vs_full_M`).

### 2.2 Lemma 1 (ground-state substitution)

Let D be self-adjoint on `l2(S, w)` with `D_kl = a_k delta_kl - n_kl`, `n_kl >= 0`, and `w_k n_kl = w_l n_lk`. For any
`f > 0` on S, `D >= diag((D f)/f)` as quadratic forms.

*Proof.* Write `u = f phi`. Then `<u, D u> = sum_k w_k a_k f_k^2 phi_k^2 - sum_{k,l} A_kl phi_k phi_l` with
`A_kl = w_k n_kl f_k f_l = A_lk >= 0`. Since `phi_k phi_l <= (phi_k^2 + phi_l^2)/2`,
`sum A_kl phi_k phi_l <= sum_k phi_k^2 sum_l A_kl`. So
`<u, D u> >= sum_k w_k f_k^2 phi_k^2 [a_k - sum_l n_kl f_l / f_k] = sum_k w_k ((D f)_k / f_k) u_k^2`. QED.

Two uses: (i) on the tail with `D = H_TT`, (ii) on the core with D = F(t) and f = v; then `F(t) v >= 0` gives
`F(t) >= 0`. Use (ii) is the Collatz-Wielandt test for a symmetrizable Z-matrix (no Perron-Frobenius needed).

### 2.3 Lemma 2 (local tail floor by colourings)

Let f(M) > 0 for `m0 < M <= 36` and `G(M) = max over colourings col in {e,t,c}^12 with cost M of
sum_links g_{pair(link)}(M)`, where `g_pair(M) = sum_{Delta in multiset(pair), M + Delta > m0} f(M + Delta)` and for a
tt pair the larger of the aligned and non-aligned sums is used. Then every tail orbit k satisfies
`delta_k >= delta_min(M_k) := 72 + r M_k - G(M_k)/f(M_k)`.

*Proof.* `delta_k f_k = (72 + r M_k) f_k - sum_{(e,tau): M_k + Delta > m0} f(M_k + Delta)`. By Lemma 0 the inner sum
splits over links, each link contributing the g of its class pair (for tt, one of the two alignments). The plaquette
classes of k form one of the colourings with cost M_k. QED.

Refinement (DERIVED, optional, `--even 1`): the number of t plaquettes is even (sign is a homomorphism, every link lies
in two plaquettes, so the product of the plaquette signs is +1). Restricting to even colourings removes phantom layers
such as M = 5 (t + c). The smoke tables of section 5 use the conservative version (all colourings) unless marked.

**The cap.** `cap = min over M > m0 of delta_min(M)`, an affine function of r on each layer. For f = 1, `G(M) <= 72`,
so `cap >= r (m0 + 1)`, with equality whenever some colouring of cost m0 + 1 has no decreasing move (isolated
excitations; true for m0 = 4..11; at m0 = 12 the gain is 1). This is the trivial complete-cutoff floor; at r = 9 it is
`9 (m0 + 1)`. The task's guess "at most 6 per nontrivial plaquette pair" is replaced by the exact table of Lemma 0:
a move changes M by at most 4, and only links with a t or c plaquette carry decreasing moves (tt, tc, cc pairs).

### 2.4 Theorem S (Schur-CW floor)

Let `t < cap`, `v > 0` on C, and `(F(t) v)_i >= 0` for every `i in C`, with F(t) as in section 0. Then
`lambda_min(QHQ) >= t`.

*Proof.* (1) Lemmas 1 and 2: `H_TT - t >= diag(delta - t) > 0`, with delta the pointwise floor of Lemma 1, defined for
every tail orbit, and `delta_k - t >= cap - t > 0`. (2) Operator monotonicity of the inverse: `0 < Lambda <= D` implies
`D^-1 <= Lambda^-1` (diagonal Lambda commutes with w). So `(H_TT - t)^-1 <= diag(1/(delta - t))`. (3) Write
`B = H_TC`; its w-adjoint has entries `(B*)_ik = w_k B_ki / w_i = -c_ik`. Then the Schur complement
`S(t) = H_CC - t - B* (H_TT - t)^-1 B >= H_CC - t - B* diag(1/(delta - t)) B = F(t)`, and
`(B* diag B)_ij = sum_k c_ik c_kj / (delta_k - t)`. (4) F(t) is self-adjoint in w (`w_i c_ik c_kj = w_k c_ki c_kj`
is symmetric in i, j), and its off-diagonal entries are <= 0; Lemma 1 (ii) gives `F(t) >= 0`. (5) The congruence
`[[A, B*], [B, D]] = L* diag(S, D) L` with `L = [[I, 0], [D^-1 B, I]]` shows that `QHQ - t >= 0` when `D > 0` and
`S >= 0`. QED.

Remarks. Moves from the core into flats are absent (Q-compression); moves from the tail into flats are impossible for
`m0 >= 4` (|Delta M| <= 4). delta_k uses the exact move histogram of each tail orbit met in the two-step paths; the cap
covers every other tail orbit. No #131 input is used: the bound is unconditional.

### 2.5 Corollary (symmetry reduction, lift-free)

If v is constant on 48-symmetry classes, `(F(t) v)_{g i} = (F(t) v)_i` for every lattice map g, since c, M, w and
delta are invariant. So the rows at one representative per class are all the rows of the full-orbit-space F(t), and
the theorem holds on the whole nonflat space. At the class level the row is
`(72 + r M_A - t) v_A - sum_B c_{A->B} v_B - sum_{moves A -> k in T} sum_{moves k -> j in C} v_[j] / (delta_k - t)`,
with `c_{A->B}` = the number of the 72 moves of the representative of A that land in class B. No weights are needed for
the check; the class weights `W'_A = sum of the orbit weights of A` enter only the Ritz upper bound and the
detailed-balance gate.

**Tests of the lift-free step (FIX-1, item 6).**
* Writer gate `GATE|symmetry_image_rows`. For every class, the writer rebuilds the row at two images of the
  representative configuration. It requires the same M, core multiset, flat count and sorted tail multiset
  `(M_k, Delta-M histogram, sorted back classes)` as at the representative.
  * Image 0 is a non-identity lattice map chosen from the key. It can coincide with the representative when the map
    stabilizes it.
  * Image 1 is another lattice map followed by a key-seeded vertex gauge transformation.
* Critic receipts (REPORTED, critic lane, `critic/orbit_verify.py` 5b04b07fd484ede3). The rows were checked at every
  orbit, not only at class representatives:
  * all 2,346 orbits pass at m0 = 6, r = 20, and all 26,106 at m0 = 7, r = 12;
  * the min slacks equal the class-level ones (179,050,580 and 48,436,191,597);
  * the Ritz values match (130.773038 and 104.854117);
  * orbit-level detailed balance holds on 11,616 and 264,576 core edges (`critic/ov_m7_r12.txt`).
* Independent verifier. `py/cert_gate.py` builds each class row at its own representative (its own tree and canonical
  form). Its row hash must equal the writer's, so a class-dependence of the row would be refused.

### 2.6 Choosing f; the r-independent threshold r_star

On each layer, `delta_min(M) - r (m0 + 1) = 72 - G(M)/f(M) + r (M - m0 - 1)`. Hence `cap(r) >= r (m0 + 1)` for every
`r >= r_star := max over M > m0 + 1 of (G(M)/f(M) - 72)/(M - m0 - 1)`, and layer m0 + 1 gains the r-independent
`72 - G(m0+1)/f(m0+1)`. Both are r-independent counts (`floorcert rstar`). MEASURED (all colourings):

| m0 | f | r_star | binding layer | gain on layer m0 + 1 |
|---:|---|---:|---:|---:|
| 10 | 1 | 0 | 12 | 0 |
| 10 | 6,5,4,3 | 10/3 | 14 | 22 |
| 10 | 8,7,6,5,4 | 2.4375 | 15 | 19.5 |
| 10 | 4,3,2,1 | 10 | 14 | 33 |
| 11 | 6,5,4,3 | 4 | 15 | 20 |
| 11 | 8,7,6,5,4 | 3 | 16 | 18 |
| 11 | 4,3,2,1 | 12 | 15 | 30 |
| 12 | 6,5,4,3 | 4.2222 | 16 | 21 |
| 12 | 8,7,6,5,4 | 2.875 | 17 | 17.875 |
| 12 | 4,3,2,1 | 12.6667 | 16 | 31 |

So the steep f = (4,3,2,1), best at the excluded points, is **not guaranteed to keep the cap >= 9(m0+1) at r = 9** for
m0 >= 10 (r_star > 9); the mild f = (8,7,6,5,4) and (6,5,4,3) are (r_star < 9), and they lose little at r = 21/2
(section 5). This is a performance statement, not a soundness one: every f > 0 gives a rigorous certificate, because the
cap is recomputed at run time and t >= cap is refused (by the writer and, independently, by `py/cert_gate.py`).

### 2.7 Integer arithmetic

v and f are integers >= 1; `r = rn/rd`, `t = tn/td` with `td = 10^4`. Each row is multiplied by `rd td > 0`:
`L_i = (rd td 72 + td rn M_i - rd tn) v_i - rd td sum_j c_ij v_j`, and each two-step term
`S_k (rd td)^2 f_k / N_k`, with `S_k = sum_{j in back(k)} v_j` and `N_k = rd td f_k (delta_k - t)` a positive integer,
is replaced by its ceiling (an upper bound). `L_i >= sum_k ceil(...)` implies `(F(t) v)_i >= 0`. All products are i128
with overflow checks (|v| <= 2^50, f <= 2^24).

## 3. The requested shape, its matching condition, and why Theorem S drops it

Requested shape: one vector V on Q, `V = v` on the core and `V = c lambda^(M - m0)` (or any formula d) on the tail, with
`(QHQ V)_i >= gamma V_i` on every row.

* Tail rows (DERIVED): for k in T,
  `72 + r M_k - sum_{l in T} c_kl d_l/d_k - sum_{j in C} c_kj v_j / d_k >= gamma`.
  The first sum is the local count of Lemma 2 (with d in place of f). The second needs the **matching condition**: for
  every core orbit j one move from the tail (`M_j >= m0 - 3`), `v_j <= K d(j)`, where d is extended to those core
  layers by the same formula; the tail inequality then holds on layers m0 + 1, ..., m0 + 4 if
  `72 + r M - [G_tail(M) + K G_core(M)]/d(M) >= gamma`, with `G_core` the colouring maximum of the moves that land in the
  core layers.
* Core rows: `(72 + r M_i - gamma) v_i - sum_C c_ij v_j - sum_T c_il d_l >= 0`. For a fixed gamma the solution
  `v = (H_CC - gamma)^-1 b` (an M-matrix inverse, entrywise >= 0) is linear in c, so **c drops out of the matching
  ratio** `v_j / d(j)`: matching is a condition on the shape of d, not on its scale.
* Theorem S solves the tail-to-core coupling exactly through the Schur complement: the tail inequality is replaced by
  the operator floor of Lemma 1 for `H_TT` alone, which never sees the core values. Moves from the tail into the core
  are dropped from delta_k (each one raises it), so the tail floor of Theorem S dominates the tail row of the requested
  shape whenever K >= 0. The global vector of the requested shape is recovered implicitly as
  `V_T = (H_TT - t)^-1 B v`, which Theorem S never needs to evaluate.

So the matching condition of the requested shape is
`max over core j with M_j >= m0 - 3 of v_j / d(j) <= K`, with K entering the layers m0 + 1..m0 + 4 as above; Theorem S
needs none.

## 4. Census (MEASURED, r-independent)

Exact enumeration in tree gauge with plaquette pruning, one representative per 48-symmetry class by lexicographic
minimality over 48 maps x 6 conjugations (`floorcert census --m0 18`, 2 min on 2 threads). For every M the orbit count
`sum norb` and the weight `sum W'` equal the closed form of the mapping lane (Frobenius on the torus plus Burnside over
conjugation), so the enumeration is complete (`GATE|census_vs_closed_form|PASS|M=1..18`).

| M | 48-symmetry classes | gauge orbits | weight | cumulative classes (nonflat, M <= m) | cumulative orbits |
|---:|---:|---:|---:|---:|---:|
| 3 | 3 | 36 | 216 | 3 | 36 |
| 4 | 70 | 1,320 | 7,128 | 73 | 1,356 |
| 5 | 0 | 0 | 0 | 73 | 1,356 |
| 6 | 57 | 990 | 3,564 | 130 | 2,346 |
| 7 | 552 | 23,760 | 142,560 | 682 | 26,106 |
| 8 | 2,066 | 81,180 | 481,140 | 2,748 | 107,286 |
| 9 | 132 | 4,620 | 19,800 | 2,880 | 111,906 |
| 10 | 4,916 | 213,840 | 1,283,040 | 7,796 | 325,746 |
| 11 | 27,124 | 1,283,040 | 7,698,240 | 34,920 | 1,608,786 |
| 12 | 30,105 | 1,374,285 | 8,181,162 | 65,025 | 2,983,071 |
| 13 | 24,276 | 1,140,480 | 6,842,880 | 89,301 | 4,123,551 |
| 14 | 190,204 | 8,981,280 | 53,887,680 | 279,505 | 13,104,831 |
| 15 | 339,944 | 16,239,960 | 97,297,200 | 619,449 | 29,344,791 |
| 16 | 223,426 | 10,488,060 | 62,922,420 | 842,875 | 39,832,851 |
| 17 | 751,056 | 35,925,120 | 215,550,720 | 1,593,931 | 75,757,971 |
| 18 | 1,695,883 | 81,011,700 | 485,704,296 | 3,289,814 | 156,769,671 |

Class sizes over M <= 18 (orbits per class : number of classes): 2:3, 3:15, 4:34, 6:94, 8:10, 12:1,958, 24:44,344,
48:3,243,356. Independent recount (MEASURED): `py/indep_verify.py` (own S3, own spanning tree, own 48-map action, own
24-letter canonical form) finds 2,346 orbits and 130 classes for M <= 6 and 26,106 orbits and 682 classes for M <= 7;
in both cases the certificate's classes map onto its classes bijectively, its own colouring bound gives the same tail
cap (182 at r = 20, m0 = 6; 111 at r = 12, m0 = 7), and its own rows accept the Rust certificates
(`VERDICT|PASS`, gamma = 129.6149 at r = 20, m0 = 6, and 104.2273 at r = 12, m0 = 7).

FIX-1 (MEASURED). The required verifier `py/cert_gate.py` uses the critic's conventions: its own tree rooted at (1,2), its
own law and its own site maps. For M <= 11 it enumerates 9,635,688 tree-gauge configurations in 1,608,786 orbits and
34,920 classes. Those are the cumulative closed-form weight, orbit and class counts above. The certificate's 34,920 keys
map onto its classes bijectively.

## 5. Smoke results (MEASURED, excluded r only)

The engine's Ritz values (`ym137/engine/out/analysis_main_d5.txt`, pencil (U0, T)) bracket the low flat-sector levels
E1..E7 near 70 and are not comparable with `lambda_min(QHQ)`; the comparison column below is this lane's own
Rayleigh-Ritz upper bound on `lambda_min(QHQ)`.

Each run: build the core rows and the two-step tail data (r-independent), then for each (r, f): inverse iteration in
fixed point for v, the outer update `t <- t + cw_lo(F(t))`, then exact bisection on t (step 10^-4) for that v. gamma is
the largest t whose rows pass; `t + 10^-4` is refused (`next_t_refused`). Ritz = Rayleigh quotient of the zero-extended
class vector (an upper bound on `lambda_min(QHQ)`; printed values are truncated, add 10^-6). Tail cap from the
all-colourings bound. Ref = `94.070673 + 3 (r - 9)` (#131 plus Weyl, REPORTED and conditional; for orientation only).

**Best gamma per (r, m0)** (f among 1; 3,2,1; 4,3,2,1; 6,3,2,1; 2,1 for m0 <= 10; among 1; 4,3,2,1 for m0 >= 11):

| m0 | classes | r = 21/2 | r = 12 | r = 14 | r = 20 |
|---:|---:|---:|---:|---:|---:|
| 4 | 73 | 71.9999 (cap) | 83.9999 (cap) | 99.9999 (cap) | 129.2797 |
| 5 | 73 | 76.4999 (cap) | 89.9999 (cap) | 107.9999 (cap) | 129.5390 |
| 6 | 130 | 89.9999 (cap) | 103.2571 | 110.5041 | 129.7394 |
| 7 | 682 | 94.4999 (cap) | 104.2273 | 110.9287 | 129.9471 |
| 8 | 2,748 | 99.2980 | 104.4206 | 110.9965 | 129.9604 |
| 9 | 2,880 | 99.3355 | 104.4332 | 111.0004 | 129.9577 |
| 10 | 7,796 | 99.3570 | 104.4433 | 111.0048 | 129.9587 |
| 11 | 34,920 | 99.3697 | 104.4502 | 111.0088 | 129.9606 |
| 12 | 65,025 | 99.3720 | 104.4510 | 111.0076 | 129.9524 (f = 1 only) |
| 13 | 89,301 | 99.3721 | 104.4512 | - | - |
| best Ritz upper | | 99.376402 (m0 = 13) | 104.454020 (m0 = 13) | 111.011355 (m0 = 12) | 129.964492 (m0 = 12) |
| trivial r (m0 + 1) at m0 = 10 | | 115.5 | 132 | 154 | 220 |
| Ref (#131 + Weyl) | | 98.5707 | 103.0707 | 109.0707 | 127.0707 |

**f = 1 (the trivial tail floor r M; cap = r (m0 + 1))**, gamma:

| m0 | r = 21/2 | r = 12 | r = 14 | r = 20 |
|---:|---:|---:|---:|---:|
| 6 | 67.7823 | 73.7329 | 80.6255 | 126.6591 |
| 7 | 74.3151 | 80.4069 | 102.0262 | 129.8441 |
| 8 | 94.4999 (cap) | 104.3214 | 110.9655 | 129.9566 |
| 9 | 99.0441 | 104.3442 | 110.9711 | 129.9557 |
| 10 | 99.1948 | 104.3846 | 110.9837 | 129.9581 |
| 11 | 99.3528 | 104.4452 | 111.0074 | 129.9606 |
| 12 | 99.3714 | 104.4510 | 111.0072 | 129.9524 |
| 13 | 99.3720 | 104.4512 | - | - |

**Mild f (r_star < 9 at these m0)**, gamma at r = 21/2 and 12:

| m0 | f | r = 21/2 | cap | r = 12 | cap |
|---:|---|---:|---:|---:|---:|
| 8 | 8,7,6,5,4 | 99.2703 | 117 | 104.4054 | 130.5 |
| 8 | 6,5,4,3 | 99.2467 | 118 | 104.3975 | 132 |
| 9 | 8,7,6,5,4 | 99.2940 | 126 | 104.4147 | 141 |
| 9 | 6,5,4,3 | 99.2930 | 127.83 | 104.4146 | 144 |
| 10 | 6,5,4,3 | 99.3271 | 137 | 104.4297 | 154 |
| 10 | 8,7,6,5,4 | 99.3205 | 135 | 104.4267 | 151.5 |

**Smallest core that works** (best f; "A" = gamma >= 80 + 3 (r - 9), the Weyl-shifted "useful" level; "B" = gamma >=
Ref; "C" = gamma within 0.05 of the best Ritz):

| r | A | B | C |
|---|---|---|---|
| 21/2 | m0 = 6 (130 classes, 90.0) | m0 = 8 (2,748, 99.2980) | m0 = 9 (2,880, 99.3355) |
| 12 | m0 = 5 (73, 90.0) | m0 = 6 (130, 103.2571) | m0 = 8 (2,748, 104.4206) |
| 14 | m0 = 4 (73, 100.0) | m0 = 6 (130, 110.5041) | m0 = 8 (2,748, 110.9965) |
| 20 | m0 = 4 (73, 129.2797) | m0 = 4 (73) | m0 = 7 (682, 129.9471) |

Two regimes: for small cores gamma sits at the cap (the tail floor binds); once `cap - lambda_min` is a few units, gamma
is set by the core and drops toward the Ritz bound geometrically in m0. A thin first tail layer helps (M = 9 holds only
4,620 orbits, so m0 = 8 behaves much better than m0 = 7 or 9 would suggest).

## 6. Fits and the r = 9 conjecture

**Fit of lambda_min(QHQ)(r) (CONJECTURE).** With `lambda ~ (gamma + Ritz)/2` at the largest m0 (the bracket is at most
0.005 wide): `r (lambda - 72 - 3 r) = -43.32, -42.57, -41.84, -40.75` at r = 21/2, 12, 14, 20. A two-point fit
`A + B/r` (A ~ -37.9, B ~ -56.9) extrapolates to `lambda_min(QHQ)(9) ~ 94.09`; the local slope over r = 21/2..14
(about -62 per unit of 1/r) gives 94.08. CONJECTURE: `lambda_min(QHQ)(9)` lies in [94.07, 94.10], consistent with #131's
94.070673 (REPORTED, a Collatz-Wielandt lower bound). The deficit of this certificate at m0 = 12 is then the deciding
quantity for whether gamma(9) exceeds 94.070673 (OPEN, borderline).

**Deficit `Ritz - gamma` (MEASURED, against the m0 = 12 Ritz values 99.3769 and 104.4543), off the cap.** f = 1: r = 21/2: 0.333, 0.182, 0.024, 0.0055 at m0 = 9..12
(cap margins `r (m0+1) - lambda` = 5.6, 16.1, 26.6, 37.1); r = 12: 0.133, 0.110, 0.070, 0.009, 0.003 at m0 = 8..12
(margins 3.5, 15.5, 27.5, 39.5, 51.5). Best f: r = 21/2: 0.079, 0.041, 0.020, 0.0072, 0.0049 at m0 = 8..12; r = 12:
0.034, 0.021, 0.011, 0.004, 0.003 at m0 = 8..12. Roughly a factor 1.5-3 per unit of m0 once the cap margin exceeds about
10, and a collapse (gamma at the cap, or far below it when the first tail layer is thick) when the margin is below
about 5.

**r = 9 (CONJECTURE).** The f = 1 cap at r = 9 is the trivial `9 (m0 + 1)`: 90, 99, 108, 117 for m0 = 9..12. With
`lambda_min(9) ~ 94.07-94.09`, the margins are -4, 5, 14, 23. Matching margins and layer structure to the excluded data:
* m0 = 9 (thick first tail layer M = 10, negative margin): gamma ~ 75-85 with f = 1; use a mild f instead;
* m0 = 10 (margin ~ 5, like r = 21/2, m0 = 9): gamma ~ 93-93.7 with f = 1, a little higher with a mild f;
  certainly >= 80;
* m0 = 11 (margin ~ 14): gamma within ~ 0.3 of lambda_min, so >= 93.7;
* m0 = 12 (margin ~ 23): gamma within ~ 0.1.
**Proposed m0 = 11**, f in {1; 8,7,6,5,4; 6,5,4,3} (all with `r_star < 9`, so their cap at r = 9 is at least
`9 x 12 = 108`), with m0 = 12 as the fallback and m0 = 10 as the cheap first try; m0 = 13 (89,301 classes, under 1 GB)
if the deficit at m0 = 12 decides the comparison with 94.070673. Any gamma >= 80 is an unconditional, lift-free floor;
gamma >= 94.070673 would confirm #131's floor without its sector-to-whole lift.

Note (MEASURED): gamma is not exactly monotone in m0 (r = 14: 111.0088 at m0 = 11, 111.0076 at m0 = 12; r = 20:
129.9606 at m0 = 11, 129.9524 at m0 = 12 with f = 1; the r = 20, m0 = 12, f = (4,3,2,1) run was stopped after 15 min of
slow inverse iteration) because the
vector comes from an inexact inverse iteration stopped at a fixed tolerance; every printed gamma is still a rigorous
bound for its own vector. The r = 9 run should use a stricter stopping rule (e.g. `cw_hi - cw_lo <= 5e-5`).

## 7. Resource estimate (MEASURED at excluded r; the row phase is r-independent)

| m0 | classes | tail targets | two-step back moves | rows (1 thread, gates on) | peak RSS | vector + bisection per (r, f) |
|---:|---:|---:|---:|---:|---:|---:|
| 8 | 2,748 | 149,332 | 414,110 | 6 s | 15 MB | 3-8 s |
| 10 | 7,796 | 433,707 | 1,465,239 | 11 s | 41 MB | 5-45 s |
| 11 | 34,920 | 1,738,430 | 7,947,874 | 82 s | 174 MB | 80-170 s |
| 12 | 65,025 | 2,977,316 | 14,202,339 | 143 s | 311 MB | 190-290 s |
| 13 | 89,301 | 4,181,826 | 22,108,268 | 45 s (3 threads) | 443 MB | 310-410 s |
| 14 (estimate) | 279,505 | ~13 M | ~70 M | ~8 min | ~1.4 GB | ~15 min |

Disk: core key files are 8 bytes per class (2.2 MB at m0 = 14); no row file is written. The r = 9 run at m0 = 11 or 12
fits easily in one process under 1 GB and a few minutes. The rows (moves, tail histograms, two-step back moves) are
r-independent, so their hash can be frozen before the r = 9 run.

**FIX-1 timings (MEASURED, m0 = 11, r = 21/2, 2 threads, machine load 7-10 on 4 cores).**
* Writer rows with the image gate (3 row builds per class): 120 s, 175 MB.
* Writer row hash: 2 s, over 138,223,384 bytes.
* Writer vector and bisection: 130 s.
* Independent verifier `py/cert_gate.py`, one thread: 9 min 38 s, 404 MB. That covers the enumeration of 1,608,786
  orbits, the per-link table, the colouring cap, all 34,920 rows and the hash.

## 8. Planted faults and the gates that refuse them (MEASURED)

### 8.1 FIX-1: every faulted certificate file through the independent verifier

The plant table is in this subsection. The older table, with the pre-FIX-1 receipts, follows in 8.2.

**What a plant run does.**
* A faulted writer produces a full certificate file (`out/fix1/plants_*/cert_*_P*.txt`). The file has the honest
  format and contains no plant flag.
* It carries:
  * the claimed t and the vector the faulted pipeline found;
  * the f it used, written in full;
  * the cap it claimed (honest unless the plant is in the cap: P4c, P4d);
  * the row hash of the rows it used.
* Each file goes through `gate_required.sh`.

**What the columns mean.**
* "writer's own verdict" is the faulted writer's gated exact check on its own data and code. P1b uses the flipped code;
  P4c and P4d use the claimed cap.
* "independent verdict" lists every gate that `py/cert_gate.py` failed by its own recomputation.

**Runs.** r = 21/2 (excluded) at m0 = 6, 7 and 8. Two configurations have the cap binding, (6; 4,3,2,1) and
(7; 4,3,2,1). Two have the core binding, (7; 1) and (8; 8,7,6,5,4). Receipts: `out/fix1/PLANTS_RECEIPT.txt`; one
`.gate.txt` per file.

**New plants.**
* P5a: in every row, one count of the move to the core neighbour with the largest v is sent to the class with the
  smallest v, count kept.
* P5b: in every tail move, the two-step move back to the core class with the largest v is sent instead to the class
  with the smallest v, count kept.

Both pass `completeness_row` and `completeness_tail`.

| m0; f | plant | claimed t | t > honest | writer's own verdict | independent verdict (cert_gate.py) | required gate |
|---|---|---:|---|---|---|---|
| 6; 4,3,2,1 | P1a_wrong_sign_offdiagonal | 89.9999 | false | REFUSE zsign_core_count | REFUSE row_check, row_hash | REFUSE |
| 6; 4,3,2,1 | P1b_wrong_sign_schur_term_code | 89.9999 | false | PASS | PASS | PASS |
| 6; 4,3,2,1 | P2a_all_tail_neighbours_missing | 89.9999 | false | REFUSE completeness_row | REFUSE row_check, row_hash | REFUSE |
| 6; 4,3,2,1 | P2b_heaviest_tail_neighbour_missing | 89.9999 | false | REFUSE completeness_row | REFUSE row_hash | REFUSE |
| 6; 4,3,2,1 | P2c_two_step_paths_missing | 89.9999 | false | REFUSE completeness_tail | REFUSE row_check, row_hash | REFUSE |
| 6; 4,3,2,1 | P3a_tail_f_not_positive | 88.7774 | false | REFUSE positivity_f | REFUSE positivity_f | REFUSE |
| 6; 4,3,2,1 | P3b_core_v_not_positive | 89.9999 | false | REFUSE positivity_v | REFUSE positivity_v | REFUSE |
| 6; 4,3,2,1 | P4a_gamma_overstated_by_1e-4 | 90.0000 | true | REFUSE tail_layer_floor | REFUSE t_below_tail_cap | REFUSE |
| 6; 4,3,2,1 | P4b_tail_target_floors_overstated | 89.9999 | false | REFUSE completeness_tail | REFUSE row_hash | REFUSE |
| 6; 4,3,2,1 | P4c_tail_cap_overstated_by_10 | 88.2249 | false | PASS | REFUSE tail_cap_claim | REFUSE |
| 6; 4,3,2,1 | P4d_colouring_bound_understated_10pct | 88.2249 | false | REFUSE observed_tail_floor_below_claim | REFUSE tail_cap_claim | REFUSE |
| 6; 4,3,2,1 | P5a_misrouted_core_target | 89.9999 | false | REFUSE class_detailed_balance | REFUSE row_check, row_hash | REFUSE |
| 6; 4,3,2,1 | P5b_misrouted_two_step_target | 89.9999 | false | PASS | REFUSE row_check, row_hash | REFUSE |
| 6; 4,3,2,1 | HONEST | 89.9999 | - | PASS | PASS | PASS |
| 7; 4,3,2,1 | P1a_wrong_sign_offdiagonal | 94.4999 | false | REFUSE zsign_core_count | REFUSE row_check, row_hash | REFUSE |
| 7; 4,3,2,1 | P1b_wrong_sign_schur_term_code | 94.4999 | false | PASS | PASS | PASS |
| 7; 4,3,2,1 | P2a_all_tail_neighbours_missing | 94.4999 | false | REFUSE completeness_row | REFUSE row_check, row_hash | REFUSE |
| 7; 4,3,2,1 | P2b_heaviest_tail_neighbour_missing | 94.4999 | false | REFUSE completeness_row | REFUSE row_check, row_hash | REFUSE |
| 7; 4,3,2,1 | P2c_two_step_paths_missing | 94.4999 | false | REFUSE completeness_tail | REFUSE row_check, row_hash | REFUSE |
| 7; 4,3,2,1 | P3a_tail_f_not_positive | 94.4999 | false | REFUSE positivity_f | REFUSE positivity_f | REFUSE |
| 7; 4,3,2,1 | P3b_core_v_not_positive | 94.4999 | false | REFUSE positivity_v | REFUSE positivity_v | REFUSE |
| 7; 4,3,2,1 | P4a_gamma_overstated_by_1e-4 | 94.5000 | true | REFUSE tail_layer_floor | REFUSE t_below_tail_cap | REFUSE |
| 7; 4,3,2,1 | P4b_tail_target_floors_overstated | 94.4999 | false | REFUSE completeness_tail | REFUSE row_check, row_hash | REFUSE |
| 7; 4,3,2,1 | P4c_tail_cap_overstated_by_10 | 98.8764 | true | PASS | REFUSE tail_cap_claim, t_below_tail_cap | REFUSE |
| 7; 4,3,2,1 | P4d_colouring_bound_understated_10pct | 98.8764 | true | PASS | REFUSE tail_cap_claim, t_below_tail_cap | REFUSE |
| 7; 4,3,2,1 | P5a_misrouted_core_target | 94.4999 | false | REFUSE class_detailed_balance | REFUSE row_check, row_hash | REFUSE |
| 7; 4,3,2,1 | P5b_misrouted_two_step_target | 94.4999 | false | PASS | REFUSE row_check, row_hash | REFUSE |
| 7; 4,3,2,1 | HONEST | 94.4999 | - | PASS | PASS | PASS |
| 7; 1 | P1a_wrong_sign_offdiagonal | 81.9355 | true | REFUSE zsign_core_count | REFUSE row_check, row_hash | REFUSE |
| 7; 1 | P1b_wrong_sign_schur_term_code | 74.3151 | false | PASS | PASS | PASS |
| 7; 1 | P2a_all_tail_neighbours_missing | 83.9999 | true | REFUSE completeness_row | REFUSE row_check, row_hash | REFUSE |
| 7; 1 | P2b_heaviest_tail_neighbour_missing | 75.7580 | true | REFUSE completeness_row | REFUSE row_check, row_hash | REFUSE |
| 7; 1 | P2c_two_step_paths_missing | 83.9999 | true | REFUSE completeness_tail | REFUSE row_check, row_hash | REFUSE |
| 7; 1 | P3a_tail_f_not_positive | 74.3174 | true | REFUSE positivity_f | REFUSE positivity_f | REFUSE |
| 7; 1 | P3b_core_v_not_positive | 74.3151 | false | REFUSE positivity_v | REFUSE positivity_v | REFUSE |
| 7; 1 | P4a_gamma_overstated_by_1e-4 | 74.3152 | true | REFUSE row_check | REFUSE row_check | REFUSE |
| 7; 1 | P4b_tail_target_floors_overstated | 74.3203 | true | REFUSE completeness_tail | REFUSE row_hash | REFUSE |
| 7; 1 | P4c_tail_cap_overstated_by_10 | 31.5000 | false | PASS | REFUSE tail_cap_claim | REFUSE |
| 7; 1 | P4d_colouring_bound_understated_10pct | 31.5000 | false | REFUSE observed_tail_floor_below_claim | REFUSE tail_cap_claim | REFUSE |
| 7; 1 | P5a_misrouted_core_target | 75.9202 | true | REFUSE class_detailed_balance | REFUSE row_check, row_hash | REFUSE |
| 7; 1 | P5b_misrouted_two_step_target | 83.9999 | true | PASS | REFUSE row_check, row_hash | REFUSE |
| 7; 1 | HONEST | 74.3151 | - | PASS | PASS | PASS |
| 8; 8,7,6,5,4 | P1a_wrong_sign_offdiagonal | 103.5000 | true | REFUSE zsign_core_count | REFUSE row_check, row_hash | REFUSE |
| 8; 8,7,6,5,4 | P1b_wrong_sign_schur_term_code | 99.2706 | true | PASS | REFUSE row_check | REFUSE |
| 8; 8,7,6,5,4 | P2a_all_tail_neighbours_missing | 99.4577 | true | REFUSE completeness_row | REFUSE row_check, row_hash | REFUSE |
| 8; 8,7,6,5,4 | P2b_heaviest_tail_neighbour_missing | 99.2829 | true | REFUSE completeness_row | REFUSE row_check, row_hash | REFUSE |
| 8; 8,7,6,5,4 | P2c_two_step_paths_missing | 99.4577 | true | REFUSE completeness_tail | REFUSE row_check, row_hash | REFUSE |
| 8; 8,7,6,5,4 | P3a_tail_f_not_positive | 93.6179 | false | REFUSE positivity_f | REFUSE positivity_f | REFUSE |
| 8; 8,7,6,5,4 | P3b_core_v_not_positive | 99.2703 | false | REFUSE positivity_v | REFUSE positivity_v | REFUSE |
| 8; 8,7,6,5,4 | P4a_gamma_overstated_by_1e-4 | 99.2704 | true | REFUSE row_check | REFUSE row_check | REFUSE |
| 8; 8,7,6,5,4 | P4b_tail_target_floors_overstated | 99.2799 | true | REFUSE completeness_tail | REFUSE row_check, row_hash | REFUSE |
| 8; 8,7,6,5,4 | P4c_tail_cap_overstated_by_10 | 99.2703 | false | PASS | REFUSE tail_cap_claim | REFUSE |
| 8; 8,7,6,5,4 | P4d_colouring_bound_understated_10pct | 99.2703 | false | REFUSE observed_tail_floor_below_claim | REFUSE tail_cap_claim | REFUSE |
| 8; 8,7,6,5,4 | P5a_misrouted_core_target | 102.2422 | true | REFUSE class_detailed_balance | REFUSE row_check, row_hash | REFUSE |
| 8; 8,7,6,5,4 | P5b_misrouted_two_step_target | 99.3581 | true | PASS | REFUSE row_check, row_hash | REFUSE |
| 8; 8,7,6,5,4 | HONEST | 99.2703 | - | PASS | PASS | PASS |

**Findings (MEASURED, r = 21/2).**

1. **Honest files.** All four honest files get `GATE_REQUIRED|PASS`, and the verifier's own row hash equals the
   writer's: m0 = 6 `d591edb7e9b546cb`, m0 = 7 `6cfcff1492d3e02a`, m0 = 8 `714b8ba3e318c8f8`. The m0 = 7 hash is the same
   as at r = 12 (smoke), as it must be, because the rows do not depend on r.
2. **Every faulted file that differs from the honest file is refused.** Each refusal comes from the verifier's own
   recomputation:
   * row-data plants (P1a, P2a-c, P4b, P5a, P5b): `row_hash` every time, plus `row_check` whenever the claimed (t, v)
     also fails the true rows;
   * P3a and P3b: `positivity_f` (the header carries the negative f) and `positivity_v`;
   * P4a: `t_below_tail_cap` where the cap binds, `row_check` where the core binds;
   * P4c and P4d: `tail_cap_claim`, because the verifier's own colouring cap differs from the header. Where the claimed
     t also exceeds the true cap, `t_below_tail_cap` fails too (m0 = 7, f = 4,3,2,1: 98.8764 > 94.5).
3. **Faults the writer's own gates pass, which only the independent gate refuses.**
   * P1b, the Schur-sign code error. At m0 = 8 it claims 99.2706 > 99.2703, and `row_check` refuses it. This is the
     critic's counterexample.
   * P4c: the faulted writer trusts its own claimed cap.
   * P4d at (7; 4,3,2,1): no observed tail target exceeds the understated G.
   * P5b, a misrouted two-step move with its count kept, in all four configurations.
   * P5a, a misrouted one-step move, is now also refused by the writer's new `class_detailed_balance` gate.
4. **Provably false claims.** Four claims exceed the Ritz upper bound 99.3765 on lambda_min(QHQ), all at m0 = 8: P1a
   103.5000, P5a 102.2422, P2a and P2c 99.4577. All four are refused.
5. **A PASS on a faulted run happens only when the faulted file is identical to the honest one.** This is P1b at
   (6; 4,3,2,1), (7; 4,3,2,1) and (7; 1). There the cap, or an M = 3 row with no tail moves at m0 = 7, binds, so the
   flipped Schur sign cannot raise t. The writer then writes the honest t and v, and the file has the honest sha256. That
   file is a valid certificate, so PASS is the correct verdict.
6. **Cases where only the row hash refuses.** P2b and P4b at m0 = 6, and P4b at (7; 1): the faulted (t, v) still
   satisfies the true rows, and the header's row hash is wrong.
7. **Divergent faulted pipelines.** P4c and P4d at (7; 1) stayed at the initial t = 31.5; P3a at m0 = 8 reached 93.6179.
   These are recorded as they came out; each is still refused by its own gate.

### 8.2 Pre-FIX-1 receipts (writer-internal gates)

Each fault is planted on purpose; the whole pipeline (vector and bisection) is rerun on the faulted data with the gates
off ("bare" = the row algebra alone), and the gated checker then judges the faulted certificate. "Provably false" means
the bare gamma exceeds a Rayleigh-Ritz upper bound on `lambda_min(QHQ)` from a larger core (`--ub`). Runs:
`out/plants_rust_m7_r12.txt` (r = 12, m0 = 7, ub 104.4605), `out/plants_rust_m7_r21_2.txt` (r = 21/2, m0 = 7, ub
99.3771, cap binding), `out/plants_rust_m6_r20.txt` (r = 20, m0 = 6, ub 129.9706), and `out/py_plants.txt`,
`out/py_P1b.txt` (independent Python verifier).

| fault | what is planted | bare gamma (honest) | gate that refuses |
|---|---|---|---|
| P1a wrong sign | every core off-diagonal count negated (not a Z-matrix) | 108.0000 (104.2273), above ub: provably false | `zsign_core_count` |
| P1b wrong sign | Schur term added instead of subtracted (code error) | 131.9213 at r = 20 (129.6149), above ub 129.9706 | independent verifier: `REFUSE gate=row_check` (`out/py_P1b.txt`) |
| P2a missing tail neighbours | all tail targets dropped (complete-cutoff mistake) | 104.7669 (104.2273), above ub | `completeness_row` (21 of 72 moves) |
| P2b missing tail neighbour | the heaviest tail target of each row dropped | 104.2572 | `completeness_row` (71 of 72) |
| P2c missing two-step paths | every move from a tail target back into the core dropped | 104.7669, above ub | `completeness_tail` (68 of 72) |
| P3a d not positive | f(m0 + 2) negated | 98.6246 at r = 21/2 (94.4999) | `positivity_f` |
| P3b d not positive | smallest core entry of v set to 0 | bare check also fails | `positivity_v` |
| P4a floor overstated | gamma + 10^-4 | - | `row_check` |
| P4b floor overstated | tail-staying decreasing moves forgotten (delta_k inflated) | 104.2537 | `completeness_tail` |
| P4c floor overstated | analytic tail cap claimed 10 higher | 98.8764 at r = 21/2 (cap 94.5) | `tail_layer_floor` (cap recomputed from the colourings) |
| P4d floor overstated | colouring bound G(M) understated by 10 % | - | `observed_tail_floor_below_claim` (3,328 of 149,332 observed targets at m0 = 8, r = 12); at m0 = 7 no observed target exceeds it, and the recomputation of G(M) refuses |
| Python plants | v zeroed / t + 1 / f negated / cap + 50 | - | `positivity_v` / `row_check` / `positivity_f` / `tail_cap_recomputed` (vacuous; see below) |

The baseline certificate passes each gated check, and `t + 10^-4` is refused in every run.

**Superseded by FIX-1 (critic).**
* Rows P2a-c, P4b and P4c above were refused only inside the writer, by its own counters and its own cap.
* The Python `capup` "refusal" was triggered by the plant flag itself. It is deleted.
* Section 8.1 replaces these rows by faulted files that go through the independent verifier.

## 9. Gate list (all PASS on every smoke run)

`s3_link_table`, `link_multiset_table`, `local_delta_vs_full_M`, `core_census_vs_closed_form`, core completeness of every
one-step and two-step target (`expect` on the class index), `class_detailed_balance`, `observed_ge_layer` (every observed
tail target's exact f-sum is at most G(M)), `zsign_core_count`, `completeness_row`, `completeness_tail`, `positivity_v`,
`positivity_f`, `tail_layer_floor`, `zsign_schur_denominator`, `row_check`; independent verifier: `class_bijection`, its
own tail cap, its own rows.

FIX-1 additions.
* Writer:
  * `symmetry_image_rows` (section 2.5);
  * `class_detailed_balance`, now also inside the exact check, so a misrouted one-step move is refused;
  * `ROWHASH` and `KEYSHASH` on every build;
  * the r policy (section 12).
* Required independent gate `py/cert_gate.py`: `r_policy`, `class_bijection`, `keys_hash`, `positivity_f`,
  `positivity_v`, `tail_cap_claim` (the header's cap must equal its own colouring cap), `t_below_tail_cap`, `row_check`
  (all rows, every failure counted) and `row_hash` (its own canonical rows against the header).
* `gate_required.sh` pins the verifier's hash. It prints `GATE_REQUIRED|PASS` only on `VERDICT|PASS` with equal row
  hashes.

## 10. Files and fingerprints (sha256, first 16 hex)

**FIX-1 (current).**

| file | sha256 (16 hex) | role |
|---|---|---|
| `rs/src/main.rs` | 7824ed780aa7f15e | floorcert source (FIX-1) |
| `rs/Cargo.toml` | 63026f703d730712 | Rust 1.81, no dependencies, overflow checks on |
| `rs/Cargo.lock` | 964f252c22008671 | lock file (no dependencies) |
| `rs/target/release/floorcert` | 0432b8265b88921e | binary, cargo +1.81 build --release (rustc 1.81.0), not frozen (no FREEZE pins compiled in) |
| `py/cert_gate.py` | 6043d0897250a7c8 | REQUIRED independent verifier (adopted from critic/class_verify.py 756b3a2590293c1a) |
| `gate_required.sh` | 13a92ab7562dc8a3 | required-gate driver, pins py/cert_gate.py |
| `py/indep_verify.py` | 497d2fbb64eb14e9 | second-opinion verifier (m0 <= 7), capup deleted, r whitelist |
| `out/fix1/run_fix1.sh` | 5436e2d97eea435d | FIX-1 run driver (smoke, honest11, plants, rows12) |
| `out/fix1/adhoc.sh` | f153f6056d77e5c7 | light checks (sha256 cross-check, r refusals, token scan, body comparison) |
| `out/fix1/receipts.sh` | 411a1a61a7d32506 | rebuilds RECEIPT.txt and PLANTS_RECEIPT.txt from the logs (supersedes the receipt() of run_fix1.sh) |
| `out/fix1/receipt_table.sh` | cc9d492d1bf3c5f2 | plant table formatter |
| `out/fix1/ledger.sh` | 80b85e9c81895ad0 | computation ledger |
| `out/fix1/fingerprints.sh` | 337ca2c9984d3a6c | this table |
| `out/fix1/smoke/selftest.txt` | 345f71973e0982dc | SHA-256 and r-policy self-test |
| `out/fix1/smoke/cert_m7_r12_1_f4-3-2-1.txt` | 6b0864111909134d | smoke certificate, r = 12, m0 = 7 |
| `out/fix1/smoke/cert_m7_r12_1_f4-3-2-1.txt.gate.txt` | fc6886655b76f271 | GATE_REQUIRED|PASS, smoke |
| `out/fix1/honest_m11/writer.txt` | d9e5bb5f9dd572a7 | writer log, r = 21/2, m0 = 11 (ROWHASH, CERT) |
| `out/fix1/honest_m11/cert_m11_r21_2_f8-7-6-5-4.txt` | a217a469e1bb4822 | honest certificate, r = 21/2, m0 = 11 |
| `out/fix1/honest_m11/cert_m11_r21_2_f8-7-6-5-4.txt.gate.txt` | 2bf1ce715db454e3 | GATE_REQUIRED|PASS, m0 = 11 |
| `out/fix1/honest_m11/core_keys_m11.bin` | e25b8b392161f6f0 | core keys m0 = 11 (= out/core_keys_m11.bin) |
| `out/fix1/PLANTS_RECEIPT.txt` | 9b9918354d65a3ed | per-plant writer and independent verdicts, m0 = 6, 7, 8 |
| `out/fix1/rows_m12/writer.txt` | 5fa6b7cf38bbdc88 | writer row hash, m0 = 12 |
| `out/fix1/rows_m12/verifier.txt` | 10b9f7407598efe4 | verifier row hash, m0 = 12 |
| `out/fix1/rows_m12/core_keys_m12.bin` | 942c2eed527aa2c3 | core keys m0 = 12 |
| `out/fix1/adhoc/sha256_crosscheck.txt` | d462fc755cb3e898 | floorcert sha256 = sha256sum |
| `out/fix1/adhoc/r_refusals.txt` | 0d76495274cbc401 | writer r refusals |
| `out/fix1/adhoc/py_r_refusals.txt` | 0abebd34ab3b43f4 | Python verifiers' r refusals |
| `out/fix1/adhoc/token_scan.txt` | 104eafcab1d8ac56 | integer-only token scan |
| `out/fix1/adhoc/body_vs_critic.txt` | b15d38d16e4974bb | m0 = 11 body = critic's |
| `out/fix1/second_opinion/indep_m7_r12_honest.txt` | bf326f77e50fd454 | indep_verify PASS (smoke) |
| `out/fix1/second_opinion/indep_m7_r12_capclaim121.txt` | be485fddff0989b2 | indep_verify REFUSE tail_cap_claim |
| `out/fix1/LEDGER.txt` | 53e3b7d4c838ffb8 | ledger of every FIX-1 computation |
| `CHANGES.txt` | 1e34581a0353a647 | change log (FIX-1 section) |

The NOTE's own hash cannot be in its own table; it is returned with the FIX-1 report. Every FIX-1 computation is listed,
with the sha256 of its program and output, in `out/fix1/LEDGER.txt`.

**Pre-FIX-1 (superseded; the sources are kept unchanged in `prefix1/`).**

| file | sha256 (16 hex) | role |
|---|---|---|
| `rs/src/main.rs` | 7be0180828047e8e | floorcert: census, cert, tail, rstar, planted faults (pre-FIX-1 build) |
| `rs/Cargo.toml` | 63026f703d730712 | Rust 1.81, no dependencies, overflow checks on |
| `py/indep_verify.py` | 3b5ad10165c4e94b | independent verifier (m0 <= 7) |
| `out/grid/run.sh` | 384102a302666359 | smoke grid driver (m0 = 7..12) |
| `out/py_plants.sh` | c04f031ab5191528 | Python planted faults |
| `out/plants_rust_m7_r12.txt` | c8c5f510cbdc3645 | planted faults, r = 12 |
| `out/plants_rust_m7_r21_2.txt` | 5eb119475b7e2122 | planted faults, r = 21/2 (cap binding) |
| `out/plants_rust_m6_r20.txt` | 6e0ba602d899e1a5 | P1b faulted certificate, r = 20 |
| `out/plants_rust_m8_r12.txt` | 7d4f34daf69d073b | planted faults, r = 12, m0 = 8 |
| `out/py_plants.txt` | acd3e92f33942a70 | Python refusals |
| `out/py_P1b.txt` | fc9eccb69c837551 | Python refuses the P1b certificate |
| `out/py_verify_m7_r12.txt` | bf326f77e50fd454 | Python PASS, m0 = 7, r = 12 |

The grid outputs `out/grid/m4.txt` .. `m13.txt` and `mild_m8..10.txt` came from builds of the same certificate path made
earlier in the session (later edits added the planted-fault suite, `rstar`, `--even` and the order of the gate
messages). The final build reproduces `out/grid/m8.txt` line for line (`out/repro_final_m8.txt`, every CERT line
identical except the timing field). Pre-freeze disclosure: every smoke run used r in {21/2, 12, 14, 20}. The pre-FIX-1
program refused r <= 9 only, which admitted r = 9 + epsilon; the critic's one such run is disclosed at the top of this
NOTE. Since FIX-1 the whitelist of section 12 applies.

## 11. OPEN

* The r = 9 run (after its own frozen prediction): m0 = 11 and 12 with f = 1 and the two mild f; freeze the row hash
  (r-independent) first.
* Independent review of Theorem S, Lemma 1 (the ground-state substitution used twice) and Lemma 2.
* A sharper tail: f depending on the plaquette colouring (a product of class weights) keeps Lemma 2 local; larger
  clusters for G(M) (the alignment relaxation is the main slack); the even-t refinement for the cap.
* A Ritz upper bound with a first-order tail response (the Dirichlet Ritz value converges slowly at r = 20).
* ~~The independent verifier is Python and covers m0 <= 7~~. Closed by FIX-1: `py/cert_gate.py` checks every row at
  m0 = 11, and computes the row hash at m0 = 12 in its rows-only mode (section 12).
* The NOTE section 6 r = 9 statements are CONJECTURES. They are carried into the floor's frozen prediction (to be
  written by the prediction step); FIX-1 does not supersede them.

## 12. FIX-1: the required independent gate, the row hash and the r = 9 procedure

**r policy (both languages).**
* Excluded values: r in {21/2, 12, 14} or r >= 20. Everything else is refused before any computation, with
  `REFUSE|gate=r_policy` and exit 3. That includes 10, which is within 1 of 9.
* r = 9 is a separate mode. The writer refuses it unless all of these hold:
  * the binary was built with `FLOORCERT_FREEZE_COMMIT` (40 hex) and `FLOORCERT_PREDICTION_SHA256` (64 hex) compiled in
    (`option_env!`);
  * `--freeze-commit` and `--prediction-sha256` equal those pins;
  * the `--prediction` file hashes to the pin.
* Only the frozen binary can run at r = 9. It then prints a `FREEZE` line with its own sha256 and writes `freeze=` and
  `pred=` into the certificate header.
* The verifiers accept r = 9 only with the same three arguments matching that header.
* The r = 9 mode has never been run. The refusals were tested at r = 10, 19/2, 90000001/10000000 and 8: each was
  refused at argument parsing and wrote no file.

**Row hash (r- and f-independent).**
* SHA-256 is written in std-only Rust. Its constants are rederived in integers from the first 64 primes, and it passes
  the FIPS 180-4 vectors.
* Input is a canonical text serialization of the rows:
  * per class, in key order: `C key M flat( tkey:count)*`;
  * per tail move, sorted by (M_k, h, back keys): `T M_k h0,..,h8( bkey)*`;
  * a final line `END classes tails backs`.
* `py/cert_gate.py` builds the same text from its own rows with hashlib. The writer puts `rowhash=` and `keyshash=` into
  every certificate header.

**The r = 9 procedure (for the frozen run; nothing here was run at r = 9).**
1. Freeze: commit the sources with the prediction file. The sources are `rs/src/main.rs`, `rs/Cargo.toml`,
   `rs/Cargo.lock`, `py/cert_gate.py` and `gate_required.sh`. Also pin the r-independent row hash and the core_keys hash
   of the chosen m0 (table below).
2. Build the frozen binary:
   `FLOORCERT_FREEZE_COMMIT=<commit> FLOORCERT_PREDICTION_SHA256=<sha> cargo +1.81 build --release`.
3. Rows first: `floorcert rowhash --m0 11` must print the pinned row hash.
4. Run: `floorcert cert --m0 11 --r 9 --f '1;8,7,6,5,4;6,5,4,3' --write-cert --freeze-commit <commit> --prediction
   <file> --prediction-sha256 <sha>`.
5. Gate: `gate_required.sh <cert> --freeze-commit <commit> --prediction <file> --prediction-sha256 <sha>`. A gamma is
   quoted only with its `GATE_REQUIRED|PASS` line.

**Pre-freeze pins (MEASURED, r-independent; full sha256).**

| m0 | classes | core_keys sha256 | row hash (writer = verifier) | tail moves | back moves | serialized bytes |
|---:|---:|---|---|---:|---:|---:|
| 7 | 682 | 051ef322cd8442a1dc1139f29755c74a74af142d516febbeee43d83545205df7 | 6cfcff1492d3e02a7311a8622ef2dbd41c946898012379519d3ddcbb8958ea3d | 40,850 | 93,040 | 2,101,058 |
| 11 | 34,920 | e25b8b392161f6f02d933f6a1e78643b3ff95ae3fb69b72b02a36c2c8a5f3a7e | 8369f4a981a888f4e028b155f3306371c2eacb421bed9bbc444b86e7ef862884 | 1,738,430 | 7,947,874 | 138,223,384 |
| 12 | 65,025 | 942c2eed527aa2c327ce2aa5e811c0c64b0c524a46671f4ccb99ee1086ff5479 | f835b2e1ded4b7f3f38d9d7f3f8437ebfa0a6ede53783f224ebbd1e9b4b7dee7 | 2,977,316 | 14,202,339 | 247,570,170 |

At m0 = 12 the writer computed the hash with `floorcert rowhash --m0 12` (rows and image gate 92 s and the hash
2 s, on 2 threads, 312 MB). `py/cert_gate.py --rows-only` computed it independently (2,983,071 orbits, 65,025 classes,
14 min 40 s on one thread, 733 MB, `out/fix1/rows_m12/`). The verifier's own hash also equals the writer's at m0 = 6 (d591edb7e9b546cb...) and
m0 = 8 (714b8ba3e318c8f8..., `out/fix1/plants_*`).
Neither the row hash nor the core_keys hash depends on r or f.
