# Integer-only copy of second-seat/c3_random.py, made on the operator's word that floating point is to be redone in integers. The original stays beside it as evidence.
# C3: exact-rational attack on the divided-difference identities and on monotonicity of the value, on random Z-matrices.
# Non-symmetric, reducible and symmetric matrices, any order of thresholds, t_k above and below mu, uniform and random sources.
import random, sys, itertools, time
from fractions import Fraction as F

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 27
trials = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
rng = random.Random(seed)


def minors_positive(A):
    n = len(A)
    m = [row[:] for row in A]
    for k in range(n):
        p = m[k][k]
        if p <= 0:
            return False
        for i in range(k + 1, n):
            f = m[i][k] / p
            if f:
                for j in range(k, n):
                    m[i][j] -= f * m[k][j]
    return True


def minors_nonneg_shift(H, t):
    """t <= perron level of the Z-matrix H: H - t + eps is an M-matrix for every eps > 0; test with exact rational eps small."""
    n = len(H)
    eps = F(1, 10**30)
    return minors_positive([[H[i][j] - (t - eps if i == j else 0) for j in range(n)] for i in range(n)])


def solve(A, b):
    n = len(A)
    m = [A[i][:] + [b[i]] for i in range(n)]
    for k in range(n):
        piv = next(i for i in range(k, n) if m[i][k] != 0)
        m[k], m[piv] = m[piv], m[k]
        for i in range(n):
            if i != k and m[i][k] != 0:
                f = m[i][k] / m[k][k]
                m[i] = [x - f * y for x, y in zip(m[i], m[k])]
    return [m[i][n] / m[i][i] for i in range(n)]


def shift(H, t):
    n = len(H)
    return [[H[i][j] - (t if i == j else 0) for j in range(n)] for i in range(n)]


def value(H, x):
    n = len(H)
    return min(sum(H[i][j] * x[j] for j in range(n)) / x[i] for i in range(n))


def apply_h(H, x):
    n = len(H)
    return [sum(H[i][j] * x[j] for j in range(n)) for i in range(n)]


def random_z(n, kind):
    H = [[F(0)] * n for _ in range(n)]
    if kind == "sym_w":
        w = [F(rng.randint(1, 96)) for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if rng.randrange(2) == 0:
                    v = F(rng.randint(1, 12))  # w_i z_ij = w_j z_ji = -v
                    H[i][j] = -v / w[i]
                    H[j][i] = -v / w[j]
            H[i][i] = F(rng.randint(1, 80))
    elif kind == "reducible":
        cut = rng.randint(1, n - 1)
        for i in range(n):
            for j in range(n):
                if i != j and (i < cut) == (j < cut) and rng.randrange(10) < 6:
                    H[i][j] = -F(rng.randint(1, 9), rng.randint(1, 5))
            H[i][i] = F(rng.randint(1, 80), rng.randint(1, 3))
    else:
        for i in range(n):
            for j in range(n):
                if i != j and rng.randrange(10) < 6:
                    H[i][j] = -F(rng.randint(1, 9), rng.randint(1, 5))
            H[i][i] = F(rng.randint(1, 80), rng.randint(1, 3))
    return H


def level_bracket(H):
    """Bisection on rationals for the Perron level by the M-matrix test: returns lo < level <= hi, hi - lo small."""
    n = len(H)
    lo = min(H[i][i] for i in range(n)) - sum(abs(H[i][j]) for i in range(n) for j in range(n)) - 1
    hi = max(H[i][i] for i in range(n)) + 1
    while not minors_positive(shift(H, lo)):
        lo -= 100
    for _ in range(40):
        mid = (lo + hi) / 2
        if minors_positive(shift(H, mid)):
            lo = mid
        else:
            hi = mid
    return lo, hi


stats = dict(cases=0, chains=0, id_fail=0, pos_fail=0, eq_fail=0, mono_fail=0, above_level=0, tk_below_mu=0, tk_above_mu=0, min_slack=None)
t0 = time.time_ns()
for trial in range(trials):
    n = rng.randint(2, 6)
    kind = rng.choice(["general", "reducible", "sym_w"])
    H = random_z(n, kind)
    lo, hi = level_bracket(H)
    k = rng.randint(2, 4)
    # thresholds: below the level, some close to it
    span = max(F(1), hi - min(H[i][i] for i in range(n)) + 5)
    ts = set()
    while len(ts) < k:
        ts.add(lo - span * F(rng.randint(1, 1000), 1000) ** rng.randint(1, 4))
    ts = list(ts)
    rng.shuffle(ts)
    src = [F(1)] * n if rng.randrange(2) == 0 else [F(rng.randint(1, 50)) for _ in range(n)]
    ds = [solve(shift(H, t), src) for t in ts]
    stats["cases"] += 1

    def dd(sub):
        out = [F(0)] * n
        for i in sub:
            den = F(1)
            for j in sub:
                if j != i:
                    den *= ts[i] - ts[j]
            for h in range(n):
                out[h] += ds[i][h] / den
        return out

    # Every ordering of the thresholds: the chain is X_{p1}, X_{p1 p2}, ...
    for perm in itertools.permutations(range(k)):
        prev = src
        prev_val = value(H, src)
        chain = []
        for m in range(1, k + 1):
            sub = perm[:m]
            x = dd(sub)
            # Identity 1: (H - t_last) X_m = X_{m-1}
            lhs = apply_h(shift(H, ts[perm[m - 1]]), x)
            if lhs != prev:
                stats["eq_fail"] += 1
            # Identity 2: X_m = R(t_p1) ... R(t_pm) s, computed by chained solves
            y = src
            for idx in sub:
                y = solve(shift(H, ts[idx]), y)
            if y != x:
                stats["id_fail"] += 1
            if min(x) <= 0:
                stats["pos_fail"] += 1
                break
            val = value(H, x)
            stats["chains"] += 1
            slack = val - prev_val
            if stats["min_slack"] is None or slack < stats["min_slack"]:
                stats["min_slack"] = slack
            if slack < 0:
                stats["mono_fail"] += 1
                print("MONO_FAIL", kind, H, ts, perm, m, str(prev_val), str(val))
            if ts[perm[m - 1]] < prev_val:
                stats["tk_below_mu"] += 1
            else:
                stats["tk_above_mu"] += 1
            if not minors_nonneg_shift(H, val):
                stats["above_level"] += 1
                print("ABOVE_LEVEL", kind, H, ts, perm, m)
            prev, prev_val = x, val
print({k: (str(v) if isinstance(v, F) else v) for k, v in stats.items()}, f"secs={(time.time_ns()-t0)//10**9}")
