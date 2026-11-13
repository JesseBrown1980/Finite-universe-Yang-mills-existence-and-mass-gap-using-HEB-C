#!/usr/bin/env python3
"""inner_light_v1.py -- the Law 62 inner-light residue of Yang-Mills residual leaves.

FIND BEFORE BUILDING (Law 39) / IMPORT, DO NOT REIMPLEMENT (Law 63): the functions basis, own, free,
rot120 and shadow_waves are NOT rewritten here. Their source text is lifted by ast from the shipped,
hash-verified tools/shadow_net.py and executed unchanged. That tool is the July float scaffold of the
laws; this run is labelled FLOAT_SCAFFOLD_AS_SHIPPED. An integer redo is a separate step.

Read-only. No server is started, nothing is written outside the out file. HBP rows on stdout.
  python inner_light_v1.py <leafA> <leafB> <seeds>
"""
import ast, hashlib, math, sys
import numpy as np

TOOL = r"D:/asolaria-absorb/ASOLARIA-UNIVERSE-SIMULATOR/tools/shadow_net.py"
WANT = open(TOOL + ".sha256").read().split()[0]
src = open(TOOL, "rb").read()
assert hashlib.sha256(src).hexdigest() == WANT, "shadow_net.py differs from its sha256 sidecar"
tree = ast.parse(src.decode("utf-8"))
keep = []
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in ("basis", "own", "free", "rot120", "shadow_waves"):
        keep.append(node)
    elif isinstance(node, ast.Assign) and any(getattr(t, "id", "") in ("PATHS", "BAS", "MAXW") for t in node.targets):
        keep.append(node)
ns = {"np": np, "math": math}
exec(compile(ast.Module(body=keep, type_ignores=[]), TOOL, "exec"), ns)
PATHS, free, shadow_waves, MAXW = ns["PATHS"], ns["free"], ns["shadow_waves"], ns["MAXW"]
print("TOOL|path=%s|sha256=%s|functions_lifted=%s|rewritten=0|mode=FLOAT_SCAFFOLD_AS_SHIPPED|json=0"
      % (TOOL, WANT, ",".join(n.name if isinstance(n, ast.FunctionDef) else n.targets[0].id for n in keep)))


def leaves(path):
    rows = []
    for line in open(path):
        if line.startswith("LEAF|"):
            d = dict(w.split("=", 1) for w in line.strip().split("|")[1:] if "=" in w)
            rows.append((int(d["key"]), int(d["slack"])))
    rows.sort()
    return rows


def body(rows):  # the residual field as bytes: one 16-byte little-endian record per row, in key order
    return b"".join(s.to_bytes(16, "little") for _, s in rows)


def mixer(seed):  # SplitMix64, integer only
    st = [seed & 0xFFFFFFFFFFFFFFFF]
    def nxt():
        st[0] = (st[0] + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        z = st[0]
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        return z ^ (z >> 31)
    return nxt


def shuffled(seq, seed):
    r = mixer(seed)
    a = list(seq)
    for i in range(len(a) - 1, 0, -1):
        j = r() % (i + 1)
        a[i], a[j] = a[j], a[i]
    return a


def residues(raw, refraw):
    """first-wave normalised residue per path (Law 62: least-squares distance to the three-arm span)."""
    out = []
    for N in PATHS:
        w = shadow_waves(free(raw, N), free(refraw, N), MAXW[N])
        out.append(w[0] if w else float("nan"))
    return out


def fmt(v):
    return "_".join("%.6f" % x for x in v)


A, B, NS = leaves(sys.argv[1]), leaves(sys.argv[2]), int(sys.argv[3])
bA, bB = body(A), body(B)
print("BODY|name=A_weak_certificate|rows=%d|bytes=%d|sha256=%s|json=0" % (len(A), len(bA), hashlib.sha256(bA).hexdigest()))
print("BODY|name=B_strong_certificate|rows=%d|bytes=%d|sha256=%s|json=0" % (len(B), len(bB), hashlib.sha256(bB).hexdigest()))
print("PATHS|%s|arms=B_and_its_two_thirds_of_a_turn|json=0" % "_".join(map(str, PATHS)))

self_r = residues(bB, bB)
print("SELFCHECK|body=B_against_arms_from_B|residue=%s|must_be_zero=1|max=%.3e|json=0" % (fmt(self_r), max(self_r)))
real = residues(bA, bB)
print("REAL|body=A_against_arms_from_B|residue=%s|mean=%.6f|json=0" % (fmt(real), sum(real) / len(real)))

ctl = {"byte_shuffle": [], "row_shuffle": [], "random_values_same_bit_length": []}
for k in range(NS):
    ctl["byte_shuffle"].append(residues(bytes(shuffled(bA, 1000 + k)), bB))
    ctl["row_shuffle"].append(residues(body(list(enumerate(s for _, s in shuffled(A, 2000 + k)))), bB))
    r = mixer(3000 + k)
    rv = []
    for key, s in A:
        bl = max(s.bit_length(), 1)
        v = ((r() << 64) | r()) & ((1 << bl) - 1) | (1 << (bl - 1))
        rv.append((key, v))
    ctl["random_values_same_bit_length"].append(residues(body(rv), bB))
zero = residues(bytes(len(bA)), bB)
print("CONTROL|name=zero_body|residue=%s|json=0" % fmt(zero))
for name, runs in ctl.items():
    arr = np.array(runs)
    lo, hi, mu = arr.min(0), arr.max(0), arr.mean(0)
    below = (arr < np.array(real)).sum(0)
    verdict = ["OUTSIDE" if (real[i] < lo[i] or real[i] > hi[i]) else "INSIDE" for i in range(len(PATHS))]
    print("CONTROL|name=%s|runs=%d|min=%s|max=%s|mean=%s|runs_below_real=%s|per_path=%s|json=0"
          % (name, NS, fmt(lo), fmt(hi), fmt(mu), "_".join(map(str, below)), "_".join(verdict)))
print("END|room_writes=0|servers_started=0|json=0")
