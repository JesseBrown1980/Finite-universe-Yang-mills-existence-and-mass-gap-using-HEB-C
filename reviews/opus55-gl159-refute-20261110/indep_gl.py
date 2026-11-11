#!/usr/bin/env python3
"""Independent refuter for PR #159 (global-lock GL1/GL3).  Written from scratch; imports
nothing from the PR.  Integer only: no float, no fractions module, no '/' operator.

Conventions deliberately different from the PR:
  * electric move = RIGHT multiplication U_l -> U_l t (same operator: the class sum is central);
  * plaquette = v(x,y) h(x,y+1) v(x+1,y)^-1 h(x,y)^-1 (opposite orientation);
  * comb gauge tree: every vertical link below the top row + the bottom horizontal row;
  * link id = 2*(x*LY+y)+d, d=0 horizontal, d=1 vertical;
  * inertia: own fraction-free elimination with max-|diag| symmetric pivoting;
  * threshold grid: lambda = a / 2^44, floor grid 2^32.

usage: indep_gl.py LXxLY r [mode=full|census|floor] [ext3=1] [check=<file of PR LEVEL rows>]
Rows to stdout, TAG|k=v|...|json=0.
"""
import hashlib
import sys
import time
from itertools import permutations

# ---------------- S3 ----------------
GR = sorted(permutations((0, 1, 2)))
GI = {g: i for i, g in enumerate(GR)}
MUL = [[GI[tuple(GR[a][GR[b][i]] for i in range(3))] for b in range(6)] for a in range(6)]
ID = GI[(0, 1, 2)]
INV = [next(b for b in range(6) if MUL[a][b] == ID) for a in range(6)]
TRS = [g for g in range(6) if g != ID and MUL[g][g] == ID]
FIXP = [sum(1 for i in range(3) if GR[g][i] == i) for g in range(6)]
COST = [2 - (FIXP[g] - 1) for g in range(6)]          # 2 - chi_std
CONJ = [[MUL[MUL[c][a]][INV[c]] for a in range(6)] for c in range(6)]
assert len(TRS) == 3 and sorted(COST) == [0, 2, 2, 2, 3, 3]


def out(tag, **kv):
    print(tag + "|" + "|".join(k + "=" + str(v) for k, v in kv.items()) + "|json=0", flush=True)


def die(why):
    out("FAILED", check=why)
    raise SystemExit(2)


def need(c, why):
    if not c:
        die(why)


