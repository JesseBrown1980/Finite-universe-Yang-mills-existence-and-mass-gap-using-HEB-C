#!/usr/bin/env python3
"""Issue #137: write the exact 8x8 trial matrices U and G of the three K3 points to a file.

For a recount by a seat that has not seen how the counts were derived: with these integers,
L(floor) = 6*(b*floor_num - a*10^6)*U - 10^6*G can be formed and its inertia taken by any exact
method, without rebuilding the K3 ball. The matrices are captured from the pinned, unmodified
draft script and their hashes must equal those of the replay's rows. Integer arithmetic only.
usage: python3 -I -B dump_k3_matrices.py     (prints the rows; no arguments)
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
REPLAY_SHA = "6b86dacf2465a561ef8d566c815d08e24c548a46e15e420bfdf67ed2212829ed"
OLD_G = 94070673
POINTS = (699567503, 699686993, 699689591)
B, STEPS, SCALE, N3 = 10 ** 7, 12, 10 ** 12, 155378


def main():
    if len(sys.argv) != 1:
        raise SystemExit("usage: python3 -I -B dump_k3_matrices.py   (no arguments)")
    if hashlib.sha256(open(SCRIPT, "rb").read()).hexdigest() != SCRIPT_SHA:
        raise SystemExit("REFUSE draft_script_sha256")
    rep = open(REPLAY, "rb").read()
    if hashlib.sha256(rep).hexdigest() != REPLAY_SHA:
        raise SystemExit("REFUSE replay_result_sha256")
    text = rep.decode("utf-8")
    work = tempfile.mkdtemp(prefix="y137k3dump_")
    shutil.copyfile(SCRIPT, os.path.join(work, "y137_k3_sector_isolation.py"))
    shutil.copyfile(CHECKER, os.path.join(work, "finite_s3_3x4_r9_first_gap.py"))
    spec = importlib.util.spec_from_file_location(
        "y137_k3_sector_isolation", os.path.join(work, "y137_k3_sector_isolation.py"))
    mod = importlib.util.module_from_spec(spec)
    saved = sys.stdout
    sys.stdout = open(os.devnull, "w")
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
    sys.stdout = saved
    print("K3MATHDR|points=3|z_den=" + str(B) + "|steps=12|scale=10^12|rounding=checker"
          "|matrices=U_and_G_8x8_symmetric_exact_integers|flat_order=the_draft_script's"
          "|reflection=flats_0..5_fixed,_flat6<->flat7|L=6*(b*floor_num-a*10^6)*U-10^6*G"
          "|draft_script_sha256=" + SCRIPT_SHA + "|json=0")
    for a in POINTS:
        U, G, hu, hg = got[a]
        if ("U_sha256=" + hu) not in text or ("G_sha256=" + hg) not in text:
            raise SystemExit("REFUSE matrix_hash_not_in_replay_rows")
        for name, M, h in (("U", U, hu), ("G", G, hg)):
            for i in range(8):
                print("K3MAT|z_num=" + str(a) + "|matrix=" + name + "|row=" + str(i) + "|"
                      + ",".join(str(v) for v in M[i]) + "|json=0")
            print("K3MATSHA|z_num=" + str(a) + "|matrix=" + name + "|sha_matrix=" + h
                  + "|json=0")
    print("K3MATEND|rows=" + str(3 * 2 * 9 + 2) + "|json=0")


if __name__ == "__main__":
    main()
