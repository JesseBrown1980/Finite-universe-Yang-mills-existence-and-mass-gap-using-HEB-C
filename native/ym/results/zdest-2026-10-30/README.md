# zdest: z pulled instantly from the destination, light at c = 1 (2026-10-30)

Operator-authorized ("Think, then test again, then push results to github"). The predictions
were sealed in `PREREG.hbp` (`8f4ec5e9…`) before any code. Rust 1.81, clippy `-D warnings` exit 0,
integer only, json=0.

**Statement under test (operator):** "No quantum data can leave at c without having z pulled
instantly from its destination at n instant … Anything in the matrix even if locality is
considered should not be affected. 1 matrix, 1 universe regardless."

**Model.** The zlight lattice: a 64×64 torus of canonical trits, a local linear GF(3) rule, c = 1.
- The source S = (20,32) fires at step 0.
- Destinations D1 = (40,32) and D2 = (20,52), each 20 steps from S.
- **RULE (operator's):** z = sha256(global root ‖ destination token). The token is pulled at
  step 0, before emission, and pulled again when the destination is switched. The pull writes no
  cell.
- **BOOKKEEPING (control):** z = the global root only.
- The switch from D1 to D2 happens at step 5, before light reaches either destination.

| prediction | result |
|---|---|
| M1: under RULE, z changes at step 0 and follows the switch instantly at step 5 | held: 0, then 5 |
| M2: under BOOKKEEPING, z cannot see the switch | held: never differs |
| M3: the pull and the switch change no cell (every grid identical across all four laser runs, at every step) | held |
| M4: locality: every cell beyond distance t from S equals the no-laser control at step t | held: 0 violations |
| M5: each destination's own cell changes only when light arrives | held: step 20 for D1 and for D2 |
| M6 (rank check of another seat's claim): J has rank 1 mod 3; I + R − R² and I − R + R² have det 4, which is 1 mod 3, so both are invertible | held |

**Reading.**
- A z pulled instantly from the destination can coexist with light at c = 1 in one matrix, with
  no cell anywhere disturbed: "1 matrix, 1 universe, nothing affected" holds in this model.
- Switching the destination shows in z at once and nowhere in the matrix. Plain bookkeeping
  cannot see the switch, so the rule is distinguishable from bookkeeping.
- The curved j (either direction) is invertible mod 3, so no input pattern is lost. The
  symmetric J collapses everything to rank 1.
- **Scope:** this shows the rule is consistent with locality in software. It does not show that
  physics requires it. The rule defines z to include the destination, so M1 is by construction;
  the substance is in M2–M5.

**Chain:**

| layer | file |
|---|---|
| HBI | `ZDEST.hbi` |
| HBP | `PREREG.hbp`, `RESULT.hbp` |
| SHA | `SHA256SUMS`, `*.hbp.sha256` |
| SH | `run.sh` |
| HASH | `ZDEST.seal` |

The source reaches `tribit/mod.rs` and `torusl/src/sha.rs` through absolute `#[path]`s on the
acer host; their hashes are in `RESULT.hbp`.
