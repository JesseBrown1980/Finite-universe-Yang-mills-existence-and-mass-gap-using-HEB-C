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
"""
import hashlib
import os
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


def main():
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
