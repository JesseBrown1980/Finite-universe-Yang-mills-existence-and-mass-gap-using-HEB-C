"""Exact reduced signed integer pairs; all numeric state is Python int.

No fractions.Fraction, Decimal, float, IEEE operations, or rounding.
Division returns another integer (numerator, denominator) pair.
"""
from functools import total_ordering
from math import gcd


@total_ordering
class IntegerRatio:
    __slots__ = ("num", "den")

    def __init__(self, num: int, den: int = 1) -> None:
        if type(num) is not int or type(den) is not int:
            raise TypeError("both numerator and denominator must be exact integers")
        if den == 0:
            raise ZeroDivisionError("zero denominator")
        if den < 0:
            num, den = -num, -den
        common = gcd(num, den)
        self.num, self.den = num // common, den // common

    @staticmethod
    def coerce(other):
        if isinstance(other, IntegerRatio):
            return other
        if type(other) is int:
            return IntegerRatio(other)
        return NotImplemented

    def __add__(self, other):
        rhs = self.coerce(other)
        if rhs is NotImplemented:
            return NotImplemented
        return IntegerRatio(self.num * rhs.den + rhs.num * self.den,
                            self.den * rhs.den)
    __radd__ = __add__

    def __neg__(self):
        return IntegerRatio(-self.num, self.den)

    def __sub__(self, other):
        rhs = self.coerce(other)
        return NotImplemented if rhs is NotImplemented else self + (-rhs)

    def __rsub__(self, other):
        lhs = self.coerce(other)
        return NotImplemented if lhs is NotImplemented else lhs - self

    def __mul__(self, other):
        rhs = self.coerce(other)
        if rhs is NotImplemented:
            return NotImplemented
        return IntegerRatio(self.num * rhs.num, self.den * rhs.den)
    __rmul__ = __mul__

    def __truediv__(self, other):
        rhs = self.coerce(other)
        if rhs is NotImplemented:
            return NotImplemented
        if rhs.num == 0:
            raise ZeroDivisionError("division by zero integer numerator")
        return IntegerRatio(self.num * rhs.den, self.den * rhs.num)

    def __rtruediv__(self, other):
        lhs = self.coerce(other)
        return NotImplemented if lhs is NotImplemented else lhs / self

    def __pow__(self, exponent):
        if type(exponent) is not int:
            return NotImplemented
        if exponent >= 0:
            return IntegerRatio(self.num ** exponent, self.den ** exponent)
        if self.num == 0:
            raise ZeroDivisionError("negative power of zero")
        return IntegerRatio(self.den ** (-exponent), self.num ** (-exponent))

    def __eq__(self, other):
        rhs = self.coerce(other)
        if rhs is NotImplemented:
            return NotImplemented
        return self.num == rhs.num and self.den == rhs.den

    def __lt__(self, other):
        rhs = self.coerce(other)
        if rhs is NotImplemented:
            return NotImplemented
        return self.num * rhs.den < rhs.num * self.den

    def __str__(self):
        return str(self.num) if self.den == 1 else f"{self.num}/{self.den}"

    def __repr__(self):
        return f"IntegerRatio({self.num}, {self.den})"

    def __hash__(self):
        return hash((self.num, self.den))


def selftest():
    R = IntegerRatio
    assert str(R(12, -18)) == "-2/3"
    assert R(1, 3) + R(1, 6) == R(1, 2)
    assert R(7, 3) - R(2, 3) == R(5, 3)
    assert 1 - R(1, 7) == R(6, 7)
    assert R(1, 5) * R(15, 2) == R(3, 2)
    assert 3 * R(1, 7) == R(3, 7)
    assert R(3, 4) / R(9, 2) == R(1, 6)
    assert 1 / R(3, 4) == R(4, 3)
    assert R(2, 3) ** 3 == R(8, 27)
    assert R(2, 3) ** -1 == R(3, 2)
    assert R(-1, 3) < 0 < R(1, 3)
    assert min(R(2, 3), R(1, 2)) == R(1, 2)
    assert sum((R(1, 2), R(1, 3))) == R(5, 6)
    assert type((R(1, 3)/2).num) is int
    for invalid in (1.0, '1', None):
        try:
            R(invalid)
        except TypeError:
            pass
        else:
            raise AssertionError("non-integer accepted")
    return True


if __name__ == "__main__":
    assert selftest()
    print("HEBC-INTEGER-RATIO|result=PASS|numeric_runtime=int_only|float=0|json=0")
