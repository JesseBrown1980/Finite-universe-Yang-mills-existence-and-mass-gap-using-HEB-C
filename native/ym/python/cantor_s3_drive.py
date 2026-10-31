#!/usr/bin/env python3
"""Reproducible finite-S3 Cantor response (numerical test, NOT a mass-gap proof).

Input is the integer upper-triangle sector format emitted by native/ym ymsec.
That sector is already Gauss-invariant; this module does not certify its origin.
Uses M, the existing magnetic plaquette sum, as gauge-invariant drive W.
"""
from __future__ import annotations

import argparse
import hashlib
import math
from pathlib import Path

import numpy as np

SIGNAL_SHA256 = '1f48fa5083237cd4bdadc3f6c4f9094b864ca1386d7d09b5b27c19b5f27f6913'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cantor_signal() -> bytes:
    out = bytearray()
    for index in range(3**6):
        n, twos = index, 0
        for _ in range(6):
            digit, n = n % 3, n // 3
            if digit == 1:
                out.append(0)
                break
            twos += digit // 2
        else:
            out.append(1 if twos % 2 == 0 else 2)
    result = bytes(out)
    if sha256(result) != SIGNAL_SHA256 or [result.count(i) for i in range(3)] != [665, 32, 32]:
        raise ValueError('Cantor source verification failed')
    return result


def load_matrix(path: Path, max_states: int = 4096) -> tuple[np.ndarray, np.ndarray, str]:
    raw = path.read_bytes()
    try:
        tokens = list(map(int, raw.decode('ascii').split()))
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError('Matrix must contain ASCII integers only') from exc
    if not tokens:
        raise ValueError('Empty sector matrix')
    n = tokens[0]
    if not 1 <= n <= max_states or len(tokens) < 1 + 2*n or (len(tokens)-1-2*n) % 3:
        raise ValueError('Invalid sector dimension or matrix layout')
    weights, magnetic = tokens[1:1+n], tokens[1+n:1+2*n]
    if any(w <= 0 for w in weights):
        raise ValueError('Orbit weights must be positive')
    electric = np.zeros((n, n), dtype=np.float64)
    seen = set()
    for i, j, z in zip(*[iter(tokens[1+2*n:])]*3):
        if not 0 <= i <= j < n or (i, j) in seen:
            raise ValueError('Matrix needs unique upper-triangle entries')
        seen.add((i, j))
        if i != j and (weights[i] * z) % weights[j] != 0:
            raise ValueError('Invalid weighted reverse electric entry')
        value = float(z) * math.sqrt(weights[i] / weights[j])
        electric[i, j] = value
        electric[j, i] = value
    if not np.all(np.isfinite(electric)):
        raise ValueError('Non-finite electric entries')
    return electric, np.asarray(magnetic, dtype=np.float64), sha256(raw)


def propagators(electric: np.ndarray, magnetic: np.ndarray, r: float,
                coupling: float, dt: float) -> dict[int, np.ndarray]:
    if not all(map(math.isfinite, (r, coupling, dt))) or dt <= 0:
        raise ValueError('Invalid coupling or step')
    h0 = electric + np.diag(r * magnetic)
    out = {}
    for pulse in (0, 1, -1):
        h = h0 + np.diag((coupling * pulse) * magnetic)
        values, vectors = np.linalg.eigh(h)
        u = (vectors * np.exp(-1j * dt * values)) @ vectors.T
        out[pulse] = u
    return out


def replay(sequence: list[int], unitaries: dict[int, np.ndarray], basis: int,
           reverse: bool = True) -> tuple[np.ndarray, float, float]:
    n = next(iter(unitaries.values())).shape[0]
    if not 0 <= basis < n:
        raise ValueError('Initial basis index out of range')
    state = np.zeros(n, dtype=np.complex128)
    state[basis] = 1
    initial = state.copy()
    max_norm_error = 0.0
    for s in sequence:
        state = unitaries[s] @ state
        max_norm_error = max(max_norm_error, abs(float(np.vdot(state, state).real) - 1.0))
    terminal = state.copy()
    inverse_error = float('nan')
    if reverse:
        for s in reversed(sequence):
            state = unitaries[s].conj().T @ state
        inverse_error = float(np.max(np.abs(state - initial)))
    return terminal, max_norm_error, inverse_error


