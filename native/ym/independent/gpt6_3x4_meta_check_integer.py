#!/usr/bin/env python3
"""Independent metadata and arithmetic check for the 2026-11-03 3x4 room store, in integers only.
A copy of gpt6_3x4_meta_check.py, which stays beside it as evidence, with its two Decimal subtractions in millionths.
The full stored-row and pair replay is a separate verification stage.
"""
from hashlib import sha256

HEADER = (
    "YMROOMHDR|L=3x4|sector=Sx+Sy+|n=45508080|nl=24|rooms=3356267422|"
    "entries=3310759342|payload_bytes=26850881536|stream_bytes=26850885632|"
    "chunk=16MiB|payload_merkle=ec03c5f8ea5abd37ed8f80e0e9e7f00e37840a753f33a1008fbd090b18072a0b|"
    "keys_sha256=bf5a1a43f99f4acd5f73f7da55e628e5bedbd5b4b29ef1b21c87b789d0d13b79|"
    "w_self_adjoint=PASS|json=0"
)
PIN_HEADER_SHA = "65dd63a89d7e1a7cdd3e7876c834c6698a01081ea7a63738e305890bee9e6a21"
N = 45_508_080
ENTRIES = 3_310_759_342
PAIRS = 1_632_625_631
WEIGHT = 13_060_694_016
PADDING = 742_160
CHECKS = []


def check(label, actual, expected):
    good = actual == expected
    CHECKS.append(good)
    print(f"META_CHECK|name={label}|actual={actual}|expected={expected}|verdict={'PASS' if good else 'FAIL'}|json=0")


fields = dict(part.split("=", 1) for part in HEADER.split("|")[1:])
raw = (HEADER + "\n").encode("ascii")
if len(raw) > 4096:
    raise SystemExit("invalid header length")
block = raw + bytes(4096 - len(raw))
check("header_block_sha256", sha256(block).hexdigest(), PIN_HEADER_SHA)
check("lattice", fields["L"], "3x4")
check("rows", int(fields["n"]), N)
check("link_count", int(fields["nl"]), 24)
check("entries", int(fields["entries"]), ENTRIES)
check("pair_count", (int(fields["entries"]) - int(fields["n"])) // 2, PAIRS)
check("pair_parity", (ENTRIES - N) % 2, 0)
check("rows_plus_entries", int(fields["rooms"]), N + ENTRIES)
check("room_padding_bytes", int(fields["payload_bytes"]) - 8 * int(fields["rooms"]), PADDING)
check("header_plus_payload", int(fields["stream_bytes"]), 4096 + int(fields["payload_bytes"]))
check("weight_sum", 6 ** (3 * 4 + 1), WEIGHT)
# In millionths of J_E, as integers.
check("r9_gap", 94070673 - 70031000, 24039673)
check("all_r9_baseline", 94070673 - 72000000, 22070673)
failed = CHECKS.count(False)
print(f"META_CHECK_DONE|checks={len(CHECKS)}|failed={failed}|json=0")
raise SystemExit(0 if failed == 0 else 1)
