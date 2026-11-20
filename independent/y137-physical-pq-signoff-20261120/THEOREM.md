# #137 — independently reconstructed original weighted physical P/Q operator

**Scope:** 3×4 periodic finite S₃ at original r=9, all gauge-invariant states and all spatial-symmetry sectors. The exact 8-flat physical P/Q operator definition and first-shell boundary admit independent mathematical and executable verification. The whole-Q spectral-floor top-vector provenance and final E₁→E₂ Wilson theorem still have separate acceptance gates.

## Whole-space group and physical metric

Fix a spanning tree of 11 edges on the 12 sites. The gauge-fixed configuration comprises 13 S₃-valued links, with residual simultaneous conjugation by S₃. For a representative x, its residual conjugation orbit has multiplicity w(x) in {1,2,3,6}. The physical gauge-orbit inner product is, up to a common factor,

\[
\langle f,h\rangle_W=\sum_{x\text{ gauge orbit}}w(x)\overline{f_x}h_x .
\]

Let c(x,y) count the 24 links × 3 involutive left-transposition moves carrying representative x into orbit y. Every move reverses by the same transposition. A residual simultaneous conjugation sends each transposition to another transposition; therefore it bijects the 72 moves on every one of the w(x) representatives of x with reverse moves on the w(y) representatives of y. This proves for **every** original gauge orbit pair, including states beyond the computed 264-boundary,

\[
\boxed{w(x)c(x,y)=w(y)c(y,x).}
\]

In J_E units the exact Hamiltonian is H(r) = 72 I − C + r M, with M the real gauge-invariant diagonal magnetic cost. Consequently W H = Hᵀ W globally; the orthonormal W^(1/2) conjugate is symmetric. The proof depends on finite S₃ group action and the uniform 72 reversible moves, independent of any particular truncation.

## Original flat P and complete nonflat Q

The plaquette cost is 3 minus the number of fixed permutation letters, zero precisely on the identity holonomy. All-zero plaquettes on a torus correspond to homomorphisms from π₁(T²)=Z² into S₃, i.e. commuting ordered S₃ holonomy pairs up to conjugation. There are exactly 18 commuting ordered pairs and exactly eight simultaneous-conjugacy classes, proving that **P comprises exactly eight entire-space magnetic-flat orbits**. Q is the complete W-orthogonal complement, including all spatial symmetry sectors.

The independent permutation calculation confirms the canonical 8-flat channel order and

\[
\boxed{W_P=\operatorname{diag}(1,3,2,3,3,2,2,2).}
\]

It then reconstructs every one of the 576 original moves leaving these eight flats, finds exactly 264 distinct nonflat Q destinations, and independently reenumerates all 72 reverse moves of each of those 264 destinations. Every destination has exactly one flat parent, magnetic cost 4, and orbit weight either 3 or 6; all 264 forward/reverse coefficients satisfy the physical weighted adjoint equality.

All flat moves leave P and M vanishes on P, so H_PP=72 I₈. Define B=QHP in the same physical orbit-coordinate basis; B(q,p)=−c(q,p) and its W-adjoint B*(p,q)=−c(p,q). Since all Q destinations coupled to P have been exhaustively enumerated,

\[
\boxed{(B^* B)_{ij}
=\sum_{q\in Q} c(p_i,q)c(q,p_j)
=72\,\delta_{ij}.}
\]

This is an identity for **the complete original Q Hilbert space**, not just a chosen K3/K4 subset. It justifies the exact full-state norm estimate used in merged [original Wilson transfer PR #337](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/337): when QHQ≥γI and E<γ,

\[
\|(QHQ-E)^{-1}Bp\|_W^2
\leq 72\,\|p\|_{W_P}^2/(\gamma-E)^2.
\]

## Original winding Wilson operator in exactly the same basis

O multiplies every gauge-orbit state by the integer sum of four horizontal length-3 and three vertical length-4 fundamental winding characters in the standard S₃ representation, χ(g)=number of fixed letters minus one. This is gauge-invariant and diagonal in the physical orbit basis. Therefore **POQ=QOP=0**, and the independent exact group calculation obtains

\[
O_P=\operatorname{diag}(14,8,5,6,0,2,-7,-7),
\]

\[
(O_9)_P=2O_P-16I_8
=\operatorname{diag}(12,0,-6,-4,-16,-12,-30,-30).
\]

The global identity O₉=2O−16I is a pointwise identity, so its E₁→E₂ amplitude between distinct-energy orthogonal true eigenstates is exactly twice that of O, and its squared spectral weight is four times that of O.

## Executable check and adversarial controls

The independent [physical source verifier](verify_pq.py) uses Python exact integer permutation arithmetic and imports **no** historical finite graph, K3 source, momentum-sector or Wilson module. It independently enumerates the original eight flat orbit keys, all 264 first-shell Q orbit rows, weights, the complete 72-move row counts, weighted reciprocity, full B*B matrix and the Wilson character. It fingerprints the full 264-pair physical boundary using the canonical 13-link base-6 address and physical weights:

SHA-256: **8d41471666def3e72caf199cd87f6bfbb94fc06a66c037f1c88156c4d6c78d34**.

Seven altered-operator controls must all be rejected: forged flat weight, forward move coefficient, reverse move coefficient, a second flat parent, forged original Wilson value, forged O₉ value, or deletion of one P/Q coupling. The hosted workflow runs ordinary and optimized Python and requires identical exact receipts, preventing unsafe proof reliance on removable assertions.

The already merged [Perron composite source replay PR #332](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/332) separately authenticated all 34 frozen input files and physically rebuilt 45,508,080 nonflat sector-store rows with zero mismatches and Merkle PASS. The independently verified finite nonflat Perron lower bound is 94.070673 J_E under its positive witness and whole-symmetry lift premises; Wilson arithmetic conservatively uses γ=94.068200 J_E. Original K3/Q4/Q5 source-to-μ₃ checks and the full-matrix signed moment/Loewner theorem are independently accepted in merged PRs #331, #335 and #338.

**Physical P/Q operator sign-off scope:** The complete exact group-theoretic W-adjoint identity, the 8-flat original P and its complete Q complement, all original P–Q transitions, H_PP, B*B=72I, original Wilson diagonal and O₉ relation are established by explicit group algebra and independently reproduced first-shell arithmetic. The original first-Wilson positive spectral-weight theorem remains **SOURCE-CONDITIONAL / FORMAL HOLD** pending a final joined sign-off on the **whole-Q Perron witness/symmetry lift and source-moment-to-original-physical-Schur identification**. The four-dimensional continuum Yang–Mills problem remains OPEN.
