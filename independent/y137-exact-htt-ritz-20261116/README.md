# Y137 — independent exact four-vector Ritz acceptance from actual physical Htt

November 16, 2026. Research draft stacked on Stage I [PR #251](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/251), with original frozen H20738 source inputs retained.

## New authenticated result

The original finite 3x4 periodic S3 Hamiltonian at r=9 was applied to all **633,919 physical residual-support coordinates** in eight source-backed hosted shards: **45,642,168 original 72-move electric transitions** and **6,557,422 within-support electric transitions**. Original [Actions run #43992456055](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43992456055) reports **eight of eight shards PASS and full exact fan-in PASS**. Its results are pinned in RESULT-HTT-FULL-20261116.hbp and include all three independent nonzero Htt elements, exact weighted symmetry and both PSD inequalities 0 <= Htt <= 468 Gram(v).

Here t_i=(I-P_old)(D H-z_i)u_i is the true original-source old-Galerkin-orthogonal full physical residual, D=10^9, and v_i=d t_i is the integer scaled residual using the original 4x4 Gram Schur determinant d. The original PR #249 Gram(v)=d E, with E the 2x2 integer residual Gram numerator; the source cross coupling is D*<u_i,H v_j>=E_ij. These facts make an exact generalized four-vector pencil for {u1,u2,v1,v2}:

- Upper left 2x2: D K_uu - z G_uu.
- Upper right and lower left 2x2: E.
- Lower right 2x2: D Htt - z d E.

The independent verifier uses both 4x4 integer Bareiss inertia under symmetric row/column permutations and a separate **2x2 Schur-complement inertia**. It first proves D Htt - (72D)d E is positive definite, making the lower block positive definite throughout 0 <= z <= 72D. Hence the two algorithms must yield identical inertia at every rational bisection point. This explicitly tests both archived bracket endpoints and all intermediate steps.

| Four-dimensional projected Ritz level | Exact numerator bracket (denominator 10^9) | Strict upper bound J_E |
|---|---|---|
| First | (69913037769, 69913037770) | 69.913037770 |
| Second | (69952639134, 69952639135) | 69.952639135 |

The difference between these **four-dimensional projected Ritz levels** is enclosed by 0.039601364 < gap_Ritz < 0.039601366 J_E. This separation is a reduced-space statistic, **not** a certified enclosure of the complete physical gap. The upper endpoints provide variational upper bounds for the corresponding first two Ritz levels of the larger 20,738-dimensional Galerkin subspace. Its full 20,738x20,738 projected Hamiltonian roots are not computed; the exact Htt plus the displayed two old-to-new source couplings do not alone determine all 20,736 other old-to-new entries.

The next acceptance work is exact full old-to-new coupling, new Ritz eigenvectors and their complete original physical full-H residuals (possibly shell5), followed by Wilson eigendirection/sample-specific transfer. First-excitation Wilson spectral-weight positivity HOLD; issue #137 OPEN; 4D continuum Yang–Mills mass gap OPEN.

## Reproduction

python3 -I -B independent/y137-exact-htt-ritz-20261116/independent_four_ritz.py toy

python3 -I -B independent/y137-exact-htt-ritz-20261116/independent_four_ritz.py real

Workflow: .github/workflows/y137-htt-four-ritz-accept.yml.
