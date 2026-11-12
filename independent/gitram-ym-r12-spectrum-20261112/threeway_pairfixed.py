#!/usr/bin/env python3
"""Predeclared 3-way test conditional on ALL three pairwise trit tables.

Input: immutable GitRAM cutoff artifact from run 43222707802, r=12 only.
Frozen statistic: squared 2x2x2 alternating triple contrasts, summed within M.
Null: 81 seeded Metropolis chains on 3x3x3 tables. Every accepted move
preserves AB, AC and BC counts IN EACH magnetic-number class exactly.
An MCMC exploration is not an exact uniform-fiber sampler or a proof of mixing.
The conditional null weights count tables by 1 / product(n_abc!), the
conditional multinomial model with arbitrary pairwise log-linear effects.
Everything in leaf reconstruction and null updates is exact rational/integer.
"""
import argparse
from collections import Counter,defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations,product
import random
from pathlib import Path

SEED=b'YM-R12-FROZEN-THREEWAY-PAIRS-20261112-V1'
TRIALS=81
STEPS=30000
LEVELS=(0,1,2)
CUBES=[]
for aa in combinations(LEVELS,2):
    for bb in combinations(LEVELS,2):
        for cc in combinations(LEVELS,2):
            pos=[];neg=[]
            for i,j,k in product((0,1),repeat=3):
                index=9*aa[i]+3*bb[j]+cc[k]
                (pos if (i+j+k)%2==0 else neg).append(index)
            CUBES.append((tuple(pos),tuple(neg)))
assert len(CUBES)==27

def hashfile(p):
    return sha256(Path(p).read_bytes()).hexdigest()

def check_artifact(d):
    checks=(d/'SHA256SUMS').read_text().splitlines()
    for line in checks:
        digest,name=line.split(None,1)
        name=name.lstrip(' *')
        p=d/name
        if not p.is_file() or hashfile(p)!=digest:
            raise ValueError('FILE_INTEGRITY_FAILURE '+name)
    return len(checks)

def load_rows(d,cutoff):
    raw=(d/'rows.txt').read_bytes()
    lines=raw.decode('ascii').splitlines()
    if lines[0]!=f'floorcert-rows-v1 m0={cutoff}':
        raise ValueError('unexpected core cutoff')
    rows=[];end=None
    for line in lines[1:]:
        parts=line.split()
        if not parts:continue
        if parts[0]=='C':
            key,mag,flat=map(int,parts[1:4])
            core=[tuple(map(int,t.split(':'))) for t in parts[4:]]
            rows.append((key,mag,flat,core,[]))
        elif parts[0]=='T':
            tailM=int(parts[1]);hist=tuple(int(x) for x in parts[2].split(','))
            if len(hist)!=9:raise ValueError('histogram size')
            rows[-1][4].append((tailM,hist,tuple(map(int,parts[3:]))))
        elif parts[0]=='END':
            end=tuple(map(int,parts[1:]))
        else:raise ValueError('unexpected row text')
    assert end==(len(rows),sum(len(r[4]) for r in rows),sum(len(t[2]) for r in rows for t in r[4]))
    assert all(flat+sum(count for _,count in core)+len(tail)==72 for _,_,flat,core,tail in rows)
    assert [r[0] for r in rows]==sorted({r[0] for r in rows})
    return rows,hashfile(d/'rows.txt')

def certificate(d,rows,rowhash,cutoff):
    certs=sorted(d.glob(f'cert_m{cutoff}_r12_1_f*.txt'))
    assert len(certs)==3
    result=[]
    for p in certs:
        lines=p.read_text().splitlines()
        header=lines[0]
        if not header.startswith('# floorcert certificate: '):raise ValueError('wrong certificate')
        fields=dict(x.split('=',1) for x in header.split() if '=' in x)
        assert fields['rowhash']==rowhash and int(fields['m0'])==cutoff
        rn,rd=map(int,fields['r'].split('/'))
        assert rn==12*rd
        tn,td=map(int,fields['t'].split('/'))
        assert td>0
        f=tuple(map(int,fields['f'].split(',')))
        assert f and all(v>0 for v in f)
        vals={}
        for line in lines[1:]:
            if not line.strip() or line.startswith('#'):continue
            k,m,v=map(int,line.split())
            assert k not in vals and v>0
            vals[k]=(m,v)
        assert len(vals)==len(rows)
        assert all(vals[r[0]][0]==r[1] for r in rows)
        result.append((p,fields,tn,td,f,vals))
    return result

