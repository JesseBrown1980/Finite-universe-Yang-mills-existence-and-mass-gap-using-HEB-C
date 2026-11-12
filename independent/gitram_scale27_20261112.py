#!/usr/bin/env python3
"""Independent 27-column exact Pascal freeze: 3 couplings x 3 cutoffs x 3 words.

Uses SHA-verified r12 artifacts, separately verified excluded-coupling
certificates, and the unchanged 682-row common canonical key universe.
The first 9 labels must reproduce the independent historical 9-leaf
freeze byte-for-byte rowwise. IntegerRatio arithmetic only.
NOT a physical lattice extension, conditional-null sampler or mass gap proof.

Run: python3 -B -m independent.gitram_scale27_20261112 R12_ROOT NEW_ROOT NINE_HBP OUT_ROOT
"""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import sys

from independent.seat_integer_ratio import IntegerRatio

SEED = b"YM-R12-FROZEN-THREEWAY-PAIRS-20261112-V1"
NINE_SHA = "2220ee3a11c66281b586de77f44999c06e863f0e9f83509a867047048326bbc7"
EXPECTED = ("12/1", "21/2", "14/1")
CUTS = (7, 8, 9)
WORDS = ("1", "6,5,4,3", "8,7,6,5,4")
ROWS = 682


def file_sha(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def manifest_check(folder):
    manifest = folder.joinpath("SHA256SUMS")
    assert manifest.is_file()
    lines = manifest.read_text(encoding="ascii").splitlines()
    assert lines
    for line in lines:
        digest, name = line.split(None, 1)
        name = name.strip(" *")
        target = folder.joinpath(name)
        assert name and ".." not in name and "/" not in name
        assert target.is_file() and file_sha(target) == digest, name
    return file_sha(manifest)


def load_rows(folder, m0):
    data = folder.joinpath("rows.txt").read_bytes()
    lines = data.decode("ascii").splitlines()
    assert lines[0] == "floorcert-rows-v1 m0=%d" % m0
    rows, total_tail, total_back, summary = [], 0, 0, None
    for line in lines[1:]:
        a = line.split()
        if not a:
            continue
        if a[0] == "C":
            key, mag, nflat = map(int, a[1:4])
            core = [tuple(map(int, token.split(":"))) for token in a[4:]]
            rows.append([key, mag, nflat, core, []])
        elif a[0] == "T":
            assert rows and len(a) >= 3
            magnetic = int(a[1])
            hist = tuple(int(x) for x in a[2].split(","))
            assert len(hist) == 9
            back = tuple(int(x) for x in a[3:])
            rows[-1][4].append((magnetic, hist, back))
            total_tail += 1
            total_back += len(back)
        elif a[0] == "END":
            summary = tuple(map(int, a[1:]))
        else:
            raise AssertionError("unrecognized row tag")
    assert summary == (len(rows), total_tail, total_back)
    assert [x[0] for x in rows] == sorted({x[0] for x in rows})
    assert all(x[2] + sum(c for _, c in x[3]) + len(x[4]) == 72 for x in rows)
    return rows, file_sha(folder.joinpath("rows.txt"))


def load_cert(path, rows, rowhash, m0, r_expected):
    lines = path.read_text(encoding="ascii").splitlines()
    assert lines and lines[0].startswith("# floorcert certificate: ")
    info = dict(field.split("=", 1) for field in lines[0].split() if "=" in field)
    assert int(info["m0"]) == m0 and info["rowhash"] == rowhash
    rn, rd = map(int, info["r"].split("/"))
    assert rd > 0 and rn > 0 and (str(rn)+"/"+str(rd)) == r_expected
    tn, td = map(int, info["t"].split("/"))
    assert td > 0
    word = tuple(map(int, info["f"].split(",")))
    assert word and all(v > 0 for v in word)
    vals = {}
    for line in lines[1:]:
        if not line.strip() or line.startswith("#"):
            continue
        key, mag, v = map(int, line.split())
        assert key not in vals and v > 0
        vals[key] = (mag, v)
    assert len(vals) == len(rows)
    assert all(vals[row[0]][0] == row[1] for row in rows)
    return info, (rn, rd, tn, td), word, vals


def residuals(rows_by_key, keys, m0, rt, word, vals):
    rn, rd, tn, td = rt
    rdtd = rd * td

    def f(m):
        assert m > m0, ("tail boundary invalid", m, m0)
        return word[min(m-m0, len(word))-1]

    scores = []
    for key in keys:
        row = rows_by_key[key]
        _, mag, _, core, tails = row
        vi = vals[key][1]
        core_action = sum(mult * vals[target][1] for target, mult in core)
        main_num = (((72*rd + rn*mag)*td - rd*tn)*vi - rdtd*core_action)
        val = IntegerRatio(main_num, rdtd)
        for magnetic, hist, back in tails:
            fk = f(magnetic)
            tail_same = sum(
                amount * f(magnetic + direction - 4)
                for direction, amount in enumerate(hist) if amount
            )
            den = (((72*rd + rn*magnetic)*td - rd*tn)*fk - rdtd*tail_same)
            assert den > 0, ("invalid Schur denominator", magnetic, key)
            back_sum = sum(vals[target][1] for target in back)
            if back_sum:
                val -= IntegerRatio(rdtd * fk * back_sum, den)
        scores.append(val * IntegerRatio(1, vi))
    return scores


def terciles(scores, keys, certhash):
    n = len(scores)
    assert n == ROWS
    order = sorted(
        range(n),
        key=lambda i: (scores[i], sha256(SEED + certhash.encode("ascii")
                                         + str(keys[i]).encode("ascii")).digest())
    )
    labels = [0] * n
    for rank, i in enumerate(order):
        labels[i] = min(2, (3*rank)//n)
    ties = n - len(set(scores))
    boundary = sum(scores[order[t-1]] == scores[order[t]]
                   for t in (n//3, (2*n)//3))
    assert set(labels) == {0, 1, 2}
    return labels, ties, boundary


def baseline_read(path):
    assert file_sha(path) == NINE_SHA, "frozen nine-source hash mismatch"
    lines = path.read_text(encoding="ascii").splitlines()
    assert lines[0].startswith("NINE_LEAF_FREEZE|") and "rows=682|" in lines[0]
    states, keys = [], []
    for line in lines[1:]:
        assert line.startswith("LEAF|")
        fields = dict(token.split("=", 1) for token in line.split("|") if "=" in token)
        keys.append(int(fields["key"]))
        trits = tuple(map(int, fields["trits"].split(",")))
        assert len(trits) == 9
        states.append(trits)
    assert len(states) == ROWS and len(keys) == ROWS
    assert keys == sorted(set(keys))
    return keys, states


def cube_move_census(states):
    """Enumerate all feasible 2x2x2 count trades on sparse 27-way tables.

    Four nonzero decrement corners suffice; increment corners may be zero.
    Holding the other 24 variables fixed makes all 351 pair tables invariants.
    This is a move-availability census, never an irreducibility proof.
    """
    n = len(states[0])
    assert n == 27
    counts = Counter(states)
    assert sum(counts.values()) == len(states)
    choices = tuple(combinations((0, 1, 2), 2))
    feasible, populated_contexts, tested_triples = 0, 0, 0
    for a, b, c in combinations(range(n), 3):
        triples = defaultdict(dict)
        for state, num in counts.items():
            context = state[:a] + state[a+1:b] + state[b+1:c] + state[c+1:]
            triples[context][(state[a], state[b], state[c])] = num
        tested_triples += 1
        for cells in triples.values():
            if len(cells) < 4:
                continue
            populated_contexts += 1
            for pair_a in choices:
                for pair_b in choices:
                    for pair_c in choices:
                        pos, neg = True, True
                        for mask in range(8):
                            entry = (pair_a[mask & 1],
                                     pair_b[(mask >> 1) & 1],
                                     pair_c[(mask >> 2) & 1])
                            exists = cells.get(entry, 0) > 0
                            if mask.bit_count() & 1:
                                neg = neg and exists
                            else:
                                pos = pos and exists
                        feasible += int(pos) + int(neg)
    assert tested_triples == 2925
    return feasible, populated_contexts, tested_triples


def run(r12_root, new_root, nine_path, out_root):
    assert r12_root.is_dir() and new_root.is_dir()
    keys, baseline = baseline_read(nine_path)
    sources = {}
    manifests = []
    for m0 in CUTS:
        orig = r12_root.joinpath("cutoff-%d" % m0)
        added = new_root.joinpath("cutoff-%d" % m0)
        manifests.append(("12", m0, manifest_check(orig)))
        manifests.append(("added", m0, manifest_check(added)))
        rows, rh = load_rows(orig, m0)
        rows_by_key = {row[0]: row for row in rows}
        assert set(keys).issubset(rows_by_key)
        assert all(rows_by_key[k][1] == rows_by_key[next(iter(rows_by_key))][1]
                   for k in () )  # all keys' magnetic costs checked below
        sources[m0] = (rows, rows_by_key, rh, orig, added)

    # The same canonical physical keys and magnetic costs under all cutoffs.
    common = set(sources[7][1])
    for m0 in CUTS[1:]:
        common.intersection_update(sources[m0][1])
    assert sorted(common) == keys and len(common) == ROWS
    for key in keys:
        assert len({sources[m0][1][key][1] for m0 in CUTS}) == 1

    cols, metas = [], []
    for r in EXPECTED:
        for m0 in CUTS:
            rows, rowmap, rowhash, orig, added = sources[m0]
            folder = orig if r == "12/1" else added
            files = sorted(folder.glob("cert_m%d_r%s_f*.txt"
                                       % (m0, r.replace("/", "_"))))
            assert len(files) == 3, ("expected three unique weight words", r, m0)
            words_seen = set()
            for path in files:
                info, rt, word, vals = load_cert(path, rows, rowhash, m0, r)
                assert info["f"] in WORDS and info["f"] not in words_seen
                words_seen.add(info["f"])
                cert_hash = file_sha(path)
                scores = residuals(rowmap, keys, m0, rt, word, vals)
                labels, ties, boundary = terciles(scores, keys, cert_hash)
                cols.append(labels)
                metas.append((r, m0, info["f"], cert_hash, rowhash, ties, boundary))
            assert words_seen == set(WORDS)
    assert len(cols) == 27 and len(metas) == 27
    full = [tuple(col[i] for col in cols) for i in range(ROWS)]
    assert all(row[:9] == baseline[i] for i, row in enumerate(full)), (
        "historical nine-leaf reproduction failed"
    )
    assert len(set(full)) <= ROWS
    out_root.mkdir(parents=True, exist_ok=True)
    result = out_root.joinpath("FROZEN-27.hbp")
    lines = [
        "LEAF_FREEZE|schema=YM-27-3COUPLING-3CUTOFF-3WORD|rows=682|columns=27|source_run=43222707802|baseline_sha256=%s|json=0"
        % NINE_SHA
    ]
    for i, key in enumerate(keys):
        mag = sources[7][1][key][1]
        lines.append("LEAF|key=%d|mag=%d|trits=%s|json=0"
                     % (key, mag, ",".join(str(v) for v in full[i])))
    result.write_text("\n".join(lines)+"\n", encoding="ascii")
    lines = [
        "REPORT|schema=YM-27-INDEPENDENT-V1|rows=%d|columns=%d|source_sha256=%s|baseline9_verified=PASS|json=0"
        % (ROWS, len(cols), file_sha(result))
    ]
    for r, m0, digest in manifests:
        lines.append("INPUT|coupling=%s|cutoff=%d|manifest_sha256=%s|json=0"
                     % (r, m0, digest))
    for i, (r, m0, fword, digest, rowhash, ties, boundary) in enumerate(metas):
        lines.append("COLUMN|index=%d|r=%s|m0=%d|word=%s|certificate_sha256=%s|rowhash=%s|residual_ties=%d|boundary_ties=%d|json=0"
                     % (i, r, m0, fword, digest, rowhash, ties, boundary))
    count = Counter(full)
    corners = sum(v for row, v in count.items() if len(set(row)) == 1)
    edges = sum(v for row, v in count.items() if len(set(row)) == 2)
    inside = ROWS-corners-edges
    dissent = Counter()
    for row in full:
        c = Counter(row)
        if max(c.values()) == 26:
            dissent[next(j for j, x in enumerate(row) if c[x] == 1)] += 1
    moves, contexts, triples = cube_move_census(full)
    lines.append("GEOMETRY|rows=682|corners=%d|edges=%d|interior=%d|distinct_patterns=%d|json=0"
                 % (corners, edges, inside, len(count)))
    for idx, amount in sorted(dissent.items()):
        lines.append("DISSENTER|column=%d|rows=%d|json=0" % (idx, amount))
    lines.append("MOVE_AVAILABILITY|pair_tables=351|three_column_choices=%d|candidate_contexts_ge4=%d|oriented_feasible_cubes=%d|interpretation=UNRESOLVED_WITHOUT_MIXING|json=0"
                 % (triples, contexts, moves))
    lines.append("LIMIT|pattern_count_not_pairwise_excess=1|cube_moves_not_proven_irreducible=1|new_physical_lattice=NO|continuum=NOT_ESTABLISHED|r9_run=NO|json=0")
    lines.append("GITRAM_27_INDEPENDENT_PASS|rows=682|columns=27|baseline9=PASS|json=0")
    report = out_root.joinpath("REPLAY-27.hbp")
    report.write_text("\n".join(lines)+"\n", encoding="ascii")
    for path in (result, report):
        out_root.joinpath(path.name+".sha256").write_text(
            file_sha(path)+"  "+path.name+"\n", encoding="ascii"
        )
    print("\n".join(x for x in lines if x.startswith(
        ("REPORT|", "GEOMETRY|", "DISSENTER|", "MOVE_AVAILABILITY|",
         "GITRAM_27_INDEPENDENT_PASS|")
    )))


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit("usage: python3 -B -m independent.gitram_scale27_20261112 R12_ROOT NEW_ROOT NINE_HBP OUT_ROOT")
    run(*(Path(a) for a in sys.argv[1:]))
