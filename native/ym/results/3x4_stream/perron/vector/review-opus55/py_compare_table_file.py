# Read last: the author's table file on D: against the signature set from my own constraints and my own rule. Set equality.
# usage: py_compare_table_file.py AUTHOR_TABLE LX LY   Python integers, json=0. Exit 1 on any difference.
import sys
from math import isqrt
PATH, LX, LY = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
P, NL = LX * LY, 2 * LX * LY
def c2s(n):
    return 0 if n == 0 else isqrt(4 * n - 1) + 1
def adj(s):
    if s == 0:
        return 0
    if s == P:
        return 2 * s
    return 2 * s - min(c2s(s), min(LX, LY), c2s(P - s))
RULE = ((2, 0, 3),), ((0, 0, 1), (0, 1, 2)), ((2, -1, 3),), ((-2, 0, 1), (-2, 2, 2)), ((-2, 1, 2), (-2, 2, 1)), ((0, -1, 1), (0, 0, 2)), ((2, -2, 3),)
mine = set()
for a in range(0, P + 1, 2):
    for b in range(0, P - a + 1):
        if (a, b) == (0, 0):
            continue
        A, B, I = adj(a), adj(b), adj(a + b)
        for tt in range(0, A + 1):
            for tc in range(0, min(4 * a - 2 * tt, 4 * b) + 1):
                for cc in range(0, min(B, (4 * b - tc) // 2, I - tt - tc) + 1):
                    et, ec = 4 * a - 2 * tt - tc, 4 * b - tc - 2 * cc
                    ee = NL - et - ec - tt - tc - cc
                    if ee < 0:
                        continue
                    for tts in range(0, tt + 1):
                        n = (ee, et, ec, tts, tt - tts, tc, cc)
                        near = {}
                        flat = 0
                        for pat, c in enumerate(n):
                            if c:
                                for da, db, m in RULE[pat]:
                                    t = (a + da, b + db)
                                    if t == (0, 0):
                                        flat += m * c
                                    else:
                                        near[t] = near.get(t, 0) + m * c
                        mine.add((a, b, flat, tuple(sorted(near.items()))))
names = {}
theirs = set()
diag_bad = 0
for line in open(PATH, encoding='utf-8'):
    f = dict(x.split('=', 1) for x in line.strip().split('|')[1:] if '=' in x)
    if line.startswith('LUMP|'):
        names[int(f['id'])] = (int(f['a']), int(f['b']))
    elif line.startswith('SIG|'):
        a, b = names[int(f['lump'])]
        near = {}
        if f['n']:
            for p in f['n'].split(','):
                i, c = p.split(':')
                near[names[int(i)]] = int(c)
        if int(f['diag']) != 3 * NL:
            diag_bad += 1
        theirs.add((a, b, int(f['flat']), tuple(sorted(near.items()))))
print("TABLE_FILE_COMPARE|Lx=%d|Ly=%d|mine=%d|theirs=%d|only_mine=%d|only_theirs=%d|diag_bad=%d|verdict=%s|json=0" % (LX, LY, len(mine), len(theirs), len(mine - theirs), len(theirs - mine), diag_bad, 'SAME' if mine == theirs and not diag_bad else 'DIFFER'))
sys.exit(0 if mine == theirs and not diag_bad else 1)
