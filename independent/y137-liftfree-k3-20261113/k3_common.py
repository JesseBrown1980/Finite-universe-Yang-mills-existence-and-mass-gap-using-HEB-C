#!/usr/bin/env python3
"""Shared loader for the lift-free K3 replay, its checker and the matrix dump (issue #137).

The draft script of PR #155 is pinned by sha256 and the merged #136 checker by git blob. Both
are copied into a fresh directory when this file is imported, and the draft script is then
imported from there by a plain import, unmodified; nothing is stored into the module. The K3 ball is built by calling the
draft's own functions in the order its main() calls them. Integer arithmetic only.
"""
import hashlib
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPT = os.path.join(HERE, "src155", "y137_k3_sector_isolation.py")
CHECKER = os.path.join(ROOT, "independent", "finite_s3_3x4_r9_first_gap.py")
SCRIPT_SHA = "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff"
CHECKER_BLOB = "91bd1e80cbfcfb76198966aa177d097ecfbe8143"
OLD_G = 94070673
NEW_G = 94068200
PS = 1000000
POINTS = (699567503, 699686993, 699689591)
K3_B, K3_STEPS, K3_SCALE = 10 ** 7, 12, 10 ** 12
K3_SIZES = (155378, 1356528, 1985218)


def refuse(label):
    print("LIFT_FREE_K3_REFUSE|gate=" + label + "|json=0", flush=True)
    raise SystemExit(1)


def blob(path):
    raw = open(path, "rb").read()
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + bytes((0,)) + raw).hexdigest()


if len(sys.argv) != 1:
    raise SystemExit("no arguments")
if hashlib.sha256(open(SCRIPT, "rb").read()).hexdigest() != SCRIPT_SHA:
    refuse("draft_script_sha256")
if blob(CHECKER) != CHECKER_BLOB:
    refuse("checker_git_blob")
WORK = tempfile.mkdtemp(prefix="y137k3_")
shutil.copyfile(SCRIPT, os.path.join(WORK, "y137_k3_sector_isolation.py"))
shutil.copyfile(CHECKER, os.path.join(WORK, "finite_s3_3x4_r9_first_gap.py"))
sys.path.insert(0, WORK)
import y137_k3_sector_isolation as mod  # noqa: E402  (the pinned copy in the fresh directory)

if os.path.dirname(os.path.abspath(mod.__file__)) != os.path.abspath(WORK):
    refuse("draft_module_not_from_the_fresh_directory")
if not (mod.FLOOR_NUM == OLD_G and mod.PS == PS and mod.K3_POINTS == POINTS
        and mod.K3_B == K3_B and mod.K3_STEPS == K3_STEPS and mod.K3_SCALE == K3_SCALE):
    refuse("draft_constants")


def build_k3():
    """The K3 ball, by the draft's own functions in the order of its main()."""
    c = mod.c
    w, m, adj, q_flat, outer = c.graph()
    states, flat, layer_sizes = mod.rebuild_states()
    if not (len(states) == len(w) == 8042 and layer_sizes == [8, mod.SHELL1, 7770]):
        refuse("K2_layers")
    where = {k: i for i, k in enumerate(states)}
    ball2 = mod.ball_from_checker(w, m, adj, q_flat, outer)
    ball3, ex = mod.build_k3(states, where, w, m, adj, outer, ball2["C"])
    if (ball3["n"], len(ball3["oj"]), ball3["nf"]) != K3_SIZES:
        refuse("K3_sizes")
    return ball3


def lower_for(a, floor_num, U, G):
    gamma = K3_B * floor_num - a * PS
    if gamma <= 0:
        refuse("gamma_not_positive")
    return [[6 * gamma * U[i][j] - PS * G[i][j] for j in range(8)] for i in range(8)]
