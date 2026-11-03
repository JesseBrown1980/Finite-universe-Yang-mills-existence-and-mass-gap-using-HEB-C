# Does the author's points() enumerate every integer solution of the constraints? Brute force from the constraints alone, then set equality per lump.
# The author's file is read as text and only its pure functions are executed, in a namespace of their own, as the subject under test. Nothing of it enters my own checks.
# usage: py_points_compare.py AUTHOR_LOCAL_TABLE_PY LX LY [--sabotage]
# With --sabotage the brute force drops one solution per lump (or adds one impossible row), and the comparison must go red.
# Python integers only, json=0. Exit 1 on any difference.
import sys
from math import isqrt
src = open(sys.argv[1], encoding='utf-8').read()
cut = src.index('def signature')
head = src[:cut]
ns = {}
exec(compile(head, 'author_local_table_head', 'exec'), ns)
LX, LY = int(sys.argv[2]), int(sys.argv[3])
sabotage = '--sabotage' in sys.argv
P = LX * LY
NL = 2 * P


def c2s(n):
    return 0 if n == 0 else isqrt(4 * n - 1) + 1


def adj(s):
    if s == 0:
        return 0
    if s == P:
        return 2 * s
    return 2 * s - min(c2s(s), min(LX, LY), c2s(P - s))


def brute(a, b):
    out = set()
    # Every value of the free counts allowed by nonnegativity alone, then the filter.
    for tts in range(0, 2 * a + 1):
        for ttd in range(0, 2 * a - tts + 1):
            for tc in range(0, 4 * min(a, b) + 1):
                for cc in range(0, 2 * b + 1):
                    et = 4 * a - 2 * (tts + ttd) - tc
                    ec = 4 * b - tc - 2 * cc
                    inner = tts + ttd + tc + cc
                    ee = NL - et - ec - inner
                    if et < 0 or ec < 0 or ee < 0:
                        continue
                    if tts + ttd > adj(a) or cc > adj(b) or inner > adj(a + b):
                        continue
                    out.add((ee, et, ec, tts, ttd, tc, cc))
    return out


lumps = [(a, b) for a in range(0, P + 1, 2) for b in range(0, P - a + 1) if (a, b) != (0, 0)]
total, diff = 0, 0
for a, b in lumps:
    mine = brute(a, b)
    if sabotage and mine:
        mine.discard(next(iter(mine)))
    theirs_list = list(ns['points'](a, b, LX, LY))
    theirs = {(n['ee'], n['eT'], n['eC'], n['TTs'], n['TTd'], n['TC'], n['CC']) for n in theirs_list}
    assert len(theirs) == len(theirs_list)
    # Each point satisfies the sum rule.
    for t in theirs:
        assert sum(t) == NL
    total += len(mine)
    if mine != theirs:
        diff += 1
        if diff <= 5:
            print("POINTS_DIFF|a=%d|b=%d|only_mine=%s|only_theirs=%s|json=0" % (a, b, sorted(mine - theirs)[:5], sorted(theirs - mine)[:5]))
print("POINTS_COMPARE|Lx=%d|Ly=%d|lumps=%d|solutions=%d|lumps_differing=%d|sabotage=%d|verdict=%s|json=0" % (LX, LY, len(lumps), total, diff, 1 if sabotage else 0, 'SAME' if diff == 0 else 'DIFFER'))
sys.exit(1 if diff else 0)