class Torus:
    def __init__(self, LX, LY):
        self.LX, self.LY = LX, LY
        self.V = LX * LY
        self.NL = 2 * self.V
        self.NMOVE = 3 * self.NL
        L = lambda x, y, d: 2 * ((x % LX) * LY + (y % LY)) + d
        self.L = L
        self.ends = [None] * self.NL
        for x in range(LX):
            for y in range(LY):
                self.ends[L(x, y, 0)] = ((x, y), ((x + 1) % LX, y))
                self.ends[L(x, y, 1)] = ((x, y), (x, (y + 1) % LY))
        # plaquettes: list of (link, inverse?) in path order
        self.plaqs = []
        for y in range(LY):
            for x in range(LX):
                self.plaqs.append(((L(x, y, 1), 0), (L(x, y + 1, 0), 0), (L(x + 1, y, 1), 1), (L(x, y, 0), 1)))
        self.F = len(self.plaqs)
        tree = [L(x, 0, 0) for x in range(LX - 1)] + [L(x, y, 1) for x in range(LX) for y in range(LY - 1)]
        need(len(tree) == self.V - 1, "tree_size")
        ts = set(tree)
        self.kept = [l for l in range(self.NL) if l not in ts]
        need(len(self.kept) == self.V + 1, "kept_size")
        self.kpos = {l: i for i, l in enumerate(self.kept)}
        self.istree = [l in ts for l in range(self.NL)]
        # gauge-fix order: (site, via link, parent site)
        order = []
        for x in range(LX - 1):
            order.append(((x + 1, 0), L(x, 0, 0), (x, 0)))
        for x in range(LX):
            for y in range(LY - 1):
                order.append(((x, y + 1), L(x, y, 1), (x, y)))
        self.gorder = [(s[0] * LY + s[1], l, p[0] * LY + p[1]) for s, l, p in order]
        self.kends = [(self.ends[l][0][0] * LY + self.ends[l][0][1], self.ends[l][1][0] * LY + self.ends[l][1][1])
                      for l in self.kept]

    def full(self, key):
        U = [ID] * self.NL
        for l, a in zip(self.kept, key):
            U[l] = a
        return U

    def canon(self, U):
        g = [ID] * self.V
        for s, l, p in self.gorder:
            g[s] = MUL[g[p]][U[l]]
        k = [MUL[MUL[g[s]][U[l]]][INV[g[e]]] for l, (s, e) in zip(self.kept, self.kends)]
        return min(tuple(cj[a] for a in k) for cj in CONJ)

    @staticmethod
    def orbit_size(key):
        return len({tuple(cj[a] for a in key) for cj in CONJ})

    def mag(self, U):
        m = 0
        for pl in self.plaqs:
            h = ID
            for l, iv in pl:
                h = MUL[h][INV[U[l]] if iv else U[l]]
            m += COST[h]
        return m

    def moves(self, key):
        """multiset of canonical targets of the 3*NL right-multiplication moves"""
        U = self.full(key)
        res = {}
        for l in range(self.NL):
            o = U[l]
            for t in TRS:
                U[l] = MUL[o][t]
                if self.istree[l]:
                    c = self.canon(U)
                else:
                    kk = list(key)
                    kk[self.kpos[l]] = U[l]
                    c = min(tuple(cj[a] for a in kk) for cj in CONJ)
                res[c] = res.get(c, 0) + 1
            U[l] = o
        need(sum(res.values()) == self.NMOVE, "move_total")
        return res

    def low_configs(self, mmax):
        order = []
        for pl in self.plaqs:
            for l, _ in pl:
                if l in self.kpos and l not in order:
                    order.append(l)
        need(sorted(order) == sorted(self.kept), "order_cover")
        when = {l: i for i, l in enumerate(order)}
        closes = [[] for _ in order]
        for pl in self.plaqs:
            ks = [when[l] for l, _ in pl if l in self.kpos]
            closes[max(ks)].append(pl)
        U = [ID] * self.NL
        found = []

        def go(i, m):
            if i == len(order):
                found.append((tuple(U[l] for l in self.kept), m))
                return
            l = order[i]
            for a in range(6):
                U[l] = a
                mm = m
                for pl in closes[i]:
                    h = ID
                    for ll, iv in pl:
                        h = MUL[h][INV[U[ll]] if iv else U[ll]]
                    mm += COST[h]
                if mm <= mmax:
                    go(i + 1, mm)
            U[l] = ID
        go(0, 0)
        return found


# ---------------- exact inertia (own code) ----------------
def neg_count(A):
    """negative eigenvalue count of a symmetric integer matrix; None if undecidable by
    diagonal pivoting (zero diagonal everywhere in the remaining block)."""
    n = len(A)
    for i in range(n):
        for j in range(i + 1, n):
            if A[i][j] != A[j][i]:
                die("inertia_symmetry")
    B = [r[:] for r in A]
    prev = 1
    neg = 0
    sign_prev = 1
    for k in range(n):
        # max |diag| pivot among remaining
        best = max(range(k, n), key=lambda i: abs(B[i][i]))
        if B[best][best] == 0:
            return None
        if best != k:
            B[k], B[best] = B[best], B[k]
            for row in B:
                row[k], row[best] = row[best], row[k]
        p = B[k][k]
        s = 1 if p > 0 else -1
        if s != sign_prev:
            neg += 1
        sign_prev = s
        Bk = B[k]
        for i in range(k + 1, n):
            Bi = B[i]
            f = Bi[k]
            for j in range(k + 1, n):
                q, rr = divmod(Bi[j] * p - f * Bk[j], prev)
                if rr:
                    die("bareiss_division")
                Bi[j] = q
        prev = p
    return neg


