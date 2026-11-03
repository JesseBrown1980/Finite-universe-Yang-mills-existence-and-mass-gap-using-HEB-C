# The fit of warmcal.py again, in integers only, from the recorded rows of WARMCAL-small.hbp. The original script and its rows stay as evidence.
# The model: 1/(t_cert - t) = a/(lambda1 - t) + b, through the two nearest thresholds on each store. With e = t_cert - t and m = lambda1 - t,
#   a = (e1 - e2) m1 m2 / ((m1 - m2) e1 e2),   b = 10^6 (1/e1 - a/m1) = 10^6 (e2 (m1 - m2) - (e1 - e2) m2) / ((m1 - m2) e1 e2).
# The fit informs the choice of a threshold, and each certificate comes from its run at that threshold.
# usage: warmcal_integer.py WARMCAL-small.hbp     Exits 1 if a value differs from the four decimals the float fit printed. Integer only, json=0.
import sys


def fields(row):
    return dict(x.split("=", 1) for x in row.split("|")[1:] if "=" in x)


def round4(top, bottom):
    # The nearest integer multiple of 10^-4 to top / bottom, for bottom > 0, ties to even as a printed float would almost never meet.
    q, r = divmod(top * 10000, bottom)
    if 2 * r > bottom or (2 * r == bottom and q % 2 == 1):
        q += 1
    return q


def text4(v):
    sign = "-" if v < 0 else ""
    v = abs(v)
    return "%s%d.%04d" % (sign, v // 10000, v % 10000)


points, printed = {}, {}
for line in open(sys.argv[1], encoding="utf-8"):
    line = line.rstrip("\r\n")
    if line.startswith("WARMCAL|"):
        f = fields(line)
        points.setdefault(f["L"], []).append((int(f["t_milli"]), int(f["t_cert_milli"]), int(f["lambda1_mid_milli"])))
    elif line.startswith("WARMCAL_FIT|"):
        f = fields(line)
        printed[f["L"]] = (f["a"], f["b"])
fails = 0
for name in sorted(points):
    (t1, c1, lam), (t2, c2, _) = points[name][-2], points[name][-1]
    e1, e2, m1, m2 = c1 - t1, c2 - t2, lam - t1, lam - t2
    den = (m1 - m2) * e1 * e2
    a_top = (e1 - e2) * m1 * m2
    b_top = 10 ** 6 * (e2 * (m1 - m2) - (e1 - e2) * m2)
    if den < 0:
        den, a_top, b_top = -den, -a_top, -b_top
    a4, b4 = text4(round4(a_top, den)), text4(round4(b_top, den))
    same = (a4, b4) == printed[name]
    fails += 0 if same else 1
    print("WARMCAL_FIT_INTEGER|L=%s|a_top=%d|b_top=%d|den=%d|a_4dp=%s|b_4dp=%s|float_a=%s|float_b=%s|same_to_4dp=%d|tag=CONJECTURE|json=0" % (name, a_top, b_top, den, a4, b4, printed[name][0], printed[name][1], 1 if same else 0))
print("WARMCAL_INTEGER_DONE|stores=%d|failed=%d|json=0" % (len(points), fails))
sys.exit(1 if fails else 0)
