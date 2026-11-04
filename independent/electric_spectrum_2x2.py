#!/usr/bin/env python3
"""Exact spectrum of the pure electric operator on the periodic 2x2 S3 torus. Integer only, json=0.

E = sum over the 8 links of (3 - sum over the 3 transpositions of the link move), on the 1,393
gauge-invariant orbits. The statement: eigenvalue 0 is simple, nothing lies strictly between 0 and 6,
and 6 has multiplicity 4, so gap(E) = 6 exactly. Scope: this finite torus.

Modes, each exits 1 on the first check that does not hold:
  a                         Path A, the 6x6 single-link matrix, its cubic and its exact ranks.
  b                         Path B, the multiplicities from the characters of S3, on 2x2 and on 2x3.
  c                         Path C, on the real matrix from gpt6_2x2_from_permutations.py: the operator
                            pin, P(E) = 0 on all 1,393 basis vectors, each P/(x-c) at E nonzero, the
                            traces, the multiplicities read back from prefix traces, the four length-2
                            Wilson loops and the eight link operators.
  same                      The matrix and the bound inside seat_global_coupling.py against that matrix.
  f MEASURE                 Path F, the conclusion with its steps, from the rows pinned in MEASURE.
  g [FOLDER]                Path G, the formula gap(E) = 3*min(4,Lx,Ly) on a periodic torus: the vertex rule, the girth
                            of the torus multigraph, and every low-cost assignment of the tori listed below. With
                            FOLDER, also the second seat's 28 tori from its logs there.
  predictions PRED RETRY RETRY2 MEASURE
                            Each prediction row against the rows in MEASURE. A row with another value reads MISS, an
                            appended row included, since every row with the head counts. When every row present reads
                            as predicted, a row absent from MEASURE reads NOT_MEASURED with its reason. It prints every
                            verdict and exits 0, so a miss is recorded beside its row.

Red controls, each must exit 1:
  a --alter-entry, b --bad-character, c --alter-entry, c --drop-factor C, c --add-factor C, g --bad-character,
  g --cap C, g --alter-vertex, g --alter-vertex-from-2x2, g --permutation-character, g --alter-empty-vertex,
  and f on a MEASURE with a changed row.
"""
import os
import runpy
import sys
from contextlib import redirect_stdout
from io import StringIO
from itertools import combinations, permutations, product

HERE = os.path.dirname(os.path.abspath(__file__))
OPERATOR_PIN = "b6c608f50f81f3bf48fb0203b48e0e3bfc867037dc1d0a96633aa80b962137f3"
INDEP_CODE_PIN = "a501b563619c4364e4d8b15564a33de57e659fc00043c05af223f4e9c7bc9f61"
INDEP_KERNEL_PIN = "c5a66e8fafdf56b63eb385085ef3b352a7559e6072f8c99791b74b46392bc40a"
INDEP_KERNEL_SOURCE_BLOB = "b159b7eda3c60ea24e518c855800116ac2fff2d7"


def emit(tag, *fields):
    print("|".join((tag,) + fields + ("json=0",)), flush=True)


def fail(path, reason, *fields):
    emit("ELECTRIC_FAIL", "path=" + path, "reason=" + reason, *fields)
    sys.exit(1)


def table_text(table):
    return ",".join("%d:%d" % (c, table[c]) for c in sorted(table) if table[c])


# ---------------------------------------------------------------- exact small-matrix arithmetic


def mat_mul(a, b):
    columns = range(len(b[0]))
    return [[sum(x * b[k][j] for k, x in enumerate(row)) for j in columns] for row in a]


def shifted(a, c):
    return [[x - c * (i == j) for j, x in enumerate(row)] for i, row in enumerate(a)]


def is_zero(a):
    return all(x == 0 for row in a for x in row)


def exact_rank(matrix, path):
    """Rank by fraction-free elimination. Each division is checked to be exact."""
    m = [list(row) for row in matrix]
    rank = 0
    previous = 1
    for col in range(len(m[0])):
        pivot = next((r for r in range(rank, len(m)) if m[r][col]), None)
        if pivot is None:
            continue
        m[rank], m[pivot] = m[pivot], m[rank]
        head = m[rank]
        for r in range(rank + 1, len(m)):
            row = m[r]
            factor = row[col]
            for j in range(col + 1, len(head)):
                value = head[col] * row[j] - factor * head[j]
                if value % previous:
                    fail(path, "elimination_not_exact")
                row[j] = value // previous
            row[col] = 0
        previous = head[col]
        rank += 1
        if rank == len(m):
            break
    return rank


# ---------------------------------------------------------------- path A, one link


def s3_table():
    perms = tuple(permutations(range(3)))
    index = {p: i for i, p in enumerate(perms)}
    mul = tuple(tuple(index[tuple(perms[a][perms[b][k]] for k in range(3))] for b in range(6)) for a in range(6))
    transpositions = tuple(x for x in range(6) if x != 0 and mul[x][x] == 0)
    return perms, mul, transpositions


def single_link_matrix():
    """A[g][h] = 3 delta(g,h) - #{t : t g = h}, the matrix of 3 - sum_t R_t with (R_t f)(g) = f(t g)."""
    _, mul, transpositions = s3_table()
    a = [[0] * 6 for _ in range(6)]
    for g in range(6):
        a[g][g] += 3
        for t in transpositions:
            a[g][mul[t][g]] -= 1
    return a, len(transpositions)


def path_a(alter):
    a, count = single_link_matrix()
    if count != 3:
        fail("A", "transposition_count", "count=%d" % count)
    if alter:
        a[0][1] += 1
    a3, a6 = shifted(a, 3), shifted(a, 6)
    if not is_zero(mat_mul(mat_mul(a, a3), a6)):
        fail("A", "cubic_nonzero")
    pairs = (("A(A-3)", mat_mul(a, a3)), ("A(A-6)", mat_mul(a, a6)), ("(A-3)(A-6)", mat_mul(a3, a6)))
    if any(is_zero(p) for _, p in pairs):
        fail("A", "a_factor_of_the_cubic_is_not_needed")
    rank0, rank3, rank6 = exact_rank(a, "A"), exact_rank(a3, "A"), exact_rank(a6, "A")
    m0, m3, m6 = 6 - rank0, 6 - rank3, 6 - rank6
    trace = sum(a[i][i] for i in range(6))
    if m0 + m3 + m6 != 6 or 3 * m3 + 6 * m6 != trace:
        fail("A", "multiplicities_do_not_close", "m=%d,%d,%d" % (m0, m3, m6), "trace=%d" % trace)
    emit("ELECTRIC_A", "group=S3", "order=6", "transpositions=%d" % count, "matrix=3I-sum_t_R_t",
         "row_sums=%d" % max(abs(sum(row)) for row in a), "trace=%d" % trace)
    emit("ELECTRIC_A", "cubic=A(A-3)(A-6)", "value=0", "exact=1", *(n + "=NONZERO" for n, _ in pairs),
         "minimal_polynomial=x(x-3)(x-6)")
    emit("ELECTRIC_A", "rank_A=%d" % rank0, "rank_A_minus_3=%d" % rank3, "rank_A_minus_6=%d" % rank6,
         "multiplicities=0x%d,3x%d,6x%d" % (m0, m3, m6), "sum=%d" % (m0 + m3 + m6), "result=PASS")
    emit("ELECTRIC_A_DERIVED", "step=link_operators_on_different_links_commute_and_each_has_spectrum_in_0,3,6",
         "so=every_eigenvalue_of_E_is_a_sum_of_8_values_in_0,3,6", "spectrum_of_E_in=3Z_intersect_[0,48]",
         "measured_on_the_1393_matrix_by=ELECTRIC_C_LINKS", "tag=DERIVED")


# ---------------------------------------------------------------- path B, characters

