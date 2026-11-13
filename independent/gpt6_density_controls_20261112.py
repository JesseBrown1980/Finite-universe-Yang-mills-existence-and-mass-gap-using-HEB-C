#!/usr/bin/env python3
"""Independent integer-only 19,683-room density-controls auditor.

"reported": check nine user-reported spread/range cells, exact joint-rank
benchmark and paired REAL differences. No raw controls were published.
"strict FILE": require 6 cells (frozen/global-hash x 729/2187/6561),
27 controls per cell, 162 per-control histogram fingerprints, 6,561
function trajectory hashes in both modes at paired ticks. Identical
per-function digit-count digests are only producer claims until the raw
digit sequences are independently supplied. Exact paired null differences
are evaluated using each control's matching index. No inference of
quantum behavior from this deterministic room simulation.
"selftest": mutated histograms and malformed cells must fail closed.
No floating point, JSON or external libraries. r=9 is never invoked.
"""
from collections import Counter
from hashlib import sha256
from math import gcd
from pathlib import Path
import sys

DENSITIES=(729,2187,6561)
MODES=("frozen","global-hash")
REPORTED={
("frozen",729):(499,424,547),
("frozen",2187):(471,465,633),
("frozen",6561):(446,480,597),
("respond",729):(598,555,661),
("respond",2187):(582,518,591),
("respond",6561):(514,458,530),
("global-hash",729):(602,567,604),
("global-hash",2187):(578,499,553),
("global-hash",6561):(446,457,492)
}

def outside(x,lo,hi):
    assert lo<=hi
    return x<lo or x>hi

def reduced(n,d):
    assert d>0 and n>=0
    z=gcd(n,d)
    return n//z,d//z

def rank_benchmark(m):
    # Under exchangeability and independent cells only: p=2/(m+1).
    assert m>=2
    n=m+1
    a=3*4*(n-2)+8 # exactly >=2 of 3 out of m-controls range
    den=n*n*n
    return reduced(a,den),reduced(a*(n-2)*(n-2)*(n-2),den*n*n*n)

def audit_reported():
    flags={}
    print("CONTRACT|dataset=USER_REPORTED_9_CELL_SUMMARIES|raw_density_runs=NOT_AVAILABLE|source=conversation|json=0")
    for m in ("frozen","respond","global-hash"):
        for d in DENSITIES:
            x,lo,hi=REPORTED[(m,d)]
            mark="OUTSIDE" if outside(x,lo,hi) else "INSIDE"
            flags[(m,d)]=mark
            print("REPORTED_CELL|mode=%s|functions=%d|real=%d|control_min=%d|control_max=%d|result=%s|json=0"%(m,d,x,lo,hi,mark))
    assert sum(x=="OUTSIDE" for x in flags.values())==3
    assert sum(flags[("global-hash",d)]=="OUTSIDE" for d in DENSITIES)==2
    assert sum(flags[("frozen",d)]=="OUTSIDE" for d in DENSITIES)==1
    for d in DENSITIES:
        f=REPORTED[("frozen",d)][0];h=REPORTED[("global-hash",d)][0]
        local=REPORTED[("respond",d)][0]
        print("MATCHED_REAL|functions=%d|global_minus_frozen=%d|global_minus_local=%d|paired_controls=UNAVAILABLE|json=0"%(d,h-f,h-local))
        fmin=REPORTED[("frozen",d)][1]
        fmax=REPORTED[("frozen",d)][2]
        hmin=REPORTED[("global-hash",d)][1]
        hmax=REPORTED[("global-hash",d)][2]
        dmin=hmin-fmax
        dmax=hmax-fmin
        forced=outside(h-f,dmin,dmax)
        print("MATCHED_ENVELOPE|functions=%d|real_delta=%d|control_delta_lower_bound=%d|control_delta_upper_bound=%d|forced_outside_for_every_pairing=%d|json=0"%(d,h-f,dmin,dmax,int(forced)))
        assert (forced if d==2187 else not forced)

    for m in (9,27):
        event,joint=rank_benchmark(m)
        print("EXCHANGEABLE_INDEPENDENT_BENCHMARK|controls=%d|global_2of3_n=%d|global_2of3_d=%d|and_frozen_0of3_n=%d|and_frozen_0of3_d=%d|NOT_an_empirical_pvalue=1|json=0"%(m,*event,*joint))
    print("LIMIT|same_spread_not_same_trajectory=1|27_shuffle_input_not_in_repository=1|quantum_and_field_not_established=1|json=0")
    print("DENSITY_REPORTED_AUDIT_PASS|cells=9|outliers=3|json=0")

def shahex(x):
    return len(x)==64 and all(c in "0123456789abcdef" for c in x)

def parse(line):
    items=line.strip().split("|")
    assert items[0] in ("CELL","HIST","TRACE")
    f=dict(x.split("=",1) for x in items[1:])
    assert f.get("json")=="0"
    return items[0],f

def check_digit_permutation(before,after):
    """Independent source-level control: compare each function's raw digit counts."""
    assert len(before)==len(after)
    for a,b in zip(before,after):
        assert len(a)==len(b) and Counter(a)==Counter(b),"SHUFFLE_INVALID"
    return True

