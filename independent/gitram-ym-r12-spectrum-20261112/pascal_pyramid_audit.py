#!/usr/bin/env python3
"""Exact integer Pascal-pyramid composition audit for frozen 3^k trit columns.

Usage: python3 pascal_pyramid_audit.py FROZEN-LEAVES.hbp OUTPUT.hbp [EXPECTED_SHA256]

This is a distribution audit, NOT a pairwise-conditioned null or a physical
continuum proof. No floats, no JSON. Checks a single complete frozen source.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from math import comb, gcd
from pathlib import Path
import sys


def parse(path):
    payload = Path(path).read_bytes()
    digest = sha256(payload).hexdigest()
    lines = payload.decode("ascii").splitlines()
    assert lines and lines[0].startswith(("NINE_LEAF_FREEZE|", "LEAF_FREEZE|")), (
        "expected a frozen leaf header"
    )
    header = dict(s.split("=", 1) for s in lines[0].split("|") if "=" in s)
    expected_rows = int(header["rows"])
    assert expected_rows > 0
    found = set()
    rows, keys = [], []
    for line in lines[1:]:
        assert line.startswith("LEAF|"), ("non-leaf source line", line[:50])
        fields = dict(s.split("=", 1) for s in line.split("|") if "=" in s)
        key = int(fields["key"])
        assert key not in found, ("duplicate key", key)
        found.add(key)
        trits = tuple(int(x) for x in fields["trits"].split(","))
        assert all(x in (0, 1, 2) for x in trits)
        keys.append(key)
        rows.append(trits)
    assert len(rows) == expected_rows
    assert keys == sorted(keys), "key order must be canonical"
    n = len(rows[0])
    assert n > 0 and all(len(r) == n for r in rows)
    # Only powers of three (9,27,81,243,...) for the scale campaign.
    v = n
    while v > 1 and v % 3 == 0:
        v //= 3
    assert v == 1 and n >= 9, ("columns must be powers of three >= 9", n)
    if "columns" in header:
        assert int(header["columns"]) == n
    return rows, digest, n


def integer_power(value, exponent):
    assert isinstance(exponent, int) and exponent >= 0
    acc = 1
    for _ in range(exponent):
        acc *= value
    return acc


def reduced(numer, denom):
    assert denom > 0 and numer >= 0
    factor = gcd(numer, denom)
    return numer // factor, denom // factor


def scaled_ratio(numer, denom, scale):
    assert denom > 0 and numer >= 0
    return numer * scale // denom


def analyze(path, destination, expected=None):
    rows, digest, n = parse(path)
    if expected is not None:
        assert digest == expected, ("source pin mismatch", digest, expected)
    count = len(rows)
    compositions = Counter(tuple(r.count(v) for v in (0, 1, 2)) for r in rows)
    patterns = len(set(rows))
    assert sum(compositions.values()) == count
    corners = sum(v for c, v in compositions.items() if max(c) == n)
    edges = sum(v for c, v in compositions.items() if min(c) == 0 and max(c) != n)
    interior = count - edges - corners
    dis = Counter()
    for row in rows:
        c = [row.count(v) for v in range(3)]
        if max(c) == n-1:
            dis[next(i for i, trit in enumerate(row) if c[trit] == 1)] += 1
    assert sum(dis.values()) <= count
    marg = [[sum(r[i] == v for r in rows) for v in range(3)] for i in range(n)]
    assert all(sum(x) == count for x in marg)
    # Exact independent-column comparison using each observed single-column
    # marginal, not a uniform-thirds assumption. Cross-column correlations
    # are absent ONLY in this diagnostic reference.
    denominator = integer_power(count, n)
    all_one_num = sum(
        _product(marg[i][symbol] for i in range(n))
        for symbol in range(3)
    )
    missing_num = sum(
        _product(count - marg[i][symbol] for i in range(n))
        for symbol in range(3)
    )
    corner_num = count * all_one_num
    edge_num = count * (missing_num - 2*all_one_num)
    interior_num = count * (denominator - missing_num + all_one_num)
    assert corner_num >= 0 and edge_num >= 0 and interior_num >= 0
    assert corner_num + edge_num + interior_num == count * denominator
    expected_corners = reduced(corner_num, denominator)
    expected_edges = reduced(edge_num, denominator)
    expected_interior = reduced(interior_num, denominator)
    uniform_denominator = integer_power(3, n)
    independent_uniform_corners = reduced(3*count, uniform_denominator)
    independent_uniform_edges = reduced(
        3*(integer_power(2, n)-2)*count, uniform_denominator
    )

    out = [
        "CONTRACT|schema=GITRAM-PASCAL-PYRAMID-AUDIT-V1|source_sha256=%s|rows=%d|columns=%d|arithmetic=exact|reference=independent_column_marginals|pair_conditioned=NO|json=0"
        % (digest, count, n),
        "GEOMETRY|corners=%d|edges=%d|interior=%d|compositions=%d|possible_compositions=%d|unique_labeled_patterns=%d|json=0"
        % (corners, edges, interior, len(compositions), comb(n+2, 2), patterns),
        "INDEPENDENT_COLUMN_REFERENCE|corner_expected_n=%d|corner_expected_d=%d|edge_expected_n=%d|edge_expected_d=%d|interior_expected_n=%d|interior_expected_d=%d|json=0"
        % (*expected_corners, *expected_edges, *expected_interior),
        "UNIFORM_REFERENCE|corner_expected_n=%d|corner_expected_d=%d|edge_expected_n=%d|edge_expected_d=%d|json=0"
        % (*independent_uniform_corners, *independent_uniform_edges),
        "READOUT|independent_corner_ppb=%d|independent_edge_ppb=%d|independent_interior_ppb=%d|json=0"
        % (scaled_ratio(corner_num, count*denominator, 1000000000),
           scaled_ratio(edge_num, count*denominator, 1000000000),
           scaled_ratio(interior_num, count*denominator, 1000000000))
    ]
    for (a, b, c), multiplicity in sorted(compositions.items()):
        out.append("COMPOSITION|low=%d|middle=%d|high=%d|rows=%d|json=0"
                   % (a, b, c, multiplicity))
    for column, amount in sorted(dis.items()):
        out.append("DISSENTER|column=%d|rows=%d|json=0" % (column, amount))
    # Exact cross-column pair checksum for future pair-fixed controls.
    pair_lines = []
    for i, j in combinations(range(n), 2):
        table = [0]*9
        for row in rows:
            table[3*row[i] + row[j]] += 1
        assert sum(table) == count
        pair_lines.append("%d:%d:%s" % (i, j, ",".join(map(str, table))))
    pair_hash = sha256(("\n".join(pair_lines)+"\n").encode("ascii")).hexdigest()
    out += [
        "PAIR_MARGINS|tables=%d|ordered_sha256=%s|status=MEASURED_NOT_CONDITIONED|json=0"
        % (comb(n, 2), pair_hash),
        "LIMIT|independent_reference_not_exact_pair_null=1|sampling_mixing=NOT_TESTED|physical_continuum=NOT_ESTABLISHED|json=0",
        "GITRAM_PASCAL_PYRAMID_AUDIT_PASS|columns=%d|rows=%d|source_sha256=%s|json=0"
        % (n, count, digest)
    ]
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(out)+"\n", encoding="ascii")
    (target.parent/(target.name+".sha256")).write_text(
        "%s  %s\n" % (sha256(target.read_bytes()).hexdigest(), target.name),
        encoding="ascii"
    )
    print("\n".join(x for x in out if x.startswith(("CONTRACT|", "GEOMETRY|", "DISSENTER|", "PAIR_MARGINS|", "GITRAM_PASCAL_PYRAMID_AUDIT_PASS|"))))


def _product(values):
    result = 1
    for x in values:
        result *= x
    return result


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        raise SystemExit("usage: pascal_pyramid_audit.py FROZEN.hbp OUTPUT.hbp [SHA256]")
    analyze(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv)==4 else None)
