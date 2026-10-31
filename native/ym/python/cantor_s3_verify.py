#!/usr/bin/env python3
"""Separate SciPy matrix-exponential verifier of Cantor-driven finite S3 receipt.

Rebuilds weighted representation, triadic pulses, and 729 products without
calling the primary diagonalization driver. Finite numerical cross-check only.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

import numpy as np
from scipy.linalg import expm

EXPECTED_SIGNAL = '1f48fa5083237cd4bdadc3f6c4f9094b864ca1386d7d09b5b27c19b5f27f6913'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pulses() -> bytes:
    seq = bytes([1])
    for _ in range(6):
        flip = bytes(3-v if v else 0 for v in seq)
        seq = seq + bytes(len(seq)) + flip
    if sha(seq) != EXPECTED_SIGNAL:
        raise ValueError('Independent Cantor construction disagrees')
    return seq


def read_sector(path: Path) -> tuple[np.ndarray, np.ndarray, str]:
    data = path.read_bytes()
    a = list(map(int, data.decode('ascii').split()))
    n = a[0]
    if not 1 <= n <= 4096 or len(a) < 1+2*n or (len(a)-1-2*n) % 3:
        raise ValueError('Invalid sector matrix layout')
    weights = np.array(a[1:1+n], dtype=np.float64)
    magnetic = np.array(a[1+n:1+2*n], dtype=np.float64)
    if np.any(weights <= 0):
        raise ValueError('Nonpositive weights')
    rows = np.zeros((n,n), dtype=np.float64)
    seen = set()
    for offset in range(1+2*n, len(a), 3):
        i,j,z = a[offset:offset+3]
        if not 0 <= i <= j < n or (i,j) in seen:
            raise ValueError('Invalid or repeated triangle entry')
        seen.add((i,j))
        rows[i,j] = z
        if i != j:
            rows[j,i] = (a[1+i] * z) / a[1+j]
    scaled = weights[:,None]**0.5 * rows / weights[None,:]**0.5
    if np.max(np.abs(scaled-scaled.T)) > 1e-12:
        raise ValueError('Weighted Hermiticity failed')
    return scaled, magnetic, sha(data)


def verify(matrix: Path, receipt: Path, index: Path, tolerance: float = 1e-9) -> str:
    raw_receipt = receipt.read_bytes()
    record = {}
    for line in raw_receipt.decode('utf-8').splitlines():
        fields = line.split('|')
        record[(fields[0], next((v for v in fields[1:] if v.startswith('control=')), ''))] = dict(
            field.split('=',1) for field in fields[1:] if '=' in field)
    hbi = index.read_bytes().decode('utf-8').splitlines()
    prev = '0'*64
    lines = raw_receipt.splitlines(keepends=True)
    offset = 0
    if len(hbi) != len(lines):
        raise ValueError('HBI line count mismatch')
    for k, (raw, entry) in enumerate(zip(lines, hbi)):
        prev = sha((prev + sha(raw)).encode('ascii'))
        fields = dict(x.split('=',1) for x in entry.split('|')[1:] if '=' in x)
        if fields.get('line') != str(k) or fields.get('offset') != str(offset) or fields.get('bytes') != str(len(raw)) or fields.get('sha256') != sha(raw) or fields.get('chain') != prev:
            raise ValueError(f'HBI chain failure at line {k}')
        offset += len(raw)
    e,m,matrix_sha = read_sector(matrix)
    receipt_input = record[('INPUT','')]
    if receipt_input['matrix_sha256'] != matrix_sha or receipt_input['signal_sha256'] != EXPECTED_SIGNAL:
        raise ValueError('Input provenance mismatch')
    params = record[('PARAM','')]
    r, lam, dt = (float(params[k]) for k in ('JB_over_JE','lambda','dt'))
    basis = int(receipt_input['basis_index'])
    if basis >= len(m) or basis < 0:
        raise ValueError('Basis index invalid')
    signal = list(pulses())
    def values(shift: int = 0) -> list[int]:
        trits = signal[shift:] + signal[:shift]
        return [0 if q==0 else 1 if q==1 else -1 for q in trits]
    us = {s:expm((-1j*dt) * (e + np.diag((r+lam*s)*m))) for s in (-1,0,1)}
    def run(seq: list[int]) -> np.ndarray:
        state = np.zeros(len(m), dtype=np.complex128)
        state[basis] = 1
        for s in seq:
            state = us[s] @ state
        return state
    cases = {'cantor':values(), 'zero':[0]*729, 'inverted':[-i for i in values()], 'rotated_one':values(1)}
    out = {k:run(v) for k,v in cases.items()}
    max_diff = 0.0
    for name, state in out.items():
        expected = record[('RUN', f'control={name}')]
        mag = np.vdot(state, m*state).real
        prob = abs(state[basis])**2
        max_diff=max(max_diff, abs(mag-float(expected['magnetic_expectation'])), abs(prob-float(expected['return_probability'])))
        if abs(np.vdot(state,state).real-1) > tolerance:
            raise ValueError('Second route has norm drift')
    fidelity = abs(np.vdot(out['cantor'],out['zero']))**2
    max_diff=max(max_diff, abs(fidelity-float(record[('COMPARE','')]['driven_vs_zero_fidelity'])))
    if max_diff > tolerance:
        raise ValueError(f'Replay mismatch {max_diff:.12g} exceeds {tolerance}')
    return f'CANTOR_S3_INDEPENDENT|result=PASS|method=scipy_expm|states={len(m)}|slots=729|max_observable_delta={max_diff:.12g}|tol={tolerance}|scope=finite_numerical_crosscheck|mass_gap_certified=0|json=0'


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--matrix', required=True, type=Path)
    ap.add_argument('--receipt', required=True, type=Path)
    ap.add_argument('--index', required=True, type=Path)
    ns=ap.parse_args()
    print(verify(ns.matrix,ns.receipt,ns.index))


if __name__ == '__main__':
    main()
