# A second path for the integer Cantor drive: Python integers only, written apart from cantorint.rs, with its own signal construction, precision and series.
# It takes the Taylor series of exp(-i H / 27) with no spectral shift, at 200 bits, forward only, and prints enclosures at scale 10^30 for one control.
#
# usage: verify_cantorint.py MATRIX R CONTROL
# Bound, in units of 2^-200 and in the weighted norm: 729 slots of (K 3^ceil(x) ceil(sqrt(2 sum w)) + ceil(sqrt(w_b)) + 1), with x >= ||H|| / 27 from the largest row sum.
# Integer only, json=0.
import hashlib, sys
from math import isqrt

MATRIX, R, CONTROL = sys.argv[1], int(sys.argv[2]), sys.argv[3]
P = 200
SCALE = 10 ** 30


def pulses():
    # The signal by the Cantor recursion, which is not how the Rust tool builds it.
    seq = [1]
    for _ in range(6):
        seq = seq + [0] * len(seq) + [3 - v if v else 0 for v in seq]
    if hashlib.sha256(bytes(seq)).hexdigest() != "1f48fa5083237cd4bdadc3f6c4f9094b864ca1386d7d09b5b27c19b5f27f6913":
        raise SystemExit("the signal differs")
    return [{0: 0, 1: 1, 2: -1}[v] for v in seq]


raw = open(MATRIX, "rb").read()
tok = [int(x) for x in raw.split()]
n = tok[0]
w, m = tok[1:1 + n], tok[1 + n:1 + 2 * n]
off = [[] for _ in range(n)]
ed = [0] * n
for k in range(1 + 2 * n, len(tok), 3):
    i, j, z = tok[k], tok[k + 1], tok[k + 2]
    if i == j:
        ed[i] = z
    else:
        if (w[i] * z) % w[j]:
            raise SystemExit("a reverse entry is not an integer")
        off[i].append((j, 27 * z))
        off[j].append((i, 27 * (w[i] * z // w[j])))
sig = pulses()
if CONTROL == "cantor":
    seq = sig
elif CONTROL == "zero":
    seq = [0] * len(sig)
elif CONTROL == "inverted":
    seq = [-v for v in sig]
elif CONTROL == "rotated_one":
    seq = sig[1:] + sig[:1]
else:
    raise SystemExit("a control of another name")
diag = {f: [27 * ed[i] + (27 * R + f) * m[i] for i in range(n)] for f in (-1, 0, 1)}
row_sum = max(sum(abs(z) for _, z in off[i]) + max(abs(diag[f][i]) for f in diag) for i in range(n))
# The least K with x^(K+1) / (K+1)! <= 2^-P, with x = row_sum / 729.
K, top, bot = 0, row_sum << P, 729
while top > bot:
    K += 1
    top *= row_sum
    bot *= 729 * (K + 1)
x_ceil = -(-row_sum // 729)


def int_power(base, exponent):
    """base to a whole exponent at or above zero, by squaring, in ints. A negative exponent raises ValueError, where ** on two ints gives floating point."""
    if not isinstance(exponent, int):
        raise TypeError("int_power takes an int exponent, not %s" % type(exponent).__name__)
    if exponent < 0:
        raise ValueError("int_power takes an exponent at or above zero, not %d" % exponent)
    result = 1
    while exponent:
        if exponent & 1:
            result *= base
        exponent >>= 1
        if exponent:
            base *= base
    return result


def root_up(v):
    s = isqrt(v)
    return s if s * s == v else s + 1


delta = 729 * (K * int_power(3, x_ceil) * root_up(2 * sum(w)) + root_up(w[0]) + 1)
re, im = [0] * n, [0] * n
re[0] = 1 << P
for f in seq:
    d = diag[f]
    tre, tim = re[:], im[:]
    for term in range(1, K + 1):
        den = 729 * term
        nre, nim = [0] * n, [0] * n
        for i in range(n):
            a, b = d[i] * tre[i], d[i] * tim[i]
            for j, z in off[i]:
                a += z * tre[j]
                b += z * tim[j]
            # -i (a + i b) = b - i a, with Python's floor division.
            nre[i] = b // den
            nim[i] = -a // den
        tre, tim = nre, nim
        for i in range(n):
            re[i] += tre[i]
            im[i] += tim[i]
unit2 = 1 << (2 * P)
top_m = sum(w[i] * m[i] * (re[i] ** 2 + im[i] ** 2) for i in range(n))
top_r = re[0] ** 2 + im[0] ** 2
top_n = sum(w[i] * (re[i] ** 2 + im[i] ** 2) for i in range(n))
err = 2 * delta * (1 << P) + delta * delta


def enclosure(top, big_a):
    lo = ((top - big_a * err) * SCALE) // (w[0] * unit2)
    hi = -((-(top + big_a * err) * SCALE) // (w[0] * unit2))
    return lo, hi


mlo, mhi = enclosure(top_m, max(m))
rlo, rhi = enclosure(top_r * w[0], 1)
print("SECOND_PATH|control=%s|r=%d|P=%d|K=%d|row_sum=%d|delta_bits=%d|magnetic_expectation_lo_e30=%d|magnetic_expectation_hi_e30=%d|return_probability_lo_e30=%d|return_probability_hi_e30=%d|norm_dev_bits=%d|json=0" % (CONTROL, R, P, K, row_sum, delta.bit_length(), mlo, mhi, rlo, rhi, abs(top_n - w[0] * unit2).bit_length()))
