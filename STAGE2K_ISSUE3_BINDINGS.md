# Stage 2K — Issue #3: C1, instant, z, Z-instant and the §71.5 residual on the 1,393-state torus

**Date:** 2026-11-06. **Code:** `native/src/issue3_bindings.rs`. **Evidence:** `native/ym/results/issue3-bindings-20261106/`.
**Frozen prediction:** `PREDICTION-ISSUE3.hbp`, SHA-256 `cf9c22657c16098e1d19aa0ce5a7a352242cd6d1578e0746409bbede31698a17`, committed alone before any code.

This stage answers issue #3 binding by binding. Each verdict is one of **BOUND** (with the exact test), **BOUND_IN_KERNEL_ONLY**, or **UNBOUND** (with the reason). The checks call the functions already in this crate: `torus2::{Torus2, gauge_transform, plaquette}`, `shadow_residual::{inspect, canonical_pair, winding_rotation}`, `rime_hamiltonian_bridge::inspect`, `rime_gear::{freeze, validate_snapshot, mediated_call}`, the vendored Clasy `trit::Trit` and `lib::{PERM, character, mul, inv}`. Three private helpers were made `pub(crate)` so the new module can call them; their bodies are unchanged. Integer arithmetic only.

## Sources, pinned

All three source repositories were read as data, and their code was read only. Full rows: `SOURCE-PINS.hbp`.

| Term | Repository @ commit | File, blob, line | Text |
|---|---|---|---|
| z | the-human-based-understanding @ `f38cfec0` | README.md `a442f743`, l.70 | "the wave SQUARED. Binary. The inversion. 'your z is my s'" |
| z, the rule | the-zebras-z-is-the-squared-wave @ `3b3fe023` (linked from HBU index.html l.423) | index.html `bbf68650`, l.95–100 | `SQUARE ? (w >= 0 ? 1 : 0)`: z is the square wave cut from the smooth sine s, same frequency and phase, two values |
| c, r, j | HBU @ `f38cfec0` | README.md l.41, 62, 51 | c "the speed of 1"; r "the radius… straight there, bidirectionally"; j "the reverse of the radius… curved" |
| Law 4 | HBU @ `f38cfec0` | README.md l.357; RECORD.md l.64 | "Instant is not always instant — it is instant PER LEVEL, three per level." |
| 0 = INSTANT | ASOLARIA-UNIVERSE-SIMULATOR @ `3f9f42da` | LAW-71 `24e5e883`, l.63 | `0 = FROZEN FREE IS = BLACK = INSTANT` |
| instant, kernel | SIM @ `3f9f42da` | LAW-71 l.322–327 | one atomic logical play/freeze transaction; no WAS–WILL edge bypasses IS; the physical reading is `UNVERIFIED_PHYSICS` |
| C0, C1, C2 | SIM @ `3f9f42da` | LAW-71 l.341–344 | `C0=(-,.,+)_BLACK`, `C1=R(C0)=ANTI`, `C2=R²(C0)`, `R³(C0)=C0` |
| R, the trianti | SIM @ `3f9f42da` | crates/asolaria-tribit/src/tribit.rs `9a27567d`, l.112–124 | `rotate = from_digit(digit + 1)`, order three, `R ≠ R²` |
| §71.5 residual | SIM @ `3f9f42da` | LAW-71 l.150–161 | `||v − P_S v|| / ||v||`, `P_S` the projection onto the rank-two span of three arms summing to zero |
| the arms | SIM @ `3f9f42da` | LAW-62 `259e452c`, l.47–49 | three arms sum to zero, span rank two; the arms are set per body |

## Verdicts

| # | Binding | Verdict | Test (in `issue3_bindings::tests`) |
|---|---|---|---|
| 1 | C1 = R(C0) on the flat S3 torus classes | **BOUND** on the 8 flat classes | `c1_is_the_flat_winding_up_to_three_base_points_per_cycle` |
| 2 | R extended to the 1,393 physical states | **UNBOUND** | `r_has_no_lattice_or_commuting_extension_on_1393` |
| 3 | instant = one atomic freeze, three per level | **BOUND_IN_KERNEL_ONLY** | `instant_is_one_freeze_per_level_with_three_equal_views` |
| 4 | z = the two-valued square wave | **UNBOUND** | `z_square_wave_is_gauge_invariant_and_loses_the_magnetic_energy` |
| 5 | the joined term "Z-instant" | **UNBOUND**: undefined in source | `SOURCE-SEARCH.hbp` |
| 6 | §71.5 residual against the S3 Wilson observable | **BOUND**: the arm plane carries the Wilson loop, the residual is the trivial representation | `residual_is_trivial_rep_and_arm_plane_trace_is_the_wilson_magnetic`, control `plane_magnetic_disagrees_when_a_plaquette_is_misread` |

### 1. C1 — BOUND on the flat moduli (MEASURED)

