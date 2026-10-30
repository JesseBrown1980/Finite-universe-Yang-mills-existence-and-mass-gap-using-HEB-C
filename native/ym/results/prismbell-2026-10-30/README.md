# prism-Bell: CHSH on the actual three-prism mechanism, separated stations (2026-10-30)

Operator-authorized: "a stronger next test would retain the actual three-prism output patterns
and define two physically separated measurement stations, with independently selected settings
and recorded raw outcomes."
- Predictions sealed in `PREREG.hbp` (`72c6daf1…`).
- A pre-run addendum (`0dd5b76f…`), sealed before any code, flags that P3 may fail.

Rust 1.81, clippy `-D warnings` exit 0, integer only, json=0.

**Setup.**
- prism3's real 40-cell propagation: curved j± per prism, c = 1.
- Station A reads a final branch in subtree 0; station B reads one in subtree 2 (6 hops apart
  through the source).
- Each station's setting picks its branch. Settings are chosen per trial, after emission, by
  independent station hashes.
- Outcome = the sign of the amplitude.
- 131,072 trials per model; every raw (t, x, y, a, b) row is kept in `RAW-*.hbp`.

| model | S | no signalling | prediction |
|---|---|---|---|
| LOCKED (z from laser, root, trial; no settings) | −0.0016 | yes | P1 held: \|S\| within 5σ of 0 |
| PULL (z also pulled from both stations' settings, with per-trial randomness) | −0.0093 | yes | P2 held: \|S\| within 5σ of 0 |
| PULL_NOLAMBDA (z from both settings, no per-trial randomness) | **1.998** overall; **4** for laser −1, **0** for laser +1 | **NO: signalling** | P3 original **FAIL** (the addendum predicted it); P3 per laser held |
| TUNED (positive control, quantum-matching z) | **2.834** | yes | P4 held: above 2, within 2√2 |

- P5 ("no signalling in every model") **FAILED**, because of PULL_NOLAMBDA.
- P6 held: all outcomes ±1, all rows counted.

**What this shows about the real mechanism.**
1. **Hash-scrambled destination pull gives no Bell correlations (PULL).** Even with z pulled
   from both stations, per-trial randomness makes the prism signs average out: S ≈ 0. Access to
   the far setting is necessary, not sufficient.
2. **A deterministic destination pull does correlate, but it signals (PULL_NOLAMBDA).** For one
   laser sign the hash happened to give the maximal pattern, S = 4. But each station's own
   statistics then depend on the far setting, so a message could be sent. That breaks "nothing in
   the matrix affected".
3. **The mechanism alone faces a trade-off:** randomized, it is silent; deterministic, it
   signals. Quantum-like correlations without signalling (TUNED: 2.834) need a specific
   correlation rule on top of the prism mechanism. Three seats' earlier tests reached the same
   conclusion in abstract form; this test shows it in the actual mechanism.

**Scope:** software model, not a physical claim.

**Chain:**

| layer | file |
|---|---|
| HBI | `PBELL.hbi` |
| HBP | `PREREG.hbp`, `ADDENDUM-PRERUN.hbp`, `RESULT.hbp`, `RAW-*.hbp` |
| SHA | `SHA256SUMS`, `*.hbp.sha256` |
| SH | `run.sh` |
| HASH | `PBELL.seal` |

No JSON. The source reaches `tribit/mod.rs` and `sha.rs` through absolute `#[path]`s on the acer
host; their hashes are in `RESULT.hbp`.
