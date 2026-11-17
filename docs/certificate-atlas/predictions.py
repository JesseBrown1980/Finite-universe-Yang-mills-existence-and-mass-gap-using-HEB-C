#!/usr/bin/env python3
"""Fail-closed, no-floating-point atlas hypothesis tests from a frozen JSON file.

The file's SHA is pinned; source values are parsed as exact decimal digit strings.
All arithmetic is integer pairs and cross multiplication, including Feshbach toy.
The asymptotic fit is retrospective, and Wilson spectral weight stays HOLD.
"""
import hashlib
import sys
from math import gcd, isqrt
from pathlib import Path

DATA_SHA = 'a40c19559ac9739610abd4241d1ec9585f23c509f1dfbdfa04e0daa08cb7e0f5'

def need(condition, label):
    if not condition:
        raise SystemExit('ATLAS_EXACT_REFUSE|check='+label+'|json=0')

def rat(n,d=1):
    need(d!=0,'nonzero_rational_denominator')
    if d<0:n,d=-n,-d
    c=gcd(abs(n),d)
    return (n//c,d//c)

def pos(a):return a[0]>=0

def neg(a):return (-a[0],a[1])

def add(a,b):return rat(a[0]*b[1]+b[0]*a[1],a[1]*b[1])

def mul(a,b):return rat(a[0]*b[0],a[1]*b[1])

def sub(a,b):return add(a,neg(b))

def reciprocal(a):return rat(a[1],a[0])

def le(a,b):return a[0]*b[1]<=b[0]*a[1]

def lt(a,b):return a[0]*b[1]<b[0]*a[1]

def pow_n(a,n):
    need(n>=0,'no_negative_integer_exponents')
    result=rat(1)
    for _ in range(n):result=mul(result,a)
    return result

def show(a):return str(a[0])+'/'+str(a[1])

def decimal(text):
    raw=text.strip().strip(',')
    sign=-1 if raw.startswith('-') else 1
    if sign<0:raw=raw[1:]
    terms=raw.split('.')
    need(len(terms)<=2 and all(q.isdigit() for q in terms),'numeric_decimal_only')
    if len(terms)==1:return rat(sign*int(terms[0]))
    den=1
    for _ in terms[1]:den*=10
    return rat(sign*int(terms[0]+terms[1]),den)

def get_3x3(text):
    entries={}
    within=False
    entry={}
    for line in text.splitlines():
        s=line.strip()
        if s.startswith('"gap_measurements": ['):within=True;continue
        if s.startswith('"spectral_measurements": ['):within=False
        if not within:continue
        if s=='{':entry={};continue
        if s.startswith('"name": '):entry['name']=s.split('"')[3]
        elif s.startswith('"r": '):entry['r']=int(s.partition(':')[2].strip().rstrip(','))
        elif s.startswith('"lower": '):entry['lower']=decimal(s.partition(':')[2])
        elif s.startswith('"upper": '):
            part=s.partition(':')[2].strip().rstrip(',')
            entry['upper']=None if part=='null' else decimal(part)
        elif s.startswith('"kind": '):entry['kind']=s.split('"')[3]
        elif s in ('}', '},') and entry.get('name')=='3x3' and entry.get('kind')=='interval':
            rr=entry['r'];need(rr not in entries,'duplicate_3x3_cell');entries[rr]=entry
    need(set(entries)=={9,27,81,243},'four_original_3x3_intervals')
    return entries

def rsum(values):
    result=rat(0)
    for value in values:result=add(result,value)
    return result

def bilinear(matrix,u,v):
    return rsum(mul(mul(u[i],matrix[i][j]),v[j]) for i in range(len(u)) for j in range(len(v)))

def feshbach_toy():
    Qdiag=[rat(9),rat(11),rat(13)]
    B=[[rat(n) for n in row] for row in ((2,-1),(0,1),(-2,3))]
    O=[[rat(n) for n in row] for row in ((2,1,2,0,1),(1,3,-1,1,0),(2,-1,4,1,-2),(0,1,1,5,2),(1,0,-2,2,6))]
    p1,p2=[rat(1),rat(2)],[rat(-1),rat(1)]
    E1,E2=rat(1),rat(2)
    def complement(p,E):
        return [neg(mul(rsum(mul(B[i][j],p[j]) for j in range(2)),reciprocal(sub(Qdiag[i],E)))) for i in range(3)]
    q1,q2=complement(p1,E1),complement(p2,E2)
    actual=bilinear(O,p2+q2,p1+q1)
    pp=bilinear([row[:2] for row in O[:2]],p2,p1)
    pq=rsum(mul(mul(p2[i],O[i][j+2]),q1[j]) for i in range(2) for j in range(3))
    qp=rsum(mul(mul(q2[j],O[j+2][i]),p1[i]) for j in range(3) for i in range(2))
    qq=rsum(mul(mul(q2[i],O[i+2][j+2]),q1[j]) for i in range(3) for j in range(3))
    effective=rsum((pp,pq,qp,qq))
    need(effective==actual,'original_Feshbach_observable_identity')
    need(sub(effective,qq)!=actual,'omit_QOQ_negative_control')
    for p,q,E in ((p1,q1,E1),(p2,q2,E2)):
        norm=rsum(mul(value,value) for value in p)
        for i in range(3):
            bp=rsum(mul(B[i][j],p[j]) for j in range(2))
            norm=add(norm,mul(mul(bp,bp),reciprocal(mul(sub(Qdiag[i],E),sub(Qdiag[i],E)))))
        need(norm==rsum(mul(v,v) for v in p+q),'full_physical_projected_norm_identity')
    return actual,qq

def line(tag,**parts):
    return tag+'|'+'|'.join(k+'='+str(v) for k,v in parts.items())+'|json=0'

def main():
    path=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('certificates.json')
    raw=path.read_bytes()
    need(hashlib.sha256(raw).hexdigest()==DATA_SHA,'full_original_certificate_data_sha')
    data=raw.decode('utf-8')
    entries=get_3x3(data)
    out=[line('ATLAS_SOURCE',commit='98c39fbaa1e6ecf9e6454062e90801f385356063',data_sha256=DATA_SHA,records=80)]
    inferred={}
    for r in sorted(entries):
        a=entries[r]
        model2=sub(rat(3*r),rat(21,r))
        model3=sub(model2,rat(43,r*r))
        inside=le(a['lower'],model3) and le(model3,a['upper'])
        need(inside==(r!=9),'four_asymptotic_model_expectations')
        inflo=mul(sub(model2,a['upper']),rat(r*r))
        infhi=mul(sub(model2,a['lower']),rat(r*r))
        inferred[r]=(inflo,infhi)
        out.append(line('ATLAS_GAP_TEST',r=r,certified_lo=show(a['lower']),certified_hi=show(a['upper']),
          model2=show(model2),model3=show(model3),model3_inside='YES' if inside else 'NO',
          inferred_c3_lo=show(inflo),inferred_c3_hi=show(infhi)))
    fake=sub(sub(rat(81),rat(21,27)),rat(44,27*27))
    need(not(le(entries[27]['lower'],fake) and le(fake,entries[27]['upper'])),'wrong_c3_44_rejected')
    common_lower,common_upper=inferred[27]
    for rr in (81,243):
        if lt(common_lower,inferred[rr][0]):common_lower=inferred[rr][0]
        if lt(inferred[rr][1],common_upper):common_upper=inferred[rr][1]
    need(le(common_lower,rat(43)) and le(rat(43),common_upper),'c3_43_inside_high_r_common')
    need(lt(common_upper,inferred[9][0]),'r9_outside_high_r_c3')
    out.append(line('ATLAS_GAP_VERDICT',higher_r='3_OF_3',r9='MODEL_REJECTED',wrong_44='REJECTED',
       coefficient_43_high_r='COMPATIBLE',uniform_r9='REJECTED',scope='RETROSPECTIVE_ONLY'))
    Q,E2,E3,cap=decimal('94.0682'),decimal('69.949433884'),decimal('69.968699300'),rat(468)
    sep,sep3=sub(Q,E2),sub(E3,E2)
    kappa=mul(sub(cap,E2),reciprocal(sep))
    scalar=10**18
    root=isqrt(kappa[0]*scalar*scalar//kappa[1])
    sqlo,sqhi=rat(root,scalar),rat(root+1,scalar)
    rho_lo=mul(sub(sqlo,rat(1)),reciprocal(add(sqlo,rat(1))))
    rho_hi=mul(sub(sqhi,rat(1)),reciprocal(add(sqhi,rat(1))))
    need(lt(rat(0),rho_lo) and lt(rho_hi,rat(1)),'rho_range')
    for name,goal,want in (('ONE_PERCENT',rat(1,100),11),('THREE_PER_THOUSAND',rat(3,1000),13),('OLD_1_OVER_700',rat(1,700),15),('TEN_THOUSANDTH',rat(1,10000),20)):
        current=rat(1)
        degree=0
        while not lt(mul(rat(2),current),goal):
            current=mul(current,rho_hi)
            degree+=1
            need(degree<=99,'Chebyshev_degree_limit')
        need(degree==want,'Chebyshev_minimal_sufficient_degree')
        out.append(line('ATLAS_FILTER_TEST',target=name,degree=degree,
           upper_bound=show(mul(rat(2),current)),scope='THEORETICAL_INVERSE_RESIDUAL_ONLY'))
    ratio=mul(sep,reciprocal(sep3))
    need(lt(rat(1000),ratio),'spectral_scale_ratio_gt_1000')
    out.append(line('ATLAS_FILTER_VERDICT',Q_minus_E2=show(sep),E3_minus_E2=show(sep3),ratio=show(ratio),
       rho_lower=show(rho_lo),rho_upper=show(rho_hi),physical_Wilson='NOT_COMPUTED'))
    value,qq=feshbach_toy()
    out.append(line('ATLAS_FESHBACH_TOY',transition=show(value),QOQ_term=show(qq),
       exact_effective_observable='PASS',complete_normalization='PASS',omitted_QOQ='REJECTED',physical_S3_Wilson='NOT_COMPUTED'))
    out.append(line('ATLAS_VERDICT',readme_data='SHA_PINNED',retrospective_high_r='3_OF_3',
        r9='MODEL_REJECTED',Chebyshev_integer_pairs='PASS',Feshbach_toy='PASS',Wilson_weight='HOLD',continuum='OPEN'))
    print('\n'.join(out))

if __name__=='__main__':main()