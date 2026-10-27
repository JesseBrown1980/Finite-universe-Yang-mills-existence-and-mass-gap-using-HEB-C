#!/usr/bin/env python3
"""Shadow stack layer 2: a count-preserving CNF for the 2x2 gauge-orbit count, checked by
exact #SAT on two independent engines. Integer-only, json=0.

The object counted: configurations of the 5 free links (maximal-tree gauge fixed) in S3^5,
up to simultaneous conjugation by S3. INDEP_BUILD records gauge_orbits = burnside = 1393.

Count-preserving encoding: exactly one assignment per orbit, its lexicographically
smallest member: x <=_lex g x g^-1 for all g in S3. Link variables are one-hot (exactly one
value per link). Auxiliary variables are defined by full equivalences (Tseitin, <->), so
each link assignment extends in exactly one way: the total model count equals the count
projected onto the link variables, and the run checks that it does.

Gates (all must hold, else NOT_CERTIFIED):
  E1  pycosat: every model enumerated over ALL variables         -> count A
  E2  pysat (Minisat22): models enumerated projected on link vars -> count B
  E3  every model of E1 decodes to a configuration that is the lex-min of its orbit,
      checked directly in Python without the CNF
  E4  direct enumeration of S3^5 orbits (no CNF), and Burnside (6^5 + 3*2^5 + 2*3^5)/6
  E5  A = B = E4 = Burnside = 1393 (the recorded value)
usage: orbit_cnf.py [--fault drop_g|loose_aux]      writes ORBIT-2X2.cnf, prints the receipt
Controls: drop_g removes every lex constraint for one conjugation (count must rise);
loose_aux leaves one auxiliary variable undetermined (total != projected count).
"""
import hashlib
import itertools
import sys

K = 5          # free links on the 2x2 torus after the maximal-tree gauge fix
EXPECT = 1393  # INDEP_BUILD gauge_orbits for L = 2x2


def s3():
    els = sorted(itertools.permutations(range(3)))          # 6 elements, fixed order
    idx = {p: i for i, p in enumerate(els)}
    mul = [[idx[tuple(a[b[k]] for k in range(3))] for b in els] for a in els]
    inv = [idx[tuple(sorted(range(3), key=lambda k: a[k]))] for a in els]
    return els, mul, inv


def conj_tables():
    els, mul, inv = s3()
    return [[mul[mul[g][v]][inv[g]] for v in range(6)] for g in range(6)], els


class CNF:
    def __init__(self):
        self.n, self.cl = 0, []

    def var(self):
        self.n += 1
        return self.n

    def add(self, c):
        self.cl.append(list(c))


def encode(fault=None):
    conj, els = conj_tables()
    f = CNF()
    x = [[f.var() for _ in range(6)] for _ in range(K)]
    for l in range(K):                                     # exactly one value per link
        f.add(x[l])
        for a, b in itertools.combinations(range(6), 2):
            f.add([-x[l][a], -x[l][b]])
    for g in range(6):
        p = conj[g]
        if p == list(range(6)):
            continue                                       # identity
        e_prev = None                                      # e_0 = true
        for l in range(K):
            # lex: while the prefix is equal, x_l must not exceed... value v with p[v] < v is forbidden
            bad = [v for v in range(6) if p[v] < v]
            if fault == "drop_g" and g == 1:
                bad = []                                   # control: one conjugation's lex constraints removed
            for v in bad:
                f.add(([-e_prev] if e_prev else []) + [-x[l][v]])
            # fix_l <-> OR_{v : p[v] == v} x[l][v]
            fixv = [v for v in range(6) if p[v] == v]
            fx = f.var()
            f.add([-fx] + [x[l][v] for v in fixv])
            for v in fixv:
                f.add([fx, -x[l][v]])
            # e_{l+1} <-> e_l AND fix_l
            e = f.var()
            if fault == "loose_aux" and g == 1 and l == 0:
                f.add([-e, fx])                            # one direction only: aux no longer determined
            elif e_prev is None:
                f.add([-e, fx]); f.add([e, -fx])
            else:
                f.add([-e, e_prev]); f.add([-e, fx]); f.add([e, -e_prev, -fx])
            e_prev = e
    return f, x, conj


def lexmin(cfg, conj):
    return all(tuple(cfg) <= tuple(conj[g][v] for v in cfg) for g in range(6))


def direct_orbits(conj):
    seen, orbits = set(), 0
    for cfg in itertools.product(range(6), repeat=K):
        if cfg in seen:
            continue
        orbits += 1
        for g in range(6):
            seen.add(tuple(conj[g][v] for v in cfg))
    return orbits


def main(argv):
    fault = argv[argv.index("--fault") + 1] if "--fault" in argv else None
    f, x, conj = encode(fault)
    dimacs = "p cnf %d %d\n" % (f.n, len(f.cl)) + "".join(" ".join(map(str, c)) + " 0\n" for c in f.cl)
    open("ORBIT-2X2.cnf" if not fault else "ORBIT-2X2-%s.cnf" % fault, "w").write(dimacs)
    h = hashlib.sha256(dimacs.encode()).hexdigest()
    import pycosat
    from pysat.solvers import Solver
    a, decoded_ok, models = 0, True, set()
    for m in pycosat.itersolve(f.cl, vars=f.n):
        a += 1
        pos = set(v for v in m if v > 0)
        cfg = tuple(next(v for v in range(6) if x[l][v] in pos) for l in range(K))
        models.add(cfg)
        decoded_ok &= lexmin(cfg, conj)
    b = 0
    linkvars = [v for row in x for v in row]
    with Solver(name="m22", bootstrap_with=f.cl) as s:
        while s.solve():
            m = s.get_model()
            b += 1
            s.add_clause([-v for v in linkvars if m[v - 1] > 0])
    d = direct_orbits(conj)
    burn = (6 ** K + 3 * 2 ** K + 2 * 3 ** K) // 6
    print("SAT_CNF|object=S3^%d_mod_conjugation|vars=%d|clauses=%d|cnf_sha256=%s|fault=%s|json=0" % (K, f.n, len(f.cl), h, fault or "none"))
    print("SAT_COUNT|E1_pycosat_all_vars=%d|E2_pysat_m22_projected=%d|E3_models_lexmin=%d|E3_distinct=%d|E4_direct=%d|burnside=%d|recorded=%d|json=0"
          % (a, b, int(decoded_ok), len(models), d, burn, EXPECT))
    ok = a == b == len(models) == d == burn == EXPECT and decoded_ok
    print("SAT_VERDICT|%s|json=0" % ("CERTIFIED" if ok else "NOT_CERTIFIED"))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
