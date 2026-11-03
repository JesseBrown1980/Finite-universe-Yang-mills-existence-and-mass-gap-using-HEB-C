# Puts one fault at a time into a small copy of the 2x2 store, with every hash repaired, and runs three checkers on it: the outside
# seat's Go checker at its pinned source, check_d_strict.py, and allpairs. The public store is never touched.
#
# usage: run_fixture_controls.py --base fixture-2x2.rooms.gz --out DIR [--predict-only] [--go EXE --strict PY --allpairs EXE]
#
# Faults, each with the merkle, the sector hash and the manifest recomputed, so a checker's later gates can see it:
#   rowsum  diagonal+1 on one row. Row sums break, every pair holds.
#   pair    z-1 on one off-diagonal and diagonal+1 on the same row. That pair breaks, the row sums hold.
# Every row gets the row-sum fault and every unordered pair gets the pair fault, on the pair's non-flat end.
# The Go checker's form gives (w_h z_hj - w_j z_jh)(x_h y_j - y_h x_j) for one bad pair, with x, y its own SplitMix64 values in -3..3,
# so this file predicts from those values which pairs it reports, and its exact residual. Writes FIXTURE-CONTROLS.hbp. Fails closed.
# Integer only, json=0.
import gzip, hashlib, os, struct, subprocess, sys, tempfile

BASE_SHA = "b31e730606db130585f9560f7adab87444d744876c3a8e36f6f9ef2bf0aa431f"
GO_SEED = 0x79D8C82AEA6808DE
M64 = (1 << 64) - 1
JE, JB = 1000, 9000


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def sha(b):
    return hashlib.sha256(b).hexdigest()


def go_seeded(i):
    x = (i ^ GO_SEED) & M64
    out = []
    for _ in range(2):
        x = (x + 0x9E3779B97F4A7C15) & M64
        z = x
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
        out.append(((z ^ (z >> 31)) % 7) - 3)
    return out[0], out[1]


base = bytearray(gzip.open(arg("--base"), "rb").read())
if sha(base) != BASE_SHA:
    raise SystemExit("fixture hash")
end = base.index(b"\n")
LINE = base[:end].decode()
FLD = dict(x.split("=", 1) for x in LINE.split("|") if "=" in x)
N, PAYLOAD, ROOMS = int(FLD["n"]), int(FLD["payload_bytes"]), int(FLD["rooms"])
PADDING = PAYLOAD - 8 * ROOMS
TAIL = len(base) - 4096 - PAYLOAD
if PADDING < 0 or TAIL != 0:
    raise SystemExit("fixture layout")
rows, p = [], 4096
for h in range(N):
    w, mag, cnt = struct.unpack_from("<IHH", base, p)
    ents = [struct.unpack_from("<Ii", base, p + 8 + 8 * k) + (p + 8 + 8 * k,) for k in range(cnt)]
    rows.append((w, mag, ents))
    p += 8 + 8 * cnt
flat = {h for h, r in enumerate(rows) if r[1] == 0}
control = [0 if h in flat else 1 for h in range(N)]
blind = [0 if h in flat else 1 + h % 5 for h in range(N)]


def vec_bytes(d):
    return b"".join(struct.pack("<q", v) for v in d)


def value(d):
    best = None
    for h, (w, mag, ents) in enumerate(rows):
        if mag == 0:
            continue
        t = 1000 * JB * mag * d[h] + 1000 * JE * sum(z * d[j] for j, z, _ in ents)
        q = t // d[h]
        if best is None or q < best[0]:
            best = (q, h, mag)
    return best


zmap = {(h, j): z for h, r in enumerate(rows) for j, z, _ in r[2]}
pairs = sorted((h, j) for (h, j) in zmap if h < j)
for h, j in pairs:
    if (j, h) not in zmap or rows[h][0] * zmap[(h, j)] != rows[j][0] * zmap[(j, h)]:
        raise SystemExit("fixture is not W-self-adjoint")
if any((h in flat and j in flat) for h, j in pairs):
    raise SystemExit("flat-flat coupling in the fixture")
if sum(1 for k in zmap if k[0] > k[1]) != len(pairs):
    raise SystemExit("pair count")


def nonflat_end(h, j):
    return (j, h) if h in flat else (h, j)


def go_factor(h, j):
    xh, yh = go_seeded(h)
    xj, yj = go_seeded(j)
    return xh * yj - yh * xj


def go_residual(h, j):
    # z_hj falls by 1, so the form moves by w_h * (-1) * factor. The diagonal's factor is 0.
    return -rows[h][0] * go_factor(h, j)


