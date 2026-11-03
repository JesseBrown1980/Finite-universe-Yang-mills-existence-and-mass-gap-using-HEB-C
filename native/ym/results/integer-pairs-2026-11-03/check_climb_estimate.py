#!/usr/bin/env python3
# perron_climb_integer.py's estimate(), read out of its source and run on the points of every CLIMB_ESTIMATE row the recorded climbs printed.
# The 3x4 store takes no pass here: the function needs only the three points. usage: check_climb_estimate.py   Integer only, json=0.
import ast
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "3x4_stream", "perron")
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
from intpair import IntPair, qdiv  # noqa: E402

path = os.path.join(P, "perron_climb_integer.py")
tree = ast.parse(open(path, encoding="utf-8").read())
function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "estimate")
scope = {"F": IntPair, "qdiv": qdiv}
exec(compile(ast.Module([function], []), path, "exec"), scope)
bad = 0
for name in ("CLIMB-local-restart.hbp", "HOSTED-CLIMB-41448187715.hbp"):
    for line in open(os.path.join(P, name), encoding="utf-8"):
        if line.startswith("CLIMB_ESTIMATE|"):
            f = dict(x.split("=", 1) for x in line.strip().split("|")[1:] if "=" in x)
            points = [tuple(int(v) for v in pt.split(":")) for pt in f["from_points"].split(",")]
            got = scope["estimate"](points)
            same = 1 if got == int(f["level_estimate_milli"]) else 0
            bad += 1 - same
            print("CLIMB_ESTIMATE_CHECK|file=%s|recorded=%s|from_points=%s|got=%s|same=%d|json=0" % (name, f["level_estimate_milli"], f["from_points"], got, same))
sys.exit(1 if bad else 0)
