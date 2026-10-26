"""Full-space eigenvalue counts from line-subgroup sectors (integer only, json=0).

The translation group T = Z_LX x Z_LY acts on the gauge-orbit space V. Over the
rationals V splits into isotypic parts, one per subgroup K with T/K cyclic (the
kernel of a rational irreducible representation). The states invariant under K,
V^K, are the sum of the parts whose kernel contains K, so

    N(V^K, t) = sum over K' >= K of iso(K', t)
    iso(K, t) = N(V^K, t) - sum over K' > K of iso(K', t)      (Mobius)
    N(V, t)   = sum over K of iso(K, t).

N(V^K, t) is the sum of the negative counts of the sectors of mode K:
  K = T          zero-momentum sectors  (kind prefix "")
  K = line(v)    YMSEC_TRANS sectors    (kind prefix tx / ty / td / ta)
Every point-group character sector of the mode is included (the same canonical
sector labels ymsec accepts). Every count shard must report result=PASS and
ambiguous=0.

One point plus the free zero: with --orbit, a mode related to an already
counted mode by a lattice symmetry of H reuses that count (td -> ta via the
reflection sx; tx -> ty via the x<->y swap on a square lattice). Without
--orbit every mode is read from its own shards.

usage: python full_space_mobius.py ROOT LX LY JE JB T FDIG TOL [--orbit]
"""

from __future__ import annotations

import sys
from itertools import product
from pathlib import Path

MODES = {"x": (1, 0), "y": (0, 1), "d": (1, 1), "a": (1, -1)}


def line(v, lx, ly):
    return frozenset(((m * v[0]) % lx, (m * v[1]) % ly) for m in range(lx * ly))


def subgroup(gens, lx, ly):
    elems = {(0, 0)}
    frontier = [(0, 0)]
    while frontier:
        nxt = []
        for e in frontier:
            for g in gens:
                h = ((e[0] + g[0]) % lx, (e[1] + g[1]) % ly)
                if h not in elems:
                    elems.add(h)
                    nxt.append(h)
        frontier = nxt
    return frozenset(elems)


def cyclic_quotient(k, lx, ly):
    index = lx * ly // len(k)
    for t in product(range(lx), range(ly)):
        seen, cur = set(), (0, 0)
        while True:
            coset = frozenset(((cur[0] + a) % lx, (cur[1] + b) % ly) for a, b in k)
            if coset in seen:
                break
            seen.add(coset)
            cur = ((cur[0] + t[0]) % lx, (cur[1] + t[1]) % ly)
        if len(seen) == index:
            return True
    return False


def kernel_subgroups(lx, ly):
    elems = list(product(range(lx), range(ly)))
    subs = {subgroup([a, b], lx, ly) for a in elems for b in elems}
    return sorted((k for k in subs if cyclic_quotient(k, lx, ly)), key=lambda k: (-len(k), sorted(k)))


def point_ops(k, lx, ly):
    def img(p, t):
        fx, fy = p in (1, 3), p in (2, 3)
        return ((lx - t[0]) % lx if fx else t[0], (ly - t[1]) % ly if fy else t[1])

    return [p for p in range(4) if all(img(p, t) in k for t in k)]


def sectors(points):
    out = []
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        has = points.__contains__
        if not has(1) and not has(3) and sx != 1:
            continue
        if not has(2) and not has(3) and sy != 1:
            continue
        if not has(1) and not has(2) and has(3) and sx != 1:
            continue
        out.append((sx, sy))
    return out


def read_count(root, prefix, lx, ly, sx, sy, rest):
    sid = "_".join([f"{prefix}count", str(lx), str(ly), str(sx), str(sy), *map(str, rest)])
    hbp = Path(root) / "shards" / sid / "run.hbp"
    text = hbp.read_text()
    line_ = next(l for l in text.splitlines() if l.startswith("SHELL_SCHUR|"))
    f = dict(p.split("=", 1) for p in line_.split("|")[1:] if "=" in p)
    if f.get("result") != "PASS" or f.get("ambiguous") != "0":
        raise SystemExit(f"FULL_SPACE|error=count_not_certified|shard={sid}|json=0")
    return int(f["negative"]), sid


def main(argv):
    orbit = "--orbit" in argv
    args = [a for a in argv if a != "--orbit"]
    root = args[0]
    lx, ly = int(args[1]), int(args[2])
    rest = [int(a) for a in args[3:8]]
    T = subgroup([(1, 0), (0, 1)], lx, ly)
    ks = kernel_subgroups(lx, ly)
    names = {}
    for k in ks:
        if k == T:
            names[k] = ""
            continue
        mode = next((m for m, v in MODES.items() if line(v, lx, ly) == k), None)
        if mode is None:
            raise SystemExit(f"FULL_SPACE|error=kernel_not_a_line|order={len(k)}|json=0")
        if "t" + mode not in names.values():
            names[k] = "t" + mode
        else:  # the same subgroup reached by two line vectors (e.g. d = a on 2x2)
            names[k] = "t" + mode
    lines = [f"FULL_SPACE|L={lx}x{ly}|reduction=mobius_over_line_subgroups|t_milli={rest[2]}|kernels={len(ks)}|orbit={int(orbit)}|json=0"]
    nk = {}
    for k in ks:
        prefix = names[k]
        src = prefix
        if orbit and prefix == "ta" and any(names[j] == "td" for j in ks):
            src = "td"
        if orbit and prefix == "ty" and lx == ly and any(names[j] == "tx" for j in ks):
            src = "tx"
        pts = point_ops(k, lx, ly) if k != T else [0, 1, 2, 3]
        total = 0
        for sx, sy in sectors(pts):
            n, sid = read_count(root, src, lx, ly, sx, sy, rest)
            total += n
            lines.append(f"SECTOR_COUNT|kernel={prefix or 'T'}|source={src or 'T'}|shard={sid}|negative={n}|json=0")
        nk[k] = total
        lines.append(f"INVARIANT_COUNT|kernel={prefix or 'T'}|order={len(k)}|points={''.join(map(str, pts))}|N={total}|json=0")
    iso = {}
    for k in sorted(ks, key=len, reverse=True):
        iso[k] = nk[k] - sum(iso[j] for j in iso if j > k)
        lines.append(f"ISOTYPIC|kernel={names[k] or 'T'}|count={iso[k]}|json=0")
    full = sum(iso.values())
    lines.append(f"FULL_SPACE_COUNT|L={lx}x{ly}|t_milli={rest[2]}|N={full}|json=0")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1:])