def strict(path):
    data=Path(path).read_bytes()
    cells={};hist={};traces={}
    for line in data.decode("ascii").splitlines():
        if not line or line.startswith("#"):continue
        kind,f=parse(line)
        m=f["mode"];d=int(f["density"])
        assert m in MODES and d in DENSITIES
        key=(m,d)
        if kind=="CELL":
            assert key not in cells
            real=int(f["real"])
            ctrl=tuple(int(x) for x in f["controls"].split(","))
            assert real>=0 and len(ctrl)==27 and all(c>=0 for c in ctrl)
            cells[key]=(real,ctrl)
        elif kind=="HIST":
            j=int(f["control"])
            assert 0<=j<27 and int(f["functions"])==d
            a,b=f["original_sha256"],f["shuffled_sha256"]
            assert shahex(a) and shahex(b) and a==b,"DIGIT_PRESERVATION_DIGEST_MISMATCH"
            assert (key,j) not in hist
            hist[(key,j)]=a
        else:
            assert d==6561
            tick=int(f["tick"]);digest=f["state_sha256"]
            assert tick>=0 and shahex(digest) and (m,tick) not in traces
            traces[(m,tick)]=digest
    assert set(cells)=={(m,d) for m in MODES for d in DENSITIES},"SIX_CELLS_REQUIRED"
    assert set(hist)=={((m,d),j) for m in MODES for d in DENSITIES for j in range(27)},"162_SHUFFLE_RECEIPTS_REQUIRED"
    ta={t for m,t in traces if m=="frozen"}
    tb={t for m,t in traces if m=="global-hash"}
    assert ta and ta==tb and 0 in ta,"TRAJECTORY_TICK_PAIRS_REQUIRED"
    print("SOURCE|sha256=%s|cells=6|hist_receipts=162|json=0"%sha256(data).hexdigest())
    frozen_hits=global_hits=paired_hits=0
    for d in DENSITIES:
        f,fc=cells[("frozen",d)]
        h,hc=cells[("global-hash",d)]
        fo=outside(f,min(fc),max(fc))
        ho=outside(h,min(hc),max(hc))
        delta=h-f
        pair=tuple(hc[j]-fc[j] for j in range(27))
        po=outside(delta,min(pair),max(pair))
        frozen_hits+=int(fo);global_hits+=int(ho);paired_hits+=int(po)
        print("DENSITY_MATCH|functions=%d|frozen_outside=%d|global_outside=%d|real_feedback_delta=%d|matched_control_min=%d|matched_control_max=%d|matched_delta_outside=%d|json=0"%(d,int(fo),int(ho),delta,min(pair),max(pair),int(po)))
    first=next((t for t in sorted(ta) if traces[("frozen",t)]!=traces[("global-hash",t)]),None)
    print("TRAJECTORY|functions=6561|paired_ticks=%d|first_state_hash_difference=%s|aggregate_spread_cannot_establish_identity=YES|json=0"%(len(ta),"NONE" if first is None else str(first)))
    pass_sealed=(global_hits>=2 and frozen_hits==0)
    print("SEALED_GATE|global_outside=%d|frozen_outside=%d|pass=%s|feedback_delta_outside=%d|json=0"%(global_hits,frozen_hits,"YES" if pass_sealed else "NO",paired_hits))
    print("LIMIT|histogram_digests_require_raw_digit_audit=1|trajectory_hashes_not_full_trajectories=1|shared_runs_not_independent_cells=1|quantum_claim=NO|json=0")
    print("DENSITY_STRICT_AUDIT_PASS|cells=6|control_receipts=162|json=0")
    return pass_sealed,paired_hits,first

def selftest():
    assert check_digit_permutation(("001122","11100022"),("221100","21010210"))
    try:check_digit_permutation(("012",),("011",))
    except AssertionError:pass
    else:raise AssertionError("mutated digits accepted")
    h1="a"*64;h2="b"*64;lines=[]
    for m in MODES:
        for d in DENSITIES:
            real=700 if m=="global-hash" and d!=729 else 500
            lines.append("CELL|mode=%s|density=%d|real=%d|controls=%s|json=0"%(m,d,real,",".join("500" for _ in range(27))))
            for j in range(27):
                lines.append("HIST|mode=%s|density=%d|control=%d|functions=%d|original_sha256=%s|shuffled_sha256=%s|json=0"%(m,d,j,d,h1,h1))
    for m in MODES:
        for tick in (0,1,2):
            lines.append("TRACE|mode=%s|density=6561|tick=%d|state_sha256=%s|json=0"%(m,tick,h2 if m=="global-hash" and tick>0 else h1))
    payload="\n".join(lines)+"\n"
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as td:
        p=Path(td).joinpath("sample.hbp")
        p.write_text(payload,encoding="ascii")
        yes,num,first=strict(p)
        assert yes and num==2 and first==1
        p.write_text(payload.replace("shuffled_sha256="+h1,"shuffled_sha256="+h2,1),encoding="ascii")
        try:strict(p)
        except AssertionError:pass
        else:raise AssertionError("tampered digit receipt accepted")
    print("DENSITY_AUDITOR_SELFTEST_PASS|mutated_digits=REFUSED|paired_differences=PASS|trajectory_change=PASS|json=0")

if __name__=="__main__":
    if len(sys.argv)==2 and sys.argv[1]=="reported":audit_reported()
    elif len(sys.argv)==2 and sys.argv[1]=="selftest":selftest()
    elif len(sys.argv)==3 and sys.argv[1]=="strict":strict(sys.argv[2])
    else:raise SystemExit("use: reported | selftest | strict DATA.hbp")
