#!/usr/bin/env python3
"""
HEB-C integer-only rule: verification code uses integer arithmetic only.

Parses each given Python file and fails if it contains a float literal, true
division (/), a float format spec, float(), Decimal, Fraction, or wall-clock
float timing (time.time, time.perf_counter). Integer floor division (//) and
integer formatting are allowed.

usage: integer_only_audit.py FILE.py...
"""
import ast
import sys

BANNED_NAMES = {"float", "Decimal", "Fraction"}
BANNED_ATTRS = {"Decimal", "Fraction", "perf_counter"}
FLOAT_FORMATS = ("%f", "%.", "%e", "%g", ":.", ":f", ":e", ":g")


def audit(path):
    hits = []
    for n in ast.walk(ast.parse(open(path).read(), path)):
        if isinstance(n, ast.Constant) and isinstance(n.value, float):
            hits.append((n.lineno, "float literal"))
        elif isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
            hits.append((n.lineno, "true division /"))
        elif isinstance(n, ast.AugAssign) and isinstance(n.op, ast.Div):
            hits.append((n.lineno, "true division /="))
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and any(f in n.value for f in FLOAT_FORMATS):
            hits.append((n.lineno, "float format"))
        elif isinstance(n, ast.Name) and n.id in BANNED_NAMES:
            hits.append((n.lineno, n.id))
        elif isinstance(n, ast.Attribute) and (n.attr in BANNED_ATTRS or (n.attr == "time" and isinstance(n.value, ast.Name) and n.value.id == "time")):
            hits.append((n.lineno, "." + n.attr))
    return sorted(set(hits))


def main():
    bad = 0
    for path in sys.argv[1:]:
        hits = audit(path)
        bad += len(hits)
        print("INTEGER-AUDIT|file=%s|violations=%d|%s|json=0"
              % (path, len(hits), ",".join("L%d:%s" % h for h in hits).replace("|", "/") or "clean"))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
