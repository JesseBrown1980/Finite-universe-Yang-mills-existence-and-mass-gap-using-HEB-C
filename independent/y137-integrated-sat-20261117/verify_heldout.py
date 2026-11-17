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


def sha(value):
    return hashlib.sha256(repr(value).encode("ascii")).hexdigest()


def parse_receipt(line):
    fields = line.strip().split("|")[1:]
    result = {}
    for item in fields:
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        assert key not in result
        result[key] = value
    assert result.get("json") == "0"
    return result


def independent_reductions(n, clauses, source_sha):
    """Independent truth-table motif construction and opposite-pivot rank."""
    groups = {}
    for clause in clauses:
        key = tuple(sorted(abs(lit) for lit in clause))
        groups.setdefault(key, []).append(clause)
    rows = []
    accepted = set()
    proof = hashlib.sha256(source_sha.encode("ascii")).hexdigest()
    for scope, group in sorted(groups.items()):
        if len(group) != 4:
            continue
        canonical = {tuple(sorted(clause, key=abs)) for clause in group}
        if len(canonical) != 4:
            continue
        allowed = []
        for pattern in range(8):
            truth = {scope[j]: (pattern >> j) & 1 for j in range(3)}
            if all(any(truth[abs(lit)] == int(lit > 0)
                       for lit in clause) for clause in group):
                allowed.append(pattern)
        if len(allowed) != 4:
            continue
        parity = {pattern.bit_count() & 1 for pattern in allowed}
        if len(parity) != 1:
            continue
        rhs = next(iter(parity))
        forbidden = {tuple(-v if (pattern >> j) & 1 else v
                           for j, v in enumerate(scope))
                     for pattern in range(8)
                     if (pattern.bit_count() & 1) != rhs}
        if forbidden != canonical:
            continue
        mask = sum(1 << (v - 1) for v in scope)
        rows.append((mask, rhs))
        accepted.add(scope)
        proof = sha((proof, scope, mask, rhs))
    # Independently reduce the equations from their smallest pivots,
    # unlike the engine's rightmost-pivot incremental elimination.
    reduced = [[mask, rhs] for mask, rhs in rows]
    rank = 0
    for bit in range(n):
        selected = next((i for i in range(rank, len(reduced))
                         if reduced[i][0] & (1 << bit)), None)
        if selected is None:
            continue
        reduced[rank], reduced[selected] = reduced[selected], reduced[rank]
        for i in range(rank + 1, len(reduced)):
            if reduced[i][0] & (1 << bit):
                reduced[i][0] ^= reduced[rank][0]
                reduced[i][1] ^= reduced[rank][1]
        rank += 1
    inconsistent = any(mask == 0 and rhs for mask, rhs in reduced[rank:])
    residual = sum(1 for clause in clauses
                   if tuple(sorted(abs(v) for v in clause)) not in accepted)
    return proof, len(rows), residual, rank, inconsistent


def receipt_fields(receipt, n, clauses, raw_bytes):
    """All accepted proof, model, normalization, and source receipt fields."""
    kind = receipt["kind"]
    source_sha = sha(clauses)
    assert int(receipt["variables"]) == n
    assert receipt["fixture_seed"] == "frozen-" + kind + "-" + str(n) + "-v1"
    assert int(receipt["clauses"]) == len(clauses)
    assert receipt["source_sha256"] == source_sha
    assert receipt["dimacs_sha256"] == hashlib.sha256(raw_bytes).hexdigest()
    proof, accepted, residual, rank, inconsistent = independent_reductions(
        n, clauses, source_sha)
    assert receipt["proof_sha256"] == proof
    assert int(receipt["recognized"]) == accepted
    assert int(receipt["residual"]) == residual
    assert int(receipt["rank"]) == rank
    assert int(receipt["free_variables"]) == (0 if inconsistent else n - rank)
    status = receipt["status"]
    assert status in ("EXACT", "EXACT_UNSAT", "HOLD_BUDGET")
    if status == "HOLD_BUDGET":
        assert receipt["model_count"] == "HOLD"
        assert receipt["witness_integer"] == "NONE"
        assert int(receipt["search_nodes"]) == 20000
        count = None
        witness = None
    else:
        count = int(receipt["model_count"])
        assert count >= 0
        assert (status == "EXACT_UNSAT") == inconsistent
        if count == 0:
            assert receipt["witness_integer"] == "NONE"
            witness = None
        else:
            assert status == "EXACT"
            witness = int(receipt["witness_integer"])
            assert 0 <= witness < (1 << n)
            assert all(check(clause, witness) for clause in clauses)
    assert receipt["witness_sha256"] == sha(witness)
    assert receipt["result_sha256"] == sha((
        kind, n, source_sha, count, rank, proof, status))
    assert int(receipt["total_metered_units"]) > 0
    assert int(receipt["source_generation_ns"]) >= 0
    assert int(receipt["source_generation_bytes"]) == len(raw_bytes)
    assert int(receipt["elapsed_ns"]) >= int(receipt["source_generation_ns"])
    assert int(receipt["watcher_checks"]) >= 0
    assert int(receipt["fischer_scores"]) >= 0
    assert int(receipt["baseline_nodes"]) >= 0
    assert receipt["baseline_status"] in ("EXACT", "HOLD_BUDGET", "NOT_EXACT_REPLAYED")
    return count


