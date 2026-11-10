# T1 pre-freeze check 2: N_m = sum over orderings of the m links of a cyclic line of
# prod_{j=1}^{m-1} 1/arcs(first j links). Claim: N_m = binom(2m-2, m-1).
# Pure combinatorics on a cycle graph; no torus, no group. Integers only.
import itertools


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def arcs(sel, m):
    # number of maximal runs of selected nodes on the cycle C_m (proper nonempty subset)
    return sum(1 for i in range(m) if sel[i] and not sel[(i - 1) % m])


def binom(n, k):
    r = 1
    for i in range(k):
        r = r * (n - i) // (i + 1)
    return r


for m in range(2, 9):
    num, den = 0, 1
    for perm in itertools.permutations(range(m)):
        sel = [False] * m
        d = 1
        for j in range(m - 1):
            sel[perm[j]] = True
            d *= arcs(sel, m)
        num, den = num * d + den, den * d
        g = gcd(num, den)
        num, den = num // g, den // g
    print("N_m", m, str(num) + "/" + str(den), "binom", binom(2 * m - 2, m - 1))
    assert den == 1 and num == binom(2 * m - 2, m - 1)
print("CYCLE_ORDERINGS_OK")
