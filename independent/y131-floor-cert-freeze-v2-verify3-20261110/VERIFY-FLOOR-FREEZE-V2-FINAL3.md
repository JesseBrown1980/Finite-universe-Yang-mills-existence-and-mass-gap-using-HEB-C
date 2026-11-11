# Floor freeze v2: third final-head check (78c89c31)

The full record is `VERIFY-FLOOR-FREEZE-V2-FINAL3.hbp`; its sha256 is in the sidecar file. Nothing was run at r = 9 or within 1 of it, and `--launch-r9` was never passed.

**Verdict: PASS against the reviewer's boundary. No HIGH findings.**

## Attacks that are now rejected

I reran every earlier attack with my own scripts:

| Attack | Result |
|---|---|
| L1 | integrity FAIL, exit 1, 0 certificates |
| T1 | not effective: PATH is fixed and no planted program was called |
| T2 (also `ENV`, `LD_`, `PYTHON` variables, exported functions) | refused before start, exit 4 |
| T3 | the tools tmpfs is not visible from the host (ENOENT), or is read-only through `/proc/PID/root` (EROFS) |
| T4 | the evaluator runs from memory; a changed tree copy gives integrity FAIL |
| PQ | RESOURCE_LIMIT_EXCEEDED, exit 1 |
| T7d | refused, exit 4 |

Exit codes are 0, 3, 2, 1 and 4 as documented. In V4 the step whose verifier crashed is set aside.

## New attacks

- Python modules planted in the working folder and the tree: not imported.
- `unshare` blocked by dropping capabilities: refused (exit 4), with no unprotected fallback.
- Git checks: a changed file mode is refused, and a checkout with dubious ownership is refused.
- Pin-free binary built through the launcher: its hash matches row 016.

## Second-environment recheck (row 125)

I ran the recheck from a clean export without reading the launcher's final line. The documented command works. The certificates pass the gate again and the verdict fields recompute to the same values.

## Residuals

- Root entering the launcher's mount namespace (N3) can still get a PASS with one planted gate call. This is outside the reviewer's boundary and disclosed in row 127; the row 125 recheck is the control for it.
- LOW findings:
  - Stage 2 does not check that it runs in its own mount namespace (FS2 shows two tmpfs mounts left on the host).
  - The recheck takes the writer's Ritz value from the receipt.
  - Recheck certificate paths are relative to the run directory, which the rule does not say.
  - The refused-variable list at the start does not cover every bash start-up variable.

## Full-size rehearsal

A full-size m0 11 and m0 12 run on this launcher reproduces the 3b91d1a0 numbers exactly, with census rows 028 and 029 clean. m0 13 at full size was not run.
