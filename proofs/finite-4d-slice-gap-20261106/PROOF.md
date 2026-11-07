# Finite 4D Yang–Mills-type gauge universes: existence and a positive transfer mass gap

**November 6, 2026 — FINITE THEOREM, proof for Opus independent review.**

This note gives an explicit finite-dimensional existence and spectral-gap theorem for the **isotropic 3+1-dimensional finite-group gauge models** already implemented as exact spatial-slice transfers in [`Finite-Universe-SU-N-solved`](https://github.com/JesseBrown1980/Finite-Universe-SU-N-solved/blob/main/docs/FINITE-SLICE-MATRIX-FULLSPACE.md), and records the distinct existing 2×2 S₃ Hamiltonian theorem from this repository. It does **not** prove a continuous SU(3) theory, a continuum Yang–Mills theory, the Clay problem, or a gap uniform in lattice size, spacing, or coupling. It does not claim the numerical value of the interacting gap. Cryptographic hashes are evidence records, not the origin of the spectrum.

## The finite universe and its six isotropic plaquette orientations

Let the spatial slice have 8 vertices, 24 oriented spatial links (both periodic directions on every 2-site axis), 24 spatial plaquettes, and eight temporal links to the next slice. Each slab also has 24 temporal plaquettes. All six spatial-temporal plaquette orientations carry **the same** finite-group class weight. Take any integer number `N_t >= 2` of periodic temporal slices, and let `G` be one of:

* `Z3`, the center of SU(3), with `w(identity)=4`, `w(other)=1`.
* `S3`, non-Abelian, faithfully embedded in SU(3) as sign-twisted permutation matrices. Write `chi` for this 3-dimensional representation's character; `w(g)=2+chi(g)` is `5` at the identity, `1` on transpositions and `2` on 3-cycles.

These are **finite-group, Wilson-like class weights**, not an assertion that `S3`'s three values are one ordinary continuous-SU(3) Wilson exponential at some beta. Each weight is strictly positive, central, real and invariant under group inversion. The distinct spatial directions and temporal direction have equal local weights.

Let `U,V in G^24` be neighboring spatial link configurations; `g in G^8` labels temporal links, and `s(e),t(e)` are edge endpoints. Set

```
A(U) = PRODUCT over 24 spatial plaquettes p of w(hol_p(U))
K(U,V) = SUM over g in G^8 of PRODUCT over 24 spatial links e
         w( U_e * g_t(e) * inverse(V_e) * inverse(g_s(e)) )
T(U,V) = A(U) * K(U,V).
```

Every object is a finite integer or an integer matrix. Gauge invariance is the independent left/right vertex action on links. Let `P` be the orthogonal **full** gauge-average projection in the configuration basis under counting measure, and define the one-link central-convolution matrix `C1[a,b]=w(a*b^{-1})`, `C=C1^(tensor 24)`. Then, exactly,

```
K = |G|^8 P C P;     T = A K = P T P.
```

`P` commutes with `C` because the weight is a class function, and `A` commutes with `P` because plaquette weights are gauge invariant. **No small four-state catalogue is substituted for the physical space.** The physical dimensions are 129,140,163 for `Z3`, and 2,821,153,019,713 for `S3`, already counted in the companion repo by gauge-tree reduction and Burnside's lemma.

## Theorem A — finite existence and simple vacuum

**Claim.** The complete finite 4D partition at every `N_t>=2` is a positive, finite integer, and `T` has a unique strictly positive vacuum on the full gauge-invariant Hilbert space.

**Proof.** Every one of the finitely many link assignments has weight equal to a product of strictly positive integers, so the original periodic path sum is finite and positive. More precisely, after summing time links between consecutive slices, the sum is `Z_Nt=Tr(T^Nt)>0`, with the trace over all spatial configurations; no continuum path measure or limiting procedure is invoked. Since `T=P T P`, the same trace is over the exact gauge-invariant subspace. Every entry `K(U,V)>0` (it is a sum of `|G|^8` positive summands), and every `A(U)>0`, so `T(U,V)>0`. Finite Perron–Frobenius theory gives a simple top eigenvalue `lambda0>0` and a strictly positive eigenvector `h`. `T` commutes with every gauge transformation; uniqueness of the positive eigenvector makes `h` gauge invariant. Thus it is the vacuum of the full physical transfer. QED.

**Important:** Perron simplicity alone gives a gap in *modulus* for positive matrices; to call the transfer Hamiltonian positive/self-adjoint, we separately prove positivity of the entire physical spectrum next.

## Theorem B — positive physical spectrum (the exact local matrix check)

**Claim.** The single-link `C1` has the following positive eigenvalues, counted with multiplicity:

| Group | `C1` spectrum | exact leading principal minors (basis used by the auditor) |
|---|---|---|
| `Z3` | `6,3,3` | `4,15,54` |
| `S3` | `12,6,3,3,3,3` | `5,24,99,405,1539,5832` |

**Proof.** The separate `audit.py` constructs the groups directly as modular addition or permutations of three symbols. It computes every entry `w(a b^{-1})` from the group law. Its integer row elimination checks the eigenspace nullities at the displayed eigenvalues, and its fraction-free Bareiss determinants show that **all** leading principal minors are positive. Consequently `C1` is symmetric positive definite (Sylvester's criterion). The explicit group-character decomposition gives the same eigenvalue list. Thus `C` is strictly positive definite. Because `P` is an orthogonal projector commuting with `C`, `K=|G|^8 P C P` is strictly positive definite *on the whole physical gauge-invariant subspace*. Since `A` is strictly positive and diagonal, `T=A K` is similar to the symmetric, strictly positive operator

```
S = A^(1/2) K A^(1/2),
A^(-1/2) T A^(1/2) = S.
```

Therefore all physical eigenvalues are real and **strictly positive**, with the largest simple. The logarithm of normalized `S` defines a self-adjoint, nonnegative finite transfer Hamiltonian. QED.

## Theorem C — an explicit nonzero finite mass gap

Write the ordered physical eigenvalues as `lambda0 > lambda1 >= lambda2 > 0` (with multiplicities after `lambda1`); define the transfer mass gap, in lattice units,

```
a m_gap := log(lambda0/lambda1).
```

**Claim.** For `N=max_g w(g)^24`,

```
0 < lambda1/lambda0 <= (N-1)/N < 1,
a m_gap >= log(N/(N-1)) > 1/N > 0.
```

In particular:

| Group | `N` | exact ratio upper bound | exact positive gap lower bound |
|---|---:|---:|---|
| `Z3` | `281474976710656 = 4^24` | `281474976710655/281474976710656` | `log(281474976710656/281474976710655)` |
| `S3` | `59604644775390625 = 5^24` | `59604644775390624/59604644775390625` | `log(59604644775390625/59604644775390624)` |

**Proof.** The temporal kernel satisfies the exact entrywise bound

```
|G|^8 <= K(U,V) <= |G|^8 N,
```

because it has `|G|^8` terms and each term is a product of 24 integers in `[1,wmax]`. Take the strictly positive Perron eigenvector `h` from Theorem A. Its *Doob-transformed* Markov matrix is

```
Q(U,V) = T(U,V) h(V)/(lambda0 h(U))
       = K(U,V) h(V) / SUM_W K(U,W) h(W).
```

Every row sums to one. Define the same reference probability vector for every row, `pi(V)=h(V)/SUM_W h(W)`. By the two exact bounds on `K`,

```
Q(U,V) >= pi(V)/N.
```

Hence `Q = (1/N) J + (1-1/N) R`, where `J(U,V)=pi(V)` and `R` is another stochastic matrix. For every real-valued vector `f`, the oscillation seminorm `osc(f)=max(f)-min(f)` obeys `osc(Qf) <= (1-1/N) osc(f)`, because `Jf` is constant and `R` is stochastic. Every nonconstant eigenvector of `Q` with eigenvalue `theta` therefore has `|theta|<=1-1/N`. The eigenvalues of `Q` are those of `T/lambda0`; Theorem B makes all of them strictly positive on the physical subspace. This proves the ratio inequality. Finally `-log(1-x)>x` for `0<x<1` gives the claimed gap. QED.

The lower bounds are **very small**. They prove nonzero separation, not the observed numerical mass or a useful prediction in physical units without further calibration. At a fixed spacing `a` the bound is `m_gap > 1/(a N)`; no limit in `a` is taken.

## Theorem D — powers of three are a valid spectral jump, not automatically a fast algorithm

For every integer `k >= 0`, the exact transfer over `3^k` temporal slices is `T^(3^k)`. Its nonvacuum-to-vacuum spectral ratio obeys

```
(lambda1/lambda0)^(3^k) <= ((N-1)/N)^(3^k)
                              <= N/(N+3^k).
```

The last inequality is *integer-provable for every nonnegative exponent `m`*: start from `(1-1/N)^0=1`; if it holds at `m`, multiply by `(N-1)/N`, and observe that `(N-1)/(N+m) <= N/(N+m+1)` because the numerator cross-product falls short by `m+1`. The auditor directly checks the rational integer cross-products at `m=1,3,9,27` for both groups.

This is a rigorous **equation-level jump** that does not require finding every physical state. It does *not* assert that computing arbitrary `T^(3^k) f` in a compressed tensor format costs logarithmic time, or that tensor bond growth has been controlled. These are further algorithmic obligations. Every slice can have its own state hash and hash-chain record; those records verify bytes/history, not Perron eigenvalues.

## Companion: the independent fixed 2×2 S₃ Hamiltonian theorem

The **distinct** fixed periodic `2x2` (two-dimensional spatial) model already filed in this repository uses

```
H(J_E,J_B) = J_E E + J_B M,
E = weighted self-adjoint graph Laplacian,
M = nonnegative magnetic diagonal.
```

The independent complete graph reconstruction has `1393` weighted orbit vertices, total orbit weight `W=7776`, connected electric graph with diameter `D=8`, off-diagonal integer jump rates at least one, electric diagonals at most `24`, and magnetic diagonals at most `12`. If `J_E>0`, its graph is irreducible and the bottom eigenvalue is simple. An exact weighted path argument (not requiring the stronger electric spectral certificate) gives

```
gap(E) >= 2/(W*D) = 1/31104.
```

Indeed, for every pair `i,j`, a path with at most `D` edges gives `(f_i-f_j)^2 <= D * <f,E f>_W`, since every edge has conductance at least 1. The weighted-variance identity gives `Var_W(f) = (1/W) SUM_{i<j} w_i*w_j*(f_i-f_j)^2 <= (W*D/2)*<f,E f>_W`, hence the inequality. The positive ground-state eigenvector `v` of `E+rM`, `r=J_B/J_E`, satisfies `v_min/v_max >= (24+12r)^(-8)`. Combining the ground-state transform and the Poincare bound gives the **unconditional-from-graph-data** lower bound

```
gap(H) >= J_E / (31104 * (24+12 J_B/J_E)^16) > 0
       for all J_E>0, J_B>=0.
```

The repository's independently checked stronger electric antecedent `gap(E)=6` sharpens that to the pre-existing bound `6 J_E/(24+12 J_B/J_E)^16`. The premises are in [`independent/SEAT_GLOBAL_COUPLING_GAP_THEOREM.md`](../../independent/SEAT_GLOBAL_COUPLING_GAP_THEOREM.md) and [`independent/ELECTRIC_SPECTRUM_2X2_REPORT.md`](../../independent/ELECTRIC_SPECTRUM_2X2_REPORT.md). Our new script checks the group convolution and arithmetic, **not a fresh reconstruction of all 1393 electric rows**.

At `J_E=0, J_B>0`, this separate Hamiltonian has **eight flat degenerate vacua**, so its gap `E1-E0` is **zero**. Do not claim positivity at this endpoint. In the `J_E>0` region the finite theorem is valid pointwise, not uniformly as `J_E->0`.

## Verification, attacks and acceptance

* Prediction frozen before this proof at [`PREDICTION.hbp`](PREDICTION.hbp) commit `ac7e88dc0c45410f40bd65a6da143520d976ac69`.
* `audit.py` uses exact integers, generates the `Z3`/`S3` multiplication and inverse tables without importing the existing engines, reconstructs all one-link convolution entries, verifies eigenvalue nullities and Sylvester minors, checks the orbit count and powers-of-three ratio arithmetic, and records failures of deliberate controls.
* Reproduce: `python3 proofs/finite-4d-slice-gap-20261106/audit.py > /tmp/FINITE4D-PROOF-AUDIT.hbp` and `cmp /tmp/FINITE4D-PROOF-AUDIT.hbp proofs/finite-4d-slice-gap-20261106/AUDIT.hbp`.
* The result is **DERIVED at the mathematical finite-model level**, **MEASURED for the independent local convolution arithmetic**, and **OPEN for Opus's independent non-author proof audit**. Full interacting eigenvalues, efficient arbitrary tensor contraction width, full SU(3), continuous SU(2), and Clay continuum remain explicitly unproved here.

## Relation to other fixed-volume proofs

For a *different* model, continuous SU(2) at a fixed finite lattice, the existing four-dimensional work gives an explicit bound `|lambda1|/lambda0 <= tanh(beta*N_links)` at `beta>0`, with its separate reflection and transfer hypotheses, as filed in [`YM4-02d`](https://github.com/JesseBrown1980/yang-mills-4-dimensional-continum-proof/blob/main/docs/NOTE-YM4-02d-QUANTITATIVE-GAP.md). Its stronger small-beta locality region is in [`YM4-02e`](https://github.com/JesseBrown1980/yang-mills-4-dimensional-continum-proof/blob/main/docs/NOTE-YM4-02e-KSTEP-AND-LOCALITY.md). These results concern **continuous SU(2)** at fixed lattice, not `S3` or `Z3`; do not transfer numerical gap bounds across gauge groups without a proved correspondence.