def sha(b):
    return hashlib.sha256(b).hexdigest()


# ---------------- model on interned states ----------------
class Model:
    def __init__(self, tor):
        self.t = tor
        self.id = {}
        self.keys = []
        self.w = []
        self.m = []
        self.nb = {}

    def intern(self, key):
        i = self.id.get(key)
        if i is None:
            i = len(self.keys)
            self.id[key] = i
            self.keys.append(key)
            self.w.append(Torus.orbit_size(key))
            self.m.append(self.t.mag(self.t.full(key)))
        return i

    def nbr(self, i):
        v = self.nb.get(i)
        if v is None:
            mv = self.t.moves(self.keys[i])
            v = [(self.intern(k), c) for k, c in mv.items()]
            self.nb[i] = v
        return v


def census(md):
    t = md.t
    raw = t.low_configs(4)
    by = {0: set(), 3: set(), 4: set()}
    rc = {0: 0, 3: 0, 4: 0}
    for cfg, m in raw:
        need(m in by, "parity_M_in_0_3_4")
        rc[m] += 1
        key = min(tuple(cj[a] for a in cfg) for cj in CONJ)
        by[m].add(md.intern(key))
    F = t.F
    pairs = F * (F - 1) // 2
    # group theory (derived in REFUTE-GL159.md, Frobenius counts N(e)=18, N(3-cycle)=9):
    want_raw = {0: 18, 3: 18 * F, 4: 108 * pairs}
    want_orb = {0: 8, 3: 3 * F, 4: 20 * pairs}
    for m in (0, 3, 4):
        need(rc[m] == want_raw[m], "raw_count_M" + str(m))
        need(len(by[m]) == want_orb[m], "orbit_count_M" + str(m))
        need(sum(md.w[i] for i in by[m]) == want_raw[m], "orbit_weight_sum_M" + str(m))
        for i in by[m]:
            need(md.m[i] == m, "mag_recheck")
    n = t.V + 1
    dim = 6 ** n + 3 * 2 ** n + 2 * 3 ** n
    need(dim % 6 == 0, "burnside")
    out("I_CENSUS", lattice=str(t.LX) + "x" + str(t.LY), F=F, dim=dim // 6, flat=len(by[0]), flat_raw=rc[0],
        m3=len(by[3]), m3_raw=rc[3], m4=len(by[4]), m4_raw=rc[4],
        m4_weight_hist=",".join(str(sum(1 for i in by[4] if md.w[i] == k)) + "@w" + str(k) for k in (1, 2, 3, 6)))
    return sorted(by[0], key=lambda i: md.keys[i]), sorted(by[3], key=lambda i: md.keys[i]), sorted(by[4])


def floor_data(md, m4):
    s4 = set(m4)
    rho = 0
    p2 = 0
    cache = {}
    for h in m4:
        r44 = 0
        q = 0
        for x, c in md.nbr(h):
            mx = md.m[x]
            if x in s4:
                r44 += c
            elif mx >= 6:
                v = cache.get(x)
                if v is None:
                    v = sum(cc for y, cc in md.t.moves(md.keys[x]).items() if md.id.get(y) in s4)
                    cache[x] = v
                q += c * v
            else:
                need(mx in (0, 3), "M4_neighbour_parity")
        rho = max(rho, r44)
        p2 = max(p2, q)
    out("I_FLOOR_INPUTS", rho44=rho, P2max=p2, m6plus_nbrs=len(cache))
    return rho, p2


FG = 1 << 32


def floor_num(N3, r, rho, p2):
    A = N3 + 4 * r - rho
    B = 6 * r
    need(A > 0 and A * B >= p2, "floor_at_zero")
    lo, hi = 0, FG * min(A, B)
    while hi - lo > 1:
        mid = (lo + hi) >> 1
        if (A * FG - mid) > 0 and (B * FG - mid) > 0 and (A * FG - mid) * (B * FG - mid) >= p2 * FG * FG:
            lo = mid
        else:
            hi = mid
    return lo


