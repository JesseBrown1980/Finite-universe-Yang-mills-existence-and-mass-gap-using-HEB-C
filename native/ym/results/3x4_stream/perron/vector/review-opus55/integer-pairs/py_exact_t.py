# Integer copy of native/ym/results/3x4_stream/perron/vector/review-opus55/py_exact_t.py, written by native/scripts/make_integer_pairs.py: 0 divisions moved to qdiv and 1 text pairs. The original stays as evidence.
# Exact table minimum from my own constraint derivation, on a given vector. No code from the author.
# usage: py_exact_t.py LX LY R_NUM R_DEN GFILE [CLAIM_MICRO] [--sabotage=NAME]
# Python integers and exact integer pairs only, json=0. Exit 1 when CLAIM_MICRO differs.
import sys
from math import isqrt
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", "..", "..", "scripts"))
from intpair import IntPair as Fr
args=[x for x in sys.argv[1:] if not x.startswith('--')]
opts=[x for x in sys.argv[1:] if x.startswith('--')]
LX,LY,RN,RD=int(args[0]),int(args[1]),int(args[2]),int(args[3])
GF=args[4]
CLAIM=int(args[5]) if len(args)>5 else None
sab=[o.split('=')[1] for o in opts if o.startswith('--sabotage=')]
P=LX*LY; NL=2*P
g={}
for line in open(GF,encoding='utf-8'):
    parts=line.strip().split('|')
    if parts[0]!='G': continue
    d=dict(p.split('=',1) for p in parts[1:] if '=' in p)
    g[(int(d['a']),int(d['b']))]=int(d['g'])
lumps=[(a,b) for a in range(0,P+1,2) for b in range(0,P-a+1)]
missing=[l for l in lumps if l not in g]
extra=[l for l in g if l not in lumps]
nonpos=[l for l in lumps if l in g and g[l]<=0]
print("VECTOR|file=%s|rows=%d|lumps=%d|missing=%d|extra=%d|nonpositive=%d|json=0"%(GF.split('/')[-1],len(g),len(lumps),len(missing),len(extra),len(nonpos)))
assert not missing and not nonpos
gv=dict(g); gv[(0,0)]=0   # d=0 on flats: Dirichlet
if 'nonzero_flat' in sab:
    gv[(0,0)]=g[(2,0)]*100
if 'dent' in sab:
    gv[(4,4)]=gv[(4,4)]//1000
def c2s(n):  # ceil(2 sqrt n)
    return 0 if n==0 else isqrt(4*n-1)+1
def adjmax(s):
    if s==0: return 0
    if s==P: return 2*s
    return 2*s-min(c2s(s),min(LX,LY),c2s(P-s))
if 'planar_adj' in sab:
    def adjmax(s):
        return 2*s-c2s(s)
MOVES={'ee':[(2,0,3)],'eT':[(0,0,1),(0,1,2)],'eC':[(2,-1,3)],'TTs':[(-2,0,1),(-2,2,2)],'TTd':[(-2,1,2),(-2,2,1)],'TC':[(0,-1,1),(0,0,2)],'CC':[(2,-2,3)]}
if 'swap_rule' in sab:
    MOVES['TTs']=[(-2,0,2),(-2,2,1)]
def weight(a,b,pat):
    base=gv[(a,b)]
    tot=0
    for da,db,c in MOVES[pat]:
        t=(a+da,b+db)
        if t not in gv:
            return None
        tot+=c*(base-gv[t])
    return tot
best=None; bestrows=[]; points=0; per={}
rn,rd=RN,RD
for (a,b) in lumps:
    if (a,b)==(0,0): continue
    M=2*a+3*b
    if 'wrong_M' in sab:
        M=2*a+2*b
    base=gv[(a,b)]
    W={p:weight(a,b,p) for p in MOVES}
    A,B,I=adjmax(a),adjmax(b),adjmax(a+b)
    lumpmin=None
    for tt in range(0,min(A,2*a)+1):
      # split of tt into same and diff: every split is a point
      for tts in range(0,tt+1):
        ttd=tt-tts
        rem=4*a-2*tt
        for tc in range(0,min(rem,4*b)+1):
            et=rem-tc
            ccmax=min(B,(4*b-tc)//2,I-tt-tc)
            for cc in range(0,ccmax+1):
                ec=4*b-tc-2*cc
                ee=NL-et-ec-tt-tc-cc
                if ee<0: continue
                points+=1
                n={'ee':ee,'eT':et,'eC':ec,'TTs':tts,'TTd':ttd,'TC':tc,'CC':cc}
                s=0
                for p,c in n.items():
                    if c:
                        w=W[p]
                        if w is None:
                            raise SystemExit("MOVE_LEAVES_LUMPS|a=%d|b=%d|p=%s|json=0"%(a,b,p))
                        s+=c*w
                # R = r M + s/base
                num=(RN*M*base+RD*s)
                den=RD*base
                if lumpmin is None or num*lumpmin[1]<lumpmin[0]*den:
                    lumpmin=(num,den,dict(n))
    if lumpmin is None:
        continue
    per[(a,b)]=lumpmin
    if best is None or lumpmin[0]*best[1]<best[0]*lumpmin[1]:
        best=(lumpmin[0],lumpmin[1],(a,b),lumpmin[2])
tex=Fr(best[0],best[1])
fl=(tex*1000000).__floor__()
print("TABLE_MIN|Lx=%d|Ly=%d|r=%d/%d|points=%d|lumps_with_points=%d|t_micro=%d|at=%s|n=%s|json=0"%(LX,LY,RN,RD,points,len(per),fl,best[2],best[3]))
print("GAP|flat_bound=%d|gap_micro=%d|json=0"%(3*NL,fl-3*NL*1000000))
tight=sorted(((Fr(v[0],v[1]),k) for k,v in per.items()))[:12]
print("TIGHTEST_LUMPS|"+";".join("%s:%d"%(k,(x*1000000).__floor__()) for x,k in tight)+"|json=0")
for k in sorted(per):
    v=per[k]
    print("LUMPMIN|a=%d|b=%d|micro=%d|n=%s|json=0"%(k[0],k[1],(Fr(v[0],v[1])*1000000).__floor__(),[v[2][p] for p in ('ee','eT','eC','TTs','TTd','TC','CC')]))
if CLAIM is not None:
    same = fl==CLAIM
    print("CLAIM|given=%d|mine=%d|same=%d|exact_ge_given=%d|verdict=%s|json=0"%(CLAIM,fl,1 if same else 0,1 if tex>=Fr(CLAIM,1000000) else 0,'PASS' if same else 'FAIL'))
    sys.exit(0 if same else 1)
