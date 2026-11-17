#!/usr/bin/env python3
"""Clean-room SAT receipt verifier. No engine import; exact integer only."""
import hashlib
import sys
from pathlib import Path


def sha(x):
    return hashlib.sha256(repr(x).encode("ascii")).hexdigest()


def check_clause(clause, bits):
    return any(bool((bits >> (abs(v) - 1)) & 1) == (v > 0) for v in clause)


def hidden(n):
    value = 0
    for i in range(n):
        value |= (hashlib.sha256(("hidden:" + str(n) + ":" + str(i))
                  .encode("ascii")).digest()[0] & 1) << i
    return value


def fixture(n):
    original = hidden(n)
    triples = []
    for i in range(n):
        triples.append((i + 1, (i + 1) % n + 1, (i + n // 3) % n + 1))
    for i in range(0, n, 3):
        triples.append((i + 1, (i + n // 3 + 1) % n + 1,
                        (i + 2 * n // 3 + 2) % n + 1))
    clauses = []
    equations = []
    for triple in triples:
        mask = sum(1 << (v - 1) for v in triple)
        rhs = (mask & original).bit_count() & 1
        equations.append((mask, rhs))
        for assignment in range(8):
            if (assignment.bit_count() & 1) != rhs:
                clauses.append(tuple(-v if (assignment >> k) & 1 else v
                                     for k, v in enumerate(triple)))
    return tuple(clauses), tuple(equations)


def generic_source(n):
    original = hidden(n)
    clauses = []
    for i in range(n):
        triples = ((i + 1, ((i + n // 3) % n) + 1, ((i + 2 * n // 3) % n) + 1),
                   (i + 1, ((i + 1) % n) + 1, ((i + n // 2) % n) + 1))
        for j, triple in enumerate(triples):
            clause = []
            for k, v in enumerate(triple):
                h = hashlib.sha256(("generic:" + str(i) + ":" + str(j) + ":" +
                                    str(k)).encode("ascii")).digest()[0]
                clause.append(v if h & 1 else -v)
            if not check_clause(clause, original):
                clause[0] = -clause[0]
            clauses.append(tuple(clause))
    return tuple(clauses)


def hybrid_source(n):
    clauses, equations = fixture(n)
    first = clauses[:4 * (n // 2)]
    scopes = {tuple(sorted(abs(lit) for lit in c)) for c in first}
    extra = []
    for c in generic_source(n):
        if tuple(sorted(abs(lit) for lit in c)) not in scopes:
            extra.append(c)
        if len(extra) == n // 2:
            break
    assert len(extra) == n // 2
    return first + tuple(extra), equations[:n // 2], tuple(extra)


def gaussian_left(n, equations):
    rows = [[m, rhs] for m, rhs in equations]
    rank = 0
    pivots = []
    for bit in range(n):
        candidate = next((i for i in range(rank, len(rows))
                          if (rows[i][0] >> bit) & 1), None)
        if candidate is None:
            continue
        rows[rank], rows[candidate] = rows[candidate], rows[rank]
        for i in range(rank + 1, len(rows)):
            if (rows[i][0] >> bit) & 1:
                rows[i][0] ^= rows[rank][0]
                rows[i][1] ^= rows[rank][1]
        pivots.append(bit)
        rank += 1
    assert all(mask or not rhs for mask, rhs in rows[rank:])
    witness = 0
    for j in range(rank - 1, -1, -1):
        mask, rhs = rows[j]
        witness |= (rhs ^ ((mask & witness).bit_count() & 1)) << pivots[j]
    assert all(((mask & witness).bit_count() & 1) == rhs
               for mask, rhs in equations)
    return rank, witness


def brute_parallel(n, clauses):
    assert n <= 24
    count = 1 << n
    allbits = (1 << count) - 1
    masks = {}
    for v in range(1, n + 1):
        width = 1 << (v - 1)
        mask = ((1 << width) - 1) << width
        covered = 2 * width
        while covered < count:
            mask |= mask << covered
            covered *= 2
        masks[v] = mask
    accepted = allbits
    for clause in clauses:
        satisfying = 0
        for lit in clause:
            bitmask = masks[abs(lit)]
            satisfying |= bitmask if lit > 0 else allbits ^ bitmask
        accepted &= satisfying
    return accepted.bit_count()


def residual_count(n, equations, residual, cap):
    rows = [[mask, rhs] for mask, rhs in equations]
    rank = 0
    pivots = []
    for bit in range(n):
        selected = next((i for i in range(rank, len(rows))
                         if rows[i][0] & (1 << bit)), None)
        if selected is None:
            continue
        rows[rank], rows[selected] = rows[selected], rows[rank]
        for i in range(rank + 1, len(rows)):
            if rows[i][0] & (1 << bit):
                rows[i][0] ^= rows[rank][0]
                rows[i][1] ^= rows[rank][1]
        pivots.append(bit)
        rank += 1
    free = [i for i in range(n) if i not in pivots]
    if (1 << len(free)) > cap:
        return None
    total = 0
    for bits in range(1 << len(free)):
        value = sum(((bits >> i) & 1) << var for i, var in enumerate(free))
        for i in range(rank - 1, -1, -1):
            mask, rhs = rows[i]
            value |= (rhs ^ ((mask & value).bit_count() & 1)) << pivots[i]
        if all(check_clause(clause, value) for clause in residual):
            total += 1
    return total


def parse(line):
    return dict(field.split("=", 1) for field in line.strip().split("|")[1:]
                if "=" in field)


def replay_proof(source_sha, equations, n):
    proof = hashlib.sha256(source_sha.encode("ascii")).hexdigest()
    scoped = []
    for mask, rhs in equations:
        scope = tuple(i + 1 for i in range(n) if (mask >> i) & 1)
        scoped.append((scope, mask, rhs))
    for scope, mask, rhs in sorted(scoped):
        proof = sha((proof, scope, mask, rhs))
    return proof


def verify_row(row):
    kind, n = row["kind"], int(row["variables"])
    if kind == "parity":
        clauses, equations = fixture(n)
        residual = ()
    elif kind == "mixed":
        clauses, equations, residual = hybrid_source(n)
    else:
        assert kind == "generic"
        clauses, equations = generic_source(n), ()
        residual = clauses
    assert sha(clauses) == row["source_sha256"]
    assert int(row["clauses"]) == len(clauses)
    assert int(row["recognized"]) == len(equations)
    assert int(row["residual"]) == len(residual)
    assert row["proof_sha256"] == replay_proof(row["source_sha256"], equations, n)
    rank, known_solution = gaussian_left(n, equations)
    assert rank == int(row["rank"])
    assert all(((mask & known_solution).bit_count() & 1) == rhs
               for mask, rhs in equations)
    status = row["status"]
    if status == "EXACT":
        count = int(row["model_count"])
        if kind == "parity":
            independent_count = 1 << (n - rank)
        elif kind == "mixed":
            independent_count = residual_count(n, equations, residual, 262144)
            assert independent_count is not None
        else:
            independent_count = brute_parallel(n, clauses)
        assert count == independent_count
        witness = int(row["witness_integer"])
        assert all(check_clause(c, witness) for c in clauses)
        assert sha(witness) == row["witness_sha256"]
    else:
        assert status == "HOLD_BUDGET" and row["model_count"] == "HOLD"
        assert row["witness_integer"] == "NONE"
        count = None
    assert row["result_sha256"] == sha((kind, n, row["source_sha256"], count,
                                        rank, row["proof_sha256"], status))
    assert int(row["total_metered_units"]) > 0
    assert int(row["elapsed_ns"]) > 0
    return status


def main(path):
    lines = Path(path).read_text(encoding="ascii").splitlines()
    assert any(line.startswith("SAT_CONTROL|") for line in lines)
    assert any(line.startswith("SAT_INTEGRATED_FINAL|cases=11|") for line in lines)
    rows = [parse(line) for line in lines if line.startswith("SAT_INTEGRATED|")]
    assert len(rows) == 11
    expected = ([("parity", n) for n in (48, 72, 384)] +
                [("mixed", n) for n in (12, 24, 36, 48, 72)] +
                [("generic", n) for n in (12, 18, 24)])
    assert [(r["kind"], int(r["variables"])) for r in rows] == expected
    states = [verify_row(row) for row in rows]
    assert all(r["corrected_proposals"] == "1" for r in rows[:8])
    assert all(r["corrected_proposals"] == "0" for r in rows[8:])
    print("SAT_INTEGRATED_INDEPENDENT|cases=11|exact=" +
          str(states.count("EXACT")) + "|hold=" + str(states.count("HOLD_BUDGET")) +
          "|source_sha=PASS|proof_chain=PASS|independent_left_rank=PASS|"
          "complete_model_counts=PASS|original_CNF_witnesses=PASS|status=PASS")


if __name__ == "__main__":
    assert len(sys.argv) == 2
    main(sys.argv[1])
