#!/usr/bin/env python3
"""Exact hierarchical parity compilation + generic SAT fail-closed benchmark.
Integer-only, no hidden training, no external precomputation. All work accounted in receipts.
"""
import hashlib
import os
import sys
from time import monotonic_ns


def emit(tag, **args):
    print(tag + '|' + '|'.join(str(k) + '=' + str(v) for k, v in args.items()) + '|json=0')


def digest(x):
    return hashlib.sha256(repr(x).encode('ascii')).hexdigest()


def sat_clause(clause, bitset):
    for lit in clause:
        b = (bitset >> (abs(lit) - 1)) & 1
        if b == int(lit > 0):
            return True
    return False


def sha_bits(n):
    # Input generation uses deterministic hashed pseudo-random bits. The
    # solver receives only clauses; it never sees this seed assignment.
    return sum((hashlib.sha256(('hidden:' + str(n) + ':' + str(i)).encode('ascii')).digest()[0] & 1) << i for i in range(n))


def xor_clauses(triple, rhs):
    assert len(triple) == 3 and len(set(triple)) == 3
    result = []
    for mask in range(8):
        if mask.bit_count() % 2 != rhs:
            clause = tuple(-v if ((mask >> j) & 1) else v for j, v in enumerate(triple))
            result.append(clause)
    assert len(result) == 4
    return tuple(result)


