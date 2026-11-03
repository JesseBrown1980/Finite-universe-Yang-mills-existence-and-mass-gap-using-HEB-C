# Controls for the fix of H1, H2 and H4 of the second seat's review, part three. Each runs on the hardened executable at 9c2c7e6 and on the fixed one, and every outcome is predicted
# here before any run. The race and the store of equal columns follow that review's hard/race.py and hard/shapes.py, written here to run on Linux as well.
#
# usage: run_oneread_controls.py --base fixture-2x2.rooms.gz --out DIR --old EXE --new EXE [--runs N] [--host local|hosted]
#
#   race     A writer toggles the header block on a copy between the trusted block and the same block with the changed store's merkle, while the tool runs on a store with one pair changed.
#            New: exit 0 in 0 of N. Old: at least 1 of N here on this seat's machine, recorded without a prediction on a hosted runner, whose core count differs.
#            With no writer, on both: the trusted block exits 1, and the changed block exits 2.
#   columns  65,534 equal columns on both sides of one pair: exit 2 on both, with the counters of the review's table. The new tool in at most a tenth of the old tool's time.
#   offset   The real 2x2 stream after 8,192 bytes of junk, at OFFSET 8192: exit 0 on both. New: the row prints offset=8192. Old: no offset field.
#   clean    The real 2x2 stream at OFFSET 0: every field of the two final rows the same apart from secs, exe_sha256 and offset=0, and the same pass rows apart from secs.
#
# Writes ONEREAD-CONTROLS.hbp into DIR. Exits 1 if any prediction misses. Integer only, json=0.
import gzip, hashlib, math, os, struct, subprocess, sys, tempfile, time


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


BASE, OUT, OLD, NEW = arg("--base"), arg("--out"), arg("--old"), arg("--new")
RUNS, HOST = int(arg("--runs", "2000")), arg("--host", "local")
BASE_SHA = "b31e730606db130585f9560f7adab87444d744876c3a8e36f6f9ef2bf0aa431f"
MIB = 1 << 20
LEAF = 16 * MIB
os.makedirs(OUT, exist_ok=True)
log = open(os.path.join(OUT, "ONEREAD-CONTROLS.hbp"), "w", encoding="utf-8", newline="\n")
fails = 0


def sha(b):
    return hashlib.sha256(b).hexdigest()


def row(text):
    log.write(text + "\n")
    log.flush()
    print(text)


def met(name, ok, detail=""):
    global fails
    fails += 0 if ok else 1
    row("ONEREAD_CONTROL|%s|met=%d|%sjson=0" % (name, 1 if ok else 0, detail + "|" if detail else ""))


def fields(line):
    return dict(x.split("=", 1) for x in line.split("|") if "=" in x)


def run(exe, path, off="0"):
    t0 = time.perf_counter_ns()
    r = subprocess.run([exe, path, off], capture_output=True, text=True)
    ms = (time.perf_counter_ns() - t0) // 1000000
    rows = r.stdout.splitlines()
    last = ([x for x in rows if x.startswith("ALLPAIRS|")] or [""])[-1]
    return r.returncode, fields(last), rows, ms


raw = gzip.open(BASE, "rb").read()
if sha(raw) != BASE_SHA:
    raise SystemExit("the fixture differs")
row("ONEREAD_TOOLS|host=%s|old_sha256=%s|new_sha256=%s|runs=%d|json=0" % (HOST, sha(open(OLD, "rb").read()), sha(open(NEW, "rb").read()), RUNS))
eol = raw.index(b"\n")
LINE = raw[:eol].decode()
F = fields(LINE)
N, PAY = int(F["n"]), int(F["payload_bytes"])
P = raw[4096:4096 + PAY]
tmp = tempfile.mkdtemp(prefix="oneread-")

# clean
path = os.path.join(tmp, "clean.bin")
open(path, "wb").write(raw)
co, fo, ro, _ = run(OLD, path)
cn, fn, rn, _ = run(NEW, path)
keep = lambda f: {k: v for k, v in f.items() if k not in ("secs", "exe_sha256", "offset")}
passes = lambda rows: [{k: v for k, v in fields(x).items() if k != "secs"} for x in rows if x.startswith("ALLPAIRS_PASS|")]
met("clean_same_rows", co == 0 and cn == 0 and keep(fo) == keep(fn) and passes(ro) == passes(rn) and "offset" not in fo and fn.get("offset") == "0", "old_exit=%d|new_exit=%d|new_offset=%s" % (co, cn, fn.get("offset", "-")))

# offset
path = os.path.join(tmp, "prefix.bin")
open(path, "wb").write(b"\xCD" * 8192 + raw)
co, fo, _, _ = run(OLD, path, "8192")
cn, fn, _, _ = run(NEW, path, "8192")
met("offset_printed", co == 0 and cn == 0 and "offset" not in fo and fn.get("offset") == "8192", "old_exit=%d|new_exit=%d|new_offset=%s" % (co, cn, fn.get("offset", "-")))

# columns
k = 65534


def pair_rows(a, b, k):
    ra = struct.pack("<IHH", 1, 3, k + 1) + struct.pack("<Ii", a, k) + struct.pack("<Ii", b, -1) * k
    rb = struct.pack("<IHH", 1, 3, k + 1) + struct.pack("<Ii", a, -1) * k + struct.pack("<Ii", b, k)
    return ra + rb


