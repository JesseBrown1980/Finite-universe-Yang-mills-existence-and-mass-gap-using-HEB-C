#!/usr/bin/env python3
"""The orbit CNF of orbit_cnf.py for k free links, counted exactly by Ganak (total and
projected onto the link variables) and compared with a direct count that uses no CNF
(direct_orbits.rs), Burnside, and the recorded gauge_orbits. Integer-only, json=0.
  L = 2x2: k = 5,  recorded 1,393       (INDEP_BUILD)
  L = 3x3: k = 10, recorded 10,097,891  (stage A YMSEC gauge_orbits)
usage: orbit_ganak.py K RECORDED DIRECT_BIN [--fault drop_g|loose_aux]
"""
import hashlib
import subprocess
import sys

import orbit_cnf as oc


def main(argv):
    k, recorded, direct = int(argv[0]), int(argv[1]), argv[2]
    fault = argv[argv.index("--fault") + 1] if "--fault" in argv else None
    oc.K = k
    f, x, _ = oc.encode(fault)
    dimacs = "p cnf %d %d\n" % (f.n, len(f.cl)) + "".join(" ".join(map(str, c)) + " 0\n" for c in f.cl)
    h = hashlib.sha256(dimacs.encode()).hexdigest()
    if not fault:
        open("ORBIT-K%d.cnf" % k, "w").write(dimacs)
    from pyganak import Counter
    c1 = Counter()
    c1.new_vars(f.n)
    c1.add_clauses(f.cl)
    total = c1.count()
    c2 = Counter()
    c2.new_vars(f.n)
    c2.add_clauses(f.cl)
    c2.set_sampling_set([v for row in x for v in row])
    proj = c2.count()
    d = dict(p.split("=", 1) for p in subprocess.run([direct, str(k)], capture_output=True, text=True, check=True)
             .stdout.strip().split("|")[1:] if "=" in p)
    burn = (6 ** k + 3 * 2 ** k + 2 * 3 ** k) // 6
    print("SAT_CNF|K=%d|vars=%d|clauses=%d|cnf_sha256=%s|fault=%s|json=0" % (k, f.n, len(f.cl), h, fault or "none"))
    print("SAT_COUNT|ganak_total=%d|ganak_projected=%d|direct_no_cnf=%s|burnside=%d|recorded=%d|json=0"
          % (total, proj, d["lexmin_count"], burn, recorded))
    ok = total == proj == int(d["lexmin_count"]) == burn == recorded
    print("SAT_VERDICT|%s|json=0" % ("CERTIFIED" if ok else "NOT_CERTIFIED"))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
