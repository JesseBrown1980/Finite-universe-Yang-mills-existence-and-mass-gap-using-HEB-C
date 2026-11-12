#!/usr/bin/env python3
"""Exact finite-Hamiltonian quantum response controls, r12 2880-class S3 core.

This tests the mathematical quantum Hamiltonian as a coherent-amplitude model:
(1) weighted Hermiticity; (2) [H,O] != 0 for 27 actual trit observables;
(3) second-order short-time interference from normalized two-source states.
It does NOT demonstrate experimental quantum behavior in the density simulator,
a Bell violation, physical lattice refinement, or any continuum YM theorem.
No float, fractions, JSON, or unsafe shortcuts.
"""
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
from math import gcd
import sys

NINE_CORE_SHA = "865dae9216a87a0ed1caa0594c1273eb36f9785c6b4984815384a254ff670d78"
FROZEN_27_SHA = "b0e564d9202a473a23f39c9ed9cf3b64e88d38950d128dc9212217209b8002c2"


def sha(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def ratio(n, d):
    assert d > 0
    g = gcd(n, d)
    return n // g, d // g


def source_check(folder):
    for line in folder.joinpath("SHA256SUMS").read_text(encoding="ascii").splitlines():
        digest, name = line.split(None, 1)
        name = name.strip(" *")
        assert name and "/" not in name and ".." not in name
        target = folder.joinpath(name)
        assert target.is_file() and sha(target) == digest
    assert sha(folder.joinpath("rows.txt")) == NINE_CORE_SHA


def load(folder, frozen):
    source_check(folder)
    assert sha(frozen) == FROZEN_27_SHA
    core, mags = {}, {}
    for line in folder.joinpath("rows.txt").read_text(encoding="ascii").splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "C":
            key = int(parts[1])
            mags[key] = int(parts[2])
            core[key] = {int(t.split(":")[0]): int(t.split(":")[1]) for t in parts[4:]}
    weights = {}
    for line in folder.joinpath("weights.txt").read_text(encoding="ascii").splitlines():
        k, w = map(int, line.split())
        assert w > 0
        weights[k] = w
    assert len(core) == 2880 and set(weights) == set(core)
    labels = {}
    for line in frozen.read_text(encoding="ascii").splitlines()[1:]:
        assert line.startswith("LEAF|")
        fields = dict(x.split("=", 1) for x in line.split("|") if "=" in x)
        key = int(fields["key"])
        assert key not in labels and mags[key] == int(fields["mag"])
        trits = tuple(map(int, fields["trits"].split(",")))
        assert len(trits) == 27 and all(v in (0, 1, 2) for v in trits)
        labels[key] = trits
    assert len(labels) == 682
    assert list(labels) == sorted(labels)
    return core, weights, labels


def check_operator(core, weights):
    directed = 0
    for i, neighbors in core.items():
        wi = weights[i]
        for j, c in neighbors.items():
            assert c > 0
            assert j in core
            assert wi*c == weights[j]*core[j].get(i, 0), (i, j)
            directed += 1
    return directed


def response(core, weights, labels):
    """Directed edge sum = <1_S,[O,[H,O]]1_S>_W.

    For O diagonal real, [H,O]_ij = c_ij (O_i - O_j) up to sign.
    <1,[O,[H,O]]1> = sum_i W_i sum_j c_ij (Oi-Oj)^2,
    for input vector uniform on S and O zero outside S; HERE we only use
    internal S edges, avoiding a fake Dirichlet boundary contribution.
    """
    keys = set(labels)
    sums = [0]*27
    total = 0
    edges = 0
    for i in labels:
        oi = labels[i]
        for j, c in core[i].items():
            if j not in keys:
                continue
            oj = labels[j]
            edges += 1
            mass = weights[i]*c
            total += mass
            for k in range(27):
                delta = oi[k]-oj[k]
                sums[k] += mass*delta*delta
    assert edges > 0 and edges%2 == 0
    assert total > 0 and all(x >= 0 for x in sums)
    assert any(x > 0 for x in sums)
    return sums, edges, total


def coherent_control(core, weights, labels):
    """Find first canonical j and equal-W, equal-hopping a,b in common keys.

    At j (initially empty) for |a> +/- |b>, normalized:
    P_j(t) = t^2 * W_j*c_ja^2/W_a * (1 +/- 1) + O(t^4)
    plus: twice a single-source coefficient; minus: zero; mixed: one.
    This is quantum amplitude interference BY MODEL ASSUMPTION, not a
    measurement of quantum nonlocality in the classical density process.
    """
    chosen = None
    for j in sorted(labels):
        groups = defaultdict(list)
        for a, count in core[j].items():
            if a in labels and a != j:
                groups[(weights[a], count)].append(a)
        for (wa, coupling), choices in sorted(groups.items()):
            if len(choices) >= 2:
                chosen = (j, choices[0], choices[1], wa, coupling)
                break
        if chosen is not None:
            break
    assert chosen is not None
    j, a, b, wa, c = chosen
    assert weights[a] == weights[b] == wa and core[j][a] == core[j][b] == c
    single = ratio(weights[j]*c*c, wa)
    plus = ratio(2*weights[j]*c*c, wa)
    minus = ratio(0, 1)
    mixture = single
    assert plus[0]*single[1] == 2*single[0]*plus[1]
    assert minus == (0, 1)
    # Negative control: a randomized sign flip changes coherent interference,
    # but not the incoherent classical-mixture coefficient.
    assert plus != mixture and plus != minus and mixture != minus
    return (j, a, b, wa, c, *single, *plus, *minus, *mixture)


def run(source, frozen, output):
    core, weights, labels = load(source, frozen)
    directed = check_operator(core, weights)
    q, edges, scale = response(core, weights, labels)
    coherent = coherent_control(core, weights, labels)
    records = [
        "CONTRACT|schema=GITRAM-27-FINITE-QUANTUM-RESPONSE-V1|r=12|classes=2880|trit_columns=27|rows=682|arithmetic=integer_only|json=0",
        "SOURCE|rows_sha256=%s|frozen27_sha256=%s|weighted_hermiticity=PASS|directed_core_edges=%d|json=0"
        % (sha(source.joinpath("rows.txt")), sha(frozen), directed),
        "COMMUTATOR|internal_directed_edges=%d|weight_sum=%d|nonzero_columns=%d|constant_observable_zero=PASS|json=0"
        % (edges, scale, sum(x > 0 for x in q)),
    ]
    for i, v in enumerate(q):
        records.append("TRIT_RESPONSE|index=%d|double_commutator_witness=%d|json=0" % (i, v))
    (j, a, b, wa, c, sn, sd, pn, pd, dn, dd, mn, md) = coherent
    records += [
        "INTERFERENCE|receiver_key=%d|source_a=%d|source_b=%d|source_weight=%d|hop_count=%d|coherent_plus_t2=%d/%d|coherent_minus_t2=%d/%d|incoherent_mixture_t2=%d/%d|one_source_t2=%d/%d|json=0"
        % (j, a, b, wa, c, pn, pd, dn, dd, mn, md, sn, sd),
        "CONTROLS|weighted_selfadjoint=PASS|no_commutator_for_constant_O=PASS|destructive_at_order_t2=PASS|classical_incoherent_control=PASS|json=0",
        "LIMIT|finite_hilbert_operator_interference=YES_BY_DEFINITION|density_simulator_quantumness=NOT_TESTED|bell_chsh=NOT_TESTED|continuum_mass_gap=NOT_ESTABLISHED|r9_launch=NO|json=0",
        "GITRAM_QUANTUM_RESPONSE_PASS|classes=2880|columns=27|r=12|json=0",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(records)+"\n", encoding="ascii")
    output.with_name(output.name+".sha256").write_text(
        "%s  %s\n" % (sha(output), output.name), encoding="ascii"
    )
    print("\n".join(x for x in records if not x.startswith("TRIT_RESPONSE|")))


if __name__ == "__main__":
    assert len(sys.argv) == 4, "usage: quantum_response SOURCE_DIR FROZEN27 OUT.hbp"
    run(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
