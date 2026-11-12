#!/usr/bin/env python3
"""Nested powers-of-three readouts of one authenticated finite S3 wave proxy.

IMPORTANT: A readout leaf is a sampled CLASS ADDRESS, not a new independent
ternary measurement or an enlargement of the finite lattice. This preserves
the pinned r=12, cutoff-9, 2880-class operator and the original three sources.
The exact-rational reversible second-order recurrence is a wave DIAGNOSTIC,
not unitary Yang-Mills time evolution, a continuum limit, or a mass-gap proof.
No floats, no JSON, no r=9 invocation.
"""
from collections import deque
from pathlib import Path
import sys

import nine_leaf_play as base

LEVELS = (9, 27, 81, 243, 729, 2187)
OBSERVE = (0, 3, 6, 9)
DEN = base.D
SOURCE_RUN = base.SOURCE_RUN


def address_order(keys, mags, adj):
    """Deterministic graph BFS, retaining the original nine-address prefix.

    Exhaust any connected component before beginning another, explicitly
    recording the number of components. Graph order is NOT geometric space.
    """
    centre = min((i for i, m in enumerate(mags) if m == 3),
                 key=lambda i: keys[i])
    seeds = [centre] + sorted(range(len(keys)), key=lambda i: keys[i])
    order, seen, components = [], set(), 0
    for seed in seeds:
        if seed in seen:
            continue
        components += 1
        seen.add(seed)
        order.append(seed)
        queue = deque([seed])
        while queue:
            i = queue.popleft()
            neighbours = sorted((j for j in adj[i] if j not in seen and j != i),
                                key=lambda j: (mags[j], -adj[i][j], keys[j]))
            for j in neighbours:
                if j not in seen:
                    seen.add(j)
                    order.append(j)
                    queue.append(j)
    assert len(order) == len(keys)
    assert len(set(order)) == len(keys)
    return order, components


