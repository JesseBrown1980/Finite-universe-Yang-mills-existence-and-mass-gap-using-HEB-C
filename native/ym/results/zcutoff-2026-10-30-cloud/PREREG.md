# zcutoff, cloud seat: a collapsing vortex in a finite fluid, at three resolutions.
Pre-registration, frozen before any code.

Question: where OpenAI's September 2026 construction shrinks a vortex core to zero volume while speed
diverges (core volume ~ tau^(3/2 - h), speed ~ tau^(-1/2 - h)), what does a finite fluid do?

Substrate: the D3Q27 lattice gas of Taylor_green_regularity-resolved-and-solved (27 channels, trits
0..2, the repository's 288 involutive gates, 32 per cell per tick, gate (t*32 + cell*17 + j*37) mod 288,
then streaming). Gates rebuilt in Rust and checked byte-equal to GATES.lut (sha256 a7fca71a…).
Rust 1.81, std only, integer only, json=0.

## Runs
Unit box, L^3 cells, L in {24, 48, 96}; cell size dx = 1/L; one tick = dx of time (speed 1 per tick).
Start: every channel at occupancy 1 (density 27, zero momentum).
Drive: a swirl about the z axis through the box centre, with a core radius that collapses,
R(t)^2 = R0^2 * (T - t) / T with R0 = L/4 cells and T = 2L ticks (the same physical schedule at every L;
R^2 falls linearly in time, so R ~ tau^(1/2)). At tick t, a cell whose distance from the axis satisfies
d^2 <= R(t)^2 and (7*cell + 13*t) mod 4 = 0 gets one azimuthal push: x by the sign of -(y - c),
y by the sign of (x - c), each moving one particle from the opposite face channel (n_from >= 1,
n_to <= 1). Pushes conserve mass and kinetic energy exactly. Run until t = T.

## Integer diagnostics per tick
JMAX = max over cells of |j|^2; WMAX = max over cells of |curl j|^2 (undivided central differences,
lattice units); CORE = number of cells with |curl j|^2 * 2 >= WMAX (the core); mass and energy totals.
Physical peak vorticity squared scales as WMAX * L^2 (curl divided by dx); physical core area in a z
slice scales as CORE / L^3 (cells) / dx.

## Predictions
- C1 every tick, every L: occupancy in 0..2; mass and energy equal their tick-0 values.
- C2 caps: JMAX <= JCAP and WMAX <= WCAP at every tick and L, where JCAP = max |j|^2 over every cell
  state (computed exactly in the program by enumeration) and WCAP = 3 * (4 * JAXIS)^2 with JAXIS the
  largest single momentum component of a cell (computed the same way).
- C3 the cap rises with resolution: P(L) = (max over ticks of WMAX) * L^2 is strictly increasing,
  P(24) < P(48) < P(96).
- C4 the core shrinks with resolution but never below the grid: min over ticks of CORE >= 1 at every L,
  and the minimum physical core volume, (min CORE) / L^3, is strictly decreasing in L.
- C5 measured, not predicted: max WMAX / WCAP at each L (how close each run gets to its cap), the tick
  of peak vorticity, and P(96)/P(48) against P(48)/P(24).
Any build failure or missing row is INCONCLUSIVE.
