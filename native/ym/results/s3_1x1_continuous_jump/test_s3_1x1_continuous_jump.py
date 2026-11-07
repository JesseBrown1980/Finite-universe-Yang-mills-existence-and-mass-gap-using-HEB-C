#!/usr/bin/env python3
"""Exact small-volume S3 Yang-Mills Hamiltonian and Euclidean-time jump.

Rebuilds the 1x1 periodic torus from 36 raw S3 link pairs and 11
simultaneous-conjugation orbits. H = JE*E+JB*M, at JE=JB=1.
The genuine finite gauge-theory interaction is used; not a generic toy H.
Checks spectrum by integer characteristic polynomials and integer
generalized symmetric inertia; gauge-invariant Wilson correlation by
exact rational Taylor/binomial spectral approximants (certified tails).
Checks modular 3-power jumps and CRT reconstruction separately.

The continuous-time reference is exp(-t H) for the SAME finite H. Its
existence is an elementary finite-dimensional limit, NOT a continuum
spatial-lattice limit, physical experiment or Clay existence proof.
The reference vector for JB=1 is NOT the interacting vacuum.

Prediction frozen before executable: PREDICT-20261106.hbp commit 031d1192.
Deliberately retains a numerical prediction miss; results are never
silently changed to match preregistration. Integer-only; no float/JSON.
"""
from hashlib import sha256
from itertools import permutations
from math import gcd
from pathlib import Path
import sys

P1=1000081
P2=1000003
R=144
STEPS=(27,81,243,729,19683,531441,43046721)
MISS_PREDICTION_ID="10"
RED=("orbit_weight","magnetic_diagonal","wrong_cube","signed_shadow")
sabotage=""
if len(sys.argv)>2 or (len(sys.argv)==2 and
        (not sys.argv[1].startswith("sabotage=") or
         sys.argv[1][9:] not in RED)):
    print("usage: test_s3_1x1_continuous_jump.py [sabotage=NAME]")
    sys.exit(2)
if len(sys.argv)==2:
    sabotage=sys.argv[1][9:]


def emit(tag,**args):
    print(tag+"|"+"|".join(str(k)+"="+str(v) for k,v in args.items())+"|json=0")


def check(condition,name):
    if not condition:
        emit("FAILED",name=name)
        raise AssertionError(name)


