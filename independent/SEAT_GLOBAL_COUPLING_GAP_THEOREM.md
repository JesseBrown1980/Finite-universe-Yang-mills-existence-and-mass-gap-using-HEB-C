# Global coupling-ratio lower gap bound for the *fixed* finite S₃ 2×2 torus

**Status:** Independently reconstructed finite graph, exact combinatorial arithmetic, and a new analytic bound conditional on the original native **electric-only gap = 6**. Sharper intervals invoke Stage 2G E₀ and PR #9 E₁ antecedents; the magnetic-end inequality comes from draft PR #11. Not a larger-lattice or continuum theorem.

## Scope and scale

The exactly defined 1,393-state Hamiltonian on the weighted Gauss-invariant sector is

`H(JE,JB) = JE E + JB M`.

For `JE>0`, introduce `r=JB/JE>=0` and `h(r)=E+rM`, so the actual gap is `gap(H)=JE gap(h(r))`. For `JB>0`, the reversed parameter is `s=JE/JB=1/r`. The exact electric endpoint is `gap(E)=6`; the magnetic-only endpoint has eight degenerate flat states and gap zero.

## Checked finite graph properties

Independent PR #7 source reconstruction, using exact permutation-group orbit enumeration rather than the native Rust operator, gives:

- 1,393 orbit states, `sum_i w_i = 7,776`, positive weights in `{1,2,3,6}`.
- 32,385 sparse electric coefficients, weighted detailed balance `w_i E_ij=w_j E_ji`.
- `E_ij<=0` for distinct states, `E_ii=d_i<=24`, each row sums to zero. Hence `<f,Ef>_W = 1/2 sum_{i,j} w_i(-E_ij)(f_i-f_j)^2 >=0`.
- `M` diagonal, `0<=M_i<=12`, with weighted average `sum_i w_i M_i / sum_i w_i = 8`.
- The complete undirected graph of strictly negative electric entries is connected with **shortest-path diameter D=8**. The verifier checks all 1,393 source vertices by exact breadth-first search, not a sample.
- Every present edge has integer jump rate `c_ij=-E_ij>=1`; `E` has an exact **electric-only gap 6**, a pre-existing native analytic certificate, not a result freshly established by this script.

These facts yield a coarse but **explicit rigorous bound at every positive finite coupling ratio**, rather than requiring potentially enormous cell enumeration.

## Ground-state Harnack / Dirichlet proof

Fix `r>=0`, let `v_i>0` be the unique ground-state eigenvector of `h(r)=E+rM`, with energy `e_0(r)>=0` (positivity follows from connected stoquastic electric graph and PSD of E/M).

The eigenvector equation at vertex `i` is

`sum_{j != i} c_ij v_j = [d_i + r M_i - e_0(r)] v_i`.

For any electric graph edge `i-j`, positivity of every term and `c_ij>=1` imply

`v_j <= (d_i+r M_i) v_i <= (24+12r) v_i`.

The opposite directed edge also exists by weighted detailed balance; the same holds in reverse. Thus, following a shortest path between the maximum and minimum values of `v` (at most `D=8` edges),

`v_min/v_max >= (24+12r)^(-8)`.

The standard exact ground-state (Doob) transformation on this finite weighted graph gives, for `f_i=v_i u_i`,

`<f,(h-e0)f>_W = (1/2) sum_{i,j != i} w_i c_ij v_i v_j (u_i-u_j)^2`.

When `f` is weighted-orthogonal to `v`, then `sum_i w_i v_i^2 u_i=0`. For any constant `c`, the original electric Poincaré inequality says

`<u,Eu>_W >= 6 min_c sum_i w_i(u_i-c)^2`.

The transformed energy dominates `v_min^2 <u,Eu>_W` and the transformed variance satisfies

`min_c sum_i w_i v_i^2(u_i-c)^2 <= v_max^2 min_c sum_i w_i(u_i-c)^2`.

Dividing gives the variational first-excitation bound

`gap(h(r)) >= 6(v_min/v_max)^2 >= 6/(24+12r)^16`.

**Global finite-model inequality, for every real `JE>0, JB>=0`:**

`gap(JE E + JB M) >= 6 JE/(24+12 JB/JE)^16 > 0.`

This is typically extremely tiny and not close to optimal. The statement establishes **strict positivity pointwise for every finite ratio**, but not a positive constant uniform as `r→∞` or `JE→0`. For `JE=0,JB>0` the gap is exactly zero.

## Sharper certified intervals, valid for ALL real ratios in each chart

Write `g(r)=gap(E+rM)`. The old quantitative anchors are strict `E1(1)>13.240` and `E0(5/3)<36.699228/3=12.233076`, with `E1(5/3)>50.840/3`. Because `0<=M<=12I`, individual ordered eigenvalues are nondecreasing and 12-Lipschitz in `r`. A constant trial function gives `E0(r)<=8r`.

1. **Electric-to-middle `0<=r<=1`:** `E1(r)>13.240-12(1-r)`, `E0(r)<=8r`, so `g(r)>31/25+4r`.
2. **Monotone cross-endpoint cell `1<=r<=5/3`:** `E1(r)>=E1(1)>13.240` and `E0(r)<=E0(5/3)<12.233076`, so **`g(r)>251731/250000=1.006924`**.
3. **Middle extension `5/3<=r<=2`:** `E1(r)>=E1(5/3)>1271/75` and `E0(r)<=8r`, so **`g(r)>1271/75-8r`**, at `r=2` still `>71/75`.
4. **Remaining middle/tail `r>=2`:** the globally certified Harnack/Poincaré formula applies, with no finite gap in the coverage of coupling ratios.
5. **Magnetic near-end `r>=10000` (`s<=1/10000`):** PR #11's independently reconstructed 8-flat second-order Schur result is sharper: **`g(r)>1/r`**, or `gap(H)>JE^2/JB`.

At `r=0`, native electric spectral theory gives the **exact** `g(0)=6`; this is stronger than the general inequality.

These bounds form a **complete quantitative positive lower envelope** for every `JE>0,JB>=0` on the fixed finite 2×2 S₃ torus. The complete coverage uses one global graph inequality rather than claiming every segment has separately computed narrow spectral cells. Tighter certified cell-based enclosures for `2<r<10000` remain useful future work but are **not necessary to establish pointwise positivity for this finite model**.

## Executable review and reproducibility

`independent/seat_global_coupling.py` rebuilds the operator, checks all electric rows and weighted self-adjointness, exact `M` mean and Gershgorin ranges, and exhaustively measures all graph eccentricities. It requires the pinned full PR #9 inertia output and PR #11 magnetic measure, and checks the exact rational interval endpoint arithmetic. The analytic ground-state transform argument above should be reviewed as a **mathematical proof**, not reduced to whether its Python assertions pass.

```bash
python3 independent/seat_global_coupling.py > /tmp/seat_global_coupling.measure
cmp /tmp/seat_global_coupling.measure independent/seat_global_coupling.measure
```

No floats, no JSON. Draft PR, separate from the unmerged native-operator verification PRs. No statement about larger tori, mass gap uniform in lattice spacing or volume, 4D continuum gauge theory or the Clay problem follows from the finite theorem.

## Integer-only audited runtime

This verifier imports `seat_integer_ratio.IntegerRatio`, which stores only integer numerators/denominators. Cross-products, division and ordering use integer multiplications and integer floor-division, never IEEE floating-point arithmetic, `fractions.Fraction`, or decimal libraries. The integer-only AST gate and exact receipt replay run in CI. Proof conclusions and HBP/HBI/STURM antecedents remain the same as before refactoring.
