# Finite S₃ magnetic end: exact eight-flat-vacuum splitting

**Audit status:** Independent permutation-group reconstruction of the existing 1,393-state periodic 2×2 **finite S₃** model; pure integer/rational 8×8 reduction. This adds no new operator. This is not the 4D Yang–Mills mass-gap theorem.

## Two correct coupling charts

Let `H(JE,JB)=JE E + JB M`. The scale-free electric chart `E+rM` uses `r=JB/JE` with electric endpoint `r=0`, where the finite gauge-invariant electric gap equals **6**. The magnetic chart `M+sE` uses `s=JE/JB` with magnetic endpoint `s=0`, where eight flat states are exactly degenerate. One should not reverse the direction of these limits. Positive-semidefiniteness of both `E` and `M` implies each **individual ordered eigenvalue** increases with its chart parameter; the *gap itself* need not increase. The interval/cell inequality `gap([a,b]) >= E1(a)-E0(b)` holds whenever both eigenvalues are monotone, even if gap is not.

## Exact finite operator controls

The original operator, independently constructed from six permutations of three symbols (PR #7), has 1,393 Gauss-orbit states, 32,385 stored electric entries, positive orbit weights `W` and diagonal magnetic potential in `{0,3,4,6,7,8,9,10,12}`.

For every row `i`, `E_ii=d_i∈[0,24]`, `E_ij<=0` for `i!=j`, `Σ_j E_ij=0`, and `w_i E_ij=w_j E_ji`. Thus, for any real vector `f`,

`<f,E f>_W = (1/2) Σ_{i,j != i} w_i (-E_ij) (f_i-f_j)^2 >= 0.`

This is a direct exact **PSD proof**, not an eigenvalue guess. Weighted Gershgorin also gives `||E||_W <=48`. The magnetic-only flat subspace `P` has dimension 8, with orbit keys `0,7,21,1332,1339,3996,4017,4024`, weights `1,3,2,3,3,2,2,2`. Its orthogonal complement `Q` obeys `3 I <= M_Q <=12 I`.

## First-order surprise: no splitting

Exact compression gives

`P E P = 24 I_8`,

because a single transposition of one link takes any flat state into a nonflat orbit. Therefore the proposed first-order flat-sector gap `delta=gap(PEP)` equals **zero**. In particular, there is **no positive linear gap coefficient `delta*s`** at the magnetic end.

## Second-order effective operator

For `H_s=M+sE`, the complete second-order degenerate-perturbation operator, after removing the common first-order shift `24s I`, is

`B = -P E Q (M_Q)^(-1) Q E P`.

In the original W-weighted orbit basis (not a Euclidean orthonormal basis), its exact rows are:

```text
[-6,-3, 0,-3, 0, 0, 0, 0]
[-1,-6,-2, 0,-1, 0, 0, 0]
[ 0,-3,-6, 0, 0, 0, 0, 0]
[-1, 0, 0,-6,-1,-2, 0, 0]
[ 0,-1, 0,-1,-6, 0, 0, 0]
[ 0, 0, 0,-3, 0,-6, 0, 0]
[ 0, 0, 0, 0, 0, 0,-6, 0]
[ 0, 0, 0, 0, 0, 0, 0,-6]
```

The independently computed exact characteristic polynomial (Faddeev–LeVerrier over rationals, no float or numerical eigenvalue solver) is

`chi_B(lambda)=(lambda+6)^4 (lambda^2+12lambda+22) (lambda^2+12lambda+30).`

Hence the eight eigenvalue shifts are `-6±sqrt(14)`, `-6±sqrt(6)`, and `-6` (multiplicity 4). The first excited-minus-ground **second-order coefficient** is exactly

`delta2=sqrt(14)-sqrt(6) > 0` (approximately 1.29217 as a reader aid only).

Finite-dimensional analytic degenerate perturbation theory then gives

`gap(M+sE) = (sqrt(14)-sqrt(6))*s^2 + O(s^3)` as `s->0+`.

Equivalently at fixed `JB>0`, `gap(H(JE,JB)) = (sqrt(14)-sqrt(6))*JE^2/JB + O(JE^3/JB^2)`. The leading power near the magnetic-only end is **quadratic**, not linear. The exact small-s inequality below does not depend merely on the asymptotic symbol.

## Conservative rigorous nonzero small-s region

Let `C=Q E P`, `D(s)=M_Q+s E_QQ`. By the min–max principle there are exactly eight low eigenvalues of `H_s` in `[0,24s]` for sufficiently small positive `s`, while eigenvalue 9 is at least 3. On this interval the Feshbach/Schur complement is

`F(lambda)=24s I-s^2 C* (D(s)-lambda)^(-1) C`.

The star is the W-weighted adjoint. The preceding exact matrix implies `||C||^2 <= 12 ||-B|| <120`, because `||-B||=6+sqrt(14)<10`. For `0<=lambda<=24s`, positivity of `E_QQ`, `M_Q>=3I`, `||E_QQ||<=48` and the resolvent identity give

`||(D(s)-lambda)^(-1)-M_Q^(-1)|| <= 24s/(3-24s)`.

Therefore, for `0<s<=1/10000`,

`||F(lambda)-(24s I+s^2 B)|| < s^2 * [2880s/(3-24s)] <= (120/1249) s^2.`

The symmetric Schur inertia identity and the monotonicity of `F(lambda)-lambda I` in `lambda` bracket each of the eight low eigenvalues within that error of `24s+s^2 eigenvalue(B)`. In particular,

`gap(M+sE) > s^2 [sqrt(14)-sqrt(6)-2*(120/1249)] > s^2,`

because `sqrt(14)>37/10`, `sqrt(6)<5/2`, and `6/5-240/1249>1`. Thus the following entire **continuous, uncountable coupling region** has a rigorous finite-model lower bound:

**For every `JB>0` and `0<JE/JB<=1/10000`, `gap(JE E+JB M)> JE^2/JB`.**

This bound is very conservative; it is not an optimal range or a lower bound uniform as `s->0`. It complements the mid-chart Weyl rectangles and the electric-only endpoint `gap(E)=6`.

## Reproduce

```bash
python3 independent/seat_magnetic_endpoint.py > /tmp/magnetic.measure
cmp /tmp/magnetic.measure independent/seat_magnetic_endpoint.measure
```

The script reruns the exact source operator reconstruction, checks graph-Laplacian PSD conditions and `PEP`, verifies every entry of the 8×8 second-order matrix and W symmetry, and computes its full characteristic polynomial using only standard-library rational arithmetic. It tests the rational small-s constants and produces zero-JSON pipe records. CI separately checks the stage-2G-to-stage-2H coupling rectangles in the same branch.

**Limitations:** Same model as PR #7 and PR #9; no independent new Hamiltonian measurement. No larger lattice sizes, confinement, continuum gauge group, physical host independence, or Clay existence theorem.
