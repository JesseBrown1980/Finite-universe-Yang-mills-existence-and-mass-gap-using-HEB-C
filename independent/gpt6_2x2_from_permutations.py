#!/usr/bin/env python3
"""Independent 2x2 finite S3 audit: all arithmetic is integers, no third-party modules.
Reconstructs the 1,393-space Hamiltonian WITHOUT importing the seat's builders.
Finite S3 verification only; NOT a continuum Yang-Mills mass-gap theorem.
"""
from itertools import permutations, product
from collections import Counter, deque
from hashlib import sha256
import sys

P = tuple(permutations(range(3)))
G = {p: i for i, p in enumerate(P)}
C = tuple(tuple(G[tuple(P[x][P[y][k]] for k in range(3))]
                for y in range(6)) for x in range(6))
I = tuple(next(y for y in range(6) if C[x][y] == C[y][x] == 0)
          for x in range(6))
assert all(C[x][I[x]] == 0 for x in range(6))
T = tuple(x for x in range(6) if C[x][x] == 0 and x != 0)
assert len(T) == 3

# Eight positive links on the periodic 2x2 spatial square.
EDGE = ((0, 2), (1, 3), (2, 0), (3, 1),
        (0, 1), (1, 0), (2, 3), (3, 2))
TREE = (0, 1, 4)
FREE = (2, 3, 5, 6, 7)


def multiply(*args):
    result = 0
    for x in args:
        result = C[result][x]
    return result


def number(q):
    return sum(int(x) * 6**k for k, x in enumerate(q))


