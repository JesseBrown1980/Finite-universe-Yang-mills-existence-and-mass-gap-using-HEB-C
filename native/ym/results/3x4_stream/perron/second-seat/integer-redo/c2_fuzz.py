# Integer-only copy of second-seat/c2_fuzz.py, made on the operator's word that floating point is to be redone in integers. The original stays beside it as evidence.
# C2: random synthetic stores run through the pinned binaries, compared with exact forms and an exact smallest root found by a Sturm chain,
# which shares no logic with the tool's elimination. usage: c2_fuzz.py SEED TRIALS
import hashlib, math, os, random, struct, subprocess, sys, time
from fractions import Fraction as F

R = "C:/tmp/opus55/ym-two-sided"
TOOLS = [f"{R}/bin/perronritz-grid.exe", f"{R}/bin/perronritz.exe"]
seed, trials = int(sys.argv[1]), int(sys.argv[2])
rng = random.Random(seed)
tmp = f"{R}/tmpfuzz{seed}"
os.makedirs(tmp, exist_ok=True)
LEAF = 16 * 1048576


def write_store(path, rows):
    payload = bytearray()
    for w, mag, ent in rows:
        payload += struct.pack("<IHH", w, mag, len(ent))
        for j, z in ent:
            payload += struct.pack("<Ii", j, z)
    shas = "".join(hashlib.sha256(bytes(payload[i : i + LEAF])).hexdigest() for i in range(0, len(payload), LEAF))
    line = f"YMROOMHDR|L=1x{len(rows)}|sector=Sx+Sy+|n={len(rows)}|payload_bytes={len(payload)}|payload_merkle={hashlib.sha256(shas.encode()).hexdigest()}|w_self_adjoint=PASS|json=0\n"
    b = line.encode()
    with open(path, "wb") as f:
        f.write(b + bytes(4096 - len(b)) + bytes(payload))


def wv(path, v):
    with open(path, "wb") as f:
        f.write(b"".join(struct.pack("<q", x) for x in v))


def fields(line):
    return dict(x.split("=", 1) for x in line.strip().split("|")[1:] if "=" in x)


# --- polynomial tools, exact ---
def det_poly(A, G):
    """Coefficients (low first) of det(A - x G) by interpolation at k+1 integer points, exact rationals."""
    k = len(A)
    xs = list(range(k + 1))
    ys = []
    for x in xs:
        m = [[F(A[i][j] - x * G[i][j]) for j in range(k)] for i in range(k)]
        d = F(1)
        for c in range(k):
            pi = next((i for i in range(c, k) if m[i][c] != 0), None)
            if pi is None:
                d = F(0)
                break
            if pi != c:
                m[c], m[pi] = m[pi], m[c]
                d = -d
            d *= m[c][c]
            for i in range(c + 1, k):
                f = m[i][c] / m[c][c]
                if f:
                    m[i] = [a - f * b for a, b in zip(m[i], m[c])]
        ys.append(d)
    # Newton interpolation to monomial coefficients
    coef = [F(0)] * (k + 1)
    for i in range(k + 1):
        # Lagrange basis
        basis = [F(1)]
        den = F(1)
        for j in range(k + 1):
            if j != i:
                den *= xs[i] - xs[j]
                basis = [F(0)] + basis  # multiply by x
                for t in range(len(basis) - 1):
                    basis[t] += basis[t + 1] * (-xs[j])
        for t in range(k + 1):
            coef[t] += ys[i] * basis[t] / den
    return coef


def strip(p):
    p = list(p)
    while p and p[-1] == 0:
        p.pop()
    return p


def pmod(a, b):
    a = strip(a)
    b = strip(b)
    while len(a) >= len(b):
        q = a[-1] / b[-1]
        off = len(a) - len(b)
        for i, v in enumerate(b):
            a[i + off] -= q * v
        a.pop()
        a = strip(a) if not a or a[-1] == 0 else a
    return a


def deriv(p):
    return [i * p[i] for i in range(1, len(p))]


def sturm(p):
    p = strip(p)
    chain = [p, deriv(p)]
    while strip(chain[-1]) and len(strip(chain[-1])) > 1:
        r = pmod(chain[-2], chain[-1])
        if not strip(r):
            break
        chain.append([-x for x in r])
    return [strip(c) for c in chain if strip(c)]


def val(p, x):
    s = F(0)
    for c in reversed(p):
        s = s * x + c
    return s


def sc(chain, x):
    signs = [val(c, x) for c in chain]
    signs = [s for s in signs if s != 0]
    return sum(1 for a, b in zip(signs, signs[1:]) if (a > 0) != (b > 0))


