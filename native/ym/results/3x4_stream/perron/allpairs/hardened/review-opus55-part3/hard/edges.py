# Attacks roomscan::scan on chunk and leaf edges, with the largest rows, at sizes where a row, the padding or both straddle a 64 MiB chunk or a 16 MiB leaf.
# A Python reader computes every expected value. Stores stay under hard/tmp and are deleted after each case.
# usage: edges.py EXE_A EXE_B OUT  Integer only, json=0.
import hashlib, os, struct, subprocess, sys

EXE_A, EXE_B, OUT = sys.argv[1:4]
TMP = os.path.dirname(os.path.dirname(os.path.abspath(OUT))) + "/tmp/e"
os.makedirs(TMP, exist_ok=True)
MIB = 1 << 20
LEAF = 16 * MIB
CHUNK = 64 * MIB
BN = subprocess.BELOW_NORMAL_PRIORITY_CLASS
log = open(OUT, "w", encoding="utf-8", newline="\n")
bad = 0


def sha(b):
    return hashlib.sha256(b).hexdigest()


def merkle(pl):
    return sha("".join(sha(pl[i:i + LEAF]) for i in range(0, len(pl), LEAF)).encode())


def rows_of(total_bytes, first=0):
    """Rows that fill total_bytes exactly. Every size is 8 + 8*cnt with cnt <= 65535. A first row of that many bytes shifts the large rows off the chunk edges."""
    big = 8 + 8 * 65535
    out, h, left = bytearray(), 0, total_bytes
    while left > 0:
        size = first if first else (big if left >= big else left)
        first = 0
        cnt = (size - 8) // 8
        out += struct.pack("<IHH", 1, 3, cnt)
        for j in range(cnt):
            out += struct.pack("<Ii", 1 << 30 | j, -1)
        h += 1
        left -= size
    assert len(out) == total_bytes
    return bytes(out), h


def case(name, row_bytes, pad_nonzero_at=None, tail=0, first=0):
    global bad
    data, n = rows_of(row_bytes, first)
    rooms = row_bytes // 8
    stream = (row_bytes + 4096 + MIB - 1) // MIB * MIB
    payload = stream - 4096
    pl = bytearray(data) + bytearray(payload - row_bytes)
    if pad_nonzero_at is not None:
        pl[row_bytes + pad_nonzero_at] = 7
    pl = bytes(pl)
    entries = rooms - n
    line = "YMROOMHDR|L=1x40|sector=x|n=%d|rooms=%d|entries=%d|payload_bytes=%d|stream_bytes=%d|chunk=16MiB|payload_merkle=%s|keys_sha256=0|w_self_adjoint=PASS|json=0" % (n, rooms, entries, payload, stream, merkle(pl))
    path = TMP + "/e.bin"
    with open(path, "wb") as o:
        o.write((line + "\n").encode().ljust(4096, b"\0"))
        o.write(pl)
        o.write(b"\xAB" * tail)
    want_pad = payload - row_bytes
    results = []
    for exe in (EXE_A, EXE_B):
        r = subprocess.run([exe, path, "0"], capture_output=True, text=True, creationflags=BN)
        last = ([x for x in r.stdout.splitlines() if x.startswith("ALLPAIRS|")] or [""])[-1]
        f = dict(x.split("=", 1) for x in last.split("|") if "=" in x)
        ok = r.returncode == 2 and f.get("rows_read") == str(n) and f.get("entries") == str(entries) and f.get("padding_bytes") == str(want_pad) and f.get("padding_nonzero") == str(0 if pad_nonzero_at is None else 1) and f.get("padding") == ("PASS" if pad_nonzero_at is None else "FAIL") and f.get("header_rooms") == "PASS" and f.get("merkle") == "PASS" and f.get("bytes_after_stream") == str(tail)
        results.append((r.returncode, f, ok))
    ok = all(x[2] for x in results)
    bad += 0 if ok else 1
    f = results[0][1]
    log.write("EDGE|case=%s|row_bytes=%d|n=%d|payload=%d|exit=%d|rows_read=%s|padding_bytes=%s|padding_nonzero=%s|padding=%s|header_rooms=%s|bytes_after_stream=%s|met=%d|json=0\n" % (name, row_bytes, n, payload, results[0][0], f.get("rows_read", "-"), f.get("padding_bytes", "-"), f.get("padding_nonzero", "-"), f.get("padding", "-"), f.get("header_rooms", "-"), f.get("bytes_after_stream", "-"), int(ok)))
    log.flush()
    os.remove(path)


# Rows end exactly on a chunk, a leaf, one row room short and one past. Stream sizes follow from the multiple-of-1-MiB rule.
case("rows_end_on_the_64MiB_chunk", CHUNK)
case("rows_end_one_room_before_the_chunk", CHUNK - 8)
case("rows_end_one_room_after_the_chunk", CHUNK + 8)
case("rows_end_on_a_16MiB_leaf", LEAF)
case("rows_end_where_the_stream_ends", 2 * MIB - 4096)
case("rows_end_one_room_before_the_stream_ends", 2 * MIB - 4096 - 8)
case("stray_byte_first_padding_byte_on_chunk_edge", CHUNK, pad_nonzero_at=0)
case("stray_byte_last_padding_byte_on_chunk_edge", CHUNK, pad_nonzero_at=MIB - 4096 - 1)
case("stray_byte_first_padding_byte_after_chunk", CHUNK + 8, pad_nonzero_at=0)
case("stray_byte_last_padding_byte", 2 * MIB - 4096 - 8, pad_nonzero_at=7)
case("rows_past_two_chunks_with_a_tail", 2 * CHUNK + 16, tail=33)
# Large rows that straddle the chunk edge, ending on it, and ending just past it.
case("large_rows_straddle_the_chunk", CHUNK + 16, first=16)
case("large_row_straddles_and_rows_end_on_the_next_chunk", 2 * CHUNK, first=16)
case("large_row_straddles_with_a_stray_last_padding_byte", CHUNK + 16, first=16, pad_nonzero_at=MIB - 4096 - 16 - 1)
log.write("EDGES_DONE|not_met=%d|json=0\n" % bad)
log.close()
print("EDGES_DONE|not_met=%d|json=0" % bad)
sys.exit(1 if bad else 0)
