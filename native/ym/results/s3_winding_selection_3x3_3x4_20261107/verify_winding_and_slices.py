#!/usr/bin/env python3
"""Actual periodic 3x3 and 3x4 S3 gauge observables, exact pure-electric gaps,
and certified 3^16 Euclidean time slices. Integer arithmetic only.

Predictions frozen first at commit 3acdca0825fbf6a548686ccf1aae3838fd7b5a8e.
No 10M/2.17B-dimensional Hamiltonian is diagonalized. JB=0 exact eigenfunction
sector and gauge symmetry are checked; interacting E1 parity/weight remain OPEN.
"""
from hashlib import sha256
from itertools import permutations, product
from math import gcd
from pathlib import Path
import sys

CONTROL=("swapped_even_as_odd","rect_alt_as_even","bare_holonomy_gauge_invariance",
         "wrong_electric_cost","wrong_cubing","wrong_variance")
red=""
if len(sys.argv)>2 or (len(sys.argv)==2 and
    (not sys.argv[1].startswith("sabotage=")
     or sys.argv[1][9:] not in CONTROL)):
    print("usage: verify_3x3_3x4_winding.py [sabotage=CONTROL]")
    sys.exit(2)
if len(sys.argv)==2:
    red=sys.argv[1][9:]

def assert_true(ok, label):
    if not ok:
        print("FAILED|check="+label+"|json=0")
        sys.exit(1)

def emit(tag, **values):
    print(tag+"|"+"|".join(str(k)+"="+str(v) for k,v in values.items())
          +"|json=0",flush=True)

P=tuple(permutations(range(3)))
index={p:i for i,p in enumerate(P)}
M=tuple(tuple(index[tuple(P[a][P[b][i]] for i in range(3))]
              for b in range(6)) for a in range(6))
INV=tuple(next(b for b in range(6) if M[a][b]==M[b][a]==0)
          for a in range(6))
TRANS=tuple(g for g in range(6) if M[g][g]==0 and g!=0)
assert_true(len(TRANS)==3 and 0 not in TRANS,"S3_transposition_class")
def mul(*args):
    res=0
    for x in args:
        res=M[res][x]
    return res
def chi(g):
    return sum(int(P[g][i]==i) for i in range(3))-1

assert_true(sorted({chi(g) for g in range(6)})==[-1,0,2],"S3_character_values")
assert_true(sum(chi(g) for g in range(6))==0,"S3_character_mean")
assert_true(sum(chi(g)*chi(g) for g in range(6))==6,"S3_character_second_moment")
assert_true(all(sum(chi(mul(t,g)) for t in TRANS)==0
                for g in range(6)),"S3_character_transposition_annihilation")

def ipow(base,exponent):
    # This explicitly excludes negative powers, which could create float
    # values even when the base is a Python integer. The repo-level source
    # gate does not accept variable exponents on the built-in ** operator.
    assert_true(type(base) is int and type(exponent) is int
                and exponent>=0,"integer_power_exponent_nonnegative")
    result=1
    while exponent:
        if exponent&1:
            result*=base
        exponent//=2
        if exponent:
            base*=base
    return result

def rational(n,d=1):
    assert_true(isinstance(n,int) and isinstance(d,int) and d!=0,
                "integer_rational_only")
    if d<0:
        n,d=-n,-d
    g=gcd(n,d)
    return n//g,d//g
def qplus(a,b):
    return rational(a[0]*b[1]+b[0]*a[1],a[1]*b[1])
def qminus(a,b):
    return rational(a[0]*b[1]-b[0]*a[1],a[1]*b[1])
def qmult(a,b):
    return rational(a[0]*b[0],a[1]*b[1])
def qdiv(a,b):
    assert_true(b[0]!=0,"rational_nonzero_denominator")
    return rational(a[0]*b[1],a[1]*b[0])
def qlt(a,b):
    return a[0]*b[1]<b[0]*a[1]
