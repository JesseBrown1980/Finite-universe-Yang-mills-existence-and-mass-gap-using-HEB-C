#!/usr/bin/env python3
"""Independent full 3x3 vacuum-ball Ritz calculation, integer-only.

Uses the published SHA-pinned raw matrix, but NOT the original seat's
Krylov builder, Bareiss inertia routine or eigenvalue outputs. Applies
H using outgoing graph rows and weighted reversibility, then calls the
separately authored GPT-6 outward-interval Schur inertia routine.
Ritz eigenvalues bound individual full Hamiltonian eigenvalues FROM ABOVE.
Their differences are NOT certificates of the full Hamiltonian gap.
"""
from pathlib import Path
from collections import defaultdict
from hashlib import sha256
from importlib.util import spec_from_file_location, module_from_spec

# -I excludes the script directory: resolve this authored companion module
# by a fixed path next to the verifier, not via user-controlled PYTHONPATH.
HERE = Path(__file__).resolve().parent
spec = spec_from_file_location("gpt6_interval_local", HERE / "gpt6_sturm_interval.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cannot locate independently written interval verifier")
module = module_from_spec(spec)
spec.loader.exec_module(module)
inertia = module.inertia
import sys

PINS = {
    "b33_k1.matrix": "a9de0a8c8f070b7ded4b158290dad6b8d97fc83aabb17e1fe64de62b89a17a40",
    "b33_k2.matrix": "82339f3d4bed2a311d2443d555ab65d7190f8d94ad7a6babb276c553b96e3ffe",
    "b33_k3.matrix": "d86a347ba16d00c73482400ea24d58be83d00d00811aa50dd994a661f2b2c866",
}

def parse(path):
    raw = path.read_bytes()
    name = path.name
    if name not in PINS or sha256(raw).hexdigest() != PINS[name]:
        raise ValueError("unknown or modified 3x3 matrix digest")
    tokens = tuple(map(int, raw.split()))
    n = tokens[0]
    weights = tokens[1:1+n]
    mag = tokens[1+n:1+2*n]
    rest = tokens[1+2*n:]
    if len(rest) % 3 or any(x <= 0 for x in weights):
        raise ValueError("invalid matrix file")
    rows = [dict() for _ in range(n)]
    coords = set()
    for i, j, value in zip(rest[0::3], rest[1::3], rest[2::3]):
        if not 0 <= i <= j < n or (i,j) in coords:
            raise ValueError("duplicate or invalid coordinate")
        coords.add((i,j))
        if value:
            rows[i][j] = value
            if i != j:
                num = weights[i] * value
                if num % weights[j]:
                    raise ValueError("nonintegral weighted reverse edge")
                rows[j][i] = num // weights[j]
    if any(any(weights[i]*z != weights[j]*rows[j].get(i,0)
                   for j,z in row.items()) for i,row in enumerate(rows)):
        raise ValueError("failure of weighted Hermiticity")
    return n, weights, mag, rows

def propagate(rows, weights, mag, vector, je, jb):
    out = defaultdict(int)
    for source, value in vector.items():
        if not value:
            continue
        wj = weights[source]
        for target, zji in rows[source].items():
            num = 24*je*wj*zji*value
            if num % weights[target]:
                raise ArithmeticError("weighted reverse action mismatch")
            out[target] += num // weights[target]
        out[source] += 24*jb*mag[source]*value
    return {i: v for i, v in out.items() if v}

def dot(weights, one, two):
    if len(one) > len(two):
        one, two = two, one
    return sum(weights[i]*value*two.get(i,0) for i,value in one.items())

def ritz_matrices(path, je, jb, order):
    n, weights, mag, rows = parse(path)
    flats = [i for i, x in enumerate(mag) if x == 0]
    assert len(flats) == 8
    basis = [{i: 1} for i in flats]
    previous = basis
    for _ in range(order):
        previous = [propagate(rows,weights,mag,v,je,jb) for v in previous]
        basis.extend(previous)
    applied = [propagate(rows,weights,mag,v,je,jb) for v in basis]
    N = len(basis)
    gram = [[dot(weights,x,y) for y in basis] for x in basis]
    energy = [[dot(weights,x,y) for y in applied] for x in basis]
    assert all(gram[i][j] == gram[j][i] and energy[i][j] == energy[j][i]
               for i in range(N) for j in range(N))
    return n,gram,energy

def negative_of(matrix):
    return inertia([{j: (x*10**50,x*10**50) for j,x in enumerate(row) if x}
                    for row in matrix])[0]

def bracket(gram,energy,level):
    n=len(gram)
    # energy matrix is 24 * H in our exact rational coordinates.
    def negative(t):
        shifted=[[10**6*energy[i][j] - t*gram[i][j]
                  for j in range(n)] for i in range(n)]
        return negative_of(shifted)
    lo, hi = 0, 4800*10**6
    assert negative(lo) <= level < negative(hi)
    while hi - lo > 1:
        mid=(lo+hi)//2
        if negative(mid) <= level:
            lo=mid
        else:
            hi=mid
    # Convert the strict t enclosure into an outward-rounded bound on
    # the Ritz eigenvalue in millionths: floor at low, CEIL at high.
    return lo//24, (hi+23)//24

def main(path,je,jb,order):
    n,gram,energy=ritz_matrices(path,je,jb,order)
    assert negative_of(gram)==0
    energies=[bracket(gram,energy,k) for k in range(8)]
    assert all(energies[i][0] <= energies[i+1][1] for i in range(7))
    trial_gap_lo=energies[1][0]-energies[0][1]
    trial_gap_hi=energies[1][1]-energies[0][0]
    print("GPT6_3X3_RITZ|matrix=%s|states=%d|JE=%d|JB=%d|order=%d|dim=%d|"
          "ritz_e0_micro=%d..%d|ritz_e1_micro=%d..%d|ritz_gap_micro=%d..%d|"
          "full_gap=NOT_CERTIFIED|method=INTEGER_INTERVAL_LDL|json=0" %
          (path.name,n,je,jb,order,len(gram),
           *energies[0],*energies[1],trial_gap_lo,trial_gap_hi))

if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit("usage: gpt6_3x3_ritz_independent.py MATRIX JE JB ORDER")
    main(Path(sys.argv[1]), *map(int,sys.argv[2:]))
