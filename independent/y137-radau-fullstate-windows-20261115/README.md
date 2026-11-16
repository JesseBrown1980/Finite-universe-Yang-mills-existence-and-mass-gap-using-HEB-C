# #137: full-state transfer error with the three-moment bracket, and energy windows from the bracket

Seat ACER-CLAUDE-FABLE52, 2026-11-15, at the operator's direction. Prediction and program pushed in `9bc4bcb` before the run. Four of four predictions met. Exact integers, 18 seconds.

## Result (`RESULT-FSW.hbp`)

| Combined normalised full-state error (E1 + E2) | Value | Times the 1/700 gate |
|---|---|---|
| accepted in #187 | 0.144090460519 | 100.9 |
| step 1: three-moment bracket, accepted vector, accepted windows | 0.030452701775 | 21.3 |
| step 2: the same with energy windows from the bracket | 0.019880853054 | 13.9 |

Step 1 is #187's composition unchanged (the routine first reproduces #187's own four numbers from #187's inputs), fed with the kept-vector residual and width action of the three-moment bracket and #187's directional energy term. Sines 0.008302191642 and 0.021219904598; errors 0.008553967855 and 0.021898733920.

Step 2 narrows the energy windows. At the sample `z` the bracket gives integer bounds `tL <= lambda_k(S(z)) < tH < 0` by exact inertia bisection in the flat metric. For `E <= z`, `S(z) + (z-E) <= S(E) <= S(z) + (z-E)(1+tau)` with `tau = 72/(gamma-z)^2`, and `E_k` is the zero of the k-th eigenvalue of `S(E)`, so `z + tL <= E_k <= z - |tH|/(1+tau)`.

| Level | Accepted window (width) | Bracket window (width) |
|---|---|---|
| E1 | 69.908500000 .. 69.909875505 (0.001375505) | 69.909429421 .. 69.909586556 (0.000157135) |
| E2 | 69.948100000 .. 69.949729820 (0.001629820) | 69.949264147 .. 69.949433884 (0.000169737) |

Both new windows lie inside the accepted ones. The gap E2 - E1 is then above 0.039677591 (accepted 0.038224495). With these windows the sines are 0.005584615805 and 0.013697673102 and the errors 0.005751642394 and 0.014129210660.

## Scope

Source-conditional as #198 and #187: the accepted Q floor 94.0682, the window `g <= X <= h`, the archived moments, the accepted Q norms of #185, the accepted #180 vectors, `E3_lo` of #182. The new energy windows additionally rest on the three-moment bracket. Verdict HOLD: 0.0199 is above 1/700. Issue #137 OPEN.

## What remains in the numerator (per trillion, E1 and E2)

Width action 144,398,350 and 142,342,765; centred residual 31,272,838 and 66,461,984; energy term 40,703,480 and 41,761,844. The width action is the largest part again; the next moment narrows it.
