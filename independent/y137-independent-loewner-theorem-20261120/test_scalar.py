#!/usr/bin/env python3
"""Independent integer-only exact signed-Schur Gauss/Lobatto sign toy.

For X=diag(2,3,5,7), V=(1,1,1,1)^T, g=2, h=7,
recover moment formulas and both strict matrix-scalar bounds.
No input files, external imports, float calculations, or producer code.
Theorem general matrix proof is in THEOREM.md.
"""
from math import lcm

class Hold(Exception):
    pass

def need(ok,why):
    if not ok:raise Hold(why)

def lt(a,b,c,d):
    need(b>0 and d>0,"positive_exact_denominators")
    return a*d<c*b

def validate(g,h,mu,source):
    need(0<g<h and all(g<=x<=h for x in source),
         "strict_physical_operator_support")
    m0,m1,m2,m3=mu
    kdet=m1*m3-m2*m2
    need(m1>0 and kdet>0,"positive_Gauss_2x2_Gram")
    l_num=m3*m0*m0-2*m2*m0*m1+m1*m1*m1
    l_den=kdet
    need(l_num>0,"positive_Gauss_lower")
    s=g+h
    gh=g*h
    b=s*m1-m2-gh*m0
    c=s*m2-m3-gh*m1
    need(c>0,"strict_positive_Lobatto_weighted_Gram")
    u_num=(s*m0-m1)*c-b*b
    u_den=gh*c
    need(u_num>0 and u_den>0,"positive_Lobatto_upper")
    return (l_num,l_den),(u_num,u_den),b,c,kdet

def main():
    x=(2,3,5,7)
    g,h=2,7
    mu=tuple(sum(t**k for t in x) for k in range(4))
    need(mu==(4,17,87,503),"frozen_scalar_exact_moments")
    lower,upper,b,c,det=validate(g,h,mu,x)
    need(lower==(1129,982) and upper==(698,588) and
         (b,c,det)==(10,42,982),"exact_independent_Gauss_Lobatto_formula")
    denom=lcm(*x)
    f_num=sum(denom//t for t in x)
    need((f_num,denom)==(247,210),"original_full_inverse_resolvent")
    need(lt(lower[0],lower[1],f_num,denom),
         "Gauss_below_true_full_resolvent")
    need(lt(f_num,denom,upper[0],upper[1]),
         "Lobatto_above_true_full_resolvent")
    # S=U0-F, so Schur order is the opposite of the F order.
    u0=3
    s_lower=(u0*upper[1]-upper[0],upper[1])
    s_true=(u0*denom-f_num,denom)
    s_upper=(u0*lower[1]-lower[0],lower[1])
    need(lt(s_lower[0],s_lower[1],s_true[0],s_true[1]) and
         lt(s_true[0],s_true[1],s_upper[0],s_upper[1]),
         "original_Schur_fourmoment_bracket_orientation")
    # Negative controls must exercise mathematics rather than receipt SHA.
    rejected=0
    def refuse(fn):
        nonlocal rejected
        try:fn()
        except Hold:rejected+=1
        else:raise Hold("incorrect_Loewner_premise_accepted")
    refuse(lambda:validate(3,h,mu,x))
    refuse(lambda:validate(g,6,mu,x))
    refuse(lambda:validate(g,h,(mu[0],mu[1],mu[2],1),x))
    refuse(lambda:need(lt(upper[0],upper[1],f_num,denom),
                       "wrong_Lobatto_lower_order"))
    refuse(lambda:need(lt(f_num,denom,lower[0],lower[1]),
                       "wrong_Gauss_upper_order"))
    refuse(lambda:need(lt(s_upper[0],s_upper[1],s_true[0],s_true[1]),
                       "reversed_Schur_lower"))
    need(rejected==6,"all_exact_negative_controls")
    print("Y137_FOUR_MOMENT_LOEWNER_TOY|original_X_spectrum=2,3,5,7"+
          "|original_source_moments=4,17,87,503"+
          "|Gauss_lower=1129/982|true_inverse=247/210"+
          "|Lobatto_upper=698/588"+
          "|exact_Gauss_less_than_F_less_than_Lobatto=PASS"+
          "|Schur_lower_less_than_S_less_than_upper=PASS"+
          "|wrong_support_and_reversed_bounds=6_REJECTED"+
          "|abstract_matrix_theorem=GRAM_SCHUR_COMPLEMENT"+
          "|physical_source=SEPARATE_PREMISE"+
          "|first_Wilson=FORMAL_HOLD|continuum_4D=OPEN|json=0",flush=True)

if __name__=="__main__":
    try:main()
    except Hold as e:
        print("Y137_FOUR_MOMENT_LOEWNER_HOLD|reason="+str(e)+
              "|original_Wilson=FORMAL_HOLD|json=0",flush=True)
        raise SystemExit(2) from None
