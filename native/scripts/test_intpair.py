#!/usr/bin/env python3
"""
IntPair against CPython's rational class, value for value, on a seeded integer-only random set and an exhaustive small grid.

The one file allowed to import fractions and decimal: fractions is the reference, and each gives a value IntPair must refuse.
Every operation runs on both classes with the same operands, and the two outcomes must match: same value, same kind (int or
pair), same exception type. Operands reach 3,000 bits, denominators are negative as often as positive, zero is common, and some
denominators are multiples of the hash modulus. Where CPython's class would hand back floating point, IntPair must raise
TypeError, and that is tested too. rejection_checks makes two deliberate floats, half and 4 * half, and two complex values, each only to be refused.

usage: test_intpair.py [SEED] [ROUNDS]     Prints one INTPAIR_DIFF row. Exit 1 on any failure.
       test_intpair.py --teeth             Breaks IntPair one way at a time. Every break must be seen. Exit 1 if one is missed.
       test_intpair.py --int-power         int_power against ** on ints, its refusals, and a broken copy that must be seen. Exit 1 on any failure.
The true division here goes through operator.truediv, so this file holds no division token. Integer only, json=0.
"""
import copy
import decimal
import fractions
import math
import operator
import os
import pickle
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intpair import IntPair, int_power, qdiv  # noqa: E402

F = fractions.Fraction
Q = IntPair
P = sys.hash_info.modulus
SHOWN = 20


class Tally:
    def __init__(self):
        self.count = 0
        self.fails = 0

    def fail(self, name, got, want):
        self.fails += 1
        if self.fails <= SHOWN:
            print("INTPAIR_FAIL|op=%s|got=%s|want=%s|json=0" % (name, str(got)[:200], str(want)[:200]), flush=True)


def outcome(call):
    try:
        return call()
    except ArithmeticError as e:
        return ("raised", type(e).__name__)
    except (TypeError, ValueError) as e:
        return ("raised", type(e).__name__)


def same(a, b):
    """a came from IntPair, b from the reference."""
    if isinstance(b, F):
        return type(a) is Q and type(a.numerator) is int and type(a.denominator) is int and a.numerator == b.numerator and a.denominator == b.denominator
    if isinstance(b, tuple):
        return isinstance(a, tuple) and len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return type(a) is type(b) and a == b


def check(tally, name, on_pair, on_ref):
    tally.count += 1
    a, b = outcome(on_pair), outcome(on_ref)
    if not same(a, b):
        tally.fail(name, a, b)


def must_raise(tally, name, call, kind=TypeError):
    tally.count += 1
    try:
        got = call()
    except kind:
        return
    except Exception as e:
        tally.fail(name, type(e).__name__, kind.__name__)
        return
    tally.fail(name, got, kind.__name__)


def gen_int(rng):
    k = rng.randrange(16)
    sign = -1 if rng.randrange(2) else 1
    if k < 3:
        return rng.randint(-12, 12)
    if k < 6:
        return rng.randrange(-10 ** 6, 10 ** 6)
    if k < 10:
        return sign * rng.getrandbits(rng.randrange(1, 400))
    if k == 10:
        return sign * rng.getrandbits(rng.randrange(400, 3000))
    if k == 11:
        return sign * P * rng.randint(1, 5)
    if k == 12:
        return sign * ((1 << rng.randrange(1, 300)) + rng.randint(-1, 1))
    if k == 13:
        return sign * int_power(10, rng.randrange(0, 40)) * rng.randint(1, 9)
    if k == 14:
        return 0
    return sign * rng.randint(1, 2)


def gen_nonzero(rng):
    v = gen_int(rng)
    return v if v else rng.choice((1, -1, 2, -2))


def gen_pair(rng):
    n, d = gen_int(rng), gen_nonzero(rng)
    if rng.randrange(8) == 0:
        d = 1
    return n, d