The source R, `from_digit(digit + 1)`, applied entrywise to `C0 = (−,·,+)` gives `C1 = (·,+,−)`, `C2 = (+,−,·)` and `C3 = C0`. Of the 27 trit triples, 0 are fixed, so R acts freely with order three. On the eight flat classes, `winding_rotation` gives 2 fixed classes and two 3-cycles, the same counts `shadow_residual::inspect` reports. Each 3-cycle is isomorphic to `{C0, C1, C2}` as a C3-set, with exactly 3 equivariant bijections per cycle. Those 3 are the choice of which flat class plays C0, a choice the source leaves free. The binding covers the 6 moving flat classes; the 2 fixed classes lie outside the source's single free 3-cycle. `constellation_gate::C1_FLAT_WINDING_BOUND = true` follows this test, and `C1_CONNECTED` stays `false` for the 1,393 states.

### 2. R on the 1,393 states — UNBOUND (MEASURED)

- The cellular automorphism group of the periodic 2×2 lattice has **32** elements, read off the existing `gauge_transform` (incidence) and `plaquette` (faces), and **0** of them have order divisible by three. Every lattice symmetry has 2-power order, so R is a mapping-class action on the flat moduli, induced by no lattice symmetry.
- The Stage 2I witness reproduces: the H_E fourth moments of flat orbits 271 and 276, which R relates, differ by **408**. Any W-unitary map that sends flat basis states to their R-images fails to commute with H_E.
- The formula `(x, y) → (y⁻¹, x y⁻¹)` is conjugation-equivariant with `R³ = id` on all 36 S3 pairs, commuting or not. The pair class `(q0, q2)` takes **11** values on the 1,393 states, with up to **216** states per class. The pair leaves the other three loop variables unassigned, and a lift of R to them is open in the sources.

### 3. Instant — BOUND_IN_KERNEL_ONLY (MEASURED)

`rime_gear::freeze` is the kernel's play/freeze transaction. One call commits the input hash and all three views to one `frozen_sha`. Three sequential levels (revisions 0, 1, 2) each give 3 equal views, the three frozen hashes are distinct, and re-freezing level 0 reproduces it byte for byte. `mediated_call(WAS, WILL) = false` in both directions. A forged view, an emptied view and input arriving after its play epoch are each rejected. This matches the source text at LAW-71 l.322 and Law 4's "three per level". The binding's scope is the kernel transaction; the torus gauge observables sit outside it, and the source itself keeps the physical reading at `UNVERIFIED_PHYSICS`.

### 4. z — UNBOUND (MEASURED)

The source fixes the quantizer: z is the sign threshold `w ≥ 0 → 1, else 0` of a smooth wave s. Applied to the S3 Wilson character (2, 0, −1), z takes **2** values and is gauge invariant (33,432 gauge checks, 1,393 states × 4 sites × 6 elements). Arithmetic squaring χ² takes **3** values, so the source's "squared" is the square wave, and arithmetic squaring gives a different observable. The plaquette sum Σ_p z(χ(U_p)) takes 5 values, and states 0 and 1 share the sum 4 with H_B = 0 and 4: the sum loses the magnetic energy. Which lattice wave z acts on is open in the sources, so z stays UNBOUND.

### 5. "Z-instant" — UNBOUND, undefined in source (MEASURED)

`git grep -i -E 'z[-_ ]?instant'` at the three pinned commits gives 0 hits in 3 + 943 + 2 files, and recall `:4796` gives `count=0`. In this repository the term first appears in issue #3 and `STAGE2D`. Its two halves are separately sourced: z in row 4, instant in row 3. A rule joining them is open.

### 6. §71.5 residual and the Wilson loop — BOUND (MEASURED)

With the arms `3e_i − (1,1,1)` = (2,−1,−1), (−1,2,−1), (−1,−1,2), which sum to zero and have normal (3,3,3), `3P_S = 3I − J` is integer. The arm choice is this stage's own: it is the S3 permutation triad. LAW-62 sets arms per body.

- The permutation matrices of `PERM` form a homomorphism (36/36 products).
- `tr(3P_S · M_g) = 3·character(g)` for **6/6** group elements: the Wilson character in the standard representation is the trace on the §71.5 plane.
- `Σ_p (2 − tr(P_S M_{U_p}))` equals the native `H_B` on **1,393/1,393** states and is gauge invariant (33,432 checks).
- The §71.5 residual is invariant under every permutation (744 checks). Transported by the x-holonomy of each of the 1,393 states, the probe (1,2,4) has **1** residual value, while the plane trace takes 3. The residual line is the trivial representation and is constant over the gauge field.
- `Torus2::electric_gap_witness` passes: the plane-trace Wilson loop is the exact E = 6 electric eigenvector.
- Negative control: replacing one plaquette's plane trace by the residual line's trace breaks the H_B match.

This is an exact gauge-invariant observable map. It reproduces the actual magnetic operator diagonal and the existing electric witness. The certified gaps stay in their own stages (2G, 2H); this stage records `spectral_gap_inference=NONE`.

