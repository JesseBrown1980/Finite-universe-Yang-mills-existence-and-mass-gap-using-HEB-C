#!/usr/bin/env python3
"""End-to-end falsification on tori small enough to hold the WHOLE gauge-invariant space.
Builds K (orbit-indicator basis, symmetric) and W exactly from my own Torus (indep_gl.py),
then by exact integer inertia:
  * tests the floor lemma: neg(K_CC - fl W_CC) must be 0 (C = complement of flats + M3);
  * tests the PR code's LEVEL rows: count(H < lo_j) <= j-1 and count(H < hi_j) >= j.
usage: fullspace.py LXxLY r[,r..] [pr_rows_file]
Integer only.
"""
import sys
sys.path.insert(0, "/mnt/c/tmp/opus55/gl159-refute")
from indep_gl import Torus, Model, census, floor_data, floor_num, floor_ok, neg_count, out, FG, CONJ  # noqa


def all_orbits(md):
    t = md.t
    n = len(t.kept)
    ids = set()
    tot = 6 ** n
    for code in range(tot):
        k = []
        c = code
        for _ in range(n):
            k.append(c % 6)
            c //= 6
        key = min(tuple(cj[a] for a in k) for cj in CONJ)
        ids.add(md.intern(key))
    return sorted(ids)


def main():
    LX, LY = (int(v) for v in sys.argv[1].split("x"))
    rs = [int(v) for v in sys.argv[2].split(",")]
    prf = sys.argv[3] if len(sys.argv) > 3 else ""
    t = Torus(LX, LY)
    md = Model(t)
    flats, m3, m4 = census(md)
    S = all_orbits(md)
    n = t.V + 1
    dim = (6 ** n + 3 * 2 ** n + 2 * 3 ** n) // 6
    out("F_SPACE", lattice=sys.argv[1], orbits=len(S), burnside=dim, match=(len(S) == dim))
    pos = {x: i for i, x in enumerate(S)}
    N3 = t.NMOVE
    nbrs = {x: md.nbr(x) for x in S}
    for x in S:
        for y, c in nbrs[x]:
            back = dict(nbrs[y]).get(x, 0)
            if md.w[x] * c != md.w[y] * back:
                out("F_FAIL", check="detailed_balance")
                raise SystemExit(2)
    rho, p2 = floor_data(md, m4)
    Pset = set(flats) | set(m3)
    C = [x for x in S if x not in Pset]
    cpos = {x: i for i, x in enumerate(C)}

    def Kmat(r, idx, sel):
        m = len(sel)
        K = [[0] * m for _ in range(m)]
        for x in sel:
            i = idx[x]
            K[i][i] += md.w[x] * (N3 + r * md.m[x])
            for y, c in nbrs[x]:
                j = idx.get(y)
                if j is not None:
                    K[i][j] -= md.w[x] * c
        return K

    pr = []
    if prf:
        for s in open(prf).read().splitlines():
            if s.startswith("LEVEL|"):
                f = dict(it.split("=", 1) for it in s.split("|")[1:] if "=" in it)
                pr.append(f)
    for r in rs:
        fn = floor_num(N3, r, rho, p2)
        KC = Kmat(r, cpos, C)
        mC = len(C)
        Wc = [md.w[x] for x in C]
        nfl = neg_count([[FG * KC[i][j] - (fn * Wc[i] if i == j else 0) for j in range(mC)] for i in range(mC)])
        out("F_FLOOR_TEST", lattice=sys.argv[1], r=r, rho44=rho, P2max=p2, floor_num=fn, floor_den=FG,
            neg_KCC_minus_floor=nfl, lemma_holds=(nfl == 0))
        K = Kmat(r, pos, S)
        Wd = [md.w[x] for x in S]
        m = len(S)

        def cnt(a, b):
            return neg_count([[b * K[i][j] - (a * Wd[i] if i == j else 0) for j in range(m)] for i in range(m)])
        for f in pr:
            if int(f["r"]) != r:
                continue
            j = int(f["level"][1:])
            d = int(f["den"])
            hi = int(f["hi_num"])
            ch = cnt(hi, d)
            okh = ch is not None and ch >= j
            if f["lo_num"] != "NONE":
                cl = cnt(int(f["lo_num"]), d)
                okl = cl is not None and cl <= j - 1
            else:
                cl, okl = "NONE", "NONE"
            out("F_PR_LEVEL", lattice=sys.argv[1], r=r, level=f["level"], lo=f["lo_dec"], hi=f["hi_dec"],
                count_below_lo=cl, count_below_hi=ch, lower_true=okl, upper_true=okh)


if __name__ == "__main__":
    main()
