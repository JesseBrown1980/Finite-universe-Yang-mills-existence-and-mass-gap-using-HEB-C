# #137 — exact eight-flat coupling norm and two-energy Wilson interval control

Research draft, November 17, 2026. **This gate follows accepted original-source coordinate-Wilson mixed-block cancellation (draft PR #269 and merged atlas note #270).** All prior scientific source scripts, accepted Hamiltonian matrices and receipts remain unchanged.

## Source-specific question

How much can the **exact** original seven-loop two-energy Feshbach effective Wilson operator change when its two energy arguments move from the historical PR #180 samples \(s_1=69.909875505\), \(s_2=69.949729820\) to the Stage E source-conditional true energy intervals

\[
E_1\in(69.909429421,69.909586556),\quad
E_2\in(69.949264147,69.949433884)
\]
in units \(J_E\)?

Because the original Wilson observable is diagonal in the weighted gauge-orbit coordinates and the original eight-flat P projector is a coordinate projector, \(POQ=QOP=0\) exactly. Let \(Q=1-P\), \(B=QHP\), \(A=QHQ\), \(R(z)=(A-z)^{-1}\), \(O_Q=QOQ\). Then

\[
O_{\rm eff}(E_2,E_1)=POP+B^\dagger R(E_2)O_QR(E_1)B.
\]

The pinned original S₃ source is used to calculate the entire **8×8 exact weighted \(B^\dagger B\)** from all original K2 first-shell couplings, not from an inferred graph. The W-P-normalized squared operator norm obeys the exact elementary positive-matrix bound

\[
\|B\|_{W_P\to W_Q}^2\le\operatorname{Tr}_{W_P}(B^\dagger B)
=\sum_{i=1}^8\frac{\sum_{q} w_q n(q,i)^2}{w_i}.
\]

The original \(QHQ\ge94.0682\) lift-free floor and \(\|O_Q\|\le14\) then imply the **source-specific two-energy Lipschitz envelope**

\[
\begin{aligned}
\|O_{\rm eff}(E_2,E_1)-O_{\rm eff}(s_2,s_1)\|
\le 14\|B\|^2\left[
\frac{\delta_2}{(g-E_2^{hi})(g-s_2)(g-E_1^{hi})}
+\frac{\delta_1}{(g-s_2)(g-E_1^{hi})(g-s_1)}
\right]
\end{aligned}
\]
where \(\delta_i=\max_{E_i\text{ in certified interval}}|E_i-s_i|\), all quantities are in \(J_E\) units. This follows by **one exact resolvent identity and a telescoping product**; there is no polynomial approximation or unquantified remainder. The upper bound is computed with integer numerator and denominator pairs and strict cross multiplication.

For the exact normalized full physical-state metric on flat vectors,
\[
G(E)=I+B^\dagger (QHQ-E)^{-2}B,
\]
the derivative identity \(G'(E)=2B^\dagger (QHQ-E)^{-3}B\) gives
\[
\|G(E_i)-G(s_i)\|\le\frac{2\|B\|^2\delta_i}{(g-s_i)^3}.
\]
Both certified intervals lie strictly below their historical sample energies.

## Acceptance and negative controls

- Reconstruct the original 8+264+7770 K2 geometry from the previously pinned physical source and verify exact weighted P/Q detailed balance;
- enumerate every nonzero Q→flat source coupling, calculate **all 64** exact weighted \(B^\dagger B\) entries, check symmetric W Gram, and SHA-256 seal the complete integer matrix;
- bound \(\|B\|^2\) by the exact W trace, independently compare against the global \(\|H\|^2\le468^2\) fallback;
- use exact integer numerator/denominator arithmetic for the physical-energy-window and metric-variation bounds;
- negative controls reject a falsified larger energy displacement, missing first-shell support, changed source pins, or an ineffective trace bound;
- freeze exact result HBP and GitHub Actions provenance in a hosted receipt.

**Scope:** This is an operator-norm bound on the *energy arguments* of the exact full-Q effective Wilson matrix. It **does not yet compute** that matrix, its actual true-energy eight-flat eigendirections, the truncated 20-step PR #180 inverse-action error, or the signed normalized true first-excitation transition. A very small energy-argument error can coexist with an inconclusive eigenvector/projector error; no inference from a small Lipschitz number directly to Wilson spectral-weight positivity is authorized.

Stage E complete physical finite gap: source-conditional PASS; first Wilson spectral weight: **HOLD**; four-dimensional continuum theorem: **OPEN**.
