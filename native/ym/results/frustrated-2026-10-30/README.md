# Frustrated-orientation benchmark (2026-10-30)

Approved by the reviewer, relayed by the operator: "Frustrated-orientation benchmark: Proceed with
preregistered comparisons."
- Predictions sealed in `PREREG.hbp` (`3b04bdae…`) before any code.
- The wording follows the reviewers: the local bound applies when the controller cannot see the
  settings; otherwise S, signalling and leakage are measured, not presumed.

Rust 1.81, clippy `-D warnings` exit 0, integer only, json=0.

The coupling idea comes from the spin-glass repo (`bea0d4c`). None of its code is reused, so its
`f64` arithmetic and O(M²) transform are not used here.

**Model.**
- The three prism orientations are spins s_k = ±1 (j+ or j−).
- Frustrated couplings J12 = +1, J23 = +1, J13 = −1, frozen before the laser fires.
- Energy E = −Σ J s s − Σ h s.

**Route part** (27 destinations, laser +1; the fields steer each prism toward delivering +1):

| controller | delivery | energy sum |
|---|---|---|
| HASH (bits of z) | 15/27 | +7 |
| EXACT (frustrated, 8 binary states) | **25/27** | −77 |
| TERNARY relaxation (27 states, 0 = neutral) | 25/27 | −77 |
| FIELD_ONLY control (J = 0) | 27/27 | — |

| prediction | result |
|---|---|
| R1: field-only delivers 27/27 | held |
| R2: EXACT energy ≤ HASH energy for every destination | held, 27/27 |
| R3: TERNARY energy ≤ EXACT energy for every destination | held, 27/27. It was strictly lower in **0** of 27: the neutral state added no lower energy here |

**Bell part** (prism-Bell stations, 131,072 trials; orientations from EXACT with fields taken
from z):

| model | S | signalling | prediction |
|---|---|---|---|
| FROZEN-LOCAL (z cannot see the settings) | −0.371 | none (max marginal difference 0.006 < tolerance 0.028) | B1 held: below the local bound of 2 |
| FROZEN-JOINT (z sees both settings) | −0.367 (measured) | none (0.003 < 0.028) | B2 measured, not presumed |

**Reading.**
- **Frustration is a real optimizer here.** It delivers 25/27 against hashing's 15/27, at much
  lower energy. Competing couplings cost 2 deliveries against fields alone (27/27): the frustrated
  triangle cannot satisfy everything.
- **The neutral ternary state found no lower energy** on these instances. The spin-glass repo's
  ternary advantage is not shown here.
- **Bell:** frustrated selection creates a non-zero correlation (S ≈ −0.37), well inside the
  local bound. Letting z see both settings changes almost nothing (−0.367), with no signalling,
  because the settings enter only through hashed fields. As the correction (PR #48, PR #49) says,
  this is a fact about this mechanism, not a theorem. A balanced controller built for it can
  exceed 2.
- **Scope:** software model, not physical correlations.

**Chain:**

| layer | file |
|---|---|
| HBI | `FRUST.hbi` |
| HBP | `PREREG.hbp`, `RESULT.hbp` |
| SHA | `SHA256SUMS`, `*.hbp.sha256` |
| SH | `run.sh` |
| HASH | `FRUST.seal` |

No JSON. The source reaches `tribit/mod.rs` and `sha.rs` through absolute `#[path]`s on the acer
host; their hashes are in `RESULT.hbp`.
