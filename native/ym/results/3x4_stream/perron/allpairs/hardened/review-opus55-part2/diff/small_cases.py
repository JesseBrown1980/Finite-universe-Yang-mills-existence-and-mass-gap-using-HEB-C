# Three direct cases the wider runs left open. Written after the runs that raised them. usage: small_cases.py EXE OUT_HBP FIXTURE_GZ   Integer only, json=0.
import gzip, hashlib, os, struct, subprocess, sys

EXE, OUT, GZ = sys.argv[1:4]
TMP = os.path.dirname(os.path.abspath(OUT)) + "/small.bin"
log = open(OUT, "w", encoding="utf-8", newline="\n")
bad = 0


def sha(b):
    return hashlib.sha256(b).hexdigest()


def merkle(pl):
    return sha("".join(sha(pl[i:i + (16 << 20)]) for i in range(0, len(pl), 16 << 20)).encode())


def run(name, data, want):
    global bad
    open(TMP, "wb").write(data)
    r = subprocess.run([EXE, TMP, "0"], capture_output=True, text=True)
    last = ([x for x in r.stdout.splitlines() if x.startswith("ALLPAIRS|")] or [""])[-1]
    f = dict(x.split("=", 1) for x in last.split("|") if "=" in x)
    ok = r.returncode == want
    bad += 0 if ok else 1
    log.write("SMALL_CASE|case=%s|want_exit=%d|exit=%d|verdict=%s|header_entries=%s|whole_space_count=%s|codes=%s|sum_w=%s|met=%d|json=0\n" % (name, want, r.returncode, f.get("verdict"), f.get("header_entries"), f.get("whole_space_count"), f.get("codes"), f.get("sum_w"), int(ok)))


# A zero-sided lattice over rows whose weights sum to 6, the value 6^(0+1) would give if the zero check were gone.
pl = struct.pack("<IHH", 3, 3, 2) + struct.pack("<IiIi", 0, 1, 1, -1) + struct.pack("<IHH", 3, 3, 2) + struct.pack("<IiIi", 0, -1, 1, 1)
line = "YMROOMHDR|L=0x4|nl=0|n=2|entries=4|payload_bytes=%d|payload_merkle=%s|w_self_adjoint=PASS|json=0\n" % (len(pl), merkle(pl))
run("zero_side_with_sum_w_6", line.encode().ljust(4096, b"\0") + pl, 2)
# The one header substitution outside the print-only fields that exited 0: the separator after w_self_adjoint=PASS becomes the newline.
b = bytearray(gzip.open(GZ, "rb").read())
at = b.index(b"w_self_adjoint=PASS|") + len(b"w_self_adjoint=PASS")
b[at] = 0x0A
run("newline_right_after_w_self_adjoint", bytes(b), 0)
# The same store with the two last fields swapped, so the newline would cut w_self_adjoint off.
c = gzip.open(GZ, "rb").read()
e = c.index(b"\n")
li = c[:e].replace(b"|w_self_adjoint=PASS|json=0", b"|json=0\nw_self_adjoint=PASS")
run("w_self_adjoint_only_after_the_newline", (li + b"\n").ljust(4096, b"\0") + c[4096:], 1)
os.remove(TMP)
log.write("SMALL_CASES_DONE|not_met=%d|json=0\n" % bad)
log.close()
print(open(OUT, encoding="utf-8").read())
sys.exit(1 if bad else 0)
