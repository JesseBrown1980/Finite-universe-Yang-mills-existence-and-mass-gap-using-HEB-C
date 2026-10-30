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
| 2×5 | zero momentum | ≥ 21.778000 J_E | [`native/ym/results/2x5_stage_b/`](native/ym/results/2x5_stage_b/HEBC-YM-2X5-STAGE-B.hbp), sealed `PASS` |
| 3×3 | full physical space, all momenta (10,097,891 states) | ≥ 17.9 J_E; at r = 9, > 19.366578 J_E | [`native/ym/results/3x3_full_space/`](native/ym/results/3x3_full_space/CERTIFY-RESULT.md), certify `PASS` |
| 2×2, 2×3 | full physical space, all momenta | 8 levels below t₁ and below t_B at r = 9 | [`native/ym/results/full_space_r9/`](native/ym/results/full_space_r9/summary.hbp) |

**Point certificates** of E₉ − E₈, in units of J_E:

| r | 2×2 | 2×3 | 2×4 | 3×3 |
|---|---|---|---|---|
| 9 | [22.829351, 22.830510] | [22.999140, 23.000177] | [22.833511, 22.835420] | [23.938578, 23.939630] |
| 27 | [79.625728, 79.626755] | [79.711705, 79.713463] | [79.639284, 79.640698] | [80.161963, 80.163325] |
| 81 | [242.543881, 242.545661] | [242.572553, 242.573741] | [242.548047, 242.549116] | [242.733980, 242.735244] |
| 243 | [728.847290, 728.848700] | [728.856505, 728.858026] | [728.848613, 728.849874] | [728.911221, 728.913186] |

2×5 at r = 9, zero momentum: E₉ − E₈ ∈ [22.613640, 22.615366] J_E.

The gap above the cluster is nearly the same on every lattice and grows like 3r.
The cluster's internal splitting E₂ − E₁ depends on shape. On 2×L it follows
L/r; on 3×3 it is third order (0.002 at r = 27). Full tables:
[`native/ym/results/2xL/README.md`](native/ym/results/2xL/README.md).

**Gap law, exact to second order in 1/r**
([`native/ym/results/zgap2-2026-10-30-cloud/`](native/ym/results/zgap2-2026-10-30-cloud/README.md)):

E₉ − E₈ = 3r·J_E − c_L·J_E/r + O(1/r²)

| Lattice | c_L |
|---|---|
| 3×3, 3×4, 4×4 | **21**, the same exact value on all three |
| 2×4 | 73/2 |
| 2×3 | 69/2 |
| 2×2 | 36.762472… |

The leading gap is 3·J_B: the lowest excitation above the flat vacua is a single plaquette carrying a
3-cycle. First order adds nothing. At second order, both the vacuum and the excited energies shift in
proportion to the number of links; their difference is local and comes out exactly 21 on every lattice
of width 3 or more (the integer characteristic polynomial of the reduced operator is (x − 84)³ on
3×3, 3×4 and 4×4, over 4). The width-2 lattices differ because virtual electric flips wrap their
short direction. The certified 3×3 values at r = 27, 81 and 243 follow 21 + 43/r. This size-independence
of the gap correction is the locality the BHM/TQO volume-uniform proof, the immediate research track,
builds on. Frozen for the first 3×4 full-space certificate: r·(3r − Δ/J_E) at r = 243 in
[21.095802, 21.573297].

**Checks on the evidence:**
- **Re-execution:** all 224 2×L shards re-run byte for byte.
- **Integrity:** every shard's index and anchor regenerated from its contents.
- **Fresh machines:** the 3×3 certificates were regenerated in 25 GitRAM cells
  with pinned matrix SHA-256s.
- **Two routes to the same counts:** the split-column pipeline reproduces the
  unsplit 2×4 certificate exactly.
- **3×3 full space:** the N-Nest certify tree (depths 0–4) re-executes and checks the
  stage B evidence: 340 of 340 nodes green, 50 of 50 HTTP-0 watcher jobs
  (run 40725530804, erratum 1). Two counts make up the result, 8 levels below t₁ =
  52.533422 and 8 below t_F = 71.9 J_E. They come from the full 10,097,891-dimensional
  space, by Möbius inversion over the translation-line sectors.
- **2×5:** 128 GitRAM cells and 4 strict merges. A seal-only run (40563902487) admitted
  all 132 original artifacts by digest, without recomputing them, and sealed `PASS`.

**3×4 scaling status (October 30, 2026; production HOLD):**

- Dimension check: the streaming pilot reconciled 2,177,317,873 gauge orbits; the
  Sx+Sy+ sector contains 45,508,080 states.
- The **frozen P4 production-memory pilot passed** on main commit `6c34c35`:
  [GitHub Actions run 41053502633](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41053502633).
  Its sealed outcome is `PILOT_OUTCOME|PILOT_PASS|reason=all_gates`. K = 1, 2
  and 4 were admitted with no OOM events; column-zero outputs were byte-identical.
  The pilot-derived bounds under the frozen 12 GiB resident-memory admission model are
  `COL_BYTES=889192448` (measured, above the declared 728,129,280), `RESERVE=2067791872`
  and `CAP=12` = ⌊(12,884,901,888 − 2,067,791,872) / 889,192,448⌋.
- The cgroup `memory.peak` reached the 12 GiB limit at each measured K with no OOM, while
  the frozen admission metric uses RSS/anonymous-memory peaks. Reclaimable file cache is
  the candidate cause; production runtime checks at higher K measure it.
