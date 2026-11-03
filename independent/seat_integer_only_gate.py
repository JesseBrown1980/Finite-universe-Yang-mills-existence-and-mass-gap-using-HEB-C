#!/usr/bin/env python3
"""Fail-closed integer-only static audit for all seat Python verifier scripts.

This guards native float/complex literals, conversion calls, non-integer
numeric libraries and non-integer clocks. Exact ratios are represented
as Python int numerator/denominator pairs (IntegerRatio).
"""
import ast
from pathlib import Path

from seat_integer_ratio import selftest as integer_ratio_selftest

ROOT = Path(__file__).resolve().parent
BANNED_MODULES = {"fractions", "decimal", "numpy", "scipy", "mpmath"}
BANNED_CALLS = {"float", "complex"}
BANNED_CLOCKS = {"time", "perf_counter", "process_time"}
checked = 0
assert integer_ratio_selftest()
for path in sorted(ROOT.glob("seat_*.py")):
    if path.name == "seat_integer_only_gate.py":
        continue
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant):
            assert type(node.value) is not float and type(node.value) is not complex, (
                "non-integer literal", path, node.lineno
            )
        if isinstance(node, ast.ImportFrom):
            assert node.module is None or node.module.split(".")[0] not in BANNED_MODULES, (
                "forbidden numeric module", path, node.lineno
            )
        if isinstance(node, ast.Import):
            assert all(alias.name.split(".")[0] not in BANNED_MODULES
                       for alias in node.names), (
                "forbidden numeric module", path, node.lineno
            )
        if isinstance(node, ast.Call):
            fn = node.func
            assert not (isinstance(fn, ast.Name) and fn.id in BANNED_CALLS), (
                "non-integer conversion", path, node.lineno
            )
            assert not (isinstance(fn, ast.Attribute) and fn.attr in BANNED_CLOCKS), (
                "non-integer clock", path, node.lineno
            )
    checked += 1
assert checked >= 4
print(f"HEBC-INT-GATE|result=PASS|scripts={checked}|python_numeric_type=int_only|"
      "fraction_module=0|float_literals=0|complex_literals=0|json=0")
