# Yang–Mills 3D certificate atlas — source audit and falsifiable hypothesis

**Source:** Complete `README.md`, frozen `main` commit `98c39fbaa1e6ecf9e6454062e90801f385356063` (2026-11-17). Retrieved through the connected GitHub source and processed in full: **865 of 865 lines**, **166,833 characters**, **35 headings**. The source includes historical checkpoints; later statements supersede earlier administrative HOLD wording. [Open the exact README](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/blob/98c39fbaa1e6ecf9e6454062e90801f385356063/README.md).

## November 17, 2026 — original Wilson source resolves two Feshbach blocks exactly

[Scientific draft #269](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/269) passed its [original-source hosted test #44098587193](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/44098587193). The original faithful-character sum over the **seven noncontractible winding loops** is a gauge-invariant **diagonal multiplication operator** in the weighted canonical physical S₃ orbit basis. The eight-flat Feshbach projector P selects eight orbit **coordinate states** and Q=I−P selects all other orbit coordinates, so **POQ=QOP=0 exactly**, by disjoint coordinate support. This is specific to the original Wilson multiplication observable and this coordinate projector; it does not follow for an arbitrary Wilson-like matrix or Ritz/Krylov projection.

Consequently, the physical original seven-loop effective observable simplifies from the general four-term expression below to

\[
O_{\mathrm{eff}}(E_2,E_1)=POP+B^\dagger R_2\,QOQ\,R_1 B,\qquad R_i=(QHQ-E_i)^{-1}.
\]

The hosted source replay reconstructed the actual 24-link Wilson values, eight flat and 155,378 nonflat K3 coordinates, and both archived 20-step fixed-sample Q trials. It recorded the *signed original unshifted* fixed-trial terms `POP=208705615476647104000000000000000000000000` and `QOQ=8232562954387472001525446876257519879344`, with both mixed terms zero. Their exact sum `216938178431034576001525446876257519879344` reproduced the frozen raw #180 Wilson sample and its normalized squared value (floor 1,158,787 parts per billion). The omitted-QOQ negative control was rejected, and nonorthogonal fixed-sample overlap was correctly retained under O→O+3I. The earlier source-certified full-Q-dressed **fixed-sample** conventional Wilson lower squared weight >416,300 parts per billion is a separate, unchanged #180 result.

**Scientific boundary:** These are fixed flat trial vectors at historical sampled energies 69.909875505 and 69.949729820 J_E, not the certified true E₁/E₂ energies or true eigendirections. The two-resolvent QOQ physical **8×8 effective matrix**, strict true-energy projector intervals and full-state normalization remain uncomputed. This simplifies the next source acceptance from four numerical terms to two, but **does not** convert the atlas's degree-15 theoretical inverse-residual bound into a Wilson-transfer error or prove a positive true first-excitation spectral weight. Issue #137 **HOLD**, continuum **OPEN**.

## November 17, 2026 — executable exact-integer hypothesis tests

[Research PR #268](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/268) completed [hosted run #44094490381](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/44094490381), **PASS**, with the repository's strict integer-only source audit finding **zero violations**. The [13-row exact receipt](RESULT-ATLAS-PREDICTIONS-20261117.hbp) matches the hosted [SHA-256-sealed artifact](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/44094490381/artifacts/14332877885) byte-for-byte; receipt SHA-256 `d775f3c3689ae298eef7f2eedaca0e9194f9113ad203047b058a58452ebb635a`.

**Strong-coupling retrospective test, not a blind forecast.** The fixed approximation `f(r)=3r−21/r−43/r²` for the **3×3 high-cluster** gap lies within the actual certified point intervals at `r=27,81,243` (**3/3**); it lies **outside** the certified `r=9` interval. A forged third-order coefficient **44** is excluded by the `r=27` interval. The inferred coefficient interval at `r=9` is `[58.889970,58.975182]`, while the three higher-coupling intervals share `[42.936075,43.928973]`, containing 43. These effective-coefficient comparisons were **already observed and explicitly recorded** in the repository's earlier `native/ym/results/zgap2-2026-10-30-cloud/README.md`; this new test adds an independent fail-closed executable replay, not a claim of discovering a new physical coefficient. Higher-order corrections at `r=9` remain necessary.

**Spectral-filter theorem diagnostic.** The repo's source-conditional floor and operator ceiling give `g_Q−E₂^hi=24.118766116 J_E`, versus `E₃^lo−E₂^hi=0.019265416 J_E`. With exact integer square-root enclosures, the standard Chebyshev **inverse-residual** estimate `2ρ^m` is strictly below 0.01 at degree **11**, 0.003 at degree **13**, 1/700 at degree **15**, and 0.0001 at degree **20**. **These are *theoretical worst-case Q-inverse residual bounds*, not measured eigendirection errors or original Wilson overlap errors.** The `m=15` result does not close issue #137.

**Feshbach identity falsification control.** On an independent exact symmetric 5×5 rational matrix, the full-space observable transition and the projected `O_eff(E₂,E₁)` transition both evaluate to `1168/297`; omitting the `QOQ` term changes the answer by `2192/1485` and is rejected. The full-state normalization identity is independently exact in the same toy. This validates the algebraic decomposition and a negative control, **not** the original 3×4 S₃ observable source or Wilson positivity.

**Next genuinely prospective source test:** preregister a new `r=729` 3×3 gap computation (model point prediction `1162246115/531441 J_E ≈ 2186.971112504 J_E`) and compare its new outward-certified interval with the prediction. At present this number is a model point, **not** a certified spectral enclosure or a guaranteed error bound. More importantly for issue #137, construct and certify the four terms of the original **source-authenticated** effective Wilson observable, including the deflated `QOQ` action and rigorous normalization. Wilson first weight **HOLD**; continuum problem **OPEN**.

## Contents and scientific scope

The interactive atlas has four switchable views:

1. **3D high-cluster gap landscape:** **39 recorded points**, with sector point-interval data (not all full physical) separated from whole-torus **lower bounds**. Coordinates: lattice area, log10 coupling, and \((E_9-E_8)/(rJ_E)\). The translucent sheet is the *asymptotic* prediction \(3-21/r^2\) for minimum side ≥3, not a proven global upper bound.
2. **3D spectral evidence:** **15 measurements** of projected Ritz and full physical \(E_1,E_2,E_3\) bounds, plus \(QHQ\) compression floors. These are distinct mathematical scopes.
3. **3D algorithmic atlas:** **26 functional evidence nodes**. Coordinates: log10(reported state/basis cardinality), log10(reported work/check count), and functional operation code (0 geometry, 1 H, 2 H², 3 H³, 4 localizer, 5 inertia, 6 observable). The work-count units differ by node; they describe scale, **not a legitimate runtime regression**.
4. **Prediction from two distinct spectral scales:** algebraic Chebyshev bounds (not solver runtime measurements).

The atlas thus indexes **80 quantitative, functionally linked certificate records**. This deliberately separates finite Yang–Mills measurements from unrelated CHSH, fluid, HTTP, and other software demonstrations also preserved in the README; it is not a claim that every numerical token in that long README represents a physical gap certificate.

## Exact source-derived anchors

| Source quantity | Certified scope | Value |
|---|---|---:|
| Whole finite physical 3×4 Hilbert cardinality | Burnside gauge-orbit count | 2,177,317,873 |
| High nonflat compression floor (lift-dependent) | \(\lambda_\min(QHQ)\) | at least 94.070673 \(J_E\) |
| Independent lift-free \(QHQ\) floor | 3×4, r=9 | at least 94.0682 \(J_E\) |
| E1 whole finite energy | Source-conditional Stage E | (69.909429421,69.909586556) \(J_E\) |
| E2 whole finite energy | Source-conditional Stage E | (69.949264147,69.949433884) \(J_E\) |
| E3 whole finite lower bound | Sector isolation | ≥69.968699300 \(J_E\) |
| Whole finite first gap | Strict endpoint subtraction | (0.039677591,0.040004463) \(J_E\) |
| Whole 20,738D Ritz gap | Stage K 10×10 certificate | >0.016962230 \(J_E\) |
| Exact full-physical H² support | Stage L input and output | 633,919 inputs, 8,805,188 output targets |
| Original Wilson trial centered moment | Stage N fixed sample | negative, approximately −0.644753 \(J_E\) per norm |
| Four-vector full-physical residuals | Stage M, two witnesses | ≤0.416071217745 and ≤0.407236191045 \(J_E\) |
| Current combined Wilson-transfer error | Earlier source certificate | 0.011911898006; one route requires <1/700 |

The physical energy gap exists *within the accepted fixed-finite and source/Perron hypotheses*. Positivity of the specified first-excitation Wilson observable and a four-dimensional continuum theorem remain open.

## Literature-consistent perturbative surface and a falsifiable finite-size hypothesis

The README gives an exact second-order high-cluster expansion for \(\min(L_x,L_y)\ge3\):

\[\Delta_{9,8}(L_x,L_y;r)/J_E=3r-21/r+O(r^{-2}).\]

The 3×3 point intervals at r=27,81,243 are consistent with the further README-listed \(-43/r^2\) correction; it does **not** fit the interval at r=9, where higher terms are important:

| r | 3×3 point interval (JE) | \(3r-21/r-43/r^2\) | In interval? | inferred compatible c3 range |
|---:|---:|---:|---|---:|
| 9 | (23.938578,23.939630) | 24.135802 | no | (58.890, 58.975) |
| 27 | (80.161963,80.163325) | 80.163237 | yes | (42.936, 43.929) |
| 81 | (242.733980,242.735244) | 242.734187 | yes | (36.064, 44.357) |
| 243 | (728.911221,728.913186) | 728.912852 | yes | (23.280, 139.311) |


**Proposed finite-size test, not an established theorem:** In a strong-magnetic expansion, a virtual electric-flip process that winds around a periodic direction must use at least \(L_\min\) steps. Predict that the earliest *winding-dependent* correction is no earlier than \(O(r^{1-L_\min})\) to the leading \(3r\) energy scale. This is compatible with the README's distinct \(1/r\) coefficient at width two and its shared coefficient 21 for width ≥3. It predicts that the \(1/r^2\) coefficient may differ on 3×3, 3×4 and 4×4 because the first two permit length-three winding processes. **Test:** calculate third-order coefficients independently for those three tori; reject the hypothesis if a length-four torus develops a winding correction already at second order or if source enumeration disproves the topological-order argument. Linked-cluster and strong-coupling expansions motivate this kind of analysis but do not automatically establish the proposed coefficient for this Hamiltonian.

## Primary algorithmic hypothesis: deflate first, certify the Wilson observable second

We have *two very different spectral separations*, derived from the recorded certified endpoints:

- Low-state-to-next-state separation: \(E_3^{lo}-E_2^{hi}=0.019265416\,J_E\).
- Deflated Q-block-to-low-state separation, even using the **lift-free** floor: \(g_Q-E_2^{hi}=24.118766116\,J_E\).
- Ratio of these separations: approximately **1,251.9×**.

For a deflated inverse of \(QHQ-z\) on \([g_Q,468]\) at \(z=E_2^{hi}\), the standard Chebyshev minimax inverse bound has

\[\kappa=\frac{468-z}{g_Q-z}\approx 16.50377,\quad \rho=\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\approx 0.604937,\quad \max_{\lambda\in[g_Q,468]}|1-(\lambda-z)p_{m-1}(\lambda)|\le 2\rho^m,\]

with the last inequality interpreted as the **Chebyshev polynomial residual bound for the inverse action**, not an accepted repo-specific energy or Wilson error estimate. The corresponding degree required for theoretical amplitude suppression by 10× and 100× is approximately **6** and **11**.

If instead one directly tries to isolate E2 using a full-band Chebyshev polynomial normalized at E2 and bounded on \([E_3^{lo},468]\), then

\[p_m(E)=T_m\left(\frac{2E-(468+E_3^{lo})}{468-E_3^{lo}}\right)/T_m\left(\frac{2E_2^{hi}-(468+E_3^{lo})}{468-E_3^{lo}}\right),\]

\[\sup_{E\ge E_3^{lo}}|p_m(E)|\le1/\cosh(m\gamma),\quad \gamma\approx0.013914163.\]

Under this conservative full-band bound, 10× and 100× amplitude suppression need degrees **216** and **381**, respectively. They are *upper-envelope worst-case polynomial* comparisons; neither polynomial by itself certifies the nonzero Wilson signal. This enormous method dependence is the main feature of the 3D certificate geometry.

**My falsifiable hypothesis:** the remaining first-excitation Wilson spectral-weight acceptance is more likely to come from a *two-energy, Q-deflated effective observable* of small flat-sector dimension than from uniform high-degree filtering of the full 2.177-billion-orbit operator or another 429-million-direction basis. Let \(P\) span the eight flat physical orbit states, \(Q=I-P\), \(B=QHP\), and \(R_j=(QHQ-E_j)^{-1}\) (well-defined under the accepted Q floor). Then the exact low-energy effective observable between flat components is

\[O_{eff}(E_2,E_1)=POP-POQ\,R_1 B-B^\dagger R_2 QOP+B^\dagger R_2 QOQ\,R_1 B.\]

The physical overlap is \(\langle x_2,O_{eff}(E_2,E_1)x_1\rangle_W\) when the *full* eigenstates are \(\psi_j=x_j\oplus(-R_j Bx_j)\), with exact W normalization. This is a standard Feshbach/Schur partitioning identity applied here to the Wilson operator; it is **not** a proven nonzero overlap. The crucial missing certificate is a strict lower bound on this scalar after all Q-sector and true-state projector errors are included.

### Four registered predictions / falsifiers

1. For the **original seven-loop multiplication observable with the eight-flat coordinate projector**, authenticate the exact structural zeros POQ=QOP=0, and independently source-certify the remaining **POP** and **double-resolvent QOQ** terms. For more general projectors or observables, retain the full four-term formula. Omitting QOQ invalidates the source claim.
2. Produce two-sided exact rational enclosures for the flat 8×8 (or a symmetry-reduced) source-specific effective Wilson matrix with the lift-free Q floor and current E1/E2 spectral windows. A nonpositive lower overlap is a valid HOLD, not a falsification of physical Wilson visibility.
3. Compare cost and sharpness of increasing Q-block inverse degree 6→11→16 with full-band polynomial filter degrees ~216 and ~381, without equating a generic contraction factor to a measured actual error. If Q-block intervals do not contract as the exact residual bound predicts, reject this implementation or its pinning.
4. Recompute the third-order strong-magnetic high-cluster coefficient at 3×3, 3×4 and 4×4. The 3×3 width-three wrap prediction and leading 21-coefficient locality hypothesis may be refuted with exact coefficient extraction.

## Literature comparison (conceptual methods, not prior-art adjudication)

- **Golub and Meurant, _Matrices, Moments and Quadrature_**: Lanczos, matrix-valued spectral measures and Gauss/Radau quadrature explain why exact low-order moments and Schur windows can bound eigenvalues without brute-force diagonalization. https://academic.oup.com/book/52895/chapter-abstract/421920963
- **Collatz–Wielandt / Perron–Frobenius**: positive-vector row-ratio lower bounds motivate the repository's nonflat Perron certificate. https://people.math.wisc.edu/hans/coneinv.pdf
- **Chebyshev approximations and generalized spectral projectors**: the two spectral separations give wildly different polynomial convergence factors; this statement is conditional on the actual spectral enclosure and the chosen approximation problem. https://elekpub.bib.uni-wuppertal.de/download/pdf/3552813.pdf
- **Kato–Temple residual bounds**: the isolation margin and certified full-physical residual control eigenstate certification; Stage M's residuals are larger than its low-state spectral separations. https://doi.org/10.1016%2FS0377-0427%2800%2900413-1
- **Bravyi–Hastings–Michalakis**: local perturbation stability of topological ground bands under its hypotheses; the repo's finite S3 certificates do not yet instantiate a continuum SU(2) mass-gap proof. https://arxiv.org/abs/1001.0344
- **Hamiltonian linked-cluster expansion methods**: motivates distinguishing local coefficients from winding corrections, without asserting a specific new 3×4 coefficient. https://www.sciencedirect.com/science/article/pii/0550321384902189

## Deliverables

- [Interactive 3D certificate atlas](yang_mills_3d_certificate_atlas.html)
- [Source-linked machine-readable certificate inventory](yang_mills_certificate_inventory.json)
- [3D high-cluster preview](yang_mills_3d_graph_preview.png)
- [3D algorithmic preview](yang_mills_3d_algorithmic_graph.png)

**Bottom line:** the finite physical E2−E1 gap is already positive under the frozen finite-model hypotheses; the Wilson first-excitation transition and 4D continuum result are separate, open theorem targets. The proposed short route is to exploit the much larger Q-complement separation and certify an observable-specific Feshbach effective matrix. Its feasibility is a hypothesis to test, not a result already established.