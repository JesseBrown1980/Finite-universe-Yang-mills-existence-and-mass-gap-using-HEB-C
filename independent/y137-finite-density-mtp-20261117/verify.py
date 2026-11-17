#!/usr/bin/env python3
"""Independent receipt-level exact-integer EoS and finite-MTP pilot checker."""
from collections import Counter
from math import gcd
import sys


def parse(line):
    cols=line.strip().split('|')
    assert len(cols)>2 and cols[-1] in ('','json=0')
    d={}
    for x in cols[1:]:
        if x=='':
            continue
        k,v=x.split('=',1)
        assert k not in d
        d[k]=v
    return cols[0],d


def q(s):
    a,b=map(int,s.split(':'))
    assert b>0 and gcd(a,b)==1
    return a,b


def eq_scale(part,whole,num,den):
    a,b=part; c,d=whole
    return a*d*den==c*b*num


def eq_plus(total,a,b):
    x,y=total;m,n=a;p,z=b
    return x*n*z==y*(m*z+p*n)


def finite_pressure(row):
    rho=q(row['r2_measured_density'])
    pr=q(row['P_radial']);pt=q(row['P_tangential']);pp=q(row['P_azimuthal'])
    d8=q(row['anisotropy_eq8']);d5=q(row['anisotropy_eq5'])
    assert eq_scale(pr,rho,1,2)
    assert eq_scale(pt,rho,7,10)
    assert eq_scale(pp,rho,3,5)
    assert eq_plus(pt,d8,pr)
    assert eq_plus(d5,d8,pp)
    assert q(row['r2_EoS_proposed_profile'])==(6,1)
    assert row['ledger']=='1728' and row['L_total']=='0:0:0'
    assert row['energy_conditions']=='WEC_DEC_SEC_TWO_CONVENTIONS_PASS'
    assert len(row['source_sha256'])==64 and len(row['result_sha256'])==64
    for x in (pr,pt,pp):
        assert x[0]>=0
        assert x[0]*rho[1]<=rho[0]*x[1]
    return True


def main():
    assert len(sys.argv)==2
    lines=open(sys.argv[1],encoding='utf8').read().splitlines()
    data=[parse(line) for line in lines]
    group=Counter(k for k,_ in data)
    assert group['DENSITY_PAPERS']==1 and group['DENSITY_NEGATIVES']==1
    assert group['DENSITY_SLICE']>=8
    assert group['DENSITY_FINAL']==1 and group['DENSITY_COMPARISON']==1
    assert group['DENSITY_REPLAY']==1
    snap=[d for k,d in data if k=='DENSITY_SLICE']
    assert all(finite_pressure(x) for x in snap)
    final=next(d for k,d in data if k=='DENSITY_FINAL')
    comp=next(d for k,d in data if k=='DENSITY_COMPARISON')
    assert int(final['bonds_total_created'])-int(final['bonds_total_released'])==int(final['bonds_final'])
    assert int(final['final_vacuum'])-int(final['bonds_final'])==1728
    assert final['energy_exact']=='PASS' and final['local_speed']=='C_LE_1_PASS'
    assert final['total_angular_momentum']=='0:0:0'
    assert final['pair_exclusivity']=='PASS' and final['pressure_active']=='1'
    assert int(final['spontaneous_loop']=='YES')==0
    assert int(final['max_cold_core'])<int(final['preset_core_trigger'])
    assert int(final['anisotropic_EoS_motion_brakes'])>0
    assert int(final['bonds_total_created'])>0 and int(final['bonds_total_released'])>0
    assert int(comp['with_pressure_brakes'])==int(final['anisotropic_EoS_motion_brakes'])
    assert comp['without_pressure_brakes']=='0'
    assert int(comp['without_pressure_max_cold_core'])>int(comp['with_pressure_max_cold_core'])
    assert comp['global_table_pressure_changes_next_slice']=='YES'
    assert comp['spontaneous_loop_with_pressure']=='NO'
    assert comp['spontaneous_loop_without_pressure']=='NO'
    assert next(d for k,d in data if k=='DENSITY_REPLAY')['status']=='PASS'
    print('DENSITY_INDEPENDENT_ACCEPT|snapshot_pressure_rows='+str(len(snap))+
          '|rational_EoS_3components_and_2anisotropies=PASS'+
          '|bond_creation_destruction_ledger=PASS'+
          '|angular_and_local_c_gates=PASS'+
          '|pressure_arm_independently_crosschecked=PASS'+
          '|spontaneous_loop=NO|status=PASS|json=0')

if __name__=='__main__':
    main()

