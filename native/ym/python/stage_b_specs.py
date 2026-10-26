#!/usr/bin/env python3
"""Stage B count specs for a lattice from a sealed stage A receipt.

Refuses unless every cluster shard in the receipt reports converged=1 (the
10/10 gate, applied here as well because run 40318106269 predates it in the
workflow) and the 8 lowest intervals per coupling are 7 from (+,+) and 1 from
(-,-). Thresholds follow volume_point.py exactly:
  t0 = lowest lo - 2, ts = second lo - 2 (if the first two intervals are
  separated), t1 = max hi of the 8 lowest + 2, tB = floor(E9 lo/1000)*1000 - 1000.
Prints one backend count spec per line (JE=1000, JB=1000*r): vacuum sectors at
t0/ts/t1/tB, mixed sectors at tB. Stage B cells must additionally require
ambiguous=0 and result=PASS in each count line; an AMBIGUOUS count is a
failed cell, never a certificate.
usage: stage_b_specs.py SEALED_STAGE_A LX LY        json=0
"""
import re
import sys


def main():
    path, lx, ly = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    ivs, conv, n_cluster = {}, {}, 0
    pat = re.compile(r"^SHARD\|cluster_%d_%d_(-?1)_(-?1)_1_(\d+)_12_4\|(.*)$" % (lx, ly))
    for line in open(path):
        m = pat.match(line.rstrip("\n"))
        if not m:
            continue
        s, r, body = (int(m.group(1)), int(m.group(2))), int(m.group(3)), m.group(4)
        if body.startswith("CLUSTER|"):
            n_cluster += 1
            conv[(s, r)] = "|converged=1|" in body
        elif body.startswith("CLUSTER_LEVEL|"):
            iv = re.search(r"interval=\[(\d+),(\d+)\]", body)
            ivs.setdefault(r, []).append((int(iv.group(1)), int(iv.group(2)), s))
    if not conv or not all(conv.values()):
        print("STAGE_B|result=FAIL|reason=clusters_converged=%d/%d|json=0" % (sum(conv.values()), len(conv)))
        sys.exit(2)
    for r in sorted(ivs):
        v = sorted(ivs[r])
        low8 = v[:8]
        if sum(1 for x in low8 if x[2] == (1, 1)) != 7 or sum(1 for x in low8 if x[2] == (-1, -1)) != 1:
            print("STAGE_B|r=%d|result=FAIL|reason=lowest8_not_7_plus_1|json=0" % r)
            sys.exit(2)
        t0 = low8[0][0] - 2
        t1 = max(x[1] for x in low8) + 2
        tb = v[8][0] // 1000 * 1000 - 1000
        ts = low8[1][0] - 2 if low8[0][1] < low8[1][0] - 2 else None
        if not t1 < tb:
            print("STAGE_B|r=%d|result=FAIL|reason=t1_not_below_tB|json=0" % r)
            sys.exit(2)
        jb = 1000 * r
        c = lambda s, t, fd, tol: print("count/%d/%d/%d/%d/1000/%d/%d/%d/%d" % (lx, ly, s[0], s[1], jb, t, fd, tol))
        c((1, 1), t0, 13, 10)
        if ts is not None:
            c((1, 1), ts, 13, 10)
            c((-1, -1), ts, 13, 10)
        else:
            c((-1, -1), t0, 13, 10)
        for s in ((1, 1), (-1, -1)):
            c(s, t1, 12, 1000)
        for s in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
            c(s, tb, 12, 1000)
    print("STAGE_B|L=%dx%d|clusters_converged=%d/%d|couplings=%s|result=PASS|json=0" % (lx, ly, sum(conv.values()), len(conv), ",".join(map(str, sorted(ivs)))), file=sys.stderr)


if __name__ == "__main__":
    main()