UNARY = (
    ("neg", operator.neg), ("pos", operator.pos), ("abs", abs), ("bool", bool), ("int", int), ("str", str), ("hash", hash),
    ("trunc", math.trunc), ("floor", math.floor), ("ceil", math.ceil), ("round", round), ("dunder_floor", lambda x: x.__floor__()),
    ("numerator", lambda x: x.numerator), ("denominator", lambda x: x.denominator), ("as_integer_ratio", lambda x: x.as_integer_ratio()),
    ("is_integer", lambda x: x.is_integer()), ("percent_s", lambda x: "%s" % x), ("percent_d", lambda x: "%d" % x), ("fstring", lambda x: f"{x}"),
    ("fstring_s", lambda x: f"{x!s:>18}"), ("format_empty", lambda x: format(x, "")),
)
BINARY = (
    ("add", operator.add), ("sub", operator.sub), ("mul", operator.mul), ("truediv", operator.truediv), ("floordiv", operator.floordiv), ("mod", operator.mod), ("divmod", divmod),
    ("lt", operator.lt), ("le", operator.le), ("gt", operator.gt), ("ge", operator.ge), ("eq", operator.eq), ("ne", operator.ne),
)
MAX_DENOMINATORS = (1, 2, 3, 10, 999, 10 ** 6, 2 ** 40, 0, -1)


def unary_checks(tally, n, d, rng):
    q, f = outcome(lambda: Q(n, d)), outcome(lambda: F(n, d))
    tally.count += 1
    if not same(q, f):
        tally.fail("construct", q, f)
    if isinstance(f, tuple):
        return None
    for name, op in UNARY:
        check(tally, name, lambda: op(q), lambda: op(f))
    tally.count += 1
    if repr(q).replace("IntPair", "Fraction") != repr(f):
        tally.fail("repr", repr(q), repr(f))
    for digits in (rng.randint(-5, 7), 1, 2, 4, 0):
        check(tally, "round_n", lambda: round(q, digits), lambda: round(f, digits))
    for most in (rng.choice(MAX_DENOMINATORS), rng.randint(1, 10 ** 9)):
        check(tally, "limit_denominator", lambda: q.limit_denominator(most), lambda: f.limit_denominator(most))
    tally.count += 1
    if not same(q.limit_denominator(), f.limit_denominator()):
        tally.fail("limit_denominator_default", q.limit_denominator(), f.limit_denominator())
    if q.denominator == 1:
        tally.count += 2
        if hash(q) != hash(q.numerator):
            tally.fail("hash_of_whole", hash(q), hash(q.numerator))
        if {q.numerator: 1}.get(q) != 1 or {q: 1}.get(q.numerator) != 1:
            tally.fail("dict_key", q, q.numerator)
    for name, call in (("pickle", lambda: pickle.loads(pickle.dumps(q))), ("copy", lambda: copy.copy(q)), ("deepcopy", lambda: copy.deepcopy(q))):
        check(tally, name, call, lambda: f)
    return q, f


def binary_checks(tally, a, b, m):
    qa, fa = a
    qb, fb = b
    for name, op in BINARY:
        check(tally, name, lambda: op(qa, qb), lambda: op(fa, fb))
        check(tally, name + "_int_right", lambda: op(qa, m), lambda: op(fa, m))
        check(tally, name + "_int_left", lambda: op(m, qb), lambda: op(m, fb))
    check(tally, "qdiv", lambda: qdiv(qa, qb), lambda: operator.truediv(fa, fb))
    check(tally, "qdiv_int_right", lambda: qdiv(qa, m), lambda: operator.truediv(fa, m))
    check(tally, "qdiv_int_left", lambda: qdiv(m, qb), lambda: operator.truediv(m, fb))
    check(tally, "qdiv_two_ints", lambda: qdiv(m, qb.numerator), lambda: F(m, fb.numerator))
    check(tally, "construct_pair_pair", lambda: Q(qa, qb), lambda: F(fa, fb))
    check(tally, "construct_int_pair", lambda: Q(m, qb), lambda: F(m, fb))
    check(tally, "construct_pair_int", lambda: Q(qa, m), lambda: F(fa, m))
    check(tally, "construct_copy", lambda: Q(qa), lambda: F(fa))
    check(tally, "construct_int", lambda: Q(m), lambda: F(m))


