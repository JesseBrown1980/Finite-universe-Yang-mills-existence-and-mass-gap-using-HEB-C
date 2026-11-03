# Builds the stores for the memory probes. Two clean rows, then TRAIL bytes of zero padding inside the payload, merkle correct, so allpairs should pass
# while it holds the padding in memory. usage: mem_stores.py PATH TRAIL_MiB   Integer only, json=0.
import hashlib, struct, sys

path, mib = sys.argv[1], int(sys.argv[2])
rows = struct.pack("<IHH", 1, 3, 2) + struct.pack("<IiIi", 0, 1, 1, -1) + struct.pack("<IHH", 1, 3, 2) + struct.pack("<IiIi", 0, -1, 1, 1)
total = len(rows) + (mib << 20)
leaf = 16 << 20
hx = []
first = rows.ljust(leaf, b"\0") if total >= leaf else rows.ljust(total, b"\0")
hx.append(hashlib.sha256(first).hexdigest())
left = total - len(first)
zero_leaf = hashlib.sha256(b"\0" * leaf).hexdigest()
while left >= leaf:
    hx.append(zero_leaf)
    left -= leaf
if left:
    hx.append(hashlib.sha256(b"\0" * left).hexdigest())
root = hashlib.sha256("".join(hx).encode()).hexdigest()
line = "YMROOMHDR|L=x|sector=x|n=2|rooms=6|entries=4|payload_bytes=%d|payload_merkle=%s|w_self_adjoint=PASS|json=0\n" % (total, root)
with open(path, "wb") as f:
    f.write(line.encode().ljust(4096, b"\0"))
    f.write(first)
    z = b"\0" * (1 << 20)
    left = total - len(first)
    while left > 0:
        n = min(left, len(z))
        f.write(z[:n])
        left -= n
print("MEM_STORE|path=%s|trail_mib=%d|payload_bytes=%d|merkle=%s|json=0" % (path, mib, total, root))
