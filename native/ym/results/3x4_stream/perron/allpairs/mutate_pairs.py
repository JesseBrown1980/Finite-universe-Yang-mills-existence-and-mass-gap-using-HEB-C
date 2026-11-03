# Damage controls for the pair and row-sum gates: a small store with one change and its merkle REPAIRED, so the hash lets it through.
# usage: mutate_pairs.py IN OUT MODE ROW
#   entry   z-1 on the row's first off-diagonal, diagonal+1: the pair breaks, the row sum holds
#   rowsum  diagonal+1: the row sum breaks, every pair holds
#   weight  w+1: every pair of the row breaks
#   mag     M+1: pairs and row sums hold
#   column  the first off-diagonal with a free next column moves there: two entries lose their partners
#   swap    the row's first two entries trade places: columns no longer ascend
#   sym2    both sides of one pair change, with w_h z_hj = w_j z_jh kept and both diagonals compensated
# Prints the pair it touched. Integer only, json=0.
import hashlib, math, struct, sys

src, out, mode, row = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
b = bytearray(open(src, "rb").read())
end = b.index(b"\n")
line = b[:end].decode()
f = dict(x.split("=", 1) for x in line.split("|") if "=" in x)
n, payload = int(f["n"]), int(f["payload_bytes"])
starts = []
p = 4096
for h in range(n):
    starts.append(p)
    p += 8 + 8 * struct.unpack_from("<IHH", b, p)[2]


def ents(h):
    p = starts[h]
    cnt = struct.unpack_from("<IHH", b, p)[2]
    return [struct.unpack_from("<Ii", b, p + 8 + 8 * k) + (p + 8 + 8 * k,) for k in range(cnt)]


def bump(pos, dz):
    j, z = struct.unpack_from("<Ii", b, pos)
    struct.pack_into("<Ii", b, pos, j, z + dz)


p = starts[row]
w, mag, cnt = struct.unpack_from("<IHH", b, p)
e = ents(row)
off = [x for x in e if x[0] != row]
dia = next(x for x in e if x[0] == row)
touched = ""
if mode == "entry":
    bump(off[0][2], -1)
    bump(dia[2], 1)
    touched = "h=%d|j=%d" % (row, off[0][0])
elif mode == "rowsum":
    bump(dia[2], 1)
    touched = "h=%d" % row
elif mode == "weight":
    struct.pack_into("<I", b, p, w + 1)
    touched = "h=%d|off_diagonals=%d" % (row, len(off))
elif mode == "mag":
    struct.pack_into("<H", b, p + 4, mag + 1)
    touched = "h=%d" % row
elif mode == "column":
    cols = {x[0] for x in e}
    x = next(x for x in off if x[0] + 1 < n and x[0] + 1 not in cols)
    struct.pack_into("<Ii", b, x[2], x[0] + 1, x[1])
    touched = "h=%d|j=%d|new_j=%d" % (row, x[0], x[0] + 1)
elif mode == "swap":
    a, c = e[0], e[1]
    struct.pack_into("<Ii", b, a[2], c[0], c[1])
    struct.pack_into("<Ii", b, c[2], a[0], a[1])
    touched = "h=%d" % row
elif mode == "sym2":
    x = off[0]
    j = x[0]
    wj = struct.unpack_from("<IHH", b, starts[j])[0]
    g = math.gcd(w, wj)
    a, c = wj // g, w // g
    rev = next(y for y in ents(j) if y[0] == row)
    dj = next(y for y in ents(j) if y[0] == j)
    bump(x[2], -a)
    bump(dia[2], a)
    bump(rev[2], -c)
    bump(dj[2], c)
    touched = "h=%d|j=%d|da=%d|db=%d" % (row, j, a, c)
else:
    raise SystemExit("bad mode")
pl = bytes(b[4096:4096 + payload])
hx = "".join(hashlib.sha256(pl[i:i + (16 << 20)]).hexdigest() for i in range(0, len(pl), 16 << 20))
root = hashlib.sha256(hx.encode()).hexdigest()
new_line = line.replace("payload_merkle=" + f["payload_merkle"], "payload_merkle=" + root)
assert len(new_line) == len(line)
b[:end] = new_line.encode()
open(out, "wb").write(b)
print("MUTATED|mode=%s|%s|merkle_repaired=1|old=%s|new=%s|json=0" % (mode, touched, f["payload_merkle"][:16], root[:16]))
