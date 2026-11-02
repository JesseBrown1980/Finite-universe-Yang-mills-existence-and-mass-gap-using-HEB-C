# Rebuilds sampled rows of a sector store from the definition of H and compares them with the stored rows, field by field.
# Exact Python integers, standard library only, separately written from the store's builder. It uses the builder's published
# formats for keys and rows, and derives everything else here: S3 from permutations, plaquettes from the lattice, the lattice
# symmetries from reflections and translations, and each row from the 3*nl electric moves.
#
# H = J_E*E + J_B*M on gauge-invariant states. E sums (1 - tau) over the three transpositions on every link, and
# M = sum over plaquettes of (2 - chi(U_p)), with chi = fixed points - 1. In the Sx+Sy+ sector a row holds one -1 per move into
# each target orbit, and the diagonal is 3*nl minus the moves back into the row's own orbit. All characters are trivial.
#
# Key of a state: gauge-fix to the comb tree, read the free links in ascending link order as base-6 digits, and take the least
# code over global conjugation and the lattice symmetries. Digits name permutations in the order of PERMS below.
#
# usage: verify_sample_rows.py LX LY DEV PASSA [--all] [--per-M K] [--uniform U] [--seed S] [--rows a,b,c]
#   DEV   a path, or first:count:seglen:prefix for the sector files <prefix>NNN.rooms
#   PASSA key table: 16 bytes per row, key u64, weight u32, magnetic number u32, little-endian
# Any mismatch prints one VERIFY_ROWS_FAIL row and exits 2. Success prints one VERIFY_ROWS row. json=0.
import array, bisect, hashlib, random, struct, sys, time

MIB = 1048576
PERMS = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
IDX = {p: i for i, p in enumerate(PERMS)}
MUL = [[IDX[tuple(a[b[i]] for i in range(3))] for b in PERMS] for a in PERMS]
INV = [next(j for j in range(6) if MUL[i][j] == IDX[(0, 1, 2)]) for i in range(6)]
FIXED = [sum(1 for i in range(3) if p[i] == i) for p in PERMS]
CHI = [f - 1 for f in FIXED]
TRANSPOSITIONS = [i for i in range(6) if FIXED[i] == 1]
ID = IDX[(0, 1, 2)]
CONJ = [[MUL[MUL[c][v]][INV[c]] for v in range(6)] for c in range(6)]


def fail(reason):
    print(f"VERIFY_ROWS_FAIL|reason={reason}|json=0", flush=True)
    sys.exit(2)


class Lattice:
    def __init__(self, lx, ly):
        self.lx, self.ly = lx, ly
        self.n = lx * ly
        self.nl = 2 * self.n
        tree = {self.ylink(0, y) for y in range(ly - 1)} | {self.xlink(x, y) for x in range(lx - 1) for y in range(ly)}
        self.free = [l for l in range(self.nl) if l not in tree]
        self.pow6 = [6**i for i in range(len(self.free))]
        # Endpoints of each link, as sites.
        self.ends = [None] * self.nl
        for x in range(lx):
            for y in range(ly):
                self.ends[self.xlink(x, y)] = (self.site(x, y), self.site(x + 1, y))
                self.ends[self.ylink(x, y)] = (self.site(x, y), self.site(x, y + 1))
        self.free_ends = [(self.ends[l][0], self.ends[l][1], l) for l in self.free]
        # The tree path from (0,0): up the column at x = 0, then along each row.
        self.steps = []
        for y in range(1, ly):
            self.steps.append((self.site(0, y), self.site(0, y - 1), self.ylink(0, y - 1)))
        for x in range(1, lx):
            for y in range(ly):
                self.steps.append((self.site(x, y), self.site(x - 1, y), self.xlink(x - 1, y)))
        self.plaquettes = [
            (self.xlink(x, y), self.ylink(x + 1, y), self.xlink(x, y + 1), self.ylink(x, y)) for x in range(lx) for y in range(ly)
        ]
        # Lattice symmetries: reflect then translate. A reflected link is the forward link one step back, inverted.
        self.ops = []
        for fx in (False, True):
            for fy in (False, True):
                for tx in range(lx):
                    for ty in range(ly):
                        dest = [None] * self.nl
                        for x in range(lx):
                            for y in range(ly):
                                px = -x if fx else x
                                py = -y if fy else y
                                dest[self.xlink(x, y)] = (self.xlink((px - 1 if fx else px) + tx, py + ty), fx)
                                dest[self.ylink(x, y)] = (self.ylink(px + tx, (py - 1 if fy else py) + ty), fy)
                        self.ops.append(dest)

    def site(self, x, y):
        return (x % self.lx) * self.ly + (y % self.ly)

    def xlink(self, x, y):
        return self.site(x, y)

    def ylink(self, x, y):
        return self.n + self.site(x, y)

    def links_from_key(self, key):
        u = [ID] * self.nl
        for l in self.free:
            u[l] = key % 6
            key //= 6
        if key != 0:
            fail("key_has_extra_digits")
        return u

    def magnetic(self, u):
        m = 0
        for a, b, c, d in self.plaquettes:
            p = MUL[MUL[MUL[u[a]][u[b]]][INV[u[c]]]][INV[u[d]]]
            m += 2 - CHI[p]
        return m

    def gauge_fixed_digits(self, u):
        h = [ID] * self.n
        for hd, t, l in self.steps:
            h[hd] = MUL[h[t]][u[l]]
        return [MUL[MUL[h[t]][u[l]]][INV[h[hd]]] for t, hd, l in self.free_ends]

    def orbit_key(self, u):
        best = None
        pow6 = self.pow6
        out = [0] * self.nl
        for dest in self.ops:
            for l, (d, inv) in enumerate(dest):
                out[d] = INV[u[l]] if inv else u[l]
            q = self.gauge_fixed_digits(out)
            for r in CONJ:
                code = 0
                for v, p in zip(q, pow6):
                    code += r[v] * p
                if best is None or code < best:
                    best = code
        return best

    def orbit_codes(self, u):
        codes = set()
        pow6 = self.pow6
        out = [0] * self.nl
        for dest in self.ops:
            for l, (d, inv) in enumerate(dest):
                out[d] = INV[u[l]] if inv else u[l]
            q = self.gauge_fixed_digits(out)
            for r in CONJ:
                code = 0
                for v, p in zip(q, pow6):
                    code += r[v] * p
                codes.add(code)
        return codes


