# T1 pre-freeze check 1: group-level facts about S3 used by NOTE.md.
# Integers only. No torus is built here. Run: python3 -I -B s3_gamma.py
import itertools

E = (0, 1, 2)
G = list(itertools.permutations(range(3)))


def mul(p, q):
    return tuple(p[q[i]] for i in range(3))


def inv(p):
    r = [0, 0, 0]
    for i in range(3):
        r[p[i]] = i
    return tuple(r)


def nfix(p):
    return sum(1 for i in range(3) if p[i] == i)


def kind(p):
    f = nfix(p)
    return "e" if f == 3 else ("T" if f == 1 else "C")


def sgn(p):
    return 1 if kind(p) in ("e", "C") else -1


T = [g for g in G if kind(g) == "T"]
assert len(T) == 3
comm = [(a, b) for a in G for b in G if mul(a, b) == mul(b, a)]
assert len(comm) == 18


def conj(c, p):
    return mul(mul(c, p), inv(c))


def flat_class(a, b):
    ka, kb = kind(a), kind(b)
    if ka == "e" and kb == "e":
        return 0
    if ka == "e" and kb == "T":
        return 1
    if ka == "e" and kb == "C":
        return 2
    if ka == "T" and kb == "e":
        return 3
    if ka == "T" and kb == "T":
        assert a == b
        return 4
    if ka == "C" and kb == "e":
        return 5
    if ka == "C" and b == a:
        return 6
    if ka == "C" and b == inv(a):
        return 7
    raise AssertionError


# orbits under simultaneous conjugation, checked against flat_class
orbits = {}
for (a, b) in comm:
    key = min((conj(c, a), conj(c, b)) for c in G)
    orbits.setdefault(key, set()).add((a, b))
assert len(orbits) == 8
weights = [0] * 8
for key, mem in orbits.items():
    labs = set(flat_class(a, b) for (a, b) in mem)
    assert len(labs) == 1
    weights[labs.pop()] = len(mem)
print("FLAT_ORBITS", len(orbits), "WEIGHTS", weights)
assert weights == [1, 3, 2, 3, 3, 2, 2, 2]

# representative per class
rep = [None] * 8
for (a, b) in comm:
    k = flat_class(a, b)
    if rep[k] is None:
        rep[k] = (a, b)


def gamma(direction):
    # A[src][tgt] = number of t in T giving the target class
    A = [[0] * 8 for _ in range(8)]
    for s in range(8):
        a, b = rep[s]
        for t in T:
            if direction == "V":
                if mul(t, a) != mul(a, t):
                    continue
                na, nb = a, mul(t, b)
            else:
                if mul(t, b) != mul(b, t):
                    continue
                na, nb = mul(t, a), b
            assert mul(na, nb) == mul(nb, na)
            A[s][flat_class(na, nb)] += 1
    return A


def matmul(X, Y):
    n = len(X)
    return [[sum(X[i][k] * Y[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def charpoly(A):
    # Newton identities, exact integer division asserted
    n = len(A)
    p = []
    P = [row[:] for row in A]
    for k in range(1, n + 1):
        p.append(sum(P[i][i] for i in range(n)))
        P = matmul(P, A)
    e = [1]
    for k in range(1, n + 1):
        s = 0
        for i in range(1, k + 1):
            s += (-1) ** (i - 1) * e[k - i] * p[i - 1]
        assert s % k == 0
        e.append(s // k)
    return [(-1) ** k * e[k] for k in range(n + 1)]  # coeffs of x^n, x^(n-1), ...


GV = gamma("V")
GH = gamma("H")
GS = [[GV[i][j] + GH[i][j] for j in range(8)] for i in range(8)]
for name, A in (("GAMMA_V", GV), ("GAMMA_H", GH), ("GAMMA_V+H", GS)):
    print(name, A)
    # detailed balance with the orbit weights: w_s A[s][t] == w_t A[t][s]
    for i in range(8):
        for j in range(8):
            assert weights[i] * A[i][j] == weights[j] * A[j][i]
    print(name, "CHARPOLY", charpoly(A))
assert charpoly(GV) == [1, 0, -10, 0, 9, 0, 0, 0, 0]
assert charpoly(GH) == [1, 0, -10, 0, 9, 0, 0, 0, 0]
assert charpoly(GS) == [1, 0, -20, 0, 84, 0, 0, 0, 0]
# #143 control: C1 on 3x4 = (3/2) Gamma_V; check the block rows quoted there (x2 to stay integer)
assert [[3 * GV[i][j] for j in (0, 1, 2)] for i in (0, 1, 2)] == [[0, 9, 0], [3, 0, 6], [0, 9, 0]]
assert [[3 * GV[i][j] for j in (3, 4)] for i in (3, 4)] == [[0, 3], [3, 0]]

# M=3 internal states: non-commuting pairs, orbits, sign labels, band-process counts
nonc = [(a, b) for a in G for b in G if mul(a, b) != mul(b, a)]
assert len(nonc) == 18
morb = {}
for (a, b) in nonc:
    key = min((conj(c, a), conj(c, b)) for c in G)
    morb.setdefault(key, set()).add((a, b))
assert len(morb) == 3 and all(len(m) == 6 for m in morb.values())
for key, mem in sorted(morb.items()):
    labs = set((sgn(a), sgn(b)) for (a, b) in mem)
    assert len(labs) == 1
    a, b = key
    u = mul(mul(a, b), mul(inv(a), inv(b)))
    assert kind(u) == "C"
    alpha = sum(1 for s in T if kind(mul(mul(a, mul(s, b)), mul(inv(a), inv(mul(s, b))))) != "e")
    beta = sum(1 for s in T if mul(mul(a, s), mul(inv(a), s)) != u)
    ii = sum(1 for t in T if mul(t, a) == mul(a, t))
    print("M3_INTERNAL", "signs", labs.pop(), "kinds", kind(a) + kind(b), "alpha_valid", alpha, "beta_valid", beta, "rowpair_valid", ii)


def isqrt(n):
    if n == 0:
        return 0
    x = 1 << ((n.bit_length() + 1) // 2)
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y


D = 10 ** 12
s14 = isqrt(14 * D * D)
s6 = isqrt(6 * D * D)
s2 = isqrt(2 * D * D)


def show(name, num):
    print(name, str(num // D) + "." + str(num % D).zfill(12))


show("SQRT14-SQRT6", s14 - s6)
show("9/8*(SQRT14-SQRT6)", 9 * (s14 - s6) // 8)
show("5/4*(SQRT14-SQRT6)", 5 * (s14 - s6) // 4)
show("SQRT14", s14)
show("21+17/2*SQRT2+SQRT14", 21 * D + 17 * s2 // 2 + s14)
show("27+17/2*SQRT2", 27 * D + 17 * s2 // 2)
s21 = isqrt(21 * D * D)
s5 = isqrt(5 * D * D)
show("(SQRT21+3)/4", (s21 + 3 * D) // 4)
show("9/8*SQRT14", 9 * s14 // 8)
show("5/4*SQRT14", 5 * s14 // 4)
show("(15-3*SQRT5)/2", (15 * D - 3 * s5) // 2)
print("S3_GAMMA_OK")
