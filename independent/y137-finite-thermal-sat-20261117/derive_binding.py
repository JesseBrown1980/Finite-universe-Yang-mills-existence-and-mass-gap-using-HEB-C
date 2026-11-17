#!/usr/bin/env python3
"""Exact microcanonical binding preference from finite bath degeneracies."""
from hashlib import sha256
from math import comb

def emit(tag, **kw):
    print(tag+'|'+'|'.join(str(k)+'='+str(v) for k,v in kw.items())+'|json=0')

def counts(R,E,g):
    assert R>=1 and 0<=E<=R and 1<=g<=6
    return g*comb(R,E), comb(R,E+1) if E+1<=R else 0

def gate(R,E,g):
    u,b=counts(R,E,g)
    return 'BIND_FAVORED' if b>u else 'SEPARATE_FAVORED' if b<u else 'EQUAL'

def lazy_reversible_kernel(R,E,g):
    u,b=counts(R,E,g)
    q=u+b
    assert q>0
    rows=((2*u+b,b),(u,u+2*b))
    assert all(sum(row)==2*q for row in rows)
    assert u*rows[0][1]==b*rows[1][0]
    assert rows[0][0]-rows[1][0]==q
    return rows,2*q

def enumerate_reference(R,E,g):
    assert R<=10
    u=b=0
    for mask in range(1<<R):
        k=mask.bit_count()
        if k==E:
            for _direction in range(g):
                u+=1
        if k==E+1:
            b+=1
    return u,b

def main():
    cases=0
    for R in (4,6,8,10):
        for E in range(R+1):
            for g in range(1,7):
                assert enumerate_reference(R,E,g)==counts(R,E,g)
                lazy_reversible_kernel(R,E,g)
                cases+=1
    emit('THERMAL_ORACLE',enumerated_cases=cases,
         independent_bath_bitmask_counts='PASS',
         detailed_balance='PASS',stochastic_row_sums='PASS',
         lazy_markov_spectral_gap='1/2',
         actual_YM_gap='NOT_TESTED',status='PASS')
    data=[]
    for R in (24,48):
        for g in (6,3,1):
            favor=[E for E in range(R+1) if gate(R,E,g)=='BIND_FAVORED']
            ties=[E for E in range(R+1) if gate(R,E,g)=='EQUAL']
            assert favor==list(range(len(favor)))
            cutoff=max(favor) if favor else -1
            for E in range(R):
                u,b=counts(R,E,g)
                assert b*g*(E+1)==u*(R-E)
            data.append((R,g,cutoff))
            emit('THERMAL_CROSSOVER',bath_modes=R,
                 available_separation_directions=g,
                 max_bath_excitation_preferring_binding=cutoff,
                 exactly_equal_energy_levels=':'.join(str(v) for v in ties) or 'NONE',
                 condition='R_MINUS_E_GT_G_TIMES_E_PLUS_ONE',
                 cutoff_origin='FINITE_MICROSTATE_DEGENERACIES',status='PASS')
    for E in (0,1,2,3,6,12,18,23,24):
        u,b=counts(24,E,6)
        rows,d=lazy_reversible_kernel(24,E,6)
        emit('THERMAL_SAMPLE',bath_modes=24,bath_excitation=E,directions=6,
             unbound_multiplicity=u,bound_multiplicity=b,
             bound_probability_num=b,bound_probability_den=u+b,
             transition_numerators=':'.join(str(v) for row in rows for v in row),
             transition_denominator=d,preferred=gate(24,E,6))
    assert gate(24,4,6)=='SEPARATE_FAVORED'
    assert gate(24,4,3)=='BIND_FAVORED'
    assert gate(24,4,1)=='BIND_FAVORED'
    emit('THERMAL_DENSITY',bath_modes=24,bath_excitation=4,
         free_routes_six=gate(24,4,6),
         crowded_routes_three=gate(24,4,3),
         highly_crowded_routes_one=gate(24,4,1),
         same_bath_energy='YES',status='PASS')
    # Complete occupancy is not a Big Loop theorem; swaps remain possible.
    two_full=((0,1),(1,0))
    assert all(len(set(v))==2 for v in two_full) and two_full[0]!=two_full[1]
    emit('THERMAL_BIGLOOP_NEGATIVE',
         fully_occupied_two_cell_universe='YES',
         allowed_swap_transition='YES',
         saturation_implies_unique_big_crunch='NO',
         cosmic_reset='SEPARATE_DYNAMICAL_POSTULATE',status='PASS')
    emit('THERMAL_FINAL',
         threshold_receipt_sha256=sha256(repr(tuple(data)).encode('ascii')).hexdigest(),
         assumed_finite_energy_reservoir='YES',assumed_unit_binding_energy='YES',
         observed_QCD_transition_temperature='NOT_DERIVED',
         full_six_pyramid_simulation='RULE_NOT_YET_WIRED',
         original_S3_gap='UNCHANGED',S3_first_Wilson_weight='HOLD',status='PASS')

if __name__=='__main__':
    main()
