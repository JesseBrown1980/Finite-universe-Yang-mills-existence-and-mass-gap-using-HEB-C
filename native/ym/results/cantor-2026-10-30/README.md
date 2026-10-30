# Cantor all-band laser test (2026-10-30)

Operator question: "does the laser use the cantor signal of ALL wavelengths, not just light? From
sound to gamma and beyond." Authorized: "all three". The predictions were sealed in `PREREG.hbp`
(`96d5364d…`) before any code. Rust 1.81, clippy `-D warnings` exit 0, integer only, json=0.

**Source.**
- A Cantor laser at depth 4: each level splits into three, and the middle third is dropped.
- That leaves 16 bands out of 81 sub-bands; every address is free of the digit 1.
- Bands are labelled by level only. No physical frequency (sound … gamma) is claimed for any band.

| prediction | result |
|---|---|
| C1: every band, through its own c = 1 channel, arrives at step 20 exactly (no dispersion) | held: 16/16 at step 20 |
| C1 control: bands given different speeds arrive at different steps (20 × (1 + count of 2s)) | held: 20 … 100, exact. The test detects dispersion |
| C2: Cantor structure: counts 2, 4, 8, 16, 32, 64; no digit 1; each level = {0,2} × the previous level | held |
| C3 LOCAL (z without settings): S within 5σ of 0, no signalling | held: S = 0.011 |
| C3 PULL (z pulled from both stations, per-trial randomness): S within 5σ of 0, no signalling | held: S = −0.016 |
| C3 DET (deterministic): theorem: never both no signalling and \|S\| > 2 | held. Case: no signalling, S = −2 exactly (local) |

**Reading.**
- **c = 1 holds for every band at every level.** The whole Cantor spectrum arrives together, the
  simulation counterpart of the GRB-090510 light-timing test (T6). The control shows a
  band-dependent speed would have been seen.
- **Carrying all 16 bands does not change the Bell trade-off.** Randomized, the product over
  bands is silent (S ≈ 0). Deterministic, this run happened to stay local (S = −2, no
  signalling). The theorem guarantees a deterministic model can never be both non-signalling and
  above 2. Quantum-like correlations without signalling still need an extra correlation rule;
  bandwidth alone does not supply it.
- **Scope:** software model; band labels are levels, not measured frequencies.

**Chain:**

| layer | file |
|---|---|
| HBI | `CANTOR.hbi` |
| HBP | `PREREG.hbp`, `RESULT.hbp` |
| SHA | `SHA256SUMS`, `*.hbp.sha256` |
| SH | `run.sh` |
| HASH | `CANTOR.seal` |

No JSON. The source reaches `tribit/mod.rs` and `sha.rs` through absolute `#[path]`s on the acer
host; their hashes are in `RESULT.hbp`.
