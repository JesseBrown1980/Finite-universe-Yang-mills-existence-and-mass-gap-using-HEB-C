#!/usr/bin/env python3
"""Acceptance gates for the global-lock measurement (PR #159).  Integer only, json=0.

Each gate recomputes its reference value from the lattice with the filed independent
code reviews/opus55-gl159-refute-20261110/indep_gl.py (other link numbering, other
plaquette orientation, other gauge tree, other elimination), and compares the
measurement with that recomputation.  A receipt field is read only as the value under
test.  A failing gate prints FAILED|check=<name>|json=0 and exits 1.

usage:
  gl_accept.py module  DIR LXxLY            gates on the code in DIR (gl_measure.py, gl_core.py)
  gl_accept.py receipt LXxLY ROWS INDEP...  gates on a file of gl_measure rows; INDEP are files
                                            of indep_gl.py rows (one r each) for the level index
  gl_accept.py replay  ROWS_A ROWS_B        rows equal on shared fields (timing, hashes set aside)
  gl_accept.py electric [sign=-1]           link term h_E has spectrum 0,3,6 (exact matrix identity)

Gate names:
  accept_census_counts_equal_independent_recount
  accept_m4_exterior_edges_complete          every M=4 row: same move-count profile as the recount
  accept_rho44_equals_independent_recount
  accept_P2max_equals_independent_recount
  accept_m6_neighbour_count_equals_independent_recount
  accept_floor_at_most_certified_value       (3N+4r-rho44-l)(6r-l) >= P2max with recounted rho44, P2max
  accept_level_rows_carry_the_floor_row
  accept_lower_endpoint_below_floor
  accept_independent_rows_from_filed_script
  accept_independent_rows_match_recount
  accept_level_has_independent_enclosure
  accept_level_index_E1 / _E8 / _E9          enclosure meets the independent enclosure of that level
  accept_replay_computational_rows_equal
  accept_electric_link_spectrum_0_3_6
"""
import contextlib
import hashlib
import io
import sys
from collections import Counter
from itertools import permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
REVIEW = HERE.parents[2].joinpath("reviews", "opus55-gl159-refute-20261110")
# The refuter's filed code, imported as filed.  Run this script with python3 -B so that the
# review folder stays as the manifest lists it.
sys.path.insert(0, str(REVIEW))
import indep_gl as ig  # noqa: E402
R_LIST = (27, 81, 243, 729)
SET_ASIDE = ("ms", "peak_kb", "script_sha256", "core_sha256")


def check(t, label):
    if not t:
        print("FAILED|check=" + label + "|json=0", flush=True)
        raise SystemExit(1)


def emit(label, **f):
    print(label + "|" + "|".join(str(k) + "=" + str(v) for k, v in f.items()) + "|json=0", flush=True)


def rows_of(path):
    out = []
    for s in Path(path).read_text().splitlines():
        if not s:
            continue
        parts = s.split("|")
        out.append((parts[0], dict(p.split("=", 1) for p in parts[1:] if "=" in p)))
    return out


def recount(LX, LY):
    """rho44, P2max, the M>=6 neighbour count and the M=4 row profiles, from the lattice,
    by the filed independent code."""
    tor = ig.Torus(LX, LY)
    md = ig.Model(tor)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        flats, m3, m4 = ig.census(md)
        rho, p2 = ig.floor_data(md, m4)
    text = buf.getvalue()
    sys.stdout.write(text)
    sys.stdout.flush()
    m6 = None
    for s in text.splitlines():
        if s.startswith("I_FLOOR_INPUTS|"):
            m6 = int(dict(p.split("=", 1) for p in s.split("|")[1:] if "=" in p)["m6plus_nbrs"])
    prof = Counter()
    for h in m4:
        prof[(md.w[h], tuple(sorted((-1 if x == h else md.m[x], c) for x, c in md.nbr(h))))] += 1
    return dict(N3=tor.NMOVE, flat=len(flats), m3=len(m3), m4=len(m4), rho=rho, p2=p2, m6=m6,
                prof=prof)


