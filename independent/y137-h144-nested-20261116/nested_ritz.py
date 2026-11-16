#!/usr/bin/env python3
"""#137 exact nested 12/24/48/96/144-dimensional 3x4 S3 Ritz pencils.

The old 12-dimensional physical W-Galerkin basis is retained EXACTLY.
New coordinates are canonical Q orbit indicators, greedily source-scored and
pairwise non-adjacent in the verified K2 weighted graph. Consequently their
offdiagonal H block is identically zero, so all below-72 inertia counts reduce
by exact block elimination to a 12x12 integer symmetric Schur form.

The experiment computes exact projected H and G, full matrices and SHA, exact
strict-rank certificates and all first-two Ritz brackets. Full-space residual
and Wilson spectral weight are separate gates; never infer them from Ritz alone.
"""
import hashlib
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
H12_PATH = os.path.join(ROOT, "independent",
                        "y137-12x12-krylov-20261116", "exact_krylov_12.py")
H12_RESULT = os.path.join(ROOT, "independent",
                          "y137-12x12-krylov-20261116", "RESULT-H12-20261116.hbp")
H12_CODE_BLOB = "2bb1c89a53b701e5d3e6b369662a10effcc7e9dc"
H12_RESULT_BLOB = "9876d083ecdbd91f81ddbd99ea311467d81a1ba7"
G12_SHA = "f77d8d060eb779574bb40d918e8886de333e0d0afdbdfba67639cb104fd4484f"
K12_SHA = "8abe46fc8d0ca1d9300ad1edb934ca0d92dae08bf7c933350abb208737cac50a"
DEN = 1000000000
SIZES = (12, 24, 48, 96, 144)
OLD_RITZ = ((69924680131, 69924680132),
            (69963663574, 69963663575))
ORIGINAL_SAMPLES = (69909875505, 69949729820)
DIM_BASE = 12
NF = 8
NQ = 4
TARGET = 144
RANK = TARGET - DIM_BASE


def need(condition, why):
    if not condition:
        print("Y137_H144_REFUSE|reason=" + why + "|json=0", flush=True)
        raise SystemExit(1)


def emit(tag, **kw):
    print(tag + "|" + "|".join(str(k) + "=" + str(v) for k, v in kw.items())
          + "|json=0", flush=True)


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii")
                        + b"\x00" + raw).hexdigest()


def sha(text):
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def matrix_sha(rows):
    return sha("|".join(str(x) for row in rows for x in row))


def load_h12():
    need(blob(open(H12_PATH, "rb").read()) == H12_CODE_BLOB,
         "original_H12_source_changed")
    need(blob(open(H12_RESULT, "rb").read()) == H12_RESULT_BLOB,
         "original_H12_result_changed")
    spec = importlib.util.spec_from_file_location("h12_original", H12_PATH)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    lines = open(H12_RESULT, encoding="ascii").read().splitlines()
    need(len(lines) == 8, "original_H12_receipt_length")
    x = lines[2]
    need(x.startswith("Y137_H12_MATRIX|"), "original_H12_matrix_row")
    data = dict(term.split("=", 1) for term in x.split("|")[1:]
                if "=" in term)
    def parse(value):
        return [[int(z) for z in line.split(",")]
                for line in value.split(";")]
    G, H = parse(data["gram"]), parse(data["hamiltonian"])
    need(len(G) == len(H) == DIM_BASE
         and all(len(row) == DIM_BASE for row in G + H),
         "original_H12_dimension")
    need(matrix_sha(G) == G12_SHA == data["gram_sha256"]
         and matrix_sha(H) == K12_SHA == data["hamiltonian_sha256"],
         "original_H12_matrix_hash")
    return old, G, H


