# GPT-6 independent integer Sturm, 3×3 Ritz, and hybrid-bound audit — 2026-11-03

**Scope:** finite S₃ gauge Hamiltonians. **NOT** the Clay four-dimensional continuum Yang–Mills proof. Historical failed controls and outputs remain pinned and visible.

## I. Independent full four-sector 2×2 Sturm

**Independently run, exact integers, 40 guard digits.** [gpt6_sturm_sectors.py](gpt6_sturm_sectors.py) starts from the different-model [gpt6_2x2_from_permutations.py](gpt6_2x2_from_permutations.py), reconstructs spatial translations on all eight physical links, and projects onto four translation characters. It does not use the earlier seat's sector builder. All four canonical matrix-byte SHA-256 pins match.

[gpt6_sturm_interval.py](gpt6_sturm_interval.py) then builds the positive-orbit-weighted, symmetric, shifted matrix directly from these four source files. Its independent Schur elimination encloses every quotient using eight exact integer endpoint corners, chooses sign-definite minimum-degree pivots, and fails if any pivot contains zero. It does NOT import the other seat's Sturm algorithm. All 1,393 pivots complete at each of eight frozen thresholds.

| (JE, JB, threshold/1000) | Negative eigenvalues in (++, +−, −+, −−) | Verdict |
|---|---|---|
| (1,1,7000) | 0,0,0,0 | INDEPENDENT PASS |
| (1,1,13240) | 1,0,0,0 | INDEPENDENT PASS |
| (1,1,13300) | 3,0,0,0 | INDEPENDENT PASS |
| (3,5,50840) | 1,0,0,0 | INDEPENDENT PASS |
| (1,2,18250) | 1,0,0,0 | INDEPENDENT PASS |
| (2,5,34400) | 1,0,0,0 | INDEPENDENT PASS |
| (2,5,39400) | 1,0,0,0 | INDEPENDENT PASS |
| (1,3,19300) | 1,0,0,0 | INDEPENDENT PASS |

The all-sector counts 1 at the two pilot boundaries give continuous positive-gap cells by ordered-eigenvalue monotonicity: **r∈[2,5/2]: gap(E+rM)>21/20** and **r∈[5/2,3]: gap(E+rM)>2/5**, with JE=1; multiply by JE for non-unit electric coupling. This is a finite 2×2 theorem only. The eight registered output lines are pinned in [gpt6_sturm_interval.measure](gpt6_sturm_interval.measure). Hosted CI must regenerate matrices from independently rebuilt S₃ permutations, replay all eight thresholds and reject a corrupted source byte and a wrong expected inertia.

## II. 3×3 block-Krylov Ritz correction

**Independent mathematical review found a substantive interpretation defect in the original report.** Cauchy interlacing and Rayleigh–Ritz give *upper bounds on each ordered eigenvalue* of the full 3×3 Hamiltonian. If the trial eigenvalues are μ₀≥λ₀ and μ₁≥λ₁, the difference μ₁−μ₀ is neither a lower nor an upper bound on λ₁−λ₀. The integer-only counterexamples in [gpt6_ritz_scope.py](gpt6_ritz_scope.py) show both directions with explicit diagonal matrices.

A second defect is **non-outward rounding of Ritz bisection brackets.** The original source line `energies.append((lo // 24, hi // 24))` floors both ends, although the rigorous high endpoint must be **ceiled** to `(hi+23)//24`. The new counterexample has exact microenergy 5/16 and raw bracket 7<24E<8: the old displayed [0,0] excludes it; corrected [0,1] includes it. This means the original identical-micro lines in [seat_3x3_vacuum_block_ritz.measure](seat_3x3_vacuum_block_ritz.measure) are historical rounded *Ritz estimates*, not rigorous enclosures. They cannot certify a full-Hamiltonian gap or a physical 3×3 tunnelling law.

The independent [gpt6_3x3_ritz_independent.py](gpt6_3x3_ritz_independent.py) builds the vacuum-generated Krylov Gram and Hamiltonian matrices from the SHA-pinned raw 3×3 graph file by *row-oriented weighted graph action*, and uses the alternative integer-interval Schur inertia routine. It outputs outward-rounded Ritz eigenvalue intervals and explicitly tags `full_gap=NOT_CERTIFIED`. The companion workflow checks K=1 and K=3 at r=27, including a tampered raw-matrix rejection. The historical source and original receipts are retained, with a conspicuous correction inserted at the top of [the original report](SEAT_3X3_VACUUM_BLOCK_RITZ_REPORT.md).

**Still open for a true 3×3 gap proof:** rigorous lower bounds for one of the relevant eigenvalues and upper/lower estimates of opposite directions, such as independently certified full-space inertia/Sturm bounds; or an independently proved perturbation theorem with explicit remainder and spectral separation. A 32-dimensional trial spectrum alone cannot provide these.

