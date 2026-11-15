#!/usr/bin/env python3
"""Outside benchmark: this repository's S3 rule on TWO open plaquettes sharing a link, by brute force
over all 6^7 link states, against the published 11x11 D3 two-plaquette matrices (H_1E and H_B,
printed page 95) of the Bologna thesis eprint 29471. Integers only.

The thesis matrices carry sqrt(2) only in the row and column of the eleventh basis state. Scaling that
basis vector by sqrt(2) (a similarity, same characteristic polynomial) and doubling gives integer matrices.
Repository rule = thesis rule with lE = 1, lB = r/2, plus the constant 2r per plaquette.
"""
from itertools import permutations, product

G = tuple(permutations(range(3)))
IDX = {a: i for i, a in enumerate(G)}
MUL = tuple(tuple(IDX[tuple(G[a][G[b][i]] for i in range(3))] for b in range(6)) for a in range(6))
INV = tuple(next(b for b in range(6) if MUL[a][b] == 0 and MUL[b][a] == 0) for a in range(6))
TRANS = tuple(i for i in range(1, 6) if MUL[i][i] == 0)
CHAR = tuple(sum(int(G[a][j] == j) for j in range(3)) - 1 for a in range(6))
# vertices: 0 1 2 (bottom), 3 4 5 (top); link k from u to v
LINKS = ((0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5))
N = 11

# thesis, printed page 95: 2*H_1E after the sqrt(2) scaling of basis vector 11
HE2 = [[0] * N for _ in range(N)]
for i, d in enumerate((0, 24, 12, 24, 36, 30, 12, 30, 18, 24, 21)):
    HE2[i][i] = 2 * d
HE2[8][10], HE2[9][10], HE2[10][8], HE2[10][9] = 6, -6, 3, -3
# thesis H_B = -lB * P, P as printed (rows), with s = sqrt(2)
P_PRINTED = (
    "0 0 2 0 0 0 2 0 0 0 0", "0 0 2 0 0 0 0 2 0 0 0", "2 2 2 0 0 0 0 0 1 1 s", "0 0 0 0 0 2 2 0 0 0 0",
    "0 0 0 0 0 2 0 2 0 0 0", "0 0 0 2 2 2 0 0 1 1 s", "2 0 0 2 0 0 2 0 1 1 s", "0 2 0 0 0 0 0 2 1 1 s",
    "0 0 1 0 0 1 1 1 0 0 2s", "0 0 1 0 0 1 1 1 0 0 2s", "0 0 s 0 0 s s s 2s 2s 0")


def emit(label, **f):
    print(label + "|" + "|".join("%s=%s" % kv for kv in f.items()) + "|json=0", flush=True)


def need(c, why):
    if not c:
        emit("BENCH2_REFUSE", reason=why)
        raise SystemExit(1)


def scaled_P(symmetrise):
    """2 * D^-1 P D with D = diag(1,..,1,sqrt2): integer matrix. Returns (matrix, printed_is_symmetric)."""
    raw = [row.split() for row in P_PRINTED]
    sym = all(raw[i][j] == raw[j][i] for i in range(N) for j in range(N))
    if symmetrise:
        need(raw[4][7] == "2" and raw[7][4] == "0", "expected_single_asymmetry_at_(5,8)_(8,5)")
        raw[7][4] = "2"
        need(all(raw[i][j] == raw[j][i] for i in range(N) for j in range(N)), "symmetrised_not_symmetric")
    out = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            t = raw[i][j]
            if t.endswith("s"):
                c = int(t[:-1] or "1")
                need((i == N - 1) != (j == N - 1), "sqrt2_outside_last_row_or_column")
                out[i][j] = 4 * c if j == N - 1 else 2 * c  # column: *sqrt2*sqrt2*... ; row: /sqrt2
            else:
                out[i][j] = 2 * int(t)
    return out, sym


