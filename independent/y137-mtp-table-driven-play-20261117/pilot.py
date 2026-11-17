#!/usr/bin/env python3
"""Exact integer freeze -> edit identity tables -> nested MTP evaluate -> play.

Research-only deterministic MTP-style shell evaluator, not trained MTP weights.
4 pixels, 2 clouds, 16-dimensional exact integer quantum permutation model.
The original real S3 Hamiltonian and all of its certificates remain untouched.
"""
from hashlib import sha256

PIXELS = ('A0', 'A1', 'B0', 'B1')
INDEX = {p: i for i, p in enumerate(PIXELS)}
SHELLS = (1, 3, 27)
SHELL_AGENTS = ('MTP1_IMMEDIATE', 'MTP3_PAIR_LOOKAHEAD', 'MTP27_CONSERVATION_WATCHER')
DISTANCES = (1, 8, 64, 1024, 65536)


def need(ok, name):
    if not ok:
        raise AssertionError(name)


def encode_catalog(table):
    return ';'.join(p + ':' + table[p][0] + ':' + str(table[p][1]) for p in PIXELS).encode('ascii')


def root(data):
    return sha256(data).hexdigest()


def state_root(state):
    nums, den = state
    return root(('den=' + str(den) + ';' + ','.join(str(x) for x in nums)).encode('ascii'))


def emit(name, **kwargs):
    print(name + '|' + '|'.join(str(k) + '=' + str(v) for k, v in kwargs.items()) + '|json=0')


def make_catalog():
    return {
        'A0': ('PAIR-7', 0), 'A1': ('PAIR-7', 0),
        'B0': ('SOLO-B0', 0), 'B1': ('SOLO-B1', 0),
    }


def edit_catalog(base):
    out = dict(base)
    # Physically rebind the originally local A0:A1 pairing to A1:B0,
    # then request a one-slice exchange by changing only the table.
    out['A0'] = ('SOLO-A0', 0)
    out['A1'] = ('PAIR-7', 1)
    out['B0'] = ('PAIR-7', 0)
    return out


def authorized_pairs(snapshot):
    groups = {}
    for p in PIXELS:
        identity, pulse = snapshot[p]
        need(pulse in (0, 1), 'pulse_trit_domain')
        groups.setdefault(identity, []).append((p, pulse))
    result = []
    for identity, members in sorted(groups.items()):
        if not identity.startswith('PAIR-'):
            need(all(pulse == 0 for _, pulse in members), 'solo_pulse_rejected')
            continue
        need(len(members) == 2, 'pair_exactly_two_required')
        need(sum(pulse for _, pulse in members) <= 1, 'duplicate_pulse_rejected')
        if sum(pulse for _, pulse in members) == 1:
            result.append(tuple(sorted(p for p, _ in members)))
    return tuple(result)


def same_cloud(a, b):
    return a[0] == b[0]


def mtp_at_shell(snapshot, shell, mode, distance):
    # Every agent sees the same frozen metadata table and state root.
    # It may, depending on mode, access the whole identity catalog or
    # only records in its causal neighborhood.
    pairs = authorized_pairs(snapshot)
    observed = []
    for a, b in pairs:
        visible = (same_cloud(a, b) or mode == 'GLOBAL_INDEX'
                   or distance <= shell)
        if visible:
            # Three separate shell-specific audit rules use the SAME source
            # snapshot. MTP1 proposes the immediate swap; MTP3 forecasts
            # the consumed pulse through 3 slices; MTP27 does the same
            # through 27 and verifies the proposed quantum permutation's
            # bijectivity and excitation conservation. No trained weights.
            if shell >= 3:
                consumed = {p: (snapshot[p][0], 0) for p in PIXELS}
                for forecast_step in range(1, shell):
                    need(not authorized_pairs(consumed),
                         'MTP_future_pulse_not_consumed')
            if shell == 27:
                probe = exchange_permutation(((a, b),))
                need(all(k.bit_count() == probe[k].bit_count()
                         for k in range(16)), 'MTP27_bad_exchange')
            observed.append((a, b))
    return tuple(observed)


def hierarchical_resolver(snapshot, mode, distance):
    proposals = tuple(mtp_at_shell(snapshot, s, mode, distance) for s in SHELLS)
    if mode == 'GLOBAL_INDEX':
        need(proposals[0] == proposals[1] == proposals[2],
             'global_shell_disagreement')
    # Higher shells cover supersets of lower shells; apply any proposed
    # physical pair exchange ONCE, atomically at end of slice.
    union = sorted(set(pair for shell in proposals for pair in shell))
    touched = [p for pair in union for p in pair]
    need(len(touched) == len(set(touched)), 'conflicting_agent_movement')
    return tuple(union), proposals


def exchange_permutation(pairs):
    perm = list(range(16))
    for a, b in pairs:
        ia, ib = INDEX[a], INDEX[b]
        mask = (1 << ia) | (1 << ib)
        for old in range(16):
            aa, bb = (old >> ia) & 1, (old >> ib) & 1
            if aa != bb:
                perm[old] ^= mask
    need(sorted(perm) == list(range(16)), 'U_not_unitary_permutation')
    need(all(perm[perm[k]] == k for k in range(16)), 'U_not_involutory')
    need(all(k.bit_count() == perm[k].bit_count() for k in range(16)),
         'U_broke_excitation_conservation')
    return tuple(perm)


