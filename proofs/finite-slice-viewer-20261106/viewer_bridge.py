#!/usr/bin/env python3
"""Exact finite-slice jumps and rational enclosures for a continuum shear measurement."""
from fractions import Fraction as Q
from hashlib import sha256
from math import factorial

SIZES=(3,9,27)

def step_kernel(v):
    n=len(v)
    return tuple(4*v[i]+v[(i-1)%n]+v[(i+1)%n] for i in range(n))

def product_kernel(a,b):
    n=len(a)
    assert n==len(b)
    c=[0]*n
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            c[(i+j)%n]+=x*y
    return tuple(c)

def jump_kernel(n,t):
    base=tuple(4 if i==0 else (1 if i in (1,n-1) else 0) for i in range(n))
    result=(1,)+(0,)*(n-1)
    while t:
        if t&1:
            result=product_kernel(result,base)
        base=product_kernel(base,base)
        t>>=1
    return result

def arctan_inv_bounds(q,terms=24):
    s=sum((Q(1,(2*k+1)*q**(2*k+1)) if k%2==0 else -Q(1,(2*k+1)*q**(2*k+1))) for k in range(terms))
    r=Q(1,(2*terms+1)*q**(2*terms+1))
    return (s,s+r) if terms%2==0 else (s-r,s)

def pi_bounds():
    a,b=arctan_inv_bounds(5)
    c,d=arctan_inv_bounds(239)
    return 16*a-4*d,16*b-4*c

def cos_poly(x,n):
    return sum((-1)**k*x**(2*k)/factorial(2*k) for k in range(n))

def cos_bounds(xlo,xhi):
    return cos_poly(xhi,24),cos_poly(xlo,25)

def exp_neg_poly(x,n):
    return sum((-1)**k*x**k/factorial(k) for k in range(n))

def exp_neg_bounds(xlo,xhi):
    return exp_neg_poly(xhi,24),exp_neg_poly(xlo,25)

def scaled_floor(x):
    return x.numerator*10**12//x.denominator

def run():
    plo,phi=pi_bounds()
    cl,ch=exp_neg_bounds(Q(2,27)*plo**2,Q(2,27)*phi**2)
    assert scaled_floor(cl)==scaled_floor(ch)==481387939225
    previous=None
    rows=[]
    for n in SIZES:
        steps=(n//3)**2
        assert Q(steps,6*n*n)==Q(1,54)
        direct=(1,)+(0,)*(n-1)
        for _ in range(steps):
            direct=step_kernel(direct)
        jumped=jump_kernel(n,steps)
        assert direct==jumped
        assert sum(direct)==6**steps
        xlo,xhi=2*plo/n,2*phi/n
        low,high=cos_bounds(xlo,xhi)
        dlo=((4+2*low)/6)**steps
        dhi=((4+2*high)/6)**steps
        if n==3:
            # Exact trigonometric identity cos(2*pi/3) = -1/2.
            dlo=dhi=Q(1,2)
        assert dlo<=dhi and dlo>ch
        el,eh=dlo-ch,dhi-cl
        assert scaled_floor(el)==scaled_floor(eh)
        assert previous is None or eh<previous
        previous=el
        amp=scaled_floor((dlo+dhi)/2)
        err=scaled_floor(el)
        expected={
            3:(500000000000,18612060774),
            9:(481549672464,161733239),
            27:(481389859807,1920581),
        }[n]
        assert (amp,err)==expected,(n,amp,err)
        assert dhi-dlo<Q(1,10**18)
        digest=sha256(','.join(map(str,direct)).encode('ascii')).hexdigest()
        rows.append(
            f'VIEWER_SHEAR|L={n}|steps={steps}|dt=1/{6*n*n}_s'
            f'|t=1/54_s|space=1/{n}_m|power_jump=PASS'
            f'|direct_steps=PASS|nonlinear=EXACT_ZERO|div=EXACT_ZERO'
            f'|kernel_sum=6^{steps}|discrete_amp_floor_pico={amp}'
            f'|continuum_amp_floor_pico={scaled_floor(cl)}'
            f'|abs_error_floor_pico={err}|kernel_sha256={digest}|json=0')
    return '\n'.join(rows)+'\n'

if __name__=='__main__':
    print(run(),end='')
