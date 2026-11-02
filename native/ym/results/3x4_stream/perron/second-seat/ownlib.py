# Own reader and exact tools. Written from the format text in PERRON-REVIEW.md section 2, no code shared with the tools.
# Everything that decides a verdict is exact integer arithmetic.
import hashlib, struct, heapq

LEAF = 16 * 1048576


def read_store(path, offset=0):
    with open(path, "rb") as f:
        f.seek(offset)
        hdr = f.read(4096)
        line = hdr[: hdr.index(b"\n")].decode()
        fld = dict(x.split("=", 1) for x in line.split("|")[1:] if "=" in x)
        n, payload = int(fld["n"]), int(fld["payload_bytes"])
        data = f.read(payload)
    assert len(data) == payload
    shas = b"".join(hashlib.sha256(data[i : i + LEAF]).hexdigest().encode() for i in range(0, payload, LEAF))
    merkle_ok = hashlib.sha256(shas).hexdigest() == fld["payload_merkle"]
    rows = []
    p = 0
    for h in range(n):
        w, mag, cnt = struct.unpack_from("<IHH", data, p)
        p += 8
        ent = list(struct.iter_unpack("<Ii", data[p : p + 8 * cnt]))
        p += 8 * cnt
        rows.append((w, mag, ent))
    tail_zero = not any(data[p:])
    return fld, rows, merkle_ok, tail_zero


def audit(rows):
    """Exact audit of the structure: W-symmetry on every pair, row sums, signs, flats."""
    n = len(rows)
    bad_sym = bad_sum = pos_off = 0
    z = [dict(e) for _, _, e in rows]
    w = [r[0] for r in rows]
    for h, zh in enumerate(z):
        if sum(zh.values()) != 0:
            bad_sum += 1
        for j, v in zh.items():
            if j != h and v > 0:
                pos_off += 1
            if w[h] * v != w[j] * z[j].get(h, 0):
                bad_sym += 1
    flats = [h for h, r in enumerate(rows) if r[1] == 0]
    ff = sum(1 for h in flats for j in z[h] if j != h and rows[j][1] == 0)
    fdiag = [z[h].get(h, 0) for h in flats]
    return dict(n=n, bad_sym=bad_sym, bad_sum=bad_sum, pos_off=pos_off, flats=flats, flat_flat=ff, flat_diag=fdiag,
                min_nonflat_M=min(r[1] for r in rows if r[1] > 0), max_M=max(r[1] for r in rows))


def read_vec(path):
    with open(path, "rb") as f:
        b = f.read()
    return [x[0] for x in struct.iter_unpack("<q", b)]


def build(rows, je=1000, jb=9000):
    """Non-flat rows of H' in t_milli units. keep: store row -> index. Returns (keep list, W, M, E-rows as dict j->z)."""
    keep = [h for h, r in enumerate(rows) if r[1] != 0]
    idx = {h: i for i, h in enumerate(keep)}
    W = [rows[h][0] for h in keep]
    M = [rows[h][1] for h in keep]
    Z = []
    for h in keep:
        Z.append({idx[j]: v for j, v in rows[h][2] if j in idx})
    return keep, W, M, Z


def hp_rows(Z, M, je, jb):
    u, v = 1000 * je, 1000 * jb
    out = []
    for i, zi in enumerate(Z):
        r = {j: u * x for j, x in zi.items()}
        r[i] = r.get(i, 0) + v * M[i]
        out.append(r)
    return out


def barta(H, x):
    """min_i floor((Hx)_i / x_i) with the row; x must be positive; exact."""
    best = None
    for i, r in enumerate(H):
        if x[i] <= 0:
            raise ValueError(f"nonpositive at {i}")
        t = sum(v * x[j] for j, v in r.items())
        q = t // x[i]
        if best is None or q < best[0]:
            best = (q, i)
    return best


def barta_exact_num(H, x):
    """min_i (Hx)_i / x_i as an exact pair (num, den), with the row."""
    best = None
    for i, r in enumerate(H):
        t = sum(v * x[j] for j, v in r.items())
        if best is None or t * best[1] < best[0] * x[i]:
            best = (t, x[i], i)
    return best


