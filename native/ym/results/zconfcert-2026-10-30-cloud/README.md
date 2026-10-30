# zconfcert: certified finite-coupling energies of the S3 static-charge sector

Second confinement package. It encloses, at finite coupling, the ground energies of the vacuum and of
the sector with two static S3 charges (`std` and its conjugate) d links apart, and compares
V(d, r) = E_charged − E_vac with the second-order law from `zconf` (#56). Every count runs as a job of the
HEB-C HTTP-0 backend (`hebc_ym_http0 serve`), which stores canonical `run.hbp` / `index.hbi` /
`run.anchor` shards and re-executes the final brackets byte for byte. Predictions were frozen in
`PREREG.md` (`b8079bb4…`) before the solver existed; `ADDENDUM.md` (`4d3f1a98…`) was sealed before any
certificate count. Rust 1.81, clippy `-D warnings`, integer arithmetic only, json=0.

## Result: Q1–Q7 all PASS

| Check | Result |
| --- | --- |
| Q1 builder and r = 0 | all 6 matrices exactly W-self-adjoint; vacuum 0 and charged 3d certified exactly |
| Q2 certificates | 24 energies, each enclosed to ≤ 10⁻⁹ J_E (widths 5.19 × 10⁻¹⁰ to 9.78 × 10⁻¹⁰ J_E, i.e. 140 to 264 threshold units of 1/270 000 000 000 J_E) |
| Q3 second order | at r = 1/27, κ_eff within 1% of κ_g on every geometry and d (15% registered) |
| Q4 convergence | κ_eff moves toward κ_g as r falls from 1/9 to 1/27, every cell |
| Q5 local mechanism | κ_eff(L3)/κ_eff(L2) = 1.9999 at r = 1/27 ([1.7, 2.3] registered) |
| Q6 confinement | σ(d, r) = V(d+1, r) − V(d, r) certified positive in all 8 cells |
| Q7 HTTP-0 replay of #56 | `zconf` job `run.hbp` byte-identical to the sealed RESULT (`bb9ca0f4…`), verify PASS |

Geometries (open boundaries, so the pair has no periodic image): L2 = 2×4 ladder, string on the edge
row, one plaquette per string link, d = 1, 2, 3; L3 = 3×2 strip, string on the middle row, two plaquettes
per string link, d = 1.

### Static-charge potential V(d, r) (lower ends of the certified intervals, J_E units)

| | r = 1/27 | r = 1/9 | r = 1/3 | r = 1 |
| --- | --- | --- | --- | --- |
| L2, d = 1 | 2.999952015 | 2.999561714 | 2.995877806 | 2.957863985 |
| L2, d = 2 | 5.999904030 | 5.999123305 | 5.991744331 | 5.914466331 |
| L2, d = 3 | 8.999856045 | 8.998684933 | 8.987614069 | 8.871360829 |
| L3, d = 1 | 2.999904033 | 2.999123577 | 2.991768698 | 2.917095550 |

### κ_eff = (V − 3d)/(d r²) against the exact second-order coefficient

| | κ_g | r = 1/27 | r = 1/9 | r = 1/3 | r = 1 |
| --- | --- | --- | --- | --- | --- |
| L2, d = 1 | −5/144 = −0.034722 | −0.034981 | −0.035501 | −0.037100 | −0.042136 |
| L2, d = 2 | −5/144 | −0.034981 | −0.035506 | −0.037151 | −0.042767 |
| L2, d = 3 | −5/144 | −0.034981 | −0.035507 | −0.037158 | −0.042880 |
| L3, d = 1 | −5/72 = −0.069444 | −0.069960 | −0.070990 | −0.074082 | −0.082904 |

The certified energies reproduce the #56 law V(d, r) = 3d + n_g d (s_str − s_vac) r² with
s_vac = −1/12, s_str = −17/144: the coefficient is the same for every d, and it doubles exactly when each
string link sits in two plaquettes instead of one. The remaining drift of κ_eff is linear in r (the third
order term, about −0.007 d r³ on L2), and per unit length it is the same for every d to within 2% at r = 1. The string tension
σ(r) = V(d+1, r) − V(d, r) is 2.99995 at r = 1/27 and 2.9566 at r = 1 on L2, positive throughout.

## How it is computed

- `ymconf` (new bin in `native/ym/crates/torusl`) builds each sector: comb gauge tree, free links,
  orbit representatives under global conjugation, Gauss weights, electric moves, magnetic diagonal, in the
  standard exchange format.
- The charged sector is the gauge-invariant sector of the strip plus one auxiliary link from b to a with no
  electric or magnetic term. States with that link in irrep R are exactly the sector with charge R at one
  end and its conjugate at the other; the penalty 10(E_l − 3)² (0 on `std`, 90 on trivial and sign)
  selects R = `std` exactly and commutes with H.
- `sturmrs` (interval Sturm inertia, outward rounding) counts negative eigenvalues of
  W(1000(J_E Z + J_B M) − T W) with J_E = 2.7×10⁸. A count of 0 certifies E₀ > T; a count ≥ 1 certifies
  E₀ < T. Each energy is bracketed from the second-order prediction and bisected to width ≤ 10⁻⁹ J_E;
  the two final bracket counts are re-executed by the backend's `verify`.
- New backend job kinds: `confmat/ROWS/COLS/XA/XB/CH`, `confcount/ROWS/COLS/XA/XB/CH/JE/JB/T`, and
  `zconf`, which runs `zconfpt`, a byte-identical copy of the #56 source (sha256 `a7166920…`).
- `RESULT.noserver.hbp` is the output of a first launch in which the server refused the request limit
  (maximum 10000) and the driver ran with no server; it contains no counts and is kept as a record.

## Replay and integrity chain

`run.sh` checks both seals, builds the native/ym workspace and the driver with Rust 1.81, runs clippy,
starts `hebc_ym_http0 serve` on a fresh ROOT, runs all 734 counts through it and checks byte identity with
`RESULT.hbp`; `hebc-ym-cloud-replay.yml` runs it on the exact head. `SHA256SUMS` covers every other file,
`ZCONFCERT.hbi` holds the chained `EMIT` rows (`pid[0] = sha16("EMITTER-SEED|YM-ZCONFCERT-2026-10-30-CLOUD")`,
`pid[n] = sha16(pid[n-1]|name)`), and `ZCONFCERT.seal = sha256(SHA256SUMS + ZCONFCERT.hbi)`.
