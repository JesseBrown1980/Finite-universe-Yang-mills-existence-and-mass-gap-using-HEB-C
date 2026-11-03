#!/usr/bin/env python3
"""
Exact signed rationals as a reduced pair of Python ints. The operator's rule: integer only.

IntPair holds a numerator and a positive denominator with no common factor, both int, and every operation returns an exact
int or IntPair. Division is the named function qdiv(a, b), so a script using it holds no true-division token at all. It takes
any mix of int and IntPair, and two ints give an exact pair. The operators / and % still work on IntPair, so a value handed to
code that divides stays exact, and integer_only_audit.py flags any such / in the calling script.

The arithmetic follows the algorithms of CPython's rational class, gcd shortcuts and limit_denominator included, and hash()
agrees with it value for value, so sets and dicts of these iterate in the same order and hash(IntPair(n)) == hash(n).
A float, complex, Decimal or Fraction raises TypeError from every operator and comparison, == and != included, and from a dict
lookup that reaches a pair by its hash. A str or None raises TypeError from arithmetic and ordering, and == reads them as
unequal, as on any Python object. limit_denominator and round take int or IntPair. A power with a non-integer exponent and a
non-empty format spec raise TypeError too, because those are the places where the same class in CPython hands back floating point.
test_intpair.py compares this against CPython's class value for value. Integer only, json=0.
"""
from math import gcd
import numbers
import sys

HASH_MODULUS = sys.hash_info.modulus
HASH_INF = sys.hash_info.inf


def _refuse_other_numbers(other):
    """Every numeric type outside int and IntPair registers as numbers.Number: float, complex, Decimal and Fraction among them."""
    if isinstance(other, numbers.Number):
        raise TypeError("IntPair takes int or IntPair, not %s" % type(other).__name__)


def _make(n, d):
    """A pair known to be reduced, with d above zero."""
    p = object.__new__(IntPair)
    p._n = n
    p._d = d
    return p


