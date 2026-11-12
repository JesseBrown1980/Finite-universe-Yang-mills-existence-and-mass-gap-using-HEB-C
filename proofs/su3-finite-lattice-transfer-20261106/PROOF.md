# Finite-slice continuous-SU(3) transfer theorem and slice-screen observer

**Scope:** a periodic 2x2x2 spatial lattice with any finite number of Euclidean time slices, continuous SU(3) link variables, positive beta, and fixed positive spacing. The link Hilbert space remains infinite dimensional even though the lattice has finitely many links. This is a finite-lattice theorem, **not a spacetime-continuum or Clay proof**.

## Definition (exact continuous SU(3), not the finite subgroup S3)

Let G=SU(3), with normalized Haar measure and 24 oriented spatial links on eight spatial vertices. The Wilson weight is

\[
w_\beta(g)=\exp((\beta/3)\operatorname{Re}\operatorname{tr}_{\mathbf3}(g)).
\]

Let A(X) be the product of w over all 24 spatial plaquettes. Let the temporal kernel be

\[
K(X,Y)=\int_{G^8}\prod_{e\in E_s}
w_\beta(U_e g_{t(e)} V_e^{-1}g_{s(e)}^{-1})\prod_x dg_x.
\]

On H=L²(G^24), let P be the exact gauge-average projection, C1 the one-link convolution by w, C=C1 tensor-power 24, and T=A P C P on PH. Its symmetrization S=A^(1/2) P C P A^(1/2) is similar to T.

## Theorem 1: positive finite-slice existence and unique vacuum

The conservative trace bound -3 ≤ Re tr3(g) ≤ 3 gives exp(-beta) ≤ w(g) ≤ exp(beta), hence exp(-24 beta) ≤ K(X,Y) ≤ exp(24 beta). Every finite-temporal-period Wilson partition function is finite and positive.

C1 has a continuous kernel on a compact group, so is compact. Tensoring finitely many C1 factors, projecting by bounded P, and multiplying by bounded A preserve compactness. S is self-adjoint with strictly positive kernel on PH. Positivity improvement and the compact Perron-Jentzsch theorem give a simple top eigenvalue lambda0>0 with gauge-invariant strictly positive vacuum Omega.

## Theorem 2: strictly positive physical transfer spectrum

Use chi3+chibar3=2 Re tr3. The character identity

\[
w_\beta(g)=\sum_{a,b\ge0}\frac{(\beta/6)^{a+b}}{a!b!}
\chi_{\mathbf3}(g)^a\chi_{\overline{\mathbf3}}(g)^b
\]

is absolutely convergent. Every SU(3) irrep (p,q) occurs in the tensor product 3^tensor-p times anti3^tensor-q, so the coefficient of *every* irreducible character is strictly positive for beta>0. All other tensor-product multiplicities are nonnegative integers. Peter-Weyl/Schur orthogonality therefore makes C1 strictly positive definite, not merely positive pointwise. C is injective positive definite. P commutes with C, and A is strictly positive; therefore S is injective positive definite on PH. Its transfer eigenvalues satisfy lambda0>lambda1≥lambda2>...>0, with possible multiplicities and accumulation only at zero.

## Theorem 3: an explicit fixed-lattice mass gap

Take the positive Perron vector h of T. The Doob Markov kernel is

\[
Q(X,dY)=K(X,Y)h(Y)dY/\int K(X,Z)h(Z)dZ.
\]

A(X) cancels from the ratio. From the bounds on K, uniformly over X,

\[
Q(X,dY)\ge\delta\,\pi(dY),\quad
\delta=\exp(-48\beta),\quad \pi(dY)=h(Y)dY/\int h.
\]

Consequently Q=delta J+(1-delta)R for some Markov R and constant-output Markov J. Oscillation contracts by (1-delta), and every nonconstant bounded eigenfunction has normalized eigenvalue at most 1-delta in modulus. Eigenfunctions of the continuous compact transfer kernel are continuous and bounded. Theorem 2 excludes negative physical eigenvalues. Thus

\[
\boxed{0<\lambda_1/\lambda_0\le1-\exp(-48\beta)<1}
\]
\[
\boxed{a\,m_{\mathrm{gap}}
=\log(\lambda_0/\lambda_1)\ge-\log(1-\exp(-48\beta))>0.}
\]

This is a highly conservative pointwise bound at fixed lattice and beta. No volume-uniform bound, continuum uniformity, or numerical glueball mass follows.

## Theorem 4: viewer continuity from exact slices

Fix the *calibrated or symbolic* interval dt>0. On PH, B=S/lambda0 is positive self-adjoint with spectrum in (0,1]. Define Hviewer=-log(B)/dt by spectral calculus and U(t)=exp(-t Hviewer)=B^(t/dt). U(t) is a strongly continuous positive self-adjoint contraction semigroup. At sample times n dt, U(n dt)=B^n exactly; at 3^k dt, the exact time-jump is B^(3^k). This creates a continuous-time *interpolation of the fixed lattice dynamics*, not a proof that physical spacetime is continuous.

For any bounded real gauge-invariant Wilson-loop observable O, write v=(O-<Omega,O Omega>)Omega, orthogonal to Omega. Its exact connected viewer correlator obeys

\[
C_O(t)=\langle v,U(t)v\rangle
=\sum_{j\ge1}|\langle v,\psi_j\rangle|^2
\exp[-t\log(\lambda_0/\lambda_j)/dt].
\]

It is nonnegative and continuous (and completely monotone for t>0), with

\[
0\le C_O(t)\le C_O(0)\exp[-m_{\mathrm{gap}}t].
\]

Thus an observer can sample exact discrete slices and see a rigorously continuous exponential-correlation law in viewer time, *provided the model and chosen time calibration are stated*. It does not prove convergence to quantum Yang-Mills on R4.

## Slice-screen / Q-PRISM observation protocol

Reuse the older qprism-3d-slice-harness and deterministic-slice-time-harness as observer/audit architecture. The source state is not a rendered screen or a SHA digest: the screen is a projection of gauge-invariant measurements from a well-defined simulation.

1. Record spatial geometry, group, beta, dt, canonical observable definition, slice index, sources, and hashes. Retain the actual observable data or exact reconstructible representations, not only the digest.
2. Measure Wilson loops and connected temporal correlators at n=0,1,3,9,27 and 3^k checkpoints; verify direct evolution against exact jump identities *when computationally available*. A large symbolic jump alone does not certify a numerical SU(3) matrix element.
3. Display the derived continuous-time interpolation between samples as a **model consequence**, separate from independently sampled slices. The exact semigroup agrees at integer times by construction. Do not count it as an independent fit to nature.
4. Demand multi-resolution, physically calibrated comparisons of correlation lengths, masses and Wilson loops before claiming measured physical continuum agreement. That scaling bridge is OPEN.
5. Keep physical-vacuum fluctuations, gauge projection and the observable algebra. No photons, detectors, laboratory noise, or viewer pixels are silently identified with raw link variables.

## Scientific limitations

A finite spatial lattice with exact SU(3) gauge symmetry is different from (a) a finite-group S3 lattice, (b) a finite-dimensional quantum-link truncation, and (c) the Clay Yang-Mills theory on R4. This proof only handles (a fixed-volume lattice version of) the first case, without its continuum limit. No SHA hash generates entanglement; hashes authenticate the encoding of states and observed transitions. The exact group-theoretic proof still requires outside mathematical review, and audit_viewer.py only validates its finite-group calibration model, not SU(3) Haar integrals.
