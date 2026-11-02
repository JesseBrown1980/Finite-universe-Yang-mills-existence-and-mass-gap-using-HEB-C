# C6: end-to-end on 2x2. Count the eigenvalues of my own whole-space H(r) below a threshold, by integer elimination with 200 bits of fixed point, no interlacing and no Barta used.
# This is the supporting count; the deciding step is the exact Barta on whole-space rows in c6_lift.py.
import heapq, pickle, sys, time
R = "C:/tmp/opus55/ym-two-sided"
with open(f"{R}/whole22.pkl", "rb") as f:
    w = pickle.load(f)
Wh, Mw, rows, flats, nl = w["W"], w["Mw"], w["rows"], w["flats"], w["nl"]
n = len(Wh)
S = 200


def count_below(jb, theta):
    """Number of negative pivots of W (H(r) - theta). Exact inertia if arithmetic were exact; fixed point here, with margins far above 2^-150."""
    u, v = 10**6, 1000 * jb
    a = []
    for i in range(n):
        r = {j: (Wh[i] * u * z) << S for j, z in rows[i].items()}
        r[i] = r.get(i, 0) + ((Wh[i] * v * Mw[i] - Wh[i] * theta) << S)
        a.append(r)
    done = [False] * n
    heap = [(len(a[i]), i) for i in range(n)]
    heapq.heapify(heap)
    neg = 0
    smallest = None
    while heap:
        dg, p = heapq.heappop(heap)
        if done[p]:
            continue
        if dg != len(a[p]):
            heapq.heappush(heap, (len(a[p]), p))
            continue
        done[p] = True
        ap = a[p]
        d = ap.pop(p)
        if d == 0:
            raise ArithmeticError("zero pivot")
        if d < 0:
            neg += 1
        ab = abs(d)
        smallest = ab if smallest is None or ab < smallest else smallest
        nb = list(ap.items())
        for ii, (i, vi) in enumerate(nb):
            ai = a[i]
            del ai[p]
            for j, vj in nb[ii:]:
                t = vi * vj // d
                ai[j] = ai.get(j, 0) - t
                if j != i:
                    a[j][i] = a[j].get(i, 0) - t
        for i, _ in nb:
            heapq.heappush(heap, (len(a[i]), i))
        a[p] = None
    return neg, smallest.bit_length() - S


t0 = time.time()
nn, sm = count_below(9000, 46467674)
print(f"TIME_ONE_COUNT|secs_wall={time.time()-t0:.1f}|whole_count_at_lambda1={nn}|log2_smallest_pivot={sm}|json=0", flush=True)
cases = [(4000, 26309589, 27000), (5000, 31009624, 12000), (6000, 35247219, 6000), (9000, 46467673, 9000)]
fails = 0
for jb0, tc, jb in cases:
    theta = tc + 3000 * (jb - jb0)
    c9, sm9 = count_below(jb, theta)
    c8, sm8 = count_below(jb, 24 * 10**6 + 1)
    ok = c9 <= 8 and c8 >= 8
    fails += 0 if ok else 1
    print(f"COUNT|JB0={jb0}|JB={jb}|theta={theta}|levels_below_theta={c9}|levels_below_flat_bound_plus_1={c8}|statement_holds={ok}|log2_smallest_pivot={min(sm9, sm8)}|secs_wall={time.time()-t0:.0f}|json=0", flush=True)
print(f"C6_COUNT|fails={fails}|json=0", flush=True)
for th in (46576171, 46578124):
    print(f"E9_BRACKET_TEST|JB=9000|theta={th}|levels_below={count_below(9000, th)[0]}|secs_wall={time.time()-t0:.0f}|json=0", flush=True)
