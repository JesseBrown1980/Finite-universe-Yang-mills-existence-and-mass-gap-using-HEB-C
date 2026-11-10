# T3: SU(2)_k past the degree-11 ceiling, and the q-deformed lattice caveat

Lane T3 of the finite-vs-continuous tests. 2026-11-09. **PREDICTIONS ONLY: measurement_status = NOT_RUN.** Nothing here is MEASURED. No repository writes, no GitHub posts.

All files sit in `/tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/fc-tests/T3/`:

| file | sha256 (first 16 hex) | role |
|---|---|---|
| `NOTE.md` | – | this note: definitions, proofs |
| `ROWS.hbp` | – | one prediction per line |
| `t3_small_checks.py` | `e7e1fb839db6f61f` | pre-freeze check P1 (k ≤ 2 only) |
| `small_checks.out` | `8c7a22012024b94e` | its output, 41 checks, 0 failed |
| `t3_closed_forms.py` | `efe9a44a9e9dc34b` | pre-freeze computation P2 (closed forms only) |
| `closed_forms.out` | `08ad75df28761589` | its output, 62 checks, 0 failed |
| `T3_TABLE.txt` | `3c8e7da5564a106b` | the predicted M_n(k) table, from the closed form A3 only |
| `t3_rowlint.py` | `835a9375c1dbc94b` | format check of ROWS.hbp; confirms the TABLE rows equal `T3_TABLE.txt` |

**Tags.** DERIVED: proved in this note; nobody else has read the proofs yet. REPORTED: from a record I opened; §5 lists what I opened and what I read in it. CONJECTURE: not proved. OPEN: an unanswered question. MEASURED: not used in this lane.

---

## 0. Results in brief

**(a) Fingerprint law (DERIVED).** M_n(k), the multiplicity of spin 0 in V_{1/2}^{⊗n} in SU(2)_k, counts walks of length n from 0 back to 0 on the path graph with vertices 0, …, k. So M_n(k) = 0 for odd n, and M_{2m}(k) is the number of Dyck paths of semilength m and height ≤ k. Hence M_{2m}(k) = Catalan(m) for m ≤ k. The first break is at n = 2k+2, with M_{2k+2}(k) = Catalan(k+1) − 1. Closed forms valid for every n:
- the reflection sum (A3);
- the Verlinde/Chebyshev spectral sum (A5), which is the (k+1)-point Gauss quadrature of the SU(2) Haar trace law;
- the generating function P_k/P_{k+1} (A6);
- the recurrence with characteristic polynomial U_{k+1}(x/2) (A7).

The deficit Catalan(m) − M_{2m}(k) is a comb of second differences of the binomial row (A4).

**(b) Design degree (DERIVED; the 2I values are REPORTED).** t_fp(SU(2)_k) = 2k+1, with only k+1 simple objects. It exceeds 11 exactly when k ≥ 6. This is optimal: a law on N points cannot match the SU(2) trace moments through degree 2N, and the only one that matches through 2N−1 is SU(2)_{N−1} (B3). Every finite subgroup G ⊂ SU(2) has an atom at trace 2 (the identity), which costs at least one degree: t(G) ≤ 2N_G − 2, and t(G) ≤ 2N_G − 3 when −1 ∈ G (B4). At k = 5, SU(2)_5 and 2I both have degree 11. At n = 12 they break in opposite directions: 131 < 132 < 133 (B5).

**(c) Lattice caveat.** Construction C_k (§4.1) is a generalized lattice gauge theory in Oeckl's sense, built on the spherical category SU(2)_k. Its plaquette weight is the fusion-ring exponential W(β) = exp((β/2)[V_{1/2}]). With Rep SU(2) in place of SU(2)_k, the same construction is Wilson LGT with weight exp((β/2) tr U_p).
- **Case (i): only fusion multiplicities enter.** This covers the 2D lattice with free boundary, the 2D thermodynamic limit and the pillow. The free energy per plaquette satisfies f_k − f_SU(2) = −β^{2k+2}/(4^{k+1}(2k+2)!) + (2k²+5k+4)β^{2k+4}/(4^{k+2}(2k+4)!) + O(β^{2k+6}). This mirrors the finite-group transfer theorem, with ι replaced by −1. DERIVED.
- **Case (ii): quantum dimensions enter.** On the 3D cubic lattice the elementary cube is weighted by [2]^{−4} instead of 2^{−4}. The first difference is at β⁶ for every k ≥ 2 (β⁴ for k = 1). Its coefficient is (sec⁴(π/(k+2)) − 1)/3072 for k ≥ 3 and 11/11520 for k = 2, about π²/(1536(k+2)²). On small 2D tori the difference appears at β^{L₁L₂}. DERIVED.
- **The quantum dimension can be read off whatever plaquette weight is used** (C6): Ψ₆ = d_{1/2}² = 4cos²(π/(k+2)) for SU(2)_k against 4 for SU(2). DERIVED.
- **Hamiltonian qKS of Zache, González-Cuadra and Zoller.** The second order is identical to SU(2). The first difference is at fourth order in 1/g⁴. CONJECTURE.

**What this says about the frame.** SU(2)_k is a finite structure that reproduces SU(2)'s invariant-count fingerprint through degree 2k+1. That degree grows without bound in k, which no finite subgroup can do. The fingerprint then breaks at a computable point, by exactly −1. The fingerprint degree carries over to the lattice free energy only where the free energy sees nothing but spin-0 multiplicities. In 3D, the first closed surface already sees the quantum dimension at β⁶, with an O(1/k²) coefficient. So the "universal hash" of SU(2)_k (the Catalan prefix plus a deficit of −1) is honest for invariant counts. It is not honest for 3D gauge free energies.

---

