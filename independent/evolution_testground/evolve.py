#!/usr/bin/env python3
"""
Let it evolve, then measure: Euclidean-time relaxation of the finite S3
2x2-torus Hamiltonian H = JE*E + JB*M, integer-only (HEB-C rule).

Every excited state decays faster than the ground state under v <- (c - H) v,
c above the spectrum. The energy E(k) = <v,Hv>_W / <v,v>_W settles to E0 and
its successive drops shrink by rho^2 per step, rho = (c - E1)/(c - E0).
So the measured gap is  (c - E0) * (1 - rho).  This is a MEASUREMENT, not a
certificate; it is compared against the certified Sturm brackets.

Integer form: orbit weights are 1,2,3,4,6,8,12,24, so A = 24*H is an integer
matrix (A_ij = 24*z_ij for i<=j, A_ji = 24*w_i*z_ij / w_j, exact). The vector
is rescaled by integer right-shifts to stay near 2^BITS. Start vector is a
deterministic integer LCG sequence, so it overlaps every symmetry sector
(a perfectly symmetric start would only ever see symmetric excitations).

No float, Decimal or Fraction anywhere; energies are reported in integer
milli-units of JE.
"""
import math

BITS = 120
SCALE = 10 ** 40          # fixed-point scale for energies inside the estimator


def load(path):
    t = open(path).read().split()
    n = int(t[0])
    w = [int(x) for x in t[1:1 + n]]
    mag = [int(x) for x in t[1 + n:1 + 2 * n]]
    rest = t[1 + 2 * n:]
    rows = [dict() for _ in range(n)]
    for k in range(0, len(rest), 3):
        i, j, z = int(rest[k]), int(rest[k + 1]), int(rest[k + 2])
        if not z:
            continue
        rows[i][j] = 24 * z
        if i != j:
            num = 24 * w[i] * z
            if num % w[j]:
                raise SystemExit("EVOLVE|error=non_integer_24H|json=0")
            rows[j][i] = num // w[j]
    return n, w, mag, rows


def operator(rows, mag, je, jb):
    """Integer A = 24*(JE*E + JB*M) as a list of (index, value) rows."""
    out = []
    for i, row in enumerate(rows):
        r = {j: je * v for j, v in row.items()}
        r[i] = r.get(i, 0) + 24 * jb * mag[i]
        out.append(sorted((j, v) for j, v in r.items() if v))
    return out


def gershgorin_top(A):
    return max(sum(abs(v) for _, v in row) for row in A)


def evolve(path, je, jb, steps=4000):
    n, w, mag, rows = load(path)
    A = operator(rows, mag, je, jb)
    c24 = gershgorin_top(A) + 24                       # c above the spectrum (in units of 1/24)
    seed, v = 12345, []
    for _ in range(n):
        seed = (seed * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        v.append((seed >> 11) - (1 << 52))
    energies = []
    for _ in range(steps):
        Av = [sum(a * v[j] for j, a in row) for row in A]
        num = sum(w[i] * v[i] * Av[i] for i in range(n))      # 24*<v,Hv>_W
        den = sum(w[i] * v[i] * v[i] for i in range(n))       # <v,v>_W
        energies.append((SCALE * num) // (24 * den))           # E(k)*SCALE, per JE when je=1
        v = [c24 * v[i] - Av[i] for i in range(n)]            # v <- 24*(c - H) v
        top = max(abs(x) for x in v)
        shift = top.bit_length() - BITS
        if shift > 0:
            v = [x >> shift for x in v]
    return energies, c24


def measure_gap(energies, c24, je, tail=40):
    """Gap from the geometric decay of successive energy drops, integer-only.
    Uses the LAST `tail` clean drops (late time, where only E1 still decays;
    early drops are contaminated by faster higher states) and their median
    ratio. Returns (gap, E0) in milli-units per JE, or (None, None)."""
    d = [energies[k] - energies[k + 1] for k in range(len(energies) - 1)]
    clean = [k for k in range(len(d) - 1) if d[k] > 10 ** 8 and d[k + 1] > 10 ** 8]
    if len(clean) < 5:
        return None, None
    ratios = sorted((d[k + 1] * SCALE) // d[k] for k in clean[-tail:])
    rho2 = ratios[len(ratios) // 2]                    # rho^2 * SCALE
    rho = math.isqrt(rho2 * SCALE)                     # rho * SCALE
    e0 = energies[-1]                                  # E0 * SCALE (settled)
    c = (c24 * SCALE) // 24
    gap = ((c - e0) * (SCALE - rho)) // SCALE          # gap * SCALE
    return (gap * 1000) // (SCALE * je), (e0 * 1000) // (SCALE * je)
