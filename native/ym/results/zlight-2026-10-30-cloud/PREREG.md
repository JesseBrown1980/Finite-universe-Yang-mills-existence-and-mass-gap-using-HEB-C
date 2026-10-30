# z-versus-light cross-check, pre-registration (frozen before any code runs)

Independent second implementation, written in this container, of the test the acer seat is building.
Integer-only, json=0, Rust 1.81. Nothing here reads the acer implementation.

## Model
- Grid 33 x 33 of u32 cells, all 0 at the start. Horizon: steps 0..=48.
- Laser fires at step 0 from S = (0,16). The beam is a directed front that advances exactly one cell per
  step (c = 1) in its aim direction and leaves its payload value in every cell it has passed (a trail).
- Variants: aim in {east, north} x payload in {1,2,3}, plus a baseline with no laser (7 runs).
- Target T = (32,16), Manhattan distance 32 from S, in the east beam's path; the north beam never reaches it.
- Global layer z: Merkle root (SHA-256, binary tree, last leaf duplicated) over all 1,089 cells, recomputed every step.
- Local layer at T: SHA-256 of T's own cell value only.

## Predictions (each is PASS only on exact integer equality)
- P1 global root differs from the baseline's at step 0 in all 6 laser runs.
- P2 T's local hash first differs from baseline at step 32 for east runs, and never (-1) for north runs.
- P3 before arrival (steps 0..=31) T's local view sequence is identical in all 7 runs:
  distinct sequences = 1, so a local observer at T learns 0 bits about aim or payload.
- P4 after arrival (step 32) T's local view takes 4 distinct values over the 7 runs
  (3 east payloads, and one shared value for north + baseline).
- P5 the global root at step 0 takes 7 distinct values over the 7 runs: the instant layer carries
  everything, but only to a reader of the full state.
Any build failure, missing line or unequal count is INCONCLUSIVE or FAIL, never PASS.
