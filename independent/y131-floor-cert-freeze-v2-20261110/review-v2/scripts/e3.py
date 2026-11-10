import re,subprocess,hashlib,os,sys
R='/root/floor-v2/repo'
A='/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-v2-20261110'
V1='/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-20261110'
rec=open(V1+'/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp',encoding='utf-8').read()
ok=bad=0; inrec=0; present=0; n=0
for l in open(A+'/review-v1/E3-PROVENANCE.hbp',encoding='utf-8'):
    if not l.startswith('E3|path='): continue
    d=dict(w.split('=',1) for w in l.strip().split('|')[1:] if '=' in w)
    n+=1
    if (d['path']+'@'+d['sha16']) in rec: inrec+=1
    for base in (A,V1):
        if os.path.exists(os.path.join(base,d['path'])): present+=1; print('PRESENT_IN_TREE',base[-30:],d['path'])
    if d['provenance']=='verified':
        c,p=d['where'].split(':',1)
        b=subprocess.run(['git','-C',R,'cat-file','blob',c+':'+p],capture_output=True).stdout
        h=hashlib.sha256(b).hexdigest()
        if h==d['sha256'] and h.startswith(d['sha16']): ok+=1
        else: bad+=1; print('VERIFIED_MISMATCH',d['path'],h)
print('entries',n,'path@sha16_found_in_v1_record',inrec,'verified_ok',ok,'verified_bad',bad,'present_in_tree',present)
# not_established spot check: hash every blob reachable from all refs, look for any not_established sha16
objs=subprocess.run(['git','-C',R,'rev-list','--all','--objects'],capture_output=True,text=True).stdout.split('\n')
ids=[o.split(' ')[0] for o in objs if o]
typ=subprocess.run(['git','-C',R,'cat-file','--batch-check'],input='\n'.join(ids)+'\n',capture_output=True,text=True).stdout.split('\n')
blobs=[t.split(' ')[0] for t in typ if ' blob ' in t]
ne=set()
for l in open(A+'/review-v1/E3-PROVENANCE.hbp',encoding='utf-8'):
    if l.startswith('E3|path=') and 'provenance=not_established' in l:
        ne.add(re.search(r'sha16=([0-9a-f]{16})',l).group(1))
p=subprocess.Popen(['git','-C',R,'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
hits=0
for b in blobs:
    p.stdin.write((b+'\n').encode()); p.stdin.flush()
    hdr=p.stdout.readline().split(); sz=int(hdr[2]); data=p.stdout.read(sz); p.stdout.read(1)
    if hashlib.sha256(data).hexdigest()[:16] in ne: hits+=1; print('NOT_ESTABLISHED_BUT_IN_HISTORY',b,hashlib.sha256(data).hexdigest()[:16])
print('blobs_hashed',len(blobs),'not_established_fingerprints',len(ne),'hits_in_local_history',hits)
