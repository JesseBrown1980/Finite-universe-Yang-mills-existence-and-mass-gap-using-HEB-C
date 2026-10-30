# zteleport, cloud seat: the iterated-teleportation hierarchy for the zbell models (2026-10-30)

Tests which zbell correlations stay stable through the teleportation hierarchy T_N of Dmello, Xu,
Renou and Gross, "An operational characterization of finite-dimensional quantum theory"
(arXiv 2610.03694): Theorem 18 and Corollary 20 give exactly 2√2 for any theory whose correlations
survive iterated teleportation and violate CHSH. Rust 1.81, std only, integer and exact-rational,
clippy `-D warnings` exit 0, HBI → HBP → SHA → SH → HASH, json=0. The zbell baselines in
`../zbell-2026-10-30-cloud/` (PR #44) are unchanged.

## Hierarchy

N + 1 resources in a chain; N middle stations each return one of four outcomes; the two endpoints play
CHSH. S_N = Σ_μ p(μ)·S_μ, exact rational. 2√2 is never computed: quantum checks compare S² with 8.

## Result (`RESULT.hbp`): 5 of 5 registered predictions PASS

| model | N = 0 | N = 1 | N = 2 | N = 3 | N = 4 |
|---|---|---|---|---|---|
| Q: Bell states, Bell-state measurements (locally composed) | S² = 8 | S² = 8 | S² = 8 | S² = 8 | S² = 8 |
| PRW: PR boxes, best of every local wiring | 4 | **2** (best of 2,048) | **2** (best of 4,194,304) | | |
| ZPR: z as global controller (zbell S = 4) | 4 | 4 | 4 | 4 | 4 |
| ZT: z global, tuned (zbell Z-T2) | 1368/486 | same | same | same | same |
| LH: local hash selection | 0.07 | 0.21 | 0.51 | 1.02 | 1.61, every S_μ ≤ 2 |

- Q satisfies the hierarchy exactly: for every N up to 4 and every one of the 4^N outcome strings,
  p(μ) = 4^−N, the conditional correlation matrix is the starting one in a Pauli frame
  (T_μ = D·T₀, det D = +1, zero residual), S² = 8, and the endpoint marginals are zero.
- PR correlations composed by local operations do not survive one step. The best wiring gives S = 2
  at N = 1 and N = 2: given the station's outcome, the endpoints' parity is linear in s and t, with
  no s·t term.
- z as a global controller keeps any correlation, 4 or the tuned 2.81, at every N with uniform
  outcomes and exact no-signalling. The hierarchy constrains theories whose resources compose
  locally; a z that sees every setting meets the hierarchy by construction.
- Local hash selection stays at or below 2 for every outcome. Its average rises with N because
  conditioning on 4^N outcomes splits the 486 shared values into small groups, and small groups of a
  deterministic local strategy sit at the local bound.

So the rule that stops at 2√2 is local composition: correlations carried by resources that compose
through local operations, and survive that composition, land on the quantum value. A z that is
global needs that rule added for its correlations to land there.

## Replay and integrity chain

`run.sh` checks the prediction seal (`4184c4c2…`), builds with Rust 1.81, runs clippy and checks
byte identity with `RESULT.hbp`; `hebc-ym-cloud-replay.yml` runs it on the exact PR head.
`SHA256SUMS` covers every other file, `ZTELEPORT.hbi` holds the chained `EMIT` rows
(`pid[0] = sha16("EMITTER-SEED|YM-ZTELEPORT-2026-10-30-CLOUD")`), and
`ZTELEPORT.seal = sha256(SHA256SUMS + ZTELEPORT.hbi)`.
