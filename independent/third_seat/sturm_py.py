#!/usr/bin/env python3
"""
Third-seat interval Sturm inertia check for the finite S3 2x2-torus operator
(PR #9 reproduction without GMP). Written independently of
seat_sturm_biginterval.cpp: Python arbitrary-precision integers, its own
scale (10^SCALE_DIGITS), its own pivot rule (smallest current row degree,
ties broken by smallest pivot-interval width relative to magnitude).

Matrix input: the integer exchange file from seat_sturm_integer_matrix.py
  n, then n weights w, n magnetic values mag, then upper-triangle "i j z".
B = W (1000 H - t I), H = JE * E + JB * diag(mag), entries (W E)_ij = w_i z_ij.
B is congruent to 1000 W^1/2 H W^-1/2 - t W, whose inertia equals that of
H - (t/1000) I when H is W-self-adjoint, so #negative pivots = #eigenvalues
of H below t/1000. A pivot is used only if its interval excludes zero.

Every Schur update x*y/d is enclosed outward: numerator range from the four
corner products, divided by the extreme denominator in each sign case, floor
below and ceiling above (Python // is floor division for all signs).
Integer arithmetic only, timing included (monotonic_ns, integer ms). Output lines end json=0.
usage: sturm_py.py MATRIX JE JB T_NUM [SCALE_DIGITS]
"""
import sys
import time


def cdiv(a, b):
    return -((-a) // b)


def quotient(x, y, d):
    """Outward enclosure of {a*b/c : a in x, b in y, c in d}, 0 not in d."""
    if d[0] <= 0 <= d[1]:
        raise ValueError("pivot interval contains zero")
    p = (x[0] * y[0], x[0] * y[1], x[1] * y[0], x[1] * y[1])
    lo, hi = min(p), max(p)
    dlo, dhi = d
    if dhi < 0:
        lo, hi, dlo, dhi = -hi, -lo, -d[1], -d[0]
    if lo >= 0:
        return lo // dhi, cdiv(hi, dlo)
    if hi <= 0:
        return lo // dlo, cdiv(hi, dhi)
    return lo // dlo, cdiv(hi, dlo)


def selftest():
    import itertools
    for al, ah, bl, bh in itertools.product(range(-3, 4), repeat=4):
        if al > ah or bl > bh:
            continue
        for dl in range(1, 4):
            for dh in range(dl, 4):
                for s in (1, -1):
                    d = (dl, dh) if s == 1 else (-dh, -dl)
                    q = quotient((al, ah), (bl, bh), d)
                    for a in range(al, ah + 1):
                        for b in range(bl, bh + 1):
                            for c in range(dl, dh + 1):
                                n, den = a * b, s * c
                                if q[0] > n // den or q[1] < cdiv(n, den):
                                    return False
    return True


def load(path, je, jb, tn, scale):
    tok = open(path).read().split()
    n = int(tok[0])
    w = [int(v) for v in tok[1:1 + n]]
    mag = [int(v) for v in tok[1 + n:1 + 2 * n]]
    rest = tok[1 + 2 * n:]
    if len(rest) % 3 or any(v <= 0 for v in w):
        raise ValueError("malformed matrix file")
    a = [dict() for _ in range(n)]
    for k in range(0, len(rest), 3):
        i, j, z = int(rest[k]), int(rest[k + 1]), int(rest[k + 2])
        if not 0 <= i <= j < n or j in a[i]:
            raise ValueError("bad entry")
        if z:
            v = 1000 * je * w[i] * z * scale
            a[i][j] = (v, v)
            a[j][i] = (v, v)
    for k in range(n):
        dv = (1000 * jb * mag[k] * w[k] - tn * w[k]) * scale
        old = a[k].get(k, (0, 0))
        a[k][k] = (old[0] + dv, old[1] + dv)
    return a, len(rest) // 3


def certify(a):
    n = len(a)
    active = set(range(n))
    neg = pos = 0
    t0 = time.monotonic_ns()
    for step in range(n):
        best, key = None, None
        for i in active:
            d = a[i].get(i)
            if d is None or d[0] <= 0 <= d[1]:
                continue
            k = (len(a[i]), d[1] - d[0])
            if key is None or k < key:
                best, key = i, k
        if best is None:
            return neg, pos, step, "UNCERTAIN"
        k = best
        d = a[k][k]
        if d[1] < 0:
            neg += 1
        else:
            pos += 1
        nb = [(j, v) for j, v in a[k].items() if j != k]
        for x in range(len(nb)):
            i, vi = nb[x]
            for y in range(x, len(nb)):
                j, vj = nb[y]
                c = quotient(vi, vj, d)
                o = a[i].get(j, (0, 0))
                v = (o[0] - c[1], o[1] - c[0])
                if v == (0, 0):
                    a[i].pop(j, None)
                    a[j].pop(i, None)
                else:
                    a[i][j] = v
                    a[j][i] = v
        for j in list(a[k]):
            if j != k:
                a[j].pop(k, None)
        a[k].clear()
        active.discard(k)
        if (step + 1) % 100 == 0:
            print("PROGRESS|pivots=%d/%d|negative=%d|elapsed_ms=%d|json=0" % (step + 1, n, neg, (time.monotonic_ns() - t0) // 1000000),
                  file=sys.stderr, flush=True)
    return neg, pos, n, "COMPLETE"


def main():
    if not selftest():
        sys.exit("FAIL|reason=interval arithmetic selftest|json=0")
    path, je, jb, tn = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    digits = int(sys.argv[5]) if len(sys.argv) > 5 else 80
    a, entries = load(path, je, jb, tn, 10 ** digits)
    t0 = time.monotonic_ns()
    neg, pos, done, status = certify(a)
    ok = status == "COMPLETE" and neg == 1
    print("STURM-PY|result=%s|status=%s|JE=%d|JB=%d|threshold=%d/1000|scale_digits=%d|upper_entries=%d"
          "|pivots=%d/%d|negative=%d|positive=%d|ambiguous=0|E1_gt_threshold_certified=%d|elapsed_ms=%d|json=0"
          % ("PASS" if ok else "FAIL", status, je, jb, tn, digits, entries, done, len(a), neg, pos, int(ok),
             (time.monotonic_ns() - t0) // 1000000))
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
