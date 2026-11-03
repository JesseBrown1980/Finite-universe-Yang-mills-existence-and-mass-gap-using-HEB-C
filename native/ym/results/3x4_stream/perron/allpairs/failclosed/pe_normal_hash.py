# The MSVC linker stamps each Windows build with its link time and a fresh PDB GUID, so two builds of one source hash differently.
# This hashes a PE file with those fields zeroed: the COFF time stamp, the time stamp of each debug directory entry, and the GUID and age
# of the CodeView record. Two builds that print the same normal_sha256 differ in those fields and nowhere else.
#
# usage: pe_normal_hash.py EXE [EXE ...]     Exits 1 if the files do not all give one normal_sha256. Integer only, json=0.
import hashlib, struct, sys


def fields(b):
    """Yields (offset, length, name) for each stamped field."""
    pe = struct.unpack_from("<I", b, 0x3C)[0]
    if b[pe:pe + 4] != b"PE\0\0":
        raise SystemExit("not a PE file")
    yield pe + 8, 4, "coff_timestamp"
    nsec = struct.unpack_from("<H", b, pe + 6)[0]
    opt = pe + 24
    optsize = struct.unpack_from("<H", b, pe + 20)[0]
    if struct.unpack_from("<H", b, opt)[0] != 0x20B:
        raise SystemExit("not PE32+")
    dbg_rva, dbg_size = struct.unpack_from("<II", b, opt + 112 + 6 * 8)
    if dbg_size % 28:
        raise SystemExit("debug directory size")
    secs = []
    p = opt + optsize
    for _ in range(nsec):
        vs, va, rs, rp = struct.unpack_from("<IIII", b, p + 8)
        secs.append((va, max(vs, rs), rp))
        p += 40

    def off(rva):
        for va, size, rp in secs:
            if va <= rva < va + size:
                return rva - va + rp
        raise SystemExit("rva outside the sections")

    d = off(dbg_rva)
    for k in range(dbg_size // 28):
        e = d + 28 * k
        yield e + 4, 4, "debug_timestamp"
        kind = struct.unpack_from("<I", b, e + 12)[0]
        raw = struct.unpack_from("<I", b, e + 24)[0]
        if kind == 2:
            if b[raw:raw + 4] != b"RSDS":
                raise SystemExit("codeview record")
            yield raw + 4, 20, "rsds_guid_and_age"


hashes = set()
for path in sys.argv[1:]:
    b = bytearray(open(path, "rb").read())
    raw = hashlib.sha256(b).hexdigest()
    names = {}
    for at, n, name in list(fields(bytes(b))):
        b[at:at + n] = bytes(n)
        names[name] = names.get(name, 0) + n
    normal = hashlib.sha256(b).hexdigest()
    hashes.add(normal)
    print("PE_NORMAL|file_sha256=%s|bytes=%d|zeroed=%s|normal_sha256=%s|json=0" % (raw, len(b), ",".join("%s:%d" % kv for kv in sorted(names.items())), normal))
print("PE_NORMAL_COMPARE|files=%d|distinct_normal=%d|json=0" % (len(sys.argv) - 1, len(hashes)))
sys.exit(0 if len(hashes) == 1 else 1)
