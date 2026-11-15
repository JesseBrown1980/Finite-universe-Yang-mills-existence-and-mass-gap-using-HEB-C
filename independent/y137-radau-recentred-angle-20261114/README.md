# #137: eigendirection angle on the three-moment bracket of #198

Seat ACER-CLAUDE-FABLE52, 2026-11-14, at the operator's direction. Prediction and program pushed in `aa09c96` before the run. Three of five predictions met, two missed.

## Result (exact integers, 29 seconds, `RESULT-RECENTRED.hbp`)

The sine bound is `(centred residual + width action + energy term) / (gap - mu)` as in #184 and #186, with the bracket `S(z) = H - Y`, `0 <= Y <= H - L` taken from #198.

| Sine bound | E1 | E2 | Sum |
|---|---|---|---|
| accepted in #187 | 0.043364646417 | 0.095928035901 | 0.139292682318 |
| **accepted #180 vector kept, three-moment bracket** | **0.009531656764** | **0.024623397607** | **0.034155054371** |
| re-centred vector, three-moment bracket | 0.008668866148 | 0.020639344508 | 0.029308210656 |

The accepted vector, kept unchanged, gains a factor 4.5 at E1 and 3.9 at E2. The fixed-sample Wilson amplitude above 1/50 of #180 belongs to that vector, so it carries over with no new Wilson computation.

Parts of the numerator for the kept vector (per trillion): centred residual 31,272,838 and 66,461,984; width action 144,398,350 and 142,342,765; energy term (global form, `72 drift / ((gamma - E_hi)(gamma - z))`) 169,691,876 and 201,730,993. The energy term is now the largest part.

## Predictions

- A1, A2, A3 met: re-centred sines 0.00867 and 0.02064, sum 0.0293, above the 1/700 gate. Verdict HOLD.
- A4 missed: the seat predicted the kept vector would be at least twice as loose as the re-centred one. It is 1.10 and 1.19 times as loose.
- A5 missed: the seat predicted a flat-metric sine of 0.005 to 0.12 between the two vectors. Measured 0.000734 and 0.002809. The accepted vector already sits close to the null direction of the bracket.

## Where the gate stands

With #187's ratio of full-state error to sine (1.0315 and 1.0358) the combined error would be about 0.0353, about 25 times the 1/700 gate, against 101 times in #187. That figure is an estimate; the full-state replay with these sines is not run here.

## Next

1. Rerun the #187 full-state composition with the kept-vector sines, using #187's accepted directional energy term in place of the global one (by hand from the accepted figures that gives sines near 0.0083 and 0.0212; not computed by this program).
2. Narrower energy windows: the energy term is proportional to the window width (1.38 and 1.63 thousandths now).
3. The four-moment bracket when `mu3` lands: it narrows the width action.

## Scope

Source-conditional as #198. Eigendirection bound only. Wilson weight HOLD; issue #137 OPEN.
