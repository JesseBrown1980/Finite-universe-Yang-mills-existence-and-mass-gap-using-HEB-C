#!/usr/bin/env python3
"""Integer-only SHA experiment: content keys are NOT spectral measurements.

A changed input SHA never implies inertia. Exact monotonicity between two
already certified Sturm anchors MAY infer inertia for a different coupling,
without new elimination, on this SAME finite 1393-state S3 Hamiltonian.

Accepted interpolation: JE=10, 20 <= JB <= 25, T=180000 (in 1/1000 units).
Reason:
E1(1,2)>18250/1000 -> E1(10,20)>182500/1000
E0(2,5)<34400/1000 -> E0(10,25)<172000/1000
M >= 0, so E0(10,JB)<=E0(10,25) and
E1(10,JB)>=E1(10,20) when 20<=JB<=25.
Therefore E0(10,JB)<180000/1000<E1(10,JB) (inertia=1).

The hash is only a canonical identifier; it cannot predict inertia.
"""
import hashlib
import sys
from pathlib import Path

from seat_translation_sectors import EXPECTED_BLOCK_SHA, EXPECTED_OPERATOR_SHA

HERE = Path(__file__).resolve().parent
ANCHOR_PATH = HERE / "seat_translation_pilot.measure"

def anchors_ok():
    source = ANCHOR_PATH.read_text(encoding="ascii").splitlines()
    expected = (("1", "2", "18250"), ("2", "5", "34400"))
    assert len(source) == 4
    for je, jb, t in expected:
        hit = [x for x in source if
               f"|JE={je}|JB={jb}|threshold={t}/1000|" in x]
        assert len(hit) == 1
        assert "|pivots=1393/1393|negative=1|" in hit[0]
        assert "|ambiguous=0|" in hit[0] and hit[0].endswith("|json=0")
    return hashlib.sha256(ANCHOR_PATH.read_bytes()).hexdigest()

def matrix_hash(folder, je, jb, t):
    """Hash real weighted-symmetric integer Sturm input, not the key string."""
    fingerprints = []
    for name in ("pp", "pm", "mp", "mm"):
        path = folder / (name + ".matrix")
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == EXPECTED_BLOCK_SHA[name]
        toks = raw.split()
        n = int(toks[0])
        assert n in (385, 336)
        weight = list(map(int, toks[1:n+1]))
        magnetic = list(map(int, toks[n+1:2*n+1]))
        rest = toks[2*n+1:]
        assert len(rest) % 3 == 0 and len(weight) == len(magnetic) == n
        out = hashlib.sha256()
        out.update(b"HEBC-EXACT-WEIGHTED-STURM-MATRIX-V1\n")
        out.update((name + "|" + str(n) + "\n").encode("ascii"))
        # Canonical upper triangle: hash actual integer matrix entries,
        # including all zeros on the diagonal as explicit cells.
        diag_found = set()
        for k in range(0, len(rest), 3):
            i, j, e = map(int, rest[k:k+3])
            assert 0 <= i <= j < n
            v = weight[i] * (1000 * je * e)
            if i == j:
                v += weight[i] * (1000 * jb * magnetic[i] - t)
                diag_found.add(i)
            out.update(f"{i}|{j}|{v}\n".encode("ascii"))
        assert len(diag_found) == n
        fingerprints.append(out.hexdigest())
    h = hashlib.sha256()
    h.update(("HEBC-DIRECT-SUM-V1|operator=" + EXPECTED_OPERATOR_SHA
             + "|JE=" + str(je) + "|JB=" + str(jb)
             + "|threshold=" + str(t)
             + "|part_sha=" + "|".join(fingerprints) + "\n").encode("ascii"))
    return h.hexdigest()

def proof_transport(folder, jb, t):
    assert type(jb) is int and type(t) is int
    witness_sha = anchors_ok()
    old_sha = matrix_hash(folder, 10, 20, 180000)
    new_sha = matrix_hash(folder, 10, jb, t)
    print("HEBC-SHA-EXPERIMENT|result=PASS|mode=HASH_ONLY|"
          f"reference_couplings=10,20|target_couplings=10,{jb}|"
          f"old_sturm_input_sha={old_sha}|new_sturm_input_sha={new_sha}|"
          f"same_hash={int(old_sha==new_sha)}|"
          "cached_measurement_for_new_key=NONE|"
          "inertia_from_hash=UNKNOWN|json=0")
    if not 20 <= jb <= 25 or t != 180000:
        print("HEBC-SHA-EXPERIMENT|result=REFUSED|mode=PROOF_TRANSPORT|"
              "reason=OUTSIDE_PINNED_INTEGER_COUPLING_CELL|"
              "negative_from_hash=UNKNOWN|json=0")
        return 2
    e0_upper = 34400 * 5
    e1_lower = 18250 * 10
    assert e0_upper == 172000
    assert e1_lower == 182500
    assert e0_upper < t < e1_lower
    assert old_sha != new_sha or jb == 20
    print("HEBC-SHA-EXPERIMENT|result=PASS|mode=ORDER_THEOREM|"
          f"target_couplings=10,{jb}|threshold={t}/1000|"
          f"E0_strict_lt={e0_upper}/1000|E1_strict_gt={e1_lower}/1000|"
          f"negative=1|original_anchors_sha={witness_sha}|"
          "method=INTEGER_CROSS_MULTIPLICATION_AND_M_PSD|"
          "new_sturm_pivots_executed=0|"
          "scope=FINITE_S3_2X2_ONLY|json=0")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: seat_sha_measure_experiment.py SECTOR_DIR JB T_NUM")
    try:
        sys.exit(proof_transport(Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])))
    except (AssertionError, ValueError, OSError) as exc:
        print(f"HEBC-SHA-EXPERIMENT|result=FAIL|reason={type(exc).__name__}|json=0")
        sys.exit(2)
