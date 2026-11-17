# Issue #137: actual table-governed MTP slice evolution (research pilot)

**2026-11-17.** The earlier #289 freeze/edit/play toy held its physical transfer matrix `U = I16` constant. It therefore only demonstrated that catalog edits are inert under a frozen transfer. The user's design requires **freezing a source slice**, **editing its metatag catalog**, then **running shell-specific MTP evaluators to construct the next physical transfer**. This pilot tests that distinct contract. It is a new model rule, not a reinterpretation of the previously accepted finite Yang–Mills Hamiltonian.

## Source/ontology

- `Metatagging-data-for-a-Quantum-universe` (`metatag_v2_behcs.py` and `docs/THE-LEARNING-PIPELINE-slices-are-time-2026-07-03.md`): persistent PID/catalog and disposable time slices; HRM/MTP-1,2,3 read a frozen slice and preserve derivative receipts.
- `ASOLARIA-AS-NEURAL-NETWORK/canon/laws/LAW-SLICE-ENGINE.md`: registered frozen positional slices do not advance unless an external engine drive runs.
- User's prior `Law 24 — The MTP Slice Agent (×1/×3/×27 lookahead, −/0/+ directions)`: **architectural inspiration**. The actual trained MTP weights, full historical spatial-shell scorer, and a working cross-cloud neural inference stack were not authenticated or loaded. This pilot uses **three independently checked deterministic MTP-style adapters** at horizons 1, 3, and 27.
- Parent PR #288: real finite `3×4`, `S3`, 24-link gauge-orbit source, bounded nonnegative diagonal plaquette overlap law and conditional perturbative gap estimates. Parent PR #289: metatag retagging under `I16` (negative comparison). New code is in a separate 4-qubit toy quantum register; no new S3 matrix entry is represented as certified.

## Actual freeze → edit → evaluate → play contract

Initial quantum registers `A0,A1` in cloud A and `B0,B1` in cloud B: Hilbert dimension `2^4=16`. The frozen metadata binds `PAIR-7` to **A0:A1**, while B0,B1 have standalone keys. The edited table changes A0 to standalone, binds **A1:B0** to `PAIR-7`, and sets a one-slice `pulse=1` on A1. This changes only the table at the moment of the edit. The quantum state remains fixed until `play`.

1. **Freeze** physical state SHA, the original identity catalog SHA and `U0=I16` SHA; retain immutable source.
2. **Edit** the complete catalog snapshot; SHA must change while the physical state SHA remains unchanged.
3. **Evaluate** the edited snapshot with three shell-specific MTP agents: MTP1 proposes the immediate paired exchange, MTP3 separately forecasts that the pulse is consumed and does not re-fire across three slices, and MTP27 checks the 27-slice pulse horizon and verifies the quantum permutation conserves total excitation.
4. **Resolve** independent proposals: the global-index mode requires all three MTP agents to agree. Deduplicate updates and refuse conflicting group memberships, duplicate pulses, ambiguous three-party keys, or conservation failure.
5. **Construct** the quantum transfer from the evaluated catalog. The authorized `PAIR-7` rule is an exact **SWAP(A1,B0)** on the 16D state. Its 16×16 matrix is an integer permutation, orthogonal/unitary, reversible, and excitation conserving. It differs from the originally frozen identity matrix.
6. **Play** by applying this newly constructed transfer atomically to the frozen state and consuming the pulse; emit new physical-state and metatag-catalog roots.

**Global-index semantics:** All three MTP agents in each shell can read the entire identity table at once. They predict the same remote pairwise exchange even when the two cloud addresses have a large separation. This is **a specified nonlocal table-read/interaction rule**. It supplies the required information/interaction path as part of the simulator; the resulting distance-independent remote change is *not* spontaneous entanglement signalling, not evidence of faster-than-light particle communication, and not a consequence of the previous S3 Hamiltonian.

**Local-radius negative control:** At shells with radii `1,3,27`, the MTP agent sees the remote partner only if the clouds are within that radius. The quantum SWAP is authorized only after an evaluator can see both members. At distances above 27, remote action is blocked in the same slice. This is an artificial finite neighborhood control, not a calibrated relativistic light cone.

## Exact observable tests

| Source state | Rule | Receiver result after one frame |
|---|---|---|
| Product state with the only excitation at A1 | Original `U=I16`, even after tag edit, **no play** | `P(B0=1)=0` |
| Same source | Edited table builds remote SWAP in **global-index** mode | `P(B0=1)=1`, `P(A1=1)=0`; conserved excitation count `1→1` |
| Same source | **Local-radius** mode with separation 64, 1024, or 65536 | `P(B0=1)=0` in the first frame |
| Bell state initially entangled **A0:A1** entirely in A | Edited table builds physical SWAP(A1,B0) | Bell pair moves to **A0:B0**; `P(B0=1)` changes from `0` to `1/2` |
| Bell state already entangled **A0:B0** | A physical SWAP of its two members | B's local density matrix remains exactly unchanged; no free Bell-only signalling |

All quantum states are exact real integer coefficient vectors with squared-normalization denominator `1` or `2`. Bell amplitudes are represented exactly as `(1,1)/√2`, with integer partial traces. State transitions are integer permutation matrices. No continuous-time physical QFT simulation and no floating-point arithmetic are involved.

**Distances:** 1, 8, 64, 1024, 65536 address units. These are logical labels. A global evaluator ignoring distance makes the result identical by construction. This is precisely the hypothesis being tested, not an independently measured law.

**Fail-closed controls:** missing pulse, unpaired/colliding identity, duplicate initiator, state frozen during table editing, replay nondeterminism, wrong shell visibility, nonunitary transfer, particle-number nonconservation, and false claims about Bell-only communication.

## Scientific acceptance boundary

- **PASS (computational toy):** the corrected table-governed mechanism *does* produce remote next-slice state changes and can transfer a Bell pair across separated clouds, **when the MTP evaluators are explicitly granted global catalog access and the rule builds a nonlocal SWAP gate**.
- **PASS (control):** when remote reading is limited by finite shell radii, the same-slice remote change disappears beyond radius 27; when `U` is frozen to `I16`, no physical update occurs from a table edit alone.
- **HOLD / OPEN:** this does not prove quantum entanglement can communicate outside a causal light cone. It tests a user-proposed **additional nonlocal interaction mechanism**. A conventional unitary generated by spatially local interactions has different causal structure. A globally shared classical table itself can carry command information.
- **HOLD:** existing original S3 source-conditional gap remains unchanged; this *different* 4-qubit Hamiltonian cannot import its numerical gap or first Wilson-weight certificate. To introduce the table-controlled operator into the original S3 Hilbert space, one must define a gauge-invariant, Hermitian coupling and certify its norm; the existing signed perturbative gap survives for any **static** original-space perturbation with norm `≤ 1/64 J_E`, with conditional gap `>0.008427591 J_E`, but time-dependent table-driven slices require a separate dynamics analysis.

Review as an independently runnable research prototype. `python3 -I -B pilot.py` emits only HBP-style integer output and SHA256 receipts. Don't merge source-conditional Yang–Mills claims into the new toy.