#!/usr/bin/env python3
"""Second-order splitting of eight magnetic-flat states of the finite S3 torus.
Exact Python Fraction arithmetic. No JSON, floating point or diagonalizer.
Uses the independently reconstructed full 1393-state matrix from PR #7.
"""
from contextlib import redirect_stdout
from fractions import Fraction as Q
from io import StringIO
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
with redirect_stdout(StringIO()):
    data=runpy.run_path(str(HERE/'seat_yang_mills_audit.py'))
rows=data['rowmaps']; weights=data['weights']; mag=data['mag']; keys=data['keys']
n=len(rows)
assert n==1393 and len(weights)==len(mag)==n
assert sum(len(row) for row in rows)==32385
assert sum(weights)==7776
flat=[i for i,v in enumerate(mag) if v==0]
assert len(flat)==8
assert [keys[i] for i in flat]==[0,7,21,1332,1339,3996,4017,4024]
assert [weights[i] for i in flat]==[1,3,2,3,3,2,2,2]
nonflat=[i for i in range(n) if mag[i]!=0]
assert min(mag[i] for i in nonflat)==3 and max(mag)==12
for i,row in enumerate(rows):
    diag=row.get(i,0)
    assert 0<=diag<=24 and sum(row.values())==0
    assert sum(-v for j,v in row.items() if j!=i)==diag
    assert all(v<0 for j,v in row.items() if j!=i)
    for j,v in row.items():
        assert weights[i]*v==weights[j]*rows[j].get(i,0)
assert all(rows[i].get(j,0)==(24 if i==j else 0) for i in flat for j in flat)

# Weighted-inner-product operator compression, in original orbit basis:
# B = -P E Q (M restricted to Q)^(-1) Q E P
B=[]
for i in flat:
    line=[]
    for j in flat:
        element=-sum((Q(rows[i][k]*rows[k][j],mag[k])
             for k in rows[i] if k not in flat and j in rows[k]),Q(0))
        line.append(element)
    B.append(line)
assert all(weights[i]*B[a][b]==weights[j]*B[b][a]
           for a,i in enumerate(flat) for b,j in enumerate(flat))
expected=[[-6,-3,0,-3,0,0,0,0],
          [-1,-6,-2,0,-1,0,0,0],
          [0,-3,-6,0,0,0,0,0],
          [-1,0,0,-6,-1,-2,0,0],
          [0,-1,0,-1,-6,0,0,0],
          [0,0,0,-3,0,-6,0,0],
          [0,0,0,0,0,0,-6,0],
          [0,0,0,0,0,0,0,-6]]
assert B==[[Q(x) for x in row] for row in expected]

# Faddeev-LeVerrier: exact characteristic polynomial (no eigensolver).
def mul(a,b):
    return [[sum((a[i][k]*b[k][j] for k in range(8)),Q(0))
             for j in range(8)] for i in range(8)]
I=[[Q(i==j) for j in range(8)] for i in range(8)]
T=I
poly=[Q(1)]
for k in range(1,9):
    A=mul(B,T)
    coeff=-sum(A[i][i] for i in range(8))/k
    poly.append(coeff)
    T=[[A[i][j]+coeff*I[i][j] for j in range(8)] for i in range(8)]
def polymul(x,y):
    z=[0]*(len(x)+len(y)-1)
    for i,a in enumerate(x):
        for j,b in enumerate(y):z[i+j]+=a*b
    return z
expected_poly=[1]
for _ in range(4):expected_poly=polymul(expected_poly,[1,6])
expected_poly=polymul(expected_poly,[1,12,22])
expected_poly=polymul(expected_poly,[1,12,30])
assert poly==expected_poly

# Rigorous explicit small-s bound for H/JB = M+s E:
#   gap > s^2 for 0 < s <= 1/10000.
# ||E||<=48, 3<=M_Q<=12, PEP=24 I,
# ||Q E P||^2 <=12 ||-B|| <120 since 6+sqrt(14)<10.
# For lambda in [0,24s] and D=M_Q+s E_QQ,
# ||(D-lambda)^-1-M_Q^-1|| <= 24s/(3-24s).
# Therefore exact low-level effective matrix differs from
# 24s I+s^2 B by at most s^2 * eta(s), eta(s)<2880s/(3-24s).
# Spectral-counting via the Schur complement yields:
# gap > s^2*(sqrt(14)-sqrt(6)-2eta(s)).
S=Q(1,10000)
eta=Q(120)*24*S/(3-24*S)
assert eta==Q(120,1249)
assert Q(37,10)**2<14 and Q(5,2)**2>6
assert Q(6,5)-2*eta>1
print('HEBC-MAGNETIC|result=PASS|dim=1393|flat=8|E_psd=GRAPH_LAPLACIAN|E_norm_le=48|M_nonflat_ge=3|M_max=12|json=0')
print('HEBC-MAGNETIC|result=PASS|flat_keys=0,7,21,1332,1339,3996,4017,4024|PEP=24I8|first_order_gap=0|json=0')
for ix,row in enumerate(B):
    print(f'HEBC-MAGNETIC|result=PASS|B_row={ix}|values={",".join(str(x) for x in row)}|json=0')
print('HEBC-MAGNETIC|result=PASS|second_order_charpoly=(x+6)^4*(x^2+12x+22)*(x^2+12x+30)|first_gap_coeff=sqrt14_minus_sqrt6|positive=1|json=0')
print('HEBC-MAGNETIC|result=PASS|s_upper=1/10000|error_coeff_max=120/1249|strict_gap_gt=s^2|in_JE_JB_units=JE^2/JB|scope=FINITE_S3_2X2_ONLY|continuum_proven=0|json=0')
