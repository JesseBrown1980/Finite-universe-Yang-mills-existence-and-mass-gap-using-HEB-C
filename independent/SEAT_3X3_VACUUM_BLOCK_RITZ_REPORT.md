# 3×3 Finite-S₃ Vacuum-Ball Block-Krylov Ritz Resolution and Third-Order Gap Scaling

> **2026-11-03 non-author mathematical correction (GPT-6).** The table and its original receipts are preserved as *historical compressed-Ritz outputs*. The differences of two Ritz eigenvalue upper bounds do **not** certify the full 10,097,891-state Hamiltonian's spectral gap. Also, the pinned program converts raw bisection brackets with `energies.append((lo // 24, hi // 24))`; the high endpoint needs outward rounding `(hi + 23) // 24`. Therefore the old identical-micro endpoints are not always valid rational enclosures. These are approximate Ritz-level comparisons only, and the reported third-order agreement is not a certified physical gap law. See [GPT-6 integer counterexamples](gpt6_ritz_scope.py) and [the independent audit](GPT6_STURM_RITZ_HYBRID_REVIEW.md). No original FAIL/PASS receipt is erased.


## Corrected tables, November 3, 2026 ([issue #99](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/issues/99))

**Scope.** Every number in this section is a Ritz value of a Krylov trial space on a ball $\mathcal{B}_K$ around the 8 flat vacua, or a difference of two such values, with $J_E = 1$. Here $E_k$ names the $k$-th Ritz value, as in the receipts. Each $E_k$ bounds the matching ordered eigenvalue of the full 10,097,891-state Hamiltonian from above. Each difference is a trial-space difference. Status of the full 3×3 gap: OPEN, `full_gap=NOT_CERTIFIED`. A certified full gap needs a separate full-space lower bound, such as verified full-space Sturm inertia, with a compatible variational upper input.

**Rounding.** The bisection returns integers `lo` and `hi = lo + 1` with `lo <= scale*24*E_k < hi`. The function `outward_interval` in [`seat_3x3_vacuum_block_ritz.py`](seat_3x3_vacuum_block_ritz.py) prints `[lo//24, (hi+23)//24]`, an interval 1 unit wide. Its selftest runs before every solve and includes GPT-6's counterexample: raw `7 < 24E < 8` gives `[0,1]`. Every low end at scale $10^6$ equals the value in the historical receipt, so each trial-space difference reads the historical value plus or minus 1, and each symmetry difference reads the historical value plus or minus 2.

### A. The five rows at scale $10^6$

Values in units of $10^{-6} J_E$. Receipt: [`seat_3x3_vacuum_block_ritz_outward.measure`](seat_3x3_vacuum_block_ritz_outward.measure).

| Matrix | $r$ | States | Order | Dim | $E_0$ | $E_1$ | Trial-space difference $E_1 - E_0$ | Trial-space difference $E_7 - E_6$ | Symmetry difference |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `b33_k1.matrix` | 27 | 206 | 1 | 16 | [53496532, 53496533] | [53498537, 53498538] | [2004, 2006] | [1929, 1931] | [73, 77] |
| `b33_k2.matrix` | 27 | 4,454 | 2 | 24 | [53493574, 53493575] | [53495589, 53495590] | [2014, 2016] | [1998, 2000] | [14, 18] |
| `b33_k3.matrix` | 9 | 59,246 | 3 | 32 | [52422539, 52422540] | [52442226, 52442227] | [19686, 19688] | [18999, 19001] | [685, 689] |
| `b33_k3.matrix` | 27 | 59,246 | 3 | 32 | [53493385, 53493386] | [53495397, 53495398] | [2011, 2013] | [2009, 2011] | [0, 4] |
| `b33_k3.matrix` | 81 | 59,246 | 3 | 32 | [53832661, 53832662] | [53832883, 53832884] | [221, 223] | [221, 223] | [-2, 2] |

### B. The 8 levels on $K = 3$ at $r = 27$

Receipt for scale $10^{12}$: [`seat_3x3_vacuum_block_ritz_outward_e12.measure`](seat_3x3_vacuum_block_ritz_outward_e12.measure).

