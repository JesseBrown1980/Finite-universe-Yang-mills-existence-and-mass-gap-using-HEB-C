#!/usr/bin/env python3
"""
HEB-C integer-only rule: verification code uses integer arithmetic only.

Parses each given Python file and fails if it contains a float literal, true
division (/), a float format spec, float(), Decimal, Fraction, an import of
fractions or decimal under any name, or wall-clock float timing (time.time,
time.perf_counter). Integer floor division (//) and integer formatting are
allowed.

usage: integer_only_audit.py FILE.py...
       integer_only_audit.py --selftest    Runs the snippets below. Exits 1 if one is misread.
"""
import ast
import sys

BANNED_NAMES = {"float", "Decimal", "Fraction"}
BANNED_ATTRS = {"Decimal", "Fraction", "perf_counter"}
BANNED_MODULES = {"fractions", "decimal"}
FLOAT_FORMATS = ("%f", "%.", "%e", "%g", ":.", ":f", ":e", ":g")


def audit_text(text, path):
    hits = []
    for n in ast.walk(ast.parse(text, path)):
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
        elif isinstance(n, ast.ImportFrom) and (n.module or "").split(".")[0] in BANNED_MODULES:
            hits.append((n.lineno, "from " + n.module + " import"))
        elif isinstance(n, ast.Import):
            hits += [(n.lineno, "import " + a.name) for a in n.names if a.name.split(".")[0] in BANNED_MODULES]
    return sorted(set(hits))


def audit(path):
    return audit_text(open(path).read(), path)


MUST_HIT = (
    "x = 0.5\n", "x = 1 / 2\n", "a /= b\n", "x = float(1)\n",
    "from fractions import Fraction as F\n", "from fractions import Fraction\n", "from fractions import *\n", "from decimal import Decimal as D\n",
    "import fractions\n", "import fractions as f\n", "import decimal as d\n", "def f():\n    from fractions import Fraction as G\n    return G(1, 2)\n",
)
MUST_PASS = (
    "x = a // b\n", "from intpair import IntPair as F, qdiv\nx = qdiv(F(1, 2), 3)\n", "import os, sys\n", "# from fractions import Fraction as F\nx = 1\n",
    "s = 'from fractions import Fraction as F'\n", "from .fractionsish import y\n",
)


def selftest():
    failed = 0
    for text in MUST_HIT:
        if not audit_text(text, "snippet"):
            failed += 1
            print("INTEGER_AUDIT_SELFTEST|missed=%r|json=0" % text)
    for text in MUST_PASS:
        hits = audit_text(text, "snippet")
        if hits:
            failed += 1
            print("INTEGER_AUDIT_SELFTEST|flagged=%r|first=%s|json=0" % (text, hits[0][1]))
    print("INTEGER_AUDIT_SELFTEST_DONE|must_hit=%d|must_pass=%d|failed=%d|json=0" % (len(MUST_HIT), len(MUST_PASS), failed))
    return 1 if failed else 0


def main():
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    bad = 0
    for path in sys.argv[1:]:
        hits = audit(path)
        bad += len(hits)
        print("INTEGER-AUDIT|file=%s|violations=%d|%s|json=0"
              % (path, len(hits), ",".join("L%d:%s" % h for h in hits).replace("|", "/") or "clean"))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
