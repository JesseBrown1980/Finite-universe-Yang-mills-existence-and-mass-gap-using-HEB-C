#!/usr/bin/env python3
"""
rime_sphere_carrier.py - the Python half of the Stage 2J RIME sphere bridge.

It IMPORTS the original transform from the vendored, byte-pinned source
(native/vendor/rime_sphere_source/rime_prism_pipeline.py, simulator commit
3f9f42d). Nothing here re-implements the NTT (Law 63.3: if the code you need
is in the file you are reading, import it).

It writes two files that the Rust bridge must reproduce byte-for-byte:
  carrier.rime   - the bank header plus the FULL 27 NTT coefficients per block
                   (and any tail bytes). This is what preserves byte-exact
                   recovery; the balanced-ternary triples only label positions.
  xcheck.measure - C1 and the C3 / C4 counts, computed with the original ntt/intt.

usage: rime_sphere_carrier.py OUT_DIR [INPUT_FILE]
Without INPUT_FILE it uses the original pipeline's own fallback bytes,
bytes((i*7)%251 for i in range(13500)).

       rime_sphere_carrier.py --decode CARRIER OUT
Independent decoder (review 5643283114). It validates with a different
technique from the Rust side: a strict whole-document grammar (one regex
full-match on the raw bytes), where Rust re-renders and compares. It then
inverts with the ORIGINAL intt. Any rejection prints FAIL|reason=... and
exits 1.

       rime_sphere_carrier.py --compare-original ORIGINAL_OUTPUT RUN_MEASURE
Checks the original script's OWN printed C3 table and C4 random line against
the bridge's c3_bytes / c4_random counts for the same input.
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "..", "vendor", "rime_sphere_source")
sys.path.insert(0, SOURCE)

from rime_prism_pipeline import ntt, intt  # noqa: E402  (original, unmodified)
from rime_sphere import primitive_root       # noqa: E402  (original, unmodified)

P = 1000081
N = 27
C3_KS = (3, 9, 18, 24, 26, 27)
C4_BLOCKS = 100


def default_input():
    return bytes((i * 7) % 251 for i in range(13500))


_NUM = rb"(?:0|[1-9][0-9]*)"
_CARRIER = re.compile(
    rb"RIMECARRIER\|schema=hebc\.rime\.sphere\.carrier\.v1"
    rb"\|p=(" + _NUM + rb")\|g=(" + _NUM + rb")\|w=(" + _NUM + rb")\|N=27"
    rb"\|bytes=(" + _NUM + rb")\|blocks=(" + _NUM + rb")\|tail=(" + _NUM + rb")"
    rb"\|input_sha=([0-9a-f]{64})\|json=0\n"
    rb"((?:B\|" + _NUM + rb"\|" + _NUM + rb"(?:," + _NUM + rb"){26}\n)*)"
    rb"(?:T\|((?:[0-9a-f]{2})+)\n)?"
)


class Reject(Exception):
    pass


def decode_carrier(raw):
    m = _CARRIER.fullmatch(raw)
    if not m:
        raise Reject("carrier does not match the canonical grammar")
    p, g, w, nbytes, nblocks, ntail = (int(x) for x in m.groups()[:6])
    sha = m.group(7).decode()
    rows = m.group(8).split(b"\n")[:-1] if m.group(8) else []
    tail = bytes.fromhex(m.group(9).decode()) if m.group(9) else b""
    eg = primitive_root(P)
    if (p, g, w) != (P, eg, pow(eg, (P - 1) // N, P)):
        raise Reject("carrier bank is not the supported bank")
    if len(rows) != nblocks or len(tail) != ntail:
        raise Reject("carrier row counts disagree with header")
    if nbytes != N * nblocks + ntail:
        raise Reject("declared byte length does not equal 27*blocks + tail")
    out = bytearray()
    for i, row in enumerate(rows):
        idx, vals = row[2:].split(b"|")
        if int(idx) != i:
            raise Reject("block rows out of order")
        X = [int(v) for v in vals.split(b",")]
        if any(v >= P for v in X):
            raise Reject("coefficient outside Z/p")
        r = intt(X, w, P, N)  # original, unmodified
        if any(v > 255 for v in r):
            raise Reject("inverse value is not a byte")
        out.extend(r)
    out.extend(tail)
    if hashlib.sha256(bytes(out)).hexdigest() != sha:
        raise Reject("decoded bytes do not match the carried input sha")
    return bytes(out)


def decode_main(src, dst):
    try:
        data = decode_carrier(open(src, "rb").read())
    except Reject as e:
        sys.stderr.write("FAIL|reason=%s|json=0\n" % e)
        sys.exit(1)
    open(dst, "wb").write(data)
    print("RIMESPHEREDECODE-PY|result=PASS|bytes=%d|json=0" % len(data))


def compare_original_main(original_txt, run_measure):
    text = open(original_txt).read()
    measure = open(run_measure).read()
    bridge = dict(kv.split("=", 1) for kv in measure.strip().split("|")[1:] if "=" in kv)
    pct = lambda m, t: "%.1f" % (100.0 * m / t)
    rows = dict(re.findall(r"^\s+(\d+)/27\s+\d+%\s+([0-9.]+)%\s*$", text, re.M))
    problems, checked = [], 0
    for item in bridge["c3_bytes"].split(","):
        k, frac = item.split(":")
        m, t = (int(x) for x in frac.split("/"))
        if rows.get(k) != pct(m, t):
            problems.append("C3 k=%s original=%s bridge=%s" % (k, rows.get(k), pct(m, t)))
        checked += 1
    rnd = re.search(r"random address.*?:\s*([0-9.]+)% recovered", text)
    m, t = (int(x) for x in bridge["c4_random"].split("/"))
    if not rnd or rnd.group(1) != pct(m, t):
        problems.append("C4 random original=%s bridge=%s" % (rnd and rnd.group(1), pct(m, t)))
    checked += 1
    if problems:
        sys.stderr.write("FAIL|reason=%s|json=0\n" % "; ".join(problems))
        sys.exit(1)
    print("ORIGINAL-VS-BRIDGE|result=PASS|c3_rows=%d|c4_random=1|checked=%d|json=0" % (checked - 1, checked))


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--decode":
        return decode_main(sys.argv[2], sys.argv[3])
    if len(sys.argv) >= 2 and sys.argv[1] == "--compare-original":
        return compare_original_main(sys.argv[2], sys.argv[3])
    if len(sys.argv) < 2:
        sys.exit("usage: rime_sphere_carrier.py OUT_DIR [INPUT_FILE]")
    out = sys.argv[1]
    data = open(sys.argv[2], "rb").read() if len(sys.argv) > 2 else default_input()
    g = primitive_root(P)
    w = pow(g, (P - 1) // N, P)
    nblocks = len(data) // N
    blocks = [list(data[i * N:(i + 1) * N]) for i in range(nblocks)]
    tail = data[nblocks * N:]
    coeffs = [ntt(b, w, P, N) for b in blocks]

    lines = [
        "RIMECARRIER|schema=hebc.rime.sphere.carrier.v1|p=%d|g=%d|w=%d|N=%d|bytes=%d|blocks=%d|tail=%d|input_sha=%s|json=0"
        % (P, g, w, N, len(data), nblocks, len(tail), hashlib.sha256(data).hexdigest())
    ]
    for i, X in enumerate(coeffs):
        lines.append("B|%d|%s" % (i, ",".join(str(c) for c in X)))
    if tail:
        lines.append("T|%s" % tail.hex())
    carrier = ("\n".join(lines) + "\n").encode()

    c1 = all(intt(X, w, P, N) == b for X, b in zip(coeffs, blocks))
    c3 = []
    for k in C3_KS:
        match = 0
        for X, b in zip(coeffs, blocks):
            r = intt([X[i] if i < k else 0 for i in range(N)], w, P, N)
            match += sum(1 for a, c in zip(r, b) if a == c)
        c3.append("%d:%d/%d" % (k, match, N * nblocks))
    rnd = 0
    used = blocks[:C4_BLOCKS]
    for b in used:
        r = intt([(i * 2654435761 + 7) % P for i in range(N)], w, P, N)
        rnd += sum(1 for a, c in zip(r, b) if a == c)
    measure = (
        "RIMESPHERE-XCHECK|schema=hebc.rime.sphere.xcheck.v1|w=%d|blocks=%d|c1=%s|c3=%s|c4_random=%d/%d|carrier_sha=%s|json=0\n"
        % (w, nblocks, "PASS" if c1 else "FAIL", ",".join(c3), rnd, N * len(used),
           hashlib.sha256(carrier).hexdigest())
    )

    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "carrier.rime"), "wb").write(carrier)
    open(os.path.join(out, "xcheck.measure"), "w").write(measure)
    sys.stdout.write(measure)
    if not c1:
        sys.exit(1)


if __name__ == "__main__":
    main()