def gate_module(d, LX, LY):
    ref = recount(LX, LY)
    # gl_measure.py and its gl_core.py are taken from the folder under test
    sys.path.insert(0, str(Path(d).resolve()))
    import gl_measure as gm
    lat = gm.Lattice(LX, LY)
    md = gm.Model(lat, "")
    flats, m3, m4 = gm.census(md)
    check((len(flats), len(m3), len(m4)) == (ref["flat"], ref["m3"], ref["m4"]) and md.N3 == ref["N3"],
          "accept_census_counts_equal_independent_recount")
    prof = Counter()
    for h in m4:
        prof[(md.w(h), tuple(sorted((-1 if x == h else md.m(x), c) for x, c in md.nbr(h))))] += 1
    emit("ACCEPT_M4_ROWS", rows=sum(prof.values()), distinct_profiles=len(prof),
         distinct_profiles_recount=len(ref["prof"]),
         moves_to_m6plus=sum(n * sum(c for m, c in p if m >= 6) for (w, p), n in prof.items()),
         moves_to_m6plus_recount=sum(n * sum(c for m, c in p if m >= 6) for (w, p), n in ref["prof"].items()))
    check(prof == ref["prof"], "accept_m4_exterior_edges_complete")
    rho, p2 = gm.floor_inputs(md, m4, set(flats) | set(m3))
    check(rho == ref["rho"], "accept_rho44_equals_independent_recount")
    check(p2 == ref["p2"], "accept_P2max_equals_independent_recount")
    for r in R_LIST:
        n = gm.floor_value(md, r, rho, p2)
        ok = ig.floor_ok(ref["N3"], r, ref["rho"], ref["p2"], n, gm.FD)
        emit("ACCEPT_FLOOR", lattice=str(LX) + "x" + str(LY), r=r, floor_num=n, floor_den=gm.FD,
             valid_by_recount=int(ok))
        check(ok, "accept_floor_at_most_certified_value")
    emit("ACCEPT_END", gate="module", lattice=str(LX) + "x" + str(LY), result="PASS")


def gate_receipt(LX, LY, rows_file, indep_files):
    ref = recount(LX, LY)
    lattice = str(LX) + "x" + str(LY)
    rows = rows_of(rows_file)
    fi = [f for t, f in rows if t == "FLOOR_INPUTS"]
    check(len(fi) == 1 and int(fi[0]["m4_orbits"]) == ref["m4"],
          "accept_census_counts_equal_independent_recount")
    check(int(fi[0]["rho44"]) == ref["rho"], "accept_rho44_equals_independent_recount")
    check(int(fi[0]["P2max"]) == ref["p2"], "accept_P2max_equals_independent_recount")
    check(int(fi[0]["m6_neighbours"]) == ref["m6"], "accept_m6_neighbour_count_equals_independent_recount")
    floors = {}
    for t, f in rows:
        if t == "FLOOR":
            r, n, d = int(f["r"]), int(f["floor_num"]), int(f["floor_den"])
            check(f["lattice"] == lattice and r not in floors, "accept_level_rows_carry_the_floor_row")
            check(ig.floor_ok(ref["N3"], r, ref["rho"], ref["p2"], n, d), "accept_floor_at_most_certified_value")
            floors[r] = (n, d)
    script = hashlib.sha256(REVIEW.joinpath("indep_gl.py").read_bytes()).hexdigest()
    indep = {}
    for p in indep_files:
        for t, f in rows_of(p):
            if t == "I_BEGIN":
                check(f["script_sha256"] == script, "accept_independent_rows_from_filed_script")
            if t == "I_FLOOR_INPUTS":
                check((int(f["rho44"]), int(f["P2max"]), int(f["m6plus_nbrs"])) == (ref["rho"], ref["p2"], ref["m6"]),
                      "accept_independent_rows_match_recount")
            if t == "I_LEVEL" and f["lattice"] == lattice:
                indep[(int(f["r"]), f["level"])] = (int(f["lo_num"]), int(f["hi_num"]), int(f["den"]))
    levels = 0
    for t, f in rows:
        if t != "LEVEL":
            continue
        r, lvl = int(f["r"]), f["level"]
        check(f["lattice"] == lattice and r in floors
              and (int(f["floor_num"]), int(f["floor_den"])) == floors[r],
              "accept_level_rows_carry_the_floor_row")
        check(f["lo_num"] != "NONE", "accept_lower_endpoint_below_floor")
        lo, hi, den = int(f["lo_num"]), int(f["hi_num"]), int(f["den"])
        fn, fd = floors[r]
        check(lo <= hi and lo * fd < fn * den, "accept_lower_endpoint_below_floor")
        check((r, lvl) in indep, "accept_level_has_independent_enclosure")
        ilo, ihi, iden = indep[(r, lvl)]
        meet = lo * iden <= ihi * den and ilo * den <= hi * iden
        emit("ACCEPT_LEVEL", lattice=lattice, r=r, level=lvl, lo_num=lo, hi_num=hi, den=den,
             indep_lo_num=ilo, indep_hi_num=ihi, indep_den=iden, meets=int(meet))
        check(meet, "accept_level_index_" + lvl)
        levels += 1
    check(levels > 0 and levels == 3 * len(floors), "accept_level_has_independent_enclosure")
    emit("ACCEPT_END", gate="receipt", lattice=lattice, file_sha256=hashlib.sha256(Path(rows_file).read_bytes()).hexdigest(),
         floors=len(floors), levels=levels, result="PASS")


