# Payload sizes on and around the tool's 16 MiB leaves and 64 MiB chunks, with the merkle from hashlib. Then one changed byte on each side of a leaf and chunk edge.
# usage: sizes.py OUT_HBP   Integer only, json=0.
import hashlib, os, struct, subprocess, sys

ROOT = "C:/tmp/opus55/allpairs-review-20261103"
EXE = "D:/ym-3x4-room-run/p0-ball/allpairs/allpairs.exe"
TMP = ROOT + "/attack/stores/size.bin"
MIB = 1 << 20
log = open(sys.argv[1], "w", encoding="utf-8", newline="\n")
ROWS = struct.pack("<IHH", 1, 3, 2) + struct.pack("<IiIi", 0, 1, 1, -1) + struct.pack("<IHH", 1, 3, 2) + struct.pack("<IiIi", 0, -1, 1, 1)
bad = 0


def sha(b):
    return hashlib.sha256(b).hexdigest()


def merkle(pl):
    return sha("".join(sha(pl[i:i + 16 * MIB]) for i in range(0, len(pl), 16 * MIB)).encode())


def wrap(pl, root):
    line = "YMROOMHDR|L=x|sector=x|n=2|rooms=6|entries=4|payload_bytes=%d|payload_merkle=%s|w_self_adjoint=PASS|json=0\n" % (len(pl), root)
    return line.encode().ljust(4096, b"\0") + pl


def run():
    r = subprocess.run([EXE, TMP, "0", "1000"], capture_output=True, text=True)
    last = [x for x in r.stdout.splitlines() if x.startswith("ALLPAIRS|")][-1]
    return r.returncode, dict(x.split("=", 1) for x in last.split("|") if "=" in x)


for size in [len(ROWS), 16 * MIB - 8, 16 * MIB, 16 * MIB + 8, 64 * MIB - 8, 64 * MIB, 64 * MIB + 8, 128 * MIB]:
    pl = ROWS.ljust(size, b"\0")
    root = merkle(pl)
    with open(TMP, "wb") as o:
        o.write(wrap(pl, root))
    code, f = run()
    ok = code == 0 and f.get("verdict") == "PASS" and f.get("merkle") == "PASS"
    bad += 0 if ok else 1
    log.write("SIZE|payload_bytes=%d|exit=%d|verdict=%s|ok=%d|json=0\n" % (size, code, f.get("verdict"), int(ok)))
    # A changed byte at the last position, and on each side of the first leaf and chunk edge, merkle left as it was.
    for pos in sorted({size - 1, 16 * MIB - 1, 16 * MIB, 64 * MIB - 1, 64 * MIB}):
        if pos < len(ROWS) or pos >= size:
            continue
        with open(TMP, "r+b") as o:
            o.seek(4096 + pos)
            o.write(b"\x01")
        code, f = run()
        ok = code == 1 and f.get("verdict") == "FAIL" and "merkle" in f.get("reason", "")
        bad += 0 if ok else 1
        log.write("SIZE_BYTE|payload_bytes=%d|changed_at=%d|exit=%d|ok=%d|json=0\n" % (size, pos, code, int(ok)))
        with open(TMP, "r+b") as o:
            o.seek(4096 + pos)
            o.write(b"\x00")
os.remove(TMP)
log.write("SIZES_DONE|failed=%d|json=0\n" % bad)
log.close()
print("SIZES_DONE|failed=%d" % bad)
sys.exit(1 if bad else 0)
