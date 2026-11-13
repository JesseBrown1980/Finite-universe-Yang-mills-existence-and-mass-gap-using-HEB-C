# 3×4 floor certificate at r = 9: the weight-word search

**Outcome: IMPROVED BELOW THRESHOLD.** One bounded search over the weight word of the tail layers raised the
lift-free certified lower bound on the 3×4 non-flat space at r = 9 from 94.0673 to **94.0682 J_E**. The frozen
threshold 94.070673 is 0.002473 above it and lies inside the enclosure [94.0682, 94.076549].

The search was directed by the operator on 2026-11-13 and follows a protocol committed before any run
(`PROTOCOL-WORD-SEARCH.hbp`, commit `069b3e8`). The protected r = 9 run of PR #172 was not rerun; its frozen
binary (sha256 `027b0515…f8ba85`) and the pinned verifier were used unchanged.

## Steps and results

| Step | What ran | Result |
|---|---|---|
| Screening | 17 fixed words at cutoff 11, one process each (`screen_m11.sh`, `screen/`) | 17 of 17 recorded, all row checks pass; control 6,5,4,3 reads 94.0485 as in the protected run |
| Selection | Largest cutoff-11 bound (`SELECT.hbp`) | 81,54,36,24,16 at 94.0606; seven candidates were above 94.0485 |
| Confirmation | Winner written as a certificate at cutoff 11 and gated (`confirm_m11.sh`, `confirm/`) | `GATE_REQUIRED\|PASS` at 94.0606 |
| Prediction | `PREDICT-WORD-SEARCH-M13.hbp`, commit `15f8db0`, pushed before the run | word, threshold 94.070673, hashes, command, three fixed outcomes |
| Cutoff 13 | One certificate and the pinned verifier (`run_m13.sh`, `m13/`) | `GATE_REQUIRED\|PASS` at **94.0682**; upper bound 94.076549 |

## Screening table (cutoff 11, units J_E)

| Word | Lower bound | Word | Lower bound |
|---|---|---|---|
| 81,54,36,24,16 | 94.0606 | 2,1 | 94.0474 |
| 4,3,2,1 | 94.0590 | 6,6,5,3 | 94.0473 |
| 9,6,4,3 | 94.0564 | 9,8,7,6,5,4 | 94.0425 |
| 256,192,144,108,81 | 94.0557 | 5,6,4,3 | 94.0421 |
| 3,2,1 | 94.0556 | 10,9,8,7,6,5 | 94.0396 |
| 5,4,3,2 | 94.0534 | 12,11,10,9,8,7,6 | 94.0347 |
| 7,6,5,4,3 | 94.0488 | 12,10,7,3 | 92.9999 (tail cap 93) |
| 6,5,4,3 (control) | 94.0485 | 3,4,5,6 | 27.0000 (tail cap 61.3) |
| | | 32,16,8,4,2,1 | −11.0001 (tail cap −11) |

## Reading

- The winner's gain over 6,5,4,3 is 0.0121 at cutoff 11 and 0.0009 at cutoff 13.
- The search under this protocol is closed: one campaign, one candidate, one cutoff-13 certificate.
- The lift-dependent floor 94.070673 of PR #131 stays as stated. The second-machine check of the protected
  receipt is a separate audit.
- Observation, kept apart from the certificates: bounds move little between cutoffs 12 and 13. This says
  nothing proven about higher cutoffs.

## Check it yourself

From a clone at freeze commit `c8dbcdbf`, in `independent/y131-floor-cert-freeze-v2-20261110`:

```
bash work/design/gate_required.sh <path>/m13/cert_m13_r9_1_f81-54-36-24-16.txt \
  --freeze-commit c8dbcdbf990114292313cbc410a745a14ba0b778 \
  --prediction final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp \
  --prediction-sha256 9f1076dd756d5b3ff3cb7c18974f52ce1c088f23e06ca3077ac05ab66f44f99c
```

The certificate's sha256 is `7ad6e19977796ba4ecd321fdd028156fe57ee7ff782a6aef0aedb0a686c4a6b6`. All files
are listed in `SHA256SUMS`; the summary row file is `RESULT-WORD-SEARCH.hbp`.
