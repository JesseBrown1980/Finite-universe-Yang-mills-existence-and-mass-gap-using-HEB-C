# Finite-universe Yang–Mills with HEB-C

## Where we stand, November 4, 2026

All of it is on GitHub, and this table is kept current. The full register, with the open list and the decisions waiting on the operator, is [`docs/RESEARCH-STATUS-2026-11-03.md`](docs/RESEARCH-STATUS-2026-11-03.md).

| Track | Where it stands | Next |
|---|---|---|
| **3×4, with its store** | **E₉ − E₈ ≥ 24.039673 J_E at r = 9.** All 45,508,080 rows recomputed from the rules and all 1,632,625,631 pairs compared exactly. The checker was hardened and rerun on the full store in [#85](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/85) | A replay on another machine. The formal verdict and rule stay on HOLD for the operator |
| **4×4, 4×5 and 5×5, with no store** | **E₉ − E₈ ≥ 23.947629, 23.618291 and 21.792208 J_E at r = 9** ([#89](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/89)). The simple form of the bound passed a second seat and GPT-6. The stronger hybrid form passed a separate program, and the pinned checker reads the same certificates on the real 3×3 and 3×4 stores. GPT-6 confirms [the census its vectors must cover and the E₈ bound](independent/GPT6_STURM_RITZ_HYBRID_REVIEW.md) | [A different model's replay of the E₉ vectors](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/issues/100), then 6×6 and lower r |
| **Independent non-author 2×2 reconstruction** | **1,393 states, all 32,385 electric coefficients, all 8 second-order magnetic rows, graph diameter 8, and translation block sizes 385+336+336+336 reproduced** with an independently written integer verifier. The reviewer distinguishes conditional coupling arguments from prior unrerun inertia thresholds | [GPT-6 scope and code](independent/GPT6_THEOREM_REVIEW_2026-11-03.md) |
| **Independent four-sector Sturm verification** | **Eight registered thresholds** independently rechecked through a new integer Sylvester engine over all four translation sectors (1,393 pivots each). The 2≤r≤3 cells follow from the confirmed inertia counts. **3×3 Ritz:** its level differences are trial-space differences with `full_gap=NOT_CERTIFIED`, and the rounding is corrected in [#101](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/101) | [Separate review and Ritz correction](independent/GPT6_STURM_RITZ_HYBRID_REVIEW.md) |
| **3×3 Ritz report** | **[Issue #99](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/issues/99) repaired in [#101](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/101).** Every level prints as an outward interval, and the gap fields read as trial-space differences with `full_gap=NOT_CERTIFIED`. At r = 27 on K = 3: E₀ = [53493385, 53493386], E₁ = [53495397, 53495398] and trial-space difference [2011, 2013] in 10⁻⁶ J_E, or [2012517234, 2012517236] in 10⁻¹² J_E. Beside (9/8)(√14 − √6)/r² the ratio reads 1.096930 to 1.096931, 1.009243 to 1.009244 and 1.000983 to 1.000984 at r = 9, 27 and 81. GPT-6's verifier printed the same E₀, E₁ and trial-space difference on all five rows, a second seat's own check on ball matrices it rebuilt from S₃ held all 64 levels inside their intervals, and the old receipt stays byte-identical | [Corrected tables](independent/SEAT_3X3_VACUUM_BLOCK_RITZ_REPORT.md). A full-space lower bound for a 3×3 full-gap statement is open. Section G names the native zero-momentum intervals to weigh, with a transfer to the full space for r ≥ 9 tagged NAMED |
| **2×2, every coupling** | Certified at chosen points and cells, with [a separate seat's reconstruction and an analytic bound at every ratio](independent/README.md) | GPT-6's reviews are in, [#95](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/95) and [#98](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/98). The every-ratio bound's antecedent gap(E) = 6 is counted in [#102](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/102) |
| **2×2, the electric end** | **gap(E) = 6 exactly at J_B = 0**: 0 simple, nothing strictly between 0 and 6, and 6 with multiplicity 4, with all 13 costs and their multiplicities. [P(E) = 0 exact on all 1,393 basis vectors](independent/ELECTRIC_SPECTRUM_2X2_REPORT.md), GPT-6's Sturm engine unchanged at 16 thresholds, and the separate seat's builder through the Rust minors on the full 1,393-dimensional matrix. The bound at every ratio takes this as its one named antecedent. A second seat attacked it, with the [verdict not refuted](independent/reviews/opus55-electric-gap/README.md). gap(E) = 3·min(4, Lx, Ly) on every periodic S₃ torus is DERIVED, by the girth of the torus | Local receipts, with hosted replay open: the real 2×3 matrix, the digits runs and the `ownla.rs` logs. Path E stays local by cost. Open: a machine check of the Doob and Poincaré step. The second seat read path G and the prediction check's heads at `52134ab`, and the diff `52134ab..c937efc` after it |
| **Integers only** | Floating point found in the Python scripts was [redone in integers](docs/RESEARCH-STATUS-2026-11-03.md), with the float runs kept as evidence. The Cantor-27 drive now reads [exact to 30 digits](native/ym/results/cantor-integer-2026-11-03/README.md), and [a gate on every pull request](native/scripts/no_float_gate.py) fails on new floats, its list pinned file by file. [The exact rationals and clocks are on integer pairs and integer clocks](native/ym/results/integer-pairs-2026-11-03/README.md), and [the run-time rows](native/ym/results/runtime-float-2026-11-04/README.md) read 34 float hits on `cluster` going to 0 with the num crates' default features off | The gate's required checks and branch settings are the operator's |
| **Every volume at once** | The [stability plan](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/blob/main/docs/YM_TOPOLOGICAL_STABILITY_PROOF.md) ([#88](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/88)): the geometry and the theorem matching for even square tori | The finite-size constant as a number, then odd and rectangular tori |
| **The road to SU(2)** | [The companion repository](https://github.com/JesseBrown1980/Finite-Universe-SU-N-solved): S₃, Q8, 2T and 2O sealed, 2I in progress in its [draft #9](https://github.com/JesseBrown1980/Finite-Universe-SU-N-solved/pull/9) | The 2I official run |
| **The continuum** | [The continuum track](native/ym/shadow/CONTINUUM-TRACK.md) names the milestones | A separate obligation after uniformity in volume. In the operator's scope the physical volume stays finite, so the limit in question is zero spacing at fixed finite physical volume |

Merged on November 3: the checker fixes, the no-store bound and the stability plan (#84 to #92), GPT-6's audits (#95, #98), the integer redo (#96, #97), and every older PR that still applied (#5 to #9, #11 to #18, #31, #39, #42 to #44, #47), each in its place below. The register lists all of them, and the few still open. Each result here is a statement about one finite lattice. The second seat's FAIL on the original `allpairs` and every later finding stay on record, with the status of each in [`PERRON-TWO-SIDED.md`](native/ym/results/3x4_stream/perron/PERRON-TWO-SIDED.md), section 5.

Merged on November 4: the 3×3 Ritz repair ([#101](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/101)), the count of gap(E) = 6 ([#102](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/102)), and integer pairs, the final gate and the compiled check ([#103](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/103)). `main` requires `no-float`, `no-float-base` and `no-float-compiled`, with branches up to date. A pass is evidence and no proof of integer-only execution: [what the gate reads and leaves out](native/scripts/no_float_gate.py).

Four-dimensional companion: [the continuum repository](https://github.com/JesseBrown1980/yang-mills-4-dimensional-continum-proof). On its `main`, [Lemma 0003](https://github.com/JesseBrown1980/yang-mills-4-dimensional-continum-proof/blob/main/docs/LEMMA-0003-SUBGROUP-DESIGNS.md) gives which finite-group calculations agree with SU(2), and through what order: through the group's strength t exactly when no plane has both sides 1, DERIVED, [checked by GPT-6 at the proof level](https://github.com/JesseBrown1980/yang-mills-4-dimensional-continum-proof/blob/main/reviews/gpt6-sign-and-bridge/README.md). [Lemma 0004](https://github.com/JesseBrown1980/yang-mills-4-dimensional-continum-proof/blob/ym4-02c-reflection-transfer/docs/LEMMA-0004-REFLECTION-TRANSFER.md), reflection positivity and the transfer operator at each fixed lattice and β, is a draft on the operator's HOLD, and GPT-6 independently verified its sign theorem. Scope set by the operator, November 4, 2026: "We're not doing physical volume becoming infinite. We're a finite system." Zero spacing at fixed finite physical volume is OPEN.

A second location for the evidence, with its provenance: [`evidence-20261104`](https://huggingface.co/datasets/Jessedbrown/ym-3x4-room-store/tree/1b2fbfcdfdcac7c610cc933bdd295626c61f1a0e/evidence-20261104) on Hugging Face holds the 3×4 run's receipts, certificates and verifier outputs, every pull request with its SHAs, and one PASS, FAIL, HOLD or OPEN row per track. The gates stay GitHub's required checks and the operator's word.

Exact spectral certificates for S₃ lattice gauge theory on periodic finite
lattices, run headless through the HEB-C HTTP-0 backend. GitRAM distributes the
work across GitHub Actions cells. Every computation is integer-only, Rust 1.81,
and every receipt line ends in `json=0`.

The Hamiltonian is H = J_E·E + J_B·M on gauge-invariant states. The electric
term E sums over the three transpositions on every link, the magnetic term is
M = Σ_p (2 − χ(U_p)), and r = J_B/J_E. Results are eigenvalue counts below
chosen thresholds, from interval inertia (LDLᵀ with outward rounding and
magnetic-shell Schur reduction), and Perron lower bounds from one exact pass over
the rows, with every step recorded in HBP/HBI receipts. Each result is a statement about
one finite lattice. Uniformity in volume and the continuum limit are separate open
obligations: see [the theory route](#the-theory-route).

**Companion work.** [Finite-Universe SU(N)](https://github.com/JesseBrown1980/Finite-Universe-SU-N-solved) is the companion repository: S₃ confinement at strong coupling, exact Wilson-loop certificates for the finite SU(2) subgroups Q8, 2T and 2O, and the road to continuous SU(2). In this repository, [the volume-uniform proof plan](docs/YM_TOPOLOGICAL_STABILITY_PROOF.md) and [the continuum track](native/ym/shadow/CONTINUUM-TRACK.md) hold the next obligations.

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

**The same gap in the whole gauge-invariant space, by the Perron bound (November 2, 2026).** Author-maintained
certification, with an outside seat's checker, every row recomputed from the rules and every pair compared exactly on 3×4. These sit beside the rows above. Receipts are in
[`native/ym/results/3x4_stream/perron/`](native/ym/results/3x4_stream/perron/PERRON-RESULT.hbp), from PR #79:

| Lattice | `t_cert` at r = 9 (J_E) | E₉ − E₈ for every r ≥ 9 | E₉ − E₈ at r = 9 | λ₁(H′) ≤ (J_E) | Rows recomputed from the definition of H |
|---|---|---|---|---|---|
| 2×2 | 46.466823 | ≥ 22.466823 + 3(r − 9) J_E | | 46.467674 | All 211 |
| 2×3 | 58.441733 | ≥ 22.441733 + 3(r − 9) J_E | | 58.443134 | All 2,646 |
| 3×3 | 76.448116 | ≥ 22.448116 + 3(r − 9) J_E | > 23.914694 J_E | 76.448399 | All 288,645 |
| 3×4 | **94.070673** | **≥ 22.070673 + 3(r − 9) J_E** | **≥ 24.039673 J_E** | 94.070936 | All 45,508,080 |

In the orbit basis every off-diagonal entry of H is ≤ 0. With the flat rows removed to give H′, any positive vector d gives
E₉ ≥ λ₁(H′) ≥ min_h (H′d)_h / d_h, by Cauchy interlacing and Barta / Collatz–Wielandt, and one sector's rows bound the whole space
([derivation](native/ym/results/3x4_stream/perron/PERRON-BOUND.md)). The solver is untrusted, since a poor d simply gives a weaker bound. Only the exact pass counts.
`perroncert check` prints `t_cert` on every lattice here, and `check_d_strict.py`, separately written, gives the same value on 3×3 and 3×4, and an outside seat's Go checker gives it on 3×4.
The λ₁(H′) column comes from `perronritz pass`, by min-max on the span of the stored vectors.

- **Lower couplings.** With the same bound at any coupling: on 3×3, E₉ − E₈ ≥ 0.114091 + 3(r − 4.06) J_E for every r ≥ 4.06, and on 3×4, E₉(r) > 72 ≥ E₈(r)
  for every r ≥ 6.076. On 3×3 the flat bound's route ends between r = 4 and r = 4.06, from exact brackets on λ₁(H′). On 3×4 a vector of 49 numbers, [fitted at r = 5.4](native/ym/results/3x4_stream/perron/vector/VECTOR-BOUND.md), reads 72.133111 through `perroncert check`, so E₉ − E₈ ≥ 0.133111 + 3(r − 5.4) J_E for every r ≥ 5.4.
- **How it was reached.** perroncert's vectors are resolvents, so differences of them are free steps of inverse iteration. The hosted climb
  ([run 41448187715](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41448187715)) reached 94.058570, and a third divided difference of its vector with two lower ones reached
  94.070673 in one more pass: [`PERRON-TWO-SIDED.md`](native/ym/results/3x4_stream/perron/PERRON-TWO-SIDED.md). The first certificate, 93.061051, stays in the record.
- **The same vectors on two machines.** Local Windows and hosted Linux, each with its own build, give the same SHA-256 at T = 93.95 after 3 and after 6 passes.

| Evidence for the 3×4 row | Status |
|---|---|
| `perroncert check` and `check_d_strict.py`, one author | **94.070673 J_E**, same value, row and M, on [`perron/top/x3-c.bin`](https://huggingface.co/datasets/Jessedbrown/ym-3x4-room-store/tree/29723023f37ade227af51e1b92a4a4d55d4bb3f8/perron/top), all structure checks passing |
| Three outside reviews of the argument | Accepted on reading, with the lift conditional on the row check, now done on all rows |
| An outside seat's replay of the first certificate, [run 41444444894](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41444444894) | 93.061051 with the same row and M, and 5,556 rebuilt rows matching |
| A second seat's attempt to refute the new work, with its own exact checks | [No printed bound refuted](native/ym/results/3x4_stream/perron/REVIEW-OPUS55.md): 8 of 8 claims survived, and its 8 findings are handled |
| **A checker written by someone else** | **Passed:** an outside seat's Go checker, [run 41509351749](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41509351749), prints 94.070673 J_E with the same row and M on `x3-c.bin`, and the predicted values on two other vectors, with merkle, sector, vector, row-sum and self-adjoint checks passing and two fault controls rejected. Its self-adjoint test draws x, y from −3..3 with one fixed seed, where one bad pair passes at 289 of 2,401. On a fixture with every hash repaired, [run 41575947849](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41575947849), it reported all 211 row-sum faults and 1,071 of 1,198 single-pair faults, with 127 passing, each as predicted. [Its log, source and scope](native/ym/results/3x4_stream/perron/PERRON-TWO-SIDED.md) |
| **Every 3×4 row recomputed from the rules** | **Done:** a second seat's `fullrebuild` gives 45,508,080 rows, 0 mismatches in key, weight, M or entries, and merkle PASS, in 7,870 s on this seat's machine, [as predicted in writing first](native/ym/results/3x4_stream/perron/FULLREBUILD-RUN.hbp). Afterwards all 34 local sectors match the public manifest. With a store's merkle repaired after one change, it caught 4 of 4 |
| **Every off-diagonal pair compared exactly** | **Done:** `allpairs` gives 1,632,625,631 pairs with w_h z_hj = w_j z_jh, 0 mismatches and 0 unpaired entries, and merkle PASS on each of 4 passes, in 2,704 s on this seat's machine, [with a prediction row time-stamped before the start](native/ym/results/3x4_stream/perron/allpairs/ALLPAIRS-RUN.hbp), which reached git after the run. The controls on small stores met all 49 predicted outcomes, 40 of `allpairs` and 9 of `fullrebuild`. **Correction:** a review found that the tool's two count gates let `OPEN` through. This run printed `PASS` on both. The corrected tool needs `PASS` on both for exit 0, and [its header controls](native/ym/results/3x4_stream/perron/allpairs/failclosed/HEADER-CONTROLS.hbp) met all 124 predicted outcomes, with the original reaching exit 0 on each of the 22 cases at `OPEN`. A full 3×4 run with the corrected tool [printed the same rows](native/ym/results/3x4_stream/perron/allpairs/failclosed/pin-0fd24d3/ALLPAIRS-3x4-PIN.out) apart from seconds |
| **A vector of few numbers, and a bound with no store** | **New. A second seat on this seat's model read it, [verdict PASS](native/ym/results/3x4_stream/perron/vector/review-opus55/VECTOR-REVIEW.md), and GPT-6 on another model rebuilt it, [verdict PASS at the four points it checked](native/ym/results/3x4_stream/perron/vector/review-gpt6/REVIEW-e0466bd.md):** [on 3×4 at r = 9](native/ym/results/3x4_stream/perron/vector/VECTOR-BOUND.md), `perroncert check` reads 85.120864 with two numbers and 89.921453 with 49, against the flat bound 72. The ratio depends only on local patterns, and all 45,508,073 non-flat rows of the 3×4 store fall in the table derived from that rule with no store. That table gives, for any torus and with no store, **E₉ − E₈ ≥ 16.252744 J_E on 4×4 at r = 9**, 14.017195 on 4×5 and 4.016734 on 5×5, and a positive bound on L×L for r above about 1.5·L + 1, up to L = 8 so far. Its reader added E₈ ≤ 3·nl + 2r − √(4r² + 3·nl) for min(Lx, Ly) ≥ 4, and a hybrid vector, with no store, that gives **E₉ between 117.453728 and 117.580284 on 4×4 at r = 9, so E₉ − E₈ ≥ 23.947629**. [A separate program](native/ym/results/3x4_stream/perron/vector/VECTOR-BOUND.md#the-attack-on-the-hybrid-certificate) reads the same certificates from the definition of H, with every orbit counted, and the pinned `perroncert check` reads them on the real 3×3 and 3×4 stores, to the micro. Another model's attack on it stays open. Each is a statement about one finite torus |
| **A second seat's review of `allpairs`** | **FAIL overall**, on fail-closed behavior and on wording, [in its report](native/ym/results/3x4_stream/perron/allpairs/failclosed/review-opus55/ALLPAIRS-REVIEW.md). **The recorded 3×4 numbers stand:** its own reader, in one pass on this seat's machine, gives the same 1,632,625,631 pairs and four windows, with the 34 sectors matching the public manifest. PASS on windows, on unpaired edges and on the pair count. Two of its defects are closed in the corrected tool, and D3 to D8 stayed open in that tool, among them that the output never names its store. It ran on the same model as this seat, so a replay on another machine stays open. **Since then:** [D3 to D8 are fixed](native/ym/results/3x4_stream/perron/PERRON-TWO-SIDED.md), with controls on the old executables and hosted Linux. Part three of the review read FAIL on one race and one recipe path, both now fixed. A full 3×4 run on the final tool, with its prediction on GitHub first, exits 0 in 2,880 s and meets every predicted field, with the same 1,632,625,631 pairs, and now names its store by its two hashes |
| A registered rule for this route, and the operator's word on a verdict | Open |

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
[21.095802, 21.573297]. Open: the run at r = 243, which the Perron bound makes affordable from below.

**Confinement law, exact to second order in r, certified at finite coupling**
([`zconf`](native/ym/results/zconf-2026-10-30-cloud/README.md),
[`zconfcert`](native/ym/results/zconfcert-2026-10-30-cloud/README.md)):

V(d, r) = 3d·J_E + n_g·d·(s_str − s_vac)·r²·J_E + O(r³),  s_vac = −1/12,  s_str = −17/144

Two static S3 charges (the 2-dimensional irrep and its conjugate) d links apart are joined by a string of
`std` links costing exactly 3·J_E per link at r = 0. At second order each plaquette holding a string link
shifts by s_str instead of s_vac, so the string tension falls by n_g·5/144·r², with n_g the number of
plaquettes per string link (κ = −5/72 in the 2D bulk). The certified finite-coupling energies, run as
HTTP-0 jobs, confirm the law: at r = 1/27 κ_eff = −0.034981 on a ladder (n_g = 1, κ_g = −0.034722) and
−0.069960 on a strip (n_g = 2, κ_g = −0.069444), a ratio of 1.9999, the same for d = 1, 2, 3, with the
remaining drift linear in r. V(d, r) is certified increasing in d at every coupling measured
(σ = 2.99995 at r = 1/27, 2.9566 at r = 1). Together with the gap law, this gives exact results from
both coupling directions: strong electric (r → 0) and strong magnetic (r → ∞).

**Spatial Wilson loops, exact series and certified values**
([`zwilson`](native/ym/results/zwilson-2026-10-30-cloud/README.md)): on the same open ladder,
⟨χ_std(U_C)⟩ for the 1×A loop starts exactly at order r^A, with coefficients 1/6, 7/432 and 11/6912
for A = 1, 2, 3, identical in two independent bases. Certified at finite coupling through HTTP-0 (to
2.6 × 10⁻⁹, from the concavity of the ground energy in a loop source), the loops match those leading
terms to within 0.5–2.2% at r = 1/27, converge toward them as r falls, and fall by the same factor per added
plaquette (0.0036 at r = 1/27, 0.111 at r = 1): the area law, certified.

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

**3×4 production (November 1, 2026): the 60M run passed, `negative=0`, `ambiguous=0`, a vacuum lower bound.**

- **Production run [41321108365](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41321108365)** ran from `main`
  `1cc821c` at `t_milli=60000000`, `TOL=1000`. All 18 column jobs (17 of 8 columns and one of 1, over
  the 137 core columns) and the merge succeeded, 5 h 34 min from dispatch to the merge row. The merged
  row gives `negative=0`, `positive_core=137`, `positive_H=45,507,943`, `ambiguous=0`, `result=PASS`: all
  45,508,080 levels of the (+,+) sector lie above 60 J_E at r = 9. This is a **vacuum lower bound**, and the
  gap comes from the Perron bound in the results above. Receipt: [`production-41321108365/`](native/ym/results/3x4_stream/production-41321108365/)
  (`PRODUCTION-RECEIPT.hbp`).
- **Control run [41294035019](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41294035019) passed:** C1 548/548 `SCOL` rows
  byte-identical to the local pilot; C2 10,123 s against the 10,800 s limit; C3 34/34 store
  sectors from [Hugging Face](https://huggingface.co/datasets/Jessedbrown/ym-3x4-room-store) matched
  their SHA-256, with the payload merkle `ec03c5f8…` checked on every pass. Receipt:
  [`control/`](native/ym/results/3x4_stream/control/) (`CONTROL-RECEIPT.hbp` sha `f1c4d53e…`, PR #70).
- **Gap-verdict rule registered** (PR #71):
  [`GAP-VERDICT-RULE-3X4.md`](native/ym/results/3x4_stream/GAP-VERDICT-RULE-3X4.md), sha `d635a6e5…`,
  chained to the control receipt. Its only admissible threshold is 60M. The 72M–90M ladder is
  not admissible until a spec revision sizes the job matrix to the larger cores.
- **Fail-closed gate** ([workflow](.github/workflows/hebc-ym-3x4-fanout.yml), PR #69): refusal
  runs [41307404040](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41307404040) (rule not yet registered) and
  [41307428999](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41307428999) (72M) both refused before any column job ran.
- **Plan:** [frozen fan-out spec](native/ym/results/3x4_stream/PRODUCTION-FANOUT-SPEC.md) plus
  [revision 1](native/ym/results/3x4_stream/PRODUCTION-FANOUT-SPEC-REV1.md) (PR #72). The
  8-column job time has not been measured; doubling the 4-column control would put it at about
  20,246 s, under the 21,000 s timeout (an estimate). Under revision 1, a job that does not finish is re-run
  locally with the same pinned `roomschur` source after a local 0:4 control, and merged locally.
  **Correction, November 1:** the estimate above compared `roomschur` time with a limit on the whole
  job, and it doubled the column count when the control had 3 active columns. On the limit's grain
  the same doubling is 20,690 to 21,071 s, so "under the timeout" did not follow. Measured times are
  in the [correction note](native/ym/results/3x4_stream/PRODUCTION-FANOUT-SPEC-REV1-CORRECTION.md).
- **P0 passed, November 2:** `flatcomp` on the 3×4 store, merkle checked, gives 7 flat states, all diagonals 72 and
  0 flat-flat couplings, as predicted before the run. This is the registered rule's precondition.
- **The gap on 3×4, November 2:** see the Perron table in the results above. An outside seat's checker stopped first on a wrong
  line of this project's format guide, now corrected, with its diagnostic printing the predicted `trailing=742160 nonzero=0 merkle_matches=true`, and then passed.
- **Open:** the 3×4 gap verdict, by a rule revision for the Perron route or by the registered rule, whose route needs the (+,+)
  excitation bound and, for zero momentum, the other three sectors' stores. The fan-out spec revision for thresholds above 60M is on
  hold, since the Perron route could replace it.

**3×4 scaling status (October 30, 2026; production HOLD), kept as recorded. On November 1 the HOLD
was lifted for `t_milli=60000000` only, with the pinned `roomschur` source `8c2ebe80`. The 90M
ambiguity remains open, and any threshold above 60M stays on HOLD until a spec revision admits it:**

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
  **Recheck, November 1:** the 9 undecided columns came from the last step of the merge, and the column solves
  stand. A new tool, `schurcert`, reads the same column enclosures and decides all 2,940 columns: `negative=44`,
  `positive=2896`, `ambiguous=0`. On November 2, exact minors from separately written code gave the same count on the
  midpoint matrix, one matrix inside the enclosures, with every minor nonzero. This covers the final step on 3×3. Open:
  a second-seat review, and a registered spec naming `schurcert` as its merge step, which is what the 90M gate below
  waits for.
  Receipt: [`3x3_inertia_recheck/`](native/ym/results/3x3_inertia_recheck/).
- **Production stays on HOLD** until the remaining gates pass: the 90M ambiguity,
  binary/source provenance and production admission. The memory pilot gate has passed. See
  [the admission rule](native/ym/results/3x4_stream/PRODUCTION-ADMISSION.md),
  [frozen pilot specification](native/ym/results/3x4_stream/MEMORY-PILOT-SPEC.md),
  and [PR #37: local segmented evidence, unmerged](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/37).
  The admission-rule file carries the pre-pilot HOLD text; the October 30 measured values
  are recorded here and in the pilot receipt.

**Other in progress:** full-space counts on 2×4 through the reflection-only
sectors; a separately written operator and inertia verifier. **Open on the Perron route:** a solve at lower coupling on 3×4; `perroncert` guards at absurd inputs, where it wraps and
`check_d_strict.py` refuses; on the outside seat's Go checker, an exact pair test in its own code;
a reading of the one-read change to `allpairs` by another seat; the other tools that still read through `roomio.rs`; a replay of `fullrebuild` and `allpairs` on another machine.

### Evidence classes and verification

| Evidence class | What is established | Next |
|---|---|---|
| Exact integer-arithmetic certificates of fixed-lattice spectral-gap bounds (S₃) | 2×L sector results and 3×3 full-space counts with sealed integer receipts and checks; whole-space Perron bounds on 2×2, 2×3, 3×3 and 3×4, author-maintained, with an outside seat's checker, all rows recomputed and all pairs compared exactly on 3×4 | The BHM/TQO volume-uniform proof, the immediate research track |
| 3×4 dimension, memory and control | 2,177,317,873 reconciled gauge orbits; P4 `PILOT_PASS`, `CAP=12`; hosted control C1–C3 PASS; gap rule registered; 60M production PASS (`negative=0`, `ambiguous=0`); P0 PASS on the store; Perron bound 94.070673 J_E by the author's two checkers and an outside seat's Go checker, with λ₁(H′) ≤ 94.070936 J_E; all 45,508,080 rows recomputed from the rules and all 1,632,625,631 pairs compared exactly, 0 mismatches | A rule revision and the operator's word on a 3×4 gap verdict; 90M ambiguity |
| Cross-seat operator experiments | Replayed software models of reach, curve, hash and CHSH on discrete lattices | A physical z mechanism; a rule that yields the quantum bound 2√2 from the model |
| Production | 60M run 41321108365: 18 of 18 column jobs and the merge succeeded, `negative=0`, `ambiguous=0`; no local re-run was needed | A spec revision before any threshold above 60M, if the Perron route leaves one needed |

### z/r/j, prism and Bell software models

Software models of the z/r/j layer on discrete lattices, each with replayed
SHA/HBI/HBP receipts. PASS/FAIL judgments stay as originally registered.

- [zlight (merged acer reference)](native/ym/results/zlight-2026-10-30/):
  the global digest changes at the step the laser fires, while light moves one cell
  per step; the target's own cell changes only when the light arrives.
  [The cloud seat's zlight](native/ym/results/zlight-2026-10-30-cloud/), merged November 3 from #39,
  keeps its original P5 FAIL.
- [Per-level r/j (merged acer reference)](native/ym/results/perlevel-2026-10-30/):
  ring-neighbour propagation against hierarchical three-per-level connectivity,
  each with its own metric and schedule.
  [zlevel](native/ym/results/zlevel-2026-10-30-cloud/), [zcurve](native/ym/results/zcurve-2026-10-30-cloud/) and
  [zbell](native/ym/results/zbell-2026-10-30-cloud/), merged November 3 from #44, are the independent Rust tests, with their
  registered failures, and the replay workflow rebuilds each with Rust 1.81 and checks byte identity.
- [CHSH (merged software reference)](native/ym/results/chsh-2026-10-30/):
  Bell-local models stay within `|S|<=2`. A controller that reads both settings, with a
  balanced shared hidden variable, gives `S=4` with both stations' own counts unchanged
  by the far setting. See also [the three-seat control](native/ym/results/chsh-prism3-2026-10-30-third-seat/), merged November 3 from #47: a hash-local model at S = 1.28925, and two centralized generators at 2.84235 and 4.
- [Teleportation hierarchy (merged, PR #53)](native/ym/results/zteleport-2026-10-30-cloud/):
  Bell states with Bell-state measurements keep S² = 8 exactly through four teleportation steps;
  PR-box correlations under every local wiring fall to the local bound 2 after one step; a global
  z controller keeps any value. Correlations carried by locally composed resources land on 2√2.
- [Finite-fluid cutoff (zcutoff)](native/ym/results/zcutoff-2026-10-30-cloud/) and
  [transport on the current gates (zcalib)](native/ym/results/zcalib-2026-10-30-cloud/): in the D3Q27
  lattice gas, a swirl driven toward zero core radius at 24³, 48³ and 96³ concentrates (axis vorticity
  681 → 2,011 → 4,078) while its core holds 1/8 of the box, and at 96³ the cells reach the occupancy cap;
  kinematic viscosity 0.44 and 0.43 at two sizes, c_s² = 2/3 exactly.
- [prism3 (merged, PR #45)](native/ym/results/prism3-2026-10-30/),
  [prism-Bell (merged, PR #48)](native/ym/results/prismbell-2026-10-30/) and
  [Cantor (merged, PR #49)](native/ym/results/cantor-2026-10-30/): Cantor's 16 bands are
  simulated channels, one per Cantor level; all 16 arrive together at step 20. The
  prism-Bell and Cantor corrections are append-only files beside the original sealed records.
- [Frustrated-orientation benchmark (merged, PR #51)](native/ym/results/frustrated-2026-10-30/):
  the field-only control delivers 27/27 and frustrated optimization 25/27, against
  hash selection's 15/27; energy and Bell outcomes are reported separately.
- [One matrix](native/ym/results/z-one-matrix-20261030/), merged November 3 from #42: a destination-bound z token
  with wrong, stale and mutated-token gates, both signed curved-j orientations at rank 3 over GF(3) against rank 1 for J,
  and a per-level cross-check. Its original no-return prediction's FAIL stays on record, beside a revised window issued after it.
- [Three prisms](native/ym/results/qprism-three-2026-10-30/), merged November 3 from #43: 27 branches and 54 cases, all eight
  registered software checks PASS, and the deliberately exposed global token reads LEAK.

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
at r ≥ 9 on each lattice, and the Perron bound adds, on the same terms as its table above, every r ≥ 4.06 on
3×3 and every r ≥ 6.076 on 3×4. Each is a statement about one finite lattice. Two steps are open: completing the
instantiation, and the value of r₀. The document tracks them lemma by lemma. The continuum limit is a further obligation
beyond those.

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
- The Perron route's tools: `perroncert` (solver and exact check), `check_d_strict.py` (fail-closed Python checker),
  `verify_sample_rows.py` (rows rebuilt from the definition), `perronritz` (side from above, every coupling,
  divided differences), `second-seat/fullrebuild.rs` (every row recomputed from the rules), and `allpairs` (every off-diagonal pair, exactly). `outside-go-41509351749/` holds the outside seat's
  Go checker, its log and its artifact, `allpairs/fixture-controls/` the faults that reach each checker's gates, `allpairs/failclosed/` the correction to the count gates of `allpairs`, and `allpairs/hardened/` and `allpairs/oneread/` the fixes for D3 to D8 and H1 to H4, with their controls, reviews and full 3×4 runs. The bound with no store adds `prodvec`, `localaudit` and `hybridcheck`, in `crates/evolvers`, with `vector/` beside them.

## 2×2 coupling ladder: E₁ − E₀

On the full 1,393-state 2×2 torus, the first excitation gap is certified at
these points:
- **(J_E, J_B) = (1, 1):** E₀ ∈ [7.634198, 7.634199], E₁ ∈ [13.240000, 13.242733], gap ∈ [5.605801, 5.608535].
- **(J_E, J_B) = (3, 5):** gap ∈ [14.140772, 14.142823].

A further set of certified cells covers r = J_B/J_E ∈ [3, 10,022]. They come
from interval Sturm counts over the four translation sectors, monotone cells and
SHA-keyed ledgers, in [`independent/ladder/`](independent/ladder/LADDER_METHOD.md). The weak-coupling law there
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

**A separate seat's work on this torus,** [`independent/`](independent/README.md), merged November 3 from #7 to #15 and #18: a separate reconstruction with the native operator's SHA-256, all 1,393 Sturm pivots certified at (1, 1) and (3, 5), the exact second-order splitting at the magnetic end, an analytic lower bound at every coupling ratio, proved cells on 0 ≤ r ≤ 2, the four translation sectors, and a first resolution of the 3×3 flat levels on a ball of 59,246 orbits. A non-author proof review of its theorems stays open.

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
- **Stage 2I, the RIME C3 test:** an exact counterexample to one natural bridge. A basis-preserving C3
  extension that commutes with the torus Hamiltonian fails at the fourth moment, 417,192 against 416,784
  for H_E, between two flat orbits of equal weight. Earlier moments agree, and a true square-axis swap
  passes as a control. [Report](STAGE2I_RIME_C3_HAMILTONIAN_MOMENT_OBSTRUCTION.md).
- **Stage 2J, the RIME Prism bridge:** the original Python NTT and its controls stay unchanged, pinned by
  git blob, with Rust HBP/HBI receipts around them. The carrier holds all 27 coefficients and round-trips
  byte for byte in both decoders, and every malformed carrier in its fixtures stops closed.
  [Report](STAGE2J_RIME_SPHERE_BRIDGE.md).
- **HTTP-0 finite S₃ wave observatory:** an explicitly specified second-order wave equation on all 1,393
  components, as an exact integer-numerator recurrence on arbitrary-length integers, served with controls and a
  web page. [First version](HTTP0_FINITE_S3_WAVE_OBSERVATORY.md), [its correction to exact numerators](HTTP0_EXACT_INTEGER_NO_ROUNDING.md).
- **Cantor-27 drive on the S₃ sector, in integers only:** the 729-slot Cantor signal on the 211-state sector, with
  each value in an enclosure one unit wide at 10⁻³⁰, and a separately written path printing the same. [The result](native/ym/results/cantor-integer-2026-11-03/README.md).
  The earlier floating-point run stays beside it as evidence, and it was right to about 12 digits.
- **Constellation audit:** the original 3/27/243 sector transitions and
  45/405/3,645 keys compiled into the native build, with a gauge-invariant
  243-sector index of the 1,393 torus orbits.
  [Audit](STAGE2D_CONSTELLATION_SOURCE_AUDIT.md).
- **Clasy X3 kernel:** the 81-mode finite-field shell model with its exact
  all-time invariant, 81 × 243 and 243 × 81 batches, and receipts.
  [Pinned reference](CLASY_X3_PINNED_REFERENCE.md),
  [roadmap](CLASY_X3_TO_HEBC_HTTP0_NEXT_HURDLES.md),
  [continuum guide](CLASY_X3_CONTINUUM_HURDLES_GUIDE.md).
- **3×3 certify generator:** a step under `bash -e` stopped before writing its receipt lines. Every outcome now
  writes them, and the step is green only for PASS, with synthetic controls.
  [Note](native/ym/results/3x3_full_space/CERTIFY-PACKAGING-FIX.md).
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

To repeat the 3×4 certificate from public files, or to attack it, see [the review guide](native/ym/results/3x4_stream/perron/PERRON-REVIEW.md).

Theory and architecture: Jesse Daniel Brown.
