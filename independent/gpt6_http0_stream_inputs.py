#!/usr/bin/env python3
"""Independent streamed freeze-leaf audit for the 3x4 S3 key table and Perron vector.

Each leaf reads matching record positions from two original external binary inputs,
validates the row metadata and d positivity, then emits a SHA-256 anchored HBP leaf.
Only Python standard library. Exit 2 on malformed data, mismatch or short read.
"""
import hashlib
import io
import os
import struct
import sys

ROWS = 45508080
LEAF = 59049  # 3^10; ceil(ROWS/LEAF)=771
KEY_SHA = 'eefd7752031cf6e1cbfd53dd47128805d1a98bb41de0a9e269222d0e2c6e3cbc'
VEC_SHA = 'f5c5428db1fc5d91d2ab891689f0dac7263dc26c8f9b60a2db82728f6ea0dcd1'
RECORD = struct.Struct('<QII')
VECTOR = struct.Struct('<q')


def die(reason):
    print('HTTP0_YM_INPUT_FAIL|reason=' + reason + '|json=0', flush=True)
    raise SystemExit(2)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def examine(keys, vec, count, leaf_size, expect_keys, expect_vec, summary, leaves):
    key_h = hashlib.sha256()
    vec_h = hashlib.sha256()
    # The externally frozen hash commitments select the exact input bytes.
    chain = hashlib.sha256(('HTTP0-S3-3X4-LEAF-V1|' + expect_keys + '|' + expect_vec).encode('ascii')).digest()
    prior = -1
    n = 0
    total_w = 0
    flats = 0
    flat_w = 0
    nonflat_min = 1000
    nonflat_max = 0
    d_min = None
    d_max = 0
    zeros = 0
    leaf_no = 0
    while n < count:
        rows = min(leaf_size, count - n)
        kb = keys.read(rows * RECORD.size)
        vb = vec.read(rows * VECTOR.size)
        if len(kb) != rows * RECORD.size or len(vb) != rows * VECTOR.size:
            die('truncated_leaf_' + str(leaf_no))
        key_h.update(kb)
        vec_h.update(vb)
        leaf_w = 0
        leaf_flats = 0
        for off, ((key, w, m), (d,)) in enumerate(zip(RECORD.iter_unpack(kb), VECTOR.iter_unpack(vb))):
            h = n + off
            if key <= prior:
                die('unsorted_or_duplicate_key_at_' + str(h))
            if w < 1 or w > 288:
                die('invalid_weight_at_' + str(h))
            if m > 36:
                die('invalid_magnetic_cost_at_' + str(h))
            if m == 0:
                if d != 0:
                    die('flat_vector_nonzero_at_' + str(h))
                leaf_flats += 1
                flat_w += w
                zeros += 1
            else:
                if d <= 0:
                    die('nonpositive_vector_at_' + str(h))
                nonflat_min = min(nonflat_min, m)
                nonflat_max = max(nonflat_max, m)
                d_min = d if d_min is None else min(d_min, d)
                d_max = max(d_max, d)
            prior = key
            leaf_w += w
        total_w += leaf_w
        flats += leaf_flats
        fields = (
            'HTTP0_YM_FREEZE|leaf=' + str(leaf_no) + '|start=' + str(n)
            + '|rows=' + str(rows) + '|key_sha256=' + digest(kb)
            + '|vector_sha256=' + digest(vb) + '|weight_sum=' + str(leaf_w)
            + '|flats=' + str(leaf_flats)
        )
        prev = chain.hex()
        chain = hashlib.sha256(chain + (fields + '|json=0\n').encode('ascii')).digest()
        if leaves:
            print(fields + '|prev=' + prev + '|seal=' + chain.hex() + '|json=0')
        leaf_no += 1
        n += rows
    if keys.read(1) or vec.read(1):
        die('trailing_bytes')
    if key_h.hexdigest() != expect_keys:
        die('key_sha256')
    if vec_h.hexdigest() != expect_vec:
        die('vector_sha256')
    if summary:
        if n != ROWS or total_w != 6**13 or flats != 7 or flat_w != 18:
            die('orbit_census')
        if nonflat_min != 3 or nonflat_max != 36 or d_min != 9610602 or d_max != 13054544824728578:
            die('magnetic_or_vector_extrema')
    print(
        'HTTP0_YM_INPUTS|rows=' + str(n) + '|leaves=' + str(leaf_no)
        + '|key_sha256=' + key_h.hexdigest() + '|vector_sha256=' + vec_h.hexdigest()
        + '|orbit_weight_sum=' + str(total_w) + '|flats=' + str(flats)
        + '|flat_weight_sum=' + str(flat_w) + '|nonflat_M_min=' + str(nonflat_min)
        + '|nonflat_M_max=' + str(nonflat_max) + '|d_min=' + str(d_min)
        + '|d_max=' + str(d_max) + '|frozen_root_sha256=' + chain.hex()
        + '|status=PASS|json=0', flush=True
    )
    return chain.hex()


def selftest():
    records = [
        (1, 2, 0), (2, 4, 3), (3, 2, 9), (8, 4, 36),
        (12, 2, 3), (13, 4, 6), (17, 1, 0), (31, 5, 2),
    ]
    vectors = [0, 3, 9, 11, 12, 14, 0, 15]
    kb = b''.join(RECORD.pack(*x) for x in records)
    vb = b''.join(VECTOR.pack(x) for x in vectors)
    # Exercise short final leaf, domain checks, input hashes and content anchor.
    root = examine(io.BytesIO(kb), io.BytesIO(vb), len(records), 3, digest(kb), digest(vb), False, True)
    if len(root) != 64:
        die('selftest_anchor')
    import contextlib
    for fault in ('key_flip', 'vec_flip', 'extra_byte', 'truncate', 'duplicate_key', 'flat_nonzero', 'bad_weight'):
        a, b = bytearray(kb), bytearray(vb)
        if fault == 'key_flip':
            a[10] ^= 1
        if fault == 'vec_flip':
            b[9] ^= 1
        if fault == 'extra_byte':
            a.extend(b'x')
        if fault == 'truncate':
            b.pop()
        if fault == 'duplicate_key':
            a[16:24] = a[0:8]
        if fault == 'flat_nonzero':
            b[0] = 1
        if fault == 'bad_weight':
            a[8:12] = (0).to_bytes(4, 'little')
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                examine(io.BytesIO(a), io.BytesIO(b), len(records), 3, digest(kb), digest(vb), False, False)
            except SystemExit as e:
                if e.code != 2:
                    raise RuntimeError('wrong rejection code ' + fault)
            else:
                raise RuntimeError('accepted tampered ' + fault)
    print('HTTP0_YM_INPUT_CONTROLS|attacks=7|rejected=7|short_final_leaf=PASS|seal_chain=PASS|status=PASS|json=0')


def main(args):
    if args == ['--selftest']:
        selftest()
        return
    if len(args) != 2:
        die('usage_gpt6_http0_stream_inputs_KEYS_VECTOR')
    for path, expected in ((args[0], ROWS * RECORD.size), (args[1], ROWS * VECTOR.size)):
        if os.path.getsize(path) != expected:
            die('file_size_' + os.path.basename(path))
    with open(args[0], 'rb', buffering=1048576) as keys, open(args[1], 'rb', buffering=1048576) as vec:
        examine(keys, vec, ROWS, LEAF, KEY_SHA, VEC_SHA, True, True)


if __name__ == '__main__':
    main(sys.argv[1:])
