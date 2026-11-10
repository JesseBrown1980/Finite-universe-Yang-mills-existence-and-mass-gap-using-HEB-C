# REFUTE-GL159: independent refutation attempt on PR #159 (head b3eeca0)

Hot-path receipt: `REFUTE-GL159.hbp` (121 rows, json=0) and `REFUTE-GL159.hbp.sha256`. This file is the readable companion to it. Every number below is copied from that receipt.

## Verdict

No row is REFUTED.

- **GL1:** 3 rows MET, 1 row NOT_RESOLVED. My own integer code, which imports nothing from the PR, reproduces each one.
- **GL3:** 4 of 4 MET, reproduced independently.
- **Exterior floor and inertia argument:** valid, and the floor bounds the whole physical complement, not only the ball.
- **Provenance note:** two of the three receipt files were made by a script that is not in git (sha e9397ce5…). The committed script (daf78b00…) reproduces every computational row of those files. No receipt replays byte for byte, because the files carry timing fields; with those fields removed, the k3plus file matches exactly.
- **Gap in the self-checks:** the PR's own checks do not catch a planted wrong floor, a dropped exterior edge, or a wrong level index at r values with no anchor. Those faults are caught only by a replay or an independent recomputation, which this report supplies.

## Per row

| row | PR | independent (indep_gl.py, own conventions) | status |
|---|---|---|---|
| GL1 3x4 r=81 | [21.340976, 21.428772] | [21.279115, 21.714875] ⊂ [21, 21.790123] | CONFIRMED_WITH_NOTE (MET needs the k3plus run; the k3plus run on its own already gives MET) |
| GL1 3x4 r=729 | [21.033509, 21.041012] | [21.035004, 21.039760] | CONFIRMED_WITH_NOTE (receipt from the uncommitted script; the committed script reproduces it) |
| GL1 3x3 r=729 | [21.044892, 21.050573] | [21.046331, 21.049384] | CONFIRMED_WITH_NOTE (same provenance note) |
| GL1 3x4 r=27 | [22.12, 31.20] NOT_RESOLVED | [21.563, 50.838] NOT_RESOLVED | CONFIRMED |
| GL3 3x3 r=27 | [9.044103, 9.095315] | [9.044105, 9.095313] | CONFIRMED |
| GL3 3x3 r=81 | [9.006863, 9.008560] | [9.006863, 9.008560] | CONFIRMED |
| GL3 3x4 r=27 | [9.012197, 9.129277] | [9.012197, 9.129277] | CONFIRMED |
| GL3 3x4 r=81 | [9.006059, 9.009521] | [9.006059, 9.009521] | CONFIRMED |

## Exterior floor (DERIVED, plus MEASURED checks)

