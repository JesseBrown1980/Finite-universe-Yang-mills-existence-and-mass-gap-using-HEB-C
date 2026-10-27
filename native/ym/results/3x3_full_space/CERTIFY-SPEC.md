# 3×3 full space at r = 9: the certify step (frozen before it is run)

This completes `STAGE-B-SPEC.md`. That spec fixes the thresholds, the counts, the
assembly and the verdict arithmetic, and none of that changes here. This document fixes
how the sealed stage-B parts are certified: what is checked at every node of the N-Nest
tree, by which watcher, and within what budget. It is frozen before the certify step is
run on either part, and before part 1 has sealed.

## Inputs

- **The core table:** `HEBC-YM-3X3-FULLSPACE-CORES-T1-TF.hbp` and its SHA-256, the sealed
  table the stage-B workflows were generated from. Its 32 `CORE` lines are the complete
  list of counts: 16 sectors × {t1, t_F}. Read with the same split rule (`SPLIT = COLS = 100`),
  it gives 272 cells, 20 merges and 12 unsplit counts, matching the two generated part
  workflows exactly.
- **Stage A:** `HEBC-YM-3X3-FULLSPACE-STAGE-A-R9.hbp` and its SHA-256, which records every
  sector shard line by line, including `MATRIX_SHA`.
- **Stage B:** the sealed parts, downloaded by run id. Part 1 is run `40392589541` and
  part 2 is run `40392589603`. Each holds `PART-n.hbp`, `PART-n.sha256` and the final
  shard of each of its counts.
- **Cell receipts:** the cell artifacts of the same runs (`cell-*`), used for the merge
  and sample watchers.

## The tree and its watchers

`node_green = (reported == watcher_recomputed) AND all(child_green)`, as in
`python/nnest_gate.py`. Every watcher below recomputes independently. Each depth names
its watcher.

| depth | node | reported | watcher |
|---|---|---|---|
| 0 | `N_full(t)`, for `t ∈ {t1, t_F}` | `FULL_SPACE_COUNT` from `full_space_mobius.py` | an independent Möbius sum in `full_space_certify.py`, plus the three assembly gates of `STAGE-B-SPEC.md`: isotypic counts nonnegative, dimension reconciliation = 10,097,891 gauge orbits, and the symmetric lines `N(V^{K_x}) = N(V^{K_y})` and `N(V^{K_d}) = N(V^{K_a})`, each line read from its own shards (no `--orbit`) |
| 1 | `N(V^K, t)` for each kernel `K` | `INVARIANT_COUNT` | the sum of the child sector counts, read from the sealed shards |
| 2 | each count's final shard (`*count` or `*countmerge`) | the sealed `run.hbp` | **re-executed** through `hebc_ym_http0` on a fresh runner and compared byte for byte. A merge is re-run from the cell receipts; an unsplit count is re-run from its spec. |
| 3 | each cell of a merged count (`*countcols`) | the cell `run.hbp` | the SHA-256 of the cell receipt must equal the `MERGE_INPUT … hbp_sha256` recorded by the merge, the cells must partition the columns exactly, and a **hash-selected sample** of cells is re-executed and compared byte for byte (rule below) |
| 4 | each sector (`*sector`) | the `INPUT_MATRIX sha256` recorded by its counts | the sector **rebuilt** through `hebc_ym_http0`, its matrix SHA-256 equal to every `INPUT_MATRIX` that cites it, and its `YMSEC` dimensions feeding the depth-0 dimension gate |

**Seal integrity, before any node:**
- every `PART-n.hbp` matches its `PART-n.sha256`;
- its last line is `GITRAM_SEAL … status=PASS`;
- `verify_shard_integrity.py` passes on every sealed shard;
- the parts together hold every one of the 32 stage-A counts exactly once, and nothing
  else.

## The sample of cells (the hash trick)

Re-executing every cell would cost about as much as stage B itself (part 2's cells ran
up to 163 minutes, and the largest cells up to about 2.7 hours each). The sample is the
**two** cells, over all `countcols` cells of both parts, with the smallest
`SHA-256("CERTIFY-3X3-V1|" + cell spec)`. It is deterministic, unbiased by size or
outcome, and fixed by this text before part 1 exists. The rule selects:

- `tdcountcols/3/3/1/-1/1000/9000/71900000/12/1000/0/100`
- `countcols/3/3/1/1/1000/9000/71900000/12/1000/300/389` Every cell, sampled or not, is
still checked by hash at depth 3 and through its merge's re-execution at depth 2.

## Budget, fixed now (the infinite-three bound)

Only the spine is recomputed in full: the merges, the unsplit counts, the sectors and
the sums. The leaves are checked by hash and by sample. By the infinite-three
convergence bound `R_total = B / (1 − q)`, with `q = 1/3`, verification plus production
should cost at most `1.5 · B`, where `B` is the stage-B runner time. So the certify step's
runner time should be at most `B / 2`.

The receipt records both runner times in integer seconds, taken from the job timings,
and the ratio in per mille:
`CERTIFY_BUDGET|stage_b_seconds=…|certify_seconds=…|ratio_permille=…|bound_permille=500`.
Exceeding the bound is reported as `BUDGET_EXCEEDED`. It is a cost flag, not a
correctness gate.

## Verdict

- **INCONCLUSIVE** if any seal-integrity check fails, or any node at any depth is
  `MISTAKE_FLAGGED` or held because a child is missing. A fraction of the tree never
  certifies.
- Otherwise the verdict is exactly the one fixed in `STAGE-B-SPEC.md`: **PASS** iff
  `(N_full(t1), N_full(t_F)) = (8, 8)`, **MISMATCH** for any other computed pair, with the
  bounds and statements written there.

## How it runs

Every watcher job goes through the HEB-C HTTP-0 server (`scripts/http0_jobs.sh`:
`hebc_ym_http0 serve`, then `POST /job/<spec>` and `GET /verify/<spec>`, both PASS). The
workflow is generated by `python/full_space_certify_workflow.py` once part 1 has sealed,
and the verdict is written by `python/full_space_certify.py assemble`.

## Controls (run on 2×2 before the freeze; receipt `CERTIFY-TEST-2X2.hbp`)

| control | what is done | expected outcome |
|---|---|---|
| C1 | clean tree | every node green |
| C2 | rerun the certify job | identical verdict file |
| C3 | remove one sealed shard | `INCONCLUSIVE`, missing node named |
| C4 | plant a one-byte fault at each depth (a count shard, a cell receipt, a sector hash, a sum) | caught at that depth, path named |

**2×2 result** (`python/certify_test_2x2.py`):
- **Setup:** a miniature stage A and stage B with merges forced (`SPLIT = 40`), every job
  through HTTP-0.
- **Outcome:** all controls PASS, and the clean tree certifies (8, 8) at
  t = 23.746649 / 46.576000. That is the same pair the independent verifier agreed on.
- **Workflow code:** the workflow's own watcher shell code, run locally on the 2×2 data,
  reproduced a merge, an unsplit count, a sector and a sampled cell byte for byte.
