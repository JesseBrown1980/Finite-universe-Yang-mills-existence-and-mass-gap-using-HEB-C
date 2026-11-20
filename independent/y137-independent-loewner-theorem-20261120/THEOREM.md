# Independent exact matrix four-moment Loewner proof for the original finite Schur enclosure

**2026-11-20 · Issue #137 · mathematical proof review.** This establishes the abstract finite-dimensional **matrix** Gauss/Lobatto bound used for the original signed four-moment Yang–Mills Schur calculation. It is applicable to the authentic full-Q source once its original Hamiltonian self-adjointness, spectral support interval and source moment equalities have been accepted. Those original finite numerical checks have existing separately hosted evidence; they remain independent premises of this lemma.

## Precise mathematical statement

Let `X=X* > 0` act on a finite-dimensional real/complex inner-product space with a **proved entire-Q spectral enclosure** `0 < g I <= X <= h I`, `g<h`. Let `V` map an (m)-dimensional source space into the Q Hilbert space, and let

[
mu_k = V^* X^k V,quad k=0,1,2,3,
qquad F=V^*X^{-1}V.
]

All `mu_k` are Hermitian. Put

[
K=egin{pmatrix}mu_1&mu_2\mu_2&mu_3end{pmatrix},
quad T=(mu_0 mu_1),
quad
b=(g+h)mu_1-mu_2-ghmu_0,
quad
c=(g+h)mu_2-mu_3-ghmu_1.
]

Assume `K` is strictly positive definite and `c` strictly positive definite. Then the following **Loewner** matrix inequalities hold, with no scalar reduction or commutativity requirement between the moment matrices:

[
oxed{quad
T K^{-1}T^* preceq Fpreceqrac{(g+h)mu_0-mu_1-bc^{-1}b}{gh}
quad}
]

Consequently, for any given Hermitian flat bilinear matrix `U0`, with the actual physical original Schur matrix `S=U0-F`,

[
oxed{quad U_0-F_{mathrm{Lobatto}}
preceq S
preceq U_0-F_{mathrm{Gauss}}quad}.
]

These are exactly the orientations in the source's `bracket4` calculation.

## Preliminary localizer theorem — the exact admissible signed fourth moment

For the same `C=[V,XV]`, the two endpoint localizer matrices are themselves Hilbert-space Grams:

[
G_g=C^*(X-gI)C=
egin{pmatrix}
mu_1-gmu_0 & mu_2-gmu_1\
mu_2-gmu_1 & mu_3-gmu_2
end{pmatrix}succeq0,
]

[
G_h=C^*(hI-X)C=
egin{pmatrix}
hmu_0-mu_1 & hmu_1-mu_2\
hmu_1-mu_2 & hmu_2-mu_3
end{pmatrix}succeq0.
]

Assume their upper-left blocks `D=mu1-g mu0` and `E=h mu0-mu1` are strictly positive definite. Their exact **matrix** Schur complements give a necessary whole-Q fourth-moment window:

[
gmu_2+(mu_2-gmu_1)D^{-1}(mu_2-gmu_1)
preceqmu_3
preceq
hmu_2-(hmu_1-mu_2)E^{-1}(hmu_1-mu_2).
]

This proves the source's `mu3_acceptance.window` inequalities and their orientations with no commutativity assumption between `mu0`, `mu1`, `mu2` and `mu3`. The two archived signed full-Q 16×16 original localizers can be checked directly by exact integer principal minors or a valid fraction-free LDL factorization. They are **necessary source-consistency checks**. Actual equality with the Hamiltonian's full-Q signed `mu3` requires the separately accepted complete physical matrix reconstruction, and is *not* inferred merely from being within this window.

## Proof A — matrix Gauss lower bound by the full Hilbert Gram

Consider the trial operator `C=[V, XV]` mapping two copies of the (m)-space into Q. Its `X`-weighted Gram is

[
C^*XC
=egin{pmatrix}mu_1&mu_2\mu_2&mu_3end{pmatrix}
=K,
]

