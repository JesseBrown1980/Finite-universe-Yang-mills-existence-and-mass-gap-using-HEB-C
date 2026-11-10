# T2: how the break moves for finite subgroups of SU(2), predictions only

2026-11-09 · prediction lane T2 · nothing here is MEASURED. No exact plaquette curve was evaluated, no torus was diagonalised, and nothing was written outside this lane directory.

**Tags.** DERIVED: proved in this note, possibly using a REPORTED input. REPORTED: from a source whose record I opened (listed in §10). CONJECTURE: a numeric value or interval from truncated asymptotic expansions, or a claim not proved here. OPEN: not settled here.

**The owner's frame, as applied here.** A finite subgroup G ⊂ SU(2) looks like SU(2) up to a resolution and then breaks at a computable point. In the 2D one-plaquette observable, two finite invariants of G control the break:

- **The onset** β_x is set by the design degree t, through the Casimir of the first missing spin j* = (t+1)/2.
- **The turnover** (the peak of the deviation and its descent) is set by the gap Δ₁ to the nearest non-identity element, together with its multiplicity N₁.

At large β every group converges to the same G-independent envelope, which is SU(2)'s own Gaussian-fluctuation term 3/(2β). That envelope is the shared fingerprint in this test.

---

## 1. Definitions (used by every row)

- c_g = tr(g)/2 ∈ [−1, 1]. The 2D lattice with free boundary factorises into independent plaquettes (gauge-fix on a maximal tree: each plaquette variable is then uniform on K and independent; this is the same model as `predictions/su2-ladder`). So everything reduces to one plaquette.
- z_G(β) = |G|⁻¹ Σ_g e^{β c_g} and P_G(β) = d ln z_G/dβ = Σ_g c_g e^{β c_g} / Σ_g e^{β c_g}.
- z_SU2(β) = ∫ dU e^{β tr U/2} = 2 I₁(β)/β and P_SU2(β) = I₂(β)/I₁(β).
- **Relative deviation** δ_G(β) = P_G(β)/P_SU2(β) − 1. It is positive (Theorem 3), so it equals |P_G − P_SU2|/P_SU2.
- For a threshold θ:
  - β_up(θ) = inf{β > 0 : δ_G(β) ≥ θ}
  - β_down(θ) = sup{β > 0 : δ_G(β) ≥ θ}
  - "never" means sup_β δ_G < θ.
- β_x(G) = β_up(1/100). The peak is (argmax δ_G, max δ_G).
- d_n = dim V_{n/2}^G, the Molien coefficient, so n = 2j. M_n^K = E_K[(tr U)^n].

## 2. Part (a): design degree, ι_G, and the Transfer coefficients

**Lemma A** (Transfer theorem, Lemma 2.4 and Cor. 2.5, re-derived; DERIVED). For a finite subgroup G:

1. M_n^G − M_n^Haar = Σ_{j>0} m(n,j) d_{2j} ≥ 0, where m(n,j) is the Clebsch–Gordan multiplicity of spin j in (½)^{⊗n} and m(n, n/2) = 1.
2. Hence t(G) + 1 = min{n ≥ 1 : d_n > 0}, and ι_G = M_{t+1}^G − M_{t+1}^Haar = d_{t+1}.

**Lemma B** (2D one-plaquette coefficient; DERIVED). ln z_K(β) = Σ_{n≥1} κ_n^K β^n / (2^n n!), with κ_n the cumulants of tr U under K.

- If M_n^G = M_n^H for n ≤ t, then the cumulants agree for n ≤ t.
- κ_{t+1}^G − κ_{t+1}^H = M_{t+1}^G − M_{t+1}^H, because κ_{t+1} is M_{t+1} plus a polynomial in M_1..M_t.
- So ln z_G − ln z_SU2 = ι β^{t+1}/(2^{t+1}(t+1)!) + O(β^{t+2}).
- Differentiating gives P_G − P_SU2 = ι β^t/(2^{t+1} t!) + O(β^{t+1}).

