# Third-seat Sturm inertia reproduction (non-author of PRs #7–#9)

The finite S₃ 2×2-torus E₁ lower bounds from PR #9, reproduced by a separate
verifier that shares no code with `seat_sturm_biginterval.cpp`, uses no GMP,
and was run outside GitHub's runners.

| run | threshold t | pivots | negative | ambiguous | result |
|---|---|---|---|---|---|
| JE=1, JB=1 | 13.240 | 1393/1393 | 1 | 0 | E₁ > 13.240 certified |
| JE=3, JB=5 | 50.840 | 1393/1393 | 1 | 0 | E₁ > 50.840 certified |
| control JE=1, JB=1 | 7.000 (below E₀) | 1393/1393 | 0 | 0 | correctly not 1 |
| control JE=1, JB=1 | 13.300 (above E₂) | 1393/1393 | 3 | 0 | correctly not 1 |

`negative=1` with zero ambiguous pivots means exactly one eigenvalue of H lies
below t, so E₀ < t < E₁. The controls show the verifier counts 0 and 3 when
that is the truth. Each run took 140–155 s on two cores.

## What is independent, and what is shared

- **Independent:** the implementation (Python arbitrary-precision integers, not
  GMP), the precision (scale 10⁸⁰, not 10¹⁰⁰), the pivot rule (smallest row
  degree, ties broken by narrowest interval), the author, and the machine.
- **Shared:** the input matrix. It comes from `independent/seat_sturm_integer_matrix.py`
  (PR #8), which builds on PR #7's operator. Regenerated file sha256:
  `137285e0a1b55bdf0c8c56bec6bd69e0ab9138e6e7c05350d677f186e1981d2c`. That operator's
  sha `b6c608f5…` matches the native one, but anything wrong upstream of it
  would be shared by every verifier that reads this file.

## Method

B = W(1000·H − t·I) with W the positive diagonal orbit weights. Because H is
W-self-adjoint, S = W^½HW^−½ is symmetric and B = W^½(1000·S − t·I)W^½, so B is
congruent to 1000·S − t·I and has the inertia of H − (t/1000)·I. Symmetric elimination uses only pivots whose interval excludes
zero, in any symmetric order (Haynsworth inertia additivity). Every Schur update
x·y/d is enclosed outward: corner products, extreme denominator per sign case,
floor below, ceiling above. An exhaustive self-test on small intervals runs
before every certificate.

## Reproduce

```bash
python3 independent/seat_sturm_integer_matrix.py > m.txt
sha256sum m.txt   # 137285e0…
for args in "1 1 13240" "3 5 50840" "1 1 7000" "1 1 13300"; do
  python3 -I independent/third_seat/sturm_py.py m.txt $args 80 2>/dev/null
done | grep '^STURM-PY' | sed 's/|elapsed_s=[0-9]*//' > out.measure
sed 's/|elapsed_s=[0-9]*//' independent/third_seat/third_seat_sturm.measure | cmp - out.measure
```

`elapsed_s` is wall time and varies by machine, so it is stripped before the
comparison. Every other field must match byte for byte.

Scope: two inequalities on one finite 1,393-state operator. No infinite-volume
or continuum Yang–Mills claim follows. No JSON (`json=0`).
