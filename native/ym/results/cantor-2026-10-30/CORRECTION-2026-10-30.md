# Correction, recorded beside the sealed Cantor package (2026-10-30)

This file adds a correction. It changes nothing in the sealed package: every file in
`SHA256SUMS` and the seal `CANTOR.seal` (`21b38b47…`) are unchanged, and every measured number
stands.

- **C3 DET is correct as measured.** DET had no shared λ: z = sha256(x ‖ y), with no per-trial
  randomness. The theorem it cites (deterministic, no shared λ, no signalling ⇒ local ⇒ |S| ≤ 2)
  applies to exactly that model.
- **The README's general wording is over-broad.** "Randomized, the product over bands is silent"
  describes this mechanism's hash: it scrambled the sign of the correlation. It is not a theorem.
  With a shared λ that varies across trials and a controller that sees both settings, a balanced
  construction reaches S = 4 without observable signalling, as long as the stations cannot read λ
  (cloud zbell, PR #44; Acer CHSH Q3, PR #46).
- The two results use different assumptions, and neither invalidates the other's recorded
  experiment. The open question remains the cap at 2√2 arising from the mechanism itself.
- C1 (all 16 bands arrive at step 20, and the dispersion control detects spread) and C2 (Cantor
  structure) are unaffected.
