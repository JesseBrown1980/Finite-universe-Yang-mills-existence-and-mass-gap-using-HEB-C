# Exact count of gauge-fixed configurations per lump, from characters of S3 on the punctured torus, against my enumerations.
# For a fixed assignment of classes to plaquettes, the number of gauge-fixed configurations is the number of (x, y, c_1..c_k) with [x, y] c_1 ... c_k = e and c_i in the class given:
#   N = |G| sum_rho d_rho^(-k) prod_i |C_i| chi_rho(C_i).
# For S3, with a transpositions and b 3-cycles: N = 6 * 3^a 2^b (1 + (-1)^a + 0^a (-1)^b / 2^(a+b)), so 12 * 3^a 2^b for even a >= 2, 12 * 2^b + 6 (-1)^b for a = 0, 0 for odd a.
# Lump count = P! / (a! b! (P-a-b)!) * N, and the total over lumps must be 6^(P+1).
# usage: py_lump_counts.py LX LY [census FILE] [ritz FILE]... Python integers, json=0. Exit 1 on any difference.
import sys
from math import comb
LX, LY = int(sys.argv[1]), int(sys.argv[2])
P = LX * LY
def n_of(a, b):
    if a % 2:
        return 0
    if a == 0:
        return 12 * 2 ** b + 6 * (-1) ** b
    return 12 * 3 ** a * 2 ** b
count = {}
for a in range(0, P + 1):
    for b in range(0, P - a + 1):
        c = comb(P, a) * comb(P - a, b) * n_of(a, b)
        if c:
            count[(a, b)] = c
total = sum(count.values())
ok = total == 6 ** (P + 1) and count[(0, 0)] == 18
print("LUMP_FORMULA|Lx=%d|Ly=%d|lumps=%d|total=%d|expected=%d|flats=%d|json=0" % (LX, LY, len(count), total, 6 ** (P + 1), count[(0, 0)]))
args = sys.argv[3:]
for kind, path in zip(args[0::2], args[1::2]):
    bad = 0
    n = 0
    if kind == 'census':
        for line in open(path, encoding='utf-8'):
            if line.startswith('LUMP|'):
                d = dict(x.split('=', 1) for x in line.strip().split('|')[1:] if '=' in x)
                k = (int(d['a']), int(d['b']))
                n += 1
                if count.get(k, 0) != int(d['configs']):
                    bad += 1
    else:
        byM = {}
        for k, c in count.items():
            m = 2 * k[0] + 3 * k[1]
            if m:
                byM[m] = byM.get(m, 0) + c
        seen = set()
        for line in open(path, encoding='utf-8'):
            if line.startswith('MODEL_M|'):
                d = dict(x.split('=', 1) for x in line.strip().split('|')[1:] if '=' in x)
                m = int(d['M'])
                seen.add(m)
                n += 1
                if byM.get(m, 0) != int(d['gauge_fixed_configs']):
                    bad += 1
        top = max(seen)
        missing = [m for m in byM if m <= top and m not in seen]
        bad += len(missing)
    print("LUMP_COUNT_CHECK|kind=%s|file=%s|rows=%d|bad=%d|json=0" % (kind, path.split('/')[-1], n, bad))
    ok = ok and bad == 0
sys.exit(0 if ok else 1)
