#!/usr/bin/env python3
"""
Do indep_verify.py's two lines that moved from float to math.isqrt give what they gave?

isqrt and primes_below run only on the Python path, leading_minor_signs. A run through the Rust kernel never reaches them,
so this runs them directly: the recorded commit's file and this one side by side, on the inputs of the documented case.

1. isqrt on the row norms of the real 2x2 matrix, at all three thresholds, and the prime count they lead to.
2. primes_below on that many primes, the whole list.
3. isqrt on wide integers, perfect squares and their neighbours.
4. leading_minor_signs from both files and from the Rust kernel, on random symmetric matrices and on leading blocks of the
   real matrix under the run's own shuffle.

usage: indep_sqrt_check.py RECORDED_FILE THIS_FILE KERNEL [sabotage=isqrt|primes|signs]
Exits 1 on any difference, so each sabotage must exit 1. Integer only, json=0.
"""
import hashlib
import importlib.util
import math
import os
import random
import sys

RECORDED_SHA = "ca60e319d287daa657d7a1242568e8480b39744b9a465896c080d91b238f42e4"
THRESHOLDS = (23746649, 46576000, 90123457)
R = 9


def load(path, name, kernel=""):
    os.environ["INDEP_MINORS"] = kernel
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def text_sha(values):
    return hashlib.sha256(",".join(str(v) for v in values).encode()).hexdigest()


def real_matrix(n, weight, rows, mag, t, perm):
    # The B of count_below, under the permutation perm.
    pos = {v: i for i, v in enumerate(perm)}
    B = [[0] * n for _ in range(n)]
    for i in range(n):
        ii = pos[i]
        diag_e = sum(rows[i].values())
        for j, c in rows[i].items():
            B[ii][pos[j]] -= weight[i] * c * 1_000_000
        B[ii][ii] += weight[i] * (diag_e * 1_000_000 + R * 1_000_000 * mag[i] - t)
    return B


def main(argv):
    recorded, current, kernel = argv[:3]
    sabotage = argv[3].split("=")[1] if len(argv) > 3 else ""
    old = load(recorded, "indep_recorded")
    new = load(current, "indep_current")
    side = load(current, "indep_kernel", kernel)
    fails = 0
    same_file = sha(recorded) == RECORDED_SHA
    fails += 0 if same_file else 1
    print("INDEP_SQRT|recorded_sha256=%s|matches_receipt=%d|current_sha256=%s|kernel_sha256=%s|sabotage=%s|json=0" % (sha(recorded), 1 if same_file else 0, sha(current), sha(kernel), sabotage or "none"), flush=True)
    if sabotage == "isqrt":
        new.isqrt = lambda n: math.isqrt(n) + 1
    if sabotage == "primes":
        real = new.primes_below
        new.primes_below = lambda limit, count, skip: real(limit, count + 1, skip)[1:]
    if sabotage == "signs":
        real_signs = new.leading_minor_signs
        new.leading_minor_signs = lambda B: [-s for s in real_signs(B)]

    # 1. The real row norms.
    _, n, weight, rows, mag = new.build(2, 2)
    need_max = 0
    for t in THRESHOLDS:
        B = real_matrix(n, weight, rows, mag, t, list(range(n)))
        norms = [sum(v * v for v in row) for row in B]
        a = [old.isqrt(s) for s in norms]
        b = [new.isqrt(s) for s in norms]
        same = sum(1 for x, y in zip(a, b) if x == y)
        bits_old = max((x + 1).bit_length() for x in a)
        bits_new = max((y + 1).bit_length() for y in b)
        need = (bits_new * n + 2) // 30 + 2
        need_max = max(need_max, need)
        fails += 0 if same == n and bits_old == bits_new else 1
        print("INDEP_SQRT_ROWS|t_milli=%d|r=%d|rows=%d|same=%d|bits_recorded_file=%d|bits_this_file=%d|primes_needed=%d|json=0" % (t, R, n, same, bits_old, bits_new, need), flush=True)

    # 2. The whole prime list, the longest one the three thresholds ask for.
    p_old = old.primes_below(1 << 31, need_max, set())
    p_new = new.primes_below(1 << 31, need_max, set())
    same = p_old == p_new
    fails += 0 if same else 1
    print("INDEP_SQRT_PRIMES|count=%d|same_list=%d|first=%d|last=%d|sha256=%s|json=0" % (need_max, 1 if same else 0, p_new[0], p_new[-1], text_sha(p_new)), flush=True)

    # 3. Wide integers, squares and their neighbours.
    rng = random.Random(27)
    values = list(range(0, 2000)) + [(1 << k) + d for k in range(1, 400) for d in (-1, 0, 1)]
    for _ in range(30000):
        root = rng.getrandbits(rng.randrange(1, 300))
        values += [root * root - 1 if root else 0, root * root, root * root + 1]
    a = [old.isqrt(v) for v in values]
    b = [new.isqrt(v) for v in values]
    same = sum(1 for x, y in zip(a, b) if x == y)
    fails += 0 if same == len(values) else 1
    print("INDEP_SQRT_WIDE|values=%d|same=%d|sha256=%s|json=0" % (len(values), same, text_sha(b)), flush=True)

    # 4. All three sign paths on random symmetric matrices, then on blocks of the real matrix.
    both, with_kernel, count, skipped = 0, 0, 0, 0
    for size in range(1, 25):
        for _ in range(4):
            B = [[0] * size for _ in range(size)]
            for i in range(size):
                for j in range(i, size):
                    B[i][j] = B[j][i] = rng.randrange(-10 ** 9, 10 ** 9 + 1)
            sides = []
            try:
                sides = [old.leading_minor_signs(B), new.leading_minor_signs(B), side.kernel_signs(B)]
            except RuntimeError:
                skipped += 1
                continue
            count += 1
            both += 1 if sides[0] == sides[1] else 0
            with_kernel += 1 if sides[1] == sides[2] else 0
    fails += 0 if both == count and with_kernel == count else 1
    print("INDEP_SQRT_MATRICES|matrices=%d|recorded_file_vs_this_file_same=%d|this_file_vs_kernel_same=%d|skipped_for_a_zero_pivot=%d|json=0" % (count, both, with_kernel, skipped), flush=True)
    for t in THRESHOLDS:
        shuffle = random.Random(1)
        perm = list(range(n))
        shuffle.shuffle(perm)
        B = real_matrix(n, weight, rows, mag, t, perm)
        for k in (40, 80):
            block = [row[:k] for row in B[:k]]
            s_old, s_new, s_kernel = old.leading_minor_signs(block), new.leading_minor_signs(block), side.kernel_signs(block)
            fails += 0 if s_old == s_new == s_kernel else 1
            changes, prev = 0, 1
            for s in s_new:
                changes += s != prev
                prev = s
            print("INDEP_SQRT_BLOCK|t_milli=%d|k=%d|same_all_three=%d|negative=%d|sha256=%s|json=0" % (t, k, 1 if s_old == s_new == s_kernel else 0, changes, text_sha(s_new)), flush=True)
    print("INDEP_SQRT_DONE|failed=%d|json=0" % fails, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
