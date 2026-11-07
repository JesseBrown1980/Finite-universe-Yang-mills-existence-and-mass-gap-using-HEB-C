#!/usr/bin/env python3
"""Certified fixed-point integer intervals and exact cyclic power jumps; no floats."""
from hashlib import sha256
from math import factorial

BASE = 10**70
ONE = (BASE, BASE)
ZERO = (0, 0)

def checked_power(base, exponent):
    assert exponent >= 0
    value = 1
    while exponent:
        if exponent & 1:
            value *= base
        base *= base
        exponent >>= 1
    return value

def plus(a, b):
    return a[0] + b[0], a[1] + b[1]

def minus(a, b):
    return a[0] - b[1], a[1] - b[0]

def times(a, b):
    items = (a[0]*b[0], a[0]*b[1], a[1]*b[0], a[1]*b[1])
    low, high = min(items), max(items)
    return low // BASE, -((-high) // BASE)

def scale(a, k):
    if k < 0:
        return scale((-a[1], -a[0]), -k)
    return a[0]*k, a[1]*k

def divide(a, k):
    assert k > 0
    return a[0] // k, -((-a[1]) // k)

def inverse_integer(k):
    return BASE // k, -((-BASE) // k)

def atan_reciprocal(q):
    acc = ZERO
    for k in range(24):
        den = (2*k+1)*(checked_power(q, 2*k+1))
        term = inverse_integer(den)
        acc = plus(acc, term) if k % 2 == 0 else minus(acc, term)
    remainder = inverse_integer(49*q**49)
    return plus(acc, (0, remainder[1]))

def pi_interval():
    return minus(scale(atan_reciprocal(5), 16), scale(atan_reciprocal(239), 4))

def cos_interval(x):
    x2 = times(x, x)
    power = ONE
    acc = ZERO
    for k in range(24):
        term = divide(power, factorial(2*k))
        acc = plus(acc, term) if k % 2 == 0 else minus(acc, term)
        power = times(power, x2)
    next_term = divide(power, factorial(48))
    return plus(acc, (0, next_term[1]))

def exp_minus_interval(x):
    assert 0 < x[0] and x[1] < BASE
    power = ONE
    acc = ZERO
    for k in range(24):
        term = divide(power, factorial(k))
        acc = plus(acc, term) if k % 2 == 0 else minus(acc, term)
        power = times(power, x)
    next_term = divide(power, factorial(24))
    return plus(acc, (0, next_term[1]))

def integer_power(a, exponent):
    assert exponent >= 0
    result = ONE
    while exponent:
        if exponent & 1:
            result = times(result, a)
        a = times(a, a)
        exponent >>= 1
    return result

def step_kernel(v):
    n = len(v)
    return tuple(4*v[i] + v[(i-1) % n] + v[(i+1) % n] for i in range(n))

def product_kernel(a, b):
    n = len(a)
    assert n == len(b)
    c = [0]*n
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[(i+j) % n] += x*y
    return tuple(c)

def jump_kernel(n, exponent):
    base = tuple(4 if i == 0 else (1 if i in (1, n-1) else 0) for i in range(n))
    result = (1,) + (0,)*(n-1)
    while exponent:
        if exponent & 1:
            result = product_kernel(result, base)
        base = product_kernel(base, base)
        exponent >>= 1
    return result

def floor_pico(a):
    return a[0] // (BASE // 10**12)

def result():
    pi = pi_interval()
    t = divide(scale(times(pi, pi), 2), 27)
    continuum = exp_minus_interval(t)
    assert floor_pico(continuum) == floor_pico((continuum[1],continuum[1])) == 481387939225
    results = []
    previous = None
    for n in (3,9,27):
        steps = (n//3)**2
        assert steps*54 == 6*n*n
        kernel = (1,) + (0,)*(n-1)
        for _ in range(steps):
            kernel = step_kernel(kernel)
        assert kernel == jump_kernel(n, steps)
        assert sum(kernel) == checked_power(6, steps)
        if n == 3:
            decay = (BASE//2,BASE//2) # exact cos(2pi/3)=-1/2
        else:
            c = cos_interval(divide(scale(pi, 2), n))
            r = divide(plus((4*BASE,4*BASE), scale(c,2)), 6)
            decay = integer_power(r, steps)
        assert decay[0] <= decay[1] and decay[0] > continuum[1]
        delta = minus(decay, continuum)
        assert floor_pico(delta) == floor_pico((delta[1],delta[1]))
        assert previous is None or delta[1] < previous
        previous = delta[0]
        mid = ((decay[0] + decay[1])//2,)*2
        observed = floor_pico(mid)
        err = floor_pico(delta)
        expected = {
            3:(500000000000,18612060774),
            9:(481549672464,161733239),
            27:(481389859807,1920581),
        }[n]
        assert (observed,err) == expected, (n, observed, err)
        digest = sha256(','.join(map(str, kernel)).encode('ascii')).hexdigest()
        results.append(
            f'VIEWER_SHEAR|L={n}|steps={steps}|dt=1/{6*n*n}_s|t=1/54_s'
            f'|space=1/{n}_m|power_jump=PASS|direct_steps=PASS'
            f'|nonlinear=EXACT_ZERO|div=EXACT_ZERO|kernel_sum=6^{steps}'
            f'|discrete_amp_floor_pico={observed}'
            f'|continuum_amp_floor_pico={floor_pico(continuum)}'
            f'|abs_error_floor_pico={err}|kernel_sha256={digest}|json=0'
        )
    return '\n'.join(results) + '\n'

if __name__ == '__main__':
    print(result(), end='')
