#!/usr/bin/env python3
"""Sharp two- and three-moment Schur brackets (matrix Gauss, Lobatto and Radau forms for 1/x)
from the archived accepted-K3 moments mu0, mu1, mu2, beside the degree-1 and degree-2
Chebyshev brackets of RESULT-N1 and draft #197. Integers only. See PREDICTION.hbp.
"""
import hashlib
import os
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE = os.path.join(ROOT, "independent", "y137-shell4-diagonal-cache-20261114", "RESULT-MAGNETIC-CACHE.hbp")
MU1 = os.path.join(ROOT, "independent", "y137-real-Q-moment-20261114", "RESULT-MU1.hbp")
MU2 = os.path.join(ROOT, "independent", "y137-d11-shell5-spill-20261114", "RESULT-MU2.hbp")
N1 = os.path.join(ROOT, "independent", "y137-real-Q-moment-20261114", "RESULT-N1.hbp")
N2 = os.path.join(ROOT, "independent", "y137-d11-mu3-envelope-n2-schur-20261114", "RESULT-N2.hbp")
BLOBS = {
    "source": "6454216973b8e59d65174c7cadc4f22c7dcf0354",
    "mu1": "86abf9611f8b9df5e03e796e81f513cba826c085",
    "mu2": "31de869725d0e760e650365d4c386b4b2fd722e6",
    "n1": "6021f9e24532132fa52bc8ffa5477ef08e7430c8",
}
Z = (69909875505, 69949729820)
N = 8


def need(cond, reason):
    if not cond:
        print("Y137_RADAU_REFUSE|reason=" + reason + "|json=0", flush=True)
        raise SystemExit(1)


def emit(label, **entries):
    print(label + "|" + "|".join(str(k) + "=" + str(v) for k, v in entries.items()) + "|json=0", flush=True)


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()


def read(path, pin, tag):
    raw = open(path, "rb").read()
    if pin is not None:
        need(blob(raw) == BLOBS[pin], "immutable_" + pin + "_source_changed")
    rows = []
    for line in raw.decode("utf-8").splitlines():
        if not line.startswith(tag + "|"):
            continue
        d = {}
        for p in line.split("|")[1:]:
            need("=" in p, "malformed_source_row")
            k, v = p.split("=", 1)
            need(k not in d, "duplicate_source_field")
            d[k] = v
        rows.append(d)
    need(len(rows) == 2, "wrong_sample_count")
    return rows


def matrix(text):
    m = [[int(x) for x in row.split(",")] for row in text.split(";")]
    need(len(m) == N and all(len(row) == N for row in m), "8x8_shape")
    return m


def sha(m):
    return hashlib.sha256("|".join(str(x) for row in m for x in row).encode("ascii")).hexdigest()


def add(a, b):
    return [[a[i][j] + b[i][j] for j in range(N)] for i in range(N)]


def scale(a, n):
    return [[n * x for x in row] for row in a]


def sub(a, b):
    return [[a[i][j] - b[i][j] for j in range(N)] for i in range(N)]


def mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(N)) for j in range(N)] for i in range(N)]


