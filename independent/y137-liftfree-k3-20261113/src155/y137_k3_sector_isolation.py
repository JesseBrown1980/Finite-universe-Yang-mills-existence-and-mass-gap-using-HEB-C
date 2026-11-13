#!/usr/bin/env python3
"""Issue #137: finite 3x4 S3 at r = 9, K3 trial ball, reflection-sector isolation.

Written 2026-11-09 by the local Opus 5.5 seat, pid 8467a937cba309f7. Integer only, json=0.
It takes NO command-line arguments: the merged #136 checker parses sys.argv when it is
imported, and this script never assigns to sys.argv.

1. It imports the merged #136 checker (git blob 91bd1e80, pinned below) and reuses its
   primitives: canonical, from_key, neighbors, weight, magnetic, graph, add_gram, det,
   inertia and check.
2. threshold_ball() is the checker's threshold() generalised to a numerator a over a
   denominator b, a number of Jacobi steps, a scale and a trial ball (K2 or K3). It returns
   the UPPER form U and the LOWER witness L as 8x8 integer matrices. EQUIVALENCE: at b = 100,
   4 steps, scale 10^9 and the K2 ball, its tuple (lower inertia, upper inertia, sha256 of
   U, G, L) must equal the checker's own threshold() on the checker's four frozen LEVELS.
3. K3 = 8 flats + 264 + 7770 + 147344 orbits, built as the original fe_k3 chain built it:
   the 147344 one-step exterior targets of K2 become trial states, and the residual moves to
   shell 4, whose orbits are all generated here with exact weights (1985218 of them).
4. The lattice reflection x -> -x is verified exactly on K3 and on every shell-4 target:
   a permutation of the states that keeps weights, potential, diagonal, Q-Q couplings, Q-P
   couplings and Q-to-exterior couplings. It fixes flats 0..5 and swaps flats 6 and 7. Each
   8x8 matrix is split by integer congruence into the reflection-even block (columns: the
   six fixed flats and flat6+flat7) and the odd 1x1 block (flat6-flat7); the blocks must
   decouple exactly, and the inertia is counted per sector.
5. It evaluates the thresholds below and writes Y137-K3-SECTOR-ISOLATION.hbp and its
   .sha256 beside this file.

Why integer floor division in the Jacobi steps is harmless. Accuracy is never assumed.
  Let X be ANY integer matrix with one row of 8 entries per Q state of the ball, zero
  outside the ball, and let psi(v) be the trial vector whose flat part is SCALE*v and whose
  Q part is -X v. With exact integers only, the code computes
      U(v) = < psi(v), (b H - a) psi(v) >_W                 (b H - a applied exactly)
      G(v) = 6 || Q (b H - a) psi(v) ||_W^2                   (every Q row of the ball and
                                                             every exterior target summed)
  and nothing is left out of G, because X vanishes outside the ball and the exterior list
  holds every orbit one electric move outside it. For every v the 8-flat Schur complement
  S(z) obeys
      < SCALE v, S(z) SCALE v > <= < psi, (H - z) psi >                     (any X)
      < SCALE v, S(z) SCALE v > >= < psi, (H - z) psi > - ||Q(H - z) psi||^2 / gamma
  with gamma = floor - z > 0 and floor <= lambda_min(QHQ) (the second line is the exact
  Feshbach identity <r,(QHQ - z)^-1 r> <= ||r||^2 / gamma, for any X). Hence
  n_-(U) <= N(z) <= n_-(L) whatever X is, and the same holds for v restricted to a
  reflection sector. Floor division only decides WHICH X is used, that is, how close X is
  to SCALE times the true Q resolvent; it changes how tight the counts are, never whether
  they are valid. With SCALE = 10^12 and b = 10^7 one unit of rounding per entry is
  10^-12 of the flat coefficient, while the residual that G measures exactly is dominated by
  the shell-4 truncation (its share is about 0.99999998 in the original K3 cross-check).
  The lower side needs z < floor (checked as gamma_num > 0); the upper side needs nothing.

Packing. Several Python integer sums below pack the 8 nonnegative components of a row into
one integer with field width W and add packed rows. That is exact when every component is
nonnegative and every field sum stays below 2^W; each width is computed from the measured
maximum entry and the measured maximum row sum before it is used, and the EQUIVALENCE test
runs the same code on K2 against the checker.
"""
import hashlib
import os
import sys
import time
from array import array

if len(sys.argv) != 1:
    raise SystemExit("usage: python3 -I -B y137_k3_sector_isolation.py   (no arguments)")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import finite_s3_3x4_r9_first_gap as c  # noqa: E402  (reads sys.argv at import; none given)

CHECKER_FILE = "finite_s3_3x4_r9_first_gap.py"
CHECKER_BLOB = "91bd1e80cbfcfb76198966aa177d097ecfbe8143"
SCRIPT_FILE = "y137_k3_sector_isolation.py"
OUT_NAME = "Y137-K3-SECTOR-ISOLATION.hbp"
FLOOR_NUM = 94070673            # #131 floor numerator over c.PERRON_SCALE = 10^6
PS = c.PERRON_SCALE
SHELL1 = 264
K3_STEPS = 12
K3_SCALE = 10 ** 12
K3_B = 10 ** 7
K3_POINTS = (699567503, 699686993, 699689591)
# K3L_EVAL rows of the original fe_k3lower.py chain (steps 12, SCALE 10^12, z_den 10^7):
# (even_lower_count, even_upper_count, odd_lower_count, odd_upper_count)
ORIG_K3 = {699567503: (2, 2, 0, 0), 699686993: (2, 2, 0, 0), 699689591: (3, 2, 0, 0)}
ORIG_K3_SOURCE = {699567503: "k3-lower.rows+k3-cross.rows", 699686993: "k3-lower.rows",
                  699689591: "k3-lower.rows"}
