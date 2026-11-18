#!/usr/bin/env python3
"""Integer-only, reproducible 3x4x8 Euclidean S3 heatbath/cooling pilot.

Hamiltonian-matched symmetric Trotter transfer at a=ln(2)/3, J_E=1,
J_B=9. This is a finite-step approximation, not the exact e^{-a H}.
Temporal plaquette heat-kernel weights: identity 13, transposition 3,
3-cycle 1 (overall 24). Spatial plaquette weights: 8^(chi+1)
(1, 8, 512), equivalent to e^{-a*9*(2-chi)} up to a common factor.
The temporal links enforce the gauge projection in the path integral.
No continuum/mass-gap/true-Wilson-weight certificate is claimed.
"""
from itertools import permutations
from random import Random
from hashlib import sha256
from math import gcd
import sys

LX, LY, NT = 3, 4, 8
V = LX * LY * NT
P = tuple(permutations(range(3)))
IDX = {p: i for i, p in enumerate(P)}
MUL = tuple(tuple(IDX[tuple(P[a][P[b][k]] for k in range(3))]
                  for b in range(6)) for a in range(6))
INV = tuple(next(j for j in range(6) if MUL[i][j] == MUL[j][i] == 0)
            for i in range(6))
CHI = tuple(sum(P[i][k] == k for k in range(3))-1 for i in range(6))
TEMP = tuple(13 if c == 2 else 3 if c == 0 else 1 for c in CHI)
SPAT = tuple(8 ** (c+1) for c in CHI)
TRANS = tuple(i for i in range(6) if CHI[i] == 0)
assert len(TRANS) == 3 and CHI[0] == 2


def node(x, y, t):
    return (t % NT * LY + y % LY) * LX + x % LX


def edge(x, y, t, d):
    return 3 * node(x, y, t) + d


def shift(x, y, t, d):
    if d == 0:
        return (x+1, y, t)
    if d == 1:
        return (x, y+1, t)
    return (x, y, t+1)


PLAQS = []
INC = [[] for _ in range(3*V)]
SPATIAL = []
for t in range(NT):
    for y in range(LY):
        for x in range(LX):
            for d, e in ((0,1),(0,2),(1,2)):
                xd,yd,td = shift(x,y,t,d)
                xe,ye,te = shift(x,y,t,e)
                p = ((edge(x,y,t,d), 1),
                     (edge(xd,yd,td,e), 1),
                     (edge(xe,ye,te,d), -1),
                     (edge(x,y,t,e), -1))
                k=len(PLAQS)
                PLAQS.append((p, d==0 and e==1))
                if d==0 and e==1:
                    SPATIAL.append(k)
                for j,_ in p:
                    INC[j].append(k)
assert len(PLAQS) == 3*V and len(SPATIAL)==V
assert all(len(z)==4 for z in INC)
SPATSET=set(SPATIAL)
SPATLINKS=tuple(i for i in range(3*V) if i % 3 != 2)


def hol(U,k):
    p,_=PLAQS[k]
    a=0
    for e,sign in p:
        v=U[e]
        a=MUL[a][v if sign==1 else INV[v]]
    return a


def local_weight(U,i,kind='all'):
    z=1
    for k in INC[i]:
        if kind=='spatial' and k not in SPATSET:
            continue
        v=hol(U,k)
        z*=SPAT[v] if k in SPATSET else TEMP[v]
    return z


def heatbath(U, i, rng):
    old=U[i]
    ws=[]
    for g in range(6):
        U[i]=g
        ws.append(local_weight(U,i))
    U[i]=old
    total=sum(ws)
    assert total>0
    r=rng.randrange(total)
    for g,w in enumerate(ws):
        if r<w:
            U[i]=g
            return
        r-=w
    raise AssertionError('heatbath_partition')


def microcanonical(U,i,rng):
    old=U[i]
    w=local_weight(U,i)
    equal=[]
    for g in range(6):
        U[i]=g
        if local_weight(U,i)==w:
            equal.append(g)
    U[i]=equal[rng.randrange(len(equal))]
    assert local_weight(U,i)==w


def sheet_move(U,rng):
    """Reversible global toron-sheet Metropolis proposal with exact weights.

    Shared left multiplication along a full spatial boundary sheet, for
    every Euclidean time slice. Proposals g and g^-1 are equally probable.
    In particular, this can escape an exactly flat cold-start sector.
    """
    direction=rng.randrange(2)
    g=1+rng.randrange(5)
    if direction==0:
        links=[edge(LX-1,y,t,0) for t in range(NT) for y in range(LY)]
    else:
        links=[edge(x,LY-1,t,1) for t in range(NT) for x in range(LX)]
    touched=set(k for e in links for k in INC[e])
    def local_product():
        total=1
        for k in touched:
            h=hol(U,k)
            total*=SPAT[h] if k in SPATSET else TEMP[h]
        return total
    old_weight=local_product()
    old_links=[U[e] for e in links]
    for e in links:
        U[e]=MUL[g][U[e]]
    new_weight=local_product()
    assert old_weight>0 and new_weight>0
    if new_weight>=old_weight or rng.randrange(old_weight)<new_weight:
        return 1
    for e,old in zip(links,old_links):
        U[e]=old
    return 0


