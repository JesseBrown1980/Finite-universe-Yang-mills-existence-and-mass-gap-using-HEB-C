# Is the 5x5 vector really two numbers? Tests g(a,b) against g00 * eps2^(a/2) * eta^b with eps2 and eta read from the file's first rows.
# Prints the largest relative deviation in parts per 10^12, exact rationals, json=0.
import sys
from fractions import Fraction as Fr
g = {}
for line in open(sys.argv[1], encoding='utf-8'):
    if line.startswith('G|'):
        d = dict(x.split('=', 1) for x in line.strip().split('|')[1:] if '=' in x)
        g[(int(d['a']), int(d['b']))] = int(d['g'])
g00 = g[(0, 0)]
eta = Fr(g[(0, 1)], g00)
eps2 = Fr(g[(2, 0)], g00)
worst = Fr(0)
at = None
for (a, b), v in g.items():
    model = g00 * eps2 ** (a // 2) * eta ** b
    dev = abs(model - v) / v
    if dev > worst:
        worst = dev
        at = (a, b)
print("TWO_NUMBERS|rows=%d|g00=%d|eps2_e9=%d|eta_e9=%d|worst_dev_per_1e12=%d|at=%s|json=0" % (len(g), g00, (eps2 * 10**9).__floor__(), (eta * 10**9).__floor__(), (worst * 10**12).__floor__(), at))
