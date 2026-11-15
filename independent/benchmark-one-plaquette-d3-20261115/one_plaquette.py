#!/usr/bin/env python3
"""Outside benchmark: this repository's S3 rule on ONE open plaquette, by brute force over all
6^4 link states, against the published D3 one-plaquette Hamiltonian matrix (3.3.27) and the
limit tables 3.11 and 3.12 of the Bologna thesis "Quantum simulation of non-Abelian gauge
theories" (amslaurea.unibo.it/id/eprint/29471). Integers only.

Repository rule (independent/finite_s3_3x4_r9_first_gap.py): for each link and each of the three
transpositions t, the move U_link -> t*U_link, electric term sum(1 - move); magnetic term
r * sum over plaquettes of (2 - chi(p)), chi the character of the two-dimensional representation.
Thesis: H = lE * sum_links Laplacian(Gamma_1 = reflections) - lB * 2 * chi_2(plaquette).
So the repository rule is the thesis rule with lE = 1, lB = r/2, plus the constant 2r per plaquette.
"""
from itertools import permutations, product

G = tuple(permutations(range(3)))
IDX = {a: i for i, a in enumerate(G)}
MUL = tuple(tuple(IDX[tuple(G[a][G[b][i]] for i in range(3))] for b in range(6)) for a in range(6))
INV = tuple(next(b for b in range(6) if MUL[a][b] == 0 and MUL[b][a] == 0) for a in range(6))
TRANS = tuple(i for i in range(1, 6) if MUL[i][i] == 0)
CHAR = tuple(sum(int(G[a][j] == j) for j in range(3)) - 1 for a in range(6))
LINKS = ((0, 1), (1, 2), (3, 2), (0, 3))  # link k runs from vertex u to vertex v


def emit(label, **f):
    print(label + "|" + "|".join("%s=%s" % kv for kv in f.items()) + "|json=0", flush=True)


def need(c, why):
    if not c:
        emit("BENCH_REFUSE", reason=why)
        raise SystemExit(1)


def holonomy(U):
    return MUL[MUL[MUL[U[0]][U[1]]][INV[U[2]]]][INV[U[3]]]


def gauge(U, vertex, g):
    out = list(U)
    for k, (u, v) in enumerate(LINKS):
        if u == vertex:
            out[k] = MUL[g][out[k]]
        if v == vertex:
            out[k] = MUL[out[k]][INV[g]]
    return tuple(out)


def orbits():
    states = list(product(range(6), repeat=4))
    parent = {s: s for s in states}

    def find(s):
        while parent[s] != s:
            parent[s] = parent[parent[s]]
            s = parent[s]
        return s

    for s in states:
        for vertex in range(4):
            for g in (1, 2, 3, 4, 5):
                a, b = find(s), find(gauge(s, vertex, g))
                if a != b:
                    parent[a] = b
    groups = {}
    for s in states:
        groups.setdefault(find(s), []).append(s)
    return sorted(groups.values(), key=len)


def orbit_matrix(r, electric=1):
    """H on gauge-invariant functions in the orbit-indicator basis: (H psi)(U) row for a state of orbit a."""
    orbs = orbits()
    where = {s: i for i, o in enumerate(orbs) for s in o}
    n = len(orbs)
    H = [[0] * n for _ in range(n)]
    for a, o in enumerate(orbs):
        rows = set()
        for s in o:
            row = [0] * n
            row[a] += electric * 12 + r * (2 - CHAR[holonomy(s)])
            for k in range(4):
                for t in TRANS:
                    m = list(s)
                    m[k] = MUL[t][m[k]]
                    row[where[tuple(m)]] -= electric
            rows.add(tuple(row))
        need(len(rows) == 1, "orbit_basis_not_closed")
        H[a] = list(rows.pop())
    return H, [len(o) for o in orbs], [CHAR[holonomy(o[0])] for o in orbs]