## 1. Data and conventions

**1.1 (REPORTED, Zache et al. 2023).**
- **Simple objects:** V_j with j ∈ {0, 1/2, …, k/2}, all self-dual.
- **Fusion:** V_{j₃} ⊂ V_{j₁} ⊗ V_{j₂}, with multiplicity 1, exactly when all three hold: |j₁−j₂| ≤ j₃ ≤ j₁+j₂; j₁+j₂+j₃ ∈ ℤ; and j₁+j₂+j₃ ≤ k.
- **Quantum dimensions:** d_j = [2j+1], where [n] = sin(nπ/(k+2))/sin(π/(k+2)).

The task writes q = exp(iπ/(k+2)) and the paper writes q = e^{2πi/(k+2)}. I use [n] only through the sine ratio, which is the same in both.

**Lemma 1.2 (DERIVED from 1.1).** V_{1/2} ⊗ V_{a/2} = V_{(a−1)/2} ⊕ V_{(a+1)/2}, with V_{−1/2} := 0 and V_{(k+1)/2} := 0.

*Proof.* With j₁ = 1/2, the triangle and integrality conditions leave j₃ = j₂ ± 1/2. The level condition 1/2 + j₂ + j₃ ≤ k reads 2j₂ ≤ k when j₃ = j₂ − 1/2, which always holds. When j₃ = j₂ + 1/2 it reads j₂ + 1/2 ≤ k/2. ∎

**1.3 Walks.** Let A_k be the adjacency matrix of the path graph P_k on the vertices a = 0, …, k, where a = 2j. In the Grothendieck ring, [V_{1/2}]^{n+1} = [V_{1/2}]·[V_{1/2}]^n. So the multiplicity vector N_n(a) of V_{a/2} in V_{1/2}^{⊗n} satisfies N_0 = e_0 and N_{n+1} = A_k N_n. Hence:
- N_n(a) = (A_k^n)_{a0} is the number of walks of length n from 0 to a in P_k;
- M_n(k) = N_n(0).

**1.4 SU(2) baseline.** The baseline is the same construction on the half-infinite path {0, 1, 2, …}. This is the Clebsch–Gordan rule, NAMED as in TRANSFER-THEOREM §2. Then:
- M_n^{SU(2)} = C_{n/2} for n even and 0 for n odd, where C_m = binom(2m, m)/(m+1).

Write L(p) := E_Haar[p(tr U)]. Then:
- L is a positive-definite functional on polynomials, because tr U has a continuous law on [−2, 2] (NAMED: Weyl integration);
- L(x^n) = M_n^{SU(2)};
- the polynomials U_n(x/2) are L-orthonormal (NAMED: Schur orthogonality, since χ_{n/2}(U) = U_n(tr U/2)).

---

## 2. (a) The fingerprint law

**Theorem A1.** M_n(k) = 0 for odd n, and M_{2m}(k) = #{Dyck paths of semilength m and height ≤ k}.

*Proof.* P_k is bipartite, so closed walks have even length. A closed walk 0 → 0 of length 2m inside [0, k] is a ±1 sequence whose partial sums stay in [0, k] and end at 0. That is a Dyck path of height ≤ k. ∎

**Corollary A2.**
- (i) M_{2m}(k) = C_m for m ≤ k.
- (ii) M_{2k+2}(k) = C_{k+1} − 1.
- (iii) M_n(k) ≤ M_n^{SU(2)} for all n. The inequality is strict exactly for even n ≥ 2k+2.
- (iv) M_n(k) ≤ M_n(k+1).

*Proof.*
- (i) A Dyck path of semilength m has height ≤ m.
- (ii) At m = k+1, the only path with height above k is U^{k+1}D^{k+1}.
- (iii) The bounded paths are a subset of all paths. For even n = 2m ≥ 2k+2, the path U^mD^m is excluded.
- (iv) Inclusion. ∎

**Theorem A3 (reflection closed form).** Put K = k+2, and let binom vanish outside 0..n. For every n ≥ 0:

  M_n(k) = Σ_{t∈ℤ} [binom(n, n/2 + tK) − binom(n, n/2 + tK + 1)]  (n even),  M_n(k) = 0  (n odd).

More generally, N_n(b) = Σ_t [B(n, b+2tK) − B(n, −b−2+2tK)], where B(n, c) = binom(n, (n+c)/2) when n+c is even and |c| ≤ n, and B(n, c) = 0 otherwise.

*Proof.* Let F(n, b) denote the right-hand side, for all integers b.
1. B(n+1, c) = B(n, c−1) + B(n, c+1), so F(n+1, b) = F(n, b−1) + F(n, b+1).
2. F(n, −1) = 0, because the two sums agree term by term.
3. F(n, k+1) = 0, because −(k+1) − 2 + 2tK = (k+1) + 2(t−1)K.
4. F(0, b) = δ_{b0} for 0 ≤ b ≤ k. The term b + 2tK = 0 forces t = 0 and b = 0. The term −b − 2 + 2tK = 0 has no solution with 0 ≤ b ≤ k.

The bounded walk count N_n(b) satisfies the same recursion on [0, k], with zero boundary values at −1 and k+1 and the same initial value. By induction on n, F = N on [0, k]. At b = 0, use B(n, 2tK − 2) = binom(n, n/2 + 1 − tK) and re-index t → −t. ∎

**Corollary A4 (deficit law).** Put D_m(k) := C_m − M_{2m}(k) ≥ 0. Then

  D_m(k) = Σ_{t ≥ 1} [binom(2m, m+tK−1) − 2·binom(2m, m+tK) + binom(2m, m+tK+1)].

