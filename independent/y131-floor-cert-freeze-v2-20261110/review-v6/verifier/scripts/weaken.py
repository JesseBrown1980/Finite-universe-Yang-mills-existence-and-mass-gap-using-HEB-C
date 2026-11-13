#!/usr/bin/env python3
# weaken.py -- verifier seat (opus55), final-head verification 5. Integers only.
# Rewrites one floorcert certificate into a WEAKER but still valid one:
#   python3 -I weaken.py CERT t NUM/DEN                 lower the claimed t (the proved lower bound)
#   python3 -I weaken.py CERT vfrom OTHER_CERT NUM/DEN  take the class vector v of OTHER_CERT (same m0, same keys) and t
#   python3 -I weaken.py CERT vscale P/Q NUM/DEN        multiply v of the classes with odd key by P/Q (integer floor), set t
# The header keeps m0, r, f, cap, rowhash and keyshash (none depends on v or t).
import sys, re


def rows(path):
    L = open(path).read().split("\n")
    return L[0], [l for l in L[1:] if l.strip() and not l.startswith("#")], [l for l in L[1:] if l.startswith("#")]


def main():
    cert, mode = sys.argv[1], sys.argv[2]
    hdr, R, com = rows(cert)
    if mode == "t":
        t = sys.argv[3]
        V = R
    elif mode == "vfrom":
        _, R2, _ = rows(sys.argv[3])
        t = sys.argv[4]
        v2 = {}
        for l in R2:
            k, M, v = l.split()
            v2[k] = v
        V = []
        for l in R:
            k, M, v = l.split()
            V.append("%s %s %s" % (k, M, v2[k]))
    elif mode == "vscale":
        p, q = map(int, sys.argv[3].split("/"))
        t = sys.argv[4]
        V = []
        for l in R:
            k, M, v = l.split()
            vv = int(v)
            if int(k) % 2 == 1:
                vv = vv * p // q
            V.append("%s %s %d" % (k, M, max(vv, 1)))
    else:
        raise SystemExit("unknown mode")
    hdr2 = re.sub(r" t=[0-9]+/[0-9]+ ", " t=%s " % t, hdr)
    open(cert, "w", newline="\n").write("\n".join([hdr2] + V + com) + "\n")
    print("WEAKEN|mode=%s|t=%s|rows=%d|header_changed=%d" % (mode, t, len(V), 1 if hdr2 != hdr else 0))


main()
