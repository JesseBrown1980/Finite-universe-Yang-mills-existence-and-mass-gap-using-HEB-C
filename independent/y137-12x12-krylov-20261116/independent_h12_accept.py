#!/usr/bin/env python3
"""Independent full-12-dimensional exact inertia verifier for the Y137 H12 receipt.

Uses the frozen result only, not the 4x4 builder's Schur shortcut or graph
source. Fraction-free 12x12 Sylvester sequence; integer arithmetic only.
"""
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RESULT = os.path.join(HERE, "RESULT-H12-20261116.hbp")
DEN = 1000000000
ANCHORS = (69909875505, 69949729820)
RITZ = ((1, 69924680131, 69924680132),
        (2, 69963663574, 69963663575))
G_SHA = "f77d8d060eb779574bb40d918e8886de333e0d0afdbdfba67639cb104fd4484f"
H_SHA = "8abe46fc8d0ca1d9300ad1edb934ca0d92dae08bf7c933350abb208737cac50a"
SOURCE_BLOB = "2bb1c89a53b701e5d3e6b369662a10effcc7e9dc"


def need(ok, why):
    if not ok:
        print("Y137_H12_ACCEPT_REFUSE|reason=" + why + "|json=0", flush=True)
        raise SystemExit(1)


def parse(line, tag):
    need(line.startswith(tag + "|"), "wrong_receipt_tag")
    out = {}
    for term in line.split("|")[1:]:
        key, eq, value = term.partition("=")
        need(eq and key not in out, "malformed_or_duplicate_receipt_field")
        out[key] = value
    need(out.get("json") == "0", "missing_receipt_end")
    return out


def mats(s):
    lines = s.split(";")
    need(len(lines) == 12, "matrix_row_count")
    out = [[int(x) for x in row.split(",")] for row in lines]
    need(all(len(row) == 12 for row in out), "matrix_column_count")
    return out


def matrix_sha(a):
    return hashlib.sha256("|".join(str(x) for row in a for x in row)
                          .encode("ascii")).hexdigest()


def det(A):
    """Second independent rational-free Bareiss implementation."""
    n = len(A)
    r = [row[:] for row in A]
    if n == 1:
        return r[0][0]
    divisor = 1
    sign = 1
    for k in range(n - 1):
        if r[k][k] == 0:
            swap = next((j for j in range(k + 1, n) if r[j][k] != 0), None)
            if swap is None:
                return 0
            r[k], r[swap] = r[swap], r[k]
            sign = -sign
        d = r[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                q = d * r[i][j] - r[i][k] * r[k][j]
                need(q % divisor == 0, "nonexact_Sylvester_division")
                r[i][j] = q // divisor
            r[i][k] = 0
        divisor = d
    return sign * r[-1][-1]


def leading(A):
    need(all(A[i][j] == A[j][i]
             for i in range(12) for j in range(12)), "matrix_nonsymmetric")
    return [det([row[:k] for row in A[:k]]) for k in range(1, 13)]


def inertia(A):
    s = leading(A)
    need(all(s), "degenerate_exact_inertia")
    previous = 1
    n = 0
    for current in s:
        n += int((current < 0) != (previous < 0))
        previous = current
    return n


def full_pencil(G, H, z):
    return [[DEN * H[i][j] - z * G[i][j] for j in range(12)]
            for i in range(12)]


def verify():
    source = open(RESULT, encoding="ascii").read().splitlines()
    need(len(source) == 8, "receipt_row_count")
    p = parse(source[0], "Y137_H12_PROVENANCE")
    stats = parse(source[1], "Y137_H12_SOURCE")
    data = parse(source[2], "Y137_H12_MATRIX")
    pin = [parse(x, "Y137_H12_INERTIA") for x in source[3:5]]
    ritz = [parse(x, "Y137_H12_RITZ") for x in source[5:7]]
    verdict = parse(source[7], "Y137_H12_VERDICT")

    need(p.get("script_blob") == SOURCE_BLOB and
         p.get("original_PR180_blob") == stats.get("source_180_gitblob") and
         p.get("scope") == "EXACT_RITZ_SUBSPACE_ONLY",
         "original_source_provenance")
    need(stats.get("k2_nonflat_rows") == "8034"
         and stats.get("weighted_row_vs_pair") == "16_OF_16_EXACT"
         and stats.get("graph_unordered_weighted_pairs") == "20736"
         and stats.get("K2_K3_exterior_edges") == "500664"
         and stats.get("total_K2_selfloops") == "0",
         "source_operator_census_changed")
    G, H = mats(data["gram"]), mats(data["hamiltonian"])
    need(matrix_sha(G) == G_SHA == data["gram_sha256"]
         and matrix_sha(H) == H_SHA == data["hamiltonian_sha256"],
         "matrix_SHA_mismatch")
    need(data.get("rank") == "12" and
         data.get("weighted_metric") == "W_ORBIT" and
         data.get("operator") == "H_JE", "incompatible_matrix_units")

    all_gram = leading(G)
    need(all(v > 0 for v in all_gram), "nonpositive_full_12_Gram")
    W = (1, 3, 2, 3, 3, 2, 2, 2)
    need(all(G[i][j] == (W[i] if i == j else 0)
             for i in range(8) for j in range(12)),
         "wrong_flat_metric_or_PQ_overlap")
    need(all(H[i][j] == (72 * W[i] if i == j else 0)
             for i in range(8) for j in range(8)),
         "wrong_flat_electric_P_block")
    need(any(H[i][j] for i in range(8) for j in range(8, 12)),
         "missing_PQ_Krylov_coupling")

    for sample, z in zip(pin, ANCHORS):
        need(int(sample["z_num"]) == z and
             int(sample["z_den"]) == DEN,
             "swapped_frozen_energy")
        observed = inertia(full_pencil(G, H, z))
        need(observed == int(sample["negative"]), "source_Ritz_inertia_disagreement")

    for actual, (k, lo, hi) in zip(ritz, RITZ):
        need(int(actual["k"]) == k
             and int(actual["lower_z_num"]) == lo
             and int(actual["upper_z_num"]) == hi
             and int(actual["denominator"]) == DEN
             and hi - lo == 1, "Ritz_bracket_not_pinned")
        need(inertia(full_pencil(G, H, lo)) == k - 1
             and inertia(full_pencil(G, H, hi)) == k,
             "independent_12x12_inertia_not_bracketing")

    need(verdict.get("generalized_gram") == "STRICT_PD"
         and verdict.get("original_Wilson_weight") == "HOLD"
         and verdict.get("full_complement_gap") == "NOT_CERTIFIED",
         "incorrect_scientific_scope")

    # Two deliberately bad constructions must be rejected.
    G_bad = [row[:] for row in G]
    G_bad[0][0] = 0
    need(not all(v > 0 for v in leading(G_bad)),
         "missing_zero_Gram_negative_control")
    H_bad = [row[:] for row in H]
    H_bad[0][8] += 1
    need(any(H_bad[i][j] != H_bad[j][i]
             for i in range(12) for j in range(12)),
         "missing_PQ_Hermitian_negative_control")
    print("Y137_H12_ACCEPT|rows=12|columns=12"
          "|full_12_Gram_positive_leading_minors=12_OF_12"
          "|exact_frozen_12x12_inertia=2_OF_2"
          "|first_two_Ritz_brackets=4_OF_4"
          "|original_source_SHA=PINNED"
          "|negative_corruptions=2_OF_2_REFUSED"
          "|source_full_state_residual=NOT_COMPUTED"
          "|Wilson_weight=HOLD|json=0", flush=True)


if __name__ == "__main__":
    verify()
