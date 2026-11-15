# The region dictionary of docs/YM_TOPOLOGICAL_STABILITY_PROOF.md, section 3, for tori of any sides: odd sides and rectangles included.
# It stands beside docs/check_bhm_dictionary.py (even squares, 2 x 2 sites), which is unchanged. Set inclusions only: no group, no quantum state.
#
# Sites. Each direction is cut into consecutive intervals of cells of width 2 or 3 (an odd side needs at least one 3). A site is a product of
# one interval in x and one in y, so a site holds 2 x 2, 2 x 3, 3 x 2 or 3 x 3 cells. The site lattice is Z_Kx x Z_Ky. S(r) is an r x r square
# of sites, and H0 = sum over C in S(2) of G_C.
#
# The assignment, one rule per direction. With X(c) the site interval of cell c:
#   plaquette at cell a : block starting at X(a) when a is the last cell of its interval, at X(a) - 1 otherwise;
#   star at vertex x    : block starting at X(x) - 1.
# On width-2 intervals this is the rule of the first script.
#
# Required, for every A in S(r) with r <= min(Kx, Ky) - 2 whose B' does not wrap:
#   (i)   each term's support lies in the block it is assigned to, and every block of S(2) is used;
#   (ii)  A's links lie in the rectangular sublattice A';
#   (iii) V(A') is the interior vertex set of B' (one original layer more on each side), and B' spans less than the torus in both directions;
#   (iv)  every plaquette and every interior star of B' is assigned to a block inside B, the square of A and its nearest neighbours.
# Exits 1 if any fails. With the argument sabotage=first_cell the plaquette rule is changed and the script must exit 1.
# Integer only, json=0.
import sys

SABOTAGE = "sabotage=first_cell" in sys.argv


def cuts(widths):
    """Start cell of each interval, the interval of each cell, and whether each cell is the last of its interval."""
    start, of, last = [], [], []
    c = 0
    for i, w in enumerate(widths):
        start.append(c)
        for j in range(w):
            of.append(i)
            last.append(j == w - 1)
        c += w
    return start, of, last


class Torus:
    def __init__(self, wx, wy):
        self.wx, self.wy = wx, wy
        self.Lx, self.Ly = sum(wx), sum(wy)
        self.Kx, self.Ky = len(wx), len(wy)
        self.sx, self.ox, self.lastx = cuts(wx)
        self.sy, self.oy, self.lasty = cuts(wy)

    def h(self, x, y):
        return ("h", x % self.Lx, y % self.Ly)

    def v(self, x, y):
        return ("v", x % self.Lx, y % self.Ly)

    def plaquette(self, a, b):
        return {self.h(a, b), self.h(a, b + 1), self.v(a, b), self.v(a + 1, b)}

    def star(self, x, y):
        return {self.h(x, y), self.v(x, y), self.h(x - 1, y), self.v(x, y - 1)}

    def block_cells(self, X, Y):
        """Cells of the 2 x 2 block of sites starting at site (X, Y)."""
        xs = [(self.sx[(X + i) % self.Kx] + j) % self.Lx for i in range(2) for j in range(self.wx[(X + i) % self.Kx])]
        ys = [(self.sy[(Y + i) % self.Ky] + j) % self.Ly for i in range(2) for j in range(self.wy[(Y + i) % self.Ky])]
        return {(x, y) for x in xs for y in ys}

    def assign_plaquette(self, a, b):
        a, b = a % self.Lx, b % self.Ly
        if SABOTAGE:
            X = self.ox[a]
        else:
            X = self.ox[a] if self.lastx[a] else self.ox[a] - 1
        Y = self.oy[b] if self.lasty[b] else self.oy[b] - 1
        return (X % self.Kx, Y % self.Ky)

    def assign_star(self, x, y):
        x, y = x % self.Lx, y % self.Ly
        return ((self.ox[x] - 1) % self.Kx, (self.oy[y] - 1) % self.Ky)

    def check_terms(self):
        used = set()
        for a in range(self.Lx):
            for b in range(self.Ly):
                for name, term, c in (("plaquette", self.plaquette(a, b), self.assign_plaquette(a, b)), ("star", self.star(a, b), self.assign_star(a, b))):
                    if not {(l[1], l[2]) for l in term} <= self.block_cells(c[0], c[1]):
                        return "term_%s_%d_%d_outside_block_%d_%d" % (name, a, b, c[0], c[1])
                    used.add(c)
        if len(used) != self.Kx * self.Ky:
            return "blocks_used_%d_of_%d" % (len(used), self.Kx * self.Ky)
        return None

    def check_region(self, X0, Y0, r):
        x0, y0 = self.sx[X0], self.sy[Y0]
        spanx = sum(self.wx[(X0 + i) % self.Kx] for i in range(r))
        spany = sum(self.wy[(Y0 + i) % self.Ky] for i in range(r))
        A_links = set()
        for i in range(spanx):
            for j in range(spany):
                A_links |= {self.h(x0 + i, y0 + j), self.v(x0 + i, y0 + j)}
        A_prime = set()
        for i in range(spanx + 1):
            for j in range(spany + 1):
                if i < spanx:
                    A_prime.add(self.h(x0 + i, y0 + j))
                if j < spany:
                    A_prime.add(self.v(x0 + i, y0 + j))
        if not A_links <= A_prime:
            return "A_links_outside_Aprime"
        if spanx + 2 >= self.Lx or spany + 2 >= self.Ly:
            return "Bprime_wraps"
        B_blocks = {((X0 - 1 + i) % self.Kx, (Y0 - 1 + j) % self.Ky) for i in range(r + 1) for j in range(r + 1)}
        for i in range(spanx + 2):
            for j in range(spany + 2):
                if self.assign_plaquette(x0 - 1 + i, y0 - 1 + j) not in B_blocks:
                    return "plaquette_%d_%d_of_Bprime_assigned_outside_B" % (x0 - 1 + i, y0 - 1 + j)
        for i in range(1, spanx + 2):
            for j in range(1, spany + 2):
                if self.assign_star(x0 - 1 + i, y0 - 1 + j) not in B_blocks:
                    return "star_%d_%d_of_Bprime_assigned_outside_B" % (x0 - 1 + i, y0 - 1 + j)
        return None


