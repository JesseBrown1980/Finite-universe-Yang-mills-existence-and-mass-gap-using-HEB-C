# Separately written check of a Perron certificate, streaming, for stores too large for RAM. Exact Python
# integers, no code shared with perroncert. Recomputes the stream merkle and min_h (H'd)_h / d_h, rounded down.
# usage: check_d_stream.py DEV D_FILE JE JB
#   DEV is a path, or first:count:seglen:prefix for the sector files <prefix>NNN.rooms
# Output row CHECK_D, json=0.
import array, hashlib, os, struct, sys, time

dev, dfile, je, jb = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
t0 = time.monotonic_ns()
MIB = 1048576


class Stream:
    def __init__(self, spec):
        parts = spec.split(":", 3)
        if len(parts) == 4 and parts[0].isdigit():
            self.first, self.count, self.seg = int(parts[0]), int(parts[1]), int(parts[2])
            self.names = [f"{parts[3]}{self.first + k:03d}.rooms" for k in range(self.count)]
        else:
            self.seg = os.path.getsize(spec)
            self.names = [spec]
        self.k, self.pos = 0, 0
        self.f = open(self.names[0], "rb", buffering=0)

    def read(self, n):
        out = bytearray()
        while n > 0:
            b = self.f.read(min(n, self.seg - self.pos))
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


d = array.array("q")
with open(dfile, "rb") as f:
    d.frombytes(f.read())
assert sys.byteorder == "little"
s = Stream(dev)
head = s.read(4096)
line = head[: head.index(b"\n")].decode()
fld = dict(x.split("=", 1) for x in line.split("|")[1:] if "=" in x)
n, payload, rooms = int(fld["n"]), int(fld["payload_bytes"]), int(fld["rooms"])
assert len(d) == n, "d length"
u = 1000 * je
top = 1000 * jb
best = None
flats = pos_off = bad_d = h = 0
carry = b""
shas = bytearray()
left = payload
walked = 0
unpack_h = struct.Struct("<IHH").unpack_from
unpack_e = struct.Struct("<Ii").iter_unpack
while left > 0:
    chunk = s.read(min(16 * MIB, left))
    assert chunk, "short read"
    left -= len(chunk)
    shas += hashlib.sha256(chunk).hexdigest().encode()
    buf = carry + chunk
    p = 0
    end = len(buf)
    while h < n and p + 8 <= end:
        w, mag, cnt = unpack_h(buf, p)
        q = p + 8 + 8 * cnt
        if q > end:
            break
        if mag == 0:
            flats += 1
            if d[h] != 0:
                bad_d += 1
        elif d[h] <= 0:
            bad_d += 1
        else:
            dh = d[h]
            t = top * mag * dh
            for j, z in unpack_e(buf[p + 8 : q]):
                if z > 0 and j != h:
                    pos_off += 1
                t += u * z * d[j]
            r = t // dh
            if best is None or r < best[0]:
                best = (r, h, mag)
        walked += q - p
        p = q
        h += 1
    carry = buf[p:]
    if h == n:
        assert not any(carry), "nonzero padding"
        carry = b""
assert h == n, "rows"
assert walked == 8 * rooms, "rooms"
merkle = hashlib.sha256(bytes(shas)).hexdigest()
assert merkle == fld["payload_merkle"], "merkle"
secs = (time.monotonic_ns() - t0) // 1_000_000_000
print(f"CHECK_D|n={n}|flats={flats}|t_cert_milli={best[0]}|min_row={best[1]}|min_mag={best[2]}|positive_offdiag={pos_off}|bad_d={bad_d}|merkle=PASS|secs={secs}|json=0")
