# 3×3 full space at r = 9: certify result (run 40725530804, erratum 1)

**`CERTIFY_VERDICT|PASS|N_full_t1=8|N_full_tF=8`**, issued after
`CERTIFY_CORRECTNESS|CERTIFIED|depths=0-4|nodes_green=340|seal=1|http0=1`.

- **Receipt.** `CERTIFY-3X3-FULLSPACE.hbp`; its `.sha256` sidecar verifies.
- **Workflow.** Commit `a5a991f`, generated with `SPLIT = 100`, `COLS = 60` (erratum 1).
- **Stage B inputs.** Runs 40392589541 and 40392589603, admitted all-or-nothing.

## The chain, in the frozen order

| step | receipt lines | result |
|---|---|---|
| seal integrity | `SEAL` ×3 | both `PART-n` checksums match and `sealed_pass=1`; shard integrity `PASS`; coverage 32 of 32 finals |
| HTTP-0 | `HTTP0` | 50 of 50 watcher jobs, accounting and order `PASS`, one server binary `838bb005…` |
| depth 4 | 16 `NNEST` | 16 of 16 sectors rebuilt equal to the stage A record, with matrix hashes |
| depth 3 | 280 `NNEST` | 260 of 260 cells: receipt hash and input-matrix hash match. 20 of 20 merges: exact column partition. Both sampled cells re-executed **byte-identical** (`tdcountcols/3/3/1/1/…/0/60`, `tacountcols/3/3/1/-1/…/1260/1320`) |
| depth 2 | 32 `NNEST` | 32 of 32 finals re-executed byte-identical: `ambiguous=0`, `result=PASS`, children green |
| depth 1 | 10 `NNEST` | at each threshold, all five kernels `T`, `tx`, `ty`, `td`, `ta` report 8, equal to the watcher's sum of sectors |
| depth 0 | 2 `NNEST` | at t1 and at t_F: reported 8 = watcher Möbius 8; isotypic counts nonnegative; symmetric lines equal; dimension 10,097,891 = gauge orbits 10,097,891 |
| correctness | `CERTIFY_CORRECTNESS` | `CERTIFIED`, 340 nodes green, nothing held |
| verdict | `CERTIFY_VERDICT` | `PASS`, (N_full(t1), N_full(t_F)) = (8, 8) |
| budget (separate) | `CERTIFY_BUDGET` | `BUDGET_PASS`: 84,877 s certify against 1,699,491 s stage B, 49‰ against the 500‰ bound |

## Bindings

- **Admission.** `CERTIFY_ADMISSION` records the admitted-file hash `c8f390ac…1d15`. It is
  the same as the earlier run and the local dry run. It also records both manifest hashes
  and `ADMIT_TOTAL … result=PASS`.
- **Plan parameters.** `CERTIFY_PLAN_PARAMS` records `split=100|cols=60` and erratum 1 at
  SHA-256 `8c63afff…62e6`, which is the erratum as committed at `a5a991f`. The outcome
  section was appended to that file later, in `daf6f15`. It also records the generator,
  `full_space_certify.py` and `certify_admit.py` hashes, and workflow commit `a5a991f`.
- **Identity.** `CERTIFY_IDENTITY` records the stage B runs, the core-table and stage A
  hashes, the server binary, the request cap and the code and spec hashes.

## What is certified (exact integer arithmetic, fixed 3×3 lattice, full physical space)

These are the statements fixed in `STAGE-B-SPEC.md`, given `PASS`:

- **At r = 9.** E₈ < t1 = 52.533422 J_E and E₉ ≥ t_F = 71.900000 J_E, so
  **E₉ − E₈ > 19.366578 J_E** over the full 10,097,891-dimensional physical space.
- **For all r ≥ 9.** E₉(r) is non-decreasing in r, so E₉(r) ≥ 71.9. The eight flat states
  bound E₈ ≤ 54 (3·2·3·3). So **E₉ − E₈ ≥ 17.9 J_E**.

## Independent cross-checks (shadow evidence, not part of the seal)

- **Orbit count.** The gauge-orbit count 10,097,891 by exact #SAT agrees with the
  dimension reconciliation.
- **Column partitions.** All 20 merges have checked UNSAT proofs of exact column coverage:
  part 2 on 2026-10-27, part 1 on 2026-10-28.
- **Earlier run.** Run 40688572522 used the same admitted inputs with the defective
  100-column plan. Its verdict was `INCONCLUSIVE`, recorded in advance. Its 16 sectors,
  260 cells and 32 finals re-executed byte-identical to stage B, as they did here.
