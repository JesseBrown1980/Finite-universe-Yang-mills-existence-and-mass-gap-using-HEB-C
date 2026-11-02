# C6: my own build of the whole gauge-invariant space on small periodic lattices, sharing no code with ymroom, ball, or verify_sample_rows.
# My own comb tree and canonical form. The store's key is decoded only to align rows, and every aligned row is then compared in full.
# usage: c6_lattice.py LX LY
import itertools, pickle, random, struct, sys, time
sys.path.insert(0, "C:/tmp/opus55/ym-two-sided")
from ownlib import read_store, read_vec, hp_rows, build, barta, ceil_div

LX, LY = int(sys.argv[1]), int(sys.argv[2])
R = "C:/tmp/opus55/ym-two-sided"
DEV = f"{R}/dev{LX}{LY}.bin"
PASSA = f"D:/ym-3x4-room-run/p0-ball/small/{LX}x{LY}/passa.bin"
t0 = time.time()

P = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
I = {p: i for i, p in enumerate(P)}
MUL = [[I[tuple(a[b[k]] for k in range(3))] for b in P] for a in P]
E = I[(0, 1, 2)]
INV = [next(j for j in range(6) if MUL[i][j] == E) for i in range(6)]
TR = [i for i, p in enumerate(P) if sum(p[k] == k for k in range(3)) == 1]
COST = [0] * 6
for i, p in enumerate(P):
    fixed = sum(p[k] == k for k in range(3))
    COST[i] = 2 - (fixed - 1)
assert sorted(COST) == [0, 2, 2, 2, 3, 3] and len(TR) == 3
CONJ = [[MUL[MUL[g][v]][INV[g]] for v in range(6)] for g in range(6)]

V = LX * LY
nl = 2 * V


def s(x, y):
    return (x % LX) + LX * (y % LY)  # my site numbering differs from the store's


def hl(x, y):
    return s(x, y)


def vl(x, y):
    return V + s(x, y)


ends = {}
for x in range(LX):
    for y in range(LY):
        ends[hl(x, y)] = (s(x, y), s(x + 1, y))
        ends[vl(x, y)] = (s(x, y), s(x, y + 1))
plaq = [(hl(x, y), vl(x + 1, y), hl(x, y + 1), vl(x, y)) for x in range(LX) for y in range(LY)]
# My tree: the bottom row of horizontal links, then all vertical links but the last in each column.
tree = [hl(x, 0) for x in range(LX - 1)] + [vl(x, y) for x in range(LX) for y in range(LY - 1)]
tree_set = set(tree)
assert len(tree) == V - 1
free = [l for l in range(nl) if l not in tree_set]
# site order so that each new site hangs off a known one
steps = []
known = {s(0, 0)}
for l in tree:
    a, b = ends[l]
    assert a in known and b not in known
    steps.append((a, b, l))
    known.add(b)


def magnetic(u):
    m = 0
    for a, b, c, d in plaq:
        m += COST[MUL[MUL[MUL[u[a]][u[b]]][INV[u[c]]]][INV[u[d]]]]
    return m


def canon(u):
    """Gauge orbit of a full link assignment: gauge-fix on my tree, then least code over global conjugation."""
    g = [E] * V
    for a, b, l in steps:
        g[b] = MUL[g[a]][u[l]]
    q = [MUL[MUL[g[ends[l][0]]][u[l]]][INV[g[ends[l][1]]]] for l in free]
    best = None
    for c in CONJ:
        code = 0
        for v in q:
            code = code * 6 + c[v]
        if best is None or code < best:
            best = code
    return best


def links_of(code):
    u = [E] * nl
    for l in reversed(free):
        u[l] = code % 6
        code //= 6
    return u


# 1. Whole-space orbits, enumerating every gauge-fixed configuration.
nfree = len(free)
sizes = {}
for tup in itertools.product(range(6), repeat=nfree):
    u = [E] * nl
    for l, v in zip(free, tup):
        u[l] = v
    c = canon(u)
    sizes[c] = sizes.get(c, 0) + 1
codes = sorted(sizes)
idx = {c: i for i, c in enumerate(codes)}
n = len(codes)
W = [sizes[c] for c in codes]
print(f"WHOLE|L={LX}x{LY}|nl={nl}|gauge_fixed_configs={6**nfree}|orbits={n}|sum_w={sum(W)}|secs_wall={time.time()-t0:.0f}|json=0", flush=True)
assert sum(W) == 6**nfree
Mw = [magnetic(links_of(c)) for c in codes]
flats = [i for i in range(n) if Mw[i] == 0]
print(f"WHOLE_M|flats={len(flats)}|min_nonflat_M={min(m for m in Mw if m)}|max_M={max(Mw)}|values={sorted(set(Mw))}|json=0", flush=True)

# 2. Whole-space rows: one -1 per move; diagonal 3 nl minus the moves back to the same orbit.
rows = []
for i, c in enumerate(codes):
    u = links_of(c)
    z = {}
    for l in range(nl):
        old = u[l]
        for t in TR:
            u[l] = MUL[t][old]
            j = idx[canon(u)]
            z[j] = z.get(j, 0) - 1
        u[l] = old
    back = -z.pop(i, 0)
    z[i] = 3 * nl - back
    rows.append(z)
