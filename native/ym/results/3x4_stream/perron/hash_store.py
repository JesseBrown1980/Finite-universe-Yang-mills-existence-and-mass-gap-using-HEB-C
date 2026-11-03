# Read-only: hashes the local store and the key table, and compares them with the public manifest. usage: hash_store.py MANIFEST
import hashlib, sys, time
want = {}
for ln in open(sys.argv[1], encoding="ascii"):
    p = ln.split()
    if len(p) == 2:
        want[p[1].lstrip("*").split("/")[-1]] = p[0]
assert len(want) == 34
t0 = time.time()
ok = 0
for k in range(341, 375):
    name = f"sector-{k}.rooms"
    h = hashlib.sha256()
    with open("D:/ASOLARIA-HOST8-ROOMS-300G/" + name, "rb") as f:
        while True:
            b = f.read(1 << 22)
            if not b:
                break
            h.update(b)
    if h.hexdigest() == want[name]:
        ok += 1
    else:
        print("MISMATCH", name, h.hexdigest(), want[name], flush=True)
h = hashlib.sha256()
with open("D:/ym-3x4-room-run/passA.bin", "rb") as f:
    while True:
        b = f.read(1 << 22)
        if not b:
            break
        h.update(b)
print(f"STORE_HASHES|sectors_match={ok}/34|manifest_sha256={hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest()}|passA_sha256={h.hexdigest()}|secs={int(time.time()-t0)}|json=0", flush=True)
