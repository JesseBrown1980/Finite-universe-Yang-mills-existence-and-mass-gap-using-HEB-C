# Writes a signature table for the S3 gauge theory on an Lx x Ly torus with no store, from the local rule alone, in the format `prodvec fit` reads.
#
# A move on link l by a transposition s changes only the two plaquettes that hold l. In the frame of l, their holonomies x and y become s x and s y. So the change in
# (a, b), the numbers of plaquettes holding a transposition and a 3-cycle, depends only on the pattern of the link:
#
#   pattern  x, y                       moves as (da, db) x count
#   ee       e, e                       (+2, 0) x 3
#   eT       e, t                       (0, 0) x 1, (0, +1) x 2
#   eC       e, c                       (+2, -1) x 3
#   TT=      t, t, the same in the frame  (-2, 0) x 1, (-2, +2) x 2
#   TTx      t, t', different           (-2, +1) x 2, (-2, +2) x 1
#   TC       t, c                       (0, -1) x 1, (0, 0) x 2
#   CC       c, c'                      (+2, -2) x 3
#
# Each plaquette holds 4 links, so with n_p the number of links of pattern p:
#   4a = n_eT + n_TC + 2 n_TT,   4b = n_eC + n_TC + 2 n_CC,   nl = the sum of all n_p.
# The links with both plaquettes in a set S of plaquettes number at most 2|S| - min(ceil(2 sqrt |S|), min(Lx, Ly), ceil(2 sqrt(P - |S|))):
#   with no full row and no full column, S touches rows A and columns B with AB >= |S|, and each touched row and column gives at least 2 boundary links;
#   with a full row and no full column, or the reverse, every column or every row gives at least 2;
#   with both, the complement has neither, so the first case applies to it.
#
# Every non-flat gauge orbit then has its row in this table: its lump, 3 nl on the diagonal, and its moves by lump. The table holds every integer point of those constraints, with a even,
# since the signs of all plaquettes multiply to +1. A vector with d a function of the lump has the ratio of `perroncert check` at that row, so the minimum over this table is a lower bound
# on that ratio over the whole space of orbits, for every torus with these sides. It uses no rows of H.
#
# usage: local_table.py LX LY OUT [--check TABLE]
#   --check TABLE  reads a census table from a real store and requires each of its signatures to be in this one, exactly. Exits 1 on any that is not.
# Integer only, json=0.
import sys

MOVES = {
    "ee": ((2, 0, 3),),
    "eT": ((0, 0, 1), (0, 1, 2)),
    "eC": ((2, -1, 3),),
    "TTs": ((-2, 0, 1), (-2, 2, 2)),
    "TTd": ((-2, 1, 2), (-2, 2, 1)),
    "TC": ((0, -1, 1), (0, 0, 2)),
    "CC": ((2, -2, 3),),
}


def ceil2sqrt(n):
    # The least integer v with v^2 >= 4 n.
    v = 0
    while v * v < 4 * n:
        v += 1
    return v


def adj_max(s, lx, ly):
    p = lx * ly
    if s == 0:
        return 0
    if s == p:
        return 2 * s
    return 2 * s - min(ceil2sqrt(s), min(lx, ly), ceil2sqrt(p - s))


def points(a, b, lx, ly):
    nl = 2 * lx * ly
    for tts in range(0, adj_max(a, lx, ly) + 1):
        for ttd in range(0, adj_max(a, lx, ly) - tts + 1):
            net = 4 * a - 2 * (tts + ttd)
            for tc in range(0, min(net, 4 * b) + 1):
                for cc in range(0, adj_max(b, lx, ly) + 1):
                    if 2 * cc + tc > 4 * b:
                        break
                    inner = tts + ttd + tc + cc
                    if inner > adj_max(a + b, lx, ly):
                        break
                    et = net - tc
                    ec = 4 * b - tc - 2 * cc
                    ee = nl - et - ec - inner
                    if ee < 0:
                        continue
                    yield {"ee": ee, "eT": et, "eC": ec, "TTs": tts, "TTd": ttd, "TC": tc, "CC": cc}


def signature(a, b, n):
    near = {}
    flat = 0
    for pat, count in n.items():
        if count == 0:
            continue
        for da, db, c in MOVES[pat]:
            t = (a + da, b + db)
            if t == (0, 0):
                flat += c * count
            else:
                near[t] = near.get(t, 0) + c * count
    return flat, near


def main():
    lx, ly, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    p, nl = lx * ly, 2 * lx * ly
    lumps = [(a, b) for a in range(0, p + 1, 2) for b in range(0, p - a + 1)]
    index = {v: i for i, v in enumerate(lumps)}
    seen = {}
    rows = 0
    for (a, b) in lumps:
        if (a, b) == (0, 0):
            continue
        for n in points(a, b, lx, ly):
            flat, near = signature(a, b, n)
            if any(t not in index or t[0] < 0 or t[1] < 0 for t in near):
                raise SystemExit("a move leaves the lumps at %s %s" % ((a, b), n))
            key = (a, b, flat, tuple(sorted(near.items())))
            if key not in seen:
                seen[key] = rows
                rows += 1
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        for i, (a, b) in enumerate(lumps):
            f.write("LUMP|id=%d|a=%d|b=%d|rows=0|json=0\n" % (i, a, b))
        for (a, b, flat, near), row in sorted(seen.items(), key=lambda kv: kv[1]):
            text = ",".join("%d:%d" % (index[t], c) for t, c in near)
            f.write("SIG|lump=%d|diag=%d|flat=%d|rows=1|row=%d|n=%s|json=0\n" % (index[(a, b)], 3 * nl, flat, row, text))
    print("LOCAL_TABLE|Lx=%d|Ly=%d|nl=%d|lumps=%d|signatures=%d|json=0" % (lx, ly, nl, len(lumps), len(seen)))
    if "--check" in sys.argv:
        names, missing, total, rows_total, self_moved = {}, 0, 0, 0, 0
        for line in open(sys.argv[sys.argv.index("--check") + 1], encoding="utf-8"):
            f = dict(x.split("=", 1) for x in line.strip().split("|")[1:] if "=" in x)
            if line.startswith("LUMP|"):
                names[int(f["id"])] = (int(f["a"]), int(f["b"]))
            elif line.startswith("SIG|"):
                a, b = names[int(f["lump"])]
                near = {}
                if f["n"]:
                    for pair in f["n"].split(","):
                        i, c = pair.split(":")
                        near[names[int(i)]] = int(c)
                # A move that returns to its own orbit shows as a smaller diagonal. It is a move into the row's own lump.
                back = 3 * nl - int(f["diag"])
                self_moved += 1 if back else 0
                if back:
                    near[(a, b)] = near.get((a, b), 0) + back
                key = (a, b, int(f["flat"]), tuple(sorted(near.items())))
                total += 1
                rows_total += int(f["rows"])
                if key not in seen:
                    missing += 1
                    if missing <= 8:
                        print("LOCAL_CHECK_MISSING|a=%d|b=%d|flat=%s|near=%s|rows=%s|row=%s|json=0" % (a, b, f["flat"], sorted(near.items()), f["rows"], f["row"]))
        print("LOCAL_CHECK|store_signatures=%d|store_rows=%d|signatures_with_a_move_back_to_their_own_orbit=%d|not_in_the_local_table=%d|json=0" % (total, rows_total, self_moved, missing))
        sys.exit(1 if missing else 0)


main()
