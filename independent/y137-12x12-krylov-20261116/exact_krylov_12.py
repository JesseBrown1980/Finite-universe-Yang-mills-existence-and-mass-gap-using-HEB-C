#!/usr/bin/env python3
"""#137: exact 12-dimensional Rayleigh--Ritz Galerkin pencil for 3x4 S3, r=9.

Eight flat orbit basis vectors plus four Q-Krylov directions:
    f1 = QHP v1, f2 = QHP v2,
    g1 = QHQ f1, g2 = QHQ f2.
The original fixed unshifted Wilson sample flat vectors v1,v2 are HASH PINNED.
Every G_ij=<b_i,b_j>_W and H_ij=<b_i,H b_j>_W is an exact integer.
H_QQ is separately contracted by CSR rows and unordered weighted edges.

This is a variational compression, NOT yet a full-space spectral enclosure,
Wilson transition certificate, or continuum mass-gap theorem.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DUAL = os.path.join(ROOT, "independent", "y137-q-dual-weight-20261113",
                    "RESULT-WILSON-Q-DUAL.hbp")
DUAL_BLOB = "40762ceb865829156e4765b720f52d39a8be9b6f"
DEN = 1000000000
ORIGINAL_SAMPLES = (69909875505, 69949729820)
N_P = 8
N_K = 4
N = 12
ZERO = (0, 0, 0, 0)


def need(cond, why):
    if not cond:
        print("Y137_H12_REFUSE|reason=" + why + "|json=0", flush=True)
        raise SystemExit(1)


def emit(tag, **kwargs):
    print(tag + "|" + "|".join(str(k) + "=" + str(v)
          for k, v in kwargs.items()) + "|json=0", flush=True)


def gitblob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii")
                        + b"\x00" + raw).hexdigest()


def matrix(n=N):
    return [[0] * n for _ in range(n)]


def flatten(m):
    return ";".join(",".join(str(x) for x in row) for row in m)


def sha(m):
    return hashlib.sha256("|".join(str(x) for row in m for x in row)
                          .encode("ascii")).hexdigest()


def symmetric(m):
    return all(m[i][j] == m[j][i]
               for i in range(len(m)) for j in range(len(m)))


def determinant(a):
    """Bareiss exact integer determinant; only 1..4 principal pivots used."""
    n = len(a)
    need(all(len(row) == n for row in a), "non_square_Bareiss")
    t = [row[:] for row in a]
    if n == 1:
        return t[0][0]
    prev = 1
    sign = 1
    for k in range(n - 1):
        if not t[k][k]:
            z = next((i for i in range(k + 1, n) if t[i][k]), None)
            if z is None:
                return 0
            t[k], t[z] = t[z], t[k]
            sign = -sign
        pivot = t[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = pivot * t[i][j] - t[i][k] * t[k][j]
                need(numerator % prev == 0, "nonintegral_Bareiss")
                t[i][j] = numerator // prev
            t[i][k] = 0
        prev = pivot
    return sign * t[-1][-1]


def leading_dets(a):
    return [determinant([row[:j] for row in a[:j]])
            for j in range(1, len(a) + 1)]


def negatives(a):
    """Symmetric, nonzero-leading-principal-minor Sylvester inertia."""
    need(symmetric(a), "inertia_nonsymmetric")
    dets = leading_dets(a)
    need(all(dets), "singular_leading_minor_needs_exact_pivoting")
    before = 1
    negative = 0
    for d in dets:
        negative += int((d < 0) != (before < 0))
        before = d
    return negative


def read_original_samples():
    raw = open(DUAL, "rb").read()
    need(gitblob(raw) == DUAL_BLOB, "original_180_receipt_blob_mismatch")
    records = [l for l in raw.decode("ascii").splitlines()
               if l.startswith("Y137_QDUAL_FLATS|")]
    need(len(records) == 1, "original_trial_vector_receipt_missing")
    d = dict(x.split("=", 1) for x in records[0].split("|")[1:]
             if "=" in x)
    need(d.get("sector") == "even" and d.get("certification") == "trial_only",
         "original_trial_scope_changed")
    v1 = tuple(int(x) for x in d["v1"].split(","))
    v2 = tuple(int(x) for x in d["v2"].split(","))
    need(len(v1) == len(v2) == N_P and
         v1[0] == v2[3] == DEN, "frozen_8flat_vector_mismatch")
    return v1, v2


def source_module():
    """Import the already pinned original K2 and K3 graph architecture."""
    prev = sys.argv[:]
    sys.argv = sys.argv[:1]  # inherited pinned loader prohibits extra argv
    try:
        sys.path.insert(0, os.path.join(ROOT, "independent",
                                        "y137-liftfree-k3-20261113"))
        import k3_common
    finally:
        sys.argv = prev
    return k3_common.mod


def raw_graph(mod):
    c = mod.c
    w, magnetic, adjacency, q_flat, exterior = c.graph()
    states, flat, sizes = mod.rebuild_states()
    need(sizes == [8, 264, 7770] and len(states) == len(w) == 8042,
         "original_K2_census")
    need([c.weight(s) for s in states] == w and
         [c.magnetic(c.from_key(s)) for s in states] == magnetic,
         "independent_K2_weights_magnetic")
    ball = mod.ball_from_checker(w, magnetic, adjacency, q_flat, exterior)
    need(ball["n"] == 8034 and ball["nf"] == 147344 and
         len(ball["C"]) == ball["n"], "original_Q_K2_source")
    return ball, magnetic


def act(ball, v):
    """Full QHQ action on vectors supported on Q(K2), restricted to K2."""
    rs, dst, cc = ball["rs"], ball["oj"], ball["oc"]
    diag = ball["dbase"]
    answer = []
    for i in range(ball["n"]):
        row = diag[i] * v[i]
        for e in range(rs[i], rs[i + 1]):
            row -= cc[e] * v[dst[e]]
        answer.append(row)
    return answer


def dot(w, x, y):
    return sum(w[i] * x[i] * y[i] for i in range(len(w)))


def exact_pencil(ball, V, magnetic):
    """Build 8+4 basis; independent row and unordered-pair H contractions."""
    q = ball["n"]
    wf, wq = ball["wf"], ball["wq"]
    C = ball["C"]
    need(wf == [1, 3, 2, 3, 3, 2, 2, 2], "wrong_8flat_orbit_order")
    F = []
    for vec in V:
        F.append([-sum(row[p] * vec[p] for p in range(N_P))
                  if row is not None else 0 for row in C])
    A_F = [act(ball, v) for v in F]
    Qcols = F + A_F
    A_Q = A_F + [act(ball, v) for v in A_F]

    # Confirm no first-step Q action was silently truncated beyond shell2.
    ext_source = ball["esrc"]
    need(all(F[k][i] == 0 for k in range(2) for i in ext_source),
         "Q_Bv_has_nonzero_source_at_K2_exterior")

    gram = matrix()
    hamiltonian = matrix()
    for p in range(N_P):
        gram[p][p] = wf[p]
        hamiltonian[p][p] = 72 * wf[p]

    for a in range(N_K):
        x = Qcols[a]
        for p in range(N_P):
            c = -sum(wq[i] * C[i][p] * x[i]
                     for i in range(q) if C[i] is not None)
            hamiltonian[p][N_P + a] = c
            hamiltonian[N_P + a][p] = c
        for b in range(N_K):
            gram[N_P + a][N_P + b] = dot(wq, x, Qcols[b])
            hamiltonian[N_P + a][N_P + b] = dot(wq, x, A_Q[b])
    need(symmetric(gram) and symmetric(hamiltonian),
         "weighted_Krylov_source_matrix_asymmetry")

    # Exact B*B=72 W_flat is a frozen independent source identity.
    for p in range(N_P):
        for t in range(2):
            need(hamiltonian[p][N_P + t] == 72 * wf[p] * V[t][p],
                 "original_BstarB_exact_72_regression")

    # Independent unordered weighted-pair contraction of the full 4x4 H_QQ.
    pair_h = [[0] * N_K for _ in range(N_K)]
    for i in range(q):
        wi = wq[i]
        for a in range(N_K):
            v = wi * ball["dbase"][i] * Qcols[a][i]
            for b in range(N_K):
                pair_h[a][b] += v * Qcols[b][i]
    rs, oj, oc = ball["rs"], ball["oj"], ball["oc"]
    reverse = [dict(zip(oj[rs[i]:rs[i+1]], oc[rs[i]:rs[i+1]]))
               for i in range(q)]
    need(all(len(reverse[i]) == rs[i+1] - rs[i] for i in range(q)),
         "duplicate_directed_K2_edge")
    pairs = 0
    for i in range(q):
        wi = wq[i]
        for j, coeff in reverse[i].items():
            need(j != i, "stored_self_edge_not_absorbed_in_diagonal")
            if j <= i:
                continue
            need(j < q and reverse[j].get(i, 0) * wq[j] == wi * coeff,
                 "K2_W_reciprocity_failed")
            flux = wi * coeff
            pairs += 1
            for a in range(N_K):
                for b in range(N_K):
                    pair_h[a][b] -= flux * (
                        Qcols[a][i] * Qcols[b][j] +
                        Qcols[a][j] * Qcols[b][i])
    Hqq = [row[N_P:] for row in hamiltonian[N_P:]]
    need(pair_h == Hqq, "independent_K2_row_pair_H_disagreement")

    # Complete 72-move census: all K2 internal, flat, and exterior.
    ext_moves = [0] * q
    for i, wc in zip(ball["esrc"], ball["ewc"]):
        need(wc % wq[i] == 0, "bad_weighted_exterior")
        ext_moves[i] += wc // wq[i]
    # The diagonal stores 72+9m-selfloop. Reconstruct m by Q source.
    selfloops = 0
    for i in range(q):
        m_i = magnetic[8+i]
        selfc = 72 + 9 * m_i - ball["dbase"][i]
        need(selfc >= 0, "negative_selfloop")
        inflat = sum(C[i]) if C[i] is not None else 0
        inside = sum(oc[e] for e in range(rs[i], rs[i+1]))
        need(inflat + inside + ext_moves[i] + selfc == 72,
             "full_72_move_K2_row_failure")
        selfloops += selfc
    sub = [row[N_P:] for row in gram[N_P:]]
    dets = leading_dets(sub)
    need(all(d > 0 for d in dets), "four_Q_Krylov_directions_dependent")
    need(all(gram[i][j] == 0 for i in range(N_P) for j in range(N_P,N)),
         "P_Q_orthogonality_failure")
    return gram, hamiltonian, {
        "k2_nonflat_rows": q,
        "source_Q_f_support": [sum(v != 0 for v in f) for f in F],
        "source_Q_Af_support": [sum(v != 0 for v in f) for f in A_F],
        "graph_unordered_weighted_pairs": pairs,
        "K2_K3_exterior_edges": len(ball["esrc"]),
        "total_K2_selfloops": selfloops,
        "four_krylov_gram_determinant": dets[-1],
        "four_krylov_leading_minors_sha256": hashlib.sha256(
            ",".join(str(x) for x in dets).encode("ascii")).hexdigest()
    }


def inertia_at(g, h, z_num):
    """n_-(H-zG), exact 4x4 Schur complement for z < 72."""
    A = 72 * DEN - z_num
    need(0 <= z_num < 72 * DEN and A > 0, "inertia_outside_positive_flat_range")
    wf = [g[i][i] for i in range(N_P)]
    s = [[6 * A * (DEN * h[N_P+i][N_P+j]
                    - z_num * g[N_P+i][N_P+j]) for j in range(N_K)]
         for i in range(N_K)]
    for i in range(N_K):
        for j in range(N_K):
            cross = sum((6 // wf[p]) * h[p][N_P+i] * h[p][N_P+j]
                        for p in range(N_P))
            s[i][j] -= DEN * DEN * cross
    return negatives(s)


def ritz_threshold(g, h, k):
    """Upper bracket to one-billionth on kth Ritz eigenvalue below 72."""
    lo, hi = 0, 72 * DEN - 1
    need(inertia_at(g, h, lo) < k and inertia_at(g, h, hi) >= k,
         "requested_Ritz_level_not_in_0_to_72")
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if inertia_at(g, h, mid) >= k:
            hi = mid
        else:
            lo = mid
    need(inertia_at(g, h, lo) < k and inertia_at(g, h, hi) >= k,
         "Ritz_threshold_monotonicity")
    return lo, hi


def toy():
    a = [[2, 1], [1, 2]]
    need(determinant(a) == 3 and leading_dets(a) == [2, 3],
         "toy_Bareiss")
    need(negatives([[3, 1], [1, -2]]) == 1,
         "toy_Sylvester")
    bad = [[3, 1], [2, -2]]
    need(not symmetric(bad), "toy_wrong_hermiticity_not_rejected")
    v1, v2 = read_original_samples()
    need(v1 != v2, "toy_original_Q_flat_vector_collision")
    emit("Y137_H12_TOY", exact_integer_Bareiss="PASS",
         inertia_control="PASS", nonsymmetric_negative="REFUSED",
         original_180_Q_flat_sha="PINNED",
         real_matrix="NOT_COMPUTED", Wilson_weight="HOLD")


def real():
    V = read_original_samples()
    mod = source_module()
    ball, magnetic = raw_graph(mod)
    g, h, checks = exact_pencil(ball, V, magnetic)
    emit("Y137_H12_SOURCE", model="3x4_S3_r9",
         base="eight_physical_flats_plus_Bv1_Bv2_A_Bv1_A_Bv2",
         basis_dim=N, **checks,
         weighted_row_vs_pair="16_OF_16_EXACT",
         original_BstarB_72="PASS",
         source_180_gitblob=DUAL_BLOB)
    emit("Y137_H12_MATRIX", gram=flatten(g), hamiltonian=flatten(h),
         gram_sha256=sha(g), hamiltonian_sha256=sha(h),
         weighted_metric="W_ORBIT", operator="H_JE",
         rank=N, exact_integer="PASS",
         Wilson_weight="HOLD")
    for z in ORIGINAL_SAMPLES:
        emit("Y137_H12_INERTIA", z_num=z, z_den=DEN,
             negative=inertia_at(g, h, z),
             origin="EXACT_GENERALIZED_RITZ_NOT_FULL_EIGENVALUE")
    for k in (1, 2):
        lo, hi = ritz_threshold(g, h, k)
        emit("Y137_H12_RITZ", k=k, lower_z_num=lo, upper_z_num=hi,
             denominator=DEN, threshold_count_before=k-1,
             threshold_count_after=k,
             certificate="SUBSPACE_MINMAX_UPPER_ONLY",
             exact_full_state_residual="NOT_COMPUTED")
    emit("Y137_H12_VERDICT", generalized_gram="STRICT_PD",
         full_K2_72_move_census="PASS", row_pair_H4="PASS",
         two_Ritz_levels="EXACT_ONE_BILLIONTH_BRACKETS",
         original_Wilson_weight="HOLD",
         full_complement_gap="NOT_CERTIFIED",
         issue_137="OPEN", json=0)


def main(argv):
    if argv == ["toy"]:
        toy()
    elif argv == ["real"]:
        real()
    else:
        raise SystemExit("usage: exact_krylov_12.py toy|real")


if __name__ == "__main__":
    main(sys.argv[1:])
