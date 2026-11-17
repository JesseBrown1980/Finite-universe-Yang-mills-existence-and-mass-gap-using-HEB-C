#!/usr/bin/env python3
"""Clean-room exact verifier of selected 3SAT parity hierarchy receipts.
Does not import the pilot or its counted algorithm. Integer-only.
"""
import hashlib
import sys


def sha_repr(obj):
    return hashlib.sha256(repr(obj).encode('ascii')).hexdigest()


def data_value(s):
    parts=s.strip().split('|')
    assert parts[-1] == 'json=0'
    return parts[0],dict(x.split('=',1) for x in parts[1:-1])


def fixture(n):
    hidden=0
    for i in range(n):
        b=hashlib.sha256(('hidden:'+str(n)+':'+str(i)).encode('ascii')).digest()[0]&1
        hidden |= b<<i
    triples=[]
    for i in range(n):
        triples.append((i+1,(i+1)%n+1,(i+n//3)%n+1))
    for i in range(0,n,3):
        triples.append((i+1,(i+n//3+1)%n+1,(i+2*n//3+2)%n+1))
    clauses=[]
    equations=[]
    for triple in triples:
        assert len(set(triple))==3
        rhs=0
        mask=0
        for v in triple:
            rhs ^= ((hidden>>(v-1))&1)
            mask |= 1<<(v-1)
        # Transform parity into exactly four rejecting 3CNF clauses.
        for j in range(8):
            if (j.bit_count()&1)!=rhs:
                clauses.append(tuple(-v if ((j>>k)&1) else v for k,v in enumerate(triple)))
        equations.append((mask,rhs))
    return tuple(clauses),tuple(equations)


def gaussian_left(n,eqs):
    # Independent leftmost-pivot elimination, distinct from the pilot's
    # rightmost-pivot block-wise incremental reduction.
    rows=[[m,b] for m,b in eqs]
    pivot_cols=[]
    r=0
    xor_ops=0
    for p in range(n):
        selected=None
        for q in range(r,len(rows)):
            if rows[q][0]&(1<<p):
                selected=q
                break
        if selected is None:
            continue
        rows[r],rows[selected]=rows[selected],rows[r]
        for q in range(r+1,len(rows)):
            if rows[q][0]&(1<<p):
                rows[q][0] ^= rows[r][0]
                rows[q][1] ^= rows[r][1]
                xor_ops += 1
        pivot_cols.append(p)
        r+=1
    assert all((m!=0 or b==0) for m,b in rows[r:])
    assignment=0
    for j in range(r-1,-1,-1):
        mask,rhs=rows[j]
        p=pivot_cols[j]
        v=rhs ^ ((mask & assignment).bit_count() & 1)
        assignment |= v<<p
    for m,b in eqs:
        assert (m&assignment).bit_count()%2 == b
    return len(pivot_cols),assignment,xor_ops


def check_clause(c,bits):
    for v in c:
        current=(bits>>(abs(v)-1))&1
        if current==int(v>0):
            return True
    return False


def count_all(n,clauses):
    return sum(int(all(check_clause(c,a) for c in clauses)) for a in range(1<<n))


def bitparallel_count(n, clauses):
    """Independent complete 2^n-assignment truth vector, n<=21 only.
    This oracle deliberately allocates exponential bits and is NOT the solver.
    """
    assert n<=21
    count=1<<n
    everything=(1<<count)-1
    masks={}
    for v in range(1,n+1):
        block=1<<(v-1)
        x=((1<<block)-1)<<block
        covered=2*block
        while covered<count:
            x |= x<<covered
            covered*=2
        masks[v]=x
    states=everything
    for clause in clauses:
        c=0
        for lit in clause:
            pos=masks[abs(lit)]
            c |= pos if lit>0 else (everything ^ pos)
        states &= c
    return states.bit_count()


def generic_source(n):
    hidden=0
    for i in range(n):
        bit=hashlib.sha256(('hidden:'+str(n)+':'+str(i)).encode('ascii')).digest()[0]&1
        hidden |= bit<<i
    result=[]
    for i in range(n):
        triples=((i+1,((i+n//3)%n)+1,((i+2*n//3)%n)+1),
                 (i+1,((i+1)%n)+1,((i+n//2)%n)+1))
        for j,tri in enumerate(triples):
            c=[]
            for k,v in enumerate(tri):
                hashed=hashlib.sha256(('generic:'+str(i)+':'+str(j)+':'+str(k)).encode('ascii')).digest()[0]
                c.append(v if hashed&1 else -v)
            if not check_clause(c,hidden):
                c[0]=-c[0]
            result.append(tuple(c))
    return tuple(result)


def main(path):
    lines=[data_value(l) for l in open(path,encoding='utf-8') if l.strip()]
    parity={int(d['variables']):d for k,d in lines if k=='MTP_PARITY'}
    generic={int(d['variables']):d for k,d in lines if k=='MTP_GENERIC'}
    hybrid={int(d['variables']):d for k,d in lines if k=='MTP_HYBRID'}
    ends=[d for k,d in lines if k=='MTP_GLOBAL_FINAL']
    assert len(ends)==1 and len(parity)==14 and len(generic)==12 and len(hybrid)==5
    assert ends[0]['P_equals_NP']=='NOT_ESTABLISHED'
    assert ends[0]['generic_global_constraints_always_compact']=='NO'
    assert ends[0]['measured_whole_process_peak_RSS_kib'].isdigit()
    oracle=0
    for n,row in sorted(parity.items()):
        clauses,eqs=fixture(n)
        assert len(clauses)==int(row['clauses'])
        assert sha_repr(clauses)==row['source_sha256']
        assert len(eqs)==int(row['recognized_xor_groups'])
        rank,witness,ops=gaussian_left(n,eqs)
        assert rank==int(row['rank'])
        assert 1<<(n-rank)==int(row['exact_model_count'])
        assert all(check_clause(c,witness) for c in clauses)
        assert row['MTP3_corrected_agent_errors']=='1'
        assert int(row['naive_factor_peak_projected_entries'])==(1<<(int(row['naive_factor_joint_bits'])-1))
        assert int(row['defined_metric_total_work_units_including_baselines'])>0
        assert int(row['source_clause_bytes'])==len(repr(clauses).encode('ascii'))
        if n<=12:
            assert count_all(n,clauses)==int(row['exact_model_count'])
            oracle+=1
    assert int(parity[1152]['rank'])==1152
    assert len(parity)==14 and oracle==2
    assert int(generic[72]['naive_factor_joint_bits'])==50
    generic_checked=0
    for n in (6,9,12,15,18,21):
        source=generic_source(n)
        assert sha_repr(source)==generic[n]['source_sha256']
        exact=bitparallel_count(n,source)
        assert exact==int(generic[n]['actual_exact_model_count'])
        assert generic[n]['after_preflight']=='GENERIC_EXACT_WITHIN_BUDGET'
        generic_checked+=1
    for n in (24,30,36,48,60,72):
        assert generic[n]['after_preflight']=='HOLD_TABLE_LIMIT'
        assert generic[n]['actual_exact_model_count']=='HOLD'
        assert int(generic[n]['actual_allocated_peak_factor_slots'])<=32768
    hcl,hrows=fixture(12)
    assert len(hcl)>=24
    hybrid_source=hcl[:24]
    for c in generic_source(12):
        scope=tuple(sorted(set(abs(v) for v in c)))
        seen={tuple(sorted(set(abs(v) for v in z))) for z in hybrid_source}
        if scope not in seen:
            hybrid_source+=(c,)
        if len(hybrid_source)==30:
            break
    assert sha_repr(hybrid_source)==hybrid[12]['source_sha256']
    assert bitparallel_count(12,hybrid_source)==36
    assert generic[72]['after_preflight']=='HOLD_TABLE_LIMIT'
    assert hybrid[12]['exact_brute_model_count']=='36'
    assert hybrid[12]['full_problem_model_count']=='HOLD_RESIDUAL_GENERIC'
    print('MTP_GLOBAL_INDEPENDENT|parity_families_reconstructed=14|cleanroom_left_pivot_rank_and_counts=PASS|parity_full_2powN_oracles=2|generic_full_2powN_oracles=6|generic_max_oracle_assignments=2097152|hybrid_12_full_oracle=PASS|original_3CNF_clause_witness_check=PASS|source_sha256=PASS|large_max_variables=1152|generic_table_cap_abstention=PASS|P_equals_NP=NOT_CLAIMED|status=PASS|json=0')


if __name__=='__main__':
    assert len(sys.argv)==2
    main(sys.argv[1])
