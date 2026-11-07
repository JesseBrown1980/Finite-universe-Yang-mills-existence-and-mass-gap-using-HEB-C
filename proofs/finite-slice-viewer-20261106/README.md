# Finite-slice universe to continuous-looking viewer measurements

**2026-11-06 · research bridge · finite-model benchmark, not a Clay proof.**

The underlying universe is discrete and processed one time slice at a time. A viewer observes derived quantities in chosen units. The step size is **not assumed** to be a Planck time; choosing it requires independent physical calibration. The per-slice SHA-256 receipt identifies computed bytes and a history chain can certify replay, but changing or predicting a hash does **not** change the dynamics.

## Measurement interface

Choose a physical length scale `a_x`, time scale `a_t`, an observation operator `O`, and an error tolerance `epsilon` **before** comparing to physical data. For a positive gauge transfer `T`, write `lambda0 > lambda1` for two eigenvalues in the relevant measured channel. Their ideal normalized one-mode correlator has

```
C(n*a_t)/C(0) = (lambda1/lambda0)^n,
m_viewer = log(lambda0/lambda1)/a_t.
```

For `n=3^k`, the exact equation-level jump is `T^(3^k)`. The jump is valid only with the original operator and with mathematically justified evaluation. A single exact exponential correlation does **not** establish all continuum axioms, relativistic locality, scattering, or experiment-level equivalence.

For lattice Yang–Mills the meaningful measurements include Wilson-loop area/perimeter dependence, charge-sector potentials, gauge-invariant mass correlators, finite-size effects, and restoration of rotational symmetry. Each requires a controlled observer definition and uncertainties. A match at one resolution or one scale is insufficient.

## Independent calibration example: 3D Navier–Stokes shear

An exactly divergence-free 3D shear velocity `u=(u_x(y),0,0)` has identically zero nonlinear advection. It reduces the spatially periodic, unforced Navier–Stokes equations to the heat equation. This lets us test the viewer bridge *without claiming it solves full nonlinear 3D fluid regularity*.

Fix the physical spatial circumference at **1 meter**, viscosity `nu=1 m^2/s`, and viewer observation time `t=1/54 s`. Use resolutions `L=3,9,27` in the `y` direction, physical spacing `a_x=1/L meters`, and explicit forward Euler time `dt=a_x^2/(6*nu)`. All three runs observe the **same** physical time using `n=1,9,81` microscopic updates. The integer numerator update on a cyclic lattice is

```
K_next[i] = 4*K[i] + K[i-1] + K[i+1]   (cyclic indices)
K(0) = delta[i,0];  denominator after n steps is 6^n.
```

The exact power jump is `(4I+S+S^-1)^n`, computed independently by exponentiation by squaring in the cyclic convolution ring. Both algorithms return **identical 27- or fewer-integer kernels**; the large 3D field is not stored.

The first Fourier-harmonic decay multiplier is

```
d_L(t) = ((4+2*cos(2*pi/L))/6)^n.
d_cont(t) = exp(-4*pi*pi/54).
```

The script uses **integer arithmetic and rational intervals only**: Machin's arctangent formula bounds `pi`, and alternating Taylor remainders bound `cos` and `exp`. The error intervals are tight enough to pin the following trillionth-place floors:

| Sites along y | Steps | Finite multiplier | Continuous multiplier | Absolute error |
|---:|---:|---:|---:|---:|
| 3 | 1 | 0.500000000000 | 0.481387939225... | 0.018612060775... |
| 9 | 9 | 0.481549672465... | 0.481387939225... | 0.000161733239... |
| 27 | 81 | 0.481389859807... | 0.481387939225... | 0.000001920582... |

The finite and continuum multipliers **are not identical**. The discrepancy decreases sharply as resolution improves. That is an observable, explicitly checked convergence demonstration, not a claim that every physical observable converges similarly.

Run reproducibly from the root:

```sh
python3 proofs/finite-slice-viewer-20261106/viewer_bridge.py > /tmp/viewer_bridge.hbp
cmp proofs/finite-slice-viewer-20261106/RESULT.hbp /tmp/viewer_bridge.hbp
```

## What remains before any claim about physical four-dimensional SU(3)

1. Specify the exact finite local SU(3) representation, gauge constraints, interactions, reflection-positive transfer, observables, and time/length calibration.
2. Verify the exact matrix jumps preserve the physical Gauss-law sector, not merely a tiny diagnostic catalogue.
3. Compare a nontrivial collection of gauge-invariant observables over multiple powers-of-three lattice scales, with explicit error bars and independent implementations.
4. Separate mathematical appearance of continuous fields at viewer resolution from actual construction on continuous `R^4`, which is a distinct official Millennium requirement.

**Verdict:** FINITE SHEAR VIEWER CONVERGENCE PASS; Yang–Mills viewer equivalence OPEN; physical Planck-scale interpretation UNCALIBRATED; Clay continuous-spacetime theorem NOT PROVEN.
