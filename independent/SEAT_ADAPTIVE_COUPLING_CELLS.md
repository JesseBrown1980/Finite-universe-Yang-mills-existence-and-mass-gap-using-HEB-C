# Exact coupling cells and low-energy derivative lemma — finite S₃ 2×2 torus

**Scope:** This is a rigorous *finite 1,393-state Hamiltonian* extension stacked on draft PR #12. It certifies six endpoint-comparison cells covering `0<=r<=2` without new expensive eigenvalue solves, and derives a theorem permitting wider cells at large `r` once additional spectral anchors exist. **It does not claim sharp cell coverage of `2<r<10000`**; that entire range has only PR #12's explicit, weak, but positive graph bound at present.

## Two kinds of evidence must remain distinct

- **Existing rigorous anchors**, in the electric chart `h(r)=E+r M`, `r=JB/JE`: `E1(0)=6`, `E0(0)=0`; at `r=1`, `E0<=7.634199`, `E1>13.240`; at `r=5/3`, `E0<=36.699228/3`, `E1>50.840/3`. The latter are existing Stage 2G and PR #9 proofs, not new computations in this branch. The exact `M` diagonal lies in `[0,12]`, and its weighted average in the constant electric ground state equals `8`.
- **Conditional future anchors** for large `r`: The new low-energy derivative theorem below is rigorous, but a cell claim made using a *hypothetical* `g(a)>=1/a` is **not** a certificate until an actual pointwise lower bound is produced. The script emits `result=CONDITIONAL_ONLY|anchor_certified=0` and never `PASS` for those examples.

## Endpoint cell lemma

Since `M>=0`, ordered eigenvalues `E0(r),E1(r)` are nondecreasing (the gap itself need not be). For every real `r in [a,b]`,

`g(r) = E1(r)-E0(r) >= E1(a)-E0(b)`.

Thus if a rigorous `E1(a)>=L` and `E0(b)<=U` give `L-U>0`, the entire continuous cell has `g(r)>=L-U>0`. We may weaken any strict eigenvalue lower bound to a nonstrict bound for this purpose.

From `0<=M<=12I`, `E1(r)>=E1(a)-12(a-r)` for `r<=a`, and `E0(r)<=E0(a)+12(r-a)` for `r>=a`. Two elementary trial spaces give `E0(r)<=8r` (constant electric state) and `E0(r)<=24` (flat-vacuum state).

## Six **proved** cells, no added spectral runs

The script reconstructs the full exact finite operator, checks weighted symmetry, potential range, 8 flat states, and `PEP=24I8`; reads the original certified threshold receipts; and derives all bounds with Python strict integer-pair arithmetic.

| Electric-chart interval `r` | Strictly positive certified lower bound on `gap(h(r))` |
|---|---|
| `[0,1/4]` | `>=4` |
| `[1/4,1/2]` | `>=2` |
| `[1/2,3/4]` | `>=31/25 = 1.24` |
| `[3/4,1]` | `>=2605801/1000000 = 2.605801` |
| `[1,5/3]` | `>=251731/250000 = 1.006924` |
| `[5/3,2]` | `>=71/75 ≈0.9467` |

The non-monotonic pattern of these *lower bounds* is not a claim that the true gap oscillates. For general `JE>0`, multiply all normalized bounds by `JE`.

## Rigorous low-energy Lipschitz theorem for `r>8`

Let `P` project onto the eight `M=0` basis vectors and `Q=I-P`. PR #11 independently verified `PEP=24I8`, `M_Q>=3I`, `M_Q<=12I`, and the second-order matrix `B=-PEQ M_Q^{-1} QEP`. Its exact characteristic polynomial gives `||-B||=6+sqrt(14)<10`, whence

`||QEP||² <= ||M_Q|| ||-B|| <12·10=120`

in the weighted Hilbert space. The complete original electric graph is PSD, so `E_QQ>=0`.

By min-max, the **lowest eight** eigenvalues of `h(r)` are `<=24`, because their restriction to the eight-dimensional trial subspace P is `24I8`. For any normalized eigenstate `psi=p+q` with eigenvalue `lambda<=24`, the Q component obeys

`(r M_Q + E_QQ - lambda I) q = -QEP p`.

For every `r>8`, the Q operator is bounded below by `(3r-24)I>0`. Thus

`||q|| <= sqrt(120)/(3r-24) ||p||`.

Since M vanishes on P and `M_Q<=12I`, the slope of **either of the first two** ordered eigenvalues, wherever differentiable, satisfies

`0<=E_k'(r)<=1440/(3r-24)^2`, for `k=0,1`.

This remains a valid integrated Lipschitz bound across degeneracies, via one-sided eigenvalue derivatives/finite-dimensional Hermitian perturbation theory. For `8<a<=b`,

`0<=E_k(b)-E_k(a)<=480[(3a-24)^{-1}-(3b-24)^{-1}]`.

This is much sharper at large `r` than the global operator bound `12(b-a)`.

### Conditional cell width

Suppose an independent future calculation *actually* certifies `g(a)>=1/a` for some `a>8`. Put

`L(a)=1440/(3a-24)^2`, `h=(1/(2a))/L(a)=(3a-24)^2/(2880a)`.

Then for all `r in [a,a+h]`,

`g(r)>=E1(a)-E0(a+h)>=g(a)-L(a)h>=1/(2a)>0`.

Two illustrative, explicitly **uncertified** anchor assumptions:

| Hypothetical anchor `a` | Rigorous slope bound `L(a)` | Width `h` *if* `g(a)>=1/a` is separately proved |
|---|---|---|
| `100` | `10/529` | `529/2000 ≈0.2645` |
| `10000` | `5/3120002` | `1560001/50000 ≈31.2` |

Those widening steps are about 0.26–0.31% of `r`, showing why a geometric-type adaptive grid becomes valid **conditionally**. They also show that *a few hundred* points is not assured by the present conservative constants. Optimizing the actual transition-sector norm and proving fresh high-`r` anchors is still worthwhile.

## Reproduce

```bash
python3 independent/seat_adaptive_cells.py > /tmp/seat_adaptive_cells.measure
cmp /tmp/seat_adaptive_cells.measure independent/seat_adaptive_cells.measure
```

The new CI workflow verifies all 11 exact, zero-JSON output lines, the six positive cell margins, and explicit `OPEN`/`CONDITIONAL_ONLY` markers. This source demonstrates the *mathematical foundation* for adaptive cells, rather than completing the expensive new-inertia anchor schedule.

**Limits:** This is the fixed periodic 2×2 S₃ lattice only. No increase in lattice size, gauge group, or spacetime dimension; no 4D continuum Yang–Mills theorem. No PR was merged.

## Integer-only audited runtime

This verifier imports `seat_integer_ratio.IntegerRatio`, which stores only integer numerators/denominators. Cross-products, division and ordering use integer multiplications and integer floor-division, never IEEE floating-point arithmetic, `fractions.Fraction`, or decimal libraries. The integer-only AST gate and exact receipt replay run in CI. Proof conclusions and HBP/HBI/STURM antecedents remain the same as before refactoring.
