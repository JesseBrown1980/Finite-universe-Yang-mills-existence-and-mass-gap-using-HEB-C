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

## Addendum, fixed before the certify step runs (reviewer, 2026-10-27)

**Correctness and cost are separate results.**

| result | what it depends on |
|---|---|
| `CERTIFY_CORRECTNESS\|CERTIFIED` | seal integrity, the HTTP-0 request accounting, and every node at depths 0–4 green with nothing held |
| `CERTIFY_VERDICT` | the stage-B verdict of `STAGE-B-SPEC.md`, issued only after CERTIFIED |
| `CERTIFY_BUDGET` | `BUDGET_PASS` or `OVER_BUDGET` |

The budget is an operational wall-clock check (certify runner time ≤ ½ × stage-B runner
time). It can block production acceptance, but it never changes a computed count. It
is kept apart from the structural work bound `C₀ / (1 − q)`, which describes how the work
shrinks level by level and is not a timing claim.

**Identity.** The receipt carries `CERTIFY_IDENTITY`:

- both stage-B run ids;
- the SHA-256 of the core table and of stage A;
- the HTTP-0 server binary hash and the request cap;
- the SHA-256 of `CERTIFY-SPEC.md`, `STAGE-B-SPEC.md`, `full_space_certify.py`,
  `full_space_mobius.py`, `full_space_workflow.py`, `verify_shard_integrity.py` and
  `http0_jobs.sh`.

A verdict is tied to the rules and code that produced it.

**Coverage, stated exactly.** Depth 3 is a universal hash and partition check on every
cell, plus **two** full cell regenerations chosen by the frozen hash rule. It is not an
independent replay of every cell. The receipt line `COVERAGE` records the count of cells
checked, the rule and the selected cell ids.

**The request cap fails closed.** `scripts/http0_jobs.sh` refuses any plan over the cap
of 10,000 requests, refuses a server that does not start, and records the requests
planned and completed, together with the server's exit status. The assembly requires,
for every one of the 50 watcher jobs:

- a record;
- `completed = planned`;
- exit 0;
- one server binary across all jobs;
- the job's sector sent before its count in the same server run.

Anything else is `NOT_CERTIFIED`.

**Clean roots.** Every watcher starts from an empty root on a fresh runner. The 2×2 test
starts from an empty working directory and proves sector-before-count ordering from its
own job log (control C5), not from the presence of final files.

**2×2 test after the addendum** (`CERTIFY-TEST-2X2.hbp`): C1–C8 PASS, covering the clean
tree, the rerun, a missing shard, faults at depths 1–4, the run's own order, tampered
request accounting, a plan over the cap and a server that fails to start. 186 jobs ran,
all through `scripts/http0_jobs.sh`.

## Addendum 2: input admission, fixed before the certify step runs (reviewer, 2026-10-28)

Part 1 sealed (run 40392589541: 239 cells, 13 merges, `GITRAM_SEAL … status=PASS`). Part
2 had already sealed (run 40392589603: 33 cells, 7 merges). No 3×3 stage B count had
been aggregated or evaluated for a verdict when this addendum was written. **Nothing in
the mathematics changes:**

- **Thresholds and rules.** t1 = 52.533422 and t_F = 71.900000 stay as they are, as do
  every sector and dimension rule and every symmetric-line and N-Nest gate.
- **Code.** The watcher shell code and `full_space_certify.py assemble` are byte-identical
  to those frozen above.
- **Verdict.** `PASS` iff `(N_full(t1), N_full(t_F)) = (8, 8)` and every gate passes.
  Missing, malformed, duplicated, timed-out or unverified evidence is `INCONCLUSIVE`.
  Only a fully computed, unexpected pair is `MISMATCH`.

What is added is how the inputs are admitted.

**Frozen manifests (metadata only, no content read).** The two files are
`CERTIFY-ADMIT-MANIFEST-PART1.hbp` and `CERTIFY-ADMIT-MANIFEST-PART2.hbp`, each with its
own `.sha256`. They are written by `certify_admit.py manifest` from the GitHub API
listing of each run.

- **What each records.** For every artifact: its artifact ID, size, raw-ZIP SHA-256 and
  expected identity, taken from the part workflow's own matrices.
  - `cell-NNN` maps to its cell shard and the count it belongs to.
  - `merge-mNN` maps to its merge shard.
  - `sealed-part-n` maps to `PART-n.hbp`, `PART-n.sha256` and the final shard of every
    count of that part.
- **Part 1.** 253 artifacts: 239 cells, 13 merges, 13 finals.
- **Part 2.** 41 artifacts: 33 cells, 7 merges, 19 finals.
- **Totals.** 272 cells, 20 merges and 32 finals, with zero problems in either part. Both
  parts are from head `39f0de1`.

**The `admit` job, which runs first and computes nothing.**

1. **Frozen and fresh.** It checks both manifests' SHA-256. Fresh API metadata must
   reproduce each manifest byte for byte. It then downloads every artifact by ID, with
   bounded retries.
2. **Phase 1, before any extraction.** Each part directory holds exactly one
   `<artifact_id>.zip` per manifest entry and nothing else. Every size and raw SHA-256
   matches.
3. **Phase 2a, still no extraction.**
   - Every ZIP passes `testzip`.
   - Every ZIP has exactly its expected members: five files per shard, plus `PART-n.*`
     for a sealed part.
   - Shard identities are unique across both parts.
   - The totals are exactly 272, 20 and 32.