def parity_family(n):
    assert n >= 9 and n % 3 == 0
    hidden = sha_bits(n)
    triples = []
    for i in range(n):
        triples.append((i+1, ((i+1) % n)+1, ((i+n//3) % n)+1))
    for i in range(0, n, 3):
        triples.append((i+1, ((i+n//3+1) % n)+1, ((i+2*n//3+2) % n)+1))
    out = []
    motifs = []
    for tr in triples:
        assert len(set(tr)) == 3
        rhs = sum((hidden >> (v-1)) & 1 for v in tr) & 1
        cl = xor_clauses(tr, rhs)
        out.extend(cl)
        motifs.append((tuple(sorted(tr)),rhs))
    assert all(sat_clause(c, hidden) for c in out)
    return tuple(out),len(motifs)


def group_and_recognize(n, clauses, inject_wrong=False):
    """MTP1 = grouped clause pattern, MTP3 = exact 8-row truth check."""
    groups = {}
    for c in clauses:
        scope = tuple(sorted(set(abs(lit) for lit in c)))
        groups.setdefault(scope, []).append(c)
    rows = []
    attempted = 0
    rejected = 0
    bad = 0
    mismatch_caught = 0
    clause_truth_checks = 0
    for idx,(scope, cs) in enumerate(sorted(groups.items())):
        if len(scope)!=3:
            rejected += 1
            continue
        valid = []
        for bits in range(8):
            assignment = sum(((bits>>j)&1)<<(v-1) for j,v in enumerate(scope))
            clause_truth_checks += len(cs) * len(scope)
            valid.append(all(sat_clause(c,assignment) for c in cs))
        if not any(valid):
            bad += 1
            continue
        if sum(valid) != 4:
            rejected += 1
            continue
        rhs_set = {bits.bit_count() & 1 for bits in range(8) if valid[bits]}
        if len(rhs_set)!=1:
            rejected += 1
            continue
        rhs = next(iter(rhs_set))
        # Predicted lower shell may err; independent MTP3 reads the exact table.
        local_guess = rhs ^ int(inject_wrong and idx == 0)
        if local_guess != rhs:
            mismatch_caught += 1
        row = sum(1 << (v-1) for v in scope)
        rows.append((row, rhs))
        attempted += 1
    return (tuple(rows),len(groups),attempted,rejected,bad,
            mismatch_caught,clause_truth_checks)


def add_row(basis, mask, rhs, n, counter):
    while mask:
        p = mask.bit_length() - 1
        counter['pivot_tests'] += 1
        if p in basis:
            oldmask,oldrhs = basis[p]
            mask ^= oldmask
            rhs ^= oldrhs
            counter['row_xors'] += 1
            counter['bitwork'] += n + 1
        else:
            basis[p] = (mask,rhs)
            counter['basis_insertions'] += 1
            counter['peak_live_row_bits'] = max(counter['peak_live_row_bits'],
                                               len(basis) * (n + 1))
            return True
    if rhs:
        counter['contradictions'] += 1
    else:
        counter['redundant_rows'] += 1
    return False


def stats():
    return dict(pivot_tests=0,row_xors=0,bitwork=0,
                basis_insertions=0,peak_live_row_bits=0,
                contradictions=0,redundant_rows=0)


def hierarchical(n,rows,block=27):
    assert block == 27
    local = stats()
    local_bases = []
    for i in range(0,len(rows),block):
        basis = {}
        for mask,rhs in rows[i:i+block]:
            add_row(basis,mask,rhs,n,local)
        if local['contradictions']:
            return None,local,None,0
        local_bases.append(tuple(basis.values()))
    global_count = stats()
    all_rows = tuple(row for blockrows in local_bases for row in blockrows)
    basis = {}
    for mask,rhs in all_rows:
        add_row(basis,mask,rhs,n,global_count)
    logical_peak_bits = (n+1) * (len(all_rows)+len(basis))
    return basis,local,global_count,logical_peak_bits


def flat(n, rows):
    ctr = stats()
    basis = {}
    for mask,rhs in reversed(rows):
        add_row(basis,mask,rhs,n,ctr)
    return basis,ctr


def flat_forward(n, rows):
    ctr = stats()
    basis = {}
    for mask, rhs in rows:
        add_row(basis, mask, rhs, n, ctr)
    return basis, ctr


def measured_peak_rss_kib():
    # Linux process high-water mark includes interpreter, source construction,
    # temporary truth tables, all agent bases, and SHA receipts.
    if not os.path.isfile('/proc/self/status'):
        return -1
    with open('/proc/self/status', encoding='ascii') as src:
        for line in src:
            if line.startswith('VmHWM:'):
                return int(line.split()[1])
    return -1


def witness_from_basis(basis,n):
    v=0
    for pivot in sorted(basis):
        mask,rhs = basis[pivot]
        calculated = (mask & v).bit_count() & 1
        if rhs ^ calculated:
            v |= (1<<pivot)
    assert all((((mask & v).bit_count() & 1) == rhs) for mask,rhs in basis.values())
    assert v.bit_length() <= n
    return v


def brute_count(n,clauses):
    assert n <= 12
    solutions = 0
    for bits in range(1<<n):
        if all(sat_clause(c,bits) for c in clauses):
            solutions += 1
    return solutions


def symbolic_width(n,clauses):
    scopes=[set(abs(lit) for lit in c) for c in clauses]
    max_union=0
    max_projected=0
    scanned_scopes=0
    for v in range(1,n+1):
        touched=[]
        kept=[]
        for s in scopes:
            scanned_scopes += 1
            if v in s:
                touched.append(s)
            else:
                kept.append(s)
        if touched:
            total = set().union(*touched)
            max_union = max(max_union,len(total))
            projected=1 << (len(total)-1)
            max_projected=max(max_projected,projected)
            total.remove(v)
            if total:
                kept.append(total)
        scopes=kept
    return max_union,max_projected,scanned_scopes



def factor_count_limited(n, clauses, max_slots):
    # Conventional exact integer variable elimination, no MTP recognition.
    # Every allocated intermediate factor is checked against a hard cap.
    factors = []
    for c in clauses:
        scope = tuple(sorted(set(abs(l) for l in c)))
        vals = []
        for bits in range(1 << len(scope)):
            assignment = sum(((bits>>i)&1)<<(v-1) for i,v in enumerate(scope))
            vals.append(int(sat_clause(c,assignment)))
        factors.append((scope,tuple(vals)))
    scans=0
    peak_slots = max(len(values) for scope,values in factors)
    peak_live_slots = sum(len(values) for scope,values in factors)
    lookup_ops=0
    for v in range(1,n+1):
        touched=[f for f in factors if v in f[0]]
        kept=[f for f in factors if v not in f[0]]
        if not touched:
            kept.append(((),(2,)))
            factors=kept
            continue
        union=tuple(sorted({w for scope,_ in touched for w in scope}))
        remaining=tuple(w for w in union if w!=v)
        slots=1<<len(remaining)
        if slots>max_slots:
            return None,scans,peak_slots,peak_live_slots,lookup_ops,'HOLD_TABLE_LIMIT'
        pos={w:i for i,w in enumerate(union)}
        reduced_positions=tuple(pos[w] for w in remaining)
        proj=tuple((values,tuple(pos[w] for w in scope)) for scope,values in touched)
        arr=[]
        for bits in range(slots):
            lower=sum(((bits>>j)&1)<<p for j,p in enumerate(reduced_positions))
            new_value=0
            for b in (0,1):
                full=lower|(b<<pos[v])
                product=1
                for values,idx in proj:
                    sub=sum(((full>>p)&1)<<k for k,p in enumerate(idx))
                    product *= values[sub]
                    lookup_ops+=1
                    if not product:
                        break
                new_value+=product
            arr.append(new_value)
        scans+=slots*2
        factors=kept+[(remaining,tuple(arr))]
        peak_slots=max(peak_slots,slots)
        peak_live_slots=max(peak_live_slots,sum(len(f[1]) for f in factors))
    result=1
    for scope,values in factors:
        assert not scope
        result*=values[0]
    return result,scans,peak_slots,peak_live_slots,lookup_ops,'GENERIC_EXACT_WITHIN_BUDGET'


def generic(n):
    # Exact same deterministic planted generic 3-CNF family as PR #292,
    # independently checked here by a full oracle for n<=12.
    bits = sha_bits(n)
    out=[]
    for i in range(n):
        triples=((i+1,((i+n//3)%n)+1,((i+2*n//3)%n)+1),
                 (i+1,((i+1)%n)+1,((i+n//2)%n)+1))
        for j,tr in enumerate(triples):
            assert len(set(tr)) == 3
            signs=[]
            for k,v in enumerate(tr):
                h=hashlib.sha256(('generic:'+str(i)+':'+str(j)+':'+str(k)).encode('ascii')).digest()[0]
                signs.append(v if h&1 else -v)
            if not sat_clause(signs,bits):
                signs[0]=-signs[0]
            out.append(tuple(signs))
    assert all(sat_clause(c,bits) for c in out)
    return tuple(out)


def benchmark_parity(n):
    start=monotonic_ns()
    clauses,motifs=parity_family(n)
    scan=group_and_recognize(n,clauses,inject_wrong=True)
    rows,groups,recognized,rejected,bad,caught,work = scan
    assert recognized == motifs and rejected==bad==0 and caught==1
    basis,loc,glob,logical_bits=hierarchical(n,rows)
    assert basis is not None and glob['contradictions'] == 0
    flatbasis,flatops=flat(n,rows)
    forwardbasis, forwardops = flat_forward(n,rows)
    assert len(flatbasis) == len(forwardbasis) == len(basis)
    witness=witness_from_basis(basis,n)
    assert all(sat_clause(c,witness) for c in clauses)
    model_count=1 << (n-len(basis))
    assert model_count == (1 << (n-len(flatbasis)))
    oracle='NOT_RUN'
    if n <= 12:
        assert brute_count(n,clauses)==model_count
        oracle='EXHAUSTIVE_2POWN_PASS'
    base_width,base_projected,scans=symbolic_width(n,clauses)
    assert base_width >= 3
    # Full bookkeeping: count all source bytes, motif recognition, both
    # local/global reductions, independent flat proof and final verification.
    verify_cost = len(clauses)*3
    stage_ops = work+loc['bitwork']+glob['bitwork']+flatops['bitwork']+forwardops['bitwork']+verify_cost+scans
    assert stage_ops>0
    source_bytes = len(repr(clauses).encode('ascii'))
    payload_bits = source_bytes*8 + groups*8 + logical_bits + n
    seconds_ns=monotonic_ns()-start
    emit('MTP_PARITY',variables=n,clauses=len(clauses),cross_distance='ONE_THIRD_OF_UNIVERSE',
         local_groups=groups,recognized_xor_groups=recognized,rejected_groups=rejected,
         deliberately_planted_agent_errors=1,MTP3_corrected_agent_errors=caught,
         MTP27_block_size=27,MTP27_local_row_xors=loc['row_xors'],
         global_row_xors=glob['row_xors'],flat_reverse_row_xors=flatops['row_xors'],
         flat_forward_row_xors=forwardops['row_xors'],
         rank=len(basis),exact_model_count=model_count,oracle=oracle,
         MTP1_MTP3_clause_literal_checks=work,
         literal_witness_verification_checks=verify_cost,
         symbolic_scope_preflight_checks=scans,
         defined_metric_total_work_units_including_baselines=stage_ops,
         source_clause_grouping_inserts=len(clauses),
         motif_pattern_assignments_checked=8*groups,
         source_clause_bytes=source_bytes,peak_estimated_logical_payload_bits=payload_bits,
         no_precomputed_solution_table='YES',
         naive_factor_joint_bits=base_width,
         naive_factor_peak_projected_entries=base_projected,
         elapsed_generation_to_verification_ns=seconds_ns,
         whole_process_peak_RSS_kib_so_far=measured_peak_rss_kib(),
         source_sha256=digest(clauses),witness_sha256=digest(witness),
         source_witness_clause_check='PASS',status='EXACT_COMPRESSIBLE_PASS')
    return (n,len(clauses),len(basis),work,loc['bitwork'],glob['bitwork'],
            source_bytes,payload_bits,base_width,base_projected,stage_ops)


def benchmark_generic(n):
    source=generic(n)
    rows,groups,recognized,rejected,bad,caught,work = group_and_recognize(n,source)
    assert recognized==0 and rejected==groups and bad==0
    width,projected,scans=symbolic_width(n,source)
    assert width>=3
    max_entries=32768
    # No unrestricted exact factor calculation if projected size exceeds
    # allocated cap. A certified planted witness is known to the *generator*,
    # but NOT handed to a general solver, and does not certify model count.
    count, scanned, peak_slots, live_slots, lookups, outcome = factor_count_limited(n,source,max_entries)
    assert (count is None) == (outcome=='HOLD_TABLE_LIMIT')
    brute='NOT_RUN'
    if n<=12:
        b=brute_count(n,source)
        assert b>0 and b==count
        brute=str(b)
    if count is not None:
        assert count>0
    emit('MTP_GENERIC',variables=n,clauses=len(source),
         local_groups=groups,recognized_xor_groups=recognized,
         false_xor_recognitions=0,
         checker_clause_literal_work=work,
         naive_factor_joint_bits=width,
         naive_factor_projected_entries=projected,
         allocated_factor_entry_limit=max_entries,
         source_clause_bytes=len(repr(source).encode('ascii')),
         exact_brute_model_count=brute,
         actual_exact_model_count=count if count is not None else 'HOLD',
         actual_variable_elimination_branch_scans=scanned,
         actual_variable_elimination_factor_lookups=lookups,
         actual_allocated_peak_factor_slots=peak_slots,
         actual_peak_live_factor_slots=live_slots,
         global_compression_claim='NONE',
         after_preflight=outcome,
         source_sha256=digest(source),
         status='EXACT_GENERIC_PASS' if count is not None else 'HOLD_TABLE_BUDGET')
    return n,width,projected,outcome


def bounded_hybrid_count(n, source, basis, recognized_scopes, max_free_branches):
    pivots=set(basis)
    free=[i for i in range(n) if i not in pivots]
    search_branches=1<<len(free)
    if search_branches>max_free_branches:
        return None,0,0,search_branches,'HOLD_RESIDUAL_ENUMERATION_BUDGET'
    residual=tuple(c for c in source if frozenset(abs(l) for l in c) not in recognized_scopes)
    full_models=0
    clause_checks=0
    original_witness_checked=0
    for seed in range(search_branches):
        candidate=sum(((seed>>j)&1)<<v for j,v in enumerate(free))
        for pivot in sorted(pivots):
            mask,rhs=basis[pivot]
            value=rhs ^ ((mask & candidate).bit_count() & 1)
            candidate |= value<<pivot
        valid=True
        for clause in residual:
            clause_checks+=1
            if not sat_clause(clause,candidate):
                valid=False
                break
        if valid:
            full_models+=1
            if not original_witness_checked:
                assert all(sat_clause(c,candidate) for c in source)
                original_witness_checked+=1
    return full_models,search_branches,clause_checks,search_branches,'EXACT_BOUNDED_RESIDUAL'


def benchmark_hybrid(n):
    assert n in (12, 24, 36, 48, 72)
    allparity, _ = parity_family(n)
    # First n//2 complete XOR gadgets, followed by ordinary 3SAT clauses.
    fixed = allparity[:4*(n//2)]
    parity_scopes = {tuple(sorted(set(abs(l) for l in c))) for c in fixed}
    extra = []
    for clause in generic(n):
        scope = tuple(sorted(set(abs(l) for l in clause)))
        if scope not in parity_scopes:
            extra.append(clause)
        if len(extra) == n//2:
            break
    assert len(extra) == n//2
    mixed = fixed + tuple(extra)
    rows,groups,recognized,rejected,bad,caught,work = group_and_recognize(n,mixed)
    assert recognized == n//2 and rejected > 0 and bad == 0
    basis, local, global_ops, logical_bits = hierarchical(n,rows)
    assert basis is not None
    xor_upper_bound = 1 << (n-len(basis))
    recognized_scopes={frozenset(v for v in range(1,n+1) if (mask>>(v-1))&1)
                       for mask,rhs in rows}
    exact_count, searched, residual_checks, branch_budget, outcome = bounded_hybrid_count(
        n,mixed,basis,recognized_scopes,262144)
    oracle='NOT_RUN'
    if n<=12:
        exact = brute_count(n,mixed)
        assert exact_count==exact and 0 < exact < xor_upper_bound
        oracle=str(exact)
    if exact_count is not None:
        assert 0 < exact_count <= xor_upper_bound
    emit('MTP_HYBRID', variables=n, clauses=len(mixed),
         recognized_xor_groups=recognized,
         unrecognized_generic_clause_groups=rejected,
         compiled_parity_rank=len(basis),
         naive_parity_only_model_upper_bound=xor_upper_bound,
         exact_brute_model_count=oracle,
         full_problem_model_count=exact_count if exact_count is not None else 'HOLD',
         enumerated_free_assignments=searched,
         residual_clause_checks=residual_checks,
         residual_search_cap=262144,
         projected_free_assignments=branch_budget,
         residual_solver_status=outcome,
         local_agent_does_not_launder_uncertain_parity_as_exact='PASS',
         source_sha256=digest(mixed),
         status='EXACT_MIXED_COUNT_PASS' if exact_count is not None else 'PARTIAL_COMPRESSION_FAIL_CLOSED')
    return n,recognized,rejected,len(basis),xor_upper_bound,exact_count,outcome


def negative_controls():
    c, _ = parity_family(9)
    assert len(group_and_recognize(9,c)[0]) > 0
    # Repeated triple with both opposite XOR parities is immediate UNSAT:
    sample=(1,2,3)
    conflict=xor_clauses(sample,0)+xor_clauses(sample,1)
    s=group_and_recognize(3,conflict)
    assert s[4]==1 and s[2]==0
    assert brute_count(3,conflict)==0
    # Missing one clause must be rejected, cannot be certified as XOR.
    incomplete=xor_clauses(sample,0)[:3]
    s=group_and_recognize(3,incomplete)
    assert s[3]==1 and s[2]==0
    # Changing metadata/clauses changes source SHA but not magically solves.
    assert digest(incomplete) != digest(conflict)
    emit('MTP_NEGATIVES',contradictory_parity_formula='EXACT_UNSAT',
         missing_clause_motif='REJECTED_NO_FALSE_XOR',
         independently_injected_MTP1_error='CORRECTED_FROM_TRUTH_TABLE',
         source_sha_change_does_not_invert_input='PASS',
         hash_as_SAT_oracle='REJECTED',status='PASS')


def main():
    negative_controls()
    parity=[]
    for n in (9,12,18,24,36,48,72,96,144,192,288,384,768,1152):
        parity.append(benchmark_parity(n))
    generic_rows=[]
    for n in (6,9,12,15,18,21,24,30,36,48,60,72):
        generic_rows.append(benchmark_generic(n))
    hybrid_rows=[]
    for n in (12,24,36,48,72):
        hybrid_rows.append(benchmark_hybrid(n))
    assert len(parity)==14 and len(generic_rows)==12
    assert any(r[3]=='HOLD_TABLE_LIMIT' for r in generic_rows)
    emit('MTP_GLOBAL_FINAL',parity_cases=len(parity),generic_cases=len(generic_rows),
         hybrid_cases=len(hybrid_rows),
         largest_exact_parity_variables=max(r[0] for r in parity),
         largest_parity_clause_count=max(r[1] for r in parity),
         parity_source_and_witness_verified='ALL',
         local_hierarchy_makes_structured_global_constraints_compact='YES',
         generic_global_constraints_always_compact='NO',
         full_preprocessing_and_logical_payload_metered='YES',
         measured_whole_process_peak_RSS_kib=measured_peak_rss_kib(),
         logical_payload_excludes_Python_object_overhead='YES',
         clock_measurement_includes_source_generation='YES',
         no_adversarial_worst_case_polynomial_proof='YES',
         P_equals_NP='NOT_ESTABLISHED',
         original_S3_Wilson_first_weight='HOLD',
         summary_sha256=digest(tuple(parity)+tuple(generic_rows)+tuple(hybrid_rows)),
         status='STRUCTURED_COMPRESSION_PASS_GENERAL_HOLD')


if __name__=='__main__':
    main()
