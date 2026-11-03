# Cantor-27 S3 response — isolated numerical experiment

**Scope:** reproduces a 729-slot 27 Hz / 27 second signal schedule, applied to the existing finite S3 lattice-gauge sector. Time evolution uses dt=1/27 in arbitrary units with hbar=1. This is **not** a physical 27-second calibration or a spectral-gap certificate.

The original signal is [CANTOR-729-TRITS.bin](https://github.com/JesseBrown1980/AAAAAAAAAAAAAA-Quantum-observations-of-hidden-model-states/blob/main/cantor27/CANTOR-729-TRITS.bin), SHA-256 1f48fa5083237cd4bdadc3f6c4f9094b864ca1386d7d09b5b27c19b5f27f6913. The script independently regenerates its exact 729 bytes, rejecting any changed source. There are 32 positive, 32 negative, and 665 free-zero slots. Trit 2 is defined to mean a negative signed coupling; it is **not** a Z3 gauge-link operator.

The original ymsec matrix represents the S3 Hamiltonian H0=E+r M with exact integer upper-triangle electric entries, orbit weights, and diagonal magnetic energy M. It is already a gauge-invariant sector if built with the frozen ymsec implementation. This experiment applies the gauge-invariant magnetic perturbation:

    H_t = E + r M + lambda f(c_t) M,
    f(0)=0, f(1)=1, f(2)=-1,
    U_t = exp(-i dt H_t), psi_final = U_728 ... U_0 psi_initial.

For an upper entry z[i,j] and orbit weights w[i], w[j], the symmetric matrix uses E_ij = z[i,j] * sqrt(w[i]/w[j]). This follows from the existing exact self-adjointness equality w[i] z[i,j] = w[j] z[j,i]. The code checks that each reverse electric entry is integral, constructs the symmetric representation, diagonalizes each of three possible Hamiltonians, and applies their unitary matrices in sample order. Reversing the sequence with U_t adjoints checks numerical recovery. Null controls are zero drive, sign inversion, and deterministic one-slot rotation.

## Run on actual 2x2 (+,+) S3 sector

From repository root:

~~~sh
cd native/ym
cargo +1.81.0 build --release --offline --locked -p torusl --bin ymsec
./target/release/ymsec 2 2 1 1 /tmp/cantor-s22.matrix
python -m pip install numpy==2.3.5 scipy==1.17.0
OPENBLAS_NUM_THREADS=1 python python/cantor_s3_drive.py \
  --matrix /tmp/cantor-s22.matrix --out /tmp/cantor-s22-drive \
  --expected-matrix-sha 902a8a01d527416ea02d7ce54737fa5513d814046a6e9cdd7f9acf67cc864ccb
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s python -p 'test_cantor_s3_drive.py' -v
~~~

Outputs are reproducible, plain-text HBP science records and HBI per-line SHA-256 chains. Pass thresholds are absolute numerical tolerances, **not certified error intervals**. They use an unsigned generated SHA chain, not independent external authentication. The 211-state source sector is recorded in native/ym/results/2xL/22/shards/sector_2_2_1_1/run.hbp. The CI workflow runs the original matrix generator before this test; there is no 243-state Z3 substitution.

The finite drive and its controls do not prove the mass gap, volume uniformity, or continuum existence. Existing sealed S3 certificates are unchanged. Only after independent replay on the real generated matrix may its results be described as a checked finite S3 numerical response.
