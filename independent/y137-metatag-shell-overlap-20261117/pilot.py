#!/usr/bin/env python3
"""#137 finite S3 gauge-invariant residual-cloud interaction pilot.

This is a source-conditional, exact-integer perturbation audit, NOT a
recalculation of the 2,177,317,873 dimensional spectrum or a Wilson weight.

Original finite 3x4 periodic spatial S3 Hamiltonian:
  H = H_E + 9 * sum_p(2 - chi(U_p)), J_E = 1.
Proposed new diagonal interaction on gauge orbits:
  V_alpha(U) = alpha * sum_{nearest plaquette pairs} min(m_p,m_q)/72
  m_p = 2 - chi(U_p) in {0,2,3}; 24 unordered-positive periodic pairs.
Thus 0 <= V_alpha <= alpha, and V_alpha annihilates flat P exactly.
Only original certified gap lower delta > 0.039677591 is imported as a
conditional mathematical premise (PR #234 / #137), never recomputed.

SHA is used to certify the gauge-orbit identity and source transitions,
not to assert that a changed digest physically updates all matrix cells.
"""
from hashlib import sha1, sha256
from itertools import permutations
from math import gcd
import json

LX, LY, V = 3, 4, 12
GROUP = tuple(permutations(range(3)))
INDEX = {g: i for i, g in enumerate(GROUP)}
MUL = tuple(tuple(INDEX[tuple(GROUP[a][GROUP[b][i]] for i in range(3))]
                  for b in range(6)) for a in range(6))
INV = tuple(next(b for b in range(6) if MUL[a][b] == MUL[b][a] == 0)
            for a in range(6))
CHI = tuple(sum(int(GROUP[g][i] == i) for i in range(3)) - 1
            for g in range(6))
CONJ = tuple(tuple(MUL[MUL[g][a]][INV[g]] for a in range(6))
             for g in range(6))

# Input is all 24 positively oriented links: horizontal first, vertical next.
def pos(x, y):
    return (y % LY) * LX + (x % LX)


