# Recomputes the reader's Lane A fingerprints in Python big integers on the clean small stores, with the r the reader used, and compares them with its output.
# usage: fingerprint_check.py   Integer only, json=0.
import struct

ROOT = "C:/tmp/opus55/allpairs-review-20261103/"
P = (1 << 127) - 1
R = int("3cdeda4c464c8facdffc46b1043c8f59", 16)
bad = 0
for name, path, out in [
    ("2x2", "D:/ym-3x4-room-run/p0-ball/small/2x2/dev.bin", "out/reader-clean-2x2.out"),
    ("2x3", "D:/ym-3x4-room-run/p0-ball/small/2x3/dev.bin", "out/reader-clean-2x3.out"),
    ("3x3", "D:/ym-3x4-room-run/p0-ball/c33/dev33.bin", "out/reader-clean-c33.out"),
]:
    b = open(path, "rb").read()
    line = b[: b.index(b"\n")].decode()
    n = int(dict(x.split("=", 1) for x in line.split("|") if "=" in x)["n"])
    p = 4096
    up, lo, nu, nl = 1, 1, 0, 0
    for h in range(n):
        w, _, cnt = struct.unpack_from("<IHH", b, p)
        p += 8
        v = struct.unpack_from("<" + "Ii" * cnt, b, p)
        p += 8 * cnt
        for k in range(cnt):
            j, z = v[2 * k], v[2 * k + 1]
            if j == h:
                continue
            a, c = (h, j) if j > h else (j, h)
            m = (a << 95) | (c << 64) | ((w * z + (1 << 63)) & ((1 << 64) - 1))
            if j > h:
                up = up * (R - m) % P
                nu += 1
            else:
                lo = lo * (R - m) % P
                nl += 1
    rec = [x for x in open(ROOT + out, encoding="utf-8").read().splitlines() if x.startswith("REVIEW_READER|")][0]
    f = dict(x.split("=", 1) for x in rec.split("|") if "=" in x)
    same = int("%032x" % up == f["fingerprint_upper"] and "%032x" % lo == f["fingerprint_lower"] and nu == int(f["upper"]) and nl == int(f["lower"]))
    bad += 0 if same else 1
    print("FINGERPRINT_CHECK|L=%s|python_upper=%032x|reader_upper=%s|python_lower=%032x|reader_lower=%s|same=%d|json=0" % (name, up, f["fingerprint_upper"], lo, f["fingerprint_lower"], same), flush=True)
print("FINGERPRINT_CHECK_DONE|failed=%d|json=0" % bad)
raise SystemExit(1 if bad else 0)
