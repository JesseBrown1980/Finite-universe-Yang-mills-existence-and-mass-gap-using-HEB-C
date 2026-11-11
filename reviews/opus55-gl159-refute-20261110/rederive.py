#!/usr/bin/env python3
"""Re-derive GL1/GL3 from the PR's measured LEVEL_ENCLOSURE rows with own integer code,
and re-run the frozen-interval comparison.  No float, no fractions module."""
import sys
rows = open(sys.argv[1]).read().splitlines()
L = {}
for s in rows:
    if s.startswith("LEVEL_ENCLOSURE|"):
        f = dict(it.split("=", 1) for it in s.split("|")[1:] if "=" in it)
        def q(t):
            n, d = t.split("/"); return int(n), int(d)
        L[(f["lattice"], int(f["r"]), f["level"])] = (q(f["lo"]), q(f["hi"]))
def sub(a, b): return (a[0] * b[1] - b[0] * a[1], a[1] * b[1])
def lt(a, b): return a[0] * b[1] < b[0] * a[1]
def le(a, b): return a[0] * b[1] <= b[0] * a[1]
def dec(a, k=9, up=False):
    n, d = a; s = 10 ** k
    v = -((-n * s) // d) if up else (n * s) // d
    return str(v // s) + "." + str(v % s).rjust(k, "0")
def verdict(lo, hi, plo, phi):
    if le(plo, lo) and le(hi, phi): return "MET"
    if lt(hi, plo) or lt(phi, lo): return "MISS"
    return "NOT_RESOLVED"
for lat, r in (("3x4", 27), ("3x4", 81), ("3x4", 729), ("3x3", 729)):
    e8lo, e8hi = L[(lat, r, "E8")]; e9lo, e9hi = L[(lat, r, "E9")]
    dhi = sub(e9hi, e8lo); dlo = sub(e9lo, e8hi)
    clo = (r * (3 * r * dhi[1] - dhi[0]), dhi[1]); chi = (r * (3 * r * dlo[1] - dlo[0]), dlo[1])
    v = verdict(clo, chi, (21, 1), (21 * r + 64, r))
    print("R_GL1|lattice=%s|r=%d|c_hat=[%s,%s]|frozen=[21,%s]|verdict=%s|json=0" % (lat, r, dec(clo), dec(chi, up=True), dec((21 * r + 64, r), up=True), v))
W = {}
for lat in ("3x3", "3x4"):
    for r in (27, 81, 243, 729):
        e1lo, e1hi = L[(lat, r, "E1")]; e8lo, e8hi = L[(lat, r, "E8")]
        W[(lat, r)] = (sub(e8lo, e1hi), sub(e8hi, e1lo))
for lat, r in (("3x3", 27), ("3x3", 81), ("3x4", 27), ("3x4", 81)):
    a = W[(lat, r)]; b = W[(lat, 3 * r)]
    assert a[0][0] > 0 and b[0][0] > 0
    rlo = (a[0][0] * b[1][1], a[0][1] * b[1][0]); rhi = (a[1][0] * b[0][1], a[1][1] * b[0][0])
    v = verdict(rlo, rhi, (6, 1), (27, 2))
    print("R_GL3|lattice=%s|r=%d|rho=[%s,%s]|frozen=[6,27/2]|verdict=%s|json=0" % (lat, r, dec(rlo, 6), dec(rhi, 6, True), v))
