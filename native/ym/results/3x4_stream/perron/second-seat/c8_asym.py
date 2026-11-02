# C8: how much does E_ab = E_ba on chosen vectors catch? Mutate one entry of the real 2x2 store, fix the merkle, keep row sums at 0, and ask all the tools.
import hashlib, itertools, os, struct, subprocess, sys
sys.path.insert(0, "C:/tmp/opus55/ym-two-sided")
from ownlib import *

R = "C:/tmp/opus55/ym-two-sided"
T = f"{R}/bin/perronritz-grid.exe"
C = f"{R}/bin/perroncert.exe"
STRICT = "D:/ym-3x4-room-run/p0-ball/check_d_strict.py"
tmp = f"{R}/tmpasym"
os.makedirs(tmp, exist_ok=True)
DEV = f"{R}/dev22.bin"
fld, rows, ok, _ = read_store(DEV)
vecs = [f"{R}/vec/2x2-{t}.bin" for t in (45000000, 46000000, 46400000)]
ds = [read_vec(v) for v in vecs]
n = len(rows)
rows = [(w, m, list(e)) for w, m, e in rows]


def write_like(path, rws, nl_field=8):
    payload = bytearray()
    for w, mag, ent in rws:
        payload += struct.pack("<IHH", w, mag, len(ent))
        for j, z in ent:
            payload += struct.pack("<Ii", j, z)
    rooms = len(payload) // 8
    entries = sum(len(e) for _, _, e in rws)
    # pad to the same stream layout as the store
    total = int(fld["payload_bytes"])
    payload += bytes(total - len(payload))
    shas = "".join(hashlib.sha256(bytes(payload[i : i + LEAF])).hexdigest() for i in range(0, len(payload), LEAF))
    line = f"YMROOMHDR|L={fld['L']}|sector={fld['sector']}|n={n}|nl={nl_field}|rooms={rooms}|entries={entries}|payload_bytes={total}|stream_bytes={int(total)+4096}|chunk=16MiB|payload_merkle={hashlib.sha256(shas.encode()).hexdigest()}|keys_sha256=none|w_self_adjoint=PASS|json=0\n"
    b = line.encode()
    with open(path, "wb") as f:
        f.write(b + bytes(4096 - len(b)) + bytes(payload))


def mutate(h, j):
    r2 = [(w, m, list(e)) for w, m, e in rows]
    w, m, e = r2[h]
    e2 = []
    for jj, z in e:
        if jj == j:
            e2.append((jj, z - 1))
        elif jj == h:
            e2.append((jj, z + 1))
        else:
            e2.append((jj, z))
    r2[h] = (w, m, e2)
    return r2


def tool_row(args):
    r = subprocess.run([T, "pass"] + args, capture_output=True, text=True)
    out = r.stdout.strip().splitlines()
    return r.returncode, out[-1][:170]


# Pair 1: any coupled pair
h, j = next((h, j) for h in range(n) if rows[h][1] for j, z in rows[h][2] if j != h and z < 0 and rows[j][1])
p = f"{tmp}/m1.bin"
write_like(p, mutate(h, j))
print(f"MUTATION_1|row={h}|column={j}|z_minus_1|diag_plus_1|row_sum_stays_0|json=0")
print("  merkle_ok_on_mutant", read_store(p)[2])
print("  pass_1_vector", tool_row([p, "0", "1000", "9000", vecs[2]]))
print("  pass_2_vectors", tool_row([p, "0", "1000", "9000", vecs[1], vecs[2]]))
print("  pass_3_vectors", tool_row([p, "0", "1000", "9000"] + vecs))
s = subprocess.run(["python3", "-I", STRICT, p, vecs[2], "1000", "9000", "--self-adjoint", "27"], capture_output=True, text=True)
print("  strict_self_adjoint", s.returncode, s.stdout.strip()[:120])
s = subprocess.run(["python3", "-I", STRICT, p, vecs[2], "1000", "9000"], capture_output=True, text=True)
print("  strict_without_the_form", s.returncode, s.stdout.strip()[:150])
c = subprocess.run([C, "check", p, "0", "1000", "9000", vecs[2]], capture_output=True, text=True)
print("  perroncert_check", c.returncode, c.stdout.strip()[:140])

# Pair 2: coupled rows where all vectors are exactly proportional, so the chosen-vector test cannot see this pair.
blind = []
for h in range(n):
    if rows[h][1] == 0:
        continue
    for j, z in rows[h][2]:
        if j <= h or z == 0 or rows[j][1] == 0:
            continue
        if all(ds[a][h] * ds[b][j] == ds[b][h] * ds[a][j] for a, b in itertools.combinations(range(3), 2)):
            blind.append((h, j))
print(f"BLIND_PAIRS_FOR_THE_THREE_STORED_VECTORS|count={len(blind)}|first={blind[:5]}|json=0")
pairs_total = sum(1 for h in range(n) if rows[h][1] for j, z in rows[h][2] if j > h and z != 0 and rows[j][1])
print(f"COUPLED_PAIRS_TOTAL|{pairs_total}|json=0")
if blind:
    h, j = blind[0]
    p2 = f"{tmp}/m2.bin"
    write_like(p2, mutate(h, j))
    print("  blind_mutant_pass_3_vectors", tool_row([p2, "0", "1000", "9000"] + vecs))
    s = subprocess.run(["python3", "-I", STRICT, p2, vecs[2], "1000", "9000", "--self-adjoint", "27"], capture_output=True, text=True)
    print("  blind_mutant_strict", s.returncode, s.stdout.strip()[:120])

# Pair 3: two vectors built so that they are proportional at one coupled pair. That shows the blindness is a property of the test, not of this data.
h, j = next((h, j) for h in range(n) if rows[h][1] for j, z in rows[h][2] if j != h and z < 0 and rows[j][1])
d0 = list(ds[1])
d1 = list(ds[2])
d0[h], d0[j] = 1000, 1000
d1[h], d1[j] = 777, 777
a0, a1 = f"{tmp}/a0.bin", f"{tmp}/a1.bin"
for pth, v in ((a0, d0), (a1, d1)):
    with open(pth, "wb") as f:
        f.write(b"".join(struct.pack("<q", x) for x in v))
print("  built_vectors_on_mutant_1", tool_row([p, "0", "1000", "9000", a0, a1]))
