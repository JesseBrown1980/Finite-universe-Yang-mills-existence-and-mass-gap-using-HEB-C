# C2: where can a release build wrap silently? Absurd couplings on the real 2x2 store, and a crafted store outside the strict row structure.
import hashlib, os, struct, subprocess, sys
sys.path.insert(0, "C:/tmp/opus55/ym-two-sided")
from ownlib import *
R = "C:/tmp/opus55/ym-two-sided"
T, C = f"{R}/bin/perronritz-grid.exe", f"{R}/bin/perroncert.exe"
tmp = f"{R}/tmpwrap"
os.makedirs(tmp, exist_ok=True)


def run(*a):
    r = subprocess.run([str(x) for x in a], capture_output=True, text=True)
    return r.returncode, r.stdout.strip().splitlines()


D = f"{R}/dev22.bin"
vec = f"{R}/vec/2x2-46400000.bin"
J = 2**128 // 1000 + 1  # 1000 * JB wraps to a small positive number
print("JB_WRAP", J, 1000 * J - 2**128)
rc, out = run(T, "pass", D, 0, 1000, f"9000,{J}", vec)
print(rc, [l for l in out if "JB=" in l])
rc, out = run(C, "check", D, 0, 1000, J, vec)
print(rc, [l[:150] for l in out])
K = 2**127 // 1000 + 5
print("JB_WRAP_NEG", K, 1000 * K - 2**128)
rc, out = run(T, "pass", D, 0, 1000, f"{K}", vec)
print(rc, [l for l in out if "JB=" in l])
Je = 2**128 // 1000 + 1
rc, out = run(T, "pass", D, 0, Je, "9000", vec)
print("JE_WRAP", rc, [l for l in out if "JB=" in l])

# Moderately large JE: u * ed wraps in the table while the forms stay exact in BigInt.
Je = 10**32
rc, out = run(T, "pass", D, 0, Je, "9000", vec)
print("JE_1e32", rc, [l for l in out if "JB=" in l or "ERROR" in l])
fld, rows, ok, _ = read_store(D)
keep, W, M, Z = build(rows)
x = read_vec(vec)
H = hp_rows(Z, M, Je, 9000)
print("JE_1e32_exact_barta", barta(H, [x[h] for h in keep]))
rc, out = run(C, "check", D, 0, Je, 9000, vec)
print("JE_1e32_perroncert", rc, [l[:160] for l in out])
print("JE_threshold: u*ed wraps once 1000*JE*max|ed| >= 2^127; max|ed| here", max(abs(sum(v * x[keep[j]] for j, v in Z[i].items())) for i in range(len(keep))))


# A crafted store: one row with 9000 repeated columns at z = -2^31. Row sum nonzero, columns repeated: outside check_d_strict's structure.
def write_store(path, rows):
    payload = bytearray()
    for w, mag, ent in rows:
        payload += struct.pack("<IHH", w, mag, len(ent))
        for j, z in ent:
            payload += struct.pack("<Ii", j, z)
    shas = "".join(hashlib.sha256(bytes(payload[i : i + LEAF])).hexdigest() for i in range(0, len(payload), LEAF))
    line = f"YMROOMHDR|L=1x{len(rows)}|sector=Sx+Sy+|n={len(rows)}|nl=1|rooms=0|entries=0|payload_bytes={len(payload)}|payload_merkle={hashlib.sha256(shas.encode()).hexdigest()}|w_self_adjoint=PASS|json=0\n"
    b = line.encode()
    with open(path, "wb") as f:
        f.write(b + bytes(4096 - len(b)) + bytes(payload))


rows2 = [(1, 3, [(0, 10)] + [(1, -(2**31))] * 9000), (1, 3, [(1, 10)] + [(0, -(2**31))] * 9000)]
s = f"{tmp}/huge.bin"
write_store(s, rows2)
vv = [1, 2**63 - 1]
p = f"{tmp}/huge-d.bin"
with open(p, "wb") as f:
    f.write(b"".join(struct.pack("<q", q) for q in vv))
rc, out = run(T, "pass", s, 0, 1000, "9000", p)
print("HUGE_pass", rc, [l for l in out if "LOWER" in l or "ERROR" in l or "UPPER" in l][:4])
rc, out = run(C, "check", s, 0, 1000, 9000, p)
print("HUGE_check", rc, [l[:170] for l in out])
exact = None
for h, (w, mag, ent) in enumerate(rows2):
    t = 1000 * 9000 * mag * vv[h] + 10**6 * sum(z * vv[j] for j, z in ent)
    q = t // vv[h]
    exact = q if exact is None else min(exact, q)
print("HUGE_exact_min_ratio", exact)
rc = subprocess.run(["python3", "-I", f"{R}/../../../asolaria-noop"], capture_output=True) if False else None
c = subprocess.run(["python3", "-I", "D:/ym-3x4-room-run/p0-ball/check_d_strict.py", s, p, "1000", "9000"], capture_output=True, text=True)
print("HUGE_strict", c.returncode, c.stdout.strip()[:160])