def charpoly3(M):
    tr = M[0][0] + M[1][1] + M[2][2]
    minors = (M[0][0] * M[1][1] - M[0][1] * M[1][0] + M[0][0] * M[2][2] - M[0][2] * M[2][0]
              + M[1][1] * M[2][2] - M[1][2] * M[2][1])
    det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
           + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
    return (1, -tr, minors, -det)


def roots_per_billion(p):
    """The three real roots, each floored to 1e-9, by sign changes on an integer grid then bisection."""
    S = 1000000000

    def val(x):  # sign of p(x/S)
        return x ** 3 * p[0] + x * x * S * p[1] + x * S * S * p[2] + S ** 3 * p[3]

    out, step = [], S // 100
    x = -100 * S
    while x < 100 * S:
        a, b = x, x + step
        if val(a) == 0 or (val(a) < 0) != (val(b) < 0):
            while b - a > 1:
                m = (a + b) // 2
                if (val(m) < 0) == (val(a) < 0) and val(m) != 0:
                    a = m
                else:
                    b = m
            out.append(a if val(a) != 0 else a)
        x += step
    return out


def main():
    need(len(TRANS) == 3 and sorted(CHAR) == [-1, -1, 0, 0, 0, 2], "group_tables")
    for r in (9, 12):
        H, sizes, chars = orbit_matrix(r)
        need(sizes == [216, 432, 648] and chars == [2, -1, 0], "three_orbits_identity_rotation_reflection")
        # thesis (3.3.27) with lE = 1, lB = r/2, plus the constant 2r: integer when r is even or doubled
        T2 = [[0, 0, -2 * r], [0, 48, -2 * r], [-2 * r, -2 * r, 24 - 2 * r]]  # 2*H1
        T2 = [[T2[i][j] + (4 * r if i == j else 0) for j in range(3)] for i in range(3)]  # + 2*(2r)
        H2 = [[2 * x for x in row] for row in H]
        same = charpoly3(H2) == charpoly3(T2)
        roots = roots_per_billion(charpoly3(H))
        need(len(roots) == 3, "three_real_roots")
        emit("BENCH_ONE_PLAQUETTE", r=r, thesis_lE=1, thesis_lB="%d/2" % r, constant=2 * r,
             orbit_sizes="216,432,648", brute_force_charpoly=",".join(map(str, charpoly3(H))),
             charpoly_equals_thesis_matrix=int(same),
             levels_floor_per_billion=",".join(map(str, roots)), gap_floor_per_billion=roots[1] - roots[0])
        need(same, "thesis_matrix_mismatch")
    He, _, _ = orbit_matrix(0)
    Hm, _, chars = orbit_matrix(1, electric=0)
    # run 1 used the grid root finder here; it counts an exact integer root twice (INSTRUMENT FAULT,
    # RESULT-BENCH-RUN1-INSTRUMENT-FAULT.hbp). The electric levels are integers, so they are tested exactly.
    pe = charpoly3(He)
    e_roots = [x for x in range(-100, 101) if x ** 3 * pe[0] + x * x * pe[1] + x * pe[2] + pe[3] == 0]
    m_vals = sorted(2 * Hm[i][i] - 4 for i in range(3))
    emit("BENCH_LIMITS", electric_levels=",".join(map(str, e_roots)), thesis_table_3_11_Gamma1="0,12,24",
         magnetic_levels_in_thesis_units=",".join(map(str, m_vals)), thesis_table_3_12="-4,0,2",
         electric_match=int(e_roots == [0, 12, 24]), magnetic_match=int(m_vals == [-4, 0, 2]))
    need(e_roots == [0, 12, 24] and m_vals == [-4, 0, 2], "limit_tables_mismatch")
    emit("BENCH_VERDICT", one_plaquette_rule_matches_published_D3_matrix=1, scope="one_open_plaquette_only",
         source="thesis_matrix_3.3.27_and_tables_3.11_3.12_read_2026-11-15")


if __name__ == "__main__":
    main()
