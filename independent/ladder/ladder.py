#!/usr/bin/env python3
"""
Predict-then-verify coupling ladder for the finite S3 2x2-torus gap
(HEB-C, integer-only). Fischer rule: predict the move from certified data,
verify it with one rigorous certificate; nothing unverified is recorded.

Units: per-JE milli-energies. r = JB/JE held as (p, q): JE = q, JB = p.
A per-JE threshold x (milli) is passed as absolute threshold q*x for
H = JE*E + JB*M.

Certificate = number of eigenvalues of H below t, from the interval Sturm
verifier, summed over the four exact Z2xZ2 translation sectors (PR #14
reduction, sector shas pinned). Every SPOT_EVERY-th anchor is re-certified on
the full 1393-state matrix; any disagreement stops the run.
  count == 1  =>  E0 < t < E1          count >= 1  =>  E0 < t

Cell lemma (eigenvalues of E + rM non-decreasing in r, M >= 0):
  on [r_i, r_j]:  gap/JE  >=  L_i - T,   whenever E0(r_j) < T is certified,
  L_i = certified E1 lower bound at r_i.

Prediction (only chooses what to certify; never recorded as a result):
the rise of E0 between ratios from the exact second-order law
E0 ~ 24 - (6+sqrt14)/r (PR #11), and E1 near the anchor from the same law
shifted by the offset measured at the previous anchor. math.isqrt; no float.

Each certificate is SHA-256 keyed on (mode, matrix shas, JE, JB, t, digits)
and appended to ledger.hbp (json=0); reruns resume from the ledger.
"""
import hashlib
import math
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
# Inputs (regenerate; see LADDER_METHOD.md):
#   STURM_BIN  : built from independent/ladder/sturmrs (cargo build --release)
#   FULL_MATRIX: python3 independent/seat_sturm_integer_matrix.py > full.matrix
#   SECTOR_DIR : python3 independent/seat_translation_sectors.py SECTOR_DIR
VERIFIER = os.environ.get("STURM_BIN", os.path.join(HERE, "sturmrs", "target", "release", "sturmrs"))
FULL = os.environ.get("FULL_MATRIX", os.path.join(HERE, "work", "full.matrix"))
SECTORS = [os.path.join(os.environ.get("SECTOR_DIR", os.path.join(HERE, "work", "sectors")), n + ".matrix")
           for n in ("pp", "pm", "mp", "mm")]
SECTOR_SHA = {"pp": "fb6dbb3acbd411f61779f98881e6545d21ab7a39816c351d755fafe2c3f2c652",
              "pm": "9dc22f4bb6f410ebfcdc0bfb3854bf6d2827901ee379ed685772649d28315d48",
              "mp": "88eb8250eaf85815f155f09656f8a4dd19733148dd9e4505af978bed5974a75b",
              "mm": "d7dce164177f2b5498a367c9df78ff8d64c8d173a262daa65815b321ff21b653"}
FULL_SHA = "137285e0a1b55bdf0c8c56bec6bd69e0ab9138e6e7c05350d677f186e1981d2c"
LEDGER = os.path.join(HERE, "ledger.hbp")
DIGITS = 30
Q = 64
SPOT_EVERY = 10
K = 10 ** 6
A0 = 6 * K + math.isqrt(14 * K * K)   # (6+sqrt14)*10^6, floor
A1 = 6 * K + math.isqrt(6 * K * K)    # (6+sqrt6)*10^6, floor


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


for name, path in zip(("pp", "pm", "mp", "mm"), SECTORS):
    assert sha(path) == SECTOR_SHA[name], "sector matrix sha mismatch: " + name
assert sha(FULL) == FULL_SHA, "full matrix sha mismatch"


def load_cache():
    cache = {}
    if os.path.exists(LEDGER):
        for line in open(LEDGER):
            f = dict(kv.split("=", 1) for kv in line.strip().split("|")[1:] if "=" in kv)
            if f.get("kind") == "cert":
                cache[f["key"]] = int(f["count"])
    return cache


CACHE = load_cache()


def record(line):
    with open(LEDGER, "a") as fh:
        fh.write(line + "|json=0\n")


def run_one(matrix, je, jb, t):
    out = subprocess.run([VERIFIER, matrix, str(je), str(jb), str(t), str(DIGITS)], capture_output=True, text=True)
    f = dict(kv.split("=", 1) for kv in out.stdout.strip().split("|")[1:] if "=" in kv)
    if f.get("status") != "COMPLETE" or f.get("ambiguous") != "0":
        raise SystemExit("LADDER|error=uncertified|matrix=%s|JE=%d|JB=%d|t=%d|json=0" % (os.path.basename(matrix), je, jb, t))
    return int(f["negative"])


