# The protected r = 9 floor run: result

Date: 2026-11-13 (UTC). Seat: ACER-CLAUDE-FABLE52 (pid `61089a99becaa89b`), on the word of OP-JESSE
("I give the word now, so you can run out as soon as it's ready to go", 2026-11-12), after the sixth verification
of the freeze (report `13f70e27`, no HIGH or MEDIUM finding; gate D recheck ACCEPT=YES).

The run was made once, from a fresh clone of the freeze commit `c8dbcdbf990114292313cbc410a745a14ba0b778`
(857 of 857 pinned files, record `9f1076dd…f99c`, launcher `ae114b64…187f`), with the frozen command
`bash final/tools/run_floor.sh --launch-r9`. Started 2026-11-12T20:55:11Z, ended 2026-11-13T00:50:17Z, launcher exit 2.

## Verdict line of the launcher

`CERTIFICATE=PASS | PREDICTION=UNRESOLVED | DECISION=UNRESOLVED`

| cutoff m0 | certified lower bound G (max over the three words) | upper bound U | decision after the step |
|---|---|---|---|
| 11 | 94.0485 | 94.109268 | UNRESOLVED, advance |
| 12 | 94.0661 | 94.078052 | UNRESOLVED, advance |
| 13 | 94.0673 | 94.076703 | UNRESOLVED, stop (last allowed step) |

- The prediction tested: lambda_min(QHQ) >= g0, with g0 = 94.070673 (record row 073).
- Rule: G_max >= g0 gives ABOVE; U_min < g0 gives BELOW; otherwise UNRESOLVED.
- At the last allowed step, G_max = 94.0673 < g0 = 94.070673 <= U_min = 94.076703. The certified enclosure
  [94.0673, 94.076703] contains g0, so the run does not decide the prediction. The lower bound stops 0.003373 short.
- All 9 certificates (3 cutoffs x 3 weight words) were accepted by the verifier; every required gate and the closing
  pin check held; no operational failure. PREDICT rows met: 058-071 and 073; row 072 is the open branch.

The run is not repeated and no parameter is changed. What the result is: a certified two-sided enclosure of the
non-flat floor at r = 9 of width 0.009403, and an undecided prediction.

## Files

- `RECEIPT-HASH-PUBLISHED.hbp`: the receipt hash `79e6c40a…daa1`, committed (`3e3ae505`) before the recheck (row 138).
- `run9/`: the receipt, the nine certificates with their core keys, and the launcher's logs, as written by the run.
- `r9.stdout.txt`, `r9.exit`, `LAUNCHED`: the launcher's output, exit code and start time.
- `r9_prepare.sh`, `r9_launch.sh`: the scripts that prepared the clone and made the one launch.
- `recheck-attempt1.txt`, `r9_recheck.sh`: a first call of the checker that omitted `commit=C`; the checker stopped
  with `certificates_rechecked=0` (a usage error of this seat, kept). `r9_recheck2.sh` is the corrected call.
- The recheck output is added when it finishes. By row 143 of the record the checker does not ACCEPT an UNRESOLVED
  receipt as a decision; its certificate rechecks and recomputed fields are what it contributes here.

Scope: the 3x4 S3 lattice, non-flat space, coupling r = 9, cutoffs 11 to 13. Same machine as the launch for the
recheck; a second physical environment has not checked this receipt.
