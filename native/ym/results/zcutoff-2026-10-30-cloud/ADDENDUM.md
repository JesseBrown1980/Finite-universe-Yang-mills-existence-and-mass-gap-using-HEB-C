# Addendum 1 (sealed after run 1, before run 2)

Run 1 (`RESULT.hbp`, C1 to C4 PASS) stays the registered result for PREREG.md. Its C3 and C4 use the
cell maximum WMAX and a half-maximum core count. The Taylor–Green noise test (seal a83e8f18…) showed
this lattice's fine-scale vorticity sits at a thermal noise floor, so those two measures may track noise
and the L^2 unit factor rather than the vortex. Run 2 adds, without changing run 1's arm or rows:

Arms at each L: DRIVE (run 1's arm) and CONTROL (the same cells and ticks pushed, with the x and y push
signs taken from bits of (31 * cell + 17 * t) instead of the swirl).

Diagnostics per tick:
- OZ = sum over z of curl_z j at the 4 cells x, y in {L/2 - 1, L/2} (undivided differences). It sums
  4L cells along the vortex line, so cell noise averages down; physical axis vorticity is proportional
  to OZ / 4 at every L (mean over 4L cells, divided by dx = 1/L).
- Radial swirl profile: rings k = floor(sqrt(d2) / 2) in doubled coordinates; per ring the sum of
  a = jx * (-dy2) + jy * dx2 (r times the azimuthal momentum, up to a factor 2) and the cell count.
  RCORE = the ring with the largest mean azimuthal momentum, sum_a / (count * (2k + 1)), the edge of
  the vortex core in cells.

Predictions:
- A1 the vortex is real: at every L, max over ticks of OZ (DRIVE) > 10 * max over ticks of |OZ| (CONTROL).
- A2 concentration rises with resolution: peak OZ (DRIVE) is strictly increasing, L = 24 < 48 < 96.
- A3 the cell maximum is noise: at every L, max WMAX of CONTROL is within 25% of max WMAX of DRIVE.
- A4 measured, not predicted: RCORE (cells and as a fraction of L) at the end of the drive and its
  minimum over ticks, with the peak OZ ratios between resolutions.
Run 2 must reproduce every run-1 line byte for byte; its new values are on new lines.
