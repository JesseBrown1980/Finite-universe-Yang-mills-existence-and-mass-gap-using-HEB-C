#!/usr/bin/env python3
"""Exact paired reverse-vs-forward r12 Schur certificate ranking.

Assumes source hash-verified 3x4 S3 rows and original y140 leaves/certs,
and independently verified new reverse-GS certificates.
All calculations exact int and IntegerRatio; independent of float V20/V21.
The comparison-matrix parameter t may change under reversed outer solve
and is therefore recorded as a potential nuisance, not silently held fixed.
"""
from pathlib import Path
import sys
from independent.seat_integer_ratio import IntegerRatio as Rat
from independent.gpt6_gs_sweep_order_20261112 import (
    chk, rows_read, cert_read, matrix, leaves_read, spear, h, f_at, DT, R, WORDS
)

def schur_slack(rows,m0,word,t,vals):
    slacks={}
    for key,mag,flat,core,tails in rows:
        vi=vals[key][1]
        lhs=((72+R*mag)*DT-t)*vi
        lhs-=DT*sum(c*vals[j][1] for j,c in core)
        rhs=0
        for m,hist,back in tails:
            fk=f_at(word,m,m0)
            same=sum(cnt*f_at(word,m+k-4,m0) for k,cnt in enumerate(hist) if cnt)
            den=((72+R*m)*DT-t)*fk-DT*same
            assert den>0
            source=sum(vals[j][1] for j in back)
            n=source*DT*DT*fk
            rhs+=(n+den-1)//den
        slack=lhs-rhs
        assert slack>=0, ("negative reverse certificate slack",key,slack)
        slacks[key]=slack
    return slacks

def calculate(folder,m0,leafdir,revdir):
    chk(folder)
    rows,rhash=rows_read(folder,m0)
    assert len(rows)=={7:682,8:2748,9:2880}[m0]
    allgood=0;favors=0
    for name in WORDS:
        stem=name.replace(",","-")
        p=leafdir.parent.joinpath("certificates","cert_m%d_r12_1_f%s.txt"%(m0,stem))
        rp=revdir.joinpath("cert_m%d_r12_1_f%s.txt"%(m0,stem))
        assert p.is_file() and rp.is_file()
        ow,ot,ov=cert_read(p,m0,rhash,rows)
        nw,nt,nv=cert_read(rp,m0,rhash,rows)
        assert ow==nw
        oldleaf=leaves_read(leafdir.joinpath("S_cert_m%d_r12_1_f%s.leaf.hbp"%(m0,stem)),rows,ov)
        oldq=[Rat(oldleaf[x[0]][2],oldleaf[x[0]][1]) for x in rows]
        _,_,_,ou,ob=matrix(rows,m0,ow,ot,ov)
        os1=spear(oldq,ou);os2=spear(oldq,ob)
        nq=schur_slack(rows,m0,nw,nt,nv)
        newq=[Rat(nq[x[0]],nv[x[0]][1]) for x in rows]
        _,_,_,nu,nb=matrix(rows,m0,nw,nt,nv)
        ns1=spear(newq,nu);ns2=spear(newq,nb)
        stronger=ns2>ns1
        favors+=int(stronger)
        allgood+=1
        print("REVERSE_WRITER|m0=%d|f=%s|n=%d|orig_t=%d/10000|reverse_t=%d/10000|orig_rho_forward_milli=%d|orig_rho_backward_milli=%d|reversed_rho_forward_milli=%d|reversed_rho_backward_milli=%d|reverse_favors_backward=%d|t_changed=%d|orig_certificate_sha256=%s|reverse_certificate_sha256=%s|json=0"%(
            m0,name,len(rows),ot,nt,os1,os2,ns1,ns2,int(stronger),int(ot!=nt),h(p),h(rp)))
    assert allgood==3
    print("REVERSE_WRITER_CUTOFF_PASS|m0=%d|words=3|backward_favored=%d|certificates_checked=3|r9=HOLD|json=0"%(m0,favors))

if __name__=="__main__":
    if len(sys.argv)!=5:raise SystemExit("use: python3 -m independent.gpt6_reverse_writer_eval_20261112 PINNED_ROWS M0 ORIGINAL_Y140_LEAVES NEW_REVERSE_CERTS")
    calculate(Path(sys.argv[1]),int(sys.argv[2]),Path(sys.argv[3]),Path(sys.argv[4]))
