# Read only: finds which byte the running bit flip has reached, by comparing its temporary store with the clean rows.
import struct, time
d = open("D:/ym-3x4-room-run/p0-ball/small/2x2/dev.bin", "rb").read()
line = d[:d.index(b"\n")].decode()
f = dict(x.split("=", 1) for x in line.split("|") if "=" in x)
n = int(f["n"])
p = 4096
for _ in range(n):
    cnt = struct.unpack_from("<H", d, p + 6)[0]
    p += 8 + 8 * cnt
clean = d[4096:p]
for t in range(3):
    try:
        b = open("C:/tmp/opus55/allpairs-review-20261103/fuzz/tmp-f.bin", "rb").read()
    except OSError:
        continue
    pl = b[4096:]
    if len(pl) != len(clean):
        continue
    diff = [i for i in range(len(clean)) if clean[i] != pl[i]]
    if diff:
        print("FLIP_PROGRESS|byte=%d|of=%d|per_mille=%d|at=%s|json=0" % (diff[0], len(clean), diff[0] * 1000 // len(clean), time.strftime("%H:%M:%S", time.gmtime())))
        break
