#!/usr/bin/env python3
"""Separately implemented exact-byte audit of three fixed 3x4 Yang-Mills receipts indexed by
HEB-C HTTP-0's 3^16 virtual namespace. Standard library, integer-only, no JSON.
This verifies frozen source records, NOT the 45,508,080-row recomputation.
"""
import hashlib
from pathlib import Path
import shutil
import sys
import tempfile

SOURCE_COMMIT = "5517268b511d5f28e307b21fc53eede3200ed7b9"
CAPACITY = 3**16
DOMAIN_OFFSET = 3**4
SOURCES = (
    (
        "PERRON",
        "native/ym/results/3x4_stream/perron/PERRON-RESULT.hbp",
        "de19b354127c59ba3c2328fd310b5ff6a1103829c8d1d86c58b433aeec115a18",
        "cbd428014a4d440732a5c0a541ed57a9041becee",
        44107,
        "PERRON_RESULT",
        None,
        {
            "best_t_cert_milli": "94070673",
            "lambda1_upper_milli": "94070936",
            "gap_verdict": "OPEN",
            "all_rows_rebuild_second_seat": "MATCHED_45508080_of_45508080",
        },
    ),
    (
        "FULLREBUILD",
        "native/ym/results/3x4_stream/perron/FULLREBUILD-RUN.hbp",
        "cccada48ce34abeb12d77c8c4a0917dd4d9acb489aac3a9fe5d77b29f47a0a07",
        "d6e264cdf3a30929edc552bf85077f4aa08b799c",
        1230,
        "PREDICTION_RESULT",
        "fullrebuild_3x4",
        {
            "rows_rebuilt": "45508080",
            "rows_read": "45508080",
            "canonical_key_mismatch": "0",
            "weight_mismatch": "0",
            "M_mismatch": "0",
            "entries_mismatch": "0",
            "merkle": "PASS",
            "prediction_met": "1",
            "exit": "0",
            "sectors_match_manifest": "34/34",
        },
    ),
    (
        "ALLPAIRS",
        "native/ym/results/3x4_stream/perron/allpairs/ALLPAIRS-RUN.hbp",
        "8af3e4e76672abc92bf0d17113680cda387a353de082916a5e2921756ca95ce0",
        "6cf863c8ac0d4943fb5077c77fa4fc02b3e0acc2",
        3815,
        "PREDICTION_RESULT",
        "allpairs_3x4",
        {
            "n": "45508080",
            "rows_read": "45508080",
            "pairs": "1632625631",
            "passes": "4",
            "value_mismatch": "0",
            "lower_without_upper": "0",
            "upper_without_lower": "0",
            "row_sum_nonzero": "0",
            "merkle_each_pass": "PASS",
            "verdict": "PASS",
            "prediction_met": "1",
            "exit": "0",
        },
    ),
)


def required_field(line, name):
    prefix = name + "="
    found = [x[len(prefix):] for x in line.split("|") if x.startswith(prefix)]
    if len(found) != 1:
        raise ValueError("missing or ambiguous " + name)
    return found[0]


def exact_row(text, tag, run):
    matches = []
    for line in text.splitlines():
        if not line.startswith(tag + "|"):
            continue
        if run is not None and required_field(line, "run") != run:
            continue
        matches.append(line)
    if len(matches) != 1:
        raise ValueError("missing or ambiguous source record " + tag)
    if required_field(matches[0], "json") != "0":
        raise ValueError("not a native HBP receipt")
    return matches[0]



def count_address_collisions(domain_offset):
    """Compute all native Clay/Taylor leaves and YM addresses using exact trits."""
    clay_addresses = set()
    for tick in (1, 2, 3):
        for arm in range(3):
            for register in range(81):
                address = (tick - 1) * (3**15) + arm * (3**14) + register
                if address >= CAPACITY or address in clay_addresses:
                    raise ValueError("invalid or duplicated Clay/Taylor leaf address")
                clay_addresses.add(address)
    if len(clay_addresses) != 729:
        raise ValueError("incomplete native Clay/Taylor address set")
    ym_addresses = [domain_offset + index for index in range(len(SOURCES))]
    if len(set(ym_addresses)) != len(SOURCES):
        raise ValueError("duplicate Yang-Mills address")
    if any(address < 0 or address >= CAPACITY for address in ym_addresses):
        raise ValueError("Yang-Mills address outside ternary capacity")
    return sum(address in clay_addresses for address in ym_addresses)



