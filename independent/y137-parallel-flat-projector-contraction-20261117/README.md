# Issue 137: independent true-flat projector Wilson contraction gate

This is the **second parallel track** of issue 137, independent of the QOQ full-source 40/60-step experiment in #274. It uses exact source records already accepted on original main plus the signed 64-entry matrix interval from hosted #273 (frozen byte-for-byte at job 134120671522, run 44106643165).

## Source ingredients

- Original 3×4 finite S3, r=9, original eight-flat coordinate W weights (1,3,2,3,3,2,2,2).
- Original 24-link seven-loop Wilson observable, diagonal multiplication; POQ=QOP=0; original B†B=72I; original ||O||≤14.
- Original PR180 accepted two even flat sample directions, checked against its accepted immutable receipt.
- Original PR184 accepted **true low flat Schur-null branch** angular ceilings sin(theta1)≤108258863901/10^12 and sin(theta2)≤253465115951/10^12. Its earlier true-E windows contain the later narrower accepted Stage E physical windows.
- The actual 64 signed entry intervals of M(E2,E1)=POP+B†R2 QOQ R1B from hosted PR273, with original 1,985,218 physical exterior targets included in its full Q-residual errors, true E1/E2 windows covered, and 64 source hashes frozen. This file is a **hosted-result copy, not an independently recomputed Q source**.

The tested identity for normalized W-flat sample vectors v_i and phase-aligned **true W-flat unit eigendirections** x_i is

    x_i = c_i v_i + h_i, h_i ⟂ v_i, ||h_i||≤s_i,
    c_i ≥ sqrt(1-s_i²).

Expanding the true Wilson effective bilinear amplitude and projecting the two source vectors first gives the **correct full contamination**:

    |<x2,M x1>| >= c1*c2 |<v2,M v1>|
                       -s2 ||(I-P_v2)M v1||
                       -s1 ||(I-P_v1)M† v2||
                       -s1*s2 ||M||.

This keeps both observable-targeted deflated actions and the exact two-state cross term. Each deflated norm for the center Mhat is computed from exact W-weighted integer quadratic forms (not estimated by 14), and inflated by the Frobenius norm upper bound on the full signed matrix interval Mtrue-Mhat. The center sample scalar is reduced by its actual source 64-entry signed interval radius before applying c1c2. The last ||M|| uses the valid original-source inequality

    ||M||_W ≤14*(1+72/[(gamma-E1_hi)(gamma-E2_hi)]).

All square roots, interval divisions, flat-angle cosines, sample normalization and the final strict signed margin are rounded *outward*, using integers exclusively.

A strictly positive margin would be a source-conditional **candidate**, pending independent review and full-state normalization; otherwise HOLD is an explicitly quantified negative result about the *sufficient verifier*. Even if margin is nonpositive, it does not refute first Wilson weight. These source state angles remain from #184, not the improved Stage E moved-vector angles; the experiment tells us whether current accepted frozen directions can close the gate, and publishes comparable evidence.

**The finite first physical energy gap remains source-conditionally certified. First Wilson spectral weight HOLD until the true-state acceptance conditions are independently reviewed. Four-dimensional continuum theorem OPEN.**

Reproduce

    python3 -I -B independent/y137-parallel-flat-projector-contraction-20261117/flat_wilson_gate.py toy
    python3 -I -B independent/y137-parallel-flat-projector-contraction-20261117/flat_wilson_gate.py real

The dedicated GitHub Actions workflow proves provenance, exact arithmetic, negative controls and archive hashes. It does not silently upgrade a positive arithmetic result into an accepted physical theorem.
