# zwilson: certified spatial Wilson loops of the S3 vacuum

Third confinement package. It computes the vacuum expectation of the spatial Wilson loop
W(C) = χ_std(U_C) for the 1×1, 1×2 and 1×3 rectangles on the open 2×4 ladder (the zconfcert L2
geometry), exactly as a strong-coupling series and as certified intervals at finite coupling. Every
computation is a job of the HEB-C HTTP-0 backend (`hebc_ym_http0 serve`). Predictions were frozen in
`PREREG.md` (`4907f52d…`) before the builder, the series solver or any count existed. Rust 1.81, clippy
`-D warnings`, integer arithmetic only, json=0.

## Result: W1–W5 all PASS

### Exact series (two independent bases, identical rationals)

| Loop | r | r² | r³ | r⁴ |
| --- | --- | --- | --- | --- |
| 1×1 | **1/6** | 1/48 | 55/36288 | −25/290304 |
| 1×2 | 0 | **7/432** | 25/6048 | 54323/94058496 |
| 1×3 | 0 | 0 | **11/6912** | 56087/91445760 |

Each loop starts exactly at order r^A, with A its area in plaquettes: the area law at strong coupling.
Method A (49 gauge orbits with Gauss weights) and method B (216 gauge-fixed configurations, unit weights)
agree term by term, and both reproduce the vacuum energy series E = 6r − r²/4 − r³/48 − 89r⁴/72576 (the
r² term is N_p·s_vac = 3·(−1/12), as in #56). The 1×2 coefficient 7/432 is the direct two-plaquette
path (1/108) plus the cross term ⟨ψ₁|W|ψ₁⟩ (1/144); for the dimension-normalised loop W/2 every
coefficient halves (1/12, 7/864, 11/13824).

### Certified finite-coupling values ⟨W(C)⟩ (all widths ≤ 2.6 × 10⁻⁹)

| Loop | r = 1/27 | r = 1/9 | r = 1/3 | r = 1 |
| --- | --- | --- | --- | --- |
| 1×1 | 0.0062014933 | 0.0187777844 | 0.0579252648 | 0.1888827026 |
| 1×2 | 0.0000224378 | 0.0002058037 | 0.0019607348 | 0.0209300537 |
| 1×3 | 0.0000000815 | 0.0000022778 | 0.0000670311 | 0.0023361374 |

(lower ends shown; the exact rational intervals are in `RESULT.hbp`.)

| Check | Result |
| --- | --- |
| W1 series | A and B identical; zero below order A; leading coefficients positive; c₁,₁ = 1/6 |
| W2 certificates | 12 values, widths 3–7 × (1/2.7·10⁹), every lower end > 0 |
| W3 leading order | ⟨W⟩/(c_A,A r^A) at r = 1/27: 1.0046 (1×1), 1.0095 (1×2), 1.008–1.022 (1×3) |
| W4 convergence | that ratio is closer to 1 at r = 1/27 than at r = 1/9 for every loop |
| W5 area law | ⟨W(1×(A+1))⟩ < ⟨W(1×A)⟩ at every r; at r = 1/27 the ratios 0.0036181 and 0.00363–0.00368 match the predicted 0.0036008 and 0.0036376 |

Adding one plaquette to the loop multiplies ⟨W⟩ by about c_{A+1,A+1}/c_{A,A}·r: 0.0036 at r = 1/27,
0.011 at r = 1/9, 0.034 at r = 1/3 and 0.111 at r = 1, the same for both steps (1×1→1×2 and
1×2→1×3) to within 2% at every coupling. That constant factor per plaquette is the area law, now
certified at finite coupling.

## How it is computed

- `ymwser` (new bin in `native/ym/crates/sturmrs`) builds both bases and runs Rayleigh–Schrödinger
  perturbation theory with H0 = E and V = M to order 4 in exact rationals, including every
  ⟨ψ_j|W|ψ_{k−j}⟩ term and the normalisation; the singular system is solved as (WE + w wᵀ)x = Wb.
- `ymconf` Wilson mode writes the diagonal J_B·M + Λ·W(C), so `sturmrs` (called with J_B = 1) counts
  H + λW with λ = Λ/J_E = 10⁻⁸ and J_E = 2.7 × 10¹⁴.
- The ground energy is concave in λ, so (E₀(λ) − E₀(0))/λ ≤ ⟨W⟩ ≤ (E₀(0) − E₀(−λ))/λ, valid also for a
  degenerate ground state. Each E₀ is bracketed to one threshold unit (3.7 × 10⁻¹⁸ J_E) and the outer
  ends give the interval: (L₊ − U₀)/λ ≤ ⟨W⟩ ≤ (U₀ − L₋)/λ.
- New backend job kinds: `wilsonmat/ROWS/COLS/X0/X1/JB/LAM`, `wilsoncount/ROWS/COLS/X0/X1/JB/LAM/JE/T`,
  `wilsonseries/ROWS/COLS/METHOD/ORDER`. 1082 counts and both series jobs, with every final bracket and
  both series re-executed by `verify`.

## Replay and integrity chain

`run.sh` checks the prediction seal, builds the native/ym workspace and the driver with Rust 1.81, runs
clippy, starts `hebc_ym_http0 serve` on a fresh ROOT, runs everything through it and checks byte identity
with `RESULT.hbp`; `hebc-ym-cloud-replay.yml` runs it on the exact head. `SHA256SUMS` covers every other
file, `ZWILSON.hbi` holds the chained `EMIT` rows (`pid[0] = sha16("EMITTER-SEED|YM-ZWILSON-2026-10-30-CLOUD")`,
`pid[n] = sha16(pid[n-1]|name)`), and `ZWILSON.seal = sha256(SHA256SUMS + ZWILSON.hbi)`.
