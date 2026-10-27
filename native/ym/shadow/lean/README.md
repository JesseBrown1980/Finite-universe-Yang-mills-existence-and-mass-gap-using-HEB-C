# Shadow stack, layer 1: Lean

Machine-checked logic behind the Yang–Mills receipts. Core Lean 4 only (no Mathlib), so
the trusted base is the Lean kernel. The toolchain is pinned in `lean-toolchain`.

| theorem | file | statement |
|---|---|---|
| `admission_12GiB` | `HebcShadow/Admission.lean` | if every admitted block uses ≤ `col`, the rest uses ≤ `reserve`, and the admission rule is enforced, then total usage ≤ 12 GiB, for any sequence of arrivals and completions |
| `countmerge_conserves` | `HebcShadow/Partition.lean` | cells whose column boundaries run nondecreasing from 0 to the core size add up to the whole count, for any per-column contribution |
| `gap_r9` | `HebcShadow/Gap.lean` | sorted eigenvalues and counts (8, 8) at (t1, t_F) = (52,533,422, 71,900,000) milli-J_E ⇒ E₉ − E₈ > 19,366,578 |
| `gap_all_r` | `HebcShadow/Gap.lean` | E₉(r) ≥ E₉(9) ≥ 71,900,000 and E₈ ≤ 54,000,000 ⇒ E₉ − E₈ ≥ 17,900,000 |

`bash audit.sh > LEAN-AUDIT.hbp` builds everything, hashes the sources, and records each
theorem's axioms (`#print axioms`). It passes only if no `sorry` appears and no axiom
beyond Lean's standard three (`propext`, `Quot.sound`, `Classical.choice`) is used.

These theorems formalize what the receipts' logic claims. They do not re-run the
production computation. The production counts and the frozen gates still decide
certification, as the shadow stack's order requires: AI proposes, SAT and #SAT
challenge, Lean verifies the logic, and the deterministic receipts decide.
