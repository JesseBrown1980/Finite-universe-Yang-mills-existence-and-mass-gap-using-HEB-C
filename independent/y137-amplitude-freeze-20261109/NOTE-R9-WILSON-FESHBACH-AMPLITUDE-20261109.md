# r = 9 Wilson-sum first-excitation amplitude: the Feshbach certificate, frozen before the run (#137, cloud seat)

Written 2026-11-09 by the cloud seat's synthesis seat (Claude Opus 5.5), from the math lane (`math/NOTE-MATH.md`) and
the engine lane (`engine/`). Companion files: the frozen rows
`PREDICT-S3-3X4-R9-WILSON-FESHBACH-AMPLITUDE-20261109.hbp` and the post-freeze work order `ENGINE-PLAN.txt`.

**Status: PRE-RUN FREEZE.** This lane computed nothing that depends on r for the 3x4 model at r = 9. Section 12 lists
every computation made before the freeze, with fingerprints.

**Scope line.** Every result is conditional on #131's floor, named exactly
`accepted_source_assumption=lambda_min_QHQ_whole_GE_94070673/1000000` (hypothesis H4). The UPPER (Rayleigh-Ritz)
counts are the only floor-free outputs. The model is the finite periodic 3x4 spatial S3 lattice at r = 9, with no
continuum, 4D, SU(N) or Clay claim.

Tags: MEASURED (r-independent combinatorics, or excluded r > 9 only), DERIVED (proved here), REPORTED (another lane),
CONJECTURE (a frozen prediction), OPEN.

---

## 0. Summary

* **Theorem I (isolation, DERIVED).** Exact integer inertia tests on 7x7 rational matrices certify the following.
  H has exactly one eigenvalue E1 < tau1 and exactly one eigenvalue E2 in (tau1, tau2). Both are simple and both lie
  in the fully symmetric sector, which is reflection-even and has zero momentum. No other eigenvalue of H is ≤ tau2.
  The tests cover both Schur witnesses at tau1 and at tau2, and the odd level by a 1x1 Feshbach form. Every other
  sector has no flat and lies above the floor.
* **Theorem A (amplitude, DERIVED).** A closed rational formula gives
  `|<psi2, O_sum psi1>_W| / (||psi1|| ||psi2||) >= a_lo`, so `weight_first >= a_lo^2` when `a_lo > 0`. Every nonflat
  state enters only through exact identities and the floor.
* **Corollary A' (upper bound, DERIVED, new in this note).** The same quantities give an upper bound a_hi. It is used
  only to test the frozen amplitude prediction.
* **Excluded-r smoke (MEASURED, r = 10.5 to 40).** I ran the math lane's own certificate code (`fesh.certify`) on the
  engine's exact 7x7 integer data, without the adjoint. The isolation tests pass at every depth ≥ 2. The amplitude
  bound is refused at depth ≤ 3 for r ≤ 14 in both sine forms, and at r = 16 with Lemma 7 (the Lemma 7' form gives
  0.003676 there). It is positive at depths 4 and 5 for every excluded r. At r = 10.5,
  depth 5, with the midpoint z*, a_lo = 0.027521, against the Ritz main term 0.029008. The cross-flat factor k_c is
  1.41 to 1.44 at depth 5, independent of r. That replaces the math lane's OPEN range of 1 to 7.
* **Frozen method.** X and Y on 5 shells of the 48-symmetry sector. The exterior is shell 6 (2,465,466 classes,
  MEASURED). The odd sector also uses 5 shells. z* is the pass-1 midpoint rule and c is the pass-1 ground Rayleigh
  rule. The scale is S = 10^15 with 256-bit accumulators. Python ints and an independent C++17 integer checker
  (its own bignum, standard library only) run every 7x7 test.
