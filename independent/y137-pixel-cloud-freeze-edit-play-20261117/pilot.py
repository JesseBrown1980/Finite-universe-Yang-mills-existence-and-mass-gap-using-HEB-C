#!/usr/bin/env python3
"""#137/288: exact finite pixel-cloud freeze -> retag -> play controls.

Four physical two-level pixels in two disjoint clouds: A0,A1 and B0,B1.
The PREPARED A0/B0 Bell state is frozen before the spatial clouds separate.
Retagging a shared metadata table is a classical record edit, not a quantum
operation. We independently test local A gates and a physical local B SWAP.
All probabilities use exact integer numerator with fixed denominator 2.
No floats, Fractions, NumPy, JSON, clocks, RNG, process or network access.
This is a small independent quantum-information toy, not a 2.17B S3 solve.
"""
from hashlib import sha256
from pathlib import Path

QUBITS=('A0','A1','B0','B1')
DIM=1<<len(QUBITS)
NORM=2
DISTANCES=(1,8,64,1024,65536)
# A0 is the high bit, B1 the low bit; |0000>+|1010> over sqrt(2).
BELL={0:1,10:1}
# A0/A1 entangled entirely inside cloud A, cloud B starts in |00>.
LOCAL_BELL={0:1,12:1}


def require(test, reason):
    if not test:
        print('PIXEL_CLOUD_REFUSE|reason='+reason+'|json=0',flush=True)
        raise SystemExit(1)


def emit(tag,**items):
    print(tag+'|'+'|'.join(str(k)+'='+str(v) for k,v in items.items())+'|json=0')


def bit(index, qubit):
    return (index >> (len(QUBITS)-1-qubit))&1


def keybits(index, keep):
    v=0
    for i in keep:
        v=(v<<1)|bit(index,i)
    return v


def state_hash(st):
    return sha256(';'.join(str(k)+':'+str(st[k]) for k in sorted(st)).encode('ascii')).hexdigest()


def table_hash(table):
    return sha256('\n'.join(k+'='+table[k] for k in sorted(table)).encode('ascii')).hexdigest()


def frozen_matrix_hash():
    # 16 by 16 identity transfer: evolution does not access metatag tables.
    return sha256(bytes(1 if i==j else 0 for i in range(DIM) for j in range(DIM))).hexdigest()


def check_state(st):
    require(all(isinstance(v,int) and v in (-1,1) for v in st.values()),'bad_amplitudes')
    require(sum(v*v for v in st.values())==NORM,'normalization')
    require(all(0<=k<DIM for k in st),'bad_basis_address')
    return st


def reduced(st,keep):
    """Exact partial trace numerator over all complement pixels (denominator 2)."""
    trace=tuple(i for i in range(len(QUBITS)) if i not in keep)
    out={}
    for a,amp in st.items():
        for b,bmp in st.items():
            if keybits(a,trace)!=keybits(b,trace):
                continue
            i,j=keybits(a,keep),keybits(b,keep)
            out[(i,j)]=out.get((i,j),0)+amp*bmp
    size=1<<len(keep)
    return tuple(tuple(out.get((i,j),0) for j in range(size)) for i in range(size))


def zz(st,i,j):
    return sum(c*c*(1 if bit(b,i)==bit(b,j) else -1)
               for b,c in st.items())


def xx(st,i,j):
    mask=(1<<(3-i))|(1<<(3-j))
    return sum(c*st.get(b^mask,0) for b,c in st.items())


def single_x(st,i):
    mask=1<<(3-i)
    return sum(c*st.get(b^mask,0) for b,c in st.items())


def one_probability(st,i):
    return sum(c*c for b,c in st.items() if bit(b,i))


def local_pauli(st,i,kind):
    mask=1<<(3-i)
    if kind=='X':
        v={b^mask:c for b,c in st.items()}
    elif kind=='Z':
        v={b:(-c if bit(b,i) else c) for b,c in st.items()}
    else:
        require(False,'bad_local_gate')
    return check_state(v)


def local_swap(st,i,j):
    mi,mj=1<<(3-i),1<<(3-j)
    v={}
    for b,c in st.items():
        if bit(b,i)!=bit(b,j):
            b^=mi|mj
        v[b]=c
    return check_state(v)


def local_b_signature(st):
    return repr(reduced(st,(2,3)))


