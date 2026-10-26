# 2×L finite-volume ladder through the HEB-C HTTP-0 backend

Lattices 2×2, 2×3, 2×4, zero-momentum sector, r = JB/JE ∈ {9, 15, 27, 45, 81, 243}.
Each point comes from `python/volume_point.py`. It runs backend jobs (sector,
flatcomp, cluster, shellschur counts), sets thresholds by the fixed 3×3 rule,
and builds certificates with `shell_gap_cert.py --lattice`. Units: JE.

`check.sh` re-derives everything from the committed shards without running any
tool. It checks the flat-state bound, rebuilds all 18 point certificates (and
compares them with `certs_*.hbp`), and builds the monotone-cell + ray
continuation over r ∈ [9, ∞).

| r | 2×2 E9 − E8 | 2×3 E9 − E8 | 2×4 E9 − E8 | 3×3 E9 − E8 (frozen reference) |
|---|---|---|---|---|
| 9 | [22.829351, 22.830510] | [22.999140, 23.000177] | [22.833511, 22.835420] | [23.938578, 23.939630] |
| 15 | [42.498075, 42.499545] | [42.652240, 42.653390] | [42.529393, 42.530821] | [43.371514, 43.372787] |
| 27 | [79.625728, 79.626755] | [79.711705, 79.713463] | [79.639284, 79.640698] | [80.161963, 80.163325] |
| 45 | [134.179201, 134.180318] | [134.230005, 134.231391] | [134.185334, 134.187200] | [134.512046, 134.514099] |
| 81 | [242.543881, 242.545661] | [242.572553, 242.573741] | [242.548047, 242.549116] | [242.733980, 242.735244] |
| 243 | [728.847290, 728.848700] | [728.856505, 728.858026] | [728.848613, 728.849874] | [728.911221, 728.913186] |

First splitting E2 − E1:

| r | 2×2 | 2×3 | 2×4 | 3×3 |
|---|---|---|---|---|
| 9 | [0.154378, 0.154388] | [0.341105, 0.341115] | [0.457164, 0.457178] | [0.019821, 0.019847] |
| 27 | [0.048223, 0.048233] | [0.111394, 0.111404] | [0.148593, 0.148627] | [0.001967, 0.002059] |
| 81 | [0.015961, 0.015971] | [0.037039, 0.037057] | [0.049340, 0.049460] | [0.000074, 0.000370] |
| 243 | [0.005313, 0.005323] | [0.012322, 0.012370] | [0.016305, 0.016617] | inconclusive |

Continuation (monotone cells + ray; E8(r) ≤ 3·(2·LX·LY), from flatcomp): the gap above
the eight-state cluster is at least 22.727075 (2×2), 22.798240 (2×3) or
22.565393 (2×4) for every r ≥ 9.

These are finite lattices only. The gap above the cluster barely changes with
volume or shape. The first splitting grows with L along the 2×L family, close
to L/r at large r. It is third-order suppressed on 3×3. Nothing here is
uniform in volume.
