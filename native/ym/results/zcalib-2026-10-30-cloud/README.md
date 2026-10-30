# zcalib: viscosity, sound and equation of state on the current gates (2026-10-30)

Transport coefficients of the D3Q27 lattice gas measured on `GATES.lut`, the table every 2026-10-30
lattice-gas run uses (it keeps the all-ones state fixed in every gate). Rust 1.81, std only, integer only,
clippy `-D warnings` exit 0, HBI → HBP → SHA → SH → HASH, json=0. ln 2 and π² enter only as integer bounds.

## Result (`RESULT.hbp`)

| quantity | value | check |
|---|---|---|
| Kinematic viscosity, clean decay window | 0.4397 (Ly = 24), 0.4258 (Ly = 48), cells²/tick | V2 PASS: within 3% |
| Equation of state | Tr Π / ρ = 2 exactly, c_s² = 2/3 | K3 PASS |
| Mass, energy, occupancy | exact every tick | K1 PASS |
| Early half-life ratio T_half(48)/T_half(24) | 82/26 = 3.15, against 4 for pure diffusion | K2 FAIL (square-wave harmonics) |
| Sound speed from zero crossings | not a clean period: the start also excites a non-propagating thermal mode | S2 FAIL |

- The current table gives ν ≈ 0.43, about 27% below the 0.588 measured with the earlier table in
  effective-viscosity-and-pressure-from-the-discrete-dynamics-in-trits; both stay on record.
- Post hoc, from the oscillation peaks at Lx = 24 the period is about 28 ticks, c ≈ 0.86, between the
  equation-of-state 0.816 and the earlier acoustic 0.894; a period fit is the next run.

`PREREG.md` (`ea40210b…`) frozen before any code; `ADDENDUM.md` (`01040f0c…`) added the late-window
viscosity and the moving-channel sound start before run 2. `RESULT.run1.hbp` is run 1. `run.sh` rebuilds
with Rust 1.81 and checks byte identity.
