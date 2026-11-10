# T1 pre-freeze check 3 (smallest torus only, 2x2): orbit census and the second-order
# Schur coefficients by explicit two-move path counting, for the flat sector (M=0)
# and the single-3-cycle-flux sector (M=3). No Hamiltonian is built or diagonalized.
# Integers only; amplitudes are reported in units of 1/4 (x4) so they stay integral.
import itertools

G = list(itertools.permutations(range(3)))
IDX = {g: i for i, g in enumerate(G)}


def mul(p, q):
    return tuple(p[q[i]] for i in range(3))


def inv(p):
    r = [0, 0, 0]
    for i in range(3):
        r[p[i]] = i
    return tuple(r)


def nfix(p):
    return sum(1 for i in range(3) if p[i] == i)


E = (0, 1, 2)
T = [g for g in G if nfix(g) == 1]
LX = LY = 2
LINKS = [("h", x, y) for y in range(LY) for x in range(LX)] + [("v", x, y) for y in range(LY) for x in range(LX)]
LI = {l: i for i, l in enumerate(LINKS)}
NL = len(LINKS)


def h(x, y):
    return LI[("h", x % LX, y % LY)]


def v(x, y):
    return LI[("v", x % LX, y % LY)]


def src(l):
    return (l[1], l[2])


def tgt(l):
    return ((l[1] + 1) % LX, l[2]) if l[0] == "h" else (l[1], (l[2] + 1) % LY)


PLAQ = [(x, y) for y in range(LY) for x in range(LX)]


def hol(c, x, y):
    return mul(mul(c[h(x, y)], c[v(x + 1, y)]), mul(inv(c[h(x, y + 1)]), inv(c[v(x, y)])))


def mp(g):
    return 3 - nfix(g)  # 2 - chi_std


def Mval(c):
    return sum(mp(hol(c, x, y)) for (x, y) in PLAQ)


TREE = [h(0, 0), v(0, 0), v(1, 0)]
FREE = [i for i in range(NL) if i not in TREE]


def canon(c):
    k = {(0, 0): E}
    k[(1, 0)] = mul(k[(0, 0)], c[h(0, 0)])
    k[(0, 1)] = mul(k[(0, 0)], c[v(0, 0)])
    k[(1, 1)] = mul(k[(1, 0)], c[v(1, 0)])
    g = [mul(mul(k[src(LINKS[i])], c[i]), inv(k[tgt(LINKS[i])])) for i in range(NL)]
    for i in TREE:
        assert g[i] == E
    best = None
    for cc in G:
        tup = tuple(IDX[mul(mul(cc, g[i]), inv(cc))] for i in FREE)
        if best is None or tup < best:
            best = tup
    return best


def from_canon(tup):
    c = [E] * NL
    for i, gi in zip(FREE, tup):
        c[i] = G[gi]
    return c


def sgn(g):
    return -1 if nfix(g) == 1 else 1


# census in tree gauge
flat, m3 = set(), set()
count_flat = count_m3 = 0
for vals in itertools.product(range(6), repeat=len(FREE)):
    c = from_canon(vals)
    M = Mval(c)
    if M == 0:
        count_flat += 1
        flat.add(canon(c))
    elif M == 3:
        count_m3 += 1
        m3.add(canon(c))
    assert M != 1 and M != 2
print("TREE_GAUGE_FLAT_CONFIGS", count_flat, "FLAT_ORBITS", len(flat))
print("TREE_GAUGE_M3_CONFIGS", count_m3, "M3_ORBITS", len(m3))
assert count_flat == 18 and len(flat) == 8 and count_m3 == 72 and len(m3) == 12


def flat_label(c):
    a = mul(c[h(0, 0)], c[h(1, 0)])
    b = mul(c[v(0, 0)], c[v(0, 1)])
    fa, fb = nfix(a), nfix(b)
    ka = "e" if fa == 3 else ("T" if fa == 1 else "C")
    kb = "e" if fb == 3 else ("T" if fb == 1 else "C")
    if ka == "e":
        return {"e": 0, "T": 1, "C": 2}[kb]
    if ka == "T":
        return 3 if kb == "e" else 4
    if kb == "e":
        return 5
    return 6 if b == a else 7


