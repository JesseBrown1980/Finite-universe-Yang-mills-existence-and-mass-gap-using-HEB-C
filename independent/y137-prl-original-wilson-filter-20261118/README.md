# #137 — Original S3 Wilson: PRL-inspired exact second temporal-filter moment

Research draft, November 18, 2026. Motivated by Nicolas Gosling *et al.*, *Probing the memory of a superconducting qubit environment*, Physical Review Letters, accepted October 28, 2026, DOI [10.1103/j1r2-5ph7](https://doi.org/10.1103/j1r2-5ph7).

The article measures non-Poissonian quantum-jump histories to distinguish a hidden long-lived two-level system from a memoryless bath. That physical model does not contain the original S3 Yang–Mills Wilson Hamiltonian. The separate exact mathematical transfer here is to retain and compare **a sequence of spectral correlation moments** in the actual source rather than only the previous unfiltered signed first moment. This is not a claimed fit of the paper or an assertion that Yang–Mills has an environmental TLS.

## Original authenticated source

This experimental PR is stacked on [Stage N PR #264](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/264), which itself uses the original source in merged #180. It does **not** modify the Hamiltonian or observable. Stage N reconstructs the periodic 3×4 S3 8 flat + 155,378 K3 states with 1,985,218 exterior shell-4 orbit targets and the original seven-loop / 24-link Wilson observable. It constructs the rational original fixed approximate ground witness \`phi\`, with W-positive orbit weights, and the exactly phi-centered vector \`v=(<phi,phi>_W O-<phi,O phi>_W)phi\`.

Stage N computed \`<v,Hv>_W\` from the full physical original source; its one-sided unfiltered positive-moment sufficiency test returned **negative**, so the original first-excitation Wilson spectral weight remains **HOLD**.

## New exact calculation

Apply **the actual original physical H** to every coordinate of \`v\`. On the flat and K3 supports use the genuine electric CSR matrix and flat/Q coupling; on the shell-4 exterior compute every weighted coupling. Verify the W-adjoint bilinear identity \`<v,Hv>_W\` by an independent row-action contraction against Stage N's original first-moment function. Then calculate the **new actual second moment**

    m0 = <v,v>_W
    m1 = <v,Hv>_W
    m2 = <Hv,Hv>_W = <v,H² v>_W,

including **all** shell-4 physical H-action coordinates. This is an exact integer construction, with no truncated high-energy tail in \`m2\`.

With accepted source-wide bound \`0 <= H <= 468 I\`, set \`T=468 I-H\`, and record exact two- and one-step correlation moments

    C0=m0,
    C1=<v,T v>_W=468 m0-m1,
    C2=<v,T² v>_W=468² m0-2*468 m1+m2.

Check \`0 <= C1 <= 468 C0\`, \`0 <= C2 <= 468 C1\`, and \`C0*C2 >= C1²\` using only signed integers. The mean energy after one low-pass weighting is \`468-C2/C1\`, and the original mean energy is \`m1/m0\`; the exact Cauchy-Schwarz inequality ensures the former cannot exceed the latter. This is an observable-correlator measurement on the **original physical model and original fixed trial**, rather than on a synthetic diagonal matrix.

## Scientific acceptance boundary

The second moment alone **does not isolate the first-excitation spectral projection**. The trial \`phi\` remains an approximate ground vector, so the centered \`v\` is not exactly orthogonal to the *true* physical ground. Future filtering also needs certified \`E3\`-through-high-sector tail suppression and true-ground error control; one cannot infer a positive E2 weight simply from \`C2>0\`. Stage N's historical negative one-sided signed moment also remains on record. This PR cannot change issue #137 from HOLD absent a source-certified strict first-excitation lower bound.

Independent \`verify.py\` checks the integer moment identities, immutable source scope, canonical hashes, the weighted spectral inequalities, and five tampered receipts. The producer also verifies the first-moment bilinear identity by a second original H-action route. A full independent graph reconstruction remains a separate reviewer obligation; these checks are not represented as one.

## Run

    python3 -I -B independent/y137-prl-original-wilson-filter-20261118/moment_filter.py toy
    python3 -I -B independent/y137-prl-original-wilson-filter-20261118/moment_filter.py real > FILTER.hbp
    python3 -I -B independent/y137-prl-original-wilson-filter-20261118/verify.py FILTER.hbp

Status: original finite 3×4 S3 first-gap certificate source-conditionally PASS; original E1→E2 seven-loop Wilson weight HOLD; 4D continuum Yang–Mills theorem OPEN.