This is a comb of second differences of the binomial row, with period K. For m ≤ 2k+2 only the t = 1 term survives. With r = m − k − 1:

  D_{k+1+r}(k) = binom(2m, r) − 2·binom(2m, r−1) + binom(2m, r−2).

Explicit values:

| m | D_m(k) | valid for |
|---|---|---|
| k+1 | 1 | all k |
| k+2 | 2k+2 | all k |
| k+3 | 2k² + 7k + 4 | all k |
| k+4 | 2(k+3)(k+4)(2k+1)/3 | k ≥ 2 |
| k+5 | N(N−1)(N² − 13N + 34)/24, with N = 2k+10 | k ≥ 3 |

*Proof.* Pair the terms t and −t in A3 and use binom(2m, m−s) = binom(2m, m+s). For t ≥ 2, the smallest index m + 2K − 1 exceeds 2m exactly when m < 2k+3. For the polynomials, substitute r = 0, …, 4. For example, r = 3 gives N(N−1)(N−2)/6 − N(N−1) + N = N(N−2)(N−7)/6 with N = 2k+8. ∎

**Theorem A5 (spectral form = Verlinde formula = Gauss quadrature).** Put θ_l = πl/K, x_l = 2cos θ_l and w_l = (2/K) sin²θ_l, for l = 1, …, k+1. Then

  M_n(k) = Σ_l w_l x_l^n,  and more generally  N_n(a) = Σ_l w_l x_l^n U_a(cos θ_l).

The x_l are the k+1 zeros of U_{k+1}(x/2). Every w_l > 0, and Σ_l w_l = 1.

*Proof.*
1. Set v_l(a) = √(2/K) sin((a+1)θ_l). Then v_l(a−1) + v_l(a+1) = 2cos θ_l·v_l(a), with v_l(−1) = v_l(k+1) = 0.
2. These vectors are orthonormal. For s ≢ 0 mod 2K, Σ_{b=1}^{K−1} cos(sbπ/K) = −(1 + (−1)^s)/2, and that gives Σ_b sin(lbπ/K) sin(l′bπ/K) = (K/2)δ_{ll′}.
3. So (A^n)_{a0} = Σ_l x_l^n v_l(0) v_l(a), and v_l(a)/v_l(0) = sin((a+1)θ_l)/sin θ_l = U_a(cos θ_l).
4. U_{k+1}(cos θ) = sin(Kθ)/sin θ, which vanishes at every θ_l. ∎

So the fingerprint measure ν_k := Σ_l w_l δ_{x_l} is the (k+1)-point Gauss quadrature (Chebyshev, second kind) of the Haar trace law. In Verlinde form, S_{ab} = √(2/K) sin(π(a+1)(b+1)/K) and w_l = S_{0,l−1}². The proof above does not depend on that formula.

**Theorem A6 (generating function).** Σ_m M_{2m}(k) x^m = P_k(x)/P_{k+1}(x), where P_h(x) = Σ_j (−1)^j binom(h−j, j) x^j, P_0 = P_1 = 1 and P_{h+1} = P_h − x·P_{h−1}.

*Proof.* Let G_h be the generating function of Dyck paths with height ≤ h. Decomposing at the first return gives G_h = 1 + x·G_{h−1}·G_h, with G_0 = 1. Induction gives G_h = P_h/P_{h+1}. The binomial form satisfies the same recursion by Pascal's rule. ∎ Also, det(t − A_k) = U_{k+1}(t/2) = t^{k+1}·P_{k+1}(t^{−2}).

**Theorem A7 (recurrence).** For n ≥ k+1:

  M_n(k) = Σ_{j=1}^{⌊(k+1)/2⌋} (−1)^{j+1} binom(k+1−j, j) M_{n−2j}(k).

*Proof.* Apply Cayley–Hamilton to the characteristic polynomial U_{k+1}(t/2) = Σ_j (−1)^j binom(k+1−j, j) t^{k+1−2j}, multiply by A^{n−k−1}, and take the (0, 0) entry. ∎

**Proposition A8 (small k).**
- k = 1: M_{2m} = 1.
- k = 2: M_{2m} = 2^{m−1} for m ≥ 1.
- k = 3: M_{2m} = F_{2m−1} for m ≥ 1, with Fibonacci F_1 = F_2 = 1.
- k = 4: M_{2m} = (3^{m−1} + 1)/2 for m ≥ 1.
- k = 5: M_n = 5M_{n−2} − 6M_{n−4} + M_{n−6} for n ≥ 6.

*Proof.* Apply A7 with the first values from A2. For k = 3 the recurrence is M_{2m} = 3M_{2m−2} − M_{2m−4}. For k = 4 it is M_n = 4M_{n−2} − 3M_{n−4}, whose roots are 1 and 3. ∎

**Proposition A9 (every spin).** Let m_k(n, j) be the multiplicity of V_j in V_{1/2}^{⊗n} at level k, and m_∞ its SU(2) value. Then m_k(n, j) = m_∞(n, j) for n < 2k+2−2j, and m_k(2k+2−2j, j) = m_∞ − 1.

*Proof.* A walk 0 → 2j that touches k+1 has length at least (k+1) + (k+1−2j). Exactly one walk has that length. ∎

**2.10 The predicted table.** `T3_TABLE.txt` gives M_n(k) for k = 1..12 and n = 0..30. Every value was computed from A3 alone, using binomials only. No fusion iteration and no path enumeration were run for k ≥ 3.

The canonical text is twelve lines `k=K|n=0..30|M=v0,...,v30`, in ascending k, each ending in a newline. Its sha256 is `3c8e7da5564a106b203d0b0fd8e5a87ce5b17f4370ab734f50880bf7359c526c`.

The A3 values satisfy A2, A4, A6 and A7 for all twelve k (48 checks in P2). These checks compare closed forms with each other; they are not a measurement.