## III. Large-lattice hybrid vectors — separate gate

The *simple* store-free lump bounds on 4×4, 4×5 and 5×5 already passed GPT-6's separate full integer reconstruction, move-table verification, physical configurations and sabotage controls ([the review](../native/ym/results/3x4_stream/perron/vector/review-gpt6/REVIEW-e0466bd.md)). These must not be relabelled as a review of the **stronger hybrid** vector.

**New independent hybrid census: exact group convolution — PASS.** [gpt6_hybrid_census.py](gpt6_hybrid_census.py) does **not** import any hybrid author/second-seat code. It enumerates the six S₃ permutations, determines the 36 commutators of two torus holonomies, and convolves P plaquette elements by group product and conjugacy-type cost. On a genus-one lattice, P plaquette holonomies have ordered product equal to the global holonomy commutator; this exactly counts all gauge-fixed configurations before residual conjugation using a small dynamic program. The eight independent totals are pinned in [gpt6_hybrid_census.measure](gpt6_hybrid_census.measure):

| Torus | M cutoff | Non-flat assignments | (a,b)=(0,4) assignments |
|---|---:|---:|---:|
| 3×3 | 13 | 3,590,190 | 24,948 |
| 3×4 | 14 | 78,547,410 | 98,010 |
| 4×4 | 8 | 2,151,648 | 0 |
| 4×4 | 10 | 6,919,488 | 0 |
| 4×4 | 12 | 119,790,792 | **360,360** |
| 4×4 | 14 | **624,556,872** | **360,360** |
| 4×5 | 13 | **642,825,270** | 959,310 |
| 5×5 | 11 | **563,254,650** | 0 |

Every one has 18 additional flat gauge-fixed configurations. The withdrawn 4×4 cutoff-12 vector counted only 315,216 of the independently expected 360,360 (0,4) assignments; **45,144 are missing**. The 3×4 cutoff-12 failure analog has 98,010 expected and 94,446 represented, short 3,564. A negative control falsifies the expected 4×4 cutoff-12 total by one and must exit nonzero. These calculations independently verify the denominator census **but do not themselves check that all cut-14 representatives in the released vector cover the census or that any hybrid Collatz-Wielandt inequality holds**.

**Independent outward-rounded arithmetic — PASS, certificate premises not reverified.** [gpt6_hybrid_arithmetic.py](gpt6_hybrid_arithmetic.py) recomputes the integer micro-unit upper bound from the dressed-flat formula `E8 ≤ 3nl+2r−sqrt(4r²+3nl)` using `math.isqrt`, subtracting a floor of the square root to ensure the E8 endpoint is rounded *up*. For the four registered hybrid E9 lower claims it yields, respectively: (4×4,r9) `117453728−93506099=23947629`, (4×4,r6) `103521056−92508067=11012989`, (4×5,r9) `140546984−116928693=23618291`, and (5×5,r9) `168020667−146228459=21792208`, all in millionths of JE. **This independently verifies the numerical subtraction and square-root enclosure, not the 16-state trial-space theorem or the hybrid E9 lower certificates.**

The hybrid at cuts (4×4,r=9,M≤14), (4×4,r=6,M≤14), (4×5,r=9,M≤13), (5×5,r=9,M≤11) has already passed the author's `hybridcheck` (a separate codebase) and its stored fault controls. Those checks record exact low-M representative counts, high-M lump envelopes and the nontrivial *retracted* cut-12 failures with missing `(a,b)=(0,4)` orbit coverage. The vectors are recorded in the GitHub release `vectors-20261103` with SHA-256 manifests. **No new GPT-6 independent exhaustive low-M enumeration of 825,865 representatives, independent 16-dimensional E₈ construction, or large-vector Ritz Rayleigh quotient is claimed here.** Thus the hybrid numerical values remain **PENDING A DIFFERENT-MODEL REPLAY**, even though the simpler bounds are independently confirmed. Prior controls and full source remain available for the next separately gated work.

The previously cited 3×3 Ritz *gap difference* cannot be used as an extra certified hybrid-gap bound without the corresponding independent full-spectrum lower/upper information. Hybrid E₉ lower estimates and dressed-flat E₈ upper estimates need their own valid min–max proofs and exact arithmetic, not Ritz-gap subtraction.

## IV. Merge decision

This audit may merge once its own hosted CI reproduces all eight full-sector inertias, both outward-rounded actual 3×3 Ritz trials and the fault controls. It **does not** merge or lift [formal 3×4 verdict draft #68](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/68), change the continuum claims, or claim the hybrid is independently certified.
