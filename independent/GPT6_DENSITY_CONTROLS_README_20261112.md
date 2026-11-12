# Density controls: independent measurement contract (November 12, 2026)

The 19,683-room matrix with its D:-resident authenticated stubs is NOT available on the hosted runner. The reported nine-cell occupancy ranges from the operator's separate seat are transcribed in the accompanying Python auditor as conversation-supplied aggregates, **not independently replayed local simulator trajectories**.

## Nine reported density cells, 9 uniform-digit scrambles

| Mode | 729 | 2187 | 6561 |
| --- | --- | --- | --- |
| Frozen | 499 [424,547] | 471 [465,633] | 446 [480,597] |
| Respond-local | 598 [555,661] | 582 [518,591] | 514 [458,530] |
| Global-hash | 602 [567,604] | 578 [499,553] | 446 [457,492] |

3/9 individual comparisons fall outside their scramble range. Frozen 6561 also falls outside, preventing causal field attribution. The hash-vs-frozen **real** spread differences are +103,+107,0. They cannot be assigned significance without the paired per-scramble differences.

### New exact pairing-independent feedback envelope

Even without the 27 matched controls or the individual nine control values, the published minimum and maximum ranges imply bounds on all possible pairwise scrambled feedback differences:

| Functions | Real global minus frozen | Minimum possible control difference | Maximum possible control difference | Guaranteed outside? |
| --- | ---: | ---: | ---: | --- |
| 729 | +103 | +20 | +180 | Not determined |
| 2187 | +107 | -134 | +88 | **Yes** |
| 6561 | 0 | -140 | +12 | Not determined |

For example, any control difference at 2187 obeys global_control - frozen_control <= 553 - 465 = 88. The real difference is 578 - 471 = 107, **19 units above the largest possible control**. This is robust to pairing the nine controls in any order, assuming the reported ranges and mode values share the same spread definition. It is only one density, against the weaker **uniform-digit** scrambles, so it does not establish the predeclared stricter 27 within-function shuffle gate or a collective field.

## Strict 27-control, 6-cell workflow

The other seat committed the hypothesis before observing its new output:

1. Real is outside 27 per-function digit-permutation controls for 2 or more of 3 densities in global-hash mode.
2. Real is inside the controls for all 3 frozen-mode densities.
3. This is an ordering-sensitive effect hypothesis only; not a proof of a quantum or continuum field.

The auditor accepts a sealed ASCII file with six CELL rows, 162 HIST rows, and TRAJECTORY hashes at matched ticks (named TRACE), all `json=0`.

- `CELL|mode=frozen|density=729|real=499|controls=1,2,...27|json=0`: record **27 actual** control spreads, ordered by the same matched scramble seeds across frozen and global-hash. The literal ellipsis is NOT valid input.
- `HIST|mode=frozen|density=729|control=0|functions=729|original_sha256=<64hex>|shuffled_sha256=<64hex>|json=0`: producer claims the canonical SHA256 of each function's counts of 0,1,2 before and after shuffling. The auditor checks hash equality and completeness, **not the raw digits themselves**. For independent histogram checking, the underlying digit lists must be supplied and inspected separately.
- `TRACE|mode=frozen|density=6561|tick=0|state_sha256=<64hex>|json=0`: SHA256 of all function identities, positions, headings and room states at that tick, with ordering and serialization documented by producer; supply the same ticks for both modes. Different hashes establish different encoded states; equal spread counts alone do not.

`python3 -B independent/gpt6_density_controls_20261112.py reported` audits the known aggregates. `selftest` exercises valid/invalid permutation, matched-difference, trajectory and tampering checks on **synthetic fixtures**, not on the physical room store. `strict <data>` reads real six-cell evidence when provided. Inability to authenticate the raw digits or reproduce the D: store is explicitly a remaining verification HOLD.

## Exact rank reference (not empirical significance)

For m=9 independent, exchangeable, tie-free controls, a new test draw is outside their min/max with probability 2/(m+1)=1/5. For m=27, the probability is 1/14. Assuming independence across densities and modes, the joint two-of-three global / zero-of-three frozen criterion has probability 832/15625 (~5.32%) for m=9 and 10985/941192 (~1.17%) for m=27. Shared trajectories, scrambling or common centre pull invalidate the independence assumption; this is only a benchmark.

The global-hash read is nonlocal and cannot independently demonstrate a causal relativistic field. No computations at r=9. r9 remains on HOLD.
