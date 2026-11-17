#!/usr/bin/env python3
"""Independent source replay and exact result verifier; does not load engine.py."""
import hashlib
import importlib.util
import sys
from pathlib import Path

PRIOR = Path(__file__).resolve().parent.parent.joinpath("y137-hierarchical-mtp-sat-20261117", "verify.py")


def sha(x):
    return hashlib.sha256(repr(x).encode("ascii")).hexdigest()


def load_cleanroom():
    spec = importlib.util.spec_from_file_location("independent_source_reconstruction", PRIOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse(line):
    fields = line.strip().split("|")
    return dict(field.split("=", 1) for field in fields[1:]
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


def verify_row(src, row, gen):
    kind, n = row["kind"], int(row["variables"])
    if kind == "parity":
        clauses, eqs = gen.fixture(n)
        residual = ()
    elif kind == "mixed":
        clauses, eqs, residual = gen.hybrid_source(n)
    else:
        assert kind == "generic"
        clauses = gen.generic_source(n)
        eqs, residual = (), clauses
    clauses = tuple(clauses)
    assert gen.sha_repr(clauses) == row["source_sha256"]
    assert len(clauses) == int(row["clauses"])
    assert row["source_sha256"] == sha(clauses)
    assert int(row["recognized"]) == len(eqs)
    assert len(residual) == int(row["residual"])
    assert replay_proof(row["source_sha256"], eqs, n) == row["proof_sha256"]
    rank, independent_witness, _ = gen.gaussian_left(n, eqs)
    assert rank == int(row["rank"])
    if eqs:
        assert all(gen.check_clause(clause, independent_witness)
                   for clause in clauses if
                   tuple(sorted(abs(v) for v in clause)) in
                   {tuple(i + 1 for i in range(n) if (mask >> i) & 1)
                    for mask, rhs in eqs})
    status = row["status"]
    if status == "EXACT":
        count = int(row["model_count"])
        if kind == "parity":
            expected = 1 << (n - rank)
        elif kind == "mixed":
            expected, trials, checks = gen.hybrid_count_via_left_pivot(
                n, eqs, residual, 262144)
            assert expected is not None
        else:
            assert n <= 24
            expected = gen.bitparallel_count(n, clauses)
        assert count == expected
        witness = int(row["witness_integer"])
        assert all(gen.check_clause(c, witness) for c in clauses)
        assert sha(witness) == row["witness_sha256"]
    else:
        assert status == "HOLD_BUDGET"
        assert row["model_count"] == "HOLD"
        assert row["witness_integer"] == "NONE"
        count = None
    assert sha((kind, n, row["source_sha256"], count, rank,
                row["proof_sha256"], status)) == row["result_sha256"]
    assert int(row["total_metered_units"]) > 0
    assert int(row["watcher_checks"]) > 0 or not eqs
    assert int(row["fischer_scores"]) >= 0
    assert int(row["elapsed_ns"]) > 0
    return status


def main(path):
    gen = load_cleanroom()
    lines = Path(path).read_text(encoding="ascii").splitlines()
    assert any(line.startswith("SAT_CONTROL|") for line in lines)
    assert any(line.startswith("SAT_INTEGRATED_FINAL|cases=11|") for line in lines)
    rows = [parse(line) for line in lines if line.startswith("SAT_INTEGRATED|")]
    assert len(rows) == 11
    keys = [(r["kind"], int(r["variables"])) for r in rows]
    assert keys == ([( "parity", n) for n in (48, 72, 384)] +
                    [( "mixed", n) for n in (12, 24, 36, 48, 72)] +
                    [( "generic", n) for n in (12, 18, 24)])
    states = [verify_row(None, row, gen) for row in rows]
    assert rows[0]["source_sha256"] != rows[1]["source_sha256"]
    assert all(r["corrected_proposals"] == "1" for r in rows[:8])
    assert all(r["corrected_proposals"] == "0" for r in rows[8:])
    assert all(r["baseline_status"] in ("EXACT", "HOLD_BUDGET", "NOT_EXACT_REPLAYED")
               for r in rows)
    print("SAT_INTEGRATED_INDEPENDENT|cases=11|exact=" +
          str(states.count("EXACT")) + "|hold=" + str(states.count("HOLD_BUDGET")) +
          "|source_sha=PASS|proof_chain=PASS|independent_left_rank=PASS|"
          "complete_model_counts=PASS|original_CNF_witnesses=PASS|status=PASS")


if __name__ == "__main__":
    assert len(sys.argv) == 2
    main(sys.argv[1])