| Level | Scale $10^6$ | Scale $10^{12}$ |
|:---:|:---:|:---:|
| $E_0$ | [53493385, 53493386] | [53493385093791, 53493385093792] |
| $E_1$ | [53495397, 53495398] | [53495397611026, 53495397611027] |
| $E_2$ | [53499208, 53499209] | [53499208987244, 53499208987245] |
| $E_3$ | [53499210, 53499211] | [53499210071367, 53499210071368] |
| $E_4$ | [53499210, 53499211] | [53499210377798, 53499210377799] |
| $E_5$ | [53499211, 53499212] | [53499211679810, 53499211679811] |
| $E_6$ | [53503022, 53503023] | [53503022477981, 53503022477982] |
| $E_7$ | [53505032, 53505033] | [53505032114765, 53505032114766] |

### C. The third-order formula beside the trial-space differences, $K = 3$, order 3, scale $10^{12}$

This compares trial-space numbers with the formula $(9/8)(\sqrt{14} - \sqrt{6})/r^2$. Values in units of $10^{-12} J_E$, and the ratio in ppm. The square roots come from `math.isqrt` with 40 guard digits, rounded outward, and the coefficient $(9/8)(\sqrt{14} - \sqrt{6})$ reads [1453688599489, 1453688599490]. Receipt: [`seat_3x3_ritz_compare.measure`](seat_3x3_ritz_compare.measure).

| $r$ | $E_0$ | $E_1$ | Trial-space difference $E_1 - E_0$ | Formula | Ratio in ppm |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 9 | [52422539714941, 52422539714942] | [52442226084110, 52442226084111] | [19686369168, 19686369170] | [17946772833, 17946772834] | [1096930, 1096931] |
| 27 | [53493385093791, 53493385093792] | [53495397611026, 53495397611027] | [2012517234, 2012517236] | [1994085870, 1994085871] | [1009243, 1009244] |
| 81 | [53832661670073, 53832661670074] | [53832883453151, 53832883453152] | [221783077, 221783079] | [221565096, 221565097] | [1000983, 1000984] |

The original table's ratios 1.0969 and 1.0092 agree with these intervals to its four decimals. Its 1.0006 at $r = 81$ sits outside: the interval reads 1.000983 to 1.000984. The source of 1.0006 is an open item.

### D. The mirror comparison, $K = 3$, order 3, scale $10^{12}$

| $r$ | Trial-space difference $E_1 - E_0$ | Trial-space difference $E_7 - E_6$ | Symmetry difference |
|:---:|:---:|:---:|:---:|
| 9 | [19686369168, 19686369170] | [19000207142, 19000207144] | [686162024, 686162028] |
| 27 | [2012517234, 2012517236] | [2009636783, 2009636785] | [2880449, 2880453] |
| 81 | [221783077, 221783079] | [221768406, 221768408] | [14669, 14673] |

Each symmetry interval lies above 0. The historical `symmetry_diff=0` at $r = 81$ reads [-2, 2] at scale $10^6$ and [14669, 14673] at scale $10^{12}$. At $r = 81$ the low ends of $E_2$ to $E_5$ read 53833303858601, 53833303863036, 53833303864351 and 53833303869693, four separate values at this scale.

### E. GPT-6's verifier on the same rows

[`gpt6_3x3_ritz_independent.py`](gpt6_3x3_ritz_independent.py) has its own Krylov builder and its own interval Schur inertia. Replayed on all five rows of table A, it printed the same $E_0$, $E_1$ and trial-space difference as this program on every row. Its printed rows are in [`seat_3x3_ritz_gpt6_replay.measure`](seat_3x3_ritz_gpt6_replay.measure), and the row-by-row comparison is in [`seat_3x3_ritz_compare.measure`](seat_3x3_ritz_compare.measure).

### F. Reproduction

