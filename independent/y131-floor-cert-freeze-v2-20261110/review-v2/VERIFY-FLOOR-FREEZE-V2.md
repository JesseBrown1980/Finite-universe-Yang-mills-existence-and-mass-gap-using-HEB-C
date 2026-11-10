# Verification of floor-certificate freeze version 2 (cfc57bef)

The authoritative record is `VERIFY-FLOOR-FREEZE-V2.hbp`, with its sha256 in the `.sha256` sidecar. Nothing was run at r = 9 or within 1 of it, and the launcher was never started in default mode.

**Verdict: HOLD.** The scope, build, clippy, regression, row record, E3, no-float gate and lint all reproduce. Three launcher defects remain, and each fix edits a pinned file, so each one needs a new freeze:

1. **PASS semantics (reviewer blocker).** A falsified prediction prints `result=PASS|comparison=BELOW_FALSIFIED_H4`. This was seen in runs A3 and BU_plus. The boundary inequalities are already exact (floor_eval.py:497-498): g0 = G_max gives ABOVE, and g0 = U_min gives UNDECIDED. The output format at floor_eval.py:609-667 and run_floor.sh:10,40,47,193-195 has to change, and so do record rows 116 and 008.
2. **Machine-wide kill (reviewer blocker).** run_floor.sh:107 runs `pkill -KILL -x floorcert`. In run L5 it killed an unrelated process named floorcert. GNU `timeout` already signals its own process group, and `peak_rss.py` stays in that group (run pg.sh). The fix is to delete line 107, or to run the command as `setsid timeout ... &` and then `kill -KILL -- -$cpid`.
3. **Gate script swap after the pin check (new).** In run L1, `gate_required.sh` was replaced after pin check 1 by a script that only replays old logs. The run still ended in PASS with 2 accepted certificates, and no verifier was executed. The fix is to hash the gate, the verifier, `peak_rss.py` and the evaluator before each use, and to run a closing pin check before any PASS.

These were refused correctly: 12 offline evaluator faults and 6 more live faults. Each ended in FAIL or UNRESOLVED with 0 accepted certificates. The single rerun of row 008 is enforced (L6), and UNRESOLVED is reachable (A1, BG_plus, BU_eq).

Lower-severity findings:
- **2 GB versus row 006(b) (medium):** a process that finishes over 2 GB ends in FAIL, although row 006(b) calls that case operational and allows a fallback.
- **An empty `--test-r` value would start the default r = 9 run (low).** This was found by reading the code, not by running it.
- **Verifier exit 1 is read as a refusal (low).**
- **Row 034 depends on a remote-only commit (low).**