def run(matrix: Path, basis: int = 0, r: float = 9., coupling: float = 1/27,
        dt: float = 1/27, tolerance: float = 1e-8,
        expected_matrix_sha: str | None = None) -> tuple[str, str]:
    if not math.isfinite(tolerance) or tolerance <= 0:
        raise ValueError('Tolerance must be positive')
    electric, magnetic, matrix_hash = load_matrix(matrix)
    if expected_matrix_sha is not None and matrix_hash != expected_matrix_sha:
        raise ValueError('Sector matrix digest mismatch')
    signal = cantor_signal()
    seq = [{0: 0, 1: 1, 2: -1}[s] for s in signal]
    u = propagators(electric, magnetic, r, coupling, dt)
    n = len(magnetic)
    eye = np.eye(n)
    unitarity = max(float(np.max(np.abs(x.conj().T @ x - eye))) for x in u.values())
    sequences = {
        'cantor': seq,
        'zero': [0]*len(seq),
        'inverted': [-s for s in seq],
        'rotated_one': seq[1:] + seq[:1],
    }
    outputs = {}
    for name, pulses in sequences.items():
        psi, norm_error, inverse_error = replay(pulses, u, basis)
        outputs[name] = (psi, norm_error, inverse_error)
    def fmt(x: float) -> str:
        return f'{x:.12g}'
    lines = [
        'CANTOR_S3|schema=CANTOR-S3-NUMERICAL-V1|model=S3|method=dense_hermitian_eigh|kind=NUMERICAL_TEST_NOT_CERTIFICATE|json=0',
        f'INPUT|matrix_sha256={matrix_hash}|signal_sha256={SIGNAL_SHA256}|states={n}|basis_index={basis}|samples=729|positive=32|negative=32|zero=665|json=0',
        f'PARAM|JE=1|JB_over_JE={fmt(r)}|lambda={fmt(coupling)}|dt={fmt(dt)}|hbar=1|drive=M|sign=2_to_minus_1|json=0',
        f'CHECK|weighted_hermitian=PASS|unitarity_max={fmt(unitarity)}|tol={fmt(tolerance)}|json=0',
    ]
    for name, (psi, norm, inverse) in outputs.items():
        w_exp = float(np.vdot(psi, magnetic * psi).real)
        ret = float(abs(psi[basis]) ** 2)
        lines.append(f'RUN|control={name}|norm_max={fmt(norm)}|inverse_max={fmt(inverse)}|magnetic_expectation={fmt(w_exp)}|return_probability={fmt(ret)}|json=0')
    fidelity = float(abs(np.vdot(outputs['cantor'][0], outputs['zero'][0]))**2)
    lines.append(f'COMPARE|driven_vs_zero_fidelity={fmt(fidelity)}|json=0')
    passed = (unitarity <= tolerance and all(
        err <= tolerance and inv <= tolerance
        for _, err, inv in outputs.values()))
    lines.append(f'VERDICT|result={"PASS" if passed else "FAIL"}|scope=finite_sector_numerical_evolution|mass_gap_certified=0|hidden_model_state=0|json=0')
    hbp = ('\n'.join(lines) + '\n').encode('utf-8')
    running = '0' * 64
    index_lines = []
    offset = 0
    for k, line in enumerate(hbp.splitlines(keepends=True)):
        digest = sha256(line)
        running = sha256((running + digest).encode('ascii'))
        index_lines.append(f'HBI|line={k}|offset={offset}|bytes={len(line)}|sha256={digest}|chain={running}|json=0')
        offset += len(line)
    hbi = ('\n'.join(index_lines) + '\n').encode('utf-8')
    return hbp.decode(), hbi.decode()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--matrix', required=True, type=Path, help='ymsec sector matrix (n, weights, magnetic, upper triples)')
    ap.add_argument('--out', required=True, type=Path, help='output prefix for .hbp and .hbi')
    ap.add_argument('--basis', type=int, default=0)
    ap.add_argument('--r', type=float, default=9.0)
    ap.add_argument('--coupling', type=float, default=1/27)
    ap.add_argument('--dt', type=float, default=1/27)
    ap.add_argument('--tol', type=float, default=1e-8)
    ap.add_argument('--expected-matrix-sha', help='reject matrix if SHA-256 differs')
    args = ap.parse_args()
    hbp, hbi = run(args.matrix, args.basis, args.r, args.coupling, args.dt, args.tol, args.expected_matrix_sha)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.with_suffix('.hbp').write_text(hbp, encoding='utf-8')
    args.out.with_suffix('.hbi').write_text(hbi, encoding='utf-8')
    print(hbp, end='')
    if 'VERDICT|result=FAIL|' in hbp:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
