# Experiment: can changing the SHA supply a new measurement?

**Short answer: No.** SHA-256 is a deterministic content fingerprint, not a stored spectral function. Changing its bits does not change a Hamiltonian in a mathematically controlled way, reveal missing matrix entries, or provide its eigenvalue/inertia. Replacing the old SHA field with a new string is merely a changed label unless accompanied by the actual matrix and independent verification.

**Useful shortcut: Yes, sometimes.** Two existing full integer Sturm certificates on the same finite 1,393-state S₃ torus can imply an exact new inertia result by *operator order*. This is faster than a new matrix elimination, but the mathematical theorem—not SHA—supplies the missing information.

## Concrete same-operator experiment (integer only)

Existing PR #14 pinned full-block interval Sturm results:

- `(JE,JB)=(1,2)`, `T=18250` in thousandths: exactly one eigenvalue below `18250/1000`. Thus `E1(1,2)>18250/1000`.
- `(JE,JB)=(2,5)`, `T=34400`: exactly one eigenvalue below `34400/1000`. Thus `E0(2,5)<34400/1000`.

By **homogeneity of the same Hamiltonian**,

- `E1(10,20)>182500/1000`, scaling the first operator by 10.
- `E0(10,25)<172000/1000`, scaling the second by 5.

The magnetic operator is positive semidefinite, so the two ordered eigenvalues are nondecreasing as JB increases while JE stays fixed. Therefore, for every integer `20<=JB<=25`,

`E0(10,JB) <= E0(10,25) < 172000/1000 < 180000/1000 < 182500/1000 < E1(10,20) <= E1(10,JB)`.

Consequently the shifted 1,393-state Hamiltonian at each such **new** coupling has **exactly one negative eigenvalue below `180000/1000`**. No new 1,393-pivot elimination is required to infer this fact. The gaps are guaranteed greater than `(182500-172000)/1000 = 10500/1000` in the stated JE=10 units.

The proof uses only integer multiplication and comparison. The actual matrix SHA for `(10,20)`, `(10,23)`, and `(10,25)` will be different; the new SHA is not used to derive inertia.

## Executable comparison

```bash
python3 independent/seat_translation_sectors.py /tmp/sha-sector
python3 independent/seat_sha_measure_experiment.py /tmp/sha-sector 20 180000
python3 independent/seat_sha_measure_experiment.py /tmp/sha-sector 23 180000
python3 independent/seat_sha_measure_experiment.py /tmp/sha-sector 25 180000
# This MUST fail closed: outside pinned operator-order region.
python3 independent/seat_sha_measure_experiment.py /tmp/sha-sector 26 180000

# Independent direct check on the new coupling:
python3 independent/seat_translation_sturm.py /tmp/sha-sector 10 23 180000 30 1
```

The test hashes the **actual weighted-symmetric integer shifted matrix contents** for all four translation sectors, including all parameters and operator SHA. Merely mutating a stored digest cannot satisfy the actual content check, and a new unseen hash never produces a cached spectral result. A valid complete prior measurement can be reused when its *unchanged original* input fingerprint and provenance match; a new result may be inferred only where a separate rigorous theorem supports it.

## What this does not establish

This shortcut transfers some certified *inequalities and inertia counts* across nearby couplings. It does not reconstruct the complete eigenspectrum, prove all new thresholds at unseen couplings, produce actual new physics measurements, derive 4D continuum Yang–Mills, or replace future exact Sturm checks outside rigorously bounded regions.

Every calculation uses Python integers and SHA-256. No `Fraction`, float or JSON. This is a separated draft experiment; PR #14 and earlier draft branches remain unmerged.
