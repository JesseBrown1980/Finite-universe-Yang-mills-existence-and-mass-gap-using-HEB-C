# A few more named cases on the hardened allpairs: differing_fields on odd headers, caps the tool must refuse, a manifest swapped in a clone. Each states what it expects.
# usage: attack_more.py EXE FIXTURE_GZ LF_CLONE EMPTY_SECTORS OUT  Integer only, json=0.
import gzip, hashlib, os, subprocess, sys

EXE, GZ, CLONE, EMPTY, OUT = sys.argv[1:6]
TMP = os.path.dirname(os.path.dirname(os.path.abspath(OUT))) + "/tmp/m"
os.makedirs(TMP, exist_ok=True)
base = gzip.open(GZ, "rb").read()
eol = base.index(b"\n")
LINE = base[:eol]
PAY = base[4096:]
log = open(OUT, "w", encoding="utf-8", newline="\n")
bad = 0


def run(data, args=("0",)):
    p = TMP + "/m.bin"
    open(p, "wb").write(data)
    r = subprocess.run([EXE, p] + list(args), capture_output=True)
    rows = [x for x in r.stdout.split(b"\n") if x.startswith(b"ALLPAIRS|")]
    last = rows[-1] if rows else b""
    f = {}
    for x in last.split(b"|"):
        if b"=" in x:
            k, v = x.split(b"=", 1)
            f[k.decode("latin-1")] = v.decode("latin-1")
    return r.returncode, f, last


def case(name, data, want_exit, args=("0",), check=None):
    global bad
    code, f, last = run(data, args)
    ok = code == want_exit and (check is None or check(f))
    bad += 0 if ok else 1
    log.write("MORE|case=%s|exit=%d|want_exit=%d|store_identity=%s|identity_differs_len=%d|identity_differs_head=%s|verdict=%s|row_bytes=%d|met=%d|json=0\n" % (name, code, want_exit, f.get("store_identity", "-"), len(f.get("identity_differs", "")), f.get("identity_differs", "-")[:40].encode("unicode_escape").decode().replace("|", "~"), f.get("verdict", "-"), len(last), int(ok)))
    log.flush()


def with_line(line):
    return line.ljust(0) + b"\n" + bytes(4096 - len(line) - 1) + PAY


# Many empty parts: the line stays under the block, and no key repeats, since a part with no = names no key.
case("many_empty_parts", with_line(LINE + b"|" * 900), 2, check=lambda f: f.get("store_identity") == "FAIL")
case("many_distinct_keys", with_line(LINE + b"".join(b"|k%d=1" % i for i in range(300))), 2, check=lambda f: f.get("store_identity") == "FAIL" and len(f.get("identity_differs", "")) > 1000)
case("bad_utf8_key", with_line(LINE + bytes([124, 255, 254, 61, 49])), 2, check=lambda f: f.get("store_identity") == "FAIL")
case("control_bytes_in_a_key", with_line(LINE + bytes([124, 13, 9, 7, 61, 49])), 2, check=lambda f: f.get("store_identity") == "FAIL")
case("all_of_the_block_is_the_line", with_line(LINE + b"|" + b"z" * (4096 - len(LINE) - 2)), 2)
case("no_newline_in_the_block", (LINE + b"|" + b"z" * 4096)[:4096] + PAY, 1)
case("line_is_not_utf8_at_the_start", b"\xffYMROOMHDR" + base[10:], 1)
# Refused caps and offsets.
case("cap_not_a_number", base, 1, args=("0", "x"))
case("cap_negative", base, 1, args=("0", "-1"))
case("cap_past_u64", base, 1, args=("0", "18446744073709551616"))
case("offset_not_a_number", base, 1, args=("x",))
case("offset_inside_the_header", base, 1, args=("1",))
# No arguments, and a store that is not there: exit 1, no panic.
r = subprocess.run([EXE], capture_output=True)
ok = r.returncode == 1
bad += 0 if ok else 1
log.write("MORE|case=no_arguments|exit=%d|met=%d|json=0\n" % (r.returncode, int(ok)))
r = subprocess.run([EXE, TMP + "/not-there.bin", "0"], capture_output=True)
ok = r.returncode == 1
bad += 0 if ok else 1
log.write("MORE|case=no_such_store|exit=%d|met=%d|json=0\n" % (r.returncode, int(ok)))
os.remove(TMP + "/m.bin")
log.write("MORE_DONE|not_met=%d|json=0\n" % bad)
log.close()
print("MORE_DONE|not_met=%d|json=0" % bad)
sys.exit(1 if bad else 0)
