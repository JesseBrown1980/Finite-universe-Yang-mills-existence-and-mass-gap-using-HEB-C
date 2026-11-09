#!/usr/bin/env python3
# negctl_gpt6.py (cloud seat, #137 fix pass 3): the two negative-control receipts of GPT-6's audit
# (issue #137 comment 6747959074, section 2). Toy matrices only: no r, no 3x4 model data.
# Python ints only (no float, fractions, decimal or math module). Run: python3 -I -B negctl_gpt6.py
# Sign convention of the package: B = -H_QP, X ~ A^-1 B, R = B - A X. GPT-6 writes F = H_QP = -B, so its X and R
# are the negatives of ours; every Gram, U, T, LO and UP value is the same.
import hashlib
import sys


def gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def q(n, d=1):
    if d == 0:
        raise ZeroDivisionError("zero denominator")
    if d < 0:
        n, d = -n, -d
    g = gcd(n, d)
    return (n // g, d // g)


def add(x, y):
    return q(x[0] * y[1] + y[0] * x[1], x[1] * y[1])


def sub(x, y):
    return q(x[0] * y[1] - y[0] * x[1], x[1] * y[1])


def mul(x, y):
    return q(x[0] * y[0], x[1] * y[1])


def div(x, y):
    return q(x[0] * y[1], x[1] * y[0])


def s(x):
    return "%d/%d" % x


def sign(x):
    return (x[0] > 0) - (x[0] < 0)


def lcm(a, b):
    return a // gcd(a, b) * b


def neg_count(m):
    # Sylvester-Jacobi on leading minors of a symmetric rational matrix; every minor must be nonzero.
    n = len(m)
    signs = [1]
    for k in range(1, n + 1):
        signs.append(sign(det([row[:k] for row in m[:k]])))
    if 0 in signs:
        return None
    return sum(1 for i in range(n) if signs[i] != signs[i + 1])


def det(m):
    # exact rational Gaussian elimination (small matrices only)
    m = [row[:] for row in m]
    n = len(m)
    d = (1, 1)
    for c in range(n):
        p = next((r for r in range(c, n) if m[r][c][0] != 0), None)
        if p is None:
            return (0, 1)
        if p != c:
            m[c], m[p] = m[p], m[c]
            d = q(-d[0], d[1])
        d = mul(d, m[c][c])
        for r in range(c + 1, n):
            f = div(m[r][c], m[c][c])
            m[r] = [sub(m[r][j], mul(f, m[c][j])) for j in range(n)]
    return d


def lo_le_up_identity(U, T, G, tau, gamma):
    # NOTE section 9: K b (g b - a d0) LO(a/b) = (g b - a d0)(b Uhat - a That) - d0 Ghat, for p = 1.
    a, b = tau
    g, d0 = gamma
    gap = g * b - a * d0
    lo = sub(sub(U, mul(tau, T)), div(G, sub(gamma, tau)))
    K = 1
    for x in (U, T, mul((b * b, 1), G)):
        K = lcm(K, x[1])
    Uh, Th, Gh = mul((K, 1), U), mul((K, 1), T), mul((K * b * b, 1), G)
    assert Uh[1] == Th[1] == Gh[1] == 1
    lhs = mul((K * b * gap, 1), lo)
    rhs = (gap * (b * Uh[0] - a * Th[0]) - d0 * Gh[0], 1)
    ok = lhs == rhs and gap > 0 and Gh[0] >= 0
    return ok, lo


def sha(b):
    return hashlib.sha256(b).hexdigest()


def out(line):
    print(line)


def toy_floor():
    # GPT-6 counterexample 1: H - z = [[1,-2],[-2,1]] at z = 0, P = {0}, Q = {1}, W = I.
    H = [[q(1), q(-2)], [q(-2), q(1)]]
    z = q(0)
    true_neg = neg_count(H)  # eigenvalues -1 and 3: one below z
    Hpp, Hqp, Hqq = H[0][0], H[1][0], H[1][1]
    B = q(-Hqp[0], Hqp[1])  # B = -H_QP = 2
    A = sub(Hqq, z)
    S_true = sub(sub(Hpp, z), div(mul(B, B), A))
    X = q(0)
    U = add(sub(sub(Hpp, mul(X, B)), mul(B, X)), mul(mul(X, Hqq), X))
    T = add(q(1), mul(X, X))
    R = sub(B, mul(A, X))
    G = mul(R, R)
    up = sub(U, mul(z, T))
    up_neg = 1 if sign(up) < 0 else 0
    # the honest source record and its pin (the toy analogue of #131's PERRON-BOUND.md and PERRON-RESULT.hbp)
    src_honest = b"TOY1-FLOOR-SOURCE|lambda_min_QHQ_GE=1/1|Q_dim=1|H_QQ=1/1|json=0\n"
    pin = sha(src_honest)
    src_forged = b"TOY1-FLOOR-SOURCE|lambda_min_QHQ_GE=100/1|Q_dim=1|H_QQ=1/1|json=0\n"

    def gate(asserted, source):
        # floor-source gate: (i) the source's sha256 equals the pin; (ii) the asserted floor equals the source's
        # value as a reduced integer pair; (iii) toy only, because Q is 1-dimensional: A(z) - (gamma - z) >= 0.
        h_ok = sha(source) == pin
        fields = dict(f.split("=", 1) for f in source.decode().strip().split("|")[1:])
        vn, vd = fields["lambda_min_QHQ_GE"].split("/")
        v_ok = q(int(vn), int(vd)) == asserted
        direct_ok = sign(sub(A, sub(asserted, z))) >= 0
        verdict = "PASS" if (h_ok and v_ok and direct_ok) else "REFUSE"
        return verdict, h_ok, v_ok, direct_ok

    out("NEGCTL|toy=1_wrong_floor|H_minus_z=[[1,-2],[-2,1]]|z=0|P=e0|Q=e1|W=I|true_neg_H_minus_z=%d|S_true=%s|B=%s|"
        "A=%s|X=%s|U=%s|T=%s|R=%s|G=%s|UP=%s|neg_UP=%d|json=0"
        % (true_neg, s(S_true), s(B), s(A), s(X), s(U), s(T), s(R), s(G), s(up), up_neg))
    cases = [("1a_asserted_100_honest_source", q(100), src_honest),
             ("1b_asserted_100_forged_source", q(100), src_forged),
             ("1c_control_true_floor_1", q(1), src_honest)]
    res = {}
    for name, gam, src in cases:
        ok_id, lo = lo_le_up_identity(U, T, G, z, gam)
        lo_neg = 1 if sign(lo) < 0 else 0
        claims_no_crossing = (up_neg == 0 and lo_neg == 0)
        false_positive = claims_no_crossing and true_neg >= 1
        v, h_ok, v_ok, d_ok = gate(gam, src)
        res[name] = (false_positive, v, lo_neg)
        out("NEGCTL|toy=1_wrong_floor|case=%s|gamma=%s|source_sha256=%s|pin=%s|LO=%s|neg_LO=%d|neg_UP=%d|"
            "certificate_algebra_LO_LE_UP_identity=%s|certificate_reads_no_crossing=%s|false_positive=%s|"
            "gate=floor_source|gate_hash=%s|gate_value=%s|gate_toy_direct_A_minus_gamma_GE_0=%s|gate_verdict=%s|json=0"
            % (name, s(gam), sha(src)[:16], pin[:16], s(lo), lo_neg, up_neg, "PASS" if ok_id else "FAIL",
               "YES" if claims_no_crossing else "NO", "PRODUCED" if false_positive else "NO",
               "PASS" if h_ok else "FAIL", "PASS" if v_ok else "FAIL", "PASS" if d_ok else "FAIL", v))
    ok = (res["1a_asserted_100_honest_source"][:2] == (True, "REFUSE")
          and res["1b_asserted_100_forged_source"][:2] == (True, "REFUSE")
          and res["1c_control_true_floor_1"] == (False, "PASS", 1))
    out("NEGCTL_RESULT|toy=1_wrong_floor|false_positive_produced_on_purpose=YES|refused_by=floor_source_gate|"
        "not_by=certificate_algebra|control_passes_and_reads_the_crossing=YES|receipt=%s|json=0"
        % ("PASS" if ok else "FAIL"))
    return ok


def toy_exterior():
    # GPT-6 counterexample 2: C = 9/10, F = (-1,0)^T, A = [[2,-1],[-1,1]], X_gpt6 = (-1/2,0)^T, z = 0, W = I.
    # As a graph: vertices P0 (flat), Q1 (inner, where X lives), Q2 (exterior); H_st = -c_st.
    names = ["P0", "Q1", "Q2"]
    Hfull = [[q(9, 10), q(-1), q(0)], [q(-1), q(2), q(-1)], [q(0), q(-1), q(1)]]
    z = q(0)
    true_neg = neg_count(Hfull)
    W = {"P0": q(1), "Q1": q(1), "Q2": q(1)}
    A = [[Hfull[1][1], Hfull[1][2]], [Hfull[2][1], Hfull[2][2]]]
    gamma = q(1, 4)
    Ag = [[sub(A[0][0], gamma), A[0][1]], [A[1][0], sub(A[1][1], gamma)]]
    floor_valid = neg_count(Ag) == 0
    detA = sub(mul(A[0][0], A[1][1]), mul(A[0][1], A[1][0]))
    Ainv00 = div(A[1][1], detA)
    B = [q(1), q(0)]  # B = -H_QP
    S_true = sub(Hfull[0][0], mul(mul(B[0], Ainv00), B[0]))
    X = {"Q1": q(1, 2)}  # ours = -X_gpt6
    inner = ["Q1"]
    # U0 = H_PP - X^T B - B^T X + X^T H_QQ X (X supported on Q1)
    U = add(sub(sub(Hfull[0][0], mul(X["Q1"], B[0])), mul(B[0], X["Q1"])), mul(mul(X["Q1"], Hfull[1][1]), X["Q1"]))
    T = add(q(1), mul(X["Q1"], X["Q1"]))
    R_inner = sub(B[0], mul(Hfull[1][1], X["Q1"]))  # R on Q1 at z = 0
    G_inner = mul(mul(W["Q1"], R_inner), R_inner)

    def writer_G(ext_list):
        # the certificate writer's exterior: R_e = sum_i c(e->i) X_i over its own list of exterior targets
        g = G_inner
        for e in ext_list:
            k = names.index(e)
            Re = q(0)
            for i in inner:
                c = q(-Hfull[k][names.index(i)][0], Hfull[k][names.index(i)][1])
                Re = add(Re, mul(c, X[i]))
            g = add(g, mul(mul(W[e], Re), Re))
        return g

    def regen():
        # exterior-regeneration gate: regenerate every move of every inner representative from H itself (the
        # definition), keep the targets outside P and the inner set with multiplicities, hash that multiset, and
        # recompute the exterior Gram through W_i c(i->e) / W_e, never reading the writer's exterior list.
        acc = {}
        lines = []
        tally = {}
        for i in inner:
            ki = names.index(i)
            for k, e in enumerate(names):
                if k == ki:
                    continue
                c = -Hfull[ki][k][0]
                assert Hfull[ki][k][1] == 1 and c >= 0
                if c == 0:
                    continue
                tally[i] = tally.get(i, 0) + c
                if e == "P0" or e in inner:
                    continue
                lines.append("%s>%s:%d\n" % (i, e, c))
                acc[e] = add(acc.get(e, q(0)), mul(mul(W[i], q(c)), X[i]))
        h = sha("".join(sorted(lines)).encode())
        g = G_inner
        rext = {}
        for e, a in acc.items():
            Re = div(a, W[e])
            rext[e] = Re
            g = add(g, mul(mul(W[e], Re), Re))
        return g, h, sorted(lines), tally, rext

    G_re, h_re, ms, tally, rext = regen()
    out("NEGCTL|toy=2_dropped_exterior|H_minus_z=[[9/10,-1,0],[-1,2,-1],[0,-1,1]]|z=0|P=P0|inner=Q1|exterior=Q2|W=I|"
        "true_neg_H_minus_z=%d|S_true=%s|gamma=%s|floor_valid_PD(A-gamma)=%s|X=(%s,0)|U=%s|T=%s|R=(%s,%s)|"
        "regen_multiset=%s|regen_multiset_sha256=%s|regen_tally_Q1=%d|regen_G=%s|json=0"
        % (true_neg, s(S_true), s(gamma), "YES" if floor_valid else "NO", s(X["Q1"]), s(U), s(T), s(R_inner),
           s(rext["Q2"]), ";".join(x.strip() for x in ms), h_re[:16], tally["Q1"], s(G_re)))
    cases = [("2a_exterior_row_dropped", []), ("2c_control_complete_exterior", ["Q2"])]
    res = {}
    for name, lst in cases:
        G = writer_G(lst)
        ok_id, lo = lo_le_up_identity(U, T, G, z, gamma)
        up = sub(U, mul(z, T))
        up_neg = 1 if sign(up) < 0 else 0
        lo_neg = 1 if sign(lo) < 0 else 0
        claims_no_crossing = (up_neg == 0 and lo_neg == 0)
        false_positive = claims_no_crossing and true_neg >= 1
        v = "PASS" if G == G_re else "REFUSE"
        res[name] = (false_positive, v, lo_neg)
        out("NEGCTL|toy=2_dropped_exterior|case=%s|writer_exterior_list=%s|writer_G=%s|UP=%s|LO=%s|neg_UP=%d|neg_LO=%d|"
            "certificate_algebra_LO_LE_UP_identity=%s|certificate_reads_no_crossing=%s|false_positive=%s|"
            "gate=exterior_regeneration|gate_G=%s|gate_verdict=%s|json=0"
            % (name, ",".join(lst) if lst else "EMPTY", s(G), s(up), s(lo), up_neg, lo_neg,
               "PASS" if ok_id else "FAIL", "YES" if claims_no_crossing else "NO",
               "PRODUCED" if false_positive else "NO", s(G_re), v))
    ok = (res["2a_exterior_row_dropped"][:2] == (True, "REFUSE")
          and res["2c_control_complete_exterior"] == (False, "PASS", 1))
    out("NEGCTL_RESULT|toy=2_dropped_exterior|false_positive_produced_on_purpose=YES|refused_by=exterior_regeneration_gate|"
        "not_by=certificate_algebra|control_passes_and_reads_the_crossing=YES|receipt=%s|json=0"
        % ("PASS" if ok else "FAIL"))
    return ok


def main():
    out("NEGCTL_HEADER|source=issue137_comment_6747959074_section_2|models=toy_2x2_and_toy_3x3_only|r=none|"
        "arithmetic=python_ints_only|json=0")
    a = toy_floor()
    b = toy_exterior()
    out("NEGCTL_END|receipts=2|both_PASS=%s|json=0" % ("YES" if (a and b) else "NO"))
    return 0 if (a and b) else 1


if __name__ == "__main__":
    sys.exit(main())