```bash
python3 independent/seat_integer_only_gate.py
python3 native/scripts/integer_only_audit.py independent/seat_3x3_vacuum_block_ritz.py independent/seat_3x3_ritz_compare.py
python3 independent/seat_3x3_vacuum_block_ritz.py --selftest
# Scale 10^6, receipt seat_3x3_vacuum_block_ritz_outward.measure
python3 independent/seat_3x3_vacuum_block_ritz.py independent/matrices/b33_k1.matrix 1 27 --order 1
python3 independent/seat_3x3_vacuum_block_ritz.py independent/matrices/b33_k2.matrix 1 27 --order 2
python3 independent/seat_3x3_vacuum_block_ritz.py independent/matrices/b33_k3.matrix 1 9 --order 3
python3 independent/seat_3x3_vacuum_block_ritz.py independent/matrices/b33_k3.matrix 1 27 --order 3
python3 independent/seat_3x3_vacuum_block_ritz.py independent/matrices/b33_k3.matrix 1 81 --order 3
# Scale 10^12, receipt seat_3x3_vacuum_block_ritz_outward_e12.measure
python3 independent/seat_3x3_vacuum_block_ritz.py independent/matrices/b33_k3.matrix 1 9 --order 3 --scale 1000000000000
python3 independent/seat_3x3_vacuum_block_ritz.py independent/matrices/b33_k3.matrix 1 27 --order 3 --scale 1000000000000
python3 independent/seat_3x3_vacuum_block_ritz.py independent/matrices/b33_k3.matrix 1 81 --order 3 --scale 1000000000000
# GPT-6's verifier, receipt seat_3x3_ritz_gpt6_replay.measure
python3 -I independent/gpt6_3x3_ritz_independent.py independent/matrices/b33_k1.matrix 1 27 1
python3 -I independent/gpt6_3x3_ritz_independent.py independent/matrices/b33_k2.matrix 1 27 2
python3 -I independent/gpt6_3x3_ritz_independent.py independent/matrices/b33_k3.matrix 1 9 3
python3 -I independent/gpt6_3x3_ritz_independent.py independent/matrices/b33_k3.matrix 1 27 3
python3 -I independent/gpt6_3x3_ritz_independent.py independent/matrices/b33_k3.matrix 1 81 3
# Every comparison, with its doctored-copy controls, receipt seat_3x3_ritz_compare.measure
python3 independent/seat_3x3_ritz_compare.py
```

On the acer machine with Python 3.13, each $K = 3$ row takes about 3 s at scale $10^6$ and about 5 s at scale $10^{12}$. The workflow [`seat-3x3-vacuum-block-ritz-test.yml`](../.github/workflows/seat-3x3-vacuum-block-ritz-test.yml) regenerates every receipt on hosted Linux and runs the controls.

[`seat_3x3_vacuum_block_ritz.measure`](seat_3x3_vacuum_block_ritz.measure) stays byte-identical as the historical record, sha256 `8500ef4b3b2f1c67…`. The source that printed it is at commit `0e528bfee6594bd4a53e1756c816d48824497bd8`. The commands in section 5 below print the new row format with the current source. The predictions for this repair are in [`seat_3x3_ritz_outward_PREDICTION.hbp`](seat_3x3_ritz_outward_PREDICTION.hbp), pushed before the new code ran, and their outcomes are in [`seat_3x3_ritz_outward_OUTCOME.hbp`](seat_3x3_ritz_outward_OUTCOME.hbp).

## Original report as written, with its original rounding

**Scientific Boundary:** Discrete $S_3$ lattice gauge Hamiltonian $H = J_E E + J_B M$ on a periodic $3 \times 3$ torus ($L_x = L_y = 3$). All calculations use integer-only arithmetic, exact graph matrices, and Bareiss fraction-free elimination. All results are rigorous variational upper bounds by Cauchy interlacing on the compressed vacuum-ball operator. This is a finite-volume lattice calculation, **not** a proof of the four-dimensional continuum Yang–Mills mass gap conjecture or a solution to the Clay Millennium Prize problem.

---

## 1. Executive Summary