def floor_ok(N3, r, rho, p2, n, d):
    """is lambda'=n/d a valid floor by the Schur-test lemma?"""
    A, B = (N3 + 4 * r - rho) * d - n, 6 * r * d - n
    return A > 0 and B > 0 and A * B >= p2 * d * d


# ---------------- certificate ----------------
DS = 10 ** 9    # trial scale


def ball(md, seeds, Pset, extra_m_le=None):
    seen = set(seeds) | Pset
    l1 = set()
    for s in seeds:
        for x, _ in md.nbr(s):
            if x not in seen:
                l1.add(x)
    seen |= l1
    layers = [sorted(l1)]
    return seen, layers


def solve_trial(md, r, B, cols, Pcol, lam):
    """integer Gauss-Seidel for (K_BB - lam W_BB) Y = -D K_BP on ball B (list), columns cols.
    lam = (a, b).  Only the residual is trusted later."""
    a, b = lam
    N3 = md.t.NMOVE
    pos = {x: i for i, x in enumerate(B)}
    nc = len(cols)
    cp = {p: j for j, p in enumerate(cols)}
    dg, offs, rhs = [], [], []
    for x in B:
        w = md.w[x]
        cs = 0
        o = []
        f = [0] * nc
        for y, c in md.nbr(x):       # K_xy = -w_x c(x->y)
            if y == x:
                cs += c
            elif y in pos:
                o.append((pos[y], w * c * b))
            else:
                j = Pcol.get(y)
                if j is not None and j in cp:
                    f[cp[j]] += DS * w * c * b      # -D K_xP = +D w c
        d = b * w * (N3 - cs + r * md.m[x]) - a * w
        need(d > 0, "trial_diag_positive")
        dg.append(d)
        offs.append(o)
        rhs.append(f)
    Y = [[0] * nc for _ in B]
    for sweep in range(600):
        ch = 0
        for i in range(len(B)):
            s = rhs[i][:]
            for j, c in offs[i]:
                yj = Y[j]
                for t in range(nc):
                    s[t] += c * yj[t]
            d = dg[i]
            yi = Y[i]
            for t in range(nc):
                v = (2 * s[t] + d) // (2 * d)
                if v != yi[t]:
                    yi[t] = v
                    ch += 1
        if ch == 0:
            break
    return Y, sweep + 1


