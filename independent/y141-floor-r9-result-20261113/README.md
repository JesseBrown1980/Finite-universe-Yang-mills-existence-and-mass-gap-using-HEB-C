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
- `recheck/`: the recheck, in two sessions. By row 143 of the record the checker does not ACCEPT an UNRESOLVED
  receipt as a decision; its certificate rechecks are what it contributes here.

## Recheck of the nine certificates

Made in a separate git checkout of the freeze commit `c8dbcdbf`, on the same machine, with the pinned gate
(`work/design/gate_required.sh`, row 020) and the frozen prediction file.

| # | certificate | gate | lower bound read (J_E) | session |
|---|---|---|---|---|
| 1 | m0 = 11, word 1 | PASS | 93.9879 | `recheck2.txt` (the checker `recheck_floor.py`) |
| 2 | m0 = 11, word 8,7,6,5,4 | PASS | 94.0450 | same |
| 3 | m0 = 11, word 6,5,4,3 | PASS | 94.0485 | same |
| 4 | m0 = 12, word 1 | PASS | 94.0620 | same |
| 5 | m0 = 12, word 8,7,6,5,4 | PASS | 94.0661 | same |
| 6 | m0 = 12, word 6,5,4,3 | PASS | 94.0660 | same |
| 7 | m0 = 13, word 1 | PASS | 94.0641 | `recheck3.txt` (the same gate, called directly) |
| 8 | m0 = 13, word 8,7,6,5,4 | PASS | 94.0671 | same |
| 9 | m0 = 13, word 6,5,4,3 | PASS | 94.0673 | same |

- The checker's session (`r9_recheck2.sh`) confirmed the four checkout pins, the receipt hash against the published
  one, HEAD equal to the freeze commit and the nine paths, then passed certificates 1 to 6. The host stopped it for
  low memory during certificate 7 (other jobs of this seat were running beside it; nothing in the checker failed).
- On the operator's word the work was picked up from the certificates, not redone: `r9_recheck3_pickup.sh` ran the
  same pinned gate on the three cutoff-13 certificates, one at a time. Its full gate outputs are the three
  `recheck3.gate_*.txt` files.
- Each of the nine bounds equals the one the launcher recorded. The per-step maxima are 94.0485, 94.0661, 94.0673.
- What this is: nine certificate-level confirmations in two parts. The checker's single closing verdict line was not
  produced, and for an UNRESOLVED receipt it would read ACCEPT=NO by design (row 143).

Scope: the 3x4 S3 lattice, non-flat space, coupling r = 9, cutoffs 11 to 13. Same machine as the launch for the
recheck; a second physical environment has not checked this receipt.
