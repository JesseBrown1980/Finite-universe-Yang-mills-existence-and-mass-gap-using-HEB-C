# Recomputes the reader's Lane B in Python on a faulted 2x2 store, with fixed keys, and compares the nonzero sum with the reader's output.
# usage: keyed_sum_check.py   Integer only, json=0.
import hashlib, os, struct, subprocess

ROOT = "C:/tmp/opus55/allpairs-review-20261103/"
READER = ROOT + "bin/review-reader.exe"
TMP = ROOT + "attack/stores/keyed.bin"
M64 = (1 << 64) - 1
P61 = (1 << 61) - 1
K0, K1 = 0x0123456789abcdef, 0xfedcba9876543210
R = "1234567890abcdef1234567890abcdef"


def rotl(x, b):
    return ((x << b) | (x >> (64 - b))) & M64


def sipround(v):
    v[0] = (v[0] + v[1]) & M64
    v[1] = rotl(v[1], 13) ^ v[0]
    v[0] = rotl(v[0], 32)
    v[2] = (v[2] + v[3]) & M64
    v[3] = rotl(v[3], 16) ^ v[2]
    v[0] = (v[0] + v[3]) & M64
    v[3] = rotl(v[3], 21) ^ v[0]
    v[2] = (v[2] + v[1]) & M64
    v[1] = rotl(v[1], 17) ^ v[2]
    v[2] = rotl(v[2], 32)


def sip3(a, b, c):
    v = [K0 ^ 0x736f6d6570736575, K1 ^ 0x646f72616e646f6d, K0 ^ 0x6c7967656e657261, K1 ^ 0x7465646279746573]
    for m in (a, b, c, 24 << 56):
        v[3] ^= m
        sipround(v)
        sipround(v)
        v[0] ^= m
    v[2] ^= 0xFF
    for _ in range(4):
        sipround(v)
    return v[0] ^ v[1] ^ v[2] ^ v[3]


b = bytearray(open("D:/ym-3x4-room-run/p0-ball/small/2x2/dev.bin", "rb").read())
eol = b.index(b"\n")
line = b[:eol].decode()
f = dict(x.split("=", 1) for x in line.split("|") if "=" in x)
n, pay = int(f["n"]), int(f["payload_bytes"])
# One changed value on row 40's first off-diagonal, diagonal compensated.
p = 4096
for h in range(40):
    p += 8 + 8 * struct.unpack_from("<H", b, p + 6)[0]
cnt = struct.unpack_from("<H", b, p + 6)[0]
ents = [struct.unpack_from("<Ii", b, p + 8 + 8 * k) + (p + 8 + 8 * k,) for k in range(cnt)]
off = next(e for e in ents if e[0] != 40)
dia = next(e for e in ents if e[0] == 40)
struct.pack_into("<Ii", b, off[2], off[0], off[1] - 1)
struct.pack_into("<Ii", b, dia[2], 40, dia[1] + 1)
pl = bytes(b[4096:4096 + pay])
sha = lambda x: hashlib.sha256(x).hexdigest()
root = sha("".join(sha(pl[i:i + (16 << 20)]) for i in range(0, len(pl), 16 << 20)).encode())
new = line.replace(f["payload_merkle"], root)
b[:len(new)] = new.encode()
open(TMP, "wb").write(b)
# Python's own sum over the faulted rows.
p = 4096
s = 0
for h in range(n):
    w, _, cnt = struct.unpack_from("<IHH", b, p)
    p += 8
    for k in range(cnt):
        j, z = struct.unpack_from("<Ii", b, p)
        p += 8
        if j == h:
            continue
        lo, hi = (h, j) if j > h else (j, h)
        t = sip3(lo, hi, (w * z) & M64) % P61
        s = (s + t) % P61 if j > h else (s - t) % P61
r = subprocess.run([READER, TMP, "--r", R, "--k0", "%x" % K0, "--k1", "%x" % K1], capture_output=True, text=True)
rec = [x for x in r.stdout.splitlines() if x.startswith("REVIEW_READER|")][-1]
g = dict(x.split("=", 1) for x in rec.split("|") if "=" in x)
same = int(str(s) == g["keyed_sum61"] and s != 0)
print("KEYED_SUM_CHECK|fault_row=40|fault_col=%d|python_sum=%d|reader_sum=%s|reader_exit=%d|same=%d|json=0" % (off[0], s, g["keyed_sum61"], r.returncode, same))
os.remove(TMP)
raise SystemExit(0 if same else 1)