def smallest_root_ceil(A, G):
    """Least integer t with at least one root of det(A - x G) at or below t. Uses square-free Sturm: counts distinct roots in (lo, t]."""
    p = det_poly(A, G)
    chain = sturm(p)
    hi = 1
    while sc(chain, F(-hi)) != sc(chain, F(hi)) and False:
        pass
    bound = 1 + max(abs(c) for c in strip(p)) / abs(strip(p)[-1])  # Cauchy
    lo = -math.ceil(bound)
    hi = math.ceil(bound)
    # roots in (lo, t] = V(lo) - V(t)
    Vlo = sc(chain, F(lo))
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if Vlo - sc(chain, F(mid)) >= 1:
            hi = mid
        else:
            lo = mid
    return hi


def pd_exact(M):
    n = len(M)
    m = [[F(x) for x in r] for r in M]
    for c in range(n):
        if m[c][c] <= 0:
            return False
        for i in range(c + 1, n):
            f = m[i][c] / m[c][c]
            if f:
                m[i] = [a - f * b for a, b in zip(m[i], m[c])]
    return True


def rank_exact(M):
    n = len(M)
    m = [[F(x) for x in r] for r in M]
    rk = 0
    for c in range(n):
        p = next((i for i in range(rk, n) if m[i][c] != 0), None)
        if p is None:
            continue
        m[rk], m[p] = m[p], m[rk]
        for i in range(rk + 1, n):
            f = m[i][c] / m[rk][c]
            if f:
                m[i] = [a - f * b for a, b in zip(m[i], m[rk])]
        rk += 1
    return rk


def gen_case():
    n = rng.randint(2, 11)
    nflat = rng.randint(0, 2) if n > 3 else 0
    flat = set(rng.sample(range(n), nflat))
    # Weights with an lcm so that z_ij = -c L / w_i is an integer and w_i z_ij = -c L symmetric
    pool = rng.choice([[1], [1, 2, 3, 4, 6, 12], [1, 2, 4, 8, 16, 32, 48, 96], [5, 7, 35]])
    w = [rng.choice(pool) for _ in range(n)]
    L = 1
    for x in w:
        L = L * x // math.gcd(L, x)
    z = [dict() for _ in range(n)]
    cmax = rng.choice([1, 3, 12, 500])
    for i in range(n):
        for j in range(i + 1, n):
            if rng.randrange(10) < rng.choice([3, 6, 10]):
                c = rng.randint(1, cmax)
                z[i][j] = -c * L // w[i]
                z[j][i] = -c * L // w[j]
    mode = rng.choice(["rowsum", "rowsum", "free", "negdiag"])
    for i in range(n):
        off = -sum(z[i].values())
        if mode == "rowsum":
            z[i][i] = off
        elif mode == "free":
            z[i][i] = off + rng.randint(0, 50)
        else:
            z[i][i] = off - rng.randint(0, 90)
    M = [0 if i in flat else rng.randint(1, 36) for i in range(n)]
    rows = [(w[i], M[i], sorted((j, v) for j, v in z[i].items())) for i in range(n)]
    k = rng.randint(1, 4)
    sz = rng.choice([3, 10, 1000, 10**6, 10**12, 10**15])
    ds = []
    kind = rng.choice(["positive", "mixed", "dep", "near", "zero", "eigen"])
    for a in range(k):
        v = []
        for i in range(n):
            if i in flat:
                v.append(0)
            elif kind == "mixed":
                v.append(rng.randint(-sz, sz))
            else:
                v.append(rng.randint(1, sz))
        ds.append(v)
    if kind == "dep" and k >= 2:
        ds[1] = [x * rng.randint(1, 3) for x in ds[0]]
    if kind == "near" and k >= 2:
        ds[1] = [x * 1000 + (rng.randint(-1, 1) if i not in flat else 0) for i, x in enumerate(ds[0])]
        ds[1] = [x if i not in flat else 0 for i, x in enumerate(ds[1])]
    if kind == "zero":
        ds[k - 1] = [0] * n
    je = rng.choice([1000, 1000, 1, 7, 3000])
    jbs = rng.sample([0, 1, 777, 4000, 6000, 9000, 27000, 243000], rng.randint(1, 3))
    return n, flat, w, M, z, rows, ds, je, jbs