Sample values: M_30(12) = C_15 − 376 = 9694469; M_30(11) = C_15 − 3220 = 9691625; M_30(6) = 7319744.

---

## 3. (b) Design degree

**Definition.** For a law μ of the trace variable x, let t_fp(μ) := max{t : ∫x^n dμ = M_n^{SU(2)} for every n ≤ t}.
- For a finite G ⊂ SU(2), μ_G is the law of tr g with g uniform in G. Then t_fp(μ_G) equals the design strength t(G) (REPORTED, TRANSFER-THEOREM Lemma 2.4).
- For SU(2)_k, μ = ν_k.

**Theorem B1.** t_fp(SU(2)_k) = 2k+1. For k = 1..12 the values are 3, 5, 7, …, 25. *Proof:* A2. ∎

**Corollary B2.** t_fp > 11 exactly when k ≥ 6. SU(2)_6 has 7 simple objects and degree 13. The ceiling over finite subgroups is 11, reached by 2I with 9 irreducible representations (REPORTED).

**Theorem B3 (Gauss optimality and the sign of the break).** Let μ be a probability law on ℝ with exactly N atoms.
1. t_fp(μ) ≤ 2N − 1.
2. t_fp(μ) = 2N − 1 if and only if μ = ν_{N−1}.
3. ∫x^{2N} dν_{N−1} = C_N − 1, a deficit of exactly 1.

*Proof.*
1. p = Π(x − x_i)² has degree 2N, with μ(p) = 0 < L(p).
2. Suppose μ matches through degree 2N−1, and put π = Π(x − x_i). For deg q ≤ N−1, L(πq) = μ(πq) = 0. So π is L's monic orthogonal polynomial of degree N, namely π = U_N(x/2), and the atoms are its zeros. The weights are fixed: μ({x_i}) = μ(ℓ_i²) = L(ℓ_i²), where ℓ_i is the Lagrange basis and has degree 2N − 2. So μ is unique, and ν_{N−1} qualifies by B1.
3. x^{2N} − π² has degree ≤ 2N−1. So L(x^{2N}) − μ(x^{2N}) = L(U_N(x/2)²) − 0 = 1. ∎

This gives a second proof of A2(ii). It also explains the sign: a quadrature with all nodes in the interior undershoots at the first degree it gets wrong.

**Theorem B4 (finite subgroups are pinned at the identity).** Let G ⊂ SU(2) be finite, with N_G distinct trace values.
- Then t(G) ≤ 2N_G − 2.
- If −1 ∈ G, then t(G) ≤ 2N_G − 3. This applies to every G of even order.
- Both bounds are tight in examples. C₂ = {±1} has N = 2 and t = 1. Q8 has N = 3, with traces 2, −2, 0 of weight 1/8, 1/8, 3/4. That law is the 3-point Gauss–Lobatto rule, with t = 3 and ι = 2.

*Proof.* Take f = (2 − x)·Π_{x_i ≠ 2}(x − x_i)², of degree 2N_G − 1. If −1 ∈ G, take instead f = (4 − x²)·Π_{x_i ≠ ±2}(x − x_i)², of degree 2N_G − 2. In both cases f ≥ 0 on [−2, 2], f is not identically 0, and f vanishes on every atom. So μ_G(f) = 0 < L(f), and the moments must differ by degree deg f.

A group of even order has an element of order 2 (Cauchy), and the only such element in SU(2) is −1.

For Q8: M_2 = 1 = C_1, while M_4 = 4 ≠ 2. ∎

For 2I, N = 9 (REPORTED/NAMED). Elements of orders 1, 2, 4, 6 and 3 have traces 2, −2, 0, 1 and −1. Elements of orders 5 and 10 have traces ±(1+√5)/2 and ±(√5−1)/2. The bound is 15; the actual degree is 11 (REPORTED).

Per atom, SU(2)_k reaches the Gauss maximum 2N − 1. A finite subgroup cannot, because its identity is an atom at the endpoint of the interval.

**B5 (the mirror at k = 5).** SU(2)_5 and 2I both have t_fp = 11. At n = 12:

| | M_12 |
|---|---|
| SU(2)_5 | 131 |
| SU(2) (Haar) | 132 |
| 2I | 133 (REPORTED, TRANSFER-THEOREM §2.4) |

In the 2D free-boundary model of Proposition C2, the first-break coefficients are −1/1961990553600 for SU(2)_5 and +1/1961990553600 for 2I. The 2I value is REPORTED: su2-ladder `GAUGE_FIRST_BREAK` and the TRANSFER-THEOREM table.

**B6 (sign).** SU(2)_k always breaks by a deficit: D ≥ 0 for every n, and D > 0 for every even n ≥ 2k+2. Finite subgroups always break by an excess: M^G − M^Haar = Σ m(n, j) dim V_j^G ≥ 0 (REPORTED, Lemma 2.4). The sign is structural. Fusion truncation deletes walks, while passing to a subgroup adds invariants.

---

## 4. (c) The lattice caveat

**4.1 Construction C_k (a definition precise enough to measure).**
- **Category.** SU(2)_k as a unitary spherical fusion category, with d_j = [2j+1] > 0. The baseline is Rep SU(2): d_j = 2j+1 and untruncated fusion.
- **Plaquette weight.** W(β) := Σ_n (β/2)^n [V_{1/2}]^n / n! = Σ_j a_j(β)[V_j], in the complexified Grothendieck ring. Equivalently,
  a_j(β) = Σ_n (β/2)^n N_n(2j)/n! = Σ_l w_l e^{β cos θ_l} U_{2j}(cos θ_l)  (by A5).
  For Rep SU(2), a_j = ∫ e^{(β/2) tr U} χ_j(U) dU, the character coefficients of the Wilson weight.