class IntPair:
    __slots__ = ("_n", "_d")

    def __new__(cls, a=0, b=None):
        self = object.__new__(cls)
        if b is None:
            if type(a) is int:
                self._n, self._d = a, 1
            elif isinstance(a, IntPair):
                self._n, self._d = a._n, a._d
            elif isinstance(a, int):
                self._n, self._d = int(a), 1
            else:
                raise TypeError("IntPair takes int or IntPair, not %s" % type(a).__name__)
            return self
        if type(a) is int and type(b) is int:
            n, d = a, b
        elif isinstance(a, (int, IntPair)) and isinstance(b, (int, IntPair)):
            an, ad = (a._n, a._d) if isinstance(a, IntPair) else (int(a), 1)
            bn, bd = (b._n, b._d) if isinstance(b, IntPair) else (int(b), 1)
            n, d = an * bd, bn * ad
        else:
            raise TypeError("IntPair takes int or IntPair, not %s and %s" % (type(a).__name__, type(b).__name__))
        if d == 0:
            raise ZeroDivisionError("IntPair(%d, 0)" % n)
        g = gcd(n, d)
        if d < 0:
            g = -g
        self._n, self._d = n // g, d // g
        return self

    numerator = property(lambda self: self._n)
    denominator = property(lambda self: self._d)

    def is_integer(self):
        return self._d == 1

    def as_integer_ratio(self):
        return (self._n, self._d)

    def limit_denominator(self, max_denominator=1000000):
        """The closest pair with denominator at most max_denominator, by the continued fraction, as CPython does it."""
        if not isinstance(max_denominator, (int, IntPair)):
            raise TypeError("limit_denominator takes int or IntPair, not %s" % type(max_denominator).__name__)
        if max_denominator < 1:
            raise ValueError("max_denominator should be at least 1")
        if self._d <= max_denominator:
            return _make(self._n, self._d)
        p0, q0, p1, q1 = 0, 1, 1, 0
        n, d = self._n, self._d
        while True:
            a = n // d
            q2 = q0 + a * q1
            if q2 > max_denominator:
                break
            p0, q0, p1, q1 = p1, q1, p0 + a * p1, q2
            n, d = d, n - a * d
        k = (max_denominator - q0) // q1
        if 2 * d * (q0 + k * q1) <= self._d:
            return _make(p1, q1)
        return _make(p0 + k * p1, q0 + k * q1)

    def __repr__(self):
        return "IntPair(%d, %d)" % (self._n, self._d)

    def __str__(self):
        return str(self._n) if self._d == 1 else "%d/%d" % (self._n, self._d)

    def __add__(self, other):
        if type(other) is IntPair:
            na, da, nb, db = self._n, self._d, other._n, other._d
            g = gcd(da, db)
            if g == 1:
                return _make(na * db + da * nb, da * db)
            s = da // g
            t = na * (db // g) + nb * s
            g2 = gcd(t, g)
            if g2 == 1:
                return _make(t, s * db)
            return _make(t // g2, s * (db // g2))
        if isinstance(other, int):
            return _make(self._n + other * self._d, self._d)
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if type(other) is IntPair:
            na, da, nb, db = self._n, self._d, other._n, other._d
            g = gcd(da, db)
            if g == 1:
                return _make(na * db - da * nb, da * db)
            s = da // g
            t = na * (db // g) - nb * s
            g2 = gcd(t, g)
            if g2 == 1:
                return _make(t, s * db)
            return _make(t // g2, s * (db // g2))
        if isinstance(other, int):
            return _make(self._n - other * self._d, self._d)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, int):
            return _make(other * self._d - self._n, self._d)
        return NotImplemented

    def __mul__(self, other):
        if type(other) is IntPair:
            na, da, nb, db = self._n, self._d, other._n, other._d
            g1 = gcd(na, db)
            if g1 > 1:
                na //= g1
                db //= g1
            g2 = gcd(nb, da)
            if g2 > 1:
                nb //= g2
                da //= g2
            return _make(na * nb, da * db)
        if isinstance(other, int):
            g = gcd(other, self._d)
            return _make(self._n * (other // g), self._d // g)
        return NotImplemented

    __rmul__ = __mul__

    def _div(self, other):
        nb, db = other._n, other._d
        if nb == 0:
            raise ZeroDivisionError("IntPair(%d, 0)" % db)
        na, da = self._n, self._d
        g1 = gcd(na, nb)
        if g1 > 1:
            na //= g1
            nb //= g1
        g2 = gcd(db, da)
        if g2 > 1:
            da //= g2
            db //= g2
        n, d = na * db, nb * da
        if d < 0:
            n, d = -n, -d
        return _make(n, d)

    def __truediv__(self, other):
        if isinstance(other, (int, IntPair)):
            return self._div(IntPair(other))
        return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, int):
            return IntPair(other)._div(self)
        return NotImplemented

    def __floordiv__(self, other):
        if isinstance(other, (int, IntPair)):
            o = IntPair(other)
            return (self._n * o._d) // (self._d * o._n)
        return NotImplemented

    def __rfloordiv__(self, other):
        if isinstance(other, int):
            return (other * self._d) // self._n
        return NotImplemented

    def __mod__(self, other):
        if isinstance(other, (int, IntPair)):
            o = IntPair(other)
            return IntPair((self._n * o._d) % (o._n * self._d), self._d * o._d)
        return NotImplemented

    def __rmod__(self, other):
        if isinstance(other, int):
            return IntPair((other * self._d) % self._n, self._d)
        return NotImplemented

    def __divmod__(self, other):
        if isinstance(other, (int, IntPair)):
            o = IntPair(other)
            q, r = divmod(self._n * o._d, self._d * o._n)
            return q, IntPair(r, self._d * o._d)
        return NotImplemented

    def __rdivmod__(self, other):
        if isinstance(other, int):
            q, r = divmod(other * self._d, self._n)
            return q, IntPair(r, self._d)
        return NotImplemented

    def __pow__(self, exponent, modulo=None):
        if modulo is not None:
            return NotImplemented
        if isinstance(exponent, IntPair):
            if exponent._d != 1:
                raise TypeError("a power with a non-integer exponent has no exact pair in general")
            exponent = exponent._n
        elif not isinstance(exponent, int):
            _refuse_other_numbers(exponent)
            return NotImplemented
        if exponent >= 0:
            return _make(self._n ** exponent, self._d ** exponent)
        power = -exponent
        if self._n > 0:
            return _make(self._d ** power, self._n ** power)
        if self._n == 0:
            raise ZeroDivisionError("IntPair(%d, 0)" % self._d ** power)
        return _make((-self._d) ** power, (-self._n) ** power)

    def __rpow__(self, base, modulo=None):
        if modulo is not None or not isinstance(base, int):
            return NotImplemented
        if self._d != 1:
            raise TypeError("a power with a non-integer exponent has no exact pair in general")
        if self._n >= 0:
            return base ** self._n
        return IntPair(base) ** self._n

    def __pos__(self):
        return _make(self._n, self._d)

    def __neg__(self):
        return _make(-self._n, self._d)

    def __abs__(self):
        return _make(abs(self._n), self._d)

    def __int__(self):
        return -(-self._n // self._d) if self._n < 0 else self._n // self._d

    __trunc__ = __int__

    def __floor__(self):
        return self._n // self._d

    def __ceil__(self):
        return -(-self._n // self._d)

    def __round__(self, ndigits=None):
        """Half toward even, as CPython does it."""
        if ndigits is None:
            d = self._d
            whole, rest = divmod(self._n, d)
            if rest * 2 < d:
                return whole
            if rest * 2 > d:
                return whole + 1
            return whole if whole % 2 == 0 else whole + 1
        if not isinstance(ndigits, (int, IntPair)):
            raise TypeError("round takes int or IntPair digits, not %s" % type(ndigits).__name__)
        shift = 10 ** abs(ndigits)
        if ndigits > 0:
            return IntPair(round(self * shift), shift)
        return IntPair(round(self._div(IntPair(shift))) * shift)

    def __hash__(self):
        try:
            inverse = pow(self._d, -1, HASH_MODULUS)
        except ValueError:
            value = HASH_INF
        else:
            value = hash(hash(abs(self._n)) * inverse)
        result = value if self._n >= 0 else -value
        return -2 if result == -1 else result

    def __eq__(self, other):
        if type(other) is IntPair:
            return self._n == other._n and self._d == other._d
        if isinstance(other, int):
            return self._n == other and self._d == 1
        _refuse_other_numbers(other)
        return NotImplemented

    def __lt__(self, other):
        if type(other) is IntPair:
            return self._n * other._d < self._d * other._n
        if isinstance(other, int):
            return self._n < self._d * other
        return NotImplemented

    def __le__(self, other):
        if type(other) is IntPair:
            return self._n * other._d <= self._d * other._n
        if isinstance(other, int):
            return self._n <= self._d * other
        return NotImplemented

    def __gt__(self, other):
        if type(other) is IntPair:
            return self._n * other._d > self._d * other._n
        if isinstance(other, int):
            return self._n > self._d * other
        return NotImplemented

    def __ge__(self, other):
        if type(other) is IntPair:
            return self._n * other._d >= self._d * other._n
        if isinstance(other, int):
            return self._n >= self._d * other
        return NotImplemented

    def __bool__(self):
        return self._n != 0

    def __format__(self, spec):
        if spec:
            raise TypeError("a format spec prints an IntPair through floating point; use str or the numerator and denominator")
        return str(self)

    def __reduce__(self):
        return (IntPair, (self._n, self._d))

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self


def qdiv(a, b):
    """a over b, exact. a and b are each int or IntPair, and the answer is always an IntPair."""
    if not isinstance(a, (int, IntPair)) or not isinstance(b, (int, IntPair)):
        raise TypeError("qdiv takes int or IntPair, not %s and %s" % (type(a).__name__, type(b).__name__))
    return IntPair(a)._div(IntPair(b))