def verify(receipt, directory):
    kind, n = receipt["kind"], int(receipt["variables"])
    name = kind + "-" + str(n)
    raw_bytes = directory.joinpath(name + ".cnf").read_bytes()
    parsed_n, clauses = independent_dimacs(raw_bytes.decode("ascii"))
    assert parsed_n == n
    assert clauses == expected_fixture(kind, n, receipt["fixture_seed"])
    declared_count = receipt_fields(receipt, n, clauses, raw_bytes)
    if kind == "xor":
        actual = independent_xor_count(n, clauses)
        assert actual is not None
    elif kind == "unsat":
        # All eight independent three-variable configurations excluded.
        assert len({tuple(c) for c in clauses[-8:]}) == 8
        actual = 0
    else:
        actual = counted_dpll(n, clauses, 3000000)
    if receipt["status"] != "HOLD_BUDGET":
        assert actual is not None and actual == declared_count
    elif actual is not None:
        # A HOLD may be independently resolved; it never claims the answer.
        assert actual >= 0
    return ("UNSAT" if actual == 0 else "SAT" if actual is not None else "UNKNOWN"), actual


def assignment_from_tokens(tokens, n):
    assert tokens
    values = {}
    terminated = False
    for token in tokens:
        assert not terminated, "literals after end marker"
        value = int(token)
        if value == 0:
            terminated = True
            continue
        assert 1 <= abs(value) <= n
        assert abs(value) not in values
        values[abs(value)] = value > 0
    assert terminated and values
    return values


def model_satisfies_partial(clauses, assignments):
    # All clauses must have an assigned true literal; unknown variables
    # are never optimistically treated as satisfying a clause.
    return all(any(assignments.get(abs(lit)) == (lit > 0)
                   for lit in clause if abs(lit) in assignments)
               for clause in clauses)


def verify_external_model(name, n, clauses, root, minisat_exit, picosat_exit):
    transcripts = root.joinpath("solver-transcripts")
    mini_sol = transcripts.joinpath(name + ".mini.sol").read_text(encoding="ascii")
    mini_log = transcripts.joinpath(name + ".mini.log").read_text(encoding="ascii")
    pico_log = transcripts.joinpath(name + ".pico.log").read_text(encoding="ascii")
    assert mini_log.strip() and pico_log.strip()
    assert transcripts.joinpath(name + ".mini-mem.txt").is_file()
    assert transcripts.joinpath(name + ".pico-mem.txt").is_file()
    mini = mini_sol.split()
    assert mini
    assert mini[0] == ("SAT" if minisat_exit == "10" else "UNSAT")
    pico_statuses = [line.split()[1] for line in pico_log.splitlines()
                     if line.startswith("s ") and len(line.split()) >= 2]
    assert pico_statuses == (["SATISFIABLE"] if picosat_exit == "10"
                             else ["UNSATISFIABLE"])
    pico_tokens = [token for line in pico_log.splitlines()
                   if line.startswith("v ")
                   for token in line.split()[1:]]
    if minisat_exit == "20":
        assert mini == ["UNSAT"] and not pico_tokens
        return "UNSAT"
    mini_values = assignment_from_tokens(mini[1:], n)
    pico_values = assignment_from_tokens(pico_tokens, n)
    assert model_satisfies_partial(clauses, mini_values)
    assert model_satisfies_partial(clauses, pico_values)
    return "SAT"


def corruption_controls(receipts, folder):
    seed_row = next(row for row in receipts if row["kind"] == "xor")
    name = seed_row["kind"] + "-" + seed_row["variables"]
    source_bytes = folder.joinpath(name + ".cnf").read_bytes()
    n, clauses = independent_dimacs(source_bytes.decode("ascii"))
    assert receipt_fields(seed_row, n, clauses, source_bytes) == int(seed_row["model_count"])
    mutations = {
        "source_sha256": "0" * 64,
        "dimacs_sha256": "0" * 64,
        "proof_sha256": "0" * 64,
        "result_sha256": "0" * 64,
        "witness_sha256": "0" * 64,
        "rank": str(int(seed_row["rank"]) + 1),
        "recognized": str(int(seed_row["recognized"]) + 1),
        "residual": str(int(seed_row["residual"]) + 1),
        "free_variables": str(int(seed_row["free_variables"]) + 1),
        "model_count": str(int(seed_row["model_count"]) + 1),
        "witness_integer": str(int(seed_row["witness_integer"]) ^ 1),
        "fixture_seed": seed_row["fixture_seed"] + "-tamper",
        "status": "HOLD_BUDGET",
    }
    for key, replacement in mutations.items():
        changed = dict(seed_row)
        changed[key] = replacement
        try:
            receipt_fields(changed, n, clauses, source_bytes)
        except (AssertionError, ValueError):
            pass
        else:
            raise AssertionError("tampered receipt accepted: " + key)
    hold_row = next(row for row in receipts if row["status"] == "HOLD_BUDGET")
    assert hold_row["kind"] == "planted" and hold_row["variables"] == "30"
    changed = dict(hold_row)
    changed["status"] = "EXACT"
    changed["model_count"] = "1"
    changed["witness_integer"] = "0"
    hb = folder.joinpath("planted-30.cnf").read_bytes()
    hn, hc = independent_dimacs(hb.decode("ascii"))
    try:
        receipt_fields(changed, hn, hc, hb)
    except (AssertionError, ValueError):
        pass
    else:
        raise AssertionError("forged HOLD-to-EXACT accepted")
    # Corrupted external SAT assignments must also be rejected.
    try:
        assignment_from_tokens(["1", "-1", "0"], 3)
    except AssertionError:
        pass
    else:
        raise AssertionError("contradictory model accepted")
    try:
        assignment_from_tokens(["1"], 3)
    except AssertionError:
        pass
    else:
        raise AssertionError("unterminated model accepted")
    print("SAT_HELDOUT_TAMPER|field_mutations_rejected=13|"
          "forged_hold_to_exact_rejected=PASS|"
          "bad_external_models_rejected=2|status=PASS")