def build_forms(md, r, P, groups, lam):
    """groups: [(ballstates, colindices)].  Returns A0,A1 (U = A0 - lam A1), G0x6, G1x6, G2x6."""
    n = len(P)
    N3 = md.t.NMOVE
    Pcol = {p: j for j, p in enumerate(P)}
    Y = {}
    info = []
    for B, cols in groups:
        Yb, sw = solve_trial(md, r, B, cols, Pcol, lam)
        info.append(str(len(B)) + "x" + str(len(cols)) + "@" + str(sw))
        for x, y in zip(B, Yb):
            v = Y.setdefault(x, [0] * n)
            for t, j in enumerate(cols):
                v[j] = y[t]
    # R0_x = D K_xP + sum_j K_xj Y_j, over every C state x  (K symmetric: K_xj = -w_j c(j->x))
    R0 = {}
    for j, y in Y.items():
        wj = md.w[j]
        nz = [(t, v) for t, v in enumerate(y) if v]
        for x, c in md.nbr(j):
            if x in Pcol:
                continue
            row = R0.setdefault(x, {})
            for t, v in nz:
                row[t] = row.get(t, 0) - wj * c * v
    for p, key in enumerate(P):
        wp = md.w[key]
        for x, c in md.nbr(key):
            need(x not in Pcol, "P_P_direct_move")
            row = R0.setdefault(x, {})
            row[p] = row.get(p, 0) - DS * wp * c
    for x, y in Y.items():                         # diagonal K_xx Y_x
        cs = sum(c for z, c in md.nbr(x) if z == x)
        dk = md.w[x] * (N3 + r * md.m[x])           # self-moves already added above via -w c
        row = R0.setdefault(x, {})
        for t, v in enumerate(y):
            if v:
                row[t] = row.get(t, 0) + dk * v
    for x in R0:
        need(md.m[x] >= 4, "residual_row_in_C")
    A0 = [[0] * n for _ in range(n)]
    A1 = [[0] * n for _ in range(n)]
    for p, key in enumerate(P):
        A0[p][p] = DS * DS * md.w[key] * (N3 + r * md.m[key])  # no P self moves (checked)
        A1[p][p] = DS * DS * md.w[key]
    # cross term D (K_PC Y + Y^T K_CP):  K_px = -w_p c(p->x)
    for p, key in enumerate(P):
        wp = md.w[key]
        for x, c in md.nbr(key):
            y = Y.get(x)
            if y is None:
                continue
            for q in range(n):
                if y[q]:
                    v = -DS * wp * c * y[q]
                    A0[p][q] += v
                    A0[q][p] += v
    # Y^T K_CC Y = Y^T (R0 - D K_CP) restricted to Y rows ; Y^T W Y
    G0 = [[0] * n for _ in range(n)]
    G1 = [[0] * n for _ in range(n)]
    for x, y in Y.items():
        row = R0[x]
        w = md.w[x]
        nzy = [(t, v) for t, v in enumerate(y) if v]
        # D K_xP part
        kp = {}
        for z, c in md.nbr(x):
            j = Pcol.get(z)
            if j is not None:
                kp[j] = kp.get(j, 0) - DS * w * c
        for i, yi in nzy:
            for j in range(n):
                kv = row.get(j, 0) - kp.get(j, 0)
                if kv:
                    A0[i][j] += yi * kv
            for j, yj in nzy:
                A1[i][j] += w * yi * yj
            for j, rv in row.items():
                G1[i][j] -= 6 * yi * rv
                G1[j][i] -= 6 * yi * rv
    for x, row in R0.items():
        f = 6 // md.w[x]
        need(f * md.w[x] == 6, "weight_divides_6")
        it = [(t, v) for t, v in row.items() if v]
        for i, vi in it:
            Gi = G0[i]
            for j, vj in it:
                Gi[j] += f * vi * vj
    G2 = [[6 * A1[i][j] for j in range(n)] for i in range(n)]
    for p, key in enumerate(P):
        G2[p][p] -= 6 * DS * DS * md.w[key]
    for M_, nm in ((A0, "A0"), (A1, "A1"), (G0, "G0"), (G1, "G1"), (G2, "G2")):
        for i in range(n):
            for j in range(i):
                need(M_[i][j] == M_[j][i], "sym_" + nm)
    return dict(A0=A0, A1=A1, G0=G0, G1=G1, G2=G2, ball=len(Y), resid_rows=len(R0),
                ext=sum(1 for x in R0 if x not in Y), info=";".join(info))


def negU(F, a, b):
    n = len(F["A0"])
    return neg_count([[b * F["A0"][i][j] - a * F["A1"][i][j] for j in range(n)] for i in range(n)])


def negL(F, a, b, fn, fd):
    gap = fn * b - a * fd
    if gap <= 0:
        return None
    n = len(F["A0"])
    A0, A1, G0, G1, G2 = F["A0"], F["A1"], F["G0"], F["G1"], F["G2"]
    return neg_count([[6 * gap * (b * A0[i][j] - a * A1[i][j]) - fd * (b * b * G0[i][j] + a * b * G1[i][j] + a * a * G2[i][j])
                       for j in range(n)] for i in range(n)])


GB = 1 << 44


def up_bisect(F, j, lo, hi, steps):
    need(negU(F, hi, GB) >= j, "U_hi_bracket")
    for _ in range(steps):
        mid = (lo + hi) >> 1
        v = negU(F, mid, GB)
        if v is not None and v >= j:
            hi = mid
        else:
            lo = mid
    return hi