- At thresholds 60M, 72M and 90M, the room-backed and shell implementations
  **AGREE under comparator v2**. At 90M both give the same **AMBIGUOUS outcome
  (negative 37, 9 undecided columns)**.
- **Production stays on HOLD** until the remaining gates pass: the 90M ambiguity,
  binary/source provenance and production admission. The memory pilot gate has passed. See
  [the admission rule](native/ym/results/3x4_stream/PRODUCTION-ADMISSION.md),
  [frozen pilot specification](native/ym/results/3x4_stream/MEMORY-PILOT-SPEC.md),
  and [PR #37: local segmented evidence, unmerged](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/37).
  The admission-rule file carries the pre-pilot HOLD text; the October 30 measured values
  are recorded here and in the pilot receipt.

**Other in progress:** full-space counts on 2×4 through the reflection-only
sectors; a separately written operator and inertia verifier.

### Evidence classes and verification

| Evidence class | What is established | Next |
|---|---|---|
| Exact integer-arithmetic certificates of fixed-lattice spectral-gap bounds (S₃) | 2×L sector results and 3×3 full-space counts with sealed integer receipts and checks | The BHM/TQO volume-uniform proof, the immediate research track |
| 3×4 dimension and memory pilots | 2,177,317,873 reconciled gauge orbits; P4 memory `PILOT_PASS` and `CAP=12` | 90M ambiguity, provenance, production admission, 3×4 gap verdict |
| Cross-seat operator experiments | Replayed software models of reach, curve, hash and CHSH on discrete lattices | A physical z mechanism; a rule that yields the quantum bound 2√2 from the model |
| Production | Memory pilot passed | Remaining production gates |

### z/r/j, prism and Bell software models

Software models of the z/r/j layer on discrete lattices, each with replayed
SHA/HBI/HBP receipts. PASS/FAIL judgments stay as originally registered.

- [zlight (merged acer reference)](native/ym/results/zlight-2026-10-30/):
  the global digest changes at the step the laser fires, while light moves one cell
  per step; the target's own cell changes only when the light arrives.
  [Cloud zlight PR #39](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/39)
  keeps its original P5 FAIL.
- [Per-level r/j (merged acer reference)](native/ym/results/perlevel-2026-10-30/):
  ring-neighbour propagation against hierarchical three-per-level connectivity,
  each with its own metric and schedule.
  [PR #44](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/44)
  holds the independent zlevel, signed zcurve and zbell Rust tests, their registered
  failures, and a workflow that rebuilds each with Rust 1.81 and checks byte identity.
- [CHSH (merged software reference)](native/ym/results/chsh-2026-10-30/):
  Bell-local models stay within `|S|<=2`. A controller that reads both settings, with a
  balanced shared hidden variable, gives `S=4` with both stations' own counts unchanged
  by the far setting. See also [three-seat control PR #47](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/47).
- [Teleportation hierarchy (merged, PR #53)](native/ym/results/zteleport-2026-10-30-cloud/):
  Bell states with Bell-state measurements keep S² = 8 exactly through four teleportation steps;
  PR-box correlations under every local wiring fall to the local bound 2 after one step; a global
  z controller keeps any value. Correlations carried by locally composed resources land on 2√2.
- [Finite-fluid cutoff (zcutoff)](native/ym/results/zcutoff-2026-10-30-cloud/) and
  [transport on the current gates (zcalib)](native/ym/results/zcalib-2026-10-30-cloud/): in the D3Q27
  lattice gas, a swirl driven toward zero core radius at 24³, 48³ and 96³ concentrates (axis vorticity
  681 → 2,011 → 4,078) while its core holds 1/8 of the box, and at 96³ the cells reach the occupancy cap;
  kinematic viscosity 0.44 and 0.43 at two sizes, c_s² = 2/3 exactly.
- [PR #42 destination-pull](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/42),
  [PR #43 three prisms](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/43),
  [PR #48 prism-Bell](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/48)
  and [PR #49 Cantor](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/49)
  are open experiments. Cantor's 16 bands are simulated channels, one per Cantor level;
  all 16 arrive together at step 20. The prism-Bell and Cantor corrections are
  append-only files beside the original sealed records.
- The frustrated-orientation benchmark is local-seat evidence, to be committed with its
  frozen predictions, including the field-only control at 27/27 against frustrated
  optimization at 25/27.

## The theory route

[`docs/YM_TOPOLOGICAL_STABILITY_PROOF.md`](docs/YM_TOPOLOGICAL_STABILITY_PROOF.md),
architecture by Jesse Daniel Brown. On the raw link space the magnetic plaquette
term has the same local ground projector as Kitaev's quantum double D(S₃). Its
eight flat states are the D(S₃) torus ground space. With E as a bounded local
perturbation of strength 6/r per link, the route is topological-order stability
(Bravyi–Hastings–Michalakis, with Cui et al. for the quantum-double TQO
conditions).

**What the theorem gives.** Once its TQO, region, buffer and local-gap
hypotheses are instantiated for this Hamiltonian, it gives r₀ and c > 0 with
E₉ − E₈ ≥ c·J_B, uniformly over growing two-dimensional tori, for r ≥ r₀. It
also gives a band width that shrinks exponentially with torus size.

**What is measured, and what is open.** The finite certificates measure the gap
at r ≥ 9 on each lattice. Two steps are open: completing the instantiation, and
the value of r₀. The document tracks them lemma by lemma.

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
