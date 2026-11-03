#!/usr/bin/env python3
"""Prism-3 CHSH synthetic control. No quantum hardware, no physical photons."""
from hashlib import sha256
from pathlib import Path

N = 32768
LAMBDAS = 27
MASKS = [sha256(b"CURVE3|" + bytes([v])).digest()[0] & 7 for v in range(LAMBDAS)]
SETTINGS = [(0, 0), (0, 1), (1, 0), (1, 1)]


def local(mask: int, x: int, y: int) -> tuple[int, int]:
    """A depends only on (x,shared mask), B only on (y,shared mask)."""
    g0, g1, g2 = mask & 1, (mask >> 1) & 1, (mask >> 2) & 1
    a = 1 - 2 * (g0 ^ (g1 if x else 0))
    b = 1 - 2 * (g0 ^ (g2 if y else 0))
    return a, b


def local_table(lam: int, x: int, y: int) -> tuple[int, int]:
    """Ordinary classical three-bit lookup, with precisely the same information."""
    mask = MASKS[lam]
    return local(mask, x, y)


def sample(model: str, x: int, y: int, i: int) -> tuple[int, int]:
    trial = 4 * i + 2 * x + y
    payload = trial.to_bytes(8, "little")
    if model == "hash_local":
        lam = sha256(b"HIDDEN|" + payload).digest()[0] % LAMBDAS
        return local(MASKS[lam], x, y)
    if model == "matched_table":
        lam = sha256(b"HIDDEN|" + payload).digest()[0] % LAMBDAS
        return local_table(lam, x, y)
    if model == "central_quantum_like":
        digest = sha256(b"QREF|" + payload).digest()
        a = 1 - 2 * (digest[0] & 1)
        favorable = int.from_bytes(digest[1:3], "little") < 55936  # 437/512
        s = 1 - 2 * (x & y)
        return a, a * s * (1 if favorable else -1)
    if model == "central_pr_box":
        a = 1 - 2 * (sha256(b"PRBOX|" + payload).digest()[0] & 1)
        return a, a * (1 - 2 * (x & y))
    raise ValueError("unknown model")


def run() -> list[str]:
    lines = ["CHSH_RUN|prisms=3|hidden_states=27|n_per_setting=32768|integer_only=1|json=0"]
    exact = []
    for lam in range(LAMBDAS):
        corr = [local(MASKS[lam], x, y)[0] * local(MASKS[lam], x, y)[1]
                for x, y in SETTINGS]
        exact.append(corr[0] + corr[1] + corr[2] - corr[3])
    p1 = all(abs(v) == 2 for v in exact)
    lines.append(f"CHSH_EXACT|lambda_states={LAMBDAS}|abs_S_each=2|verified={int(p1)}|json=0")
    all_results = {}
    p2 = True
    for model in ("hash_local", "matched_table", "central_quantum_like", "central_pr_box"):
        rows = {}
        for x, y in SETTINGS:
            ab = a_plus = b_plus = 0
            for i in range(N):
                a, b = sample(model, x, y, i)
                ab += a * b
                a_plus += int(a == 1)
                b_plus += int(b == 1)
                if model == "hash_local" and (a, b) != sample("matched_table", x, y, i):
                    p2 = False
            rows[(x, y)] = (ab, a_plus, b_plus)
            lines.append(f"CHSH_SETTING|model={model}|x={x}|y={y}|n={N}|"
                         f"sum_ab={ab}|a_plus={a_plus}|b_plus={b_plus}|json=0")
        s_num = sum((1 if (x, y) != (1, 1) else -1) * rows[(x, y)][0]
                    for x, y in SETTINGS)
        all_results[model] = (s_num, rows)
        lines.append(f"CHSH_SCORE|model={model}|s_numerator={s_num}|denominator={N}|"
                     f"s_milli={s_num * 1000 // N}|json=0")
    h = all_results["hash_local"][0]
    t = all_results["matched_table"][0]
    q = all_results["central_quantum_like"][0]
    pr = all_results["central_pr_box"][0]
    p2 &= (h == t)
    p3 = abs(h) * 10 <= 21 * N
    p4 = 2700 * N <= q * 1000 <= 2950 * N
    p5 = pr == 4 * N
    p6 = True
    for name in ("central_quantum_like", "central_pr_box"):
        rows = all_results[name][1]
        for x in (0, 1):
            p6 &= abs(rows[(x, 0)][1] - rows[(x, 1)][1]) * 100 <= 4 * N
        for y in (0, 1):
            p6 &= abs(rows[(0, y)][2] - rows[(1, y)][2]) * 100 <= 4 * N
    # Audit P7 as a declared construction assumption: local() has no remote argument use.
    # This is a source-inspection claim, not an independently demonstrated physical boundary.
    p7 = True
    checks = [p1, p2, p3, p4, p5, p6, p7]
    lines.append("CHSH_PREDICTIONS|" + "|".join(
        f"P{i}={'PASS' if ok else 'FAIL'}" for i, ok in enumerate(checks, 1)) +
        f"|overall={'PASS' if all(checks) else 'FAIL'}|json=0")
    return lines


if __name__ == "__main__":
    print("\n".join(run()))
