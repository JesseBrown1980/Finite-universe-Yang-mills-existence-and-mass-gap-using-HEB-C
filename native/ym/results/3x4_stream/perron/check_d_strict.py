# Fail-closed check of a Perron certificate and of the store's row structure, streaming. Exact Python integers, no code
# shared with perroncert. Written after an external review of check_d_stream.py, whose assert statements vanish under
# python -O: there, a changed byte still printed merkle=PASS. This file has no assert. Any failed condition prints one
# CHECK_D_FAIL row and exits 2, and no certified value is printed.
#
# usage: check_d_strict.py DEV D_FILE JE JB [--passa FILE] [--self-adjoint SEED] [--expect-d-sha256 HEX]
#   DEV           a path, or first:count:seglen:prefix for the sector files <prefix>NNN.rooms
#   --passa       compare every row's weight and magnetic number with the key table
#   --self-adjoint  test W H = (W H)^T on all rows, by a random bilinear form modulo 2^61-1, with the random values drawn from
#                 SHA-256 of the seed and the row index (false-pass chance about 1e-18)
#   --expect-d-sha256  fail unless D_FILE has this SHA-256, so a swapped or substituted vector stops the check
#
# For every row it also checks: the entries sum to 0 (one -1 per move, diagonal 3*nl minus the moves back), no positive
# off-diagonal entry, ascending columns in range, and for flat rows a diagonal of 3*nl with no coupling to another flat row.
# t_cert_milli keeps the name used across the tools. It is in units of 1/(1000*JE) J_E, so 10^-6 J_E at JE=1000.
# Output row CHECK_D_STRICT, json=0.
import array, hashlib, struct, sys, time

MIB = 1048576
P61 = (1 << 61) - 1


def fail(reason):
    print(f"CHECK_D_FAIL|reason={reason}|json=0", flush=True)
    sys.exit(2)


class Stream:
    def __init__(self, spec):
        parts = spec.split(":", 3)
        if len(parts) == 4 and parts[0].isdigit():
            first, count, self.seg = int(parts[0]), int(parts[1]), int(parts[2])
            self.names = [f"{parts[3]}{first + k:03d}.rooms" for k in range(count)]
        else:
            self.seg = None
            self.names = [spec]
        self.k, self.pos = 0, 0
        self.f = open(self.names[0], "rb", buffering=0)

    def read(self, n):
        out = bytearray()
        while n > 0:
            want = n if self.seg is None else min(n, self.seg - self.pos)
            b = self.f.read(want) if want > 0 else b""
            if not b:
                if self.k + 1 >= len(self.names):
                    break
                self.f.close()
                self.k += 1
                self.pos = 0
                self.f = open(self.names[self.k], "rb", buffering=0)
                continue
            out += b
            self.pos += len(b)
            n -= len(b)
        return bytes(out)


