#!/usr/bin/env python3
"""Nine-column Pascal geometry change under independently certified reversed GS.

Compare immutable original y140 r12 certificate leaves to certificates from
a pinned one-loop-only reversed Rust writer on identical canonical 682 rows.
Equal-rank trits use a SEED+canonical-key tie-break, identical across runs,
to avoid mistaking changed cert SHA for changed mathematical residual.
This is descriptive geometry, not a pair-fixed higher-order null.
No floating point, JSON, or r9.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import sys
from independent.seat_integer_ratio import IntegerRatio as Rat
from independent.gpt6_gs_sweep_order_20261112 import (
    chk, rows_read, cert_read, leaves_read, WORDS, h
)
from independent.gpt6_reverse_writer_eval_20261112 import schur_slack

SEED=b"GPT6-YM-R12-GS-SWEEP-PASCAL-KEY-20261112"
M0S=(7,8,9)
ROWS=682

def ranks(values, keys):
    assert len(keys)==ROWS==len(values)
    order=sorted(range(ROWS),key=lambda i:(values[i],
      sha256(SEED+str(keys[i]).encode("ascii")).digest()))
    out=[-1]*ROWS
    for rank, i in enumerate(order):
        out[i]=min(2,3*rank//ROWS)
    assert Counter(out)=={0:228,1:227,2:227} or Counter(out)=={0:228,1:228,2:226}
    return out, ROWS-len(set(values))

def geometry(states):
    assert len(states)==ROWS and len(states[0])==9
    assert all(len(row)==9 and all(v in (0,1,2) for v in row) for row in states)
    counts=Counter(states)
    layer=Counter()
    compositions=set()
    dissenter=Counter()
    for row in states:
        hist=Counter(row)
        layer[len(hist)]+=1
        compositions.add(tuple(hist.get(k,0) for k in range(3)))
        if max(hist.values())==8:
            dissenter[next(i for i,v in enumerate(row) if hist[v]==1)]+=1
    assert sum(layer.values())==ROWS
    return len(counts),len(compositions),layer,dissenter

def pair_equal(before,after):
    count_equal=0
    for a in range(9):
        for b in range(a+1,9):
            old=Counter((row[a],row[b]) for row in before)
            new=Counter((row[a],row[b]) for row in after)
            count_equal+=int(old==new)
    return count_equal

def main(rowsroot, reverse_root, leaves_root, dest):
    source={}
    manifests={}
    for m in M0S:
        folder=rowsroot.joinpath("original","cutoff-%d"%m)
        chk(folder)
        rows,rowhash=rows_read(folder,m)
        manifests[m]=h(folder.joinpath("SHA256SUMS"))
        source[m]=(rows,rowhash)
    shared=set(row[0] for row in source[7][0])
    for m in (8,9):
        shared.intersection_update(row[0] for row in source[m][0])
    keys=sorted(shared)
    assert len(keys)==ROWS and all(x in shared for x in keys)
    old_cols=[];new_cols=[]
    source_records=[]
    for m in M0S:
        rows,rowhash=source[m]
        fnew=reverse_root.joinpath("reverse","cutoff-%d"%m)
        assert fnew.is_dir()
        for word_text in WORDS:
            stem=word_text.replace(",","-")
            p=leaves_root.parent.joinpath("certificates","cert_m%d_r12_1_f%s.txt"%(m,stem))
            rp=fnew.joinpath("cert_m%d_r12_1_f%s.txt"%(m,stem))
            assert p.is_file() and rp.is_file()
            ow,ot,ov=cert_read(p,m,rowhash,rows)
            rw,rt,rv=cert_read(rp,m,rowhash,rows)
            assert ow==rw
            origin=leaves_read(leaves_root.joinpath("S_cert_m%d_r12_1_f%s.leaf.hbp"%(m,stem)),rows,ov)
            reverse=schur_slack(rows,m,rw,rt,rv)
            oldvalues=[Rat(origin[key][2],ov[key][1]) for key in keys]
            newvalues=[Rat(reverse[key],rv[key][1]) for key in keys]
            oldlabels,otie=ranks(oldvalues,keys)
            newlabels,ntie=ranks(newvalues,keys)
            old_cols.append(oldlabels);new_cols.append(newlabels)
            changed=sum(x!=y for x,y in zip(oldlabels,newlabels))
            source_records.append(
                "PASCAL_COLUMN|index=%d|cutoff=%d|word=%s|old_floor_n=%d|reverse_floor_n=%d|floor_den=10000|old_ties=%d|new_ties=%d|changed_rows=%d|source_sha256=%s|reverse_sha256=%s|json=0"%
                (len(old_cols)-1,m,word_text,ot,rt,otie,ntie,changed,h(p),h(rp))
            )
    assert len(old_cols)==len(new_cols)==9
    before=[tuple(col[i] for col in old_cols) for i in range(ROWS)]
    after=[tuple(col[i] for col in new_cols) for i in range(ROWS)]
    old=geometry(before);new=geometry(after)
    changed_rows=sum(a!=b for a,b in zip(before,after))
    changed_trits=sum(sum(a!=b for a,b in zip(x,y)) for x,y in zip(before,after))
    exact_pairs=pair_equal(before,after)
    assert 0<=changed_rows<=ROWS and 0<=changed_trits<=ROWS*9
    assert 0<=exact_pairs<=36
    lines=[
        "PASCAL_COMPARE|schema=GPT6-GS-SWEEP-PASCAL-V1|rows=682|columns=9|r=12|trit_ties=fixed_key_sha256|json=0"
    ]
    for m in M0S:
        lines.append("SOURCE|cutoff=%d|pinned_manifest_sha256=%s|rowhash=%s|json=0"%(m,manifests[m],source[m][1]))
    lines+=source_records
    for name,g in (("original",old),("reversed",new)):
        distinct,compositions,layer,dissent=g
        lines.append("PASCAL_LAYER|direction=%s|corners=%d|edges=%d|interior=%d|distinct_labeled=%d|distinct_compositions=%d|json=0"%
                     (name,layer[1],layer[2],layer[3],distinct,compositions))
        for i,count in sorted(dissent.items()):
            lines.append("PASCAL_DISSENTER|direction=%s|column=%d|rows=%d|json=0"%(name,i,count))
    lines.append("PASCAL_DIFFERENCE|rows_changed=%d|trits_changed=%d|pair_tables_unchanged=%d|pair_tables_total=36|json=0"%
                 (changed_rows,changed_trits,exact_pairs))
    lines.append("LIMIT|geometry_is_not_a_pair_fixed_statistical_test=1|all_reversed_columns_share_same_sweep=1|quantum_and_continuum_field_unproved=1|r9=HOLD|json=0")
    lines.append("PASCAL_GS_ORDER_COMPARISON_PASS|rows=682|columns=9|r=12|r9=HOLD|json=0")
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text("\n".join(lines)+"\n",encoding="ascii")
    dest.with_name(dest.name+".sha256").write_text(
        h(dest)+"  "+dest.name+"\n",encoding="ascii")
    print("\n".join(x for x in lines if x.startswith((
        "PASCAL_LAYER|","PASCAL_DISSENTER|","PASCAL_DIFFERENCE|",
        "PASCAL_GS_ORDER_COMPARISON_PASS|"
    ))))

if __name__=="__main__":
    if len(sys.argv)!=5:
        raise SystemExit("python -B -m independent.gpt6_gs_pascal_order_20261112 ROWSROOT REVERSE_ROOT Y140_LEAFROOT DEST")
    main(*(Path(s) for s in sys.argv[1:]))
