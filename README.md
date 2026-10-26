# Finite-universe Yang–Mills with HEB-C

Exact spectral certificates for S₃ lattice gauge theory on periodic finite
lattices, run headless through the HEB-C HTTP-0 backend. GitRAM distributes the
work across GitHub Actions cells. Every computation is integer-only, Rust 1.81,
and every receipt line ends in `json=0`.

The Hamiltonian is H = J_E·E + J_B·M on gauge-invariant states. The electric
term E sums over the three transpositions on every link, the magnetic term is
M = Σ_p (2 − χ(U_p)), and r = J_B/J_E. Results are eigenvalue counts below
chosen thresholds, from interval inertia (LDLᵀ with outward rounding and
magnetic-shell Schur reduction), with every step recorded in HBP/HBI receipts.

## Results

**Gap above the eight-state flat-vacuum cluster, E₉ − E₈, for every r ≥ 9**
(monotone coupling cells plus the flat-state bound E₈ ≤ 3 × number of links):

| Lattice | Sectors | Bound for every r ≥ 9 | Where |
|---|---|---|---|
| 3×3 | zero momentum | E₉ − E₈ ≥ 23.357514 J_E | [`native/ym/reference/`](native/ym/reference/ym3x3_frozen_8fd12e6.hbp), regenerated on fresh machines in [`native/ym/results/3x3_regeneration/`](native/ym/results/3x3_regeneration/) |
| 2×2 | zero momentum | ≥ 22.727075 J_E | [`native/ym/results/2xL/`](native/ym/results/2xL/README.md) |
| 2×3 | zero momentum | ≥ 22.798240 J_E | same |
| 2×4 | zero momentum | ≥ 22.565393 J_E | same |
| 2×2, 2×3 | full physical space, all momenta | 8 levels below t₁ and below t_B at r = 9 | [`native/ym/results/full_space_r9/`](native/ym/results/full_space_r9/summary.hbp) |

**Point certificates** of E₉ − E₈, in units of J_E:

| r | 2×2 | 2×3 | 2×4 | 3×3 |
|---|---|---|---|---|
| 9 | [22.829351, 22.830510] | [22.999140, 23.000177] | [22.833511, 22.835420] | [23.938578, 23.939630] |
| 27 | [79.625728, 79.626755] | [79.711705, 79.713463] | [79.639284, 79.640698] | [80.161963, 80.163325] |
| 81 | [242.543881, 242.545661] | [242.572553, 242.573741] | [242.548047, 242.549116] | [242.733980, 242.735244] |
| 243 | [728.847290, 728.848700] | [728.856505, 728.858026] | [728.848613, 728.849874] | [728.911221, 728.913186] |

The gap above the cluster is nearly the same on every lattice and grows like 3r.
The cluster's internal splitting E₂ − E₁ depends on shape. On 2×L it follows
L/r; on 3×3 it is third order (0.002 at r = 27). Full tables:
[`native/ym/results/2xL/README.md`](native/ym/results/2xL/README.md).

**Checks on the evidence:**
- **Re-execution:** all 224 2×L shards re-run byte for byte.
- **Integrity:** every shard's index and anchor regenerated from its contents.
- **Fresh machines:** the 3×3 certificates were regenerated in 25 GitRAM cells
  with pinned matrix SHA-256s.
- **Two routes to the same counts:** the split-column pipeline reproduces the
  unsplit 2×4 certificate exactly.

**In progress:**
- 2×5 at r = 9, zero momentum, through 128 GitRAM cells and 4 strict merges.
- Full-space counts on 2×4 and 3×3 through the reflection-only sectors.
- A separately written operator and inertia verifier.

## The theory route

[`docs/YM_TOPOLOGICAL_STABILITY_PROOF.md`](docs/YM_TOPOLOGICAL_STABILITY_PROOF.md),
architecture by Jesse Daniel Brown. On the raw link space the magnetic plaquette
term has the same local ground projector as Kitaev's quantum double D(S₃). Its
eight flat states are the D(S₃) torus ground space. With E as a bounded local
perturbation of strength 6/r per link, topological-order stability
(Bravyi–Hastings–Michalakis, with Cui et al. for the quantum-double TQO
conditions) gives E₉ − E₈ ≥ c·J_B uniformly in volume for r ≥ r₀, and a band
width that shrinks exponentially with torus size. The document marks which
lemmas are proved and which are being instantiated.

## Architecture

- [`native/ym/`](native/ym/README.md): the HTTP-0 execution and verification
  backend `hebc_ym_http0`, plus the sector tools (`ymsec`, `flatcomp`, `cluster`,
  `shellschur`). One job is one disk shard: `run.hbp`, `index.hbi`,
  `run.anchor`, `run.measure`. The headless command and the loopback route share
  one code path.
