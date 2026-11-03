# Checks the region dictionary of docs/YM_TOPOLOGICAL_STABILITY_PROOF.md, section 3: the combinatorics that lets Cui et al., Theorem 3.1, give
# Bravyi-Hastings-Michalakis's TQO-1 and TQO-2 for the periodic L x L S3 model. It decides set inclusions on the lattice, with no group and no quantum state.
#
# Links are h(x, y) from (x, y) to (x+1, y) and v(x, y) from (x, y) to (x, y+1), owned by cell (x, y). BHM's sites are blocks of k x k cells. S(r) is an
# r x r square of sites, and H0 = sum over C in S(2) of G_C, each star and plaquette assigned to one C holding its whole support.
#
# For k = 1 it prints the first place the inclusion fails. For k = 2 it requires every inclusion, for every even L in range, every A in S(r), r <= L/2 - 2:
#   (i)   each term's support lies in the block it is assigned to, and each block in S(2) is used;
#   (ii)  A's links lie in the rectangular sublattice A';
#   (iii) V(A') lies in the interior vertices of the rectangular sublattice B', and B' spans less than L, so it sits in a contractible region;
#   (iv)  every interior star and every plaquette of B' is assigned to a block inside B, the square of A and its nearest neighbours, so ran P_B lies in Cui's H_B'.
# Exits 1 if any fails. Integer only, json=0.
import sys


def h(x, y, L):
    return ("h", x % L, y % L)


def v(x, y, L):
    return ("v", x % L, y % L)


def plaquette(a, b, L):
    return {h(a, b, L), h(a, b + 1, L), v(a, b, L), v(a + 1, b, L)}


def star(x, y, L):
    return {h(x, y, L), v(x, y, L), h(x - 1, y, L), v(x, y - 1, L)}


def site(link, k):
    return (link[1] // k, link[2] // k)


def block_cells(X, Y, side, k, L):
    return {((X * k + i) % L, (Y * k + j) % L) for i in range(side * k) for j in range(side * k)}


def owners(links):
    return {(l[1], l[2]) for l in links}


def assign_plaquette(a, b, k, L):
    """The block (X, Y), in S(2) of sites, for the plaquette at (a, b)."""
    if k == 1:
        return (a, b)
    return ((a // 2 if a % 2 else a // 2 - 1) % (L // 2), (b // 2 if b % 2 else b // 2 - 1) % (L // 2))


def assign_star(x, y, k, L):
    if k == 1:
        return ((x - 1) % L, (y - 1) % L)
    return (((x - 1) // 2 if x % 2 == 0 else x // 2 - 1) % (L // 2), ((y - 1) // 2 if y % 2 == 0 else y // 2 - 1) % (L // 2))


def check_terms(L, k):
    K = L // k
    used = set()
    for a in range(L):
        for b in range(L):
            for name, term, c in (("plaquette", plaquette(a, b, L), assign_plaquette(a, b, k, L)), ("star", star(a, b, L), assign_star(a, b, k, L))):
                if not owners(term) <= block_cells(c[0], c[1], 2, k, L):
                    return "term_%s_%d_%d_outside_block_%d_%d" % (name, a, b, c[0], c[1])
                used.add(c)
    if len(used) != K * K:
        return "blocks_used_%d_of_%d" % (len(used), K * K)
    return None


def check_region(L, k, X0, Y0, r):
    """A in S(r) at site (X0, Y0), B in S(r + 2) one site larger on each side. Returns the first failed inclusion, or None."""
    x0, y0 = X0 * k, Y0 * k
    span = r * k
    A_links = set()
    for x in range(x0, x0 + span):
        for y in range(y0, y0 + span):
            A_links |= {h(x, y, L), v(x, y, L)}
    # A' is the smallest rectangular sublattice holding A's links, with vertices x0 .. x0 + span in each direction.
    lo, hi = 0, span
    A_links_in = set()
    for i in range(lo, hi + 1):
        for j in range(lo, hi + 1):
            if i < hi:
                A_links_in.add(h(x0 + i, y0 + j, L))
            if j < hi:
                A_links_in.add(v(x0 + i, y0 + j, L))
    if not A_links <= A_links_in:
        return "A_links_outside_Aprime"
    # B' has vertices one original layer beyond A' on each side, so that V(A') is its interior.
    bx0, by0, bspan = x0 - 1, y0 - 1, span + 2
    if bspan >= L:
        return "Bprime_wraps"
    B_sites = {((X0 - 1 + i) % (L // k), (Y0 - 1 + j) % (L // k)) for i in range(r + 1) for j in range(r + 1)}
    for i in range(bspan):
        for j in range(bspan):
            a, b = bx0 + i, by0 + j
            c = assign_plaquette(a % L, b % L, k, L)
            if c not in B_sites:
                return "plaquette_%d_%d_of_Bprime_assigned_outside_B" % (a, b)
    for i in range(1, bspan):
        for j in range(1, bspan):
            x, y = bx0 + i, by0 + j
            c = assign_star(x % L, y % L, k, L)
            if c not in B_sites:
                return "star_%d_%d_of_Bprime_assigned_outside_B" % (x, y)
    return None


fails = 0
# k = 1: the unit-cell blocks. The first place the inclusion fails, on a lattice large enough to hold it.
first = None
for r in (1, 2, 3):
    bad = check_region(24, 1, 5, 5, r)
    print("BHM_DICTIONARY_UNIT_CELL|L=24|r=%d|terms=%s|inclusion=%s|json=0" % (r, check_terms(24, 1) or "PASS", bad or "PASS"))
    first = first or bad
# k = 2 on every even L in range.
regions = 0
for L in range(8, 42, 2):
    t = check_terms(L, 2)
    if t:
        fails += 1
        print("BHM_DICTIONARY_FAIL|L=%d|%s|json=0" % (L, t))
    K = L // 2
    for r in range(1, K - 1):
        for X0 in range(K):
            for Y0 in range(K):
                regions += 1
                bad = check_region(L, 2, X0, Y0, r)
                if bad:
                    fails += 1
                    if fails < 12:
                        print("BHM_DICTIONARY_FAIL|L=%d|r=%d|X0=%d|Y0=%d|%s|json=0" % (L, r, X0, Y0, bad))
    # r = K - 1 needs a B' as wide as the torus, so that is where the range ends.
    edge = check_region(L, 2, 0, 0, K - 1)
    print("BHM_DICTIONARY_K2|L=%d|sites_per_side=%d|r_max=%d|at_r_max_plus_1=%s|json=0" % (L, K, K - 2, edge or "PASS"))
print("BHM_DICTIONARY_DONE|k=2|regions=%d|failed=%d|unit_cell_first_failure=%s|json=0" % (regions, fails, first or "-"))
sys.exit(1 if fails else 0)