def widths_for(L, three_at):
    """Width-2 intervals, with one width-3 interval at index three_at when L is odd."""
    if L % 2 == 0:
        return [2] * (L // 2)
    w = [2] * ((L - 3) // 2 + 1)
    w[three_at % len(w)] = 3
    return w


def run(family, tori):
    regions = fails = wraps = 0
    for wx, wy in tori:
        t = Torus(wx, wy)
        bad = t.check_terms()
        if bad:
            fails += 1
            if fails < 8:
                print("BHM_GENERAL_FAIL|family=%s|Lx=%d|Ly=%d|%s|json=0" % (family, t.Lx, t.Ly, bad))
        for r in range(1, min(t.Kx, t.Ky) - 1):
            for X0 in range(t.Kx):
                for Y0 in range(t.Ky):
                    bad = t.check_region(X0, Y0, r)
                    if bad == "Bprime_wraps":
                        wraps += 1
                        continue
                    regions += 1
                    if bad:
                        fails += 1
                        if fails < 8:
                            print("BHM_GENERAL_FAIL|family=%s|Lx=%d|Ly=%d|r=%d|X0=%d|Y0=%d|%s|json=0" % (family, t.Lx, t.Ly, r, X0, Y0, bad))
    print("BHM_GENERAL|family=%s|tori=%d|regions=%d|regions_skipped_because_Bprime_would_wrap=%d|failed=%d|json=0" % (family, len(tori), regions, wraps, fails))
    return regions, fails


total = bad_total = 0
# 1. regression: even squares with width-2 intervals, the family of the first script (it counts 38,352 regions).
r1, f1 = run("even_squares_8_to_40", [(widths_for(L, 0), widths_for(L, 0)) for L in range(8, 42, 2)])
# 2. odd squares, the width-3 interval at every position in x and at two positions in y.
odd = []
for L in range(9, 31, 2):
    n = (L - 3) // 2 + 1
    for px in range(n):
        for py in (0, n // 2):
            odd.append((widths_for(L, px), widths_for(L, py)))
r2, f2 = run("odd_squares_9_to_29_three_at_every_x_position", odd)
# 3. rectangles of every parity.
rect = [(widths_for(Lx, 1), widths_for(Ly, 2)) for Lx in range(8, 23) for Ly in range(8, 23) if Lx != Ly]
r3, f3 = run("rectangles_8_to_22", rect)
# 4. width-3 intervals only, and mixtures with several 3s.
mixed = [([3] * k, [3] * k) for k in range(4, 9)] + [([2, 3] * k, [3, 2, 2] * k) for k in range(2, 6)] + [([3, 3, 2] * k, [2, 3] * k) for k in range(2, 5)]
r4, f4 = run("width_3_and_mixtures", mixed)
total, bad_total = r1 + r2 + r3 + r4, f1 + f2 + f3 + f4
print("BHM_GENERAL_DONE|sabotage=%s|regions=%d|failed=%d|even_square_regions=%d|largest_site=3x3_cells_18_links|json=0" % ("first_cell" if SABOTAGE else "none", total, bad_total, r1))
sys.exit(1 if bad_total else 0)