def pow_checks(tally, a, rng):
    qa, fa = a
    k = rng.randint(-7, 7)
    check(tally, "pow_int", lambda: qa ** k, lambda: fa ** k)
    check(tally, "pow_pair", lambda: qa ** Q(k), lambda: fa ** F(k))
    m = rng.randint(-20, 20)
    check(tally, "rpow", lambda: m ** Q(k), lambda: m ** F(k))
    must_raise(tally, "pow_three_args", lambda: pow(qa, 2, 7))


def collection_checks(tally, items, rng):
    qs = [q for q, _ in items]
    fs = [f for _, f in items]
    for name, op in (("sum", sum), ("min", min), ("max", max)):
        check(tally, name, lambda: op(qs), lambda: op(fs))
    tally.count += 3
    if [str(x) for x in sorted(qs)] != [str(x) for x in sorted(fs)]:
        tally.fail("sorted", qs, fs)
    if [str(x) for x in set(qs)] != [str(x) for x in set(fs)]:
        tally.fail("set_order", qs, fs)
    if [str(x[0]) for x in {(q, 1) for q in qs}] != [str(x[0]) for x in {(f, 1) for f in fs}]:
        tally.fail("tuple_set_order", qs, fs)
    probe = rng.randrange(len(qs))
    tally.count += 1
    if {q: i for i, q in enumerate(qs)}[qs[probe]] != {f: i for i, f in enumerate(fs)}[fs[probe]]:
        tally.fail("dict_lookup", qs[probe], fs[probe])


