# Issue #137 — original Wilson directional Q-dual over the certified physical energy windows

**Research draft, November 17, 2026.** Independent numerical source lane focused on the QOQ double-resolvent term, complementary to #275's true flat-sector projector test. Exact integer arithmetic, original physical 3×4 S₃ graph, full shell4 residuals.

The baseline #273 8×8 entry-by-entry source interval has a maximum radius approximately 0.147. A 40/60-iteration sweep in #274 yielded no tightening. This lane instead reuses the source-accepted signed dual-residual mechanism of #180, applied to the genuine original seven-loop *unshifted* Wilson observable at the Stage E **physical E1 and E2 upper energy endpoints** and over the complete certified energy intervals.

## Source-conditional exact identity

Let P be the eight-flat physical coordinate projector, Q its complement and `B=QHP`. O is the original seven-loop diagonal multiplication operator: `POQ=QOP=0`. Choose the original W-flat *fixed* source vectors v1,v2 (source SHA-pinned #180), and define for the unknown true physical energies E1,E2

    q_i(E_i)=-(QHQ-E_i)^(-1) B (T v_i),   T=10^12,
    M(E2,E1)=<T v2,O_P T v1>_W+<q_2(E2),O_Q q_1(E1)>_W.

For the accepted finite E_i brackets, first compute the original 155,378-state K3 Jacobi trials y_i **at the true energy upper endpoints** z_i. Let A_i=b(QHQ-z_i), b=10^9, and r_i=A_i y_i+bB(Tv_i). From the accepted full-Q physical source, the complete shell4 residual norms `||r_i||²` are exact, including all outside-K3 coordinates. Compute dual approximations u21≈b A_2^(-1)(O_Q y1) and u12≈b A_1^(-1)(O_Q y2) with their complete original shell4 residual norms d21²,d12². The signed true-endpoint matrix element obeys

    | b M(z2,z1) - [ b(<Tv2,O_P Tv1>+<y2,O_Q y1>)
                              - <r2,u21> - <r1,u12> ] |
       <= ||r2|| ||d21||/gap2 + ||r1|| ||d12||/gap1
          + b*||O_Q|| ||r1|| ||r2||/(gap1 gap2),

where `gap_i=b*(gamma-z_i)>0`. The code computes this error with strict outward integer square roots. It uses `||O_Q||<=14` and the source-accepted nonflat floor gamma≥94.0682.

**Both true physical energy windows**, not just their upper endpoints, are covered by an independent exact resolvent drift: `||B||²=72` in the original normalized flat W metric, `||O||<=14`, and the exact widths of both E_i intervals. Norm enclosures for the fixed-flat-direction full physical states account for Q residual correction and energy dependence.

The output is a *source-certified fixed-flat-direction* signed transition-margin test, with separate source-dual and true-energy-window errors. Positive margin would establish an original Wilson action on these fixed flat trial directions, independent of a full 8×8 coordinatewise box estimate. **It would not, by itself, certify a positive first-excitation Wilson weight**; the true flat Schur eigendirections and their coupling to the original fixed v1,v2 must still be enclosed and reviewed. Source #275's first projector-deflation test is currently HOLD, with accepted angles approximately 0.1083/0.2535.

This is a research draft. Any source-integrity failure, changed original B coupling, missing full shell4 contribution or inconsistent rational scaling causes a refusal; a nonpositive signed source margin remains HOLD. No update to main theorem status until independent review. The finite physical first energy gap remains source-conditionally certified; actual first Wilson weight HOLD, continuum mass-gap theorem OPEN.

Reproduce using `.github/workflows/y137-original-wilson-directional-dual.yml` or `python3 -I -B independent/y137-directional-original-wilson-20261117/dual_endpoints.py real`.