1. **Parity.** The plaquette product is a commutator, so it is even, and the number of transposition plaquettes is even. Hence M ∈ {0, 3, 4, 6, 7, …}. The M=0 and M=3 sets are complete by census, so the complement C splits as C4 ∪ C6+.
2. **The M=4 block.** A_44 ≥ N3 + 4r − rho44, by Gershgorin on the count matrix c(x→y), which is similar to the symmetric form. rho44 counts self-moves.
3. **The M≥6 block.** D ≥ 6r. This block holds every state with M ≥ 5 together with all the electric mixing among them, because E is positive semidefinite and so is its restriction (each link's spectrum is {0, 3, 6}). This is how states with M ≥ 5 are covered.
4. **The coupling block.** ‖B‖² ≤ ρ(Q) ≤ P2max, where Q is the two-step path-count matrix M4 → M≥6 → M4, similar to B W⁻¹ Bᵀ. This bounds the electric mixing between M=4 and the exterior.
5. **Schur test.** If (α − λ)(β − λ) ≥ ‖B‖², then H_CC ≥ λ on all of C. This is the whole physical complement, not only the ball.

Measured checks:
- **My own census agrees with group theory:**
  - M=0: 8 orbits.
  - M=3: 27 orbits on 3x3 and 36 on 3x4 (3F, all free).
  - M=4: 720 on 3x3 and 1320 on 3x4, i.e. 20·C(F,2), with 4 size-3 orbits and 16 free orbits per plaquette pair.
  - Raw counts: 18, 18F and 108·C(F,2), from Frobenius N(e)=18 and N(3-cycle)=9.
- **Floor inputs:** my rho44, P2max and floor equal the PR's to 6 decimals at all 8 (lattice, r) points.
- **Floor lemma on whole tori:** on the full 1x3 and 3x1 tori (all 251 orbits), neg(K_CC − fl·W) = 0 at r = 9, 27, 81. That is 6 of 6 tests on the whole complement.
- **Weak point, harmless:** the code's `electric_term_psd_gershgorin` check is a tautology (0 ≥ 0). E ≥ 0 is true by representation theory, not by that check.

## Schur and inertia logic

- **Upper side.** The upper bound uses min-max on the injective trial span, so it holds unconditionally.
- **Lower side.** The lower bound is the Haynsworth count, valid because every certified λ satisfies λ < floor (the code enforces this). S(λ) ≥ U − G/(fl − λ) holds because the exact residual is taken over every C row the trial or P touches.
- **Bisection.** Every reported endpoint was evaluated directly, so the bisection does not need monotonicity.
- **Level indices.** The indices are whole-space counts, so E1, E8, E9 and W = E8 − E1 are the right levels.
- **Degeneracy.** E9 is separated from E10 on 3x3. On 3x4 at r=81, my E9 and E10 enclosures overlap, so the two levels are near-degenerate there; the count-based index is still correct.
- **Intersected runs.** Each run is a certificate on its own, so taking the intersection is legitimate.
- **Inertia at the PR's endpoints, in my certificate.** All E9 endpoints pass except 3x4 at r=27 and r=81. Where an endpoint fails, my trial is the looser one and my enclosure contains the PR's. No count contradicts the PR.

## Planted faults, run on the PR's own code

| fault | where | PR self-checks | caught by |
|---|---|---|---|
| floor ×1.05 | 3x3 r=243 | PASSED | independent floor recheck: REJECTS |
| P2max ×0.95 | 3x3 r=243 | PASSED | independent floor recheck: REJECTS |
| one dropped M4→M≥6 edge | 3x3 r=243 | PASSED | replay / recompute only |
| E7 reported as E8 | r=243 and r=729 | PASSED both | not caught; the on-file anchor is too wide to separate the levels |
| E10 reported as E9 | r=243 | CAUGHT, by `onfile_E9_zero_momentum_anchor_3x3` | own check |
| E10 reported as E9 | r=729 (no anchor) | PASSED | not caught; the GL1 verdict would still read MET |

## Blind order and scope

- **Commit order: MEASURED.**
  - 32ebe74 is the parent of b3eeca0.
  - The first 45 lines of the b3eeca0 measurement file are byte-identical to the 32ebe74 file.
  - The block hash is 755767ce….
  - `gl_derive measure` and `gl_derive compare` both regenerate their files byte-identically.
- **Frozen files.** The frozen file's sha is 93350dd4… at all 5 commits. The erratum's sha is c358974c… from 26756c9 onward.
- **Push order: CANNOT_SEE.** GitHub has no push event and no check run for 32ebe74. The PR was opened at 13:06:42Z, after both commits.
- **Scope.** The PR touches no zgap2 path. GL2 and 4x4 appear only as NOT_MEASURED rows.

## Files

These are in C:/tmp/opus55/gl159-refute/:
- my code: `indep_gl.py`, `fullspace.py`, `rederive.py`, `plant.py`, `build_refute_hbp.py`;
- the runner scripts: `replay.sh`, `plant_run.sh`, `small_run.sh`, `indep_batch.sh`, `derive_replay.sh`, `blind.sh`;
- the output folders: `replay/`, `indep/`, `plant/`, `small/`.
