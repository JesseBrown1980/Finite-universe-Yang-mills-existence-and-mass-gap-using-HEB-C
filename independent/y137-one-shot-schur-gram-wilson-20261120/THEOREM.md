# #137 — the Schur–Gram shortcut to the finite first Wilson certificate

**Date:** November 20, 2026. **Original:** physical 3×4 periodic \(\mathrm S_3\), coupling \(r=9\), full physical W metric, eight magnetic-flat states, nonflat Q of dimension 2,177,317,865. **Verdict:** NEW EXACT MATHEMATICAL IDENTITY AND FILTER ENVELOPES PASS; ORIGINAL FINITE WILSON SOURCE-CONDITIONAL / FORMAL HOLD; CONTINUUM OPEN.

## Pattern across old/new atlas certificates

The archive already has the key ingredients: original physical eight-flat P, exact \(\|B\|^2=72\) and diagonal Wilson O (#341); whole Q positive floor \(D=QHQ\ge94.070673\) (#332/#345), Wilson conservative floor \(\gamma=94.068200\); exact W-weighted full-Q Schur source and signed moments (#331/#335/#343); 8×8 matrix Gauss/Lobatto enclosure (#338); source-conditional E1/E2 energy intervals, projector angles and correlated Wilson action (#315/#319/#337). The original signed O9 margin is \(9,285,530,088/10^{12}>0\) and complete-state squared Wilson lower candidate is \(17,074,763/10^{12}\), still under FORMAL HOLD.

The strong structure is **8-dimensional flat Schur with a certified infinite-looking but finite Q resolvent**, rather than a 2.18-billion-dimensional eigenvector solve. The shortest scientific route is to join already produced exact data into a single independently checkable source/energy/observable certificate, with a fail-closed primary source chain.

## The new exact divided-difference identity

On the same *physical* W-weighted basis, write
\[
H=\begin{pmatrix}A&B^\ast\\B&D\end{pmatrix},\quad
S(z)=A-zI-B^\ast(D-zI)^{-1}B,\quad R_i=(D-E_iI)^{-1}.
\]
For \(E_1<E_2<\gamma\), the resolvent identity \(R_2-R_1=(E_2-E_1)R_2R_1\) implies
\[
\boxed{\,G_{21}=I+B^\ast R_2R_1B
       ={S(E_1)-S(E_2)\over E_2-E_1}.\,}
\]
Here \(G_{21}\) is the **full-state cross Gram in eight flat coordinates**: for \(\psi_i(p)=(p,-R_iBp)\), \(\langle\psi_2(v),\psi_1(u)\rangle_W=\langle v,G_{21}u\rangle_{W_P}\). Consequently the entire Q-space *overlap* correction is obtainable from two existing 8×8 Schur matrices. No separate large Q overlap/replay is mathematically needed for this correction.

For any diagonal original Wilson multiplication \(O\), the true effective cross-energy observable is
\[
M_O(E_2,E_1)=O_P+B^\ast R_2O_QR_1B.
\]
For any scalar \(c\),
\[
\boxed{M_{O-cI}(E_2,E_1)=M_O(E_2,E_1)-cG_{21}.}
\]
The true flat directions satisfy \(S(E_i)p_i=0\), so \(p_2^\ast G_{21}p_1=0\) **exactly**. Thus any scalar centering produces the *same true transition*. For frozen approximate vectors, **do not erase the Gram correction**: their cross overlap is generally nonzero. The executable tests both cases.

### Exact minimax Wilson centering

The source-audited seven-loop original observable has global range \(-7\le O\le14\). Its minimax center is \(c=7/2\), represented without fractions as
\[
O_{\mathrm{opt}}=2O-7I,\qquad
\|O_{\mathrm{opt}}\|\le21.
\]
The earlier shifted operator \(O_9=2O-16I\) has \(\|O_9\|\le30\), and
\[
\boxed{M_{\mathrm{opt}}=M_9+9G_{21}.}
\]
For exact distinct true states the \(9G_{21}\) matrix element vanishes, and either doubled Wilson observable equals twice the original Wilson transition. **This gives a 30% tighter generic observable-norm bound without changing the physics.** It must not be used to lower the first-order source-specific penalties in the already-frozen O9 receipt without independently updating those source actions.

The eight original flat diagonal values are \(O_P=(14,8,5,6,0,2,-7,-7)\), so the new integer-centered values are \(O_{\rm opt,P}=(21,9,3,5,-7,-3,-21,-21)\). This recentering is an exact shift, not a new Wilson observable.

## Original archived eight-flat matched source cross-check

The original artifact [hosted run #44560968064](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/44560968064), file \`original-Wilson/SOURCE.hbp\`, supplies the original *source-matched approximate* vectors \(v_1,v_2\), each with 8 W-flat entries and SHA-256 pins \`b143c480b2a7ef813e38acc1f1a89db94af27a8cef02c6eb05fdab5791afe164\`, \`a7e40e835dc2fac1eaf6eba891fa6623d67dafa829b37d7e95c6b932cbfb7732\`. In particular **the second vector's final two entries are both 5,301,152**; substituting 53,011 must fail its SHA check.

Independent exact \(W_P\)-integer arithmetic on the **original eight flat components** gives:

- \(\|v_1\|_{W_P}^2=5\,985\,138\,300\,502\,958\,552\);
- \(\|v_2\|_{W_P}^2=6\,011\,785\,104\,049\,132\,129\);
- \(\langle v_2,v_1\rangle_{W_P}=-287\,631\,158\,976\,534\), hence the approximate flat directions are not orthogonal;
- original shifted P-block action \(\langle v_2,O_{9,P}v_1\rangle_W=409\,631\,480\,361\,936\,852\);
- midpoint shifted P-block action \(\langle v_2,O_{\mathrm{opt},P}v_1\rangle_W=407\,042\,799\,931\,148\,046\).

Thus \(407042799931148046-409631480361936852=9(-287631158976534)\) exactly. The P-only normalized shift has magnitude around \(0.000431558447\), below the previously reported **source-conditional** signed O9 margin \(0.009285530088\). This **P-only** test is informative source verification and cannot be substituted for the physical **full P+Q** cross Gram: a real acceptance gate must compute the Q correction via the same physical Schur matrices and true-energy eigenbranch projectors.

## Quantitative one-shot polynomial corridor

For either true-energy interval, use its upper endpoint \(E_i^{hi}\), the accepted conservative \(\gamma=94.068200\) and \(H_Q\le468\). Set \(g_i=\gamma-E_i^{hi}>0\), \(h_i=468-E_i^{hi}\), and
\[
\rho_i={\sqrt{h_i}-\sqrt{g_i}\over\sqrt{h_i}+\sqrt{g_i}}<1.
\]
The standard degree-\(n\) Chebyshev residual polynomial yields a degree-\(n-1\) inverse approximation \(P_{n-1,i}(D)\) with rigorous whole-Q operator norm error
\[
\|R_i-P_{n-1,i}(D)\|\le \epsilon_i(n):={2\rho_i^n\over g_i}.
\]
For a multiplication observable bounded by \(C\), using \(\|B\|^2=72\) and a two-factor telescope,
\[
\boxed{\|\Delta M\|\le72C\left({\epsilon_2\over g_1}
 +{\epsilon_1\over g_2}+\epsilon_1\epsilon_2\right).}
\]
This inequality holds on the complete original Q if its spectrum lies in the authenticated interval; there is no sector or finite-shell substitution. The independent verifier rounds every square-root *outward* to 12 decimal places with integer isqrt and compares the resulting rational errors exactly.

| Approximation | Generic doubled observable cap | Upper error, per \(10^{12}\) | Compared with original conditional signed margin \(9,285,530,088/10^{12}\) |
|---|---:|---:|---|
| Chebyshev \(n=14\), old \(O_9\) | 30 | 13,006,928,810 | insufficient |
| Chebyshev \(n=14\), new \(O_{\rm opt}\) | 21 | 9,104,850,167 | smaller, narrow |
| Chebyshev \(n=15\), old \(O_9\) | 30 | 7,864,055,405 | smaller |
| Chebyshev \(n=18\), old \(O_9\) | 30 | 1,739,136,977 | below half |
| Chebyshev \(n=27\), old \(O_9\) | 30 | 18,831,448 | ~493-fold margin |
| Geometric 81 (\(3^4\)), old \(O_9\) | 30 | 396,756,589 | below one-twentieth |

All the numbers above are **outward rounded whole-Q operator-error upper bounds**, **not measured polynomial Wilson signals**. A new complete original source polynomial-action certificate would have to establish a signed approximate transition exceeding the relevant error and projector penalties. Degree 14 is a theoretical threshold and may be computationally expensive: propagating 14–27 full Q sparse actions fills massive new supports. The already-authenticated **two original direct Q-dual residuals** therefore remain the more practical straight shot.

### The legitimate matrix-law jump

For a fixed linear \(T\) with \(\|T\|<1\) the exact radix-three identity
\[
\sum_{j=0}^{3^k-1}T^j
 =\prod_{\ell=0}^{k-1}\big(I+T^{3^\ell}+T^{2\cdot3^\ell}\big)
\]
supplies an exact geometric-resolvent approximation with tail \(\|T\|^{3^k}/g\). In this particular original window, \(3^4=81\) terms give the upper error in the last row. The **NTT sublinear jump is not authorized for the original gauge Hamiltonian**: unlike its specially proven circulant ring examples, no full S3 gauge-orbit Fourier diagonalization has been established. Dense cubing can cost vastly more than sparse stepping. The law is valid as algebra and as a comparison/falsification witness, not a claim of fast 81-step original Q playback.

The more useful **Matrix Law frozen-trial parameter jump** requires no 81-step Q propagation. With one fixed source map \(Y\), the exact \(S(z)\) source envelopes are built from small cached matrices whose \(z\)-dependence is polynomial. The independent original source-to-Schur identification (#343) establishes the required exact \(U,R,W\) conventions. The two energies may therefore be verified from pinned 8×8 source matrices and exact interval arithmetic instead of repeating the K3/Q4/Q5 producer.

## Straight-shot acceptance path: one joined fail-closed gate

1. **Physical source and floor pin:** accept the original S3 group enumeration, 8-flat W metric, 264 P/Q boundary edges, B*B=72I, O range/diagonal (#341), the original 34-sector positive Perron witness and its entire-Q lift (#332/#345). Freeze the SHA of each actual input file and avoid reading any duplicate or unpinned physics operator.
2. **Two Schur/projector rows:** from the accepted original U0, μ0..μ3, reconstruct both actual W-weighted 8×8 Loewner matrices and the four exact endpoint inertia counts (E1 0→1, E2 1→2). Reconstruct matched 8-flat directions, directional 8×8 matrix residual, 7×7 compressed singular lower and interval projector angles, rather than trusting their printed scalar values alone (#317/#319). This is low-dimensional exact arithmetic; use frozen-trial parameter replay and fail-closed altered-input controls.
3. **One same-Q original Wilson action:** from the accepted K3/Q4/Q5 source and two already archived original Q-dual vectors, check the complete signed Q4 exterior residuals, the **forward and weighted-adjoint** Wilson actions, and exact identity/centering controls. Use the same physical P/Q/W and E1/E2 source pins (#315/#331/#335). There is no need to solve 2.18 billion eigenvector coordinates.
4. **Exact last inequality:** confirm the original conservative positivity signal minus both first-order and mixed projector errors: \(62,163,774,481-25,196,361,952-27,389,725,641-292,156,800=9,285,530,088>0\) per trillion. Apply exact full-state normalization and factor 1/4 for the original O transition. The established source-conditional squared floor is \(17,074,763/10^{12}\). Accept the original finite theorem **only when all original source, projector and action gates pass together with immutable pins**. The 4D continuum problem remains distinct.

**Decision:** The Schur–Gram divided difference removes the need to redo a whole-Q cross-overlap computation when centering. The minimax integer center offers a 30% tighter norm. The 14/15-step Chebyshev threshold provides an independent potential route to positivity, but recreating its signed source action is expensive. For a short path to the original Wilson certificate, **reuse the existing exact moment/Q-dual source artifacts and discharge the two remaining primary-source binding audits in one joined proof job**. This manuscript's new algebraic toy and spectral estimates alone remain **MATHEMATICAL PASS / ORIGINAL FINITE WILSON FORMAL HOLD**.
