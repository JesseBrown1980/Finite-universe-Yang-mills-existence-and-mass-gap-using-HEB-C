# Independent verifier

[`indep_verify.py`](indep_verify.py) is a second implementation of the finite
S₃ gauge Hamiltonian and of the inertia count, written separately from the
production tools (`torusl`/`ymsec`, `flatcomp`, `cluster`, `shellschur`). It
imports none of them, and it uses integer arithmetic only.

- **Basis.** A spanning tree is gauge-fixed to the identity. Each gauge orbit
  is a conjugation class of the non-tree link tuple, labelled by its least
  member and weighted by the size of that class.
- **Hamiltonian.** H = E + r·M, built from its definition. E is the Cayley
  Laplacian of the three transpositions on every link. M is Σ (2 − χ(U_p)) over
  the plaquettes, with χ the real character of the standard representation.
  The move counts are checked to make W·A symmetric.
- **Count.** The number of eigenvalues below t is the number of negative
  eigenvalues of B = W(10⁶ A) − t·W. That is the number of sign changes in the
  leading principal minors of a randomly permuted B. Each minor is computed
  modulo 31-bit primes past twice its Hadamard bound and reconstructed by CRT.

It checks the full operator, without symmetry reduction, against the
production full-space counts.

```bash
python indep_verify.py 2 2 9 23746649,46576000,90123457
```

On November 3 its two floating-point square roots became `math.isqrt`, on the operator's word that floating point is to be redone in integers. They run on the Python path, so [`indep_sqrt_check.py`](indep_sqrt_check.py) runs them side by side with the recorded commit's file, and they read the same on every real input, in [`INDEPENDENT-2X2-R9-INTEGER.hbp`](../results/independent/INDEPENDENT-2X2-R9-INTEGER.hbp). The earlier receipt keeps its commit and its code hash.
