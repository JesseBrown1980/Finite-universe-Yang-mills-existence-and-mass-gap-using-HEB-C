# Separately written check of a Perron certificate: exact Python integers over a ymroom stream, without
# perroncert's reader or checker. Recomputes the stream merkle and min_h (H'd)_h / d_h, rounded down.
# usage: check_d.py DEV D_FILE JE JB    Output row CHECK_D, json=0.
import hashlib, sys, array, struct

dev, dfile, je, jb = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
d = array.array("q")
with open(dfile, "rb") as f:
    d.frombytes(f.read())
if sys.byteorder != "little":
    d.byteswap()
with open(dev, "rb") as f:
    head = f.read(4096)
    line = head[: head.index(b"\n")].decode()
    fld = dict(x.split("=", 1) for x in line.split("|")[1:] if "=" in x)
    n, payload_bytes = int(fld["n"]), int(fld["payload_bytes"])
    pay = f.read(payload_bytes)
assert len(pay) == payload_bytes and len(d) == n
shas = b"".join(hashlib.sha256(pay[i : i + 16 * 1048576]).hexdigest().encode() for i in range(0, len(pay), 16 * 1048576))
merkle = hashlib.sha256(shas).hexdigest()
assert merkle == fld["payload_merkle"], "merkle"
u = 1000 * je
best = None
flats = pos_off = bad_d = 0
p = 0
for h in range(n):
    w, mag, cnt = struct.unpack_from("<IHH", pay, p)
    p += 8
    if mag == 0:
        flats += 1
        bad_d += d[h] != 0
        p += 8 * cnt
        continue
    dh = d[h]
    if dh <= 0:
        bad_d += 1
        p += 8 * cnt
        continue
    s = 1000 * jb * mag * dh
    for j, z in struct.iter_unpack("<Ii", pay[p : p + 8 * cnt]):
        if j != h and z > 0:
            pos_off += 1
        s += u * z * d[j]
    p += 8 * cnt
    r = s // dh
    if best is None or r < best[0]:
        best = (r, h, mag)
assert p == 8 * int(fld["rooms"]) and not any(pay[p:]), "payload walk"
print(f"CHECK_D|n={n}|flats={flats}|t_cert_milli={best[0]}|min_row={best[1]}|min_mag={best[2]}|positive_offdiag={pos_off}|bad_d={bad_d}|merkle=PASS|json=0")