stats = dict(cases=0, form_mismatch=0, upper_rows=0, upper_mismatch=0, open_rows=0, open_mismatch=0, unsound=0, not_least_negative=0, lower_rows=0, lower_mismatch=0, old_new_differ=0, refused=0)
t0 = time.time_ns()
for trial in range(trials):
    n, flat, w, M, z, rows, ds, je, jbs = gen_case()
    store = f"{tmp}/s.bin"
    write_store(store, rows)
    paths = []
    for i, v in enumerate(ds):
        p = f"{tmp}/d{i}.bin"
        wv(p, v)
        paths.append(p)
    args = ["pass", store, "0", str(je), ",".join(map(str, jbs))] + paths
    out = subprocess.run([TOOLS[0]] + args, capture_output=True, text=True).stdout.strip().splitlines()
    if trial % 7 == 0:
        out2 = subprocess.run([TOOLS[1]] + args, capture_output=True, text=True).stdout.strip().splitlines()
        if [l for l in out if not l.startswith("PERRONRITZ|")] != [l for l in out2 if not l.startswith("PERRONRITZ|")]:
            stats["old_new_differ"] += 1
    stats["cases"] += 1
    if not out or out[-1].startswith("PERRONRITZ_ERROR"):
        stats["refused"] += 1
        msg = out[-1] if out else "EMPTY"
        if "self-adjoint" in msg or "positive off" in msg or "flat rows" in msg:
            print("UNEXPECTED_REFUSAL", msg)
        continue
    k = len(ds)
    # exact forms by my own loops
    nf = [i for i in range(n) if i not in flat]
    G = [[sum(w[h] * ds[a][h] * ds[b][h] for h in nf) for b in range(k)] for a in range(k)]
    E = [[sum(w[h] * ds[a][h] * sum(v * ds[b][j] for j, v in z[h].items()) for h in nf) for b in range(k)] for a in range(k)]
    Mf = [[sum(w[h] * M[h] * ds[a][h] * ds[b][h] for h in nf) for b in range(k)] for a in range(k)]
    for l in out:
        if l.startswith("PERRONRITZ_FORM|"):
            f = fields(l)
            a, b = int(f["a"]), int(f["b"])
            if (int(f["G"]), int(f["E"]), int(f["M"])) != (G[a][b], E[a][b], Mf[a][b]):
                stats["form_mismatch"] += 1
                print("FORM_MISMATCH", trial, f, G[a][b], E[a][b], Mf[a][b])
    for l in out:
        if l.startswith("PERRONRITZ_UPPER|"):
            f = fields(l)
            jb = int(f["JB"])
            pick = [int(x) for x in f["vectors"].split("+")]
            u, v = 1000 * je, 1000 * jb
            Am = [[u * E[x][y] + v * Mf[x][y] for y in pick] for x in pick]
            Gm = [[G[x][y] for y in pick] for x in pick]
            singular = rank_exact(Gm) < len(pick)
            if "result" in f:
                stats["open_rows"] += 1
                if not singular:
                    stats["open_mismatch"] += 1
                    print("OPEN_BUT_INDEPENDENT", trial, l)
                continue
            stats["upper_rows"] += 1
            if singular:
                stats["open_mismatch"] += 1
                print("VALUE_BUT_DEPENDENT", trial, l)
                continue
            printed = int(f["upper_milli"])
            mine = smallest_root_ceil(Am, Gm)
            if printed != mine:
                if printed == 0 and mine < 0:
                    stats["not_least_negative"] += 1
                else:
                    stats["upper_mismatch"] += 1
                    print("UPPER_MISMATCH", trial, l, mine)
            # Soundness against the whole matrix: H' - printed must not be positive definite (exact, W-symmetrised).
            nn = len(nf)
            Hw = [[0] * nn for _ in range(nn)]
            pos = {h: i for i, h in enumerate(nf)}
            for h in nf:
                for j, zv in z[h].items():
                    if j in pos:
                        Hw[pos[h]][pos[j]] += w[h] * u * zv
                Hw[pos[h]][pos[h]] += w[h] * v * M[h] - w[h] * printed
            if pd_exact(Hw):
                stats["unsound"] += 1
                print("UNSOUND", trial, l)
        elif l.startswith("PERRONRITZ_LOWER|"):
            f = fields(l)
            jb = int(f["JB"])
            i = int(f["vector"])
            u, v = 1000 * je, 1000 * jb
            d = ds[i]
            best = None
            for h in nf:
                t = v * M[h] * d[h] + u * sum(zv * d[j] for j, zv in z[h].items())
                q = t // d[h]
                if best is None or q < best:
                    best = q
            stats["lower_rows"] += 1
            if best != int(f["t_cert_milli"]):
                stats["lower_mismatch"] += 1
                print("LOWER_MISMATCH", trial, l, best)
print(f"C2_FUZZ|seed={seed}|{stats}|secs_wall={(time.time_ns()-t0)//10**9}|json=0")
