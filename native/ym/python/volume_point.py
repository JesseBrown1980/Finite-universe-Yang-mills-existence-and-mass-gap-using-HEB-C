#!/usr/bin/env python3
"""One coupling point of the finite-volume experiment, run entirely through the
HEB-C HTTP-0 backend (hebc_ym_http0 jobs, one disk shard each).

Phases (each a backend job; existing shards are replay-verified, not trusted):
  1. sector + flatcomp for the four zero-momentum C2v sectors of LX x LY;
  2. cluster (block eigensolver, residual intervals) at JE=1, JB=R in the two
     vacuum-carrying sectors (+,+) and (-,-);
  3. thresholds from the merged intervals, by the fixed rule used for 3x3:
       t0 = lowest lo - 2          (expect N = 0)
       ts = second-lowest lo - 2   (expect N = 1; skipped if intervals overlap)
       t1 = highest lo..hi of the 8 lowest + 2   (expect N = 8)
       tB = floor(E9 lo / 1000)*1000 - 1000      (expect N = 8)
  4. shellschur counts at JE=1000, JB=1000*R (micro-unit thresholds) in the
     vacuum sectors at t0/ts/t1/tB and the two mixed sectors at tB;
  5. shell_gap_cert.py --lattice LXxLY on the shard contents.
The 8 lowest levels must be 7 from (+,+) and 1 from (-,-); otherwise the point
stops with a FAIL line (the rule is not silently changed). Integer-only.
usage: volume_point.py BACKEND ROOT LX LY R        json=0
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VAC = ((1, 1), (-1, -1))
ALL = ((1, 1), (-1, -1), (1, -1), (-1, 1))


def job(b, root, spec):
    out = subprocess.run([b, "job", root, spec], capture_output=True, text=True).stdout
    if not out.startswith("HEBC_YM|result=PASS|"):
        print("VOLUME_POINT|result=FAIL|spec=%s|backend=%s|json=0" % (spec, out.strip().replace("|", "/")))
        sys.exit(2)
    sid = spec.replace("/", "_")
    return open(os.path.join(root, "shards", sid, "run.hbp")).read()


def main():
    b, root, lx, ly, r = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    lat = "%dx%d" % (lx, ly)
    for s in ALL:
        job(b, root, "sector/%d/%d/%d/%d" % (lx, ly, s[0], s[1]))
        job(b, root, "flatcomp/%d/%d/%d/%d" % (lx, ly, s[0], s[1]))
    clusters, ivs = [], []
    for s in VAC:
        txt = job(b, root, "cluster/%d/%d/%d/%d/1/%d/12/4" % (lx, ly, s[0], s[1], r))
        for line in txt.splitlines():
            clusters.append("YM%dX%d_S%d_%d_r%d_%s" % (lx, ly, s[0], s[1], r, line))
            if line.startswith("CLUSTER_LEVEL|"):
                f = dict(kv.split("=", 1) for kv in line.split("|")[1:] if "=" in kv)
                lo, hi = f["interval"].split("/")[0].strip("[]").split(",")
                ivs.append((int(lo), int(hi), s))
            if line.startswith("CLUSTER|") and "|converged=1|" not in line:
                print("VOLUME_POINT|L=%s|r=%d|result=FAIL|reason=cluster_not_converged|sector=%d,%d|json=0" % (lat, r, s[0], s[1]))
                sys.exit(2)
    ivs.sort()
    low8 = ivs[:8]
    if sum(1 for v in low8 if v[2] == (1, 1)) != 7 or sum(1 for v in low8 if v[2] == (-1, -1)) != 1:
        print("VOLUME_POINT|L=%s|r=%d|result=FAIL|reason=lowest8_not_7_plus_1|json=0" % (lat, r))
        sys.exit(2)
    t0 = low8[0][0] - 2
    t1 = max(v[1] for v in low8) + 2
    e9lo = ivs[8][0]
    tb = e9lo // 1000 * 1000 - 1000
    ts = low8[1][0] - 2 if low8[0][1] < low8[1][0] - 2 else None
    if not (t1 < tb):
        print("VOLUME_POINT|L=%s|r=%d|result=FAIL|reason=t1_not_below_tB|json=0" % (lat, r))
        sys.exit(2)
    jb = 1000 * r
    counts = []

    def cnt(s, t, fd, tol):
        counts.append(job(b, root, "count/%d/%d/%d/%d/1000/%d/%d/%d/%d" % (lx, ly, s[0], s[1], jb, t, fd, tol)))

    cnt((1, 1), t0, 13, 10)
    if ts is not None:
        cnt((1, 1), ts, 13, 10)
        cnt((-1, -1), ts, 13, 10)
    else:
        cnt((-1, -1), t0, 13, 10)
    for s in VAC:
        cnt(s, t1, 12, 1000)
    for s in ALL:
        cnt(s, tb, 12, 1000)
    cdir = os.path.join(root, "cert")
    os.makedirs(cdir, exist_ok=True)
    cf, nf = os.path.join(cdir, "clusters_%s_r%d.hbp" % (lat, r)), os.path.join(cdir, "counts_%s_r%d.hbp" % (lat, r))
    open(cf, "w").write("\n".join(clusters) + "\n")
    open(nf, "w").write("".join(counts))
    print("VOLUME_POINT|L=%s|r=%d|t0=%d|ts=%s|t1=%d|tB=%d|json=0" % (lat, r, t0, ts if ts is not None else "none", t1, tb))
    res = subprocess.run([sys.executable, os.path.join(HERE, "shell_gap_cert.py"), "--lattice", lat, cf, str(r), nf], capture_output=True, text=True)
    sys.stdout.write(res.stdout)
    if res.returncode != 0:
        sys.exit(res.returncode)


if __name__ == "__main__":
    main()