These are exactly Transfer 1's per-plaquette coefficients (B) and (C′). In 2D they hold on the nose for every plaquette.

**Invariant degrees** (Klein; a standard result, used here only as a cross-check). The Molien series is (1 + t^p)/((1 − t^q)(1 − t^r)), with (q, r, p):

| group | (q, r, p) |
|---|---|
| Z_m | (2, m, m) |
| Dic_n | (4, 2n, 2n+2) |
| 2T | (6, 8, 12) |
| 2O | (8, 12, 18) |
| 2I | (12, 20, 30) |

So the smallest positive invariant degree is 2 for Z_m (m ≥ 3), 4 for Dic_n (n ≥ 2), and 6, 8, 12 for 2T, 2O, 2I. The value of ι is 1, except ι = 2 for Q8, where 2n = 4 makes x⁴ + y⁴ a second quartic invariant.

**Pre-freeze check.** Script `prefreeze/t2_groups.py` (§9) independently verified the inputs:

- It built all ten groups by exact quaternion closure over Z[√2], Z[√3] and Z[φ].
- It recomputed d_n (n ≤ 40) from the group as averages of Chebyshev characters, and found them equal to Klein's closed forms.
- It recomputed M_n from the group, and found them equal to Σ m(n,j) d_{2j}.
- 151 of 151 checks passed.

The values also agree with Transfer 1 §2.4 (M₄ = 3 and M₆ = 11 for Dic₃, M₆ = 10 for Dic₄, M₆ = 6 for 2T, M₈ = 15 for 2O, M₁₂ = 133 for 2I).

| G | \|G\| | t | ι | M_{t+1}^G | M_{t+1}^Haar | coefficient of β^{t+1} in ln z_G − ln z_SU2 | coefficient of β^t in P_G − P_SU2 |
|---|---|---|---|---|---|---|---|
| Z₃ | 3 | 1 | 1 | 2 | 1 | 1/8 | 1/4 |
| Z₄ | 4 | 1 | 1 | 2 | 1 | 1/8 | 1/4 |
| Z₆ | 6 | 1 | 1 | 2 | 1 | 1/8 | 1/4 |
| Q8 = Dic₂ | 8 | 3 | 2 | 4 | 2 | 1/192 | 1/48 |
| Dic₃ | 12 | 3 | 1 | 3 | 2 | 1/384 | 1/96 |
| Dic₄ | 16 | 3 | 1 | 3 | 2 | 1/384 | 1/96 |
| Dic₆ | 24 | 3 | 1 | 3 | 2 | 1/384 | 1/96 |
| 2T | 24 | 5 | 1 | 6 | 5 | 1/46080 | 1/7680 |
| 2O | 48 | 7 | 1 | 15 | 14 | 1/10321920 | 1/1290240 |
| 2I | 120 | 11 | 1 | 133 | 132 | 1/1961990553600 | 1/163499212800 |

## 3. Exact structure of the one-plaquette curve (DERIVED)

**Proposition 1** (character identity). For every finite G ⊂ SU(2) and every real β:

  z_G(β) = (2/β) Σ_{n≥0} d_n (n+1) I_{n+1}(β).

Equivalently, R(β) := z_G/z_SU2 = Σ_{n≥0} d_n (n+1) I_{n+1}(β)/I₁(β), and P_G − P_SU2 = R′/R.

*Proof.*
1. The class function f(θ) = e^{β cos θ} expands in characters as f = Σ_j a_j χ_j, with a_j = ⟨f, χ_j⟩_Haar.
2. Weyl's measure on classes is (2/π) sin²θ dθ, and χ_j = sin((2j+1)θ)/sin θ. So a_j = (1/π) ∫₀^π [cos 2jθ − cos(2j+2)θ] e^{β cos θ} dθ = I_{2j}(β) − I_{2j+2}(β), using DLMF 10.32.3. By DLMF 10.29.1 this equals (2(2j+1)/β) I_{2j+1}(β).
3. Averaging over G gives E_G[χ_j] = dim V_j^G = d_{2j} (Lemma A). Exchanging the finite average with the sum is legitimate because the a_j decay faster than any power for fixed β. For j = 0, (2/β) I₁ = z_SU2. ∎

