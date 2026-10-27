#!/usr/bin/env python3
"""End-to-end test of full_space_certify.py on the 2x2 lattice, every job and verify
sent through the HEB-C HTTP-0 server (hebc_ym_http0 serve) (integer only, json=0): a miniature stage A + stage B with split counts forced
(SPLIT = COLS = 40), sealed the same way, every watcher run, then the controls of
CERTIFY-SPEC.md:
  C1 clean tree green, verdict computed
  C2 rerun -> identical verdict file
  C3 a missing sealed shard -> INCONCLUSIVE, node named
  C4 a fault planted at depth 2 (count shard), 3 (cell receipt), 4 (sector record),
     1 (a reported sum) -> flagged at that depth
usage: certify_test_2x2.py BIN WORK T1 TF
"""
import hashlib
import os
import shutil
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import full_space_mobius as fsm  # noqa: E402

SPLIT = COLS = 40
JE, JB, FD, TOL = 1000, 9000, 12, 1000


def sh(*a, env=None):
    r = subprocess.run(a, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout + r.stderr


SERVERS = {}


def server(b, root):
    """One HEB-C HTTP-0 server per root: every job and verify goes through the route."""
    root = os.path.abspath(root)
    if root not in SERVERS:
        os.makedirs(root, exist_ok=True)
        port = 18100 + len(SERVERS)
        log = open(root + ".serve.log", "w")
        p = subprocess.Popen([b, "serve", root, str(port), "10000"], stdout=log, stderr=subprocess.STDOUT,
                             env=dict(os.environ, HEBC_YM_FRESH="1"))
        for _ in range(200):
            txt = open(root + ".serve.log").read()
            if "READY" in txt:
                break
            if p.poll() is not None:
                raise SystemExit("TEST|server_failed|root=%s|%s|json=0" % (root, txt.strip()[:200]))
            time.sleep(0.05)
        else:
            raise SystemExit("TEST|server_not_ready|root=%s|json=0" % root)
        SERVERS[root] = (p, port)
    return SERVERS[root][1]


def http(port, method, path):
    req = urllib.request.Request("http://127.0.0.1:%d%s" % (port, path), method=method)
    with urllib.request.urlopen(req, timeout=3600) as r:
        return r.read().decode()


def job(b, root, spec):
    port = server(b, root)
    out = http(port, "POST", "/job/" + spec)
    if not out.startswith("HEBC_YM|result=PASS"):
        raise SystemExit("TEST|job_failed|spec=%s|%s|json=0" % (spec, out.strip()[:200]))
    out = http(port, "GET", "/verify/" + spec)
    if "result=PASS" not in out:
        raise SystemExit("TEST|verify_failed|spec=%s|%s|json=0" % (spec, out.strip()[:200]))


def stop_servers():
    for p, _ in SERVERS.values():
        p.terminate()
        p.wait()


def sid(s):
    return s.replace("/", "_")


def build(b, work, t1, tf):
    lx = ly = 2
    T = fsm.subgroup([(1, 0), (0, 1)], lx, ly)
    sectors = []
    for k in fsm.kernel_subgroups(lx, ly):
        mode = "" if k == T else "t" + next(m for m, v in fsm.MODES.items() if fsm.line(v, lx, ly) == k)
        pts = fsm.point_ops(k, lx, ly) if k != T else [0, 1, 2, 3]
        sectors += ["%ssector/%d/%d/%d/%d" % (mode, lx, ly, sx, sy) for sx, sy in fsm.sectors(pts)]
    # stage A: sector shards recorded line by line; cores from the counts themselves
    a = os.path.join(work, "stageA_root")
    for s in sectors:
        job(b, a, s)
    lines = []
    for s in sectors:
        lines += ["SHARD|%s|%s" % (sid(s), l) for l in open(os.path.join(a, "shards", sid(s), "run.hbp")).read().splitlines()]
    lines.append("GITRAM_SEAL|name=2x2-test|status=PASS|json=0")
    os.makedirs(os.path.join(work, "root"), exist_ok=True)
    R = os.path.join(work, "root")
    open(os.path.join(R, "stageA.hbp"), "w").write("\n".join(lines) + "\n")
    cores = []
    for s in sectors:
        mode = s.split("sector")[0]
        rest = "/".join(s.split("/")[1:5])
        for t in (t1, tf):
            spec = "%scount/%s/%d/%d/%d/%d/%d" % (mode, rest, JE, JB, t, FD, TOL)
            job(b, a, spec)
            core = next(int(p.split("=")[1]) for p in open(os.path.join(a, "shards", sid(spec), "run.hbp")).read().split("|")
                        if p.startswith("core="))
            cores.append("CORE|spec=%s|core_rows=%d|json=0" % (spec, core))
    cores.append("LOCAL_SEAL|cores=%d|status=PASS|json=0" % len(cores))
    open(os.path.join(R, "cores.hbp"), "w").write("\n".join(cores) + "\n")
    for f in ("stageA", "cores"):
        h = hashlib.sha256(open(os.path.join(R, f + ".hbp"), "rb").read()).hexdigest()
        open(os.path.join(R, f + ".sha256"), "w").write("%s  %s.hbp\n" % (h, f))
    # stage B exactly as the workflows do it: cells, merges, seal
    plan = subprocess.run([sys.executable, os.path.join(HERE, "full_space_certify.py"), "plan",
                           os.path.join(R, "cores.hbp"), os.path.join(R, "cores.sha256"), str(SPLIT), str(COLS)],
                          capture_output=True, text=True, check=True).stdout
    import full_space_workflow as fsw
    entries = fsw.plan(fsw.read_cores(os.path.join(R, "cores.hbp"), os.path.join(R, "cores.sha256")), SPLIT, COLS)
    cellroot = os.path.join(work, "cells_root")
    os.makedirs(os.path.join(R, "cells"), exist_ok=True)
    os.makedirs(os.path.join(R, "parts", "shards"), exist_ok=True)
    merged = 0
    built = set()
    for count, cells, merge in entries:
        sec = count.split("count")[0] + "sector/" + "/".join(count.split("/")[1:5])
        if sec not in built:                       # each cell job builds its sector first, as the workflow does
            job(b, cellroot, sec)
            built.add(sec)
        for c in cells:
            job(b, cellroot, c)
            if merge:
                shutil.copytree(os.path.join(cellroot, "shards", sid(c)), os.path.join(R, "cells", sid(c)))
        final = merge or count
        if merge:
            merged += 1
            mroot = os.path.join(work, "m_" + sid(merge))
            dest = os.path.join(mroot, "scol", sid(count))
            os.makedirs(dest)
            for c in cells:
                shutil.copytree(os.path.join(cellroot, "shards", sid(c)), os.path.join(dest, sid(c)))
            job(b, mroot, count.split("count")[0] + "sector/" + "/".join(count.split("/")[1:5]))
            job(b, mroot, merge)
            src = os.path.join(mroot, "shards", sid(merge))
        else:
            src = os.path.join(cellroot, "shards", sid(count))
        shutil.copytree(src, os.path.join(R, "parts", "shards", sid(final)))
    seal = ["SHARD|%s|x|json=0" % d for d in sorted(os.listdir(os.path.join(R, "parts", "shards")))]
    seal.append("GITRAM_SEAL|name=2x2-test|part=1/1|counts=%d|merges=%d|status=PASS|json=0" % (len(entries), merged))
    p = os.path.join(R, "parts", "PART-1.hbp")
    open(p, "w").write("\n".join(seal) + "\n")
    open(p[:-4] + ".sha256", "w").write("%s  PART-1.hbp\n" % hashlib.sha256(open(p, "rb").read()).hexdigest())
    # watchers on fresh roots: sectors rebuilt, finals re-executed, sample cells re-executed
    for line in plan.splitlines():
        f = dict(x.split("=", 1) for x in line.split("|")[1:] if "=" in x)
        kind = f.get("kind")
        if kind == "sector":
            w = os.path.join(work, "w_" + sid(f["spec"]))
            job(b, w, f["spec"])
            shutil.copytree(os.path.join(w, "shards", sid(f["spec"])), os.path.join(R, "watch", "sectors", sid(f["spec"])))
        elif kind in ("final", "sample"):
            spec = f["spec"]
            w = os.path.join(work, "w_" + sid(spec))
            base = spec.split("count")[0]
            rest = spec.split("/", 1)[1]
            if "countmerge" in spec:
                cid = sid(base + "count/" + rest)
                os.makedirs(os.path.join(w, "scol", cid))
                for c in os.listdir(os.path.join(R, "cells")):
                    if c.startswith(sid(base + "countcols/" + rest) + "_"):
                        shutil.copytree(os.path.join(R, "cells", c), os.path.join(w, "scol", cid, c))
            job(b, w, base + "sector/" + "/".join(rest.split("/")[:4]))
            job(b, w, spec)
            dst = "finals" if kind == "final" else "sample"
            shutil.copytree(os.path.join(w, "shards", sid(spec)), os.path.join(R, "watch", dst, sid(spec)))
    return R, merged, len(entries)


def certify(R, t1, tf, env=None):
    r = subprocess.run([sys.executable, os.path.join(HERE, "full_space_certify.py"), "assemble", R, str(t1), str(tf),
                        str(SPLIT), str(COLS)], capture_output=True, text=True, env=env)
    return r.returncode, r.stdout


def flip(path):
    b = bytearray(open(path, "rb").read())
    i = b.rfind(b"negative=") + len("negative=")
    b[i] = ord("9") if b[i] != ord("9") else ord("8")
    open(path, "wb").write(bytes(b))


def main():
    b, work, t1, tf = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    try:
        R, merged, finals = build(b, work, t1, tf)
    finally:
        stop_servers()
    out = ["CERTIFY_TEST|L=2x2|t1_milli=%d|tF_milli=%d|finals=%d|merged=%d|split=%d|json=0" % (t1, tf, finals, merged, SPLIT)]
    rc, v1 = certify(R, t1, tf)
    verdict = v1.strip().splitlines()[-1]
    green = rc in (0, 1) and "MISTAKE_FLAGGED" not in v1 and "HELD" not in v1
    out.append("CONTROL|C1_clean_tree_green|%s|%s|json=0" % ("PASS" if green else "FAIL", verdict))
    rc2, v2 = certify(R, t1, tf)
    out.append("CONTROL|C2_rerun_identical|%s|json=0" % ("PASS" if v2 == v1 else "FAIL"))

    def fresh():
        d = os.path.join(work, "ctl")
        shutil.rmtree(d, ignore_errors=True)
        shutil.copytree(R, d, symlinks=True)
        return d

    d = fresh()
    victim = sorted(os.listdir(os.path.join(d, "parts", "shards")))[0]
    shutil.rmtree(os.path.join(d, "parts", "shards", victim))
    rc, v = certify(d, t1, tf)
    out.append("CONTROL|C3_missing_shard_holds|%s|json=0" % ("PASS" if rc == 2 and "INCONCLUSIVE" in v else "FAIL"))

    def caught(label, depth, d, env=None):
        rc, v = certify(d, t1, tf, env)
        hit = [l for l in v.splitlines() if l.startswith("NNEST|depth=%d|" % depth) and "MISTAKE_FLAGGED" in l]
        out.append("CONTROL|C4_%s|depth=%d|%s|path=%s|json=0" % (label, depth, "PASS" if rc == 2 and hit else "FAIL",
                                                                  hit[0].split("|")[2] if hit else "-"))

    d = fresh()
    f = next(x for x in sorted(os.listdir(os.path.join(d, "parts", "shards"))) if "countmerge" not in x)
    flip(os.path.join(d, "watch", "finals", f, "run.hbp"))           # the re-execution disagrees with the seal
    caught("count_shard", 2, d)
    d = fresh()
    c = sorted(os.listdir(os.path.join(d, "cells")))[0]
    flip(os.path.join(d, "cells", c, "run.hbp"))
    caught("cell_receipt", 3, d)
    d = fresh()
    s = sorted(os.listdir(os.path.join(d, "watch", "sectors")))[0]
    p = os.path.join(d, "watch", "sectors", s, "run.hbp")
    t = open(p).read()
    i = t.index("MATRIX_SHA|sha256=") + len("MATRIX_SHA|sha256=")
    open(p, "w").write(t[:i] + ("0" if t[i] != "0" else "1") + t[i + 1:])
    caught("sector_record", 4, d)
    d = fresh()
    caught("reported_sum", 1, d, dict(os.environ, CERTIFY_FAULT="sum"))
    print("\n".join(out))
    ok = all("|PASS|" in l for l in out if l.startswith("CONTROL|"))
    print("CERTIFY_TEST_VERDICT|%s|json=0" % ("PASS" if ok else "FAIL"))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
