# Turns a RITZ row's A, B, C into rigorous micro bounds in Python integers.
#   lambda_1(H') <= A/B.   E_9 <= the top eigenvalue of [[f I_8, c], [c^T, A/B]], f = 3 nl, |c|^2 = C/B.
# For U (micro): top <= U/10^6 iff U/10^6 >= A/B and U/10^6 >= f and (U/10^6 - f)(U/10^6 - A/B) >= C/B.
# usage: py_ritz_bound.py FILE [CLAIM_MICRO]   Prints one row per RITZ row in FILE. json=0.
import sys
claim = int(sys.argv[2]) if len(sys.argv) > 2 else None
worst = 0
for line in open(sys.argv[1], encoding='utf-8'):
    if not line.startswith('RITZ|'):
        continue
    d = dict(x.split('=', 1) for x in line.strip().split('|')[1:] if '=' in x)
    A, B, C, f = int(d['A']), int(d['B']), int(d['C']), int(d['flat_diag'])
    # ceiling of 10^6 A / B
    rho = -((-A * 10**6) // B)
    Ff = f * 10**6
    def ok(U):
        return U >= rho and U >= Ff and (U - Ff) * (U * B - A * 10**6) >= C * 10**12
    lo = max(rho, Ff)
    if ok(lo):
        U = lo
    else:
        hi = lo + 1
        while not ok(hi):
            hi = lo + 2 * (hi - lo)
        l2 = lo
        while hi - l2 > 1:
            mid = (hi + l2) // 2
            if ok(mid):
                hi = mid
            else:
                l2 = mid
        U = hi
    print("RITZ_BOUND|Lx=%s|Ly=%s|r=%s|mcut=%s|states=%s|lambda1_upper_micro=%d|E9_upper_micro=%d|coupling_shift_micro=%d|json=0" % (d['Lx'], d['Ly'], d['r'], d['mcut'], d['states'], rho, U, U - rho))
    if claim is not None:
        below = U < claim
        print("RITZ_VS_CLAIM|claim_micro=%d|E9_upper_micro=%d|refutes=%d|slack_micro=%d|json=0" % (claim, U, 1 if below else 0, U - claim))
        worst = worst or (1 if below else 0)
sys.exit(worst)
