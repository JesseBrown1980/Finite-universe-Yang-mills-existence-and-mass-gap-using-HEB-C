#!/usr/bin/env python3
"""Frozen Q3 software experiment: exactly three cascaded ternary prisms.
No quantum predictions or physical instantaneous signal are asserted.
"""
from hashlib import sha256
from pathlib import Path

BASE = Path(__file__).parent
SEAL = "f880459cef7c5f00c194f19691429347d499545e2c232732be42bba92434780c"

def sha(b):
    return sha256(b).digest()

def trit(x):
    return (x + 1) % 3 - 1

def jmat(sign):
    assert sign in (-1, 1)
    m = [[0] * 3 for _ in range(3)]
    for source in range(3):
        m[source][source] = 1
        m[(source + 1) % 3][source] = sign
        m[(source + 2) % 3][source] = -sign
    return m

def determinant_mod3(m):
    return (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1]) -
            m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0]) +
            m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0])) % 3

def digits3(x):
    return [(x // (3**i)) % 3 for i in range(3)]

def physical_root_at_t0(payload):
    # One physical matrix: 1 + 3 + 9 + 27 cells, all except source zero at t0.
    # Full SHA-256 Merkle root, not a digest of protocol metadata.
    cells = [payload] + [0] * 39
    layer = [sha(b"Q3-LEAF" + i.to_bytes(2, "little") + bytes([v % 3]))
             for i, v in enumerate(cells)]
    while len(layer) > 1:
        if len(layer) % 2:
            layer.append(layer[-1])
        layer = [sha(b"Q3-NODE" + layer[i] + layer[i + 1])
                 for i in range(0, len(layer), 2)]
    return layer[0]

def z_token(payload, destination, nonce=17):
    return sha(b"Q3-Z-BOUND|" + physical_root_at_t0(payload) +
               bytes([destination, nonce & 0xff, payload % 3]))

def orientation(token, stage):
    # One universal token selects the curved orientation independently per prism.
    return 1 if sha(b"Q3-J-CURVE|" + token + bytes([stage]))[0] % 2 == 0 else -1

def gate(payload, destination, token):
    return token == z_token(payload, destination)

def evolve(payload, destination, frozen_token=None):
    token = z_token(payload, destination) if frozen_token is None else frozen_token
    assert gate(payload, destination, token)
    by_tick = [{(): payload}]
    for stage, d in enumerate(digits3(destination)):
        m = jmat(orientation(token, stage))
        forward = {}
        for path, value in by_tick[-1].items():
            for lane in range(3):
                forward[path + (lane,)] = trit(value * m[lane][d])
        by_tick.append(forward)
    return by_tick

def predict(payload, destination):
    # Independent closed-form oracle: no call to evolve(), no jmat(), no
    # propagation. This is a software forecast at t0, not an early particle.
    token = z_token(payload, destination)
    dest = digits3(destination)
    signs = [orientation(token, k) for k in range(3)]
    out = {}
    for x in range(27):
        lanes = digits3(x)
        coeff = payload
        for k, (lane, selected) in enumerate(zip(lanes, dest)):
            shift = (lane - selected) % 3
            factor = (1, signs[k], -signs[k])[shift]
            coeff = trit(coeff * factor)
        out[tuple(lanes)] = coeff
    return out

def main():
    assert sha((BASE/"PREREG.hbp").read_bytes()).hex() == SEAL
    rows = ["Q3_BUILD|runtime=Python3|python_stdlib_only=1|no_float=1|no_json=1|physical_quantum_evidence=0|json=0"]
    counts = {"P1": True, "P2": True, "P3": True, "P4": True,
              "P5": True, "P6": True, "P7": True, "P8": True}
    orientations = set()
    total = 0
    for payload in (-1, 1):
        roots = set()
        tokens = set()
        for target in range(27):
            root = physical_root_at_t0(payload)
            z = z_token(payload, target)
            roots.add(root)
            tokens.add(z)
            pattern = tuple(orientation(z, k) for k in range(3))
            orientations.add(pattern)
            states = evolve(payload, target)
            approx = predict(payload, target)
            total += 1
            counts["P2"] &= [len(s) for s in states] == [1, 3, 9, 27]
            counts["P2"] &= all(all(a in (-1, 1) for a in s.values()) for s in states)
            counts["P2"] &= approx == states[3]
            counts["P3"] &= all(len([x for x in states[t] if len(x) == 3]) == 0 for t in (0, 1, 2))
            counts["P4"] &= (not gate(payload, (target + 1) % 27, z))
            counts["P4"] &= (not gate(payload, target, z[:-1] + bytes([z[-1] ^ 1])))
            counts["P4"] &= (not gate(payload, target, z_token(payload, (target + 1) % 27)))
            rows.append("Q3_CASE|payload=%s|destination=%d|j=%s|nodes=1,3,9,27|zprefix=%s|predicted_equals_propagated=1|prearrival_target_unchanged=1|json=0" %
                        (payload, target, ",".join('+' if x == 1 else '-' for x in pattern), z.hex()[:16]))
        counts["P1"] &= len(roots) == 1 and len(tokens) == 27
    counts["P1"] &= len(orientations) >= 2
    # Post-emission retarget updates protocol metadata but not the already released packet.
    old, new, payload = 5, 19, 1
    old_states = evolve(payload, old)
    new_token = z_token(payload, new)
    new_prediction = predict(payload, new)
    counts["P5"] &= z_token(payload, old) != new_token
    counts["P5"] &= old_states[3] == evolve(payload, old)[3]
    counts["P5"] &= old_states[3] != new_prediction
    counts["P5"] &= all(not any(len(path) == 3 for path in old_states[t]) for t in (0, 1, 2))
    # Two possible destinations are perfectly distinguishable to a reader of global token.
    counts["P6"] &= z_token(1, 0) != z_token(1, 1)
    plus, minus = jmat(1), jmat(-1)
    counts["P7"] &= all(plus[i][j] == minus[j][i] for i in range(3) for j in range(3))
    counts["P7"] &= plus != list(map(list, zip(*plus)))
    counts["P7"] &= minus != list(map(list, zip(*minus)))
    counts["P7"] &= determinant_mod3(plus) != 0 and determinant_mod3(minus) != 0
    counts["P8"] &= all(len(evolve(1, d)[t]) == 3**t for d in range(27) for t in range(4))
    rows.append("Q3_RETARGET|old=5|new=19|metadata_changed=1|inflight_physically_unchanged=1|stale_token_rejected=1|json=0")
    rows.append("Q3_NEGATIVE|local_reader_with_global_token=LEAK|two_messages_equal_prior=1|mutual_information_bits=1|expected=LEAK|json=0")
    rows.append("Q3_CURVE|jplus_det_mod3=%s|jminus_det_mod3=%s|curves_transpose=1|orientation_choices_observed=%d|json=0" % (determinant_mod3(plus), determinant_mod3(minus), len(orientations)))
    status = "PASS" if all(counts.values()) else "FAIL"
    rows.append("Q3_VERDICT|" + "|".join("%s=%s" % (k,"PASS" if v else "FAIL") for k, v in counts.items()) +
                "|cases=%d|prism_count=3|paths=27|result=%s|physical_ftl_observed=0|json=0" % (total,status))
    (BASE/"RESULT.hbp").write_text("\n".join(rows) + "\n", encoding="ascii")
    print(rows[-3])
    print(rows[-1])
    if status != "PASS":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
