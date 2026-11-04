#!/usr/bin/env python3
"""Multiplicities from prefix traces, by my own triangular solve, against my character table. Integer only, json=0.
usage: readback.py LOG TABLE_LOG
"""
import sys


def main(argv):
    tables = {}
    with open(argv[1]) as h:
        for line in h:
            if line.startswith("OWN_TABLE_M|"):
                cells = dict(p.split("=", 1) for p in line.strip().split("|")[1:] if "=" in p)
                tables[cells["L"]] = cells["table"]
    with open(argv[0]) as h:
        for line in h:
            if not line.startswith("OWN_REAL_ANNIHILATE|"):
                continue
            cells = dict(p.split("=", 1) for p in line.strip().split("|")[1:] if "=" in p)
            roots = [int(x) for x in cells["roots"].split(",")]
            traces = [int(x) for x in cells["prefix_traces"].split(",")]
            m = [0] * len(roots)
            exact = True
            for j in range(len(roots) - 1, -1, -1):
                rest = traces[j]
                for i in range(j + 1, len(roots)):
                    term = m[i]
                    for c in roots[:j]:
                        term *= roots[i] - c
                    rest -= term
                pivot = 1
                for c in roots[:j]:
                    pivot *= roots[j] - c
                if rest % pivot:
                    exact = False
                m[j] = rest // pivot
            text = ",".join("%d:%d" % (c, x) for c, x in zip(roots, m))
            print("OWN_REAL_READBACK|L=%s|columns_nonzero=%s|exact=%d|last_trace=%d|table=%s|equals_character_table=%d|json=0"
                  % (cells["L"], cells["columns_nonzero"], exact, traces[-1], text, text == tables.get(cells["L"])))


if __name__ == "__main__":
    main(sys.argv[1:])
