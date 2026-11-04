#!/usr/bin/env python3
"""Second seat's own multiplicity table. Integer only, json=0.

My incidence: sites v = x + Lx*y, links 2v (+x) and 2v+1 (+y). No import from the builder.
My character table: from the action of S3 on three points, by summing over the 6 elements.
My dim Inv: two routes. (1) characters summed over the group. (2) the rank of the group-average
projector on explicit integer matrices of the three irreps, with no characters used.
Counting: (a) plain enumeration of 3^links assignments, for small tori. (b) vertex elimination on the
tensor network, carrying a polynomial in the cost, for larger tori.

modes:
  table LX LY          full polynomial by vertex elimination, with Burnside and reflection checks.
  enum LX LY           plain enumeration, full table and assignments with states.
  low LX LY MAXCOST    the table truncated at MAXCOST, by vertex elimination.
"""
import sys

# ---------------------------------------------------------------- S3 on three points
ELEMENTS = []
for a in range(3):
    for b in range(3):
        for c in range(3):
            if a != b and b != c and a != c:
                ELEMENTS.append((a, b, c))
assert len(ELEMENTS) == 6


def fixed_points(p):
    return sum(1 for i in range(3) if p[i] == i)


def parity(p):
    inversions = sum(1 for i in range(3) for j in range(i + 1, 3) if p[i] > p[j])
    return 1 if inversions % 2 == 0 else -1


# Characters by construction: trivial, sign, and permutation minus trivial.
CHI = {
    "one": {p: 1 for p in ELEMENTS},
    "sgn": {p: parity(p) for p in ELEMENTS},
    "tau": {p: fixed_points(p) - 1 for p in ELEMENTS},
}
NAMES = ("one", "sgn", "tau")
COST = {"one": 0, "sgn": 6, "tau": 3}


# Costs read off the characters: 3 - 3 chi(t)/chi(e), exact.
def cost_from_character(name):
    chi = CHI[name]
    e = chi[(0, 1, 2)]
    t = chi[(1, 0, 2)]
    assert (3 * e - 3 * t) % e == 0
    return (3 * e - 3 * t) // e


for name in NAMES:
    assert cost_from_character(name) == COST[name]


def inv_by_characters(labels):
    total = 0
    for p in ELEMENTS:
        term = 1
        for name in labels:
            term *= CHI[name][p]
        total += term
    assert total % 6 == 0
    return total // 6


# ---------------------------------------------------------------- explicit integer matrices
def perm_matrix_on_sumzero(p):
    # Basis of the sum-zero subspace: b0 = e0 - e2, b1 = e1 - e2. Coordinates of a vector
    # (v0, v1, v2) with v0 + v1 + v2 = 0 are (v0, v1). p sends e_i to e_{p[i]}.
    columns = []
    for b in ((1, 0, -1), (0, 1, -1)):
        image = [0, 0, 0]
        for i in range(3):
            image[p[i]] += b[i]
        assert sum(image) == 0
        columns.append((image[0], image[1]))
    return [[columns[0][0], columns[1][0]], [columns[0][1], columns[1][1]]]


def rep_matrix(name, p):
    if name == "one":
        return [[1]]
    if name == "sgn":
        return [[parity(p)]]
    return perm_matrix_on_sumzero(p)


def kron(a, b):
    out = []
    for ra in a:
        for rb in b:
            out.append([x * y for x in ra for y in rb])
    return out


