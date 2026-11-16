# Stage C — improved sufficient bound from all 2,140,596 K3/Q4 residuals

**Production result:** hosted Actions run 43867687831 reconstructs the exact original signed residual R on all 155,378 K3 + 1,985,218 Q4 canonical states at both frozen energies, with their original accepted K3 Y/U/G hashes. Physical V1 is the *next operator action*: V1 = X R. All arithmetic below is exact integers.

Let b=1000000000, z1=69909875505, z2=69949729820.

| Quantity | Energy 1 | Energy 2 |
|---|---:|---:|
| Max signed K3 residual magnitude | 851548647970 | 858366110260 |
| Max signed Q4 residual magnitude | 1780311574000000000 | 1785811470000000000 |
| Full K3/Q4 residual maximum bit length | 61 | 61 |
| max_i(|D_i|+72b) | 398090124495 | 398050270180 |
| Analytic upper bound for max K3/Q4 physical V1 | 708724456133549405130000000000 | 710842738124042964600000000000 |
| Upper bound bit length | 100 | 100 |

Each of the 72 electric moves is retained and R vanishes outside K3+Q4. With D_i=b(72+9m_i)-z and 0<=m_i<=36, the original full row bound gives:

\[
|(XR)_i^a| \le (|D_i|+b\sum_j c_{ij})\max_{j,a}|R_j^a|
\le (|D_i|+72b) \max|R| < 2^{100}.
\]

The original independently authenticated Q5 spools store 18,598,040 unsigned V1/b amplitudes in 82-bit lanes. Since b<2^30, every physical Q5 V1 amplitude is strictly less than 2^112. Combining the blocks, provided original source identity and support hypotheses are preserved:

\[
\boxed{M=\max_{K3,Q4,Q5,a}|V_{1,i}^a|<2^{112}.}
\]

This improves the cloud reviewer's sufficient M<2^117 condition by five exponent bits. Because the full support has N=20,738,636<2^25, physical orbit weights W=6w<=36<2^6, and |D|+72b<2^39, each physical row contraction obeys |XV1|<2^151. The absolute sum of every complete 8x8 matrix entry's row contributions is bounded by

\[
2^{112+151+25+6}=\boxed{2^{294}}<2^{304}.
\]

The same strict bound applies to **every prefix partial sum** by the triangle inequality, independent of row order.

For unordered weighted edges, first retain the *uncoarsened* degree at each source. Under independently verified W_i c_ij = W_j c_ji, the absolute total of all paired offdiagonal terms is at most 6b M² sum_i w_i sum_{j!=i}c_ij. The diagonal and true-self-loop terms are at most 6 M² sum_i w_i (|D_i|+b c_ii). Adding these **before replacing any degree by 72** gives the strict overall bound 6 M² sum_i w_i (|D_i|+b[c_ii+sum_{j!=i}c_ij]) = 6 M² sum_i w_i (|D_i|+72b) <=36 N M² max_i(|D_i|+72b) <2^294. This covers every pair-order prefix partial sum as the total of absolute contributions.

**Scope:** The actual full-source K3/Q4 R maxima are measured exactly and their signed residual hashes are sealed. The full physical V1 signed source files, independently complete K3/Q4/Q5 support joins, all cross-block weighted reciprocity, two full signed 8x8 mu3 matrices, and exact Wilson normalization are separate HOLD gates. A physical V1 <2^112 bound does not itself compute a third moment. Every future 320-bit accumulator must still refuse signed overflow and enforce the runtime 2^294 absolute-sum cap.

Source: hosted run 43867687831, receipt RESULT-WORKER1-C-FULL-R-ENVELOPE-20261116.hbp.

Original full residual SHA256:
E1: 5ba2369a34826b2d8cd5d9ad5d60c8ed4ab7b24108694e4eb63a1cecf40e5d09
E2: aa8dac4b761124bb32b6dbb52fcf138c733ca6fa04f84b5c790758c37b6b6824