def lo_bisect(F, j, lo, hi, steps, fn, fd):
    v = negL(F, lo, GB, fn, fd)
    if v is None or v > j - 1:
        return None
    for _ in range(steps):
        mid = (lo + hi) >> 1
        v = negL(F, mid, GB, fn, fd)
        if v is not None and v <= j - 1:
            lo = mid
        else:
            hi = mid
    return lo


def dec(n, d, k, up):
    s = 10 ** k
    q = -((-n * s) // d) if up else (n * s) // d
    sg = "-" if q < 0 else ""
    q = abs(q)
    return sg + str(q // s) + "." + str(q % s).rjust(k, "0")


def main():
    t0 = time.monotonic_ns()
    a = sys.argv[1:]
    LX, LY = (int(v) for v in a[0].split("x"))
    r = int(a[1])
    opt = dict(mode="full", ext3="1", check="")
    for s in a[2:]:
        k, v = s.split("=", 1)
        opt[k] = v
    tor = Torus(LX, LY)
    md = Model(tor)
    out("I_BEGIN", lattice=a[0], r=r, mode=opt["mode"], ext3=opt["ext3"], float_used=0,
        script_sha256=sha(open(__file__, "rb").read()))
    flats, m3, m4 = census(md)
    if opt["mode"] == "census":
        return
    P = flats + m3
    Pset = set(P)
    for p in P:
        for x, _ in md.nbr(p):
            need(x not in Pset, "P_P_direct_move")
    # symmetry of the weighted move counts on P and M4 rows: w_x c(x->y) == w_y c(y->x)
    for x in P + m4[:200]:
        for y, c in md.nbr(x):
            back = dict(md.nbr(y)).get(x, 0)
            need(md.w[x] * c == md.w[y] * back, "detailed_balance")
    rho, p2 = floor_data(md, m4)
    N3 = tor.NMOVE
    fn = floor_num(N3, r, rho, p2)
    out("I_FLOOR", lattice=a[0], r=r, floor_num=fn, floor_den=FG, floor_dec=dec(fn, FG, 6, False),
        floor_ok_self=floor_ok(N3, r, rho, p2, fn, FG), floor_plus_one_ok=floor_ok(N3, r, rho, p2, fn + 1, FG))
    if opt["mode"] == "floor":
        return
    # balls: flats radius 2; M3 radius 1 plus (ext3) every neighbour with M<=7 of the radius-1 layer
    s1, L1 = ball(md, flats, Pset)
    L2 = set()
    for x in L1[0]:
        for y, _ in md.nbr(x):
            if y not in s1:
                L2.add(y)
    Bf = L1[0] + sorted(L2)
    s3, M1 = ball(md, m3, Pset)
    B3 = list(M1[0])
    if opt["ext3"] == "1":
        e = set()
        for x in M1[0]:
            for y, _ in md.nbr(x):
                if y not in s3 and md.m[y] <= 7:
                    e.add(y)
        B3 += sorted(e)
    out("I_BALLS", flat_ball=len(Bf), m3_ball=len(B3))
    cf = list(range(len(flats)))
    c3 = list(range(len(flats), len(P)))
    # pass 1: rough U-only estimates
    Fa = build_forms(md, r, P, [(Bf, cf)], (N3, 1))
    e8u = up_bisect(Fa, 8, 0, (N3 + 1) * GB, 40)
    e1u = up_bisect(Fa, 1, 0, (N3 + 1) * GB, 40)
    Fb3 = build_forms(md, r, P, [(B3, c3)], (N3 + 3 * r, 1))
    e9u = up_bisect(Fb3, 9, (N3 + 1) * GB, (N3 + 3 * r + 1) * GB, 40)
    res = {}
    lamB = ((e1u + e8u) >> 1, GB)
    FB = build_forms(md, r, P, [(Bf, cf), (B3, c3)], lamB)
    out("I_FORMS", stage="B", ball=FB["ball"], exterior=FB["ext"], resid_rows=FB["resid_rows"], gs=FB["info"])
    for lvl, j in (("E1", 1), ("E8", 8)):
        hi = up_bisect(FB, j, 0, (N3 + 1) * GB, 70)
        lo = lo_bisect(FB, j, 0, hi, 70, fn, FG)
        res[lvl] = (lo, hi, FB)
    FC = build_forms(md, r, P, [(Bf, cf), (B3, c3)], (e9u, GB))
    out("I_FORMS", stage="C", ball=FC["ball"], exterior=FC["ext"], resid_rows=FC["resid_rows"], gs=FC["info"])
    hi9 = up_bisect(FC, 9, (N3 + 1) * GB, (N3 + 3 * r + 1) * GB, 70)
    top = min(hi9, (fn * GB) // FG - 1)
    lo9 = lo_bisect(FC, 9, (N3 + 1) * GB, top, 70, fn, FG)
    res["E9"] = (lo9, hi9, FC)
    # also E10 upper, to see whether E9 is degenerate (index sensitivity)
    hi10 = up_bisect(FC, 10, (N3 + 1) * GB, (N3 + 3 * r + 1) * GB, 70)
    lo10 = lo_bisect(FC, 10, (N3 + 1) * GB, min(hi10, (fn * GB) // FG - 1), 70, fn, FG)
    res["E10"] = (lo10, hi10, FC)
    hi7 = up_bisect(FB, 7, 0, (N3 + 1) * GB, 70)
    lo7 = lo_bisect(FB, 7, 0, hi7, 70, fn, FG)
    res["E7"] = (lo7, hi7, FB)
    for lvl in ("E1", "E7", "E8", "E9", "E10"):
        lo, hi, _ = res[lvl]
        out("I_LEVEL", lattice=a[0], r=r, level=lvl, lo_num=lo, hi_num=hi, den=GB,
            lo_dec="NONE" if lo is None else dec(lo, GB, 12, False), hi_dec=dec(hi, GB, 12, True))
    # c_hat and W in my grid
    e8lo, e8hi, _ = res["E8"]
    e9lo, e9hi, _ = res["E9"]
    e1lo, e1hi, _ = res["E1"]
    if e8lo is not None and e9lo is not None:
        clo = r * (3 * r * GB - (e9hi - e8lo))
        chi = r * (3 * r * GB - (e9lo - e8hi))
        out("I_CHAT", lattice=a[0], r=r, c_hat_lo=dec(clo, GB, 9, False), c_hat_hi=dec(chi, GB, 9, True),
            frozen_hi=dec(21 * r + 64, r, 9, True),
            inside_frozen=(clo >= 21 * GB and chi * r <= (21 * r + 64) * GB))
    if e1lo is not None and e8lo is not None:
        out("I_W", lattice=a[0], r=r, W_lo=dec(e8lo - e1hi, GB, 12, False), W_hi=dec(e8hi - e1lo, GB, 12, True),
            W_lo_num=e8lo - e1hi, W_hi_num=e8hi - e1lo, den=GB)
    # test the PR's own endpoints in MY certificate
    if opt["check"]:
        for s in open(opt["check"]).read().splitlines():
            if not s.startswith("LEVEL|"):
                continue
            f = dict(it.split("=", 1) for it in s.split("|")[1:] if "=" in it)
            if f["lattice"] != a[0] or int(f["r"]) != r:
                continue
            lvl = f["level"]
            j = int(lvl[1:])
            D12 = int(f["den"])
            F_ = res[lvl][2]
            hi = int(f["hi_num"])
            vu = negU(F_, hi, D12)
            if f["lo_num"] != "NONE":
                lo = int(f["lo_num"])
                vl = negL(F_, lo, D12, fn, FG)
            else:
                vl = "NONE"
            out("I_PR_ENDPOINT", lattice=a[0], r=r, level=lvl, pr_lo=f["lo_dec"], pr_hi=f["hi_dec"],
                negU_at_pr_hi=vu, upper_holds_in_mine=(vu is not None and vu >= j),
                negL_at_pr_lo=vl, lower_holds_in_mine=(vl not in (None, "NONE") and vl <= j - 1))
    out("I_END", lattice=a[0], r=r, ms=(time.monotonic_ns() - t0) // 1000000)


if __name__ == "__main__":
    main()
