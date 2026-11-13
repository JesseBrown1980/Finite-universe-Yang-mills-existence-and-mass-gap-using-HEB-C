#!/usr/bin/env python3
"""Issue #137: independent check of the inertia counts of the lift-free K3 replay.

Written after replay_k3.py ran (its counts were known), with a different exact method:
  * the trial matrices U and G of the three K3 points are captured again from the pinned,
    unmodified draft script, and their hashes must equal those of the replay's rows;
  * L_new = 6*(b*NEW_G - a*10^6)*U - 10^6*G is formed here;
  * negative eigenvalues are counted from the characteristic polynomial (Faddeev-LeVerrier in
    integers, every division exact) by Descartes' rule of signs on p(-x). For a real symmetric
    matrix all roots are real, so the rule gives the exact count; a zero constant term (a zero
    eigenvalue) is refused. The replay and the draft use the checker's inertia() instead;
  * the reflection sectors are split here with this file's own basis (flats 0..5 and
    flat6+flat7 even; flat6-flat7 odd) and the even/odd cross terms must vanish exactly.
Integer arithmetic only. No arguments.
usage: python3 -I -B check_k3.py
"""
import hashlib
import importlib.util
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPT = os.path.join(HERE, "src155", "y137_k3_sector_isolation.py")
CHECKER = os.path.join(ROOT, "independent", "finite_s3_3x4_r9_first_gap.py")
REPLAY = os.path.join(HERE, "RESULT-K3-LIFTFREE.hbp")
SCRIPT_SHA = "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff"
CHECKER_BLOB = "91bd1e80cbfcfb76198966aa177d097ecfbe8143"
REPLAY_SHA = "6b86dacf2465a561ef8d566c815d08e24c548a46e15e420bfdf67ed2212829ed"
OLD_G, NEW_G, PS = 94070673, 94068200, 1000000
POINTS = (699567503, 699686993, 699689591)
B, STEPS, SCALE, N3 = 10 ** 7, 12, 10 ** 12, 155378
EXPECT = {699567503: (2, 2, 0, 0), 699686993: (2, 2, 0, 0), 699689591: (3, 2, 0, 0)}


def out(label, **fields):
    print(label + "|" + "|".join(str(k) + "=" + str(v) for k, v in fields.items())
          + "|json=0", flush=True)


def refuse(label):
    print("LIFT_FREE_K3_CHECK_REFUSE|gate=" + label + "|json=0", flush=True)
    raise SystemExit(1)


