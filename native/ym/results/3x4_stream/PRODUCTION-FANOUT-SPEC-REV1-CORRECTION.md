# Correction beside fan-out spec revision 1, §0 (November 1, 2026)

`PRODUCTION-FANOUT-SPEC-REV1.md` stays frozen and unchanged, and its `.sha256` sidecar still
verifies. Production run 41321108365 was dispatched with that text in place. This note sits beside
it and changes no binary, argument, threshold, column split, tolerance or gate.

## 1. The statement

§0 of revision 1 says that if time grew in proportion to column count, a K = 8 job "would be about
20,246 s against the 21,000 s job timeout". The body of PR #72 says the same. The README goes
further: "under the 21,000 s timeout".

## 2. What was wrong

1. **It compared two different grains.** 20,246 s is twice the control's `secs=10123`, which times
   the `roomschur` step alone. The 21,000 s limit is `timeout-minutes: 350` on the whole `columns`
   job, which also covers checkout, build and store download. That other time measured 444 to 825 s
   on the finished production jobs, so the same doubling on the limit's grain is 20,690 to 21,071 s.
   "Under the timeout" did not follow: it depended on how long the store download took (406 to 789 s).
2. **It doubled the wrong number.** The control has K = 4 but only 3 active columns (column 0 is
   zero; every sweep row in `control/scol-0-4.err` says `active=3`). Production jobs have K = 8 and
   6, 7 or 8 active columns.

## 3. Measured

`roomschur` time is `secs=` in each job's `FANOUT_JOB` row. Whole-job time runs from the job's start
to its end as GitHub records them.

| Jobs | Active columns | `roomschur` (s) | Whole job (s) |
|---|---|---|---|
| Control 0:4, run 41294035019 | 3 | 10,123 | 10,600 |
| 136:137 | 1 | 6,958 | 7,783 |
| 2 jobs at K = 8 | 6 | 13,066 to 14,356 | 13,513 to 14,800 |
| 3 jobs at K = 8 | 7 | 14,837 to 15,303 | 15,281 to 15,748 |
| 12 jobs at K = 8 | 8 | 14,991 to 18,455 | 15,489 to 19,106 |

These cover all 18 jobs. The slowest, job 120:128 (8 active), finished 1,894 s under the limit. Per-job
rows are in `production-41321108365/PRODUCTION-RECEIPT.hbp`.

## 4. What this shows and does not show

- **Less than proportional, on these jobs.** The two 6-active jobs have twice the control's active
  columns and 1.29 and 1.42 times its `roomschur` time. The finished 8-active jobs have 2.67 times
  the active columns and 1.48 to 1.82 times the time.
- **Those ratios are not a growth law.** Each job ran on its own runner. Jobs with the same active
  count differ by up to about 23%, and job 40:48 (8 active) finished before job 72:80 (7 active).
- **The cause is still CONJECTURE.** The reason §0 gives, that a sweep re-reads the whole store
  whatever K is, is consistent with these numbers but was not measured separately.
