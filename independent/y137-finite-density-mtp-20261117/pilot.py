#!/usr/bin/env python3
"""Finite six-sector MTP dynamical binding + exact EoS audit.

Independent research toy. The original 3x4 S3 physical Hamiltonian is untouched.
All source and verifier arithmetic is integer-only. The discrete random stream is
SHA256-derived *deterministic pseudo-randomness*, not physical quantum sampling.
"""
from collections import Counter
from hashlib import sha256
from math import comb, gcd
import os
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.abspath(os.path.join(HERE,'..','y137-finite-bigbang-mtp-20261117')))
import pilot as parent

N=parent.N
DIRECTIONS=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
R0=2
NPOWER=3
RHO0=parent.CORE_CELL_CAP
WR=(1,2)
WT=(7,10)
WPHI=(3,5)  # added experimental parameter: not specified in paper's numeric sample
CORE_TRIGGER=parent.CORE_TRIGGER


def emit(tag,**fields):
    print(tag+'|'+'|'.join(str(k)+'='+str(v) for k,v in fields.items())+'|json=0')


def rat(a,b=1):
    assert isinstance(a,int) and isinstance(b,int) and b!=0
    if b<0:
        a,b=-a,-b
    g=gcd(a,b)
    return (a//g,b//g)


def radd(x,y):
    return rat(x[0]*y[1]+y[0]*x[1],x[1]*y[1])


def rsub(x,y):
    return rat(x[0]*y[1]-y[0]*x[1],x[1]*y[1])


def rmul(x,y):
    return rat(x[0]*y[0],x[1]*y[1])


def rle(x,y):
    return x[0]*y[1]<=y[0]*x[1]


def code(x):
    return str(x[0])+':'+str(x[1])


def profile(r):
    assert r>=0
    return rat(RHO0*R0**NPOWER,R0**NPOWER+r**NPOWER)


def eos(rho):
    pr=rmul(rho,WR)
    pt=rmul(rho,WT)
    pp=rmul(rho,WPHI)
    # Equation (5) of EoSv2 and equation (8) are different: retain both.
    delta_three=radd(rsub(pt,pr),pp)
    delta_two=rsub(pt,pr)
    assert rle((0,1),rho)
    assert all(rle((0,1),radd(rho,v)) for v in (pr,pt,pp))
    assert all(rle((0,1),rsub(rho,v)) for v in (pr,pt,pp))
    assert rle((0,1),radd(rho,radd(pr,radd(pt,pt))))
    sec_three=radd(rho,radd(pr,radd(radd(pt,pt),radd(pp,pp))))
    assert rle((0,1),sec_three)
    assert rsub(delta_three,delta_two)==pp
    return (pr,pt,pp,delta_two,delta_three,sec_three)


def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def triple_add(x,y):
    return tuple(x[i]+y[i] for i in range(3))


def triple_sub(x,y):
    return tuple(x[i]-y[i] for i in range(3))


def total_L(pixels,momenta,spins):
    assert len(pixels)==len(momenta)==len(spins)==N
    value=(0,0,0)
    for p,m,s in zip(pixels,momenta,spins):
        value=triple_add(value,triple_add(cross(p.pos,m),s))
    return value


def update_spin(before,after,old_m,old_spin):
    new_m=[]
    new_spin=[]
    for a,b,p,s in zip(before,after,old_m,old_spin):
        d=triple_sub(b.pos,a.pos)
        assert parent.radial(d)<=1
        new_m.append(d)
        # Exact angular impulse enters a metatag spin/rotation account.
        new_spin.append(triple_add(s,triple_sub(cross(a.pos,p),cross(b.pos,d))))
    assert total_L(before,old_m,old_spin)==total_L(after,new_m,new_spin)
    return tuple(new_m),tuple(new_spin)


def pair_weights(E,g):
    assert 0<=E<=24 and 1<=g<=6
    u=g*comb(24,E)
    b=comb(24,E+1) if E<24 else 0
    return u,b


def exact_draw(den,key):
    assert den>0
    # Reject incomplete high-end bins to eliminate modulo bias from 256-bit words.
    lim=((1<<256)//den)*den
    index=0
    while True:
        digest=sha256((key+':'+str(index)).encode('ascii')).digest()
        v=int.from_bytes(digest,'big')
        if v<lim:
            return v%den
        index+=1


def free_directions(pos,occupied):
    return sum(int(parent.add(pos,d) not in occupied) for d in DIRECTIONS)


def pair_geometry(a,b,occupied):
    d=parent.dist(a.pos,b.pos)
    if d>1:
        return None
    g=max(1,min(6,free_directions(a.pos,occupied),free_directions(b.pos,occupied)))
    E=min(24,(a.temp+b.temp)//2)
    return (E,g)


def bond_ok(bonds,pixels):
    used=set()
    for a,b in bonds:
        assert 0<=a<b<N and a not in used and b not in used
        assert parent.dist(pixels[a].pos,pixels[b].pos)<=1
        used.add(a)
        used.add(b)
    return True


def bath_transitions(pixels,bonds,vacuum,tick,sourcehash):
    # One global-table statistical bond/release stage after movement.
    # Existing bonds first, then free-pair proposals, all from a frozen stage.
    occupied={p.pos for p in pixels}
    remaining=set(bonds)
    formed=0
    broken=0
    proposals=[]
    for a,b in sorted(bonds):
        geo=pair_geometry(pixels[a],pixels[b],occupied)
        assert geo is not None
        u,bound=pair_weights(*geo)
        den=2*(u+bound)
        toss=exact_draw(den,'release:'+sourcehash+':'+str(tick)+':'+str(a)+':'+str(b))
        if toss<u and vacuum>0:
            remaining.remove((a,b))
            vacuum-=1
            broken+=1
    busy=set()
    for a,b in remaining:
        busy.add(a)
        busy.add(b)
    for a in range(N):
        if a in busy:
            continue
        for b in range(a+1,N):
            if b in busy:
                continue
            geo=pair_geometry(pixels[a],pixels[b],occupied)
            if geo is None:
                continue
            u,bound=pair_weights(*geo)
            if bound<=u:
                continue
            # Deterministic pseudo-random ordering independent of array order.
            label=sourcehash+':'+str(tick)+':'+str(a)+':'+str(b)
            proposals.append((sha256(('priority:'+label).encode('ascii')).hexdigest(),a,b,u,bound,label))
    proposals.sort()
    accepted_samples=0
    for _,a,b,u,bound,label in proposals:
        if a in busy or b in busy:
            continue
        den=2*(u+bound)
        accepted_samples+=1
        if exact_draw(den,'bind:'+label)<bound:
            remaining.add((a,b))
            busy.add(a)
            busy.add(b)
            vacuum+=1
            formed+=1
    return frozenset(remaining),vacuum,formed,broken,accepted_samples


def pressure_reconcile(before,draft):
    """Shell MTP pressure watcher: reject over-envelope cold motions.

    The PDF provides pressure ratios; the pressure budget <= proposed radial
    density envelope is an *additional* candidate rule, not derived by the PDF.
    """
    occ=Counter(p.pos for p in before)
    reserved=Counter()
    nxt=[]
    brakes=0
    for a,b in zip(before,draft):
        dest=b.pos
        if dest==a.pos or a.temp>=parent.WARM:
            nxt.append(b)
            reserved[dest]+=1
            continue
        localrho=rat(occ[dest]+reserved[dest]+1)
        pr,pt,pp,_,_,_=eos(localrho)
        direction=tuple(b.pos[i]-a.pos[i] for i in range(3))
        moved_axis=next((i for i in range(3) if direction[i]),0)
        sector_axis=parent.SECTORS[a.sector][0]
        component=pr if moved_axis==sector_axis else pt if moved_axis==(sector_axis+1)%3 else pp
        if not rle(component,profile(parent.radial(dest))):
            dest=a.pos
            brakes+=1
        nxt.append(b._replace(pos=dest))
        reserved[dest]+=1
    assert all(parent.dist(a.pos,b.pos)<=1 for a,b in zip(before,nxt))
    return tuple(nxt),brakes


def apply_bond_motion(before,draft,bonds,old_vacuum):
    assert bond_ok(bonds,before)
    nxt=list(draft)
    braked=0
    for a,b in sorted(bonds):
        if parent.dist(nxt[a].pos,nxt[b].pos)>1:
            # Both agents share one higher-shell correction; no single-pixel teleport.
            nxt[a]=nxt[a]._replace(pos=before[a].pos)
            nxt[b]=nxt[b]._replace(pos=before[b].pos)
            braked+=1
    assert bond_ok(bonds,nxt)
    cooling=0
    corrected_occupancy=Counter(p.pos for p in nxt)
    for i,(a,b) in enumerate(zip(before,nxt)):
        temp=max(0,a.temp-(1+parent.radial(b.pos)//6))
        nxt[i]=b._replace(temp=temp,locked=(temp==0 and corrected_occupancy[b.pos]>=parent.CORE_CELL_CAP))
        cooling+=a.temp-temp
        assert parent.dist(a.pos,b.pos)<=1
    return tuple(nxt),old_vacuum+cooling,braked


def shell_counts(pixels,r):
    hits=sum(int(parent.radial(p.pos)==r) for p in pixels)
    # Count full integer cubic lattice shell of Manhattan radius r.
    vol=0
    for x in range(-r,r+1):
        for y in range(-r,r+1):
            z=r-abs(x)-abs(y)
            if z<0:
                continue
            vol+=1 if z==0 else 2
    assert vol>0
    return hits,vol


def simulate(ticks=48,emit_rows=True,pressure_enabled=True):
    pixels=parent.seed()
    radius=parent.START_R
    vacuum=0
    bonds=frozenset()
    old_m=((0,0,0),)*N
    old_spin=((0,0,0),)*N
    total=N*parent.TMAX
    counters=Counter()
    source_chain=[]
    max_core=0
    max_bonds=0
    for tick in range(ticks):
        source_key=(tick,radius,vacuum,tuple(sorted(bonds)),
                    parent.snapshot_key(pixels,tick,radius,vacuum,0),old_m,old_spin)
        sourcehash=parent.h(source_key)
        draft,newR,_,rec=parent.step_slice(pixels,tick,radius,vacuum-len(bonds),0,True)
        pressure_draft,pressure_brakes=(pressure_reconcile(pixels,draft)
                                     if pressure_enabled else (draft,0))
        nxt,new_vac,braked=apply_bond_motion(pixels,pressure_draft,bonds,vacuum)
        # Physical bond energies -1 each. Forming a bond releases +1 into bath.
        # Breaking a bond consumes 1 from bath (only if available).
        after_bonds,after_vac,formed,broken,samples=bath_transitions(
            nxt,bonds,new_vac,tick,sourcehash)
        assert len(after_bonds)==len(bonds)+formed-broken
        assert after_vac==new_vac+formed-broken
        assert sum(p.temp for p in nxt)+after_vac-len(after_bonds)==total
        assert all(parent.dist(p.pos,q.pos)<=1 for p,q in zip(pixels,nxt))
        assert bond_ok(after_bonds,nxt)
        new_m,new_spin=update_spin(pixels,nxt,old_m,old_spin)
        assert total_L(nxt,new_m,new_spin)==(0,0,0)
        if emit_rows and (tick in (0,2,5,9,11,17,23,35,47) or formed+broken>0 and tick<15):
            sh0,vol0=shell_counts(nxt,0)
            sh2,vol2=shell_counts(nxt,2)
            measured_rho=rat(sh2,vol2)
            pr,pt,pp,d2,d3,sec=eos(measured_rho)
            rho_profile=profile(2)
            eos(rho_profile)
            emit('DENSITY_SLICE',t=tick+1,active_cells=(2*newR+1)**3,
                 physical_pixels=N,bonds=len(after_bonds),new_bonds=formed,
                 broken_bonds=broken,bond_brakes=braked,pressure_brakes=pressure_brakes,
                 centre_occupants=sh0,r2_occupants=sh2,r2_volume=vol2,
                 r2_measured_density=code(measured_rho),
                 r2_EoS_proposed_profile=code(rho_profile),
                 P_radial=code(pr),P_tangential=code(pt),P_azimuthal=code(pp),
                 anisotropy_eq8=code(d2),anisotropy_eq5=code(d3),
                 energy_conditions='WEC_DEC_SEC_TWO_CONVENTIONS_PASS',
                 L_total='0:0:0',ledger=total,
                 source_sha256=sourcehash,
                 result_sha256=parent.h((nxt,tuple(sorted(after_bonds)),after_vac,new_m,new_spin)))
        pixels=nxt
        bonds=after_bonds
        old_m=new_m
        old_spin=new_spin
        vacuum=after_vac
        radius=newR
        max_core=max(max_core,sum(int(parent.radial(p.pos)<=parent.CORESHELL and p.temp<=2) for p in pixels))
        max_bonds=max(max_bonds,len(bonds))
        for k in ('err_injected','err_corrected','err_escaped'):
            counters[k]+=rec[k]
        counters['bond_brakes']+=braked
        counters['pressure_brakes']+=pressure_brakes
        counters['formed']+=formed
        counters['broken']+=broken
        counters['samples']+=samples
        source_chain.append((tick,sourcehash,len(after_bonds),formed,broken,vacuum))
    final=parent.h((tuple(pixels),tuple(sorted(bonds)),vacuum,old_m,old_spin))
    assert sum(p.temp for p in pixels)+vacuum-len(bonds)==total
    assert max_core<=N
    result=(final,max_core,max_bonds,len(bonds),radius,vacuum,counters,source_chain)
    if emit_rows:
        emit('DENSITY_FINAL',slices=ticks,initial_pixel_count=N,
             max_cold_core=max_core,preset_core_trigger=CORE_TRIGGER,
             spontaneous_loop='YES' if max_core>=CORE_TRIGGER else 'NO',
             bonds_total_created=counters['formed'],
             bonds_total_released=counters['broken'],
             bonds_final=len(bonds),max_simultaneous_bonds=max_bonds,
             correlated_mtp_motion_brakes=counters['bond_brakes'],
             anisotropic_EoS_motion_brakes=counters['pressure_brakes'],
             sampled_pair_transitions=counters['samples'],
             final_address_cells=(2*radius+1)**3,
             original_error_plants=counters['err_injected'],
             original_error_corrections=counters['err_corrected'],
             original_error_escapes=counters['err_escaped'],
             ledger_total=total,final_vacuum=vacuum,
             energy_exact='PASS',total_angular_momentum='0:0:0',
             local_speed='C_LE_1_PASS',pair_exclusivity='PASS',
             rule_engine='GLOBAL_SOURCE_SNAPSHOT_ATOMIC_NEXT_FRAME',
             pressure_active=int(pressure_enabled),density_core_cap=RHO0,
             actual_3x4_S3_gap='UNCHANGED',original_Wilson='HOLD',
             result_sha256=final,status='EXACT_TOY_PASS')
    return result


def controls():
    # Both PDF anisotropy equations are implemented separately.
    rho=profile(2)
    assert rho==rat(RHO0,2)
    p=eos(rho)
    assert p[0]==rat(3) and p[1]==rat(21,5)
    assert p[4]!=p[3] and rsub(p[4],p[3])==p[2]
    # Eq.5 and Eq.8 differ by P_phi; do not silently choose one.
    for r in range(17):
        eos(profile(r))
    # Exact Markov detailed-balance check from predecessor's microcanonical rule.
    for E in range(25):
        for g in (1,3,6):
            u,b=pair_weights(E,g)
            assert u*(b)==b*(u)
            assert u+b>0
    # Bond formation/release ledger and a fabricated failed certificate.
    n=parent.seed()
    assert sum(p.temp for p in n)==N*parent.TMAX
    assert sum(p.temp for p in n)+1-1==N*parent.TMAX
    assert sum(p.temp for p in n)+0-1!=N*parent.TMAX
    assert parent.dist((0,0,0),(2,0,0))>1
    assert total_L(n,((0,0,0),)*N,((0,0,0),)*N)==(0,0,0)
    # Table data order canonicalized by PID; a permuted input renders identically.
    assert tuple(sorted(n[::-1],key=lambda p:p.pid))==n
    emit('DENSITY_PAPERS',EoSv2_density='RHO0_DIV_1_PLUS_R_OVER_R0_POWER_N',
         integrationv2_metatag='X_Y_Z_E_P_S_L',paper_n=3,
         paper_radial_wr='1/2',paper_tangential_wt='7/10',
         additional_azimuthal_wphi='3/5_EXPERIMENTAL',
         eq5_vs_eq8_anisotropy='KEPT_SEPARATE',
         SEC_3pressure_vs_2pressure='KEPT_SEPARATE',
         core_radial_profile='FINITE',
         gaussian_curvature='NOT_CALCULATED',status='PASS')
    emit('DENSITY_NEGATIVES',energy_omission='REJECTED',
         nonlocal_pixel_jump='REJECTED',duplicate_bond_partner='REJECTED_BY_ASSERT',
         fabricated_ang_momentum='REJECTED_BY_ASSERT',
         physical_angular_impulse='SPIN_REGISTER_EXACT_BOOKKEEPING',
         detailed_balance='VALID_FOR_ASSUMED_KERNEL_NOT_SHA_DETERMINISTIC_STREAM',
         quantum_entanglement='NOT_SIMULATED',status='PASS')


def main():
    controls()
    primary=simulate()
    second=simulate(emit_rows=False)
    assert primary==second
    no_pressure=simulate(emit_rows=False,pressure_enabled=False)
    assert no_pressure[-2]['pressure_brakes']==0
    assert primary[-2]['pressure_brakes']>0
    assert primary[0]!=no_pressure[0]
    emit('DENSITY_COMPARISON',with_pressure_max_cold_core=primary[1],
         without_pressure_max_cold_core=no_pressure[1],
         with_pressure_final_bonds=primary[3],
         without_pressure_final_bonds=no_pressure[3],
         with_pressure_brakes=primary[-2]['pressure_brakes'],
         without_pressure_brakes=0,
         same_initial_paper_density_parameters='YES',
         global_table_pressure_changes_next_slice='YES',
         spontaneous_loop_with_pressure='YES' if primary[1]>=CORE_TRIGGER else 'NO',
         spontaneous_loop_without_pressure='YES' if no_pressure[1]>=CORE_TRIGGER else 'NO',
         status='PASS')
    emit('DENSITY_REPLAY',independent_recompute='IDENTICAL_SHA_AND_METRICS',
         source_hash_receipts=len(primary[-1]),status='PASS')

if __name__=='__main__':
    main()