def count(p, q, x, mode="sectors"):
    je, jb, t = q, p, q * x
    shas = FULL_SHA if mode == "full" else ",".join(SECTOR_SHA[n] for n in ("pp", "pm", "mp", "mm"))
    k = hashlib.sha256(("%s|%s|%d|%d|%d|%d" % (mode, shas, je, jb, t, DIGITS)).encode()).hexdigest()
    if k in CACHE:
        return CACHE[k]
    t0 = time.monotonic_ns()
    if mode == "full":
        c, detail = run_one(FULL, je, jb, t), "full"
    else:
        parts = [run_one(m, je, jb, t) for m in SECTORS]
        c, detail = sum(parts), "pp:%d,pm:%d,mp:%d,mm:%d" % tuple(parts)
    CACHE[k] = c
    record("LADDER|kind=cert|mode=%s|key=%s|JE=%d|JB=%d|t=%d/1000|count=%d|detail=%s|ms=%d"
           % (mode, k, je, jb, t, c, detail, (time.monotonic_ns() - t0) // 1000000))
    return c


def pred_e0(p, q):
    return 24000 - (A0 * q + p * 1000 - 1) // (p * 1000)


def pred_e1(p, q):
    return 24000 - (A1 * q + p * 1000 - 1) // (p * 1000)


def tight_e1_lower(p, q, guess, step):
    """Largest certified x with count == 1 found by a short search from guess."""
    x, best, n = guess, None, 0
    while n < 8:
        n += 1
        c = count(p, q, x)
        if c == 1:
            best = x
            x += step
        elif best is not None:
            if step <= 4:
                return best, n
            step //= 2
            x = best + step
        elif c >= 2:
            x -= step
            step *= 2
        else:
            x += step
            step *= 2
    if best is None:
        raise SystemExit("LADDER|error=no_E1_lower|p=%d|q=%d|json=0" % (p, q))
    return best, n


def tight_e0_upper(p, q, start, step):
    """Smallest certified x with count >= 1, searching down from a certified start."""
    best, x, n = start, start - step, 0
    while n < 8 and step > 4:
        n += 1
        if count(p, q, x) >= 1:
            best = x
            x -= step
        else:
            step //= 2
            x = best - step
    return best, n


def main():
    r_end = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    budget_s = int(sys.argv[2]) if len(sys.argv) > 2 else 6600
    start = time.monotonic_ns()
    p, q = 3 * Q, Q
    L, n1 = tight_e1_lower(p, q, 20327, 64)          # anchor r=3 (E1 > 20.327 certified in the pilot)
    U, n0 = tight_e0_upper(p, q, 19300, 256)         # E0(3) < 19.300 certified (PR #14), tightened
    record("LADDER|kind=anchor|r=%d/%d|E0_upper=%d/1000|E1_lower=%d/1000|tries=%d" % (p, q, U, L, n0 + n1))
    print("anchor r=%d/%d  E0 < %d/1000  E1 > %d/1000" % (p, q, U, L), flush=True)
    off1, anchors = L - pred_e1(p, q), 1
    while p < r_end * q:
        if (time.monotonic_ns() - start) // 10 ** 9 > budget_s:
            print("LADDER|status=budget_reached|r=%d/%d|json=0" % (p, q), flush=True)
            return
        margin = max(1, (L - U) // 4)
        target = L - margin                          # certify E0(next) < target
        room = target - U                            # allowed predicted rise of E0
        lo, hi = p + 1, p * 3
        while lo < hi:                               # largest next with predicted rise <= room/2
            mid = (lo + hi + 1) // 2
            if 2 * (pred_e0(mid, q) - pred_e0(p, q)) <= room:
                lo = mid
            else:
                hi = mid - 1
        nxt = lo
        while count(nxt, q, target) == 0:            # refuted line: halve the jump
            if nxt == p + 1:
                raise SystemExit("LADDER|error=cannot_advance|r=%d/%d|json=0" % (p, q))
            nxt = p + max(1, (nxt - p) // 2)
        record("LADDER|kind=cell|r_lo=%d/%d|r_hi=%d/%d|E1_lower_at_lo=%d/1000|E0_upper_at_hi=%d/1000|gap_per_JE_gt=%d/1000"
               % (p, q, nxt, q, L, target, L - target))
        U2, n0 = tight_e0_upper(nxt, q, target, max(8, margin))
        L2, n1 = tight_e1_lower(nxt, q, pred_e1(nxt, q) + off1, max(8, (L - U) // 8))
        anchors += 1
        if anchors % SPOT_EVERY == 0:                # full-matrix spot check of the anchor's E1 certificate
            if count(nxt, q, L2, "full") != count(nxt, q, L2):
                raise SystemExit("LADDER|error=sector_full_mismatch|r=%d/%d|json=0" % (nxt, q))
            print("  spot-check r=%d/%d full matrix agrees" % (nxt, q), flush=True)
        record("LADDER|kind=anchor|r=%d/%d|E0_upper=%d/1000|E1_lower=%d/1000|tries=%d" % (nxt, q, U2, L2, n0 + n1))
        print("cell [%d/%d, %d/%d] gap/JE > %d/1000 | anchor E0 < %d/1000  E1 > %d/1000  (%d certs)"
              % (p, q, nxt, q, L - target, U2, L2, n0 + n1 + 1), flush=True)
        off1 = L2 - pred_e1(nxt, q)
        p, L, U = nxt, L2, U2
    print("LADDER|status=complete|r_end=%d|json=0" % r_end, flush=True)


if __name__ == "__main__":
    main()