def charpoly(M):
    """Faddeev-LeVerrier, exact integers."""
    n = len(M)
    coeffs, A = [1], [[0] * n for _ in range(n)]
    for k in range(1, n + 1):
        A = [[sum(M[i][l] * (A[l][j] + (coeffs[-1] if l == j else 0)) for l in range(n)) for j in range(n)] for i in range(n)]
        tr = sum(A[i][i] for i in range(n))
        need(tr % k == 0, "Faddeev_division")
        coeffs.append(-tr // k)
    return tuple(coeffs)


def holonomies(U):
    a = MUL[MUL[MUL[U[0]][U[5]]][INV[U[2]]]][INV[U[4]]]
    b = MUL[MUL[MUL[U[1]][U[6]]][INV[U[3]]]][INV[U[5]]]
    return a, b


def gauge(U, vertex, g):
    out = list(U)
    for k, (u, v) in enumerate(LINKS):
        if u == vertex:
            out[k] = MUL[g][out[k]]
        if v == vertex:
            out[k] = MUL[out[k]][INV[g]]
    return tuple(out)


def orbit_data():
    states = list(product(range(6), repeat=7))
    parent = {s: s for s in states}

    def find(s):
        root = s
        while parent[root] != root:
            root = parent[root]
        while parent[s] != root:
            parent[s], s = root, parent[s]
        return root

    for s in states:
        for vertex in range(6):
            for g in (1, 3):  # one 3-cycle or transposition pair generates S3; both indices checked below
                a, b = find(s), find(gauge(s, vertex, g))
                if a != b:
                    parent[a] = b
    where, sizes = {}, []
    for s in states:
        r = find(s)
        if r not in where:
            where[r] = len(sizes)
            sizes.append(0)
        sizes[where[r]] += 1
    need(len({MUL[1][1], MUL[3][3]}) >= 1 and len({1, 3} & set(TRANS)) >= 1, "generator_choice")
    # full invariance check on every generator and state
    for s in states[::97]:
        for vertex in range(6):
            for g in range(1, 6):
                need(find(gauge(s, vertex, g)) == find(s), "orbit_not_gauge_closed")
    return states, find, where, sizes


def orbit_matrix(r, electric, data):
    states, find, where, sizes = data
    n = len(sizes)
    H, seen = [None] * n, [False] * n
    for s in states:
        a = where[find(s)]
        row = [0] * n
        ha, hb = holonomies(s)
        row[a] += electric * 21 + r * (4 - CHAR[ha] - CHAR[hb])
        for k in range(7):
            for t in TRANS:
                m = list(s)
                m[k] = MUL[t][m[k]]
                row[where[find(tuple(m))]] -= electric
        if H[a] is None:
            H[a] = row
        else:
            need(H[a] == row, "orbit_basis_not_closed")
    return H


def main():
    need(len(TRANS) == 3 and sorted(CHAR) == [-1, -1, 0, 0, 0, 2], "group_tables")
    data = orbit_data()
    need(len(data[3]) == N and sum(data[3]) == 6 ** 7, "eleven_gauge_orbits")
    emit("BENCH2_ORBITS", count=N, sizes=",".join(map(str, sorted(data[3]))))
    He = orbit_matrix(0, 1, data)
    e_same = charpoly([[2 * x for x in row] for row in He]) == charpoly(HE2)
    emit("BENCH2_ELECTRIC", brute_force_charpoly_equals_thesis_H1E=int(e_same))
    Hm = orbit_matrix(1, 0, data)
    m_levels = sorted(2 * Hm[i][i] - 8 for i in range(N))
    target = [-8, -4, -4, -2, -2, 0, 0, 2, 2, 4, 4]
    results = {}
    for name, symm in (("AS_PRINTED", False), ("SYMMETRISED_(8,5)=2", True)):
        P2, printed_symmetric = scaled_P(symm)
        want = [1]
        for v in target:  # prod (x - 2v) for the doubled matrix 2*H_B = -2P at lB = 1
            want = [a - 2 * v * b for a, b in zip(want + [0], [0] + want)]
        m_same = charpoly([[-x for x in row] for row in P2]) == tuple(want)
        full = []
        for r in (9, 12):
            H = orbit_matrix(r, 1, data)
            T2 = [[2 * HE2[i][j] - r * P2[i][j] + (16 * r if i == j else 0)
                   for j in range(N)] for i in range(N)]  # 4*H_thesis = 2*(2HE) - r*(2P) + 16r
            full.append(charpoly([[4 * x for x in row] for row in H]) == charpoly(T2))
        results[name] = (m_same, full)
        emit("BENCH2_THESIS_HB", reading=name, printed_matrix_symmetric=int(printed_symmetric),
             magnetic_spectrum_equals_text=int(m_same), full_charpoly_equal_r9=int(full[0]), full_charpoly_equal_r12=int(full[1]))
    emit("BENCH2_LIMITS", brute_force_magnetic_levels_thesis_units=",".join(map(str, m_levels)),
         thesis_text="-8,-4,-4,-2,-2,0,0,2,2,4,4", match=int(m_levels == target))
    ok = e_same and m_levels == target and any(all(v[1]) and v[0] for v in results.values())
    emit("BENCH2_VERDICT", two_plaquette_rule_matches_published_D3=int(ok),
         matching_reading=",".join(k for k, v in results.items() if v[0] and all(v[1])) or "NONE",
         scope="two_open_plaquettes_only")
    need(ok, "two_plaquette_mismatch")


if __name__ == "__main__":
    main()