# K3_BEGIN of the original (k3-amp-roots.rows): q_states, q_nnz, shell4_targets, shell4_edges
ORIG_K3_SIZES = (155378, 1356528, 1985218, 9690600)
# K2 cross-row: sector_split.py (the checker's threshold source run with b = 1000), steps 4,
# scale 10^9, run-fine-steps4.out, z = 69956/1000
K2_CROSS = (69956, 1000, 4)
ORIG_K2_CROSS = dict(total_lower=5, total_upper=1, even_lower=4, even_upper=1, odd_lower=1,
                     odd_upper=0,
                     L="80b0dd3f0d12cf97cec4ee26d57419e9997a7c4b31092ba89c0be9264b881ed9",
                     U="83fdb7a12a0eae1438bd0b4e58497f6a75e80248c173463e9c42d2cd3c8d9e31",
                     G="3b22c095597cbb58ba474011618cd9e6ee4b8d5d10cfe11706321a647922530b")
SHELL4_STRIDE = 199
ODD_PAIR = (6, 7)
ZERO8 = (0, 0, 0, 0, 0, 0, 0, 0)

ROWS = []
T0 = time.monotonic_ns()


def emit(label, **fields):
    row = label + "|" + "|".join(str(k) + "=" + str(v) for k, v in fields.items()) + "|json=0"
    ROWS.append(row)
    print(row, flush=True)


def note(label, **fields):
    # stdout only (times, file presence): never written into the .hbp
    sec = (time.monotonic_ns() - T0) // 1000000000
    print(label + "|" + "|".join(str(k) + "=" + str(v) for k, v in fields.items())
          + "|sec=" + str(sec) + "|json=0", flush=True)


def sha_matrix(M):
    return hashlib.sha256("|".join(str(z) for row in M for z in row).encode()).hexdigest()


def frac(a, b):
    return str(a) + "/" + str(b)


def code(key):
    v = 0
    for x in reversed(key):
        v = v * 6 + x
    return v


def decode(v):
    out = []
    for _ in range(13):
        v, r = divmod(v, 6)
        out.append(r)
    return tuple(out)


# ----------------------------------------------------------------------------- packing
def pack(Y, W):
    s1, s2, s3, s4, s5, s6, s7 = W, 2 * W, 3 * W, 4 * W, 5 * W, 6 * W, 7 * W
    return [y[0] | (y[1] << s1) | (y[2] << s2) | (y[3] << s3) | (y[4] << s4)
            | (y[5] << s5) | (y[6] << s6) | (y[7] << s7) for y in Y]


def entry_range(Y):
    lo = min(min(y) for y in Y)
    hi = max(max(y) for y in Y)
    return lo, hi


def pack_for_sums(Y, maxrow):
    # fields hold sums of at most maxrow (total weight) copies of an entry <= hi
    lo, hi = entry_range(Y)
    c.check(lo >= 0, "packed_entries_nonnegative")
    W = max((maxrow * hi).bit_length(), hi.bit_length()) + 1
    return pack(Y, W), W


# ----------------------------------------------------------------------------- balls
def csr_rows(rows):
    rs = array("q", [0])
    oj = array("i")
    oc = array("h")
    for row in rows:
        for j, cc in row:
            oj.append(j)
            oc.append(cc)
        rs.append(len(oj))
    return rs, oj, oc


def finish_ball(ball):
    rs, oc, es, ewc = ball["rs"], ball["oc"], ball["es"], ball["ewc"]
    ball["maxrow"] = max(max(sum(oc[rs[i]:rs[i + 1]]) for i in range(ball["n"])), 1)
    ball["maxwc"] = max(max(sum(ewc[es[f]:es[f + 1]]) for f in range(ball["nf"])), 1)
    c.check(all(W in (1, 2, 3, 6) for W in ball["eW"]), "exterior_weight_divides_six")
    c.check(min(ball["oc"]) > 0 and min(ball["ewc"]) > 0, "positive_couplings")
    return ball


def ball_from_checker(w, m, adj, q_flat, outer):
    """The checker's own K2 data (graph()) in the generic ball layout."""
    n = len(adj)
    rows = []
    dbase = []
    for i, row in enumerate(adj):
        selfc = dict(row).get(i, 0)
        rows.append([(j, cc) for j, cc in row if j != i])
        dbase.append(72 + 9 * m[8 + i] - selfc)
    rs, oj, oc = csr_rows(rows)
    es = array("q", [0])
    esrc = array("i")
    ewc = array("i")
    eW = array("b")
    for W, edges in outer:
        for i, wc in edges:
            esrc.append(i)
            ewc.append(wc)
        es.append(len(esrc))
        eW.append(W)
    C = [None if not any(r) else list(r) for r in q_flat]
    return finish_ball(dict(name="K2", wf=list(w[:8]), n=n, wq=list(w[8:]), dbase=dbase,
                            rs=rs, oj=oj, oc=oc, C=C, nf=len(outer), es=es, esrc=esrc,
                            ewc=ewc, eW=eW))