* **Verdict rule (frozen, HBP row 131).** Only depth 5 sets a verdict. Depths 2 to 4 are ladder entries: their check
  outcomes are reported, and they never stop the run. Run-integrity checks (pins, census, identities, replay) refuse
  the whole run at any depth. The reported verdict and the one reportable bound follow the reported route alone
  (row 131's frozen table); every other a_lo is printed as a LADDER or INFORMATIVE measurement, never as a bound. The
  floor pin is scoped by r: gamma0 = 94070673/10^6 at r = 9, and #131's floor plus the Weyl step,
  94070673/10^6 + 3(r - 9), at the excluded r of the smoke and the post-freeze regression and fault runs.
* **Frozen prediction (CONJECTURE).** The primary a_lo at r = 9 is positive and lies in [0.0295, 0.0333]. The true
  amplitude lies in [0.0325, 0.0337]. The depth ladder is: the depth-2 entry is not PASS, because F_GAP fails there
  (HBP row 133; the depth-2 isolation outcome is not predicted); isolation passes at depths 3, 4 and 5; the amplitude
  bound is nonpositive at depth 3; a_lo is positive at depths 4 and 5.
* **GPT-6's design audit (issue #137 comment 6747959074, posted before any frozen r = 9 measurement).** Each of its
  six items is a REQUIRED HBP row that cites the comment (rows 146-151), mapped to the rows that answer it (section
  15). The floor source is pinned at #131's merge commit (FLOOR_PIN, rows 041 and 136); the sector-to-whole lift is
  **not** audited by this package. Separate C++17 code (the regenerator xext) regenerates the depth-5 exterior and
  every hat from the published X and Y (checks EXT_REGEN and SIGN_POLAR, rows 134, 135, 139). GPT-6's two exact
  counterexamples are run as negative-control receipts, each false positive refused by its independent gate and not
  by the certificate's algebra (rows 141, 142). A second, separately frozen floor may be evaluated beside the verdict,
  read and report only (Lemma 11, rows 137, 138), and the package's E3 - E2 bounds are cross-checked against #155 and
  #136 (row 140). No frozen prediction changed.

---

## 1. Model, observable and target (as frozen in PR #148 rows 01-12)

* Omega: the gauge orbits of the periodic 3x4 S3 lattice, |Omega| = 2,177,317,873. Orbit weights w_s, with
  `<f,g>_W = sum_s w_s f_s g_s`.
* `H/J_E = 72 I - T + r M` at r = 9: `H_ss = 72 + r m_s - c_ss` and `H_st = -c_st`, where c_st counts the
  (link, transposition) moves from s into t. Every orbit has 72 such moves (24 links x 3 transpositions).
* `O = O_sum = sum_y chi(W_x(y)) + sum_x chi(W_y(x))`, with `chi = #fixed points - 1`, values 2, 0, -1. It is a
  diagonal operator with values in [O_min, O_max] = [-7, 14]. It is gauge invariant and invariant under the 48
  lattice maps. It is not #144's dual electric shift.
* F: the 8 flat orbits; P: the indicator projection onto F; Q = 1 - P. Both are W-orthogonal because W is diagonal.
* Target (PR #148 rows 10 and 11): `weight_first = ||P_first (O - <O>_0) psi_0||_W^2`. Once Theorem I shows that P_first
  has rank 1, this equals `|<psi2, O psi1>_W|^2 / (||psi1||^2 ||psi2||^2)`, because `<psi2, psi1>_W = 0`.

## 2. Hypotheses

| name | statement | status |
|---|---|---|
| H1 | Detailed balance `w_s c_st = w_t c_ts` (so W H is symmetric) | integer test on every stored edge (check `H1_DETAILED_BALANCE`) |
| H2 | The 48 maps Gamma (12 translations x 4 reflection combinations) permute Omega, preserving w, m, O, c, and Gamma F = F | structural, r-independent |
| H3 | Gamma fixes six flats and moves only {(c,c), (c,c^-1)}, swapped exactly when `chi_odd = s_x s_y = -1`; `chi_odd` is a homomorphism | MEASURED, r-independent (`flat3x4.py` 48e35d86d061afd4; engine selftest 5037da106c67f3ab) |
| H4 | `<f, H f>_W >= gamma0 <f, f>_W` for every f supported off F in the **whole** orbit space, `gamma0 = 94070673/10^6` | CONDITIONAL on #131 (PERRON-BOUND.md sections 1-2; whole-orbit lift accepted, measured on 2x2 and 2x3; #152 reproduced 94.070673 at row 45,507,968). Source pinned at #131's merge commit d1385b3 (section 15.2); the lift is not audited by this package |
| H5 | No flat-to-flat move and m = 0 on F, so `H_FF = 72 I` | checked in #136; not used by any proof below |

Symmetric-sector flats, in the order (e,e), (e,t), (e,c), (t,e), (t,t), (c,e), {(c,c),(c,c^-1)}:
`W_P = diag(1,3,2,3,3,2,4)` and `O_P = (14,8,5,6,0,2,-7)`. The odd flat vector is `f_odd = e_(c,c) - e_(c,c^-1)`, with
`||f_odd||_W^2 = 4` and O = -7. These agree with PR #148 row 15 (flat weights 1,3,2,3,3,2,2,2).

## 3. Sector reduction (Lemma S)

Put `Pi_triv = |Gamma|^-1 sum_g g` and `Pi_odd = |Gamma|^-1 sum_g chi_odd(g) g`, and let
`Pi_rest = 1 - Pi_triv - Pi_odd`.

**Lemma S.** Under H2, H3 and H4:
1. V = V_triv + V_odd + V_rest is a W-orthogonal decomposition into H-invariant subspaces.
2. `P V_rest = 0`, so V_rest lies in range Q, and every eigenvalue of H on V_rest is ≥ gamma0.
3. `P V_triv` has dimension 7, spanned by the six fixed flats and `e_(c,c) + e_(c,c^-1)`, and `P V_odd = span{f_odd}`.
4. O maps V_triv into itself. If psi1 and psi2 both lie in V_triv, then `<psi2, O psi1>` can be computed in V_triv.
   If E2 were the odd level, then `<psi2, O psi1> = 0` exactly (the dark case of PR #148 row 19).

*Proof.* (1) Each g is W-unitary and commutes with H and O. The characters 1 and chi_odd are real and distinct, so the
projectors are W-orthogonal and commute with H. (2) By H3, the permutation representation of Gamma on R^F is
7 x trivial + 1 x chi_odd. So Pi_rest kills every function supported on F. Since P commutes with every g,
`P Pi_rest f = Pi_rest P f = 0`. For f in V_rest we therefore have f = Q f, and H4 gives
`<f, H f> >= gamma0 ||f||^2`. (3) Read off from H3. (4) O commutes with Gamma, and V_triv is W-orthogonal to V_odd. QED.

H4 is used on the **whole** nonflat space, because V_rest is not inside the symmetric sector.

**Class bases.** V_triv has the basis `1_K` over the Gamma-classes K, with Gram `W_K = sum_{s in K} w_s` and matrix
`h_KL = (72 + r m_K) delta_KL - #{moves from a representative s_K into L}`. V_odd has the basis
`f_K = sum_{t in K} chi_odd(g_t) e_t` over the classes whose stabiliser lies in ker chi_odd, with the same W_K and with
`h_KL = (H f_L)(s_K)`. Both satisfy `W_K h_KL = W_L h_LK` (test H1), and both are orthogonal bases. Everything below
applies in either sector, with p = 7 or p = 1 flat directions.

## 4. Feshbach-Schur and the two witnesses

Work in one sector. For z < gamma0, put `A(z) = Q(H - z)Q` on range Q, `B = -H_QP` (Q x p), and
`S(z) = W_P (H_PP - z) - B^T W_Q A(z)^-1 B` (p x p, symmetric).

**Lemma 1 (Haynsworth).** For z < gamma0: (a) the number of eigenvalues of H below z is neg S(z); (b) the multiplicity
of z as an eigenvalue equals dim ker S(z); (c) `ker(H - z) = { phi + A(z)^-1 B phi : phi in ker S(z) }`.

*Proof.* `W(H - z)` is symmetric, and congruent through W^(1/2) to a matrix similar to H - z. Detailed balance gives
`W_P H_PQ = (W_Q H_QP)^T = -B^T W_Q`. Then `W(H - z) = L^T diag(S(z), W_Q A(z)) L` with
`L = [[I, 0], [-A(z)^-1 B, I]]`. Sylvester's law gives `In(H - z) = In S(z) + In A(z)`, and `A(z) > 0` by H4.
For (c): `(H - z)(phi + A^-1 B phi)` equals `W_P^-1 S(z) phi` on P and 0 on Q. QED.

**Lemma 2 (truncated-resolvent identity).** Let X be any Q x p array of finite support. Put
`R(z) = B - A(z) X = R0 + z X` with `R0 = B - H_QQ X`, and

    U0 = W_P H_PP - X^T W B - B^T W X + X^T W H_QQ X,   T = W_P + X^T W X,   G(z) = R(z)^T W R(z).

Then exactly

    S(z) = U0 - z T - Delta(z),   Delta(z) = R(z)^T W A(z)^-1 R(z),   0 <= Delta(z) <= G(z) / (gamma0 - z).

*Proof.* Write B = A X + R. Since `W A = A^T W`, we have `A^T W A^-1 = W`, so
`B^T W A^-1 B = X^T W A X + X^T W R + R^T W X + R^T W A^-1 R`. Substituting `X^T W R = X^T W B - X^T W A X` gives
`B^T W A^-1 B = X^T W B + B^T W X - X^T W A X + R^T W A^-1 R`. Insert this into S(z) and use `A = H_QQ - z`. For the
bounds: H4 gives `A(z) >= (gamma0 - z)` in the W metric, so `0 <= A^-1 <= (gamma0 - z)^-1`. QED.

If X lives on shells 1..n, then R0 lives on shells 1..n+1. The shell-(n+1) part is `-(H X)` there and does not depend
on z. On the inner shells, `R(z) = R(z*) + (z - z*) X`, where R(z*) is the exact rounding residual of the solve. The
exterior and inner supports are disjoint, so

    G(z) = G(z*) + (z - z*) (X^T W R(z*) + R(z*)^T W X) + (z - z*)^2 X^T W X,                    (4.1)

where only the inner part of R(z*) enters the middle term. The engine prints the four integer matrices this needs
(GEX + GIN = G(z*), XWR, M0 = X^T W X).

**Corollary 3 (two witnesses).** For rational tau < gamma0, put `UP(tau) = U0 - tau T` and
`LO(tau) = UP(tau) - G(tau)/(gamma0 - tau)`. Then

    #{E < tau} >= neg UP(tau),        #{E <= tau} <= neg LO(tau) + null LO(tau).

*Proof.* `LO(tau) <= S(tau) <= UP(tau)`, then Weyl monotonicity and Lemma 1. QED.

**Remark 4.4 (UP is floor-free).** For `psi = phi + X phi` we have exactly `<psi, H psi>_W = phi^T U0 phi` and
`<psi, psi>_W = phi^T T phi`. So `kappa_j := lambda_j(U0, T) >= E_j` by Rayleigh-Ritz, without any floor.

## 5. Theorem I (isolation)

Let C_t be the symmetric-sector data (p = 7) and C_o the odd-sector data (p = 1, with its own X_o). Choose rationals
`tau1 < tau2 < gamma0`.

* I0: `tau2 < gamma0`.
* I1: `neg UP(tau1) = 1` and `neg LO(tau1) = 1`, with every leading minor of both nonzero.
* I2: `neg UP(tau2) = 2` and `neg LO(tau2) = 2`, with every leading minor of both nonzero.
* I3: `LO_odd(tau2) = U0_odd - tau2 T_odd - G_odd(tau2)/(gamma0 - tau2) > 0`.

**Theorem I.** If I0 to I3 pass then, conditional on H4, H on the whole space has exactly one eigenvalue E1 < tau1 and
exactly one eigenvalue E2 in (tau1, tau2). Both are simple, both eigenvectors lie in V_triv, and no other eigenvalue of
H is ≤ tau2. So psi1 is the unique ground state and P_first has rank 1, which answers PR #148 F8.

*Proof.* In V_triv, I1 and Corollary 3 give `#{E < tau1} >= 1` and `#{E <= tau1} <= 1`. So exactly one eigenvalue is
≤ tau1, and it is < tau1. I2 gives, in the same way, exactly two eigenvalues ≤ tau2, both < tau2. The second of them is
therefore in (tau1, tau2). Counts include multiplicity, so both are simple. In V_odd, I3 gives
`S_odd(tau2) >= LO_odd(tau2) > 0`, so neg S_odd(tau2) = 0 and null S_odd(tau2) = 0. By Lemma 1 (p = 1), no odd
eigenvalue is < tau2 and tau2 is not one, so none is ≤ tau2. In V_rest every eigenvalue is ≥ gamma0 > tau2 (Lemma S). Sum over the three sectors. QED.

The owner's acceptance item 1 also asks that tau2 lie above E2's certified upper bound. The driver tests this
explicitly as `tau2 > upsilon_2` (check `TAU2_ABOVE_UPSILON2`).

**Windows.** For i = 1, 2, choose rationals `sigma_i < upsilon_i` with `neg UP(upsilon_i) >= i` and
`neg LO(sigma_i) + null LO(sigma_i) <= i - 1`. Then `E_i in (sigma_i, upsilon_i)`. Inside the window range these are the
global E1 and E2 by Theorem I.

## 6. Uniform window bounds (Lemma 4)

**Lemma 4 (matrix convexity).** By (4.1), G(z) is a matrix quadratic with leading coefficient `X^T W X >= 0`. For
z in [sigma, upsilon] with `z = theta sigma + (1 - theta) upsilon`,
`theta G(sigma) + (1 - theta) G(upsilon) - G(z) = theta (1 - theta)(upsilon - sigma)^2 X^T W X >= 0`. So if
`g T - G(sigma)` and `g T - G(upsilon)` are positive definite, then `G(z) < g T` on the whole window. For a fixed vector
v, `v^T G(z) v <= max(v^T G(sigma) v, v^T G(upsilon) v)`. The same holds for the dual Gram `Dgram(z) = D(z)^T W D(z)`
with `D(z) = D(z*) + (z - z*) Y` (section 8), whose leading coefficient is `Y^T W Y >= 0`. QED.

With `g_i` certified at both ends of window i, put `eps_i = g_i / (gamma0 - upsilon_i)`. Since `gamma0 - E_i > gamma0 - upsilon_i`,
Lemma 2 gives `0 <= Delta(E_i) <= eps_i T`.

## 7. Eigenvector enclosure

Let phi_i be the P-part of psi_i. By Lemma 1(c), `psi_i = phi_i + A(E_i)^-1 B phi_i`. Then exactly
`(U0 - Delta_i) phi_i = E_i T phi_i`, with `Delta_i = Delta(E_i)`. Also phi_i ≠ 0: otherwise psi_i would lie in range Q
with `A(E_i) psi_i = 0`, which contradicts `A(E_i) > 0`.

**Lemma 5.** E_i is the i-th eigenvalue of the pencil `(U0 - Delta_i, T)`, and it is simple.
*Proof.* `U0 - Delta_i - E_i T = S(E_i)` has `neg = i - 1` and `null = 1` (Lemma 1 and Theorem I). Apply Sylvester's law
to `T^(-1/2) S(E_i) T^(-1/2)`. QED.

**Lemma 6 (neighbours).** `kappa_j - eps_i <= lambda_j(U0 - Delta_i, T) <= kappa_j` for every j (Courant-Fischer with
`0 <= Delta_i <= eps_i T`). The integer tests:
* N1+: `neg UP(l1+ + eps_1) <= 1`, nonsingular. Then `kappa_2 > l1+ + eps_1`, so `lambda_2(U0 - Delta_1, T) > l1+`.
* N2+: `neg UP(l2+ + eps_2) <= 2`, nonsingular. Then `lambda_3(U0 - Delta_2, T) > l2+`. This encloses the whole E3..E8
  tail of the pencil, which is PR #148 F7.
* N2-: `neg UP(l2-) >= 1`. Then `lambda_1(U0 - Delta_2, T) <= kappa_1 < l2-`.

**Lemma 7 (Davis-Kahan in the T geometry).** Let phihat_i be a rational vector and mu_i a rational with
`l_i- < mu_i < l_i+` (`l_1- = -infinity`). Put `delta_i = min(mu_i - l_i-, l_i+ - mu_i)`. Then
`sin angle_T(phihat_i, phi_i) <= s_i := (rho_i + sqrt(eps_i beta_i)) / delta_i`, where

    rho_i^2 = phihat^T (U0 - mu T) T^-1 (U0 - mu T) phihat / (phihat^T T phihat),
    beta_i  = max(phihat^T G(sigma_i) phihat, phihat^T G(upsilon_i) phihat) / ((gamma0 - upsilon_i) phihat^T T phihat).

*Proof.* `L' = T^-1 (U0 - Delta_i)` is self-adjoint in the T inner product. E_i is a simple eigenvalue (Lemma 5), and
every other eigenvalue lies outside (l-, l+) (Lemma 6). Let P_i be the T-orthogonal spectral projector and
`r = (U0 - Delta_i - mu T) phihat`. Then `(1 - P_i) T^-1 r = (L' - mu)(1 - P_i) phihat`, and `|L' - mu| >= delta` on
range(1 - P_i). So `||(1 - P_i) phihat||_T <= ||r||_(T^-1) / delta`. By the triangle inequality,
`||r||_(T^-1) <= rho ||phihat||_T + ||Delta phihat||_(T^-1)`. With `K = T^(-1/2) Delta T^(-1/2)` and `0 <= K <= eps`,
we get `K^2 <= eps K`. So `||Delta phihat||^2_(T^-1) <= eps phihat^T Delta phihat <= eps beta ||phihat||_T^2`, using
Lemma 4 on the scalar quadratic and `1/(gamma0 - E_i) < 1/(gamma0 - upsilon_i)`. QED.

**Lemma 7' (centred).** Under the same hypotheses, let `mu_c = mu_i - eps_i/2` with `l_i- < mu_c < l_i+`, and
`delta_c = min(mu_c - l_i-, l_i+ - mu_c)`. Then `sin angle_T(phihat_i, phi_i) <= s_c := (rho_i + eps_i/2) / delta_c`,
with rho_i the residual at mu_i.
*Proof.* `(U0 - Delta_i - mu_c T) phihat = (U0 - mu_i T) phihat - (Delta_i - (eps_i/2) T) phihat`. The first term has
T^-1 norm `rho_i ||phihat||_T`. Since `0 <= K <= eps_i`, `||K - eps_i/2|| <= eps_i/2`, so the second term has T^-1 norm at
most `(eps_i/2) ||phihat||_T`. Apply the Davis-Kahan step of Lemma 7 at mu_c. QED.

The certificate uses `min(s_i, s_c,i)`; both are proven bounds.

**Which a_lo decides, and when none is computed.** Check `A_POS` tests the min-form a_lo, with
`s_i = min(Lemma 7, Lemma 7')` (fesh row `A_centred_lower_bound_positive(Lemma7prime)`, whose sine is that minimum).
The Lemma-7-only a_lo (fesh row `A_lower_bound_positive`) is printed as an informative row and never decides a
verdict. The two can disagree: at r = 16, depth 3, the smoke gives -0.0062 for Lemma 7 alone and +0.003676 for the
min form. `fesh.certify`'s combined `ok` flag demands both, so the driver does not use it.

Lemmas 7 and 7' need their centres strictly inside the gap: `l_i- < mu_i < l_i+` and `l_i- < mu_i - eps_i/2 < l_i+`.
Check `F_GAP` tests both centres, `delta > 0` and both sine forms below 1. When a centre lies outside the gap,
`delta <= 0` and the formula returns a negative number that is not a sine bound (the smoke prints sbar = -1.138 at
depth 1, r = 10.5). `fesh.certify` still computes a_lo from it. So, wherever F_GAP fails, the driver withholds a_lo
in both forms, a_hi and the angular term, and prints them as NOT_EVALUATED.

## 8. The amplitude

Fix any rational c and put `Oc = O - c`. Since E1 ≠ E2, `<psi2, psi1>_W = 0`, so
`a := <psi2, O psi1>_W = <psi2, Oc psi1>_W`.

Let Y be any Q x p array of finite support (shells 1..m), with dual residual `D(z) = Oc X - A(z) Y = D0 + z Y`, where
`D0 = Oc X - H_QQ Y` lives on shells 1..max(n, m+1). Define

    M        = W_P Oc_P + X^T W Oc X,
    N(z1,z2) = M + Y^T W R(z1) + R(z2)^T W Y.

**Lemma 8 (amplitude identity).** With `t_i = A(E_i)^-1 R(E_i) phi_i`, so that `psi_i = phi_i + X phi_i + t_i`:

    a = phi2^T N(E1,E2) phi1 + eps_a,
    eps_a = <A(E1)^-1 D(E1) phi2, R(E1) phi1>_W + <R(E2) phi2, A(E2)^-1 D(E2) phi1>_W + <t2, Oc t1>_W.

*Proof.* Oc is diagonal, so the P and Q parts separate:
`<psi2, Oc psi1> = phi2^T M phi1 + <Oc X phi2, t1> + <t2, Oc X phi1> + <t2, Oc t1>`.
For the first cross term, A1 = A(E1) is W-self-adjoint, so
`<Oc X phi2, A1^-1 R1 phi1> = <A1^-1 Oc X phi2, R1 phi1>`. Since `A1^-1 Oc X = Y + A1^-1 D(E1)`, this equals
`phi2^T Y^T W R(E1) phi1 + <A1^-1 D(E1) phi2, R(E1) phi1>`. The second cross term is handled the same way with A2. QED.

**Bound.** H4 gives `||A(E)^-1|| <= 1/(gamma0 - upsilon)`. Lemma 4 gives `R(E_i)^T W R(E_i) <= g_i T` and
`D(E_i)^T W D(E_i) <= h_i T`. Also `||t_i|| <= sqrt(g_i) |phi_i|_T / (gamma0 - upsilon_i)`, and
`o_inf = max(O_max - c, c - O_min)` bounds |Oc| on all of Q. Cauchy-Schwarz then gives `|eps_a| <= e_a |phi1|_T |phi2|_T`
with

    e_a = sqrt(h1 g1)/(gamma0 - upsilon1) + sqrt(g2 h2)/(gamma0 - upsilon2) + o_inf sqrt(g1 g2)/((gamma0 - upsilon1)(gamma0 - upsilon2)).

These are the terms linear in the residual, times the spread of O. Lemma 8 bounds them through the adjoint solve by a
proven inequality, not by a fitted rate (refuter test 3). If m ≤ n, then Y and the exterior part of R have disjoint
supports, so `Y^T W R(z)` involves only the inner residual. The dual solve therefore needs no shell beyond shell n+1.

Lemma 8 is the goal-oriented error identity that GPT-6's audit item 5 asks for: the error of the amplitude
functional is a primal residual times an adjoint residual (or two primal residuals), divided by the distance to the
floor. Section 15.6 defines g (its norm, its scale and its role) and lists where each error is bounded.

**Secondary route (Y = 0).** With Y = 0 we get N = M and D = Oc X, and h_i becomes o, a certified bound with
`o T >= X^T Oc W Oc X`. The same formula is then the honest first-order Cauchy-Schwarz bound. It is also a proven
inequality, and it is printed in the same run as a cross-check.

**Lemma 9 (normalisation).** `||psi_i||_W <= |phi_i|_T + ||t_i|| <= |phi_i|_T (1 + taubar_i)` and
`||psi_i||_W >= |phi_i|_T (1 - taubar_i)`, with `taubar_i = sqrt(g_i)/(gamma0 - upsilon_i)`. This holds because
`||phi + X phi||_W^2 = phi^T T phi`.

**Lemma 10 (window and angular terms).** Put `zbar_i = (sigma_i + upsilon_i)/2`, `w_i = (upsilon_i - sigma_i)/2` and
`N_c = N(zbar1, zbar2)`. Since `R(z) = R0 + z X`,
`N(E1,E2) - N_c = (E1 - zbar1) Y^T W X + (E2 - zbar2) X^T W Y`. So
`|phi2^T (N(E1,E2) - N_c) phi1| <= (w1 + w2) ybar |phi1|_T |phi2|_T`, where `ybar^2 T >= Y^T W Y` and `X^T W X <= T`.
Write `u_i = phi_i/|phi_i|_T = c_i h_i + s'_i e_i`, with h_i the T-unit phihat_i, e_i T-unit and T-orthogonal to h_i,
c_i ≥ 0 (signs are free because only |a| matters) and `s'_i <= s_i`. Then

    |u2^T N_c u1| >= (1 - s1^2)(1 - s2^2) nu0 - s1 n21 - s2 n12 - s1 s2 nubar,

where `P21 = phihat2^T N_c phihat1`, `t_i = phihat_i^T T phihat_i`, `nu0^2 = P21^2/(t1 t2)`,
`n21^2 = (phihat2^T N_c T^-1 N_c^T phihat2 - P21^2/t1)/t2`, `n12^2 = (phihat1^T N_c^T T^-1 N_c phihat1 - P21^2/t2)/t1`
and `nubar^2 T >= N_c^T T^-1 N_c`.

*Proof.* Expand `u2^T N_c u1` into four terms. The term `c1 c2 h2^T N_c h1` has modulus `c1 c2 nu0`, and
`c_i = sqrt(1 - s'_i^2) >= 1 - s_i^2`. For `h2^T N_c e1 = <T^-1 N_c^T h2, e1>_T`: e1 ranges over T-unit vectors
T-orthogonal to h1, so its modulus is at most the T-norm of the part of T^-1 N_c^T h2 orthogonal to h1, which is n21.
The term `e2^T N_c h1` is bounded by n12 in the same way. Finally `|e2^T N_c e1| <= ||T^-1 N_c e1||_T <= nubar`.
The coefficients c_i are at most 1. QED.

n21 is not the spread of O alone. It is the norm of `N_c^T h2` off h1, so it includes the h2 component, about
`<O>_2 - c`. Its size is `n21^2 ~ ||(O - <O>_2) psi2||^2 + (<O>_2 - c)^2 ~ 9 + 24` for c near `<O>_1`. The excluded-r
smoke measures n21 = 5.755 and n12 = 2.984 at r = 10.5. See section 13, correction 1.

**Theorem A.** Assume Theorem I's tests, the window tests, PD certificates for g_i, h_i, ybar and nubar, N1+, N2+, N2-,
the conditions `l_i- < mu_i < l_i+` and `s_i < 1`, and the square-root bound tests. Then, conditional on H4,

    |<psi2, O_sum psi1>_W| / (||psi1||_W ||psi2||_W) >= a_lo
      := [ (1 - s1^2)(1 - s2^2) nu0 - s1 n21 - s2 n12 - s1 s2 nubar - (w1 + w2) ybar - e_a ] / ((1 + taubar1)(1 + taubar2)).

Every irrational quantity is replaced by a rational bound in the safe direction: upper bounds for s, n21, n12, nubar,
ybar, e_a and taubar, and a lower bound for nu0. If a_lo > 0, then `weight_first >= a_lo^2` (PR #148 row 11).

*Proof.* Lemmas 8 to 10 give `|a| >= |phi2^T N_c phi1| - (w1 + w2) ybar |phi1||phi2| - e_a |phi1||phi2|`. The angular
bound of Lemma 10 bounds the first term from below, and Lemma 9 bounds the norms. P_first has rank 1 by Theorem I. QED.

**Corollary A' (upper bound; new here).** Under the same tests, and if `taubar_i < 1`,

    |a| / (||psi1|| ||psi2||) <= a_hi := [ nu0 + s1 n21 + s2 n12 + s1 s2 nubar + (w1 + w2) ybar + e_a ] / ((1 - taubar1)(1 - taubar2)),

with every quantity rounded in the safe direction for an upper bound.
*Proof.* `|u2^T N_c u1| <= c1 c2 nu0 + s1 n21 + s2 n12 + s1 s2 nubar <= nu0 + ...`, then add the window and remainder
terms, and use the lower norm bound of Lemma 9. QED.

a_hi is not needed for #137. It makes the frozen amplitude interval testable: if [a_lo, a_hi] misses
[0.0325, 0.0337], then HBP row 083 is FALSIFIED. Corollary A' is new in this note, and it is open to refutation like
everything else here.

## 9. The method frozen for r = 9 (engine contract)

**Depth.** X on shells 1..5 of the symmetric sector. That is 441,939 inner rows; the exterior is shell 6, with
2,465,466 classes, accumulated by class. Y on shells 1..5 of the same graph, so D lives on shells 1..6. The odd sector
uses its shells 1..5. One build also gives depths 2, 3 and 4, and the certificate is reported for each of them (the depth
ladder). The verdict uses depth 5 only (HBP row 131): depths 2 to 4 are ladder entries, whose check outcomes are
reported and never stop the run.

**Pass 1 (rules only).** X0 is solved at `z0 = 72 - 18/r - 3/r^2` (5667/81 = 1889/27 at r = 9) by integer
Gauss-Seidel. kappa_1 and kappa_2 are bracketed by UP-inertia bisection, `fesh.pencil_eigs(U0, T, 2, lo, hi, bits=40)`
on the pass-1 hats, from `lo = 72 - 18/r - 1` to `hi` = the run's gamma0 (check FLOOR_PIN, HBP row 041): exactly
`94070673/10^6` at r = 9, and exactly `94070673/10^6 + 3(r - 9)` (HBP row 010, #131's floor plus the Weyl step with
M ≥ 3 off the flats) at excluded r > 9, as `smoke_cert.py` used. Then:
* `z* = floor(10^6 (mid1 + mid2)/2) / 10^6`, with `mid_i = (a_i + b_i)/2` the bracket midpoints;
* `c = floor(1000 R_O)/1000`, where `R_O = phi^T M_O phi / phi^T T phi` with `M_O = W_P O_P + X0^T W O X0`, and phi is
  the ground pencil vector after 3 exact inverse iterations at mid1 (`fesh.inverse_iter`, 160-bit rounding), started
  from `v0 = (1 + (7k^2 + 3k) mod 11)_{k=0..6} = (1, 11, 2, 7, 4, 4, 7)`.

Every step is exact rational arithmetic, so both floors are the same in every implementation. For HBP rows 018 and
091 only, pass 1 also prints `R_O2`, the same Rayleigh quotient on the first pencil vector after 3 inverse iterations
at mid2 (the O_first value of `smoke_cert.py`). R_O and R_O2 are Rayleigh quotients, not certified values, and R_O2
is used by no rule.

Any rational z* and c are valid. The rules only keep the residual small. At excluded r, the midpoint rule cut g_1 by
2.3x (r = 10.5) and 2.6x (r = 12) against the default z*.

**Pass 2.** X is solved at z* on shells 1..5. Y solves `A(z*) Y = (O - c) X` on shells 1..5. X_odd uses the same z*.
The stop rule is max|dX| = 0, or 6 consecutive sweeps with max|dX| ≤ 2.

**Fixed point.** `S = 10^15` and `X = X_int/S`, with `|X_int| < 2^62` asserted. The exact residual is
`Rhat = D S B - (D A) X_int` on shells 1..6, with `D = lcm(RD, ZD)`. Exterior rows are aggregated by class, and the
division by W_e is checked exact. The accumulators are 256-bit, and overflow aborts the run. Any S is valid, because
the rounding is counted exactly in R. (This replaces the math lane's suggestion of S = 2^40 with i128.)

**Hats printed (exact integers, each with its scale and sha256).** U0 (scale D S^2), T (S^2), GEX and GIN ((D S)^2),
XWR (D S^2), and M0, M1, M2 (`X^T W O^k X`, S^2). After the freeze the engine adds the dual set: DEX and DIN (the
exterior and inner Grams of D(z*)), YWD (`Y^T W D_inner(z*)`), YY (`Y^T W Y`), YWR (`Y^T W R_inner(z*)`) and YX
(`Y^T W X`), plus the odd scalars. G(z) is rebuilt by (4.1), and `Dgram(z) = Dgram(z*) + (z - z*)(YWD + YWD^T) + (z - z*)^2 YY`.
G(z*) is never used at any z ≠ z*. At the verdict depth the engine also publishes INNER-X, INNER-Y and ODD-X (the
representative, W_i, m_i and the integer rows of X and Y), so that separate code can rebuild every hat (section 15.3).

**Certificate procedure.** `fesh.certify` (d39b5d0438e6948b) runs through the engine-hat adapter of `synth/smoke_cert.py`
(9c033df34e816d17), with the Y terms added. Its fixed rules:
* lo = 72 - 18/r - 1, and pencil brackets of 90 bits;
* tau_i = the first of the fractions 1/2, 1/3, 2/3, 1/4, 3/4, 1/8, 7/8, 1/16, 15/16 between consecutive kappa midpoints
  that passes both UP and LO;
* upsilon_i = the kappa_i upper bracket, rounded up to 1e-15;
* sigma_i = the largest of 60 bisection points with LO count ≤ i - 1;
* g_i, h_i and y by 60-step PD bisection, rounded up to 1e-12 and then multiplied by 1000001/1000000, at both window ends;
  when `Y^T W Y` is the zero matrix (Y = 0, the secondary route), y = ybar = 0 and check Y_PD passes (HBP row 054),
  as `fesh.certify` itself sets;
* phihat_i by 4 exact inverse iterations with 160-bit rounding;
* square roots by isqrt to 40 digits at r = 9. The excluded-r regression X6 uses 30 digits, the setting that wrote the
  reference smoke files, together with the row-010 gamma0 and each reference tag's z* and c. The RESULT row keeps
  fesh's raw ok, tests and fail counts, which never decide a verdict, so X6 reproduces them unchanged.

The driver maps fesh's test rows onto the HBP checks by a frozen table (ENGINE-PLAN D5). It also prints the 90-bit UP
brackets of kappa_1 to kappa_7 at every depth, the window widths and the odd bracket, so that every sub-claim of HBP
rows 077 to 080 can be measured, and the inner part of g_i (`lam_max_cert(G(sigma_i) - GEX, T)`), eps_i, a_lo/nu0
and the pass-1 Rayleigh quotients, for rows 085, 089 and 091.

**Integer tests.** Every rational matrix is cleared to integers by its positive common denominator. Inertia is computed
from fraction-free Bareiss leading minors. Every division is checked exact and every minor must be nonzero; neg is the
number of sign changes in (1, D_1, ..., D_p) (Sylvester-Jacobi). PD means every minor is positive. A square-root bound
`u >= sqrt(x)` is tested as `u >= 0` and `u.n^2 x.d >= x.n u.d^2`. Every comparison is cross-multiplied. The full
check catalogue is in HBP rows 030-065. An independent C++17 checker, with its own integer type on
`std::vector<uint32_t>` limbs and no floating type, replays all of them from the printed hats (check `REPLAY_CPP`).
C++17 integers are one of the three toolchains CONTEXT.md allows. An earlier draft named Go `math/big.Int`, which it
does not allow.

**Integer form of LO, for the sign audit (check `LO_LE_UP`).** Write `tau = a/b` and `gamma0 = g/d0` with b, d0 > 0,
so `gamma0 - tau = (g b - a d0)/(b d0)`, and `g b - a d0 > 0` by I0. Let K be the least positive integer for which
`Uhat = K U0`, `That = K T` and `Ghat(a,b) = K b^2 G(a/b)` are all integer matrices. K is computed from the rational
matrices themselves, never from a scale typed by hand. (The engine prints U0 at scale D S^2, T at S^2, and G(z) is
built by (4.1) from parts at scales (D S)^2, D S^2 and S^2, with the denominators of a/b and z*.) Then exactly

    K b (g b - a d0) LO(a/b) = (g b - a d0)(b Uhat - a That) - d0 Ghat(a,b).

The driver clears its own rational LO matrix (the one whose inertia it reports) by `K b (g b - a d0)` and checks the
identity entry by entry in integers. It also checks `g b - a d0 > 0`, `diag(Ghat) >= 0` and `neg LO >= neg UP` at every
tested tau. A flipped sign breaks the identity unless Ghat = 0.

## 10. Error budget

Per unit T-norm, with `Gamma_i = gamma0 - upsilon_i` (about 24.1 at r = 9, CONJECTURE), the terms are:

| term | formula | size at r = 9 (CONJECTURE) |
|---|---|---|
| perturbation | `eps_i = g_i / Gamma_i` | `[3.3e-6, 1.25e-5]` |
| sines | `s_i ~ sqrt(eps_i beta_i)/delta_i <= eps_i/delta_i` (rho_i ~ 1e-30) | delta_1 ~ 0.0397, delta_2 ~ 0.0203 |
| angular | `s1 n21 + s2 n12 + s1 s2 nubar` | about `(g/24.1)(5.75/0.0397 + 3.0/0.0203) = 12.1 g` before the beta < g gain; `[5e-4, 2.0e-3]` for the primary min(Lemma 7, 7') |
| window | `(w1 + w2) ybar` | below 1e-6 |
| remainder, adjoint | `2 sqrt(h g)/24.1 + o_inf g/24.1^2` | ≤ 2e-4 (an estimate: the adjoint route was not smoke-tested before the freeze, and h is OPEN until measured; X7 decides the reported route, HBP row 094) |
| remainder, Y = 0 | `2 sqrt(o g)/24.1 + o_inf g/24.1^2` | `[2.3e-3, 5.0e-3]` |
| normalisation | `(1 + taubar1)(1 + taubar2)` | ≤ 1.002 |
| isolation margins | sufficient, not necessary: LO at tau2 passes if `eps(tau2) < kappa3 - tau2 ~ 0.010`, and I3 if `eps_odd < E_odd - tau2 ~ 0.010`. The tests use G(tau) itself, not g T, so they can pass with a larger eps (section 11) | the sufficient margin holds when g ≲ 0.24, that is at depths 3 to 5 at r = 9 |

**Correction to the math lane's budget.** That budget used n21 ≈ n12 ≈ 3, which gives 9.3 g for the angular term. With
c ≈ <O>_1, n21 ≈ 5.75, so the formula gives 12.1 g at r = 9. The smoke shows that the beta < g gain brings the measured
value to 11.1 g at r = 10.5 (formula 14.3 g there). The c rule matters little: at r = 10.5, depth 5 and the default z*,
the ground rule gives an angular term of 6.10e-4, against 4.94e-4 for the midpoint of <O>_1 and <O>_2 and 4.84e-4 for
c = 5. With the midpoint z*, s2 ≈ 2 s1, and the ground and mean rules differ by about 4% (estimate). The frozen rule
stays the math lane's validated ground rule.

**Excluded-r smoke (MEASURED; Y = 0; default z* = 72 - 18/r - 3/r^2; c by the ground rule; floor
gamma0(r) = 94.070673 + 3(r - 9) by Weyl with M ≥ 3, so conditional on #131; this is the run's gamma0 at excluded r
under check FLOOR_PIN, HBP rows 010 and 041).** Source:
`synth/out/smoke_noadj_ground.txt` (afe72c516847a655). Each entry is a_lo with Lemma 7 / a_lo with min(Lemma 7, 7').
"refused" means a_lo ≤ 0.

| r | depth 3 | depth 4 | depth 5 | nu0, depth 5 | k_c, depth 5 |
|---|---|---|---|---|---|
| 10.5 | refused (-0.1918 / -0.1005) | 0.016626 / 0.019392 | 0.027029 / 0.027289 | 0.029008 | 1.439 |
| 12 | refused (-0.0851 / -0.0407) | 0.020546 / 0.021602 | 0.024851 / 0.024951 | 0.025649 | 1.429 |
| 14 | refused (-0.0284 / -0.0086) | 0.020281 / 0.020631 | 0.021838 / 0.021873 | 0.022128 | 1.421 |
| 16 | -0.0062 / 0.003676 | 0.018652 / 0.018787 | 0.019298 / 0.019313 | 0.019423 | 1.416 |
| 20 | 0.007279 / 0.010436 | 0.015399 / 0.015427 | 0.015548 / 0.015552 | 0.015581 | 1.410 |
| 40 | 0.007558 / 0.007650 | 0.007806 / 0.007807 | 0.007808 / 0.007808 | 0.007809 | 1.433 |

At every excluded r and every depth ≥ 2, every isolation test passes (I0-I3, windows and neighbours). At depth 1,
I1_LO, I2_LO, I3 and W2 fail. At depth 2 only the amplitude tests fail (and F2_sine at r = 10.5 and 12). The depth-1
main term is 0 to rounding, which is PR #148 row 16. At depth 5 the I3 form value LO_odd(tau2) is 3.08e-2 at
r = 10.5 and 2.28e-2 at r = 12. Divided by T_odd ≈ 4.17, that is an energy margin of about 7.4e-3 at r = 10.5. At
depth 2 it is much smaller: 3.54e-3 at r = 10.5 and 1.32e-3 at r = 12 (2.90e-2 at depth 3 and 3.07e-2 at depth 4, at
r = 10.5). I3 is the tightest isolation test at depth 2, and its depth-2 values are not monotone in r (1.32e-3 at
r = 12 is below 3.54e-3 at r = 10.5). Wherever F_GAP fails in the smoke file (depth 1 at every r, depth 2 at r = 10.5
and 12), the a_lo values it prints are not bounds; the frozen driver does not compute them (section 7).

**Midpoint z* (MEASURED).** I ran the engine again at r = 10.5 and r = 12 with z* at the pass-1 midpoint, within 1e-6
of the rule (`synth/out/zmid_r10p5.txt`, `zmid_r12.txt`). Then g_1 = g_2:

| r, depth | g | angular (Lemma 7) | e_a, Y = 0 | nu0 | a_lo (L7 / min) |
|---|---|---|---|---|---|
| 10.5, 4 | 6.175e-4 | 7.047e-3 | 4.976e-3 | 0.029044 | 0.016989 / 0.019606 |
| 10.5, 5 | 3.160e-5 | 3.519e-4 | 1.123e-3 | 0.029008 | 0.027521 / 0.027647 |
| 12, 4 | 2.113e-4 | 2.747e-3 | 2.211e-3 | 0.025660 | 0.020683 / 0.021683 |
| 12, 5 | 9.634e-6 | 1.295e-4 | 4.716e-4 | 0.025649 | 0.025043 / 0.025093 |

**r = 9 sizes (CONJECTURE).** The exterior lambda_max(G, T) at depth 5 scales as about r^-10.2 between 10.5 and 12,
which gives 1.1e-4 to 1.3e-4 at r = 9. The inner term is `(gap21/2)^2 X^T W X ~ (0.0199)^2 x 0.0596 = 2.4e-5`. So
g ∈ [8e-5, 3e-4]. The adjoint amplitude a_lo is nu0 minus the angular term minus the adjoint remainder, over the
normalisation: [0.0325 - 0.0020 - 0.0002, 0.0337 - 0.0005]/[1.002, 1], about [0.0302, 0.0332]. Rounded outward, this
is the frozen window [0.0295, 0.0333] (HBP row 085). Without the adjoint: [0.0254, 0.0309], frozen as [0.024, 0.031].

## 11. Depth choice and the depth ladder

* **Verdict rule (HBP row 131).** One build gives depths 2 to 5. Depth 5 is the verdict depth; depths 2, 3 and 4 are
  ladder entries. At a ladder depth every check is evaluated and reported, but no outcome stops the run, sets a
  verdict or reports a bound. Run-integrity checks (pins, census, detailed balance, identities, square-root
  directions, replay, scope, and the independent regeneration of section 15.3) refuse the whole run at any depth.
  Such a FAIL takes effect at the end of the program step in which it occurs, after every check of that step has
  printed its row, and a fault run always reaches the step that runs its named check (HBP header line 10, row 131).
  The one exception is FREEZE_PIN (HBP rows 030, 113): it is a program step of its own, the first step of the engine
  and of the driver, and its FAIL, once its own CHECK row is printed, stops the program at once, before any other
  step or any arithmetic, in every run, fault runs included. Neither clause ever delays it, and PF17 is refused by
  that FAIL. Without the step-end rule, F_GAP's expected failure at depth 2 would stop the single r = 9 run before
  depth 5 was evaluated.
  The output gate A_FROM_THEOREM judges only the one row labelled BOUND, so a ladder-depth row (LADDER) or a row of
  the non-reported route (INFORMATIVE) can never fail it, and a sub-row that the F_GAP gate leaves NOT_EVALUATED is
  reported, not counted as a FAIL.
* **Isolation.** `eps(tau2) < 0.010` is a sufficient margin, not a necessary one: LO uses G(tau) itself, and the
  uniform bound g T need not be tight in the direction that decides the count. At r = 10.5, depth 2, I2_LO passed
  with eps = 0.0111, above `(kappa3 - kappa2)/2 = 0.0071`. The tightest isolation test at depth 2 was I3_ODD (section
  10). At r = 9, depth 2,
  g ≈ 0.6 (extrapolated 0.51-0.55 per unit, times k_c ≈ 1.08), so eps ≈ 0.025. The depth-2 isolation outcome is
  therefore not predicted. What is predicted (HBP row 133) is that F_GAP fails at depth 2: mu_2 leaves the gap or
  the Lemma-7 sine reaches 1, as it already does at r = 10.5 (3.49) and r = 12 (1.10). So the depth-2 entry is not
  PASS and its a_lo is not evaluated. An earlier draft predicted "HOLD at depth 2 because I2_LO fails"; that mechanism
  is withdrawn. At depth 3, g ≈ 0.03-0.04 and eps ≈ 1.6e-3, and isolation is predicted to pass at depths 3, 4 and 5
  (HBP rows 076 and 132).
* **Amplitude** at depth 3: the angular term (about 11 g ≈ 0.4) exceeds nu0, so the bound is refused. At depth 4:
  g ≈ 2.1e-3 to 2.5e-3, angular term (min) ≈ 0.015 to 0.018, so a_lo ≈ 0.012 to 0.02, frozen as [0.006, 0.024]. The
  sign without the adjoint at depth 4 is not predicted. Depth 5 is the primary depth.
* **Y on m = n = 5 shells.** This costs one more 7-column Gauss-Seidel sweep set on the same graph, and needs no
  shell 7. (The engine prototype solved Y on n+1 shells. That would need the shell-7 exterior of 9,398,188 classes and
  about 6.5 GB.)
* **Reported route.** The adjoint route was never smoke-tested before the freeze, so its h_i and its remainder
  (≤ 2e-4) are estimates. X7, after the freeze and before any r = 9 run, runs it at r = 10.5 and 12. If X7 finds the
  adjoint DEFECTIVE (a FAIL in H_WINDOW, Y_PD or ADJ_CONSISTENCY, a run that does not complete, or a min-form a_lo
  below the secondary route's), the secondary route (Y = 0) is the reported route at r = 9. The primary is still run
  and printed INFORMATIVE, and owner item 3 is HOLD (the HOLD branch of HBP row 068). The switch is recorded before
  the r = 9 run (HBP row 094), and no r = 9 outcome changes it. X7 runs with the row-010 gamma0, the run's gamma0 at
  excluded r.
* **Reported verdict and bound (HBP row 131, frozen table).** The reported verdict is the depth-5 verdict of the
  reported route R. If R is PASS, the one BOUND row is the min-form a_lo^2 of R. If R is HOLD or REFUSE, no row is a
  bound. The other route never changes this, whatever its verdict: its a_lo, a_hi and nu0 are printed INFORMATIVE.
  So, with the primary reported, primary HOLD and secondary PASS gives HOLD and no bound, and the secondary's a_lo is
  printed INFORMATIVE for the owner to rule on. Owner item 3 is HOLD whenever R is the secondary.
* **Fallback.** Depth 6 (exterior shell 7) is pre-declared only if depth 5 is HOLD in both routes, and only after a
  chunked engine is built that stays under 4 GB. No other retuning is allowed after the freeze. The fallback run's
  E3 - E2 cross-check (HBP row 140) is evaluated at its verdict depth 6, when Theorem I passes there (section 15.7).

The sector sizes are MEASURED and r-independent. Symmetric classes per shell 0..7: 7, 20, 316, 3,615, 44,071, 393,917,
2,465,466, 9,398,188. Orbits: 8, 264, 7,770, 147,344, 1,985,218, 18,598,040, 117,433,604, 449,755,567. Odd classes per
shell 0..6: 1, 2, 55, 733, 10,282, 100,689, 718,755. The odd shells are those of a signed BFS from the odd flat class:
an edge K -> L exists iff the count of moves from s_K into L, each signed by chi_odd of its canonicalising symmetry, is
nonzero; inadmissible classes (stabiliser not in ker chi_odd) are excluded, and a class reached only through zero
signed counts is not indexed (engine main.rs, `Sector::list_next`; HBP rows 015 and 139). The electric-distance shells
restricted to admissible classes give other counts (1, 2, 159, 2,881 at shells 0-3) and are not the census. The math
lane's guesses for shells 5 and 6 (5.3e5 and 6e6) and for shell 7 (7e7) are superseded.

**Sector scope of the move tallies (HBP rows 035-038, 098 and 134 (c)).** The 72-move tallies of EXT_REGEN (c) and of
C0_EXTERIOR_COMPLETE (row 037) apply to the symmetric sector only. In the odd sector the chi_odd-signed counts can
cancel, and inadmissible or zero-signed-count targets are not stored (`Sector::list_next`, which skips its own 72-move
assertion there), so no 72-move tally applies. There C0_EXTERIOR_COMPLETE requires, at every depth n and in every
aggregation call of the odd sector, that every stored edge out of odd shell n carries a nonzero signed count and an
admissible target and lands in odd shells n-1 to n+1, and that every odd shell-(n+1) class (718,755 at n = 5) enters
the odd exterior scalar. That is what the engine's `residual()`, which `solve_depth` calls for either sector,
aggregates in the odd sector: the stored signed counts of the odd shell-n lists, with the division by W_e checked
exact. MOVES72 counts the 72 raw enumerated moves before signing, in both sectors (row 036). H1_TWO_SIDED_EXTERIOR
is the symmetric sector's exterior probe (row 035). CENSUS's orbit clauses are the symmetric sector's, and the odd
sector compares its class counts with row 015 (row 038). PF02 is planted in the symmetric sector (row 098).

## 12. Pre-freeze disclosure

This lane (the cloud seat's scout, math, engine and synthesis seats) computed **no r-dependent quantity of the 3x4
model at r = 9**: no X, residual, Schur matrix, eigenvalue, eigenvector, Rayleigh quotient or amplitude. The evidence:
* the engine refuses r ≤ 9 before any arithmetic. The engine lane reported this for `--r 9`, `18/2`, `17/2` and
  `pair 9:..`, and this seat re-ran `run --r 9`, `18/2` and `17/2` and saw the same refusal;
* `smoke_cert.py` refuses r ≤ 9 before any arithmetic (MEASURED);
* the scouts ran at r = 12 and r = 20 only;
* the math toys are other models (the 1x2 and 2x2 lattices and random graphs). `toy_run.py` asserts LX x LY ≤ 4.

Every computation made before the freeze, with sha256 (first 16 hex):

**A. Scouts** (`scout/`; integer Python; r = 12 and 20, plus r-independent counts):
scout.py 9963dc01eb362079, symshells.py c7da9728b5436afc, r12s2.txt 9b15aa72226c3e03, r12s3.txt dff9c0b431d07f60,
r20s3.txt 4ade3296850e41b6, sym4.txt 96d08e1151fc57c4.

**B. Math lane** (`math/`). Every fingerprint in FINGERPRINTS.txt was re-verified (25 of 25 match):
* code: zq.py 83bb9a57bcaa794b, s3lat.py 000e6f6855a9ed8f, fesh.py d39b5d0438e6948b, fesh_v1.py 23ede6dfb6471337,
  toy_run.py 8b08d717d456daac, toy_run_v2.py 4d9d423a9856f60a, toy_run_v3.py 6ecf711379630a4c, toy_graph.py
  e76134ed7bb1c03c, flat3x4.py 48e35d86d061afd4 (r-independent 3x4), probe_sizes.py bf687eb45aad114f and
  probe_time.py 97f6b68f6c077d0f (toy lattices only), summarize.py 9115e2d29df372c5, test_zq.py 79d5fbf4c92fcb85,
  fingerprints.py b5eb5dd3cf83d6fb;
* logs: toy_1x2_r8 63bc8c9d6026cc54, toy_1x2_r8_Ox b9ea7481ee36c814, toy_1x2_r8_zshift 9f0e8664859c2bb8,
  toy_2x2_r9_Ox 795701a1a955176f, toy_2x2_r9_Ox_final 5391d2cddfbcf2c9, toy_2x2_r9_Ox_zshift 9fe8967e7c653209,
  toy_2x2_r9_Osum_scan_partial 52d1634ca13ae65e, toy_2x2_r15_Ox 0a322f39800b17fd, toy_graph_s1 f061a7630e6f9430,
  toy_graph_s1_zshift b7db4384aec55fe2, toy_graph_s2 d3f36a35d7af29b5.

The 2x2 toy at r = 9 is a different Hamiltonian, with 1,393 orbits. It gives no 3x4 quantity.

**C. Engine lane** (`engine/`; Rust 1.81, std only; excluded r = 10.5, 12, 14, 16, 20, 40, plus the r-independent
census):
* code and binary: main.rs a8fd4a9b4097b528, Cargo.toml 4faf1f0ddeb27dbb, Cargo.lock befa4fe902db6961, binary
  ym137engine 8622337d99a30dae, analyze.py a6dff6c5bdb53180, analyze_pair.py f29bbaa2992aebf7, extrapolate.py
  cb24405b70977a60, xcompare.py fb61a211ffbc3aae, scout_fullgram.py b0fc384a5478619a;
* outputs: main_d5 5787e592aba61409, odd_d5 2f50432ecd070079, pair_d5 6f68b914383fa8fc, pair_spec 8c70e6871ab3d5ef,
  smoke_r20_d3 eda50292e872c07d, xcheck_r20_n2 56bb22fa147b727d, xcheck_r20_n3 c2cc5f4f5f370a29, py_r20_s2
  85b836e3ca66d9d7, py_r20_s3 e4b5106c883b4cca, depth_r12_d2..d5 4446cc2f22b7d750 / 6e020a8916078b5a /
  8e222a188933e39f / 62187fb65a8df632, depth_timing_r12 3a25a31742bff67a, census_listed6_probe7 b03974959a67e275,
  analysis_main_d5 e6c678ab556c9e78, analysis_pair_d5 6123a1a09f87834b, analysis_odd_d5 40bb3ac1af5e7224,
  extrapolate_r9_conjecture 4661d68805530aa8 (formula evaluation at 9 from excluded-r fits only);
* reruns: census 60aeafc5233b60b4, main_d5 dc826d0df5ba6dde, selftest 5037da106c67f3ab, xcheck n2 254c341359ee8fae,
  xcheck n3 ca86c7e53a426147.

**D. Synthesis seat** (`synth/`; integer Python with `python3 -I -B`, and the same engine binary; excluded r only):
* smoke_cert.py 9c033df34e816d17. An earlier version, 402f7cafeece4822, produced the first grid; every output it wrote
  was regenerated by the final version.
* outputs: smoke_noadj_ground afe72c516847a655 (all 6 excluded r, depths 1-5), smoke_noadj_zmid_r10p5 f34e83656d3478bb,
  smoke_noadj_zmid_r12 416f875b010309a1, smoke_noadj_cmid 553a4e5d15984097, smoke_noadj_c5 c192d00a08341134.
* engine runs: zmid_r10p5.txt 83df60e52eaf2e4f (`run --sector sym --r 21/2 --zshift -20532/1000000 --mindepth 4
  --maxdepth 5 --c 5 --adjoint 0 --threads 3`) and zmid_r12.txt 1d6a02456ac392f1 (`--r 12 --zshift -13498/1000000`).
* check_hbp.py 5555a3ec0262bad7 audits the text of the prediction file only (format, tags, ids, cross-references,
  falsifier reachability and END counts); it does no model arithmetic. On the pass-2 file (sha256
  40d3255e6cfd068551bd0a90bc239ceec2a251d054b281e6c615c7fcaccf4030, 133 rows) it reported ERRORS 0 and no
  unreferenced check (output ab70ea1512ef1173; the pass-1 file b121f51c86d5824f gave the same counts). Fix pass 3
  added two row sections (audit, negctl) that it predates, so its successor check_hbp_v3.py (below) is the record
  checker of the file frozen with this NOTE.
* fix seat (second synthesis pass): kappa7_path.py 4390e53c64387a3a, output kappa7_path_r10p5_r12.txt
  a6b312d4e2ff233e (r = 10.5 and 12, depths 2 and 5). It tests the kappa1..kappa7 measurement path of ENGINE-PLAN D7
  on the existing main_d5.txt hats, and runs no engine. lo_identity_toy.py 2b0b6512807a8cef, output
  lo_identity_toy.txt 6711bd4dbd83b011: an algebra check of the cleared-denominator LO identity of section 9 on random
  rational matrices (no model data, no r); it holds on 4,500 entries, and a flipped sign breaks it. The rule constant
  `72 - 18/9 - 3/81 = 5667/81` was checked in Python ints; it is the formula's input, not a quantity of the model.
* fix seat, pass 2: fixpass2_check.py bcc65f7d9ad1bc5d, output fixpass2_check.txt 2131bfa21fa5e3df. A text audit of
  the three X6 reference files (smoke_noadj_ground, smoke_noadj_zmid_r10p5, smoke_noadj_zmid_r12); it runs no engine
  and no certificate. All 34 SMOKE rows print the row-010 floor `94070673/10^6 + 3(r - 9)`, recomputed as an exact
  integer pair (98570673/10^6 at r = 10.5, 103070673/10^6 at r = 12); at r = 9 the formula gives 94070673/10^6. It
  lists fesh's raw ok, tests and fail per RESULT row (fail = 10 at depth 1 at every r, 3 at depth 2 at r = 10.5 and
  12), confirms that F_GAP fails exactly at depth 1 for every r and at depth 2 for r = 10.5 and 12, and that all 27
  TEST rows PASS at r = 12, depth 4 in both files (the Y = 0 control of the r = 12 fault runs).
* verifier tools and re-runs between pass 2 and pass 3 (other seats; text audits, rule constants and excluded-r
  re-runs only; none computes anything at r = 9): verify2/audit_hbp.py b1fdc8b507f85cd2; verify2/check_hbp_rerun.txt
  and chk_rerun.txt 4020c41c457dd01d; verify2/kappa7_rerun.txt a6b312d4e2ff233e (r = 10.5 and 12, byte-identical to
  the disclosed kappa7 output); verify2/lo_rerun.txt 6711bd4dbd83b011; verify3/v3_ints.py 8158db5d10b03cf4 with
  output v3_ints.txt 71fe7048cee6220e; verify3/ and verify3b/ audit_hbp_v3.txt 3ffd41a13e81a5b8, check_hbp_v3.txt
  ab70ea1512ef1173 and fixpass2_check_v3.txt 2131bfa21fa5e3df.
* fix seat, pass 3 (no r, no engine, no certificate, no model data):
  * synth/negctl_gpt6.py 548f71564ee73803, output synth/out/negctl_gpt6.txt 3c10e20a2c1f01e9: GPT-6's two toy
    counterexamples only (a 2x2 and a 3x3 rational matrix; section 15.8).
  * the pass-3 HBP file: sha256 7e66d03f7324bef0466e034bdf31a8c8d1dac44af42bb252e0e4f1d949df7d2d
    (83,694 bytes, 166 lines, 151 rows). synth/check_hbp_v3.py 5de113afe7cac7d7 on it: ERRORS 0; 38 checks, which row
    131 partitions into 20 run-integrity and 18 route certificate checks; 20 faults; 6 audit and 2 negctl rows; both
    receipt pins verified against the files on disk; no unreferenced check (output check_hbp_v3_pass3.txt
    bbcd6aa2b81ad761). The original check_hbp.py on it reports only the 8 rows of the two new sections as "bad sec"
    (output 3b12ca817d388a3b). As a control, check_hbp_v3.py on the pass-2 file reports 21 errors: no audit row, no
    citation of the comment, and the old "FAIL or missing" fault verdicts (output 7c024615d4179070).
  * text-edit tools: synth/pass3_hbp_edit.py 9dba0e46149d1926 with synth/pass3_new_rows.txt 2e9abb47b5cd1777, and
    synth/pass3_plan_edit.py 620dc86993bf3548 (string edits of the HBP and the plan; no arithmetic).
  * read-only reads: git rev-parse, log, ls-tree and cat-file in the finite repo (the #131 floor-source blobs at
    d1385b3 and on origin/main 6a7fc74, and #136's checker on origin/main), and GitHub reads of issue #137's comments
    and of PR #131's metadata. No repository or GitHub write.
* round-3 critic and verifiers, between pass 3 and pass 4 (other seats; text audits, toy re-runs, r-independent
  recounts and read-only git and GitHub reads; nothing r-dependent at r = 9): `critic3/` (check_orig.txt
  3b12ca817d388a3b, check_v3.txt bbcd6aa2b81ad761, negctl_run1.txt and negctl_run2.txt 3c10e20a2c1f01e9, diffrows.py
  9f09915b76309b4d, showdiff.py 9649eabfbf33e9dd, showrow.py de6de0e0e1ddd098); `verify4_math/` (negctl_rerun.txt
  3c10e20a2c1f01e9, check_hbp_v3_rerun.txt bbcd6aa2b81ad761, recount_shells.py 0623c708547bae12 with recount_n2.txt
  35a262d19327d726 and recount_n3.txt 4d0d32629c3d135e, recount_odd.py 4a4b7e1580c900b2 with recount_odd_n3.txt
  0cf058d991b9987d, recount_balance.py 4a3732cc4f0790dc with recount_balance_n2.txt 3e7258176d0ba4c5, ints_pass3.py
  b9531021e68ee104 with ints_pass3.txt 14d33d0d5e21afdd); `verify4r/` (v4_ints.py 85b51d6bb6622f01 with v4_ints.txt
  c48c980d9c2ea847, winddiff.py a51907628c50c76c with winddiff_pass1in_to_final.txt c31885244d180d40, audit_hbp.txt
  82fee5a3ede392b0, check_hbp_orig.txt 3b12ca817d388a3b, check_hbp_v3.txt bbcd6aa2b81ad761, negctl_run1.txt and
  negctl_run2.txt 3c10e20a2c1f01e9). The pass-4 fix seat re-hashed every file in the three folders: each matches the
  fingerprint its finding gives, and none differs. One file has no stated fingerprint: verify4_math/recount_n2.time
  3e737f6a9117cec1 (60 bytes, the error line of a missing timing wrapper, no data).
* fix seat, pass 4 (no r, no engine, no certificate; nothing r-dependent at r = 9):
  * fixpass4/ints_pass4.py 18340c08ee028e85, output fixpass4/out/ints_pass4.txt c48c45c27b8f0ca1 (python3 -I -B,
    Python ints): the faults-r12 xext estimate at depth 4 (ENGINE-PLAN section 6) from the census integers of
    engine/out/census_listed6_probe7.txt (b03974959a67e275) and odd_d5.txt (2f50432ecd070079), and the order checks
    of the HBP row-140 constants and of PF18's gamma0 95/1 + 3(r - 9).
  * fixpass4/receipt155_counts.py f564d00deeaf4857, output fixpass4/out/receipt155_counts.txt 1ca9a2f21a7f7e94: reads
    #155's receipt (item F.6 below) on stdin and prints only its thresholds and inertia counts.
  * the pass-4 round-1 HBP file: sha256 50e741782979a13308ede5121bc2076bdec4a45f406e4f8d9037d3295ce62255
    (91,318 bytes, 166 lines, 151 rows). synth/check_hbp_v3.py 5de113afe7cac7d7 (unchanged; no new field type needed
    an extension) on it: ERRORS 0; 38 checks, 20 run-integrity and 18 route certificate; 20 faults; 6 audit and 2
    negctl rows; both receipt pins verified; no unreferenced check (output fixpass4/out/check_hbp_v3_pass4.txt
    fbd3a571cd40234e, identical to the pass-3 output apart from its FILE row). check_hbp.py 5555a3ec0262bad7 reports
    only the 8 rows of the two pass-3 sections as "bad sec" (fixpass4/out/check_hbp_orig_pass4.txt 730abdb907ade929).
    verify2/audit_hbp.py: 151 rows, 38 checks, row 131 splits them 20 + 18 (fixpass4/out/audit_hbp_pass4.txt
    577eda231d0eb7aa).
  * read-only reads: git cat-file, rev-parse and show in the finite repo (the #155 receipt at 30a08260, which was
    present locally, so no fetch); the engine's main.rs (`Sector::list_next`, the selftest). No repository or GitHub
    write.
* round-4 critic and verifiers, between pass 4 round 1 and round 2 (other seats; text audits and diffs, r-independent
  integer checks, an r-independent odd-census recount from the frozen text, and text reads of the excluded-r X6
  reference smoke files; nothing r-dependent at r = 9): `verify5_0_r1/` (hbpdiff.py 59fc1393ff6003f0 with
  hbpdiff_out.txt 896664946571d9d4, ints_v5.py 230c3d7345b17bac with ints_v5.txt ddbf0f5ea13e4bb4,
  odd_text_recount.py dec45609c350d03e with odd_text_recount_n4.txt 108cc626e75fa786 and odd_text_recount_n4.time
  7aa067708c5e6728, engineplan.diff 28d2ae7649c39292, note.diff 76cf147e860b7858, winddiff_pass1in_to_pass4.txt
  c31885244d180d40, check_v3_prefix.txt bbcd6aa2b81ad761, check_v3_final.txt fbd3a571cd40234e,
  check_hbp_orig_final.txt 730abdb907ade929, audit_hbp_final.txt 577eda231d0eb7aa); `verify5_1_r1/` (fielddiff.py
  be78542ce739751d with hbp_fielddiff.txt 8d2d5545251162cc, v5_ints.py 7566d85eac15b538 with v5_ints.txt
  14359b8c1660bf75 (it reads only the W2_LO sigma of smoke_noadj_zmid_r10p5 and smoke_noadj_zmid_r12, excluded r),
  ints_pass4_rerun.txt c48c45c27b8f0ca1, engineplan.diff 28d2ae7649c39292, note.diff 76cf147e860b7858,
  check_hbp_v3_prefix.txt bbcd6aa2b81ad761, check_hbp_v3_final.txt fbd3a571cd40234e, check_hbp_orig_final.txt
  730abdb907ade929, audit_hbp_final.txt 577eda231d0eb7aa). The pass-4 round-2 fix seat hashed every file in both
  folders.
* fix seat, pass 4 round 2 (text edits, no r, no engine, no certificate; nothing r-dependent at r = 9). Inputs kept
  unchanged in `fixpass4r2_prefix/`. One new text tool, fixpass4r2/fielddiff_r2.py f4f199df4edc0418 (python3 -I -B,
  str only), with output fixpass4r2/out/fielddiff_r2.txt 76d1d57a22b8ce2a: header line 10 and rows 128, 131, 139,
  140 and 148 changed, keys and tags unchanged; rows 076-096 and 132-133 and the PREDICTION_END row byte-identical to
  the round-1 file. Record-checker re-runs on the new file, outputs in `fixpass4r2/out/`:
  * the pass-4 round-2 HBP file: sha256 e840b92370315284e3bdfc48133b1d70008db24695796713d0737bb423b50bd7
    (94,239 bytes, 166 lines, 151 rows). synth/check_hbp_v3.py 5de113afe7cac7d7 on it: ERRORS 0; 38 checks, 20
    run-integrity and 18 route certificate; 20 faults; 6 audit and 2 negctl rows; both receipt pins verified; no
    unreferenced check (output check_hbp_v3_pass4r2.txt e538dc02cd527716, identical to the round-1 output apart from
    its FILE row). check_hbp.py 5555a3ec0262bad7 reports only the 8 rows of the two pass-3 sections as "bad sec"
    (check_hbp_orig_pass4r2.txt 16155f27ff3ff862). verify2/audit_hbp.py: 151 rows, 38 checks, 20 + 18
    (audit_hbp_pass4r2.txt 3a25898056eaaf2e, identical to the round-1 output apart from its sha256 line).
* round-4 verifier `verify5_0_r1/`, its own disclosure (python3 -I -B, integers and str only, no r and nothing at
  r = 9, writes only in its folder): synth/check_hbp_v3.py 5de113afe7cac7d7 on the round-1 HBP 50e74178 ->
  check_v3_final.txt fbd3a571cd40234e (ERRORS 0, 151 rows, 38 checks 20 + 18, byte-identical to fixpass4/out) and on
  the pass-3 HBP 7e66d03f -> check_v3_prefix.txt bbcd6aa2b81ad761 (differs only in its FILE row); synth/check_hbp.py
  5555a3ec0262bad7 -> check_hbp_orig_final.txt 730abdb907ade929 and verify2/audit_hbp.py b1fdc8b507f85cd2 ->
  audit_hbp_final.txt 577eda231d0eb7aa, both identical to the fix seat's outputs; verify4r/winddiff.py
  a51907628c50c76c, pass-1 input to round 1 -> winddiff_pass1in_to_pass4.txt c31885244d180d40 (identical; no window
  changed); its own hbpdiff.py 59fc1393ff6003f0 -> hbpdiff_out.txt 896664946571d9d4 (only header line 10 and rows
  015, 063, 128, 131, 134, 136, 138, 139, 140, 143, 144 and 149 changed, with no tag, on_fail or prediction row
  changed); text diffs engineplan.diff 28d2ae7649c39292 and note.diff 76cf147e860b7858 (CHANGES a byte-identical
  prefix plus the appended pass-4 section); its own odd_text_recount.py dec45609c350d03e, the frozen signed-BFS
  definition implemented from the text (own S3 table, tree gauge fixing and 48 maps; a first version tested
  admissibility on the canonicalising coset instead of the stabiliser, was fixed, and its output discarded) ->
  odd_text_recount_n4.txt 108cc626e75fa786 (time 7aa067708c5e6728, 180 s): symmetric 7, 20, 316, 3615, 44071;
  electric-distance admissible 1, 2, 159, 2881, 40973; signed-BFS odd 1, 2, 55, 733, 10282, matching rows 014, 015
  and 139; its own ints_v5.py 230c3d7345b17bac -> ints_v5.txt ddbf0f5ea13e4bb4 (the depth-4 xext counts 32,617,368
  and 364 s, memory terms, the row-140 orders, PF18 gamma0 104/1, Burnside 2,177,317,873, and 2,420 s > 30 min);
  sha256 of the four package files (equal to the fix seat's), CONTEXT ec1f0dd7, FINDINGS 64dee19c, every file in
  critic3, verify4_math, verify4r and fixpass4 (all equal to this section), engine main.rs a8fd4a9b4097b528, census
  b03974959a67e275 and odd_d5 2f50432ecd070079. Read-only: git status in the finite repo (clean), main.rs lines
  340-629, and the SHELL rows of census and odd_d5 (excluded-r file). Not opened: refute155/, any PR #155 tree file,
  the evidence folder. No repository or GitHub write.
* round-4 verifier `verify5_1_r1/`, its own disclosure (python3 -I -B, ints and str only; nothing r-dependent at
  r = 9; writes only in its folder): sha256 of final/ as round 1 left it (HBP 50e741782979a133, NOTE
  bd9778be87f8c8ef, ENGINE-PLAN ae9785c7c4500b57, CHANGES 40e2bae804746224), of fixpass4_prefix/ (7e66d03f, e9328a7a,
  729042ba, dd694951), CONTEXT ec1f0dd730696ee9, FINDINGS 64dee19c42ba343d, the 28 files of critic3/, verify4_math/
  and verify4r/ (all equal to this section) and fixpass4/ (ints_pass4.py 18340c08ee028e85, receipt155_counts.py
  f564d00deeaf4857 and 5 outputs equal to CHANGES); its own fielddiff.py be78542ce739751d -> hbp_fielddiff.txt
  8d2d5545251162cc (header line 10 plus rows 015 063 128 131 134 136 138 139 140 143 144 149 only; no tag, on_fail or
  prediction row changed); diff -> engineplan.diff 28d2ae7649c39292 and note.diff 76cf147e860b7858;
  synth/check_hbp_v3.py 5de113afe7cac7d7 -> check_hbp_v3_final.txt fbd3a571cd40234e (ERRORS 0, byte-identical to the
  fix seat's) and check_hbp_v3_prefix.txt bbcd6aa2b81ad761; synth/check_hbp.py 5555a3ec0262bad7 ->
  check_hbp_orig_final.txt 730abdb907ade929 and verify2/audit_hbp.py b1fdc8b507f85cd2 -> audit_hbp_final.txt
  577eda231d0eb7aa (both identical); ints_pass4.py re-run -> ints_pass4_rerun.txt c48c45c27b8f0ca1 (identical); its
  own v5_ints.py 7566d85eac15b538 -> v5_ints.txt 14359b8c1660bf75 (the W2_LO sigma2 of the excluded-r smoke files
  r10p5 f34e83656d3478bb and r12 416f875b010309a1, the xext census and memory sums, the PF18 orders, the row-139
  budget). Text reads: engine main.rs a8fd4a9b4097b528 (Sector::new, list_next, moves, info); the SHELL rows of
  census b03974959a67e275 and odd_d5 2f50432ecd070079; the Theorem-I and W2 TEST rows of three excluded-r smoke
  files; and fixpass4/out/receipt155_counts.txt 1ca9a2f21a7f7e94, which holds #155 thresholds and counts only.
  Read-only git calls, with no content of any PR #155 file: status --porcelain under GIT_OPTIONAL_LOCKS=0 (0 lines);
  rev-parse of d1385b3 and 30a08260; the receipt's tree entry, blob f4e08a31 and its size 9535; and the floor-source
  blobs 53378d4e and cbd42801 (17,241 and 44,107 bytes, sha256 41b9602f and de19b354, one RESULT_PERRON_3x4_TOP row).
  Not opened: refute155/ and independent/y137-evidence-20261109/. No repository or GitHub write.
* verifier of pass 4 round 2 `verify5_0_r2/`, its own disclosure (python3 -I -B, str and Python ints only, no r,
  nothing r-dependent at r = 9, no engine or certificate run, writes only in its folder): synth/check_hbp_v3.py
  5de113afe7cac7d7 on the round-2 HBP e840b92370315284 -> check_v3_final.txt e538dc02cd527716 (ERRORS 0) and on the
  fixpass4_prefix HBP 7e66d03f7324bef0 -> check_v3_prefix.txt bbcd6aa2b81ad761; synth/check_hbp.py 5555a3ec0262bad7
  -> check_hbp_orig_final.txt 16155f27ff3ff862 (exit 1, only the 8 known pass-3 "bad sec" rows); verify2/audit_hbp.py
  b1fdc8b507f85cd2 -> audit_hbp_final.txt 3a25898056eaaf2e; its own fdiff.py b6dab4d66c49e5e3 ->
  fdiff_prefix_to_final.txt 53f53e72fca2be5f, fdiff_r1_to_final.txt 3028b59cca078012 and fdiff_pass1in_to_final.txt
  a1f178abb354bb3d; its own ints_r2.py e453bacf1f92c1ee on engine/out/census_listed6_probe7.txt b03974959a67e275 and
  engine/out/odd_d5.txt 2f50432ecd070079 -> ints_r2.txt 80a64f1235a741c0; GNU diff of NOTE, ENGINE-PLAN and CHANGES
  as round 2 left them against fixpass4_prefix -> 684d5c62ebb01c21, 0212ade4a7a63a5a, 2550a870eb67d234 and against
  fixpass4r2_prefix -> 44ada9b3e7f72468, 6ef6cb9405cf86e7, dcf8c0d0d8e9b6e9; sha256 of the 4 final files, the 8 files
  of both prefix folders, CONTEXT.md ec1f0dd730696ee9, the 53 files of critic3, verify4_math, verify4r, verify5_0_r1
  and verify5_1_r1, and the fixpass4 and fixpass4r2 scripts and outputs. Text reads only: engine/rs/src/main.rs
  a8fd4a9b4097b528 (Sector::new, list_next, Tab::info, Tab::moves, selftest), the four SMOKE and
  TEST|W2_LO_count_sigma_le_1 rows of synth/out/smoke_noadj_zmid_r10p5.txt and smoke_noadj_zmid_r12.txt (excluded r
  only), fixpass4/out/receipt155_counts.txt 1ca9a2f21a7f7e94 (thresholds and inertia counts only), and the round-4
  ints and odd-recount outputs. Nothing fetched, no git command, no repository working tree or GitHub access;
  refute155/, the PR #155 tree and independent/y137-evidence-20261109/ not opened.
* verifier of pass 4 round 2 `verify5_1_r2/`, its own disclosure (python3 -I -B, str and Python ints only, no float,
  nothing r-dependent at any r, no engine or certificate run, writes only in its folder): sha256 of final/,
  fixpass4_prefix/ and fixpass4r2_prefix/, of every file in verify5_0_r1, verify5_1_r1, fixpass4, fixpass4r2,
  critic3, verify4_math and verify4r, and of CONTEXT.md, wf_design.js and FINDINGS.md -> hash_folders.txt
  0834af90090dc53c (all equal to this section's values); its own hbpdiff_r2.py 01350de254975680 -> hbpdiff_vs_fp4.txt
  ab07f826e9888307 and hbpdiff_vs_fp4r2.txt da0a510a135dea46; its own showfields.py 8e67212760499c68 ->
  predrows_pass1in_to_final.txt e6baf4dad01fc115 (plus screen views of the changed rows); re-runs of
  synth/check_hbp_v3.py 5de113afe7cac7d7 -> check_v3_final.txt e538dc02cd527716 (ERRORS 0) and check_v3_fp4.txt
  bbcd6aa2b81ad761, synth/check_hbp.py 5555a3ec0262bad7 -> check_orig_final.txt 16155f27ff3ff862 and
  verify2/audit_hbp.py b1fdc8b507f85cd2 -> audit_final.txt 3a25898056eaaf2e; diff(1) outputs engineplan_vs_fp4.diff
  0212ade4a7a63a5a, note_vs_fp4.diff 684d5c62ebb01c21, changes_vs_fp4.diff 2550a870eb67d234, engineplan_vs_fp4r2.diff
  6ef6cb9405cf86e7, note_vs_fp4r2.diff 44ada9b3e7f72468 and changes_vs_fp4r2.diff dcf8c0d0d8e9b6e9; its own
  ints_v5r2.py f66412527ca9f73e -> ints_v5r2.txt bc7691bd38bfb5bc (r-independent census integers from census
  b03974959a67e275 and odd_d5 2f50432ecd070079, rows 014, 015 and 139, the xext depth-4 moves and memory, Burnside
  2177317873, order checks of the row-140 and PF18 constants). Read-only git in the finite repo (no fetch, working
  tree clean): rev-parse of HEAD, d1385b3 and origin/main; sha256 and blob ids of PERRON-BOUND.md (41b9602f/53378d4e)
  and PERRON-RESULT.hbp (de19b354/cbd42801) at d1385b3, and the same on origin/main 6a7fc74; for #155 only
  `git ls-tree -l 30a08260 independent/Y137-K3-SECTOR-ISOLATION.hbp` (blob f4e08a31, 9535 bytes; content not read).
  Text reads: engine main.rs a8fd4a9b4097b528, the odd_d5 and census SHELL rows, the verify4_math recount outputs and
  the `verify5_*_r1` integer outputs (excluded-r only). Not opened: scratchpad/refute155/, the #155 evidence folder
  and the rest of the #155 tree. No repository or GitHub write.
* close seat, after pass 4 round 2 (text splice only; no r, no engine, no certificate; nothing r-dependent at r = 9;
  writes only in `close/`). It spliced the four verifier entries above into this section and updated the NOTE
  fingerprint in CHANGES (PASS 4, round 2). Files: close/lines_raw.txt 787b7d8c25139faf (the four entries, one line
  each); close/wrap.py 5b1d3ed9699b0f48 (textwrap at 117 columns, str only) -> close/lines_wrapped.txt
  7c0803a299c64188; close/splice.py cef48c6dc7933d73 (inserts that block before item E at one asserted anchor); the
  inputs kept unchanged as close/NOTE.before c716482af46cc306 and close/CHANGES.before 622bc481096fb985 (the round-2
  NOTE and CHANGES); and a re-run of synth/check_hbp_v3.py 5de113afe7cac7d7 on the round-2 HBP e840b92370315284 ->
  close/check_hbp_v3_close.txt e538dc02cd527716 (ERRORS 0, byte-identical to the round-2 output).
* fix seat, pass 5 (text edits; no r, no engine, no certificate; nothing r-dependent at r = 9). Inputs kept unchanged
  in `fixpass5_prefix/` (HBP e840b92370315284, NOTE 3832eb4206ab45cf, ENGINE-PLAN 1620c0bb1137fdd6, CHANGES
  2f1126740dbe971a). Tools (python3 -I -B, str only): fixpass5/pass5_edit.py 4d90c5212166ae8e (18 exact HBP and 8
  ENGINE-PLAN string edits, each asserted to occur once; output fixpass5/out/pass5_edit.txt fae17a745fbe65f4) and
  fixpass5/fielddiff_p5.py bb5c0557ac5e8ed3 -> fixpass5/out/fielddiff_p5.txt 1fa2e34d12024140 (rows 035, 036, 037,
  038, 068, 098, 128, 140 and 148 changed; no key removed and no id, sec, tag, check, on_fail, fault or refused_by
  changed; rows 076-096 and 132-133 and the PREDICTION_END row byte-identical to the input). The NOTE and CHANGES
  were edited by hand. Text reads: engine main.rs a8fd4a9b4097b528 (lines 340-960 and 1100-1420: Tab::info,
  Tab::moves, Sector::new, list_next, detailed_balance, system, residual, probe, solve_depth, run); the BUILD,
  DETAILED_BALANCE and SHELL rows of engine/out/odd_d5.txt 2f50432ecd070079 (r-independent rows); the files of
  `close/`. Every file of verify5_0_r1, verify5_1_r1, verify5_0_r2, verify5_1_r2 and close was hashed: each
  fingerprint above matches its file. close/wrap.py, re-run on close/lines_raw.txt to stdout, reproduces
  close/lines_wrapped.txt, and that block is in this section. Record-checker re-runs on the new file, outputs in
  `fixpass5/out/`:
  * the HBP file frozen with this NOTE: sha256 0b97fa83c02e94e78605f64f3086cd0a75d6af61f4e420b2f92cf3b8d454a55e
    (98,234 bytes, 166 lines, 151 rows). synth/check_hbp_v3.py 5de113afe7cac7d7 on it: ERRORS 0; 38 checks, 20
    run-integrity and 18 route certificate; 20 faults; 6 audit and 2 negctl rows; both receipt pins verified; no
    unreferenced check (output check_hbp_v3_pass5.txt 9c19f2a4072dd5dd, identical to the round-2 output apart from
    its FILE row). check_hbp.py 5555a3ec0262bad7 reports only the 8 rows of the two pass-3 sections as "bad sec"
    (check_hbp_orig_pass5.txt 37cabbc8d448e764). verify2/audit_hbp.py: 151 rows, 38 checks, 20 + 18
    (audit_hbp_pass5.txt 9dffb3f5e60f78dc, identical to the round-2 output apart from its sha256 line).
  No repository, git or GitHub access. Not opened: scratchpad/refute155/, the #155 tree and
  independent/y137-evidence-20261109/.
* verifier of pass 5 `verify6_0_r1/`, its own disclosure (python3 -I -B, str and ints only, no r, nothing r-dependent
  at r = 9, no engine or certificate run, no git, repository or GitHub access, writes only in verify6_0_r1/): sha256
  of the 4 final/ files (0b97fa83c02e94e7, 8c5f2e3d6b8df8a6, ad44841a80892fe6, d8cd61e081e9749a), of the 4
  fixpass5_prefix/ files (e840b92370315284, 3832eb4206ab45cf, 1620c0bb1137fdd6, 2f1126740dbe971a), of
  synth/check_hbp_v3.py 5de113afe7cac7d7, engine/rs/src/main.rs a8fd4a9b4097b528, and of 21 files cited in NOTE 12.D
  (close/*, fixpass5/*, verify5_0_r2/*, verify5_1_r2/*, engine/out/odd_d5.txt 2f50432ecd070079; all match);
  synth/check_hbp_v3.py on the final HBP -> check.txt 3c7298cbd5731f36 and check_stdout.txt 3c7298cbd5731f36 (no root
  arg, ERRORS 0), check_stderr.txt (empty) and, with root arg, check_root.txt 9c19f2a4072dd5dd (ERRORS 0, identical
  to fixpass5/out/check_hbp_v3_pass5.txt); GNU diff of the HBP vs fixpass5_prefix -> hbp.diff 63997b624115062b; GNU
  diff of NOTE and ENGINE-PLAN vs fixpass5_prefix (to screen); my own fielddiff.py d279ab13f1b3173c (to screen); text
  reads only of CONTEXT.md, FINDINGS-PASS4R2.md, main.rs (lines 350-431, 494-686, 825-875, 1116-1180, 1328-1350,
  1558-1570) and the BUILD/DETAILED_BALANCE/SHELL rows of engine/out/odd_d5.txt; refute155/, the PR #155 tree and
  independent/y137-evidence-20261109/ not opened.
* verifier of pass 5 `verify6_1_r1/`, its own disclosure: computations, all r-independent (python3 -I -B on str only,
  no r, no engine or certificate, nothing at r = 9, writes only in ym137/verify6_1_r1/, no repository or GitHub
  access; refute155/, the #155 tree and independent/y137-evidence-20261109/ not opened): sha256sum of final/* and
  fixpass5_prefix/* (matches above); synth/check_hbp_v3.py 5de113afe7cac7d7 on final HBP -> check_final.txt
  3c7298cbd5731f36 and with arg '.' -> check_final_dot.txt 9c19f2a4072dd5dd (ERRORS
  0, = fixpass5/out/check_hbp_v3_pass5.txt), on prefix HBP -> check_prefix.txt 2689946fe2e097c8; diff -> hbp.diff
  63997b624115062b, other.diff 716b060a2db59fb3 (NOTE/ENGINE-PLAN/CHANGES); fielddiff.py 6739c51547a7068c ->
  fielddiff.txt 47a9946b00438a3c; fpcheck.py e7f7b78b5114a7ea on NOTE (54 ok, 0 bad; stdout only); grep-row hashes of
  rows 076-096+132-133 (7661b2dfff9ef183) and non-PREDICT lines (92d7d42440c74bab) identical in both versions; text
  reads of engine/rs/src/main.rs a8fd4a9b4097b528 (lines 399-430, 540-625, 734-750, 820-875, 1110-1145, 1210-1235,
  1335-1350, 1555-1570), CONTEXT.md, pass3review/FINDINGS-PASS4R2.md; sha256 of fixpass5/ and close/ files.

**E. Context.** CONTEXT.md ec1f0dd730696ee9 (the version fix pass 4 read; it adds the section on the r = 9 amplitude
exposure, item F.7). Fix passes 2 and 3 cite a27f8b707918ab31 and pass 1 cites 723bd5eeaa481617. wf_design.js
26489abacde0f73f (workflow script, no computation).

**F. r = 9 information from other seats, visible to this seat before the freeze.**
1. The cloud seat's refutation of PR #155, in `scratchpad/refute155/`. Its rule allows r = 9 inertia counts and
   witness hashes only, never an eigenvector, Rayleigh quotient, overlap or anything involving O_sum. This package's
   agents did not read that folder.
2. The local seat's REPORTED K3 isolation trial: exactly 2 even levels below 699567503/10^7, E3_even ≥ 69.9686993,
   E_odd ≥ 69.9689591.
3. Merged #136's r = 9 windows: E1 in (69.89, 69.92) and E2 in (69.93, 69.96).
4. The local seat's series (CONJECTURE): ground 69.911, E2 69.951, E3 69.971, amplitude 5/144.
5. GPT-6's design audit (issue #137 comment 6747959074). Its r = 9 content is its reading of #155's counts ((2,2) even
   and (0,0) odd at 699686993/10^7) and of #136's E2 < 69.96, which gives E3 - E2 > 0.0086993 J_E conditional on
   #131. It carries no eigenvector or amplitude information. It enters only the cross-check of HBP row 140, and no
   predicted window was changed after it was read (fix pass 3).
6. PR #155's receipt `independent/Y137-K3-SECTOR-ISOLATION.hbp` at head 30a08260d9827d61b37d8fbb4817513f9e487369
   (sha256 cf91b9e4d842698d4972ac8df6ff6210bd3f439f561a354bca2954aac36716ef, git blob f4e08a31, 9,535 bytes), read by
   the pass-4 fix seat with `git show` (no fetch was needed). It first listed the receipt's row types and field names,
   then read the values of its HEAD, SECTOR, COMPARE, ROUNDING_VARIANT, RESULT and END rows: thresholds, inertia
   counts, witness hashes and the stated conditions. This read was an exception that the orchestrator granted to
   CONTEXT.md's rule that agents of this package must not open the #155 tree, for this one file only. Its SCOPE row
   carries an amplitude_lane field. Its value was not read; only its length (47 characters) and that it contains
   digits were seen. It may carry r = 9 amplitude-lane material, and a reader should treat it like the evidence
   folder of item 7. No other file of the #155 tree was opened. The values read enter only HBP row 140 (the pin, the
   ties of 699567503/10^7 and 699686993/10^7, and test (5) NOT_APPLICABLE), and no predicted window changed in fix
   pass 4.
7. The r = 9 amplitude exposure (REPORTED by the cloud seat's refutation of #155, its finding R1, which inspected field
   names only). #155's pinned evidence folder `independent/y137-evidence-20261109/d2-feshbach-r9/` at head 30a08260,
   on a public branch, carries the local seat's earlier r = 9 amplitude-lane output: FE_AMP, FE_AMP_EXACT, FE_LEVEL
   (Rayleigh quotients), K3_AMP, K3_LEVEL, RIGOR_TARGET, RIGOR_CHAIN_B_K3 and FE_SUMMARY rows, in .rows and .log files
   and D2-FESHBACH-R9.hbp. Those numbers are reachable now. No cloud-seat agent has read their values (REPORTED), and
   this disclosure records no read of that folder by any agent of this package; the pass-4 and pass-5 fix seats did
   not open it. The receipt of item 6, which HBP row 140 pins for every refuter to open, also carries the
   amplitude_lane field of its SCOPE row, unread by this package (item 6); treat it like this folder (HBP row 128).
   The frozen amplitude interval [0.0325, 0.0337] and every other amplitude row (HBP rows 083-092) came only from the
   series and the excluded-r extrapolation. Rows 076 (Theorem I passes at depth 5) and 094 (the primary verdict PASS)
   rest only on the excluded-r smoke and the series, and the END row's candidate_r9_a_lo, CONJECTURE
   [0.0295, 0.0333], repeats row 085's primary a_lo window. No window field of rows 076-096 changed since the pass-1
   input (verify4r/winddiff.py, above; the pass-5 field diff of section 12.D finds rows 076-096, 132-133 and the END
   row byte-identical to the pass-5 input). The local seat, as the refuter, had its own r = 9 estimate before this
   freeze (HBP row 128, r9_amplitude_exposure).

Items 2 to 4 may have influenced the isolation windows (HBP rows 077-082). The amplitude rows (083-092) rest on the
excluded-r smoke and the series only, and so do rows 076 and 094; the depth-ladder rows (132, 133) rest on the
excluded-r smoke only. The END row's candidate_r9_a_lo repeats row 085's window, and rows 093, 095 and 096 are OPEN
and predict no r = 9 value. Item 6 was read, and item 7 reached this package, after every window was frozen; item 6
carries the counts behind item 2.

## 13. Corrections to the math lane's note

1. **Spreads.** n21 includes `(<O>_2 - c)^2`. With c ≈ <O>_1 it is about 5.75, not 3 (MEASURED 5.755 at r = 10.5).
   The angular coefficient is about 12 g at r = 9, not 9.3 g.
2. **Sector sizes.** Shells 5, 6 and 7 have 393,917, 2,465,466 and 9,398,188 classes (MEASURED), not 5.3e5, 6e6 and 7e7.
3. **k_c.** MEASURED at 1.41-1.44 at depth 5 (1.25-1.27 at depth 4) at every excluded r. It is no longer a factor of
   up to 7.
4. **Isolation depth.** It passes at depth 2 at every excluded r. At r = 9 the depth-2 isolation outcome is not
   predicted (section 11). Isolation at depths 3 to 5 is predicted (HBP rows 076 and 132), and the depth-2 ladder
   entry is predicted not PASS, because F_GAP fails there (row 133).
5. **Scale.** The engine uses S = 10^15 with 256-bit accumulators and asserts `|X| < 2^62`, instead of S = 2^40 in i128.
6. **Y depth.** The engine prototype solved Y on n+1 shells. The frozen method uses m = n, as the math lane recommended.
   With m ≤ n, `Y^T W R_ext = 0`.
7. **Integer forms.** The engine's U0 hat is at scale D S^2, not S^2. The driver clears every rational matrix by its
   common denominator, so the scale never enters a test by hand. The LO identity of section 9 is written in that
   cleared form, with K computed from the rationals.
8. **New items.** Corollary A' (the upper bound); the explicit check `tau2 > upsilon_2` for the owner's item 1; the LO
   sign identity `LO_LE_UP`; and the requirement that every planted fault ends in a named refusal at r = 9 itself, not
   only in a toy. The fix pass added the per-depth verdict rule (HBP row 131), the F_GAP gate on a_lo, the min form
   as the deciding a_lo, the X7 route switch, the aggregated-move tally of C0_EXTERIOR_COMPLETE, and the C++17
   checker in place of Go. Fix pass 2 scoped the floor pin by r (the row-010 floor at excluded r), limited
   A_FROM_THEOREM to the one BOUND row, froze the verdict-and-bound table and the LADDER/INFORMATIVE labels, gave
   owner item 3 a HOLD branch for the Y = 0 route, split Y_PD for Y = 0, fixed the X6 inputs and counts, added
   measurement paths for HBP rows 085, 089 and 091, and froze how a NOT_EVALUATED measurement reads. Fix pass 3
   carried GPT-6's design audit as six REQUIRED rows (146-151), pinned the floor source (rows 041, 136), added the
   independent regenerator gates EXT_REGEN and SIGN_POLAR (rows 134, 135, 139), the negative-control receipts (rows
   141, 142), the planted faults PF18-PF20, Lemma 11 and the second-floor rule (rows 137, 138) and the E3 - E2
   cross-check (row 140), and applied the round-2 minor findings listed in CHANGES PASS 3. Fix pass 4 applied the
   round-3 critic's and verifiers' 15 minor findings (CHANGES PASS 4): BURNSIDE_TOTAL in every run and the
   step-end rule for run-integrity FAILs, the Theorem-I gate and the pinned #155 receipt for the E3 - E2 cross-check,
   the open GPT-6 lift item, PF18 through the gamma0 rule, a deterministic PF19, and the odd-census definition. Its
   round 2 applied the round-4 findings (CHANGES PASS 4, round 2): FREEZE_PIN as a first program step of its own
   whose FAIL aborts at once, the E3 - E2 contradiction tests scoped to the no-fault r = 9 run, a strict test (2),
   the CONTEXT.md exception and the unread amplitude_lane field of #155's receipt disclosed, and xext's time
   estimate corrected to about 40 min. Fix pass 5 (CHANGES PASS 5) gave C0_EXTERIOR_COMPLETE a sector scope (the
   72-move tally in the symmetric sector; in the odd sector the signed-edge form that the engine's aggregation
   matches), scoped MOVES72, CENSUS, H1_TWO_SIDED_EXTERIOR and PF02 the same way, extended the E3 - E2 tests to the
   depth-6 fallback run at its verdict depth, and completed the disclosure of the r = 9 prediction sources and of the
   pass-4 round-2 verifier and close-seat folders.

## 14. What stays conditional, OPEN, or not claimed

* **Conditional on #131 (H4):** the LO counts, the V_rest exclusion, I3, the window lower ends, Lemma 2's upper bound,
  Lemmas 5 to 7', Lemma 8's remainder bound, Lemma 9, and therefore Theorem I, Theorem A and Corollary A'. H4 rests
  on the pinned #131 source and on the sector-to-whole lift of PERRON-BOUND.md section 2, which this package does not
  audit (section 15.2).
* **Unconditional:** Lemma S parts 1, 3 and 4, the identity in Lemma 2, the UP counts, and H3.
* **OPEN:**
  * every r = 9 value;
  * the adjoint h_i at r = 9;
  * the two-sided Delta bound that would tighten Lemma 7 further;
  * a second, separately frozen floor certificate, evaluated beside the verdict as read and report only (section
    15.5);
  * a second, independent method for the amplitude itself. PR #148 row 34 asks for two methods. The C++17 checker replays
    this method's arithmetic but is not a second method. The local seat's refutation and PR #148's rational-filter
    route are candidates, and the owner rules.
* **Not claimed:** any continuum, 4D, SU(N) or Clay statement (PR #148 F12), and any unconditional upgrade of #136 (F9).
* **Release gate.** The local Opus 5.5 seat (pid 8467a937cba309f7) refutes first. #137 stays OPEN until the owner
  accepts.

## 15. GPT-6's design audit (issue #137 comment 6747959074): answers, gates, controls and the second floor

GPT-6 posted the audit on 2026-11-09, before any frozen r = 9 measurement. Its verdict: route PROMISING; r = 9
amplitude NOT CERTIFIED; refuter gate HOLD. This section answers its six items in the order CONTEXT.md lists them.
Each item is a REQUIRED HBP row that cites the comment.

### 15.1 Item map

| item | what GPT-6 requires | HBP row | answered by |
|---|---|---|---|
| 1 | quotient weights `W'_A = sum_{i in A} W_i` (never `48 W_i`); `W'_A H'_AB = W'_B H'_BA` with multiplicities; O_sum invariant under all 48 maps | 146 | rows 013, 032, 034, 035, 036, 038, 099 (PF03, now with a `48 w_rep` variant), 134, 135, 139 |
| 2 | the conditional lemma that E2 lies in the trivial 48-element representation (REPORTED) | 147 | rows 011, 012, 013, 025, 075 |
| 3 | `E3 - E2 > 0.0086993 J_E` (conditional on #131) as a cross-check; own gaps from own inertia | 148 | row 140; rows 044-050 |
| 4 | three independent gates, and negative controls that produce each false positive on purpose | 149 | rows 041 and 136 (floor source), 135 (SIGN_POLAR), 134 and 139 (EXT_REGEN), 141-142 (receipts), 098, 100, 143-145 (PF02, PF04, PF18-PF20) |
| 5 | the goal-oriented error identity; primal and adjoint residuals bounded separately; normalisation and window errors; certified isolation; g defined by norm, scale and role | 150 | Lemma 8 (row 027), rows 024, 026, 029, 051-061, 089, 092, 140; section 15.6 |
| 6 | the extrapolation 0.0330-0.0332 and the interval [0.0325, 0.0337] stay CONJECTURE; no off-target r counts as an r = 9 test | 151 | rows 063, 074, 083, 085-092, 095, 096, 126 |

### 15.2 The floor source, and what this package does not audit

FLOOR_PIN (HBP row 041) now has a source sub-row, and HBP row 136 pins the source (MEASURED by read-only git object
reads in the finite repo):

* #131 merged at commit `d1385b345703ff1dc35e7dd2ae3eba77a9ee568b` (2026-11-07T15:34:28Z; parents 7cb1d6f and
  a936834).
* `native/ym/results/3x4_stream/perron/PERRON-BOUND.md`: sha256
  `41b9602fe03b6d9b7650cd7fbebd105127f95f5cef6f62f982c6e0fa512103d0`, git blob
  `53378d4ee68dc88766873713285e3a34465a9d90`, 17,241 bytes.
* `native/ym/results/3x4_stream/perron/PERRON-RESULT.hbp`: sha256
  `de19b354127c59ba3c2328fd310b5ff6a1103829c8d1d86c58b433aeec115a18`, git blob
  `cbd428014a4d440732a5c0a541ed57a9041becee`, 44,107 bytes. This is the blob that #136's checker
  (`independent/finite_s3_3x4_r9_first_gap.py`, function `source_floor`) pins.
* Its one `RESULT_PERRON_3x4_TOP` row carries t_cert_milli, perroncert_check, check_d_strict and outside_go_checker all
  equal to 94070673, min_row 45507968 and min_mag 3.
* Both blobs are byte-identical on origin/main 6a7fc74. The last commit that touched either file is 4f8605b
  (2026-11-03).

At every r, the driver and the C++ checker read both files from the repository's object store at d1385b3 and check
their sha256, their git blobs and the value row. The run's gamma0 must equal that value over 10^6 at r = 9, plus the
row-010 Weyl step at excluded r. All of this happens before any LO form is built and reads no certificate quantity.
So an overstated floor is refused by provenance, not by numerical algebra (receipt 15.8.1; planted faults PF04 and
PF18).

What the gate does not do. The sector-to-whole lift of PERRON-BOUND.md section 2 is an argument accepted in #131 and
measured only on 2x2 and 2x3 (shellschur). **This package neither audits nor re-derives it.** #152 rebuilt every
sector row and reproduced 94.070673 at row 45,507,968 (REPORTED). As GPT-6 notes, the weighted-adjoint all-pairs
census has no independent replay. Every conditional output (HBP row 009) therefore rests on the pinned source and on
the unaudited lift.

A reading audit by two pass-3 verifiers (REPORTED; a verifier audit, not a derivation of this package; HBP row 136,
lift_reading_audit). Both read the lift argument of PERRON-BOUND.md section 2 at d1385b3 (blob 53378d4e) and found it
sound. Lift d by `d~(x) = d(rep x)`, with `d~ = 0` on the flats. For `x = g s_K` the 72 moves are the g-images of
those from s_K, so `(H'_whole d~)(x) = (H'_sector d)(K)`. H'_whole is W-symmetrisable with nonpositive off-diagonal
entries, so Collatz-Wielandt gives `lambda_min(QHQ_whole) >= min_K (H'_sector d)_K / d_K`, with no irreducibility
needed. The argument rests on two premises, which are inputs from #131 and #152 (MEASURED there, REPORTED here):
d > 0 on every nonflat sector row, and the sector rows equal H's class rows. The store facts stay #131 and #152
inputs, and HBP rows 008 and 136 keep `lift_audited_by_this_package=NO`.

GPT-6's section 3.1 lift audit therefore stays OPEN and is not met by this package (HBP row 149,
gpt6_section_3.1_lift_audit). Releasing a BOUND row that is conditional on the unaudited lift needs GPT-6's and the
owner's ruling. The second floor of section 15.5 is the package's possible remedy.

The rest of GPT-6's floor list is covered as follows:
* Strict `A(z) > 0`: every z where A(z) enters (tau_i, sigma_i, upsilon_i, the window ends and the bisection points)
  is checked below gamma0 as `g b - a d0 > 0` (LO_LE_UP and I0). Then `A(z) >= gamma0 - z > 0`, given H4.
* The weights: H1_DETAILED_BALANCE, CENSUS, BURNSIDE_TOTAL, XCHECK_LIFT and EXT_REGEN.

### 15.3 The independent exterior (EXT_REGEN) and the sign-and-polarisation gate (SIGN_POLAR)

Why the exterior needs its own gate at the verdict depth. Suppose two exterior classes e1 and e2 are merged into one,
with weight W1 + W2 and accumulator a1 + a2, while every count is kept. The exterior Gram then changes by

    a1 a1^T/W1 + a2 a2^T/W2 - (a1 + a2)(a1 + a2)^T/(W1 + W2) = (W2 a1 - W1 a2)(W2 a1 - W1 a2)^T / (W1 W2 (W1 + W2)) >= 0,

so the error lowers GEX, which is the unsafe direction. MOVES72, H1_TWO_SIDED_EXTERIOR and C0_EXTERIOR_COMPLETE can all
pass on such an error, because they are the engine's own tallies.

EXT_REGEN (HBP row 134; ENGINE-PLAN X8) is run by xext, a separate C++17 integer program. It shares no code with the
Rust engine or the Python driver, and it never reads the engine's class keys, edge lists or exterior list. It has its
own S3 table, link order, spanning tree, gauge fixing, symmetry action and class key. Its weight rule is
`W = 288 / #{(g, h) attaining the key}` over symmetries g and global conjugations h. At the verdict depth n, xext:
1. rebuilds shells 0..n+1 from the flats and reproduces the census (HBP rows 014, 139);
2. matches the published representatives of shells 1..n one to one with its own classes, with equal W_i and m_i;
3. regenerates all 72 moves of every representative of shells 0..n+1, self moves included;
4. accumulates the outside-target multiset `{(i, e, c(i->e))}` with multiplicities and a sha256; at n = 5 this is
   22,702,638 distinct pairs into 2,465,466 targets;
5. rebuilds GEX and DEX from the published X and Y twice: through `W_i c(i->e) / W_e`, with each division checked
   exact, and without division, from the shell-(n+1) back moves. It checks `W_e c(e->i) = W_i c(i->e)` on every
   exterior edge;
6. rebuilds the odd exterior scalar.

Every rebuilt matrix must equal the engine's hat exactly.

The cost at n = 5 comes from the MEASURED census:
* 31,820,112 moves from shells 0..5, of which 28,362,024 are from shell 5;
* 177,513,552 moves from shell 6, where the engine's probe counted 22,702,638 back, 29,171,690 within and 124,259,339
  forward distinct edges;
* 8,046,864 odd moves.

The engine did the same enumeration in 242 s on 3 threads. xext's memory plan stays under 1.5 GB. Its budget is 4 GB
and 2 h; over budget is a FAIL, never a skip. In that case the r = 9 run waits for GPT-6 to rule.

SIGN_POLAR (HBP row 135) makes every independent comparison a comparison of full bilinear forms. It compares
`q(v) = v^T F v` on every `e_i` and every `e_i + e_j` (28 vectors for p = 7). Since
`2 F_ij = q(e_i + e_j) - q(e_i) - q(e_j)`, this fixes every entry; a diagonal-only check can miss a wrong cross term.
It applies to:
* XCHECK_LIFT at depths 2 and 3;
* EXT_REGEN;
* REPLAY_CPP;
* xext's rebuild of every other hat at the verdict depth, from its own inner edges, magnetic costs and O values.

Its sign sub-rows are:
* `B = -H_QP >= 0` on every regenerated move from shell 1 to a flat;
* `W_i c(i->j) = W_j c(j->i)` on every regenerated inner edge;
* `q(v) >= 0` on all 28 vectors for each Gram hat;
* the LO_LE_UP identity, for the sign of the Feshbach correction in `S = U - R* A^-1 R`.

### 15.4 Lemma 11 (floor monotonicity; DERIVED, HBP row 137)

*Validity.* If H4 holds with gamma', it holds with every gamma <= gamma': for f off the flats,
`<f, H f>_W >= gamma' <f, f>_W >= gamma <f, f>_W`. So every result certified with the floor gamma also holds under
any floor gamma' >= gamma, without re-evaluation.

*Monotonicity.* Fix every printed certificate rational except gamma. That means the hats, tau_i, sigma_i, upsilon_i,
g_i, h_i, y, phihat_i, mu_i, l_i+-, rho_i, the Gram values behind beta_i, n21, n12, nubar, nu0, w_i, ybar and o_inf.
Let gamma' >= gamma > tau2. Then:

(a) `LO_{gamma'}(tau) - LO_{gamma}(tau) = (1/(gamma - tau) - 1/(gamma' - tau)) G(tau) >= 0`, because `G(tau) >= 0`.
By Weyl monotonicity, neg LO and neg LO + null LO can only decrease. So every count inequality of WINDOWS, I1_LO and
I2_LO that holds at gamma holds at gamma'. In I1_LO and I2_LO, `LO_gamma <= LO_{gamma'} <= UP`, so
`lambda_i(LO_{gamma'}) <= lambda_i(UP) < 0 < lambda_{i+1}(LO_gamma) <= lambda_{i+1}(LO_{gamma'})`. Hence LO_{gamma'} is
nonsingular with neg = i. The same argument gives `LO_odd,gamma'(tau2) >= LO_odd,gamma(tau2) > 0`. The UP tests do
not involve gamma, and I0 (`tau2 < gamma'`) holds.

(b) `eps_i = g_i/(gamma - upsilon_i)`, `beta_i`, `taubar_i = sqrt(g_i)/(gamma - upsilon_i)` and every term of e_a are
nonincreasing in gamma. UP(tau) is Loewner-decreasing in tau, so neg UP is nondecreasing in its argument. So
`neg UP(l1+ + eps1') <= neg UP(l1+ + eps1) <= 1`, the same holds for N2P, and N2M does not involve gamma.

(c) The Lemma 7 sine `(rho_i + sqrt(eps_i beta_i))/delta_i` has delta_i fixed, so it is nondecreasing in eps_i beta_i.
For the Lemma 7' sine, write `D1 = mu_i - l_i-` and `D2 = l_i+ - mu_i`. Then
`s_c = max(f1, f2)` with `f1 = (rho_i + eps_i/2)/(D1 - eps_i/2)` and `f2 = (rho_i + eps_i/2)/(D2 + eps_i/2)`.
* f1 increases with eps_i.
* `d f2 / d eps_i = (D2 - rho_i)/(2 (D2 + eps_i/2)^2)`. F_GAP at gamma gives `f2 <= s_c < 1`, so `rho_i < D2`, and
  f2 also increases with eps_i.
* For `eps' <= eps`, the centre `mu_i - eps'/2` lies in `[mu_i - eps/2, mu_i]`, inside the gap.

So F_GAP still holds, and both sines and their minimum are nondecreasing in eps_i.

(d) Write the numerator of HBP row 026 as
`N = (1 - s1^2)(1 - s2^2) nu0 - s1 n21 - s2 n12 - s1 s2 nubar - (w1 + w2) ybar - e_a`. For s_i in [0, 1), with
nu0, n21, n12 and nubar nonnegative, `dN/ds1 = -2 s1 (1 - s2^2) nu0 - n21 - s2 nubar <= 0`, and similarly for s2;
also `dN/de_a = -1`. So N is nondecreasing in gamma, while the denominator `(1 + taubar1)(1 + taubar2) >= 1` is
nonincreasing. Hence if `a_lo(gamma) > 0`, then `a_lo(gamma') >= a_lo(gamma)`. The same argument shows that a_hi is
nonincreasing. When `N(gamma) < 0` no claim is made: a smaller denominator can make a negative quotient more negative.

(e) An isqrt rounded up at a fixed number of digits is monotone, so the printed rational bounds keep these orders.

*Integer tests.* The tests are re-run at gamma'. Each inequality they test holds by (a) to (e). A re-run can fail only
where its procedure meets an exactly vanishing leading minor, or an exactly singular matrix at a new point (for
example N1P at `l1+ + eps1'`). It is then reported as it falls. No claim is made for gamma' < gamma. QED.

### 15.5 A second, separately frozen floor (HBP row 138)

The cloud seat's floor lane is designing a second floor certificate for lambda_min(QHQ_whole) at r = 9. It is
Umeno-style: an exact low-magnetic core in the full orbit space plus an analytic tail floor. It will have its own
prediction file, frozen and sha256-pinned before its own r = 9 run. If it certifies gamma2, this package uses it as
read and report only. After the final evaluation of the r = 9 run on #131's floor:
* If gamma2 >= gamma0, every result certified on #131's floor also holds conditional on the second floor alone
  (Lemma 11, validity). The driver re-evaluates every floor-dependent test and the closed formulas at gamma2, at the
  same printed rationals, with no bisection re-run and no rule retuned. The C++ checker replays it. Lemma 11 gives
  `a_lo(gamma2) >= a_lo(gamma0)` whenever `a_lo(gamma0) > 0`.
* If gamma2 < gamma0, nothing carries over, and each test is reported as it falls.

Every such row is INFORMATIVE. It carries `accepted_source_assumption_2` with that file's sha256 and is never
labelled BOUND by this package; the owner rules on any release. No CONJECTURE row is measured on the second floor, so
no frozen prediction changes. One falsifier is frozen: any certified upper bound on lambda_min(QHQ_whole) below
94.070673, from any method (for example a Ritz value from the floor lane), falsifies H4. It then blocks release of
every conditional result of this package.

*The lift.* The second floor is designed to be lift-free if its core is done in the full orbit space. If it is
frozen that way, its read-and-report evaluation is this package's answer to the lift dependency of section 15.2
(HBP rows 008, 136 and 138). Otherwise it is not.

### 15.6 Item 5: the goal-oriented identity, and what g is

*The identity* (Lemma 8, section 8):

    a = phi2^T N(E1, E2) phi1 + eps_a,
    eps_a = <A1^-1 D(E1) phi2, R(E1) phi1>_W + <R(E2) phi2, A2^-1 D(E2) phi1>_W + <t2, Oc t1>_W.

R is the primal residual and D the adjoint (dual) residual. The first two error terms are each a primal residual
times an adjoint residual, divided by the distance to the floor; the third is two primal residuals over that
distance squared. This is the second-order cancellation GPT-6 asks to see proved: it is proved, here and in Lemma 2,
not assumed.

*Each error is bounded separately:*
* the primal residual by g_i (G_WINDOW, at both window ends);
* the adjoint residual by h_i (H_WINDOW, at both window ends, with ADJ_CONSISTENCY tying h_i and N_c to the same Y);
* the normalisation by taubar_i (Lemma 9);
* the eigenvalue windows by `(w1 + w2) ybar` (Lemma 10, WINDOWS, Y_PD);
* the angular error by Lemmas 7 and 7', with the isolation certified by Theorem I and by N1P, N2P, N2M and F_GAP. Here
  delta_2 comes from the package's own neighbour test N2P, which encloses the whole E3..E8 tail of the pencil. The #155
  value enters only the cross-check of section 15.7.

*Definition of g.* g_i is the certified rational of the HBP row-022 rule for which `g_i T - G(z)` is positive definite
at `z = sigma_i` and `z = upsilon_i`. Here `G(z) = R(z)^T W R(z)` is the W-Gram of the residual `R(z) = B - A(z) X` of
the lifted flat block.
* *Norm.* By Lemma 4, `||R(z) phi||_W^2 <= g_i phi^T T phi` for every phi in R^7 and every z in window i. So sqrt(g_i)
  bounds the operator norm of the residual map from (R^7, T) to (range Q, W).
* *Scale.* g_i is an exact rational in units of J_E^2; the residual has units of J_E.
* *Role.* g_i enters only through:
  * `eps_i = g_i/(gamma0 - upsilon_i)`, the uniform bound `0 <= Delta(E_i) <= eps_i T` of Lemma 2;
  * the sines, `sqrt(eps_i beta_i)/delta_i` with `beta_i <= eps_i` in Lemma 7 and `(eps_i/2)/delta_c` in Lemma 7';
  * e_a, through `sqrt(h_i g_i)/(gamma0 - upsilon_i)` and `o_inf sqrt(g1 g2)/((gamma0 - upsilon1)(gamma0 - upsilon2))`;
  * taubar_i.

No raw vector residual is ever divided by E3 - E2. What delta_i divides is eps_i: the residual squared, over the
distance to the floor (about 24 J_E at r = 9, CONJECTURE). GPT-6's example `g = 7.4e-4` would give
`g/(E3 - E2) ~ 0.085` as a raw ratio. Here it would give `eps_2 = 3.1e-5` and `eps_2/delta_2 ~ 1.5e-3` (with
delta_2 ~ 0.0203, CONJECTURE). Every r = 9 size of g, eps and the error terms is CONJECTURE (HBP rows 089 and 092).

### 15.7 The E3 - E2 cross-check (HBP row 140)

This package's isolation uses its own inertia only. The #155 and #136 values enter this cross-check and no check.

*The #155 pin (REPORTED).* #155 is a draft. Its two constants are pinned to head
30a08260d9827d61b37d8fbb4817513f9e487369 and to its receipt `independent/Y137-K3-SECTOR-ISOLATION.hbp` (sha256
cf91b9e4d842698d4972ac8df6ff6210bd3f439f561a354bca2954aac36716ef, git blob f4e08a31, 9,535 bytes; section 12.F item 6):
* 699567503/10^7 is the z of its `Y137_K3_SECTOR` row with ball K3 and (lower, upper) counts total (2, 2), even
  (2, 2) and odd (0, 0). The same z appears in its `Y137_K3_COMPARE` and `Y137_K3_ROUNDING_VARIANT` rows and as the z0
  of its `Y137_K3_RESULT` row. Its even upper count 2 (upper side `UNCONDITIONAL_min_max`) is the floor-free
  `E2 < 69.9567503`.
* 699686993/10^7 is the z of its `Y137_K3_SECTOR` row with ball K3 and the same counts, and the `E3_even_GE` field of
  its `Y137_K3_RESULT` row. Its lower counts (lower side conditional on #131's floor) give `E3 ≥ 69.9686993`, the
  receipt's own `E3_even_GE`.

*When the row is printed.* The driver prints the E3LO quantities at the run's E3LO depth d only when Theorem I passes
there (I0, I1_UP, I1_LO, I2_UP, I2_LO and I3_ODD all PASS). d is 6, its verdict depth, in the depth-6 fallback run of
HBP row 094, and 5 in every other run. Otherwise every E3LO quantity is printed NOT_EVALUATED, and no contradiction
test is evaluated. Every quantity below is taken at depth d.

*In which run the tests count.* Tests (2) to (5) below compare with r = 9 constants, so they are evaluated only in
the no-fault r = 9 runs: the single run of step 7 of ENGINE-PLAN section 0 (HBP row 129), at depth 5, and the depth-6
fallback run of HBP row 094, if it runs, at its verdict depth 6; in each only when Theorem I passes at that depth,
with the same NOT_EVALUATED and NOT_APPLICABLE semantics. So a BOUND row released from the fallback run has had the
cross-check at its own verdict depth. In every other run (every excluded-r run: the smoke, X6, X7 and the r = 12 CI
runs; and every fault run, at r = 12 and at r = 9) the E3LO quantities may be printed as read and report, and each
of tests (2) to (5) is printed NOT_EVALUATED. That NOT_EVALUATED is a frozen outcome, not a missing output, and has
no release effect. Without this scope, an excluded-r depth-5 run in which Theorem I passes would fire test
(3): MEASURED by a round-4 verifier from the X6 reference smoke files (excluded r only; section 12.D), sigma2 is
about 70.25 at r = 10.5 and 70.48 at r = 12, at depths 4 and 5, above 699567503/10^7. A planted fault that moves
sigma2, upsilon2 or E3_hi_pkg could likewise fire a test while Theorem I still passes.

The quantities are:
* `sigma3_even`, the largest of the 60 bisection points z in [tau2, kappa3_hi] with `neg LO(z) + null LO(z) <= 2`,
  and NOT_EVALUATED when no bisection point qualifies;
* `m3 = min(sigma3_even, odd_lo, gamma0)`, NOT_EVALUATED when sigma3_even or odd_lo is; it is a lower bound on E3,
  conditional on H4;
* `E3_lo_pkg = max(tau2, m3)`, and tau2 when m3 is NOT_EVALUATED. It is a lower bound on E3, conditional on H4, and
  valid only when Theorem I passes at depth d, because Theorem I is what puts no other level at or below tau2;
* `E3_hi_pkg = min(kappa3_hi, max(tau2, U0_odd/T_odd))`, a floor-free upper bound on E3;
* the certified gap interval `(E3_lo_pkg - upsilon2, E3_hi_pkg - sigma2)`;
* the internal value `m3 - upsilon2`, printed read and report only, with no contradiction effect.

*Contradiction tests.* The former test 1 (Theorem I passes and `E3_lo_pkg - upsilon2 <= 0`) is withdrawn. Since
E3_lo_pkg ≥ tau2 by construction, it could fire only when TAU2_ABOVE_UPSILON2 fails, and then no certificate is
contradicted. The internal value above replaces it. In each no-fault r = 9 run named above, with that run's
quantities at its depth d, a contradiction occurs if any of the following holds:

2. `E3_hi_pkg < 699686993/10^7`, which contradicts #155's conditional bound `E3 ≥ 69.9686993`. The test is strict:
   equality is consistent with both certificates.
3. `sigma2 >= 699567503/10^7` or `sigma2 >= 69.96`, which contradicts the floor-free E2 bounds of #155 and #136. The
   second clause is implied by the first; it is kept for the #136 citation.
4. `upsilon2 <= 69.93`, which contradicts #136's conditional lower bound.
5. Any floor-free upper bound on E3 in #155's pinned receipt lies at or below E3_lo_pkg. This test is
   **NOT_APPLICABLE**: the receipt prints no floor-free upper bound on E3. Its upper counts are at most 2 in the even
   sector and at most 2 in total at every threshold: 1 at 69956/1000 (ball K2); 2 at 699567503/10^7, 699686993/10^7
   and 699689591/10^7 (ball K3); and an even upper count of 2 in each of its three rounding-variant rows.
   NOT_APPLICABLE is a frozen outcome, not a missing output. In every other run, test (5) is printed NOT_EVALUATED,
   like tests (2) to (4).

A contradiction, possible only in those no-fault r = 9 runs (the step-7 run and the depth-6 fallback run), falsifies
at least one of this package, #155, #136 and #131's floor. No other run prints CROSS_CONTRADICTION. It blocks release until the owner rules, and it changes
neither the run's verdict nor any frozen prediction. Otherwise the line is read and report: the
package's certified gap lower bound `E3_lo_pkg - upsilon2` is printed beside 0.0086993.

### 15.8 Negative-control receipts (HBP rows 141, 142; MEASURED, toy matrices only)

`synth/negctl_gpt6.py` (548f71564ee73803; python3 -I -B; Python ints only) prints `synth/out/negctl_gpt6.txt`
(3c10e20a2c1f01e9). It uses this package's signs, `B = -H_QP` and `R = B - A X`; GPT-6's F, X and R are the negatives
of these, and every Gram, U, T, UP and LO is the same.

1. *Wrong floor.* `H - z = [[1,-2],[-2,1]]` at z = 0, with P = e0, Q = e1, W = I and X = 0. The truth is one
   eigenvalue below z (S = -3). The forms are U = T = 1, R = 2 and G = 4.
   * With gamma asserted to be 100, `LO = 24/25` and neg UP = neg LO = 0. Both forms read no crossing, and the
     LO_LE_UP identity passes: this is the false positive, produced on purpose.
   * The floor-source gate refuses it. With the honest source (sha256 2615832b42239071, matching its pin), the value
     sub-row fails: 100/1 against the pinned 1/1. With a source edited to 100/1 (sha256 8fa8ca207c4ffeb0), the hash
     sub-row fails.
   * The control, gamma = 1 from the honest source, passes the gate and gives LO = -3 with neg LO = 1, so the crossing
     is read.
2. *Dropped exterior.* `C = 9/10`, `F = (-1,0)^T`, `A = [[2,-1],[-1,1]]`, and GPT-6's `X = (-1/2,0)^T`, at z = 0 with
   W = I. As a graph this is P0-Q1-Q2, with Q1 inner and Q2 exterior. The truth is one eigenvalue below z
   (S = -1/10), and `PD(A - 1/4)` holds, so gamma = 1/4 is a valid floor. The forms are U = 2/5 and T = 5/4.
   * With the exterior row dropped, the writer's G = 0 and UP = LO = 2/5. Both forms read no crossing, and the
     identity passes.
   * The exterior-regeneration gate refuses it. It regenerates the move multiset `Q1>Q2:1` (sha256 d05f68029cd3c6be)
     from the matrix itself and gets G = 1/4.
   * The control with the complete exterior passes the gate and gives LO = -3/5 with neg LO = 1.

Both receipts print PASS. At run scale, the same gates refuse the planted faults PF04 and PF18 (FLOOR_PIN), PF02 and
PF19 (EXT_REGEN), and PF20 (SIGN_POLAR). build-selftest re-runs the script and requires byte-identical output.
