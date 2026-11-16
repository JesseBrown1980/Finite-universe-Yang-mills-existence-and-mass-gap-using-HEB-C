# Y137 Stage G-continuous — exact Wilson-shift interval screening

**Research draft, 2026-11-16.** Reuses the original certified PR #180 unshifted Wilson sample, original #185 full-Q source norm enclosures, accepted Stage E/F per-state error limits and verified Stage G 29-point rational-shift test.

## Hosted result — exact rational intervals

[Original hosted run #43954615820](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43954615820) passed source controls and the real interval calculation. Its entire numerical output is frozen byte-for-byte in [RESULT-G-CONTINUOUS-20261116.hbp](RESULT-G-CONTINUOUS-20261116.hbp). A separate exact-integer replay of its original flat-norm and signed-sample formulas reproduced the two endpoints, all 29 original point classifications and the counts:

| Gate | Exact result |
| --- | --- |
| Shift domain | ([0,14]) |
| Binary split depth | 13 |
| Entire intervals excluded by the existing sufficient test | 20 |
| Unresolved final leaf cells | 3,533 |
| Left outside interval | ([0,5663/1024]) excluded |
| Middle candidate band | ([5663/1024,47383/4096]) inconclusive |
| Right outside interval | ([47383/4096,14]) excluded |
| Actual first Wilson spectral weight | **HOLD** |

The closed middle band is an **overapproximation of remaining candidates**: shared boundary points may also have independent exclusion witnesses. No real shift strictly outside that band in ([0,14]) can close the *existing frozen sufficient test*. No claim is made for shifts outside the tested domain, for a stronger transfer inequality, or for a different Wilson sample.

## What this proves

The original Stage G screening enumerated 29 half-unit shifts of the same physical seven-loop Wilson observable \(O\), from \(\alpha=0\) through \(14\). This extension covers **every real** rational-interval position on \([0,14]\) by a finite union of exact closed dyadic intervals. In each excluded cell it certifies that even the **minimal** accepted lower bound on the old observable-specific linear transfer cost exceeds the **maximal** source-certified shifted Wilson sample-amplitude upper bound over the entire cell.

For state \(i\), the physical eight-flat source quadratic is exactly

\[
p_i=\sum_j w_j v_{ij}^2,\quad s_i=\sum_j w_j O_j v_{ij}^2,\quad
t_i=\sum_j w_j O_j^2v_{ij}^2.
\]

The squared flat-action contribution for the shifted observable \(O_\alpha=O-\alpha I\) is

\[
\|O_\alpha U_i\|_W^2\ \ge\
\frac{p_i\alpha^2-2s_i\alpha+t_i}
 {p_i(1+q_i^2)},
\]

where \(q_i\) is the outward-rounding upper bound on original full-Q norm divided by the flat norm. The minimum of this quadratic on \([\ell,h]\) is attained at its exact rational vertex \(\alpha_i^*=s_i/p_i\), if inside, or at an endpoint.

The original source provides a signed centre \(C\) and error \(E\) for \(2O-7\), and a signed overlap \(V\) with error \(E_V\). Therefore

\[
|\langle U_2,O_\alpha U_1\rangle|
\le\frac{|C+(7-2\alpha)\,bV|+E+|7-2\alpha|E_V}
 {2b\,\|U_1\|\,\|U_2\|}.
\]

The source normalization is **lower** bounded by the physical eight-flat norm product, so this remains an upper bound. Because the upper envelope is convex in \(\alpha\), its maximum on a closed interval occurs at an endpoint. Outward integer square roots and ceilings preserve both inequality directions.

Define \(d_1=3235251105/10^{12}\), \(d_2=8676646901/10^{12}\). An interval is labeled \`EXCLUDED\` only when

\[
d_2\min_{\alpha\in I}\|O_\alpha U_1\|_{\rm flat,lower}
+d_1\min_{\alpha\in I}\|O_\alpha^* U_2\|_{\rm flat,lower}
>
\max_{\alpha\in I} |\langle U_2,O_\alpha U_1\rangle|_{\rm source,upper}.
\]

The nonnegative mixed-error term is deliberately omitted, which strengthens the exclusion. Every such interval is excluded **for the existing sufficient transfer inequality with the existing upper error certificates**. Unresolved intervals are neither acceptance nor rejection. This does not assert a vanishing physical Wilson transition.

## Sources and controls

- The original eight flat orbits, weights and Wilson values are rebuilt independently using the historical S₃ permutation/gauge canonicalization.
- All four original source blobs, immutable original PR #180 signed amplitude/overlap receipt and original #185 norm enclosures, and the source code and 29-row result of Stage G are pinned by their Git object identities.
- All shifts and interval endpoints are represented by exact integers; no floating point is used in the source, the execution or the outcome.
- The 29 original grid decisions must be reproduced or strictly strengthened by the refined exact signed-overlap upper bound. Every partition adjacency and its total coverage of \([0,14]\) are verified in cross-multiplied integers.
- The interval depth is frozen at 13 binary splits; whenever a whole interval cannot be excluded by the rigorous test, it is subdivided until that depth and then left \`UNRESOLVED\`.
- A future machine-checked theorem could formalize the elementary quadratic-minimum, convex-endpoint and partition-to-global-exclusion lemmas without importing a lattice approximation.

## Acceptance boundary and next steps

Until independent review passes, all findings remain research drafts. After acceptance, record the exact excluded intervals and surviving band, then benchmark whether more exact Q-tail information or state-specific error enclosures can actually reduce the middle uncertainty. The fixed-sample Wilson first spectral weight remains **HOLD**, issue #137 stays open, and the four-dimensional continuum problem remains open.

Run:

\`\`\`sh
python3 -I -B independent/y137-stage-g-continuous-20261116/continuous_shift.py
\`\`\`