def matmul(A, Bm):
    n = len(A)
    return [[sum(A[i][k] * Bm[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def charpoly(A):
    """Coefficients c[0..n] of det(xI - A), c[n] = 1 (Faddeev-LeVerrier, exact integers)."""
    n = len(A)
    c = [0] * (n + 1)
    c[n] = 1
    M = [[0] * n for _ in range(n)]
    for k in range(1, n + 1):
        M = matmul(A, M)
        for i in range(n):
            M[i][i] += c[n - k + 1]
        tr = sum(sum(A[i][j] * M[j][i] for j in range(n)) for i in range(n))
        if tr % k != 0:
            refuse("faddeev_leverrier_division_not_exact")
        c[n - k] = -(tr // k)
    return c


def negative_count(A):
    n = len(A)
    if any(A[i][j] != A[j][i] for i in range(n) for j in range(n)):
        refuse("matrix_not_symmetric")
    c = charpoly(A)
    if c[0] == 0:
        refuse("zero_eigenvalue")
    d = [c[i] if i % 2 == 0 else -c[i] for i in range(n + 1)]   # coefficients of p(-x)
    signs = [1 if v > 0 else -1 for v in d if v != 0]
    return sum(1 for i in range(1, len(signs)) if signs[i] != signs[i - 1])


def split(M):
    E = [[0] * 8 for _ in range(7)]
    for k in range(6):
        E[k][k] = 1
    E[6][6] = 1
    E[6][7] = 1
    o = [0, 0, 0, 0, 0, 0, 1, -1]
    Mo = [sum(M[i][j] * o[j] for j in range(8)) for i in range(8)]
    if any(sum(E[k][i] * Mo[i] for i in range(8)) != 0 for k in range(7)):
        refuse("even_odd_cross_terms_nonzero")
    ME = [[sum(E[p][i] * M[i][j] * E[q][j] for i in range(8) for j in range(8))
           for q in range(7)] for p in range(7)]
    odd = sum(o[i] * Mo[i] for i in range(8))
    if odd == 0:
        refuse("odd_form_zero")
    return ME, odd


def main():
    if len(sys.argv) != 1:
        raise SystemExit("usage: python3 -I -B check_k3.py   (no arguments)")
    if hashlib.sha256(open(SCRIPT, "rb").read()).hexdigest() != SCRIPT_SHA:
        refuse("draft_script_sha256")
    raw = open(CHECKER, "rb").read()
    if hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + bytes((0,)) + raw).hexdigest() \
            != CHECKER_BLOB:
        refuse("checker_git_blob")
    rep = open(REPLAY, "rb").read()
    if hashlib.sha256(rep).hexdigest() != REPLAY_SHA:
        refuse("replay_result_sha256")
    rows = {}
    for line in rep.decode("utf-8").split("\n"):
        if line.startswith("LIFT_FREE_K3_CALL|") and "|rounding=checker|" in line \
                and "|q_states=" + str(N3) + "|" in line:
            f = dict(p.split("=", 1) for p in line.split("|")[1:] if "=" in p)
            rows[int(f["z"].split("/")[0])] = f
    if set(rows) != set(POINTS):
        refuse("replay_rows_missing")

    work = tempfile.mkdtemp(prefix="y137k3chk_")
    shutil.copyfile(SCRIPT, os.path.join(work, "y137_k3_sector_isolation.py"))
    shutil.copyfile(CHECKER, os.path.join(work, "finite_s3_3x4_r9_first_gap.py"))
    spec = importlib.util.spec_from_file_location(
        "y137_k3_sector_isolation", os.path.join(work, "y137_k3_sector_isolation.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    original = mod.threshold_ball
    got = {}

    def capture(a, b, steps, scale, ball, floor_num, round_like_original=False, keep_y=False):
        r = original(a, b, steps, scale, ball, floor_num, round_like_original, keep_y)
        if (ball["n"] == N3 and b == B and steps == STEPS and scale == SCALE
                and floor_num == OLD_G and not round_like_original):
            got[a] = ([row[:] for row in r["U"]], [row[:] for row in r["G"]],
                      r["hu"], r["hg"])
        return r

    mod.threshold_ball = capture
    mod.main()
    if set(got) != set(POINTS):
        refuse("K3_matrices_not_captured")

    ok_all = True
    for a in POINTS:
        U, G, hu, hg = got[a]
        if hu != rows[a]["U_sha256"] or hg != rows[a]["G_sha256"]:
            refuse("U_or_G_hash_differs_from_the_replay")
        gamma = B * NEW_G - a * PS
        if gamma <= 0:
            refuse("gamma_not_positive")
        L = [[6 * gamma * U[i][j] - PS * G[i][j] for j in range(8)] for i in range(8)]
        if mod.sha_matrix(L) != rows[a]["L_new_sha256"]:
            refuse("L_new_hash_differs_from_the_replay")
        LE, Lo = split(L)
        UE, Uo = split(U)
        mine = (negative_count(LE), negative_count(UE), int(Lo < 0), int(Uo < 0))
        tot = (negative_count(L), negative_count(U))
        theirs = (int(rows[a]["new_even_lower"]), int(rows[a]["new_even_upper"]),
                  int(rows[a]["new_odd_lower"]), int(rows[a]["new_odd_upper"]))
        ok = (mine == theirs == EXPECT[a] and tot == (mine[0] + mine[2], mine[1] + mine[3])
              and tot == (int(rows[a]["new_lower"]), int(rows[a]["upper"])))
        ok_all = ok_all and ok
        out("LIFT_FREE_K3_CHECK", z=str(a) + "/" + str(B), method="charpoly_and_Descartes",
            total_lower=tot[0], total_upper=tot[1], even_lower=mine[0], even_upper=mine[1],
            odd_lower=mine[2], odd_upper=mine[3],
            replay=",".join(str(x) for x in theirs), agree=int(ok),
            U_sha256=hu, G_sha256=hg, L_new_sha256=rows[a]["L_new_sha256"])
    if not ok_all:
        refuse("counts_differ")
    out("LIFT_FREE_K3_CHECK_VERDICT", status="PRIMARY_PASS",
        statement="at z0 = 699567503/10^7 exactly 2 even levels and no odd level lie below z0; "
        "E3_even >= 699686993/10^7; E_odd >= 699689591/10^7",
        floor=str(NEW_G) + "/1000000 lift-free (PR 173)", points=3, agree=3,
        replay_result_sha256=REPLAY_SHA)


if __name__ == "__main__":
    main()