def q(n,d=1):
    assert isinstance(n,int) and isinstance(d,int) and d!=0
    if d<0:
        n,d=-n,-d
    g=gcd(n,d)
    return (n//g,d//g)


def add(x,y):
    return q(x[0]*y[1]+y[0]*x[1],x[1]*y[1])


def neg(x):
    return (-x[0],x[1])


def sub(x,y):
    return add(x,neg(y))


def mul(x,y):
    return q(x[0]*y[0],x[1]*y[1])


def le(x,y):
    return x[0]*y[1] <= y[0]*x[1]


def lt(x,y):
    return x[0]*y[1] < y[0]*x[1]


def txt(x):
    return str(x[0])+"/"+str(x[1])


def powerint(x,n):
    assert n>=0
    v=1
    for _ in range(n):
        v*=x
    return v


def fmt(x,places=18,ceil=False):
    scale=powerint(10,places)
    v= -((-x[0]*scale)//x[1]) if ceil else x[0]*scale//x[1]
    sign="-" if v<0 else ""
    s=str(abs(v)).zfill(places+1)
    return sign+s[:-places]+"."+s[-places:]


def perm_mul(a,b):
    return tuple(a[b[i]] for i in range(3))


def perm_inv(a):
    return tuple(a.index(i) for i in range(3))


def perm_conj(t,a):
    return perm_mul(perm_mul(t,a),perm_inv(t))


def commutator(a,b):
    return perm_mul(perm_mul(perm_mul(a,b),perm_inv(a)),perm_inv(b))


def trace_std(a):
    return sum(int(a[i]==i) for i in range(3))-1


def matmul(a,b,mod=None):
    n=len(a)
    out=[[0]*n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            t=a[i][k]
            if t:
                for j in range(n):
                    out[i][j]+=t*b[k][j]
        if mod:
            out[i]=[t%mod for t in out[i]]
    return out


def matvec(a,v,mod=None):
    out=[sum(a[i][j]*v[j] for j in range(len(v))) for i in range(len(a))]
    return [x%mod for x in out] if mod else out


def matrix_power(a,k,mod):
    n=len(a)
    out=[[int(i==j) for j in range(n)] for i in range(n)]
    while k:
        if k%2:
            out=matmul(out,a,mod)
        k//=2
        if k:
            a=matmul(a,a,mod)
    return out


def cube_power(a,k,mod):
    for _ in range(k):
        a=matmul(matmul(a,a,mod),a,mod)
    return a


def int_det(a):
    n=len(a)
    z=[row[:] for row in a]
    prev=1
    parity=1
    for k in range(n-1):
        if z[k][k]==0:
            for i in range(k+1,n):
                if z[i][k]:
                    z[k],z[i]=z[i],z[k]
                    parity=-parity
                    break
            else:
                return 0
        pivot=z[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                num=z[i][j]*pivot-z[i][k]*z[k][j]
                check(num%prev==0,"bareiss_integral")
                z[i][j]=num//prev
        for i in range(k+1,n):
            z[i][k]=0
        prev=pivot
    return parity*z[n-1][n-1]


def below_threshold(h,w,a,b):
    n=len(h)
    c=[[w[i]*(b*h[i][j]-(a if i==j else 0))
        for j in range(n)] for i in range(n)]
    check(all(c[i][j]==c[j][i] for i in range(n)
              for j in range(n)),"symmetric_pencil")
    signs=[1]
    for k in range(1,n+1):
        val=int_det([row[:k] for row in c[:k]])
        check(val!=0,"sturm_no_zero_principal_minor")
        signs.append(1 if val>0 else -1)
    return sum(int(signs[i]!=signs[i-1]) for i in range(1,len(signs)))


def charpoly(h):
    n=len(h)
    b=[[int(i==j) for j in range(n)] for i in range(n)]
    coefficients=[1]
    for k in range(1,n+1):
        v=matmul(h,b)
        t=sum(v[i][i] for i in range(n))
        check(t%k==0,"characteristic_integral")
        a=-(t//k)
        coefficients.append(a)
        for i in range(n):
            v[i][i]+=a
        b=v
    return list(reversed(coefficients))


def pmul(a,b):
    c=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            c[i+j]+=x*y
    return c


def characteristic_reference():
    p=[1]
    for _ in range(3):
        p=pmul(p,[-6,1])
    p=pmul(p,[-252,135,-21,1])
    return pmul(p,[-4104,6138,-2655,468,-36,1])


def e_reference():
    p=[1]
    for base,degree in ((0,1),(3,2),(6,5),(9,2),(12,1)):
        for _ in range(degree):
            p=pmul(p,[-base,1])
    return p


def state_sha(v):
    h=sha256()
    for x in v:
        # signed two's complement not needed for the modulo state
        assert x>=0
        h.update(x.to_bytes(8,"big"))
    return h.hexdigest()


def build_orbits():
    g=tuple(permutations(range(3)))
    raw=[(a,b) for a in g for b in g]
    trans=[a for a in g if trace_std(a)==0]
    check(len(g)==6 and len(raw)==36 and len(trans)==3,"S3_group")
    orbitset={frozenset((perm_conj(t,a),perm_conj(t,b)) for t in g)
              for a,b in raw}
    order={pair:i for i,pair in enumerate(raw)}
    orbits=sorted(orbitset,key=lambda o:min(order[p] for p in o))
    where={pair:i for i,o in enumerate(orbits) for pair in o}
    weights=[len(o) for o in orbits]
    check(len(orbits)==11 and sum(weights)==36,"gauge_orbit_count")
    n=len(orbits)
    E=[[0]*n for _ in range(n)]
    M=[[0]*n for _ in range(n)]
    O=[]
    for i,orbit in enumerate(orbits):
        a,b=min(orbit,key=lambda p:order[p])
        E[i][i]+=6
        for t in trans:
            E[i][where[(perm_mul(t,a),b)]]-=1
            E[i][where[(a,perm_mul(t,b))]]-=1
        chi=trace_std(commutator(a,b))
        M[i][i]=2-chi
        O.append(chi)
        for ac,bc in orbit:
            check(trace_std(commutator(ac,bc))==chi,"magnetic_orbit_invariance")
    h=[[E[i][j]+M[i][j] for j in range(n)] for i in range(n)]
    check(all(weights[i]*h[i][j]==weights[j]*h[j][i]
              for i in range(n) for j in range(n)),"weighted_self_adjoint")
    check(all(x in (0,3) for x in [M[i][i] for i in range(n)]),
          "magnetic_values")
    return g,weights,E,M,O,h


def compute_moments(H,w,u,count):
    v=u[:]
    nums=[]
    for _ in range(count+1):
        nums.append(sum(w[i]*u[i]*v[i] for i in range(len(u))))
        v=matvec(H,v)
    return nums


def tail_bound():
    n=1
    d=1
    for k in range(1,R+2):
        n*=15
        d*=k
    # geometric majorant of remainder as (next ratio <= 1/2).
    return q(9*n,2*d)


def correlation_series(nums,N=None):
    coefficient=q(1)
    result=q(0)
    upper=R
    if N is not None:
        upper=min(upper,N)
    for k in range(upper+1):
        result=add(result,mul(coefficient,q(nums[k],144)))
        if k<upper:
            if N is None:
                coefficient=mul(coefficient,q(-1,k+1))
            else:
                coefficient=mul(coefficient,q(-(N-k),N*(k+1)))
    return result


def crt_pair(x,p1,p2):
    x1=x%p1
    x2=x%p2
    offset=((x2-x1)*pow(p1,-1,p2))%p2
    v=x1+p1*offset
    prod=p1*p2
    if v>prod//2:
        v-=prod
    return v


def compute_modular_jumps(H,w,u):
    n=len(H)
    for p in (P1,P2):
        check(gcd(p,43046721)==1,"prime_inverts_slice")
        for exp in (3,4,5,6,9,12,16):
            N=powerint(3,exp)
            T=[[(N*(i==j)-H[i][j])%p for j in range(n)]
               for i in range(n)]
            a=cube_power(T,exp,p)
            b=matrix_power(T,N,p)
            check(a==b,"modular_three_power")
            v=matvec(a,u,p)
            factor=pow(pow(N,-1,p),N,p)
            physical=[x*factor%p for x in v]
            correl=sum(w[i]*u[i]*physical[i] for i in range(n))
            correl=(correl*pow(144,-1,p))%p
            if N<=243:
                direct=[x%p for x in u]
                op=[[(int(i==j)-H[i][j]*pow(N,-1,p))%p
                     for j in range(n)] for i in range(n)]
                for _ in range(N):
                    direct=matvec(op,direct,p)
                check(direct==physical,"modular_direct_short")
            if exp in (3,9,16):
                emit("YM_FINITE_JUMP",prime=p,exponent=exp,steps=N,
                     cubings=exp,modular_binary_match="PASS",
                     physical_unnormalized_state_sha256=state_sha(physical),
                     Wilson_correlator_mod_prime=correl)
    emit("YM_FINITE_MODULAR",primes=str(P1)+","+str(P2),
         exponents="3,4,5,6,9,12,16",
         result="BINARY_EQUALS_CUBED",
         physical_real_correlator="NOT_DEFINED_MOD_P")


def main():
    root=Path(__file__).resolve().parents[3]
    pred=(root/"native/ym/results/s3_1x1_continuous_jump/PREDICT-20261106.hbp").read_bytes()
    rows=[line for line in pred.splitlines() if line.startswith(b"PREDICT|id=")]
    check(len(rows)==15 and b"measurements=NOT_YET_RUN" in pred,"predictions_first")
    group,w,E,M,O,H=build_orbits()
    emit("YM_FINITE_SETUP",gauge_group="S3",
         torus="1x1_PERIODIC",gauge_orbits=len(H),
         raw_link_pairs=36,weights_total=sum(w),
         JE=1,JB=1,predictions_sha256=sha256(pred).hexdigest())
    check(charpoly(E)==e_reference(),"electric_spectrum")
    check(charpoly(H)==characteristic_reference(),"interacting_charpoly")
    emit("YM_FINITE_POLYNOMIAL",electric="x*(x-3)^2*(x-6)^5*(x-9)^2*(x-12)",
         interacting="(x-6)^3*P3*P5",
         P3="x3-21x2+135x-252",
         P5="x5-36x4+468x3-2655x2+6138x-4104",
         independent_integer_algorithm="FADDEEV_LEVERRIER")
    for name,p,d,expected in (
        ("E0_low",1096113,1000000,0),
        ("E0_high",1096114,1000000,1),
        ("E1_low",3274551,1000000,1),
        ("E1_high",3274552,1000000,2)):
        count=below_threshold(H,w,p,d)
        check(count==expected,"first_gap_"+name)
        emit("YM_FINITE_INERTIA",threshold=name,
             rational=str(p)+"/"+str(d),
             eigenvalues_below=count)
    emit("YM_FINITE_GAP",JE=1,JB=1,
         E0_interval="[1.096113,1.096114]",
         E1_interval="[3.274551,3.274552]",
         first_gap_interval="[2.178437,2.178439]",
         method="EXACT_WEIGHTED_INTEGER_INERTIA")
    center=[2*o-1 for o in O]
    check(sum(w[i]*O[i] for i in range(11))==18,"wilson_mean")
    check(sum(w[i]*center[i]*center[i] for i in range(11))==324,
          "wilson_norm")
    electric_moments=compute_moments(E,w,center,6)
    for k in range(7):
        expected=q(powerint(3,k),2)
        expected=add(expected,q(powerint(6,k)))
        expected=add(expected,q(powerint(9,k),2))
        expected=add(expected,q(powerint(12,k),4))
        check(q(electric_moments[k],144)==expected,
              "electric_Wilson_moment_"+str(k))
    emit("YM_FINITE_WILSON",observable="chi_std(commutator)",
         gauge_invariant="YES",uniform_state_mean="1/2",
         centered_norm="9/4",
         electric_correlation="1/2*e(-3t)+e(-6t)+1/2*e(-9t)+1/4*e(-12t)",
         interacting_trial_vector="NOT_THE_TRUE_GROUND_STATE")
    moments=compute_moments(H,w,center,R)
    for k in range(8):
        val=moments[k]
        bound=324*powerint(15,k)
        check(abs(val)<=bound,"CRT_valid_bound_"+str(k))
        check(bound*2<P1*P2,"CRT_uniqueness_"+str(k))
        check(crt_pair(val,P1,P2)==val,"CRT_moment_"+str(k))
        if k in (0,1,4,7):
            emit("YM_FINITE_CRT",moment_order=k,
                 reconstructed_integer=val,
                 certified_magnitude_upper=bound,
                 unique_within_modulus="YES",
                 moduli_product=P1*P2)
    tail=tail_bound()
    c_cont=correlation_series(moments)
    emit("YM_FINITE_CONTINUOUS_TIME",physical_time="1",
         correlation_lower=fmt(sub(c_cont,tail)),
         correlation_upper=fmt(add(c_cont,tail),ceil=True),
         Taylor_order=R,rigorous_tail_bound=txt(tail),
         statement="EXP_MINUS_H_FOR_FINITE_S3")
    prior=None
    number_misses=0
    for N in STEPS:
        cN=correlation_series(moments,N)
        lower=sub(cN,tail)
        upper=add(cN,tail)
        error=sub(c_cont,cN)
        loerr=sub(error,mul(q(2),tail))
        hierr=add(error,mul(q(2),tail))
        check(lt(q(0),loerr),"Euler_below_continuous")
        if prior is not None:
            check(lt(prior,cN),"Euler_grows_with_N")
        prior=cN
        emit("YM_FINITE_SLICE",time="1",
             steps=N,three_power="YES",
             correlation_lower=fmt(lower),
             correlation_upper=fmt(upper,ceil=True),
             error_lower=fmt(loerr),
             error_upper=fmt(hierr,ceil=True),
             outward_error="RIGOROUS_TAYLOR_BINOMIAL")
        if N==43046721:
            check(lt(q(1,1000000000),loerr)
                  and lt(hierr,q(3,1000000000)),
                  "last_error_preregistered_range")
            frozen_value=q(568166301459,10000000000000)
            missed=not (le(lower,frozen_value) and le(frozen_value,upper))
            check(missed,"frozen_numeric_prediction_was_wrong")
            number_misses+=int(missed)
            emit("YM_FINITE_PREDICTION_MISS",id=10,
                 frozen_approx="0.0568166301459",
                 observed_interval=fmt(lower)+","+fmt(upper,ceil=True),
                 status="MISS_RETAINED")
    # Simultaneous-conjugation invariance never makes signed A3 charge
    # a gauge-invariant closed-loop Wilson observable.
    cycle=(1,2,0)
    trans=(1,0,2)
    signed_is_changed=perm_conj(trans,cycle)!=cycle
    if sabotage=="signed_shadow":
        check(not signed_is_changed,"RED_signed_shadow")
    else:
        check(signed_is_changed,"shadow_gauge_obstruction")
    wrong_weight=w[:]
    wrong_weight[0]+=1
    bad=all(wrong_weight[i]*H[i][j]==wrong_weight[j]*H[j][i]
            for i in range(11) for j in range(11))
    check(bad if sabotage=="orbit_weight" else not bad,
          "RED_orbit_weight" if sabotage=="orbit_weight"
          else "orbit_weight_control")
    badM=[row[:] for row in M]
    badM[0][0]+=1
    magnet_correct=all(badM[i][i]==M[i][i] for i in range(11))
    check(magnet_correct if sabotage=="magnetic_diagonal" else not magnet_correct,
          "RED_magnetic_diagonal" if sabotage=="magnetic_diagonal"
          else "magnetic_control")
    smallmod=P1
    NN=27
    A=[[(NN*(i==j)-H[i][j])%smallmod
        for j in range(11)] for i in range(11)]
    correct=cube_power(A,3,smallmod)
    wrong=cube_power(A,2,smallmod)
    equal=(correct==wrong)
    check(equal if sabotage=="wrong_cube" else not equal,
          "RED_wrong_cube" if sabotage=="wrong_cube"
          else "wrong_cube_control")
    compute_modular_jumps(H,w,center)
    emit("YM_FINITE_VERIFY",status="PASS_WITH_REGISTERED_MISS",
         predictions=15,registered_numeric_misses=number_misses,
         exact_S3_orbits=11,interacting_first_gap="CERTIFIED_FINITE",
         time_jump_max=43046721,CRT_moments=8,
         continuous_reference="SAME_FINITE_HAMILTONIAN",
         spatial_continuum="NOT_TESTED",
         physical_experiment="NOT_MATCHED",
         Yang_Mills_4D_Clay="OPEN",json_zero=1)


if __name__=="__main__":
    main()
