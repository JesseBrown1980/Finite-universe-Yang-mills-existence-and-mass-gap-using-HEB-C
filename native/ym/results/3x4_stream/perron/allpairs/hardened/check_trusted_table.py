# Checks the TRUSTED table of allpairs.rs against stores built from the rules and against the public 3x4 store, so the table is checkable without trusting
# the machine that wrote it. For a whole store it compares the 4096-byte block and recomputes the payload merkle. For the 3x4 block it compares the block.
#
# usage: check_trusted_table.py SOURCE_RS [--store L PATH]... [--block L PATH]...   Fails closed. Integer only, json=0.
import hashlib, re, sys

src = open(sys.argv[1], encoding="utf-8").read()
ROWS = re.findall(r'Trusted \{\s*line: "([^"]+)",\s*header_sha256: "([0-9a-f]{64})",\s*\}', src)
if len(ROWS) != 4:
    raise SystemExit("table rows: %d" % len(ROWS))
TABLE = {dict(x.split("=", 1) for x in line.split("|") if "=" in x)["L"]: (line, h) for line, h in ROWS}
MIB = 1 << 20
fails = 0
checked = set()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def block_row(lattice, block, source):
    global fails
    line, h = TABLE[lattice]
    want = line.encode() + b"\n"
    want += bytes(4096 - len(want))
    same_line = block == want
    same_hash = sha(block) == h
    fails += 0 if same_line and same_hash else 1
    checked.add(lattice)
    print("TRUSTED_CHECK|L=%s|source=%s|block_equals_line=%d|block_sha256_equals_table=%d|header_sha256=%s|json=0" % (lattice, source, 1 if same_line else 0, 1 if same_hash else 0, h))


args = sys.argv[2:]
for i in range(0, len(args), 3):
    kind, lattice, path = args[i], args[i + 1], args[i + 2]
    if kind == "--block":
        block = open(path, "rb").read()
        if len(block) != 4096:
            raise SystemExit("block length")
        block_row(lattice, block, "public_store_first_4096_bytes")
    elif kind == "--store":
        data = open(path, "rb").read()
        block_row(lattice, data[:4096], "rebuilt_from_the_rules_by_ymroom")
        f = dict(x.split("=", 1) for x in TABLE[lattice][0].split("|") if "=" in x)
        pl = data[4096:4096 + int(f["payload_bytes"])]
        root = sha("".join(sha(pl[j:j + 16 * MIB]) for j in range(0, len(pl), 16 * MIB)).encode())
        same = root == f["payload_merkle"] and len(data) == int(f["stream_bytes"])
        fails += 0 if same else 1
        print("TRUSTED_CHECK_STORE|L=%s|bytes=%d|merkle_equals_table=%d|json=0" % (lattice, len(data), 1 if same else 0))
    else:
        raise SystemExit("usage")
missing = sorted(set(TABLE) - checked)
fails += len(missing)
print("TRUSTED_TABLE_DONE|rows=%d|checked=%d|missing=%s|failed=%d|json=0" % (len(TABLE), len(checked), ",".join(missing) or "-", fails))
sys.exit(1 if fails else 0)
