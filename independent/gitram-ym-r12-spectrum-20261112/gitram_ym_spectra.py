#!/usr/bin/env python3
"""GitRAM r=12 Schur spectrum diagnostic. Original Rust writer/verifier remain read-only."""
import argparse
import hashlib
import os
from pathlib import Path

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def instrument(src, dest):
    s=Path(src).read_text()
    changes=[
        ("import sys\nimport hashlib\n", "import sys\nimport hashlib\nimport os\n"),
        ("rh = hashlib.sha256()\nnbytes = 0\ndef feed(s):",
         "rh = hashlib.sha256()\nnbytes = 0\n"
         "_out = open(os.environ['GITRAM_ROW_OUT'],'w') if os.environ.get('GITRAM_ROW_OUT') else None\n"
         "if os.environ.get('GITRAM_WEIGHTS_OUT'):\n"
         "    with open(os.environ['GITRAM_WEIGHTS_OUT'],'w') as _w:\n"
         "        for _ci in range(ncls):\n"
         "            _w.write('%d %d\\n' % (cls2cert[_ci],cls_W[_ci]))\n"
         "def feed(s):"),
        ("    rh.update(b)\n    nbytes += len(b)\n",
         "    rh.update(b)\n    nbytes += len(b)\n"
         "    if _out is not None: _out.write(s)\n"),
        ('feed("END %d %d %d\\n" % (ncls, ntail, nback))',
         'feed("END %d %d %d\\n" % (ncls, ntail, nback))\n'
         'if _out is not None: _out.close()')
    ]
    for old,new in changes:
        if s.count(old)!=1:
            raise RuntimeError('pinned verifier instrumentation anchor not unique: '+old[:65])
        s=s.replace(old,new)
    Path(dest).write_text(s)
    print('INSTRUMENT|source_sha256=%s|scratch_sha256=%s|pinned_unchanged=1'%(sha(src),sha(dest)))

def rows_of(path):
    blob=Path(path).read_bytes()
    lines=blob.decode('ascii').splitlines()
    assert lines[0].startswith('floorcert-rows-v1 m0=')
    rows=[]
    end=None
    for line in lines[1:]:
        ss=line.split()
        if not ss: continue
        if ss[0]=='C':
            assert len(ss)>=4
            rows.append({'key':int(ss[1]),'M':int(ss[2]),'nflat':int(ss[3]),
                         'core':[(int(x),int(y)) for part in ss[4:] for x,y in [part.split(':')]],
                         'tail':[]})
        elif ss[0]=='T':
            assert rows
            h=[int(q) for q in ss[2].split(',')]
            assert len(h)==9
            rows[-1]['tail'].append((int(ss[1]),h,[int(k) for k in ss[3:]]))
        elif ss[0]=='END':
            end=tuple(int(x) for x in ss[1:])
        else: raise ValueError('invalid row type '+ss[0])
    assert end and len(rows)==end[0]
    assert sum(len(x['tail']) for x in rows)==end[1]
    assert sum(len(back) for row in rows for _,_,back in row['tail'])==end[2]
    for row in rows:
        assert row['nflat']+sum(v for _,v in row['core'])+len(row['tail'])==72
    assert [r['key'] for r in rows]==sorted({r['key'] for r in rows})
    return rows,hashlib.sha256(blob).hexdigest()

def metadata(cert):
    line=Path(cert).read_text().splitlines()[0]
    assert line.startswith('# floorcert certificate:')
    m=dict(x.split('=',1) for x in line.split() if '=' in x)
    rn,rd=map(int,m['r'].split('/'))
    assert rn==12*rd # NO r=9 invocation
    tn,td=map(int,m['t'].split('/'))
    cn,cd=map(int,m['cap'].split('/'))
    assert td>0 and cd>0
    f=tuple(map(int,m['f'].split(',')))
    assert f and min(f)>0
    return m,tn/td,cn/cd,f

