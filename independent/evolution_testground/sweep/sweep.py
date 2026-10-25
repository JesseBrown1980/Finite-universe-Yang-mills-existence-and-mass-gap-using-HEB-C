#!/usr/bin/env python3
"""Rung sweep through the HTTP-0 test ground: matrix-jump evolution on the
four Z2xZ2 sectors, global E0/E1 = two lowest of the union of sector levels,
compared with the certified rung brackets. Integer-only, json=0."""
import os, sys, urllib.request
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNGS = [0, 1, 2, 3, 5, 6, 8, 9, 15, 21, 27, 45, 63, 81, 135, 189, 243]
SECT = ("pp", "pm", "mp", "mm")

def cert():
    out = {}
    for line in open(os.environ.get("HEBC_RUNGS", os.path.join(S, "ladder", "rungs.log"))):
        if line.startswith("rung r="):
            t = line.split()
            r = int(t[1][2:]); out[r] = (int(t[4].split("/")[0]), int(t[7].split("/")[0]), int(t[10].split("/")[0]))
    return out

def field(line, k):
    for kv in line.strip().split("|"):
        if kv.startswith(k + "="):
            return kv.split("=", 1)[1]

def jexp(r, gap_milli):
    c = (24 * 12 * r * 33 // 32 + 576) // 48 + 1
    need = 60 * c * 1000 // max(1, gap_milli)       # 60 e-folds of the slowest mode
    return max(10, need.bit_length() + 1)           # Gershgorin c up to ~2x Emax; x4 reps covers the rest

C = cert()
out = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sweep.hbp"), "a")
for r in [int(x) for x in sys.argv[1:]] or RUNGS:
    gl = C.get(r, (0, 0, 5))[2] if r in C else max(4, 5600 // max(1, r))
    J = jexp(r, max(1, gl))
    lv = []
    for s in SECT:
        line = urllib.request.urlopen("http://127.0.0.1:5099/jump/%s/1/%d/%d" % (s, r, J), timeout=900).read().decode()
        e0, e1 = int(field(line, "E0").split("/")[0]), int(field(line, "E1").split("/")[0])
        d0, d1, ms = int(field(line, "dE0")), int(field(line, "dE1")), int(field(line, "ms"))
        lv += [(e0, s, 0), (e1, s, 1)]
        out.write("SWEEP|kind=sector|r=%d|sector=%s|J=%d|E0=%d/1000000|E1=%d/1000000|dE0=%d|dE1=%d|ms=%d|json=0\n" % (r, s, J, e0, e1, d0, d1, ms))
    lv.sort()
    (E0, s0, _), (E1, s1, k1) = lv[0], lv[1]
    gap = E1 - E0
    c = C.get(r)
    if c:
        U, L, G = c
        ok = "yes" if (E0 * 1 < U * 1000 + 1000 and E1 >= L * 1000 and gap >= G * 1000) else "NO"
        cs = "E0<%d E1>%d gap>%d" % (U, L, G)
    else:
        ok, cs = "-", "not yet certified"
    out.write("SWEEP|kind=global|r=%d|E0=%d/1000000|E0_sector=%s|E1=%d/1000000|E1_sector=%s%s|gap=%d/1000000|certified=%s|consistent=%s|json=0\n"
              % (r, E0, s0, E1, s1, "" if k1 == 0 else "_second", gap, cs.replace(" ", ","), ok))
    out.flush()
    print("r=%-4d E0=%d.%06d [%s]  E1=%d.%06d [%s%s]  gap=%d.%06d  | cert %s | consistent %s | J=%d"
          % (r, E0 // 10**6, E0 % 10**6, s0, E1 // 10**6, E1 % 10**6, s1, "" if k1 == 0 else "#2", gap // 10**6, gap % 10**6, cs, ok, J), flush=True)
