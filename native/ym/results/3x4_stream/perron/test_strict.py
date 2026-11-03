# Controls for check_d_strict.py on the 3x3 store. Each damaged case must exit 2 with no CHECK_D_STRICT row, with and
# without -O. Predictions are the expected reason for each case. json=0.
import array, hashlib, shutil, struct, subprocess, sys

RD = "D:/ym-3x4-room-run/p0-ball"
W = RD + "/rev1"
STORE = RD + "/c33/dev33.bin"
DV = RD + "/pc33-final/d76000000.bin"
TOOL = RD + "/check_d_strict.py"
PY = sys.executable
GOOD = "t_cert_milli=76041088|t_cert_JE=76041088/1000000|min_row=275450|min_mag=3|"
bad = 0


def run(flags, *args):
    return subprocess.run([PY, "-I", *flags, TOOL, *args], capture_output=True, text=True)


def say(s):
    print(s, flush=True)


# Good runs must agree with the recorded value, with and without -O, and with both optional checks on.
for flags in ([], ["-O"]):
    r = run(flags, STORE, DV, "1000", "9000", "--self-adjoint", "27")
    ok = r.returncode == 0 and GOOD in r.stdout and "row_sums_zero=PASS" in r.stdout and "W_self_adjoint=PASS" in r.stdout and "merkle=PASS" in r.stdout
    say(f"STRICT_GOOD|flags={'-O' if flags else 'none'}|ok={int(ok)}|{r.stdout.strip()[:330]}|json=0")
    bad += 0 if ok else 1


def locate():
    """Offsets in the 3x3 store of: a payload byte, row 1's first off-diagonal entry z, and row 1's diagonal z."""
    f = open(STORE, "rb")
    f.seek(4096)
    w, mag, cnt = struct.unpack("<IHH", f.read(8))
    off = 4096 + 8 + 8 * cnt  # row 1 header
    f.seek(off)
    w, mag, cnt = struct.unpack("<IHH", f.read(8))
    offd, dia = None, None
    for k in range(cnt):
        pos = off + 8 + 8 * k
        f.seek(pos)
        j, z = struct.unpack("<Ii", f.read(8))
        if j == 1:
            dia = pos + 4
        elif offd is None and z < 0:
            offd = pos + 4
    f.close()
    return off, offd, dia


row1, offd, dia = locate()


def damaged(name, patch):
    p = f"{W}/bad-{name}.bin"
    shutil.copyfile(STORE, p)
    with open(p, "r+b") as f:
        patch(f)
    return p


def set_i32(pos, v):
    return lambda f: (f.seek(pos), f.write(struct.pack("<i", v)))


def add_i32(pos, dv):
    def go(f):
        f.seek(pos)
        z = struct.unpack("<i", f.read(4))[0]
        f.seek(pos)
        f.write(struct.pack("<i", z + dv))
    return go


def flip(pos):
    def go(f):
        f.seek(pos)
        b = f.read(1)
        f.seek(pos)
        f.write(bytes([b[0] ^ 1]))
    return go


# A byte late in the payload, in an entry's z high bytes would trip other tests first, so flip the weight of row 2000 region
# by locating a padding-free payload byte that keeps structure: the low byte of a row weight changes only the merkle.
f = open(STORE, "rb")
f.seek(4096)
pos = 4096
for _ in range(2000):
    f.seek(pos)
    w, mag, cnt = struct.unpack("<IHH", f.read(8))
    pos += 8 + 8 * cnt
f.close()
weight_row = pos

cases = [
    ("merkle", damaged("merkle", flip(weight_row)), DV, "merkle"),
    ("positive_offdiag", damaged("posoff", set_i32(offd, 1)), DV, "positive_offdiag_row_1"),
    ("row_sum", damaged("rowsum", add_i32(dia, 1)), DV, "row_sum_not_zero_row_1"),
]
d = array.array("q")
d.frombytes(open(DV, "rb").read())
nonflat = next(i for i in range(len(d)) if d[i] != 0)
flat = next(i for i in range(len(d)) if d[i] == 0)
for name, change in (("neg_d", (nonflat, -5)), ("flat_d", (flat, 7))):
    e = array.array("q", d)
    e[change[0]] = change[1]
    path = f"{W}/bad-{name}.dbin"
    open(path, "wb").write(e.tobytes())
    cases.append((name, STORE, path, "nonpositive_d_row" if name == "neg_d" else "flat_d_nonzero_row"))
# Swapped d: two entries exchanged. The certificate stays valid but weaker, and the expected-hash option stops it.
e = array.array("q", d)
tight = 275450
partner = next(i for i in range(len(d)) if d[i] != 0 and d[i] < d[tight] // 1000)
e[tight], e[partner] = e[partner], e[tight]
swapped = f"{W}/bad-swapped.dbin"
open(swapped, "wb").write(e.tobytes())
good_sha = hashlib.sha256(d.tobytes()).hexdigest()
r = run([], STORE, swapped, "1000", "9000")
weaker = r.returncode == 0 and "CHECK_D_STRICT" in r.stdout and "t_cert_milli=76041088|" not in r.stdout and good_sha not in r.stdout
say(f"STRICT_SWAP|case=value_and_hash_change|exit={r.returncode}|ok={int(weaker)}|{r.stdout.strip()[:30]}|json=0")
bad += 0 if weaker else 1
cases.append(("swapped_d_with_expected_hash", STORE, swapped, "d_sha256_mismatch"))
short = f"{W}/bad-short.dbin"
open(short, "wb").write(d[:-1].tobytes())
cases.append(("d_length", STORE, short, "d_length"))
for name, store, dv, want in cases:
    for flags in ([], ["-O"]):
        extra = ["--expect-d-sha256", good_sha] if name == "swapped_d_with_expected_hash" else []
        r = run(flags, store, dv, "1000", "9000", *extra)
        ok = r.returncode == 2 and want in r.stdout and "CHECK_D_STRICT" not in r.stdout
        say(f"STRICT_BAD|case={name}|flags={'-O' if flags else 'none'}|exit={r.returncode}|expected={want}|ok={int(ok)}|{r.stdout.strip()[:80]}|json=0")
        bad += 0 if ok else 1
# A broken symmetric pair with the row sum kept at zero: only the self-adjoint test can see it.
sym = damaged("sym", lambda f: (add_i32(offd, -1)(f), add_i32(dia, 1)(f)))
with open(sym, "r+b") as f:
    head = f.read(4096)
    fld = dict(x.split("=", 1) for x in head[: head.index(bytes([10]))].decode().split("|")[1:] if "=" in x)
    left = int(fld["payload_bytes"])
    shas = bytearray()
    while left > 0:
        c = f.read(min(16 * 1048576, left))
        shas += hashlib.sha256(c).hexdigest().encode()
        left -= len(c)
    f.seek(0)
    f.write(head.replace(fld["payload_merkle"].encode(), hashlib.sha256(bytes(shas)).hexdigest().encode()))
r0 = run([], sym, DV, "1000", "9000")
r = run([], sym, DV, "1000", "9000", "--self-adjoint", "27")
ok = r0.returncode == 0 and r.returncode == 2 and "not_W_self_adjoint" in r.stdout
say(f"STRICT_BAD|case=self_adjoint_with_merkle_rewritten|exit_without_test={r0.returncode}|exit_with_test={r.returncode}|ok={int(ok)}|{r.stdout.strip()[:80]}|json=0")
bad += 0 if ok else 1
say(f"STRICT_CONTROLS|failed={bad}|json=0")
sys.exit(1 if bad else 0)
