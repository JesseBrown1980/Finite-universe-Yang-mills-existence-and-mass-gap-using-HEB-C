#!/usr/bin/env python3
"""Direct PE comparison: original executable vs rebuilt executable.
Excluded byte ranges (pre-registered, operator-approved, nothing else):
  1. COFF header TimeDateStamp
  2. every IMAGE_DEBUG_DIRECTORY entry TimeDateStamp
  3. CodeView RSDS GUID + Age
  4. CodeView RSDS PDB path (through its NUL terminator)
Rules: if the two files differ in size or in the offset/length of any excluded field,
the comparison cannot be made reliably -> INCONCLUSIVE_layout. Otherwise every byte
outside the excluded ranges must match: 0 differing bytes -> PASS, else MISMATCH.
Output: HBP rows, json=0."""
import struct, sys, hashlib

def u16(b, o): return struct.unpack_from('<H', b, o)[0]
def u32(b, o): return struct.unpack_from('<I', b, o)[0]

def excluded(b):
    pe = u32(b, 0x3c)
    if b[pe:pe + 4] != b'PE\0\0': raise ValueError('not_PE')
    coff = pe + 4; nsec = u16(b, coff + 2); optsz = u16(b, coff + 16); opt = coff + 20
    if u16(b, opt) != 0x20b: raise ValueError('not_PE32plus')
    ex = [('coff_timestamp', coff + 4, 4)]
    ndd = u32(b, opt + 108); dd = opt + 112; st = opt + optsz
    secs = [(u32(b, st + 40*i + 12), max(u32(b, st + 40*i + 8), u32(b, st + 40*i + 16)), u32(b, st + 40*i + 20)) for i in range(nsec)]
    def r2o(rva):
        for va, sz, rp in secs:
            if va <= rva < va + sz: return rva - va + rp
        raise ValueError('rva_unmapped')
    if ndd > 6 and u32(b, dd + 52):
        do = r2o(u32(b, dd + 48))
        for k in range(u32(b, dd + 52) // 28):
            e = do + 28*k; typ = u32(b, e + 12); ptr = u32(b, e + 24)
            ex.append((f'debugdir{k}_type{typ}_timestamp', e + 4, 4))
            if typ == 2 and b[ptr:ptr + 4] == b'RSDS':
                ex.append(('rsds_guid_age', ptr + 4, 20))
                end = b.index(b'\0', ptr + 24)
                ex.append(('pdb_path', ptr + 24, end + 1 - (ptr + 24)))
    return ex, u32(b, opt + 64)

def compare(name, a_path, b_path):
    a = open(a_path, 'rb').read(); b = open(b_path, 'rb').read()
    sa, sb = hashlib.sha256(a).hexdigest(), hashlib.sha256(b).hexdigest()
    head = f'PECMP|bin={name}|orig_sha256={sa}|rebuilt_sha256={sb}|orig_bytes={len(a)}|rebuilt_bytes={len(b)}'
    try:
        ea, ca = excluded(a); eb, cb = excluded(b)
    except Exception as e:
        return 'INCONCLUSIVE', f'{head}|verdict=INCONCLUSIVE_parse|reason={type(e).__name__}:{e}|json=0'
    if len(a) != len(b) or ea != eb:
        return 'INCONCLUSIVE', f'{head}|verdict=INCONCLUSIVE_layout|fields_orig={ea}|fields_rebuilt={eb}|json=0'.replace(' ', '')
    mask = bytearray(len(a))
    for _, o, n in ea:
        mask[o:o + n] = b'\1' * n
    diffs = [i for i in range(len(a)) if a[i] != b[i] and not mask[i]]
    exdiff = ','.join(f'{nm}:{int(a[o:o+n] != b[o:o+n])}' for nm, o, n in ea)
    v = 'PASS' if not diffs else 'MISMATCH'
    first = ','.join(hex(i) for i in diffs[:16])
    return v, (f'{head}|optional_header_checksum_orig={ca}|rebuilt={cb}|excluded={exdiff}'
               f'|excluded_bytes={int(sum(mask))}|differing_bytes_outside_exclusions={len(diffs)}'
               f'|first_offsets={first or "-"}|verdict={v}|json=0')

if __name__ == '__main__':
    v, row = compare(sys.argv[1], sys.argv[2], sys.argv[3]); print(row)
    sys.exit({'PASS': 0, 'MISMATCH': 1}.get(v, 2))