def add(a, b):
    return [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def rank_exact(m):
    m = [list(r) for r in m]
    rank = 0
    prev = 1
    cols = len(m[0]) if m else 0
    for col in range(cols):
        pivot = None
        for r in range(rank, len(m)):
            if m[r][col]:
                pivot = r
                break
        if pivot is None:
            continue
        m[rank], m[pivot] = m[pivot], m[rank]
        for r in range(rank + 1, len(m)):
            for j in range(col + 1, cols):
                v = m[rank][col] * m[r][j] - m[r][col] * m[rank][j]
                assert v % prev == 0
                m[r][j] = v // prev
            m[r][col] = 0
        prev = m[rank][col]
        rank += 1
    return rank


def inv_by_matrices(labels):
    total = None
    for p in ELEMENTS:
        k = [[1]]
        for name in labels:
            k = kron(k, rep_matrix(name, p))
        total = k if total is None else add(total, k)
    return rank_exact(total)


def invariant_table():
    table = {}
    disagreements = 0
    for i in NAMES:
        for j in NAMES:
            for k in NAMES:
                for l in NAMES:
                    a = inv_by_characters((i, j, k, l))
                    b = inv_by_matrices((i, j, k, l))
                    if a != b:
                        disagreements += 1
                    table[i, j, k, l] = a
    return table, disagreements


# ---------------------------------------------------------------- the torus, my incidence
def torus(lx, ly):
    links = []
    for y in range(ly):
        for x in range(lx):
            links.append((x + lx * y, (x + 1) % lx + lx * y))
            links.append((x + lx * y, x + lx * ((y + 1) % ly)))
    return links, lx * ly


def burnside(links, vertices):
    b = links - vertices + 1
    total = 6 ** b + 3 * 2 ** b + 2 * 3 ** b
    assert total % 6 == 0
    return total // 6


def enumerate_table(lx, ly, inv):
    links, nv = torus(lx, ly)
    ends = [[] for _ in range(nv)]
    for l, (a, b) in enumerate(links):
        ends[a].append(l)
        ends[b].append(l)
    assert all(len(e) == 4 for e in ends)
    table = {}
    with_states = 0
    n = len(links)
    label = [0] * n
    count = 3 ** n
    for code in range(count):
        c = code
        for l in range(n):
            label[l] = c % 3
            c //= 3
        states = 1
        for e in ends:
            states *= inv[NAMES[label[e[0]]], NAMES[label[e[1]]], NAMES[label[e[2]]], NAMES[label[e[3]]]]
            if not states:
                break
        if states:
            with_states += 1
            cost = sum(COST[NAMES[x]] for x in label)
            table[cost] = table.get(cost, 0) + states
    return table, with_states, count


def eliminate(lx, ly, inv, maxcost=None):
    """Vertex elimination. State: labels of the links with one processed end -> {cost: count}."""
    links, nv = torus(lx, ly)
    ends = [[] for _ in range(nv)]
    for l, (a, b) in enumerate(links):
        ends[a].append(l)
        ends[b].append(l)
    assert all(len(e) == 4 for e in ends)
    order = list(range(nv))
    processed = set()
    frontier = []  # link ids in fixed order
    states = {(): {0: 1}}
    biggest = 1
    for v in order:
        incident = ends[v]
        distinct = []
        for l in incident:
            if l not in distinct:
                distinct.append(l)
        new_links = [l for l in distinct if l not in frontier]
        position = {l: k for k, l in enumerate(frontier)}
        closes = set()
        for l in distinct:
            a, b = links[l]
            other_done = (a in processed or a == v) and (b in processed or b == v)
            if other_done:
                closes.add(l)
        keep = [l for l in frontier if l not in closes] + [l for l in new_links if l not in closes]
        next_states = {}
        n_new = len(new_links)
        for key, poly in states.items():
            for code in range(3 ** n_new):
                assign = {}
                c = code
                for l in new_links:
                    assign[l] = c % 3
                    c //= 3
                for l, k in position.items():
                    assign[l] = key[k]
                dim = inv[tuple(NAMES[assign[l]] for l in incident)]
                if not dim:
                    continue
                add_cost = sum(COST[NAMES[assign[l]]] for l in new_links)
                new_key = tuple(assign[l] for l in keep)
                target = next_states.setdefault(new_key, {})
                for cost, count in poly.items():
                    total_cost = cost + add_cost
                    if maxcost is not None and total_cost > maxcost:
                        continue
                    target[total_cost] = target.get(total_cost, 0) + count * dim
        states = {k: p for k, p in next_states.items() if p}
        frontier = keep
        processed.add(v)
        biggest = max(biggest, len(states))
    assert list(states) == [()] and frontier == []
    return states[()], biggest


def text(table):
    return ",".join("%d:%d" % (c, table[c]) for c in sorted(table) if table[c])


def main(argv):
    inv, disagreements = invariant_table()
    print("OWN_INV|tuples=81|characters_vs_matrix_rank_disagreements=%d|json=0" % disagreements)
    if disagreements:
        sys.exit(1)
    mode = argv[0]
    lx, ly = int(argv[1]), int(argv[2])
    links, nv = torus(lx, ly)
    if mode == "enum":
        table, with_states, count = enumerate_table(lx, ly, inv)
        print("OWN_ENUM|L=%dx%d|links=%d|assignments=%d|with_states=%d|sum_m=%d|burnside=%d|table=%s|json=0"
              % (lx, ly, len(links), count, with_states, sum(table.values()), burnside(len(links), nv), text(table)))
        return
    if mode == "table":
        table, biggest = eliminate(lx, ly, inv)
        total = sum(table.values())
        bs = burnside(len(links), nv)
        top = 6 * len(links)
        reflect = all(table.get(c, 0) == table.get(top - c, 0) for c in table)
        smallest = min(c for c in table if c and table[c])
        formula = 3 * min(4, lx, ly)
        print("OWN_TABLE|L=%dx%d|links=%d|sum_m=%d|burnside=%d|closure=%d|reflection=%d|smallest_nonzero_cost=%d|m_at_it=%d|formula=%d|formula_holds=%d|frontier_states_max=%d|json=0"
              % (lx, ly, len(links), total, bs, total == bs, reflect, smallest, table[smallest], formula, smallest == formula, biggest))
        print("OWN_TABLE_M|L=%dx%d|table=%s|json=0" % (lx, ly, text(table)))
        return
    if mode == "low":
        maxcost = int(argv[3])
        table, biggest = eliminate(lx, ly, inv, maxcost)
        nonzero = sorted(c for c in table if c and table[c])
        smallest = nonzero[0] if nonzero else -1
        formula = 3 * min(4, lx, ly)
        print("OWN_LOW|L=%dx%d|links=%d|maxcost=%d|table=%s|smallest_nonzero_cost=%d|formula=%d|formula_holds=%d|frontier_states_max=%d|json=0"
              % (lx, ly, len(links), maxcost, text(table), smallest, formula, smallest == formula, biggest))
        return
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