go_escapes = [(h, j) for h, j in pairs if go_factor(h, j) == 0]
CONTROL_V, BLIND_V = value(control), value(blind)
PRED = "FIXTURE_PREDICTION|base_sha256=%s|n=%d|pairs=%d|go_pairs_reported=%d|go_pairs_passed=%d|strict_pairs_reported=%d|allpairs_pairs_reported=%d|rows=%d|control=%d,%d,%d|blind=%d,%d,%d|json=0" % (
    BASE_SHA, N, len(pairs), len(pairs) - len(go_escapes), len(go_escapes), len(pairs), len(pairs), N, *CONTROL_V, *BLIND_V)
print(PRED)
if "--predict-only" in sys.argv:
    print("FIXTURE_ESCAPES|first_five=%s|json=0" % ";".join("%d,%d" % x for x in go_escapes[:5]))
    sys.exit(0)

os.makedirs(arg("--out"), exist_ok=True)
log = open(os.path.join(arg("--out"), "FIXTURE-CONTROLS.hbp"), "w", encoding="utf-8", newline="\n")
GO, STRICT, ALLPAIRS = arg("--go"), arg("--strict"), arg("--allpairs")
fails = 0


def emit(s):
    log.write(s + "\n")
    log.flush()


def met(label, ok, detail):
    global fails
    fails += 0 if ok else 1
    emit("FIXTURE_CASE|%s|met=%d|%s|json=0" % (label, 1 if ok else 0, detail))


def repaired(b):
    pl = bytes(b[4096:4096 + PAYLOAD])
    hx = "".join(sha(pl[i:i + (16 << 20)]) for i in range(0, len(pl), 16 << 20))
    root = sha(hx.encode())
    new = LINE.replace("payload_merkle=" + FLD["payload_merkle"], "payload_merkle=" + root)
    if len(new) != len(LINE):
        raise SystemExit("header length")
    out = bytearray(b)
    out[:end] = new.encode()
    return out, root


def bumped(pos_dz):
    b = bytearray(base)
    for pos, dz in pos_dz:
        j, z = struct.unpack_from("<Ii", b, pos)
        struct.pack_into("<Ii", b, pos, j, z + dz)
    return repaired(b)


def fault_rowsum(h):
    pos = next(x[2] for x in rows[h][2] if x[0] == h)
    return bumped([(pos, 1)])


def fault_pair(h, j):
    pos = next(x[2] for x in rows[h][2] if x[0] == j)
    dia = next(x[2] for x in rows[h][2] if x[0] == h)
    return bumped([(pos, -1), (dia, 1)])


tmp = tempfile.mkdtemp(prefix="fixture-")
cpath, bpath = os.path.join(tmp, "control.bin"), os.path.join(tmp, "blind.bin")
open(cpath, "wb").write(vec_bytes(control))
open(bpath, "wb").write(vec_bytes(blind))
CSHA, BSHA = sha(vec_bytes(control)), sha(vec_bytes(blind))
SECTOR = os.path.join(tmp, "sector-341.rooms")
MANIFEST = os.path.join(tmp, "SECTORS-341-374.sha256")


