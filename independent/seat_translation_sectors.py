#!/usr/bin/env python3
"""Exact Z2 x Z2 translations and integer sector matrices for finite S3 torus.

Uses PR7's native-hash-matched, independent orbit model. The lattice action
is first translated on all eight oriented links, then gauge fixed and
conjugation-canonicalized. No floats, Fraction, JSON, spectral guesses,
or preallocated 23-billion-address namespace.
Run: python3 independent/seat_translation_sectors.py /tmp/sectors
"""
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
from io import StringIO
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
EXPECTED_OPERATOR_SHA = "b6c608f50f81f3bf48fb0203b48e0e3bfc867037dc1d0a96633aa80b962137f3"
EXPECTED_BLOCK_SHA = {
    "pp": "fb6dbb3acbd411f61779f98881e6545d21ab7a39816c351d755fafe2c3f2c652",
    "pm": "9dc22f4bb6f410ebfcdc0bfb3854bf6d2827901ee379ed685772649d28315d48",
    "mp": "88eb8250eaf85815f155f09656f8a4dd19733148dd9e4505af978bed5974a75b",
    "mm": "d7dce164177f2b5498a367c9df78ff8d64c8d173a262daa65815b321ff21b653",
}
EXPECTED_DIM = {"pp": 385, "pm": 336, "mp": 336, "mm": 336}
EXPECTED_NNZ = {"pp": 7593, "pm": 6526, "mp": 6526, "mm": 6400}


def translate(U, dx, dy):
    """Pull back each x- and y-oriented link by lattice translation."""
    def vertex(x, y):
        return 2 * (x % 2) + (y % 2)
    shifted = [0] * 8
    for x in range(2):
        for y in range(2):
            a = vertex(x, y)
            b = vertex(x + dx, y + dy)
            shifted[a] = U[b]
            shifted[4 + a] = U[4 + b]
    return shifted


def build():
    with redirect_stdout(StringIO()):
        m = runpy.run_path(str(HERE / "seat_yang_mills_audit.py"))
    keys, weights, mag, rows = (m[k] for k in ("keys", "weights", "mag", "rowmaps"))
    n = len(keys)
    assert n == 1393 and sum(weights) == 7776
    assert sum(map(len, rows)) == 32385
    # PR7 independently serialized and pinned this exact operator SHA.
    assert m["operator_sha"] == EXPECTED_OPERATOR_SHA
    idx = {key: i for i, key in enumerate(keys)}
    perms = {}
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        p = [idx[m["enc"](m["can"](m["fix"](translate(m["rep"](m["dec"](k)), dx, dy))))]
             for k in keys]
        assert sorted(p) == list(range(n))
        for i in range(n):
            assert weights[i] == weights[p[i]]
            assert mag[i] == mag[p[i]]
            for j, v in rows[i].items():
                assert rows[p[i]].get(p[j], 0) == v
        perms[(dx, dy)] = p
    for a, pa in perms.items():
        for b, pb in perms.items():
            composed = perms[(a[0] ^ b[0], a[1] ^ b[1])]
            assert all(pa[pb[i]] == composed[i] for i in range(n))

    seen, orbits = set(), []
    for i in range(n):
        if i in seen:
            continue
        orbit = sorted({p[i] for p in perms.values()})
        seen.update(orbit)
        orbits.append(orbit)
    assert len(seen) == n and len(orbits) == 385
    assert Counter(map(len, orbits)) == {4: 319, 2: 51, 1: 15}

    sectors = {}
    for sx, sy, name in ((1, 1, "pp"), (1, -1, "pm"),
                         (-1, 1, "mp"), (-1, -1, "mm")):
        basis = []
        for orbit in orbits:
            root = orbit[0]
            signs = {}
            for (dx, dy), p in perms.items():
                j = p[root]
                sign = (sx if dx else 1) * (sy if dy else 1)
                if j in signs and signs[j] != sign:
                    break  # nontrivial character on the orbit stabilizer
                signs[j] = sign
            else:
                assert len(signs) == len(orbit)
                basis.append((root, signs))
        pos = {j: b for b, (_, signs) in enumerate(basis) for j in signs}
        rw = [len(signs) * weights[root] for root, signs in basis]
        rm = [mag[root] for root, _ in basis]
        rmaps = []
        for root, _ in basis:
            row = Counter()
            for j, z in rows[root].items():
                if j in pos:
                    b = pos[j]
                    row[b] += z * basis[b][1][j]
            rmaps.append({j: z for j, z in row.items() if z})

        assert len(basis) == EXPECTED_DIM[name]
        assert sum(map(len, rmaps)) == EXPECTED_NNZ[name]
        for i, row in enumerate(rmaps):
            for j, z in row.items():
                assert rw[i] * z == rw[j] * rmaps[j].get(i, 0)
        if name == "pp":
            assert all(sum(row.values()) == 0 for row in rmaps)

        # Intertwining identity: H * B = B * H_sector on all 1393 rows.
        # It is checked for every sector-basis vector, not just sampled.
        for b, (_, signs) in enumerate(basis):
            for i, row in enumerate(rows):
                lhs = sum(z * signs.get(j, 0) for j, z in row.items())
                rhs = (rmaps[pos[i]].get(b, 0) * basis[pos[i]][1][i]
                       if i in pos else 0)
                assert lhs == rhs, (name, b, i, lhs, rhs)
        sectors[name] = (rw, rm, rmaps)
    assert sum(map(lambda s: len(s[0]), sectors.values())) == n
    return sectors


def export(directory):
    sectors = build()
    directory.mkdir(parents=True, exist_ok=True)
    lines = []
    for name in ("pp", "pm", "mp", "mm"):
        w, mag, rows = sectors[name]
        raw = (str(len(w)) + "\n" + " ".join(map(str, w)) + "\n"
               + " ".join(map(str, mag)) + "\n"
               + "".join(f"{i} {j} {v}\n" for i, row in enumerate(rows)
                         for j, v in sorted(row.items()) if j >= i))
        digest = sha256(raw.encode("ascii")).hexdigest()
        assert digest == EXPECTED_BLOCK_SHA[name], (name, digest)
        (directory / (name + ".matrix")).write_bytes(raw.encode("ascii"))
        row = ("HEBC-TRANSLATION|result=PASS|sector=" + name
               + "|states=" + str(len(w))
               + "|nnz=" + str(sum(map(len, rows)))
               + "|matrix_sha256=" + digest + "|json=0")
        lines.append(row)
        print(row)
    print("HEBC-TRANSLATION|result=PASS|sum_dim=1393|sum_sector_nnz=27045|"
          "action=Z2xZ2|weights=POSITIVE|invariance=EXACT_INTEGER|"
          "intertwining=EXACT_INTEGER|operator_sha=" + EXPECTED_OPERATOR_SHA
          + "|json=0")
    return sectors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: seat_translation_sectors.py OUTPUT_DIR")
    export(Path(sys.argv[1]))