## Prediction against result

Rows as frozen in `PREDICTION-ISSUE3.hbp`; each MET or MISS stays as it read.

| # | Predicted | Measured | Status |
|---|---|---|---|
| 1 | fixed=2, cycles3=2, 0 fixed tuples, 3 bijections per cycle; BOUND_FLAT_ONLY | 2, 2, 0, (3,3); row label `BOUND` with `scope=FLAT_8_ONLY` | MET on content; the label's scope is written in the row's scope field |
| 2 | 2-power automorphism order, 0 order-3; gap 408; equivariant, R³=id on 36; pair class non-injective; UNBOUND | 32, 0; 408; 1, 1; 11 classes, max fiber 216; UNBOUND | MET |
| 3 | equal views, WAS–WILL absent, 3 levels distinct, earlier unchanged, forged rejected; BOUND_IN_KERNEL_ONLY | all as predicted, plus missing-view and unarrived-input rejection | MET |
| 4 | z 2 values, χ² 3 values, z-sum fails to determine H_B; UNBOUND | 2, 3, alias (0,1) at sum 4; UNBOUND | MET |
| 5 | 0 hits in pinned sources, recall count 0; verdict UNDEFINED_IN_SOURCE | 0, 0; row label `UNBOUND` with `reason=UNDEFINED_IN_SOURCE` | MET on content; the label is written in the row's reason field |
| 6 | 6/6 trace match, residual invariant, 1,393/1,393 magnetic, 1 residual value, witness passes; BOUND_PLANE_IS_WILSON_RESIDUAL_IS_TRIVIAL_REP | 6/6, 744/744, 1,393/1,393, 1, pass; row label `BOUND` with `residual_rep=TRIVIAL` | MET on content; the arm-plane trace reproduces the Wilson character H_B, the residual is the trivial invariant, `spectral_gap_inference=NONE`, physical `instant=UNVERIFIED_PHYSICS` |

Disclosure: rows 4 and 5 were written after reading the sources. The z rule (row 4) and the first Z-instant searches over HBU and SIM (row 5) were seen before the prediction was frozen. Rows 1, 2, 3 and 6 predicted computations that had not been run.

## Issue #3 acceptance criteria

1. **Sources and blobs:** `SOURCE-PINS.hbp`, with original notation kept.
2. **Rust 1.81 adapter:** `issue3_bindings.rs` calls this repository's own functions (`rime_gear`, `shadow_residual`, `torus2`) and the vendored Clasy `Trit`, and re-expresses R from its pinned rule (see the scope section below). Clippy `-D warnings` is clean; the code is Rust only, json=0. The source trianti R lives in the simulator crate, which this stage reads as data. Its one-line rule runs over the vendored Clasy `Trit` (row 1).
3. **Three connected tori / nine branches:** a residual rule for three tori is open in the sources, so this test is held. `rime_gear`'s WAS/IS/WILL roles are the three-role topology present, tested in row 3. The 1/6 observer and 5/6 complement remain Law 70 NO-CALL quantities, tested in Stage 2E.
4. **Negative controls:** missing view, forged view (disagreement), unarrived input, gauge transformations on all 1,393 states, the plaquette-misread control and receipt tampering.
5. **Yang–Mills map:** row 6 is an explicit gauge-invariant map that reproduces H_B exactly and carries the E = 6 electric witness, computed on the operator itself.
6. **HBI/HBP/SHA/SH/HASH:** `evidence/run.hbp` (6 chained rows), `index.hbi`, `run.anchor`, `run.measure`, `SHA256SUMS`. `issue3-verify` rebuilds everything and compares bytes.
7. **Statuses:** C1 on the 1,393 states, z, Z-instant and the physical instant stay UNVERIFIED/UNBOUND as listed.

## Reproduce

```sh
cd native
cargo +1.81.0 test --all-targets --locked --offline issue3
cargo +1.81.0 clippy --all-targets --locked --offline -- -D warnings
cargo +1.81.0 build --release --locked --offline
target/release/hebc issue3-audit issue3-evidence
target/release/hebc issue3-verify issue3-evidence
cmp issue3-evidence/run.hbp ym/results/issue3-bindings-20261106/evidence/run.hbp
```

Scope: a finite S3 lattice on a 2×2 periodic torus. The continuum four-dimensional question is a separate one.

## Scope of the original-function check, and where the open items went

- **R is re-expressed, not called.** The rotation is written as one line over the vendored Clasy `Trit`, from its pinned source rule: the simulator's `tribit.rs` lines 116–118, blob 9a27567d. The simulator's own function is not compiled or called here. Vendoring `tribit.rs` byte for byte through `#[path]`, with the same tests, is item 4 of #120.
- **#120 holds the rest of #3:** three tori with nine branches; "Z-instant" as one operator; R on all 1,393 states; that original-function call; and the LAW-036 recall lead. Each is OPEN there.
