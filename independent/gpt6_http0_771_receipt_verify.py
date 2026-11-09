#!/usr/bin/env python3
"""Independent integer-only archive audit of the 771-leaf HTTP-0 Yang-Mills certificate."""
from hashlib import sha256
from pathlib import Path
import sys

N, L, COUNT, BOUND = 45508080, 59049, 771, 94070673
KEY = 'eefd7752031cf6e1cbfd53dd47128805d1a98bb41de0a9e269222d0e2c6e3cbc'
VEC = 'f5c5428db1fc5d91d2ab891689f0dac7263dc26c8f9b60a2db82728f6ea0dcd1'
SOURCE = '2f9c33c526ae333c119a663746d57869be368a1d539bdf3f4a9d94a04e45eaab'
ROOT = '7c3c636e873b3e3000f532ea982bb0661711b0a15862cbf92e2beb97a8413c1f'

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def parse(line, tag):
    parts = line.split('|')
    require(parts[0] == tag and parts[-1] == 'json=0', 'record tag')
    result = {}
    for part in parts[1:]:
        a, sep, b = part.partition('=')
        require(sep and a not in result, 'record syntax')
        result[a] = b
    return result

def audit(root, sabotage=''):
    archive = root.joinpath('aggregate')
    receipts = {name: archive.joinpath(name).read_bytes()
                for name in ('ALL-LEAVES.hbp', 'LEAVES.hbi', 'SHA256SUMS')}
    summary = root.joinpath('whole-store-verdict.hbp').read_bytes()
    if sabotage == 'leaf':
        receipts['ALL-LEAVES.hbp'] = receipts['ALL-LEAVES.hbp'].replace(b'rows=59049', b'rows=59048', 1)
    if sabotage == 'index':
        receipts['LEAVES.hbi'] = receipts['LEAVES.hbi'].replace(b'row_count=59049', b'row_count=59048', 1)
    if sabotage == 'summary':
        summary = summary.replace(b'min_row=45507968', b'min_row=45507967')
    checks = {}
    for row in receipts['SHA256SUMS'].decode('ascii').splitlines():
        pieces = row.split()
        require(len(pieces) == 2 and pieces[1] not in checks, 'manifest shape')
        checks[pieces[1]] = pieces[0]
    for name in ('ALL-LEAVES.hbp', 'LEAVES.hbi'):
        require(checks.get('aggregate/' + name) == sha256(receipts[name]).hexdigest(), 'sha manifest ' + name)
    require(checks.get('whole-store-verdict.hbp') == sha256(summary).hexdigest(), 'sha manifest summary')
    lines = receipts['ALL-LEAVES.hbp'].decode('ascii').splitlines()
    index_rows = receipts['LEAVES.hbi'].decode('ascii').splitlines()
    require(len(lines) == COUNT + 1 and len(index_rows) == COUNT, '771 leaves count')
    require(lines[-1] + '\n' == summary.decode('ascii'), 'summary byte match')
    seed = ('HTTP0-YM-ROWFREEZE-1|' + KEY + '|' + VEC + '|' + SOURCE).encode('ascii')
    chain = sha256(seed).digest()
    expected_row, weight_sum, flat_count = 0, 0, 0
    minratio, minrow = None, None
    for idx, (line, index_line) in enumerate(zip(lines[:-1], index_rows)):
        fields = parse(line, 'HTTP0_YM_REBUILT_LEAF')
        index = parse(index_line, 'HTTP0_YM_HBI')
        size = min(L, N - expected_row)
        for k, v in (('first', expected_row), ('rows', size), ('electric_moves', size * 72),
                     ('reverse_pairs', 8), ('bound_microJE', BOUND)):
            require(fields.get(k) == str(v), 'leaf ' + str(idx) + ' ' + k)
        require(fields.get('status') == 'PASS', 'leaf status')
        row_min, local_min = int(fields['min_ratio_microJE']), int(fields['min_row'])
        require(row_min >= BOUND and expected_row <= local_min < expected_row + size, 'minimum')
        weight_sum += int(fields['orbit_weight_sum'])
        flat_count += int(fields['flats'])
        if minratio is None or row_min < minratio:
            minratio, minrow = row_min, local_min
        previous = chain.hex()
        chain = sha256(chain + line.encode('ascii') + b'\n').digest()
        for k, v in (('leaf', idx), ('row_start', expected_row), ('row_count', size),
                     ('prev', previous), ('sha256', chain.hex())):
            require(index.get(k) == str(v), 'index ' + str(idx) + ' ' + k)
        expected_row += size
    require(expected_row == N and weight_sum == 6**13 and flat_count == 7, 'global census')
    require(minratio == BOUND and minrow == 45507968, 'global minimum')
    final = parse(lines[-1], 'HTTP0_YM_FULL_ROW_REBUILD')
    for k, v in (('rows', N), ('leaves', COUNT), ('electric_moves', N*72),
                 ('orbit_weight_sum', weight_sum), ('flats', flat_count),
                 ('min_row', minrow), ('min_ratio_microJE', minratio),
                 ('root_sha256', ROOT), ('source_code_sha256', SOURCE),
                 ('input_key_sha256', KEY), ('input_vector_sha256', VEC), ('status', 'PASS')):
        require(final.get(k) == str(v), 'final ' + k)
    require(chain.hex() == ROOT, 'root')
    return ('HTTP0_YM_THIRD_REPLAY|rows=45508080|leaves=771|electric_moves=3276581760'
            '|flats=7|weight_sum=13060694016|min_row=45507968|min_ratio_microJE=94070673'
            '|root_sha256=' + chain.hex() + '|status=PASS|json=0')

def main():
    require(len(sys.argv) in (2, 3), 'usage: DIR [--selftest]')
    root = Path(sys.argv[1])
    print(audit(root))
    if len(sys.argv) == 3:
        require(sys.argv[2] == '--selftest', 'invalid control')
        for name in ('leaf', 'index', 'summary'):
            try:
                audit(root, name)
            except ValueError:
                print('HTTP0_YM_THIRD_RED|fault=' + name + '|status=REJECTED|json=0')
            else:
                raise ValueError('mutation accepted: ' + name)

if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, UnicodeError) as error:
        print('HTTP0_YM_THIRD_FAIL|reason=' + str(error) + '|json=0')
        sys.exit(2)