def table(distance):
    return {'A0':'cloud=A;site=0;pair=B0',
            'A1':'cloud=A;site=1;pair=NONE',
            'B0':'cloud=B;site='+str(distance)+';pair=A0',
            'B1':'cloud=B;site='+str(distance+1)+';pair=NONE'}


def main():
    src=Path(__file__).resolve().parent.parent/'y137-metatag-shell-overlap-20261117'/'pilot.py'
    if src.exists():
        # Optional source-binding in the stacked PR. This never imports or modifies the S3 H.
        parent_sha=sha256(src.read_bytes()).hexdigest()
    else:
        parent_sha='STANDALONE_PARENT_FILE_ABSENT'
    initial=check_state(dict(BELL))
    frozen_hash=state_hash(initial)
    transfer=frozen_matrix_hash()
    rB=reduced(initial,(2,3))
    require(rB==((1,0,0,0),(0,0,0,0),(0,0,1,0),(0,0,0,0)),
            'original_B_reduced_state')
    require(zz(initial,0,2)==xx(initial,0,2)==2,'original_Bell_correlations')
    require(zz(initial,0,3)==xx(initial,0,3)==0,'not_entangled_with_B1')
    require(one_probability(initial,2)==1 and single_x(initial,2)==0,
            'original_remote_marginal')
    require(one_probability(initial,3)==0,'original_remote_B1_zero')
    emit('PIXEL_CLOUD_FROZEN',qubits=4,clouds=2,initial_entangled_pair='A0:B0',
         state_sha256=frozen_hash,transfer_I16_sha256=transfer,
         B0_Z_prob_one='1/2',B0_X_prob_plus='1/2',
         A0_B0_XX='1',A0_B0_ZZ='1',A0_B1_XX='0',
         original_S3_source_sha256=parent_sha,status='PASS')
    for d in DISTANCES:
        old=table(d)
        old_digest=table_hash(old)
        edited=dict(old)
        edited['A0']='cloud=A;site=0;pair=B1'
        edited['B0']='cloud=B;site='+str(d)+';pair=NONE'
        edited['B1']='cloud=B;site='+str(d+1)+';pair=A0'
        new_digest=table_hash(edited)
        require(new_digest!=old_digest,'tag_edit_must_change_hash')
        # Replay through SAME frozen physical transfer. Catalog editing is
        # deliberately not a quantum gate or an assignment to amplitudes.
        played=dict(initial)
        require(state_hash(played)==frozen_hash,'tag_edit_changed_undriven_state')
        require(reduced(played,(2,3))==rB,'tag_edit_transmitted_to_B')
        require(zz(played,0,2)==xx(played,0,2)==2,'false_entanglement_move')
        require(zz(played,0,3)==xx(played,0,3)==0,'tag_created_fake_B1_entanglement')
        # Two A-local encodings from identical frozen state.
        phase=local_pauli(dict(initial),0,'Z')
        flip=local_pauli(dict(initial),0,'X')
        require(reduced(phase,(2,3))==rB,'Z_A_sent_information')
        require(reduced(flip,(2,3))==rB,'X_A_sent_information')
        require(zz(phase,0,2)==2 and xx(phase,0,2)==-2,'Z_correlator_negative_control')
        require(zz(flip,0,2)==-2 and xx(flip,0,2)==2,'X_correlator_negative_control')
        require(one_probability(phase,2)==one_probability(flip,2)==1,
                'A_edit_changed_remote_Z_probability')
        require(single_x(phase,2)==single_x(flip,2)==0,
                'A_edit_changed_remote_X_probability')
        # A genuine B-local SWAP changes actual PHYSICAL entanglement partner.
        actual_move=local_swap(dict(initial),2,3)
        require(state_hash(actual_move)!=frozen_hash,'physical_gate_must_change_state')
        require(zz(actual_move,0,3)==xx(actual_move,0,3)==2,
                'physical_B_swap_failed_move')
        require(zz(actual_move,0,2)==xx(actual_move,0,2)==0,
                'physical_B_swap_old_pair_still_entangled')
        require(reduced(actual_move,(0,1))==reduced(initial,(0,1)),
                'B_local_swap_sent_message_to_A')
        # Explicit fake signal through a shared cross-cloud table: both read
        # channels agree only because metadata is made globally accessible.
        t0=dict(edited); t1=dict(edited)
        t0['B1']+=';message=0';t1['B1']+=';message=1'
        require(table_hash(t0)!=table_hash(t1),'shared_memory_channel_not_distinct')
        require(reduced(played,(2,3))==rB,'shared_table_changed_local_quantum_state')
        # A forged deterministic remote bit would violate exact B0 marginal 1/2.
        predicted_fake_one=2
        require(predicted_fake_one!=one_probability(initial,2),
                'fake_superluminal_signal_not_rejected')
        emit('PIXEL_CLOUD_REPLAY',distance_cells=d,clouds='A:B',
             table_hash_changed='YES',state_hash_unchanged='YES',
             distant_B_density_unchanged='YES',B0_Z_prob_one='1/2',
             B0_X_prob_plus='1/2',old_entangled_pair='A0:B0',
             metadata_claimed_pair='A0:B1',physical_B1_pair_created='NO',
             A_local_Z_B0_Z_prob_one='1/2',A_local_X_B0_Z_prob_one='1/2',
             A_local_Z_joint_XX='-1',A_local_X_joint_ZZ='-1',
             B_local_SWAP_entangles_A0_B1='YES',
             globally_shared_table_message_visible='YES_CLASSICAL_CHANNEL',
             local_quantum_message_decodable='NO',status='PASS')
    # User's stronger experiment: first put BOTH entangled pixels in cloud A,
    # freeze, and merely rebind the second metatag to a pixel in cloud B.
    # The distant quantum cloud must remain in its original pure |00> state.
    local=check_state(dict(LOCAL_BELL))
    local_sha=state_hash(local)
    local_remote=reduced(local,(2,3))
    require(local_remote==((2,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0)),
            'local_pair_B_not_in_ground')
    require(xx(local,0,1)==zz(local,0,1)==2,'local_pair_not_entangled')
    for d in DISTANCES:
        source=table(d)
        source['A0']='cloud=A;site=0;pair=A1'
        source['A1']='cloud=A;site=1;pair=A0'
        source['B0']='cloud=B;site='+str(d)+';pair=NONE'
        other=dict(source)
        other['A0']='cloud=A;site=0;pair=B0'
        other['A1']='cloud=A;site=1;pair=NONE'
        other['B0']='cloud=B;site='+str(d)+';pair=A0'
        require(table_hash(source)!=table_hash(other),'local_to_remote_tag_unchanged')
        played=dict(local)
        require(state_hash(played)==local_sha,'local_pair_remote_retag_changed_quantum_state')
        require(reduced(played,(2,3))==local_remote,'local_pair_remote_B_changed')
        require(xx(played,0,2)==zz(played,0,2)==0,
                'local_pair_false_B_entanglement')
        # To really relocate entanglement requires physically crossing
        # the cloud boundary with a SWAP on A1 and B0.
        cross=local_swap(dict(local),1,2)
        require(cross==BELL,'cross_cloud_gate_did_not_change_pair')
        require(reduced(cross,(2,3))!=local_remote,
                'cross_cloud_gate_remote_local_state_unchanged')
        emit('PIXEL_CLOUD_LOCAL_PAIR_RETAG',distance_cells=d,
             original_entangled_group='A0:A1_IN_A',
             metatag_claimed_partner='A0:B0_IN_B',
             A_table_sha_changed='YES',physical_matrix_frozen='YES',
             quantum_state_sha_unchanged='YES',
             B0_Z_prob_one='0/2',B_cloud_rho_pure_ground='YES',
             A0_B0_new_entanglement='NO',
             cross_cloud_physical_SWAP_changes_B_state='YES_NONLOCAL_GATE',
             status='PASS')
    emit('PIXEL_CLOUD_VERDICT',distances=len(DISTANCES),
         meta_table_pairing='YES_CLASSICAL_CATALOG',
         actual_prepared_entanglement='YES',
         retagging_moves_physical_entanglement='NO',
         initially_local_A_entanglement_migrates_by_retag='NO',
         remote_only_entanglement_signalling='NO',
         shared_table_read='EXPLICIT_CLASSICAL_CHANNEL',
         original_S3_gap_certificate='UNCHANGED',
         S3_first_Wilson_weight='HOLD',
         experimental_superluminal_physics='NOT_TESTED',
         result='EXACT_TOY_NOSIGNALLING_PASS')


if __name__=='__main__':
    main()
