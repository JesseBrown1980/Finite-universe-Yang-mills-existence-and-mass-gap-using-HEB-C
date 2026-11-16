#!/usr/bin/env python3
"""Standalone exact 8x8 adversarial tests for the #198 mu3 window.

The Loewner Hausdorff window is mathematically valid but cannot identify the
third moment of a SPECIFIED operator X and source B. Test from 16-state
X=diag(2 I8, 3 I8), B=[2 I8; 2 I8], independent of source code in #198.
No floats, external libraries, or imports from the producer.
"""
from fractions import Fraction as Q
from math import lcm
import hashlib

N=8

def require(x,why):
    if not x: raise RuntimeError("MU3_SECONDSEAT_REFUSE_"+why)

def eye(x):
    return [[x if i==j else Q(0) for j in range(N)] for i in range(N)]

def symmetric(m):
    return all(m[i][j]==m[j][i] for i in range(N) for j in range(N))

def scaled_identity(m):
    require(symmetric(m),"ASYMMETRIC")
    require(all(m[i][j]==(m[0][0] if i==j else 0) for i in range(N) for j in range(N)),"NOT_SCALAR_IDENTITY")
    return m[0][0]

def moments():
    # X=diag(2 I8, 3 I8), B=[2 I8; 2 I8]
    return [Q(4*(2**k+3**k)) for k in range(4)]

def window(m,g,h):
    m0,m1,m2,_=m
    d=m1-g*m0; c=m2-g*m1
    e=h*m0-m1; f=h*m1-m2
    require(d>0 and e>0,"INVALID_BLOCK_PIVOTS")
    return g*m2+c*c/d,h*m2-f*f/e

def four_gauss_lower(m,m3):
    m0,m1,m2,_=m
    p=m3-m2*m2/m1
    require(p>0,"GAUSS_PIVOT_SINGULAR")
    t=m1-m2*m0/m1
    return m0*m0/m1+t*t/p

def four_lobatto_upper(m,m3,g,h):
    m0,m1,m2,_=m
    s=g+h;gh=g*h
    b=s*m1-m2-gh*m0
    c=s*m2-m3-gh*m1
    require(c>0,"LOBATTO_PIVOT_SINGULAR")
    return (s*m0-m1-b*b/c)/gh

def old_numerator_only_hash(m):
    den=1
    for row in m:
        for x in row:
            den=lcm(den,Q(x).denominator)
    ints=[str(Q(x)*den) for row in m for x in row]
    return hashlib.sha256("|".join(ints).encode("ascii")).hexdigest()

def canonical_rational_hash(m):
    pairs=[str(Q(x).numerator)+"/"+str(Q(x).denominator) for row in m for x in row]
    return hashlib.sha256("|".join(pairs).encode("ascii")).hexdigest()

def main():
    m=moments();g=Q(1);h=Q(4)
    require(m==[8,20,52,140],"REAL_MOMENT_CENSUS")
    lo,hi=window(m,g,h)
    require((lo,hi)==(Q(412,3),Q(428,3)),"WINDOW_MATH")
    fake=Q(139);true=m[3]
    require(lo<fake<hi and fake!=true,"WRONG_INTERIOR_CANDIDATE")
    require(scaled_identity(eye(fake))==fake,"EIGHT_BY_EIGHT_SHAPE")
    source_inverse=Q(4,2)+Q(4,3)
    gauss_fake=four_gauss_lower(m,fake)
    lobatto_fake=four_lobatto_upper(m,fake,g,h)
    gauss_true=four_gauss_lower(m,true)
    lobatto_true=four_lobatto_upper(m,true,g,h)
    require(source_inverse==Q(10,3),"SOURCE_INVERSE")
    require(gauss_fake==Q(64,19) and lobatto_fake==Q(141,41),"FORGED_QUADRATURE")
    require(gauss_fake>source_inverse and gauss_true<=source_inverse<=lobatto_true,"FORGED_BRACKET_NOT_CAUGHT")
    print("MU3_ATTACK|states=16|channels=8|true_mu3="+str(true)+
          "|forged_mu3="+str(fake)+"|window_lo="+str(lo)+"|window_hi="+str(hi)+
          "|forged_passes_symmetry_integer_and_window=YES|real_BtXinvB="+str(source_inverse)+
          "|forged_Gauss_lower="+str(gauss_fake)+
          "|forged_Gauss_excludes_real_source=YES|json=0",flush=True)
    a=eye(Q(1));b=eye(Q(1,2))
    require(old_numerator_only_hash(a)==old_numerator_only_hash(b) and
            canonical_rational_hash(a)!=canonical_rational_hash(b),
            "NUMERATOR_ONLY_HASH_NOT_COLLIDING")
    print("MU3_HASH_ATTACK|matrix_A=I8|matrix_B=I8_over_2|numerator_only_sha256=EQUAL|canonical_rational_sha256=DIFFERENT|recommend_canonical_num_den_pairs=YES|json=0",flush=True)
    point_m=[Q(4*2**k) for k in range(4)]
    l,u=window(point_m,g,h)
    require(l==u==point_m[3],"POINT_MASS_WINDOW")
    gauss_pivot=point_m[3]-point_m[2]**2/point_m[1]
    require(gauss_pivot==0,"POINT_MASS_GAUSS_NOT_SINGULAR")
    print("MU3_RANK_ATTACK|valid_positive_X=2I8|real_mu3_equals_window_endpoint=YES|Gauss_block_pivot=ZERO|inverse_formula_undefined=YES|need_rank_aware_HOLD_or_pseudoinverse=YES|json=0",flush=True)
    print("MU3_REVIEW|spectral_window=NECESSARY_VALID|source_authentication_by_window=FAIL|rational_hash_fingerprint=AMBIGUOUS|boundary_inverse_formula=PARTIAL|real_large_Q_mu3=NOT_COMPUTED|Wilson_weight=HOLD|json=0",flush=True)

if __name__=="__main__":
    main()