- **Complex.** A 2-complex Λ: a cellulated surface, or the 2-skeleton of ℤ_L³ or of an open box.
- **State sum.** Z(Λ; β) = Σ over labels j_p of Π_p a_{j_p}(β) · Ev(j). This is the framework of Oeckl 2003 (REPORTED); the details below are mine.
  - At every link ℓ, Ev inserts the normalized projector onto Hom(1, ⊗_{p∋ℓ} V_{j_p}). When exactly two nontrivial plaquettes j and j′ meet at ℓ, this projector is δ_{jj′}·(coev∘ev)/d_j, which is idempotent because ev∘coev = d_j.
  - Ev then evaluates the planar network around each vertex in the category.
  - Each nontrivial plaquette carries the orientation of its surface. All V_j are self-dual, and every strand used below closes, so Frobenius–Schur signs cancel in pairs.
- **Baseline check.** For Rep SU(2) this is the character expansion of ∫ Π dU_ℓ Π_p e^{(β/2) tr U_p}, which is Wilson LGT and the Z_SU(2) of the transfer theorem. Oeckl's abstract states that ordinary LGT is recovered for Rep of a compact Lie group.
- **Observables.** f(Λ; β) := ln Z / N_p as a power series in β. f_D is its L → ∞ limit on ℤ_L^D. ⟨P⟩ := ∂_β f.
- **How to measure.** Implement Ev with SU(2)_k F-symbols (for example those used by Zache et al.). Evaluate the small complexes of C2–C6 exactly (open disk, pillow, 1×2, 2×2 and 2×3 tori, open cube), or evaluate the 3D polymer expansion.

**Lemma C1 (unbranched closed surfaces).** Let S be a set of plaquettes forming a closed surface: every link of S lies in exactly two plaquettes of S, and around every vertex of S the plaquettes of S form a single cycle. Suppose the plaquettes of S carry nonzero labels and every other plaquette carries 0. Then:
- all labels on S equal one value j;
- the configuration weight is a_0^{N_p}·d_j^{χ(S)}·(a_j/(a_0 d_j))^{F(S)}, where χ = V − E + F is computed on S.

*Proof.* Since the simple objects are self-dual, Hom(1, V_j ⊗ V_{j′}) ≠ 0 exactly when j′ = j, so the label is constant on each connected component of S. Each link of S contributes 1/d_j and joins two strands. At each vertex the strands form one closed loop, worth d_j in a spherical category; this is the normalization of Levin–Wen's loop rule (5) (REPORTED). The total is a_j^F·a_0^{N_p−F}·d_j^{V−E}. ∎

*Robust to the sign convention.* For j = 1/2, every surface used below has χ − F even. So the predictions do not change if the loop value is taken as −[2], the Kauffman-bracket convention.

**Proposition C2 (2D free boundary; case (i)).** On an open 2D square lattice (a disk), Z = a_0(β)^{N_p} exactly, so f = ln a_0. Set z_k(β) = a_0^{(k)}(β) = Σ_n β^n M_n(k)/(2^n n!). This is exactly the gauge model z(β) of the su2-ladder (REPORTED). Then:
- f_k − f_SU(2) = −β^{2k+2}/(4^{k+1}(2k+2)!) + (2k²+5k+4)·β^{2k+4}/(4^{k+2}(2k+4)!) + O(β^{2k+6});
- every odd order is zero, and every order up to β^{2k+1} is zero.

*Proof.* A boundary link lies in one plaquette, so that plaquette carries 0. A link between a trivial and a labelled plaquette forces the label to 0. Connectivity then makes every label 0.

For the series: z_k − z = −Σ_{m ≥ k+1} D_m β^{2m}/(4^m (2m)!), with z = 1 + β²/8 + …. So ln(z_k/z) = (z_k − z)/z + O(β^{4k+4}). With D_{k+1} = 1 and D_{k+2} = 2k+2, the coefficient of β^{2k+4} is
1/(8·4^{k+1}(2k+2)!) − (2k+2)/(4^{k+2}(2k+4)!) = (2k²+5k+4)/(4^{k+2}(2k+4)!). ∎

This is case (i): only spin-0 multiplicities enter, and the break is at 2k+2 exactly. It mirrors the transfer theorem's N_p·ι·β^{t+1}/(2^{t+1}(t+1)!), with ι = −1 and t = 2k+1.

Equivalently, f_k = ln Σ_l w_l e^{β cos θ_l}, the Gauss quadrature of ln(2I₁(β)/β).

The same law holds in the 2D thermodynamic torus limit (C3 with P → ∞).

**Pillow (case (i)).** The pillow is two plaquettes on the same four links: a sphere with F = χ = 2. Its weight is d^χ(a/d)^F = a², with no d at all. Here Z = Σ_j a_j² = [V_0]-coefficient of W(β)² = a_0(2β), in both categories. So Δ ln Z = −β^{2k+2}/(2k+2)! + …, the mirror of the transfer theorem's pillow value +ι/(t+1)!. P1 checks this at k ≤ 2.

**Proposition C3 (2D tori; finite size, case (ii)).** On the L₁×L₂ periodic square lattice, for any L_i ≥ 1 and P = L₁L₂:

  Z = Σ_j (a_j/d_j)^P,  so  ln Z = P ln a_0 + ln(1 + Σ_{j≥1/2} (a_j/(a_0 d_j))^P).

