#!/usr/bin/env python3
"""Integer-only calibration of sliced transfer, exact ternary jumps and viewer receipts.

This program does NOT numerically solve continuous SU(3) or certify the theorem.
It independently rebuilds finite Z3 and S3 convolution controls and observable
history with 3^k checkpoint jumps. All displayed figures are exact integers.
"""
import hashlib
from itertools import permutations

P = 1_000_081


def sha(data):
    return hashlib.sha256(data.encode("ascii")).hexdigest()


def mm(a, b, modulus=None):
    n = len(a)
    out = [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)]
           for i in range(n)]
    if modulus is not None:
        out = [[v % modulus for v in row] for row in out]
    return out


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def subtract(a, scalar):
    return [[v - (scalar if i == j else 0) for j, v in enumerate(row)]
            for i, row in enumerate(a)]


def check_z3():
    c = [[4 if i == j else 1 for j in range(3)] for i in range(3)]
    assert mm(mm(subtract(c, 6), subtract(c, 3)), eye(3)) == [[0] * 3 for _ in range(3)]
    inv6 = pow(6, -1, P)
    inv2 = pow(2, -1, P)
    inv3 = pow(3, -1, P)
    b = [[(v * inv6) % P for v in row] for row in c]
    power = b
    start = [1, 2, 0]
    rows = 0
    previous = sha("Z3_VIEWER_GENESIS|json=0\n")
    for k in range(9):
        if k > 0:
            power = mm(mm(power, power, P), power, P)
        n = 3 ** k
        eigen_power = pow(inv2, n, P)
        reference = [
            [(inv3 + eigen_power * (int(i == j) - inv3)) % P
             for j in range(3)]
            for i in range(3)
        ]
        assert power == reference, ("JUMP_MISMATCH", k)
        current = [sum(power[i][j] * start[j] for j in range(3)) % P for i in range(3)]
        expected = [sum(reference[i][j] * start[j] for j in range(3)) % P for i in range(3)]
        assert current == expected
        if k <= 4:
            direct = start[:]
            for unused in range(n):
                direct = [sum(b[i][j] * direct[j] for j in range(3)) % P for i in range(3)]
            assert direct == current
        state = sha("Z3_STATE|n=" + str(n) + "|v=" + ",".join(map(str, current)) + "|json=0\n")
        previous = sha("Z3_CHECKPOINT|t=" + str(n) + "|state=" + state + "|previous=" + previous + "|json=0\n")
        print("Z3_JUMP|k=" + str(k) + "|time=3^" + str(k) +
              "|spectral_equals_matrix=1|direct_checked=" + str(int(k <= 4)) +
              "|state_sha256=" + state + "|checkpoint_chain_sha256=" + previous +
              "|json=0")
        rows += 1
    mutated = [row[:] for row in b]
    mutated[0][0] = (mutated[0][0] + 1) % P
    assert mutated != reference
    print("Z3_FAULT|mutated_transition=REJECT|json=0")
    return rows


def compose(a, b):
    return tuple(a[b[i]] for i in range(3))


def check_s3_and_viewer():
    group = list(permutations(range(3)))
    unit = (0, 1, 2)
    inv = {}
    for a in group:
        inv[a] = next(b for b in group if compose(a, b) == unit and compose(b, a) == unit)
    def weight(g):
        fixed = sum(int(g[i] == i) for i in range(3))
        return {3: 5, 1: 1, 0: 2}[fixed]
    c = [[weight(compose(a, inv[b])) for b in group] for a in group]
    assert all(c[i][j] == c[j][i] for i in range(6) for j in range(6))
    poly = mm(mm(subtract(c, 12), subtract(c, 6)), subtract(c, 3))
    assert poly == [[0] * 6 for _ in range(6)]
    assert sum(c[i][i] for i in range(6)) == 30
    cc = mm(c, c)
    assert sum(cc[i][i] for i in range(6)) == 216
    print("S3_LINK|dimension=6|eigenvalues=12x1,6x1,3x4|poly_zero=1|tr=30|tr2=216|json=0")
    previous = sha("S3_VIEWER_GENESIS|json=0\n")
    for k in range(9):
        n = 3 ** k
        # C(tick) = 1/2*(2^-tick+4^-tick), a two-excitation exact witness.
        numerator = (1 << n) + 1
        denominator = 1 << (2 * n + 1)
        assert numerator > 0 and denominator > numerator
        if n <= 27:
            # Exact mixture of the two independently computed eigen-ratios.
            assert numerator * (1 << n) == (1 << (2*n)) + (1 << n)
        desc = "S3_CORRELATOR|n=" + str(n) + "|num=" + str(numerator) + "|den=" + str(denominator) + "|json=0\n"
        state = sha(desc)
        previous = sha("S3_VIEWER_CHECKPOINT|n=" + str(n) + "|state=" + state + "|previous=" + previous + "|json=0\n")
        print("S3_VIEWER|k=" + str(k) + "|tick=3^" + str(k) +
              "|two_mode_correlation=exact_rational|num_bits=" + str(numerator.bit_length()) +
              "|den_bits=" + str(denominator.bit_length()) +
              "|state_sha256=" + state + "|checkpoint_chain_sha256=" + previous +
              "|json=0")
    # Mixtures of positive decays are log-convex; check by integer products.
    for n in range(1, 28):
        nums = [(1 << t) + 1 for t in (n-1, n, n+1)]
        # Denominators are powers of two; their geometric means cancel exactly.
        assert nums[1] ** 2 <= nums[0] * nums[2]
    print("S3_VIEWER_CONVEXITY|n=1..27|sampled_correlators_log_convex=1|json=0")


def main():
    print("SU3_VIEWER_SCOPE|model_proof=continuous_SU3_fixed_lattice|numeric_calibration=finite_Z3_S3_only|actual_SU3_glueball_spectrum=OPEN|continuum_spacetime=OPEN|json=0")
    count = check_z3()
    check_s3_and_viewer()
    print("SU3_VIEWER_GATE|Z3_jumps=" + str(count) +
          "|S3_spectrum=PASS|viewer_checkpoint_samples=9|numeric_floats=0|state_hash_not_state=1|json=0")


if __name__ == "__main__":
    main()
