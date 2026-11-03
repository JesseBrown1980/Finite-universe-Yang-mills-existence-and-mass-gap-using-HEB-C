# Current research and verification status — 2026-11-03

This register is the current entry point for the finite-universe Yang–Mills / HEB-C project. It puts established results first, names their evidence, and separates current work from preserved historical plans.

**Current main:** `ad0b56075004021914cc32cefa28185bd2daa178` (PR #84 merged). **Repository inventory baseline:** `8057ce7a2fcb4eea4244bb1245700ef00a5286d2` (PR #83 merged). **Hardening review:** source inspection pinned at `9c2c7e67e29e0b2450010bd43c3391638e6670eb`; [PR #85](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/85) subsequently advanced to `0c04ec02e6769539dbf8739242e2d2ff9eeb5272` (last checked 2026-11-03). The current PR head is linked from GitHub; new commits require their own review. The repository tree contains 2,352 tracked files, including 85 project Markdown documents and two plan-check HBP receipts. All 85 Markdown documents were screened for research status, dated planning statements and editorial framing; primary proof, code and verification documents received focused review. The broader codebase and sealed binary data have distinct execution and audit requirements.

## What the system establishes

| Research area | Established result | Supporting record |
|---|---|---|
| Native implementation | Rust 1.81 finite `S₃` gauge-Hamiltonian kernels, exact integer arithmetic, GitRAM receipts and independent checking pathways | [Main README](../README.md), [native YM README](../native/ym/README.md) |
| Stage 2B | Exact interacting two-plaquette Hamiltonian and finite spectral verification | [Stage 2B](../STAGE2B_DOUBLE_PLAQUETTE_EXACT_SPECTRUM.md) |
| Stage 2C | Periodic 2×2 `S₃` torus with 1,393 gauge-invariant states; certified mixed-coupling eigenvalue intervals | [Stage 2C](../STAGE2C_TORUS_1393_SPARSE_REPORT.md), [spectral certificate](../STAGE2I_INDEPENDENT_VERIFIER_AND_SCALING.md) |
| Finite-volume ladder | Certified sector bounds on the 2×L ladder, a full-space 3×3 certificate, and the 3×4 Perron route | [Results table](../README.md#results) |
| 3×4 Perron route | Recorded `t_cert = 94.070673 J_E` at `r=9`; 45,508,080 stored sector rows recomputed; 1,632,625,631 off-diagonal pairs compared; original and count-gate-corrected runs agree apart from elapsed seconds | [Perron bound](../native/ym/results/3x4_stream/perron/PERRON-BOUND.md), [PR #83](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/83), [PR #84](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/84) |
| 3×4 all-sector count | 2,177,317,873 gauge orbits reconciled in the registered pilot | [Pilot decision](../native/ym/results/3x4_stream/PILOT-ADMISSION-DECISION.md) |
| 3×4 production | Control C1–C3 passed and the admitted `t=60M` production run passed with `negative=0`, `ambiguous=0` | [Admission and rule records](../native/ym/results/3x4_stream/GAP-VERDICT-RULE-3X4.md) |

The finite-lattice Perron certificate gives the reported bound
`E₉ − E₈ ≥ 24.039673 J_E` at `r=9`, using the recorded whole-space upper bound `E₈ ≤ 70.031 J_E` and the derived whole-space lift. The corresponding all-`r≥9` expression uses the flat-state upper bound: `E₉ − E₈ ≥ [22.070673 + 3(r−9)] J_E`. The lift is documented in [PERRON-BOUND.md](../native/ym/results/3x4_stream/perron/PERRON-BOUND.md), section 2, and remains a priority for an independently checked derivation.

## Independent second-seat review — recorded verdict

**Overall FAIL** on the original `allpairs` implementation at `8faadb0`, reported by Claude Opus 5.5 in [ALLPAIRS-REVIEW.md](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/blob/ad0b56075004021914cc32cefa28185bd2daa178/native/ym/results/3x4_stream/perron/allpairs/failclosed/review-opus55/ALLPAIRS-REVIEW.md). The review awarded PASS to window coverage, pair/mismatch checks and an independently written pair-count reader; it awarded FAIL to **item 2 (malformed input and fail-closed behavior)** and **item 5 (claims exceeding their recorded evidence)**. Its own reader reproduced the 3×4 pair count. The machine, public store copy and model lineage are specified in that report.

**Correction record:** [PR #84](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/84) merged the D1/D2 count-gate fixes and recorded an equal-output full 3×4 rerun. [PR #85](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/85) contains D3–D8 hardening and its adversarial controls. The first hosted D3–D8 run retained a FAIL in its D4 peak-memory measurement, while all 279 predicted program outcomes matched. A small-launcher measurement correction was subsequently committed. The historical FAIL and its exact reproduction stay visible alongside the corrected source and later test outcomes.

**Verdict categories:** independently observed on hosted tests; separately source-reviewed by GPT-6; metadata-consistency-checked; full-store independently replayed when a separate run supplies that evidence. Each category has its own provenance.

## GPT-6 review-seat checks on the hardening source

**Review type:** independent reading of the implementation plus metadata-only consistency calculations, using copied source values. This section is a source review; the 13-check script reads header constants and computes arithmetic without opening the store. The complete 3×4 stream and full adversarial controls are verified by the separately documented execution tracks. **Execution status:** the standard Rust and cloud-seat CI checks for `9c2c7e6` passed. [Dedicated hosted hardening run 41620803428](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41620803428) completed with `FAIL` overall on a D4 resource-measurement assertion. All 279 precommitted adversarial outcomes, 32,768 header-bit flips, trusted-header reconstruction and 184 judge checks matched their controls. The D4 fixture was created in the Python harness before `os.wait4` sampled child peak RSS; each child inherited the same `ru_maxrss` high-watermark. A separate local reproduction using `/bin/true` and `/proc/<pid>/status` confirmed that measurement effect. A clean-process D4 memory measurement and the hardened full 3×4 replay are the next execution gates. A local Rust 1.81 build and 26.85 GB-store replay were outside this review seat's available runtime.

| Defect | Source change inspected at `9c2c7e6` | Independent review status |
|---|---|---|
| D3 — trailing payload | `roomscan::scan` reads every declared payload byte and `padding_gate` requires exact room length and zero padding | Source path inspected; hostile-store execution to confirm |
| D4 — padding-related memory | Reader counts padding without retaining it; windows bound entries and row indices | Source path inspected; runtime peak and deliberately oversized padding to confirm |
| D5 — cap reporting | `cap_requested` and effective `cap_entries` have separate fields | Source path inspected; tests to confirm |
| D6 — store identity | The full 4096-byte header SHA-256 and exact line are compared against four pinned trusted headers | Source path inspected; table provenance to confirm |
| D7 — paired-entry accounting | Entry-specific answered bits plus `lower_repeated` and `upper_without_lower` counters enforce one-to-one matching | Source path inspected; duplicate controls to confirm |
| D8 — header authentication | A trusted SHA-256 binds the exact header block, whose payload-merkle field is separately verified during streaming | Source path inspected; external pin and tamper controls to confirm |

The source uses five mandatory `PASS` gates: `header_entries`, `whole_space_count`, `header_rooms`, `padding` and `store_identity`. The replay script uses `set -euo pipefail` and the judge checks original-output hash, output fields, process exit, standard error and executable SHA-256.

**Independent arithmetic and hash checks on the public source values:**

- `3,310,759,342 = 45,508,080 + 2 × 1,632,625,631` (entries, diagonals, off-diagonal pairs).
- `6¹³ = 13,060,694,016` (reported sum of orbit weights).
- `94.070673 − 70.031000 = 24.039673`; `94.070673 − 72.000000 = 22.070673` (reported finite-lattice gap formulas).
- Independently SHA-256-hashing the exact `3×4` header line plus newline and zero-padding to 4,096 bytes reproduces `65dd63a89d7e1a7cdd3e7876c834c6698a01081ea7a63738e305890bee9e6a21`.

These checks establish internal consistency and one trusted header commitment. The [separately written Python metadata consistency checker](../native/ym/independent/gpt6_3x4_meta_check.py) reproduces 13 copied-header and arithmetic assertions (`META_CHECK_DONE|checks=13|failed=0`). They detect transcription inconsistencies within the supplied constants, including a header-block hash mismatch. The script derives its inputs from a copied header string and fixed numbers, and reads zero stored-row bytes. Run it with `python3 -I native/ym/independent/gpt6_3x4_meta_check.py`. Full-stream equality requires a fresh independently executed stream reader.

**Review recommendations:** use a clean pinned checkout for replay, reject untracked build inputs, record the actual executable hash from outside the process, retain the run log and its own immutable artifact digest, and expose judge exit status even through `tee`. A parse of a copied output proves transcript consistency; a source-built replay and authenticated CI evidence establish execution.

## Current research milestones

1. **Hardening:** complete the corrected D4 memory measurement and independent review of the evolving D3–D8 branch, preserving every FAIL receipt. [PR #85](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/85) was last checked at `0c04ec0` and retains its own merge gate. The GPT-6 source inspection remains pinned to `9c2c7e6`.
2. **3×4 reproducibility:** replay `allpairs` and `fullrebuild` on a separate machine with pinned source and independently fetched sectors. Retain the outside Go checker's own pair test as a separate verification track.
3. **Formal 3×4 gap rule:** complete independent review of the whole-space lift, register the revised rule after operator approval, then issue a specifically scoped finite-lattice verdict.
4. **Volume and continuum:** establish estimates uniform in lattice volume and construct the continuum theory satisfying the required axioms; connect the spectral lower bound to the continuum mass-gap statement.

## Historical documents and present reading order

The following files preserve dated decisions and pre-registered test protocols:

- [October 24 implementation plan](../HEBC_HTTP0_HEADLESS_YANG_MILLS_PLAN.md): first read its November 1 addendum and this register; Stage 2B, Stage 2C and later finite-lattice results have advanced since its original milestones.
- [Clasy-to-YM hurdle list](../CLASY_X3_TO_HEBC_HTTP0_NEXT_HURDLES.md): the original ordered hurdles document the development sequence; the completed two-plaquette and 2×2 torus stages now appear above as achieved results.
- [3×4 first pilot](../native/ym/results/3x4_stream/PILOT-ADMISSION-DECISION.md), [memory admission](../native/ym/results/3x4_stream/PRODUCTION-ADMISSION.md) and [early room-backed run log](../native/ym/results/3x4_room_backed/RUN-LOG.md): preserve their dated HOLD and IN PROGRESS decisions. Later 60M production and full-row evidence are recorded in the newer stream/Perron records.
- [Registered 60M rule](../native/ym/results/3x4_stream/GAP-VERDICT-RULE-3X4.md) and [Perron gap-rule draft](../native/ym/results/3x4_stream/perron/PERRON-RULE-DRAFT.md): separate workflows and approval gates.

**Editorial rule for current summaries:** lead with the mathematical object, measured achievement, certificate and source. The independent-review label for this seat is **GPT-6**; the second-seat reviewer is **Claude Opus 5.5**, with its original FAIL recorded above. Name open proof or replay tasks as positive next actions. Keep archived FAIL/INCONCLUSIVE receipts, formal assumptions, and mathematical counterexamples verbatim as part of the scientific record.
