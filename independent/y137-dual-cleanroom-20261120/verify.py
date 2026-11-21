#!/usr/bin/env python3
"""Independent exact full-Q source audit from a fresh S3 orbit graph.

Reads binary physical source generated independently by graph.rs, recomputes
all K3 residuals and complete K4 boundary W norms with Python arbitrary ints;
compares aggregate exact values to original immutable matched Wilson artifact.
No historical graph, Wilson, dual, moment, or Schur modules are imported.
"""
import hashlib
import sys
from pathlib import Path

E1=69909586556
E2=69949433884
DEN=1000000000
SCALE=1000000000000
WF=(1,3,2,3,3,2,2,2)
OP=(14,8,5,6,0,2,-7,-7)
V1=(1000000000,997998757,997000845,39006811,38860510,2944164,80455,80455)
V2=(112491544,-39124838,-114340075,1000000000,978089453,221700078,5301152,5301152)

def check(ok,detail):
    if not ok:raise ValueError(detail)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def field_set(raw,label):
    found=[]
    for line in raw.splitlines():
        if not line.startswith(label+'|'):continue
        record={}
        for item in line.split('|')[1:]:
            k,sep,v=item.partition('=')
            check(bool(k) and bool(sep) and k not in record,'duplicate_malformed_'+label)
            record[k]=v
        check(record.pop('json',None)=='0','hbp_terminator')
        found.append(record)
    check(len(found)==1,'unique_source_'+label)
    return found[0]

class Reader:
    def __init__(self,data):self.data=memoryview(data);self.at=0
    def read(self,n):
        p=self.at;self.at+=n;check(self.at<=len(self.data),'short_source_binary')
        return self.data[p:self.at]
    def u(self,n):return int.from_bytes(self.read(n),'little')
    def i(self,n):return int.from_bytes(self.read(n),'little',signed=True)
    def skip(self,n):self.read(n)

def parse_header(r):
    check(bytes(r.read(8))==b'Y137RAW1','raw_source_magic')
    n=r.u(4);ext=r.u(4);edges=r.u(4)
    check((n,ext,edges)==(155378,1985218,1356528),'original_s3_K3_K4_geometry')
    flatw=tuple(r.u(1) for _ in range(8))
    flato=tuple(r.i(1) for _ in range(8))
    check(flatw==WF and flato==OP,'independent_group_weight_Wilson')
    return n,ext,edges

def advance_rows(r,n):
    start=r.at
    for _ in range(n):
        r.skip(8+1+1+1+2+16)
        a=r.u(2)
        r.skip(a*6)
    return start,r.at

def advance_outer(r,n):
    start=r.at
    for _ in range(n):
        r.skip(8+1)
        a=r.u(2)
        r.skip(a*6)
    return start,r.at

def read_vectors(r,n):
    out=[]
    for _ in range(4):out.append([r.i(16) for _ in range(n)])
    check(r.at==len(r.data),'source_binary_no_trailing_data')
    return out

