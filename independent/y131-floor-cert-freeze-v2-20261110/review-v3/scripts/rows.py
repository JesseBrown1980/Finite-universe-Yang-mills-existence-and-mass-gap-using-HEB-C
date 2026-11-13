import subprocess,re,sys
repo='/root/floor-v2/repo'
def get(c,p):
    return subprocess.run(['git','-C',repo,'show',c+':'+p],capture_output=True).stdout.decode()
V2='independent/y131-floor-cert-freeze-v2-20261110/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp'
V1='independent/y131-floor-cert-freeze-20261110/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp'
def rows(t):
    d={}
    for l in t.split('\n'):
        m=re.match(r'^([A-Z_]+)\|id=([0-9]{3})\|',l)
        if m: d[m.group(2)]=(m.group(1),l)
    return d
H=rows(get('3b91d1a047d7485693c754ece8c7c18f43fbf326',V2)); C=rows(get('cfc57bef',V2)); O=rows(get('e74d8a46',V1))
pr=[k for k in H if H[k][0]=='PREDICT']
print('head rows',len(H),'predict',len(pr),sorted(pr))
print('predict same as cfc',sum(H[k][1]==C[k][1] for k in pr))
print('predict same as v1',sum(H[k][1]==O.get(k,('',''))[1] for k in pr),[k for k in pr if H[k][1]!=O[k][1]])
def f(l):
    d={}
    for w in l.split('|'):
        if '=' in w:
            a,b=w.split('=',1); d.setdefault(a,b)
    return d
for k in pr:
    a,b=f(H[k][1]),f(O[k][1])
    diff=[x for x in set(a)|set(b) if a.get(x)!=b.get(x)]
    if diff: print('row',k,'fields differing vs v1:',diff)
    for x in ('value','met_if','not_met_if','falsifier'):
        if a.get(x)!=b.get(x): print('  !!',k,x)
# 11 modified rows vs v1
ch=[k for k in O if k in H and H[k][1]!=O[k][1]]
print('modified v1 rows',len(ch),ch)
for k in ch:
    a,b=f(H[k][1]),f(O[k][1])
    changed=sorted(x for x in b if x in a and a[x]!=b[x]); added=[x for x in a if x not in b]; removed=[x for x in b if x not in a]
    # order check
    ka=[x for x in a if x in b]; kb=[x for x in b if x in a]
    print(k,'changed',changed,'added',added,'removed',removed,'order_same',ka==kb)
print('new rows', sorted(k for k in H if k not in O))
chc=[k for k in C if k in H and H[k][1]!=C[k][1]]
print('changed vs cfc',chc, 'new vs cfc', sorted(k for k in H if k not in C))