4. **Phase 2b, extraction into a clean root.**
   - Every `spec` names its shard.
   - Every `PART-n.sha256` verifies, and each part's last line is `GITRAM_SEAL … status=PASS`.
   - Every merge artifact equals the sealed final shard of the same ID, byte for byte.
   - Cells go to `cells/<count id or _unsplit>/`, sealed parts to `parts/`.
   - The SHA-256 of every extracted file is written to `ADMIT-FILES.sha256`.

Any failure stops the job, and nothing downstream can be certified.

**Consumers use admitted bundles only.**

- **Finals.** A final re-executing a merge downloads only `admitted-cells-<its count>`.
  It must pass `certify_admit.py check` against `ADMIT-FILES.sha256`: exactly the
  admitted files, each with its admitted hash.
- **Assemble.** It requires `needs.admit.result == success`. It downloads
  `admitted-parts` and every `admitted-cells-*`, and checks both the same way before
  `assemble` runs.
- **Sectors and sampled cells.** These are rebuilt from their specs and consume no stage B
  input.

**Receipt.** `CERTIFY_ADMISSION` adds three things: the SHA-256 of `ADMIT-FILES.sha256`,
both manifest hashes, and `ADMIT_TOTAL`.

**Controls.** `certify_admit_controls.py` runs on synthetic artifacts, with no real data:
**24 of 24 pass.** Each mutation must stop with its named reason, before
`ADMIT-FILES.sha256` exists.

| group | cases |
|---|---|
| admission | wrong digest, wrong size, missing artifact, unexpected artifact, corrupted ZIP (CRC), missing member, spec identity, `PART` checksum mismatch, `PART` not `PASS`, merge differing from its sealed shard, wrong totals, duplicate shard across parts |
| manifest | expired, wrong run, duplicate ID, unexpected name, missing name |
| consumer check | tampered file, extra file, missing file |
| baselines | admission; one group; all groups merged; parts |

**Generator diff.** Against the generator on `main`, given the same inputs:

- every watcher step (16 sectors, 32 finals, 2 samples) is identical, and the job matrices
  differ only by the added `grp` field;
- the `assemble` step is identical except for the appended `CERTIFY_ADMISSION` line;
- the old `cell-*` and `sealed-part-*` downloads by run ID are replaced by admitted bundles.

**SAT shadow, run independently.** `shadow/sat/partition_sat.py` runs on part 1's 13
sealed merge shards. They come from an admission of the same frozen manifests, run
separately from the certify workflow. Glucose 4 produces the UNSAT proofs and
drat-trim `2e3b2dc` checks them. The shadow is a cross-check, not part of the seal. A
disagreement with the primary chain triggers reconciliation, never selective acceptance.

## Addendum 3: a split-parameter defect, recorded before run 40688572522 finishes (2026-10-28, 16:05 UTC)

This was found while the certify run was in progress, before its `assemble` job had
started. No certify receipt existed, and no 3×3 full-space count had been aggregated or
evaluated for a verdict.

**The defect.**
- **Stage B's split.** The stage-B part workflows (`39f0de1`) were generated with
  `SPLIT = 100` and **`COLS = 60`**, as the commit message of `39f0de1` says: "60 columns
  per cell".
- **The certify step's split.** This spec, and the certify workflow generated from it,
  use `full_space_certify.py plan` and `assemble` with their defaults, `SPLIT = COLS = 100`.
  The sentence under "Inputs" saying `SPLIT = COLS = 100` "gives 272 cells … matching the
  two generated part workflows exactly" is wrong.
- **Checked by recomputation from the sealed core table.**
  - With `(100, 60)`, the plan's 292 job specs (272 cells and 20 merges) **equal the two
    part workflows' 292 specs exactly**.
  - With `(100, 100)`, the plan has 195 specs and does not match.

**What it does to run 40688572522 (stated before its receipt exists).**
- **Depth 3 fails closed.** For every merged count, `assemble` compares the sealed
  `MERGE_INPUT` cell list, which is 60 columns wide, with a 100-wide expected list. Every
  partition node therefore fails, and the verdict **must be `INCONCLUSIVE`**: a defect in
  the certify step's own parameters, not a mathematical `MISMATCH`.
- **The sampled cells don't exist.** The two cells sampled under the 100-wide plan,
  `tdcountcols/…/0/100` and `countcols/…/300/389`, are not stage-B cells, so their
  re-executions cannot be compared with anything.
- **What stays valid.** Admission, the sector rebuilds and the final re-executions are
  unaffected. The final re-executions take their cells from the admitted stage-B cell
  shards, not from the plan.

**The correction (frozen now, before any count is read).**
- **Split.** `SPLIT = 100`, `COLS = 60`, passed explicitly to `plan` and to `assemble`.
- **Sample.** The two cells are re-selected over the **real** cells by the unchanged rule,
  the smallest `SHA-256("CERTIFY-3X3-V1|" + cell spec)`:
  - `tdcountcols/3/3/1/1/1000/9000/71900000/12/1000/0/60`
  - `tacountcols/3/3/1/-1/1000/9000/71900000/12/1000/1260/1320`
- **Everything else unchanged.** Thresholds, gates, the verdict rule and admission are
  untouched.

A corrected certify run, the same workflow generated with `(100, 60)`, is launched only
on the operator's approval. Run 40688572522 is left to finish, and its verdict is
recorded as it comes out.
