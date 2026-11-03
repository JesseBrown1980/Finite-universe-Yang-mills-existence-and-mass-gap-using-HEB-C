#!/usr/bin/env python3
"""Independent GPT-6 S3 matrix reconstruction -> Z2xZ2 sectors; integer-only.
Source Hamiltonian is independently rebuilt from group permutations by
gpt6_2x2_from_permutations.py, not the earlier seat's sector builder.
"""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from itertools import product
from collections import Counter
from hashlib import sha256
import runpy
import sys

HERE = Path(__file__).resolve().parent
ORIGINAL_ARGV = sys.argv
with redirect_stdout(StringIO()):
    sys.argv = [str(HERE / "gpt6_2x2_from_permutations.py")]
    try:
        model = runpy.run_path(str(HERE / "gpt6_2x2_from_permutations.py"))
    finally:
        sys.argv = ORIGINAL_ARGV
keys = model["keys"]
rows = model["rows"]
weights = model["W"]
mag = model["mag"]
index = model["pos"]
number = model["number"]
fixed = model["fixed"]
expand = model["expand"]
decode = model["decode"]
EXPECTED_SHA = {
    "pp": "fb6dbb3acbd411f61779f98881e6545d21ab7a39816c351d755fafe2c3f2c652",
    "pm": "9dc22f4bb6f410ebfcdc0bfb3854bf6d2827901ee379ed685772649d28315d48",
    "mp": "88eb8250eaf85815f155f09656f8a4dd19733148dd9e4505af978bed5974a75b",
    "mm": "d7dce164177f2b5498a367c9df78ff8d64c8d173a262daa65815b321ff21b653",
}

def move_links(links, dx, dy):
    result = [0] * 8
    for x, y in product(range(2), repeat=2):
        at = 2*x + y
        src = 2*((x+dx) % 2) + ((y+dy) % 2)
        result[at] = links[src]
        result[4+at] = links[4+src]
    return result

permutations = {}
for dx, dy in product(range(2), repeat=2):
    mapping = [
        index[number(fixed(move_links(expand(decode(k)), dx, dy)))]
        for k in keys
    ]
    assert set(mapping) == set(range(1393))
    assert all(weights[i] == weights[v] and mag[i] == mag[v]
               for i, v in enumerate(mapping))
    assert all(rows[mapping[i]].get(mapping[j], 0) == z
               for i, row in enumerate(rows) for j, z in row.items())
    permutations[dx, dy] = mapping

orbits = []
visited = set()
for i in range(1393):
    if i in visited:
        continue
    orbit = {mapping[i] for mapping in permutations.values()}
    visited.update(orbit)
    orbits.append(sorted(orbit))
assert len(visited) == 1393
assert Counter(map(len, orbits)) == {4: 319, 2: 51, 1: 15}

def project(sx, sy):
    basis = []
    for orbit in orbits:
        root = orbit[0]
        signs = {}
        for dx, dy in product(range(2), repeat=2):
            j = permutations[dx, dy][root]
            value = (sx if dx else 1)*(sy if dy else 1)
            if j in signs and signs[j] != value:
                break
            signs[j] = value
        else:
            basis.append((root, signs))
    identify = {i: k for k, (_, sign) in enumerate(basis) for i in sign}
    block_w = [len(sign) * weights[root] for root, sign in basis]
    block_m = [mag[root] for root, _ in basis]
    upper = []
    nnz = 0
    for k, (root, _) in enumerate(basis):
        row = Counter()
        for j, value in rows[root].items():
            if j in identify:
                at = identify[j]
                row[at] += value * basis[at][1][j]
        row = {j: value for j, value in row.items() if value}
        nnz += len(row)
        for j, value in sorted(row.items()):
            if j >= k:
                upper.append((k, j, value))
    return block_w, block_m, upper, nnz

def write(directory):
    directory.mkdir(parents=True, exist_ok=True)
    total = 0
    for sx, sy, name in ((1, 1, "pp"), (1, -1, "pm"),
                         (-1, 1, "mp"), (-1, -1, "mm")):
        w, m, upper, nnz = project(sx, sy)
        text = (str(len(w)) + "\n" + " ".join(map(str, w)) + "\n"
                + " ".join(map(str, m)) + "\n"
                + "".join("%d %d %d\n" % values for values in upper))
        raw = text.encode("ascii")
        digest = sha256(raw).hexdigest()
        assert digest == EXPECTED_SHA[name], (name, digest)
        (directory / (name + ".matrix")).write_bytes(raw)
        print("GPT6_PROJECT|sector=%s|dim=%d|nnz=%d|sha256=%s|result=PASS|json=0"
              % (name, len(w), nnz, digest))
        total += len(w)
    assert total == 1393
    print("GPT6_PROJECT|all_sectors=4|sum_dim=1393|direct_comparison_to_other_seat=0|json=0")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: gpt6_sturm_sectors.py OUTPUT_DIR")
    write(Path(sys.argv[1]))
