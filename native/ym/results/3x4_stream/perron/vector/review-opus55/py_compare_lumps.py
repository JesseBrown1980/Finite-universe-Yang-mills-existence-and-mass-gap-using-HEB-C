# Per-lump comparison: table minimum <= class-walk minimum (when given) <= best real configuration found. Any row out of that order is a failure.
# usage: py_compare_lumps.py EXACT_OUT HUNT_OUT [CLASSES_OUT]   Integer only, json=0.
import sys
def rows(path, tag):
    out = {}
    for line in open(path, encoding='utf-8'):
        if line.startswith(tag + '|'):
            d = dict(x.split('=', 1) for x in line.strip().split('|')[1:] if '=' in x)
            out[(int(d['a']), int(d['b']))] = (int(d['micro']), d.get('n', ''))
    return out
tab = rows(sys.argv[1], 'LUMPMIN')
real = rows(sys.argv[2], 'LUMPBEST')
cls = rows(sys.argv[3], 'CLASSMIN') if len(sys.argv) > 3 else None
bad = 0
eq_table = eq_class = 0
gaps = []
for k in sorted(tab):
    t = tab[k][0]
    r = real[k][0] if k in real else None
    c = cls[k][0] if cls and k in cls else None
    if r is not None and r < t:
        bad += 1
    if c is not None and c < t:
        bad += 1
    if c is not None and r is not None and r < c:
        bad += 1
    if r is not None and r == t:
        eq_table += 1
    if c is not None and r is not None and r == c:
        eq_class += 1
    if r is not None:
        gaps.append((r - t, k))
gaps.sort(reverse=True)
print("LUMP_COMPARE|lumps=%d|real_found=%d|real_eq_table=%d|real_eq_class=%s|class_rows=%s|out_of_order=%d|largest_real_minus_table_micro=%s|json=0" % (len(tab), sum(1 for k in tab if k in real), eq_table, eq_class if cls else '-', len(cls) if cls else '-', bad, ';'.join('%s:%d' % (k, g) for g, k in gaps[:6])))
sys.exit(1 if bad else 0)