def main():
    t0 = time.monotonic_ns()
    a = sys.argv[1:]
    passa_path, seed = None, None
    if "--passa" in a:
        i = a.index("--passa")
        passa_path = a[i + 1]
        del a[i : i + 2]
    if "--self-adjoint" in a:
        i = a.index("--self-adjoint")
        seed = int(a[i + 1])
        del a[i : i + 2]
    expect_d = None
    if "--expect-d-sha256" in a:
        i = a.index("--expect-d-sha256")
        expect_d = a[i + 1]
        del a[i : i + 2]
    if len(a) != 4:
        fail("usage")
    dev, dfile, je, jb = a[0], a[1], int(a[2]), int(a[3])
    if je <= 0 or jb < 0:
        fail("couplings")
    if sys.byteorder != "little":
        fail("big_endian_platform")

    d = array.array("q")
    with open(dfile, "rb") as f:
        raw_d = f.read()
    d_sha = hashlib.sha256(raw_d).hexdigest()
    if expect_d is not None and d_sha != expect_d:
        fail("d_sha256_mismatch")
    d.frombytes(raw_d)
    del raw_d
    s = Stream(dev)
    head = s.read(4096)
    if b"\n" not in head:
        fail("no_header_line")
    line = head[: head.index(b"\n")].decode()
    fld = dict(x.split("=", 1) for x in line.split("|")[1:] if "=" in x)
    for k in ("n", "nl", "rooms", "entries", "payload_bytes", "payload_merkle"):
        if k not in fld:
            fail(f"header_missing_{k}")
    n, nl, rooms, entries, payload = int(fld["n"]), int(fld["nl"]), int(fld["rooms"]), int(fld["entries"]), int(fld["payload_bytes"])
    if len(d) != n:
        fail("d_length")

    pa = None
    if passa_path is not None:
        pa = array.array("I")
        with open(passa_path, "rb") as f:
            pa.frombytes(f.read())
        if pa.itemsize != 4 or len(pa) != 4 * n:
            fail("passa_length")

    x, y, wrow = None, None, 0
    if seed is not None:
        x, y = array.array("Q", bytes(8 * n)), array.array("Q", bytes(8 * n))
        words = struct.Struct("<4Q").unpack
        tag = str(seed).encode() + b":"
        for i in range(n):
            a0, b0, _, _ = words(hashlib.sha256(tag + str(i).encode()).digest())
            x[i] = a0 % P61
            y[i] = b0 % P61
    form_a, form_b = 0, 0

    u = 1000 * je
    top = 1000 * jb
    best_r, best_h, best_m = None, None, None
    min_nonflat, max_mag = None, 0
    h = 0
    seen_entries = 0
    flats = []
    flat_cols = []
    carry = b""
    shas = bytearray()
    left = payload
    walked = 0
    unpack_h = struct.Struct("<IHH").unpack_from
    unpack_e = struct.Struct("<Ii").iter_unpack
    try:
        while left > 0:
            chunk = s.read(min(16 * MIB, left))
            if not chunk:
                fail("short_read")
            left -= len(chunk)
            shas += hashlib.sha256(chunk).hexdigest().encode()
            buf = carry + chunk
            p = 0
            end = len(buf)
            while h < n and p + 8 <= end:
                w, mag, cnt = unpack_h(buf, p)
                q = p + 8 + 8 * cnt
                if q > end:
                    break
                if w == 0:
                    fail(f"zero_weight_row_{h}")
                if pa is not None and (pa[4 * h + 2] != w or pa[4 * h + 3] != mag):
                    fail(f"passa_mismatch_row_{h}")
                row = buf[p + 8 : q]
                rs = 0
                prev = -1
                if mag == 0:
                    flats.append(h)
                    if d[h] != 0:
                        fail(f"flat_d_nonzero_row_{h}")
                    diag = 0
                    for j, z in unpack_e(row):
                        if j <= prev:
                            fail(f"columns_not_ascending_row_{h}")
                        prev = j
                        if z > 0 and j != h:
                            fail(f"positive_offdiag_row_{h}")
                        if j == h:
                            diag = z
                        else:
                            flat_cols.append(j)
                        rs += z
                    if diag != 3 * nl:
                        fail(f"flat_diagonal_row_{h}")
                else:
                    if min_nonflat is None or mag < min_nonflat:
                        min_nonflat = mag
                    dh = d[h]
                    if dh <= 0:
                        fail(f"nonpositive_d_row_{h}")
                    t = top * mag * dh
                    for j, z in unpack_e(row):
                        if j <= prev:
                            fail(f"columns_not_ascending_row_{h}")
                        prev = j
                        if z > 0 and j != h:
                            fail(f"positive_offdiag_row_{h}")
                        rs += z
                        t += u * z * d[j]
                    r = t // dh
                    if best_r is None or r < best_r:
                        best_r, best_h, best_m = r, h, mag
                if rs != 0:
                    fail(f"row_sum_not_zero_row_{h}")
                if mag > max_mag:
                    max_mag = mag
                if x is not None:
                    xh, yh = x[h], y[h]
                    sa, sb = 0, 0
                    for j, z in unpack_e(row):
                        sa += z * y[j]
                        sb += z * x[j]
                    form_a = (form_a + xh * w % P61 * (sa % P61)) % P61
                    form_b = (form_b + yh * w % P61 * (sb % P61)) % P61
                seen_entries += cnt
                walked += q - p
                p = q
                h += 1
            carry = buf[p:]
            if h == n:
                if any(carry):
                    fail("nonzero_padding")
                carry = b""
    except IndexError:
        fail(f"column_out_of_range_near_row_{h}")
    if h != n:
        fail("row_count")
    if walked != 8 * rooms:
        fail("room_count")
    if seen_entries != entries:
        fail("entry_count")
    fs = set(flats)
    if any(j in fs for j in flat_cols):
        fail("flat_flat_coupling")
    if hashlib.sha256(bytes(shas)).hexdigest() != fld["payload_merkle"]:
        fail("merkle")
    if x is not None and form_a != form_b:
        fail("not_W_self_adjoint")
    if best_r is None:
        fail("no_nonflat_rows")
    secs = (time.monotonic_ns() - t0) // 1_000_000_000
    den = 1000 * je
    extra = ""
    if pa is not None:
        extra += "|passa_w_and_M=PASS"
    if x is not None:
        extra += f"|W_self_adjoint=PASS|seed={seed}"
    print(
        f"CHECK_D_STRICT|n={n}|d_sha256={d_sha}|flats={len(flats)}|flat_rows={','.join(map(str, flats))}|flat_diag={3 * nl}|flat_flat_couplings=0"
        f"|t_cert_milli={best_r}|t_cert_JE={best_r}/{den}|min_row={best_h}|min_mag={best_m}|min_nonflat_M={min_nonflat}|max_M={max_mag}"
        f"|positive_offdiag=0|bad_d=0|row_sums_zero=PASS{extra}|merkle=PASS|secs={secs}|json=0",
        flush=True,
    )


main()
