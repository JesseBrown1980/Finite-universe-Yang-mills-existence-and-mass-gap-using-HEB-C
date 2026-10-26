#!/usr/bin/env python3
"""Rebuild every certificate of one lattice from committed backend shards only
(no tool is executed). Cluster intervals come from cluster_* shards whose
summary line says converged=1 (a WANT=12 shard that did not converge is kept
as evidence but not used); counts come from count_* shards. Each coupling found
is passed to shell_gap_cert.py --lattice LXxLY.
usage: rebuild_from_shards.py SHARDS_DIR LX LY        json=0
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    d, lx, ly = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    lat = "%dx%d" % (lx, ly)
    clusters, counts, rs = {}, [], set()
    for name in sorted(os.listdir(d)):
        txt = open(os.path.join(d, name, "run.hbp")).read()
        m = re.match(r"cluster_%d_%d_(-?1)_(-?1)_1_(\d+)_\d+_\d+$" % (lx, ly), name)
        if m and "|converged=1|" in txt:
            sx, sy, r = m.group(1), m.group(2), int(m.group(3))
            if (sx, sy, r) in clusters:
                print("REBUILD|L=%s|result=FAIL|reason=two_converged_cluster_shards|r=%d|json=0" % (lat, r))
                sys.exit(2)
            clusters[(sx, sy, r)] = ["YM%dX%d_S%s_%s_r%d_%s" % (lx, ly, sx, sy, r, l) for l in txt.splitlines()]
            rs.add(r)
        elif name.startswith("count_%d_%d_" % (lx, ly)):
            counts.append(txt)
    with tempfile.TemporaryDirectory() as tmp:
        cf, nf = os.path.join(tmp, "clusters.hbp"), os.path.join(tmp, "counts.hbp")
        open(cf, "w").write("\n".join(l for v in clusters.values() for l in v) + "\n")
        open(nf, "w").write("".join(counts))
        bad = 0
        for r in sorted(rs):
            res = subprocess.run([sys.executable, os.path.join(HERE, "shell_gap_cert.py"), "--lattice", lat, cf, str(r), nf], capture_output=True, text=True)
            sys.stdout.write(res.stdout)
            bad += int(res.returncode != 0)
    if bad:
        sys.exit(2)


if __name__ == "__main__":
    main()
