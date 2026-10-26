#!/usr/bin/env python3
"""Cryptographic integrity of committed hebc_ym_http0 shards, recomputed from
the bytes on disk: for every shard, index.hbi is regenerated from run.hbp
(offsets, lengths, per-line SHA-256, hash chain from SHA-256("HEBC-YM-HBI-ROOT"))
and compared byte for byte, and run.anchor is regenerated from the spec file,
SHA-256(run.hbp), SHA-256(index.hbi) and the line count and compared byte for
byte. Same construction as backend/src/main.rs (index, write_shard).
This checks integrity relative to the files, not provenance or correctness.
usage: verify_shard_integrity.py SHARDS_DIR...        json=0
"""
import hashlib
import os
import sys


def h(b):
    return hashlib.sha256(b).hexdigest()


def main():
    total = bad = 0
    for d in sys.argv[1:]:
        for name in sorted(os.listdir(d)):
            p = os.path.join(d, name)
            if not os.path.isdir(p) or name.startswith("."):
                continue
            total += 1
            hbp = open(os.path.join(p, "run.hbp"), "rb").read()
            chain, off, out = h(b"HEBC-YM-HBI-ROOT"), 0, []
            for k, line in enumerate(hbp.decode().split("\n")[:-1]):
                ls = h(line.encode())
                chain = h((chain + ls).encode())
                out.append("HBI|line=%d|offset=%d|len=%d|sha=%s|chain=%s|json=0\n" % (k, off, len(line.encode()), ls, chain))
                off += len(line.encode()) + 1
            hbi = "".join(out).encode()
            spec = open(os.path.join(p, "spec")).read().strip()
            anchor = ("ANCHOR|spec=%s|hbp_sha256=%s|hbi_sha256=%s|lines=%d|json=0\n" % (spec, h(hbp), h(hbi), len(out))).encode()
            ok = hbi == open(os.path.join(p, "index.hbi"), "rb").read() and anchor == open(os.path.join(p, "run.anchor"), "rb").read() and spec.replace("/", "_") == name
            if not ok:
                bad += 1
                print("SHARD_INTEGRITY|shard=%s|result=FAIL|json=0" % name)
    print("SHARD_INTEGRITY|shards=%d|failed=%d|checked=index.hbi_regenerated,run.anchor_regenerated,spec_matches_dir|result=%s|json=0" % (total, bad, "PASS" if bad == 0 and total > 0 else "FAIL"))
    sys.exit(0 if bad == 0 and total > 0 else 2)


if __name__ == "__main__":
    main()
