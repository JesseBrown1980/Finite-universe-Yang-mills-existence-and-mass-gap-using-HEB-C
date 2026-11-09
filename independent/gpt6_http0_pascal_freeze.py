#!/usr/bin/env python3
"""Independent 27-ring Pascal/Frobenius/freeze-play control; not a YM reduction."""
import hashlib
import sys

N = 27


def check(ok, label):
    if not ok:
        print('FAILED|check=' + label + '|json=0', flush=True)
        raise SystemExit(1)


def mul(a, b):
    z = [0] * N
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    z[(i + j) % N] = (z[(i + j) % N] + x * y) % 3
    return z


def power(base, exponent):
    z = [1] + [0] * (N - 1)
    while exponent:
        if exponent & 1:
            z = mul(z, base)
        base = mul(base, base)
        exponent >>= 1
    return z


def cube_jump(t, k):
    for _ in range(k):
        t = mul(mul(t, t), t)
    return t


def sha(x):
    return hashlib.sha256(bytes(x)).hexdigest()


def main():
    sabotage = len(sys.argv) == 2 and sys.argv[1] == 'sabotage'
    check(len(sys.argv) == 1 or sabotage, 'arguments')
    eye = [1] + [0] * (N - 1)
    plus = [1, 1, 1] + [0] * (N - 3)
    minus = [1, 1, 2] + [0] * (N - 3)
    zero = [0] * N
    check(cube_jump(plus, 3) == zero, 'plus_27_zero')
    check(cube_jump(minus, 3) == eye, 'minus_27_identity')
    for k in (0, 1, 2, 3, 5, 16):
        e = 1
        for _ in range(k):
            e *= 3
        check(cube_jump(minus, k) == power(minus, e), 'jump_minus_' + str(k))
        check(cube_jump(plus, k) == power(plus, e), 'jump_plus_' + str(k))
    state = [0] * N
    state[0], state[7], state[26] = 1, 2, 1
    leaves = {}
    direct = state[:]
    for t in range(28):
        if t in (0, 1, 3, 9, 27):
            leaves[t] = direct[:]
        direct = mul(minus, direct)
    check(leaves[27] == state, 'forward_cycle')
    check(mul(power(minus, 26), leaves[9]) == mul(power(minus, 8), state), 'reverse_leaf')
    check(mul(power(minus, 18), leaves[9]) == leaves[27], 'play_from_nine')
    chain = hashlib.sha256(b'HBI|HBP|SHA|SH|HASH|27|').digest()
    for t in sorted(leaves):
        payload = leaves[t][:]
        if sabotage and t == 9:
            payload[0] = (payload[0] + 1) % 3
        check(payload == mul(power(minus, t), state), 'outside_anchor_leaf_' + str(t))
        line = ('HBP|step=' + str(t) + '|sha256=' + sha(payload) + '|json=0\n').encode('ascii')
        chain = hashlib.sha256(chain + line).digest()
    print('PASCAL27|modulus=3|ring=27|plus_27=ZERO|minus_27=IDENTITY|jump3_k=0,1,2,3,5,16|result=PASS|json=0')
    print('FREEZE_PLAY27|leaves=0,1,3,9,27|anchor=OUTSIDE_DIRECT_REPLAY|forward=PASS|reverse=PASS|tamper=REJECTED|result=PASS|json=0')
    print('HBP_CHAIN|leaves=5|sha256=' + chain.hex() + '|json=0')
    print('SCOPE|physical_ym_jump=NOT_PROVED|row_rebuild=SEPARATE|full_store_replay=NOT_RUN|json=0')


if __name__ == '__main__':
    main()
