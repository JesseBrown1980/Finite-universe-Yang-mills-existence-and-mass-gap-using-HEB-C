<!-- Documentation only. Code: branch integer-sturm-ladder at d06014a, independent/evolution_testground/ -->

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

Code: [`independent/evolution_testground` at `d06014a`](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/tree/d06014a/independent/evolution_testground). `matrix.txt` is the PR #9 1,393-state export (sha256 `137285e0…`).

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
