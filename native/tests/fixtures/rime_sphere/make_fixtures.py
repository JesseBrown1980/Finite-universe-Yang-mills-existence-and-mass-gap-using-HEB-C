#!/usr/bin/env python3
"""
Regenerates the Stage 2J adversarial carrier fixtures (review 5643283114).

valid.rime is produced from input.bin by scripts/rime_sphere_carrier.py, i.e.
by the ORIGINAL Python NTT. Every other fixture is a single, named mutation of
it, and each one corresponds to a review finding. The committed files are the
evidence; this script only documents exactly how each was made.

usage (from native/):  python3 tests/fixtures/rime_sphere/make_fixtures.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NATIVE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = 1000081

INPUT = b"hello rime prism bridge 2J!:"  # 28 bytes: one block + one tail byte


def main():
    open(os.path.join(HERE, "input.bin"), "wb").write(INPUT)
    tmp = os.path.join(HERE, "_valid")
    subprocess.run([sys.executable, os.path.join(NATIVE, "scripts", "rime_sphere_carrier.py"),
                    tmp, os.path.join(HERE, "input.bin")], check=True, stdout=subprocess.DEVNULL)
    valid = open(os.path.join(tmp, "carrier.rime"), "rb").read()
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)

    head, block, tail, end = valid.split(b"\n")
    assert end == b"" and block.startswith(b"B|0|") and tail.startswith(b"T|")
    coeffs = block[4:].split(b",")

    def join(*lines):
        return b"\n".join(lines) + b"\n"

    def hdr(old, new):
        assert old in head, old
        return head.replace(old, new)

    big = b"999999999999999999"
    shifted = [str(int(coeffs[0]) + P).encode()] + coeffs[1:]
    fixtures = {
        # --- valid baseline: must decode ---------------------------------
        "valid.rime": valid,
        # --- BLOCKING: crash paths ---------------------------------------
        "crash_bytes_huge.rime": join(hdr(b"|bytes=28|", b"|bytes=" + big + b"|"), block, tail),
        "crash_blocks_huge.rime": join(hdr(b"|blocks=1|", b"|blocks=" + big + b"|"), block, tail),
        "crash_tail_nonascii.rime": join(hdr(b"|tail=1|", b"|tail=3|"), block,
                                         "T|ab€a".encode("utf-8")),
        # --- BLOCKING: bank not validated --------------------------------
        "bank_g_altered.rime": join(hdr(b"|g=7|", b"|g=9|"), block, tail),
        "bank_p_altered.rime": join(hdr(b"|p=1000081|", b"|p=1000099|"), block, tail),
        "bank_w_altered.rime": join(hdr(b"|w=951846|", b"|w=1|"), block, tail),
        "bank_p_max_coeff_plus_p.rime": join(hdr(b"|p=1000081|", b"|p=18446744073709551615|"),
                                             b"B|0|" + b",".join(shifted), tail),
        "coeff_ge_p.rime": join(head, b"B|0|" + b",".join([str(P).encode()] + coeffs[1:]), tail),
        # --- MAJOR: non-canonical encodings ------------------------------
        "noncanon_plus_sign.rime": join(head, b"B|0|+" + block[4:], tail),
        "noncanon_leading_zero.rime": join(head, b"B|0|000" + block[4:], tail),
        "noncanon_upper_tail.rime": join(head, block, tail.upper().replace(b"T|", b"T|", 1)),
        "noncanon_crlf.rime": valid.replace(b"\n", b"\r\n"),
        "noncanon_unknown_field.rime": join(hdr(b"|json=0", b"|signed_by=anyone|json=0"), block, tail),
        "noncanon_duplicate_field.rime": join(hdr(b"|json=0", b"|w=1|p=5|json=0"), block, tail),
        "noncanon_tail_first.rime": join(head, tail, block),
        "noncanon_trailing_blank_line.rime": valid + b"\n",
        "noncanon_split_tail.rime": join(hdr(b"|tail=1|", b"|tail=1|"), block, b"T|", tail),
        "invalid_utf8.rime": join(head, block, b"T|\xff\xfe"),
    }
    for name, data in fixtures.items():
        open(os.path.join(HERE, name), "wb").write(data)
    print(f"wrote {len(fixtures)} fixtures + input.bin")


if __name__ == "__main__":
    main()
