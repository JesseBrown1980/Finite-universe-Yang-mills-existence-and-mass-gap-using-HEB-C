#!/usr/bin/env python3
"""Exact #3SAT global-factor count. Exhaustively audited small instances."""
from hashlib import sha256

def emit(tag, **kw):
    print(tag+'|'+'|'.join(str(k)+'='+str(v) for k,v in kw.items())+'|json=0')

def planted(n):
    return tuple(sha256(('seed:'+str(i)).encode('ascii')).digest()[0]&1
                 for i in range(n))

def clause_for(triplet,seed,bits):
    assert len(set(triplet))==3
    literals=[]
    for j,v in enumerate(triplet):
        h=sha256((str(seed)+':'+str(j)+':'+str(v)).encode('ascii')).digest()[0]
        literals.append(v if h&1 else -v)
    if not any((lit>0)==bool(bits[abs(lit)-1]) for lit in literals):
        literals[0]=-literals[0]
    assert any((lit>0)==bool(bits[abs(lit)-1]) for lit in literals)
    return tuple(literals)

def make_family(n,kind):
    bits=planted(n)
    clauses=[]
    if kind=='BOUNDED_WINDOW':
        for i in range(1,n-1):
            triple=(i,i+1,i+2)
            clauses.append(clause_for(triple,3*i,bits))
            clauses.append(clause_for(triple,3*i+1,bits))
    elif kind=='CROSS_COUPLED':
        assert n%3==0
        for i in range(n):
            a=i+1
            b=((i+n//3)%n)+1
            c=((i+2*n//3)%n)+1
            assert len({a,b,c})==3
            clauses.append(clause_for((a,b,c),i*7+1,bits))
            aa=i+1
            bb=((i+1)%n)+1
            cc=((i+n//2)%n)+1
            assert len({aa,bb,cc})==3
            clauses.append(clause_for((aa,bb,cc),i*7+2,bits))
    else:
        raise ValueError('unknown family')
    return tuple(clauses),bits

def satisfies_clause(c,assignment):
    return any(bool((assignment>>(abs(lit)-1))&1)==(lit>0) for lit in c)

def brute_count(n,clauses):
    solutions=0
    for assignment in range(1<<n):
        if all(satisfies_clause(c,assignment) for c in clauses):
            solutions+=1
    return solutions

def factor_clause(c):
    scope=tuple(sorted({abs(v) for v in c}))
    values=[]
    for index in range(1<<len(scope)):
        assignment=sum(((index>>k)&1)<<(v-1) for k,v in enumerate(scope))
        values.append(int(satisfies_clause(c,assignment)))
    return scope,tuple(values)

def project_mask(mask,positions):
    x=0
    for i,p in enumerate(positions):
        x|=((mask>>p)&1)<<i
    return x

def count_eliminate(n,clauses):
    factors=[factor_clause(c) for c in clauses]
    scanned=0
    max_union=0
    peak_factor_slots=max(len(v) for _,v in factors)
    peak_live_slots=sum(len(v) for _,v in factors)
    for variable in range(1,n+1):
        participating=[f for f in factors if variable in f[0]]
        unaffected=[f for f in factors if variable not in f[0]]
        if not participating:
            unaffected.append(((),(2,)))
            factors=unaffected
            continue
        union=tuple(sorted(set(v for scope,_ in participating for v in scope)))
        remaining=tuple(v for v in union if v!=variable)
        max_union=max(max_union,len(union))
        uindex={v:i for i,v in enumerate(union)}
        remaining_positions=[uindex[v] for v in remaining]
        variable_pos=uindex[variable]
        projections=[(values,tuple(uindex[v] for v in scope))
                     for scope,values in participating]
        new=[]
        for bits in range(1<<len(remaining)):
            lower=sum(((bits>>i)&1)<<p for i,p in enumerate(remaining_positions))
            total=0
            for val in (0,1):
                full=lower|(val<<variable_pos)
                term=1
                for values,positions in projections:
                    term*=values[project_mask(full,positions)]
                    if not term:
                        break
                total+=term
            new.append(total)
        scanned+=1<<len(union)
        factors=unaffected+[(remaining,tuple(new))]
        peak_factor_slots=max(peak_factor_slots,len(new))
        peak_live_slots=max(peak_live_slots,sum(len(v) for _,v in factors))
    result=1
    for scope,values in factors:
        assert not scope
        result*=values[0]
    return result,scanned,max_union,peak_factor_slots,peak_live_slots

def test_controls():
    assert brute_count(3,((1,2,3),))==7
    assert count_eliminate(3,((1,2,3),))[0]==7
    assert brute_count(3,((1,2,3),(-1,-2,-3)))==6
    assert count_eliminate(3,((1,2,3),(-1,-2,-3)))[0]==6
    forbid=tuple(tuple(v if not (bits>>(v-1))&1 else -v
                       for v in (1,2,3)) for bits in range(8))
    assert brute_count(3,forbid)==0
    assert count_eliminate(3,forbid)[0]==0
    forced=((1,1,1),(-2,-2,-2),(3,3,3))
    assert brute_count(3,forced)==1
    assert count_eliminate(3,forced)[0]==1
    return 4

def main():
    cases=test_controls()
    emit('SAT_ORACLE',controls=cases,models_7_6_0_1='PASS',
         independent_complete_assignment_enumeration='PASS',status='PASS')
    source=[]
    summaries=[]
    for kind in ('BOUNDED_WINDOW','CROSS_COUPLED'):
        for n in (6,9,12,15,18,21):
            clauses,bits=make_family(n,kind)
            assert all(any((lit>0)==bool(bits[abs(lit)-1]) for lit in c)
                       for c in clauses)
            count,scanned,width,peak,live=count_eliminate(n,clauses)
            assert count>=1
            oracle='NOT_RUN'
            if n<=15:
                assert brute_count(n,clauses)==count
                oracle='FULL_2POWN_PASS'
            source.append((kind,n,clauses,count,width))
            summaries.append((kind,n,scanned,width,peak,live))
            emit('SAT_BENCH',family=kind,variables=n,clauses=len(clauses),
                 models_exact=count,global_factor_bits=width,
                 projected_factor_peak_entries=peak,
                 simultaneous_factor_peak_entries=live,
                 branch_assignments_evaluated=scanned,
                 full_enumeration_assignments=1<<n,oracle=oracle,
                 source_sha256=sha256(repr(clauses).encode('ascii')).hexdigest(),
                 result_sha256=sha256(repr((count,scanned,width,peak,live)).encode('ascii')).hexdigest(),
                 status='PASS')
    windows=[x for x in summaries if x[0]=='BOUNDED_WINDOW']
    cross=[x for x in summaries if x[0]=='CROSS_COUPLED']
    assert all(x[3]<=3 for x in windows)
    assert any(x[3]>3 for x in cross)
    emit('SAT_FINAL',families=2,sizes='6:9:12:15:18:21',
         bounded_frontier_max_joint_bits=max(x[3] for x in windows),
         cross_coupled_max_joint_bits=max(x[3] for x in cross),
         tested_sat_instances=len(source),
         complete_bruteforce_confirmed=sum(int(x[1]<=15) for x in source),
         global_hash_solves_sat_without_preimage='NO',
         finite_global_catalog_implies_P_equals_NP='NO',
         complexity_proof='NOT_CLAIMED',
         evidence_sha256=sha256(repr(source).encode('ascii')).hexdigest(),
         status='EXACT_MODEL_COUNT_PASS')

if __name__=='__main__':
    main()