class Stream:
    def __init__(self, spec):
        parts = spec.split(":", 3)
        if len(parts) == 4 and parts[0].isdigit():
            first, count, self.seg = int(parts[0]), int(parts[1]), int(parts[2])
            self.names = [f"{parts[3]}{first + k:03d}.rooms" for k in range(count)]
        else:
            self.seg = None
            self.names = [spec]
        self.k, self.pos = 0, 0
        self.f = open(self.names[0], "rb", buffering=0)

    def read(self, n):
        out = bytearray()
        while n > 0:
            want = n if self.seg is None else min(n, self.seg - self.pos)
            b = self.f.read(want) if want > 0 else b""
            if not b:
                if self.k + 1 >= len(self.names):
                    break
                self.f.close()
                self.k += 1
                self.pos = 0
                self.f = open(self.names[self.k], "rb", buffering=0)
                continue
            out += b
            self.pos += len(b)
            n -= len(b)
        return bytes(out)


def read_rows(dev, wanted):
    """One pass over the whole store: returns the wanted rows and recomputes the payload merkle."""
    s = Stream(dev)
    head = s.read(4096)
    if b"\n" not in head:
        fail("no_header_line")
    fld = dict(x.split("=", 1) for x in head[: head.index(b"\n")].decode().split("|")[1:] if "=" in x)
    n, payload = int(fld["n"]), int(fld["payload_bytes"])
    rows = {}
    shas = bytearray()
    unpack_h = struct.Struct("<IHH").unpack_from
    unpack_e = struct.Struct("<Ii").iter_unpack
    left, carry, h = payload, b"", 0
    while left > 0:
        chunk = s.read(min(16 * MIB, left))
        if not chunk:
            fail("short_read")
        left -= len(chunk)
        shas += hashlib.sha256(chunk).hexdigest().encode()
        buf = carry + chunk
        p, end = 0, len(buf)
        while h < n and p + 8 <= end:
            w, mag, cnt = unpack_h(buf, p)
            q = p + 8 + 8 * cnt
            if q > end:
                break
            if h in wanted:
                rows[h] = (w, mag, list(unpack_e(buf[p + 8 : q])))
            p = q
            h += 1
        carry = buf[p:]
        if h == n:
            carry = b""
    if h != n:
        fail("row_count")
    if hashlib.sha256(bytes(shas)).hexdigest() != fld["payload_merkle"]:
        fail("merkle")
    return n, rows


