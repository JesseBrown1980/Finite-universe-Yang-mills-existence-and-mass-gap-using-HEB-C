#!/usr/bin/env python3
"""#137 second-seat signed mu3 operator identity and adversarial controls.

A deliberately small EXACT toy, NOT a real Q5 calculation. No floats,
source dependencies, or archived Yang-Mills data. Eight source columns.
"""
from hashlib import sha256

WEIGHT = [1, 2, 3, 6]
MAGNETIC = [4, 7, 9, 10]
B = 10**9
Z = 69900000000
CHANNELS = 8
N = 4

# Off-diagonal common flux: w_i c_ij == w_j c_ji.
FLUX = {(0, 1): 6, (0, 2): 6, (0, 3): 12,
        (1, 2): 6, (1, 3): 12, (2, 3): 6}
EDGES = [[0] * N for _ in range(N)]
for (i, j), flux in FLUX.items():
    assert flux % WEIGHT[i] == 0 and flux % WEIGHT[j] == 0
    EDGES[i][j] = flux // WEIGHT[i]
    EDGES[j][i] = flux // WEIGHT[j]
for i, count in enumerate([2, 5, 11, 13]):
    EDGES[i][i] = count
OFF_SUPPORT = [72 - sum(row) for row in EDGES]
W = [6 * weight for weight in WEIGHT]

# Deliberately signed source values; a Q4 sign can be lost when
# reusing mu2's positive-response Gram computation for mu3.
V = [
    [2, -3, 5, -7, 11, -13, 17, -19],
    [-23, 29, -31, 37, -41, 43, -47, 53],
    [59, -61, 67, -71, 73, -79, 83, -89],
    [97, -101, 103, -107, 109, -113, 127, -131],
]


def need(ok, why):
    if not ok:
        raise SystemExit("Y137_MU3_EDGE_REFUSE|reason=" + why + "|json=0")


def mu2(v):
    return [[sum(W[i] * v[i][a] * v[i][k] for i in range(N))
             for k in range(CHANNELS)] for a in range(CHANNELS)]


def mu3_by_rows(v):
    # Complete diagonal electric count is 72, EVEN when the source
    # has self loops and its nonzero vector support is truncated.
    x = [[0] * N for _ in range(N)]
    for i in range(N):
        x[i][i] = B * (72 + 9 * MAGNETIC[i]) - Z
        for j in range(N):
            x[i][j] -= B * EDGES[i][j]
    return [[sum(W[i] * v[i][a] * x[i][j] * v[j][k]
                 for i in range(N) for j in range(N))
             for k in range(CHANNELS)] for a in range(CHANNELS)]


def mu3_by_pairs(v):
    # Independent unordered-pair bilinear, counting real self loops
    # on the diagonal and each weighted-symmetric edge exactly once.
    result = [[0] * CHANNELS for _ in range(CHANNELS)]
    for i in range(N):
        diagonal = B * (72 + 9 * MAGNETIC[i]) - Z - B * EDGES[i][i]
        for a in range(CHANNELS):
            for k in range(CHANNELS):
                result[a][k] += W[i] * diagonal * v[i][a] * v[i][k]
    for i in range(N):
        for j in range(i + 1, N):
            flux = B * W[i] * EDGES[i][j]
            for a in range(CHANNELS):
                for k in range(CHANNELS):
                    result[a][k] -= flux * (v[i][a] * v[j][k] +
                                            v[j][a] * v[i][k])
    return result


def run():
    need(all(t >= 0 for t in OFF_SUPPORT), "negative_off_support_count")
    need(all(sum(EDGES[i]) + OFF_SUPPORT[i] == 72 for i in range(N)),
         "72_raw_moves")
    need(all(WEIGHT[i] * EDGES[i][j] == WEIGHT[j] * EDGES[j][i]
             for i in range(N) for j in range(N)), "weighted_reciprocity")
    need(all(EDGES[i][i] > 0 for i in range(N)), "self_loops_absent")

    m2 = mu2(V)
    m3 = mu3_by_rows(V)
    need(m3 == mu3_by_pairs(V), "row_pair_disagreement")
    need(all(m3[a][k] == m3[k][a]
             for a in range(CHANNELS) for k in range(CHANNELS)),
         "mu3_not_symmetric")

    # Flip the SIGN of a complete Q4-like source vector. Its mu2 outer
    # product remains byte-identical, but its mixed-sign mu3 changes.
    flipped = [row[:] for row in V]
    flipped[1] = [-x for x in flipped[1]]
    need(mu2(flipped) == m2, "wrong_sign_changed_mu2")
    altered = mu3_by_rows(flipped)
    need(altered == mu3_by_pairs(flipped) and altered != m3,
         "wrong_sign_not_detected_in_mu3")
    need(altered[0][0] - m3[0][0] == -844560000000000,
         "sign_control_frozen_value")

    # Fold one real edge into a self loop: total row degree stays 72.
    # A degree-only checker would accept it; weighted reciprocity refuses.
    forged = [row[:] for row in EDGES]
    forged[0][1] -= 1
    forged[0][0] += 1
    need(sum(forged[0]) + OFF_SUPPORT[0] == 72,
         "folded_edge_not_72_preserving")
    need(WEIGHT[0] * forged[0][1] != WEIGHT[1] * forged[1][0],
         "folded_edge_not_rejected")

    print("Y137_MU3_EDGE_TOY|rows=4|channels=8|"
          "raw_moves_per_row=72|nonzero_self_loops=PASS|"
          "weighted_reverse_edges=PASS|row_pair_exact=PASS|"
          "sign_flip_mu2_identical=PASS|sign_flip_mu3_changed=PASS|"
          "folded_edge_preserves_degree_but_breaks_reciprocity=PASS|"
          "real_Q5=NOT_COMPUTED|Wilson_weight=HOLD|json=0")
    print("Y137_MU3_EDGE_NUMBERS|mu2_00=" + str(m2[0][0]) +
          "|mu3_00=" + str(m3[0][0]) +
          "|sign_flipped_mu3_00=" + str(altered[0][0]) +
          "|delta_mu3_00=" + str(altered[0][0] - m3[0][0]) +
          "|matrix_sha256=" + sha256(str(m3).encode("ascii")).hexdigest() +
          "|json=0")


if __name__ == "__main__":
    run()
