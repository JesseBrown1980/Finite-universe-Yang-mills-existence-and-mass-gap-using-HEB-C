#!/usr/bin/env python3
"""field_v19b.py (GLOBAL HASH variant of field_v19.py; see SPEC-FIELD-V19B.hbp) -- density, pull, gate and push in the room matrix: is there a collective fluctuation field?
See SPEC-FIELD-V19.hbp (sealed before the run). Integers only. The room store is not touched: the matrix is the
authenticated 27x27x27 block read earlier (out/block-*.bin), copied into memory.

Rules (operator's description, this unit's defaults where he left a choice):
  ground  the centre room pulls: a frozen trit (digit 0) moves the function one step toward the centre
  push    an active trit (digit 2) moves it one step along the direction its residual digit names
  keep    a free trit (digit 1) keeps its heading
  speed   every function moves exactly one room every tick (no stopping); walls turn it back
  gate    functions enter at the outer faces, N/27 per tick for 27 ticks
  respond in mode RESPOND a room's trit turns by one third (digit+1 mod 3) each time it is read, in memory
  density N = 729, 2187, 6561 functions (1, 3, 9 per 27-room cube on average)
Measured after a warm-up: per 27-room cube, the occupancy over time. FANO = spread/average (1000 = a fair die for
independent arrivals); FAR = how much opposite cubes rise and fall together (0 = not at all).
  python field_v19.py <block.bin> <leaf1> <leaf2> <leaf3> <controls>
"""
import sys

MASK = 0xFFFFFFFFFFFFFFFF


def mixer(seed):
    st = [seed & MASK]
    def nxt():
        st[0] = (st[0] + 0x9E3779B97F4A7C15) & MASK
        z = st[0]
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
        return z ^ (z >> 31)
    return nxt


raw = open(sys.argv[1], "rb").read()
assert len(raw) == 19683 * 8
ROOMS0 = []
for i in range(19683):
    v = int.from_bytes(raw[8 * i:8 * i + 8], "little"); t = bytearray(27)
    for k in range(27):
        t[k] = v % 3; v //= 3
    ROOMS0.append(t)


def coords(idx):
    d = []
    for _ in range(9):
        d.append(idx % 3); idx //= 3
    return d[0] + 3 * d[3] + 9 * d[6], d[1] + 3 * d[4] + 9 * d[7], d[2] + 3 * d[5] + 9 * d[8]


IDX = {}
for i in range(19683):
    IDX[coords(i)] = i
FACE = sorted(c for c in IDX if 0 in c or 26 in c)
vals = []
for p in sys.argv[2:5]:
    rows = []
    for line in open(p):
        if line.startswith("LEAF|"):
            x = dict(w.split("=", 1) for w in line.strip().split("|")[1:] if "=" in w)
            rows.append((int(x["key"]), int(x["slack"])))
    vals += sorted(rows)
NC = int(sys.argv[5])


def zob(x):
    z = (x * 0x9E3779B97F4A7C15 + 0x1234567) & MASK
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
    return z ^ (z >> 31)


def digits(v):
    top = 1
    while v >= 27:
        v //= 27; top *= 27
    return top