The j = 1/2 term differs from SU(2) at order β^P, with coefficient 2^{−P}([2]^{−P} − 2^{−P}). The ln a_0 term differs at β^{2k+2}, with coefficient −P/(4^{k+1}(2k+2)!). The first difference is at min(P, 2k+2); at equality the two coefficients add.
- **1×2 torus:** β², coefficient tan²(π/(k+2))/16 for every k. Values: 3/16, 1/16, (5−2√5)/16, 1/48, ….
- **2×2 torus:** β⁴, coefficient (sec⁴(π/(k+2)) − 1)/256 for k ≥ 2 (3/256 at k = 2). For k = 1 the coefficient is 37/768.

*Proof.* Labels propagate, because every link lies in two plaquettes. Apply C1 to the whole torus (χ = 0). The 1×2 cell structure has 2 vertices, 4 links and 2 plaquettes, and the link of each vertex is a circle, so C1 applies there too. For the group, ∫ w(X₀Y₀X₁⁻¹Y₀⁻¹)·w(X₁Y₁X₀⁻¹Y₁⁻¹) = Σ_j a_j²/d_j² agrees. ∎ In the thermodynamic limit the torus term vanishes coefficient by coefficient, and C2 is recovered.

**Lemma C4 (minimal configurations in 3D).** Work in ℤ³, or in ℤ_L³ with L ≥ 7, where every configuration of at most 6 plaquettes embeds in ℤ³: wrapping a direction needs at least L plaquettes. Let S ≠ ∅ be the set of nontrivial plaquettes of an admissible configuration. Then:
- |S| ≥ 6, with equality exactly when S is the boundary of a unit cube (and then the label is constant);
- each p ∈ S contributes a_{j_p}/a_0 = O(β^{2j_p}) ⊂ O(β).

*Proof.* A link that carries exactly one nontrivial plaquette is inadmissible, since Hom(1, V_j) = 0.

Let M be the largest z-coordinate among the vertices of S. Suppose no plaquette of S with normal ẑ lies in the plane z = M. Take p ∈ S with a vertex at height M. Then p is vertical, spans [M−1, M], and its top link ℓ lies in the plane z = M. The other plaquettes containing ℓ are two horizontal ones in that plane (excluded by assumption) and one vertical plaquette above (it would have a vertex at M+1). So ℓ lies in only one plaquette of S, a contradiction.

The same argument at the smallest height m gives a horizontal plaquette of S in the plane z = m. Also m < M: a nonempty set of plaquettes in a single plane fails at an extreme link. So S has at least two plaquettes with normal ẑ, and by symmetry at least two each with normals x̂ and ŷ. Hence |S| ≥ 6.

If |S| = 6, look at the top plaquette. Each of its four links needs a second plaquette of S. That plaquette cannot be horizontal, since the only other horizontal one lies at height m < M. So the four vertical plaquettes hanging below the top plaquette are in S, and they are all the vertical plaquettes S has. Their bottom links can then only be covered by the remaining horizontal plaquette, which therefore lies directly below the top one. So S is the boundary of a unit cube. ∎

**Theorem C5 (3D cubic lattice; case (ii)).**

  f₃(β) = ln a_0(β) + (1/3)·[2]^{−4}·(a_{1/2}/a_0)^6 + O(β⁷)

for SU(2)_k. For SU(2), replace [2] by 2; the SU(2) cube term is β⁶/3072 + …. Therefore f₃^{(k)} − f₃^{SU(2)} behaves as follows.

| k | first order | coefficient |
|---|---|---|
| 1 | β⁴ | −1/384 (from ln a_0); the next order, β⁶, has 59/11520 |
| 2 | β⁶ | 1/1024 − 1/46080 = 11/11520 |
| ≥ 3 | β⁶ | c₆(k) = (1/192)([2]^{−4} − 1/16) = (sec⁴(π/(k+2)) − 1)/3072 > 0 |

Exact values of c₆(k): k = 3, (55−24√5)/3072; k = 4, 7/27648; k = 6, (23−16√2)/3072; k = 8, (19−8√5)/15360; k = 10, (111−64√3)/3072. ROWS.hbp lists 12-digit decimals for every k.

Asymptotically, c₆ = (2x² + (7/3)x⁴ + O(x⁶))/3072 with x = π/(k+2), that is π²/(1536(k+2)²)·(1 + O(k⁻²)).

*Proof.* By C4, Z/a_0^{N_p} = 1 + N_cubes·X + O(β⁷), where X = [2]^{−4}(a_{1/2}/a_0)^6. This is C1 with (V, E, F) = (8, 12, 6): χ = 2, so d^{χ−F} = d^{−4}. On ℤ_L³, N_cubes/N_p = 1/3. Then ln(1 + …) = N_cubes·X + O(β⁷). For both categories a_{1/2}/a_0 = β/2 + O(β³). Finally ln a_0 first differs at 2k+2, by C2. ∎

**Plaquette observable.** ⟨P⟩_k − ⟨P⟩_SU(2) first differs at β⁵, with coefficient 6c₆(k) for k ≥ 3. For k = 2 the leading term is (11/1920)β⁵; for k = 1 it is −β³/96.

**Single open cube** (6 plaquettes, 12 links, 8 vertices). Here Z = Σ_j d_j^{−4} a_j^6 exactly, since every link lies in exactly two plaquettes and C1 applies. The first difference in ln Z:
- k ≥ 3: β⁶, coefficient 3c₆(k) = (sec⁴ − 1)/1024;
- k = 2: β⁶, coefficient 43/15360;
- k = 1: β⁴, coefficient −1/64.

**Proposition C6 (the quantum dimension shows whatever plaquette weight is used).** Replace a_j by any series b_j(β) with b_0(0) = 1 and b_{1/2}/b_0 = r₁β + O(β²), where r₁ ≠ 0. Let Z_plaq = b_0 (a single free plaquette), Z_cube be the open cube surface, and Z_{2×3} the 2×3 periodic torus. Then

  Ψ₆ := [ln Z_cube − 6 ln Z_plaq]_{β⁶} / [ln Z_{2×3} − 6 ln Z_plaq]_{β⁶} = d_{1/2}².

