# #137: sharp moment brackets for the Schur complement from the moments already on file

Seat ACER-CLAUDE-FABLE52, 2026-11-14, at the operator's direction, as a second-seat contribution on top of draft #197 (head `d84ca0209c`). The prediction and the program were pushed (`adac351`) before the program was run on the archived moments.

## Result

From the same three archived moments `mu0, mu1, mu2` that #197 uses, with no new operator application, the Schur complement `S(z) = U0 - F`, `F = B^T X^-1 B`, is enclosed by

    S_hi3 = U0 - (mu0 + E G^-1 E)/h,   E = h mu0 - mu1,   G = h mu1 - mu2
    S_lo3 = U0 - (mu0 - D C^-1 D)/g,   D = mu1 - g mu0,   C = mu2 - g mu1

Measured on both archived energies, in exact integers (`RESULT-RADAU.hbp`):

| Bracket | Moments used | Trace of the width, per million of the original bracket `mu0/g` (E1, E2) |
|---|---|---|
| original accepted (`U0 - mu0/g <= S <= U0`) | mu0 | 1,000,000 |
| degree 1, Chebyshev (`RESULT-N1`) | mu0, mu1, mu2 | 784,239 · 784,535 |
| degree 2, Chebyshev with the mu3 envelope (#197) | mu0, mu1, mu2 | 685,438 · 685,820 |
| two-moment, Gauss and Lobatto forms (this folder) | mu0, mu1 | 567,142 · 567,422 |
| **three-moment, Radau forms (this folder)** | mu0, mu1, mu2 | **95,553 · 95,646** |

The three-moment bracket is 139,405 and 139,463 per million of #197's bracket (about 7.2 times narrower) and lies inside it in the Loewner order at both energies; the two-moment bracket lies inside the degree-1 bracket; all four new bound matrices keep the accepted negative inertia (1 at E1, 2 at E2). All six frozen predictions R1 to R6 were met. #197's own verifier was run first on the same files and passes.

## Why it holds

For a positive semidefinite weight `Wt`, the block matrix `[[a^T Wt a, a^T Wt c],[c^T Wt a, c^T Wt c]]` is a Gram matrix. Take `a = X^(-1/2) B`, `c = X^(1/2) B`:

- `Wt = X - g` gives `[[mu0 - gF, D],[D, C]] >= 0`; with `C > 0` the Schur complement gives `F <= (mu0 - D C^-1 D)/g`.
- `Wt = h - X` gives `[[hF - mu0, E],[E, G]] >= 0`; with `G > 0` it gives `F >= (mu0 + E G^-1 E)/h`.
- `Wt = I` gives `F >= mu0 mu1^-1 mu0`; `Wt = (X - g)(h - X)` on `a` alone gives `F <= ((g+h) mu0 - mu1)/(gh)`.

These are the matrix forms of the Gauss, Gauss-Lobatto and Gauss-Radau rules for `1/x` (Golub and Meurant, *Matrices, Moments and Quadrature with Applications*). The condition is the one #197 rests on: `g <= X <= h` on Q.

The program checks `C`, `G` and `mu1` positive definite by their leading minors, the adjugate identities, the validity of each interval by all 255 principal minors, and every Loewner comparison by cross-multiplied integer matrices. Integers only; 8 seconds on one laptop thread.

## What this offers the degree-11 plan (NAMED, measured only at orders two and three)

The same construction extends to every moment count with block Hankel matrices, at no extra pass:

- with `mu0 .. mu_2n`: `[mu_(i+j) - g mu_(i+j-1)]` and `[h mu_(i+j-1) - mu_(i+j)]` for `i, j = 0..n`, where `mu_(-1) = F`; each is positive semidefinite and its Schur complement on the `F` block gives the upper and the lower bound;
- with `mu0 .. mu_(2n-1)`: `[mu_(i+j-1)]` for `i, j = 0..n` (lower bound) and `[-gh mu_(i+j-1) + (g+h) mu_(i+j) - mu_(i+j+1)]` for `i, j = 0..n-1` (upper bound).

A fixed Chebyshev polynomial contracts the bracket by the same factor whatever the measure of `B` is; these forms use the measure the moments record. Here the first added moment took the width to 0.567 of the original and the second to 0.0956, against 0.784 and 0.685. Whether later moments keep that pace is open; `mu3` (the pass #196 is preparing) is the next reading, and it would say how many of the nineteen remaining moments the 1/700 gate needs.

## Scope

Source-conditional exactly as #197: it rests on the accepted window `g <= X <= h` and on the archived moments. It encloses `S(z)` only. The first Wilson spectral weight stays HOLD and issue #137 stays OPEN.

## Files

`PREDICTION.hbp` (frozen first), `moment_radau.py`, `RESULT-RADAU.hbp`, `SHA256SUMS`.