def rayleigh(H, W, x):
    """(num, den) of <x,Hx>_W / <x,x>_W; exact."""
    a = g = 0
    for i, r in enumerate(H):
        t = sum(v * x[j] for j, v in r.items())
        a += W[i] * x[i] * t
        g += W[i] * x[i] * x[i]
    return a, g


def ceil_div(a, b):
    return -((-a) // b)


def inertia_bareiss(A):
    """Exact count of negative eigenvalues of a symmetric integer matrix by the signs of the leading principal minors.
    Fraction-free, symmetric half only. Returns (negatives, last_minor_sign), or raises ZeroDivisionError-like on a zero minor."""
    n = len(A)
    m = [list(A[i][i:]) for i in range(n)]  # row i holds columns i..n-1
    prev = 1
    neg = 0
    sign_prev = 1
    for k in range(n):
        p = m[k][0]
        if p == 0:
            if k == n - 1:
                return neg, 0, k
            raise ArithmeticError(f"zero leading minor at {k}")
        s = 1 if p > 0 else -1
        if s != sign_prev:
            neg += 1
        sign_prev = s
        rk = m[k]
        for i in range(k + 1, n):
            f = rk[i - k]
            ri = m[i]
            if f == 0:
                # (ri[j] * p - 0) / prev
                m[i] = [v * p // prev if v else 0 for v in ri]
            else:
                off = i - k
                m[i] = [(v * p - f * rk[off + c]) // prev for c, v in enumerate(ri)]
        prev = p
        m[k] = None
    return neg, sign_prev, n


def own_sparse_ldl(A, S=200):
    """Fixed-point LDL^T with greedy minimum degree. A: list of dict j->int, symmetric. Only used to PROPOSE vectors: the verdict is
    always an exact Barta or Rayleigh evaluation on the proposal. Returns (order, D, L) with L[p] = list of (i, l_ip scaled 2^S)."""
    n = len(A)
    S1 = 1 << S
    a = [{j: v << S for j, v in A[i].items()} for i in range(n)]
    done = [False] * n
    deg = [len(a[i]) for i in range(n)]
    heap = [(deg[i], i) for i in range(n)]
    heapq.heapify(heap)
    order = []
    D = [0] * n
    L = [None] * n
    ops = 0
    while heap:
        dg, p = heapq.heappop(heap)
        if done[p] or dg != len(a[p]):
            if not done[p]:
                heapq.heappush(heap, (len(a[p]), p))
            continue
        done[p] = True
        order.append(p)
        ap = a[p]
        d = ap.pop(p)
        if d <= 0:
            raise ArithmeticError(f"pivot not positive at {p} after {len(order)} steps")
        D[p] = d
        nb = list(ap.items())
        L[p] = [(i, (v << S) // d) for i, v in nb]
        for ii, (i, vi) in enumerate(nb):
            ai = a[i]
            del ai[p]
            for j, vj in nb[ii:]:
                t = vi * vj // d
                ai[j] = ai.get(j, 0) - t
                if j != i:
                    a[j][i] = a[j].get(i, 0) - t
                ops += 1
        for i, _ in nb:
            heapq.heappush(heap, (len(a[i]), i))
        a[p] = None
    return order, D, L, ops, S


def own_solve(fact, b, X):
    """Solves (L D L^T) x = b. b is scaled by 2^X; returns x scaled by 2^X, integer, rounded down at each step."""
    order, D, L, ops, S = fact
    y = list(b)
    for p in order:
        yp = y[p]
        for i, l in L[p]:
            y[i] -= (l * yp) >> S
    # y scaled 2^X; D scaled 2^S
    z = [0] * len(b)
    for p in order:
        z[p] = (y[p] << S) // D[p]
    for p in reversed(order):
        zp = z[p]
        for i, l in L[p]:
            zp -= (l * z[i]) >> S
        z[p] = zp
    return z
