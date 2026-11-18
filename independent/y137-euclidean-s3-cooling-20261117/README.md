# Original 3×4 S3 Yang–Mills: Euclidean heat-bath / cooling pilot

Date: 2026-11-17. Research-only standalone integer pilot. **Not a mass-gap or first-Wilson-weight certificate.**

## What was actually run

- Original finite group S3 (six permutations), original **3×4 periodic spatial lattice**, Euclidean time extent **8**. 288 directed positive links (192 spatial, 96 temporal), 288 plaquettes (96 spatial, 192 temporal).
- Original seven-loop *summed winding* Wilson character on every time slice: four horizontal length-three characters plus three vertical length-four characters. No substitute plaquette observable.
- The original Hamiltonian's 72 involution moves correspond to three transposition translations on each of 24 spatial links. A symmetric first-order transfer formulation uses an exactly calculable electric heat kernel at a=ln(2)/3: temporal class weights proportional to **(13,3,1)** for identity/transposition/3-cycle. The kernel has trivial/sign/standard Fourier eigenvalues **1,1/4,1/2**. These are exact integer identities, not Monte Carlo estimates.
- Magnetic ratio r=9: per-spatial-plaquette relative weights proportional to **8^(chi+1)**, i.e. (512,8,1) for character (2,0,-1). Thus the anisotropic Euclidean action is matched to a finite-step, symmetric Trotter transfer representation of the ORIGINAL Hamiltonian, not an unrelated isotropic Wilson-action beta.
- Exact-integer local heat-bath, followed by exact-weight microcanonical changes. One arm also tried reversible full boundary-sheet Metropolis moves (two per sweep); the control arm used local updates only.
- Each arm: **two independent chains** (cold/hot), **80 burn-in sweeps**, then **80 sampled configurations per chain** separated by four sweeps. Each configuration contributes eight time slices, or **1,280 slice observations per arm**. Temporal time separations 1,2,3 were measured. This is *160 configurations per arm*, not 1,280 independent samples.
- For every measured configuration, spatial-only magnetic cooling at depths 0,1,2,4. Every configuration is cloned first, preserving the original. Three frames per chain (first/middle/last sample), for each of four depths, are in the `S3_EUCLIDEAN_SNAPSHOT` lines of the run logs as complete 288-byte group-link configurations (hex), with SHA-256 hashes.

## Validation

- Eight full-lattice arbitrary gauge-transformation controls (all plaquette characters and all time-slice summed-winding values unchanged), six-element local link conditional-weight multiset equality under gauge transform, plus spatial-cooling monotonicity.
- Cold flat global sheet move acceptance and changed winding, while preserving zero magnetic energy.
- Negative controls reject using a single nonclosed link character as gauge invariant, and require distinct temporal character-class weights.
- No floating point used by the sampler, statistics or controls. Pseudorandom choices use seeded Python MT19937 `randrange` with exact integer probabilities. The numerator/denominator of every connected correlator is recorded. These are **statistical estimates**, not interval or confidence certificates.

## Results: controlled magnetic smoothing at r=9

| Arm | Chains | Spatial cooling depth | Mean magnetic plaquette sum per time slice | Mean 7-loop Wilson O | Connected C(1) | C(2) | C(3) |
|---|---|---:|---:|---:|---:|---:|---:|
| Sheet moves | pooled | 0 | 0.028 | 0.400 | 32.572 | 22.029 | 11.518 |
| Sheet moves | pooled | 4 | 0.011 | 0.400 | 32.638 | 22.076 | 11.513 |
| Local-only | cold | 0 | 0 | 14.000 | 0 | 0 | 0 |
| Local-only | hot | 0 | 0.100 | 3.200 | 1.125 | -6.265 | -3.056 |

The pooled connected correlations **cannot be interpreted as a physical mass estimate**: severe winding-sector autocorrelation and cold/hot chain disagreement invalidate an equilibrium/independence assertion. In the sheet-move arm, the cold chain accepted **366/800** sheet proposals; the hot chain accepted **0/800**. The cold sheet chain's time-centered C(1) is approximately zero while its ensemble-centered C(1) is ~42.688, showing that fluctuations between long-lived spatial winding sectors contaminate the pooled correlator. In the local-only arm, the cold chain stayed at Wilson O=14 for the entire measurement window.

Cooling reduced the measured magnetic excitation from ~0.028 to ~0.011 per time slice in the sheet-move arm, while leaving the mean Wilson value approximately unchanged. This is a **pilot diagnostic, not evidence of a positive E2 transition**. The E2 overlap is not computed and issue #137 remains HOLD.

## Mathematical scope

Let E be the original electric sum of the 72 transposition link moves and M the original magnetic character plaquette sum. For `a=ln(2)/3` and `r=9`, the exact single-link electric kernel `exp(-a(3I-S_trans))` has class weights (13,3,1)/24. A periodic Euclidean time lattice with temporal group links implements gauge projection for the **finite-step symmetric Trotter transfer** `exp(-a r M/2) exp(-a E) exp(-a r M/2)`; it is not claimed to equal `exp(-a(E+rM))` at finite a. Consequently, no energy-gap extraction from this finite-time pilot is a certificate for the original Hamiltonian.

The original Wilson two-point function at matched Euclidean time (without smoothing) can in principle help identify which spectral channels have visible amplitudes, but estimating it requires equilibrated chains, positive correlation signal across time separations, error budgets and Trotter/volume tests. Cooling changes the measured operator and needs its own transfer interpretation. The current pilot's diagnostic is **sampling nonmixing**; it should not be fitted to an exponential.

## Rerun

```shell
python3 -I -B pilot.py --quick      # 2 chains, 12 burn-in, 12 samples
python3 -I -B pilot.py --pilot      # 2 chains with sheet proposals
python3 -I -B pilot.py --no-sheet   # 2 chains, local-only negative control
```

Original source file `pilot.py` SHA-256: `050f1bc27ec6ca3266f7a58762b6eeae437f39d084f7503e76a3ed290786aafa`.

### Next practical gate

Develop a **gauge-covariant, reversible global winding-sector update** with nonzero acceptance from both hot and cold starts, then require matching within-tolerance winding-sector histograms and blocked autocorrelation/uncertainty diagnostics *before* estimating any physical correlator. When producing a candidate observable, keep the original 7-loop uncooled operator and exact issue #137 spectral-weight certificate separate.