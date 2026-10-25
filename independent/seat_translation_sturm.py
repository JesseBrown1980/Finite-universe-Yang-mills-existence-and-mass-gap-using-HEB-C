#!/usr/bin/env python3
"""Exact-integer Sturm inertia across four translation characters.

Input matrices from seat_translation_sectors.py, each pinned to SHA256.
Identical proof semantics to full 1393-dimensional interval Sturm:
B = W (1000 JE E + 1000 JB M - T I). 30 decimal integer guard digits
by default; every quotient is integer outward-rounded and every pivot
must be sign-definite. Sum of negative counts = full matrix inertia.
No Python Fraction, float, Decimal, JSON or numerical eigensolver.
"""
from hashlib import sha256
from pathlib import Path
from time import monotonic_ns
import sys
from seat_translation_sectors import EXPECTED_BLOCK_SHA, EXPECTED_DIM

PRECISION_DEFAULT = 30


def ceil_div(a, b):
    assert b != 0
    return -((-a) // b)


def quotient(x, y, d):
    """Scaled integer outward-rounded enclosure of x*y/d."""
    if d[0] <= 0 <= d[1]:
        raise ValueError("ambiguous pivot")
    p = (x[0] * y[0], x[0] * y[1], x[1] * y[0], x[1] * y[1])
    low, high = min(p), max(p)
    dl, dh = d
    if dh < 0:
        low, high, dl, dh = -high, -low, -dh, -dl
    if low >= 0:
        return low // dh, ceil_div(high, dl)
    if high <= 0:
        return low // dl, ceil_div(high, dh)
    return low // dl, ceil_div(high, dl)


def selftest():
    for al in range(-3, 4):
        for ah in range(al, 4):
            for bl in range(-3, 4):
                for bh in range(bl, 4):
                    for dl in range(1, 4):
                        for dh in range(dl, 4):
                            for sign in (-1, 1):
                                d = (dl, dh) if sign == 1 else (-dh, -dl)
                                out = quotient((al, ah), (bl, bh), d)
                                for x in range(al, ah + 1):
                                    for y in range(bl, bh + 1):
                                        for z in range(dl, dh + 1):
                                            n, v = x * y, sign * z
                                            assert out[0] <= n // v
                                            assert out[1] >= ceil_div(n, v)
    return True


def read_matrix(directory, name, je, jb, t, digits):
    path = directory / (name + ".matrix")
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != EXPECTED_BLOCK_SHA[name]:
        raise ValueError("sector source SHA mismatch: " + name)
    tok = raw.split()
    n = int(tok[0])
    if n != EXPECTED_DIM[name]:
        raise ValueError("sector size mismatch")
    w = list(map(int, tok[1:1 + n]))
    m = list(map(int, tok[1 + n:1 + 2*n]))
    rest = tok[1 + 2*n:]
    if len(rest) % 3 or any(z <= 0 for z in w):
        raise ValueError("sector format error")
    scale = 10 ** digits
    A = [dict() for _ in range(n)]
    rows = [dict() for _ in range(n)]
    for k in range(0, len(rest), 3):
        i, j, z = map(int, rest[k:k+3])
        if not 0 <= i <= j < n or j in rows[i]:
            raise ValueError("invalid upper-triangle record")
        rows[i][j] = z
        if z:
            a = 1000 * je * w[i] * z * scale
            A[i][j] = a, a
            A[j][i] = a, a
    for i in range(n):
        for j,z in rows[i].items():
            if i != j and j not in A[i]:
                raise ValueError("missing edge")
            if i != j:
                # The duplicated symmetric entries were made using the
                # source's exact positive orbit weights, not floats.
                assert A[i][j] == A[j][i]
    for i in range(n):
        d = (1000 * jb * m[i] - t) * w[i] * scale
        original = A[i].get(i, (0, 0))
        A[i][i] = (original[0] + d, original[1] + d)
    return A


def inertia(A):
    n = len(A)
    active = set(range(n))
    negative = 0
    for step in range(n):
        chosen, chosen_rank = None, None
        for i in active:
            d = A[i].get(i)
            if d is None or d[0] <= 0 <= d[1]:
                continue
            key = (len(A[i]), d[1] - d[0])
            if chosen_rank is None or key < chosen_rank:
                chosen, chosen_rank = i, key
        if chosen is None:
            return negative, step, "UNCERTAIN"
        k = chosen
        pivot = A[k][k]
        if pivot[1] < 0:
            negative += 1
        neighbors = [(j, v) for j, v in A[k].items() if j != k]
        for x, (i, vi) in enumerate(neighbors):
            for j, vj in neighbors[x:]:
                change = quotient(vi, vj, pivot)
                old = A[i].get(j, (0, 0))
                next_value = (old[0] - change[1], old[1] - change[0])
                if next_value == (0, 0):
                    A[i].pop(j, None)
                    A[j].pop(i, None)
                else:
                    A[i][j] = next_value
                    A[j][i] = next_value
        for j in list(A[k]):
            if j != k:
                A[j].pop(k, None)
        A[k].clear()
        active.remove(k)
    return negative, n, "COMPLETE"


def run(directory, je, jb, t, digits, expected=None):
    assert type(je) is int and type(jb) is int and type(t) is int
    assert je > 0 and jb >= 0 and digits in (20, 30, 40, 60, 80, 100)
    assert selftest()
    negative = 0
    by_sector = []
    for name in ("pp", "pm", "mp", "mm"):
        n = EXPECTED_DIM[name]
        result, checked, verdict = inertia(read_matrix(directory, name, je, jb, t, digits))
        if checked != n or verdict != "COMPLETE":
            raise ValueError(f"uncertified sector {name}: {checked}/{n}, {verdict}")
        negative += result
        by_sector.append(name + ":" + str(result))
    if expected is not None and negative != expected:
        raise ValueError("inertia differs from pinned known control")
    return (f"HEBC-TRANSLATION-STURM|result=PASS|JE={je}|JB={jb}|"
            f"threshold={t}/1000|scale_digits={digits}|pivots=1393/1393|"
            f"negative={negative}|sector_negatives={','.join(by_sector)}|"
            f"ambiguous=0|method=INTEGER_INTERVAL_SCHUR_DIRECT_SUM|json=0")


if __name__ == "__main__":
    if not 5 <= len(sys.argv) <= 7:
        raise SystemExit("usage: seat_translation_sturm.py DIR JE JB T_NUM [DIGITS] [EXPECTED_NEGATIVE]")
    t0 = monotonic_ns()
    directory = Path(sys.argv[1])
    je, jb, t = map(int, sys.argv[2:5])
    digits = int(sys.argv[5]) if len(sys.argv) > 5 else PRECISION_DEFAULT
    expected = int(sys.argv[6]) if len(sys.argv) > 6 else None
    result = run(directory, je, jb, t, digits, expected)
    print(result)
    print("HEBC-TRANSLATION-TIME|elapsed_ms=" + str((monotonic_ns()-t0)//1000000) +
          "|integer_clock=monotonic_ns|json=0", file=sys.stderr)