def run(N, respond, scramble_seed):
    rooms = [bytearray(t) for t in ROOMS0] if respond else ROOMS0
    src = vals[:N]
    if scramble_seed is not None:
        r = mixer(scramble_seed); s2 = []
        for key, sl in src:
            top = digits(sl); v = 0; tt = top
            while tt:
                v = v * 27 + r() % 27; tt //= 27
            s2.append((key, v, top))
        src = s2
    else:
        src = [(k, s, digits(s)) for k, s in src]
    fx = []; fy = []; fz = []; fh = []; fr = []; ft = []
    H = 0                                   # the global hash of the whole matrix state (mode GLOBAL)
    if respond == 2:
        for a in range(19683):
            ra = rooms[a]
            for k in range(27):
                H ^= zob(a * 81 + k * 3 + ra[k])
    per = N // 27; WARM = 81; MEAS = 243; T = WARM + MEAS
    s = [0] * 729; sq = [0] * 729; cr = [0] * 729
    nxt = 0
    for tick in range(T):
        if tick < 27:
            for (key, rho, top) in src[nxt:nxt + per]:
                x, y, z = FACE[key % len(FACE)]
                fx.append(x); fy.append(y); fz.append(z); fh.append(13); fr.append(rho); ft.append(top)
            nxt += per
        occ = [0] * 729
        for j in range(len(fx)):
            x = fx[j]; y = fy[j]; z = fz[j]; rho = fr[j]
            a = IDX[(x, y, z)]
            i = (rho + H) % 27 if respond == 2 else rho % 27   # GLOBAL: every function reads the hash of the whole matrix, as it is at that instant
            room = rooms[a]
            tr = room[i]
            if respond:
                room[i] = (tr + 1) % 3
                if respond == 2:
                    H ^= zob(a * 81 + i * 3 + tr) ^ zob(a * 81 + i * 3 + (tr + 1) % 3)
            if tr == 2:
                h = i
            elif tr == 1:
                h = fh[j]
            else:
                h = 13
            if h == 13:                       # the pull of the ground room (also the rest direction)
                dx = (x < 13) - (x > 13); dy = (y < 13) - (y > 13); dz = (z < 13) - (z > 13)
                if dx == 0 and dy == 0 and dz == 0:
                    dx = 1
            else:
                dx = h % 3 - 1; dy = (h // 3) % 3 - 1; dz = h // 9 - 1
            nx = x + dx; ny = y + dy; nz = z + dz
            if nx < 0 or nx > 26: nx = x - dx
            if ny < 0 or ny > 26: ny = y - dy
            if nz < 0 or nz > 26: nz = z - dz
            fx[j] = nx; fy[j] = ny; fz[j] = nz; fh[j] = h
            fr[j] = rho // 27 + (rho % 27) * ft[j]
            occ[(nx // 3) + 9 * (ny // 3) + 81 * (nz // 3)] += 1
        if tick >= WARM:
            for c in range(729):
                o = occ[c]
                if o:
                    s[c] += o; sq[c] += o * o
                    cx, cy, cz = c % 9, (c // 9) % 9, c // 81
                    cr[c] += o * occ[(8 - cx) + 9 * (8 - cy) + 81 * (8 - cz)]
    num = sum(MEAS * sq[c] - s[c] * s[c] for c in range(729)); den = MEAS * sum(s)
    far = sum(MEAS * cr[c] - s[c] * s[(8 - c % 9) + 9 * (8 - (c // 9) % 9) + 81 * (8 - c // 81)] for c in range(729))
    centre = s[4 + 9 * 4 + 81 * 4]
    return 1000 * num // den, (1000 * far // num) if num else 0, 1000 * centre // sum(s)


print("FIELDHDR|rooms=19683|cubes=729|functions_available=%d|warm_up_ticks=81|measured_ticks=243|controls_per_cell=%d|integer_only=1|room_store_writes=0|json=0" % (len(vals), NC))
for respond in (2,):
    for N in (729, 2187, 6561):
        real = run(N, respond, None)
        ctl = [run(N, respond, 19000 + 100 * respond + k) for k in range(NC)]
        row = "FIELD|mode=%s|functions=%d|per_cube=%d|FANO_real=%d|FANO_scrambled=%d..%d|FAR_real=%d|FAR_scrambled=%d..%d|centre_share_real=%d|centre_share_scrambled=%d..%d" % (
            "GLOBAL_HASH", N, N // 729, real[0], min(c[0] for c in ctl), max(c[0] for c in ctl),
            real[1], min(c[1] for c in ctl), max(c[1] for c in ctl), real[2], min(c[2] for c in ctl), max(c[2] for c in ctl))
        v = "OUTSIDE" if (real[0] < min(c[0] for c in ctl) or real[0] > max(c[0] for c in ctl)) else "INSIDE"
        print(row + "|FANO_verdict=%s|json=0" % v, flush=True)
