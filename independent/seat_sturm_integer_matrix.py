#!/usr/bin/env python3
"""Export independently reconstructed finite S3 operator to integer-only Sturm verifier.

Uses the previously published and CI-confirmed other-seat permutation-group
construction, not the Stage 2H / 2I Cholesky code. This is a non-JSON
whitespace matrix exchange format, NOT an HBP/HBI receipt.
"""
import contextlib
import io
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):
    model = runpy.run_path(str(HERE / "seat_yang_mills_audit.py"))
n = len(model["keys"])
assert n == 1393 and len(model["rowmaps"]) == n
rows, weights, mag = model["rowmaps"], model["weights"], model["mag"]
assert sum(weights) == 7776
assert sum(len(row) for row in rows) == 32385

# Exact Gauss-weighted symmetry is necessary for the integer Sylvester test.
for i, row in enumerate(rows):
    assert sum(row.values()) == 0
    for j, v in row.items():
        assert weights[i] * v == weights[j] * rows[j].get(i, 0)

out = sys.stdout
out.write(f"{n}\n")
out.write(" ".join(map(str, weights)) + "\n")
out.write(" ".join(map(str, mag)) + "\n")
for i, row in enumerate(rows):
    for j, v in sorted(row.items()):
        if j >= i:
            out.write(f"{i} {j} {v}\n")