def main(receipts, folder, baseline):
    root = Path(folder)
    lines = Path(receipts).read_text(encoding="ascii").splitlines()
    assert any(line.startswith("SAT_HELDOUT_CONTROL|") for line in lines)
    expected_final = ("SAT_HELDOUT_FINAL|cases=21|exact=20|unsat=0|hold=1|"
                      "frozen_DIMACS=PASS|")
    assert any(line.startswith(expected_final) for line in lines)
    rows = [parse_receipt(line) for line in lines
            if line.startswith("SAT_HELDOUT|")]
    expected_keys = (
        [("xor", n) for n in (24, 48, 96)] +
        [("mixed", n) for n in (12, 24, 36)] +
        [("planted", n) for n in (12, 18, 24, 30)] +
        [("random", n) for n in (12, 18, 24, 30)] +
        [("hub", n) for n in (12, 18, 24, 30)] +
        [("unsat", n) for n in (12, 24, 36)])
    assert len(rows) == len(expected_keys) == 21
    assert [(row["kind"], int(row["variables"])) for row in rows] == expected_keys
    assert sum(row["status"] == "EXACT" for row in rows) == 20
    assert sum(row["status"] == "HOLD_BUDGET" for row in rows) == 1
    assert sum(row["status"] == "EXACT_UNSAT" for row in rows) == 0
    assert [(row["kind"], row["variables"]) for row in rows
            if row["status"] == "HOLD_BUDGET"] == [("planted", "30")]
    corruption_controls(rows, root)
    found = {}
    for row in rows:
        key = row["kind"] + "-" + row["variables"]
        assert key not in found
        found[key] = verify(row, root)
    lines = Path(baseline).read_text(encoding="ascii").splitlines()
    external_rows = [line.split("\t") for line in lines
                     if line and not line.startswith("#")]
    assert len(external_rows) == 21
    external_keys = set()
    decision_count = {"SAT": 0, "UNSAT": 0}
    for cols in external_rows:
        assert len(cols) == 7
        key, minisat_exit, picosat_exit, mini_ns, pico_ns, mini_rss, pico_rss = cols
        assert key in found and key not in external_keys
        external_keys.add(key)
        assert minisat_exit in ("10", "20") and picosat_exit in ("10", "20")
        assert minisat_exit == picosat_exit
        assert all(int(value) >= 0 for value in
                   (mini_ns, pico_ns, mini_rss, pico_rss))
        # Read the original input independently, not the engine's model.
        n, clauses = independent_dimacs(
            root.joinpath(key + ".cnf").read_text(encoding="ascii"))
        external_decision = verify_external_model(
            key, n, clauses, root.parent, minisat_exit, picosat_exit)
        decision_count[external_decision] += 1
        if found[key][0] != "UNKNOWN":
            assert found[key][0] == external_decision
        elif key == "planted-30":
            assert external_decision == "SAT"
    assert len(external_keys) == 21
    assert decision_count == {"SAT": 17, "UNSAT": 4}
    print("SAT_HELDOUT_INDEPENDENT|cases=21|exact=20|hold=1|"
          "source_frozen=PASS|two_independent_SAT_decision_baselines=AGREE|"
          "external_sat_assignments=ALL_VERIFIED|hold_planted30_witness=PASS|"
          "proof_result_witness_hash_replay=PASS|rank_residual_free_replay=PASS|"
          "receipt_tamper_rejection=PASS|exact_counts_checked=PASS|"
          "source_sha_and_raw_DIMACS_sha=PASS|bounded_hold_preserved=PASS|status=PASS")


if __name__ == "__main__":
    assert len(sys.argv) == 4
    main(sys.argv[1], sys.argv[2], sys.argv[3])