def get_residuals(rows,cutoff,tn,td,f,vals):
    def f_at(m):
        assert m>cutoff
        return f[min(m-cutoff,len(f))-1]
    scores=[]
    for key,mag,flat,core,tail in rows:
        vi=vals[key][1]
        numerator=((72+12*mag)*td-tn)*vi
        numerator-=td*sum(mult*vals[k][1] for k,mult in core)
        exact=Fraction(numerator,td)
        for m,hist,back in tail:
            fk=f_at(m)
            sf=sum(h*f_at(m+offset-4) for offset,h in enumerate(hist) if h)
            den=((72+12*m)*td-tn)*fk-td*sf
            assert den>0
            sk=sum(vals[k][1] for k in back)
            if sk:exact-=Fraction(td*fk*sk,den)
        scores.append(exact/vi)
    return scores

def terciles(scores,keys,cert_hash):
    n=len(scores)
    assert n>3
    order=sorted(range(n),key=lambda i:(scores[i],sha256(SEED+cert_hash.encode()+str(keys[i]).encode()).digest()))
    labels=[None]*n
    for rank,i in enumerate(order):
        labels[i]=min(2,(3*rank)//n)
    # Count value ties that cross the tercile boundaries, a possible rank-tie artifact
    boundaries=sum(scores[order[i-1]]==scores[order[i]] for i in (n//3,(2*n)//3) if 0<i<n)
    ties=n-len(set(scores))
    biggest=max(Counter(scores).values())
    assert Counter(labels).most_common() and set(labels)=={0,1,2}
    return labels,ties,biggest,boundaries

def idx(a,b,c):return a*9+b*3+c

def histograms(labels,rows):
    tables=defaultdict(lambda:[0]*27)
    for i,row in enumerate(rows):
        tables[row[1]][idx(labels[0][i],labels[1][i],labels[2][i])]+=1
    return dict(sorted(tables.items()))

def pair_margins(t):
    ab=[0]*9;ac=[0]*9;bc=[0]*9
    for a,b,c in product(LEVELS,repeat=3):
        n=t[idx(a,b,c)]
        ab[a*3+b]+=n;ac[a*3+c]+=n;bc[b*3+c]+=n
    return (tuple(ab),tuple(ac),tuple(bc))

def stats(tables):
    contrast=0;equal=0;closure=0
    for t in tables.values():
        equal+=sum(t[idx(a,a,a)] for a in LEVELS)
        closure+=sum(t[idx(a,b,c)] for a,b,c in product(LEVELS,repeat=3) if (a+b+c)%3==0)
        for pos,neg in CUBES:
            d=sum(t[x] for x in pos)-sum(t[x] for x in neg)
            contrast+=d*d
    return contrast,equal,closure

def inequality_bounds(tables):
    # Exact pairwise-only bounds on 3-way all-equal, inclusive
    lo=hi=0
    for t in tables.values():
        n=sum(t)
        ab,ac,bc=pair_margins(t)
        eqab=sum(ab[3*a+a] for a in LEVELS)
        eqac=sum(ac[3*a+a] for a in LEVELS)
        eqbc=sum(bc[3*a+a] for a in LEVELS)
        lo+=max(0,eqab+eqac-n,eqab+eqbc-n,eqac+eqbc-n)
        hi+=min(eqab,eqac,eqbc)
    return lo,hi

def mobility(t):
    feasible=0
    for pos,neg in CUBES:
        if all(t[x]>0 for x in neg):feasible+=1
        if all(t[x]>0 for x in pos):feasible+=1
    return feasible

def sample(original,seed):
    rng=random.Random(int.from_bytes(sha256(SEED+str(seed).encode()).digest()[:16],'big'))
    ts={m:list(t) for m,t in original.items()}
    active=[m for m,t in ts.items() if mobility(t)>0]
    accept=possible=0
    for _ in range(STEPS):
        if not active:break
        m=active[rng.randrange(len(active))]
        plus,minus=CUBES[rng.randrange(27)]
        if rng.randrange(2):plus,minus=minus,plus
        t=ts[m]
        if not all(t[i]>0 for i in minus):continue
        possible+=1
        numer=1;denom=1
        for i in minus:numer*=t[i]
        for i in plus:denom*=t[i]+1
        if rng.randrange(denom)<numer:
            for i in minus:t[i]-=1
            for i in plus:t[i]+=1
            accept+=1
    # Pairwise tables must be exactly unchanged; this is the central integrity gate
    for m,t in ts.items():
        assert pair_margins(t)==pair_margins(original[m]),'pairwise preservation FAILED'
    return ts,possible,accept,len(active)

def report(d,cutoff):
    checks=check_artifact(d)
    rows,rowhash=load_rows(d,cutoff)
    certs=certificate(d,rows,rowhash,cutoff)
    keys=[r[0] for r in rows]
    labels=[];tritrows=[]
    for p,fields,tn,td,f,vals in certs:
        score=get_residuals(rows,cutoff,tn,td,f,vals)
        tri,ties,biggest,boundary=terciles(score,keys,hashfile(p))
        labels.append(tri)
        tritrows.append(f'TRIT|f={fields["f"]}|cert_sha256={hashfile(p)}|distinct_relative_residual={len(rows)-ties}|tied_entries={ties}|largest_tie={biggest}|cross_boundary_ties={boundary}|json=0')
    tables=histograms(labels,rows)
    obs=stats(tables)
    low,high=inequality_bounds(tables)
    movable={m:mobility(t) for m,t in tables.items()}
    results=[];controls=[];possible=accepted=0;active_counts=[]
    seen=set()
    for rep in range(TRIALS):
        x,p,a,k=sample(tables,rep+7000+cutoff*1000)
        controls.append(stats(x))
        possible+=p;accepted+=a;active_counts.append(k)
        seen.add(tuple((m,tuple(t)) for m,t in sorted(x.items())))
    lows=[min(c[i] for c in controls) for i in range(3)]
    highs=[max(c[i] for c in controls) for i in range(3)]
    counts=[sum(c[i]>=obs[i] for c in controls) for i in range(3)]
    line=[]
    line.append(f'CASE|m0={cutoff}|r=12|classes={len(rows)}|verified_artifact_files={checks}|rowhash={rowhash}|null=pairwise_fixed_within_M|stat_primary=alternating_cube_squared|json=0')
    line+=tritrows
    for m,t in tables.items():
        ab,ac,bc=pair_margins(t)
        eq=(sum(ab[4*a] for a in LEVELS),sum(ac[4*a] for a in LEVELS),sum(bc[4*a] for a in LEVELS))
        line.append(f'CLASS|M={m}|rows={sum(t)}|exact_AB_AC_BC_agree={eq[0]},{eq[1]},{eq[2]}|available_cube_moves={movable[m]}|json=0')
    line.append(f'PAIRWISE_BOUND|all_equal_min={low}|observed={obs[1]}|all_equal_max={high}|explanation=exact_pairwise_inclusion_exclusion|json=0')
    line.append(f'OBS|triple_contrast_sq={obs[0]}|all_equal={obs[1]}|mod3_closure={obs[2]}|json=0')
    for j,k in enumerate(('triple_contrast_sq','all_equal','mod3_closure')):
        line.append(f'CONTROL|metric={k}|samples={TRIALS}|min={lows[j]}|max={highs[j]}|at_least_observed={counts[j]}|empirical_p_ge=({counts[j]}+1)/({TRIALS}+1)|json=0')
    line.append(f'POWER|pairwise_preservation=PASS|distinct_triple_tables={len(seen)}|accepted_moves={accepted}|valid_moves_proposed={possible}|total_proposals={TRIALS*STEPS}|active_strata={max(active_counts)}|mcmc_mixing=UNPROVED|json=0')
    inconclusive=(accepted<TRIALS or len(seen)<10 or sum(t[0] for t in controls)==0)
    verdict='INCONCLUSIVE_LOW_MOBILITY' if inconclusive else ('CANDIDATE_3WAY' if counts[0]<=3 else 'NO_CONDITIONAL_EXCESS_DETECTED')
    if any('cross_boundary_ties=1' in x or 'cross_boundary_ties=2' in x for x in tritrows):
        verdict='TIE_BOUNDARY_SENSITIVE_'+verdict
    line.append(f'RESULT|primary={verdict}|pvalue_conditional_only_if_mixed=1|not_physical_hidden_variable=1|json=0')
    line.append(f'GITRAM_SHARD_PASS|m0={cutoff}|pairwise_preserved=1|n={len(rows)}|json=0')
    out=d/'THREEWAY-PAIRFIXED.hbp'
    out.write_text('\n'.join(line)+'\n')
    (d/'THREEWAY-PAIRFIXED.hbp.sha256').write_text(f'{hashfile(out)}  THREEWAY-PAIRFIXED.hbp\n')
    print('\n'.join(line))

if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('artifact_dir',type=Path)
    a.add_argument('cutoff',type=int,choices=(7,8,9))
    args=a.parse_args()
    report(args.artifact_dir,args.cutoff)
