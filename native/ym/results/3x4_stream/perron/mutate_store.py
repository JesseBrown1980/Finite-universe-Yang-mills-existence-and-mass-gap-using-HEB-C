# Damage controls for fullrebuild: a small store with one change and its merkle REPAIRED, so only recomputing the row can catch it.
# usage: mutate_store.py IN OUT MODE ROW   MODE = entry (z-1 on an off-diagonal, z+1 on the diagonal, row sum stays 0) | mag | weight
# Integer only, json=0.
import hashlib, struct, sys
src, out, mode, row = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
b = bytearray(open(src, 'rb').read())
end = b.index(b'\n')
line = b[:end].decode()
f = dict(x.split('=', 1) for x in line.split('|') if '=' in x)
n, payload = int(f['n']), int(f['payload_bytes'])
p = 4096
for h in range(n):
    w, mag, cnt = struct.unpack_from('<IHH', b, p)
    if h == row:
        if mode == 'weight':
            struct.pack_into('<I', b, p, w + 1)
        elif mode == 'mag':
            struct.pack_into('<H', b, p + 4, mag + 1)
        elif mode == 'entry':
            ents = [struct.unpack_from('<Ii', b, p + 8 + 8 * k) for k in range(cnt)]
            off = next(k for k, (j, z) in enumerate(ents) if j != h)
            dia = next(k for k, (j, z) in enumerate(ents) if j == h)
            struct.pack_into('<Ii', b, p + 8 + 8 * off, ents[off][0], ents[off][1] - 1)
            struct.pack_into('<Ii', b, p + 8 + 8 * dia, ents[dia][0], ents[dia][1] + 1)
        else:
            raise SystemExit('bad mode')
    p += 8 + 8 * cnt
# Repair the merkle, the same way the store's own header defines it, so the damage survives the hash.
pl = bytes(b[4096:4096 + payload])
hx = ''.join(hashlib.sha256(pl[i:i + (16 << 20)]).hexdigest() for i in range(0, len(pl), 16 << 20))
root = hashlib.sha256(hx.encode()).hexdigest()
new_line = line.replace('payload_merkle=' + f['payload_merkle'], 'payload_merkle=' + root)
assert len(new_line) == len(line)
b[:end] = new_line.encode()
open(out, 'wb').write(b)
print('MUTATED|mode=%s|row=%d|merkle_repaired=1|old=%s|new=%s|json=0' % (mode, row, f['payload_merkle'][:16], root[:16]))
