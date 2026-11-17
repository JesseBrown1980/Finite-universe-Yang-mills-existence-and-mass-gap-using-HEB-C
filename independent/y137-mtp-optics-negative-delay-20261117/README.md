# #137 finite MTP shell correction and apparent negative time — exact causal optics pilot

**Research draft 2026-11-17, stacked on #293.** Nine finite exact-integer pulse trials, frozen source/result SHA256 and independent receipts, plus an exact two-state quantum weak-value control.

## Source provenance
- Operator-supplied **Jesse Daniel Brown and Anton Fedotov**, *Nonlinear Temporal Dynamics: Theoretical Foundation and Explanation of Negative Time Delays in Resonant Photon Systems* (February 9, 2025, 26 pages). Sections 4–6 use phi(omega)=arctan((omega-omega0)/Gamma), with convention Delta t = -d phi/d omega; center slope is -1/Gamma. Sections 8–10 propose globally accumulated local temporal effects. Their full proposed optical-density and nonlinear equations are not implemented in this tiny FIR test.
- **D. Angulo et al.**, *Experimental Observation of Negative Weak Values for the Time Atoms Spend in the Excited State as a Photon Is Transmitted*, Physical Review Letters 136, 153601 (April 13, 2026), DOI 10.1103/gjfq-k9dv. Experiment's cross-Kerr probe and postselected weak-value measurements: narrowband (-0.82±0.31) tau0, broadband (+0.54±0.28) tau0.
- Parent finite Yang–Mills research PRs #288–#293 are rechecked. This model modifies none of the original 3x4 S3 Hamiltonian, its conditional finite gap, or actual Wilson first-excitation HOLD status.

## Exactly what is modeled
A six-link causal propagation route receives an exact integer triangle pulse. At global tick t, frozen source and MTP-like evaluators all read x[t-6], x[t-7]; no future value and no previous state rewrite are ever used.

- Baseline ordinary local response: y0[t]=(2*x[t-6]+x[t-7])/3. Low-frequency group delay relative to six-link travel is +1/3 tick.
- Local MTP1 forecast is the previous received value. MTP3 detects discrepancies and builds a corrected extrapolation. MTP27 certifies bounded gain/passivity. Their actual compiled two-tap rule, for optical-density *token* d in {1,2,4}, is
  y_d[t]=((2d+1)*x[t-6]-d*x[t-7])/(3d+1).
  These are **deterministic adapters inspired by nested MTP**, not the actual trained Asolaria predictor weights or a physical atom cloud.
- Exact transfer function after six cell shifts H_d(z)=((2d+1)-d*z^(-1))/(3d+1), giving group delay near zero frequency tau_g(0)= -d/(d+1); Nyquist group delay +d/(3d+1). Its absolute impulse coefficients sum to 1, proving the l2 response norm <= input norm. The first nonzero response occurs only after the six-cell causal delay, even with a negative relative group delay.

| d | Baseline delay | Corrected low-frequency delay | Nyquist delay |
|---|---:|---:|---:|
| 1 | +1/3 | -1/2 | +1/4 |
| 2 | +1/3 | -2/3 | +2/7 |
| 4 | +1/3 | -4/5 | +4/13 |

Each optical-density setting was tested at three triangle-pulse half-widths 3,8,16: all nine outputs have authenticated source/result SHA256 receipts, causal onset and exact integer amplitude/intensity centroids. The corrected broad-pulse outputs remain negative at baseband. This **fails the positive weak-value broadband sign observed in the experiment**. Group delay/centroid are also **not the experimental atomic excitation-time weak-value observable**, and the simulated tick is not calibrated to tau0; no fit of the 2026 data is claimed.

## Quantum non-MTP negative control
Exact normalized 2-state preket (4,3)/5, postket (4,-3)/5 and projector |1><1| have post/pre overlap 7/25 and excited-projected overlap -9/25, giving projector weak value -9/7. This is a valid negative weak value from **postselection**, with no MTP reconciliation. A negative quantum weak value is not negative elapsed wall-clock time.

## What the pilot establishes
Causal sequential processing and an MTP-style local correction can yield an apparent negative *group delay relative to flight time* without retrocausality or superluminal signal onset. This is a reproducible exact computation, not evidence that photons, spacetime, or physical observers are run by global MTP agents.

Original original-S3 conditional finite mass gap intact; original Wilson spectral weight **HOLD**. No polynomial-time NP-complete solver results from a 2-tap O(length) signal-processing method or its SHA receipt: P=NP is **NOT IMPLIED**, as earlier #292 exact 3SAT factor-width controls demonstrate. No hash digest generally inverts a full source state.

## Acceptance and next gate
Source files: pilot.py and verify.py. The independent script reconstructs waveforms, output SHA256, signal onset, exact centroid calculations, passivity and a weak-value algebraic control without invoking the pilot. Hosted CI reruns original #288 S3 and #293 density-bond controls and uses repository-wide integer-only/no-floating-point policy.

**Next scientific gate:** model cold-atom quantum scattering and postselected cross-Kerr probe observable using local causal exact matrix transfer, then compare the same 2026 narrow/broad-pulse data in an ordinary quantum control and an MTP-corrected version. The MTP version must improve a preregistered comparison to support extra explanatory power. Keep this draft for independent review.