body = pair_rows(0, 1, k)
pad = (MIB - (len(body) + 4096) % MIB) % MIB
pl = body + b"\0" * pad
merkle = sha("".join(sha(pl[i:i + LEAF]) for i in range(0, len(pl), LEAF)).encode())
line = "YMROOMHDR|L=1x40|sector=x|n=2|rooms=%d|entries=%d|payload_bytes=%d|stream_bytes=%d|chunk=16MiB|payload_merkle=%s|keys_sha256=0|w_self_adjoint=PASS|json=0" % (len(body) // 8, 2 * (k + 1), len(pl), len(pl) + 4096, merkle)
path = os.path.join(tmp, "columns.bin")
open(path, "wb").write(line.encode() + b"\n" + b"\0" * (4096 - len(line) - 1) + pl)
co, fo, _, mo = run(OLD, path)
cn, fn, _, mn = run(NEW, path)
want = {"columns_not_ascending": "131066", "value_mismatch": "0", "lower_without_upper": "0", "upper_without_lower": "0", "lower_repeated": "0"}
same = all(fo.get(a) == b and fn.get(a) == b for a, b in want.items())
met("columns_same_counters", co == 2 and cn == 2 and same, "old_exit=%d|new_exit=%d|columns_not_ascending=%s,%s" % (co, cn, fo.get("columns_not_ascending", "-"), fn.get("columns_not_ascending", "-")))
met("columns_time_at_most_a_tenth", 10 * mn <= mo, "old_ms=%d|new_ms=%d" % (mo, mn))

# race
ROWS, p = [], 0
for _ in range(N):
    w, mag, cnt = struct.unpack_from("<IHH", P, p)
    v = struct.unpack_from("<" + "Ii" * cnt, P, p + 8)
    ROWS.append([w, mag, [(v[2 * i], v[2 * i + 1]) for i in range(cnt)]])
    p += 8 + 8 * cnt
h, i = next((h, j) for h in range(N) for j, _ in ROWS[h][2] if j < h)
g = math.gcd(ROWS[h][0], ROWS[i][0])
for rw, col, d in ((h, i, ROWS[i][0] // g), (i, h, ROWS[h][0] // g)):
    e = ROWS[rw][2]
    q = [x for x, y in enumerate(e) if y[0] == col][0]
    e[q] = (col, e[q][1] - d)
    q = [x for x, y in enumerate(e) if y[0] == rw][0]
    e[q] = (rw, e[q][1] + d)
buf = bytearray()
for w, mag, ent in ROWS:
    buf += struct.pack("<IHH", w, mag, len(ent))
    for j, z in ent:
        buf += struct.pack("<Ii", j, z)
SYM2 = bytes(buf).ljust(PAY, b"\0")
M2 = sha("".join(sha(SYM2[i:i + LEAF]) for i in range(0, len(SYM2), LEAF)).encode())
A = raw[:4096]
B = A.replace(F["payload_merkle"].encode(), M2.encode())
path = os.path.join(tmp, "race.bin")
open(path, "wb").write(A + SYM2)
for exe, name in ((OLD, "old"), (NEW, "new")):
    open(path, "r+b").write(A)
    ca = run(exe, path)[0]
    open(path, "r+b").write(B)
    cb = run(exe, path)[0]
    met("no_writer_%s" % name, ca == 1 and cb == 2, "trusted_block_exit=%d|changed_block_exit=%d" % (ca, cb))
stop = path + ".stop"
writer = """
import os, sys
path, stop, a, b = sys.argv[1], sys.argv[2], bytes.fromhex(sys.argv[3]), bytes.fromhex(sys.argv[4])
f = open(path, "r+b", buffering=0)
k = 0
while True:
    f.seek(0); f.write(b)
    f.seek(0); f.write(a)
    k += 1
    if k % 4096 == 0 and os.path.exists(stop):
        break
"""
wr = subprocess.Popen([sys.executable, "-I", "-c", writer, path, stop, A[:eol + 1].ljust(4096, b"\0").hex(), B[:eol + 1].ljust(4096, b"\0").hex()])
time.sleep(1)
for exe, name in ((OLD, "old"), (NEW, "new")):
    tally = {}
    for _ in range(RUNS):
        c, f, _, _ = run(exe, path)
        key = (c, f.get("store_identity", "-"))
        tally[key] = tally.get(key, 0) + 1
    zero = sum(v for k_, v in tally.items() if k_[0] == 0)
    text = ";".join("exit_%d_identity_%s=%d" % (k_[0], k_[1], v) for k_, v in sorted(tally.items()))
    if name == "new":
        met("race_new_never_exits_0", zero == 0, "runs=%d|exit0=%d|%s" % (RUNS, zero, text))
    elif HOST == "local":
        met("race_old_shows_the_defect", zero >= 1, "runs=%d|exit0=%d|%s" % (RUNS, zero, text))
    else:
        row("ONEREAD_RACE_OLD_MEASURED|host=%s|runs=%d|exit0=%d|%s|json=0" % (HOST, RUNS, zero, text))
open(stop, "w").close()
wr.wait(timeout=60)
for name in os.listdir(tmp):
    os.remove(os.path.join(tmp, name))
os.rmdir(tmp)
row("ONEREAD_CONTROLS_DONE|failed=%d|json=0" % fails)
sys.exit(1 if fails else 0)
