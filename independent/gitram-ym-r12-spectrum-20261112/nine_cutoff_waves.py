#!/usr/bin/env python3
"""Exact replay of 9 Schur-residual trit leaves (3 cutoff x 3 weight words).

Source: previously sealed GitRAM cutoff-7/8/9 r=12 artifacts, run 43222707802.
Align 682 common canonical keys and compute exact (Fraction) local ratios.
Thirds are assigned independently to each leaf on THE COMMON 682 keys.
Forward/backward "waves" are bijective transformations of the frozen
9-trit addresses, not physical Hamiltonian evolution and not new data.
No floats, no live writer, no r=9 launch.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from itertools import combinations
import sys
import threeway_pairfixed as f

SRC_RUN=43222707802
CUTS=(7,8,9)
STEPS=3

def bytehash(b):
    return sha256(b).hexdigest()

def rime3(a,b,c):
    return ((a+b)%3,(b+c)%3,(c+a)%3)

def unrime3(u,v,w):
    a=(2*(u-v+w))%3
    b=(u-a)%3
    c=(v-b)%3
    assert rime3(a,b,c)==(u,v,w)
    return (a,b,c)

def wave(t,phase,reverse=False):
    z=list(t)
    for part in range(3):
        if phase%2==0:
            inds=(3*part,3*part+1,3*part+2)  # within each cutoff
        else:
            inds=(part,part+3,part+6)         # same weight across cutoffs
        old=tuple(z[i] for i in inds)
        new=unrime3(*old) if reverse else rime3(*old)
        for i,a in zip(inds,new):
            z[i]=a
    return tuple(z)

def calc(root,out):
    root=Path(root)
    rows_by_cut={}
    cert_by_cut={}
    trit_by_cut={}
    source_hashes={}
    for cutoff in CUTS:
        d=root/("cutoff-%d"%cutoff)
        assert f.check_artifact(d)==6
        rows,rowhash=f.load_rows(d,cutoff)
        certs=f.certificate(d,rows,rowhash,cutoff)
        assert len(certs)==3
        rows_by_cut[cutoff]=rows
        cert_by_cut[cutoff]=certs
        source_hashes[cutoff]=sha256((d/"SHA256SUMS").read_bytes()).hexdigest()
    common=set(r[0] for r in rows_by_cut[7])
    for cutoff in CUTS[1:]:
        common&=set(r[0] for r in rows_by_cut[cutoff])
    keys=sorted(common)
    assert len(keys)==682,"expected complete m0=7 shared core"
    mags={r[0]:r[1] for r in rows_by_cut[7]}
    assert all({r[0]:r[1] for r in rows_by_cut[c] if r[0] in common}==mags for c in CUTS)
    leaf_labels=[]
    leaf_headers=[]
    for cutoff in CUTS:
        rows=rows_by_cut[cutoff]
        idx={r[0]:i for i,r in enumerate(rows)}
        for cert,fields,tn,td,weights,vals in cert_by_cut[cutoff]:
            scores=f.get_residuals(rows,cutoff,tn,td,weights,vals)
            selected=[scores[idx[key]] for key in keys]
            labels,ties,biggest,boundary=f.terciles(selected,keys,f.hashfile(cert))
            assert boundary==0 or boundary>0
            leaf_labels.append(labels)
            leaf_headers.append((cutoff,fields["f"],f.hashfile(cert),ties,biggest,boundary))
    assert len(leaf_labels)==9
    states=[tuple(leaf_labels[i][j] for i in range(9)) for j in range(len(keys))]
    assert all(len(s)==9 and all(v in (0,1,2) for v in s) for s in states)
    p=Path(out)
    p.parent.mkdir(parents=True,exist_ok=True)
    frozen=p.with_name("NINE-LEAVES-FROZEN.hbp")
    frozen.write_text(
      "NINE_LEAF_FREEZE|schema=YM-R12-3CUTOFF-3WORD|source_run=%d|rows=682|json=0\n"%SRC_RUN+
      "".join("LEAF|key=%d|mag=%d|trits=%s|json=0\n"%(key,mags[key],",".join(map(str,s))) for key,s in zip(keys,states))
    )
    frozen_sha=f.hashfile(frozen)
    nine_equal=sum(len(set(s))==1 for s in states)
    pat=Counter(states)
    patterns=len(pat)
    maxi=max(pat.values())
    pairs={}
    for i,j in combinations(range(9),2):
        pairs[(i,j)]=sum(s[i]==s[j] for s in states)
    same3=[]
    for x in range(3):
        same3.append(sum(s[3*x]==s[3*x+1]==s[3*x+2] for s in states))
    original=states
    forward=[]
    current=states
    for phase in range(STEPS):
        current=[wave(s,phase) for s in current]
        forward.append(current)
        assert len(set(current))==patterns, "bijection changed pattern count"
    for phase in range(STEPS-1,-1,-1):
        current=[wave(s,phase,True) for s in current]
    assert current==original, "reversal failure"
    assert all(unrime3(*rime3(a,b,c))==(a,b,c)
               for a in range(3) for b in range(3) for c in range(3))
    lines=[
      "RUN|schema=YM-R12-NINE-LEAF-FWDREV-V1|source_run=%d|cuts=7,8,9|weight_words_per_cut=3|common_rows=%d|representation_only=1|json=0"%(SRC_RUN,len(keys)),
      "HASH|frozen_leaves_sha256=%s|source_cut7_manifest=%s|source_cut8_manifest=%s|source_cut9_manifest=%s|json=0"%(frozen_sha,source_hashes[7],source_hashes[8],source_hashes[9])
    ]
    for i,(cutoff,word,h,ties,big,boundary) in enumerate(leaf_headers):
        lines.append("LEAF_HEADER|index=%d|cutoff=%d|f=%s|sha256=%s|tied_residual_entries=%d|largest_tie=%d|tercile_cross_boundary_ties=%d|json=0"%(i,cutoff,word,h,ties,big,boundary))
    lines += [
      "OBSERVED|all_nine_equal=%d|distinct_nine_patterns=%d|largest_pattern_count=%d|pair_min=%d|pair_max=%d|three_wave_equal=%d,%d,%d|json=0"%(
        nine_equal,patterns,maxi,min(pairs.values()),max(pairs.values()),*same3),
      "PAIRWISE|number_of_pairs=%d|tie_counts=%s|json=0"%(len(pairs),",".join("%d:%d:%d"%(i,j,pairs[i,j]) for i,j in pairs)),
      "PAIRWISE_BOUND|all_nine_equal_min=0|all_nine_equal_max=%d|method=universal_upper_bound_from_min_pair_agreement|json=0"%min(pairs.values())
    ]
    for phase,st in enumerate(forward):
        lines.append("FORWARD|stage=%d|pattern_count=%d|hash_sha256=%s|json=0"%(phase+1,len(set(st)),bytehash(b"".join(bytes(s) for s in st))))
    lines += [
      "REVERSE|stages=3|rows=%d|all_original_nine_trits_restored=PASS|all_unique_patterns_preserved=PASS|json=0"%len(keys),
      "CONTROLS|original_tercile_crossing_ties=%d|exact_pairs_preserved_by_surrogate=NOT_TESTED|9way_conditional_excess=UNRESOLVED|json=0"%sum(x[-1] for x in leaf_headers),
      "INTERPRETATION|reversible_addressing_verified=1|physical_YM_time_evolution=0|new_physical_hidden_variable=0|continuum_claim=NONE|json=0",
      "GITRAM_SHARD_PASS|replay=nine_leaves|source_run=%d|rows=682|json=0"%SRC_RUN
    ]
    p.write_text("\n".join(lines)+"\n")
    p.with_name(p.name+".sha256").write_text("%s  %s\n"%(f.hashfile(p),p.name))
    print("\n".join(lines))

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: nine_cutoff_waves.py INPUT_ROOT REPORT.hbp")
    calc(sys.argv[1],sys.argv[2])