def determinant(a):
    n = len(a)
    t = [row[:] for row in a]
    sign, prev = 1, 1
    for k in range(n - 1):
        if t[k][k] == 0:
            swap = next((i for i in range(k + 1, n) if t[i][k]), None)
            if swap is None:
                return 0
            t[k], t[swap] = t[swap], t[k]
            sign = -sign
        piv = t[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                x = piv * t[i][j] - t[i][k] * t[k][j]
                need(x % prev == 0, "Bareiss_fraction_free_fault")
                t[i][j] = x // prev
        prev = piv
    return sign * t[-1][-1]


def adjugate(a):
    out = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            minor = [[a[r][c] for c in range(N) if c != j] for r in range(N) if r != i]
            out[j][i] = (-1 if (i + j) % 2 else 1) * determinant(minor)
    return out


def symmetric(a):
    return all(a[i][j] == a[j][i] for i in range(N) for j in range(N))


def psd(a):
    need(symmetric(a), "nonsymmetric_Loewner_matrix")
    for degree in range(1, N + 1):
        for ix in combinations(range(N), degree):
            if determinant([[a[i][j] for j in ix] for i in ix]) < 0:
                return False
    return True


def positive_definite(a):
    need(symmetric(a), "nonsymmetric_matrix")
    return all(determinant([row[:n] for row in a[:n]]) > 0 for n in range(1, N + 1))


def inertia(a):
    need(symmetric(a), "nonsymmetric_inertia_matrix")
    old, negative = 1, 0
    for n in range(1, N + 1):
        q = determinant([row[:n] for row in a[:n]])
        need(q != 0, "zero_leading_minor_inertia_HOLD")
        negative += int((q < 0) != (old < 0))
        old = q
    return negative


def trace(a):
    return sum(a[i][i] for i in range(N))


def inverse_parts(a, name):
    need(positive_definite(a), name + "_not_positive_definite")
    det, adj = determinant(a), adjugate(a)
    need(mul(a, adj) == scale([[int(i == j) for j in range(N)] for i in range(N)], det), name + "_adjugate_identity")
    need(symmetric(adj), name + "_adjugate_symmetry")
    return det, adj


def le(a_num, a_den, b_num, b_den):
    """a_num/a_den <= b_num/b_den in the Loewner order, positive denominators."""
    need(a_den > 0 and b_den > 0, "nonpositive_denominator")
    return psd(sub(scale(b_num, a_den), scale(a_num, b_den)))


def ppm(num, den):
    return (1000000 * num) // den


def certify(sample, mu1_src, mu2_src, n1_src, n2_src, index):
    z = Z[index]
    need(all(int(s["sample_num"]) == z for s in (sample, mu1_src, mu2_src, n1_src, n2_src)), "sample_energy_alignment")
    U0, G0 = matrix(sample["U0"]), matrix(sample["G0"])
    need(sha(U0) == sample["U_sha256"] and sha(G0) == sample["G_sha256"], "historical_U_G_hash")
    need(all(x % 6 == 0 for row in G0 for x in row), "accepted_W_metric_divisibility")
    M0 = [[x // 6 for x in row] for row in G0]
    M1, M2 = matrix(mu1_src["exact_mu1_8x8"]), matrix(mu2_src["actual_K3_mu2_8x8"])
    need(sha(M0) == mu1_src["wholeQ_mu0_sha256"] == mu2_src["actual_K3_mu0_sha256"]
         and sha(M1) == mu1_src["wholeQ_mu1_sha256"] == mu2_src["actual_K3_mu1_sha256"]
         and sha(M2) == mu2_src["actual_K3_mu2_sha256"], "frozen_three_real_moment_hashes")
    g, h = 94068200000 - z, 468000000000 - z
    need(g > 0 and h > g, "accepted_global_Q_spectrum")
    s, d = g + h, h - g
    K = 2 * s * s - d * d
    # --- three moments: weights (X-g) and (h-X) on the pair X^(-1/2)B, X^(1/2)B ---
    C, D = sub(M2, scale(M1, g)), sub(M1, scale(M0, g))
    G, E = sub(scale(M1, h), M2), sub(scale(M0, h), M1)
    detC, adjC = inverse_parts(C, "C")
    detG, adjG = inverse_parts(G, "G")
    lo3_num = add(sub(scale(U0, g * detC), scale(M0, detC)), mul(mul(D, adjC), D))
    lo3_den = g * detC
    hi3_num = sub(sub(scale(U0, h * detG), scale(M0, detG)), mul(mul(E, adjG), E))
    hi3_den = h * detG
    # --- two moments: Gauss (weight I) and Lobatto (weight (X-g)(h-X)) ---
    det1, adj1 = inverse_parts(M1, "mu1")
    hi2_num = sub(scale(U0, det1), mul(mul(M0, adj1), M0))
    hi2_den = det1
    lo2_num = add(sub(scale(U0, g * h), scale(M0, s)), M1)
    lo2_den = g * h
    need(all(symmetric(m) for m in (lo3_num, hi3_num, hi2_num, lo2_num)), "bound_symmetry")
    need(le(lo3_num, lo3_den, hi3_num, hi3_den) and le(lo2_num, lo2_den, hi2_num, hi2_den), "valid_intervals")
    # --- the brackets on file ---
    orig_hi_num, orig_hi_den = U0, 1
    orig_lo_num, orig_lo_den = sub(scale(U0, g), M0), g
    n1_hi_num, n1_hi_den = matrix(n1_src["new_upper_numerator_8x8"]), int(n1_src["new_upper_denom"])
    n1_lo_num, n1_lo_den = matrix(n1_src["new_lower_numerator_8x8"]), int(n1_src["new_lower_denom"])
    n2_hi_num, n2_hi_den = matrix(n2_src["source_Schur_upper_numerator"]), int(n2_src["source_Schur_upper_den"])
    n2_lo_num, n2_lo_den = matrix(n2_src["source_Schur_lower_numerator"]), int(n2_src["source_Schur_lower_den"])
    need(sha(n2_hi_num) == n2_src["source_Schur_upper_sha256"] and sha(n2_lo_num) == n2_src["source_Schur_lower_sha256"]
         and n2_hi_den == K * K and n2_lo_den == g * K * K and n1_hi_den == s * s and n1_lo_den == g * s * s,
         "brackets_on_file_changed")
    r1 = le(hi3_num, hi3_den, n2_hi_num, n2_hi_den) and le(n2_lo_num, n2_lo_den, lo3_num, lo3_den)
    r2 = le(hi2_num, hi2_den, n1_hi_num, n1_hi_den) and le(n1_lo_num, n1_lo_den, lo2_num, lo2_den)
    r3 = le(hi3_num, hi3_den, hi2_num, hi2_den) and le(lo2_num, lo2_den, lo3_num, lo3_den)
    inside_orig = le(hi3_num, hi3_den, orig_hi_num, orig_hi_den) and le(orig_lo_num, orig_lo_den, lo3_num, lo3_den)

    def width(hn, hd, ln, ld):
        return trace(hn) * ld - trace(ln) * hd, hd * ld

    w3, w2 = width(hi3_num, hi3_den, lo3_num, lo3_den), width(hi2_num, hi2_den, lo2_num, lo2_den)
    wn2, wn1 = width(n2_hi_num, n2_hi_den, n2_lo_num, n2_lo_den), width(n1_hi_num, n1_hi_den, n1_lo_num, n1_lo_den)
    wo = width(orig_hi_num, orig_hi_den, orig_lo_num, orig_lo_den)

    def ratio(a, b):
        return ppm(a[0] * b[1], a[1] * b[0])

    target = index + 1
    negs = [inertia(m) for m in (hi3_num, lo3_num, hi2_num, lo2_num)]
    emit("Y137_RADAU_POINT", sample_num=z, target_negative_inertia=target,
         three_moment_inside_197_degree2=int(r1), two_moment_inside_N1_degree1=int(r2),
         three_moment_inside_two_moment=int(r3), three_moment_inside_original=int(inside_orig),
         width_trace_three_moment_per_million_of_197=ratio(w3, wn2),
         width_trace_two_moment_per_million_of_N1=ratio(w2, wn1),
         width_trace_three_moment_per_million_of_original=ratio(w3, wo),
         width_trace_197_per_million_of_original=ratio(wn2, wo),
         width_trace_two_moment_per_million_of_original=ratio(w2, wo),
         width_trace_N1_per_million_of_original=ratio(wn1, wo),
         inertia_hi3=negs[0], inertia_lo3=negs[1], inertia_hi2=negs[2], inertia_lo2=negs[3],
         upper3_den=hi3_den, upper3_sha256=sha(hi3_num), lower3_den=lo3_den, lower3_sha256=sha(lo3_num),
         upper2_den=hi2_den, upper2_sha256=sha(hi2_num), lower2_den=lo2_den, lower2_sha256=sha(lo2_num))
    return r1, r2, r3, ratio(w3, wn2), ratio(w3, wo), all(n == target for n in negs)


def main():
    S = read(CACHE, "source", "Y137_CACHE_POINT")
    M1 = read(MU1, "mu1", "Y137_MU1_COMPLETE_POINT")
    M2 = read(MU2, "mu2", "Y137_D11_MU2_POINT")
    R1 = read(N1, "n1", "Y137_N1_POINT")
    R2 = read(N2, None, "Y137_N2_ENVELOPE_POINT")
    out = [certify(S[i], M1[i], M2[i], R1[i], R2[i], i) for i in range(2)]
    emit("Y137_RADAU_VERDICT",
         R1_three_moment_inside_197=int(all(o[0] for o in out)),
         R2_two_moment_inside_N1=int(all(o[1] for o in out)),
         R3_three_inside_two=int(all(o[2] for o in out)),
         R4_width_at_most_700000_per_million_of_197=int(all(o[3] <= 700000 for o in out)),
         R5_inertia_kept=int(all(o[5] for o in out)),
         R6_width_at_most_200000_per_million_of_original=int(all(o[4] <= 200000 for o in out)),
         new_operator_applications=0, new_moments=0, Wilson_weight="HOLD", issue_137="OPEN")


if __name__ == "__main__":
    main()