def rejection_checks(tally):
    half = operator.truediv(1, 2)
    real = type(half)
    q = Q(1, 2)
    third = Q(1, 3)
    for name, call in (
        ("construct_real", lambda: Q(half)), ("construct_real_den", lambda: Q(1, half)), ("construct_str", lambda: Q("1/2")), ("construct_none_num", lambda: Q(None, 2)),
        ("add_real", lambda: q + half), ("radd_real", lambda: half + q), ("sub_real", lambda: q - half), ("rsub_real", lambda: half - q),
        ("mul_real", lambda: q * half), ("rmul_real", lambda: half * q), ("truediv_real", lambda: operator.truediv(q, half)), ("rtruediv_real", lambda: operator.truediv(half, q)),
        ("floordiv_real", lambda: q // half), ("mod_real", lambda: q % half), ("divmod_real", lambda: divmod(q, half)), ("lt_real", lambda: q < half), ("ge_real", lambda: half >= q),
        ("pow_real", lambda: q ** half), ("rpow_real", lambda: half ** q), ("pow_fractional", lambda: q ** Q(1, 2)), ("rpow_fractional", lambda: 2 ** Q(1, 2)),
        ("to_real", lambda: real(q)), ("qdiv_real_left", lambda: qdiv(half, 1)), ("qdiv_real_right", lambda: qdiv(1, half)), ("qdiv_str", lambda: qdiv("a", 1)),
        ("format_spec", lambda: format(q, "8d")), ("format_spec_fixed", lambda: format(q, "f")),
        ("dict_key_real", lambda: {q: 1}.get(half)), ("in_list_real", lambda: half in [q]), ("to_complex", lambda: complex(q)),
        ("limit_str", lambda: third.limit_denominator("3")), ("limit_none", lambda: third.limit_denominator(None)),
        ("add_str", lambda: q + "a"), ("lt_str", lambda: q < "a"), ("add_none", lambda: q + None), ("lt_none", lambda: q < None),
    ):
        must_raise(tally, name, call)
    others = (("real", half), ("real_whole", 4 * half), ("complex", complex(1, 2)), ("complex_whole", complex(2, 0)), ("decimal", decimal.Decimal(1)), ("decimal_whole", decimal.Decimal(2)), ("fraction", F(1, 2)), ("fraction_whole", F(2)))
    for kind, other in others:
        for value in (q, Q(2)):
            for name, op in BINARY + (("pow", operator.pow),):
                must_raise(tally, "%s_%s_right" % (name, kind), lambda: op(value, other))
                must_raise(tally, "%s_%s_left" % (name, kind), lambda: op(other, value))
        must_raise(tally, "limit_%s" % kind, lambda: third.limit_denominator(other))
        must_raise(tally, "limit_%s_low_denominator" % kind, lambda: q.limit_denominator(other))
        must_raise(tally, "round_%s" % kind, lambda: round(q, other))
    for name, call in (("zero_den", lambda: Q(1, 0)), ("zero_pair_den", lambda: Q(Q(1), Q(0))), ("qdiv_zero", lambda: qdiv(1, 0)), ("qdiv_zero_pair", lambda: qdiv(q, Q(0))), ("neg_power_of_zero", lambda: operator.pow(Q(0), -1))):
        must_raise(tally, name, call, ZeroDivisionError)
    check(tally, "default", Q, F)
    check(tally, "bool_num", lambda: Q(True), lambda: F(True))
    check(tally, "bool_pair", lambda: Q(True, 2), lambda: F(True, 2))
    check(tally, "bool_add", lambda: Q(1, 2) + True, lambda: F(1, 2) + True)
    check(tally, "eq_none", lambda: q == None, lambda: F(1, 2) == None)  # noqa: E711
    check(tally, "ne_none", lambda: q != None, lambda: F(1, 2) != None)  # noqa: E711
    check(tally, "eq_str", lambda: q == "1/2", lambda: F(1, 2) == "1/2")
    check(tally, "ne_str", lambda: q != "1/2", lambda: F(1, 2) != "1/2")
    check(tally, "limit_pair", lambda: third.limit_denominator(Q(5, 2)), lambda: F(1, 3).limit_denominator(F(5, 2)))
    check(tally, "limit_bool", lambda: third.limit_denominator(True), lambda: F(1, 3).limit_denominator(True))
    check(tally, "round_pair", lambda: round(third, Q(2)), lambda: round(F(1, 3), F(2)))


def small_grid(tally, rng):
    """Every small value, so the ties of round and limit_denominator all come up."""
    values = []
    for n in range(-32, 33):
        for d in range(-32, 33):
            if d == 0:
                continue
            q, f = Q(n, d), F(n, d)
            values.append((q, f))
            for digits in (None, -1, 0, 1, 2):
                check(tally, "grid_round", lambda: round(q, digits), lambda: round(f, digits))
            for name, op in (("grid_floor", math.floor), ("grid_ceil", math.ceil), ("grid_int", int), ("grid_hash", hash), ("grid_str", str)):
                check(tally, name, lambda: op(q), lambda: op(f))
            if d > 0:
                for most in range(1, 14):
                    check(tally, "grid_limit", lambda: q.limit_denominator(most), lambda: f.limit_denominator(most))
    for _ in range(40000):
        a, b = rng.choice(values), rng.choice(values)
        name, op = rng.choice(BINARY)
        check(tally, "grid_" + name, lambda: op(a[0], b[0]), lambda: op(a[1], b[1]))
    return len(values)


def run(seed, rounds):
    rng = random.Random(seed)
    tally = Tally()
    rejection_checks(tally)
    grid = small_grid(tally, rng)
    pool = []
    made = 0
    for r in range(rounds):
        n, d = gen_pair(rng)
        made += 1
        item = unary_checks(tally, n, d, rng)
        if item is None:
            continue
        pool.append(item)
        if len(pool) > 64:
            pool.pop(rng.randrange(len(pool)))
        other = rng.choice(pool)
        binary_checks(tally, item, other, gen_int(rng))
        pow_checks(tally, item, rng)
        if r % 16 == 0 and len(pool) >= 2:
            collection_checks(tally, rng.sample(pool, rng.randint(2, min(32, len(pool)))), rng)
    return tally, made + grid


def bad_floor(self):
    return self._n // self._d + (1 if self._d > 1 and self._n < 0 else 0)


def bad_ceil(self):
    return self._n // self._d


def bad_int(self):
    return self._n // self._d


def bad_str(self):
    return "%d/%d" % (self._n, self._d)


def bad_hash(self):
    return hash((self._n, self._d))


def bad_lt(self, other):
    if type(other) is Q:
        return self._n * other._d <= self._d * other._n
    return self._n < self._d * other if isinstance(other, int) else NotImplemented


def bad_eq(self, other):
    if type(other) is Q:
        return self._n == other._n
    return self._n == other if isinstance(other, int) else NotImplemented


def bad_abs(self):
    return Q(self._n, self._d)


def bad_mod(self, other):
    o = Q(other)
    return Q(abs(self._n * o._d) % abs(o._n * self._d), self._d * o._d)


def bad_rsub(self, other):
    return Q(self._n - other * self._d, self._d)


def bad_round(self, digits=None):
    if digits is None:
        whole, rest = divmod(self._n, self._d)
        return whole + 1 if rest * 2 >= self._d else whole
    shift = 10 ** abs(digits)
    return Q(bad_round(self * shift), shift) if digits > 0 else Q(bad_round(qdiv(self, shift)) * shift)


def bad_limit(self, most=1000000):
    if most < 1:
        raise ValueError
    if self._d <= most:
        return self
    p0, q0, p1, q1 = 0, 1, 1, 0
    n, d = self._n, self._d
    while True:
        a = n // d
        q2 = q0 + a * q1
        if q2 > most:
            break
        p0, q0, p1, q1 = p1, q1, p0 + a * p1, q2
        n, d = d, n - a * d
    k = (most - q0) // q1
    return Q(p1, q1) if 2 * d * (q0 + k * q1) < self._d else Q(p0 + k * p1, q0 + k * q1)


def bad_pow(self, exponent, modulo=None):
    if modulo is not None:
        return NotImplemented
    if isinstance(exponent, Q):
        exponent = exponent._n
    if exponent >= 0:
        return Q(self._n ** exponent, self._d ** exponent)
    power = -exponent
    if self._n == 0:
        raise ZeroDivisionError
    return Q(self._d ** power, abs(self._n) ** power)


def bad_reduce(self):
    return (Q, (self._d, self._n))


def lenient_eq(self, other):
    if type(other) is Q:
        return self._n == other._n and self._d == other._d
    return (self._n == other and self._d == 1) if isinstance(other, int) else NotImplemented


def lenient_limit(self, most=1000000):
    if most < 1:
        raise ValueError
    if self._d <= most:
        return self
    p0, q0, p1, q1 = 0, 1, 1, 0
    n, d = self._n, self._d
    while True:
        a = n // d
        q2 = q0 + a * q1
        if q2 > most:
            break
        p0, q0, p1, q1 = p1, q1, p0 + a * p1, q2
        n, d = d, n - a * d
    k = (most - q0) // q1
    return Q(p1, q1) if 2 * d * (q0 + k * q1) <= self._d else Q(p0 + k * p1, q0 + k * q1)


def lenient_pow(self, exponent, modulo=None):
    if modulo is not None:
        return NotImplemented
    if isinstance(exponent, Q):
        if exponent._d != 1:
            raise TypeError
        exponent = exponent._n
    elif not isinstance(exponent, int):
        return NotImplemented
    if exponent >= 0:
        return Q(self._n ** exponent, self._d ** exponent)
    if self._n == 0:
        raise ZeroDivisionError
    power = -exponent
    return qdiv(self._d ** power, self._n ** power)


def lenient_rpow(self, base, modulo=None):
    if modulo is not None:
        return NotImplemented
    if self._d != 1:
        raise TypeError
    return base ** self._n if self._n >= 0 else Q(base) ** self._n


def lenient_round(self, digits=None):
    if digits is None:
        whole, rest = divmod(self._n, self._d)
        return whole if rest * 2 < self._d else whole + 1 if rest * 2 > self._d else whole + whole % 2
    shift = 10 ** abs(digits)
    return Q(lenient_round(self * shift), shift) if digits > 0 else Q(lenient_round(qdiv(self, shift)) * shift)


# (what the row calls the break, the name it replaces, its function)
TEETH = (
    ("__floor__", "__floor__", bad_floor), ("__ceil__", "__ceil__", bad_ceil), ("__int__", "__int__", bad_int), ("__str__", "__str__", bad_str), ("__hash__", "__hash__", bad_hash),
    ("__lt__", "__lt__", bad_lt), ("__eq__", "__eq__", bad_eq), ("__abs__", "__abs__", bad_abs), ("__mod__", "__mod__", bad_mod), ("__rsub__", "__rsub__", bad_rsub),
    ("__round__", "__round__", bad_round), ("limit_denominator", "limit_denominator", bad_limit), ("__pow__", "__pow__", bad_pow), ("__reduce__", "__reduce__", bad_reduce),
    ("__eq___lets_other_numbers_through", "__eq__", lenient_eq), ("limit_denominator_lets_other_numbers_through", "limit_denominator", lenient_limit),
    ("__pow___lets_whole_other_numbers_through", "__pow__", lenient_pow), ("__rpow___lets_a_float_base_through", "__rpow__", lenient_rpow), ("__round___lets_other_numbers_through", "__round__", lenient_round),
)


def teeth():
    missed = 0
    for label, name, broken in TEETH:
        keep = getattr(Q, name)
        setattr(Q, name, broken)
        try:
            tally, _ = run(27, 300)
        finally:
            setattr(Q, name, keep)
        seen = tally.fails
        missed += 0 if seen else 1
        print("INTPAIR_TOOTH|broken=%s|failures_seen=%d|json=0" % (label, seen), flush=True)
    print("INTPAIR_TEETH_DONE|breaks=%d|missed=%d|json=0" % (len(TEETH), missed), flush=True)
    return 1 if missed else 0


def int_power_rows(power):
    """(comparisons, failures): power against ** on a grid of int bases and exponents, then its refusals of a negative or non-int exponent."""
    count, fails = 0, 0
    for base in list(range(-12, 13)) + [P, -P, 1 << 200, -(3 << 300)]:
        for exponent in range(0, 40):
            count += 1
            got = power(base, exponent)
            if type(got) is not int or got != base ** exponent:
                fails += 1
    half = operator.truediv(1, 2)
    for exponent, refused in ((-1, ValueError), (-2, ValueError), (-40, ValueError), (half, TypeError), (F(2), TypeError), (Q(2), TypeError)):
        for base in (0, 1, 2, -3, 10):
            count += 1
            try:
                power(base, exponent)
            except refused:
                continue
            except (TypeError, ValueError, ArithmeticError):
                pass
            fails += 1
    return count, fails


def main(argv):
    global SHOWN
    if argv[:1] == ["--teeth"]:
        SHOWN = 0
        return teeth()
    if argv[:1] == ["--int-power"]:
        count, fails = int_power_rows(int_power)
        _, broken_seen = int_power_rows(lambda base, exponent: base ** abs(exponent) + (exponent == 7))
        print("INTPAIR_INT_POWER|comparisons=%d|failures=%d|broken_copy_failures_seen=%d|json=0" % (count, fails, broken_seen), flush=True)
        return 1 if fails or not broken_seen else 0
    seed = int(argv[0]) if argv else 27
    rounds = int(argv[1]) if len(argv) > 1 else 20000
    tally, values = run(seed, rounds)
    print("INTPAIR_DIFF|seed=%d|rounds=%d|values=%d|comparisons=%d|failures=%d|json=0" % (seed, rounds, values, tally.count, tally.fails), flush=True)
    return 1 if tally.fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