def analyze(d,m0,out):
    import numpy as np
    from scipy.sparse import coo_matrix,diags
    from scipy.sparse.linalg import eigsh
    d=Path(d)
    rows,rowhash=rows_of(d/'rows.txt')
    n=len(rows)
    assert n>7
    keys=[x['key'] for x in rows]
    ix={key:i for i,key in enumerate(keys)}
    weights=dict(tuple(map(int,line.split())) for line in (d/'weights.txt').read_text().splitlines())
    assert len(weights)==n and all(weights[k]>0 for k in ix)
    w=np.sqrt(np.array([weights[k] for k in keys],dtype=float))
    certs=sorted(d.glob('cert_m*_r12_1_f*.txt'))
    assert len(certs)==3, 'require three certified weight words'
    info=[]
    for cert in certs:
        meta,t,cap,f=metadata(cert)
        assert int(meta['m0'])==m0 and meta['rowhash']==rowhash
        vals=[line.split() for line in cert.read_text().splitlines()[1:] if line.strip() and not line.startswith('#')]
        assert len(vals)==n
        assert all(int(line[0])==row['key'] and int(line[1])==row['M'] and int(line[2])>0 for line,row in zip(vals,rows))
        info.append((cert,meta,t,cap,f))
    tc=min(a[2] for a in info)-0.1
    result=['SPECTRAL|schema=GITRAM-SCHUR-R12-DIAGNOSTIC-V1|coupling=12|m0=%d|classes=%d|rowhash=%s|numeric_only=1|json=0'%(m0,n,rowhash)]
    def build(t,f):
        rr=[];cc=[];vv=[]
        def fv(m):
            j=min(m-m0,len(f))-1
            if j<0:raise ValueError('bad tail f index')
            return f[j]
        for i,row in enumerate(rows):
            rr.append(i);cc.append(i);vv.append(72+12*row['M']-t)
            for j,c in row['core']:
                rr.append(i);cc.append(ix[j]);vv.append(-float(c))
            for m,hist,back in row['tail']:
                fm=fv(m)
                sf=sum(hist[z]*fv(m+z-4) for z in range(9) if hist[z])
                delta=72+12*m-sf/fm
                if not delta>t:raise ValueError('nonpositive Schur denominator')
                for j in back:
                    rr.append(i);cc.append(ix[j]);vv.append(-1.0/(delta-t))
        mat=coo_matrix((vv,(rr,cc)),shape=(n,n)).tocsr()
        sm=diags(w)@mat@diags(1/w)
        asym=sm-sm.T
        skew=float(np.max(np.abs(asym.data))) if asym.nnz else 0.
        if skew>2e-8:raise ValueError('weighted self-adjointness failed: %g'%skew)
        return sm,skew
    def eig(t,f):
        mat,skew=build(t,f)
        lam,vec=eigsh(mat,k=6,which='SA',tol=2e-10,maxiter=20000,
                      v0=np.arange(1,n+1,dtype=float)/n)
        order=np.argsort(lam)
        lam=lam[order];vec=vec[:,order]
        residual=np.linalg.norm(mat@vec-vec*lam,axis=0)
        if np.max(residual)>5e-5:raise ValueError('numeric residual too large')
        return lam,residual,skew
    for cert,meta,t,cap,f in info:
        tag=meta['f'].replace(',','-')
        lam,resid,skew=eig(t,f)
        result.append('CERT|f=%s|sha256=%s|gamma=%s|cap=%s|sym_error=%.5e|json=0'%(tag,sha(cert),meta['t'],meta['cap'],skew))
        for k,(v,e) in enumerate(zip(lam,resid)):
            result.append('EIG|f=%s|t=gamma|rank=%d|value=%.12f|residual=%.3e|json=0'%(tag,k,v,e))
        l2,e2,_=eig(tc,f)
        for k,(v,e) in enumerate(zip(l2,e2)):
            result.append('EIG|f=%s|t=common|common_t=%.7f|rank=%d|value=%.12f|residual=%.3e|json=0'%(tag,tc,k,v,e))
        hi=min(t+8,cap-0.005)
        if hi<=t:
            result.append('CROSS|f=%s|status=UNBRACKETED|reason=tail_cap|json=0'%tag)
            continue
        lh,_,_=eig(hi,f)
        for k in range(4):
            if lam[k]<-5e-5 or lh[k]>0:
                result.append('CROSS|f=%s|rank=%d|status=UNBRACKETED|left=%.7f|right=%.7f|json=0'%(tag,k,lam[k],lh[k]))
                continue
            low=t;high=hi
            for _ in range(12):
                mid=(low+high)/2
                lm,_,_=eig(mid,f)
                if lm[k]>0:low=mid
                else:high=mid
            result.append('CROSS|f=%s|rank=%d|status=BRACKETED|tlo=%.10f|thi=%.10f|delta_lo=%.10f|delta_hi=%.10f|json=0'%(tag,k,low,high,low-t,high-t))
    result.append('GITRAM_SHARD_PASS|m0=%d|certs=3|rows=%d|json=0'%(m0,n))
    o=Path(out);o.write_text('\n'.join(result)+'\n')
    o.with_suffix(o.suffix+'.sha256').write_text('%s  %s\n'%(sha(o),o.name))
    print('\n'.join(result))

def main():
    p=argparse.ArgumentParser()
    sp=p.add_subparsers(dest='cmd',required=True)
    i=sp.add_parser('instrument');i.add_argument('source');i.add_argument('target')
    a=sp.add_parser('analyze');a.add_argument('folder');a.add_argument('cutoff',type=int);a.add_argument('output')
    args=p.parse_args()
    if args.cmd=='instrument':instrument(args.source,args.target)
    else:analyze(args.folder,args.cutoff,args.output)
if __name__=='__main__':main()
