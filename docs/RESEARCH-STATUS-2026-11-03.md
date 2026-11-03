# Current research and verification status — 2026-11-03

This register is the current entry point for the finite-universe Yang–Mills / HEB-C project. It puts established results first, names their evidence, and separates current work from preserved historical plans.

**Last updated:** November 3, 2026, after [#89](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/89) merged. **Repository inventory baseline:** `8057ce7a2fcb4eea4244bb1245700ef00a5286d2`: 2,352 tracked files, including 85 project Markdown documents and two plan-check HBP receipts, all 85 screened for research status, dated planning statements and editorial framing, with primary proof, code and verification documents read closely. The broader codebase and sealed binary data have distinct execution and audit requirements.

## Today, on one page

**Merged on November 3:**

| PR | What it holds |
|---|---|
| [#84](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/84) | `allpairs`: both count gates must read PASS, with a full 3×4 rerun and the second seat's FAIL on record |
| [#85](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/85) | `allpairs`: D3 to D8 and H1 to H4 fixed, with controls on the old executables, hosted Linux, and full 3×4 runs. The final tool exits 0 in 2,880 s with every predicted field met |
| [#86](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/86) | This register, and GPT-6's metadata checker |
| [#87](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/87) | README links between this repository and the companion, the proof plan and the continuum track |
| [#88](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/88) | The stability plan: the region dictionary and the theorem matching for even square tori, with its correction on δ |
| [#89](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/89) | The bound with no store on 4×4, 4×5 and 5×5, the second seat's and GPT-6's reviews, and `hybridcheck`, the attack on the hybrid certificate |
| [#7](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/7) to [#15](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/15), [#18](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/18) | A separate seat's work from October 25 on the 2×2 torus and the 3×3 flat levels, in [`independent/`](../independent/README.md) |
| [#5](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/5), [#6](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/6) | Stage 2I, the RIME C3 moment test, and Stage 2J, the byte-exact RIME Prism bridge |
| [#16](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/16), [#17](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/17) | The HTTP-0 finite S₃ wave observatory and its correction to exact numerators |
| [#31](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/31) | The 3×3 certify generator's packaging fix |
| [#39](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/39), [#44](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/44), [#42](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/42), [#43](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/43), [#47](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/47) | The cloud seat's zlight, zlevel, zcurve and zbell, one-matrix evidence, three prisms and three-seat CHSH, each with its registered failures kept |

**The numbers to remember, at r = 9:**

| Lattice | E₉ − E₈ ≥ | How | Status |
|---|---:|---|---|
| 3×3 | 23.914694 | The store, every row, pinned `perroncert` and `check_d_strict.py` | Merged earlier |
| 3×4 | 24.039673 | The store, every row, pinned `perroncert`, and a Go checker written by an outside seat | Verdict and rule on HOLD |
| 4×4 | 23.947629 | No store: the hybrid vector with the tighter E₈. E₉ lies between 117.453728 and 117.580284 | Attacked by a separate program on the same model. Another model's attack is open |
| 4×5 | 23.618291 | The same | The same |
| 5×5 | 21.792208 | The same | The same |

The simpler no-store bound under those three reads 16.252744, 14.017195 and 4.016734, and it passed the second seat and GPT-6 at its four points.

**Independent GPT-6 review (November 3, 2026):** a new source-only integer reconstruction separately matched all 1,393 orbit states and 32,385 electric coefficients, the original operator SHA, every entry of the 8×8 magnetic-end effective matrix, its exact characteristic polynomial, full-graph diameter 8, and four translation-sector dimensions. See [the audit](../independent/GPT6_THEOREM_REVIEW_2026-11-03.md) and [pinned output](../independent/gpt6_2x2_from_permutations.measure). The conditional coupling theorems were checked algebraically, but earlier pure-electric spectral-gap certification, translated Sturm pivots, and the 3×3 Ritz trial space are **not new independent receipts** from that audit. Formal 3×4 gap rule still on HOLD.\n\n**Open, in the order I would take them:**

1. GPT-6's attack on the hybrid certificate: all 825,865 low-M states on 4×4, the count of each lump, the Ritz upper values, the 16-dimensional E₈ space. The vectors are on [the release](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/releases/tag/vectors-20261103).
2. The hybrid form at lower r and on 6×6 and larger, to see how far it carries.
3. The finite-size constant r₀ of the stability plan as a number, then odd and rectangular tori.
4. The 2I package in the [companion repository](https://github.com/JesseBrown1980/Finite-Universe-SU-N-solved/pull/9): the exact count at 3 J_E is still running, then the addendum, the driver and the official run.
5. A replay of `fullrebuild` and `allpairs` on another machine, with [`reproduce_oneread_run.sh`](../native/ym/results/3x4_stream/perron/allpairs/oneread/reproduce_oneread_run.sh).
6. A reading of the one-read change to `allpairs` by another seat, and the other tools that still read through `roomio.rs`.
7. A non-author proof review of the separate seat's theorems in [`independent/`](../independent/README.md).
8. A Lean proof of the pattern table and the chain.

**Waiting on the operator:**

| Decision | State |
|---|---|
| The formal 3×4 gap verdict and the gap rule | HOLD, his word. The draft rule is [#68](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/68) |
| The continuum claim | NOT CERTIFIED, his word |
| Closing [#10](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/10) and [#52](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/52) | This session's permission system stopped the closes, so they wait for his word |

**Where the data lives.** Code, receipts, reviews and predictions are in this repository. Files too large for git are on the release [`vectors-20261103`](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/releases/tag/vectors-20261103): `review-opus55-big-files.tar.gz`, sha256 `014344c914a18fa490c66c13b8b6fd84d3a1517d2091f1e2d3fb4570335cf1fc`, the second seat's 34 vectors, and `attack-big-files.tar.gz`, sha256 `10e218cbf81a4f3a2e534e2c7f552b9d35c7fa2a750abcf69f7aee90ebe727c9`, the attack's 9 vectors. Each file inside is hashed in [`review-opus55/BIG-FILES.hbp`](../native/ym/results/3x4_stream/perron/vector/review-opus55/BIG-FILES.hbp) and [`attack/BIG-FILES.hbp`](../native/ym/results/3x4_stream/perron/vector/attack/BIG-FILES.hbp). The 3×4 store is on [Hugging Face](https://huggingface.co/datasets/Jessedbrown/ym-3x4-room-store).

**The older PRs, gone through on November 3 on the operator's word.** Each merged group ran CI on the merged tree, and each group's README and register changes went in with it.

| PRs | Where they stand |
|---|---|
| [#5](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/5) to [#9](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/9), [#11](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/11) to [#18](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/18), [#31](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/31), [#39](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/39), [#42](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/42) to [#44](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/44), [#47](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/47) | Merged |
| [#10](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/10) | Open, to close: its commits are already on `main` |
| [#52](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/52) | Open, to close: its README text is now in the README |
| [#61](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/61) | Open as the record of the floating-point run. The operator's word is to redo it in integers and keep the evidence, and [the integer redo](../native/ym/results/cantor-integer-2026-11-03/README.md) is now on `main`, with that run verbatim beside it |
| [#68](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/68) | Open: the draft gap-verdict rule, on HOLD by the operator's word |

## What the system establishes

| Research area | Established result | Supporting record |
|---|---|---|
| Native implementation | Rust 1.81 finite `S₃` gauge-Hamiltonian kernels, exact integer arithmetic, GitRAM receipts and independent checking pathways | [Main README](../README.md), [native YM README](../native/ym/README.md) |
| Stage 2B | Exact interacting two-plaquette Hamiltonian and finite spectral verification | [Stage 2B](../STAGE2B_DOUBLE_PLAQUETTE_EXACT_SPECTRUM.md) |
| Stage 2C | Periodic 2×2 `S₃` torus with 1,393 gauge-invariant states; certified mixed-coupling eigenvalue intervals | [Stage 2C](../STAGE2C_TORUS_1393_SPARSE_REPORT.md), [spectral certificate](../STAGE2I_INDEPENDENT_VERIFIER_AND_SCALING.md) |
| 2×2, a separate seat | A separate reconstruction with the native operator's SHA-256, all 1,393 Sturm pivots at two couplings, the exact second-order splitting at the magnetic end, and an analytic bound at every ratio | [`independent/`](../independent/README.md) |
| Finite-volume ladder | Certified sector bounds on the 2×L ladder, a full-space 3×3 certificate, and the 3×4 Perron route | [Results table](../README.md#results) |
| 3×4 Perron route | Recorded `t_cert = 94.070673 J_E` at `r=9`; 45,508,080 stored sector rows recomputed; 1,632,625,631 off-diagonal pairs compared; original and count-gate-corrected runs agree apart from elapsed seconds | [Perron bound](../native/ym/results/3x4_stream/perron/PERRON-BOUND.md), [PR #83](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/83), [PR #84](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/84) |
| 3×4 all-sector count | 2,177,317,873 gauge orbits reconciled in the registered pilot | [Pilot decision](../native/ym/results/3x4_stream/PILOT-ADMISSION-DECISION.md) |
| 3×4 production | Control C1–C3 passed and the admitted `t=60M` production run passed with `negative=0`, `ambiguous=0` | [Admission and rule records](../native/ym/results/3x4_stream/GAP-VERDICT-RULE-3X4.md) |

The finite-lattice Perron certificate gives the reported bound
`E₉ − E₈ ≥ 24.039673 J_E` at `r=9`, using the recorded whole-space upper bound `E₈ ≤ 70.031 J_E` and the derived whole-space lift. The corresponding all-`r≥9` expression uses the flat-state upper bound: `E₉ − E₈ ≥ [22.070673 + 3(r−9)] J_E`. The lift is documented in [PERRON-BOUND.md](../native/ym/results/3x4_stream/perron/PERRON-BOUND.md), section 2, and remains a priority for an independently checked derivation.

## Companion finite-group and SU(N) research program

**Verified companion repository:** [Finite-Universe-SU-N-solved](https://github.com/JesseBrown1980/Finite-Universe-SU-N-solved), `main` at `f502321674bc7060f4efbbd86295b54baa8060b3` (checked November 3, 2026). Its [README](https://github.com/JesseBrown1980/Finite-Universe-SU-N-solved/blob/f502321674bc7060f4efbbd86295b54baa8060b3/README.md) and [finite-group laws](https://github.com/JesseBrown1980/Finite-Universe-SU-N-solved/blob/f502321674bc7060f4efbbd86295b54baa8060b3/docs/FINITE_GROUP_LAWS.md) provide the registered results and next-package predictions.

| Track | Recorded achievement | Next milestone |
|---|---|---|
| `S₃` strong-coupling confinement | Static-charge potentials, certified finite-coupling string tensions and Wilson-loop calculations on open strips | Connect finite-volume strong-coupling observables to the relevant large-volume estimates |
| Q8 finite SU(2) subgroup | Exact Wilson-loop series and certified loops; registered W4 FAIL retained | Retest W4 with a preregistered sharper interval or revised observable |
| 2T finite SU(2) subgroup | Exact series and loop checks all PASS on registered cases | Expand geometry and coupling controls |
| 2O finite SU(2) subgroup | Exact series in `Q(√2)` and certified loops on 2×3; registered checks PASS | Complete the predicted 2×4 package |
| 2I finite SU(2) subgroup | Predicted characteristic coefficients and exact orbit dimensions: 296 on open 2×3, 29,288 on open 2×4 | Build and certify the 2I result package |
| Qutrit variational network | Lower/upper energy enclosures for S₃, Q8 and 2T; N4 FAIL preserved | Resolve the registered N4 boundary behavior |
| Continuous SU(2) | A representation-basis `j_max` cutoff with rigorous truncation-error enclosures is specified as a development track | Construct and verify the continuous-group Hamiltonian and its error bounds |
| Four-dimensional SU(N) | [YM continuum track](../native/ym/shadow/CONTINUUM-TRACK.md) specifies renormalization, scale estimates, continuum reconstruction and physical mass-gap milestones | Connect finite-group benchmarks to the separate continuous-group and 3+1-dimensional constructions |

**Two parallel mathematical tracks.** The [finite `S₃` volume-uniform theorem](YM_TOPOLOGICAL_STABILITY_PROOF.md) uses quantum-double stability and extends in principle to other finite-group quantum doubles, with explicit model-specific hypotheses and constants to verify. The companion SU(N) program supplies its own finite-subgroup benchmark series and the planned representation-basis route to continuous SU(2). The [continuum research track](../native/ym/shadow/CONTINUUM-TRACK.md) identifies the four-dimensional renormalization and reconstruction sequence. These tracks share exact arithmetic, GitRAM replay, HBP/HBI evidence and independent-checking methods.

## Independent second-seat review — recorded verdict

**Overall FAIL** on the original `allpairs` implementation at `8faadb0`, reported by Claude Opus 5.5 in [ALLPAIRS-REVIEW.md](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/blob/ad0b56075004021914cc32cefa28185bd2daa178/native/ym/results/3x4_stream/perron/allpairs/failclosed/review-opus55/ALLPAIRS-REVIEW.md). The review awarded PASS to window coverage, pair/mismatch checks and an independently written pair-count reader; it awarded FAIL to **item 2 (malformed input and fail-closed behavior)** and **item 5 (claims exceeding their recorded evidence)**. Its own reader reproduced the 3×4 pair count. The machine, public store copy and model lineage are specified in that report.

**Correction record:** [PR #84](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/84) merged the D1/D2 count-gate fixes and recorded an equal-output full 3×4 rerun. [PR #85](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/85) contains D3–D8 hardening and its adversarial controls. The first hosted D3–D8 run retained a FAIL in its D4 peak-memory measurement, while all 279 predicted program outcomes matched. A small-launcher measurement correction was subsequently committed. The historical FAIL and its exact reproduction stay visible alongside the corrected source and later test outcomes. **Update:** [#85](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/85) merged at `56e0b82`. The controls ran on the old executables and the final one, on this machine and on hosted Linux, and a full 3×4 run on the final tool met every predicted field. Part three of the second seat's review read FAIL on one race and one recipe path, both now fixed, and each finding has a row in [`PERRON-TWO-SIDED.md`](../native/ym/results/3x4_stream/perron/PERRON-TWO-SIDED.md), section 5.

**Verdict categories:** independently observed on hosted tests; separately source-reviewed by GPT-6; metadata-consistency-checked; full-store independently replayed when a separate run supplies that evidence. Each category has its own provenance.

## GPT-6 review-seat checks on the hardening source

**Review type:** independent reading of the implementation plus metadata-only consistency calculations, using copied source values. This section is a source review; the 13-check script reads header constants and computes arithmetic without opening the store. The complete 3×4 stream and full adversarial controls are verified by the separately documented execution tracks. **Execution status:** the standard Rust and cloud-seat CI checks for `9c2c7e6` passed. [Dedicated hosted hardening run 41620803428](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41620803428) completed with `FAIL` overall on a D4 resource-measurement assertion. All 279 precommitted adversarial outcomes, 32,768 header-bit flips, trusted-header reconstruction and 184 judge checks matched their controls. The D4 fixture was created in the Python harness before `os.wait4` sampled child peak RSS; each child inherited the same `ru_maxrss` high-watermark. A separate local reproduction using `/bin/true` and `/proc/<pid>/status` confirmed that measurement effect. A corrected small-launcher D4 memory-control rerun [completed successfully](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41623144494); the hardened full 3×4 replay retains its own execution gate. A local Rust 1.81 build and 26.85 GB-store replay were outside this review seat's available runtime.

| Defect | Source change inspected at `9c2c7e6` | Independent review status |
|---|---|---|
| D3 — trailing payload | `roomscan::scan` reads every declared payload byte and `padding_gate` requires exact room length and zero padding | Source path inspected; hostile-store execution to confirm |
| D4 — padding-related memory | Reader counts padding without retaining it; windows bound entries and row indices | Source path inspected; runtime peak and deliberately oversized padding to confirm |
| D5 — cap reporting | `cap_requested` and effective `cap_entries` have separate fields | Source path inspected; tests to confirm |
| D6 — store identity | The full 4096-byte header SHA-256 and exact line are compared against four pinned trusted headers | Source path inspected; table provenance to confirm |
| D7 — paired-entry accounting | Entry-specific answered bits plus `lower_repeated` and `upper_without_lower` counters enforce one-to-one matching | Source path inspected; duplicate controls to confirm |
| D8 — header authentication | A trusted SHA-256 binds the exact header block, whose payload-merkle field is separately verified during streaming | Source path inspected; external pin and tamper controls to confirm |

**Since that review:** the hostile-store controls, the external pin, the duplicate controls and a full 3×4 rerun all ran, in [`PERRON-TWO-SIDED.md`](../native/ym/results/3x4_stream/perron/PERRON-TWO-SIDED.md), section 5.

The source uses five mandatory `PASS` gates: `header_entries`, `whole_space_count`, `header_rooms`, `padding` and `store_identity`. The replay script uses `set -euo pipefail` and the judge checks original-output hash, output fields, process exit, standard error and executable SHA-256.

**Independent arithmetic and hash checks on the public source values:**

- `3,310,759,342 = 45,508,080 + 2 × 1,632,625,631` (entries, diagonals, off-diagonal pairs).
- `6¹³ = 13,060,694,016` (reported sum of orbit weights).
- `94.070673 − 70.031000 = 24.039673`; `94.070673 − 72.000000 = 22.070673` (reported finite-lattice gap formulas).
- Independently SHA-256-hashing the exact `3×4` header line plus newline and zero-padding to 4,096 bytes reproduces `65dd63a89d7e1a7cdd3e7876c834c6698a01081ea7a63738e305890bee9e6a21`.

These checks establish internal consistency and one trusted header commitment. The [separately written Python metadata consistency checker](../native/ym/independent/gpt6_3x4_meta_check.py) reproduces 13 copied-header and arithmetic assertions (`META_CHECK_DONE|checks=13|failed=0`). They detect transcription inconsistencies within the supplied constants, including a header-block hash mismatch. The script derives its inputs from a copied header string and fixed numbers, and reads zero stored-row bytes. Run it with `python3 -I native/ym/independent/gpt6_3x4_meta_check.py`. Full-stream equality requires a fresh independently executed stream reader.

**Review recommendations:** use a clean pinned checkout for replay, reject untracked build inputs, record the actual executable hash from outside the process, retain the run log and its own immutable artifact digest, and expose judge exit status even through `tee`. A parse of a copied output proves transcript consistency; a source-built replay and authenticated CI evidence establish execution.

## Current research milestones

1. **Hardening:** done in [#85](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/85), with every FAIL receipt kept. Next here: a reading of the one-read change by another seat, and the other tools that still read through `roomio.rs`.
2. **3×4 reproducibility:** replay `allpairs` and `fullrebuild` on a separate machine with pinned source and independently fetched sectors. Retain the outside Go checker's own pair test as a separate verification track.
3. **Formal 3×4 gap rule:** complete independent review of the whole-space lift, register the revised rule after operator approval, then issue a specifically scoped finite-lattice verdict.
4. **Volume-uniform finite-group theorem:** instantiate quantum-double stability for the periodic `S₃` model, then test the appropriate theorem hypotheses and constants for Q8, 2T, 2O and 2I.
5. **SU(N) companion program:** continue [Finite-Universe-SU-N-solved](https://github.com/JesseBrown1980/Finite-Universe-SU-N-solved), beginning with 2I and 2O 2×4 certificates, then the continuous-SU(2) `j_max` representation basis with rigorous truncation bounds and 3+1-dimensional gauge Hamiltonians.
6. **Four-dimensional continuum:** use the [existing continuum track](../native/ym/shadow/CONTINUUM-TRACK.md) for renormalization and uniform cross-scale estimates, continuum reconstruction and the physical Yang–Mills mass-gap theorem.

## Historical documents and present reading order

The following files preserve dated decisions and pre-registered test protocols:

- [October 24 implementation plan](../HEBC_HTTP0_HEADLESS_YANG_MILLS_PLAN.md): first read its November 1 addendum and this register; Stage 2B, Stage 2C and later finite-lattice results have advanced since its original milestones.
- [Clasy-to-YM hurdle list](../CLASY_X3_TO_HEBC_HTTP0_NEXT_HURDLES.md): the original ordered hurdles document the development sequence; the completed two-plaquette and 2×2 torus stages now appear above as achieved results.
- [3×4 first pilot](../native/ym/results/3x4_stream/PILOT-ADMISSION-DECISION.md), [memory admission](../native/ym/results/3x4_stream/PRODUCTION-ADMISSION.md) and [early room-backed run log](../native/ym/results/3x4_room_backed/RUN-LOG.md): preserve their dated HOLD and IN PROGRESS decisions. Later 60M production and full-row evidence are recorded in the newer stream/Perron records.
- [Registered 60M rule](../native/ym/results/3x4_stream/GAP-VERDICT-RULE-3X4.md) and [Perron gap-rule draft](../native/ym/results/3x4_stream/perron/PERRON-RULE-DRAFT.md): separate workflows and approval gates.

**Editorial rule for current summaries:** lead with the mathematical object, measured achievement, certificate and source. The independent-review label for this seat is **GPT-6**; the second-seat reviewer is **Claude Opus 5.5**, with its original FAIL recorded above. Name open proof or replay tasks as positive next actions. Keep archived FAIL/INCONCLUSIVE receipts, formal assumptions, and mathematical counterexamples verbatim as part of the scientific record.
