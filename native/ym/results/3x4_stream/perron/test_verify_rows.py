# Controls for verify_sample_rows.py on the 2x3 store. Each damaged copy has its merkle rewritten, so only the row rebuild can
# catch it. Each must exit 2 with the predicted reason and print no VERIFY_ROWS row, with and without -O. json=0.
import hashlib, shutil, struct, subprocess, sys

RD = "D:/ym-3x4-room-run/p0-ball"
W = RD + "/rev1"
S = RD + "/small/2x3"
TOOL = RD + "/verify_sample_rows.py"
PY = sys.executable
MIB = 1048576
ROW = 100  # a non-flat row
bad = 0


def say(s):
    print(s, flush=True)


def offsets():
    f = open(S + "/dev.bin", "rb")
    pos = 4096
    for _ in range(ROW):
        f.seek(pos)
        w, mag, cnt = struct.unpack("<IHH", f.read(8))
        pos += 8 + 8 * cnt
    f.seek(pos)
    w, mag, cnt = struct.unpack("<IHH", f.read(8))
    offd, dia, last = None, None, None
    for k in range(cnt):
        p = pos + 8 + 8 * k
        f.seek(p)
        j, z = struct.unpack("<Ii", f.read(8))
        if j == ROW:
            dia = p + 4
        else:
            if offd is None and z < 0:
                offd = p + 4
            last = p
    f.close()
    return pos, w, mag, offd, dia, last


pos, w, mag, offd, dia, last = offsets()


def remerkle(path):
    with open(path, "r+b") as f:
        head = f.read(4096)
        fld = dict(x.split("=", 1) for x in head[: head.index(bytes([10]))].decode().split("|")[1:] if "=" in x)
        left = int(fld["payload_bytes"])
        shas = bytearray()
        while left > 0:
            c = f.read(min(16 * MIB, left))
            shas += hashlib.sha256(c).hexdigest().encode()
            left -= len(c)
        f.seek(0)
        f.write(head.replace(fld["payload_merkle"].encode(), hashlib.sha256(bytes(shas)).hexdigest().encode()))


def case(name, patch_store, patch_table, want):
    global bad
    store, table = f"{W}/v-{name}.bin", f"{W}/v-{name}.pa"
    shutil.copyfile(S + "/dev.bin", store)
    shutil.copyfile(S + "/passa.bin", table)
    if patch_store:
        with open(store, "r+b") as f:
            patch_store(f)
        remerkle(store)
    if patch_table:
        with open(table, "r+b") as f:
            patch_table(f)
    for flags in ([], ["-O"]):
        r = subprocess.run([PY, "-I", *flags, TOOL, "2", "3", store, table, "--per-M", "2", "--per-sector", "0", "--uniform", "2", "--rows", str(ROW)], capture_output=True, text=True)
        ok = r.returncode == 2 and want in r.stdout and "VERIFY_ROWS|" not in r.stdout
        say(f"VERIFY_BAD|case={name}|flags={'-O' if flags else 'none'}|exit={r.returncode}|expected={want}|ok={int(ok)}|{r.stdout.strip()[:90]}|json=0")
        bad += 0 if ok else 1


def add32(pos_, dv):
    def go(f):
        f.seek(pos_)
        z = struct.unpack("<i", f.read(4))[0]
        f.seek(pos_)
        f.write(struct.pack("<i", z + dv))
    return go


def both(*fs):
    return lambda f: [g(f) for g in fs]


def set_u32(pos_, v):
    return lambda f: (f.seek(pos_), f.write(struct.pack("<I", v)))


def set_u16(pos_, v):
    return lambda f: (f.seek(pos_), f.write(struct.pack("<H", v)))


T = 16 * ROW
case("row_entry", both(add32(offd, -1), add32(dia, 1)), None, f"row_differs_row_{ROW}")
case("row_target", lambda f: (f.seek(last), f.write(struct.pack("<I", struct.unpack("<I", (f.seek(last), f.read(4))[1])[0] + 1))), None, f"row_differs_row_{ROW}")
case("store_weight_only", set_u32(pos, w + 1), None, f"key_table_and_store_differ_row_{ROW}")
case("weight_in_both", set_u32(pos, w + 6), set_u32(T + 8, w + 6), f"weight_row_{ROW}")
case("magnetic_in_both", set_u16(pos + 4, mag + 1), set_u32(T + 12, mag + 1), f"magnetic_number_row_{ROW}")


# A key moved to a code in the same orbit, so M and the weight still match and only the least-key test can see it.
_src = open(TOOL, encoding="utf-8").read()
_ns = {"__name__": "tool"}
exec(_src[: _src.rindex("main()")], _ns)
_lat = _ns["Lattice"](2, 3)
_pa = open(S + "/passa.bin", "rb").read()
_keys = [struct.unpack_from("<Q", _pa, 16 * i)[0] for i in range(len(_pa) // 16)]
GAP, CODE = None, None
for i in range(ROW, len(_keys) - 1):
    between = [c for c in _lat.orbit_codes(_lat.links_from_key(_keys[i])) if _keys[i] < c < _keys[i + 1]]
    if between:
        GAP, CODE = i, between[0]
        break


def move_key(f):
    f.seek(16 * GAP)
    f.write(struct.pack("<Q", CODE))


ROW_SAVED = ROW
ROW = GAP
case("key_not_least", None, move_key, f"key_is_not_the_least_in_its_orbit_row_{GAP}")
ROW = ROW_SAVED


say(f"VERIFY_CONTROLS|failed={bad}|json=0")
sys.exit(1 if bad else 0)
