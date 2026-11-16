# Issue #137 — sufficient absolute-sum certificate for full signed μ₃, Stage C

**Scope.** This note proves a *conditional, exact* numeric bound for either supported accumulation order. It does not certify the amplitude hypothesis, the entire signed source, electric graph completeness, or actual μ₃ by itself.

For the two *frozen* numerators (z_1=69909875505), (z_2=69949729820), scale (b=10^9), the exactly supported signed source is (V_1=XR) on K3 (155,378 orbits), Q4 (1,985,218), and Q5 (18,598,040). Total (N=20,738,636<2^{25}). Every canonical orbit multiplicity (w_i\in\{1,2,3,6\}) gives physical weight (W_i=6w_i\le36<2^6). Electric coefficients (c_{ij}\ge0) have full raw degree (sum_jc_{ij}=72). Magnetic cost satisfies (0\le m_i\le36). All terms and inequalities below are exact integers.

Define (D_i=b(72+9m_i)-z). With either frozen (z), the full row coefficient satisfies
[
|D_i|+72b < 2^{39}.
]
This inequality deliberately retains the total of 72 moves, including self loops and destinations outside the supported source. Its check must be recomputed against the frozen integer (b,z) and actual canonical magnetic labels during production.

**Hypothesis to prove by independent source replay:** for both energies and every one of eight channels,
[
M=\max_{i\in K3\cup Q4\cup Q5,a}|V_{1,i}^{(a)}|<2^{117}.
]

Then, for every supported row,
[
|(XV_1)_i^{(a)}|
\le (|D_i|+b\textstyle\sum_j c_{ij})M
<2^{39}\,2^{117}=2^{156}.
]
Thus every row contribution to the (8\times8) matrix
[
\mu_{3,6}=\sum_i W_i V_{1,i}(XV_1)_i^T
]
has absolute value strictly below (2^{6+117+156}). Summing at most (N<2^{25}) such terms bounds **the absolute sum of all terms**, and hence every possible signed prefix partial sum, strictly below
[
2^{6+117+156+25}=2^{304}<2^{319}.
]

**Separately for weighted unordered pairs.** Weighted reciprocity (w_ic_{ij}=w_jc_{ji}) is a separate production gate. Write each pair contribution for (i<j) as
[
-6b\,w_ic_{ij}
\left(V_i^{(a)}V_j^{(b)}+V_j^{(a)}V_i^{(b)}\right).
]
The absolute pair total is bounded by
[
6bM^2\sum_{i<j}2w_ic_{ij}
=6bM^2\sum_{i\ne j}w_ic_{ij}
\le36N(72b)M^2.
]
Diagonal plus self-loop terms have absolute total at most
[
6M^2\sum_iw_i(|D_i|+bc_{ii}).
]
Combining both is at most (36NM^2 \max_i(|D_i|+72b)<2^{304}). Therefore **every prefix partial sum** of the paired-edge accumulator is also strictly below (2^{304}), without depending on cancellation or edge order.

**Q5 amplitude component.** The already authenticated 18,598,040 Q5 positive source vectors store unsigned packed `V1/b` lanes of width 82. As (b=10^9<2^{30}), each physical Q5 amplitude is (<2^{112}), satisfying the global (2^{117}) hypothesis. The new full signed writer must independently prove this threshold on *every* K3 and Q4 physical **V1=X R** amplitude, not merely on the input residual (R).

**Hold gates.** The production `M<2^{117}` test must pass using independently authenticated nine signed K3/Q4 source archives; geometry and source membership must be complete and disjoint from the accepted Q5 source. Each accumulator still requires signed 320-bit checked overflow and the strict (2^{304}) runtime limit. A 192-bit signed storage format alone is insufficient. If the real maximum fails the 117-bit hypothesis, derive another certified per-block/weighted absolute-sum bound; never weaken or quietly relabel the threshold.

**Current verdict:** conditional inequality PROVED; measured complete-source maximum PENDING; all supported real μ₃ matrices NOT_COMPUTED; Wilson first-excitation weight HOLD.
