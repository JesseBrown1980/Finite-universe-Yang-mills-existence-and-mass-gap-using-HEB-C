#!/usr/bin/env python3
"""pull_v23.py -- how does a pull fall off with distance under two delivery rules?  See SPEC-PULL-V23.hbp.
An attractor sits in one room. A probe room sits d rooms away (d = 3, 6, 12). Integers only.
  GLOBAL  the operator's rule: every change is in the global hash at once. Each tick the probe draws one event
          uniformly from everything in the hash: 1 attractor event and B background events. A draw of the
          attractor's event is one pull.
  LOCAL   the attractor's events leave it as quanta travelling in straight lines in random directions, one room
          per tick. A quantum that passes through the probe's room is one pull.
Nothing about distance is written into either rule.   python pull_v23.py <quanta> <ticks> <background> <seed>
"""
import sys
MASK = 0xFFFFFFFFFFFFFFFF
def mixer(seed):
    st = [seed & MASK]
    def nxt():
        st[0] = (st[0] + 0x9E3779B97F4A7C15) & MASK
        z = st[0]
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
        return z ^ (z >> 31)
    return nxt
Q = int(sys.argv[1]); T = int(sys.argv[2]); B = int(sys.argv[3]); seed = int(sys.argv[4]); r = mixer(seed)
DS = (3, 6, 12); R = 1 << 20
hit = {d: 0 for d in DS}; sent = 0
while sent < Q:
    x = r() % (2 * R + 1) - R; y = r() % (2 * R + 1) - R; z = r() % (2 * R + 1) - R
    if x * x + y * y + z * z > R * R or (x == 0 and y == 0 and z == 0):
        continue                                  # keep directions uniform over the sphere
    sent += 1
    if x > 0:
        ay = abs(y); az = abs(z)
        for d in DS:                              # exact: the ray meets the unit room centred at (d, 0, 0)
            if (2 * d - 1) * ay <= x and (2 * d - 1) * az <= x:
                hit[d] += 1
glob = {d: 0 for d in DS}
for d in DS:
    for _ in range(T):
        if r() % (B + 1) == 0:
            glob[d] += 1
print("PULL|rule=LOCAL|quanta=%d|pulls_at_3=%d|at_6=%d|at_12=%d|ratio_3_to_6_thousandths=%d|ratio_6_to_12_thousandths=%d|inverse_square_would_give=4000|json=0" % (
    Q, hit[3], hit[6], hit[12], 1000 * hit[3] // hit[6], 1000 * hit[6] // hit[12]))
print("PULL|rule=GLOBAL|ticks=%d|background=%d|pulls_at_3=%d|at_6=%d|at_12=%d|ratio_3_to_6_thousandths=%d|ratio_6_to_12_thousandths=%d|no_falloff_would_give=1000|json=0" % (
    T, B, glob[3], glob[6], glob[12], 1000 * glob[3] // glob[6], 1000 * glob[6] // glob[12]))