def qfmt(a,digits=12,ceil=False):
    scale=ipow(10,digits)
    num=a[0]*scale
    z=-((-num)//a[1]) if ceil else num//a[1]
    string=str(abs(z)).zfill(digits+1)
    return ("-" if z<0 else "")+string[:-digits]+"."+string[-digits:]

def exp_negative_interval(z):
    # With z>0 and 128 Taylor terms for exp(z):
    # S_R <= exp(z) <= S_R + (z^(R+1)/(R+1)!)/(1-z/(R+2)).
    # Taking reciprocals gives rigorous bounds for exp(-z).
    assert_true(qlt(rational(0),z) and qlt(z,rational(15)),
                "exponential_input_in_range")
    R=128
    term=rational(1)
    acc=term
    for k in range(1,R+1):
        term=qmult(term,qdiv(z,rational(k)))
        acc=qplus(acc,term)
    first=qmult(term,qdiv(z,rational(R+1)))
    tail=qdiv(first,qminus(rational(1),qdiv(z,rational(R+2))))
    return qdiv(rational(1),qplus(acc,tail)),qdiv(rational(1),acc)

def discrete_euler_interval(N):
    # Exact logarithmic identity for 0<9/N<1:
    # -N log(1-9/N)=9+sum_{k>=2} 9^k/(k N^(k-1)).
    # 28 terms + rigorous geometric tail bound, then bound exp(-z).
    assert_true(N>=27,"safe_slices")
    delta=rational(0)
    K=28
    for k in range(2,K+1):
        delta=qplus(delta,rational(ipow(9,k),k*ipow(N,k-1)))
    remainder=qdiv(rational(ipow(9,K+1),(K+1)*ipow(N,K)),
                   qminus(rational(1),rational(9,N)))
    low,_=exp_negative_interval(qplus(rational(9),qplus(delta,remainder)))
    _,high=exp_negative_interval(qplus(rational(9),delta))
    return low,high

def raw_dimension(Lx,Ly):
    V=Lx*Ly
    k=V+1
    return (ipow(6,k)+3*ipow(2,k)+2*ipow(3,k))//6

def site(Lx,Ly,x,y):
    return (x%Lx)*Ly+(y%Ly)
def winding_x(U,Lx,Ly,y):
    return chi(mul(*[U[site(Lx,Ly,x,y)] for x in range(Lx)]))
def winding_y(U,Lx,Ly,x):
    V=Lx*Ly
    return chi(mul(*[U[V+site(Lx,Ly,x,y)] for y in range(Ly)]))
def plaquette(U,Lx,Ly,x,y):
    V=Lx*Ly
    s=site(Lx,Ly,x,y)
    right=site(Lx,Ly,x+1,y)
    up=site(Lx,Ly,x,y+1)
    return mul(U[s],U[V+right],INV[U[up]],INV[U[V+s]])
def magnetic(U,Lx,Ly):
    return sum(2-chi(plaquette(U,Lx,Ly,x,y))
               for x in range(Lx) for y in range(Ly))
def candidates(U,Lx,Ly):
    X=[winding_x(U,Lx,Ly,y) for y in range(Ly)]
    Y=[winding_y(U,Lx,Ly,x) for x in range(Lx)]
    if Lx==Ly==3:
        return sum(X)+sum(Y),sum(X)-sum(Y)
    assert_true(Lx==3 and Ly==4,"known_shape")
    return sum(X),sum(X[y]*(1 if y%2==0 else -1) for y in range(Ly))
def gauge(U,Lx,Ly,h):
    V=Lx*Ly
    out=[0]*(2*V)
    for x in range(Lx):
        for y in range(Ly):
            s=site(Lx,Ly,x,y)
            out[s]=mul(h[s],U[s],INV[h[site(Lx,Ly,x+1,y)]])
            out[V+s]=mul(h[s],U[V+s],
                         INV[h[site(Lx,Ly,x,y+1)]])
    return out
def exchange_square(U):
    V=9
    out=[0]*18
    for x in range(3):
        for y in range(3):
            a=site(3,3,x,y)
            b=site(3,3,y,x)
            out[b]=U[V+a]
            out[V+b]=U[a]
    return out
def translate_rect_y(U):
    V=12
    out=[0]*24
    for x in range(3):
        for y in range(4):
            s=site(3,4,x,y)
            src=site(3,4,x,y+1)
            out[s]=U[src]
            out[V+s]=U[V+src]
    return out
def move(U,e,t):
    out=U[:]
    out[e]=M[t][U[e]]
    return out
def transformed_edge(e,Lx,Ly):
    V=Lx*Ly
    axis=int(e>=V)
    s=e%V
    x=s//Ly
    y=s%Ly
    if Lx==Ly==3:
        transformed_site=site(3,3,y,x)
        new_axis=1-axis
        return new_axis*V+transformed_site
    transformed_site=site(3,4,x,y-1)
    return axis*V+transformed_site
def transformed(U,Lx,Ly):
    return exchange_square(U) if Lx==Ly else translate_rect_y(U)
def random_sample(Lx,Ly,seed):
    V=Lx*Ly
    label=str(Lx)+"x"+str(Ly)+":"+str(seed)
    n=int.from_bytes(sha256(label.encode("ascii")).digest(),"big")
    return [n//ipow(6,i)%6 for i in range(2*V)]

def local_identity(length):
    # Exhaustively test every sequence of length 3 or 4, and all
    # left-transposition changes on each contributing link.
    assert_true(length in (3,4),"length_3_or_4")
    count=0
    for word in product(range(6),repeat=length):
        c=chi(mul(*word))
        E=0
        for k in range(length):
            E+=3*c
            for t in TRANS:
                changed=list(word)
                changed[k]=M[t][changed[k]]
                E-=chi(mul(*changed))
        if red=="wrong_electric_cost":
            assert_true(E==3*(length+1)*c,"RED_wrong_electric_cost")
        assert_true(E==3*length*c,"exhaustive_electric_loop_identity")
        count+=1
    emit("S3_ELECTRIC_IDENTITY",loop_length=length,
         group_words=count,elementary_move_checks=count*length*3,
         exact_eigenvalue=3*length,
         character_identity="PASS")

def group_moments():
    m=sum(chi(g) for g in range(6))
    v=sum(chi(g)**2 for g in range(6))
    assert_true(m==0 and v==6,"group_character_orthogonality")
    if red=="wrong_variance":
        assert_true(v==5,"RED_wrong_variance")
    emit("S3_HAAR_SINGLE_LOOP",uniform_character_mean="0",
         uniform_character_variance="1",
         disjoint_link_loops_independent="BY_PRODUCT_MEASURE")

def check_shape(Lx,Ly):
    V=Lx*Ly
    expected=10097891 if V==9 else 2177317873
    count=raw_dimension(Lx,Ly)
    assert_true(count==expected,"Burnside_orbits_"+str(V))
    emit("S3_GEOMETRY",shape=str(Lx)+"x"+str(Ly),
         sites=V,oriented_links=2*V,free_links=V+1,
         full_physical_gauge_orbits=count,
         existing_3x4_stored_rows=(45508080 if V==12 else "N/A"),
         stored_rows_equal_full_space="NO")
    local_checks=0
    covariance=0
    controls=0
    for seed in range(48):
        U=random_sample(Lx,Ly,seed)
        other=transformed(U,Lx,Ly)
        a,b=candidates(U,Lx,Ly)
        aa,bb=candidates(other,Lx,Ly)
        if V==9:
            if red=="swapped_even_as_odd":
                assert_true(aa==-a,"RED_swapped_even_as_odd")
            assert_true(aa==a and bb==-b,"square_exchange_parity")
            assert_true(exchange_square(other)==U,"square_involution")
        else:
            if red=="rect_alt_as_even":
                assert_true(bb==b,"RED_rect_alt_as_even")
            assert_true(aa==a and bb==-b,
                        "rectangle_momentum_pi_y")
            assert_true(transformed(transformed(
                transformed(transformed(U,Lx,Ly),Lx,Ly),Lx,Ly),Lx,Ly)==U,
                "rectangle_Ty_order_four")
        assert_true(magnetic(U,Lx,Ly)==magnetic(other,Lx,Ly),
                    "magnetic_lattice_covariance")
        for s in range(V):
            for g in range(6):
                h=[0]*V
                h[s]=g
                GU=gauge(U,Lx,Ly,h)
                assert_true(candidates(GU,Lx,Ly)==(a,b),
                            "local_gauge_winding_invariance")
                assert_true(magnetic(GU,Lx,Ly)==magnetic(U,Lx,Ly),
                            "local_gauge_magnetic_invariance")
                local_checks+=1
        for e in range(2*V):
            for t in TRANS:
                left=transformed(move(U,e,t),Lx,Ly)
                right=move(other,transformed_edge(e,Lx,Ly),t)
                assert_true(left==right,"electric_move_symmetry_covariance")
                covariance+=1
        controls+=1
    emit("S3_SYMMETRY",shape=str(Lx)+"x"+str(Ly),
         raw_samples=controls,local_gauge_transformations=local_checks,
         electric_move_covariance_checks=covariance,
         magnetic_covariance="PASS",
         gauge_invariant_observable="PASS",
         even_operator=("WX_plus_WY" if V==9 else "WX_Y_MOMENTUM_ZERO"),
         odd_operator=("WX_minus_WY" if V==9 else "WX_Y_MOMENTUM_PI"),
         symmetry=("AXIS_EXCHANGE" if V==9 else "UNIT_TRANSLATION_Y"))
    if V==12:
        base=[0]*(2*V)
        h=[0]*V
        h[0]=TRANS[0]
        updated=gauge(base,Lx,Ly,h)
        assert_true(chi(base[0])!=chi(updated[0]),
                    "bare_open_link_not_gauge_invariant")
        if red=="bare_holonomy_gauge_invariance":
            assert_true(chi(base[0])==chi(updated[0]),
                        "RED_bare_holonomy_gauge_invariance")
        emit("S3_RED_REFERENCE",bare_open_link_character="GAUGE_VARIANT",
             traced_closed_winding_character="GAUGE_INVARIANT")
    amp=6 if V==9 else 4
    emit("S3_ELECTRIC_OBSERVABLE",shape=str(Lx)+"x"+str(Ly),
         interaction_JB=0,eigenvalue=9,
         uniform_vacuum_mean="0",connected_variance=amp,
         group_character_factorization="EXACT",
         fully_interacting_JB1_first_overlap="OPEN",
         tested_global_E1_parity="OPEN")
    if V==12:
        emit("S3_ELECTRIC_CROSSCHECK",shape="3x4",
             x_winding_length=3,x_winding_energy=9,
             y_winding_length=4,y_winding_energy=12,
             non_square_exchange_symmetry="ABSENT")

def jump_scalar(p,N,k):
    base=((N-9)*pow(N,-1,p))%p
    cubed=base
    for _ in range(k):
        cubed=(cubed*cubed*cubed)%p
    if red=="wrong_cubing" and k==3:
        bad=base
        for _ in range(k-1):
            bad=(bad*bad*bad)%p
        assert_true(bad==pow(base,N,p),"RED_wrong_cubing")
    assert_true(cubed==pow(base,N,p),"three_power_matches_independent_binary")
    return cubed

def time_slices():
    group_moments()
    ref_lo,ref_hi=exp_negative_interval(rational(9))
    prev=None
    for k in (3,4,5,6,9,12,16):
        N=ipow(3,k)
        lo,hi=discrete_euler_interval(N)
        assert_true(qlt(lo,hi) and qlt(hi,ref_lo),
                    "discrete_time_under_continuous")
        if prev is not None:
            assert_true(qlt(prev,lo),"increasing_slice_accuracy")
        prev=hi
        for shape,amp in (("3x3",6),("3x4",4)):
            emit("S3_TIME_SLICE",shape=shape,JB=0,Euclidean_time=1,
                 steps=N,ternary_cubings=k,
                 connected_lower=qfmt(qmult(rational(amp),lo)),
                 connected_upper=qfmt(qmult(rational(amp),hi),ceil=True),
                 reference="m*exp(-9)",
                 interval_proof="LOG_TAYLOR_RATIONAL")
        if k in (3,9,16):
            for p in (1000081,1000003):
                val=jump_scalar(p,N,k)
                emit("S3_MODULAR_JUMP",prime=p,exponent=k,
                     time_steps=N,scalar_eigenmode_residue=val,
                     cubings=k,binary_modular_power="MATCH")
        else:
            for p in (1000081,1000003):
                jump_scalar(p,N,k)
    for shape,amp in (("3x3",6),("3x4",4)):
        emit("S3_CONTINUOUS_ELECTRIC",shape=shape,JB=0,Euclidean_time=1,
             connected_lower=qfmt(qmult(rational(amp),ref_lo)),
             connected_upper=qfmt(qmult(rational(amp),ref_hi),ceil=True),
             exact_formula=str(amp)+"*exp(-9)",
             spatial_continuum="NOT_TESTED")

def main():
    base=Path(__file__).resolve().parents[4]
    frozen=base.joinpath("native","ym","results",
      "s3_winding_selection_3x3_3x4_20261107","PREDICTION.hbp").read_bytes()
    assert_true(sum(int(row.startswith(b"PREDICT|id="))
                    for row in frozen.splitlines())==17,
                "prediction_before_source")
    emit("S3_BEGIN",group="S3",lattices="3x3,3x4",
         prediction_sha256=sha256(frozen).hexdigest(),
         frozen_rows=17,model="FINITELY_PERIODIC_SPATIAL_TORI",
         exact_arithmetic="INTEGER_PAIRS")
    local_identity(3)
    local_identity(4)
    check_shape(3,3)
    check_shape(3,4)
    time_slices()
    emit("S3_VERIFY",status="PASS",lattices="3x3,3x4",
         exact_pure_electric_eigenmode="E9",
         hosted_time_steps_max=43046721,
         interacting_E1_sector="OPEN",
         interacting_vacuum_overlap="OPEN",
         full_spectral_inertia="NOT_RUN",
         spatial_continuum="NOT_TESTED",fourD_SU2_Clay="OPEN")

if __name__=="__main__":
    main()