- [`native/`](native/README.md): the HEB-C kernel. It provides virtual HTTP-0
  addressing over 23,000,000,000 IDs, receipts, the 2×2 torus operator, and the
  vendored Clasy X3 kernel.
- `.github/workflows/`: GitRAM lanes for regeneration, the 2×5 stages and the
  stage B pipeline, all with sealed fan-ins.

## 2×2 coupling ladder: E₁ − E₀

On the full 1,393-state 2×2 torus, the first excitation gap is certified at
these points:
- **(J_E, J_B) = (1, 1):** E₀ ∈ [7.634198, 7.634199], E₁ ∈ [13.240000, 13.242733], gap ∈ [5.605801, 5.608535].
- **(J_E, J_B) = (3, 5):** gap ∈ [14.140772, 14.142823].

A further set of certified cells covers r = J_B/J_E ∈ [3, 10,022]. They come
from interval Sturm counts over the four translation sectors, monotone cells and
SHA-keyed ledgers, on branch `integer-sturm-ladder`. The weak-coupling law there
is r·(E₁ − E₀) → √14 − √6. Ledger and method:
[docs/LADDER_METHOD.md](docs/LADDER_METHOD.md),
[docs/EVOLUTION_TESTGROUND.md](docs/EVOLUTION_TESTGROUND.md),
[docs/SGRAM_CERTIFICATE_CACHE_NOTES.md](docs/SGRAM_CERTIFICATE_CACHE_NOTES.md).

| r | certified readings (per unit J_E) |
|---|---|
| 1 | E₀ < 7.750, E₁ > 13.187 |
| 2 | E₀ < 14.375, E₁ > 18.125 |
| 9 | E₀ < 22.895, E₁ > 23.045 |
| 27 | E₀ < 23.639, E₁ > 23.683 |
| 81 | E₀ < 23.882, E₁ > 23.895 |
| 243 | E₀ < 23.961, E₁ > 23.965 |

## Earlier stages

- **Stage 2B:** the exact 11-dimensional two-plaquette Hamiltonian, built from
  279,936 raw configurations, with gap ∈ (10, 12) at J_E = J_B = 1.
  [Report](STAGE2B_DOUBLE_PLAQUETTE_EXACT_SPECTRUM.md).
- **Stage 2C:** the 2×2 torus, 1,393 gauge-invariant states, 32,385 nonzeros,
  exact weighted self-adjointness, and 8 flat ground states at the magnetic end.
  [Report](STAGE2C_TORUS_1393_SPARSE_REPORT.md).
- **Stage 2G–2I:** rational and integer-inertia certificates and an independent
  verifier for the 2×2 torus. The vacuum energy is about 1.91 per plaquette at
  (1, 1). [2H](STAGE2H_TORUS2_INTEGER_INERTIA_CERTIFICATE.md),
  [2I](STAGE2I_INDEPENDENT_VERIFIER_AND_SCALING.md).
- **Constellation audit:** the original 3/27/243 sector transitions and
  45/405/3,645 keys compiled into the native build, with a gauge-invariant
  243-sector index of the 1,393 torus orbits.
  [Audit](STAGE2D_CONSTELLATION_SOURCE_AUDIT.md).
- **Clasy X3 kernel:** the 81-mode finite-field shell model with its exact
  all-time invariant, 81 × 243 and 243 × 81 batches, and receipts.
  [Pinned reference](CLASY_X3_PINNED_REFERENCE.md),
  [roadmap](CLASY_X3_TO_HEBC_HTTP0_NEXT_HURDLES.md),
  [continuum guide](CLASY_X3_CONTINUUM_HURDLES_GUIDE.md).
- **Plan:** [HEBC_HTTP0_HEADLESS_YANG_MILLS_PLAN.md](HEBC_HTTP0_HEADLESS_YANG_MILLS_PLAN.md),
  [Stage 2 audit](STAGE2_SCALING_SPECTRAL_AUDIT_2026-10-24.md).

## Reproduce

```sh
# backend and sector tools
cd native/ym
cargo +1.81.0 build --release --offline --locked
cargo +1.81.0 clippy --release --all-targets --offline --locked -- -D warnings
results/2xL/check.sh
target/release/hebc_ym_http0 job /tmp/root sector/2/2/1/1
target/release/hebc_ym_http0 job /tmp/root count/2/2/1/1/1/27/64000/15/10
target/release/hebc_ym_http0 serve /tmp/root 5191 16

# HEB-C kernel
cd ../
cargo +1.81.0 test --all-targets --offline
cargo +1.81.0 run --release --offline --locked -- torus2-independent 1 1 indep-1-1
cargo +1.81.0 run --release --offline --locked -- torus2-independent-verify 1 1 indep-1-1
cargo +1.81.0 run --release --offline --locked -- serve 5088
```

Theory and architecture: Jesse Daniel Brown.
