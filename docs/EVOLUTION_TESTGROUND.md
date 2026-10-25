<!-- Documentation only. Code: branch integer-sturm-ladder at 36c245f, independent/evolution_testground/ -->

# Evolution test ground (measurement, not certificate)

Let the finite S3 2x2-torus Hamiltonian H = JE·E + JB·M evolve in Euclidean
time and *measure* the gap from the relaxation, instead of forcing it.
Integer-only (HEB-C rule): A = 24·H is an exact integer matrix (orbit weights
1, 2, 3, 4, 6, 8, 12, 24); the vector is rescaled by right-shifts; the plot's
y-axis is `bit_length()` of each energy drop (exact log2). No float, Decimal or
Fraction; every text line ends `json=0`.

    v <- (c - H) v,   E(k) = <v,Hv>_W / <v,v>_W  ->  E0
    drops shrink by rho^2 per step, rho = (c - E1)/(c - E0)
    gap = (c - E0)(1 - rho)

Run (127.0.0.1 only):

    HEBC_MATRIX=/path/to/matrix.txt python3 server.py 5099
    # /            table + SVGs (measured next to certified ledger rungs)
    # /evolve/1/3  EVOLVE|JE=1|JB=3|...|kind=MEASUREMENT_NOT_CERTIFICATE|json=0
    # /svg/1/3     integer SVG of log2(energy drop) per step

Code: [`independent/evolution_testground` at `36c245f`](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/tree/36c245f/independent/evolution_testground). `matrix.txt` is the PR #9 1,393-state export (sha256 `137285e0…`).

## Measured 2026-10-25 (energies per unit JE)

| r | E0 measured | E0 certified < | gap measured | gap certified > | inside bracket | steps |
|---|---|---|---|---|---|---|
| 0 | 0.000 | 0.001 | 5.999 | 5.998 | yes | 400 |
| 1 | 7.634 | 7.750 | 5.611 | 5.437 | yes | 600 |
| 2 | 14.334 | 14.375 | 4.007 | 3.750 | yes | 900 |
| 3 | 19.243 | 19.313 | 1.473 | 1.312 | yes | 1500 |
| 5 | 21.877 | 21.885 | 0.341 | 0.325 | yes | 3000 |
| 6 | 22.282 | 22.283 | 0.257 | 0.254 | yes | 3500 |

Every measurement lands inside the interval-Sturm brackets from the ladder ledger.
The evolution was not steered: a deterministic LCG start vector excites every
symmetry sector, and the gap simply emerges from the decay rate. These are
measurements; only the Sturm certificates are proof receipts.

Estimator note: at fixed-point scale 10^12 the gap was overestimated (5.815 vs
≈5.608 at r = 1); scale 10^40 plus the median ratio of the last 40 clean drops
fixes it (5.611).

## Matrix-jump sweep over all 17 rungs, by translation sector (2026-10-25)

`evolvers/` (Rust, integer-only, clippy `-D warnings`, no f32/f64):
- `jump MATRIX JE JB J [REPS]`: P = T^(2^J), T = c − H, by repeated squaring
  (one multiply = 2^J Euclidean steps; J = 26 is about 67 million steps in
  about 3 s per sector). c = Gershgorin + 1, rigorously above the spectrum.
  E0 = Rayleigh quotient of P^REPS v0 with the exact sparse H; E1 from
  Hotelling deflation H' = H + 24·JE·Π_g (the error in g enters E1 only at
  second order). gap = E1 − E0, no ratio fitting.
- `evolvers MATRIX JE JB STEPS`: plain sparse stepping, same energies; used as
  the full-matrix cross-check (r = 1: E1 = 13.242684 full vs 13.242691 sectors).

`sweep/sweep.py` drives `/jump/SECTOR/JE/JB/J` on the HTTP-0 server for each of
the four Z2xZ2 sectors; global E0/E1 = two lowest of the union. Output
`sweep/sweep.hbp` (json=0).

| r | E0 | E1 | gap measured | gap certified > | r·gap |
|---|---|---|---|---|---|
| 0 | 0.000000 | 5.999999 | 5.999999 | 5.998 | – |
| 1 | 7.634198 | 13.242691 | 5.608493 | 5.437 | 5.608 |
| 2 | 14.334474 | 18.336753 | 4.002279 | 3.750 | 8.005 |
| 3 | 19.243727 | 20.717416 | 1.473689 | 1.312 | 4.421 |
| 5 | 21.877395 | 22.218632 | 0.341237 | 0.325 | 1.706 |
| 6 | 22.282756 | 22.540004 | 0.257248 | 0.254 | 1.543 |
| 8 | 22.745162 | 22.922488 | 0.177326 | 0.175 | 1.419 |
| 9 | 22.891903 | 23.046286 | 0.154383 | 0.150 | 1.389 |
| 15 | 23.345190 | 23.433536 | 0.088346 | 0.085 | 1.325 |
| 21 | 23.534172 | 23.596495 | 0.062323 | 0.057 | 1.309 |
| 27 | 23.638288 | 23.686516 | 0.048228 | 0.044 | 1.302 |
| 45 | 23.783323 | 23.812117 | 0.028794 | 0.025 | 1.296 |
| 63 | 23.845299 | 23.865838 | 0.020539 | 0.019 | 1.294 |
| 81 | 23.879699 | 23.895665 | 0.015966 | 0.013 | 1.293 |
| 135 | 23.927832 | 23.937406 | 0.009574 | 0.007 | 1.2925 |
| 189 | 23.948454 | 23.955292 | 0.006838 | 0.004 | 1.2924 |
| 243 | 23.959909 | 23.965227 | 0.005318 | 0.004 | 1.2923 |

All 17 consistent with the certified rungs (E0 below the certified upper
bound, E1 and the gap above the certified lower bounds).

Sector structure (measured):
- For every r > 0, E0 and E1 both lie in the ++ sector, the one holding all 8
  flat vacua: the gap is the splitting among the vacua, not a crossing into
  another symmetry sector. At r = 0 the +− and −+ levels touch E1 = 6 exactly.
- The other three sectors have M ≥ 3, so their levels rise about as 3r
  (r = 243: lowest 752.903 vs E0 = 23.960).
- +− and −+ are exactly degenerate at every rung.
- r·gap → √14 − √6 = 1.292167 (second-order magnetic-end law), reached by the
  evolution without being imposed.

Not settled to 5 micro-units: E1 at r = 2 (moving 0.00025 between the last two reps).

`sweep/sweep_bugged_shift.hbp` is an earlier run kept as evidence of a bug: its
shift assumed every sector's lowest level is below 24·JE, false at large r for
the three non-vacuum sectors. Their levels in that file are wrong; the ++ values
and the global gaps were unaffected. Fixed by the Gershgorin shift.
