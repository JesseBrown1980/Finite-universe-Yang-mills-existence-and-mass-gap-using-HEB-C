# zconf: the S3 confining phase, static-charge potential and string tension

First confinement package. It measures the energy of two static S3 charges (the 2-dimensional
irrep `std` and its conjugate) held `d` links apart, on the confining (electric) side of the
HEB-C Hamiltonian `H/J_E = E + r M`, `r = J_B/J_E`. Predictions were frozen in `PREREG.md`
(sha256 `05481f4f…`) before any code was written. Rust 1.81, std only, exact integer and rational
arithmetic, clippy `-D warnings`, json=0.

## Result

```
V(d, r) = 3 d − (5/72) d r² + O(r³)        sigma(r) = 3 − (5/72) r² + O(r³)
```

| Check | Prediction | Measured | Verdict |
| --- | --- | --- | --- |
| F1 link spectrum | trivial 0, sign 6, std 3 | 0, 6, 3 | PASS |
| F2 `V(d,0) = 3d` | d = 1..6 | 3, 6, 9, 12, 15, 18 | PASS |
| F3 kappa exact, negative, d-independent | kappa < 0 | kappa = −5/72 | PASS |
| F4 two independent methods agree | identical rationals | s_vac = −1/12, s_str = −17/144 in both | PASS |
| F5 sigma at r = 1/27, 1/9, 1/3, 1 | measured | 157459/52488, 17491/5832, 1939/648, 211/72 | recorded |

The second-order string tension would reach zero at r² = 216/5 (r ≈ 6.57). That is far outside the
range where an O(r²) series can be trusted, and it sits on the magnetic side where the gap law
(zgap2) places the deconfined/topological phase; it is recorded, not claimed as a transition point.

## How it is computed

- At r = 0 the Gauss law forces a nontrivial irrep on every link of the path; `std` (energy 3) is the
  cheapest irrep that fuses `std ⊗ std → trivial` at the interior vertices, so V(d,0) = 3d. F2 checks
  this by brute force over every irrep assignment on the path, using fusion multiplicities from the
  characters.
- O(r): `<chi_std(U_p)>` vanishes in both vacuum and string states, so there is no linear term.
- O(r²): each plaquette contributes `s_p = −Σ_R |P_R chi_p psi0|² / (|psi0|² (E_R − E_0))`, summed over
  every excited irrep assignment of its four links. A vacuum plaquette gives −1/12 (all four links
  lifted to `std`, energy 12). A plaquette holding one string link gives −17/144 (the string link
  goes to `std ⊗ std = trivial + sign + std` with weights 1/4, 1/4, 1/2 and energy gaps 6, 12, 9). Each
  string link sits in two plaquettes, so kappa = 2(s_str − s_vac) = −5/72 per unit length. Because the
  same two plaquettes repeat on every string link, kappa does not depend on d.
- Method A uses the S3 multiplication table and characters. Method B rebuilds the same quantities
  from explicit 3×3 integer permutation matrices projected on the `std` subspace by `3I − J`
  (= 3(I − J/3)), checks that the matrix characters match the table, and divides the scale factors
  back out exactly. Both give the same rationals.

Scope: perturbative to O(r²). Finite-r energy certificates, Wilson loops and volume scaling are the
next confinement packages; after S3 the same construction moves to the finite SU(2) subgroups.

## Replay and integrity chain

`run.sh` checks the prediction seal, builds with Rust 1.81, runs clippy and checks byte identity with
`RESULT.hbp`; `hebc-ym-cloud-replay.yml` runs it on the exact head. `SHA256SUMS` covers every other
file, `ZCONF.hbi` holds the chained `EMIT` rows (`pid[0] = sha16("EMITTER-SEED|YM-ZCONF-2026-10-30-CLOUD")`,
`pid[n] = sha16(pid[n-1]|name)`), and `ZCONF.seal = sha256(SHA256SUMS + ZCONF.hbi)`.