def sweep(U,rng,sheets=True):
    # Shuffle order with seeded integer PRNG, exact categorical heat-bath.
    inds=list(range(3*V))
    rng.shuffle(inds)
    for i in inds:
        heatbath(U,i,rng)
    # One conditional microcanonical move per link is reversible given U_-i.
    rng.shuffle(inds)
    for i in inds:
        microcanonical(U,i,rng)
    accepted=0
    if sheets:
        accepted=sheet_move(U,rng)+sheet_move(U,rng)
    return accepted


def magnetic(U):
    return sum(2-CHI[hol(U,k)] for k in SPATIAL)


def winding(U,t):
    horizontal=0
    for y in range(LY):
        v=0
        for x in range(LX):
            v=MUL[v][U[edge(x,y,t,0)]]
        horizontal+=CHI[v]
    vertical=0
    for x in range(LX):
        v=0
        for y in range(LY):
            v=MUL[v][U[edge(x,y,t,1)]]
        vertical+=CHI[v]
    return horizontal+vertical


def spatial_cooling(U,rng):
    inds=list(SPATLINKS)
    rng.shuffle(inds)
    before=magnetic(U)
    for i in inds:
        old=U[i]
        vals=[]
        for g in range(6):
            U[i]=g
            vals.append(local_weight(U,i,'spatial'))
        maximum=max(vals)
        winners=[g for g,w in enumerate(vals) if w==maximum]
        U[i]=old if old in winners else winners[rng.randrange(len(winners))]
    assert magnetic(U)<=before


def gauge(U, rng):
    g=[rng.randrange(6) for _ in range(V)]
    O=[0]*(3*V)
    for t in range(NT):
        for y in range(LY):
            for x in range(LX):
                n=node(x,y,t)
                for d in range(3):
                    X,Y,T=shift(x,y,t,d)
                    j=edge(x,y,t,d)
                    O[j]=MUL[MUL[g[n]][U[j]]][INV[g[node(X,Y,T)]]]
    return O


def kernel_check():
    # Exact heat kernel e^{-a (3 I - sum_{transpositions} L_t)}
    # at a=ln(2)/3: central Fourier eigenvalues (1,1/4,1/2).
    assert sum(TEMP)==24
    signs=[]
    for p in P:
        inversions=sum(p[i]>p[j] for i in range(3) for j in range(i+1,3))
        signs.append(1 if inversions%2==0 else -1)
    assert sum(TEMP[i]*signs[i] for i in range(6))==6
    assert sum(TEMP[i]*CHI[i] for i in range(6))==24
    assert all(MUL[i][INV[i]]==0 for i in range(6))
    assert sorted(CHI)==[-1,-1,0,0,0,2]
    assert sorted(set(SPAT))==[1,8,512]
    print('S3_EUCLIDEAN_KERNEL|L=3x4x8|spatial_links=192|temporal_links=96'
          '|spatial_plaquettes=96|temporal_plaquettes=192'
          '|heat_kernel_identity=13|heat_kernel_transposition=3'
          '|heat_kernel_three_cycle=1|Fourier_triv=1/1'
          '|Fourier_sign=1/4|Fourier_std=1/2'
          '|trotter_a=ln2/3|r=9|status=PASS|json=0',flush=True)


def controls():
    rng=Random(731)
    for j in range(8):
        U=[rng.randrange(6) for _ in range(3*V)]
        G=gauge(U,rng)
        assert [hol(U,k) for k in SPATIAL] != [0]*len(SPATIAL)
        assert magnetic(U)==magnetic(G)
        assert all(CHI[hol(U,k)]==CHI[hol(G,k)] for k in range(len(PLAQS)))
        assert [winding(U,t) for t in range(NT)] == [winding(G,t) for t in range(NT)]
        # Map the six link candidates under an endpoint gauge change.
        i=3*(j*7 % V)+j%3
        w=[]
        wg=[]
        for c in range(6):
            temp=U[i]
            U[i]=c
            w.append(local_weight(U,i))
            U[i]=temp
            temp=G[i]
            G[i]=c
            wg.append(local_weight(G,i))
            G[i]=temp
        assert sorted(w)==sorted(wg)
        cooling=U[:]
        for _ in range(3):
            spatial_cooling(cooling,rng)
        assert magnetic(cooling)<=magnetic(U)
    # The original cold flat sheet is an exact-energy sector-moving control.
    U=[0]*(3*V)
    old=magnetic(U)
    r=Random(111)
    accepted=sheet_move(U,r)
    assert accepted==1 and magnetic(U)==old and any(winding(U,t)!=14 for t in range(NT))
    # A naive nonclosed link character is NOT gauge invariant.
    U=[0]*(3*V)
    G=U[:]
    G[0]=TRANS[0]
    assert CHI[U[0]]!=CHI[G[0]]
    # Negative control: erasing Q temporal-class discrimination corrupts kernel.
    assert TEMP[0]!=TEMP[TRANS[0]] and TEMP[TRANS[0]]!=TEMP[3]
    print('S3_EUCLIDEAN_CONTROLS|gauge=8|conditional_class_multisets=8'
          '|spatial_cooling_monotone=8|flat_sheet_move=PASS|negative_controls=2'
          '|status=PASS|json=0',flush=True)


