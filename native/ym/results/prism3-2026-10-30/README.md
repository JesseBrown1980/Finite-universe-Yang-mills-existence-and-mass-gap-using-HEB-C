# prism3: hash-selected curved j through three prisms (2026-10-30)

Operator-authorized ("j curves based on universal hash and particles that approximate before
travel based on laser. Try the test with prisms x 3"). This is an independent Rust 1.81,
integer-only replication beside PR #43 (Python).
- Predictions were sealed in `PREREG.hbp` (`96447279…`).
- A pre-run addendum (`ADDENDUM-PRERUN.hbp`, `32f1d399…`) was sealed after the predictions and
  before any code. It records a P6 error found on review and the event order at step 1. The
  original predictions are unchanged.

**Model.**
- Source plus 3 prism stages: 1 + 3 + 9 + 27 = 40 balanced-trit cells.
- Prism k splits a beam into (stay, forward, back) with the curved j:
  j+ = (+1, +1, −1) or j− = (+1, −1, +1).
- The choice at prism k is bit k of z = sha256(laser ‖ destination ‖ world root at step 0).
- 54 configurations: 2 laser signs × 27 destinations.
- **LOCKED:** the curve directions are fixed at emission ("approximate before travel").
- **LIVE:** each prism reads the z in force when the beam arrives.
- The destination switches at step 1.

| prediction | result |
|---|---|
| P1: occupancy 1, 3, 9, 27 per step, nothing early | held |
| P2: the forecast at step 0 (from z alone) equals the propagated 27 amplitudes | held, 54/54 |
| P3: all 8 combinations of curve direction occur | held, 8 |
| P4: all final amplitudes nonzero | held |
| P5 LOCKED: z follows the switch at step 1, and the travelling beam is unchanged | held |
| P5 LIVE: the beam is redirected exactly when the switched z flips a later prism's curve, with 0 locality violations | held: 41 of 54 redirected, 0 violations |
| P6: the destination's own cell carries zero information before arrival | held: 1 distinct state |
| P6 original: 54 distinct forecasts | **FAIL: 16** (2 signs × 8 directions). Predicted to fail in the addendum; kept as written |
| P6 addendum: 54 distinct z values | held |
| P7: a stored classical 3-bit table reproduces the hash-selected run exactly | held, 54/54 |

**Reading.**
- With directions **locked at emission**, the particle's whole path is set before travel and can
  be forecast at step 0. Changing the destination afterwards changes z but not the beam.
- With **live** reading, a destination switch redirects the beam, but only at prisms the beam
  has not reached yet, and only at c = 1. Nothing changes early anywhere.
- **The limit, measured (P7):** in a deterministic simulation, hash selection is exactly a
  classical 3-bit controller. Showing that hash-selected j does something no classical
  controller can would need a Bell/CHSH-type statistical test, not more prisms.

**Chain:**

| layer | file |
|---|---|
| HBI | `PRISM3.hbi` |
| HBP | `PREREG.hbp`, `ADDENDUM-PRERUN.hbp`, `RESULT.hbp` |
| SHA | `SHA256SUMS`, `*.hbp.sha256` |
| SH | `run.sh` |
| HASH | `PRISM3.seal` |

No JSON. The source reaches `tribit/mod.rs` and `sha.rs` through absolute `#[path]`s on the acer
host; their hashes are in `RESULT.hbp`.
