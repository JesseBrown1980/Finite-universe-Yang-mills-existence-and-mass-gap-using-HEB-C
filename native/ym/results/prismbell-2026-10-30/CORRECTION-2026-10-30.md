# Correction, recorded beside the sealed prism-Bell package (2026-10-30)

This file adds a correction. It changes nothing in the sealed package: `PREREG.hbp`,
`ADDENDUM-PRERUN.hbp`, `RESULT.hbp`, `RAW-*.hbp`, `README.md`, `SHA256SUMS` and `PBELL.seal`
(`e75672ca…`) are unchanged, and every measured number stands.

**What was over-generalized.** The README's reading, "the mechanism alone faces a trade-off:
randomized, it is silent; deterministic, it correlates but signals", is stated as if it were
general. It is not.

| statement | status |
|---|---|
| Outcomes are fixed functions of the settings only, with **no shared λ varying across trials**; then no signalling implies local, so \|S\| ≤ 2 | **True** (theorem). This is Acer's deterministic no-shared-λ result |
| The same claim with a **shared λ** that varies across trials and a controller that sees **both settings** | **False.** A balanced construction (z sets how the results relate, never the marginals) reaches S = 4 with no observable marginal signalling, provided the stations cannot read λ or the global control state. This is the cloud seat's zbell result (PR #44) and Acer's own CHSH Q3 PR box (PR #46) |
| "Randomized ⇒ silent" | **Not a theorem.** In this package, PULL went silent because the hash scrambled the sign of the correlation itself. That is a property of this mechanism, not of randomness |

**What this means for this package's models.**
- PULL_NOLAMBDA had a shared λ with two values (the laser sign), so the no-shared-λ theorem does
  not cover it. Its measured signalling is a fact about that model, not a consequence of the
  theorem.
- The two results use different assumptions: deterministic with no shared λ (Acer), and balanced
  shared λ with joint settings (cloud). Neither invalidates the other's recorded experiment.
- The open question is the cap at 2√2 arising from the mechanism itself, not whether 2 can be
  exceeded without signalling. The tuned controls (2.81–2.84) show the cap can be met.

**Scope:** software models; nothing here is evidence of a physical z mechanism.