def audit(root, emit=True):
    if CAPACITY != 43_046_721 or CAPACITY < 23_000_000:
        raise ValueError("unexpected ternary namespace")
    collisions = count_address_collisions(DOMAIN_OFFSET)
    if collisions:
        raise ValueError("Yang-Mills/Clay address collision")
    checked = []
    for i, (kind, name, sha, git_blob_sha, size, tag, run, fields) in enumerate(SOURCES):
        blob = root.joinpath(name).read_bytes()
        if len(blob) != size or hashlib.sha256(blob).hexdigest() != sha:
            raise ValueError("source byte identity mismatch " + name)
        git_blob = b"blob " + str(len(blob)).encode("ascii") + b"\x00" + blob
        if hashlib.sha1(git_blob).hexdigest() != git_blob_sha:
            raise ValueError("source Git blob identity mismatch " + name)
        line = exact_row(blob.decode("utf-8"), tag, run)
        for key, expected in fields.items():
            if required_field(line, key) != expected:
                raise ValueError("source metric changed " + kind + ":" + key)
        address = DOMAIN_OFFSET + i
        digits = []
        number = address
        for _ in range(16):
            digits.append(number % 3)
            number //= 3
        if number or digits[4] != 1 or any(digits[j] for j in range(5, 16)):
            raise ValueError("address outside registered Yang-Mills domain")
        if emit:
            print(
                f"YM43_SOURCE|index={i}|id={address}|kind={kind}|"
                f"sha256={sha}|git_blob_sha1={git_blob_sha}|"
                f"bytes={size}|field_checks={len(fields)}|"
                f"source_status={'OPEN' if i == 0 else 'REPORTED_PASS'}|"
                "physics_reexecuted=0|json=0"
            )
        checked.append((kind, name))
    if emit:
        print(
            f"YM43_VERIFY|source_commit={SOURCE_COMMIT}|power=3^16|"
            f"capacity={CAPACITY}|sources={len(checked)}|"
            f"address_collision={collisions}|source_sha256=PASS|git_blob_sha1=PASS|"
            "field_validation=PASS|gap_verdict=OPEN|physics_reexecuted=0|"
            "status=PASS|json=0"
        )
    return checked


def self_test(root):
    with tempfile.TemporaryDirectory(prefix="ym43-fault-") as d:
        tmp = Path(d)
        for item in SOURCES:
            path = item[1]
            destination = tmp.joinpath(path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root.joinpath(path), destination)
        audit(tmp, emit=False)
        if count_address_collisions(0) != len(SOURCES):
            raise ValueError("injected domain overlap control not detected")
        tampered = tmp.joinpath(SOURCES[1][1])
        contents = bytearray(tampered.read_bytes())
        contents[40] ^= 1
        tampered.write_bytes(contents)
        try:
            audit(tmp, emit=False)
        except ValueError:
            pass
        else:
            raise ValueError("corrupted fullrebuild receipt was accepted")
        tampered.write_bytes(root.joinpath(SOURCES[1][1]).read_bytes())
        tmp.joinpath(SOURCES[0][1]).unlink()
        try:
            audit(tmp, emit=False)
        except OSError:
            pass
        else:
            raise ValueError("missing Perron receipt was accepted")
    print("YM43_CONTROLS|corrupt_receipt=REJECTED|missing_receipt=REJECTED|address_collision_injected=DETECTED|status=PASS|json=0")


if __name__ == "__main__":
    try:
        home = Path(__file__).resolve().parents[2]
        if len(sys.argv) > 2:
            raise ValueError("usage: verify_http0_ym43.py [repo-root]")
        if len(sys.argv) == 2:
            home = Path(sys.argv[1]).resolve()
        audit(home)
        self_test(home)
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"YM43_VERIFY|status=FAIL|reason={str(exc).replace('|', '_')}|json=0", file=sys.stderr)
        sys.exit(1)
