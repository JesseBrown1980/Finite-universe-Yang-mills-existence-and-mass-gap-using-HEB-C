# #137 / #288 — exact two-cloud pixel metatag freeze → edit → play pilot

Date: 2026-11-17. **Research-only controlled demonstration**, to be reviewed as a stacked draft on the gauge-invariant S₃ residual-shell perturbation PR #288. It does not alter the Yang–Mills Hamiltonian, introduce a new physical force, demonstrate superluminal signalling, or modify an accepted certificate.

## Source relationship and user's proposed protocol

The original `Metatagging-data-for-a-Quantum-universe` repository stores particle and paired-state metadata; `metatag_v2_behcs.py::entangle()` issues a bilateral cosign and a `PhaseCorrelation` field. That **is a catalog record**, not a quantum-state preparation gate. Original #288 supplies an **independent, assumed exchange-law two-cell toy** with exact concurrence 24/25 and a positive bounded gauge-invariant S₃ shell-overlap perturbation. Neither source contained a freeze/edit/play bridge across separated pixel clouds, so this independent experimental implementation supplies it explicitly.

The source test uses four physical two-level pixels in two clouds (A0,A1 / B0,B1), exact 16-dimensional Hilbert space, a **frozen physical transfer** `U=I_16`, and hash-identified immutable state and mutable catalog snapshots. Exact amplitudes are the integer numerators of a wavefunction of norm squared 2; every density matrix element is an exact integer over 2. There are **no floats, fractions, JSON, random samplers, or external numerical dependencies**.

To avoid conflating different arrangements, there are two separately frozen experiments:

1. **Two already-separated clouds with pre-established cross-cloud entanglement.** Prepare `(|0000>+|1010>)/sqrt(2)`: A0 and B0 form a Bell pair; A1 and B1 are zero. Freeze. Edit the metadata table to reassign A0 from B0 to B1 without changing the physical transfer. Replay and compare the full-state SHA256, remote B reduced density, X/Z local measurements, and X/X and Z/Z pair correlators. In independent branches, apply `Z_A0` and `X_A0` to encode two signals. Their **joint** A0/B0 correlations respond while the **B-only** reduced density and measurement statistics remain identical. Then perform a *physical, local-to-B* `SWAP(B0,B1)` as a positive control; the entangled partner moves to B1 because a unitary gate, not a catalog edit, has acted.
2. **Entangled group initially entirely inside cloud A.** Prepare `(|0000>+|1100>)/sqrt(2)` where A0 and A1 are entangled and cloud B is pure |00>. Freeze. Change the catalog to claim A0 is now paired with B0 at a remote site. Replay **the same** physical matrix. B remains in |00> and A0/B0 acquire no entanglement. An explicit `SWAP(A1,B0)` would relocate the physical pair, but that is a **cross-cloud, nonlocal physical gate**, so it is flagged rather than mistaken for a metatag-only effect.

Both controls run for separations `1, 8, 64, 1,024, 65,536` *logical pixel-address units*. Distance is an address-label parameter in this toy; it is **not** a dynamically simulated relativistic propagation delay or physical Planck-length measurement. This explicitly tests the 'regardless of distance' lookup hypothesis without pretending that the toy has established a physical distance law.

## Mathematical acceptance

For a frozen Bell pair `|Phi+>=(|00>+|11>)/sqrt(2)` and local unitary `U_A`, tracing out cloud A yields

```
Tr_A[(U_A ⊗ I_B) ρ_AB (U_A† ⊗ I_B)] = Tr_A[ρ_AB].
```

Consequently, `P_B0(Z=1)=1/2` and `P_B0(X=+)=1/2` in the original pair and both A-local operation branches. The normalized joint correlators `E(XX)` and `E(ZZ)` are initially `+1/+1`; after `Z_A0` they become `−1/+1`, and after `X_A0` they become `+1/−1`. These changes can only be identified **after comparing the observers' records**.

For the originally local A0/A1 Bell pair, `ρ_B=|00><00|` and `P_B0(Z=1)=0` even after the metatag pointer changes to B0. The actual cross-cloud SWAP is a separate, intentionally nonlocal positive control.

A deliberate shared-memory control writes a `message=0` or `message=1` field into the globally readable B1 table: the remote reader sees that change, while the physical reduced state stays identical. **Such an effect would be an explicit classical/global lookup channel, not an entanglement communication result**. If a finite-matrix engine's replay actually propagates table edits to B without an allowed physical update, it must document that dependency and its causal rules.

Required strict assertions: state hash unchanged for table-only edits, changed table SHA, all original Bell correlations preserved, B reduced density invariant under arbitrary A-local tested gates, physical B-only SWAP moves the true pair, initial local-A Bell pair does not migrate under table editing, remote deterministic-bit forgery rejected, and unchanged physical transfer hash.

## Yang–Mills connection and scope

The pilot runs **alongside**, not inside, the original 3×4 periodic S₃ model. Its parent PR #288's `pilot.py` and source hash are archived as part of the run when stacked. Under the original 3×4 gauge-orbit model, the new diagonal nonnegative residual interaction is bounded by `0<=V_alpha<=alpha I`, with its pre-existing perturbative gap budgets unchanged. The local pixel/Bell demonstration neither establishes a new `S₃` spectral estimate nor supplies a first-excitation Wilson spectral-weight numerator. That Wilson certificate stays **HOLD**, the continuum theorem stays **OPEN**, and no claim about physics at arbitrarily large separation follows from this logical-address test.

The run is **exact for this 16-dimensional toy**. It shows which additional physics must be supplied if someone proposes that metatags do more than identify and audit states: a specified Hamiltonian/quantum channel mapping a catalog edit into an actual change of a distant reduced state. Such a channel would require a separate locality and experimentally testable causality analysis.

## Reproduction

```sh
python3 -I -B independent/y137-pixel-cloud-freeze-edit-play-20261117/pilot.py
python3 -I -B native/scripts/integer_only_audit.py independent/y137-pixel-cloud-freeze-edit-play-20261117/pilot.py
```

The hosted workflow also reruns the exact #288 parent and checks frozen signatures, five distances, both controls, and a strictly scoped final verdict before publishing SHA256 receipts. All output rows are plain-text `|`-separated HBP-style records, not JSON.