def computational(path):
    out = []
    for t, f in rows_of(path):
        out.append((t, tuple((k, v) for k, v in f.items() if k not in SET_ASIDE)))
    return out


def gate_replay(a, b):
    ra, rb = computational(a), computational(b)
    # Row by row: same tag, and every field present in both rows equal.  A field that one script
    # version prints and the other lacks (k3plus in the header and m3_plus in BALLS, absent from
    # the first runs) is named in the output row as TAG.field and set aside.
    only_one, first = [], None
    for i, ((ta, fa), (tb, fb)) in enumerate(zip(ra, rb)):
        da, db = dict(fa), dict(fb)
        for k in list(da) + list(db):
            if (k in da) != (k in db) and ta + "." + k not in only_one:
                only_one.append(ta + "." + k)
        if ta != tb or any(da[k] != db[k] for k in da if k in db):
            first = i
            break
    emit("ACCEPT_REPLAY", rows_a=len(ra), rows_b=len(rb),
         first_differing_row="NONE" if first is None else first + 1,
         first_differing_tag="NONE" if first is None else ra[first][0], set_aside=",".join(SET_ASIDE),
         fields_in_one_file_only=",".join(only_one) if only_one else "NONE")
    check(len(ra) == len(rb) and first is None and len(ra) > 0, "accept_replay_computational_rows_equal")
    emit("ACCEPT_END", gate="replay", rows=len(ra), result="PASS")


def matmul(a, b):
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def gate_electric(sign):
    """h_E = 3I - sum over the 3 transpositions t of (f -> f(. t)) on functions on S3.
    The class sum of the transpositions is central: it acts as 3, 0, -3 on the trivial,
    standard, sign isotypic parts (dimensions 1, 4, 1), so h_E has spectrum 0, 3, 6.
    Tested here as the exact integer identity h(h-3)(h-6) = 0 with trace 18, trace h^2 = 72."""
    g = sorted(permutations((0, 1, 2)))
    idx = {p: i for i, p in enumerate(g)}
    mul = lambda a, b: tuple(a[b[i]] for i in range(3))
    tr = [p for p in g if p != (0, 1, 2) and mul(p, p) == (0, 1, 2)]
    check(len(tr) == 3, "accept_electric_link_spectrum_0_3_6")
    h = [[sign * 3 * int(i == j) for j in range(6)] for i in range(6)]
    for p in g:
        for t in tr:
            h[idx[mul(p, t)]][idx[p]] -= sign
    eye = lambda c: [[c * int(i == j) for j in range(6)] for i in range(6)]
    sub = lambda a, b: [[a[i][j] - b[i][j] for j in range(6)] for i in range(6)]
    z = matmul(matmul(h, sub(h, eye(3))), sub(h, eye(6)))
    t1 = sum(h[i][i] for i in range(6))
    h2 = matmul(h, h)
    t2 = sum(h2[i][i] for i in range(6))
    sym = all(h[i][j] == h[j][i] for i in range(6) for j in range(6))
    zero = all(v == 0 for row in z for v in row)
    emit("ACCEPT_ELECTRIC", sign=sign, symmetric=int(sym), cubic_identity=int(zero), trace=t1, trace_square=t2,
         multiplicities_0_3_6="1,4,1" if (zero and t1 == 18 and t2 == 72) else "NOT_ESTABLISHED")
    check(sym and zero and t1 == 18 and t2 == 72, "accept_electric_link_spectrum_0_3_6")
    emit("ACCEPT_END", gate="electric", result="PASS")


def main():
    a = sys.argv[1:]
    check(len(a) >= 1 and a[0] in ("module", "receipt", "replay", "electric"), "usage")
    if a[0] == "module":
        check(len(a) == 3, "usage")
        lx, ly = a[2].split("x")
        gate_module(a[1], int(lx), int(ly))
    elif a[0] == "receipt":
        check(len(a) >= 4, "usage")
        lx, ly = a[1].split("x")
        gate_receipt(int(lx), int(ly), a[2], a[3:])
    elif a[0] == "replay":
        check(len(a) == 3, "usage")
        gate_replay(a[1], a[2])
    else:
        check(len(a) == 1 or a[1:] == ["sign=-1"], "usage")
        gate_electric(-1 if len(a) == 2 else 1)


if __name__ == "__main__":
    main()
