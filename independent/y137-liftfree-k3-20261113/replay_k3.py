#!/usr/bin/env python3
"""Issue #137: the K3 reflection-sector isolation of draft #155, read on the lift-free floor.

The draft script is imported unmodified (pinned by sha256) from a fresh directory that holds
only it and the merged checker (pinned by git blob). Its main() runs as written with the old
floor and must write the draft receipt byte for byte. Every call of its threshold_ball is
observed: U and G do not depend on the floor, so the lower matrix for the new floor,
    L_new = 6 * (b*NEW_G - a*10^6) * U - 10^6 * G,
is formed from the same U and G, and its inertia and sector counts are taken with the draft
script's own functions. Integer arithmetic only. No arguments.
usage: python3 -I -B replay_k3.py
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
RESULT = os.path.join(ROOT, "independent", "y142-floor-word-search-20261113",
                      "RESULT-WORD-SEARCH.hbp")
SCRIPT_SHA = "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff"
CHECKER_BLOB = "91bd1e80cbfcfb76198966aa177d097ecfbe8143"
RESULT_BLOB = "57de51858e6a44dadd51c6e8419a549343145038"
RECEIPT_SHA = "cf91b9e4d842698d4972ac8df6ff6210bd3f439f561a354bca2954aac36716ef"
OLD_G = 94070673
NEW_G = 94068200
PS = 1000000
Z0, Z1, Z2 = 699567503, 699686993, 699689591
LADDER = (699686000, 699680000, 699650000, 699600000)
K3_B, K3_STEPS, K3_SCALE, K3_N = 10 ** 7, 12, 10 ** 12, 155378
ROWS = []


def emit(label, **fields):
    row = label + "|" + "|".join(str(k) + "=" + str(v) for k, v in fields.items()) + "|json=0"
    ROWS.append(row)
    print(row, flush=True)


def refuse(label):
    print("LIFT_FREE_K3_REFUSE|gate=" + label + "|json=0", flush=True)
    raise SystemExit(1)


def blob(path):
    raw = open(path, "rb").read()
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + bytes((0,)) + raw).hexdigest()


def main():
    if len(sys.argv) != 1:
        raise SystemExit("usage: python3 -I -B replay_k3.py   (no arguments)")
    if hashlib.sha256(open(SCRIPT, "rb").read()).hexdigest() != SCRIPT_SHA:
        refuse("draft_script_sha256")
    if blob(CHECKER) != CHECKER_BLOB:
        refuse("checker_git_blob")
    if blob(RESULT) != RESULT_BLOB:
        refuse("liftfree_result_git_blob")
    text = open(RESULT, "rb").read().decode("utf-8")
    if "gamma=940682/10000|" not in text or "pinned_verifier=GATE_REQUIRED_PASS|" not in text:
        refuse("liftfree_result_value")
    if not (NEW_G * 10000 == 940682 * PS and NEW_G < OLD_G):
        refuse("liftfree_floor_number")

    work = tempfile.mkdtemp(prefix="y137k3_")
    shutil.copyfile(SCRIPT, os.path.join(work, "y137_k3_sector_isolation.py"))
    shutil.copyfile(CHECKER, os.path.join(work, "finite_s3_3x4_r9_first_gap.py"))
    spec = importlib.util.spec_from_file_location(
        "y137_k3_sector_isolation", os.path.join(work, "y137_k3_sector_isolation.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    c = mod.c
    if not (mod.FLOOR_NUM == OLD_G and mod.PS == PS and mod.K3_POINTS == (Z0, Z1, Z2)
            and mod.K3_B == K3_B and mod.K3_STEPS == K3_STEPS and mod.K3_SCALE == K3_SCALE):
        refuse("draft_constants")
    emit("LIFT_FREE_K3_BEGIN", draft_script_sha256=SCRIPT_SHA, checker_git_blob=CHECKER_BLOB,
         liftfree_result_git_blob=RESULT_BLOB, old_floor=str(OLD_G) + "/1000000",
         new_floor=str(NEW_G) + "/1000000", draft_script_modified="NO")

    original = mod.threshold_ball
    seen = {}
    state = {"ball3": None, "calls": 0}

    def new_side(a, b, r):
        gamma = b * NEW_G - a * PS
        if gamma <= 0:
            return None
        U, G = r["U"], r["G"]
        L = [[6 * gamma * U[i][j] - PS * G[i][j] for j in range(8)] for i in range(8)]
        nlo = c.inertia(L)
        out = dict(nlo=nlo, nhi=r["nhi"], hl=mod.sha_matrix(L), sectors=None)
        try:
            out["sectors"] = mod.sectors(dict(L=L, U=U, nlo=nlo, nhi=r["nhi"]))
        except SystemExit:
            out["sectors"] = None
        return out

    def observed(a, b, steps, scale, ball, floor_num, round_like_original=False,
                 keep_y=False):
        r = original(a, b, steps, scale, ball, floor_num, round_like_original, keep_y)
        state["calls"] += 1
        if floor_num != OLD_G:
            return r
        n = new_side(a, b, r)
        is_k3 = (ball["n"] == K3_N and b == K3_B and steps == K3_STEPS and scale == K3_SCALE)
        if is_k3:
            state["ball3"] = ball
        if n is not None:
            s = n["sectors"]
            emit("LIFT_FREE_K3_CALL", call=state["calls"], q_states=ball["n"],
                 z=str(a) + "/" + str(b), steps=steps,
                 rounding="original" if round_like_original else "checker",
                 old_lower=r["nlo"], new_lower=n["nlo"], upper=r["nhi"],
                 new_even_lower="NA" if s is None else s["even_lower"],
                 new_even_upper="NA" if s is None else s["even_upper"],
                 new_odd_lower="NA" if s is None else s["odd_lower"],
                 new_odd_upper="NA" if s is None else s["odd_upper"],
                 U_sha256=r["hu"], G_sha256=r["hg"], L_old_sha256=r["hl"],
                 L_new_sha256=n["hl"])
            if n["nlo"] < r["nlo"]:
                refuse("new_lower_count_below_old_lower_count")
            if is_k3 and not round_like_original and s is not None:
                seen[a] = (s["even_lower"], s["even_upper"], s["odd_lower"], s["odd_upper"])
        return r

    mod.threshold_ball = observed
    mod.main()
    mod.threshold_ball = original

    got = hashlib.sha256(open(os.path.join(work, mod.OUT_NAME), "rb").read()).hexdigest()
    emit("LIFT_FREE_K3_DRAFT_RECEIPT", sha256=got, expected=RECEIPT_SHA,
         byte_identical=int(got == RECEIPT_SHA))
    if got != RECEIPT_SHA:
        refuse("draft_receipt_not_reproduced")
    if set(seen) != {Z0, Z1, Z2}:
        refuse("K3_points_not_all_observed")

    emit("LIFT_FREE_K3_POINTS", order="even_lower,even_upper,odd_lower,odd_upper",
         z0=",".join(str(x) for x in seen[Z0]), z1=",".join(str(x) for x in seen[Z1]),
         z2=",".join(str(x) for x in seen[Z2]), old="2,2,0,0;2,2,0,0;3,2,0,0")
    at_z0 = seen[Z0] == (2, 2, 0, 0)
    bound = None
    if seen[Z1][0] == 2 and seen[Z1][2] == 0:
        bound = Z1
    else:
        for a in LADDER:
            r = original(a, K3_B, K3_STEPS, K3_SCALE, state["ball3"], NEW_G)
            s = mod.sectors(r)
            emit("LIFT_FREE_K3_LADDER", z=str(a) + "/" + str(K3_B), even_lower=s["even_lower"],
                 even_upper=s["even_upper"], odd_lower=s["odd_lower"],
                 odd_upper=s["odd_upper"], U_sha256=r["hu"], G_sha256=r["hg"],
                 L_new_sha256=r["hl"])
            if s["even_lower"] == 2 and s["odd_lower"] == 0:
                bound = a
                break
    odd_bound = Z2 if seen[Z2][2] == 0 else bound
    holds = at_z0 and bound is not None and bound > Z0
    emit("LIFT_FREE_K3_VERDICT",
         status="ISOLATION_HOLDS_LIFT_FREE" if holds else "ISOLATION_NOT_ESTABLISHED",
         z0=str(Z0) + "/" + str(K3_B),
         even_levels_below_z0="2..2" if at_z0 else "see_POINTS",
         odd_levels_below_z0="0..0" if at_z0 else "see_POINTS",
         E3_even_GE="NA" if bound is None else str(bound) + "/" + str(K3_B),
         E_odd_GE="NA" if odd_bound is None else str(odd_bound) + "/" + str(K3_B),
         floor="lift-free_" + str(NEW_G) + "/1000000_(PR_173)",
         draft_open_items="UNCHANGED", Wilson_first_weight="OPEN")
    emit("LIFT_FREE_K3_COMPLETE", threshold_calls=state["calls"], rows=len(ROWS) + 1)
    data = ("\n".join(ROWS) + "\n").encode("utf-8")
    with open(os.path.join(work, "RESULT-K3-LIFTFREE.hbp"), "wb") as fh:
        fh.write(data)
    print("WROTE|" + os.path.join(work, "RESULT-K3-LIFTFREE.hbp") + "|sha256="
          + hashlib.sha256(data).hexdigest(), flush=True)


if __name__ == "__main__":
    main()
