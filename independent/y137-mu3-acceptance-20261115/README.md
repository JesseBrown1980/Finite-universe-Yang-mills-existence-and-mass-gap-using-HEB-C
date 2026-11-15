# #137: the acceptance test for the real third moment, frozen before mu3 is computed

GPT-6's work order on #137 asks for the real `mu3` at both frozen energies with an independent acceptance test. This
folder is that test, written and run before any `mu3` exists. `real_mu3=NOT_COMPUTED`; the Wilson weight stays HOLD.

## The window a real mu3 must fall in

With `g <= X <= h`, `mu_k = B^T X^k B`, the Gram matrices of the pair `(B, XB)` under the weights `(X - g)` and
`(h - X)` are positive, so

    L = g mu2 + C D^-1 C  <=  mu3  <=  h mu2 - G E^-1 G = U
    D = mu1 - g mu0,  C = mu2 - g mu1,  E = h mu0 - mu1,  G = h mu1 - mu2

in the Loewner order. `accept(candidate, L, U)` takes a candidate only if it is an integer symmetric 8x8 matrix
inside this window. Exact rational arithmetic; the archived `mu0, mu1, mu2` are read through the pinned loaders of
`../y137-moment-radau-20261114/moment_radau.py`.

Measured at both energies (`RESULT-MU3-ACCEPTANCE.hbp`):

| | E1 | E2 |
|---|---|---|
| window nonempty | yes | yes |
| window inside #197's cubic envelope | yes | yes |
| trace width, per million of #197's envelope | 53,853 | 53,856 |

The window is 18.6 times narrower than the envelope on file, so it rejects far more wrong candidates.

## The four-moment bracket that mu3 unlocks

    Gauss   : F >= [mu0 mu1] [[mu1, mu2], [mu2, mu3]]^-1 [mu0; mu1]
    Lobatto : F <= ((g+h) mu0 - mu1 - b c^-1 b) / (g h)
              b = (g+h) mu1 - mu2 - g h mu0,   c = (g+h) mu2 - mu3 - g h mu1
    U0 - F_Lobatto <= S(z) <= U0 - F_Gauss

Evaluated at five points of the window, `L + (k/8)(U - L)`, as the range of outcomes:

| point k/8 | width, per million of the three-moment bracket (E1 / E2) | inside the three-moment bracket | inertia kept |
|---|---|---|---|
| 1/8 | 554,963 / 555,298 | yes | yes |
| 2/8 | 603,432 / 603,663 | yes | yes |
| 4/8 | 478,947 / 479,064 | yes | yes |
| 6/8 | 263,398 / 263,453 | yes | yes |
| 7/8 | 136,932 / 136,960 | yes | yes |

So across these points the real `mu3` narrows the #198 bracket by a factor between 1.66 and 7.3.

## Known-answer test

A 12-state integer `X` with Gershgorin bounds `g = 36`, `h = 123` and an integer `B` with 3 columns, everything
exact: the true `mu3` is accepted; the true `S` lies in the three-moment and in the four-moment bracket; the
four-moment bracket lies inside the three-moment one (278,442 per million of its width); a candidate pushed above
the window, one pushed below, and an asymmetric one are each refused with the reason.

## Reading for the gate (estimate of the seat, not a measurement)

The best full-state error on file is 0.014153976076, 9.9 times the 1/700 gate. If the error scaled with the bracket
width alone, the five points above would give between 1.4 and 6.0 times the gate. The exact figure needs the real
`mu3` carried through the #187 formula, as step 4 of the work order says.

## How the real mu3 will be judged

1. `mu2` rederived byte-identically from the same `V1` records (regression).
2. `accept(mu3, L, U)` at both energies, with the window hashes of the result file.
3. The four-moment bracket computed from the real `mu3` must lie inside the #198 bracket and keep inertia 1 and 2.

Run: `python3 -I -B mu3_acceptance.py` (about 40 seconds).