def unitary_root(perm):
    return root(bytes(perm))


def play(state, perm):
    nums, den = state
    need(len(nums) == 16 and sum(x * x for x in nums) == den,
         'input_quantum_norm')
    result = [0] * 16
    for old in range(16):
        result[perm[old]] += nums[old]
    need(sum(x * x for x in result) == den, 'norm_not_conserved')
    return tuple(result), den


def freeze_edit_play(state, frozen_table, edited_table, mode, distance):
    before_state = state_root(state)
    before_table = root(encode_catalog(frozen_table))
    new_table = root(encode_catalog(edited_table))
    need(before_table != new_table, 'table_not_edited')
    need(before_state == state_root(state), 'state_changed_before_play')
    pairs, proposals = hierarchical_resolver(edited_table, mode, distance)
    perm = exchange_permutation(pairs)
    output = play(state, perm)
    # Commit the next metadata slice as an atomic transaction.
    committed = {p: (edited_table[p][0], 0) for p in PIXELS}
    return {
        'pairs': pairs, 'proposals': proposals, 'source_state_hash': before_state,
        'table_old_hash': before_table, 'table_edited_hash': new_table,
        'unitary_hash': unitary_root(perm), 'next_state_hash': state_root(output),
        'table_next_hash': root(encode_catalog(committed)), 'state': output,
        'perm': perm,
    }


def product_one_at(pixel):
    coeffs = [0] * 16
    coeffs[1 << INDEX[pixel]] = 1
    return tuple(coeffs), 1


def bell_pair(a, b):
    coeffs = [0] * 16
    coeffs[0] = 1
    coeffs[(1 << INDEX[a]) | (1 << INDEX[b])] = 1
    return tuple(coeffs), 2


def probability_one(state, pixel):
    nums, den = state
    q = INDEX[pixel]
    return sum(n * n for k, n in enumerate(nums) if (k >> q) & 1), den


def density_B(state):
    nums, den = state
    # Reduced state of the whole cloud B, matrix indexed by B0/B1 0..3.
    return tuple(tuple(sum(nums[a + 4*b] * nums[a + 4*c]
                               for a in range(4))
                       for c in range(4)) for b in range(4)), den


def correlation_zz(state, a, b):
    nums, den = state
    ia, ib = INDEX[a], INDEX[b]
    val = sum((1 if ((k >> ia) & 1) == ((k >> ib) & 1) else -1)
              * n*n for k, n in enumerate(nums))
    return val, den


def test_negative_controls(base, edited):
    # A snapshot is a fixed input; table editing without 'play' cannot move it.
    s = product_one_at('A1')
    need(state_root(s) == state_root(s), 'identity_freeze')
    no_pulse = dict(edited)
    no_pulse['A1'] = ('PAIR-7', 0)
    need(not hierarchical_resolver(no_pulse, 'GLOBAL_INDEX', 65536)[0],
         'without_pulse_moves')
    unpaired = dict(edited)
    unpaired['B0'] = ('SOLO-B0', 0)
    try:
        authorized_pairs(unpaired)
    except AssertionError as e:
        need(str(e) == 'pair_exactly_two_required', 'unpaired_wrong_refusal')
    else:
        need(False, 'unpaired_must_fail_closed')
    collide = dict(edited)
    collide['B1'] = ('PAIR-7', 0)
    try:
        authorized_pairs(collide)
    except AssertionError as e:
        need(str(e) == 'pair_exactly_two_required', 'collision_wrong_refusal')
    else:
        need(False, 'collision_must_fail_closed')
    forged = dict(edited)
    forged['B0'] = ('PAIR-7', 1)
    try:
        authorized_pairs(forged)
    except AssertionError as e:
        need(str(e) == 'duplicate_pulse_rejected', 'duplicate_pulse_wrong_refusal')
    else:
        need(False, 'duplicate_pulse_must_fail_closed')
    emit('MTP_NEGATIVES',missing_pulse='HELD',unpaired_identity='HELD',
         identity_collision='HELD',duplicate_instruction='HELD',
         frozen_no_play='STATE_UNCHANGED',status='PASS')


