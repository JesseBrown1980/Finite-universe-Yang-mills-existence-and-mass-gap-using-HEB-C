#!/usr/bin/env python3
"""Shadow check of a sealed merge's column partition (countmerge), as SAT with proof.
Claim: the merge's cells (MERGE_INPUT cols=a:b) cover every column of [0, core) exactly
once, core from the sealed core table. The CNF asserts the NEGATION (some column in
[0, core) is covered by 0 or >= 2 cells); the claim holds iff it is UNSAT. The UNSAT
proof (DRUP, Glucose 4) is checked by drat-trim. A SAT model is decoded to its column and
re-checked by plain arithmetic. With Lean's countmerge_conserves, an exact partition
means the merged count equals the whole count. Integer-only, json=0.
usage: partition_sat.py DRAT_TRIM CORES_HBP SHARD_DIR... [--fault shift|weaken_cnf]
Controls: shift opens a one-column gap (must turn SAT, column confirmed by arithmetic);
weaken_cnf hands drat-trim the formula without the negated claim (proof must not verify);
hash_tamper records a CNF hash that differs from the formula the checker saw (must not certify).
"""
import hashlib
import itertools
import os
import subprocess
import sys
import tempfile

from pysat.solvers import Solver


def cells_of(shard):
    out = []
    for line in open(os.path.join(shard, "run.hbp")):
        if line.startswith("MERGE_INPUT|"):
            f = dict(p.split("=", 1) for p in line.strip().split("|")[1:] if "=" in p)
            a, b = f["cols"].split(":")
            out.append((int(a), int(b)))
    return out


def encode(cells, core):
    n = 0
    cl = []

    def var():
        nonlocal n
        n += 1
        return n
    c = [var() for _ in range(core)]                       # the chosen column, one-hot
    cl.append(list(c))
    for i, j in itertools.combinations(range(core), 2):
        cl.append([-c[i], -c[j]])
    cov = []
    for a, b in cells:                                     # cover_i <-> OR_{j in [a,b) ∩ [0,core)} c_j
        v = var()
        js = [c[j] for j in range(max(0, a), min(b, core))]
        cl.append([-v] + js)
        for x in js:
            cl.append([v, -x])
        cov.append(v)
    two = []
    for i, j in itertools.combinations(range(len(cov)), 2):  # p <-> cov_i AND cov_j
        p = var()
        cl += [[-p, cov[i]], [-p, cov[j]], [p, -cov[i], -cov[j]]]
        two.append(p)
    none_ = var()                                          # none <-> no cell covers the column
    cl.append([none_] + cov)
    for v in cov:
        cl.append([-none_, -v])
    cl.append([none_] + two)                               # negated claim: none OR at-least-two
    return n, cl, c


def check(drat, cells, core, weaken=False, tamper_hash=False):
    n, cl, c = encode(cells, core)
    text = "p cnf %d %d\n" % (n, len(cl)) + "".join(" ".join(map(str, x)) + " 0\n" for x in cl)
    cnf_hash = hashlib.sha256(text.encode()).hexdigest()   # the proof is bound to this exact CNF
    with Solver(name="g4", bootstrap_with=cl, with_proof=True) as s:
        sat = s.solve()
        if sat:
            m = set(v for v in s.get_model() if v > 0)
            col = next(j for j in range(core) if c[j] in m)
            k = sum(1 for a, b in cells if a <= col < b)
            return "SAT", "cnf_sha256=%s|column=%d|covered_by=%d|arithmetic_confirms=%d" % (cnf_hash, col, k, k != 1)
        proof = s.get_proof()
    proof_text = "\n".join(proof) + "\n"
    proof_hash = hashlib.sha256(proof_text.encode()).hexdigest()
    recorded = cnf_hash if not tamper_hash else "0" * 64
    if weaken:                                             # control: the checker sees a formula without the negated claim
        cl = cl[:-1]
        text = "p cnf %d %d\n" % (n, len(cl)) + "".join(" ".join(map(str, x)) + " 0\n" for x in cl)
    with tempfile.TemporaryDirectory() as d:
        cnf, prf = os.path.join(d, "f.cnf"), os.path.join(d, "f.drat")
        open(cnf, "w").write(text)
        open(prf, "w").write(proof_text)
        checked_hash = hashlib.sha256(open(cnf, "rb").read()).hexdigest()
        try:
            r = subprocess.run([drat, cnf, prf], capture_output=True, text=True, timeout=600)
            verified = "s VERIFIED" in r.stdout
        except subprocess.TimeoutExpired:
            verified = False                               # a checker timeout fails closed
    bound = checked_hash == recorded
    return "UNSAT", "cnf_sha256=%s|proof_sha256=%s|checked_cnf_matches_record=%d|drat_trim=%s|proof_lines=%d" % (
        recorded, proof_hash, bound, "VERIFIED" if verified and bound else "NOT_VERIFIED", len(proof))


def main(argv):
    drat, cores = argv[0], argv[1]
    fault = argv[argv.index("--fault") + 1] if "--fault" in argv else None
    shards = [a for a in argv[2:] if not a.startswith("--") and a not in ("shift", "weaken_cnf", "hash_tamper")]
    core_of = {}
    for line in open(cores):
        if line.startswith("CORE|"):
            f = dict(p.split("=", 1) for p in line.strip().split("|")[1:] if "=" in p)
            core_of[f["spec"]] = int(f["core_rows"])
    ok = True
    for sh in shards:
        name = os.path.basename(sh.rstrip("/"))
        spec = name.replace("countmerge_", "count_", 1)
        kind, rest = spec.split("_", 1)
        core = core_of[kind + "/" + rest.replace("_", "/")]
        cells = cells_of(sh)
        if fault == "shift":
            a, b = cells[1]
            cells[1] = (a + 1, b)                          # a one-column gap
        res, det = check(drat, cells, core, weaken=fault == "weaken_cnf", tamper_hash=fault == "hash_tamper")
        good = res == "UNSAT" and "VERIFIED" in det and "NOT_VERIFIED" not in det
        ok &= good
        print("PARTITION|shard=%s|core=%d|cells=%d|fault=%s|result=%s|%s|claim=%s|json=0"
              % (name, core, len(cells), fault or "none", res, det, "EXACT" if good else "NOT_CERTIFIED"))
    print("PARTITION_VERDICT|%s|json=0" % ("CERTIFIED" if ok else "NOT_CERTIFIED"))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