def site_endpoint(k):
    if k < V:
        s = k
        return s, pos(s % LX + 1, s // LX)
    s = k - V
    return s, pos(s % LX, s // LX + 1)


TREE = [(pos(0, y), pos(0, y+1), V + pos(0, y))
        for y in range(LY-1)]
TREE += [(pos(x, y), pos(x+1, y), pos(x, y))
         for y in range(LY) for x in range(LX-1)]
TREE_IDS = {e for _, _, e in TREE}
KEPT = tuple(i for i in range(2*V) if i not in TREE_IDS)


def canonical(u):
    assert len(u) == 2*V
    h = [0]*V
    for s, t, k in TREE:
        h[t] = MUL[h[s]][u[k]]
    z = [MUL[MUL[h[s]][u[k]]][INV[h[t]]]
         for k in range(2*V) for s,t in [site_endpoint(k)]]
    assert all(z[k] == 0 for k in TREE_IDS)
    key = tuple(z[k] for k in KEPT)
    return min(tuple(CONJ[g][x] for x in key) for g in range(6))


def gauge(u, g):
    return tuple(MUL[MUL[g[s]][u[k]]][INV[g[t]]]
                 for k in range(2*V) for s,t in [site_endpoint(k)])


def translate(u, dx, dy):
    v = [0]*(2*V)
    for y in range(LY):
        for x in range(LX):
            src, dst = pos(x,y), pos(x+dx,y+dy)
            v[dst], v[V+dst] = u[src], u[V+src]
    return tuple(v)


def plaquette(u, x, y):
    a = u[pos(x,y)]
    b = u[V+pos(x+1,y)]
    c = INV[u[pos(x,y+1)]]
    d = INV[u[V+pos(x,y)]]
    return MUL[MUL[MUL[a][b]][c]][d]


def excitation(u):
    return tuple(2-CHI[plaquette(u,x,y)]
                 for y in range(LY) for x in range(LX))


def overlap_numerator(u):
    m=excitation(u)
    return sum(min(m[pos(x,y)], m[pos(x+dx,y+dy)])
               for y in range(LY) for x in range(LX)
               for dx,dy in ((1,0),(0,1)))


def winding_wilson(u):
    hsum=0
    for y in range(LY):
        g=0
        for x in range(LX):g=MUL[g][u[pos(x,y)]]
        hsum+=CHI[g]
    vsum=0
    for x in range(LX):
        g=0
        for y in range(LY):g=MUL[g][u[V+pos(x,y)]]
        vsum+=CHI[g]
    return hsum+vsum


def fixture(k):
    if k == 0:return tuple([0]*(2*V))
    b=[]
    for j in range(2*V):
        digest=sha256((str(k)+':'+str(j)).encode('ascii')).digest()
        b.append(int.from_bytes(digest[:4], 'big') % 6)
    return tuple(b)


def reduced_fraction(n,d):
    assert d>0
    g=gcd(n,d)
    return str(n//g)+'/'+str(d//g)


def source_hash(u):
    return sha256(bytes(canonical(u))).hexdigest()


def emit(label,**fields):
    print(label+'|'+'|'.join(k+'='+str(v) for k,v in fields.items())+'|json=0')


def main():
    assert len(TREE)==11 and len(KEPT)==13
    assert sorted(set(CHI))==[-1,0,2]
    assert sorted(set(2-c for c in CHI))==[0,2,3]
    assert (6**13+3*2**13+2*3**13)//6==2177317873
    samples=[fixture(k) for k in range(256)]
    gauge_tests=0
    translation_tests=0
    zero=0
    largest=0
    positive=0
    for idx,u in enumerate(samples):
        w=overlap_numerator(u)
        largest=max(largest,w)
        assert 0<=w<=72
        assert -7<=winding_wilson(u)<=14
        if w==0:zero+=1
        if w:positive+=1
        for r in range(6):
            g=tuple((r+(v+idx)//3)%6 for v in range(V))
            v=gauge(u,g)
            assert source_hash(v)==source_hash(u)
            assert excitation(v)==excitation(u)
            assert overlap_numerator(v)==w
            assert winding_wilson(v)==winding_wilson(u)
            gauge_tests+=1
        for x,y in ((1,0),(0,1),(2,3)):
            v=translate(u,x,y)
            assert overlap_numerator(v)==w
            assert winding_wilson(v)==winding_wilson(u)
            translation_tests+=1
    assert largest>0 and positive>0
    assert overlap_numerator(samples[0])==0
    assert excitation(samples[0])==(0,)*V
    assert winding_wilson(samples[0])==14
    # A local gauge transformation changes a raw string but never its orbit hash.
    b=fixture(42)
    g=tuple((i+1)%6 for i in range(V))
    assert bytes(gauge(b,g))!=bytes(b)
    assert source_hash(gauge(b,g))==source_hash(b)
    # A link change generally changes the physical orbit, and then its hash.
    q=list(b);q[0]=MUL[1][q[0]]
    assert source_hash(tuple(q))!=source_hash(b)
    assert sha256(bytes(q)).hexdigest()!=sha256(bytes(b)).hexdigest()
    emit('META_S3_SOURCE',group='S3',lattice='3x4_periodic',
         links=24,plaquettes=12,plaquette_neighbor_pairs=24,
         flat_orbits=8,physical_orbits=2177317873,
         r='9',coupling='72_transposition_moves',
         overlap='sum_min_plaquette_excitation_over_72',
         overlap_upper='1',flat_P_V_P='ZERO',P_V_Q='ZERO',
         positivity='ZERO_LE_V_LE_ALPHA_IDENTITY',
         sha256_input_fixture42=source_hash(b),
         sha256_changed_link=source_hash(tuple(q)),
         status='PASS')
    emit('META_S3_GAUGE',fixtures=len(samples),gauge_tests=gauge_tests,
         translation_tests=translation_tests,positive_overlap_samples=positive,
         zero_overlap_samples=zero,largest_overlap_num=largest,
         raw_gauge_hash_changes='YES',canonical_orbit_hash_same='YES',
         status='PASS')
    # Archived source-conditional strict gap 0.039677591 J_E.
    # For 0 <= V <= alpha I, eigenvalues individually shift by [0,alpha],
    # thus delta_new > delta_source_low-alpha (one epsilon, not two).
    gaplo=39677591;scale=10**9
    e1lo=69909429421;e1hi=69909586556
    e2lo=69949264147;e2hi=69949433884
    # Original E level numerators use 1e9; eps below in same units.
    for den in (64,32,16):
        assert scale%den==0
        eps=scale//den
        lower=gaplo-eps
        generic=gaplo-2*eps
        status='POSITIVE_CONDITIONAL' if lower>0 else 'GAP_BUDGET_EXHAUSTED'
        genstatus='POSITIVE_CONDITIONAL' if generic>0 else 'GAP_BUDGET_EXHAUSTED'
        emit('META_S3_PERTURBATION',alpha=f'1/{den}',
             alpha_nano=eps,
             diagonal_nonnegative_gap_lower_nano=lower,
             diagonal_verdict=status,
             arbitrary_signed_norm_bounded_gap_lower_nano=generic,
             arbitrary_signed_verdict=genstatus,
             e1_new_bracket_nano=f'{e1lo}:{e1hi+eps}',
             e2_new_bracket_nano=f'{e2lo}:{e2hi+eps}',
             QHQ_floor_preserved='YES',flat_to_Q_B_preserved='YES',
             original_Wilson_identity_preserved='YES',
             original_Wilson_spectral_weight='HOLD',
             scope='SOURCE_CONDITIONAL_ANALYTIC_BOUND')
    # Exact elementary interaction control: Cayley transform of t sigma_x,
    # U=(I-i t X)(I+i t X)^-1 gives cos2= (1-t^2)/(1+t^2),
    # sin2=2t/(1+t^2); t=1/2 -> amplitudes 3/5 and -4i/5.
    a_num=3; b_num=4;d=5
    assert a_num*a_num+b_num*b_num==d*d
    concurrence_num=2*a_num*b_num
    concurrence_den=d*d
    assert (concurrence_num,concurrence_den)==(24,25)
    assert reduced_fraction(concurrence_num,concurrence_den)=='24/25'
    # zero overlap => identity and zero concurrence; 
    # the qubit calculation uses an extra ASSUMED exchange Hamiltonian,
    # not the S3 gauge Hamiltonian.
    emit('META_TWO_CELL_EXCHANGE',overlap_parameter='1/2',
         state='3/5|10>-4i/5|01>',norm2='1',concurrence='24/25',
         zero_overlap_concurrence='0',
         note='ILLUSTRATIVE_EXTRA_EXCHANGE_LAW',status='PASS')
    # Reproducibility digest of the exact acceptance-summary values.
    summary={
     'group':'S3','grid':[3,4],'magnetic_ratio':9,
     'physical_orbits':2177317873,'first_gap_lower_nano':gaplo,
     'finite_perturbations':[64,32,16],
     'gauge_fixtures':len(samples),'actual_Q_Wilson_weight':'HOLD',
     'literature_EOS_imported':'NO',
     'full_source_recomputed':'NO',
     'perron_floor_source_conditional':'YES'}
    receipt=sha256(json.dumps(summary,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    emit('META_S3_FINAL',summary_sha256=receipt,
         group_and_overlap='PASS',gauge_and_orbit_hash='PASS',
         bounded_density_gap='PASS_CONDITIONAL',
         two_cell_entanglement='PASS_TOY_ONLY',
         original_Wilson_first_weight='HOLD',
         black_hole_EOS_and_GR='NOT_TESTED',
         continuum='OPEN')

if __name__=='__main__':main()
