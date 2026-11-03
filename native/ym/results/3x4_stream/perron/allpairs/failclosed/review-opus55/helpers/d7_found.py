# Builds the D7 store on a copy of the public fixture and prints the tool's pass row, to read found and stored directly. Integer only, json=0.
import gzip, hashlib, struct, subprocess
EXE = "D:/ym-3x4-room-run/p0-ball/allpairs/allpairs.exe"
GZ = "C:/tmp/opus55/ym-review-wt/native/ym/results/3x4_stream/perron/allpairs/fixture-controls/fixture-2x2.rooms.gz"
TMP = "C:/tmp/opus55/allpairs-review-20261103/attack/stores/d7.bin"
b = gzip.open(GZ, "rb").read()
eol = b.index(b"\n")
line = b[:eol].decode()
f = dict(x.split("=", 1) for x in line.split("|") if "=" in x)
n, pay = int(f["n"]), int(f["payload_bytes"])
P = b[4096:4096 + pay]
rows, p = [], 0
for _ in range(n):
    w, mag, cnt = struct.unpack_from("<IHH", P, p)
    v = struct.unpack_from("<" + "Ii" * cnt, P, p + 8)
    rows.append([w, mag, [(v[2 * i], v[2 * i + 1]) for i in range(cnt)]])
    p += 8 + 8 * cnt
def diag(h, dz):
    e = rows[h][2]
    k = [i for i, x in enumerate(e) if x[0] == h][0]
    e[k] = (h, e[k][1] + dz)
h, i = next((h, j) for h in range(n) for j, _ in rows[h][2] if j < h)
m = [c for c, _ in rows[i][2] if c > i and c != h][0]
z = [x for x in rows[h][2] if x[0] == i][0]
rows[h][2].insert(rows[h][2].index(z), z)
diag(h, -z[1])
zm = [x for x in rows[m][2] if x[0] == i][0]
rows[m][2].remove(zm)
diag(m, zm[1])
out = bytearray()
for w, mag, e in rows:
    out += struct.pack("<IHH", w, mag, len(e))
    for j, zz in e:
        out += struct.pack("<Ii", j, zz)
pl = bytes(out).ljust(pay, b"\0")
sha = lambda x: hashlib.sha256(x).hexdigest()
root = sha("".join(sha(pl[k:k + (16 << 20)]) for k in range(0, len(pl), 16 << 20)).encode())
new = line.replace(f["payload_merkle"], root)
open(TMP, "wb").write(new.encode() + b"\n" + b"\0" * (4096 - len(new) - 1) + pl)
for cap in (470000000, 100, 13):
    r = subprocess.run([EXE, TMP, "0", str(cap)], capture_output=True, text=True)
    ps = [x for x in r.stdout.splitlines() if x.startswith("ALLPAIRS_PASS|")]
    fin = [x for x in r.stdout.splitlines() if x.startswith("ALLPAIRS|")][-1]
    d = dict(x.split("=", 1) for x in fin.split("|") if "=" in x)
    tot = lambda key: sum(int(dict(y.split("=", 1) for y in q.split("|") if "=" in y)[key]) for q in ps)
    print("D7_FOUND|h=%d|i=%d|m=%d|cap=%d|exit=%d|stored=%d|found=%d|lookups=%d|pairs=%s|upper_without_lower=%s|lower_without_upper=%s|value_mismatch=%s|columns_not_ascending=%s|verdict=%s|json=0" % (h, i, m, cap, r.returncode, tot("upper_stored"), tot("found"), tot("lookups"), d["pairs"], d["upper_without_lower"], d["lower_without_upper"], d["value_mismatch"], d["columns_not_ascending"], d["verdict"]))
import os
os.remove(TMP)
