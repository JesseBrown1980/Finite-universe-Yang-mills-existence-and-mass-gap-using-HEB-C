# Final-head verification, floor certificate freeze v2 (3b91d1a0)

Authoritative record: `VERIFY-FLOOR-FREEZE-V2-FINAL.hbp` (sha256 in sidecar). Nothing ran at r = 9 or within 1 of it; `--launch-r9` was never passed.

**Verdict: HOLD.** Scope, build (1.81, clippy exit 0, binary 9533e7e9 = row 016), PREDICT rows, the 11-row account, no-float gate and lint all reproduce. The original swap (L1) now fails (Y1). But four new attacks end CERTIFICATE=PASS: three without running the verifier (T1, T2, T3) and one with a fabricated final line (T4). Requirement C is therefore only partly met, and the record does not disclose this residual.

- T1 (HIGH): a `python3` placed in `$HOME/.cargo/bin`, which run_floor.sh:29 puts first in PATH, answers the gate. No race and no hashed file changed.
- T3/T4 (HIGH): hash-then-exec TOCTOU on the private copies. The run is as root, so the copies' read-only mode has no effect. Self-restoring swaps pass every guard and the closing check.
- T2 (MEDIUM): `BASH_ENV` bypass.
- PQ (MEDIUM, disclosed in row 122): a rows-only verifier that completes at or over the limit ends PASS/UNRESOLVED, not RESOURCE_LIMIT_EXCEEDED.
- LOW: a `/../` test-out path writes inside the freeze folder (T7d); exit code 2 is shared between FAIL and UNRESOLVED.
