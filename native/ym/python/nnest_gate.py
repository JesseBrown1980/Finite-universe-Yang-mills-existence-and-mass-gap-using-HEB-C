"""N-Nest gate over HEB-C full-space results (integer only, json=0).

Every node of the verification tree is an agent's report plus a watcher that
recomputes it independently:

    node_green = (reported == watcher_recomputed) AND all(child_green)

  depth 0  R.t<T>                        full-space count N(V, t)
           watcher: Mobius sum of the kernel isotypic counts, AND equality with
           the independent reflection-only route (G = C2v, every momentum)
  depth 1  R.t<T>.k<K> / R.t<T>.refl     N(V^K, t) / reflection-only total
           watcher: sum of the sector counts read from the child shards
  depth 2  ...c<SX>_<SY>                 one count shard (shellschur)
           watcher: re-execute the job through the HTTP-0 route, byte compare
  depth 3  ...s                          its sector shard (ymsec matrix)
           watcher: re-execute through HTTP-0, byte compare, and check the
           matrix file against the SHA-256 recorded by the shard

Node lifecycle (the GLSM states of the Asolaria scoring plane):
  DESCRIBED -> EDGE_MINED (inputs located) -> PATH_FOUND (watcher ran)
            -> CONVERGED | MISTAKE_FLAGGED (hard block, path named)
The proposal plane only orders the watcher's work (cheapest leaves first); it
never decides a verdict. Correction nests to every depth; nothing here can
authorize new work (dispatch stays with the operator).

usage:
  python nnest_gate.py BIN ROOT RECORD PORT            gate one result record
  python nnest_gate.py BIN ROOT RECORD PORT --controls run the controls:
      C1 clean tree green; C2 re-run byte-identical verdict;
      C3 a missing leaf holds the tree (a fraction does not certify);
      C4 a planted fault at every depth is caught at that depth, path named.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def fields(line: str) -> dict[str, str]:
    return dict(p.split("=", 1) for p in line.split("|")[1:] if "=" in p)


def sid_to_spec(sid: str) -> str:
    return sid.replace("_", "/", 1).replace("_", "/")


def count_to_sector(spec: str) -> str:
    kind, *nums = spec.split("/")
    return "/".join([kind.replace("count", "sector")] + nums[:4])


def parse_record(text: str) -> list[dict]:
    """Blocks of mobius output, one per threshold, plus the reflection check."""
    blocks: list[dict] = []
    cur: dict | None = None
    for line in text.splitlines():
        tag = line.split("|", 1)[0]
        f = fields(line)
        if tag == "FULL_SPACE" and "reduction" in f:
            cur = {"t": f["t_milli"], "L": f["L"], "kernels": {}, "order": []}
            blocks.append(cur)
        elif tag == "SECTOR_COUNT" and cur is not None:
            k = f["kernel"]
            cur["kernels"].setdefault(k, {"sectors": [], "N": None, "iso": None})
            if k not in cur["order"]:
                cur["order"].append(k)
            cur["kernels"][k]["sectors"].append((f["shard"], int(f["negative"])))
        elif tag == "INVARIANT_COUNT" and cur is not None:
            cur["kernels"][f["kernel"]]["N"] = int(f["N"])
        elif tag == "ISOTYPIC" and cur is not None:
            cur["kernels"][f["kernel"]]["iso"] = int(f["count"])
        elif tag == "FULL_SPACE_COUNT" and cur is not None:
            cur["N"] = int(f["N"])
        elif tag == "FULL_SPACE_CHECK":
            for b in blocks:
                if b["t"] == f["t_milli"]:
                    b["reflection"] = int(f["reflection_only"])
    return blocks


class Watcher:
    """Re-executes jobs through the HTTP-0 route of hebc_ym_http0."""

    def __init__(self, bin_dir: str, root: str, port: int, budget: int):
        self.port = port
        log = Path(root) / "nnest-serve.log"
        self.proc = subprocess.Popen(
            [str(Path(bin_dir) / "hebc_ym_http0"), "serve", root, str(port), str(budget)],
            stdout=open(log, "w"),
            stderr=subprocess.STDOUT,
        )
        for _ in range(200):
            if log.exists() and "READY" in log.read_text():
                break
            time.sleep(0.05)

    def verify(self, spec: str) -> bool:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/verify/{spec}", timeout=3600) as r:
                return r.read().decode().startswith("HEBC_YM|result=PASS|action=verify|")
        except Exception:
            return False

    def close(self) -> None:
        self.proc.kill()
        self.proc.wait()


class Node:
    def __init__(self, addr: str, depth: int, reported, children=None):
        self.addr, self.depth, self.reported = addr, depth, reported
        self.children = children or []
        self.state = "DESCRIBED"
        self.recomputed = None
        self.green = False

    def failing(self) -> list[str]:
        out = [] if self.state == "CONVERGED" else [f"{self.addr}@depth{self.depth}:{self.state}"]
        for c in self.children:
            out += c.failing()
        return out


def matrix_ok(root: Path, sector_sid: str) -> bool:
    hbp = root / "shards" / sector_sid / "run.hbp"
    if not hbp.exists():
        return False
    line = next((l for l in hbp.read_text().splitlines() if l.startswith("MATRIX_SHA|")), None)
    if line is None:
        return False
    f = fields(line)
    m = root / "matrices" / f["file"]
    return m.exists() and hashlib.sha256(m.read_bytes()).hexdigest() == f["sha256"]


def read_negative(root: Path, sid: str):
    hbp = root / "shards" / sid / "run.hbp"
    if not hbp.exists():
        return None
    line = next((l for l in hbp.read_text().splitlines() if l.startswith("SHELL_SCHUR|")), None)
    if line is None:
        return None
    f = fields(line)
    if f.get("result") != "PASS" or f.get("ambiguous") != "0":
        return None
    return int(f["negative"])


def build_tree(block: dict, root: Path, lx: str, ly: str, refl_rest: str) -> Node:
    t = block["t"]
    top = f"R.t{t}"
    kernels = []
    for k in block["order"]:
        kd = block["kernels"][k]
        counts = []
        for sid, neg in kd["sectors"]:
            sx_sy = "_".join(sid.split("_")[3:5])
            sector_sid = count_to_sector(sid_to_spec(sid)).replace("/", "_")
            leaf = Node(f"{top}.k{k}.c{sx_sy}.s", 3, sector_sid)
            counts.append(Node(f"{top}.k{k}.c{sx_sy}", 2, (sid, neg), [leaf]))
        kernels.append(Node(f"{top}.k{k}", 1, (kd["N"], kd["iso"]), counts))
    refl_counts = []
    for sx, sy in (("1", "1"), ("1", "-1"), ("-1", "1"), ("-1", "-1")):
        sid = f"rcount_{lx}_{ly}_{sx}_{sy}_{refl_rest.replace('T', t)}"
        leaf = Node(f"{top}.refl.c{sx}_{sy}.s", 3, f"rsector_{lx}_{ly}_{sx}_{sy}")
        refl_counts.append(Node(f"{top}.refl.c{sx}_{sy}", 2, (sid, read_negative(root, sid)), [leaf]))
    refl = Node(f"{top}.refl", 1, block.get("reflection"), refl_counts)
    return Node(top, 0, block.get("N"), kernels + [refl])


def run_gate(tree: Node, root: Path, watcher: Watcher) -> None:
    # proposal plane: cheapest first (sector shards, then counts); never decides
    def walk(n: Node) -> None:
        for c in n.children:
            walk(c)
        n.state = "EDGE_MINED"
        kids_green = all(c.green for c in n.children)
        if n.depth == 3:
            ok = (root / "shards" / n.reported).exists() and matrix_ok(root, n.reported)
            ok = ok and watcher.verify(sid_to_spec(n.reported))
            n.recomputed = n.reported if ok else None
        elif n.depth == 2:
            sid, neg = n.reported
            ok = watcher.verify(sid_to_spec(sid))
            n.recomputed = read_negative(root, sid) if ok else None
            ok = ok and n.recomputed == neg
        elif n.depth == 1 and n.addr.endswith(".refl"):
            vals = [c.recomputed for c in n.children]
            n.recomputed = sum(vals) if all(v is not None for v in vals) else None
            ok = n.recomputed == n.reported
        elif n.depth == 1:
            vals = [c.recomputed for c in n.children]
            n.recomputed = sum(vals) if all(v is not None for v in vals) else None
            ok = n.recomputed == n.reported[0]
        else:
            kern = [c for c in n.children if not c.addr.endswith(".refl")]
            refl = next(c for c in n.children if c.addr.endswith(".refl"))
            # Mobius from the recomputed invariant counts (kernels ordered largest first)
            ok = all(c.recomputed is not None for c in kern) and refl.recomputed is not None
            if ok:
                n_t = kern[0].recomputed
                full = n_t + sum(c.recomputed - n_t for c in kern[1:])
                n.recomputed = full
                ok = full == n.reported and refl.recomputed == n.reported
                ok = ok and all(c.reported[1] == (c.recomputed - (n_t if i else 0)) for i, c in enumerate(kern))
        n.state = "PATH_FOUND"
        n.green = bool(ok) and kids_green
        n.state = "CONVERGED" if n.green else "MISTAKE_FLAGGED"

    walk(tree)


def gate(bin_dir, root, record, port, lx, ly, refl_rest) -> list[str]:
    rootp = Path(root)
    blocks = parse_record(Path(record).read_text())
    trees = [build_tree(b, rootp, lx, ly, refl_rest) for b in blocks]
    budget = 1 + sum(1 for t in trees for _ in iter_nodes(t))
    w = Watcher(bin_dir, root, port, budget)
    try:
        for t in trees:
            run_gate(t, rootp, w)
    finally:
        w.close()
    out = []
    for t in trees:
        nodes = list(iter_nodes(t))
        fails = t.failing()
        out.append(
            f"NNEST_GATE|tree={t.addr}|nodes={len(nodes)}|depth=3|green={int(t.green)}"
            f"|failing={','.join(fails) if fails else '-'}|json=0"
        )
    return out


def iter_nodes(n: Node):
    yield n
    for c in n.children:
        yield from iter_nodes(c)


def controls(bin_dir, root, record, port, lx, ly, refl_rest) -> list[str]:
    rows = []
    base = Path(root)
    c1 = gate(bin_dir, root, record, port, lx, ly, refl_rest)
    rows += [f"C1|{r}" for r in c1]
    c2 = gate(bin_dir, root, record, port + 1, lx, ly, refl_rest)
    rows.append(f"C2|rerun_identical={int(c1 == c2)}|json=0")
    blocks = parse_record(Path(record).read_text())
    t = blocks[-1]["t"]
    k = blocks[-1]["order"][1]
    sid, _ = blocks[-1]["kernels"][k]["sectors"][0]
    sector_sid = count_to_sector(sid_to_spec(sid)).replace("/", "_")
    work = base.parent / (base.name + "-nnest-controls")

    def fresh():
        if work.exists():
            shutil.rmtree(work)
        shutil.copytree(base, work, ignore=shutil.ignore_patterns("nnest-serve.log"))
        return work

    def caught(label, depth, rec, p):
        res = gate(bin_dir, str(work), rec, p, lx, ly, refl_rest)
        hit = [r for r in res if f"tree=R.t{t}|" in r][0]
        flagged = [int(x.split("@depth")[1].split(":")[0]) for x in hit.split("failing=")[1].split("|")[0].split(",") if "@depth" in x]
        ok = "green=0" in hit and bool(flagged) and max(flagged) == depth  # deepest flag = planted depth
        rows.append(f"{label}|depth={depth}|caught_at_depth={int(ok)}|{hit.split('|', 1)[1]}")
        return ok

    # C3: remove one leaf's evidence (a sector shard): the tree must hold
    fresh()
    shutil.rmtree(work / "shards" / sector_sid)
    rows.append("C3|fraction_of_evidence=one_sector_shard_removed")
    c3 = caught("C3", 3, record, port + 2)
    # C4: planted faults, one per depth
    all_caught = c3
    fresh()  # depth 3: corrupt the matrix file of one sector
    mf = work / "matrices" / fields(next(l for l in (work / "shards" / sector_sid / "run.hbp").read_text().splitlines() if l.startswith("MATRIX_SHA|")))["file"]
    data = bytearray(mf.read_bytes())
    data[-2] = ord("7") if data[-2] != ord("7") else ord("8")
    mf.write_bytes(bytes(data))
    all_caught &= caught("C4", 3, record, port + 3)
    fresh()  # depth 2: a count shard reports a different negative count
    hbp = work / "shards" / sid / "run.hbp"
    txt = hbp.read_text()
    neg = fields(next(l for l in txt.splitlines() if l.startswith("SHELL_SCHUR|")))["negative"]
    hbp.write_text(txt.replace(f"negative={neg}|", f"negative={int(neg) + 1}|", 1))
    all_caught &= caught("C4", 2, record, port + 4)
    fresh()  # depth 1: the record misreports an invariant count
    rec_txt = Path(record).read_text()
    lines = rec_txt.splitlines()
    blk_start = max(i for i, l in enumerate(lines) if l.startswith("FULL_SPACE|") and f"t_milli={t}" in l)
    for i in range(blk_start, len(lines)):
        if lines[i].startswith(f"INVARIANT_COUNT|kernel={k}|"):
            f = fields(lines[i])
            lines[i] = lines[i].replace(f"N={f['N']}|", f"N={int(f['N']) + 1}|")
            break
    r1 = work / "record-depth1.hbp"
    r1.write_text("\n".join(lines) + "\n")
    all_caught &= caught("C4", 1, str(r1), port + 5)
    fresh()  # depth 0: the record misreports the full-space count
    lines = rec_txt.splitlines()
    for i in range(blk_start, len(lines)):
        if lines[i].startswith("FULL_SPACE_COUNT|"):
            f = fields(lines[i])
            lines[i] = lines[i].replace(f"N={f['N']}|", f"N={int(f['N']) + 1}|")
            break
    r0 = work / "record-depth0.hbp"
    r0.write_text("\n".join(lines) + "\n")
    all_caught &= caught("C4", 0, str(r0), port + 6)
    shutil.rmtree(work)
    rows.append(f"NNEST_VERDICT|clean_green={int(all('green=1' in r for r in c1))}|rerun_identical={int(c1 == c2)}|EVERY_DEPTH_CATCHES_FAULT={int(all_caught)}|json=0")
    return rows


def main(argv: list[str]) -> None:
    ctl = "--controls" in argv
    a = [x for x in argv if x != "--controls"]
    bin_dir, root, record, port = a[0], a[1], a[2], int(a[3])
    head = fields(next(l for l in Path(record).read_text().splitlines() if l.startswith("FULL_SPACE_MOBIUS|")))
    lx, ly = head["L"].split("x")
    refl_rest = f"{head['JE']}_{head['JB']}_T_{head['FDIG_R']}_{head['TOL']}"
    rows = (controls if ctl else gate)(bin_dir, root, record, port, lx, ly, refl_rest)
    print("\n".join(rows))


if __name__ == "__main__":
    main(sys.argv[1:])
