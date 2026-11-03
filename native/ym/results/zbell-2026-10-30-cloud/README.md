# zbell, cloud seat: Bell/CHSH test of the z layer (2026-10-30)

The cloud seat's independent CHSH test, beside acer's PR #46 (`chsh`) and PR #48 (prism-Bell).
Integer only (every correlation is a count over n = 486 shared values λ), Rust 1.81,
clippy `-D warnings` exit 0, records in HBP (json=0).

## Setup

Two stations A and B, settings a, b ∈ {0, 1}, outcomes ±1. S·n = E(0,0)n + E(0,1)n + E(1,0)n − E(1,1)n.
Local bound |S·n| ≤ 972 (S ≤ 2). Quantum bound (S·n)² ≤ 8n² (S ≤ 2√2).
No-signalling: A's count of +1 depends only on a, B's only on b.

## Result (`RESULT.hbp`)

| model | S·n | S | no-signalling | prediction |
|---|---|---|---|---|
| L-det: all 16 fixed local strategies | ±972 | exactly ±2 each | — | P1 PASS |
| L-hash: each side hashes only its own setting and λ | 44 | 0.09 | yes | P2 PASS |
| Z-PR: z sees both settings, A = (−1)^λ, B = A·(−1)^(ab) | 1944 | 4 | yes, every count 243 / 486 | P3 PASS |
| Z-T as written | 1512 | 3.11 | yes | P4 FAIL (predicted 1368); P4b PASS |
| Z-T2 (addendum) | 1368 | 2.81 | yes | P4c PASS |
| Leak: A also reads b | — | — | no: A's +1 count 243 → 486 | P5 PASS |

Registered verdict: **FAIL**, on P4 alone. `PREREG.md` (`8434e059…`) described Z-T with
E(1,1)n = −486 but predicted S·n = 1368, which needs −342. `ADDENDUM.md` (`b687b3c7…`) recorded
this before any code ran, kept P4 as written, predicted the as-written value (P4b) and added the
corrected model Z-T2 (P4c). The clippy fix in `src/main.rs` (an unused `mut`) also came before the
only run.

## What it shows

- A side that reads only its own setting stays within |S| ≤ 2, hash or no hash.
- z reading both settings, with balanced shared λ, reaches S = 4 with no signalling in the
  observed counts: each station's +1 count is fixed whatever the far setting. The correlation
  lives in how B relates to A, never in either station's own counts.
- A station that can read λ itself learns the far setting (B, knowing A from λ, sees a when b = 1).
  Access to λ is part of the model: the stations see their outcomes, not λ.
- Within the quantum range (2.81) is reachable by tuning. A rule that brings the bound out of the
  mechanism itself is not part of this package.

## Replay and integrity chain (HBI → HBP → SHA → SH → HASH, json=0)

`run.sh` checks both seals, builds a scratch copy with Rust 1.81 against the locked `sha2 =0.10.8`
(the repo's vendored sources do not include sha2), runs clippy and checks byte identity with
`RESULT.hbp`. `hebc-ym-cloud-replay.yml` runs it on the exact PR head. `SHA256SUMS` covers every
other file, `ZBELL.hbi` holds the chained `EMIT` rows
(`pid[0] = sha16("EMITTER-SEED|YM-ZBELL-2026-10-30-CLOUD")`), and
`ZBELL.seal = sha256(SHA256SUMS + ZBELL.hbi)`.
