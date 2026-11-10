import re,sys,hashlib
v1p,v2p=sys.argv[1],sys.argv[2]
def load(p):
    R={};C=[];order=[]
    for l in open(p,encoding='utf-8').read().split('\n'):
        m=re.match(r'^([A-Z_]+)\|id=([0-9]{3})\|',l)
        if m: R[m.group(2)]=l; order.append(m.group(2))
        else: C.append(l)
    return R,C,order
def fields(l):
    out=[];
    for w in l.split('|'):
        if '=' in w: k,v=w.split('=',1); out.append((k,v))
        else: out.append((w,None))
    return out
R1,C1,o1=load(v1p);R2,C2,o2=load(v2p)
print('v1_rows',len(R1),'v2_rows',len(R2),'v1_sha',hashlib.sha256(open(v1p,'rb').read()).hexdigest()[:16],'v2_sha',hashlib.sha256(open(v2p,'rb').read()).hexdigest()[:16])
print('order_v1_seq', o1==sorted(o1), 'v2_order', o2==sorted(o2), 'v1_prefix_of_v2_order', o2[:len(o1)]==o1)
same=[i for i in R1 if R2.get(i)==R1[i]]; ch=[i for i in R1 if i in R2 and R2[i]!=R1[i]]; gone=[i for i in R1 if i not in R2]; new=[i for i in R2 if i not in R1]
print('same',len(same),'changed',len(ch),ch,'removed',gone,'new',new)
pred=[i for i in R1 if R1[i].startswith('PREDICT|')]
print('predict_rows',len(pred),'predict_changed',[i for i in pred if i in ch])
for i in ch:
    f1=fields(R1[i]); f2=fields(R2[i]); d1=dict(f1); d2=dict(f2)
    k1=[k for k,_ in f1]; k2=[k for k,_ in f2]
    added=[k for k in k2 if k not in d1]; removed=[k for k in k1 if k not in d2]
    changed=[k for k in k1 if k in d2 and d1[k]!=d2[k]]
    order_kept=[k for k in k2 if k in d1]==[k for k in k1 if k in d2]
    # is v1 line a byte-subsequence: v2 equals v1 with inserted fields?
    v1_inside = all(('|%s=%s|'%(k,v) if v is not None else '') in R2[i]+'|' or (k.startswith('json')) for k,v in f1 if v is not None)
    print('ROW',i,'added',added,'removed',removed,'changed',changed,'order_kept',order_kept,'all_v1_fields_present_verbatim',v1_inside)
    for k in changed:
        print('   ',k,'| v1:',d1[k][:300]); print('   ',k,'| v2:',d2[k][:300])
print('header_lines_v1',len([c for c in C1 if c]),'v2',len([c for c in C2 if c]))
for c in C1:
    if c not in C2: print('V1_COMMENT_CHANGED:',c[:200])
for c in C2:
    if c not in C1: print('V2_COMMENT_NEW:',c[:160])
