#!/usr/bin/env python3
"""Independent 771-leaf HBP receipt assembler, integer-only, standard library."""
import hashlib
from pathlib import Path
import sys

N = 45508080
LEAF = 59049
LEAVES = 771
SHARDS = 27
SHARD_LEAVES = 29
SUM_W = 13060694016
TIGHT_ROW = 45507968
BOUND = 94070673
KEY_SHA = 'eefd7752031cf6e1cbfd53dd47128805d1a98bb41de0a9e269222d0e2c6e3cbc'
VEC_SHA = 'f5c5428db1fc5d91d2ab891689f0dac7263dc26c8f9b60a2db82728f6ea0dcd1'


def fail(reason):
    print('HTTP0_YM_AGGREGATE_FAIL|reason=' + reason + '|json=0', flush=True)
    raise SystemExit(2)


def fields(line, kind):
    parts = line.split('|')
    if parts[0] != kind or parts[-1] != 'json=0':
        fail('record_kind_' + kind)
    result = {}
    for part in parts[1:]:
        if '=' not in part:
            fail('field_syntax')
        k, v = part.split('=', 1)
        if k in result:
            fail('duplicate_field_' + k)
        result[k] = v
    return result


def valid_line(line, expected_first, expected_rows):
    f = fields(line, 'HTTP0_YM_REBUILT_LEAF')
    for k, want in (
        ('first', expected_first), ('rows', expected_rows),
        ('electric_moves', 72 * expected_rows),
        ('reverse_pairs', 8), ('bound_microJE', BOUND),
    ):
        if f.get(k) != str(want):
            fail('leaf_' + str(expected_first) + '_' + k)
    if f.get('status') != 'PASS':
        fail('leaf_status')
    try:
        w, flats, minimum, h = map(int, (f['orbit_weight_sum'], f['flats'], f['min_ratio_microJE'], f['min_row']))
    except (ValueError, KeyError):
        fail('leaf_numeric_fields')
    if w <= 0 or flats < 0 or flats > 7 or minimum < BOUND:
        fail('leaf_measurements')
    if not expected_first <= h < expected_first + expected_rows:
        fail('min_row_outside_leaf')
    return w, flats, minimum, h


def main():
    if len(sys.argv) != 4:
        fail('usage_SHARDS_DIR_SOURCE_FILE_OUTDIR')
    directory = Path(sys.argv[1])
    code = Path(sys.argv[2])
    output = Path(sys.argv[3])
    if not directory.is_dir() or not code.is_file():
        fail('sources_absent')
    output.mkdir(parents=True, exist_ok=True)
    code_sha = hashlib.sha256(code.read_bytes()).hexdigest()
    chain = hashlib.sha256(('HTTP0-YM-ROWFREEZE-1|' + KEY_SHA + '|' + VEC_SHA + '|' + code_sha).encode('ascii')).digest()
    weight_sum = 0
    flats = 0
    absolute_min = None
    absolute_row = None
    frozen = []
    hbi = []
    completed = 0
    for shard in range(SHARDS):
        folder = directory / ('gpt6-ym3x4-shard-' + str(shard))
        source = folder / 'leaves.hbp'
        manifest = folder / 'SHA256SUMS'
        if not source.is_file() or not manifest.is_file():
            fail('missing_shard_' + str(shard))
        values = {}
        for item in manifest.read_text(encoding='ascii').splitlines():
            words = item.split()
            if len(words) != 2 or words[1] in values:
                fail('manifest_syntax_' + str(shard))
            values[words[1]] = words[0]
        if values.get('independent/gpt6_http0_symmetry_rows.cpp') != code_sha:
            fail('source_code_hash_' + str(shard))
        if values.get('leaves.hbp') != hashlib.sha256(source.read_bytes()).hexdigest():
            fail('shard_receipt_sha_' + str(shard))
        text = source.read_text(encoding='ascii').splitlines()
        leaf_lines = [x for x in text if x.startswith('HTTP0_YM_REBUILT_LEAF|')]
        shard_lines = [x for x in text if x.startswith('HTTP0_YM_SHARD|')]
        expected_leaf_count = min(SHARD_LEAVES, LEAVES - SHARD_LEAVES * shard)
        if len(leaf_lines) != expected_leaf_count or len(shard_lines) != 1 or len(text) != len(leaf_lines) + 1:
            fail('shard_line_count_' + str(shard))
        total_in_shard = 0
        for line in leaf_lines:
            start = completed * LEAF
            size = min(LEAF, N - start)
            w, f, minimum, h = valid_line(line, start, size)
            total_in_shard += size
            weight_sum += w
            flats += f
            if absolute_min is None or minimum < absolute_min:
                absolute_min = minimum
                absolute_row = h
            prev = chain.hex()
            chain = hashlib.sha256(chain + line.encode('ascii') + b'\n').digest()
            hbi.append('HTTP0_YM_HBI|leaf=' + str(completed) + '|row_start=' + str(start)
                       + '|row_count=' + str(size) + '|prev=' + prev
                       + '|sha256=' + chain.hex() + '|json=0')
            frozen.append(line)
            completed += 1
        s = fields(shard_lines[0], 'HTTP0_YM_SHARD')
        for k, target in (
            ('id', shard), ('first', shard * SHARD_LEAVES * LEAF),
            ('rows', total_in_shard), ('leaves', expected_leaf_count)
        ):
            if s.get(k) != str(target):
                fail('shard_total_' + str(shard) + '_' + k)
        if s.get('status') != 'PASS':
            fail('shard_status_' + str(shard))
    if completed != LEAVES or weight_sum != SUM_W or flats != 7 or absolute_min != BOUND or absolute_row != TIGHT_ROW:
        fail('whole_store_census_or_minimum')
    final = ('HTTP0_YM_FULL_ROW_REBUILD|rows=' + str(N) + '|leaves=' + str(completed)
             + '|electric_moves=' + str(N * 72) + '|orbit_weight_sum=' + str(weight_sum)
             + '|flats=' + str(flats) + '|min_row=' + str(absolute_row)
             + '|min_ratio_microJE=' + str(absolute_min) + '|root_sha256=' + chain.hex()
             + '|source_code_sha256=' + code_sha + '|input_key_sha256=' + KEY_SHA
             + '|input_vector_sha256=' + VEC_SHA + '|status=PASS|json=0')
    (output / 'ALL-LEAVES.hbp').write_text('\n'.join(frozen) + '\n' + final + '\n', encoding='ascii')
    (output / 'LEAVES.hbi').write_text('\n'.join(hbi) + '\n', encoding='ascii')
    print(final)


if __name__ == '__main__':
    main()
