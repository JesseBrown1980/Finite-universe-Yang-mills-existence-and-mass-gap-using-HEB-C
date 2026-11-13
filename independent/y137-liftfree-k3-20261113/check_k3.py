#!/usr/bin/env python3
"""Issue #137: independent check of the inertia counts of the lift-free K3 replay.

Written after the first replay ran (its counts were known to the writing seat): the method is
independent, the check is not blind. MATRICES-K3.hbp holds the exact matrices for a blind
recount. What this file does:
  * the trial matrices U and G of the three K3 points are computed again from the pinned,
    unmodified draft script; their hashes must equal those of the replay's rows;
  * L_new = 6*(b*NEW_G - a*10^6)*U - 10^6*G is formed here and hashed against the replay's;
  * negative eigenvalues are counted from the characteristic polynomial (Faddeev-LeVerrier in
    integers, every division exact) by Descartes' rule of signs on p(-x). For a real symmetric
    matrix all roots are real, so the rule gives the exact count; a zero constant term (a zero
    eigenvalue) is refused. The replay and the draft use the #136 checker's inertia() instead;
  * the reflection sectors are split with this file's own basis (flats 0..5 and flat6+flat7
    even; flat6-flat7 odd) and the even/odd cross terms must vanish exactly.
Integer arithmetic only. No arguments.   usage: python3 -I -B check_k3.py
"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I leaves it out
import k3_common as k  # noqa: E402
import y137_k3_sector_isolation as mod  # noqa: E402  the pinned copy; k3_common put its directory first

REPLAY = os.path.join(k.HERE, "RESULT-K3-LIFTFREE.hbp")
EXPECT = {699567503: (2, 2, 0, 0), 699686993: (2, 2, 0, 0), 699689591: (3, 2, 0, 0)}


def out(label, **fields):
    print(label + "|" + "|".join(str(a) + "=" + str(v) for a, v in fields.items())
          + "|json=0", flush=True)


def matmul(A, Bm):
    n = len(A)
    return [[sum(A[i][t] * Bm[t][j] for t in range(n)) for j in range(n)] for i in range(n)]


def charpoly(A):
    """Coefficients c[0..n] of det(xI - A), c[n] = 1 (Faddeev-LeVerrier, exact integers)."""
    n = len(A)
    c = [0] * (n + 1)
    c[n] = 1
    M = [[0] * n for _ in range(n)]
    for step in range(1, n + 1):
        M = matmul(A, M)
        for i in range(n):
            M[i][i] += c[n - step + 1]
        tr = sum(sum(A[i][j] * M[j][i] for j in range(n)) for i in range(n))
        if tr % step != 0:
            k.refuse("faddeev_leverrier_division_not_exact")
        c[n - step] = -(tr // step)
    return c


def negative_count(A):
    n = len(A)
    if any(A[i][j] != A[j][i] for i in range(n) for j in range(n)):
        k.refuse("matrix_not_symmetric")
    c = charpoly(A)
    if c[0] == 0:
        k.refuse("zero_eigenvalue")
    d = [c[i] if i % 2 == 0 else -c[i] for i in range(n + 1)]   # coefficients of p(-x)
    signs = [1 if v > 0 else -1 for v in d if v != 0]
    return sum(1 for i in range(1, len(signs)) if signs[i] != signs[i - 1])


def split(M):
    E = [[0] * 8 for _ in range(7)]
    for t in range(6):
        E[t][t] = 1
    E[6][6] = 1
    E[6][7] = 1
    o = [0, 0, 0, 0, 0, 0, 1, -1]
    Mo = [sum(M[i][j] * o[j] for j in range(8)) for i in range(8)]
    if any(sum(E[t][i] * Mo[i] for i in range(8)) != 0 for t in range(7)):
        k.refuse("even_odd_cross_terms_nonzero")
    ME = [[sum(E[p][i] * M[i][j] * E[q][j] for i in range(8) for j in range(8))
           for q in range(7)] for p in range(7)]
    odd = sum(o[i] * Mo[i] for i in range(8))
    if odd == 0:
        k.refuse("odd_form_zero")
    return ME, odd


def main():
    rep = open(REPLAY, "rb").read()
    rows = {}
    for line in rep.decode("utf-8").split("\n"):
        if line.startswith("LIFT_FREE_K3_POINT|"):
            f = dict(p.split("=", 1) for p in line.split("|")[1:] if "=" in p)
            rows[int(f["z"].split("/")[0])] = f
    if set(rows) != set(k.POINTS):
        k.refuse("replay_rows_missing")
    work = k.WORK
    ball3 = k.build_k3()
    ok_all = True
    for a in k.POINTS:
        r = mod.threshold_ball(a, k.K3_B, k.K3_STEPS, k.K3_SCALE, ball3, k.OLD_G)
        U, G = r["U"], r["G"]
        if r["hu"] != rows[a]["U_sha256"] or r["hg"] != rows[a]["G_sha256"]:
            k.refuse("U_or_G_hash_differs_from_the_replay")
        L = k.lower_for(a, k.NEW_G, U, G)
        if mod.sha_matrix(L) != rows[a]["L_new_sha256"]:
            k.refuse("L_new_hash_differs_from_the_replay")
        LE, Lo = split(L)
        UE, Uo = split(U)
        mine = (negative_count(LE), negative_count(UE), int(Lo < 0), int(Uo < 0))
        tot = (negative_count(L), negative_count(U))
        theirs = (int(rows[a]["new_even_lower"]), int(rows[a]["new_even_upper"]),
                  int(rows[a]["new_odd_lower"]), int(rows[a]["new_odd_upper"]))
        ok = (mine == theirs == EXPECT[a] and tot == (mine[0] + mine[2], mine[1] + mine[3])
              and tot == (int(rows[a]["new_total_lower"]), int(rows[a]["total_upper"])))
        ok_all = ok_all and ok
        out("LIFT_FREE_K3_CHECK", z=str(a) + "/" + str(k.K3_B),
            method="charpoly_and_Descartes", total_lower=tot[0], total_upper=tot[1],
            even_lower=mine[0], even_upper=mine[1], odd_lower=mine[2], odd_upper=mine[3],
            replay=",".join(str(x) for x in theirs), agree=int(ok),
            U_sha256=r["hu"], G_sha256=r["hg"], L_new_sha256=rows[a]["L_new_sha256"])
    if not ok_all:
        k.refuse("counts_differ")
    out("LIFT_FREE_K3_CHECK_VERDICT", status="PRIMARY_PASS",
        statement="at z0 = 699567503/10^7 exactly 2 even levels and no odd level lie below z0; "
        "E3_even >= 699686993/10^7; E_odd >= 699689591/10^7",
        floor=str(k.NEW_G) + "/1000000 lift-free (PR 173)", points=3, agree=3,
        replay_result_sha256=hashlib.sha256(rep).hexdigest())


if __name__ == "__main__":
    main()
