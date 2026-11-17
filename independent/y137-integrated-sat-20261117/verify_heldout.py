#!/usr/bin/env python3
"""Independent held-out source reconstruction, SAT and exact #SAT verifier.
Integer operations and SHA receipts only; never imports the solver.
"""
import hashlib
import sys
from pathlib import Path


def digest(parts):
    return hashlib.sha256(parts.encode("ascii")).digest()


def number(seed, *labels):
    value = "heldout-v1:" + seed + ":" + ":".join(str(k) for k in labels)
    return int.from_bytes(digest(value)[:8], "big")


def check(clause, bits):
    return any(((bits >> (abs(lit) - 1)) & 1) == int(lit > 0)
               for lit in clause)


def expected_fixture(kind, n, seed):
    planted = 0
    for index in range(n):
        planted |= (number(seed, "truth", index) & 1) << index
    fixed = []
    if kind in ("xor", "mixed"):
        assert n % 3 == 0
        upto = n if kind == "xor" else n // 2
        for index in range(upto):
            variables = (index + 1, (index + 1) % n + 1,
                         (index + n // 3) % n + 1)
            rhs = sum((planted >> (var - 1)) & 1 for var in variables) & 1
            for pattern in range(8):
                if (pattern.bit_count() & 1) != rhs:
                    fixed.append(tuple(-var if (pattern >> j) & 1 else var
                                       for j, var in enumerate(variables)))
        if kind == "xor":
            return tuple(fixed)
    avoid = {tuple(sorted(abs(x) for x in clause)) for clause in fixed}
    total = n if kind == "mixed" else (17 * n + 3) // 4
    for index in range(total):
        selected = []
        candidate = 0
        while len(selected) < 3:
            modulo = min(n, 4) if kind == "hub" and len(selected) == 0 else n
            v = number(seed, kind, "var", index, candidate) % modulo + 1
            candidate += 1
            if v not in selected:
                selected.append(v)
        if tuple(sorted(selected)) in avoid:
            legal = []
            for v in range(1, n + 1):
                if v not in selected[:2]:
                    if tuple(sorted(selected[:2] + [v])) not in avoid:
                        legal.append(v)
            selected[2] = legal[number(seed, "avoid", index) % len(legal)]
        literals = [v if number(seed, kind, "sign", index, j) & 1 else -v
                    for j, v in enumerate(selected)]
        if kind != "random" and not check(literals, planted):
            literals[0] = -literals[0]
        fixed.append(tuple(literals))
    if kind == "unsat":
        for rejected in range(8):
            fixed.append(tuple(-v if rejected & (1 << k) else v
                               for k, v in enumerate((1, 2, 3))))
    return tuple(fixed)


def independent_dimacs(raw):
    header = None
    clauses = []
    literals = []
    for line in raw.splitlines():
        fields = line.strip().split()
        if not fields or fields[0] == "c":
            continue
        if fields[0] == "p":
            assert header is None and len(fields) == 4 and fields[1] == "cnf"
            header = (int(fields[2]), int(fields[3]))
            assert header[0] > 0 and header[1] >= 0
            continue
        assert header
        for text in fields:
            v = int(text)
            if v:
                assert abs(v) <= header[0]
                literals.append(v)
                assert len(literals) <= 3
            else:
                assert len(literals) == 3 and len(set(map(abs, literals))) == 3
                clauses.append(tuple(literals))
                literals = []
    assert header and not literals and len(clauses) == header[1]
    return header[0], tuple(clauses)


def independent_xor_count(n, clauses):
    groups = {}
    for clause in clauses:
        key = tuple(sorted(abs(v) for v in clause))
        groups.setdefault(key, []).append(clause)
    equations = []
    for scope, block in sorted(groups.items()):
        if len(block) != 4:
            return None
        canonical = {tuple(sorted(c, key=abs)) for c in block}
        accepted = []
        for bits in range(8):
            assigned = sum(((bits >> i) & 1) << (v - 1)
                           for i, v in enumerate(scope))
            if all(check(c, assigned) for c in block):
                accepted.append(bits)
        if len(accepted) != 4:
            return None
        sides = {a.bit_count() & 1 for a in accepted}
        if len(sides) != 1:
            return None
        rhs = next(iter(sides))
        expected = set()
        for bits in range(8):
            if (bits.bit_count() & 1) != rhs:
                expected.add(tuple(-v if (bits >> j) & 1 else v
                                   for j, v in enumerate(scope)))
        if canonical != expected:
            return None
        equations.append((sum(1 << (v - 1) for v in scope), rhs))
    basis = {}
    for mask, rhs in equations:
        while mask:
            pivot = (mask & -mask).bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (mask, rhs)
                break
            left, bit = basis[pivot]
            mask ^= left
            rhs ^= bit
        else:
            if rhs:
                return 0
    return 1 << (n - len(basis))


def counted_dpll(n, clauses, node_limit):
    occurrence = [0] * n
    for clause in clauses:
        for lit in clause:
            occurrence[abs(lit) - 1] += 1
    order = sorted(range(n), key=lambda v: (-occurrence[v], v))
    nodes = [0]

    def visit(mask, assignment, depth):
        nodes[0] += 1
        if nodes[0] > node_limit:
            return None
        ready = True
        for clause in clauses:
            has_unknown = False
            has_true = False
            for lit in clause:
                bit = 1 << (abs(lit) - 1)
                if not (mask & bit):
                    has_unknown = True
                elif bool(assignment & bit) == (lit > 0):
                    has_true = True
                    break
            if not has_true and not has_unknown:
                return 0
            if not has_true:
                ready = False
        if ready:
            return 1 << (n - depth)
        if depth == n:
            return 0
        bit = 1 << order[depth]
        left = visit(mask | bit, assignment, depth + 1)
        if left is None:
            return None
        right = visit(mask | bit, assignment | bit, depth + 1)
        return None if right is None else left + right

    return visit(0, 0, 0)


def parse_receipt(line):
    return dict(item.split("=", 1) for item in line.strip().split("|")[1:]
                if "=" in item)


def verify(receipt, directory):
    kind = receipt["kind"]
    n = int(receipt["variables"])
    seed = receipt["fixture_seed"]
    name = kind + "-" + str(n)
    raw_bytes = directory.joinpath(name + ".cnf").read_bytes()
    raw = raw_bytes.decode("ascii")
    assert hashlib.sha256(raw_bytes).hexdigest() == receipt["dimacs_sha256"]
    got_n, clauses = independent_dimacs(raw)
    assert got_n == n
    assert clauses == expected_fixture(kind, n, seed)
    assert len(clauses) == int(receipt["clauses"])
    assert hashlib.sha256(repr(clauses).encode("ascii")).hexdigest() == receipt["source_sha256"]
    status, models = receipt["status"], receipt["model_count"]
    if kind == "xor":
        actual = independent_xor_count(n, clauses)
        assert actual is not None
    elif kind == "unsat":
        # The eight last 3-clauses forbid all 2^3 assignments.
        assert len({tuple(c) for c in clauses[-8:]}) == 8
        actual = 0
    else:
        actual = counted_dpll(n, clauses, 3000000)
    if status == "EXACT":
        assert actual is not None and actual == int(models)
        if actual:
            witness = int(receipt["witness_integer"])
            assert all(check(c, witness) for c in clauses)
        else:
            assert receipt["witness_integer"] == "NONE"
    elif status == "EXACT_UNSAT":
        assert actual == 0 and models == "0"
    else:
        assert status == "HOLD_BUDGET" and models == "HOLD"
    assert int(receipt["total_metered_units"]) > 0
    assert int(receipt["source_generation_ns"]) >= 0
    return ("UNSAT" if actual == 0 else "SAT" if actual is not None else "UNKNOWN"), actual


def main(receipts, folder, baseline):
    root = Path(folder)
    rows = [parse_receipt(line) for line in Path(receipts).read_text(encoding="ascii").splitlines()
            if line.startswith("SAT_HELDOUT|")]
    assert len(rows) == 21
    found = {}
    for row in rows:
        key = row["kind"] + "-" + row["variables"]
        assert key not in found
        found[key] = verify(row, root)
    baseline_rows = [line.split("\t") for line in Path(baseline).read_text(encoding="ascii").splitlines()
                     if line and not line.startswith("#")]
    assert len(baseline_rows) == 21
    for cols in baseline_rows:
        assert len(cols) == 7
        key, minisat_exit, picosat_exit, mini_ns, pico_ns, mini_rss, pico_rss = cols
        assert key in found
        assert minisat_exit in ("10", "20") and picosat_exit in ("10", "20")
        assert minisat_exit == picosat_exit
        assert all(int(x) >= 0 for x in (mini_ns, pico_ns, mini_rss, pico_rss))
        expected_decision = found[key][0]
        if expected_decision != "UNKNOWN":
            assert ("SAT" if minisat_exit == "10" else "UNSAT") == expected_decision
    print("SAT_HELDOUT_INDEPENDENT|cases=21|source_frozen=PASS|"
          "two_independent_SAT_decision_baselines=AGREE|exact_counts_checked=PASS|"
          "source_sha_and_raw_DIMACS_sha=PASS|bounded_hold_preserved=PASS|status=PASS")


if __name__ == "__main__":
    assert len(sys.argv) == 4
    main(sys.argv[1], sys.argv[2], sys.argv[3])
