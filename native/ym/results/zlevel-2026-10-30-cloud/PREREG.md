# zlevel, cloud seat: is j instant per level while r travels? Pre-registration (frozen before any code)

Independent of the acer implementation. Integer only, json=0, Rust 1.81, no dependencies.

## Model
- Lattices of M = 3^N cells, N in {3, 4, 5} (27, 81, 243). Cell index written in base 3 with N digits;
  digit k names the level-k triple a cell belongs to (nested blocks of 3, N levels deep).
- r on the whole lattice (light, "goes straight, bidirectional"): one step = I + R + R^-1 on the ring
  of M cells (each cell reaches its two neighbours). c = 1.
- r inside a level (triangle r): R_0 + R_0^-1, rotation of digit 0 only, cyclic inside each triple.
- j at level k ("tridirectional, curves back"): J_k = I + R_k + R_k^2, the sum over the 3 cells that
  differ only in digit k.
- z cascade: step s applies J_(s-1), so step 1 = level 0, step 2 = level 1, ... step N = level N-1.
- Reach time of (a, b): first step at which the support started at a contains b. Every ordered pair a != b.
- h(a, b): the highest base-3 digit in which a and b differ.

## Predictions (exact integer equality unless stated)
- P1 The nested product J_0 J_1 ... J_(N-1) equals the M x M all-ones matrix exactly: one application of
  every level's j reaches everything.
- P2 z cascade reach time = h(a,b) + 1 for every pair; the maximum is N.
- P3 ring-r reach time = min(|a-b|, M-|a-b|) for every pair; the maximum is (M-1)/2 (13, 40, 121).
- P4 Inside a level (h = 0): triangle r and j both reach every sibling in 1 step (2M ordered pairs).
  Ring r does not: of the 2M sibling pairs, exactly 4M/3 take 1 step and 2M/3 take 2 steps.
- P5 For pairs with h = k: maximum ring-r time = 3^(k+1) - 1 for k < N-1, and (M-1)/2 for k = N-1;
  minimum ring-r time = 1 for every k.
- P6 Boundaries: for every N there are pairs where the z cascade is slower than ring r (z > r), all of
  them with h >= 1 (neighbours across a level boundary), and pairs where z is faster (z < r).
  The counts are measured and reported, not predicted.
Any build failure, missing line or unequal value is FAIL or INCONCLUSIVE, never PASS.
