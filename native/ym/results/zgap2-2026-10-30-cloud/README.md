# zgap2, cloud seat: the second-order gap coefficient (2026-10-30)

Perturbation theory in 1/r about the magnetic term, exact, for the S₃ torus Hamiltonian
H/J_E = E + r·M used by every certificate in this repository. Rust 1.81, std only, exact integer
arithmetic (exact inertia counts, integer characteristic polynomials, a std-only big integer),
clippy `-D warnings` exit 0, HBI → HBP → SHA → SH → HASH, json=0.

## Result: the gap law

E₉ − E₈ = 3r·J_E − c_L·J_E/r + O(1/r²), with

| lattice | c_L (exact, run 2) |
|---|---|
| 3×3 | **21** |
| 3×4 | **21** |
| 4×4 | **21** |
| 2×4 | 73/2 |
| 2×3 | 69/2 |
| 2×2 | 36.762472… (irrational) |

- First order adds nothing (d₁ = 0 on every lattice): the vacua and the lowest excited level, one
  plaquette carrying a 3-cycle with the other plaquettes flat (M = 3, 3 orbits per plaquette),
  have the same electric diagonal 3 × (number of links), with no first-order mixing.
- On 3×3, 3×4 and 4×4 the integer characteristic polynomial of 4(κ_top·I − R) is the same,
  x³ − 252x² + 21168x − 592704 = (x − 84)³, so c = 84/4 = 21 exactly on all three. Both energy
  shifts grow with the number of links; their difference is local and equal on every lattice of
  width 3 or more. The 2×L values differ because virtual electric flips wrap the width-2 direction.
- The vacuum second-order operator reproduces the published flat_law laws: lowest splitting
  √14 − √6 on 2×2, exactly 3 on 2×3 and 4 on 2×4, and an exactly scalar operator on 3×3.

## Registered verdicts (`PREREG.md` a1ab70c4…, `ADDENDUM.md` 76e6d98b…)

| check | result |
|---|---|
| P0 first order adds nothing | PASS |
| P1 3×4 full-space ĉ(243) in [21.095802, 21.573297] | PENDING (frozen until a 3×4 certificate exists) |
| P2 c_3×3(∞) inside the r = 243 interval [21.095802, 21.573297] | FAIL: c = 21 exactly, below the interval |
| P2b c(∞) for 2×2, 2×3, 2×4 inside their r = 243 intervals | FAIL on 2×2 (36.762472 against 36.765900); 2×3 and 2×4 inside |
| P3 c_3×4 = c_3×3 exactly (and c_4×4), 2×L different | PASS |
| P4 vacuum operator reproduces the published laws | PASS |

P2 and P2b compared the asymptotic coefficient with a finite-coupling interval; ĉ(243) also
contains the third-order term. They stay FAIL as registered. Run 1 (`RESULT.run1.hbp`) combined the
operators with a sign that differed from the registered definition; `ADDENDUM.md` records the
change, sealed before run 2.

## The certified data against c = 21 (post hoc, not registered)

From the 3×3 point certificates, ĉ(r) = r(3r − Δ/J_E) and d = (ĉ − 21)·r in exact micro-units:

| r | ĉ(r) | d |
|---|---|---|
| 9 | [27.543330, 27.552798] | [58.889970, 58.975182] |
| 27 | [22.590225, 22.626999] | [42.936075, 43.928973] |
| 81 | [21.445236, 21.547620] | [36.064116, 44.357220] |
| 243 | [21.095802, 21.573297] | [23.279886, 139.311171] |

The intervals at r = 27, 81 and 243 share d ≈ 43, so the certificates follow 21 + 43/r at strong
coupling.

## Replay and integrity chain

`run.sh` checks both seals, builds with Rust 1.81, runs clippy and checks byte identity with
`RESULT.hbp`; `hebc-ym-cloud-replay.yml` runs it on the exact head. `SHA256SUMS` covers every
other file, `ZGAP2.hbi` holds the chained `EMIT` rows
(`pid[0] = sha16("EMITTER-SEED|YM-ZGAP2-2026-10-30-CLOUD")`), and
`ZGAP2.seal = sha256(SHA256SUMS + ZGAP2.hbi)`.