print(f"WHOLE_ROWS|built|secs_wall={time.time()-t0:.0f}|json=0", flush=True)
bad_sym = sum(1 for i, z in enumerate(rows) for j, v in z.items() if W[i] * v != W[j] * rows[j].get(i, 0))
bad_sum = sum(1 for z in rows if sum(z.values()) != 0)
flat_diag = sorted(rows[f][f] for f in flats)
ff = sum(1 for f in flats for j in rows[f] if j != f and Mw[j] == 0)
print(f"WHOLE_AUDIT|W_symmetry_bad_pairs={bad_sym}|row_sum_bad={bad_sum}|flat_diag={flat_diag}|flat_flat_couplings={ff}|json=0", flush=True)


# 3. Lattice symmetry, by generators: two translations, two reflections. A reflected link is the forward link one step back, inverted.
def apply_op(u, op):
    out = [E] * nl
    for x in range(LX):
        for y in range(LY):
            uh, uv = u[hl(x, y)], u[vl(x, y)]
            if op == "tx":
                out[hl(x + 1, y)], out[vl(x + 1, y)] = uh, uv
            elif op == "ty":
                out[hl(x, y + 1)], out[vl(x, y + 1)] = uh, uv
            elif op == "rx":
                out[hl(-x - 1, y)] = INV[uh]
                out[vl(-x, y)] = uv
            elif op == "ry":
                out[hl(x, -y)] = uh
                out[vl(x, -y - 1)] = INV[uv]
    return out


parent = list(range(n))


def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a


for i, c in enumerate(codes):
    u = links_of(c)
    for op in ("tx", "ty", "rx", "ry"):
        j = idx[canon(apply_op(u, op))]
        ra, rb = find(i), find(j)
        if ra != rb:
            parent[ra] = rb
cls = [find(i) for i in range(n)]
classes = sorted(set(cls))
print(f"SECTOR_QUOTIENT|classes={len(classes)}|secs_wall={time.time()-t0:.0f}|json=0", flush=True)

# Symmetry preserves M and W-preserves structure: exact checks at the whole-space level.
mbad = sum(1 for i in range(n) if Mw[i] != Mw[cls[i]])
print(f"G_PRESERVES_M|bad={mbad}|json=0", flush=True)

# 4. Align with the store by decoding its key (their tree and link numbering, used here only to name a config).
fld, srows, ok, _ = read_store(DEV)
sn = len(srows)
with open(PASSA, "rb") as f:
    pa = f.read()
keys = [struct.unpack_from("<QII", pa, 16 * h) for h in range(sn)]


def their_site(x, y):
    return (x % LX) * LY + (y % LY)


their_tree = {V + their_site(0, y) for y in range(LY - 1)} | {their_site(x, y) for x in range(LX - 1) for y in range(LY)}
their_free = [l for l in range(nl) if l not in their_tree]
def their_to_mine(l):
    if l < V:
        site = l
        x, y = site // LY, site % LY
        return hl(x, y)
    site = l - V
    x, y = site // LY, site % LY
    return vl(x, y)


cl_of_row = []
for h in range(sn):
    key = keys[h][0]
    u = [E] * nl
    for l in their_free:
        u[their_to_mine(l)] = key % 6
        key //= 6
    cl_of_row.append(cls[idx[canon(u)]])
print(f"ALIGN|store_rows={sn}|distinct_classes_hit={len(set(cl_of_row))}|classes={len(classes)}|json=0", flush=True)
row_of_cl = {c: h for h, c in enumerate(cl_of_row)}

# Sector rows rebuilt from my whole-space rows, compared in full with the store.
mism_w = mism_m = mism_e = 0
members = {}
for i in range(n):
    members.setdefault(cls[i], []).append(i)
my_sector = {}
for c, mem in members.items():
    w = sum(W[i] for i in mem)
    rep = mem[0]
    z = {}
    for j, v in rows[rep].items():
        if j == rep:
            continue
        z[row_of_cl[cls[j]]] = z.get(row_of_cl[cls[j]], 0) + v
    h = row_of_cl[c]
    back = -z.pop(h, 0)
    z[h] = rows[rep][rep] - back
    my_sector[h] = (w, Mw[rep], z)
    sw, sm, se = srows[h]
    if sw != w:
        mism_w += 1
    if sm != Mw[rep]:
        mism_m += 1
    if dict(se) != {j: v for j, v in z.items() if v != 0} and {j: v for j, v in dict(se).items() if v != 0} != {j: v for j, v in z.items() if v != 0}:
        mism_e += 1
print(f"SECTOR_ROWS_MATCH|rows={sn}|weight_mismatch={mism_w}|M_mismatch={mism_m}|entries_mismatch={mism_e}|json=0", flush=True)
# the rows of every member of a class, not only the rep, must give the same sector row: checks the group action on moves
rep_bad = 0
for c, mem in members.items():
    h = row_of_cl[c]
    target = {j: v for j, v in my_sector[h][2].items() if v != 0}
    for i in mem[1:]:
        z = {}
        for j, v in rows[i].items():
            if j == i:
                continue
            z[row_of_cl[cls[j]]] = z.get(row_of_cl[cls[j]], 0) + v
        back = -z.pop(h, 0)
        z[h] = rows[i][i] - back
        if {j: v for j, v in z.items() if v != 0} != target:
            rep_bad += 1
print(f"EVERY_MEMBER_GIVES_THE_SAME_ROW|bad_members={rep_bad}|json=0", flush=True)
with open(f"{R}/whole{LX}{LY}.pkl", "wb") as f:
    pickle.dump(dict(W=W, Mw=Mw, rows=rows, cls=cls, row_of_cl=row_of_cl, flats=flats, nl=nl), f)
print(f"DONE|secs_wall={time.time()-t0:.0f}|json=0")