def forward(sources, mags, weights, adj):
    """Full 2880-component integer numerators; denominator DEN**t."""
    first = [
        [DEN*x - h for x, h in zip(v, base.apply(v, mags, adj))]
        for v in sources
    ]
    frames = [[v[:] for v in sources], first]
    energy = [
        base.energy_scaled(frames[0][a], frames[1][a], weights, mags, adj)
        for a in range(3)
    ]
    assert all(e > 0 for e in energy)
    for tick in range(1, 9):
        next_layer = []
        for a in range(3):
            now = frames[tick][a]
            prev = frames[tick-1][a]
            hv = base.apply(now, mags, adj)
            next_layer.append([
                2*DEN*x - h - DEN*DEN*y
                for x, h, y in zip(now, hv, prev)
            ])
            assert base.energy_scaled(now, next_layer[-1], weights, mags, adj) == (
                energy[a] * DEN ** (2*tick)
            ), ("energy", tick, a)
        frames.append(next_layer)
    assert len(frames) == 10

    # Rewind the ENTIRE operator state, not just the selected readouts.
    reconstructed = {9: [v[:] for v in frames[9]],
                     8: [v[:] for v in frames[8]]}
    for tick in range(8, 0, -1):
        layer = []
        for a in range(3):
            now = reconstructed[tick][a]
            ahead = reconstructed[tick+1][a]
            hv = base.apply(now, mags, adj)
            numerators = [2*DEN*x - h - y
                          for x, h, y in zip(now, hv, ahead)]
            assert all(x % (DEN*DEN) == 0 for x in numerators), (
                "inverse_divisibility", tick, a
            )
            layer.append([x // (DEN*DEN) for x in numerators])
        reconstructed[tick-1] = layer
        assert layer == frames[tick-1], ("inverse_mismatch", tick)
    assert reconstructed[0] == sources
    return frames


def metrics(indices, waves, weights, adj):
    """All ratios computed with integer arithmetic, never floats."""
    selected = set(indices)
    n = len(weights)
    full_norm = sum(weights[i] * sum(w[i]*w[i] for w in waves)
                    for i in range(n))
    local_norm = sum(weights[i] * sum(w[i]*w[i] for w in waves)
                     for i in indices)
    assert 0 < full_norm and 0 <= local_norm <= full_norm
    hits = sum(any(w[i] != 0 for w in waves) for i in indices)
    edge_count, frontier, rough = 0, 0, 0
    for i in indices:
        for j, c in adj[i].items():
            if j == i:
                continue
            if j in selected:
                if i < j:
                    edge_count += 1
                    rough += weights[i] * c * sum(
                        (w[i]-w[j])**2 for w in waves
                    )
            else:
                frontier += 1
    return (hits, edge_count, frontier,
            local_norm, full_norm, rough,
            (10**9 * local_norm) // full_norm,
            (10**6 * rough) // local_norm if local_norm else -1)


def run(source_dir, output):
    d = Path(source_dir)
    # load() independently authenticates the complete SHA256SUMS and source
    # row checksum, 2880 canonical keys, positive orbit weights, and balance.
    keys, mags, weights, adj = base.load(d)
    assert len(keys) == 2880
    nine, centre, arms, witnesses = base.sample(keys, mags, weights, adj)
    order, components = address_order(keys, mags, adj)
    assert order[:9] == nine, "the original nine-leaf baseline moved"
    assert all(LEVELS[k] < LEVELS[k+1] for k in range(len(LEVELS)-1))
    assert LEVELS[-1] <= len(keys) < 3*LEVELS[-1]
    sources = base.build_sources(len(keys), arms)
    frames = forward(sources, mags, weights, adj)

    # The original three source/receiver waves remain weighted reciprocal.
    for tick in OBSERVE:
        assert base.symmetric(base.responses(frames[tick], sources, weights))

    records = [
        "CONTRACT|schema=GITRAM-TRIADIC-WAVE-READOUTS-V1|coupling=12|m0=9|full_classes=2880|sources=3|steps=9|integer_only=1|representation_only=1|json=0",
        "SOURCE|run=%d|row_sha256=%s|weights_sha256=%s|manifest_sha256=%s|json=0" % (
            SOURCE_RUN, base.sh(d/"rows.txt"), base.sh(d/"weights.txt"),
            base.sh(d/"SHA256SUMS")
        ),
        "BASELINE|nine_address_sha256=%s|centre_key=%d|components=%d|original_nine_unchanged=PASS|json=0" % (
            base.checksum([[keys[i] for i in nine]]), keys[centre], components
        )
    ]
    for level in LEVELS:
        indices = order[:level]
        address_sha = base.checksum([[keys[i] for i in indices]])
        records.append(
            "LEVEL|leaves=%d|address_sha256=%s|nested=PASS|distinct_addresses=PASS|source_columns=9_not_%d|json=0"
            % (level, address_sha, level)
        )
        for tick in OBSERVE:
            waves = frames[tick]
            hits, edges, frontier, local, total, rough, mass_ppb, rough_ppm = metrics(
                indices, waves, weights, adj
            )
            selected_wave_sha = base.checksum([
                [w[i] for i in indices] for w in waves
            ])
            # Exact ratios are retained, alongside display-friendly integer
            # ppb/ppm projections that are NOT used as proof inputs.
            records.append(
                "MEASURE|leaves=%d|tick=%d|active_addresses=%d|internal_edges=%d|frontier_arcs=%d|mass_num=%d|mass_den=%d|mass_ppb=%d|rough_num=%d|rough_den=%d|rough_ppm=%d|amplitudes_sha256=%s|json=0"
                % (level, tick, hits, edges, frontier, local, total,
                   mass_ppb, rough, local, rough_ppm, selected_wave_sha)
            )

    # Mutation controls: a terminal change changes the authenticated frame;
    # an asymmetric directed electric edge breaks source reciprocity.
    terminal = [v[:] for v in frames[9]]
    before = base.checksum(terminal)
    terminal[0][centre] += 1
    assert base.checksum(terminal) != before
    i, j = arms[0][0], arms[1][0]
    broken = [
        [DEN*x - h for x, h in zip(src, base.apply(src, mags, adj,
                                                   tamper=(i, j)))]
        for src in sources
    ]
    assert not base.symmetric(base.responses(broken, sources, weights))

    records += [
        "CONTROL|full_operator_forward_inverse=PASS|conserved_discrete_energy=PASS|weighted_reciprocity=PASS|terminal_tamper=REJECTED|asymmetric_link=REJECTED|json=0",
        "BOUNDARY|largest_fitting_power=2187|next_power=6561|available_classes=2880|requires_new_authenticated_core=YES|json=0",
        "LIMIT|new_independent_ternary_columns=0|new_physical_lattice_scales=0|physical_YM_time_evolution=NO|continuum_limit=NOT_ESTABLISHED|mass_gap_claim=NONE|r9_launch=NO|json=0",
        "GITRAM_TRIADIC_WAVE_READOUTS_PASS|levels=6|largest=2187|ticks=9|full_rewind=PASS|json=0"
    ]
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(records)+"\n", encoding="utf-8")
    (output.parent/(output.name+".sha256")).write_text(
        "%s  %s\n" % (base.sh(output), output.name), encoding="utf-8"
    )
    print("\n".join(x for x in records if not x.startswith("MEASURE|")))
    print("RESULT_SHA256|%s|json=0" % base.sh(output))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: triadic_wave_readouts.py PINNED_CUTOFF9_DIR REPORT.hbp")
    run(sys.argv[1], sys.argv[2])