def main():
    t0 = time.monotonic_ns()
    a = sys.argv[1:]

    def opt(name, default):
        if name in a:
            i = a.index(name)
            v = a[i + 1]
            del a[i : i + 2]
            return v
        return default

    per_m = int(opt("--per-M", "50"))
    uniform = int(opt("--uniform", "1000"))
    seed = int(opt("--seed", "27"))
    extra = opt("--rows", "")
    everything = "--all" in a
    if everything:
        a.remove("--all")
    if len(a) != 4:
        fail("usage")
    lx, ly, dev, passa = int(a[0]), int(a[1]), a[2], a[3]
    if sys.byteorder != "little":
        fail("big_endian_platform")
    lat = Lattice(lx, ly)

    pa = array.array("Q")
    with open(passa, "rb") as f:
        pa.frombytes(f.read())
    if pa.itemsize != 8 or len(pa) % 2:
        fail("passa_length")
    n = len(pa) // 2
    keys = pa[::2]
    for i in range(n - 1):
        if keys[i] >= keys[i + 1]:
            fail(f"keys_not_ascending_row_{i}")

    # Row choice: all flat rows, the ends, every magnetic number by reservoir, a uniform draw, and any named rows.
    rng = random.Random(seed)
    if everything:
        wanted = set(range(n))
    else:
        wanted = {0, 1, 2, n - 3, n - 2, n - 1}
        wanted |= {int(x) for x in extra.split(",") if x}
        wanted |= {rng.randrange(n) for _ in range(uniform)}
        reservoir, seen = {}, {}
        for h in range(n):
            m = pa[2 * h + 1] >> 32
            if m == 0:
                wanted.add(h)
                continue
            k = seen.get(m, 0)
            seen[m] = k + 1
            bucket = reservoir.setdefault(m, [])
            if k < per_m:
                bucket.append(h)
            else:
                j = rng.randrange(k + 1)
                if j < per_m:
                    bucket[j] = h
        for bucket in reservoir.values():
            wanted.update(bucket)
    if any(h < 0 or h >= n for h in wanted):
        fail("named_row_out_of_range")

    store_n, rows = read_rows(dev, wanted)
    if store_n != n:
        fail("store_and_key_table_differ_in_n")
    if len(rows) != len(wanted):
        fail("row_missing")
    pass_secs = (time.monotonic_ns() - t0) // 1_000_000_000

    by_m = {}
    three_nl = 3 * lat.nl
    for h in sorted(wanted):
        w, mag, stored = rows[h]
        key = pa[2 * h]
        tw = pa[2 * h + 1] & 0xFFFFFFFF
        tm = pa[2 * h + 1] >> 32
        if tw != w or tm != mag:
            fail(f"key_table_and_store_differ_row_{h}")
        u = lat.links_from_key(key)
        if lat.magnetic(u) != mag:
            fail(f"magnetic_number_row_{h}")
        codes = lat.orbit_codes(u)
        if min(codes) != key:
            fail(f"key_is_not_the_least_in_its_orbit_row_{h}")
        if len(codes) != w:
            fail(f"weight_row_{h}")
        row = {h: three_nl}
        mv = list(u)
        for e in range(lat.nl):
            base = u[e]
            for t in TRANSPOSITIONS:
                # Right multiplication: the same three targets as left multiplication, since the transpositions are a class.
                mv[e] = MUL[base][t]
                target = lat.orbit_key(mv)
                j = bisect.bisect_left(keys, target)
                if j == n or keys[j] != target:
                    fail(f"move_target_missing_from_key_table_row_{h}")
                row[j] = row.get(j, 0) - 1
            mv[e] = base
        rebuilt = sorted((j, z) for j, z in row.items() if z != 0)
        if rebuilt != sorted(stored) or [j for j, _ in stored] != [j for j, _ in rebuilt]:
            fail(f"row_differs_row_{h}")
        by_m[mag] = by_m.get(mag, 0) + 1

    listing = hashlib.sha256(",".join(map(str, sorted(wanted))).encode()).hexdigest()
    secs = (time.monotonic_ns() - t0) // 1_000_000_000
    hist = ",".join(f"{m}:{by_m[m]}" for m in sorted(by_m))
    print(
        f"VERIFY_ROWS|L={lx}x{ly}|n={n}|rows_rebuilt={len(wanted)}|all_rows={int(everything)}|per_M={per_m}|uniform={uniform}|seed={seed}"
        f"|named_rows={extra or 'none'}|rows_sha256={listing}|by_M={hist}|matched={len(wanted)}|merkle=PASS|pass_secs={pass_secs}|secs={secs}|json=0",
        flush=True,
    )


main()