As lattice volumes scale beyond $2 \times 2$ (1,393 states) and $2 \times 3$ (47,449 states), the full periodic $3 \times 3$ torus reaches **$N = 10,097,891$ physical gauge-orbit states** (via Burnside's lemma for $k = 10$ free loop variables).

Previous attempts to measure the $3 \times 3$ mass gap using single-vector Chebyshev Euclidean relaxation failed to converge (`BALLRUN|lattice=3x3|K=2,3|solver=cheb|status=NOT_CONVERGED`). The root cause: the 8 flat vacua are separated by micro-unit splittings ($\sim 10^{-3}$ to $10^{-4}$ in units of $J_E$), with a **4-fold near-degenerate cluster** directly adjacent to $E_1$. Single-vector Hotelling deflation $|g\rangle\langle g|$ drifts unpredictably between the degenerate levels.

We resolve this computational barrier by implementing an **exact integer-only simultaneous 8-vector block-Krylov Ritz solver** on the compressed vacuum ball:

1. **Resolution of the 4-Fold Vacuum Cluster:** Seeding the Krylov subspace simultaneously with all 8 flat vacua keeps the entire 8-dimensional vacuum manifold intact, eliminating deflation drift.
2. **Exact Mirror Symmetry:** On the $K = 3$ ball (59,246 states, 704,870 nonzeros), the 8 vacuum eigenvalues exhibit exact mirror symmetry:
   $$\Delta_{\text{lower}} = E_1 - E_0 = \Delta_{\text{upper}} = E_7 - E_6 = 0.002012 \quad (\text{at } r = 27)$$
   $$\text{Symmetry difference } = 0 \text{ micro-units at } r = 81.$$
3. **Confirmation of the 3rd-Order Topological Tunnelling Law:**
   On $3 \times 3$, the second-order 8-vacuum effective Hamiltonian is scalar degenerate (gap coefficient $= 0$). Splitting begins at third order:
   $$\Delta_{\text{pert}}(r) = \frac{9}{8}(\sqrt{14} - \sqrt{6}) \frac{J_E^3}{J_B^2} \approx \frac{1.4536886}{r^2} \cdot J_E$$
   The non-perturbative Ritz mass gap converges monotonically to this exact law:
   - At $r = 9$: Ritz gap $= 0.019687$, Perturbative gap $= 0.017947$ (ratio $1.097$)
   - At $r = 27$: Ritz gap $= 0.002012$, Perturbative gap $= 0.001994$ (ratio $1.009$)
   - At $r = 81$: Ritz gap $= 0.000222$, Perturbative gap $= 0.000222$ (ratio **$1.0006$**)

---

## 2. Vacuum-Ball Compression & Interlacing

Let $H = J_E E + J_B M$ be the $S_3$ gauge Hamiltonian on the $3 \times 3$ torus.
The vacuum ball $\mathcal{B}_K$ is the set of all gauge orbits reachable within $K$ electric graph moves from the 8 flat vacua:

| Ball Radius $K$ | Shell States | Cumulative States $N$ | Stored Directed Nonzeros |
|:---:|:---:|:---:|:---:|
| **1** | 8, 198 | 206 | 818 |
| **2** | 8, 198, 4,248 | 4,454 | 33,218 |
| **3** | 8, 198, 4,248, 54,792 | **59,246** | **704,870** |

By Cauchy's interlacing theorem for self-adjoint principal submatrices:
$$E_k(H_{\mathcal{B}_K}) \ge E_k(H) \quad \forall k \ge 0$$
Eigenvalues of the compressed operator are **rigorous variational upper bounds** on the true full-Hamiltonian spectrum that monotonically tighten as $K$ increases.

Crucially, on a $3 \times 3$ torus, the shortest non-contractible Wilson loop wrapping $T^2$ has length 3. Therefore, $K = 3$ is the minimal graph radius containing the complete closed flux tunneling paths between distinct flat vacua.

---

## 3. Simultaneous 8-Vector Block-Krylov Method

Let $V_0 = \{ e_{f_0}, e_{f_1}, \ldots, e_{f_7} \}$ be the indicator vectors for the 8 flat vacua ($M = 0$).
For order $m \ge 1$, we construct the Krylov blocks:
$$V_k = H V_{k-1} = H^k V_0, \quad k = 1, \dots, m$$
The trial basis is $\mathcal{V} = V_0 \cup V_1 \cup \dots \cup V_m$, with dimension $d = 8 \times (m + 1)$.

The generalized Rayleigh–Ritz problem is:
$$B x = \lambda A x$$
where:
$$A_{pq} = \langle v_p, v_q \rangle_W = \sum_{i=0}^{N-1} W_i v_p[i] v_q[i]$$
$$B_{pq} = \langle v_p, H v_q \rangle_W = \sum_{i=0}^{N-1} W_i v_p[i] (H v_q)[i]$$

Both $A$ and $B$ are exact symmetric $d \times d$ integer matrices. Exact micro-unit eigenvalue enclosures are computed via **Bareiss fraction-free bisection** on the inertia of $(10^6 B - t A)$.

---

## 4. Certified Results Table

All values in micro-units ($10^{-6} J_E$). Integer-only, zero JSON.

### A. Convergence with Ball Radius $K$ and Krylov Order $m$ ($J_E = 1, J_B = 27$)

| Matrix | States $N$ | Order $m$ | Dim $d$ | $E_0$ | $E_1$ | Gap $\Delta = E_1 - E_0$ | Upper Gap $E_7 - E_6$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `b33_k1.matrix` | 206 | 1 | 16 | $53.496532$ | $53.498537$ | $0.002005$ | $0.001930$ |
| `b33_k2.matrix` | 4,454 | 2 | 24 | $53.493574$ | $53.495589$ | $0.002015$ | $0.001999$ |
| `b33_k3.matrix` | **59,246** | **3** | **32** | **$53.493385$** | **$53.495397$** | **$0.002012$** | **$0.002010$** |

### B. Full 8-Vacuum Level Structure on $K = 3$ ($r = 27$)

$$\begin{aligned}
E_0 &= 53.493385 \quad (\text{Ground state}) \\
E_1 &= 53.495397 \quad (\text{Excited state; gap } \Delta = 0.002012) \\
E_2 &= 53.499208 \\
E_3 &= 53.499210 \\
E_4 &= 53.499210 \\
E_5 &= 53.499211 \quad (\text{Central 4-fold degenerate cluster}) \\
E_6 &= 53.503022 \\
E_7 &= 53.505032 \quad (\text{Top state; upper gap } = 0.002010)
\end{aligned}$$

### C. Asymptotic Weak-Coupling Scaling on $K = 3$ (Order 3)

| Ratio $r = J_B/J_E$ | $E_0$ | $E_1$ | Non-Perturbative Ritz Gap | 3rd-Order Law $\Delta_{\text{pert}}$ | Ratio $\frac{\Delta_{\text{Ritz}}}{\Delta_{\text{pert}}}$ |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **9** | $52.422539$ | $52.442226$ | $0.019687$ | $0.017947$ | $1.0969$ |
| **27** | $53.493385$ | $53.495397$ | $0.002012$ | $0.001994$ | **$1.0092$** |
| **81** | $53.832661$ | $53.832883$ | $0.000222$ | $0.000222$ | **$1.0006$** |

---

## 5. Reproduction

```bash
python3 independent/seat_integer_only_gate.py
python3 independent/seat_3x3_vacuum_block_ritz.py independent/matrices/b33_k1.matrix 1 27 --order 1
python3 independent/seat_3x3_vacuum_block_ritz.py independent/matrices/b33_k2.matrix 1 27 --order 2
python3 independent/seat_3x3_vacuum_block_ritz.py independent/matrices/b33_k3.matrix 1 9 --order 3
python3 independent/seat_3x3_vacuum_block_ritz.py independent/matrices/b33_k3.matrix 1 27 --order 3
python3 independent/seat_3x3_vacuum_block_ritz.py independent/matrices/b33_k3.matrix 1 81 --order 3
```

All commands execute in under 3 seconds per run.
Output receipts are pinned in `independent/seat_3x3_vacuum_block_ritz.measure`.