def sources(old):
    v1, v2 = old.read_original_samples()
    mod = old.source_module()
    ball, magnetic = old.raw_graph(mod)
    # Recreate the exact original four nonflat Krylov columns.
    C = ball["C"]
    F = [[-sum(row[p] * v[p] for p in range(NF))
          if row is not None else 0 for row in C]
         for v in (v1, v2)]
    AF = [old.act(ball, x) for x in F]
    cols = F + AF
    actions = AF + [old.act(ball, x) for x in AF]
    gram, hamiltonian, census = old.exact_pencil(ball, (v1, v2), magnetic)
    need(matrix_sha(gram) == G12_SHA and
         matrix_sha(hamiltonian) == K12_SHA,
         "independent_rebuild_original_12")
    need(census["graph_unordered_weighted_pairs"] == 20736
         and census["K2_K3_exterior_edges"] == 500664
         and census["total_K2_selfloops"] == 0,
         "verified_original_K2_72_move_census")
    states, unused, sizes = mod.rebuild_states()
    need(sizes == [8, 264, 7770], "K2_canonical_layer_order")
    return ball, states, cols, actions


def select(ball, cols, actions):
    """Deterministic exact source-weighted, graph-independent Q orbit selection.

    Score weighs the original two Wilson first-step directions and the next
    two Krylov actions. The pairwise nonadjacency makes the coordinate block
    diagonal, allowing a rigorously controlled 12x12 effective Schur solve.
    """
    w = ball["wq"]
    n = ball["n"]
    rs, oj = ball["rs"], ball["oj"]
    scores = []
    for i in range(n):
        fst = cols[0][i] ** 2 + cols[1][i] ** 2
        nxt = cols[2][i] ** 2 + cols[3][i] ** 2
        score = w[i] * (144 * fst + nxt // (72 * 72))
        scores.append((score, i))
    scores.sort(key=lambda pair: (-pair[0], pair[1]))
    selected = []
    excluded = bytearray(n)
    for score, i in scores:
        if excluded[i]:
            continue
        selected.append(i)
        excluded[i] = 1
        for idx in range(rs[i], rs[i + 1]):
            excluded[oj[idx]] = 1
        if len(selected) == RANK:
            break
    need(len(selected) == RANK, "not_enough_pairwise_nonadjacent_Q_orbits")
    selected_set = set(selected)
    need(len(selected_set) == RANK, "selected_orbit_collision")
    for i in selected:
        need(all(oj[idx] not in selected_set
                 for idx in range(rs[i], rs[i + 1])),
             "new_coordinate_block_not_diagonal")
    return selected, scores


def expanded_matrices(ball, cols, actions, chosen, G12, K12):
    n = DIM_BASE + len(chosen)
    G = [[0] * n for unused in range(n)]
    K = [[0] * n for unused in range(n)]
    for i in range(DIM_BASE):
        G[i][:DIM_BASE] = G12[i][:]
        K[i][:DIM_BASE] = K12[i][:]
    w, C, diag = ball["wq"], ball["C"], ball["dbase"]
    rs, oj, oc = ball["rs"], ball["oj"], ball["oc"]
    for k, i in enumerate(chosen):
        t = DIM_BASE + k
        wi = w[i]
        G[t][t] = wi
        K[t][t] = wi * diag[i]
        ci = C[i]
        for p in range(NF):
            h = -wi * (0 if ci is None else ci[p])
            K[t][p] = K[p][t] = h
        for a in range(NQ):
            gi = wi * cols[a][i]
            ki = wi * actions[a][i]
            G[8+a][t] = G[t][8+a] = gi
            K[8+a][t] = K[t][8+a] = ki
            # Row/pair independent contraction: sum_j W_j*x_j*H_ji.
            reverse_sum = 0
            for pos in range(rs[i], rs[i + 1]):
                j = oj[pos]
                coeff_ij = oc[pos]
                # The source requires W_i c_ij == W_j c_ji.
                rb = dict(zip(oj[rs[j]:rs[j+1]], oc[rs[j]:rs[j+1]]))
                need(wi * coeff_ij == w[j] * rb.get(i, 0),
                     "independent_weighted_pair_balance")
                reverse_sum += w[j] * rb[i] * cols[a][j]
            alt = wi * diag[i] * cols[a][i] - reverse_sum
            need(ki == alt, "cross_core_orbit_row_pair_mismatch")
    need(all(G[i][j] == G[j][i] and K[i][j] == K[j][i]
             for i in range(n) for j in range(n)),
         "weighted_H_or_G_not_symmetric")
    need([row[:DIM_BASE] for row in G[:DIM_BASE]] == G12
         and [row[:DIM_BASE] for row in K[:DIM_BASE]] == K12,
         "original_12x12_principal_block_changed")
    for k, i in enumerate(chosen):
        for l, j in enumerate(chosen):
            if k != l:
                need(G[DIM_BASE+k][DIM_BASE+l] == 0
                     and K[DIM_BASE+k][DIM_BASE+l] == 0,
                     "coordinate_block_nonzero_offdiag")
    return G, K


def leading_bareiss_signs(a):
    """One fraction-free symmetric elimination, all leading Sylvester signs."""
    m = len(a)
    v = [row[:] for row in a]
    need(all(len(x) == m for x in v), "nonsquare_Schur")
    previous = 1
    sign_prev = 1
    negative = 0
    signs = []
    for k in range(m):
        pivot = v[k][k]
        need(pivot != 0, "singular_Sylvester_leading_pivot")
        sign = -1 if pivot < 0 else 1
        negative += int(sign != sign_prev)
        sign_prev = sign
        signs.append("-" if sign < 0 else "+")
        if k == m-1:
            break
        for i in range(k + 1, m):
            for j in range(i, m):
                numer = pivot * v[i][j] - v[i][k] * v[k][j]
                need(numer % previous == 0,
                     "nonintegral_Bareiss_symmetric_pivot")
                v[i][j] = numer // previous
                v[j][i] = v[i][j]
        for i in range(k + 1, m):
            v[i][k] = v[k][i] = 0
        previous = pivot
    return negative, "".join(signs)


def gram_rank(G, chosen, cols, ball):
    """Exact Schur 4x4 rank test for all newly added orbit indicators."""
    Q = [[G[8+i][8+j] for j in range(NQ)] for i in range(NQ)]
    for idx in chosen:
        wi = ball["wq"][idx]
        for i in range(NQ):
            xi = cols[i][idx]
            for j in range(NQ):
                Q[i][j] -= wi * xi * cols[j][idx]
    dets = [determinant([row[:k] for row in Q[:k]])
            for k in range(1, NQ+1)]
    need(all(x > 0 for x in dets), "Krylov_residual_rank_lost")
    return dets[-1], sha(",".join(str(d) for d in dets))


def determinant(a):
    """Independent 4x4 exact integer determinant for Gram rank."""
    n = len(a)
    v = [row[:] for row in a]
    prev = 1
    for k in range(n-1):
        pivot = v[k][k]
        need(pivot != 0, "rank_det_pivot_zero")
        for i in range(k+1, n):
            for j in range(k+1, n):
                num = pivot * v[i][j] - v[i][k] * v[k][j]
                need(num % prev == 0, "rank_det_numer_not_divisible")
                v[i][j] = num // prev
            v[i][k] = 0
        prev = pivot
    return v[-1][-1]


def group_schur(ball, cols, actions, chosen):
    """Aggregate exact 12x12 quadratic cross-action numerators by Q diagonal."""
    w, C = ball["wq"], ball["C"]
    groups = {}
    for idx in chosen:
        diag = ball["dbase"][idx]
        if diag not in groups:
            groups[diag] = ([[0]*DIM_BASE for unused in range(DIM_BASE)],
                            [[0]*DIM_BASE for unused in range(DIM_BASE)],
                            [[0]*DIM_BASE for unused in range(DIM_BASE)])
        HH, HB, BB = groups[diag]
        h = [-(0 if C[idx] is None else C[idx][p]) for p in range(NF)]
        h += [actions[a][idx] for a in range(NQ)]
        b = [0]*NF + [cols[a][idx] for a in range(NQ)]
        wi = w[idx]
        for a in range(DIM_BASE):
            if h[a] == 0 and b[a] == 0:
                continue
            for c in range(DIM_BASE):
                HH[a][c] += wi * h[a] * h[c]
                HB[a][c] += wi * (h[a] * b[c] + b[a] * h[c])
                BB[a][c] += wi * b[a] * b[c]
    return groups


def inertia_at(z, G12, K12, groups):
    """Exact below-72 full-n inertia through positive diagonal coords + 12 Schur."""
    need(0 <= z < 72*DEN, "Ritz_inertia_outside_0_to_72")
    prod = 1
    den = {}
    for diagonal in groups:
        d = DEN * diagonal - z
        need(d > 0, "coordinate_block_not_positive")
        den[diagonal] = d
        prod *= d
    S = [[prod*(DEN*K12[i][j]-z*G12[i][j])
          for j in range(DIM_BASE)] for i in range(DIM_BASE)]
    for diagonal, (HH, HB, BB) in groups.items():
        fac = prod//den[diagonal]
        for i in range(DIM_BASE):
            for j in range(DIM_BASE):
                S[i][j] -= fac * (DEN*DEN*HH[i][j]
                                  -DEN*z*HB[i][j]+z*z*BB[i][j])
    need(all(S[i][j] == S[j][i]
             for i in range(DIM_BASE) for j in range(DIM_BASE)),
         "Schur_not_symmetric")
    return leading_bareiss_signs(S)[0]


def exact_bracket(k, G12, K12, groups):
    """One-billionth strict upper interval for generalized k-th Ritz level."""
    lo, hi = 0, 72*DEN-1
    need(inertia_at(lo,G12,K12,groups) < k and
         inertia_at(hi,G12,K12,groups) >= k,
         "Ritz_not_bracketed_below_flat_energy")
    while hi-lo > 1:
        mid=(lo+hi)//2
        if inertia_at(mid,G12,K12,groups) >= k:
            hi=mid
        else:
            lo=mid
    need(inertia_at(lo,G12,K12,groups)==k-1
         and inertia_at(hi,G12,K12,groups)==k,
         "Ritz_final_exact_endpoint_disagreement")
    return lo,hi


def parse_csv(path):
    with open(path, encoding="ascii") as f:
        return [[int(x) for x in line.strip().split(",")]
                for line in f if line.strip()]


def write_csv(path, m):
    with open(path,"w",encoding="ascii") as f:
        for row in m:
            f.write(",".join(str(x) for x in row)+"\n")


def test_small():
    need(leading_bareiss_signs([[2,1],[1,2]]) == (0,"++"),
         "toy_positive_inertia")
    need(leading_bareiss_signs([[2,1],[1,-2]]) == (1,"+-"),
         "toy_indefinite_inertia")
    need(determinant([[2,1],[1,2]])==3,
         "toy_Bareiss")
    need(matrix_sha([[1,2],[3,4]]) ==
         sha("1|2|3|4"), "toy_sha")
    emit("Y137_H144_TOY", exact_integer_inertia="PASS",
         independent_rank_det="PASS", SOURCE="PINNED_H12",
         real_144="NOT_COMPUTED",Wilson_weight="HOLD")


def real():
    old,G12,K12=load_h12()
    ball,states,cols,actions=sources(old)
    chosen,scores=select(ball,cols,actions)
    addr_rows=[]
    for i in chosen:
        key=states[8+i]
        addr_rows.append(str(i)+"|"+str(ball["wq"][i])+"|"+
                         str(ball["dbase"][i])+"|"+
                         ",".join(str(x) for x in key))
    source_hash=sha("\n".join(addr_rows))
    emit("Y137_H144_SOURCE",model="3x4_S3_r9",
         original_H12_code_blob=H12_CODE_BLOB,
         original_H12_result_blob=H12_RESULT_BLOB,
         exact_K2_Q_rows=ball["n"],frozen_W="1,3,2,3,3,2,2,2",
         new_orbit_coordinates=RANK,
         no_mutual_selected_Q_edges="PASS",
         source_rank_selection="STRICT_EXACT_GREEDY",
         selected_canonical_address_sha256=source_hash,
         full_state_operator="K2_SOURCE_PLUS_K3_EXTERIOR_FOR_RESIDUAL",
         Wilson_weight="HOLD")
    out=os.path.join(ROOT,"build","y137-h144")
    os.makedirs(out,exist_ok=True)
    with open(os.path.join(out,"SELECTED-ORBIT-ADDRESSES.txt"),
              "w",encoding="ascii") as f:
        f.write("\n".join(addr_rows)+"\n")
    prev=None
    for dim in SIZES:
        take=chosen[:dim-DIM_BASE]
        G,K=expanded_matrices(ball,cols,actions,take,G12,K12)
        rank,ranksha=gram_rank(G,take,cols,ball)
        groups=group_schur(ball,cols,actions,take)
        for z in ORIGINAL_SAMPLES:
            assert inertia_at(z,G12,K12,groups) >= 0
        ritz=[exact_bracket(k,G12,K12,groups) for k in (1,2)]
        if dim == 12:
            need(ritz == list(OLD_RITZ),
                 "original_frozen_H12_Ritz_not_reproduced")
        if prev is not None:
            need(all(ritz[i][1] <= prev[i][1] for i in range(2)),
                 "monotone_minmax_upper_Ritz_failure")
        prev=ritz
        prefix=os.path.join(out,"H"+str(dim))
        write_csv(prefix+"-GRAM.csv",G)
        write_csv(prefix+"-HAMILTONIAN.csv",K)
        for kind, data in (("GRAM",G),("HAMILTONIAN",K)):
            need(parse_csv(prefix+"-"+kind+".csv")==data,
                 "full_dense_matrix_serialization_not_reversible")
        emit("Y137_H144_STAGE",dimension=dim,gram_shape=str(dim)+"x"+str(dim),
             matrix_entries=dim*dim,
             basis_rank=dim,
             exact_residual_four_Gram_det_bits=rank.bit_length(),
             exact_rank_four_minor_sha256=ranksha,
             source_selected_count=len(take),
             selected_diag_groups=",".join(str(x) for x in sorted(groups)),
             gram_sha256=matrix_sha(G),
             hamiltonian_sha256=matrix_sha(K),
             first_Ritz_lo_num=ritz[0][0],first_Ritz_hi_num=ritz[0][1],
             second_Ritz_lo_num=ritz[1][0],second_Ritz_hi_num=ritz[1][1],
             energy_den=DEN,
             both_monotone_12_to_144="PASS",
             full_space_residual="NOT_COMPUTED",
             Wilson_weight="HOLD")
    emit("Y137_H144_VERDICT",dimension=144,
         authentic_matrix="EXACT_WEIGHTED_G_AND_K",
         basis="EIGHT_FLATS_ORIGINAL_FOUR_KRYLOV_PLUS_132_ORBITS",
         every_nesting="STRICT_SUBSPACE_INCLUSION",
         12_24_48_96_144="ALL_EXACT",
         exact_coordinate_selection="PAIRWISE_NONADJACENT",
         first_two_Ritz="EXACT_INTEGER_INERTIA_BRACKETS",
         full_space_residual="HOLD",
         first_Wilson_weight="HOLD",
         issue_137="OPEN")


if __name__ == "__main__":
    if sys.argv[1:]==["toy"]:
        test_small()
    elif sys.argv[1:]==["real"]:
        real()
    else:
        need(False,"usage_toy_or_real")
