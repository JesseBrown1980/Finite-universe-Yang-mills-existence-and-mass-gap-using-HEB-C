# CERTIFY-SPEC erratum 1: the stage B split was SPLIT = 100, COLS = 60

**Version 1, 2026-10-28.** Published before the corrected certify attempt is launched.
Read together with `CERTIFY-SPEC.md` addendum 3.

## The error

The 3×3 stage B parts (commit `39f0de1`, runs 40392589541 and 40392589603) were generated
with `SPLIT = 100` and `COLS = 60`. The certify specification, however, says
`SPLIT = COLS = 100`, and the certify workflow called `full_space_certify.py plan` and
`assemble` without split arguments, so both defaulted to 100. The frozen certify
execution plan therefore did not describe the admitted stage B cells.

## Consequence for run 40688572522

That run used the 100-column plan, so it is **not eligible for `PASS`**. Its verdict is
`INCONCLUSIVE`: a defect in the certify step's own plan, not a mathematical `MISMATCH`.
It was left to finish for its diagnostic record.

## The correction

- **Parameters.** `SPLIT = 100` and `COLS = 60` are now passed explicitly at **both** call
  sites, the watcher `plan` and the final `assemble`. The generator refuses to run
  without them.
- **Sample.** The two sampled cells are re-selected by the unchanged hash rule over the
  admitted 60-column cells:
  - `tdcountcols/3/3/1/1/1000/9000/71900000/12/1000/0/60`
  - `tacountcols/3/3/1/-1/1000/9000/71900000/12/1000/1260/1320`
- **Unchanged.** Both stage B run IDs, the frozen admission manifests, admission itself,
  the thresholds (t1 = 52.533422, t_F = 71.900000), the sector rules, every N-Nest gate
  and the verdict arithmetic. Neither sealed part is re-run.
- **Not byte-identical.** The corrected workflow differs from the frozen execution plan in
  three ways: the two sampled cells, the `assemble` arguments, and one added receipt line
  (`CERTIFY_PLAN_PARAMS`). That line binds the split, this erratum's SHA-256 and the
  hashes of the generator, `full_space_certify.py` and `certify_admit.py`.

## Controls, run before any aggregation (`certify_plan_check.py`)

The check reads the frozen manifests and only the `MERGE_INPUT` lines of the 20 admitted
sealed merges. No count field is read.

| control | job set vs admitted (292 specs) | sampled cells admitted | 20 merges' cell lists | verdict |
|---|---|---|---|---|
| `(100, 100)` | 195 specs, 161 only in the plan, 258 only admitted | 0 of 2 | not equal | **FAIL** (receipt `CERTIFY-PLAN-CHECK-100-100.hbp`) |
| `(100, 60)` | 292 specs, equal | 2 of 2 | 20 of 20 equal, in order | **PASS** (receipt `CERTIFY-PLAN-CHECK-100-60.hbp`) |