and `V*C=T`. The Gram of `X^(-1/2)V` and `X^(1/2)C` is positive semidefinite:

[
egin{pmatrix}
V^*X^{-1}V & V^*C\
C^*V & C^*XC
end{pmatrix}
=
egin{pmatrix}F&T\T^*&Kend{pmatrix}succeq0.
]

Since `K ≻ 0`, its Schur complement gives `F-T K^(-1)T* >= 0`. This is a **full matrix inequality**: every complex or real source direction is covered simultaneously.

## Proof B — endpoint-weighted matrix Lobatto upper bound

Define the positive self-adjoint operator

[
Y=(X-gI)(hI-X)succeq0.
]

Because `Y` is a polynomial in `X`, it commutes with `X`, `X^(-1)` and their square roots. Its source quadratic forms are exactly

[
egin{aligned}
A&=V^*YX^{-1}V=(g+h)mu_0-mu_1-gh F,\
b&=V^*YV=(g+h)mu_1-mu_2-ghmu_0,\
c&=V^*YX V=(g+h)mu_2-mu_3-ghmu_1.
end{aligned}
]

The Gram of `Y^(1/2)X^(-1/2)V` and `Y^(1/2)X^(1/2)V` is

[
egin{pmatrix}A&b\b&cend{pmatrix}succeq0.
]

The strict condition `c ≻ 0` implies `A-b c^(-1)b >= 0`. Substituting the exact expression for `A` and dividing by the *positive* scalar `gh` proves the claimed **upper** bound for `F`. Subtracting from `U0` reverses the order in the proper way, giving the correct lower Schur bracket. There is no appeal to an unproved scalar quadrature analogue, and no approximation.

## True energy branch and normalized eigenprojector use

For original `H=[[A,B*],[B,D]]`, `D>=gamma` and real `z<gamma`, the exact Schur operator satisfies

[
S(z)=A-zI-B^*(D-zI)^{-1}B,qquad
S'(z)=-I-B^*(D-zI)^{-2}Bpreceq-I.
]

The block congruence gives `inertia_-(H-zI)=inertia_-(S(z))`. Strict signed endpoint inertia changes `0→1` and `1→2` on separated original energy windows therefore isolate one simple eigenvalue in each window, provided the endpoint matrices are nonsingular and the full original physical P/Q operator and entire-Q floor have the stated properties. The exact source's W-flat bilinear conversion is by a fixed invertible positive weight congruence, under which all Loewner statements and inertia counts remain true.

The `U0`, `mu0..mu3`, full-Q support bounds `g,h`, and original P/Q W congruence are **physical provenance premises**. The separate signed full-state `mu3` independent run #44581486671, original Stage C/K3/Q4/Q5 full source chain (PRs #331 and #335), and independently authored source Schur matrix localizer arithmetic (`schur.py` in PR #317) provide the current finite numerical evidence. This abstract proof establishes the logical Loewner implication once those premises are accepted; it does not authenticate the full-Q Perron 34-sector archive.

## Finite source acceptance and remaining review

The existing independent signed four-moment source audit builds both actual **16×16** positive moment localizer Grams from the original SHA-verified 8×8 moments and checks strict positive pivots and all rational Schur matrix entries. The original physically signed full-state `mu3` matrices were separately calculated independently. Those checks allow the proof above to be applied **conditional on original source authentication, whole-Q support and physical metric identity**.

The [exact integer scalar witness](test_scalar.py) checks that `F_Gauss < F_true < F_Lobatto`, that Schur subtraction reverses both bounds, and that changed/missing support or inverted inequalities are rejected. It is a negative-control verification of the theorem's sign, distinct from the matrix proof itself.

**Acceptance status:** abstract matrix Loewner bound **THEOREM PROVED** under stated assumptions, original finite signed source/Schur arithmetic **SOURCE-CONDITIONAL**, final original first-Wilson squared spectral-weight positivity **FORMAL HOLD** until entire-Q Perron store source acceptance and independent original physical/theorem premise review. The four-dimensional continuum problem remains **OPEN**.
