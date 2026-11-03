# What the trust root leaves to the reader: a copy of the tool with one table row edited to a changed store's block. Built from the pinned source plus that one edit; nothing else changes.
# usage: trust_demo.py   Writes hard/trust/src/main.rs, and prints the store and block values. Integer only, json=0.
import gzip, hashlib, math, os, struct
R = "C:/tmp/opus55/allpairs-review-20261103/hard/"
base = gzip.open(R + "x/native/ym/results/3x4_stream/perron/allpairs/fixture-controls/fixture-2x2.rooms.gz", "rb").read()
eol = base.index(b"\n")
LINE = base[:eol].decode()
F = dict(x.split("=", 1) for x in LINE.split("|") if "=" in x)
N, PAY = int(F["n"]), int(F["payload_bytes"])
P = base[4096:4096 + PAY]
ROWS, p = [], 0
for _ in range(N):
    w, mag, cnt = struct.unpack_from("<IHH", P, p)
    v = struct.unpack_from("<" + "Ii" * cnt, P, p + 8)
    ROWS.append([w, mag, [(v[2 * i], v[2 * i + 1]) for i in range(cnt)]])
    p += 8 + 8 * cnt
def sha(b): return hashlib.sha256(b).hexdigest()
def merkle(pl): return sha("".join(sha(pl[i:i + (16 << 20)]) for i in range(0, len(pl), 16 << 20)).encode())
h, i = next((h, j) for h in range(N) for j, _ in ROWS[h][2] if j < h)
g = math.gcd(ROWS[h][0], ROWS[i][0])
for rw, col, d in ((h, i, ROWS[i][0] // g), (i, h, ROWS[h][0] // g)):
    e = ROWS[rw][2]
    k = [q for q, x in enumerate(e) if x[0] == col][0]
    e[k] = (col, e[k][1] - d)
    k = [q for q, x in enumerate(e) if x[0] == rw][0]
    e[k] = (rw, e[k][1] + d)
out = bytearray()
for w, mag, ent in ROWS:
    out += struct.pack("<IHH", w, mag, len(ent))
    for j, z in ent:
        out += struct.pack("<Ii", j, z)
SYM2 = bytes(out).ljust(PAY, b"\0")
new_line = LINE.replace(F["payload_merkle"], merkle(SYM2))
block = (new_line + "\n").encode().ljust(4096, b"\0")
os.makedirs(R + "tmp/t", exist_ok=True)
open(R + "tmp/t/sym2.bin", "wb").write(block + SYM2)
s = open(R + "src/native/ym/crates/evolvers/src/bin/allpairs.rs", encoding="utf-8").read()
assert s.count(LINE) == 1 and s.count(sha(base[:4096])) == 1
s = s.replace(LINE, new_line).replace(sha(base[:4096]), sha(block)).replace('"../../../torusl/src/', '"' + R + 'src/native/ym/crates/torusl/src/')
os.makedirs(R + "trust/src", exist_ok=True)
open(R + "trust/src/main.rs", "w", encoding="utf-8", newline="\n").write(s)
print("TRUST_DEMO|new_merkle=%s|new_block=%s|old_block=%s|json=0" % (merkle(SYM2), sha(block), sha(base[:4096])))