def run_go(store, root):
    open(SECTOR, "wb").write(store)
    text = ("%s  sector-341.rooms\n" % sha(store)).encode()
    open(MANIFEST, "wb").write(text)
    r = subprocess.run([GO, "-fixture", "-dir", tmp, "-control", cpath, "-blind", bpath, "-n", str(N), "-payload-bytes", str(PAYLOAD), "-manifest-sha", sha(text), "-merkle-sha", root, "-control-sha", CSHA, "-blind-sha", BSHA, "-sectors", "1", "-expected-padding", str(PADDING), "-expected-raw-tail", "0", "-expected-raw-tail-nonzero", "0"], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr.strip()


def run_strict(store):
    open(SECTOR, "wb").write(store)
    r = subprocess.run([sys.executable, "-I", STRICT, SECTOR, cpath, str(JE), str(JB), "--self-adjoint", "27"], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr.strip()


def run_allpairs(store):
    open(SECTOR, "wb").write(store)
    r = subprocess.run([ALLPAIRS, SECTOR, "0"], capture_output=True, text=True)
    row = [x for x in r.stdout.splitlines() if x.startswith("ALLPAIRS|")]
    f = dict(x.split("=", 1) for x in (row[-1] if row else "").split("|") if "=" in x)
    return r.returncode, f


# Clean store: all three pass and print the predicted values.
store, root = repaired(base)
if root != FLD["payload_merkle"]:
    raise SystemExit("merkle recipe")
code, out, err = run_go(store, root)
want = ("PASS merkle=PASS sector_hashes=PASS vector_hashes=PASS row_sums_zero=PASS W_self_adjoint=PASS" in out
        and "control t_cert_milli=%d min_row=%d min_mag=%d" % CONTROL_V in out
        and "blind t_cert_milli=%d min_row=%d min_mag=%d" % BLIND_V in out
        and "weighted_residual=0" in out)
met("tool=go|case=clean", code == 0 and want, "exit=%d" % code)
emit("GO_CLEAN_STDOUT|" + out.replace("\n", ";"))
code, out, err = run_strict(store)
met("tool=strict|case=clean", code == 0 and "|t_cert_milli=%d|" % CONTROL_V[0] in out and "|W_self_adjoint=PASS|" in out, "exit=%d" % code)
emit("STRICT_CLEAN_STDOUT|" + out.strip())
code, f = run_allpairs(store)
met("tool=allpairs|case=clean", code == 0 and f.get("verdict") == "PASS" and f.get("pairs") == str(len(pairs)), "exit=%d" % code)

# Row-sum gate, on every row.
counts = {"go": 0, "strict": 0, "allpairs": 0}
for h in range(N):
    store, root = fault_rowsum(h)
    code, out, err = run_go(store, root)
    ok = code != 0 and out == "" and err == "FAIL: row %d has sum(z)=1 not zero" % h
    counts["go"] += ok
    if not ok:
        met("tool=go|case=rowsum|row=%d" % h, False, "exit=%d|%s" % (code, err[:120]))
    code, out, err = run_strict(store)
    reason = "flat_diagonal_row_%d" % h if h in flat else "row_sum_not_zero_row_%d" % h
    ok = code == 2 and reason in out and "CHECK_D_STRICT|" not in out
    counts["strict"] += ok
    if not ok:
        met("tool=strict|case=rowsum|row=%d" % h, False, "exit=%d|%s" % (code, out[:120]))
    code, f = run_allpairs(store)
    ok = code == 2 and f.get("row_sum_nonzero") == "1" and f.get("value_mismatch") == "0" and f.get("verdict") == "FAIL"
    counts["allpairs"] += ok
    if not ok:
        met("tool=allpairs|case=rowsum|row=%d" % h, False, "exit=%d" % code)
for t in counts:
    met("tool=%s|sweep=rowsum" % t, counts[t] == N, "rows=%d|reported=%d" % (N, counts[t]))

# Pair gate, on every unordered pair.
reported = {"go": 0, "strict": 0, "allpairs": 0}
go_passed, go_wrong = 0, 0
first_escape, first_caught = None, None
for lo, hi in pairs:
    h, j = nonflat_end(lo, hi)
    store, root = fault_pair(h, j)
    code, out, err = run_go(store, root)
    factor = go_factor(h, j)
    if factor != 0:
        ok = code != 0 and out == "" and err == "FAIL: weighted self-adjoint integer residual=%d" % go_residual(h, j)
        reported["go"] += ok
        go_wrong += 0 if ok else 1
        if first_caught is None:
            first_caught = (h, j, err)
    else:
        ok = code == 0 and "W_self_adjoint=PASS" in out and "weighted_residual=0" in out
        go_passed += ok
        go_wrong += 0 if ok else 1
        if first_escape is None:
            first_escape = (h, j, out.splitlines()[0] if out else err)
    if not ok:
        met("tool=go|case=pair|h=%d|j=%d" % (h, j), False, "exit=%d|%s" % (code, err[:120]))
    code, out, err = run_strict(store)
    ok = code == 2 and "not_W_self_adjoint" in out and "CHECK_D_STRICT|" not in out
    reported["strict"] += ok
    if not ok:
        met("tool=strict|case=pair|h=%d|j=%d" % (h, j), False, "exit=%d|%s" % (code, out[:120]))
    code, f = run_allpairs(store)
    ok = code == 2 and f.get("value_mismatch") == "1" and f.get("row_sum_nonzero") == "0" and f.get("verdict") == "FAIL"
    reported["allpairs"] += ok
    if not ok:
        met("tool=allpairs|case=pair|h=%d|j=%d" % (h, j), False, "exit=%d" % code)
met("tool=go|sweep=pair", reported["go"] == len(pairs) - len(go_escapes) and go_passed == len(go_escapes) and go_wrong == 0, "pairs=%d|reported=%d|passed=%d|as_predicted=%d" % (len(pairs), reported["go"], go_passed, len(pairs) - go_wrong))
met("tool=strict|sweep=pair", reported["strict"] == len(pairs), "pairs=%d|reported=%d" % (len(pairs), reported["strict"]))
met("tool=allpairs|sweep=pair", reported["allpairs"] == len(pairs), "pairs=%d|reported=%d" % (len(pairs), reported["allpairs"]))
if first_caught:
    emit("GO_FIRST_REPORTED|h=%d|j=%d|stderr=%s" % first_caught)
if first_escape:
    emit("GO_FIRST_PASSED|h=%d|j=%d|stdout=%s" % first_escape)
emit(PRED)
emit("FIXTURE_CONTROLS_DONE|failed=%d|json=0" % fails)
log.close()
print("FIXTURE_CONTROLS_DONE|failed=%d|json=0" % fails)
sys.exit(1 if fails else 0)