For SU(2), Ψ₆ = 4. For SU(2)_k, Ψ₆ = 4cos²(π/(k+2)): 1, 2, 2.618…, 3, …, 3.8019 for k = 1..12.

*Proof.* By C1, the numerator is d^{2−6}r₁⁶ and the denominator is d^{0−6}r₁⁶. Other labels enter only at β^{12}. ∎

No transport of the Wilson weight can hide the quantum dimension. This is the sharpest form of the caveat.

**Remark C7 (the sign depends on how the weight is transported).** Suppose instead the gluing eigenvalues λ_j = b_j/d_j are kept equal to SU(2)'s: b_j := a_0^{SU(2)}·d_j·u_j^{SU(2)}, with u_j = a_j/(a_0(2j+1)) and j ≤ k/2. Then:
- the 2D thermodynamic f agrees with SU(2) to all orders;
- the 3D cube term becomes d²u⁶, so Δf₃ = (1/3)(β/4)⁶([2]² − 4) + O(β⁸) = −sin²(π/(k+2))·β⁶/3072 for every k ≥ 1.

The order β⁶ is robust. The sign and size of the O(1/k²) coefficient depend on the transport (≈ +2x² versus −x², each divided by 3072). C_k uses W from the fusion ring, the exponential of the q-plaquette loop. It is the canonical choice and the one the main rows predict.

**Remark C8 (weak coupling).** By A5, a_j(β)/a_0(β) → U_{2j}(cos(π/(k+2))) = [2j+1] = d_j as β → ∞. So W/a_0 → Σ_j d_j [V_j]. These are the Levin–Wen topological weights a_s ∝ d_s (REPORTED) and the Turaev–Viro end of Oeckl's weak-coupling limit (REPORTED). Quantum dimensions are built into the weight at weak coupling. At strong coupling they enter only through gluing, at the first closed surface that is not a pillow.

2D large-β behaviour:
- f_k = β cos(π/(k+2)) + ln w₁ + O(e^{−β(cos θ₁ − cos θ₂)});
- f_SU(2) = β − (3/2) ln β − (1/2) ln(π/2) + o(1) (NAMED: Bessel asymptotics).

The slope deficit is 1 − cos(π/(k+2)) ≈ π²/(2(k+2)²).

