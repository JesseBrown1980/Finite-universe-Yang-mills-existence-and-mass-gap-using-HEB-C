# Winding-loop selection of the first finite S3 gauge excitation — 2026-11-07

**Acceptance:** prediction-first commit 75267b64991200f63ed805f1e55f696c87d8b48f. Hosted exact run 42376841376 PASS. Receipts: MEASURED-WINDING-20261107.hbp and MEASURED-LARGER-SELECTION-20261107.hbp, both pinned on the PR. These are statements about finite group S3, not SU(2) or continuum R4.

## Interacting vacuum, not a uniform trial state

The periodic 1x1 two-spatial-dimensional torus has 36 raw S3 link configurations and 11 gauge-conjugation orbits. At J_E=J_B=1 the W-self-adjoint H=E+M is reconstructed by test_s3_interacting_vacuum.py. The positive Perron vacuum is certified by 729 shifted-power iterations and exact rational residual/Collatz bounds. The first energy splitting satisfies

    2.178437 < E1-E0 < 2.178439    (units J_E).

The single-plaquette Wilson operator chi_std([a,b]) cannot excite E1: its overlap is exactly zero by the quintic/cubic sector selection rule filed earlier. The complementary observable

    O_-(a,b) = chi_std(a) - chi_std(b)

is gauge invariant, real, and *odd* under the spatial-link exchange (a,b)->(b,a). Its exact vacuum expectation is zero. It probes the odd sector, a nonlocal winding/Polyakov-type spatial observable, not a local glueball interpolating field.

## Exactly reconstructed odd sector

The 11 gauge orbits have three exchange pairs indexed (1,3), (2,7), (6,8). Writing antisymmetric orbit vectors in the representatives (1,2,6) yields

    H_odd = [ [6,-2, 0],
              [-3,6,-3],
              [0,-1,9] ]
    W_odd = diag(6,4,12)

with characteristic polynomial x^3-21x^2+135x-252. Its smallest root is E1, with the other odd roots near 7.60146556 and 10.12398318.

The integer-only code checks all group conjugations, oddness, gauge covariance, exact weighted self-adjointness inherited from the full H, and the odd cubic matrix identity.

## First spectral weight: two different exact arithmetic calculations

1. Shift 12I-H_odd, iterate 110 times from a strictly positive vector, and use the certified odd-sector second-root threshold to bound the eigenvector's normalized angular error below 1e-19. Pair the resulting vector with O_-|vacuum> using W_odd.
2. **Without using that odd eigenvector**, isolate the three simple real cubic roots by exact integer-polynomial bisection to width 1e-18. Reconstruct the first spectral projection as a degree-two Lagrange polynomial from the rational moments mu0, mu1, mu2 in the odd subspace. Rational interval products and division give a second enclosure.

    Perron route: 3.021666777298 to 3.021666777300
    Projector route: 3.021666777298 to 3.021666777299

Both are strictly positive. They derive from the same finite Hamiltonian but use different spectral algorithms; they are not independent experimental data.

## Exact-rational interacting-vacuum correlation

C(t)=<vac| O_- exp(-(H-E0)t) O_- |vac>, since <vac|O_-|vac>=0 exactly.

    t=0  [3.022205243662, 3.022205243663]
    t=1  [0.342108549199, 0.342108549201]
    t=2  [0.038732861760, 0.038732861761]
    t=3  [0.004385267369, 0.004385267370]

All brackets are outward in rational arithmetic. The script reuses the verified vacuum and exact 192-term rational moment series, with source-backed error estimates including the Perron angle, rational energy-shift error and series truncation; the stated conservative margin is 1e-13. No floating-point constants, Decimal, Fraction or JSON are used.

## Larger 2x2 and 2x3 spatial lattices: applied operator-selection principle

The local electric and magnetic H preserve spatial graph automorphisms; this is checked directly on each tested full raw-link configuration, *without* taking a spectral shortcut.

- **2x2:** O_swap = chi(winding_x)-chi(winding_y), with matching winding loops based at the origin. It is gauge invariant and odd under axis exchange, so it only couples the symmetric vacuum to the axis-exchange-odd sector.
- **2x3:** O_tx = chi(plaquette(0,0))-chi(plaquette(1,0)), gauge invariant and odd under translation by one x cell (the x side has length two). It only couples a translation-invariant vacuum to the corresponding x-momentum-odd sector.

For **each lattice** the hosted test checks 96 reproducible configurations, 576 independent local gauge transformations, direct magnetic-covariance and full electric transition-multiset covariance, and confirms the operator takes a nonzero value. Non-gauge-invariant open-link controls and wrong-parity even-operator controls are rejected.

**Critical outstanding gate:** being in an odd sector does *not* prove nonzero overlap with that lattice's global first eigenstate. The two larger models need an actual gauge-orbit Hamiltonian, sector decomposition, root enclosures and a nonzero spectral-weight certificate. These have NOT been completed by this experiment. The previously established 3x4 E9-E8 bound remains a different statement. No physical continuum mass or experimental particle mass is claimed.

## Reproduction

    python3 -I -X utf8 native/ym/results/s3_1x1_continuous_jump/test_s3_winding_vacuum.py
    python3 -I -X utf8 native/ym/results/s3_1x1_continuous_jump/test_s3_larger_operator_selection.py

GitHub workflow .github/workflows/s3-winding-selection.yml checks the frozen 15 predictions, compiles both scripts, forbids float literals and true division, runs the independent projector and Perron weight methods, verifies the larger-lattice selection controls, and compares results against both committed HBP receipts **byte for byte**.

## Next quantitative measurement

Use the existing full-orbit/symmetry-sector H builders on 2x2 (1,393 gauge orbits) and 2x3 (47,449 gauge orbits). First enumerate which symmetry sector holds E1, then choose a gauge-invariant operator with that sector character and certify its nonzero matrix element. Do not assume the same winding difference detects E1 on every geometry; for rectangular 2x3 use distinct translation-momentum selectors. After that, study how the first physical energy and its observable overlap change with spatial resolution and volume.

This proves an operator-selection statement for the stated finite system, **not** a Clay Millennium Prize solution.