CLASS_SIZES = (1, 3, 2)  # identity, transpositions, 3-cycles
CHARACTERS = ((1, 1, 1), (1, -1, 1), (2, 0, -1))  # trivial, sign, standard tau; all real, so orientation is free


def irrep_costs(characters):
    """Eigenvalue of 3 - sum_t R_t on an irrep: 3 - 3 chi(t) / chi(e), exact."""
    costs = []
    for chi in characters:
        top = 3 * chi[0] - 3 * chi[1]
        if top % chi[0]:
            fail("B", "cost_not_exact")
        costs.append(top // chi[0])
    return tuple(costs)


def torus_links(lx, ly):
    def site(x, y):
        return ly * (x % lx) + (y % ly)
    x_links = [(site(x, y), site(x + 1, y)) for x in range(lx) for y in range(ly)]
    y_links = [(site(x, y), site(x, y + 1)) for x in range(lx) for y in range(ly)]
    return x_links + y_links


def invariant_table(characters):
    """dim Inv for every tuple of 4 irreps at a vertex, from the characters."""
    invariants = {}
    for irreps in product(range(3), repeat=4):
        total = 0
        for cls in range(3):
            term = CLASS_SIZES[cls]
            for r in irreps:
                term *= characters[r][cls]
            total += term
        if total % 6:
            fail("B", "dim_inv_not_divisible_by_6", "irreps=%d,%d,%d,%d" % irreps, "total=%d" % total)
        invariants[irreps] = total // 6
    return invariants


def character_table(lx, ly, characters):
    """m[cost] = sum over assignments of {1, sign, tau} to links of the product over vertices of dim Inv."""
    links = torus_links(lx, ly)
    vertices = lx * ly
    ends = [tuple(k for k, link in enumerate(links) for end in link if end == v) for v in range(vertices)]
    if any(len(e) != 4 for e in ends):
        fail("B", "vertex_valence")
    invariants = invariant_table(characters)
    cost_of = irrep_costs(characters)
    table = {c: 0 for c in range(0, 6 * len(links) + 1, 3)}
    assignments, with_states = 0, 0
    for assignment in product(range(3), repeat=len(links)):
        assignments += 1
        states = 1
        for a, b, c, d in ends:
            states *= invariants[assignment[a], assignment[b], assignment[c], assignment[d]]
            if not states:
                break
        if states:
            with_states += 1
            table[sum(cost_of[r] for r in assignment)] += states
    return table, len(links), vertices, assignments, with_states


def burnside(links, vertices):
    free = links - vertices + 1
    total = 6 ** free + 3 * 2 ** free + 2 * 3 ** free
    if total % 6:
        fail("B", "burnside_not_divisible")
    return total // 6


def path_b_lattice(lx, ly, characters):
    label = "%dx%d" % (lx, ly)
    table, links, vertices, assignments, with_states = character_table(lx, ly, characters)
    total = sum(table.values())
    expected = burnside(links, vertices)
    if total != expected:
        fail("B", "total_differs_from_burnside", "L=" + label, "total=%d" % total, "burnside=%d" % expected)
    top = 6 * links
    if any(table[c] != table[top - c] for c in table):
        fail("B", "reflection_broken", "L=" + label)
    smallest = min(c for c in table if c and table[c])
    formula = 3 * min(4, lx, ly)
    if smallest != formula:
        fail("B", "formula_differs", "L=" + label, "smallest=%d" % smallest, "formula=%d" % formula)
    emit("ELECTRIC_B", "L=" + label, "links=%d" % links, "vertices=%d" % vertices, "assignments=%d" % assignments,
         "assignments_with_states=%d" % with_states, "sum_m=%d" % total, "burnside=%d" % expected,
         "reflection_m[c]=m[%d-c]=1" % top, "smallest_nonzero_cost=%d" % smallest,
         "formula_3min(4,Lx,Ly)=%d" % formula, "result=PASS")
    cumulative = 0
    for c in sorted(table):
        cumulative += table[c]
        emit("ELECTRIC_B_M", "L=" + label, "cost=%d" % c, "m=%d" % table[c], "cumulative=%d" % cumulative)
    return table


def path_b(bad_character):
    characters = CHARACTERS
    if bad_character:
        characters = (CHARACTERS[0], CHARACTERS[1], (2, 0, 1))
    emit("ELECTRIC_B_COSTS", "trivial=%d" % irrep_costs(characters)[0], "sign=%d" % irrep_costs(characters)[1],
         "tau=%d" % irrep_costs(characters)[2], "class_sizes=1,3,2", "tau_character=2,0,-1")
    path_b_lattice(2, 2, characters)
    path_b_lattice(2, 3, characters)
    emit("ELECTRIC_B_FORMULA", "formula=gap(E)=3*min(4,Lx,Ly)", "tested_on=2x2,2x3", "tag=CONJECTURE")


# ---------------------------------------------------------------- path C, the real matrix


def load_gpt6_model():
    path = os.path.join(HERE, "gpt6_2x2_from_permutations.py")
    saved = sys.argv
    with redirect_stdout(StringIO()):
        sys.argv = [path]
        try:
            model = runpy.run_path(path)
        finally:
            sys.argv = saved
    return model


def apply_factor(e, c, v):
    """(E - c) v, exact, with E as rows of (column, value)."""
    return [sum([x * v[j] for j, x in row]) - c * v[i] for i, row in enumerate(e)]


def unit(n, b):
    v = [0] * n
    v[b] = 1
    return v


def first_nonzero(v):
    return next((i for i, x in enumerate(v) if x), None)


def check_annihilator(e, roots):
    """Applies the factors of P in order to every basis vector. Returns the traces of the prefix products."""
    n = len(e)
    traces = [0] * (len(roots) + 1)
    for b in range(n):
        v = unit(n, b)
        traces[0] += 1
        for k, c in enumerate(roots, 1):
            v = apply_factor(e, c, v)
            traces[k] += v[b]
        i = first_nonzero(v)
        if i is not None:
            fail("C", "P_of_E_nonzero", "basis=%d" % b, "row=%d" % i, "value=%d" % v[i],
                 "P_roots=" + ",".join(map(str, roots)))
    return traces


def factor_witness(e, roots, dropped):
    n = len(e)
    rest = [c for c in roots if c != dropped]
    for b in range(n):
        v = unit(n, b)
        for c in rest:
            v = apply_factor(e, c, v)
        i = first_nonzero(v)
        if i is not None:
            return b, i, v[i]
    return None


def newton(roots, k, x):
    value = 1
    for c in roots[:k]:
        value *= x - c
    return value


def multiplicities_from_prefix_traces(roots, traces):
    """Solves traces[k] = sum_j m[j] newton(k, roots[j]). Triangular, since newton(k, roots[j]) = 0 for j < k."""
    r = len(roots)
    m = [0] * r
    for j in range(r - 1, -1, -1):
        rest = traces[j] - sum(m[i] * newton(roots, j, roots[i]) for i in range(j + 1, r))
        pivot = newton(roots, j, roots[j])
        if rest % pivot:
            fail("C", "prefix_trace_not_divisible", "root=%d" % roots[j])
        m[j] = rest // pivot
    return {roots[j]: m[j] for j in range(r)}


def sparse_mul(a, b):
    out = []
    for row in a:
        acc = {}
        for j, x in row.items():
            for k, y in b[j].items():
                acc[k] = acc.get(k, 0) + x * y
        out.append({k: v for k, v in acc.items() if v})
    return out


def sparse_shift(a, c):
    out = []
    for i, row in enumerate(a):
        new = dict(row)
        new[i] = new.get(i, 0) - c
        out.append({k: v for k, v in new.items() if v})
    return out


def check_link_operators(model, rows):
    """The 8 link operators on the 1,393 orbits: they sum to E, commute, and each satisfies the cubic."""
    keys, pos, fixed, number, expand, decode, c_table, transpositions = (
        model["keys"], model["pos"], model["fixed"], model["number"], model["expand"], model["decode"],
        model["C"], model["T"])
    n = len(keys)
    operators = []
    for link in range(8):
        operator = []
        for i, key in enumerate(keys):
            u = expand(decode(key))
            row = {i: 3}
            for t in transpositions:
                v = list(u)
                v[link] = c_table[t][u[link]]
                j = pos[number(fixed(v))]
                row[j] = row.get(j, 0) - 1
            operator.append({k: x for k, x in row.items() if x})
        operators.append(operator)
    for i in range(n):
        total = {}
        for operator in operators:
            for j, x in operator[i].items():
                total[j] = total.get(j, 0) + x
        if {j: x for j, x in total.items() if x} != rows[i]:
            fail("C", "link_operators_do_not_sum_to_E", "row=%d" % i)
    commuting = 0
    for a, b in combinations(range(8), 2):
        if sparse_mul(operators[a], operators[b]) != sparse_mul(operators[b], operators[a]):
            fail("C", "link_operators_do_not_commute", "links=%d,%d" % (a, b))
        commuting += 1
    cubic = 0
    for operator in operators:
        product_matrix = sparse_mul(sparse_mul(operator, sparse_shift(operator, 3)), sparse_shift(operator, 6))
        if any(product_matrix):
            fail("C", "link_operator_cubic_nonzero")
        cubic += 1
    emit("ELECTRIC_C_LINKS", "operators=8", "sum_equals_E_rows=%d/%d" % (n, n), "commuting_pairs=%d/28" % commuting,
         "cubic_x(x-3)(x-6)=%d/8" % cubic, "so=spectrum_of_E_in_3Z_intersect_[0,48]", "result=PASS")


def check_wilson_loops(model, rows):
    """The four length-2 loops chi(U_a U_b) are exact eigenvectors at 6. Sector split by rank."""
    keys, expand, decode, c_table, chi, translation = (
        model["keys"], model["expand"], model["decode"], model["C"], model["chi"], model["translation"])
    reps = [expand(decode(key)) for key in keys]
    edge = model["EDGE"]
    loops = []
    for a, b in ((0, 2), (1, 3), (4, 5), (6, 7)):
        if edge[a] != (edge[b][1], edge[b][0]):
            fail("C", "loop_links_not_parallel", "links=%d,%d" % (a, b))
        loops.append([chi(c_table[u[a]][u[b]]) for u in reps])
    for f in loops:
        for i, row in enumerate(rows):
            if sum(x * f[j] for j, x in row.items()) != 6 * f[i]:
                fail("C", "wilson_loop_not_an_eigenvector_at_6", "row=%d" % i)
    rank = exact_rank(loops, "C")
    if rank != 4:
        fail("C", "wilson_loop_rank", "rank=%d" % rank)
    split = []
    for name, sx, sy in (("pp", 1, 1), ("pm", 1, -1), ("mp", -1, 1), ("mm", -1, -1)):
        projected = []
        for f in loops:
            g = [0] * len(f)
            for (dx, dy), perm in translation.items():
                sign = (sx if dx else 1) * (sy if dy else 1)
                for i, j in enumerate(perm):
                    g[i] += sign * f[j]
            if any(g):
                projected.append(g)
        split.append((name, exact_rank(projected, "C") if projected else 0))
    text = ",".join("%s=%d" % pair for pair in split)
    with_constant = ",".join(str(r + (name == "pp")) for name, r in split)
    emit("ELECTRIC_C_LOOPS", "loops=links_0,2+1,3+4,5+6,7", "eigenvalue=6", "exact_rows=1393", "rank=%d" % rank,
         "sector_rank=" + text, "with_the_constant=" + with_constant, "result=PASS")


def check_reflection(model, rows):
    """S = the product of the signs of all links, gauge invariant at valence 4. Exact: S E S = 48 - E."""
    keys, expand, decode, transpositions = model["keys"], model["expand"], model["decode"], model["T"]
    signs = []
    for key in keys:
        sign = 1
        for x in expand(decode(key)):
            if x in transpositions:
                sign = -sign
        signs.append(sign)
    n = len(rows)
    for i, row in enumerate(rows):
        reflected = {j: signs[i] * signs[j] * x for j, x in row.items()}
        direct = {j: -x for j, x in row.items()}
        direct[i] = direct.get(i, 0) + 48
        if {j: x for j, x in reflected.items() if x} != {j: x for j, x in direct.items() if x}:
            fail("C", "reflection_S_E_S_differs_from_48_minus_E", "row=%d" % i)
    emit("ELECTRIC_C_REFLECTION", "S=product_of_link_signs", "S_E_S=48-E", "exact_rows=%d/%d" % (n, n),
         "plus_signs=%d" % signs.count(1), "minus_signs=%d" % signs.count(-1),
         "so=m[c]=m[48-c]_on_the_matrix_and_B(48-T)=-S*B(T)*S", "result=PASS")


def path_c(alter, drop, add=None):
    table, _, _, _, _ = character_table(2, 2, CHARACTERS)
    roots = [c for c in sorted(table) if table[c]]
    model = load_gpt6_model()
    if model["operator_sha"] != OPERATOR_PIN:
        fail("C", "operator_pin", "sha=" + model["operator_sha"])
    if tuple(model["EDGE"]) != tuple(torus_links(2, 2)):
        fail("C", "graph_differs_from_path_B")
    rows = [dict(row) for row in model["rows"]]
    n = len(rows)
    nnz = sum(map(len, rows))
    if alter:
        j = min(k for k in rows[0] if k != 0)
        rows[0][j] -= 1
    if drop is not None:
        if drop not in roots:
            fail("C", "dropped_factor_is_not_a_root", "c=%d" % drop)
        roots = [c for c in roots if c != drop]
    if add is not None:
        if add in roots:
            fail("C", "added_factor_is_already_a_root", "c=%d" % add)
        roots = sorted(roots + [add])
    e = [sorted(row.items()) for row in rows]
    traces = check_annihilator(e, roots)
    if alter or drop is not None:
        fail("C", "red_control_did_not_go_red")
    emit("ELECTRIC_C", "builder=gpt6_2x2_from_permutations.py", "operator_sha256=" + model["operator_sha"],
         "pin=MATCH", "dim=%d" % n, "nnz=%d" % nnz, "graph_same_as_path_B=1")
    emit("ELECTRIC_C", "P_roots=" + ",".join(map(str, roots)), "degree=%d" % len(roots), "P(E)=0",
         "basis_vectors_checked=%d" % n, "nonzero_entries=0", "exact=1")
    for c in roots:
        witness = factor_witness(e, roots, c)
        if witness is None:
            fail("C", "factor_not_needed", "c=%d" % c)
        emit("ELECTRIC_C_WITNESS", "c=%d" % c, "P_over_x_minus_c_at_E=NONZERO", "basis=%d" % witness[0],
             "row=%d" % witness[1], "value=%d" % witness[2])
    if add is not None:
        fail("C", "red_control_did_not_go_red")
    emit("ELECTRIC_C", "minimal_polynomial=P", "factors_each_needed=%d/%d" % (len(roots), len(roots)),
         "so=every_listed_cost_is_an_eigenvalue")
    trace1 = sum(row.get(i, 0) for i, row in enumerate(rows))
    trace2 = sum(x * rows[j].get(i, 0) for i, row in enumerate(rows) for j, x in row.items())
    sum1 = sum(c * table[c] for c in roots)
    sum2 = sum(c * c * table[c] for c in roots)
    if trace1 != sum1 or trace2 != sum2:
        fail("C", "trace_closure", "trace_E=%d" % trace1, "sum_c_m=%d" % sum1, "trace_E2=%d" % trace2, "sum_c2_m=%d" % sum2)
    emit("ELECTRIC_C", "trace_E=%d" % trace1, "sum_c_m=%d" % sum1, "trace_E2=%d" % trace2, "sum_c2_m=%d" % sum2,
         "closure=EXACT")
    for k, value in enumerate(traces):
        emit("ELECTRIC_C_PREFIX", "k=%d" % k, "trace_of_prefix_product=%d" % value)
    read_back = multiplicities_from_prefix_traces(roots, traces)
    character = {c: table[c] for c in roots}
    if read_back != character:
        fail("C", "prefix_traces_differ_from_characters", "read_back=" + table_text(read_back))
    emit("ELECTRIC_C", "multiplicities_read_back_from_the_matrix=" + table_text(read_back),
         "equal_to_character_table=1")
    check_wilson_loops(model, rows)
    check_link_operators(model, rows)
    check_reflection(model, rows)
    emit("ELECTRIC_C", "result=PASS", "gap_E_from_P=%d" % roots[1], "m0=%d" % read_back[0],
         "m_at_gap=%d" % read_back[roots[1]], "exact=1")


# ---------------------------------------------------------------- the operator inside the every-ratio bound


def same_operator():
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    model = load_gpt6_model()
    path = os.path.join(HERE, "seat_global_coupling.py")
    with redirect_stdout(StringIO()):
        theorem = runpy.run_path(path)
    rows, weights, mag = theorem["rows"], theorem["weights"], theorem["mag"]
    n = len(rows)
    different = sum(1 for a, b in zip(rows, model["rows"]) if a != b)
    if n != 1393 or len(model["rows"]) != n or different:
        fail("SAME", "rows_differ", "different=%d" % different)
    if list(weights) != list(model["W"]) or list(mag) != list(model["mag"]):
        fail("SAME", "weights_or_magnetic_differ")
    if any(rows[i].get(i, 0) != 24 for i in range(n)):
        fail("SAME", "diagonal_not_24")
    if theorem["diameter"] != 8:
        fail("SAME", "diameter", "diameter=%d" % theorem["diameter"])
    ratio = theorem["Q"]
    checks = ((0, 24), (1, 36), (2, 48), (10, 144))
    for r, base in checks:
        if theorem["lower_all_r"](ratio(r)) != ratio(6, base ** 16):
            fail("SAME", "bound_constant", "r=%d" % r)
    emit("ELECTRIC_SAME", "script=seat_global_coupling.py", "rows_equal=%d/%d" % (n - different, n),
         "weights_equal=1", "magnetic_equal=1", "every_diagonal=24", "diameter=%d" % theorem["diameter"],
         "normalisation=E=sum_links(3-sum_t_R_t)", "result=PASS")
    emit("ELECTRIC_SAME", "bound_checked_at_r=" + ",".join(str(r) for r, _ in checks),
         "bound=6/(24+12*r)^16", "exact=1", "result=PASS")


# ---------------------------------------------------------------- path F, the conclusion from pinned rows


def read_rows(path):
    with open(path, encoding="utf-8", newline="") as handle:
        return [line.rstrip("\r\n") for line in handle if line.strip()]


def holds(lines, *needles):
    return any(all(needle in line for needle in needles) for line in lines)


def sturm_row(t, negative, counts=None):
    needles = ["GPT6_STURM|JE=1|JB=0|threshold=%d/1000|" % t, "|pivots=1393|negative=%d|" % negative, "|ambiguous=0|"]
    if counts:
        needles.append("|counts=%s|" % counts)
    return needles


def row_cells(line):
    return dict(p.split("=", 1) for p in line.split("|")[1:] if "=" in p)


def check_every_gap(lines):
    """Every certified count equals the cumulative table, and each gap between consecutive costs has a certified T."""
    table = {}
    for line in lines:
        if line.startswith("ELECTRIC_B_M|L=2x2|"):
            cells = row_cells(line)
            table[int(cells["cost"])] = int(cells["m"])
    if sum(table.values()) != 1393:
        fail("F", "table_total", "total=%d" % sum(table.values()))
    costs = sorted(c for c in table if table[c])
    gaps, reads = set(), 0
    for line in lines:
        if line.startswith("GPT6_STURM|JE=1|JB=0|threshold="):
            cells = row_cells(line)
            t = int(cells["threshold"].split("/")[0])
            below = sum(table[c] for c in costs if c * 1000 < t)
            if int(cells["negative"]) != below or sum(int(x) for x in cells["counts"].split(",")) != below:
                fail("F", "count_differs_from_the_table", "T=%d" % t, "count=" + cells["negative"], "table=%d" % below)
            if any(c * 1000 == t for c in costs):
                fail("F", "certified_row_on_an_eigenvalue", "T=%d" % t)
            gaps.add(sum(1 for c in costs if c * 1000 < t))
            reads += 1
    if gaps != set(range(1, len(costs) + 1)):
        fail("F", "a_gap_has_no_certified_T", "gaps=%d" % len(gaps))
    return ("step=6", "from=every_GPT6_STURM_row_and_the_table_of_path_B", "gaps_between_costs_and_above_the_top=%d" % len(costs),
            "gaps_with_a_certified_T=%d/%d" % (len(gaps), len(costs)), "counts_equal_to_the_cumulative_table=%d/%d" % (reads, reads), "tag=MEASURED")


def path_f(measure):
    lines = read_rows(measure)
    required = {
        "A_cubic": ["ELECTRIC_A|cubic=A(A-3)(A-6)|value=0|"],
        "A_ranks": ["ELECTRIC_A|rank_A=5|rank_A_minus_3=2|rank_A_minus_6=5|multiplicities=0x1,3x4,6x1|"],
        "C_links": ["ELECTRIC_C_LINKS|", "commuting_pairs=28/28", "cubic_x(x-3)(x-6)=8/8", "result=PASS"],
        "D_1700": sturm_row(1700, 1),
        "D_4700": sturm_row(4700, 1, "1,0,0,0"),
        "D_5999": sturm_row(5999, 1, "1,0,0,0"),
        "D_6000": ["ELECTRIC_D_SINGULAR|T=6000|", "sturm_rows=0"],
        "D_6001": sturm_row(6001, 5, "3,1,1,0"),
        "D_7700": sturm_row(7700, 5, "3,1,1,0"),
        "E_5999": ["INDEP_COUNT|L=2x2|r=0|t_milli=5999000|N=1|", "result=COMPUTED"],
        "E_7700": ["INDEP_COUNT|L=2x2|r=0|t_milli=7700000|N=5|", "result=COMPUTED"],
        "E_build": ["INDEP_BUILD|L=2x2|gauge_orbits=1393|burnside=1393|"],
        "E_code": ["INDEP_RUN|code_sha256=" + INDEP_CODE_PIN + "|"],
        "E_engine": ["ELECTRIC_ENGINE|file=native/ym/independent/indep_verify.py|sha256=" + INDEP_CODE_PIN + "|"],
        "E_kernel": ["INDEP_RUN|", "|minor_kernel_sha256=" + INDEP_KERNEL_PIN + "|"],
        "E_kernel_source": ["ELECTRIC_E_RUN|exit=0|", "|kernel_source_blob=" + INDEP_KERNEL_SOURCE_BLOB + "|"],
        "C_P": ["ELECTRIC_C|P_roots=0,6,", "|P(E)=0|basis_vectors_checked=1393|nonzero_entries=0|"],
        "C_result": ["ELECTRIC_C|result=PASS|gap_E_from_P=6|m0=1|m_at_gap=4|"],
        "C_loops": ["ELECTRIC_C_LOOPS|", "|rank=4|", "with_the_constant=3,1,1,0", "result=PASS"],
        "same_rows": ["ELECTRIC_SAME|", "rows_equal=1393/1393", "every_diagonal=24", "result=PASS"],
        "same_bound": ["ELECTRIC_SAME|bound_checked_at_r=", "result=PASS"],
    }
    for name, needles in required.items():
        if not holds(lines, *needles):
            fail("F", "missing_or_changed_row", "row=" + name)
    every_gap = check_every_gap(lines)
    emit("ELECTRIC_F", "step=1", "from=path_A_and_ELECTRIC_C_LINKS",
         "says=E_is_a_sum_of_8_commuting_link_operators_each_annihilated_by_x(x-3)(x-6)",
         "so=spectrum_of_E_in_3Z_intersect_[0,48]", "tag=DERIVED")
    emit("ELECTRIC_F", "step=2", "from=D_T=1700,4700,5999_and_E_t_milli=5999000", "count_below=1",
         "says=the_constant_is_in_the_kernel_since_every_row_sums_to_0_and_it_is_the_one_eigenvalue_below_T",
         "so=0_is_simple_and_3_is_absent", "tag=DERIVED")
    emit("ELECTRIC_F", "step=3", "from=D_T=6001,7700_and_E_t_milli=7700000", "count_below=5", "sectors=3,1,1,0",
         "says=4_eigenvalues_lie_at_or_above_T=5999_and_below_T=6001_and_step_1_leaves_only_6_there",
         "so=m6=4", "tag=DERIVED")
    emit("ELECTRIC_F", "step=4", "conclusion=gap(E)=6_exactly", "0_multiplicity=1", "6_multiplicity=4",
         "engines=gpt6_sturm_interval_four_sectors,indep_verify_full_space_rust_minors", "tag=DERIVED")
    emit("ELECTRIC_F", "step=5", "from=path_B_and_path_C", "says=P(E)=0_with_roots_from_the_characters_and_P_minimal",
         "so=the_same_conclusion_with_no_inertia_engine", "tag=DERIVED")
    emit("ELECTRIC_F", *every_gap)
    emit("ELECTRIC_F", "step=7", "from=ELECTRIC_SAME", "says=seat_global_coupling.py_uses_this_same_matrix_in_this_normalisation",
         "bound=gap(JE*E+JB*M)>=6*JE/(24+12*JB/JE)^16", "domain=JE>0,JB>=0", "scope=the_1393_state_periodic_2x2_S3_torus",
         "antecedent=gap(E)=6_now_counted_here", "tag=DERIVED")
    emit("ELECTRIC_F", "result=PASS", "scope=finite_periodic_2x2_S3_torus", "larger_lattices=OPEN", "continuum=OPEN")


# ---------------------------------------------------------------- predictions against rows

# Each row: first the head, which names the receipt row up to its value, then what that row must hold.
PREDICTION_NEEDLES = {
    "A1": ("ELECTRIC_A|cubic=", "ELECTRIC_A|cubic=A(A-3)(A-6)|value=0|exact=1|"),
    "A2": ("ELECTRIC_A|rank_A=", "|multiplicities=0x1,3x4,6x1|"),
    "A3": ("ELECTRIC_A|rank_A=", "ELECTRIC_A|rank_A=5|rank_A_minus_3=2|rank_A_minus_6=5|"),
    "B1": ("ELECTRIC_B_M|L=2x2|cost=0|m=", "ELECTRIC_B_M|L=2x2|cost=0|m=1|"),
    "B2": ("ELECTRIC_B_M|L=2x2|cost=3|m=", "ELECTRIC_B_M|L=2x2|cost=3|m=0|"),
    "B3": ("ELECTRIC_B_M|L=2x2|cost=6|m=", "ELECTRIC_B_M|L=2x2|cost=6|m=4|"),
    "B4": ("ELECTRIC_B_M|L=2x2|cost=9|m=", "ELECTRIC_B_M|L=2x2|cost=9|m=0|"),
    "B5": ("ELECTRIC_B|L=2x2|", "|sum_m=1393|burnside=1393|"),
    "B7": ("ELECTRIC_B|L=2x2|", "|reflection_m[c]=m[48-c]=1|"),
    "B8": ("ELECTRIC_B|L=2x3|", "|sum_m=47449|burnside=47449|"),
    "B9": ("ELECTRIC_B|L=2x3|", "|smallest_nonzero_cost=6|"),
    "B11": ("ELECTRIC_B_FORMULA|", "|formula=gap(E)=3*min(4,Lx,Ly)|", "|tested_on=2x2,2x3|"),
    "C1": ("ELECTRIC_C|builder=", "ELECTRIC_C|builder=gpt6_2x2_from_permutations.py|operator_sha256=" + OPERATOR_PIN + "|pin=MATCH|"),
    "C2": ("ELECTRIC_C|P_roots=", "|P(E)=0|basis_vectors_checked=1393|nonzero_entries=0|"),
    "C3": ("ELECTRIC_C|minimal_polynomial=", "ELECTRIC_C|minimal_polynomial=P|factors_each_needed=13/13|"),
    "C4": ("ELECTRIC_C|P_roots=", "ELECTRIC_C|P_roots=0,6,12,15,18,21,24,27,30,33,36,42,48|degree=13|"),
    "C5": ("ELECTRIC_C|trace_E=", "|trace_E=33432|sum_c_m=33432|"),
    "C6": ("ELECTRIC_C|trace_E=", "|trace_E2=838512|sum_c2_m=838512|"),
    "C7": ("ELECTRIC_C|multiplicities_read_back_from_the_matrix=", "|equal_to_character_table=1|"),
    "C8": ("ELECTRIC_C_LOOPS|", "|eigenvalue=6|", "|rank=4|"),
    "C9": ("ELECTRIC_C_LINKS|", "sum_equals_E_rows=1393/1393", "commuting_pairs=28/28", "cubic_x(x-3)(x-6)=8/8"),
    "D4": ("ELECTRIC_D_SINGULAR|T=6000|", "|sturm_rows=0|", "|exit=1|", "no_sign-definite_pivot"),
    "F1": ("ELECTRIC_F|step=4|", "ELECTRIC_F|step=4|conclusion=gap(E)=6_exactly|0_multiplicity=1|6_multiplicity=4|"),
    "F2": ("ELECTRIC_SAME|script=", "rows_equal=1393/1393", "every_diagonal=24"),
}
# A row with this head reads MISS for the prediction: D4 predicts that T = 6000 leaves no certified row.
PREDICTION_CONTRADICTED_BY = {"D4": "GPT6_STURM|JE=1|JB=0|threshold=6000/1000|"}
FULL_TABLE = {"B6": ("2x2", "0:1,6:4,12:34,15:40,18:176,21:192,24:499,27:192,30:176,33:40,36:34,42:4,48:1")}
LOW_TABLE = {"B10": ("2x3", ((0, 1), (3, 0), (6, 3), (9, 2), (72, 1)))}
NO_ROW = "NOT_MEASURED|reason=NO_ROW"


def rows_with_head(lines, head):
    return [line for line in lines if line.startswith(head)]


def every_row_holds(rows, *needles):
    return all(needle in row for row in rows for needle in needles)


def needle_verdict(pid, lines):
    """MET when every row with the head holds the needles, MISS when one with the head differs, NO_ROW when none has it."""
    head, *needles = PREDICTION_NEEDLES[pid]
    contradiction = PREDICTION_CONTRADICTED_BY.get(pid)
    if contradiction and any(line.startswith(contradiction) for line in lines):
        return "MISS"
    rows = rows_with_head(lines, head)
    if not rows:
        return NO_ROW
    return "MET" if every_row_holds(rows, *needles) else "MISS"


def table_verdict(label, listed, closed, lines):
    """MISS when a row of the table reads another m than the list gives its cost, where a closed list gives every other
    cost m = 0. Then NO_ROW when a listed cost has no row, and MET when each listed cost has one."""
    rows = [row_cells(line) for line in rows_with_head(lines, "ELECTRIC_B_M|L=%s|cost=" % label)]
    for cell in rows:
        if cell.get("m") != listed.get(cell["cost"], "0" if closed else cell.get("m")):
            return "MISS"
    return NO_ROW if set(listed) - {cell["cost"] for cell in rows} else "MET"


def verdict_for(fields, lines):
    pid = fields["id"]
    if pid in FULL_TABLE:
        label, text = FULL_TABLE[pid]
        return table_verdict(label, dict(piece.split(":") for piece in text.split(",")), True, lines)
    if pid in LOW_TABLE:
        label, pairs = LOW_TABLE[pid]
        return table_verdict(label, {str(c): str(m) for c, m in pairs}, False, lines)
    if pid in PREDICTION_NEEDLES:
        return needle_verdict(pid, lines)
    if fields.get("path") == "D" and "T" in fields:
        t = fields["T"]
        rows = rows_with_head(lines, "GPT6_STURM|JE=1|JB=0|threshold=%s/1000|" % t)
        if not rows:
            if holds(lines, "ELECTRIC_D_UNCERTIFIED|T=%s|" % t):
                return "NOT_MEASURED|reason=ENGINE_UNCERTIFIED_AT_THIS_T"
            return NO_ROW
        needles = ["|negative=%s|" % fields["negative"]]
        if "counts" in fields:
            needles.append("|counts=%s|" % fields["counts"])
        return "MET" if every_row_holds(rows, *needles) else "MISS"
    if fields.get("path") == "E":
        runs = rows_with_head(lines, "INDEP_COUNT|L=2x2|r=0|t_milli=%s|" % fields["t_milli"])
        builds = rows_with_head(lines, "INDEP_BUILD|L=2x2|")
        if not every_row_holds(runs, "|N=%s|" % fields["N"], "|result=COMPUTED|"):
            return "MISS"
        if not every_row_holds(builds, "|gauge_orbits=%s|" % fields["gauge_orbits"]):
            return "MISS"
        return "MET" if runs and builds else NO_ROW
    return "NOT_MEASURED|reason=NO_CHECK_FOR_THIS_ID"


def sturm_readings(lines, t):
    """Each certified row at T as (negative, sector counts), in receipt order."""
    readings = []
    for line in rows_with_head(lines, "GPT6_STURM|JE=1|JB=0|threshold=%d/1000|" % t):
        cells = row_cells(line)
        readings.append((int(cells["negative"]), tuple(int(x) for x in cells["counts"].split(","))))
    return readings


def certified_in_interval(lines, interval):
    """The sector counts of every certified row with T strictly inside the open interval, in receipt order."""
    low, high = (int(x) * 1000 for x in interval.split(","))
    found = []
    for line in rows_with_head(lines, "GPT6_STURM|JE=1|JB=0|threshold="):
        cells = row_cells(line)
        if low < int(cells["threshold"].split("/")[0]) < high:
            found.append(tuple(int(x) for x in cells["counts"].split(",")))
    return found


def stopped_in_interval(lines, interval):
    """Whether a stopped run has its T strictly inside the open interval."""
    low, high = (int(x) * 1000 for x in interval.split(","))
    return any(low < int(row_cells(line)["T"]) < high for line in rows_with_head(lines, "ELECTRIC_D_UNCERTIFIED|T="))


def retry_checks(retry_file, lines, counts):
    for line in read_rows(retry_file):
        if not line.startswith("RETRY_PREDICT|"):
            continue
        fields = dict(p.split("=", 1) for p in line.split("|")[1:] if "=" in p)
        pid = fields["id"]
        if "open_interval" in fields:
            attempts = [int(t) for t in fields["T_list"].split(",")]
            rows = certified_rows(lines, attempts)
            stopped = sum(1 for t in attempts if holds(lines, "ELECTRIC_D_UNCERTIFIED|T=%d|" % t))
            if not rows:
                verdict = "NOT_MEASURED|reason=ENGINE_UNCERTIFIED_AT_EVERY_T_TRIED" if stopped else NO_ROW
                extra = ["uncertified_attempts=%d" % stopped]
            else:
                wrong = [row for row in rows if row[1][0] != int(fields["negative"]) or ("pp" in fields and row[1][1][0] != int(fields["pp"]))]
                verdict = "MISS" if wrong else "MET"
                shown = (wrong or rows)[0]
                extra = ["certified_T=%d" % shown[0], "negative=%d" % shown[1][0],
                         "counts=" + ",".join(map(str, shown[1][1])), "uncertified_attempts=%d" % stopped]
            counts[verdict.split("|")[0]] += 1
            emit("PREDICTION_CHECK", "id=" + pid, "path=D", "source=retry", "open_interval=" + fields["open_interval"],
                 "verdict=" + verdict, *extra)
        else:
            low, high = fields["pair"].split("_with_")
            below, above = certified_in_interval(lines, low), certified_in_interval(lines, high)
            if below and above:
                totals = [tuple(a + b for a, b in zip(x, y)) for x in below for y in above]
                wrong = [total for total in totals if total != (385, 336, 336, 336)]
                verdict = "MISS" if wrong else "MET"
                extra = ["sum=" + ",".join(map(str, (wrong or totals)[0]))]
            elif (below or stopped_in_interval(lines, low)) and (above or stopped_in_interval(lines, high)):
                verdict, extra = "NOT_MEASURED|reason=A_SIDE_OF_THE_PAIR_IS_UNCERTIFIED", []
            else:
                verdict, extra = NO_ROW, []
            counts[verdict.split("|")[0]] += 1
            emit("PREDICTION_CHECK", "id=" + pid, "path=D", "source=retry", "pair=" + fields["pair"], "verdict=" + verdict, *extra)


def sector_rows(lines, t):
    """The sector counts certified at T, whole run or stopped run."""
    head = "ELECTRIC_D_SECTOR|T=%d|" % t
    out = {}
    for line in lines:
        if line.startswith(head):
            cells = dict(p.split("=", 1) for p in line.split("|")[1:] if "=" in p)
            out[cells["sector"]] = int(cells["negative"])
    return out


def mirror_pairs(lines):
    """Pairs T and 48000 - T: each sector certified on both sides adds to the sector size, and both sides stop alike."""
    sizes = {"pp": 385, "pm": 336, "mp": 336, "mm": 336}
    ran = set()
    for line in lines:
        if line.startswith("ELECTRIC_D_RUN|"):
            ran.add(int(line.split("|")[1].split("=")[1]))
    pairs, agree = 0, 0
    for t in sorted(ran):
        if t < 24000 and 48000 - t in ran:
            pairs += 1
            low, high = sector_rows(lines, t), sector_rows(lines, 48000 - t)
            alike = set(low) == set(high) and all(low[k] + high[k] == sizes[k] for k in low)
            agree += alike
    return pairs, agree


def certified_rows(lines, attempts):
    """Each certified row at the T listed, as (T, (negative, sector counts)), in the order of the list."""
    return [(t, reading) for t in attempts for reading in sturm_readings(lines, t)]


def retry2_verdict(rows, fields):
    """The verdict on certified rows against the predicted reading, with the fields of the first row that differs, or else of the first row."""
    predicted = int(fields["negative"]), tuple(int(x) for x in fields["counts"].split(","))
    wrong = [row for row in rows if row[1] != predicted]
    t, (negative, sectors) = (wrong or rows)[0]
    return "MISS" if wrong else "MET", ["certified_T=%d" % t, "negative=%d" % negative, "counts=" + ",".join(map(str, sectors))]


def retry2_checks(retry2_file, lines, counts):
    first = None
    for line in read_rows(retry2_file):
        if not line.startswith("RETRY2_PREDICT|"):
            continue
        fields = dict(p.split("=", 1) for p in line.split("|")[1:] if "=" in p)
        pid = fields["id"]
        extra = []
        if pid == "S1":
            attempts = [int(t) for t in fields["T_list"].split(",")]
            rows = certified_rows(lines, attempts)
            if not rows:
                stopped = any(holds(lines, "ELECTRIC_D_UNCERTIFIED|T=%d|" % t) for t in attempts)
                verdict = "NOT_MEASURED|reason=ENGINE_UNCERTIFIED_AT_EVERY_T_TRIED" if stopped else NO_ROW
            else:
                first = rows[0]
                verdict, extra = retry2_verdict(rows, fields)
        elif pid == "S2":
            mirror = certified_rows(lines, [48000 - first[0]]) if first else []
            if not mirror:
                verdict = "NOT_MEASURED|reason=NO_CERTIFIED_T_IN_S1_OR_NO_MIRROR_ROW"
            else:
                verdict, extra = retry2_verdict(mirror, fields)
        else:
            pairs, agree = mirror_pairs(lines)
            verdict = "MET" if pairs and pairs == agree else ("MISS" if pairs else "NOT_MEASURED|reason=NO_T_RUN_ON_BOTH_SIDES")
            extra = ["pairs=%d" % pairs, "agree=%d" % agree]
        counts[verdict.split("|")[0]] += 1
        emit("PREDICTION_CHECK", "id=" + pid, "path=D", "source=retry2", "verdict=" + verdict, *extra)


def predictions(prediction_file, retry_file, retry2_file, measure):
    lines = read_rows(measure)
    counts = {"MET": 0, "MISS": 0, "NOT_MEASURED": 0}
    for line in read_rows(prediction_file):
        if not line.startswith("PREDICT|"):
            continue
        fields = dict(p.split("=", 1) for p in line.split("|")[1:] if "=" in p)
        verdict = verdict_for(fields, lines)
        counts[verdict.split("|")[0]] += 1
        emit("PREDICTION_CHECK", "id=" + fields["id"], "path=" + fields["path"], "source=" + fields["source"], "verdict=" + verdict)
    retry_checks(retry_file, lines, counts)
    retry2_checks(retry2_file, lines, counts)
    emit("PREDICTION_SUMMARY", "rows=%d" % sum(counts.values()), "met=%d" % counts["MET"], "miss=%d" % counts["MISS"],
         "not_measured=%d" % counts["NOT_MEASURED"])


# ---------------------------------------------------------------- path G, the formula by the girth of the torus

FORMULA_CAP = 4
GIRTH_UP_TO = 12  # the girth is read on every torus with Lx, Ly up to this
ENUMERATED_UP_TO = 6  # every low-cost assignment is read on every torus with Lx, Ly up to this ...
ENUMERATED_ALSO = ((3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 8))  # ... and on these, the second seat's larger tori
SECOND_SEAT_LOGS = ("tables.log", "chars_full.log", "chars_low.log", "seven_tori_rerun.log")


def vertex_rule(characters):
    """dim Inv by k ends in tau and s ends in the sign. The rest of the 4 ends are trivial."""
    dims = {}
    for irreps, dim in invariant_table(characters).items():
        if dims.setdefault((irreps.count(2), irreps.count(1)), dim) != dim:
            fail("G", "dim_inv_differs_within_one_k_and_s", "irreps=%d,%d,%d,%d" % irreps)
    if any(dims[1, s] for s in range(4)):
        fail("G", "one_tau_end_has_an_invariant")
    if any(dims[0, s] for s in (1, 3)):
        fail("G", "odd_sign_ends_with_no_tau_have_an_invariant")
    if dims[0, 0] != 1 or dims[2, 0] != 1:
        fail("G", "a_vertex_off_or_on_a_tau_cycle_differs_from_1")
    return dims


def girth(links, vertices):
    """The shortest cycle of the multigraph: over all links, one more than the shortest path between its ends along the others."""
    around = [[] for _ in range(vertices)]
    for k, (a, b) in enumerate(links):
        around[a].append((b, k))
        around[b].append((a, k))
    best = len(links) + 1
    for k, (a, b) in enumerate(links):
        reached = {a: 0}
        frontier = [a]
        while frontier and b not in reached:
            following = []
            for u in frontier:
                for v, j in around[u]:
                    if j != k and v not in reached:
                        reached[v] = reached[u] + 1
                        following.append(v)
            frontier = following
        if b in reached:
            best = min(best, reached[b] + 1)
    return best


def low_cost_states(links, vertices, dims, top, cycle_size):
    """Reads every assignment of cost at most top, from the all-trivial one up, with dim Inv at every vertex. Returns the
    states by (sign links, tau links), the assignments read, and how many sets of cycle_size links have degree exactly 2
    at each vertex they touch."""
    states_by_labels = {}
    assignments, cycles = 0, 0
    for count in range(top // 3 + 1):
        for chosen in combinations(links, count):
            degree = {}
            for a, b in chosen:
                degree[a] = degree.get(a, 0) + 1
                degree[b] = degree.get(b, 0) + 1
            if count == cycle_size and all(d == 2 for d in degree.values()):
                cycles += 1
            untouched = dims[0, 0] ** (vertices - len(degree))
            for signs in range(count + 1):
                if 6 * signs + 3 * (count - signs) > top:
                    break
                for sign_positions in combinations(range(count), signs):
                    assignments += 1
                    sign_ends = {}
                    for position in sign_positions:
                        for end in chosen[position]:
                            sign_ends[end] = sign_ends.get(end, 0) + 1
                    states = untouched
                    for v, d in degree.items():
                        s = sign_ends.get(v, 0)
                        states *= dims[d - s, s]
                        if not states:
                            break
                    if states:
                        key = signs, count - signs
                        states_by_labels[key] = states_by_labels.get(key, 0) + states
    return states_by_labels, assignments, cycles


def torus_row(lx, ly, dims, cap):
    """The formula on one torus: every assignment up to the predicted gap, read against the girth."""
    label = "%dx%d" % (lx, ly)
    links = torus_links(lx, ly)
    value = girth(links, lx * ly)
    formula = 3 * min(cap, lx, ly)
    if 3 * value != formula:
        fail("G", "girth_differs_from_the_formula", "L=" + label, "girth=%d" % value, "formula=%d" % formula)
    labels, assignments, cycles = low_cost_states(links, lx * ly, dims, formula, value)
    by_cost = {}
    for (signs, taus), states in labels.items():
        by_cost[6 * signs + 3 * taus] = by_cost.get(6 * signs + 3 * taus, 0) + states
    if by_cost.get(0) != 1:
        fail("G", "zero_is_not_simple", "L=" + label)
    below = sum(states for cost, states in by_cost.items() if 0 < cost < formula)
    if below:
        fail("G", "states_below_the_formula", "L=" + label, "states=%d" % below, "formula=%d" % formula)
    at_gap = by_cost.get(formula, 0)
    if not at_gap or at_gap != cycles:
        fail("G", "m_at_gap_differs_from_the_shortest_cycles", "L=" + label, "m=%d" % at_gap, "cycles=%d" % cycles)
    emit("ELECTRIC_G_TORUS", "L=" + label, "links=%d" % len(links), "girth=%d" % value, "assignments_read=%d" % assignments,
         "states_below_the_gap=0", "smallest_nonzero_cost=%d" % formula, "m_at_gap=%d" % at_gap, "shortest_cycles=%d" % cycles,
         "formula_3min(4,Lx,Ly)=%d" % formula, "result=PASS")
    return label, at_gap


def second_seat_rows(folder, enumerated):
    """Each torus in the second seat's logs, read against the formula and against this path's own count."""
    tori = {}
    for name in SECOND_SEAT_LOGS:
        for line in read_rows(os.path.join(folder, name)):
            if not line.startswith(("OWN_TABLE|", "OWN_LOW|")):
                continue
            cells = row_cells(line)
            full = line.startswith("OWN_TABLE|")
            if cells["L"] in tori and (tori[cells["L"]][0] or not full):
                continue
            if full:
                if cells["closure"] != "1" or cells["reflection"] != "1":
                    fail("G", "second_seat_closure", "L=" + cells["L"])
                at_gap = int(cells["m_at_it"])
            else:
                table = dict(piece.split(":") for piece in cells["table"].split(","))
                at_gap = int(table[cells["smallest_nonzero_cost"]])
            tori[cells["L"]] = full, name, int(cells["smallest_nonzero_cost"]), at_gap
    agree = 0
    for label in sorted(tori, key=lambda text: tuple(int(x) for x in text.split("x"))):
        full, name, smallest, at_gap = tori[label]
        lx, ly = (int(x) for x in label.split("x"))
        if smallest != 3 * min(FORMULA_CAP, lx, ly):
            fail("G", "second_seat_differs_from_the_formula", "L=" + label, "smallest=%d" % smallest)
        if label in enumerated:
            if enumerated[label] != at_gap:
                fail("G", "second_seat_differs_from_this_count", "L=" + label, "m=%d" % at_gap, "here=%d" % enumerated[label])
            agree += 1
        emit("ELECTRIC_G_SECOND_SEAT", "L=" + label, "table=" + ("full_with_burnside_and_reflection" if full else "truncated_at_cost_15"),
             "log=" + name, "smallest_nonzero_cost=%d" % smallest, "m_at_it=%d" % at_gap,
             "formula_3min(4,Lx,Ly)=%d" % (3 * min(FORMULA_CAP, lx, ly)), "result=PASS")
    fulls = sum(1 for full, _, _, _ in tori.values() if full)
    rerun = sum(1 for _, name, _, _ in tori.values() if name == "seven_tori_rerun.log")
    emit("ELECTRIC_G_SECOND_SEAT_SUMMARY", "tori=%d" % len(tori), "full=%d" % fulls, "truncated=%d" % (len(tori) - fulls),
         "holding_the_formula=%d/%d" % (len(tori), len(tori)), "m_at_it_equal_to_ELECTRIC_G_TORUS=%d/%d" % (agree, len(tori)),
         "rows_from_the_second_seats_logs=%d" % (len(tori) - rerun), "rows_from_a_rerun_of_its_script=%d" % rerun)


def path_g(folder, characters, cap, altered_dims=(), first_side=1):
    dims = vertex_rule(characters)
    emit("ELECTRIC_G_VERTEX", "tuples=81", "dim_inv_by_k_tau_ends_s_sign_ends=" + ",".join("k%ds%d:%d" % (k, s, dims[k, s]) for k, s in sorted(dims)),
         "one_tau_end=0", "odd_sign_ends_with_no_tau=0", "result=PASS")
    dims.update(altered_dims)
    checked = 0
    for lx in range(1, GIRTH_UP_TO + 1):
        for ly in range(1, GIRTH_UP_TO + 1):
            value = girth(torus_links(lx, ly), lx * ly)
            if value != min(cap, lx, ly):
                fail("G", "girth_differs_from_the_formula", "L=%dx%d" % (lx, ly), "girth=%d" % value, "min=%d" % min(cap, lx, ly))
            checked += 1
    emit("ELECTRIC_G_GIRTH", "Lx=1..%d" % GIRTH_UP_TO, "Ly=1..%d" % GIRTH_UP_TO, "method=each_link_removed_then_shortest_path_between_its_ends",
         "girth_equal_to_min(4,Lx,Ly)=%d/%d" % (checked, checked), "result=PASS")
    sides = range(first_side, ENUMERATED_UP_TO + 1)
    tori = [(lx, ly) for lx in sides for ly in sides] + list(ENUMERATED_ALSO)
    enumerated = dict(torus_row(lx, ly, dims, cap) for lx, ly in tori)
    labels, _, _ = low_cost_states(torus_links(2, 2), 4, dims, 12, 0)
    split = {key: labels.get(key, 0) for key in ((2, 0), (1, 2), (0, 4))}
    if sum(split.values()) != 34:
        fail("G", "split_at_cost_12_differs_from_34", "states=%d" % sum(split.values()))
    emit("ELECTRIC_G_SPLIT", "L=2x2", "cost=12", "sign_links=2_tau_links=0_states=%d" % split[2, 0],
         "sign_links=1_tau_links=2_states=%d" % split[1, 2], "sign_links=0_tau_links=4_states=%d" % split[0, 4], "sum=34")
    if folder:
        second_seat_rows(folder, enumerated)
    emit("ELECTRIC_G_STEP", "step=1", "from=ELECTRIC_G_VERTEX", "says=the_nontrivial_links_S_of_an_assignment_with_states_have_degree_at_least_2_at_each_vertex_they_touch",
         "so=a_nonempty_S_holds_a_cycle_and_S_has_at_least_girth_links", "tag=DERIVED")
    emit("ELECTRIC_G_STEP", "step=2", "says=each_nontrivial_link_costs_at_least_3", "so=every_nonzero_cost_is_at_least_3*girth", "tag=DERIVED")
    emit("ELECTRIC_G_STEP", "step=3", "says=tau_on_a_shortest_cycle_has_k=2_at_its_vertices_and_one_state", "so=cost_3*girth_is_an_eigenvalue", "tag=DERIVED")
    emit("ELECTRIC_G_STEP", "step=4", "from=ELECTRIC_G_GIRTH", "says=the_girth_of_the_torus_multigraph_is_min(4,Lx,Ly)",
         "by=a_loop_at_min_1,a_parallel_pair_at_min_2,a_line_at_min_3,a_plaquette_at_min_at_least_4_where_a_cycle_of_3_would_need_an_even_count_of_steps", "tag=DERIVED")
    emit("ELECTRIC_G_STEP", "step=5", "says=at_cost_3*girth_S_is_all_tau_on_one_shortest_cycle", "so=m_at_gap=the_number_of_shortest_cycles", "tag=DERIVED")
    emit("ELECTRIC_G_RETAG", "formula=gap(E)=3*min(4,Lx,Ly)", "date=2026-11-03", "was=CONJECTURE", "now=DERIVED", "scope=every_periodic_S3_torus_with_Lx,Ly>=1",
         "kept_as_pinned=ELECTRIC_B_FORMULA,prediction_B11", "result=PASS")


# ---------------------------------------------------------------- command line


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    mode, rest = argv[0], argv[1:]
    if mode == "a" and rest in ([], ["--alter-entry"]):
        path_a(bool(rest))
    elif mode == "b" and rest in ([], ["--bad-character"]):
        path_b(bool(rest))
    elif mode == "c" and rest == []:
        path_c(False, None)
    elif mode == "c" and rest == ["--alter-entry"]:
        path_c(True, None)
    elif mode == "c" and len(rest) == 2 and rest[0] == "--drop-factor":
        path_c(False, int(rest[1]))
    elif mode == "c" and len(rest) == 2 and rest[0] == "--add-factor":
        path_c(False, None, int(rest[1]))
    elif mode == "same" and rest == []:
        same_operator()
    elif mode == "f" and len(rest) == 1:
        path_f(rest[0])
    elif mode == "g" and rest == ["--bad-character"]:
        path_g(None, (CHARACTERS[0], CHARACTERS[1], (2, 0, 1)), FORMULA_CAP)
    elif mode == "g" and rest == ["--permutation-character"]:
        path_g(None, (CHARACTERS[0], CHARACTERS[1], (3, 1, 0)), FORMULA_CAP)
    elif mode == "g" and len(rest) == 2 and rest[0] == "--cap":
        path_g(None, CHARACTERS, int(rest[1]))
    elif mode == "g" and rest == ["--alter-vertex"]:
        path_g(None, CHARACTERS, FORMULA_CAP, {(1, 0): 1})
    elif mode == "g" and rest == ["--alter-vertex-from-2x2"]:
        path_g(None, CHARACTERS, FORMULA_CAP, {(1, 0): 1}, 2)
    elif mode == "g" and rest == ["--alter-empty-vertex"]:
        path_g(None, CHARACTERS, FORMULA_CAP, {(0, 0): 2})
    elif mode == "g" and len(rest) <= 1:
        path_g(rest[0] if rest else None, CHARACTERS, FORMULA_CAP)
    elif mode == "predictions" and len(rest) == 4:
        predictions(rest[0], rest[1], rest[2], rest[3])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
