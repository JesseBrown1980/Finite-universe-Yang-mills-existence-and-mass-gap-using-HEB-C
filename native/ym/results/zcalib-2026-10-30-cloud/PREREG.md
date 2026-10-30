# zcalib, cloud seat: viscosity, sound speed and pressure of the lattice gas on the current gates.
Pre-registration, frozen before any code.

Why: the calibration in effective-viscosity-and-pressure-from-the-discrete-dynamics-in-trits
(nu_eff = 0.588 +- 0.008, acoustic speed 0.8937 at Lx = 72, EOS speed sqrt(2/3)) used an earlier
collision table. The Taylor–Green and cutoff runs use GATES.lut (sha256 a7fca71a…), which keeps the
all-ones state fixed in every gate. This package measures the transport coefficients on that table.

Substrate: D3Q27, trits 0..2, the 288 gates of GATES.lut (rebuilt in Rust, checked byte-equal), 32 gates
per cell per tick with gate (t*32 + cell*17 + j*37) mod 288, then streaming; box Lx x Ly x Lz periodic,
cell index (x*Ly + y)*Lz + z. Rust 1.81, std only, integer only, json=0. Irrational constants enter
only as integer bounds: ln 2 in [693147, 693148] / 10^6, pi^2 in [9869604, 9869605] / 10^6.

## Shear (viscosity)
Box 8 x Ly x 8, Ly in {24, 48}; start every channel at 1, then one push per cell along x, +x for
y < Ly/2 and -x otherwise (face channels 22 and 4). A(t) = sum over cells of jx * s(y), s = +1 for
y < Ly/2 else -1. T_half(Ly) = first tick with 2 A(t) <= A(0). nu = ln2 * Ly^2 / (4 pi^2 T_half)
(the fundamental of the square wave, decaying as exp(-nu k^2 t)), reported as an integer-bounded interval.

## Sound
Box Lx x 8 x 8, Lx in {24, 36, 48, 60, 72}; start every channel at 1 except the rest channel (index 13),
set to 2 for x < Lx/2 and 0 otherwise (a density step, zero momentum). D(t) = sum of rho * s(x). Crossing
ticks t_i: first ticks where the sign of D differs from its sign at the previous tick. c = 2 Lx / (t_5 - t_1)
(two periods of the standing wave), reported as a rational.

## Pressure (equation of state)
At the uniform state, 3 P / rho = Tr(Pi) / rho = 54 / 27 = 2 exactly, so c_s^2 = P / rho = 2/3.

## Predictions
- K1 conservation: mass and energy exact every tick in every run; occupancy in 0..2.
- K2 diffusive shear: T_half(48) / T_half(24) lies in [7/2, 9/2] (viscous decay scales as Ly^2).
- K3 the equation of state at the uniform state gives Tr(Pi) / rho = 2 exactly.
- K4 measured, not predicted: nu interval from each Ly, against the published 0.588 +- 0.008; c at each
  Lx, against sqrt(2/3) = 0.8165 and the published 0.8937.
Any build failure or missing crossing is INCONCLUSIVE.