**Conjecture C9 (Hamiltonian qKS, Zache et al. 2023).** Take H′ = Σ_ℓ E_ℓ² − λ Σ_p (𝒰_p + 𝒰_p†) with λ = 1/g⁴ (the paper's rescaling H′ = (2a/g²)H), on the point-split square lattice. Let e₀ = E₀/N_p. Then:
- e₀ = −(4/3)λ² + c₄λ⁴ + O(λ⁶);
- c₄^{SU(2)} = 326/1053;
- c₄^{(k)} = 326/1053 − (256/1053)·tan²(π/(k+2)) for k ≥ 2, and c₄^{(1)} = −16/81.

So the second order agrees for every k, and the first difference is at λ⁴ with an O(1/k²) coefficient.

Derivation (Rayleigh–Schrödinger, linked clusters):
1. Odd orders vanish.
2. At λ², creating a spin-1/2 loop has amplitude 2 and electric energy 4·(3/4) = 3.
3. At λ⁴ there are two kinds of term.
   - Single plaquette: the path 0 → ½ → 1 → ½ → 0, with energies 3, 8, 3; it is absent when k = 1. This term is 2/9 − 16/27.
   - Adjacent pairs sharing an original link: that link ends in channel 0 with probability 1/d² (energy 9/2) or in channel 1 with probability 1 − 1/d² (energy 13/2). This term is (64/9)(2/(9d²) + 2(1 − 1/d²)/13) − 32/27, counted twice per plaquette.
   - Pairs that share only an auxiliary link cancel, because the auxiliary label carries no energy.
4. Then e₄ = −[single + 2·pair].

It is a CONJECTURE because it assumes the following (H-a and H-b are REPORTED; H-c to H-e are not verified for qKS):
- (H-a) E(j) = j(j+1) on original links only (REPORTED).
- (H-b) 𝒰 is built from SU(2)_k F-symbols (REPORTED).
- (H-c) 𝒰† has the same matrix elements as 𝒰 on these states.
- (H-d) plaquette operators on different plaquettes commute (true for SU(2), and for Levin–Wen B_p^s, REPORTED).
- (H-e) the vacuum-channel weight |F|² = 1/d² (this follows from Levin–Wen (8), F^{ijk}_{j*i*0} = v_k/(v_i v_j), REPORTED).

**Conjecture C10 (D = 4).** Same as C5 with 2/3 in place of 1/3: c₆^{4D} = 2c₆^{3D} for k ≥ 3. I checked only that the unit cube is still the minimal closed configuration (C4's argument works in any D) and that an unknotted loop evaluates to d_j. Oeckl's 4D construction needs the ribbon structure, which I have not checked.

**4.12 Which case.**
- **Case (i)** (fusion multiplicities only; first difference at exactly 2k+2): the 2D free boundary, the 2D thermodynamic limit, and the pillow.
- **Case (ii)** (quantum dimensions; low order; O(1/k²) coefficient): every complex that contains an unbranched closed surface with F > χ. This covers the 2D tori at β^{L₁L₂}, and the open cube and the 3D lattice at β⁶.

Rule, DERIVED for these complexes: a closed surface S contributes d^{χ(S)−F(S)}(a_{1/2}/a_0)^{F(S)}. Since χ ≤ 2 ≤ F, the exponent χ − F is zero only for the pillow.

**OPEN.** Is there an SU(2)_k-based 3D lattice theory outside this class, for example one with link variables or a different gluing, whose free energy agrees with SU(2) through order 2k+1? By C6, no theory in the Oeckl class with SU(2)_k gluing can make Ψ₆ = 4.

---

## 5. Sources opened (REPORTED)

**Zache, González-Cuadra, Zoller**, "Quantum and classical spin network algorithms for q-deformed Kogut-Susskind gauge theories", PRL 131, 171902 (2023), arXiv:2304.02527.
- Opened: the abstract page and the HTML of v2. I read the HTML through a fetch tool's extraction, not as the PDF.
- Used:
  - the SU(2)_k labels and the level-k fusion constraint j₁+j₂+j₃ ≤ k;
  - d_j = [2j+1] and q = e^{2πi/(k+2)};
  - the electric term E(j) = j(j+1), truncated to admissible labels and applied to original links only;
  - the plaquette term as a product of SU(2)_k F-symbols on the point-split lattice;
  - H_KS = (g²/2a)ΣE² − (1/2ag²)Σ(𝒰 + 𝒰†), and the rescaled H′ = (2a/g²)H;
  - recovery of Kogut–Susskind as k → ∞.

**Levin, Wen**, "String-net condensation: A physical mechanism for topological phases", PRB 71, 045110 (2005), arXiv:cond-mat/0404617.
- Opened: the abstract, and pages 3–7 of the PDF.
- Used:
  - Fig. 3: SU(2) strings labelled by half-integers with triangle branching;
  - eq. (5): Φ(loop i) = d_iΦ;
  - eq. (8): F^{ijk}_{j*i*0} = v_k/(v_i v_j), with v_i = √d_i;
  - group case: d_i are the irrep dimensions, F is the 6j symbol, and Q_I, B_p are the LGT charge and flux operators;
  - quantum-group 6j symbols give further solutions;
  - B_p = Σ_s a_s B_p^s, with a_s = d_s/Σd_i² for the topological phase, and the B_p^s and Q_I commute.

**Oeckl**, "Generalized lattice gauge theory, spin foams and state sum invariants", J. Geom. Phys. 46 (2003) 308, arXiv:hep-th/0110259.
- Opened: the abstract only.
- Used:
  - a tensor category replaces the gauge group;
  - spherical categories are admissible in dimension ≤ 3, ribbon categories in ≤ 4, symmetric ones in any dimension;
  - ordinary LGT is recovered for Rep of a compact Lie group;
  - weak coupling gives BF theory and Turaev–Viro.
- The state-sum details in §4.1 are mine.

**Local records.**
- `iconic-3-space`, ref `pr7`, `proofs/transfer/TRANSFER-THEOREM.md`: §0–§2.4.
- `predictions/su2-ladder/PREDICTION.hbp` on `main`: the head row and the 2T, 2O and 2I rows.
- The finite-universe documents named in the task exist on `origin/main`. They were not needed for T3; I skimmed only the head of `YM_TOPOLOGICAL_STABILITY_PROOF.md`.

## 6. Pre-freeze computations

Both scripts run as `python3 -I -B`, use integers only (no float, fractions, decimal or math), and each runs in under 0.1 s.

**P1: `t3_small_checks.py`** (`e7e1fb839db6f61f`; output `8c7a22012024b94e`; 41/41 PASS). This is the only fusion enumeration in the lane: k = 1 and k = 2, n ≤ 30. It checks:
- enumeration = A3 = closed forms = A6 = A7;
- the A4 polynomials and A9;
- the C2 first and next coefficients;
- the pillow = a_0(2β);
- the 1×2 and 2×2 tori, the open cube and f₃, at k ≤ 2 with exact d²;
- the C9 arithmetic at d² ∈ {1, 2, 4};
- Ψ₆ = d² with an arbitrary weight.

**P2: `t3_closed_forms.py`** (`efe9a44a9e9dc34b`; output `08ad75df28761589`; 62/62 PASS). Closed forms only, with no fusion iteration and no path enumeration:
- A3 for k = 1..12, which writes `T3_TABLE.txt`;
- consistency of A3 with A2, A4, A6 and A7;
- the C2 rationals;
- 2cos(π/(k+2)) as the largest root of U_{k+1}(x/2), found by integer bisection to 2^{−200};
- 12-digit decimals of the case-(ii) coefficients.

**P3: `t3_rowlint.py`** (`835a9375c1dbc94b`). Format check only. Every row ends in `json=0`, every field is KEY=value, ids are unique, every prediction row has id, tag, met, not_met and falsifier, and the TABLE rows reproduce `T3_TABLE.txt` byte for byte. Result: 69 rows, 0 bad, table match 1.

## 7. Risks

1. **The measurement must be independent.** If the table is measured with the same reflection formula, agreement tests nothing. The measurement should iterate the truncated fusion rule N_{n+1} = A_k N_n.
2. **The construction in (c) is my definition.** I did not read Oeckl's body text. If a measurer uses other link or vertex normalizations, or another weight transport, the result moves to C7 or to something else. Ψ₆ (C6) does not depend on the transport.
3. **The 3D rows need L ≥ 7 or the series limit.** At small L, wrapping surfaces appear at order β^L.
4. **The Hamiltonian row depends on conventions.** C9 uses qKS conventions I could not verify, and I read that paper through an extraction tool.
5. **The 2I numbers are REPORTED.** They come from local documents: MEASURED in TRANSFER-THEOREM, and NOT_RUN predictions in the su2-ladder.
6. **The proofs have no second reader.**
7. **"Design degree" here is the trace-moment notion.** SU(2)_k has no point set on S³. The comparison with groups is fair only because, for groups, the trace-moment degree equals the design degree (Lemma 2.4).