# ----------------------------------------------------------------------------- threshold
def threshold_ball(a, b, steps, scale, ball, floor_num, round_like_original=False,
                   keep_y=False):
    """The checker's threshold() with b, steps, scale and the ball as parameters.

    The checker iterates X <- (SCALE*F + b*sum_j c_ij X_j) // diag with F = -b*C and X <= 0.
    Here Y = -X >= 0 is stored, so that rows can be packed:
        X_new = (-b*(SCALE*C_i + T_i)) // diag_i ,  T_i = sum_j c_ij Y_j ,  Y_new = -X_new.
    round_like_original=True instead takes Y_new = (b*(SCALE*C_i + T_i)) // diag_i, the floor
    on Y >= 0 that the original fe_k3 / fe_k3lower chain used (the checker floors X <= 0,
    i.e. rounds Y up). Every other line is the same for both roundings.
    """
    n, wf, wq, dbase = ball["n"], ball["wf"], ball["wq"], ball["dbase"]
    rs, oj, oc, C = ball["rs"], ball["oj"], ball["oc"], ball["C"]
    nf, es, esrc, ewc, eW = ball["nf"], ball["es"], ball["esrc"], ball["ewc"], ball["eW"]
    maxrow = ball["maxrow"]
    diag = [b * x - a for x in dbase]
    c.check(min(diag) > 0, "positive_Q_Jacobi_diagonal")
    SC = [None if ci is None else [scale * v for v in ci] for ci in C]
    nb = -b
    Y = [ZERO8] * n
    for _ in range(steps):
        P, W = pack_for_sums(Y, maxrow)
        mask = (1 << W) - 1
        shifts = [W * k for k in range(8)]
        NY = []
        for i in range(n):
            T = 0
            for idx in range(rs[i], rs[i + 1]):
                T += oc[idx] * P[oj[idx]]
            t = [(T >> s) & mask for s in shifts]
            sc = SC[i]
            if sc is not None:
                t = [t[k] + sc[k] for k in range(8)]
            d = diag[i]
            if round_like_original:
                NY.append([(b * v) // d for v in t])
            else:
                NY.append([-((nb * v) // d) for v in t])
        Y = NY
    # exact residual on the Q rows of the ball, the trial form U, the Q-row Gram
    P, W = pack_for_sums(Y, maxrow)
    mask = (1 << W) - 1
    shifts = [W * k for k in range(8)]
    U = [[0] * 8 for _ in range(8)]
    for k in range(8):
        U[k][k] = scale * scale * wf[k] * (b * 72 - a)
    G = [[0] * 8 for _ in range(8)]
    for i in range(n):
        T = 0
        for idx in range(rs[i], rs[i + 1]):
            T += oc[idx] * P[oj[idx]]
        t = [(T >> s) & mask for s in shifts]
        y = Y[i]
        d = diag[i]
        wi = wq[i]
        sc = SC[i]
        # checker: s = SCALE*F - diag*X + b*sum_j c_ij X_j, with X = -Y and F = -b*C
        if sc is None:
            s = [d * y[k] - b * t[k] for k in range(8)]
        else:
            s = [nb * sc[k] + d * y[k] - b * t[k] for k in range(8)]
        R = [wi * v for v in s]
        c.add_gram(G, R, wi)
        # checker: U[k][j] -= SCALE*wi*F[k]*X[j] + X[k]*R[j]; with X = -Y that is
        #          U[k][j] += Y[k]*R[j] - wi*b*SCALE*C[k]*Y[j]
        for k in range(8):
            yk = y[k]
            if yk:
                Uk = U[k]
                for j in range(8):
                    Uk[j] += yk * R[j]
        if sc is not None:
            for k in range(8):
                if sc[k]:
                    t2 = wi * b * sc[k]
                    Uk = U[k]
                    for j in range(8):
                        Uk[j] -= t2 * y[j]
    # complete exterior: checker R = sum_e b*wc*X_e = -b*S, add_gram adds (6/W) R R^T,
    # here S is packed and the 8 rows of sum_f (6/W_f) S_p S S^T are packed as well
    lo, hi = entry_range(Y)
    c.check(lo >= 0, "packed_entries_nonnegative")
    maxS = ball["maxwc"] * hi
    WG = max((6 * nf * maxS * maxS).bit_length(), hi.bit_length()) + 1
    maskG = (1 << WG) - 1
    shG = [WG * k for k in range(8)]
    P = pack(Y, WG)
    acc = [0] * 8
    for f in range(nf):
        S = 0
        for idx in range(es[f], es[f + 1]):
            S += ewc[idx] * P[esrc[idx]]
        if S:
            fac = 6 // eW[f]
            for p in range(8):
                sp = (S >> shG[p]) & maskG
                if sp:
                    acc[p] += fac * sp * S
    del P
    bb = b * b
    for p in range(8):
        for q in range(p, 8):
            G[p][q] += bb * ((acc[p] >> shG[q]) & maskG)
    for i in range(8):
        for j in range(i):
            G[i][j] = G[j][i]
    c.check(all(U[i][j] == U[j][i] for i in range(8) for j in range(8)),
            "exact_symmetric_trial")
    gamma_num = b * floor_num - a * PS
    c.check(gamma_num > 0, "nonflat_Perron_resolvent_floor")
    L = [[6 * gamma_num * U[i][j] - PS * G[i][j] for j in range(8)] for i in range(8)]
    nlo = c.inertia(L)
    nhi = c.inertia(U)
    return dict(L=L, U=U, G=G, nlo=nlo, nhi=nhi, hu=sha_matrix(U), hg=sha_matrix(G),
                hl=sha_matrix(L), Y=Y if keep_y else None, max_entry=hi, width=WG)


# ----------------------------------------------------------------------------- sectors
def sector_bases(pair, odd_sign):
    i, j = pair
    E = [[0] * 7 for _ in range(8)]
    col = 0
    for k in range(8):
        if k in pair:
            continue
        E[k][col] = 1
        col += 1
    E[i][6] = 1
    E[j][6] = 1
    o = [0] * 8
    o[i] = 1
    o[j] = odd_sign
    return E, o


def congr(M, E):
    cols = len(E[0])
    return [[sum(E[x][p] * M[x][y] * E[y][q] for x in range(8) for y in range(8))
             for q in range(cols)] for p in range(cols)]


def cross_terms(M, E, o):
    return [sum(E[x][p] * M[x][y] * o[y] for x in range(8) for y in range(8))
            for p in range(len(E[0]))]


def quad(M, o):
    return sum(o[x] * M[x][y] * o[y] for x in range(8) for y in range(8))


def inertia_n(A):
    k = len(A)
    c.check(all(A[i][j] == A[j][i] for i in range(k) for j in range(k)), "sector_symmetry")
    neg = 0
    prev = 1
    for t in range(1, k + 1):
        D = c.det([row[:t] for row in A[:t]])
        c.check(D != 0, "sector_nonzero_Sylvester_pivots")
        neg += int((D < 0) != (prev < 0))
        prev = D
    return neg


def sign(v):
    return (v > 0) - (v < 0)


def sectors(r):
    E, o = sector_bases(ODD_PAIR, -1)
    L, U = r["L"], r["U"]
    for M, nm in ((L, "LOWER"), (U, "UPPER")):
        c.check(all(v == 0 for v in cross_terms(M, E, o)), nm + "_even_odd_blocks_decouple")
    Le, Ue = congr(L, E), congr(U, E)
    Lo, Uo = quad(L, o), quad(U, o)
    c.check(Lo != 0 and Uo != 0, "odd_forms_nonzero")
    out = dict(even_lower=inertia_n(Le), even_upper=inertia_n(Ue), odd_lower=int(Lo < 0),
               odd_upper=int(Uo < 0), odd_L_sign=sign(Lo), odd_U_sign=sign(Uo))
    # Sylvester's law of inertia: the congruence [E | o] (determinant -2) is invertible
    c.check(out["even_lower"] + out["odd_lower"] == r["nlo"]
            and out["even_upper"] + out["odd_upper"] == r["nhi"], "sector_counts_sum_to_total")
    # sandwich order n_-(U) <= N(z) <= n_-(L) in each sector
    c.check(out["even_upper"] <= out["even_lower"] and out["odd_upper"] <= out["odd_lower"],
            "sandwich_order_per_sector")
    return out


# ----------------------------------------------------------------------------- reflection
def reflect_x(U, keep_inverse=True):
    """x -> -x: the horizontal link (x,y)->(x+1,y) becomes the reversed link that starts at
    (-x-1,y); the vertical link at (x,y) moves to (-x,y) unchanged."""
    V = c.V
    Z = [0] * (2 * V)
    for x in range(c.LX):
        for y in range(c.LY):
            h = U[c.pos(x, y)]
            Z[c.pos(-x - 1, y)] = c.INV[h] if keep_inverse else h
            Z[V + c.pos(-x, y)] = U[V + c.pos(x, y)]
    return Z


def reflected_key(key, keep_inverse=True):
    return c.canonical(reflect_x(c.from_key(key), keep_inverse))


def row_dicts(ball):
    rs, oj, oc = ball["rs"], ball["oj"], ball["oc"]
    out = []
    for i in range(ball["n"]):
        d = dict(zip(oj[rs[i]:rs[i + 1]], oc[rs[i]:rs[i + 1]]))
        c.check(len(d) == rs[i + 1] - rs[i], "row_targets_distinct")
        out.append(d)
    return out


def reflection_check(keys, lookup, wfull, mfull, ball, rowdict, keep_inverse=True):
    N = len(keys)
    pi = []
    for key in keys:
        j = lookup.get(reflected_key(key, keep_inverse))
        if j is None:
            return 0, "reflection_leaves_the_ball", None
        pi.append(j)
    seen = bytearray(N)
    for j in pi:
        seen[j] = 1
    if sum(seen) != N:
        return 0, "not_a_permutation", None
    if any(pi[k] >= 8 for k in range(8)):
        return 0, "flats_not_mapped_to_flats", None
    for s in range(N):
        if wfull[pi[s]] != wfull[s]:
            return 0, "weight_not_preserved", None
        if mfull[pi[s]] != mfull[s]:
            return 0, "potential_not_preserved", None
    n, dbase, C = ball["n"], ball["dbase"], ball["C"]
    sigma = pi[:8]
    for i in range(n):
        pq = pi[8 + i] - 8
        if dbase[pq] != dbase[i]:
            return 0, "diagonal_not_preserved", None
        rd = rowdict[i]
        td = rowdict[pq]
        if len(rd) != len(td):
            return 0, "QQ_row_length_not_preserved", None
        for j, cc in rd.items():
            if td.get(pi[8 + j] - 8) != cc:
                return 0, "QQ_coupling_not_preserved", None
        ci = C[i]
        cp = C[pq]
        for k in range(8):
            a1 = 0 if ci is None else ci[k]
            a2 = 0 if cp is None else cp[sigma[k]]
            if a1 != a2:
                return 0, "QP_coupling_not_preserved", None
    return 1, "exact", pi


def exterior_check(ball, pi, key_of, index_of):
    nf, es, esrc, ewc, eW = ball["nf"], ball["es"], ball["esrc"], ball["ewc"], ball["eW"]
    pi4 = array("i", [0]) * nf
    seen = bytearray(nf)
    for f in range(nf):
        g = index_of(reflected_key(key_of(f)))
        if g is None:
            return 0, "reflection_leaves_the_exterior"
        pi4[f] = g
        seen[g] = 1
    if sum(seen) != nf:
        return 0, "exterior_not_a_permutation"
    for f in range(nf):
        g = pi4[f]
        if eW[g] != eW[f]:
            return 0, "exterior_weight_not_preserved"
        mine = sorted((pi[8 + esrc[p]] - 8, ewc[p]) for p in range(es[f], es[f + 1]))
        theirs = sorted((esrc[p], ewc[p]) for p in range(es[g], es[g + 1]))
        if mine != theirs:
            return 0, "exterior_coupling_not_preserved"
    return 1, "exact"


def detailed_balance(ball, rowdict):
    wq = ball["wq"]
    for i in range(ball["n"]):
        for j, cc in rowdict[i].items():
            if wq[i] * cc != wq[j] * rowdict[j].get(i, 0):
                return 0
    return 1


# ----------------------------------------------------------------------------- K2 and K3
def rebuild_states():
    """graph()'s state order, rebuilt as the checker builds it."""
    flat = {}
    for a in range(6):
        for b in range(6):
            if c.MUL[a][b] != c.MUL[b][a]:
                continue
            U = [0] * (2 * c.V)
            for y in range(c.LY):
                U[c.pos(c.LX - 1, y)] = a
            for x in range(c.LX):
                U[c.V + c.pos(x, c.LY - 1)] = b
            flat[c.canonical(U)] = (a, b)
    layers = [sorted(flat)]
    seen = set(layers[0])
    for _ in range(2):
        new = set()
        for key in layers[-1]:
            new.update(c.neighbors(key))
        new.difference_update(seen)
        seen.update(new)
        layers.append(sorted(new))
    return [k for layer in layers for k in layer], flat, [len(x) for x in layers]


def build_k3(states, where, w, m, adj, outer, C2):
    """K3 as fe_k3.build_k3 / setup() built it: Q3 = the 8034 Q states of K2, then the
    147344 exterior targets in graph()'s order; the exterior of K3 is shell 4."""
    n2 = len(states) - 8
    ext_keys = []
    ext_index = {}
    ext_edges = []
    rs = array("q", [0])
    oj = array("i")
    oc = array("h")
    dbase = []
    for i in range(n2):
        row = adj[i]
        selfc = dict(row).get(i, 0)
        for j, cc in row:
            if j != i:
                oj.append(j)
                oc.append(cc)
        for dst, cc in c.neighbors(states[8 + i]).items():
            if dst in where:
                continue
            t = ext_index.get(dst)
            if t is None:
                t = len(ext_keys)
                ext_index[dst] = t
                ext_keys.append(dst)
                ext_edges.append([])
            ext_edges[t].append((i, w[8 + i] * cc))
            oj.append(n2 + t)
            oc.append(cc)
        rs.append(len(oj))
        dbase.append(72 + 9 * m[8 + i] - selfc)
    nE = len(ext_keys)
    wE = [c.weight(k) for k in ext_keys]
    c.check([(wE[t], ext_edges[t]) for t in range(nE)] == outer, "exterior_order_rebuild")
    del ext_edges
    s4 = {}
    code4 = array("q")
    w4 = array("b")
    e4f = array("i")
    e4s = array("i")
    e4c = array("h")
    mE = []
    for t in range(nE):
        key = ext_keys[t]
        mE.append(c.magnetic(c.from_key(key)))
        wt = wE[t]
        selfc = 0
        for dst, cc in c.neighbors(key).items():
            j = where.get(dst)
            if j is not None:
                c.check(j >= 8 + SHELL1, "exterior_touches_shell1_or_flat")
                oj.append(j - 8)
                oc.append(cc)
                continue
            u = ext_index.get(dst)
            if u is not None:
                if u == t:
                    selfc += cc
                else:
                    oj.append(n2 + u)
                    oc.append(cc)
                continue
            cd = code(dst)
            f = s4.get(cd)
            if f is None:
                f = len(code4)
                s4[cd] = f
                code4.append(cd)
                w4.append(c.weight(dst))
            e4f.append(f)
            e4s.append(n2 + t)
            e4c.append(wt * cc)
        rs.append(len(oj))
        dbase.append(72 + 9 * mE[t] - selfc)
        if t % 20000 == 0:
            note("K3_BUILD_PROGRESS", t=t, shell4=len(code4))
    nf = len(code4)
    ne4 = len(e4f)
    cnt = array("q", [0]) * (nf + 1)
    for f in e4f:
        cnt[f + 1] += 1
    for f in range(nf):
        cnt[f + 1] += cnt[f]
    posn = array("q", cnt[:nf])
    esrc = array("i", [0]) * ne4
    ewc = array("h", [0]) * ne4
    for idx in range(ne4):
        f = e4f[idx]
        p = posn[f]
        esrc[p] = e4s[idx]
        ewc[p] = e4c[idx]
        posn[f] = p + 1
    del posn
    ball = finish_ball(dict(name="K3", wf=list(w[:8]), n=n2 + nE, wq=list(w[8:]) + wE,
                            dbase=dbase, rs=rs, oj=oj, oc=oc, C=list(C2) + [None] * nE,
                            nf=nf, es=cnt, esrc=esrc, ewc=ewc, eW=w4))
    extra = dict(ext_keys=ext_keys, ext_index=ext_index, wE=wE, mE=mE, s4=s4, code4=code4,
                 e4f=e4f, e4s=e4s, e4c=e4c)
    return ball, extra


def direct_forms(a, b, scale, ball, Y, v, flat_out, e4f, e4s, e4c, drop_edge=False):
    """v^T U v and v^T G v by a second route: the trial vector itself, the flats' own move
    counts (not detailed balance) and a per-source walk over the shell-4 edges."""
    n, wq, dbase, C = ball["n"], ball["wq"], ball["dbase"], ball["C"]
    rs, oj, oc, wf, w4 = ball["rs"], ball["oj"], ball["oc"], ball["wf"], ball["eW"]
    Pf = [scale * x for x in v]
    Pq = [sum(Y[i][k] * v[k] for k in range(8)) for i in range(n)]
    rf = [(b * 72 - a) * Pf[k] - b * sum(cc * Pq[j] for j, cc in flat_out[k])
          for k in range(8)]
    quad_f = sum(wf[k] * Pf[k] * rf[k] for k in range(8))
    quad_q = 0
    gq = 0
    for i in range(n):
        t = 0
        for idx in range(rs[i], rs[i + 1]):
            t += oc[idx] * Pq[oj[idx]]
        ci = C[i]
        if ci is not None:
            t += sum(ci[k] * Pf[k] for k in range(8))
        r = (b * dbase[i] - a) * Pq[i] - b * t
        quad_q += wq[i] * Pq[i] * r
        gq += wq[i] * r * r
    acc = [0] * ball["nf"]
    start = 1 if drop_edge else 0
    for idx in range(start, len(e4f)):
        acc[e4f[idx]] += e4c[idx] * Pq[e4s[idx]]
    g4 = 0
    for f in range(ball["nf"]):
        s = acc[f]
        if s:
            g4 += (6 // w4[f]) * (b * s) * (b * s)
    return quad_f + quad_q, 6 * gq + g4


def form_value(M, v):
    return sum(v[p] * M[p][q] * v[q] for p in range(8) for q in range(8))


# ----------------------------------------------------------------------------- main
def main():
    raw = open(os.path.join(HERE, CHECKER_FILE), "rb").read()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + bytes((0,)) + raw).hexdigest()
    c.check(blob == CHECKER_BLOB, "checker_git_blob_pin")
    c.check(os.path.abspath(c.__file__) == os.path.join(HERE, CHECKER_FILE),
            "imported_checker_is_the_pinned_file")
    own = hashlib.sha256(open(os.path.join(HERE, SCRIPT_FILE), "rb").read()).hexdigest()
    emit("Y137_K3_HEAD", date="2026-11-09",
         seat="the local Opus 5.5 seat, pid 8467a937cba309f7",
         repo="Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C",
         written_against="origin/main 6a7fc74", issue=137, script="independent/" + SCRIPT_FILE,
         script_sha256=own, checker="independent/" + CHECKER_FILE, checker_git_blob=blob,
         source_condition="#131 floor lambda_min(QHQ_whole) >= 94.070673 J_E, "
         "whose sector rows #152 rebuilt independently",
         floor=frac(FLOOR_NUM, PS), lower_side="CONDITIONAL_on_the_floor",
         upper_side="UNCONDITIONAL_min_max", arithmetic="integer_only", arguments=0)
    perron = os.path.join(os.path.dirname(HERE), "native", "ym", "results", "3x4_stream",
                          "perron", "PERRON-RESULT.hbp")
    if os.path.exists(perron):
        src, fl = c.source_floor()
        c.check(fl == FLOOR_NUM, "pinned_floor_equals_the_stated_condition")
        note("SOURCE_FLOOR_FILE", present=1, source=src, floor_num=fl)
    else:
        note("SOURCE_FLOOR_FILE", present=0, floor_num_used=FLOOR_NUM)

    # ---------------------------------------------------------------- K2, the checker's own
    w, m, adj, q_flat, outer = c.graph()
    states, flat, layer_sizes = rebuild_states()
    c.check(len(states) == len(w) == 8042 and layer_sizes == [8, SHELL1, 7770],
            "K2_layers")
    c.check([c.weight(k) for k in states] == w
            and [c.magnetic(c.from_key(k)) for k in states] == m, "K2_state_order_rebuild")
    where = {k: i for i, k in enumerate(states)}
    ball2 = ball_from_checker(w, m, adj, q_flat, outer)
    emit("Y137_K3_CENSUS", ball="K2", flats=8, shell1=layer_sizes[1], shell2=layer_sizes[2],
         q_states=ball2["n"], q_nnz=len(ball2["oj"]), exterior_targets=ball2["nf"],
         exterior_edges=len(ball2["esrc"]), checker_exterior=len(outer),
         agree_checker=int(ball2["nf"] == 147344 == len(outer)), tag="MEASURED")
    note("K2_READY")

    # ---------------------------------------------------------------- EQUIVALENCE
    checker_out = {}
    for a, lo, hi in c.LEVELS:
        ref = c.threshold(a, w, m, adj, q_flat, outer, FLOOR_NUM)
        mine = threshold_ball(a, 100, c.STEPS, c.SCALE, ball2, FLOOR_NUM)
        got = (mine["nlo"], mine["nhi"], mine["hu"], mine["hg"], mine["hl"])
        checker_out[a] = tuple(ref)
        ok = int(got == tuple(ref) and got[:2] == (lo, hi))
        emit("Y137_K3_EQUIVALENCE", z=frac(a, 100), steps=c.STEPS, scale="10^9", ball="K2",
             checker_lower=ref[0], checker_upper=ref[1], port_lower=got[0], port_upper=got[1],
             frozen=str(lo) + "," + str(hi), U_sha256=got[2], G_sha256=got[3],
             L_sha256=got[4], byte_identical=ok, tag="MEASURED")
        c.check(ok == 1, "equivalence_with_checker_threshold")
    emit("Y137_K3_EQUIVALENCE_ALL", levels=len(c.LEVELS), identical=len(c.LEVELS),
         compared="lower_inertia,upper_inertia,sha256_U,sha256_G,sha256_L", tag="MEASURED")
    note("EQUIVALENCE_DONE")

    # ---------------------------------------------------------------- K2 symmetry
    rd2 = row_dicts(ball2)
    ok2, why2, pi2 = reflection_check(states, where, w, m, ball2, rd2)
    c.check(ok2 == 1, "K2_reflection_" + why2)
    sigma = pi2[:8]
    moved = [k for k in range(8) if sigma[k] != k]
    c.check(moved == list(ODD_PAIR) and sigma[6] == 7 and sigma[7] == 6, "flat_permutation")
    # K2's exterior is shell 3, whose states and K2 couplings are rows of K3: the K3 check
    # below covers them.
    emit("Y137_K3_SYMMETRY", ball="K2", map="x_to_minus_x", states=len(states),
         permutation=1, weight=1, potential=1, diagonal=1, QQ=1, QP=1,
         exterior="shell 3, inside the K3 check",
         flat_perm=",".join(str(x) for x in sigma), odd_flat="flat6-flat7",
         flat6_ab=",".join(str(x) for x in flat[states[6]]),
         flat7_ab=",".join(str(x) for x in flat[states[7]]), exact=1, tag="MEASURED")

    # ---------------------------------------------------------------- K2 cross-row
    a, b, steps = K2_CROSS
    r = threshold_ball(a, b, steps, c.SCALE, ball2, FLOOR_NUM)
    s = sectors(r)
    emit("Y137_K3_SECTOR", ball="K2", z=frac(a, b), steps=steps, scale="10^9",
         rounding="checker", total_lower=r["nlo"], total_upper=r["nhi"],
         even_lower_count=s["even_lower"], even_upper_count=s["even_upper"],
         odd_lower_count=s["odd_lower"], odd_upper_count=s["odd_upper"],
         odd_L_sign=s["odd_L_sign"], odd_U_sign=s["odd_U_sign"], decoupled=1,
         L_sha256=r["hl"], U_sha256=r["hu"], G_sha256=r["hg"], tag="MEASURED")
    o = ORIG_K2_CROSS
    agree = int((r["nlo"], r["nhi"], s["even_lower"], s["even_upper"], s["odd_lower"],
                 s["odd_upper"], r["hl"], r["hu"], r["hg"])
                == (o["total_lower"], o["total_upper"], o["even_lower"], o["even_upper"],
                    o["odd_lower"], o["odd_upper"], o["L"], o["U"], o["G"]))
    emit("Y137_K3_COMPARE", ball="K2", z=frac(a, b),
         original="sector_split.py run-fine-steps4.out SECTOR and S3_3X4_THRESHOLD rows",
         order="total_lower,total_upper,even_lower,even_upper,odd_lower,odd_upper",
         original_counts=",".join(str(o[k]) for k in ("total_lower", "total_upper",
                                                     "even_lower", "even_upper",
                                                     "odd_lower", "odd_upper")),
         port_counts=",".join(str(x) for x in (r["nlo"], r["nhi"], s["even_lower"],
                                               s["even_upper"], s["odd_lower"],
                                               s["odd_upper"])),
         witness_sha256_identical=int((r["hl"], r["hu"], r["hg"]) == (o["L"], o["U"], o["G"])),
         agree=agree, tag="MEASURED")
    del r
    note("K2_CROSS_DONE")

    # ---------------------------------------------------------------- K3 build
    C2 = ball2["C"]
    ball3, ex = build_k3(states, where, w, m, adj, outer, C2)
    n2 = ball2["n"]
    nE = len(ex["ext_keys"])
    sizes = (ball3["n"], len(ball3["oj"]), ball3["nf"], len(ex["e4f"]))
    emit("Y137_K3_CENSUS", ball="K3", q_states=sizes[0], q_nnz=sizes[1],
         shell3_trial_states=nE, shell4_targets=sizes[2], shell4_edges=sizes[3],
         original=",".join(str(x) for x in ORIG_K3_SIZES),
         agree_original=int(sizes == ORIG_K3_SIZES), tag="MEASURED")
    c.check(sizes == ORIG_K3_SIZES and nE == len(outer), "K3_sizes_equal_original_log")
    note("K3_BUILT")

    # ---------------------------------------------------------------- K3 symmetry
    keys3 = states + ex["ext_keys"]
    where3 = dict(where)
    for t, k in enumerate(ex["ext_keys"]):
        where3[k] = 8 + n2 + t
    w3 = list(w) + ex["wE"]
    m3 = list(m) + ex["mE"]
    rd3 = row_dicts(ball3)
    db3 = detailed_balance(ball3, rd3)
    c.check(db3 == 1, "K3_weighted_QQ_adjoint")
    flat_out = []
    for k in range(8):
        row = []
        for dst, cc in c.neighbors(states[k]).items():
            j = where[dst]
            c.check(j >= 8, "flat_to_flat_forbidden")
            row.append((j - 8, cc))
        flat_out.append(row)
    for i in range(n2):
        ci = C2[i]
        for k in range(8):
            fwd = 0 if ci is None else ci[k]
            back = dict(flat_out[k]).get(i, 0)
            c.check(w[8 + i] * fwd == w[k] * back, "weighted_P_Q_adjoint")
    ok3, why3, pi3 = reflection_check(keys3, where3, w3, m3, ball3, rd3)
    c.check(ok3 == 1, "K3_reflection_" + why3)
    c.check(pi3[:8] == sigma, "K3_flat_permutation")
    del rd3
    s4 = ex["s4"]
    code4 = ex["code4"]
    ok4, why4 = exterior_check(ball3, pi3, lambda f: decode(code4[f]),
                               lambda k: s4.get(code(k)))
    c.check(ok4 == 1, "shell4_reflection_" + why4)
    emit("Y137_K3_SYMMETRY", ball="K3", map="x_to_minus_x", states=len(keys3),
         shell4_targets=ball3["nf"], shell4_edges=sizes[3], permutation=1, weight=1,
         potential=1, diagonal=1, QQ=1, QP=1, Q_to_exterior=1, exterior_permutation=1,
         exterior_weight=1, flat_perm=",".join(str(x) for x in pi3[:8]), exact=1,
         tag="MEASURED")
    # shell-4 detailed balance on a deterministic stride sample
    es, esrc, ewc, w4 = ball3["es"], ball3["esrc"], ball3["ewc"], ball3["eW"]
    sampled = 0
    for f in range(0, ball3["nf"], SHELL4_STRIDE):
        rec = {esrc[p]: ewc[p] for p in range(es[f], es[f + 1])}
        got = {}
        for dst, cc in c.neighbors(decode(code4[f])).items():
            j = where3.get(dst)
            if j is None:
                continue
            c.check(j >= 8 + n2, "shell4_touches_K2")
            got[j - 8] = w4[f] * cc
        c.check(got == rec, "shell4_weighted_adjoint_sample")
        sampled += 1
    emit("Y137_K3_DETAILED_BALANCE", QQ_all_K3_pairs=db3, PQ_all=1,
         K2_to_shell3_all=1, shell4_sample_stride=SHELL4_STRIDE, shell4_sampled=sampled,
         shell4_sample_exact=1, shell4_unsampled="NAMED(the electric moves are involutions)",
         tag="MEASURED")
    del s4, where3, keys3, ex["s4"], ex["ext_index"]
    note("K3_SYMMETRY_DONE")

    # ---------------------------------------------------------------- K3 thresholds
    results = {}
    keep = None
    for a in K3_POINTS:
        r = threshold_ball(a, K3_B, K3_STEPS, K3_SCALE, ball3, FLOOR_NUM,
                           keep_y=(a == K3_POINTS[0]))
        s = sectors(r)
        results[a] = s
        emit("Y137_K3_SECTOR", ball="K3", z=frac(a, K3_B), steps=K3_STEPS, scale="10^12",
             rounding="checker", total_lower=r["nlo"], total_upper=r["nhi"],
             even_lower_count=s["even_lower"], even_upper_count=s["even_upper"],
             odd_lower_count=s["odd_lower"], odd_upper_count=s["odd_upper"],
             odd_L_sign=s["odd_L_sign"], odd_U_sign=s["odd_U_sign"], decoupled=1,
             max_trial_entry_bits=r["max_entry"].bit_length(),
             L_sha256=r["hl"], U_sha256=r["hu"], G_sha256=r["hg"], tag="MEASURED")
        got = (s["even_lower"], s["even_upper"], s["odd_lower"], s["odd_upper"])
        want = ORIG_K3[a]
        emit("Y137_K3_COMPARE", ball="K3", z=frac(a, K3_B),
             original="fe_k3lower.py K3L_EVAL " + ORIG_K3_SOURCE[a],
             order="even_lower,even_upper,odd_lower,odd_upper",
             original_counts=",".join(str(x) for x in want),
             port_counts=",".join(str(x) for x in got), agree=int(got == want),
             tag="MEASURED")
        if a == K3_POINTS[0]:
            keep = r
        note("K3_THRESHOLD_DONE", z=a)

    # ---------------------------------------------------------------- cross-check at z0
    v = [1, 2, 3, 4, 5, 6, 7, 8]
    a0 = K3_POINTS[0]
    vU, vG = form_value(keep["U"], v), form_value(keep["G"], v)
    dU, dG = direct_forms(a0, K3_B, K3_SCALE, ball3, keep["Y"], v, flat_out, ex["e4f"],
                          ex["e4s"], ex["e4c"])
    xU, xG = int(vU == dU), int(vG == dG)
    emit("Y137_K3_CROSSCHECK", z=frac(a0, K3_B), v="1..8", vUv_equals_direct=xU,
         vGv_equals_direct=xG, route="trial_vector,flat_move_counts,per_source_shell4_walk",
         tag="MEASURED")
    c.check(xU == 1 and xG == 1, "U_and_G_cross_check")

    # ---------------------------------------------------------------- controls (must fail)
    controls = []
    okb, whyb, _ = reflection_check(states, where, w, m, ball2, rd2, keep_inverse=False)
    controls.append(("broken_reflection_no_inverse_on_horizontal_links", okb == 0, whyb))
    del rd2
    E, o_plus = sector_bases(ODD_PAIR, 1)
    crossp = cross_terms(keep["L"], E, o_plus)
    controls.append(("odd_vector_sign_flip_flat6_plus_flat7", any(crossp),
                     "even_odd_cross_terms_nonzero=" + str(sum(1 for x in crossp if x))))
    E, o_minus = sector_bases(ODD_PAIR, -1)
    lo_odd = int(quad(keep["L"], o_minus) < 0)
    up_odd_flipped = int(-quad(keep["U"], o_minus) < 0)
    controls.append(("odd_upper_form_sign_flip", up_odd_flipped > lo_odd,
                     "upper=" + str(up_odd_flipped) + ">lower=" + str(lo_odd)
                     + "_violates_the_sandwich"))
    t3 = threshold_ball(6992, 100, 3, c.SCALE, ball2, FLOOR_NUM)
    got3 = (t3["nlo"], t3["nhi"], t3["hu"], t3["hg"], t3["hl"])
    controls.append(("equivalence_with_3_steps_instead_of_4", got3 != checker_out[6992],
                     "U_sha256_differs=" + str(int(got3[2] != checker_out[6992][2]))))
    dU2, dG2 = direct_forms(a0, K3_B, K3_SCALE, ball3, keep["Y"], v, flat_out, ex["e4f"],
                            ex["e4s"], ex["e4c"], drop_edge=True)
    controls.append(("crosscheck_with_one_shell4_edge_dropped", dG2 != vG,
                     "vGv_minus_direct_sign=" + str(sign(vG - dG2))))
    keep = None
    for k in ("e4f", "e4s", "e4c", "ext_keys", "code4"):
        ex[k] = None
    for name, failed, why in controls:
        emit("Y137_K3_CONTROL", control=name, must_fail=1, failed=int(failed), reason=why,
             tag="MEASURED")
        c.check(failed, "control_" + name)
    note("CONTROLS_DONE")

    # ---------------------------------------------------------------- original rounding
    for a in K3_POINTS:
        r = threshold_ball(a, K3_B, K3_STEPS, K3_SCALE, ball3, FLOOR_NUM,
                           round_like_original=True)
        s = sectors(r)
        got = (s["even_lower"], s["even_upper"], s["odd_lower"], s["odd_upper"])
        emit("Y137_K3_ROUNDING_VARIANT", ball="K3", z=frac(a, K3_B), steps=K3_STEPS,
             scale="10^12", rounding="original_floor_on_Y_ge_0",
             counts=",".join(str(x) for x in got),
             checker_rounding_counts=",".join(str(x) for x in (
                 results[a]["even_lower"], results[a]["even_upper"], results[a]["odd_lower"],
                 results[a]["odd_upper"])),
             original_counts=",".join(str(x) for x in ORIG_K3[a]),
             agree_original=int(got == ORIG_K3[a]), L_sha256=r["hl"], U_sha256=r["hu"],
             G_sha256=r["hg"], tag="MEASURED")
        note("VARIANT_DONE", z=a)

    # ---------------------------------------------------------------- result
    z0, z1, z2 = K3_POINTS
    r0, r1, r2 = results[z0], results[z1], results[z2]
    holds = (r0["even_lower"] == r0["even_upper"] == 2 and r0["odd_lower"] == 0
             and r0["odd_upper"] == 0 and r1["even_lower"] == 2 and r2["odd_lower"] == 0)
    if holds:
        statement = ("at z0 = 699567503/10^7 the reflection-even sector has exactly 2 levels "
                     "below z0 and the odd sector none (both one-sided counts agree), "
                     "E3_even >= 699686993/10^7 and E_odd >= 699689591/10^7, each conditional "
                     "on the floor for the lower side; the upper-side counts are unconditional")
    else:
        statement = "the measured counts differ from the expected statement; see SECTOR rows"
    emit("Y137_K3_RESULT", z0=frac(z0, K3_B), statement=statement,
         even_count_range_below_z0=str(r0["even_upper"]) + ".." + str(r0["even_lower"]),
         odd_count_range_below_z0=str(r0["odd_upper"]) + ".." + str(r0["odd_lower"]),
         E3_even_GE=frac(z1, K3_B), even_lower_count_there=r1["even_lower"],
         E_odd_GE=frac(z2, K3_B), odd_lower_count_there=r2["odd_lower"],
         lower_side="CONDITIONAL_on_the_#131_floor", upper_side="UNCONDITIONAL_min_max",
         status="HOLDS" if holds else "DIFFERS", tag="MEASURED_conditional_on_#131")
    emit("Y137_K3_SCOPE", floor="stated condition, used as given (94070673/10^6)",
         reflection_on_the_whole_space="NAMED(lattice symmetry of H); exact on K3 and shell 4",
         shell4_detailed_balance="MEASURED on the stride sample; NAMED elsewhere",
         amplitude_lane="#137 Wilson-amplitude design workflow, separate",
         port="checker threshold generalised; original K3 rounding rerun as a variant row")
    emit("Y137_K3_END", rows=len(ROWS) + 1, status="HOLDS" if holds else "DIFFERS")
    data = ("\n".join(ROWS) + "\n").encode("utf-8")
    out = os.path.join(HERE, OUT_NAME)
    with open(out, "wb") as fh:
        fh.write(data)
    digest = hashlib.sha256(data).hexdigest()
    with open(out + ".sha256", "wb") as fh:
        fh.write((digest + "  " + OUT_NAME + "\n").encode("utf-8"))
    note("WROTE", file=OUT_NAME, sha256=digest)


if __name__ == "__main__":
    main()
