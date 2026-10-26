# Stage 2H — certified integer inertia for the 1,393D S₃ torus

This note specifies a **headless, finite-volume certificate** for improved low-energy bounds on the unchanged periodic 2×2 eight-link, four-face S₃ Hamiltonian. The algorithm is in [native/src/torus2_inertia.rs](native/src/torus2_inertia.rs). This is **not** a continuum Yang–Mills existence or mass-gap result, nor a physical-hardware measurement.

## Inputs and precise scope

The source operator is the existing 1,393-dimensional gauge-orbit-value Hamiltonian in [native/src/torus2.rs](native/src/torus2.rs):

\[
H=J_E H_E+J_B H_B,\qquad
\langle f,g\rangle_W=f^\top Wg,\quad W=\operatorname{diag}(w_1,\ldots,w_{1393}),\quad w_i\in\{1,2,3,6\}.
\]

The exact model satisfies \(WH=H^\top W\). The Stage 2H thresholds are \(t=13.240\) at \((J_E,J_B)=(1,1)\) and \(t=50.840\) at \((3,5)\). They are *proposed thresholds*: acceptance requires executing the positive-definiteness gate. Stage 2G's already certified \(E_0\) rational enclosures supply the independent check \(E_0<t\).

## Rank-one inertia theorem

For an integer, positive vector \(v\) (computed deterministically by 256 steps of positive, rescaled shifted-power iteration), set \(N=v^\top Wv>0\) and \(u=Wv\). Define the *real symmetric* matrix

\[
A_t=W(H-tI)+\frac{60}{N}uu^\top.
\]

If \(A_t\succ0\) (strictly positive definite), then \(E_1>t\).

**Proof:** Set \(B=W^{1/2}(H-tI)W^{-1/2}\), a symmetric matrix similar to \(H-tI\). The congruence transform of \(A_t\) by \(W^{-1/2}\) equals \(B\) plus a positive-semidefinite rank-one operator. If \(B\) had two linearly independent nonpositive eigenvectors, some nonzero vector in their span would be orthogonal to the update direction; the rank-one addition could not make its quadratic form strictly positive. Consequently at most one eigenvalue of \(H\) can lie at or below \(t\). Since Stage 2G establishes \(E_0<t\), we obtain \(E_1>t\).

The rank-one term is a **certificate device**, not an asserted physical interaction.

## Exact integer Cholesky residual gate

The implementation builds the *integer symmetric* matrix

\[
A=1000\,N\,W H-t_{\rm num}N\,W+60\cdot1000\,uu^\top
=1000\,N\,A_t.
\]

For either proposed \(t_{\rm num}\in\{13240,50840\}\), select the positive integer fudge \(f=N\) and factor scale \(S=10^6\). It constructs an integer lower-triangular matrix \(L\) from the entries of

\[
Q=(A-fI)S^2
\]

using floor integer square roots for diagonals, nearest-integer division (ties toward zero) for off-diagonals, and overflow-checked products and sums.

Let \(R=AS^2-LL^\top\). The construction establishes *algebraically*, not statistically:

- \(R_{ii}\ge fS^2>0\), because each square root is rounded down.
- For \(i\ne j\), \(|R_{ij}|\le \lceil L_{kk}/2\rceil\), with \(k=\min(i,j)\), because the sole newly rounded off-diagonal factor has divisor \(L_{kk}>0\).

Thus it suffices to validate the fully exact, per-row inequality

\[
fS^2>\sum_{j<i}\lceil L_{jj}/2\rceil+(1393-i-1)\lceil L_{ii}/2\rceil.
\]

If any pivot, product, or row inequality fails, the certificate fails closed. Otherwise \(R\) is real symmetric and strictly diagonally dominant with positive diagonal, so \(R\succ0\). Therefore \(AS^2=LL^\top+R\succ0\), proving \(A_t\succ0\) and \(E_1>t\).

No floating-point Cholesky factors are used or trusted. The verifier reconstructs the Hamiltonian, witness, integer factor and receipt records rather than trusting a stored PASS flag.

## Independently bounded upper eigenvalue

The initial excited trial is \(z_i=v_i[\chi(X_i)-\chi(Y_i)]\), the difference of two noncontractible length-two Wilson characters. It lies in the axis-swap antisymmetric sector while \(v\) is symmetric. Repeated *integer* application of \((sI-H)\), with \(s\) chosen strictly above an exact Gershgorin bound on \(\lambda_{\max}(H)\), improves its Rayleigh quotient. Sign-symmetric integer rounding preserves the odd sector.

The implementation explicitly verifies

\[
\langle v,z\rangle_W=\langle v,Hz\rangle_W=
\langle z,Hv\rangle_W=0,\qquad
\mathcal R_H(v)<t<\mathcal R_H(z).
\]

The two-dimensional compression on \(\operatorname{span}\{v,z\}\) is therefore diagonal with larger Rayleigh quotient \(\mathcal R_H(z)\). Courant–Fischer proves \(E_1\le\mathcal R_H(z)\). The rational quotient is rounded **outward** to denominator \(10^6\), and Stage 2G's independent \(E_0\) enclosure yields the reported interval for \(\Delta=E_1-E_0\).

## Reproduction

From the repository root:

```sh
cd native
cargo +1.81.0 test --all-targets --offline --locked
cargo +1.81.0 clippy --all-targets --offline --locked -- -D warnings
cargo +1.81.0 build --release --offline --locked
target/release/hebc torus2-inertia 1 1 inertia-1-1
target/release/hebc torus2-inertia-verify 1 1 inertia-1-1
target/release/hebc torus2-inertia 3 5 inertia-3-5
target/release/hebc torus2-inertia-verify 3 5 inertia-3-5
```

Four plain-text files (HBP, HBI, anchor and measure) are written per pair. Both the exact source state and the generated certificate are reproducibly regenerated, with negative controls for tampered receipts. The unkeyed SHA anchor is an integrity record, not an externally authenticated signature.

## Scientific next step

The GitHub Actions run at commit `f6facf599a2d23585759ee66a0f3848633ff2cbf` passed Stage 2H's exact numerical gates and tamper controls. Certified finite-volume enclosures, with common denominator 1,000,000, are:

| JE,JB | E0 | E1 | E1−E0 |
|---|---|---|---|
| 1,1 | [7,634,198; 7,634,199] | [13,240,000; 13,242,733] | [5,605,801; 5,608,535] |
| 3,5 | [36,699,227; 36,699,228] | [50,840,000; 50,842,050] | [14,140,772; 14,142,823] |

Stage 2H substantially narrows the finite-volume spectral enclosures. Stage 2I can then target exact multiplicities, independently implemented rational inertia checks, multiple lattice sizes, and controlled finite-size scaling. None of those finite discrete-group steps substitutes for an independently reviewed construction of four-dimensional continuum Yang–Mills theory.