def decode(n):
    return tuple((n // 6**k) % 6 for k in range(5))


def canonical(q):
    return min((tuple(C[C[g][x]][I[g]] for x in q)
                for g in range(6)), key=number)


def fixed(U):
    # Spanning-tree gauge fixing, then residual simultaneous conjugation.
    frames = [None] * 4
    frames[0] = 0
    for _ in range(3):
        for k in TREE:
            a, b = EDGE[k]
            if frames[a] is not None and frames[b] is None:
                frames[b] = C[frames[a]][U[k]]
            if frames[b] is not None and frames[a] is None:
                frames[a] = C[frames[b]][I[U[k]]]
    assert all(x is not None for x in frames)
    q = tuple(multiply(frames[EDGE[k][0]], U[k],
                       I[frames[EDGE[k][1]]]) for k in FREE)
    return canonical(q)


def expand(q):
    U = [0] * 8
    for k, x in zip(FREE, q):
        U[k] = x
    return U


# Exact orbit partition on all 6^5 gauge-fixed free-link assignments.
weights = {}
for q in product(range(6), repeat=5):
    key = number(canonical(q))
    weights[key] = weights.get(key, 0) + 1
keys = sorted(weights)
assert len(keys) == 1393
assert sum(weights.values()) == 6**5
assert set(weights.values()) <= {1, 2, 3, 6}
pos = {key: idx for idx, key in enumerate(keys)}


def chi(x):
    if x == 0:
        return 2
    if x in T:
        return 0
    return -1


def magnetic(U):
    total = 0
    for x in range(2):
        for y in range(2):
            at = 2*x + y
            right = 2*((x+1) % 2) + y
            above = 2*x + (y+1) % 2
            hol = multiply(U[at], U[4+right],
                           I[U[above]], I[U[4+at]])
            total += 2 - chi(hol)
    return total


rows = []
mag = []
for key in keys:
    U = expand(decode(key))
    assert number(fixed(U)) == key
    mag.append(magnetic(U))
    i = pos[key]
    row = Counter({i: 24})
    for edge in range(8):
        for t in T:
            V = U.copy()
            V[edge] = C[t][U[edge]]
            row[pos[number(fixed(V))]] -= 1
    rows.append({j: value for j, value in row.items() if value})

assert sum(map(len, rows)) == 32385
assert all(sum(row.values()) == 0 for row in rows)
assert all(all(value < 0 for j, value in row.items() if j != i)
           for i, row in enumerate(rows))
W = [weights[k] for k in keys]
assert all(W[i]*value == W[j]*rows[j].get(i, 0)
           for i, row in enumerate(rows) for j, value in row.items())
flat = [i for i, x in enumerate(mag) if x == 0]
assert len(flat) == 8
assert [keys[i] for i in flat] == [0, 7, 21, 1332, 1339, 3996, 4017, 4024]
assert all(rows[i].get(j, 0) == (24 if i == j else 0)
           for i in flat for j in flat)

# Check a nontrivial pure-electric eigenmode as a sanity control. The
# eigenmode alone does not prove the absence of spectrum below 6.
wilson = [chi(C[expand(decode(key))[0]][expand(decode(key))[2]])
          for key in keys]
assert sum(W[i]*wilson[i] for i in range(len(keys))) == 0
assert all(sum(value*wilson[j] for j, value in row.items()) == 6*wilson[i]
           for i, row in enumerate(rows))
assert min(mag[i] for i in range(len(keys)) if i not in flat) == 3
assert max(mag) == 12
assert max(row.get(i, 0) for i, row in enumerate(rows)) <= 24

# Second-order magnetic-end Schur matrix in integer arithmetic.
# 2520 is a common multiple of every nonzero magnetic eigenvalue.
SCALE = 2520
B = []
for i in flat:
    result = []
    for j in flat:
        total = 0
        for k, value in rows[i].items():
            if k in flat or j not in rows[k]:
                continue
            assert SCALE % mag[k] == 0
            total += value*rows[k][j]*(SCALE // mag[k])
        assert total % SCALE == 0
        result.append(-total // SCALE)
    B.append(result)

# Deliberate red control: corrupt one matrix entry when invoked with --tamper.
if sys.argv[1:] == ["--tamper"]:
    B[0][1] -= 1
elif sys.argv[1:]:
    raise SystemExit("unknown control argument")
assert all(W[i]*B[a][b] == W[j]*B[b][a]
           for a, i in enumerate(flat) for b, j in enumerate(flat))
assert all(B[a][a] == -6 for a in range(8))
corrupt = [row.copy() for row in B]
corrupt[0][1] -= 1
assert any(W[i]*corrupt[a][b] != W[j]*corrupt[b][a]
           for a, i in enumerate(flat) for b, j in enumerate(flat))


def matrix_product(A, D):
    return [[sum(A[i][k]*D[k][j] for k in range(8))
             for j in range(8)] for i in range(8)]


identity = [[int(i == j) for j in range(8)] for i in range(8)]
running = identity
coefficient = [1]
for k in range(1, 9):
    product_matrix = matrix_product(B, running)
    trace = sum(product_matrix[i][i] for i in range(8))
    assert trace % k == 0
    coeff = -trace // k
    coefficient.append(coeff)
    running = [[product_matrix[i][j] + coeff*identity[i][j]
                for j in range(8)] for i in range(8)]


def polymul(a, b):
    output = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            output[i+j] += x*y
    return output


expected = [1]
for _ in range(4):
    expected = polymul(expected, [1, 6])
expected = polymul(expected, [1, 12, 22])
expected = polymul(expected, [1, 12, 30])
assert coefficient == expected

# All-pairs BFS, rather than taking the claimed graph diameter from a receipt.
links = [tuple(j for j, value in row.items() if j != i and value < 0)
         for i, row in enumerate(rows)]
diameter = 0
for origin in range(len(rows)):
    distances = [-1]*len(rows)
    distances[origin] = 0
    queue = deque([origin])
    while queue:
        vertex = queue.popleft()
        for nxt in links[vertex]:
            if distances[nxt] == -1:
                distances[nxt] = distances[vertex]+1
                queue.append(nxt)
    assert -1 not in distances
    diameter = max(diameter, max(distances))
assert diameter == 8

# Exact native operator hash is a final cross-check, not an input to generation.
payload = bytearray(b"HEBC-S3-TORUS2-1393-V1")
for i, key in enumerate(keys):
    payload.extend(key.to_bytes(8, "little"))
    payload.extend(W[i].to_bytes(8, "little"))
    payload.extend(bytes(decode(key)))
    payload.extend(mag[i].to_bytes(8, "little", signed=True))
    payload.extend(len(rows[i]).to_bytes(8, "little"))
    for j, value in sorted(rows[i].items()):
        payload.extend(j.to_bytes(8, "little"))
        payload.extend(value.to_bytes(8, "little", signed=True))
operator_sha = sha256(payload).hexdigest()
assert operator_sha == "b6c608f50f81f3bf48fb0203b48e0e3bfc867037dc1d0a96633aa80b962137f3"

# Translate all eight links before redoing gauge fixing.
def translated(U, dx, dy):
    result = [0]*8
    for x in range(2):
        for y in range(2):
            start = 2*x+y
            target = 2*((x+dx) % 2)+((y+dy) % 2)
            result[start] = U[target]
            result[4+start] = U[4+target]
    return result


translation = {}
for dx, dy in product(range(2), repeat=2):
    perm = [pos[number(fixed(translated(expand(decode(k)), dx, dy)))]
            for k in keys]
    assert len(set(perm)) == len(keys)
    assert all(W[i] == W[j] and mag[i] == mag[j]
               for i, j in enumerate(perm))
    assert all(rows[perm[i]].get(perm[j], 0) == value
               for i, row in enumerate(rows) for j, value in row.items())
    translation[dx, dy] = perm

orbits = []
visited = set()
for i in range(len(keys)):
    if i in visited:
        continue
    orbit = {translation[dx, dy][i] for dx, dy in product(range(2), repeat=2)}
    assert visited.isdisjoint(orbit)
    visited.update(orbit)
    orbits.append(orbit)
assert len(orbits) == 385
assert Counter(map(len, orbits)) == {4: 319, 2: 51, 1: 15}

blockcounts = []
for sx, sy in product((1, -1), repeat=2):
    count = 0
    for orbit in orbits:
        first = min(orbit)
        signs = {}
        for dx, dy in product(range(2), repeat=2):
            translated_first = translation[dx, dy][first]
            sign = (sx if dx else 1)*(sy if dy else 1)
            if translated_first in signs and signs[translated_first] != sign:
                break
            signs[translated_first] = sign
        else:
            count += 1
    blockcounts.append(count)
assert blockcounts == [385, 336, 336, 336]

# Exact integer inequalities used by the near-magnetic Schur argument:
# sqrt(14)>37/10, sqrt(6)<5/2, error<=120/1249.
assert 37**2 < 14*100 and 5**2 > 6*4
assert (6*1249-240*5) > 5*1249

print("GPT6_INDEPENDENT_MODEL|lattice=2x2|group=S3|orbits=1393|electric_nnz=32385|flat=8|graph_diameter=8|trans_dim=385,336,336,336|result=PASS|json=0")
print("GPT6_INDEPENDENT_SHA|operator_sha256="+operator_sha+"|tamper_control=PASS|json=0")
print("GPT6_INDEPENDENT_B|weights="+",".join(str(W[i]) for i in flat)+"|PEP=24I8|weighted_symmetry=PASS|charpoly=(x+6)^4*(x^2+12x+22)*(x^2+12x+30)|result=PASS|json=0")
for i, row in enumerate(B):
    print("GPT6_INDEPENDENT_B_ROW|index="+str(i)+"|value="+",".join(map(str, row))+"|json=0")
print("GPT6_INDEPENDENT_THEOREM|small_s_error_le=120/1249|gap_gt=s^2|numeric_bound=CONDITIONAL_ON_SCHUR_IDENTITIES|json=0")
print("GPT6_SCOPE|finite_S3_2x2_only=1|continuous_SU2=OPEN|continuum_mass_gap=OPEN|json=0")
