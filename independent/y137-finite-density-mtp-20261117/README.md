# #137 finite-density / MTP / real pair-transition experiment

**2026-11-17 · Research draft · exact integer proof-of-concept.** This experiment is a new toy model stacked on the original six-sector Big Bang pilot, independent of the certified original 3×4 S₃ Yang–Mills Hamiltonian. It draws its **frame and metatag definitions** from *Integration and Refinement of Digital Physics* (Brown/Fedotov, 2024; user-supplied `Intergrationv2.pdf`, pp. 3–4), and its **radial density, directional pressure and energy-condition equations** from *Equation of State for Finite-Density Black Holes* (Brown/Smith, 2024; user-supplied `EoSv2.pdf`, pp. 2–4, 8).

## Source equations and deliberate modeling choices

- Both papers write a frame transition `F_(n+1)=T(F_n)` and pixel metatags `(x,y,z,e,p,S)`; the Integration paper adds the angular-momentum label `L` and demands total `L` conservation.
- EoSv2 eq. (1): `rho_profile(r) = rho0 / [1+(r/r0)^n]`. Implement the same rational function at **integer Manhattan shell radius** with `r0=2`, `n=3` and `rho0=12`, taking the *existing* parent simulator's `CORE_CELL_CAP=12` as a density-scale parameter. This is a candidate discrete shell interpretation, **not** a fitted empirical radial density law. The 96 coincident hot initial pixels are an intentionally nonequilibrium seed exceeding this cold-core scale.
- EoSv2 eqs. (2–4): `P_r = w_r rho`, `P_t = w_t rho`, `P_phi = w_phi rho`. The papers' example uses `w_r=1/2`, `w_t=7/10`; `w_phi=3/5` is a **new declared test parameter** because the numeric example does not provide one. Pressure readouts use **measured occupancy / shell cell count** and are independently compared with the proposed analytic profile.
- EoSv2 has **two distinct anisotropy definitions**: eq. (5) `P_t - P_r + P_phi` and eq. (8) `P_t - P_r`. Both are calculated and certified separately. Likewise SEC with `rho+P_r+2P_t` and `rho+P_r+2P_t+2P_phi` are separately checked; no silent reconciliation.
- **Additional pressure-MTP decision rule (research hypothesis):** for a cold pixel's candidate destination, compare the relevant directional pressure computed from conservative occupied-plus-reserved cell count with the analytic finite-density envelope `rho_profile(r_destination)`. If the pressure would exceed the envelope, the MTP watcher holds that pixel for one slice. This pressure *brake* is a modeling postulate and may be overly restrictive. It is not a result proved from the published EoS alone.
- **Pair binding is now a real persistent state that affects subsequent motion.** A pair is eligible only if Manhattan separation ≤1 and the exact microcanonical reservoir counts favor binding. The predecessor's counting model has `U=g C(24,E)` and `B=C(24,E+1)` for free routes `g`, reservoir excitation `E = floor((T_a+T_b)/2)`. Each eligible pair samples a predeclared reversible *two-state* heatbath kernel using a deterministic SHA-derived stream (unbiased digest-to-integer rejection). A pair may form (`bond_energy=-1`), later dissolve, or persist. Each pixel may belong to only one pair. **This is a hypothetical binding model, not physically modeled quarks or glueballs.**
- Pair members share a higher-shell motion veto if unconstrained moves would separate them beyond one cell. The source slice is frozen for the local candidates; the pressure and bond resolvers deterministically commit one next state and its SHA receipt.
- Exact ledger after every tick: `sum_i T_i + E_vacuum − (#bound_pairs) = 96×18 = 1728`. Forming a bond releases one energy unit to the reservoir; breaking consumes one, and all other cooling energy is deposited into the reservoir. This is an **integer energy-accounting model**, not a real thermodynamic calibration.
- Angular momentum `L_total = sum_i [r_i × p_i + spin_i]` is exactly conserved. `p_i` is the observed one-cell displacement, and the new spin is adjusted by the opposite orbital impulse. **The spin adjustment is an explicit compensating bookkeeping rule**, not a derived dynamical spin-torque theory.
- Hilbert expansion inherits the original 96-pixel simulator's finite *address-space* expansion. It has **not** proved that the physical many-body quantum Hilbert space dynamically expands while preserving locality and gauge symmetry. A small isometric embedding remains a separate parent test.

## Exact run results, 48 slices, same initial six-sector seed

| Readout | Pressure brake ON | Same source / pressure brake OFF |
|---|---:|---:|
| Initial physical pixels | 96 | 96 |
| Final bonds | **27** | **45** |
| Total bonds formed / released | **136 / 109** | Separate control recorded in SHA replay |
| MTP pressure-based holds | **3,576** | 0 |
| MTP bond-pair holds | 0 | Separate control |
| Maximum cold core (radius ≤2, temp ≤2) | **0** | **62** |
| Prespecified spontaneous Big Loop condition (`cold core >= 72`) | **NO** | **NO** |
| Final addressed cube locations | **3,375** | Source replay recorded |
| Total energy ledger | **1728, exact** | **1728, exact** |
| Aggregate angular-momentum vector | (0,0,0) every tick | (0,0,0) every tick |
| Maximum pixel displacement per slice | 1 cell | 1 cell |
| Replay | Two byte-identical independent calculations | Separate source-condition control |

The two runs use the same metatag seed and paper parameters, with and without **the newly proposed pressure brake**. This isolates the intervention. With the brake enabled, cold inward motion was suppressed in this particular discretization, leaving no cold pixels in the radius-2 core; this is an important **negative result** for the proposed spontaneous Big Loop. We should **not** describe this pressure rule as successfully deriving a black hole or cosmic bounce.

At slice 18 in the pressured arm, the empirical Manhattan shell-radius-2 occupancy is 32 pixels across 18 cells, giving `rho_measured=16/9`, with `P_r=8/9`, `P_t=56/45`, `P_phi=16/15`; the analytic profile at that radius is `rho_profile=6`. Actual measured occupancy and analytic profile differ, so this is **not a fit to the paper's profile**. Both anisotropy conventions and the energy-condition inequalities pass for the chosen nonnegative w parameters. Their positivity follows algebraically for these w values and does not itself establish a viable astrophysical spacetime.

## Negative controls, unresolved physics

- Reject a fabricated nonlocal >1-cell pixel movement; reject duplicate bond membership; reject an energy-unit omission; refuse an unbalanced angular-momentum ledger.
- The **isolated** two-state heatbath has exact detailed balance by construction. The entire greedy multi-pair, deterministically seeded global transition has **no proven global detailed-balance law**. Its SHA value is an integrity receipt and deterministic pseudo-random seed, not independent proof of physical quantum information transfer.
- The original parent Yang–Mills S₃ Hamiltonian and accepted finite-gap floor remain **unchanged**. Original first-excitation Wilson spectral weight remains **HOLD**. The new toy's mass gap is **NOT COMPUTED**.
- No verified black-hole metric or curvature invariants, QCD particle thresholds, astrophysical time dilation, quantum entanglement, physical Hawking radiation, spontaneous Big Loop or `P=NP` result is claimed.

The next mathematical gate is to replace the empirical pressure comparison and spin-compensation rule with **derived, reversible local transitions** and test a real quantum many-body Hamiltonian with independently certified gauge constraints and finite-source spectral gap.

Run `python3 -I -B independent/y137-finite-density-mtp-20261117/pilot.py`, then archive the HBP-style rows with their SHA256 receipts. All code uses exact integers / integer numerator-denominator pairs and standard-library-only imports accepted by the repo's no-float gate.