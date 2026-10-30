# CHSH: a Bell test of the z model (2026-10-30)

Operator-authorized ("do a Bell/CHSH-type statistical test"). The predictions were sealed in
`PREREG.hbp` (`9c73974c…`) before any code. Rust 1.81, clippy `-D warnings` exit 0, exact
integer and rational arithmetic only, json=0.

**Setup.**
- Two sides, A and B. Each has a setting x or y in {0, 1}, and an outcome of +1 or −1
  (canonical trits Pos and Neg).
- S = E00 + E01 + E10 − E11.
- Bounds:
  - any **local** model: |S| ≤ 2 (Bell);
  - quantum mechanics: |S| ≤ 2√2 ≈ 2.828 (Tsirelson), checked exactly as S² ≤ 8;
  - beyond that: never seen in nature.
- Statistics use N = 102,400 = 320² trials per setting pair, so 5σ (σ ≤ 2/√N) is exactly 1/32.

| prediction | result |
|---|---|
| Q1: every one of the 16 local deterministic strategies has \|S\| = 2 exactly, so the local maximum is 2 | held |
| Q2: a local model with shared hash randomness, each side reading only its own setting, stays ≤ 2 | held (S ≈ 516/102400). This model is weak, because independent hashes decorrelate the sides; Q1 is the general bound |
| Q3: a global z that reads both settings (the PR box) gives S = 4, with no signalling | held: **S = 4**, no-signalling exact |
| Q4: a global z tuned to quantum statistics (E = ±70/99) gives exactly S = 280/99, which is greater than 2, with S² ≤ 8 and no signalling | held: S = 1120/396 = 280/99 |
| Q5: the same model sampled with hash randomness, N per pair: S above 2 by more than 5σ, and within 5σ of 2√2 | held: S = 289380/102400 ≈ 2.826 |
| Q6: control: a z that copies y into A's outcome is detected as signalling | held |

**Reading.**
- **No local model breaks 2, whatever it hashes.** Breaking 2 requires the outcome rule to read
  the *far* setting. The operator's z model (z pulled instantly from the destination) does
  exactly that. So it is a model that *can* reproduce Bell violations, which local classical
  controllers provably cannot.
- **An unconstrained z goes too far.** It can reach 4, beyond anything nature shows. Matching
  nature takes an extra rule: correlations capped at 2√2, with no signalling. Q4 and Q5 show such a
  z exists and keeps every marginal unchanged.
- **Scope:** these are software models. Real Bell experiments show nature violates the local
  bound. This test shows that the z model is the right *kind* of model to agree with them, not
  that nature uses it.

**Chain:**

| layer | file |
|---|---|
| HBI | `CHSH.hbi` |
| HBP | `PREREG.hbp`, `RESULT.hbp` |
| SHA | `SHA256SUMS`, `*.hbp.sha256` |
| SH | `run.sh` |
| HASH | `CHSH.seal` |

No JSON. The source reaches `tribit/mod.rs` and `sha.rs` through absolute `#[path]`s on the acer
host; their hashes are in `RESULT.hbp`.