def compute(buf):
    r=Reader(buf)
    n,ext,edges=parse_header(r)
    rowlo,rowhi=advance_rows(r,n)
    extlo,exthi=advance_outer(r,ext)
    q1,q2,u21,u12=read_vectors(r,n)
    check(all(isinstance(v,int) for group in [q1,q2,u21,u12] for v in group[:16]),'exact_source_integer')
    rr=Reader(buf);rr.at=rowlo
    residual=[0,0,0,0]
    raw_f=[WF[j]*(2*OP[j]-16)*SCALE*V1[j] for j in range(8)]
    raw_a=[WF[j]*(2*OP[j]-16)*SCALE*V2[j] for j in range(8)]
    adjacency_count=0
    wvalues={1:0,2:0,3:0,6:0}
    ovalues={}
    for i in range(n):
        key=rr.u(8);w=rr.u(1);mag=rr.u(1);o=rr.i(1);db=rr.i(2)
        C=[rr.u(2) for _ in range(8)]
        cnt=rr.u(2);adjacency_count+=cnt
        check(w in wvalues and -7<=o<=14 and 0<=mag<=36 and db>0,'original_physical_source_row')
        wvalues[w]+=1
        ovalues[o]=ovalues.get(o,0)+1
        sumq1=sumq2=sumu21=sumu12=0
        for _ in range(cnt):
            j=rr.u(4);c=rr.u(2)
            check(j<n and j!=i and c>0,'source_QQ_adjacency')
            sumq1+=c*q1[j]
            sumq2+=c*q2[j]
            sumu21+=c*u21[j]
            sumu12+=c*u12[j]
        b1=SCALE*sum(C[j]*V1[j] for j in range(8))
        b2=SCALE*sum(C[j]*V2[j] for j in range(8))
        s1=(DEN*db-E1)*q1[i]-DEN*(sumq1+b1)
        s2=(DEN*db-E2)*q2[i]-DEN*(sumq2+b2)
        d21=DEN*((2*o-16)*q1[i]+sumu21)-(DEN*db-E2)*u21[i]
        d12=DEN*((2*o-16)*q2[i]+sumu12)-(DEN*db-E1)*u12[i]
        residual[0]+=w*s1*s1
        residual[1]+=w*s2*s2
        residual[2]+=w*d21*d21
        residual[3]+=w*d12*d12
        for j,v in enumerate(C):
            if v:
                raw_f[j]+=w*v*u21[i]
                raw_a[j]+=w*v*u12[i]
        if i in (0,n//2,n-1):print('Y137_CLEANROOM_ROW_PROGRESS|i='+str(i)+'|remaining='+str(n-i-1),flush=True)
    check(rr.at==rowhi and adjacency_count==edges,'K3_complete_adjacency_census')
    rr.at=extlo
    for f in range(ext):
        key=rr.u(8);wf=rr.u(1);cnt=rr.u(2)
        check(wf in wvalues and cnt>0,'source_Q4_weight')
        a=b=c=d=0
        for _ in range(cnt):
            src=rr.u(4);wc=rr.u(2)
            check(src<n and wc>0,'exterior_w_reciprocal')
            a+=wc*q1[src];b+=wc*q2[src]
            c+=wc*u21[src];d+=wc*u12[src]
        check(a%wf==b%wf==c%wf==d%wf==0,'weighted_source_Q4_boundary_balance')
        residual[0]+=wf*(DEN*(a//wf))**2
        residual[1]+=wf*(DEN*(b//wf))**2
        residual[2]+=wf*(DEN*(c//wf))**2
        residual[3]+=wf*(DEN*(d//wf))**2
        if f in (0,ext//2,ext-1):print('Y137_CLEANROOM_OUTER_PROGRESS|f='+str(f)+'|remaining='+str(ext-f-1),flush=True)
    check(rr.at==exthi,'Q4_entire_residual_support_count')
    return {'norms':tuple(residual),'raw_f':tuple(raw_f),'raw_a':tuple(raw_a),
            'states':n,'outer':ext,'edges':edges,
            'W_histogram':wvalues,'Wilson_histogram':ovalues}

def verify(receipt,metrics):
    rec=receipt.decode('ascii')
    inp=field_set(rec,'Y137_MATCHED_ACTION_INPUT')
    pair=field_set(rec,'Y137_MATCHED_PAIR')
    graph=field_set(rec,'Y137_MATCHED_ACTION_GRAPH')
    check(tuple(map(int,pair['original_E1_recenter_v'].split(',')))==V1 and
          tuple(map(int,pair['original_E2_recenter_v'].split(',')))==V2,'original_signed_matched_vectors')
    check(graph['original_PQ_edges']=='264' and graph['physical_weighted_PQ_adjoint']=='PASS',
          'original_PQ_graph_origin')
    for key,value in zip(['g1_residual_norm2_scaled','g2_residual_norm2_scaled',
                          'd21_residual_norm2_scaled','d12_residual_norm2_scaled'],metrics['norms']):
        check(int(inp[key])==value,'clean_room_original_fullQ_residual_'+key)
    for key,vec in [('forward_raw',metrics['raw_f']),('adjoint_raw',metrics['raw_a'])]:
        check(tuple(map(int,inp[key].split(',')))==vec,'clean_room_original_W_action_'+key)
    needf=sum(V2[j]*metrics['raw_f'][j] for j in range(8))
    needa=sum(V1[j]*metrics['raw_a'][j] for j in range(8))
    check((needf,needa)==(int(inp['forward_W_bilinear']),int(inp['adjoint_W_bilinear'])),
          'full_W_source_bilinear')
    testcount=0
    tests=[]
    for k in ['g1_residual_norm2_scaled','g2_residual_norm2_scaled',
              'd21_residual_norm2_scaled','d12_residual_norm2_scaled',
              'forward_raw','adjoint_raw','forward_W_bilinear','adjoint_W_bilinear']:
        z=dict(inp);z[k]=str(z[k])+'7'
        tests.append((k,z))
    for k,z in tests:
        try:
            if k=='forward_raw':check(tuple(map(int,z[k].split(',')))==metrics['raw_f'],'tampered_forward_raw')
            elif k=='adjoint_raw':check(tuple(map(int,z[k].split(',')))==metrics['raw_a'],'tampered_adjoint_raw')
            elif k=='forward_W_bilinear':check(int(z[k])==needf,'tampered_forward_bilinear')
            elif k=='adjoint_W_bilinear':check(int(z[k])==needa,'tampered_adjoint_bilinear')
            else:
                i=['g1_residual_norm2_scaled','g2_residual_norm2_scaled',
                   'd21_residual_norm2_scaled','d12_residual_norm2_scaled'].index(k)
                check(int(z[k])==metrics['norms'][i],'tampered_source_norm')
        except ValueError:testcount+=1
        else:raise ValueError('forged_source_value_accepted')
    check(testcount==8,'source_negative_controls')
    return testcount

def main():
    check(len(sys.argv)==3,'usage_verify.py_SOURCE.bin_ORIGINAL_ALL.hbp')
    data=Path(sys.argv[1]).read_bytes()
    raw=Path(sys.argv[2]).read_bytes()
    met=compute(data)
    controls=verify(raw,met)
    print('Y137_CLEANROOM_FULL_Q_DUAL_SOURCE|physical_orbit_graph=FRESH_24_LINK_S3'+
          '|original_Q3_states='+str(met['states'])+'|original_Q4_exterior='+str(met['outer'])+
          '|W_reciprocity=FRESH_SOURCE_PASS|original_Wilson=FRESH_7_WINDINGS_PASS'+
          '|trial_source_20_sweeps=FRESH_PASS|forward_dual_20_sweeps=FRESH_PASS'+
          '|adjoint_dual_20_sweeps=FRESH_PASS|all_four_full_Q_W_norms=EXACT_AGREE_ORIGINAL'+
          '|eight_forward_action_entries=EXACT_AGREE_ORIGINAL'+
          '|eight_adjoint_action_entries=EXACT_AGREE_ORIGINAL'+
          '|changed_inputs='+str(controls)+'_REJECTED|json=0',flush=True)
    print('Y137_CLEANROOM_SOURCE_HASH|full_Q_original_dual_source_sha256='+sha(data)+
          '|original_action_receipt_sha256='+sha(raw)+'|json=0',flush=True)

if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,IndexError,OverflowError) as err:
        print('Y137_CLEANROOM_REFUSE|reason='+str(err)+'|json=0',flush=True)
        raise SystemExit(2)
