#!/usr/bin/env python3
"""Y137 H12: independent CRT determinants and division-free Berkowitz over Z[z].

The frozen projected Hamiltonian is a GENERALIZED K-zG pencil. Its first
eight physical flat directions have G_PP=W, K_PP=72W, G_PQ=0. Hence

 det(zG-DK)=det(W)*(z-72D)^4 *
            det((z-72D)(zG4-DK4)-D^2 C^T W^-1 C),

where D=10^9 and C=K_PQ. The 4x4 polynomial determinant has degree eight.

Berkowitz over the commutative ring Z[z] checks the full degree-twelve
polynomial against that factorization with NO division. Separately, prime
field Gaussian elimination + CRT reconstructs exact signed determinants of
all twelve leading minors at the Ritz thresholds. An integer row-L1 Leibniz
bound proves when the CRT modulus suffices to recover the original integer.
This experiment does not compute full-Q residuals or Wilson spectral weight.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
INPUT = os.path.join(ROOT, "independent", "y137-12x12-krylov-20261116",
                     "RESULT-H12-20261116.hbp")
ORIGINAL_BLOB = "9876d083ecdbd91f81ddbd99ea311467d81a1ba7"
G_SHA = "f77d8d060eb779574bb40d918e8886de333e0d0afdbdfba67639cb104fd4484f"
K_SHA = "8abe46fc8d0ca1d9300ad1edb934ca0d92dae08bf7c933350abb208737cac50a"
DEN = 1000000000
FLAT = 72
W = (1, 3, 2, 3, 3, 2, 2, 2)
E = (69909875505, 69949729820)
RITZ = ((1, 69924680131, 69924680132),
        (2, 69963663574, 69963663575))
P0 = (0,)
P1 = (1,)
PRIMES = []


def need(ok, reason):
    if not ok:
        print("Y137_H12_MOD_REFUSE|reason=" + reason + "|json=0", flush=True)
        raise SystemExit(1)


def emit(tag, **parts):
    print(tag + "|" + "|".join(k + "=" + str(v) for k, v in parts.items())
          + "|json=0", flush=True)


def gitblob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii")
                        + b"\x00" + raw).hexdigest()


def sha_matrix(a):
    return hashlib.sha256("|".join(str(x) for row in a for x in row)
                          .encode("ascii")).hexdigest()


def sha_poly(p):
    return hashlib.sha256(",".join(str(x) for x in p).encode("ascii")).hexdigest()


def record(line, tag):
    need(line.startswith(tag + "|"), "wrong_record_tag")
    d = {}
    for part in line.split("|")[1:]:
        k, eq, v = part.partition("=")
        need(eq and k not in d, "malformed_or_duplicate_receipt_field")
        d[k] = v
    need(d.get("json") == "0", "wrong_receipt_terminator")
    return d


def parse_matrix(s):
    rows = [[int(x) for x in row.split(",")] for row in s.split(";")]
    need(len(rows) == 12 and all(len(row) == 12 for row in rows),
         "incorrect_12x12_dimensions")
    need(all(rows[i][j] == rows[j][i]
             for i in range(12) for j in range(12)), "nonsymmetric_pencil")
    return rows


def original():
    raw = open(INPUT, "rb").read()
    need(gitblob(raw) == ORIGINAL_BLOB, "original_H12_receipt_SHA_mismatch")
    lines = raw.decode("ascii").splitlines()
    need(len(lines) == 8, "original_H12_receipt_length")
    src = record(lines[1], "Y137_H12_SOURCE")
    data = record(lines[2], "Y137_H12_MATRIX")
    need(src.get("weighted_row_vs_pair") == "16_OF_16_EXACT"
         and src.get("original_BstarB_72") == "PASS"
         and src.get("k2_nonflat_rows") == "8034"
         and data.get("operator") == "H_JE"
         and data.get("weighted_metric") == "W_ORBIT"
         and data.get("rank") == "12",
         "original_H12_source_not_accepted")
    gram = parse_matrix(data["gram"])
    ham = parse_matrix(data["hamiltonian"])
    need(sha_matrix(gram) == G_SHA == data["gram_sha256"]
         and sha_matrix(ham) == K_SHA == data["hamiltonian_sha256"],
         "original_H12_matrix_hash_mismatch")
    return gram, ham


def padd(a, b):
    n = max(len(a), len(b))
    out = [0] * n
    for i in range(n):
        out[i] = (a[i] if i < len(a) else 0) + (
            b[i] if i < len(b) else 0)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return tuple(out)


def pneg(a):
    return tuple(-x for x in a)


def pmul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return tuple(out)


def psum(a):
    result = P0
    for x in a:
        result = padd(result, x)
    return result


def peval(poly, x):
    result = 0
    for c in reversed(poly):
        result = result * x + c
    return result


def berkowitz(matrix):
    """Samuelson/Berkowitz Toeplitz recurrence in any commutative ring Z[z].

    Coefficients are in descending powers of a separate formal variable t.
    The last coefficient of det(t I - matrix) equals (-1)^n det(matrix).
    This procedure uses polynomial addition and multiplication only.
    """
    n = len(matrix)
    need(all(len(row) == n for row in matrix), "Berkowitz_nonsquare")
    coeffs = (P1,)
    for start in range(n - 1, -1, -1):
        m = n - start - 1
        q = [P1, pneg(matrix[start][start])]
        if m:
            trailing = [row[start + 1:] for row in matrix[start + 1:]]
            column = [matrix[start + 1 + i][start] for i in range(m)]
            row = list(matrix[start][start + 1:])
            for k in range(m):
                q.append(pneg(psum(pmul(row[i], column[i])
                                    for i in range(m))))
                if k + 1 < m:
                    row = [psum(pmul(row[i], trailing[i][j])
                                for i in range(m)) for j in range(m)]
        new = []
        for i in range(m + 2):
            new.append(psum(pmul(q[j], coeffs[i - j])
                            for j in range(min(i, len(q) - 1) + 1)
                            if 0 <= i - j < len(coeffs)))
        coeffs = tuple(new)
    det = coeffs[-1]
    if n % 2:
        det = pneg(det)
    return det


def symmetric(a):
    return all(a[i][j] == a[j][i]
               for i in range(len(a)) for j in range(len(a)))


def factorization(G, K):
    need(symmetric(G) and symmetric(K), "nonsymmetric_original")
    for i in range(8):
        for j in range(12):
            need(G[i][j] == (W[i] if i == j else 0),
                 "incompatible_flat_Gram")
        for j in range(8):
            need(K[i][j] == (FLAT * W[i] if i == j else 0),
                 "incompatible_flat_Hamiltonian")
    C = [row[8:] for row in K[:8]]
    S = [[sum(C[p][i] * C[p][j] // W[p] for p in range(8))
          for j in range(4)] for i in range(4)]
    for p in range(8):
        need(all(C[p][i] % W[p] == 0 for i in range(4)),
             "nonintegral_cross_Gram")
    need(symmetric(S), "cross_S_not_symmetric")

    full = [[(-DEN * K[i][j], G[i][j]) for j in range(12)]
            for i in range(12)]
    p12 = berkowitz(full)
    g4 = [row[8:] for row in G[8:]]
    k4 = [row[8:] for row in K[8:]]
    reduced = [[padd(pmul((-FLAT * DEN, 1),
                           (-DEN * k4[i][j], g4[i][j])),
                     (-DEN * DEN * S[i][j],))
                for j in range(4)] for i in range(4)]
    p8 = berkowitz(reduced)
    factor = P1
    for unused in range(4):
        factor = pmul(factor, (-FLAT * DEN, 1))
    detW = 1
    for v in W:
        detW *= v
    p12_from4 = pmul(pmul((detW,), factor), p8)
    need(detW == 432 and len(p12) == 13 and len(p8) == 9,
         "generalized_polynomial_degree_or_metric")
    need(p12 == p12_from4, "12x12_vs_reduced_4x4_Berkowitz")
    return p12, p8, S, detW


def isprime(p):
    """Deterministic trial-division primality for primes below 2^31."""
    if p < 2:
        return False
    if p % 2 == 0:
        return p == 2
    k = 3
    while k * k <= p:
        if p % k == 0:
            return False
        k += 2
    return True


def prime(idx):
    while len(PRIMES) <= idx:
        candidate = 2147483647 if not PRIMES else PRIMES[-1] - 2
        while candidate > 1073741823 and not isprime(candidate):
            candidate -= 2
        need(candidate > 1073741823, "exhausted_proven_31bit_primes")
        PRIMES.append(candidate)
    return PRIMES[idx]


def modular_det(A, p):
    """Exact finite-field Gaussian elimination; pivot inverses exist mod p."""
    n = len(A)
    mat = [[v % p for v in row] for row in A]
    acc = 1
    for k in range(n):
        pivot_row = k
        while pivot_row < n and mat[pivot_row][k] == 0:
            pivot_row += 1
        if pivot_row == n:
            return 0
        if pivot_row != k:
            mat[k], mat[pivot_row] = mat[pivot_row], mat[k]
            acc = (-acc) % p
        pivot = mat[k][k]
        acc = acc * pivot % p
        inverse = pow(pivot, p - 2, p)
        for i in range(k + 1, n):
            if mat[i][k] == 0:
                continue
            mult = mat[i][k] * inverse % p
            for j in range(k + 1, n):
                mat[i][j] = (mat[i][j] - mult * mat[k][j]) % p
            mat[i][k] = 0
    return acc


def crt_signed_det(A):
    """Unique signed reconstruction once M > 2 * product row 1-norms."""
    n = len(A)
    need(n and all(len(row) == n for row in A), "CRT_not_square")
    bound = 1
    for row in A:
        size = sum(abs(v) for v in row)
        if size == 0:
            return 0, 0, 0
        bound *= size
    modulus = 1
    answer = 0
    count = 0
    while modulus <= 2 * bound:
        p = prime(count)
        residue = modular_det(A, p)
        correction = ((residue - answer) * pow(modulus % p, p - 2, p)) % p
        answer += modulus * correction
        modulus *= p
        count += 1
    signed = answer if 2 * answer <= modulus else answer - modulus
    need(abs(signed) <= bound, "CRT_exceeds_certified_row_bound")
    # An extra authenticated, previously unused modulus is a strong
    # independent error detector, not a substitute for the M>2B proof.
    p_extra = prime(count)
    need(signed % p_extra == modular_det(A, p_extra),
         "CRT_extra_prime_replay_failed")
    return signed, count, modulus.bit_length()


def leading_inertia(A):
    previous_sign = 1
    negatives = 0
    max_prime_count = 0
    signs = []
    for k in range(1, len(A) + 1):
        part = [row[:k] for row in A[:k]]
        det, used, bits = crt_signed_det(part)
        need(det != 0, "zero_leading_minor_requires_pivoted_LDL")
        sign = -1 if det < 0 else 1
        negatives += int(sign != previous_sign)
        previous_sign = sign
        max_prime_count = max(max_prime_count, used)
        signs.append("-" if sign < 0 else "+")
    return negatives, "".join(signs), max_prime_count


def pencil(G, K, z):
    return [[DEN * K[i][j] - z * G[i][j] for j in range(12)]
            for i in range(12)]


def main():
    G, K = original()
    p12, p8, S, detW = factorization(G, K)
    sdet, sn, sbits = crt_signed_det(S)
    need(sdet > 0, "fourth_rank_PQ_cross_not_proved")
    need(peval(p8, 72 * DEN) == DEN**8 * sdet,
         "factor72_not_exactly_four")

    gn, gs, gp = leading_inertia(G)
    need(gn == 0 and gs == "+" * 12, "Gram_not_strictly_positive")
    emit("Y137_H12_MOD_SOURCE",
         original_H12_blob=ORIGINAL_BLOB,
         pinned_G_SHA=G_SHA, pinned_K_SHA=K_SHA,
         full_dim=12, flat_dim=8, Krylov_dim=4,
         physical_W="1,3,2,3,3,2,2,2",
         scientific_gate="EXACT_PROJECTED_PENCIL_ONLY")

    emit("Y137_H12_MOD_POLYNOMIAL",
         full_degree=len(p12) - 1, reduced_degree=len(p8) - 1,
         detW=detW, exact_lambda_72_multiplicity=4,
         full_vs_reduced_coefficients="13_OF_13_EXACT",
         full_coefficients_sha256=sha_poly(p12),
         reduced_coefficients_sha256=sha_poly(p8),
         reduced_coefficients=",".join(str(v) for v in p8),
         full_coefficients=",".join(str(v) for v in p12),
         original_Wilson_weight="HOLD")
    emit("Y137_H12_MOD_GRAM", full_12x12_leading_minors="12_OF_12_POSITIVE",
         max_31bit_primes=gp, det_CstarWinvC_strict_positive="PASS",
         det_CstarWinvC_num_bits=sdet.bit_length())

    counts = {}
    for z in (*E, *(x for _, lo, hi in RITZ for x in (lo, hi))):
        n, signs, maxp = leading_inertia(pencil(G, K, z))
        counts[z] = n
        eval12 = peval(p12, z)
        observed, used, bits = crt_signed_det(pencil(G, K, z))
        need(observed == eval12, "CRT_vs_full_Berkowitz_det")
        emit("Y137_H12_MOD_INERTIA", z_num=z, z_den=DEN,
             negatives=n, leading_signs=signs, max_31bit_primes=maxp,
             full_det_CRT_matches_polynomial="PASS")

    need(counts[E[0]] == 0 and counts[E[1]] == 1,
         "frozen_sample_inertia_changed")
    for k, lo, hi in RITZ:
        need(counts[lo] == k - 1 and counts[hi] == k
             and hi - lo == 1, "original_Ritz_inertia_not_replayed")

    emit("Y137_H12_MOD_VERDICT",
         modular_exact_determinants="PASS_BOUND_CERTIFIED",
         characteristic_Berkowitz="DIVISION_FREE_Z_POLYNOMIAL",
         generalized_pencil="PASS",
         factorization="EXACT_72_POWER4_TIMES_DEGREE8",
         original_two_Ritz_brackets="4_ENDPOINTS_EXACT",
         full_space_residual="NOT_COMPUTED",
         Wilson_weight="HOLD", issue_137="OPEN")


def toy():
    need(crt_signed_det([[1, 2], [3, 4]])[0] == -2,
         "negative_determinant_CRT_toy")
    need(crt_signed_det([[0, 1], [1, 0]])[0] == -1,
         "zero_pivot_CRT_toy")
    need(crt_signed_det([[3, 0], [0, 0]])[0] == 0,
         "zero_row_CRT_toy")
    a = [[(1,), (0, 1)], [(0, 1), (1,)]]
    need(berkowitz(a) == (1, 0, -1),
         "division_free_Berkowitz_polynomial_toy")
    need(not isprime(2147483645) and isprime(2147483647),
         "deterministic_prime_checker_toy")
    emit("Y137_H12_MOD_TOY", negative_CRT="PASS", zero_pivot="PASS",
         no_pivot_inverse_in_Z="PASS", Berkowitz_poly="PASS",
         deterministic_31bit_prime="PASS", Wilson_weight="HOLD")


if __name__ == "__main__":
    try:
        if sys.argv[1:] == ["toy"]:
            toy()
        elif sys.argv[1:] == ["real"]:
            main()
        else:
            need(False, "usage_toy_or_real")
    except (OSError, KeyError, ValueError, ZeroDivisionError) as exc:
        print("Y137_H12_MOD_REFUSE|reason=" + str(exc) + "|json=0", flush=True)
        raise SystemExit(1) from None