DEPTHS=(0,1,2,4)

def measure(U,rng, data, aux, chain, k, nsamp):
    W=U[:]
    for step in range(5):
        if step:
            spatial_cooling(W,rng)
        if step not in DEPTHS:
            continue
        z=[winding(W,t) for t in range(NT)]
        for D in (data[step],aux[step]):
            D['n']+=NT
            D['sum']+=sum(z)
            D['sumsq']+=sum(v*v for v in z)
            D['mag']+=magnetic(W)
            for tau in (1,2,3):
                D['prod'+str(tau)]+=sum(z[t]*z[(t+tau)%NT] for t in range(NT))
                D['timecen'+str(tau)]+=NT*sum(z[t]*z[(t+tau)%NT] for t in range(NT))-sum(z)**2
            D['hash'].update(bytes((x+7) for x in z))
        if k in (0,nsamp//2,nsamp-1):
            raw=bytes(W)
            print('S3_EUCLIDEAN_SNAPSHOT|chain='+str(chain)+'|sample='+str(k)
                  +'|depth='+str(step)+'|links_hex='+raw.hex()
                  +'|sha256='+sha256(raw).hexdigest()+'|json=0',flush=True)


def record(label,D):
    n=D['n']
    q=D['sum']
    # Exact integer connected covariance numerator over n^2.
    out=[]
    for tau in (1,2,3):
        num=n*D['prod'+str(tau)]-q*q
        den=n*n
        g=gcd(abs(num),den)
        out.append('C'+str(tau)+'_numer='+str(num//g))
        out.append('C'+str(tau)+'_denom='+str(den//g))
        out.append('C'+str(tau)+'_milli='+str((1000*num)//den))
        out.append('within_C'+str(tau)+'_milli='+str(1000*D['timecen'+str(tau)]//(n*NT)))
    varnum=n*D['sumsq']-q*q
    print('S3_EUCLIDEAN_MEASUREMENT|'+label+
          '|N='+str(n)+'|O_mean_milli='+str(1000*q//n)+
          '|O_var_milli='+str(1000*varnum//(n*n))+
          '|magnetic_mean_per_slice_milli='+str(1000*D['mag']*NT//(n*NT))+
          '|'+ '|'.join(out)+'|winding_sha256='+D['hash'].hexdigest()+
          '|statistical_only=YES|wilson_E2_weight=NOT_COMPUTED|json=0',flush=True)


def new_data():
    return {z:{'n':0,'sum':0,'sumsq':0,'mag':0,'prod1':0,
               'prod2':0,'prod3':0,'timecen1':0,'timecen2':0,'timecen3':0,'hash':sha256()} for z in DEPTHS}


def main():
    kernel_check()
    controls()
    cli=sys.argv[1:]
    if cli and cli!=['--pilot'] and cli!=['--quick'] and cli!=['--no-sheet']:
        raise SystemExit('usage: pilot.py [--quick|--pilot|--no-sheet]')
    quick=cli==['--quick']
    sheets=cli!=['--no-sheet']
    burn=12 if quick else 80
    nsamp=12 if quick else 80
    stride=2 if quick else 4
    data=new_data()
    for chain in range(2):
        rng=Random(20261117+chain*8009)
        U=([0]*(3*V) if chain==0 else [rng.randrange(6) for _ in range(3*V)])
        cdata=new_data()
        accepted=0
        for _ in range(burn):
            accepted+=sweep(U,rng,sheets)
        for k in range(nsamp):
            for _ in range(stride):
                accepted+=sweep(U,rng,sheets)
            measure(U,rng,data,cdata,chain,k,nsamp)
        print('S3_EUCLIDEAN_CHAIN|chain='+str(chain)+'|sheet_moves='+str(2*(burn+nsamp*stride) if sheets else 0)+'|sheet_accepted='+str(accepted)+'|json=0',flush=True)
        for d in DEPTHS:
            record('chain='+str(chain)+'|depth='+str(d),cdata[d])
    for d in DEPTHS:
        record('chain=pooled|depth='+str(d),data[d])
    print('S3_EUCLIDEAN_VERDICT|sampler=EXACT_INTEGER_HEATBATH_PLUS_MICROCANONICAL'
          '|Euclidean_transfer=FINITE_TROTTER_MATCHED_TO_ORIGINAL_S3_r9'
          '|Wilson_operator=ORIGINAL_7_LOOP_PER_SLICE'
          '|cooling=SPATIAL_MAGNETIC_ONLY|temporal_transfer=UNCHANGED'
          '|sheet_metropolis='+('YES' if sheets else 'NO')
          +'|exact_mass_gap_certificate=NO|first_Wilson_weight=HOLD'
          '|continuum=OPEN|status=PILOT_COMPLETE|json=0',flush=True)


if __name__=='__main__':
    main()
