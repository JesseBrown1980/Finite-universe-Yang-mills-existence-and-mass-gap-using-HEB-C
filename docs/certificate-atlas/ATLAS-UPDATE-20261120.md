# Certificate Atlas refresh — full repository inventory and November 17–20 update

**Snapshot audit:** complete recursive current-`main` Git tree at `3180c0111a3123d9c605eba79c22942bc4f1824c`, **5,966 entries; not truncated**. Original certificate-atlas PR [#267](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/267) merged 17 November 2026; its dataset had **80 source-linked records** (39 gap, 15 spectrum, 26 algorithm) pinned to original README commit `98c39fbaa1e6ecf9e6454062e90801f385356063`.

## Full-scope change audit

The GitHub pull-request collection was enumerated after atlas #267 through #345 inclusive, preserving all **77** later entries even when their findings are research drafts, auxiliary work, documentation, or unmerged proposals. Outcome at the audit snapshot: **35 merged, 40 open, 2 closed without merge**. The manifest `certificates-current-20261120.json` contains exact PR numbers, titles, URLs, timestamps, development status and category for all 77; a PR number or merged documentation is **not itself a certificate of a new theorem**.

The project tree at the snapshot has 1,197 `.hbp` files and 207 tracked files under `independent/y137-...`, plus original finite-model Rust and audit files. Reading every file and independently replaying every large hosted computation is beyond the scope of this atlas refresh; the review **inventoried the entire tree and PR history**, then inspected the source-connected theorem, numerical, and workflow evidence for the new atlas entries. The original immutable data/producing executables are not rewritten by this visualization.

## Reconciled certificate inventory

| Record set | Baseline November 17 | New evidence layer | Meaning |
| --- | ---: | ---: | --- |
| High-cluster gap measurements | 39 | 1 revalidation overlay | Same 3×4 `r=9` bound 24.039673, now signed whole-Q lift in #345; **not** a second independent physical gap measurement |
| Physical / Ritz spectral values | 15 | 3 revalidation overlays | Same full-physical E₁, E₂ intervals and 94.070673 whole-Q floor, with additional independent provenance |
| Computational / theorem milestones | 26 | 24 | New distinct source-work, proof, audit and SAT benchmark records; **mixed work units** |
| Wilson proof-chain map | prior Stage N diagnostic | 25 nodes including baseline | PR-linked chain showing mathematical acceptance status, source-conditional steps and final Wilson HOLD |
| Exact Wilson bounds | original first-moment HOLD | 7 quantitative bounds / source-conditional refinements | Strict conditional candidate `451/10^12` improved to `17074763/10^12`; actual first Wilson **FORMAL HOLD** |
| PR lifecycle ledger | PR #267 baseline | 77 | Exhaustive post-atlas history; 35 merged, 40 open, 2 closed-unmerged |

**Unique old + new algorithm/method records:** 26 + 24 = **50**. The single revalidation overlays for gap and spectra retain their pre-existing physical values; count them as **provenance** rather than new spectral observations. The 25 Wilson chain nodes include one old Stage N diagnostic and 24 subsequent research/proof milestones, which are distinct from the 24 algorithm records and **must not be summed as unrelated physical measurements**.

## Major new source-authenticated and mathematical receipts

- Original 3×4 physical P/Q, W-adjoint, eight flat orbits, all 576 outgoing flat transitions and 264 nonflat boundary orbits independently accepted: [#341](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/341).
- Original finite 45,508,080-row spatial-sector Perron data and 34-file **composite** input integrity: [#332](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/332). The source includes seven flats; 45,508,073 nonflat quotient rows receive the strict positive witness.
- Whole 2,177,317,865-state nonflat Q mathematical weighted-sum-of-squares lift, with verified threshold `QHQ >= 94.070673 J_E` conditional on the already accepted original comparison data: [#345](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/345), merged November 20 at `3180c0111a3123d9c605eba79c22942bc4f1824c`.
- Full K3/Q4 signed source 34,249,536 components, Q5 extended 18,598,040 states and 331,818,176 combined source values: [#331](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/331), [#335](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/335). Separate whole signed third moment for 20,738,636 states, two original energies, 128/128 matrix entries: [#330](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/330), [hosted #44581486671](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/44581486671). Cross-block pair audit: [#329](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/329), 139,517,148 pairs.
- Exact full-matrix signed localizer / Gauss–Lobatto bounds: [#338](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/338). Physical W-weighted source-to-Schur identity and `G0=6 mu0` normalization: [#343](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/343).
- True-energy E₁/E₂ conditional projector sine ceilings `0.002034354058`, `0.004260581813`: [research #319](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/319). Exact Wilson normalized transfer: [#337](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/337), conditionally positive squared original first-weight lower `17,074,763/10^12`. The original matched action/projector primary source acceptance is pending, and the first Wilson result retains **FORMAL HOLD**.
- The [#302](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/302) 21-case SAT benchmark is displayed as an **auxiliary algorithmic check**, not as a Yang–Mills spectral eigenvalue or physics certificate.

## Graph descriptions and safety checks

The [new offline combined 3D viewer](atlas-current-20261120.html) has **four modes and three precomputed camera angles**. It is SVG/CSS-only, with no JavaScript, external network calls or runtime floating-point arithmetic. Click points for direct evidence.

1. **Gap landscape:** physical size × log coupling × high-cluster gap lower divided by coupling. A triangle denotes a **lower bound**; other points may be certified intervals. The November 20 validation overlays, without moving, the original `3×4 r=9` coordinate.
2. **Spectral scatter:** log support dimension × energy index × energy in J_E. Source-conditional full-physical and Ritz/trial quantities are labeled separately; the new physical E₁/E₂ and Q floor overlays keep their exact old values.
3. **Algorithm evidence:** log support × log reported work/check count × operation category. Units include rows, moves, entries and tests: this is **not** a homogeneous complexity or runtime curve.
4. **Wilson proof-chain:** PR sequence × log support × reviewer gate height (0 hold/diagnostic, 1 source conditional, 2 source pass, 3 exact theorem). This is a **provenance visualization**, not a physical-energy axis, nor does connected history imply theorem acceptance.

The existing viewer [`index.html`](index.html) retains its original four families, including the **predictive polynomial-filter** graph, which remains an analytical model and is still available unchanged. The frozen `certificates.json` remains original and SHA-stable; the updated inventory duplicates it in the new `certificates-current-20261120.json` with explicit `new_*` arrays and the complete PR ledger. Any existing 3×3 r=9 failure of the strong-magnetic retrospective formula remains visible as a **failure**.

**Acceptance and limits:** no new continuum physics proof, no unconditional first-Wilson positivity promotion, no second physical high-cluster measurement at a duplicate coordinate, and no replacement of a one-sided lower bound with a measured eigenvalue. Finite model Wilson: **SOURCE-CONDITIONAL / FORMAL HOLD**. 4D continuum Yang–Mills: **OPEN**.

## Reproduction / review

- Original 80-record pinned inventory: [`certificates.json`](certificates.json).
- Current combined 80+24 provenance/algorithm atlas: [`certificates-current-20261120.json`](certificates-current-20261120.json).
- Original atlas viewer and source explanations: [`index.html`](index.html), [`HYPOTHESIS.md`](HYPOTHESIS.md).
- New complete graphic: [`atlas-current-20261120.html`](atlas-current-20261120.html) and [preview](overview-current-20261120.svg).
- The canonical source and mathematical joined audit: [#345](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/345), [issue #137](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/issues/137).
