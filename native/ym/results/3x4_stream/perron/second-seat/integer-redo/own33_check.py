# Integer copy of native/ym/results/3x4_stream/perron/second-seat/own33_check.py, written by native/scripts/make_integer_pairs.py: 0 divisions moved to qdiv and 2 text pairs. The original stays as evidence.
# Exact evaluation of an own33 vector by a second own code path: streaming Python integers over the store bytes. Also writes it as an i64 file for the pinned certifiers.
# usage: own33_check.py DEV X_FILE JB [I64_OUT]
import hashlib, struct, sys, time
LEAF = 16 * 1048576
dev, xf, jb = sys.argv[1], sys.argv[2], int(sys.argv[3])
out = sys.argv[4] if len(sys.argv) > 4 else None
t0 = time.monotonic_ns()
raw = open(dev, "rb").read()
line = raw[: raw.index(b"\n")].decode()
fld = dict(x.split("=", 1) for x in line.split("|")[1:] if "=" in x)
n, payload = int(fld["n"]), int(fld["payload_bytes"])
data = memoryview(raw)[4096 : 4096 + payload]
sh = b"".join(hashlib.sha256(data[i : i + LEAF]).hexdigest().encode() for i in range(0, payload, LEAF))
print("MERKLE_OWN", hashlib.sha256(sh).hexdigest() == fld["payload_merkle"])
xb = open(xf, "rb").read()
xs = [int.from_bytes(xb[i : i + 16], "little", signed=True) for i in range(0, len(xb), 16)]
# walk the rows once for the flat map
p = 0
starts = []
mags = []
for h in range(n):
    m = struct.unpack_from("<H", data, p + 4)[0]
    c = struct.unpack_from("<H", data, p + 6)[0]
    starts.append((p, m, c))
    mags.append(m)
    p += 8 + 8 * c
x = [0] * n
i = 0
for h in range(n):
    if mags[h] != 0:
        x[h] = xs[i]
        i += 1
assert i == len(xs)
u, v = 10**6, 1000 * jb
best = None
A = G = 0
for h in range(n):
    p, m, c = starts[h]
    if m == 0:
        continue
    w = struct.unpack_from("<I", data, p)[0]
    t = v * m * x[h]
    for j, z in struct.iter_unpack("<Ii", data[p + 8 : p + 8 + 8 * c]):
        t += u * z * x[j]
    A += w * x[h] * t
    G += w * x[h] * x[h]
    q = t // x[h]
    if best is None or q < best[0]:
        best = (q, h, m)
ceil = -((-A) // G)
print(f"OWN33_EXACT|barta_floor={best[0]}|row={best[1]}|M={best[2]}|rayleigh_ceil={ceil}|width={ceil - best[0]}|secs_wall={(time.monotonic_ns()-t0)//10**9}|json=0", flush=True)
if out:
    big = max(x)
    shift = max(0, big.bit_length() - 62)
    y = [v_ >> shift for v_ in x]
    with open(out, "wb") as f:
        f.write(b"".join(struct.pack("<q", q) for q in y))
    print(f"WROTE|{out}|shift={shift}|min_nonflat={min(y[h] for h in range(n) if mags[h])}|max={max(y)}|json=0")
