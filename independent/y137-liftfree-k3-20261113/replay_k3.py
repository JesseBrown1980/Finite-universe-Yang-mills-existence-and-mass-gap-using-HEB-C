#!/usr/bin/env python3
"""Issue #137: the K3 reflection-sector isolation of draft #155, read on the lift-free floor.

Version 2 of this file (the repository's no-float gate refuses a store into a module, which
version 1 used to observe the draft's calls; version 1 is kept as v1/replay_k3_v1.py with its
output). Nothing is stored into the draft module here:
  1. the draft's main() runs as written, with the old floor, and must write the draft receipt
     byte for byte;
  2. the K3 ball is built again by the draft's own functions (k3_common.build_k3) and the
     draft's threshold_ball is called at the three original points with the old floor; its U,
     G and L hashes and its counts must equal the rows of the reproduced draft receipt, which
     shows these are the draft's matrices;
  3. U and G do not depend on the floor, so L_new = 6*(b*NEW_G - a*10^6)*U - 10^6*G is formed
     from the same U and G; its inertia and sector counts are taken with the draft's own
     functions.
Integer arithmetic only. No arguments.   usage: python3 -I -B replay_k3.py
"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I leaves it out
import k3_common as k  # noqa: E402
import y137_k3_sector_isolation as mod  # noqa: E402  the pinned copy; k3_common put its directory first

RESULT = os.path.join(k.ROOT, "independent", "y142-floor-word-search-20261113",
                      "RESULT-WORD-SEARCH.hbp")
RESULT_BLOB = "57de51858e6a44dadd51c6e8419a549343145038"
RECEIPT_SHA = "cf91b9e4d842698d4972ac8df6ff6210bd3f439f561a354bca2954aac36716ef"
Z0, Z1, Z2 = k.POINTS
LADDER = (699686000, 699680000, 699650000, 699600000)
ROWS = []


def emit(label, **fields):
    row = label + "|" + "|".join(str(a) + "=" + str(v) for a, v in fields.items()) + "|json=0"
    ROWS.append(row)
    print(row, flush=True)


def fields_of(line):
    return dict(p.split("=", 1) for p in line.split("|")[1:] if "=" in p)


def main():
    if k.blob(RESULT) != RESULT_BLOB:
        k.refuse("liftfree_result_git_blob")
    text = open(RESULT, "rb").read().decode("utf-8")
    if "gamma=940682/10000|" not in text or "pinned_verifier=GATE_REQUIRED_PASS|" not in text:
        k.refuse("liftfree_result_value")
    if not (k.NEW_G * 10000 == 940682 * k.PS and k.NEW_G < k.OLD_G):
        k.refuse("liftfree_floor_number")
    work = k.WORK
    c = mod.c
    emit("LIFT_FREE_K3_BEGIN", version=2, draft_script_sha256=k.SCRIPT_SHA,
         checker_git_blob=k.CHECKER_BLOB, liftfree_result_git_blob=RESULT_BLOB,
         old_floor=str(k.OLD_G) + "/1000000", new_floor=str(k.NEW_G) + "/1000000",
         draft_script_modified="NO", stores_into_the_draft_module=0)

    mod.main()
    raw = open(os.path.join(work, mod.OUT_NAME), "rb").read()
    got = hashlib.sha256(raw).hexdigest()
    emit("LIFT_FREE_K3_DRAFT_RECEIPT", sha256=got, expected=RECEIPT_SHA,
         byte_identical=int(got == RECEIPT_SHA))
    if got != RECEIPT_SHA:
        k.refuse("draft_receipt_not_reproduced")
    draft = {}
    for line in raw.decode("utf-8").split("\n"):
        if line.startswith("Y137_K3_SECTOR|ball=K3|"):
            f = fields_of(line)
            draft[int(f["z"].split("/")[0])] = f
    if set(draft) != set(k.POINTS):
        k.refuse("draft_receipt_K3_rows")

    ball3 = k.build_k3()
    seen = {}
    for a in k.POINTS:
        r = mod.threshold_ball(a, k.K3_B, k.K3_STEPS, k.K3_SCALE, ball3, k.OLD_G)
        so = mod.sectors(r)
        d = draft[a]
        same = ((r["hu"], r["hg"], r["hl"]) == (d["U_sha256"], d["G_sha256"], d["L_sha256"])
                and (so["even_lower"], so["even_upper"], so["odd_lower"], so["odd_upper"])
                == (int(d["even_lower_count"]), int(d["even_upper_count"]),
                    int(d["odd_lower_count"]), int(d["odd_upper_count"])))
        if not same:
            k.refuse("old_floor_matrices_differ_from_the_draft_receipt")
        L = k.lower_for(a, k.NEW_G, r["U"], r["G"])
        nlo = c.inertia(L)
        sn = mod.sectors(dict(L=L, U=r["U"], nlo=nlo, nhi=r["nhi"]))
        if nlo < r["nlo"]:
            k.refuse("new_lower_count_below_old_lower_count")
        seen[a] = (sn["even_lower"], sn["even_upper"], sn["odd_lower"], sn["odd_upper"])
        emit("LIFT_FREE_K3_POINT", z=str(a) + "/" + str(k.K3_B), steps=k.K3_STEPS,
             scale="10^12", rounding="checker", q_states=ball3["n"],
             old_total_lower=r["nlo"], new_total_lower=nlo, total_upper=r["nhi"],
             old_counts=",".join(str(so[x]) for x in ("even_lower", "even_upper",
                                                      "odd_lower", "odd_upper")),
             new_even_lower=sn["even_lower"], new_even_upper=sn["even_upper"],
             new_odd_lower=sn["odd_lower"], new_odd_upper=sn["odd_upper"],
             same_U_G_L_old_as_the_draft_receipt=1, U_sha256=r["hu"], G_sha256=r["hg"],
             L_old_sha256=r["hl"], L_new_sha256=mod.sha_matrix(L))

    at_z0 = seen[Z0] == (2, 2, 0, 0)
    bound = None
    if seen[Z1][0] == 2 and seen[Z1][2] == 0:
        bound = Z1
    else:
        for a in LADDER:
            r = mod.threshold_ball(a, k.K3_B, k.K3_STEPS, k.K3_SCALE, ball3, k.NEW_G)
            s = mod.sectors(r)
            emit("LIFT_FREE_K3_LADDER", z=str(a) + "/" + str(k.K3_B),
                 even_lower=s["even_lower"], even_upper=s["even_upper"],
                 odd_lower=s["odd_lower"], odd_upper=s["odd_upper"], U_sha256=r["hu"],
                 G_sha256=r["hg"], L_new_sha256=r["hl"])
            if s["even_lower"] == 2 and s["odd_lower"] == 0:
                bound = a
                break
    odd_bound = Z2 if seen[Z2][2] == 0 else bound
    primary = at_z0 and bound == Z1 and seen[Z2] == (3, 2, 0, 0)
    holds = at_z0 and bound is not None and bound > Z0
    emit("LIFT_FREE_K3_VERDICT",
         status="ISOLATION_HOLDS_LIFT_FREE" if holds else "ISOLATION_NOT_ESTABLISHED",
         outcome=("PRIMARY_PASS" if primary else
                  "PRIMARY_CERTIFICATE_NOT_ESTABLISHED_FALLBACK_PASS" if holds else
                  "CERTIFICATE_NOT_ESTABLISHED"),
         z0=str(Z0) + "/" + str(k.K3_B),
         even_levels_below_z0="2..2" if at_z0 else "see_POINT_rows",
         odd_levels_below_z0="0..0" if at_z0 else "see_POINT_rows",
         E3_even_GE="NA" if bound is None else str(bound) + "/" + str(k.K3_B),
         E_odd_GE="NA" if odd_bound is None else str(odd_bound) + "/" + str(k.K3_B),
         floor="lift-free_" + str(k.NEW_G) + "/1000000_(PR_173)",
         draft_open_items="UNCHANGED", Wilson_first_weight="OPEN")
    emit("LIFT_FREE_K3_COMPLETE", points=3, rows=len(ROWS) + 1)


if __name__ == "__main__":
    main()