def m3_label(c):
    pos = [(x, y) for (x, y) in PLAQ if mp(hol(c, x, y)) == 3]
    assert len(pos) == 1
    sa = sgn(mul(c[h(0, 0)], c[h(1, 0)]))
    sb = sgn(mul(c[v(0, 0)], c[v(0, 1)]))
    assert sa == sgn(mul(c[h(0, 1)], c[h(1, 1)])) and sb == sgn(mul(c[v(1, 0)], c[v(1, 1)]))
    st = {(-1, -1): "TT", (-1, 1): "TC", (1, -1): "CT"}[(sa, sb)]
    return (pos[0], st)


def second_order(reps, M0, label):
    out = {}
    for tup in sorted(reps):
        c0 = from_canon(tup)
        assert Mval(c0) == M0
        src_lab = label(c0)
        row = {}
        for l1 in range(NL):
            for t1 in T:
                c1 = c0[:]
                c1[l1] = mul(t1, c1[l1])
                M1 = Mval(c1)
                assert M1 != M0  # no first-order term inside the sector
                assert 4 % (M1 - M0) == 0 and M1 > M0
                w = 4 // (M1 - M0)
                for l2 in range(NL):
                    for t2 in T:
                        c2 = c1[:]
                        c2[l2] = mul(t2, c2[l2])
                        if Mval(c2) == M0:
                            key = label(c2)
                            row[key] = row.get(key, 0) + w
        out[src_lab] = row
    return out


FL = second_order(flat, 0, flat_label)
GV_GH = {  # Gamma_V + Gamma_H counts from s3_gamma.py, class order F1..F8
    0: {1: 3, 3: 3}, 1: {0: 1, 2: 2, 4: 1}, 2: {1: 3}, 3: {0: 1, 5: 2, 4: 1},
    4: {3: 1, 1: 1}, 5: {3: 3}, 6: {}, 7: {},
}
for s in range(8):
    pred = {s: 24}
    for t, n in GV_GH[s].items():
        pred[t] = pred.get(t, 0) + 4 * n
    print("FLAT_ROW_x4", "F" + str(s + 1), sorted(FL[s].items()))
    assert FL[s] == pred
print("FLAT_SECOND_ORDER = 6*I + Gamma_V + Gamma_H  (count form)  OK")

M3 = second_order(m3, 3, m3_label)


def shift(p, d):
    return ((p[0] + d[0]) % LX, (p[1] + d[1]) % LY)


for (p, st), row in sorted(M3.items()):
    pred = {}

    def add(k, n):
        pred[k] = pred.get(k, 0) + n

    add((p, st), 60)
    add((shift(p, (1, 0)), st), 24)
    add((shift(p, (0, 1)), st), 24)
    if st in ("TT", "TC"):  # row holonomy odd: vertical partner-pair processes flip sgn B
        fb = {"TT": "TC", "TC": "TT"}[st]
        add((p, fb), 18)
        add((shift(p, (1, 0)), fb), 16)
    if st in ("TT", "CT"):  # column holonomy odd: horizontal partner-pair processes flip sgn A
        fa = {"TT": "CT", "CT": "TT"}[st]
        add((p, fa), 18)
        add((shift(p, (0, 1)), fa), 16)
    print("M3_ROW_x4", p, st, sorted(row.items()))
    assert row == pred
print("M3_SECOND_ORDER matches the hand derivation  OK")

# zero-momentum reduction (sum over target positions), x4 units
red = {}
for (p, st), row in M3.items():
    if p != (0, 0):
        continue
    for (q, st2), n in row.items():
        red[(st, st2)] = red.get((st, st2), 0) + n
print("M3_ZERO_MOMENTUM_x4", sorted(red.items()))
assert red == {("TT", "TT"): 108, ("TT", "TC"): 34, ("TT", "CT"): 34, ("TC", "TT"): 34,
               ("TC", "TC"): 108, ("CT", "TT"): 34, ("CT", "CT"): 108}
print("TORUS2X2_OK")
