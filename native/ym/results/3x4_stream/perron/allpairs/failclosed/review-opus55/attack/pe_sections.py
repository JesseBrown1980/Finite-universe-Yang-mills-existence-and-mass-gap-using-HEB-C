# Hash each PE section of two executables and report byte differences. Read only. usage: pe_sections.py A B
import hashlib, struct, sys
def load(p):
    b = open(p, "rb").read()
    pe = struct.unpack_from("<I", b, 0x3C)[0]
    nsec = struct.unpack_from("<H", b, pe + 6)[0]
    ts = struct.unpack_from("<I", b, pe + 8)[0]
    opt = struct.unpack_from("<H", b, pe + 20)[0]
    secs = {}
    o = pe + 24 + opt
    for i in range(nsec):
        name = b[o:o + 8].rstrip(b"\0").decode()
        vs, va, rs, rp = struct.unpack_from("<IIII", b, o + 8)
        secs[name] = (rp, rs, hashlib.sha256(b[rp:rp + rs]).hexdigest())
        o += 40
    return b, ts, secs
A, B = sys.argv[1], sys.argv[2]
a, ta, sa = load(A)
b, tb, sb = load(B)
print("PE_TIMESTAMP|a=%d|b=%d|equal=%d|json=0" % (ta, tb, ta == tb))
for k in sorted(set(sa) | set(sb)):
    print("PE_SECTION|name=%s|a_size=%s|b_size=%s|equal=%d|a_sha16=%s|json=0" % (k, sa.get(k, (0, 0, ""))[1], sb.get(k, (0, 0, ""))[1], sa.get(k, (0, 0, ""))[2] == sb.get(k, (0, 0, ""))[2], sa.get(k, (0, 0, "-"))[2][:16]))
if len(a) == len(b):
    diff = [i for i in range(len(a)) if a[i] != b[i]]
    print("PE_BYTES|len=%d|differing=%d|first=%s|json=0" % (len(a), len(diff), ",".join(hex(x) for x in diff[:40])))
    runs = []
    for i in diff:
        if runs and i == runs[-1][1] + 1:
            runs[-1][1] = i
        else:
            runs.append([i, i])
    for s, e in runs[:40]:
        print("PE_DIFF_RUN|start=%s|end=%s|len=%d|a=%s|b=%s|json=0" % (hex(s), hex(e), e - s + 1, a[s:min(e + 1, s + 60)], b[s:min(e + 1, s + 60)]))
