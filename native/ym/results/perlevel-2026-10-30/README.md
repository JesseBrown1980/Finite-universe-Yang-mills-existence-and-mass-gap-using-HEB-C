# Per-level test: "instant PER LEVEL, three per level" (2026-10-30)

Operator-authorized ("yes run the per level test"). Rust 1.81, clippy `-D warnings` exit 0,
integer only, HBP + SHA-256, json=0. The predictions were sealed in `PREREG.hbp` (`450f039b…`)
before any code was written.

**Sources** (the operator's dictionary, *the human-based understanding*):
- **r**: "the radius, goes straight there bidirectionally".
- **j**: "the reverse of the radius … the tridirectional curve has to come back".
- **law 4**: "Instant is not always instant — it is instant PER LEVEL, three per level.
  Something must hold each boundary."

**Model.**
- A ring of 3^N sites (N = 1…5, up to 243). Addresses are N base-3 digits (canonical
  `tribit::Zero`), and digit l is level l.
- r steps to both ring neighbours.
- j at level l mixes all three values of digit l at once, using an all-ones 3×3 matrix.
- Reach is the first tick at which a site is nonzero. Values are nonnegative integers, so nothing
  can cancel.

| prediction | result |
|---|---|
| Q1: inside one level (N = 1), r and j both reach everything in 1 tick | held |
| Q2: r needs (3^N−1)/2 ticks: 1, 4, 13, 40, 121 | held, exactly |
| Q3: j needs N ticks: 1, 2, 3, 4, 5. Each site is reached at the level of the highest digit where it differs from the source. After levels 1..l the reached set is exactly the source's block of 3^l. | held, for every source |
| Q4: every j level couples each site to exactly 3 sites | held |
| Q5: j over all levels in sequence equals the all-ones J on 3^N (every entry exactly 1) | held, for every source |
| Q6: ring neighbours across the top boundary (e.g. 80 → 81 at N = 5): r takes 1 tick, j takes N | held: 1 vs 2, 3, 4, 5 |

**Reading.**
- Law 4, made concrete: j is instant within each level, and three per level. Crossing a level
  boundary costs exactly one tick, which "holds the boundary". Across all levels, j becomes the
  global instant layer J.
- r is the light: it travels one site per tick, so it needs up to (3^N−1)/2 ticks.
- They measure different distances. r counts ring distance; j counts level distance.
  Neighbours on opposite sides of a top boundary are 1 tick apart for r and N ticks apart for j.
- **Scope:** this is a mathematical model of the dictionary's words, not a physical claim. Like
  zlight, its results follow from its definitions. The value is that the words are now exact and
  checked.

**Chain:**

| layer | file |
|---|---|
| HBI | `PERLEVEL.hbi` |
| HBP | `PREREG.hbp`, `RESULT.hbp` |
| SHA | `SHA256SUMS`, `*.hbp.sha256` |
| SH | `run.sh` (build, clippy, run, seal) |
| HASH | `PERLEVEL.seal` = sha256(`SHA256SUMS` + `PERLEVEL.hbi`) |

`src/main.rs` reaches `tribit/mod.rs` (`50e4cb85…`) through an absolute `#[path]` on the acer
host.
