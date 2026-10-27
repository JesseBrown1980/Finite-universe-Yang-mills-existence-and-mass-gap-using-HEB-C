#!/usr/bin/env python3
"""Certify a sealed full-space stage B (integer only, json=0). See
results/3x3_full_space/CERTIFY-SPEC.md.

  plan     CORES CORES_SHA [SPLIT COLS]       the watcher jobs: sectors, finals, sample cells
  assemble ROOT T1 TF [SPLIT COLS]            seal integrity, the N-Nest tree depths 0-4, verdict

ROOT layout (prepared by the certify workflow, or by the 2x2 test):
  ROOT/cores.hbp, ROOT/cores.sha256       the sealed core table stage B was generated from
  ROOT/stageA.hbp, ROOT/stageA.sha256     stage A, which records every sector shard
  ROOT/parts/PART-n.hbp, PART-n.sha256, ROOT/parts/shards/<final id>/   sealed stage B
  ROOT/cells/<cell id>/run.hbp                                         cell receipts
  ROOT/watch/sectors/<sector id>/run.hbp                               sectors rebuilt
  ROOT/watch/finals/<final id>/run.hbp                                 finals re-executed
  ROOT/watch/sample/<cell id>/run.hbp                                  sampled cells re-executed
  ROOT/timing.hbp (optional)   TIMING|stage_b_seconds=..|certify_seconds=..|json=0

node_green = (reported == watcher_recomputed) AND all(child_green). A missing input
holds its node; a held or flagged node makes the verdict INCONCLUSIVE.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import full_space_workflow as fsw  # noqa: E402  (the same plan the stage B workflows were generated from)

SAMPLE_TAG = "CERTIFY-3X3-V1|"
SAMPLE_N = 2


def sha(b):
    return hashlib.sha256(b).hexdigest()


def fields(line):
    return dict(p.split("=", 1) for p in line.strip().split("|")[1:] if "=" in p)


def sid(spec):
    return spec.replace("/", "_")


def read(path):
    with open(path, "rb") as f:
        return f.read()


def load_plan(cores_file, cores_sha, split, cols):
    cores = fsw.read_cores(cores_file, cores_sha)         # fails closed on checksum / not sealed PASS
    entries = fsw.plan(cores, split, cols)                  # (count spec, [cells], merge or None)
    sectors = sorted({e[0].split("/", 1)[0].replace("count", "sector") + "/" + "/".join(e[0].split("/")[1:5])
                      for e in entries})
    cells = [c for e in entries if e[2] for c in e[1]]
    sample = sorted(cells, key=lambda c: sha((SAMPLE_TAG + c).encode()))[:SAMPLE_N]
    core = {spec: n for spec, n in cores}
    return entries, sectors, sample, core


def cmd_plan(argv):
    split = int(argv[2]) if len(argv) > 2 else 100
    cols = int(argv[3]) if len(argv) > 3 else 100
    entries, sectors, sample, _ = load_plan(argv[0], argv[1], split, cols)
    for s in sectors:
        print("PLAN|kind=sector|spec=%s|json=0" % s)
    for spec, cells, merge in entries:
        print("PLAN|kind=final|spec=%s|count=%s|cells=%d|json=0" % (merge or spec, spec, len(cells) if merge else 0))
    for c in sample:
        print("PLAN|kind=sample|spec=%s|json=0" % c)
    print("PLAN|sectors=%d|finals=%d|merged=%d|sample=%d|json=0"
          % (len(sectors), len(entries), sum(1 for e in entries if e[2]), len(sample)))


class Tree:
    def __init__(self):
        self.rows, self.bad, self.held = [], [], []

    def node(self, depth, addr, ok, detail, held=False):
        state = "HELD" if held else ("CONVERGED" if ok else "MISTAKE_FLAGGED")
        self.rows.append("NNEST|depth=%d|node=%s|state=%s|%s|json=0" % (depth, addr, state, detail))
        if held:
            self.held.append(addr)
        elif not ok:
            self.bad.append(addr)
        return ok and not held


def cmd_assemble(argv):
    root, t1, tf = argv[0], int(argv[1]), int(argv[2])
    split = int(argv[3]) if len(argv) > 3 else 100
    cols = int(argv[4]) if len(argv) > 4 else 100
    tr = Tree()
    out = ["CERTIFY|root=%s|t1_milli=%d|tF_milli=%d|json=0" % (os.path.basename(os.path.abspath(root)), t1, tf)]
    entries, sectors, sample, core = load_plan(os.path.join(root, "cores.hbp"), os.path.join(root, "cores.sha256"),
                                                split, cols)
    stage_a = read(os.path.join(root, "stageA.hbp"))
    if sha(stage_a) != read(os.path.join(root, "stageA.sha256")).decode().split()[0]:
        print("CERTIFY|error=stage_A_checksum|json=0\nCERTIFY_VERDICT|INCONCLUSIVE|json=0")
        raise SystemExit(2)
    stage_a_lines = stage_a.decode().splitlines()
    finals = {(e[2] or e[0]): e for e in entries}

    # ---- seal integrity
    pdir = os.path.join(root, "parts")
    parts = sorted(f for f in os.listdir(pdir) if f.startswith("PART-") and f.endswith(".hbp"))
    seal_ok = bool(parts)
    for p in parts:
        body = read(os.path.join(pdir, p))
        want = read(os.path.join(pdir, p[:-4] + ".sha256")).decode().split()[0]
        good = want == sha(body) and "|status=PASS|" in body.decode().splitlines()[-1]
        out.append("SEAL|part=%s|sha256_match=%d|sealed_pass=%d|json=0" % (p, want == sha(body), "|status=PASS|" in body.decode().splitlines()[-1]))
        seal_ok &= good
    integ = subprocess.run([sys.executable, os.path.join(HERE, "verify_shard_integrity.py"), os.path.join(pdir, "shards")],
                           capture_output=True, text=True)
    integ_ok = integ.returncode == 0 and "|failed=0|" in integ.stdout and "result=PASS" in integ.stdout
    have = sorted(os.listdir(os.path.join(pdir, "shards")))
    cover_ok = sorted(sid(f) for f in finals) == have
    out.append("SEAL|shard_integrity=%s|coverage=%s|finals_expected=%d|finals_present=%d|json=0"
               % ("PASS" if integ_ok else "FAIL", "PASS" if cover_ok else "FAIL", len(finals), len(have)))
    seal_ok &= integ_ok and cover_ok

    # ---- depth 4: sectors rebuilt == stage A record; matrix hash for every citation
    matrix_sha = {}
    sector_green = {}
    for s in sectors:
        i = sid(s)
        rebuilt = os.path.join(root, "watch", "sectors", i, "run.hbp")
        recorded = [l.split("|", 2)[2] for l in stage_a_lines if l.startswith("SHARD|%s|" % i)]
        if not os.path.exists(rebuilt) or not recorded:
            sector_green[s] = tr.node(4, i, False, "reason=missing_rebuild_or_record", held=True)
            continue
        lines = read(rebuilt).decode().splitlines()
        ms = next((fields(l)["sha256"] for l in lines if l.startswith("MATRIX_SHA|")), None)
        matrix_sha[s] = ms
        sector_green[s] = tr.node(4, i, lines == recorded and ms is not None,
                                  "watcher=rebuild_http0|equals_stage_A_record=%d|matrix_sha256=%s" % (lines == recorded, ms))

    # ---- depths 3 and 2: cells and finals
    final_green = {}
    for f, (count, cells, merge) in sorted(finals.items()):
        i = sid(f)
        sec = count.split("/", 1)[0].replace("count", "sector") + "/" + "/".join(count.split("/")[1:5])
        sealed = os.path.join(pdir, "shards", i, "run.hbp")
        if not os.path.exists(sealed):
            final_green[f] = tr.node(2, i, False, "reason=missing_sealed_shard", held=True)
            continue
        sealed_b = read(sealed)
        kids_ok = sector_green.get(sec, False)
        if merge:
            minputs = [fields(l) for l in sealed_b.decode().splitlines() if l.startswith("MERGE_INPUT|")]
            expect = list(cells)
            spans = [tuple(map(int, m["cols"].split(":"))) for m in minputs]
            part_ok = ([m["spec"] for m in minputs] == expect and spans and spans[0][0] == 0
                       and all(a[1] == b[0] for a, b in zip(spans, spans[1:])) and spans[-1][1] == core[count])
            for m in minputs:
                c = os.path.join(root, "cells", sid(m["spec"]), "run.hbp")
                if not os.path.exists(c):
                    kids_ok &= tr.node(3, sid(m["spec"]), False, "reason=missing_cell_receipt", held=True)
                    continue
                cb = read(c)
                cms = next((fields(l)["sha256"] for l in cb.decode().splitlines() if l.startswith("INPUT_MATRIX|")), None)
                ok = sha(cb) == m["hbp_sha256"] and cms == matrix_sha.get(sec)
                det = "watcher=hash|hbp_sha256_match=%d|matrix_match=%d" % (sha(cb) == m["hbp_sha256"], cms == matrix_sha.get(sec))
                if m["spec"] in sample:
                    s = os.path.join(root, "watch", "sample", sid(m["spec"]), "run.hbp")
                    if not os.path.exists(s):
                        kids_ok &= tr.node(3, sid(m["spec"]), False, "reason=missing_sample_reexecution", held=True)
                        continue
                    ok &= read(s) == cb
                    det += "|sampled=1|reexecuted_byte_identical=%d" % (read(s) == cb)
                kids_ok &= tr.node(3, sid(m["spec"]), ok, det)
            mms = next((fields(l)["sha256"] for l in sealed_b.decode().splitlines() if l.startswith("INPUT_MATRIX|")), None)
            kids_ok &= tr.node(3, i + ".partition", part_ok and mms == matrix_sha.get(sec),
                               "watcher=columns|cells=%d|exact_partition=%d|matrix_match=%d" % (len(minputs), bool(part_ok), mms == matrix_sha.get(sec)))
        rer = os.path.join(root, "watch", "finals", i, "run.hbp")
        if not os.path.exists(rer):
            final_green[f] = tr.node(2, i, False, "reason=missing_reexecution", held=True)
            continue
        same = read(rer) == sealed_b
        certified = "|ambiguous=0|" in sealed_b.decode() and "|result=PASS|" in sealed_b.decode()
        final_green[f] = tr.node(2, i, same and certified and kids_ok,
                                 "watcher=reexecute_http0|byte_identical=%d|ambiguous0_pass=%d|children_green=%d"
                                 % (same, certified, kids_ok))

    # ---- depths 1 and 0: per threshold
    def negative(f):
        line = next(l for l in read(os.path.join(pdir, "shards", sid(f), "run.hbp")).decode().splitlines()
                    if l.startswith("SHELL_SCHUR|"))
        return int(fields(line)["negative"])

    def dims(s):
        line = next(l for l in read(os.path.join(root, "watch", "sectors", sid(s), "run.hbp")).decode().splitlines()
                    if l.startswith("YMSEC|"))
        f = fields(line)
        return int(f["sector_states"]), int(f["gauge_orbits"])

    lx, ly = (int(x) for x in sectors[0].split("/")[1:3])
    pair = {}
    if not (tr.held or tr.bad):
        asm = tempfile.mkdtemp(prefix="certify_asm_")
        os.makedirs(os.path.join(asm, "shards"))
        for f in finals:
            os.symlink(os.path.abspath(os.path.join(pdir, "shards", sid(f))), os.path.join(asm, "shards", sid(f)))
        for s in sectors:
            os.symlink(os.path.abspath(os.path.join(root, "watch", "sectors", sid(s))), os.path.join(asm, "shards", sid(s)))
        rest = entries[0][0].split("/")[5:]                 # JE JB T FDIG TOL of any count
        for t in (t1, tf):
            r = subprocess.run([sys.executable, os.path.join(HERE, "full_space_mobius.py"), asm, str(lx), str(ly),
                                rest[0], rest[1], str(t), rest[3], rest[4]], capture_output=True, text=True)
            rep = {l.split("|", 1)[0]: l for l in r.stdout.splitlines()}
            inv = [fields(l) for l in r.stdout.splitlines() if l.startswith("INVARIANT_COUNT|")]
            if os.environ.get("CERTIFY_FAULT") == "sum" and inv:     # control C4 only: a faulty reported sum
                inv[0]["N"] = str(int(inv[0]["N"]) + 1)
            # independent watcher: counts per kernel from the shards, then Mobius for an
            # LX = LY = p prime lattice: kernels T and the p + 1 lines, N = sum(lines) - p * N_T
            mine, mydim = {}, {}
            for f, (count, _, _) in finals.items():
                k, rest_ = count.split("/", 1)
                if int(rest_.split("/")[6]) != t:
                    continue
                kern = k[:-len("count")] or "T"
                mine[kern] = mine.get(kern, 0) + negative(f)
                d, g = dims(k.replace("count", "sector") + "/" + "/".join(rest_.split("/")[:4]))
                mydim[kern] = mydim.get(kern, 0) + d
            orbits = {dims(s)[1] for s in sectors}
            p = lx
            lines_ = [m for m in mine if m != "T"]
            mine_full = sum(mine[m] for m in lines_) - (len(lines_) - 1) * mine["T"]
            dim_full = sum(mydim[m] for m in lines_) - (len(lines_) - 1) * mydim["T"]
            iso_nonneg = mine["T"] >= 0 and all(mine[m] - mine["T"] >= 0 for m in lines_)
            sym = all(mine[a] == mine[b] for a, b in (("tx", "ty"), ("td", "ta")) if a in mine and b in mine)
            dim_ok = len(orbits) == 1 and dim_full == next(iter(orbits))
            d1_ok = bool(inv) and {f["kernel"] for f in inv} == set(mine)
            for f in inv:
                kern = f["kernel"]
                d1_ok &= tr.node(1, "t%d.%s" % (t, kern), int(f["N"]) == mine.get(kern),
                                 "reported=%s|watcher_sum_of_sectors=%s" % (f["N"], mine.get(kern)))
            fsc = fields(rep.get("FULL_SPACE_COUNT", "X|N=-1"))
            reported = int(fsc.get("N", "-1"))
            ok = (r.returncode == 0 and reported == mine_full and iso_nonneg and sym and dim_ok
                  and len(lines_) == p + 1 and d1_ok)
            tr.node(0, "t%d" % t, ok, "reported=%d|watcher_mobius=%d|isotypic_nonnegative=%d|symmetric_lines=%d|"
                    "dimension=%d|gauge_orbits=%s|lines=%d" % (reported, mine_full, iso_nonneg, sym, dim_full,
                                                                  ",".join(map(str, sorted(orbits))), len(lines_)))
            pair[t] = mine_full
        shutil.rmtree(asm)

    # ---- budget (infinite-three: certify <= B / 2)
    budget = "CERTIFY_BUDGET|unmeasured|json=0"
    tpath = os.path.join(root, "timing.hbp")
    if os.path.exists(tpath):
        tf_ = fields(read(tpath).decode().splitlines()[0])
        b, c = int(tf_["stage_b_seconds"]), int(tf_["certify_seconds"])
        budget = "CERTIFY_BUDGET|stage_b_seconds=%d|certify_seconds=%d|ratio_permille=%d|bound_permille=500|%s|json=0" % (
            b, c, c * 1000 // max(1, b), "WITHIN_BOUND" if c * 2 <= b else "BUDGET_EXCEEDED")

    out += tr.rows
    out.append(budget)
    if not seal_ok or tr.held or tr.bad or len(pair) != 2:
        out.append("CERTIFY_VERDICT|INCONCLUSIVE|seal=%d|held=%s|flagged=%s|json=0"
                   % (seal_ok, ",".join(tr.held) or "-", ",".join(tr.bad) or "-"))
        print("\n".join(out))
        raise SystemExit(2)
    v = "PASS" if (pair[t1], pair[tf]) == (8, 8) else "MISMATCH"
    out.append("CERTIFY_VERDICT|%s|N_full_t1=%d|N_full_tF=%d|nodes_green=%d|json=0" % (v, pair[t1], pair[tf], len(tr.rows)))
    print("\n".join(out))
    raise SystemExit(0 if v == "PASS" else 1)


if __name__ == "__main__":
    {"plan": cmd_plan, "assemble": cmd_assemble}[sys.argv[1]](sys.argv[2:])