So the finite group is SU(2) plus the "defect spins" 2j = n ≥ t+1:

  R − 1 = Σ_{n ≥ t+1} d_n (n+1) I_{n+1}/I₁.

**Lemma 2** (Bessel ratios increase). For ν ≥ 0, y_ν(x) = I_{ν+1}(x)/I_ν(x) is strictly increasing on (0, ∞).

*Proof.*
1. DLMF 10.29.2 gives the Riccati equation y′ = 1 − (2ν+1)y/x − y².
2. Its positive equilibrium is Y(x) = x/((ν+½) + √((ν+½)² + x²)). Y is strictly increasing, and 1 − (2ν+1)y/x − y² = −(y − Y)(y − Y₋) with Y₋ < 0.
3. Near 0, y ≈ x/(2ν+2) < x/(2ν+1) ≈ Y.
4. At a first point where y = Y we would have y′ = 0 < Y′. That contradicts reaching Y from below. So y < Y on (0, ∞), and therefore y′ > 0. ∎

(The same argument gives the lower bound y > x/((ν+1) + √((ν+1)² + x²)).)

**Theorem 3** (the finite group's plaquette is always larger).

1. P_G(β) > P_SU2(β) for every β > 0 and every finite G. Proof: I_{n+1}/I₁ = Π_{k=1}^{n} y_k is strictly increasing, so R′ = Σ d_n (n+1)(I_{n+1}/I₁)′ > 0, because d_{t+1} = ι ≥ 1. Then P_G − P_SU2 = R′/R > 0.
2. Since P_G < 1 whenever G ≠ {1}, there is a G-independent envelope: δ_G(β) < E(β) := I₁(β)/I₂(β) − 1 for every β > 0.

**Corollary 4** (small β; DERIVED). From Lemma B and P_SU2 = β/4 − β³/96 + …:

  δ_G(β) = ι β^{t−1}/(2^{t−1} t!) + O(β^t).

| G | small-β form of δ_G |
|---|---|
| Q8 | β²/12 |
| Dic_n (n ≥ 3) | β²/24 |
| 2T | β⁴/1920 |
| 2O | β⁶/322560 |
| 2I | β¹⁰/40874803200 |
| Z₃ | 1 + β/2 + O(β²) (M₃ = 2 ≠ 0) |
| Z₄ | 1 − β²/12 + O(β⁴) |
| Z₆ | 1 − β²/6 + O(β⁴) |

For the t = 1 groups, δ(0+) = ι = 1: the cyclic groups are 100 % off from the start, and β_x(Z_m) = 0.

**Corollary 5** (large β; DERIVED, with DLMF 10.40.1 REPORTED).

- Let Δ₁ = 1 − c₁, where c₁ is the largest c_g < 1, and let N₁ = #{g : c_g = c₁}. Then 1 − P_G(β) = N₁Δ₁ e^{−βΔ₁}(1 + O(e^{−βΔ₁}) + O(e^{−β(Δ₂−Δ₁)})).
- The Hankel expansion gives P_SU2 = 1 − 3/(2β) + 3/(8β²) + 3/(8β³) + 63/(128β⁴) + 27/(32β⁵) + …
- It also gives E(β) = 3/(2β) + 15/(8β²) + 15/(8β³) + 135/(128β⁴) − 45/(32β⁵) + …. These are exact rationals from `t2_asym.py`, row SU2_LARGE_BETA.
- Exactly, δ_G = E − (1 − P_G)/P_SU2. So every group's deviation approaches the same envelope from below, at the rate N₁Δ₁e^{−βΔ₁}.

| G | c₁ | Δ₁ | N₁ | N₁Δ₁ |
|---|---|---|---|---|
| Z₃ | −1/2 | 3/2 | 2 | 3 |
| Z₄ | 0 | 1 | 2 | 2 |
| Z₆ | 1/2 | 1/2 | 2 | 1 |
| Q8 | 0 | 1 | 6 | 6 |
| Dic₃ | 1/2 | 1/2 | 2 | 1 |
| Dic₄ | √2/2 | 1 − √2/2 | 2 | 2 − √2 |
| Dic₆ | √3/2 | 1 − √3/2 | 2 | 2 − √3 |
| 2T | 1/2 | 1/2 | 8 | 4 |
| 2O | √2/2 | 1 − √2/2 | 6 | 6 − 3√2 |
| 2I | (1+√5)/4 | (3−√5)/4 | 12 | 3(3−√5) |

In every case Δ₁ = 1 − cos(2π/N_max), where N_max is the largest element order. These values were read off the exact closure in `GROUPS.hbp`.

**No transition in 2D** (DERIVED). P_G is a ratio of finite exponential sums with a positive denominator, so it is real-analytic on ℝ. The 2D counterpart of four-dimensional freezing is the smooth hump of δ_G described in §6.

## 4. The three asymptotic tools (what was computed, and why it is not a measurement)

All three are truncated asymptotic expansions, evaluated in integer fixed point (10⁵⁰) by `prefreeze/t2_asym.py`. None of them is the exact curve.

- **S, strong coupling.** δ = W(x)/D(x) with x = β/2. The integer exponential-generating-function coefficients are W_n = Σ_k C(n,k)(M^G_{k+1}M^H_{n−k} − M^G_k M^H_{n−k+1}) and D_n = Σ_k C(n,k) M^G_k M^H_{n−k+1} (they are the Wronskian of z_G and z_SU2).
  - W_n = 0 for n < t, and W_t = ι.
  - The series is truncated at relative order r ∈ {8, 12}. It is used only on β ≤ 2.5.
  - Error estimate: S12 − S8.
  - Note: the Taylor series of P_SU2 = I₂/I₁ at β = 0 has radius j₁,₁ ≈ 3.83, set by the poles at β = ±i j₁,₁, where I₁(iy) = iJ₁(y) vanishes (standard value, not opened). So the strong-coupling expansion that carries Transfer 1's coefficient cannot reach the onset of 2O or 2I, whose β_x lies beyond 3.83.
- **D, character + Debye.** Proposition 1 truncated to the first K = 4 nonzero defect degrees, compared with K = 3.
  - Each I_{n+1} uses Debye's uniform expansion (DLMF 10.41.3 and 10.41.5) through U₄ and V₄, with the polynomials generated by the recursion 10.41.9. Their coefficients were checked against 10.41.10 and 10.41.11 and against Stirling at p = 1.
  - The SU(2) side is computed two ways: by Debye with ν = 1, 2, or by Hankel (DLMF 10.40.1) with optimal truncation.
  - Error estimates: D4 − D3; the contribution of the first omitted defect; Hankel against Debye on the SU(2) side.
- **L, gap.** The two-class model P₂ = (1 + N₁c₁e^{−βΔ₁})/(1 + N₁e^{−βΔ₁}) over the Hankel P_SU2.
  - Rigorous on the group side: 0 ≤ P₂ − P_G ≤ 2(|G| − 1 − N₁)e^{−βΔ₂}/(1 + N₁e^{−βΔ₁}). All dropped classes lie below c₂ < c₁ ≤ P₂, so dropping them can only raise the mean.
  - So L is an upper bound for δ_G whenever P_SU2 is exact, and L_LOWER = L − bound is a lower bound.
  - Caveat: Z₃ has a single non-identity trace value, so for Z₃ the two-class model is the full class sum. Only its SU(2) side is asymptotic.

**Choosing a tool for each crossing** (rule fixed before the rows were written):

1. Use S if the crossing lies at β ≤ 2.5.
2. Otherwise use D, if D4 − D3 and the omitted-defect term are small compared with θ and the two SU(2) evaluations agree.
3. Otherwise use L when its rigorous bracket [L_LOWER, L] is tight.

**Interval half-width** = max(0.2 % of the central value, about three times the spread between tools or truncations), widened by hand where the tools are known to be weak. Each case is stated in the row.

**Cross-validation between independent methods.** S uses integer moments; D uses Molien coefficients and Debye.

- At small β they agree, e.g. 2O at β = 2: 1.458·10⁻⁴ against 1.459·10⁻⁴.
- At the turnover D and L agree, e.g. 2I near β = 27.5: 0.045169 against the bracket [0.044975, 0.045180].

## 5. Part (b): the onset β_x(G) and its law in t

| G | t, ι | β_x (S or D) | tool spread | predicted interval | Transfer-leading law 2(ε t!/ι)^{1/(t−1)} | heat-kernel law |
|---|---|---|---|---|---|---|
| Z₃, Z₄, Z₆ | 1, 1 | 0 (δ(0+) = 1) | — | 0, DERIVED | — | — |
| Q8 | 3, 2 | 0.348038 | < 10⁻⁶ | [0.3473, 0.3488] | 0.34641 | 1.155 |
| Dic₃ | 3, 1 | 0.494155 | < 10⁻⁶ | [0.4932, 0.4951] | 0.48990 | 1.275 |
| Dic₄ | 3, 1 | 0.494925 | < 10⁻⁶ | [0.4939, 0.4959] | 0.48990 | 1.275 |
| Dic₆ | 3, 1 | 0.494926 | < 10⁻⁶ | [0.4939, 0.4959] | 0.48990 | 1.275 |
| 2T | 5, 1 | 2.29211 (S12); S8 2.29132; D 2.29110 | 0.001 | [2.287, 2.297] | 2.09327 | 2.9465 |
| 2O | 7, 1 | 4.86710 (D, Debye) / 4.86722 (D, Hankel) | 1.2·10⁻⁴ | [4.857, 4.877] | 3.84387 | 5.3848 |
| 2I | 11, 1 | 12.29801 (D, both) | 10⁻⁵ | [12.273, 12.323] | 7.26349 | 12.6259 |

**Dihedral fine structure** (structure DERIVED; numbers CONJECTURE).

- Dic₄ and Dic₆ have equal moments through M₇ (M₈ = 36 against 35), so their onsets differ only at relative order β⁶: β_x(Dic₆) − β_x(Dic₄) = +1.2·10⁻⁶.
- Dic₃ has M₆ = 11 against 10, so it breaks earlier: β_x(Dic₄) − β_x(Dic₃) = 7.69·10⁻⁴.
- Every Dic_n with n ≥ 3 shares the leading law β²/24.

**Law in t** (structure DERIVED from Proposition 1; numbers CONJECTURE).

The onset is the solution of the first-defect equation

  ι (t+2) · (d/dβ)[I_{t+2}(β)/I₁(β)] ≈ ε · I₂(β)/I₁(β),  ε = 1/100.

It has two limiting forms.

1. **Strong-coupling (Transfer) regime, β_x ≪ 1.**
   - Here I_{t+2}/I₁ ≈ (β/2)^{t+1}/(t+1)!, which gives β_x ≈ 2(ε t!/ι)^{1/(t−1)}.
   - By Stirling, this tends to (2/e)(t+1)(1 + o(1)). This is the "β_x ~ c(t+1)" law, with c = 2/e ≈ 0.736, that one would get by extrapolating Transfer 1's first coefficient.
   - It ignores the growth of the denominator I₁(β) ~ e^β/√(2πβ), and it under-predicts the onset increasingly: by 0.47 % (Q8), 0.86 to 1.02 % (Dic), 8.7 % (2T), 21.0 % (2O) and 40.9 % (2I).
2. **Heat-kernel regime, β_x ≫ 1.**
   - Here I_{n+1}/I₁ ≈ e^{−n(n+2)/(2β)} = e^{−2j(j+1)/β}: the defect of spin j is weighted by its Casimir.
   - With j* = (t+1)/2 and 2C₂ = (t+1)(t+3)/2, the onset is β_x ≈ 2C₂/Λ_t, where Λ_t is the larger root of Λ² e^{−Λ} = ε P_SU2 · 2C₂/(ι (t+2)).
   - This law over-predicts: by factors 2.58 (Dic), 1.285 (2T), 1.106 (2O) and 1.027 (2I).

The truth lies strictly between the two laws for every rung with t ≥ 3. It sits near the Transfer law at t = 3 and near the heat-kernel law at t = 11. Debye's uniform expansion interpolates between them, and its accuracy here is of order 10⁻⁵ to 10⁻⁶.

The values below were computed by hand from the central values in the table above:

| t | c_t = β_x/(t+1) | Λ_t = (t+1)(t+3)/(2β_x) |
|---|---|---|
| 3 | 0.1235 | 24.28 |
| 5 | 0.3820 | 10.47 |
| 7 | 0.6084 | 8.218 |
| 11 | 1.0248 | 6.830 |

- No linear law fits: c₁₁/c₃ = 8.30.
- The effective exponent d ln β_x / d ln(t+1) between successive rungs is 3.78, 2.62 and 2.29.
- So the onset grows faster than linearly and, at t = 11, roughly quadratically. It is set by the Casimir of the first missing spin over a slowly drifting log-weight Λ_t.
- Extrapolation (CONJECTURE; untestable with subgroups, since t ≤ 11): Λ_t keeps decreasing toward 2. The first-defect peak then shrinks like 1/t, so for hypothetical designs with t ≳ 10² a 1 % onset would not exist in this observable.

## 6. Part (c): turnover, thresholds 10 % and 50 %, peaks

Here is the predicted shape (from the tools; CONJECTURE):

- **Z₄ and Z₆** decrease monotonically from δ(0+) = 1.
- **Z₃** first rises to a maximum of 1.2402 at β ≈ 0.886 (S, converged to 10⁻⁵), then decreases.
- **Every group with t ≥ 3** is unimodal. It rises as ιβ^{t−1}/(2^{t−1}t!), peaks, and falls toward E(β) − N₁Δ₁e^{−βΔ₁}.
- **Every group** finally crosses 1 % on the way down at the universal envelope value E⁻¹(1/100) = 151.2479. This holds to within 10⁻⁵ for all ten groups: even Dic₆ is frozen to 10⁻⁹ by β = 151.

| G | β_up(10 %) | β_down(10 %) | β_up(50 %) | β_down(50 %) | peak value | peak at β |
|---|---|---|---|---|---|---|
| Z₃ | 0 | 16.22874 (L, group side exact) | 0 | 4.0531 (L, Hankel side); a Debye SU(2) side shifts the envelope crossing by +0.0035 | 1.24016 | 0.886 |
| Z₄ | 0 | 16.22871 (L, bracket < 10⁻¹²) | 0 | 3.690 to 3.706 (L, Hankel); 3.7025 (D, Debye) | 1 (sup at 0+) | 0+ |
| Z₆ | 0 | 16.17822 (L) | 0 | ≈ 2.64 (S at 2.5 extrapolated; D gives 2.653 with a Debye-side bias of about +0.01) | 1 (sup at 0+) | 0+ |
| Q8 | 1.155757 (S) | 16.22865 (L) | never | never | 0.3700 to 0.3715 | 3.72 to 3.77 |
| Dic₃ | 1.719952 (S) | 16.1779 to 16.1782 (L bracket) | never | never | 0.2479 | 4.68 |
| Dic₄ | 1.761251 (S) | 15.1919 to 15.1932 (L bracket) | never | never | 0.2100 | 4.27 to 4.29 |
| Dic₆ | 1.762092 (S) | 11.18 to 11.25 (D: K = 3 gives 11.138, K = 4 gives 11.177, omitted terms are positive; L upper bound 11.483) | never | never | 0.2060 | 4.13 to 4.15 |
| 2T | 5.56383 (D, both SU(2) sides) | 16.0112 to 16.0118 (L bracket) | never | never | 0.14305 (D); L bracket [0.1403, 0.1440] | 8.91 |
| 2O | never | never | never | never | 0.08445 (D) | 14.46 |
| 2I | never | never | never | never | 0.04517 (D; L bracket [0.04498, 0.04518]) | 27.50 |

**Envelope crossings** (SU(2) only; Hankel against Debye):

- E⁻¹(1/2) = 4.1179 (Hankel) / 4.1215 (Debye).
- E⁻¹(1/10) = 16.22874 / 16.22872.
- E⁻¹(1/100) = 151.24791, the same both ways.

By Theorem 3, every group has β_down(1/2) < E⁻¹(1/2) and β_down(1/10) < E⁻¹(1/10).

**Fingerprints.** Groups that share (c₁, N₁) share their large-β crossings:

- Z₆ and Dic₃ both have (½, 2). Their 10 % descents agree to 3·10⁻⁴: 16.17822 against 16.1779–16.1782.
- Z₃, Z₄ and Q8 are all frozen by β ≈ 16, so their 10 % descents equal E⁻¹(1/10) to within 10⁻⁴.

**Freezing law for the peak** (derived from Corollary 5 by maximising E − N₁Δ₁e^{−βΔ₁}; CONJECTURE as a numeric law).

- Write x* = β_peak Δ₁. It solves x* = ln(2N₁x*²/3), so it depends on N₁ alone: 4.3066 for N₁ = 6 (Q8 and 2O), 4.8192 for N₁ = 8 (2T), and 5.4826 for N₁ = 12 (2I).
- The peak height is δ_peak ≈ (3Δ₁/2)(x* − 1)/x*², which is proportional to the gap.
- A root exists only for N₁ ≥ 3. For N₁ = 2 (all Z_m and Dic_n with n ≥ 3) the peak is not controlled by the nearest class.
- The law gives β_peak = 9.638, 14.704 and 28.707 for 2T, 2O and 2I, against the tool values 8.911, 14.457 and 27.503.
- It gives δ_peak = 0.1233, 0.0783 and 0.0427, against 0.1430, 0.0844 and 0.0452. The law is low by 5 to 16 %.
- A near-universal combination follows: δ_peak·β_peak = 1.275 (2T), 1.221 (2O), 1.242 (2I), close to (3/2)(1 − 1/x*).

**Reading of part (c).**

- The 50 % threshold is crossed only by the cyclic groups, which start at 100 %, and only on the way down. The crossing points are 4.05 (Z₃), 3.70 (Z₄) and 2.64 (Z₆).
- The 10 % threshold is crossed upward only by Q8, Dic₃, Dic₄, Dic₆ and 2T. It is never crossed by 2O (peak 8.4 %) or 2I (peak 4.5 %).
- Its downward crossing sits at the universal 16.23 for groups that are frozen by then, and earlier when the gap is small: 16.01 (2T), 15.19 (Dic₄), about 11.2 (Dic₆).

## 7. Four dimensions (REPORTED only; no 4D numbers are predicted)

- **Petcher and Weingarten**, Phys. Rev. D 22, 2465 (1980), doi:10.1103/PhysRevD.22.2465 (INSPIRE record 153202 opened). Monte Carlo study of the gauge theories on the tetrahedral, octahedral and icosahedral subgroups of SU(2). Two phases separated by a first-order transition. "The critical gauge coupling constant moves toward zero as the order of the group is increased." The largest group agrees with Creutz's SU(2) results.
- **Rebbi**, Phys. Rev. D 21, 3350 (1980), doi:10.1103/PhysRevD.21.3350 (INSPIRE record opened). Four-dimensional models on finite non-Abelian groups: "All models examined exhibit a two-phase structure with a first-order phase transition." For the three subgroups of SU(2), the critical temperature moves toward zero as the group order increases.
- **Bhanot and Rebbi**, Phys. Rev. D 24, 3319 (1981), doi:10.1103/PhysRevD.24.3319 (INSPIRE record opened). The record concerns five finite subgroups of **SU(3)**, not SU(2): each has a first-order freezing transition before the continuum scaling region. No Bhanot–Rebbi 1981 SU(2)-subgroup paper was found. The same search returned Bhanot–Rebbi, Nucl. Phys. B180, 469 (1981), which is on SU(2) itself.

The 2D analogue predicted here is smooth (§3). Its peak position grows with |G| along 2T → 2O → 2I (8.9, 14.5, 27.5), the same ordering as the reported 4D trend. This is a qualitative parallel only.

## 8. What this does not settle (OPEN)

- Rigorous two-sided bounds on δ_G in the window between the tools, for example Dic₆ on 13 ≲ β ≲ 20, where D and L both have errors of order 10⁻³. Unimodality there is a CONJECTURE.
- Rigorous error bounds for the Hankel expansion of I_ν. DLMF 10.40(ii) states such bounds only for K_ν. The SU(2)-side error bars here are first-omitted-term estimates.
- A proof that sup δ_G < 10 % for 2O. The tools give 8.44 %, and L is a rigorous upper bound for β ≳ 9, but on the rising side only D, without a bound, is available.

## 9. Pre-freeze computations (all small; integers only; `python3 -I -B`)

| script | sha256 (first 16 hex) | output | output sha256 (first 16 hex) | what it computed |
|---|---|---|---|---|
| `prefreeze/t2_groups.py` | ae3a722e77b7e4b6 | `prefreeze/GROUPS.hbp` | 101da05eeeeda698 | Exact closure of the 10 groups; moments M_n (n ≤ 42); d_n by group sum and by Klein; t, ι, coefficients; trace classes; integer Wronskian series W_n, D_n (n ≤ 30). 151 checks, 0 failed. Runtime 0.1 s. |
| `prefreeze/t2_asym.py` (final) | 0f81d575be9c246a | `prefreeze/ASYM.hbp` | 3a0533ad62a3358f | Tools S, D and L on a β grid; crossings by bisection; local maxima; closed-form laws; exact Hankel series of P_SU2 and E; Debye polynomial checks. 12 checks, 0 failed. Runtime 9 s. |

Development runs of `t2_asym.py`, superseded and with their outputs overwritten: sha256 fe60126fd161300c (first version, defect cut by degree) and 901f3dc3bef21067 (before the no-root guard for the gap law). They differ only in truncation bookkeeping and in reporting.

**Disclosure.** While planning, before any script ran, I did rough mental arithmetic at a few points for orientation: Z₃ and Dic₃ at β = 4, the N(T) = U(1) ⋊ Z₂ model at β = 5 and 10, and the gap model for 2I at β = 16 to 35. No row value comes from that arithmetic.

No SU(2)_k enumeration, no torus and no Feshbach computation was done.

## 10. Sources opened

- DLMF §10.29 (eqs 10.29.1 and 10.29.2), §10.32 (eq 10.32.3), §10.40 (eq 10.40.1; §10.40(ii) gives bounds only for K_ν), §10.41 (eqs 10.41.3, 10.41.5, 10.41.7 to 10.41.11).
- INSPIRE records for Petcher–Weingarten 1980, Rebbi 1980, and Bhanot–Rebbi 1981 (PRD 24, 3319; NPB 180, 469), as in §7.
- Transfer 1: `iconic-3-space` ref pr7, `proofs/transfer/TRANSFER-THEOREM.md`, §§0, 2.4, 3, 4 and 7. `predictions/su2-ladder/PREDICTION.hbp`, for the 2D model and the HBP style.
