#!/usr/bin/env python3
"""Issue #137: print the exact 8x8 trial matrices U and G of the three K3 points.

For a recount by a seat that has not seen how the counts were derived: with these integers,
L(floor) = 6*(b*floor_num - a*10^6)*U - 10^6*G can be formed and its inertia taken by any exact
method, without rebuilding the K3 ball. The matrices come from the pinned, unmodified draft
script; sha_matrix is sha256 of the 64 entries in row order joined by "|". Integers only.
usage: python3 -I -B dump_k3_matrices.py | grep '^K3MAT' > MATRICES-K3.hbp     (no arguments)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I leaves it out
import k3_common as k  # noqa: E402
import y137_k3_sector_isolation as mod  # noqa: E402  the pinned copy; k3_common put its directory first


def main():
    work = k.WORK
    ball3 = k.build_k3()
    print("K3MATHDR|points=3|z_den=" + str(k.K3_B) + "|steps=12|scale=10^12|rounding=checker"
          "|matrices=U_and_G_8x8_symmetric_exact_integers|flat_order=that_of_the_draft_script"
          "|reflection=flats_0..5_fixed,_flat6<->flat7|L=6*(b*floor_num-a*10^6)*U-10^6*G"
          "|draft_script_sha256=" + k.SCRIPT_SHA + "|json=0")
    for a in k.POINTS:
        r = mod.threshold_ball(a, k.K3_B, k.K3_STEPS, k.K3_SCALE, ball3, k.OLD_G)
        for name, M, h in (("U", r["U"], r["hu"]), ("G", r["G"], r["hg"])):
            for i in range(8):
                print("K3MAT|z_num=" + str(a) + "|matrix=" + name + "|row=" + str(i) + "|"
                      + ",".join(str(v) for v in M[i]) + "|json=0")
            print("K3MATSHA|z_num=" + str(a) + "|matrix=" + name + "|sha_matrix=" + h
                  + "|json=0")
    print("K3MATEND|rows=56|json=0")


if __name__ == "__main__":
    main()
