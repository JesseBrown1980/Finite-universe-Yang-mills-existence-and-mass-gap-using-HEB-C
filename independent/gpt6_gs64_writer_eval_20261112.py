#!/usr/bin/env python3
"""Exactly check r12 64-vs-8 inner GS sweep signature and certificate floors.

Reads the immutable y140 forward eight-sweep certificate with matching
published residual leaves, and independently verified new Rust-generated
64-inner-sweep certificate against the same pinned row hash. All ranks
and comparison-matrix coefficients use exact rational/integer arithmetic.
The result tests a post-outcome scientific explanation, not a new physical
field or new r9 statement.
"""
from pathlib import Path
import sys
from independent.seat_integer_ratio import IntegerRatio as Rat
from independent.gpt6_gs_sweep_order_20261112 import (
    chk,rows_read,cert_read,leaves_read,matrix,spear,h
)
from independent.gpt6_reverse_writer_eval_20261112 import schur_slack

def evaluate(rowsdir,m0,leafdir,newdir):
    assert m0 in (7,8,9)
    chk(rowsdir)
    rows,rhash=rows_read(rowsdir,m0)
    name="6-5-4-3"
    orig=leafdir.parent.joinpath("certificates","cert_m%d_r12_1_f%s.txt"%(m0,name))
    latest=newdir.joinpath("cert_m%d_r12_1_f%s.txt"%(m0,name))
    assert orig.is_file() and latest.is_file()
    ow,ot,ov=cert_read(orig,m0,rhash,rows)
    nw,nt,nv=cert_read(latest,m0,rhash,rows)
    assert ow==nw
    original=leaves_read(leafdir.joinpath("S_cert_m%d_r12_1_f%s.leaf.hbp"%(m0,name)),rows,ov)
    oldq=[Rat(original[row[0]][2],original[row[0]][1]) for row in rows]
    _,_,_,of,ob=matrix(rows,m0,ow,ot,ov)
    oldforward=spear(oldq,of);oldbackward=spear(oldq,ob)
    fresh=schur_slack(rows,m0,nw,nt,nv)
    newq=[Rat(fresh[row[0]],nv[row[0]][1]) for row in rows]
    _,_,_,nf,nb=matrix(rows,m0,nw,nt,nv)
    newforward=spear(newq,nf);newbackward=spear(newq,nb)
    assert len(fresh)==len(rows)
    weaken=newforward<oldforward
    print("GS64|m0=%d|f=6,5,4,3|rows=%d|old_floor_n=%d|new_floor_n=%d|floor_den=10000|old_forward_rho_milli=%d|new_forward_rho_milli=%d|old_backward_rho_milli=%d|new_backward_rho_milli=%d|weakened=%d|old_certificate_sha256=%s|new_certificate_sha256=%s|json=0"%(
        m0,len(rows),ot,nt,oldforward,newforward,oldbackward,newbackward,int(weaken),h(orig),h(latest)))
    assert weaken,"64 sweeps did not weaken rank signature; preserve as falsifier"
    print("GS64_EXACT_PASS|m0=%d|word=6,5,4,3|rows=%d|r=12|r9=HOLD|json=0"%(m0,len(rows)))

if __name__=="__main__":
    if len(sys.argv)!=5:
        raise SystemExit("python -B -m independent.gpt6_gs64_writer_eval_20261112 ROWS_DIR CUTOFF LEAVES_DIR NEWCERT_DIR")
    evaluate(Path(sys.argv[1]),int(sys.argv[2]),Path(sys.argv[3]),Path(sys.argv[4]))
