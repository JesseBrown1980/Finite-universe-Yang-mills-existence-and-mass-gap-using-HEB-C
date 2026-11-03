# Cross-check of two of my own code paths: census LUMP rows against ritz MODEL_M rows, per M. usage: py_cross_m.py CENSUS_OUT RITZ_OUT. json=0.
import sys
bym={}
for line in open(sys.argv[1],encoding='utf-8'):
    if line.startswith('LUMP|'):
        d=dict(x.split('=',1) for x in line.strip().split('|')[1:] if '=' in x)
        m=2*int(d['a'])+3*int(d['b'])
        bym[m]=bym.get(m,0)+int(d['configs'])
rit={}
for line in open(sys.argv[2],encoding='utf-8'):
    if line.startswith('MODEL_M|'):
        d=dict(x.split('=',1) for x in line.strip().split('|')[1:] if '=' in x)
        rit[int(d['M'])]=int(d['gauge_fixed_configs'])
keys=sorted(set(bym)|set(rit))
bad=[k for k in keys if k!=0 and bym.get(k,0)!=rit.get(k,0)]
print("CROSS_M|Ms=%d|bad=%s|flat_configs=%d|json=0"%(len(keys),bad,bym.get(0,0)))
sys.exit(1 if bad else 0)
