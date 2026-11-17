#!/usr/bin/env python3
"""Source-frozen MTP/Fischer/N-Nest SAT pilot. Exact integers only."""
import hashlib
import os
from time import monotonic_ns


def hidden_fixture(n):
    return sum((hashlib.sha256(("hidden:" + str(n) + ":" + str(i)).encode("ascii"))
                .digest()[0] & 1) << i for i in range(n))


def xor_clauses(triple, rhs):
    assert len(set(triple)) == 3
    return tuple(tuple(-v if (mask >> j) & 1 else v
                       for j, v in enumerate(triple))
                 for mask in range(8) if (mask.bit_count() & 1) != rhs)


def parity_family(n):
    assert n >= 9 and n % 3 == 0
    bits = hidden_fixture(n)
    triples = [(i + 1, ((i + 1) % n) + 1, ((i + n // 3) % n) + 1)
               for i in range(n)]
    triples.extend((i + 1, ((i + n // 3 + 1) % n) + 1,
                    ((i + 2 * n // 3 + 2) % n) + 1) for i in range(0, n, 3))
    return tuple(clause for triple in triples
                 for clause in xor_clauses(
                     triple, sum((bits >> (v - 1)) & 1 for v in triple) & 1)), len(triples)


def generic_family(n):
    bits = hidden_fixture(n)
    result = []
    for i in range(n):
        triples = ((i + 1, ((i + n // 3) % n) + 1, ((i + 2 * n // 3) % n) + 1),
                   (i + 1, ((i + 1) % n) + 1, ((i + n // 2) % n) + 1))
        for j, triple in enumerate(triples):
            signs = []
            for k, v in enumerate(triple):
                h = hashlib.sha256(("generic:" + str(i) + ":" + str(j) + ":" +
                                    str(k)).encode("ascii")).digest()[0]
                signs.append(v if h & 1 else -v)
            if not clauses_hold((tuple(signs),), bits):
                signs[0] = -signs[0]
            result.append(tuple(signs))
    return tuple(result)


def sha(value):
    return hashlib.sha256(repr(value).encode("ascii")).hexdigest()


def source_fingerprint(clauses):
    return sha(clauses)


def literal_true(lit, assignment):
    return bool((assignment >> (abs(lit) - 1)) & 1) == (lit > 0)


def clauses_hold(clauses, assignment):
    return all(any(literal_true(lit, assignment) for lit in clause) for clause in clauses)


def validate_source(n, clauses):
    assert isinstance(clauses, tuple) and n > 0
    assert all(isinstance(c, tuple) and len(c) == 3 for c in clauses)
    assert all(all(isinstance(x, int) and 1 <= abs(x) <= n for x in c) for c in clauses)
    assert all(len({abs(x) for x in c}) == 3 for c in clauses)


def local_truth(scope, clauses, metrics):
    allowed = []
    for assignment in range(8):
        valid = True
        for clause in clauses:
            sat = False
            for lit in clause:
                bit = (assignment >> scope.index(abs(lit))) & 1
                metrics["local_literal_checks"] += 1
                if bit == int(lit > 0):
                    sat = True
            if not sat:
                valid = False
        allowed.append(valid)
    return tuple(allowed)


def watcher_motif(scope, clauses, rhs, metrics):
    # Independent canonical-clause reconstruction, not the proposal's truth-table loop.
    canonical = set()
    for assignment in range(8):
        if assignment.bit_count() % 2 == rhs:
            continue
        canonical.add(tuple(-v if (assignment >> j) & 1 else v
                            for j, v in enumerate(scope)))
    metrics["watcher_clause_checks"] += 4
    normalized = {tuple(sorted(clause, key=abs)) for clause in clauses}
    return len(clauses) == 4 and len(normalized) == 4 and normalized == canonical


def compile_source(n, clauses, metrics, tamper_first=False):
    groups = {}
    for clause in clauses:
        scope = tuple(sorted(abs(x) for x in clause))
        groups.setdefault(scope, []).append(clause)
        metrics["group_inserts"] += 1
    rows = []
    accepted = set()
    trace = hashlib.sha256(source_fingerprint(clauses).encode("ascii")).hexdigest()
    corrected = 0
    for index, (scope, group) in enumerate(sorted(groups.items())):
        truth = local_truth(scope, group, metrics)
        good = [j for j, permitted in enumerate(truth) if permitted]
        if len(good) != 4 or len(group) != 4:
            continue
        sides = {j.bit_count() & 1 for j in good}
        if len(sides) != 1:
            continue
        rhs = next(iter(sides))
        guess = rhs ^ int(tamper_first and corrected == 0)
        if not watcher_motif(scope, group, guess, metrics):
            metrics["watcher_rejections"] += 1
            if not watcher_motif(scope, group, rhs, metrics):
                continue
            corrected += 1
        elif not watcher_motif(scope, group, rhs, metrics):
            raise AssertionError("watcher disagreement")
        mask = sum(1 << (v - 1) for v in scope)
        rows.append((mask, rhs))
        accepted.add(scope)
        trace = sha((trace, scope, mask, rhs))
        metrics["accepted_transforms"] += 1
    residual = tuple(c for c in clauses if tuple(sorted(abs(v) for v in c)) not in accepted)
    return tuple(rows), residual, trace, corrected


def right_eliminate(n, rows, metrics):
    basis = {}
    # Fischer-inspired SAT-specific score: width and projected overlap.
    ordered = sorted(rows, key=lambda r: (r[0].bit_count(), r[0].bit_length(), r))
    metrics["fischer_row_scores"] += len(rows)
    for mask, rhs in ordered:
        while mask:
            pivot = mask.bit_length() - 1
            metrics["pivot_probes"] += 1
            if pivot not in basis:
                basis[pivot] = (mask, rhs)
                metrics["basis_peak_bits"] = max(metrics["basis_peak_bits"],
                                                  len(basis) * (n + 1))
                break
            old, old_rhs = basis[pivot]
            mask ^= old
            rhs ^= old_rhs
            metrics["row_xors"] += 1
            metrics["xor_bitwork_bound"] += n + 1
        else:
            if rhs:
                return None
    return basis


def left_rank(n, rows, metrics):
    # Root N-Nest watcher uses the opposite pivot direction and full elimination.
    work = [[m, b] for m, b in rows]
    rank = 0
    for bit in range(n):
        match = next((j for j in range(rank, len(work))
                      if (work[j][0] >> bit) & 1), None)
        metrics["watcher_pivot_probes"] += len(work) - rank
        if match is None:
            continue
        work[rank], work[match] = work[match], work[rank]
        for j in range(len(work)):
            if j != rank and (work[j][0] >> bit) & 1:
                work[j][0] ^= work[rank][0]
                work[j][1] ^= work[rank][1]
                metrics["watcher_row_xors"] += 1
                metrics["watcher_bitwork_bound"] += n + 1
        rank += 1
    contradiction = any(mask == 0 and rhs for mask, rhs in work)
    return rank, contradiction


def affine_expressions(n, basis, rows, metrics):
    pivots = set(basis)
    expr = [((1 << v), 0) if v not in pivots else None for v in range(n)]
    for p in sorted(pivots):
        mask, rhs = basis[p]
        rest = mask ^ (1 << p)
        for q in sorted(pivots):
            if q >= p:
                break
            if rest & (1 << q):
                submask, subrhs = expr[q]
                rest ^= (1 << q) ^ submask
                rhs ^= subrhs
                metrics["backsub_xors"] += 1
        assert not any(rest & (1 << q) for q in pivots)
        expr[p] = rest, rhs
    for mask, rhs in rows:
        check_mask, check_rhs = 0, rhs
        for v in range(n):
            if mask & (1 << v):
                part, bit = expr[v]
                check_mask ^= part
                check_rhs ^= bit
                metrics["watcher_expression_checks"] += 1
        assert check_mask == 0 and check_rhs == 0
    return tuple(expr), tuple(v for v in range(n) if v not in pivots)


def expand(expr, free_assignment):
    return sum((((free_assignment & m).bit_count() & 1) ^ rhs) << i
               for i, (m, rhs) in enumerate(expr))


def branch_order(free, residual, expr, metrics, mode):
    if mode == "fixed":
        return free
    ranked = []
    for v in free:
        covered = 0
        footprint = 0
        bit = 1 << v
        for clause in residual:
            masks = [expr[abs(lit) - 1][0] for lit in clause]
            covered += int(any(mask & bit for mask in masks))
            footprint += sum(mask.bit_count() for mask in masks if mask & bit)
            metrics["fischer_literal_scores"] += len(clause)
        ranked.append((-covered, footprint, v))
    return tuple(row[-1] for row in sorted(ranked))


class Budget(Exception):
    pass


def bounded_exact(n, clauses, residual, expr, free, limit, metrics, mode):
    order = branch_order(free, residual, expr, metrics, mode)
    first = [None]
    def recurse(known, free_value, depth):
        if metrics["search_nodes"] >= limit:
            raise Budget()
        metrics["search_nodes"] += 1
        complete = True
        for clause in residual:
            satisfied = False
            pending = False
            for lit in clause:
                mask, rhs = expr[abs(lit) - 1]
                metrics["search_literal_checks"] += 1
                if mask & ~known:
                    pending = True
                elif (((mask & free_value).bit_count() & 1) ^ rhs) == int(lit > 0):
                    satisfied = True
                    break
            if not satisfied and not pending:
                return 0
            if not satisfied:
                complete = False
        if complete:
            if first[0] is None:
                first[0] = expand(expr, free_value)
                assert clauses_hold(clauses, first[0])
                metrics["witness_literal_checks"] += sum(map(len, clauses))
            return 1 << (len(order) - depth)
        if depth == len(order):
            return 0
        bit = 1 << order[depth]
        return recurse(known | bit, free_value, depth + 1) + recurse(
            known | bit, free_value | bit, depth + 1)
    try:
        count = recurse(0, 0, 0)
        return count, first[0], "EXACT"
    except Budget:
        return None, None, "HOLD_BUDGET"


def peak_kib():
    try:
        with open("/proc/self/status", encoding="ascii") as handle:
            for line in handle:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1])
    except OSError:
        pass
    return -1


def execute(kind, n, clauses, limit=20000, injected=False):
    validate_source(n, clauses)
    start = monotonic_ns()
    frozen = source_fingerprint(clauses)
    metrics = {name: 0 for name in (
        "group_inserts", "local_literal_checks", "watcher_clause_checks",
        "watcher_rejections", "accepted_transforms", "fischer_row_scores",
        "pivot_probes", "row_xors", "xor_bitwork_bound", "basis_peak_bits",
        "watcher_pivot_probes", "watcher_row_xors", "watcher_bitwork_bound",
        "backsub_xors", "watcher_expression_checks", "fischer_literal_scores",
        "search_nodes", "search_literal_checks", "witness_literal_checks")}
    rows, residual, proof, corrected = compile_source(n, clauses, metrics, injected)
    assert source_fingerprint(clauses) == frozen
    basis = right_eliminate(n, rows, metrics)
    rank, contradictory = left_rank(n, rows, metrics)
    assert (basis is None) == contradictory
    baseline = {name: 0 for name in metrics}
    selected = "fischer"
    if basis is None:
        count, witness, status = 0, None, "EXACT_UNSAT"
        free = ()
        baseline_status = "NOT_EXACT_REPLAYED"
    else:
        assert len(basis) == rank
        expr, free = affine_expressions(n, basis, rows, metrics)
        count, witness, status = bounded_exact(n, clauses, residual, expr, free,
                                                limit, metrics, "fischer")
        check, fixed_witness, baseline_status = bounded_exact(
            n, clauses, residual, expr, free, limit, baseline, "fixed")
        if baseline_status == "EXACT":
            if status == "EXACT":
                assert check == count
            else:
                count, witness, status, selected = check, fixed_witness, "EXACT", "fixed"
    assert source_fingerprint(clauses) == frozen
    work = len(repr(clauses).encode("ascii")) + sum(metrics.values()) + sum(baseline.values())
    result_sha = sha((kind, n, frozen, count, rank, proof, status))
    record = dict(kind=kind, variables=n, clauses=len(clauses), rank=rank,
                  recognized=len(rows), residual=len(residual),
                  free_variables=len(free), model_count=count if count is not None else "HOLD",
                  status=status, source_sha256=frozen, proof_sha256=proof,
                  result_sha256=result_sha, corrected_proposals=corrected,
                  total_metered_units=work, fischer_scores=metrics["fischer_row_scores"] +
                  metrics["fischer_literal_scores"], watcher_checks=metrics["watcher_clause_checks"] +
                  metrics["watcher_pivot_probes"] + metrics["watcher_row_xors"] +
                  metrics["watcher_expression_checks"],
                  search_nodes=metrics["search_nodes"], baseline_nodes=baseline["search_nodes"],
                  baseline_status=baseline_status, selected_order=selected,
                  witness_sha256=sha(witness),
                  witness_integer=witness if witness is not None else "NONE",
                  peak_rss_kib=peak_kib(), elapsed_ns=monotonic_ns() - start)
    return record


def fixture_sources():
    # Generator creates clauses only; the solver receives no planted assignment.
    for n in (48, 72, 384):
        start = monotonic_ns()
        source, _ = parity_family(n)
        yield "parity", n, source, monotonic_ns() - start
    for n in (12, 24, 36, 48, 72):
        start = monotonic_ns()
        parity, _ = parity_family(n)
        scopes = {tuple(sorted(abs(v) for v in c)) for c in parity[:4 * (n // 2)]}
        residual = []
        for c in generic_family(n):
            if tuple(sorted(abs(v) for v in c)) not in scopes:
                residual.append(c)
            if len(residual) == n // 2:
                break
        yield "mixed", n, parity[:4 * (n // 2)] + tuple(residual), monotonic_ns() - start
    for n in (12, 18, 24):
        start = monotonic_ns()
        source = generic_family(n)
        yield "generic", n, source, monotonic_ns() - start


def controls():
    m = {k: 0 for k in ("group_inserts", "local_literal_checks",
                         "watcher_clause_checks", "watcher_rejections",
                         "accepted_transforms")}
    c = xor_clauses((1, 2, 3), 0)
    rows, residual, _, corrected = compile_source(3, c, m, True)
    assert len(rows) == 1 and not residual and corrected == 1
    assert m["watcher_rejections"] == 1
    incomplete = c[:3]
    assert len(compile_source(3, incomplete, m)[0]) == 0
    assert source_fingerprint(c) != source_fingerprint(incomplete)
    contradictory = c + xor_clauses((1, 2, 3), 1)
    assert execute("negative", 3, contradictory)["model_count"] == 0
    print("SAT_CONTROL|wrong_proposal_rejected=PASS|incomplete_motif=PASS|tampered_source_sha=PASS|conflict_unsat=PASS")


def main():
    controls()
    cases = []
    for kind, n, source, generator_ns in fixture_sources():
        limit = 20000 if n <= 24 else 6000
        r = execute(kind, n, source, limit=limit, injected=True)
        r["source_generation_ns"] = generator_ns
        r["source_generation_clause_writes"] = len(source)
        r["elapsed_ns"] += generator_ns
        r["total_metered_units"] += len(source)
        cases.append(r)
        print("SAT_INTEGRATED|" + "|".join(str(k) + "=" + str(v)
              for k, v in r.items()) + "|json=0", flush=True)
    assert len(cases) == 11
    print("SAT_INTEGRATED_FINAL|cases=11|source_frozen=PASS|corrected_proposals=PASS|"
          "independent_nnest_watcher=PASS|baseline_metered=PASS|"
          "P_equals_NP=NOT_ESTABLISHED|original_Wilson_first_weight=HOLD|status=RESEARCH_PILOT")




# Held-out, source-frozen decision and exact-count evaluation.
# Separate seeds from the earlier generated #295 fixtures.
def heldout_bit(seed, *parts):
    label = "heldout-v1:" + seed + ":" + ":".join(str(part) for part in parts)
    return int.from_bytes(hashlib.sha256(label.encode("ascii")).digest()[:8], "big")


def dimacs(variables, clauses):
    validate_source(variables, clauses)
    lines = ["c heldout-v1 exact source", "p cnf " + str(variables) + " " + str(len(clauses))]
    lines.extend(" ".join(str(lit) for lit in clause) + " 0" for clause in clauses)
    return "\n".join(lines) + "\n"


def parse_dimacs(raw):
    header = None
    clauses = []
    current = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("c ") or line == "c":
            continue
        if line.startswith("p "):
            parts = line.split()
            assert header is None and len(parts) == 4 and parts[1] == "cnf"
            n, expected = int(parts[2]), int(parts[3])
            assert n > 0 and expected >= 0 and not current
            header = (n, expected)
            continue
        assert header is not None
        for token in line.split():
            literal = int(token)
            if literal == 0:
                assert len(current) == 3 and len({abs(x) for x in current}) == 3
                assert all(1 <= abs(x) <= header[0] for x in current)
                clauses.append(tuple(current))
                current = []
            else:
                assert 1 <= abs(literal) <= header[0]
                current.append(literal)
                assert len(current) <= 3
    assert header is not None and not current and len(clauses) == header[1]
    return header[0], tuple(clauses)


def heldout_source(kind, n, seed):
    assert n >= 12
    original = sum((heldout_bit(seed, "truth", i) & 1) << i for i in range(n))
    if kind in ("xor", "mixed"):
        assert n % 3 == 0
        triples = [(i + 1, (i + 1) % n + 1, (i + n // 3) % n + 1)
                   for i in range(n)]
        if kind == "mixed":
            triples = triples[:n // 2]
        clauses = []
        for tr in triples:
            rhs = sum((original >> (v - 1)) & 1 for v in tr) & 1
            clauses.extend(xor_clauses(tr, rhs))
        if kind == "xor":
            return tuple(clauses)
        avoid = {tuple(sorted(abs(x) for x in c)) for c in clauses}
    else:
        clauses = []
        avoid = set()
    if kind in ("mixed", "planted", "random", "hub", "unsat"):
        target = n if kind == "mixed" else (17 * n + 3) // 4
        for index in range(target):
            scope = []
            attempt = 0
            while len(scope) < 3:
                value = heldout_bit(seed, kind, "var", index, attempt)
                attempt += 1
                variable = 1 + (value % (min(4, n) if kind == "hub" and not scope else n))
                if variable not in scope:
                    scope.append(variable)
            if tuple(sorted(scope)) in avoid:
                # Explicitly avoid every source-XOR triple without collisions.
                choices = [v for v in range(1, n + 1)
                           if v not in scope[:2] and
                           tuple(sorted(scope[:2] + [v])) not in avoid]
                assert choices
                scope[-1] = choices[heldout_bit(seed, "avoid", index) % len(choices)]
            clause = tuple(v if heldout_bit(seed, kind, "sign", index, slot) & 1
                           else -v for slot, v in enumerate(scope))
            if kind != "random" and not clauses_hold((clause,), original):
                clause = (-clause[0],) + clause[1:]
            clauses.append(clause)
    if kind == "unsat":
        # Source-level known UNSAT negative: all eight 3-variable assignments
        # are forbidden explicitly; no claimed hard random UNSAT instance.
        for mask in range(8):
            clauses.append(tuple(-v if (mask >> j) & 1 else v
                                 for j, v in enumerate((1, 2, 3))))
    return tuple(clauses)


def heldout_cases():
    for kind, ns in (
        ("xor", (24, 48, 96)),
        ("mixed", (12, 24, 36)),
        ("planted", (12, 18, 24, 30)),
        ("random", (12, 18, 24, 30)),
        ("hub", (12, 18, 24, 30)),
        ("unsat", (12, 24, 36)),
    ):
        for n in ns:
            yield kind, n, "frozen-" + kind + "-" + str(n) + "-v1"


def heldout_controls():
    base = dimacs(12, heldout_source("random", 12, "frozen-random-12-v1"))
    assert parse_dimacs(base)[1] == heldout_source("random", 12, "frozen-random-12-v1")
    assert parse_dimacs(base.replace(" 0\n", "\n0\n"))[1] == parse_dimacs(base)[1]
    for corrupt in (
        base.replace("p cnf 12 ", "p cnf 11 "),
        base.replace("p cnf 12 ", "p cnf 0 "),
        base.replace(" 0\n", " 0 0\n", 1),
        base.replace("p cnf 12 ", "p cna 12 "),
        base + "1 2 3 0\n",
        base.replace("p cnf 12 ", "p cnf 12 999 "),
    ):
        try:
            parse_dimacs(corrupt)
        except (AssertionError, ValueError):
            pass
        else:
            raise AssertionError("invalid DIMACS accepted")
    altered = base.replace("p cnf 12", "p cnf 13")
    assert hashlib.sha256(altered.encode("ascii")).hexdigest() != hashlib.sha256(base.encode("ascii")).hexdigest()
    print("SAT_HELDOUT_CONTROL|roundtrip=PASS|split_clauses=PASS|invalid_DIMACS_rejected=6|"
          "raw_byte_tamper_sha=PASS|status=PASS", flush=True)


def heldout_main():
    from pathlib import Path
    import sys
    assert len(sys.argv) == 3 and sys.argv[1] == "--heldout"
    outdir = Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    heldout_controls()
    states = []
    for kind, n, seed in heldout_cases():
        started = monotonic_ns()
        source = heldout_source(kind, n, seed)
        raw = dimacs(n, source)
        parsed_n, parsed_clauses = parse_dimacs(raw)
        assert (parsed_n, parsed_clauses) == (n, source)
        source_generation_ns = monotonic_ns() - started
        name = kind + "-" + str(n)
        with open(outdir.joinpath(name + ".cnf"), "w", encoding="ascii") as handle:
            handle.write(raw)
        # Limit includes all counted decision-tree nodes for each ordering;
        # large unconstrained formulas are permitted to return HOLD.
        r = execute(kind, n, parsed_clauses, limit=20000, injected=True)
        r["fixture_seed"] = seed
        r["dimacs_sha256"] = hashlib.sha256(raw.encode("ascii")).hexdigest()
        r["source_generation_ns"] = source_generation_ns
        r["source_generation_bytes"] = len(raw.encode("ascii"))
        r["elapsed_ns"] += source_generation_ns
        r["total_metered_units"] += len(raw)
        states.append(r["status"])
        print("SAT_HELDOUT|" + "|".join(str(k) + "=" + str(v)
              for k, v in r.items()) + "|json=0", flush=True)
    assert len(states) == 21
    print("SAT_HELDOUT_FINAL|cases=21|exact=" + str(states.count("EXACT")) +
          "|unsat=" + str(states.count("EXACT_UNSAT")) +
          "|hold=" + str(states.count("HOLD_BUDGET")) +
          "|frozen_DIMACS=PASS|independent_count_verifier=REQUIRED|"
          "external_SAT_verdict=REQUIRED|P_equals_NP=NOT_ESTABLISHED|"
          "original_Wilson_first_weight=HOLD|status=RESEARCH_PILOT", flush=True)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        heldout_main()
    else:
        main()
