# A store on the real 2x2 stream with one pair changed on both sides, row sums kept. Its header block toggles between the trusted block and the same block with the changed payload's merkle.
# A writer toggles the 4096 bytes on a copy while the tool runs. run_tool takes the merkle from one read of the block and the identity from another.
# usage: race.py EXE FIXTURE_GZ RUNS OUT_HBP  Integer only, json=0.
import gzip, hashlib, math, os, struct, subprocess, sys, time
EXE, GZ, RUNS, OUT = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
TMP = os.path.dirname(os.path.dirname(os.path.abspath(OUT))) + "/tmp"
base = gzip.open(GZ, "rb").read()
eol = base.index(b"\n")
LINE = base[:eol].decode()
F = dict(x.split("=", 1) for x in LINE.split("|") if "=" in x)
N, PAY = int(F["n"]), int(F["payload_bytes"])
P = base[4096:4096 + PAY]
ROWS, p = [], 0
for _ in range(N):
    w, mag, cnt = struct.unpack_from("<IHH", P, p)
    v = struct.unpack_from("<" + "Ii" * cnt, P, p + 8)
    ROWS.append([w, mag, [(v[2 * i], v[2 * i + 1]) for i in range(cnt)]])
    p += 8 + 8 * cnt
def sha(b): return hashlib.sha256(b).hexdigest()
def merkle(pl): return sha("".join(sha(pl[i:i + (16 << 20)]) for i in range(0, len(pl), 16 << 20)).encode())
h, i = next((h, j) for h in range(N) for j, _ in ROWS[h][2] if j < h)
g = math.gcd(ROWS[h][0], ROWS[i][0])
for rw, col, d in ((h, i, ROWS[i][0] // g), (i, h, ROWS[h][0] // g)):
    e = ROWS[rw][2]
    k = [q for q, x in enumerate(e) if x[0] == col][0]
    e[k] = (col, e[k][1] - d)
    k = [q for q, x in enumerate(e) if x[0] == rw][0]
    e[k] = (rw, e[k][1] + d)
out = bytearray()
for w, mag, ent in ROWS:
    out += struct.pack("<IHH", w, mag, len(ent))
    for j, z in ent:
        out += struct.pack("<Ii", j, z)
SYM2 = bytes(out).ljust(PAY, b"\0")
M2 = merkle(SYM2)
A = base[:4096]
B = A.replace(F["payload_merkle"].encode(), M2.encode())
assert len(B) == 4096 and A != B
path = TMP + "/race.bin"
open(path, "wb").write(A + SYM2)
stop = TMP + "/race.stop"
if os.path.exists(stop):
    os.remove(stop)
writer = """
import os, sys
path, stop, a, b = sys.argv[1], sys.argv[2], bytes.fromhex(sys.argv[3]), bytes.fromhex(sys.argv[4])
f = open(path, "r+b", buffering=0)
k = 0
while True:
    f.seek(0); f.write(b)
    f.seek(0); f.write(a)
    k += 1
    if k % 4096 == 0 and os.path.exists(stop):
        break
"""
BN = subprocess.BELOW_NORMAL_PRIORITY_CLASS
wr = subprocess.Popen([sys.executable, "-I", "-c", writer, path, stop, A[:eol + 1].ljust(4096, b"\0").hex(), B[:eol + 1].ljust(4096, b"\0").hex()], creationflags=BN)
time.sleep(1)
tally, shown, first_ok = {}, 0, None
log = open(OUT, "w", encoding="utf-8", newline="\n")
exe_sha = sha(open(EXE, "rb").read())
log.write("RACE_START|exe=%s|runs=%d|store=2x2_one_pair_changed_both_sides_row_sums_kept|payload_merkle_of_store=%s|payload_merkle_in_table=%s|trusted_block=%s|json=0\n" % (exe_sha[:16], RUNS, M2, F["payload_merkle"], sha(A)))
for run in range(RUNS):
    r = subprocess.run([EXE, path, "0"], capture_output=True, text=True, creationflags=BN)
    last = ([x for x in r.stdout.splitlines() if x.startswith("ALLPAIRS|")] or [""])[-1]
    f = dict(x.split("=", 1) for x in last.split("|") if "=" in x)
    key = (r.returncode, f.get("store_identity", "-"), f.get("identity_differs", "-"), (f.get("reason") or "-")[:22])
    tally[key] = tally.get(key, 0) + 1
    if r.returncode == 0 and shown < 3:
        shown += 1
        log.write("RACE_EXIT0|run=%d|%s|json=0\n" % (run, last.replace("|", "~")))
open(stop, "w").close()
wr.wait(timeout=30)
os.remove(stop)
for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
    log.write("RACE|exit=%d|store_identity=%s|identity_differs=%s|reason=%s|runs=%d|json=0\n" % (k[0], k[1], k[2], k[3].replace("|", "~"), v))
# Control: the same file, nobody writing.
open(path, "wb").write(A + SYM2)
r = subprocess.run([EXE, path, "0"], capture_output=True, text=True)
log.write("RACE_CONTROL|writer=none|block=trusted|exit=%d|json=0\n" % r.returncode)
open(path, "wb").write(B + SYM2)
r = subprocess.run([EXE, path, "0"], capture_output=True, text=True)
log.write("RACE_CONTROL|writer=none|block=with_changed_merkle|exit=%d|json=0\n" % r.returncode)
os.remove(path)
ex0 = sum(v for k, v in tally.items() if k[0] == 0)
log.write("RACE_DONE|runs=%d|exit0=%d|json=0\n" % (RUNS, ex0))
log.close()
print("RACE_DONE|runs=%d|exit0=%d|json=0" % (RUNS, ex0))
