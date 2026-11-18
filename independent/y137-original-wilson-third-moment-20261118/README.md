# Issue #137 — original seven-loop Wilson third Hamiltonian moment

Research draft, November 18, 2026. Extends the source-accepted physical second-moment [PR #304](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/304) and the Stage N original source. The original \(3\times4\), \(S_3\), \(r=9\) Hamiltonian and seven-loop Wilson multiplication are unchanged.

## Actual requested calculation

For the *original fixed rational approximate-ground trial* \(\phi\), set \(v=(\|\phi\|_W^2 O-\langle\phi,O\phi\rangle_W)\phi\). The previous source-authenticated job established exact integer
\[
m_0=\langle v,v\rangle_W,\quad
m_1=\langle v,Hv\rangle_W,\quad
m_2=\langle Hv,Hv\rangle_W.
\]
Its original physical \(m_2\) SHA-256 was **393954283e19f17cecaae35947088d9338c9d81f7dea7d271be9fd46c39487b6**, including all 1,985,218 K4 physical exterior orbits. This program checks that pinned value before proceeding.

The new exact third moment is
\[
m_3=\langle Hv,H(Hv)\rangle_W.
\]
The key support identity is that \(v\) lives on the eight flats plus K3, while \(Hv\) lives on the flats plus K3 **plus K4**. For \(m_3\), H acts on both copies of \(Hv\); K4-to-K5 matrix elements multiply zero coefficients and cannot enter the bilinear. Therefore no enumeration of the complete fifth-shell exterior is required to calculate the exact third moment.

## Faithful K4 decomposition and two independent checks

The physical Hamiltonian is \(H=E+9M\) where \(E=72I-A\) is the transposition electric term on canonical weighted gauge orbits and \(M\) is the nonnegative 12-plaquette magnetic number. All quantities are exact integers; the orbit-weight metric is positive and the original graph has detailed balance.

Let \(p_1,q_1,z_1\) be the flat, K3, K4 pieces of \(Hv\). The full quadratic form splits as
\[
m_3=
\underbrace{\langle(p_1,q_1),H_{P+K3}(p_1,q_1)\rangle_W}_{\text{original Stage N operator}}
\;-\;2\sum_{f\in K4}z_{1f}\sum_{j\in K3} w_j A_{fj}\,q_{1j}
\;+\;9\sum_{f\in K4}w_f M_f z_{1f}^2
\;+\;\underbrace{\langle z_1,E_{K4} z_1\rangle_W}_{\text{K4 electric}}.
\]

- **Bounded mode** reconstructs original source and \(Hv\), checks historical \(m_2\), computes every K4 magnetic entry and the complete K3–K4 weighted cross form. From \(0\preceq E_{K4}\preceq144I\), it produces an exact rational-integer enclosure for \(m_3\), intersected with the full-source \(0\le H\le468\) and Cauchy bounds.
- **Full mode** also traverses the original \(72\) transposition moves from every nonzero \(K4\) component, recomputes the exact electric quadratic form, and emits the actual source \(m_3\), along with the third low-pass moment \(C_3=(468I-H)^3\). It checks \(m_1m_3\ge m_2^2\), \(C_1C_3\ge C_2^2\), the operator ceiling, and the K4 electric PSD/144 ceiling.
- The independent verifier contains *no producer or original-graph imports*; it independently replays every integer identity, source/moment SHA, both spectral localizing matrices and five corruption controls. This is **arithmetic/receipt independence**; independent physical graph reconstruction remains a separate review obligation.

## More targeted first-excitation question: can all trial spectral mass lie above E3?

Let \(L_3=69.968699300\) be the accepted source-conditional lower end of the third physical energy. A positive measure supported entirely in \([L_3,468]\) has, necessarily,
\[
\begin{pmatrix}
m_1-L_3m_0 & m_2-L_3m_1\\
m_2-L_3m_1 & m_3-L_3m_2
\end{pmatrix}\succeq0.
\]
The program evaluates this **exact** 2×2 determinant with integer denominators, including endpoints of the certified interval in bounded mode.

A *negative determinant* for the actual \(m_3\) would rigorously **exclude an all-above-\(L_3\) spectral measure for this specific fixed trial**. The result would still require separating first-state leakage from the desired second-state Wilson channel. A nonnegative determinant is merely compatible with all-high support; it is not a positive proof of such support. This is a moment-localizing test, not a claimed direct application of the superconducting-TLS paper to the S3 Hamiltonian.

## Acceptance labels and reproducibility

\`\`\`
python3 -I -B independent/y137-original-wilson-third-moment-20261118/third.py toy
python3 -I -B independent/y137-original-wilson-third-moment-20261118/third.py bounds > BOUNDS.hbp
python3 -I -B independent/y137-original-wilson-third-moment-20261118/third.py full > FULL.hbp
# For independent verifier, retain only producer Y137_M3_ HBP lines.
grep '^Y137_M3_' BOUNDS.hbp > BOUNDS-ONLY.hbp
python3 -I -B independent/y137-original-wilson-third-moment-20261118/verify.py BOUNDS-ONLY.hbp
\`\`\`

On the stacked branch, the dedicated workflow runs exact source/moment SHA policy, independent bounded acceptance, and a separate exhaustive K4 full action. Every source, output and negative result is archived. Research PR remains DRAFT until hosted evidence and an independent physical-source review.

**Scientific status:** source-conditional finite first \(S_3\) gap PASS; original Wilson first-excitation weight HOLD; four-dimensional continuum theorem OPEN. The original Wilson operator and physical Hamiltonian remain unchanged.