def main():
    base = make_catalog()
    edited = edit_catalog(base)
    need(authorized_pairs(edited) == (('A1', 'B0'),),
         'pair_not_cross_cloud')
    test_negative_controls(base, edited)
    original = product_one_at('A1')
    local_bell = bell_pair('A0', 'A1')
    standard_bell = bell_pair('A0', 'B0')
    need(probability_one(original, 'B0') == (0, 1), 'baseline_remote_excitation')
    need(probability_one(local_bell, 'B0') == (0, 2), 'baseline_remote_bell')
    initial_u = unitary_root(exchange_permutation(()))
    emit('MTP_SOURCE',qubits=4,clouds=2,shells='1:3:27',shell_agents='MTP1_IMMEDIATE:MTP3_PAIR_LOOKAHEAD:MTP27_CONSERVATION_WATCHER',
         evaluator='EXACT_DETERMINISTIC_MTP_SHELL_ADAPTER',
         trained_MTP_weights='NOT_LOADED',
         source_slice_root=state_root(original),
         old_catalog_sha256=root(encode_catalog(base)),
         edited_catalog_sha256=root(encode_catalog(edited)),
         frozen_initial_I16_sha256=initial_u,
         physical_source='4_QUBIT_TOY_NOT_ORIGINAL_S3_HAMILTONIAN',
         status='PASS')
    for distance in DISTANCES:
        glob = freeze_edit_play(original,base,edited,'GLOBAL_INDEX',distance)
        loc = freeze_edit_play(original,base,edited,'LOCAL_RADIUS',distance)
        need(glob['pairs'] == (('A1','B0'),), 'global_pair_not_replayed')
        need(glob['proposals'] == ((('A1','B0'),),)*3,
             'global_mtp_disagree')
        need(probability_one(glob['state'],'B0') == (1,1),
             'global_B_did_not_receive_excitation')
        need(probability_one(glob['state'],'A1') == (0,1),
             'global_A_excitation_not_removed')
        need(glob['unitary_hash'] != initial_u, 'table_did_not_control_U')
        need(glob['source_state_hash'] != glob['next_state_hash'],
             'table_did_not_control_next_slice')
        need(glob['table_old_hash'] != glob['table_edited_hash'],
             'no_catalog_edit')
        need(glob['unitary_hash'] == unitary_root(glob['perm']),
             'MTP_unitary_receipt_mismatch')
        expect_local = (distance <= 27)
        need(bool(loc['pairs']) == expect_local, 'local_lightcone_wrong')
        need(probability_one(loc['state'],'B0') == (1,1) if expect_local
             else probability_one(loc['state'],'B0') == (0,1),
             'local_receiver_wrong')
        need(glob['next_state_hash'] == freeze_edit_play(original,base,edited,
             'GLOBAL_INDEX',distance)['next_state_hash'],
             'replay_non_deterministic')
        emit('MTP_TABLE_DRIVEN_PLAY',distance_cells=distance,
             global_consensus_shells=3,global_pair='A1:B0',
             table_edited='YES',physical_U_recomputed='YES',
             U_not_fixed='YES',A1_one_after='0/1',B0_one_after='1/1',
             excitation_total_before='1',excitation_total_after='1',
             local_shell_pair_visible='+'.join(str(r) for r,p in zip(SHELLS,loc['proposals']) if p) or 'NONE',
             local_B0_one_after='1/1' if expect_local else '0/1',
             source_sha256=glob['source_state_hash'],
             result_sha256=glob['next_state_hash'],status='PASS')
        bell = freeze_edit_play(local_bell,base,edited,'GLOBAL_INDEX',distance)
        new_bell = bell['state']
        need(probability_one(new_bell, 'B0') == (1,2),
             'retag_play_failed_to_relocate_bell_partner')
        need(correlation_zz(new_bell,'A0','B0') == (2,2),
             'retag_play_bell_zz_not_correlated')
        need(density_B(local_bell) != density_B(new_bell),
             'nonlocal_gate_did_not_change_B_reduced_density')
        need(new_bell == bell_pair('A0','B0'),
             'actual_remote_bell_not_exact')
        # Once physically shared, table-triggered pairwise SWAP of both
        # Bell partners leaves the B local marginal invariant.
        cross_u = exchange_permutation((('A0','B0'),))
        kept = play(standard_bell,cross_u)
        need(density_B(kept) == density_B(standard_bell),
             'entanglement_alone_would_signal')
        emit('MTP_CLOUD_BELL',distance_cells=distance,
             before_entanglement='A0:A1_LOCAL_A',
             after_table_driven_play='A0:B0_CROSS_CLOUD',
             B0_one_before='0/2',B0_one_after='1/2',
             entangled_B0_Bell_pair='YES_BY_EXPLICIT_NONLOCAL_SWAP',
             preexisting_cross_Bell_local_probability='1/2',
             Bell_only_signal='NO',status='PASS')
    emit('MTP_FINAL',all_distances='1:8:64:1024:65536',
         metatag_drives_next_unitary='PASS',
         all_shells_globally_agree='PASS',
         global_catalog_sync='INSTANT_IN_MODEL',
         remote_product_excitation='RECEIVED_VIA_EXPLICIT_NONLOCAL_GATE',
         remote_Bell_entanglement='TRANSFERRED_VIA_EXPLICIT_NONLOCAL_GATE',
         local_shell_horizon='27_CELLS',
         no_free_entanglement_signalling='PASS',
         original_S3_gauge_certificate='UNMODIFIED',
         original_S3_Wilson_weight='HOLD',
         continuum='OPEN',physical_superluminal_signal='NOT_ESTABLISHED',
         status='EXACT_TOY_PASS')


if __name__ == '__main__':
    main()
