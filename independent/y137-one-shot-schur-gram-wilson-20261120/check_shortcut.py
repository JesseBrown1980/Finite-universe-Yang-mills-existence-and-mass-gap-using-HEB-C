#!/usr/bin/env python3
"""Independent exact-rational Schur-Gram / Wilson centering / ternary error test.

Proof-only toy and certified norm envelope; original 3x4 Q polynomial action
and original Q-dual source authentication are separate production obligations.
Do not import producing modules or infer an unconditional Wilson result.
"""
from math import gcd, isqrt

class F:
    """Exact reduced rational implemented with integer arithmetic only."""
    __slots__ = ("n", "d")
    def __init__(self,n,d=1):
        if isinstance(n,F):
            self.n,self.d=n.n,n.d
            return
        n,d=int(n),int(d)
        if d==0: raise ZeroDivisionError("zero_rational_denominator")
        if d<0: n,d=-n,-d
        k=gcd(abs(n),d)
        self.n,self.d=n//k,d//k
    def _coerce(self,other):
        return other if isinstance(other,F) else F(other)
    def __add__(self,b):
        b=self._coerce(b)
        return F(self.n*b.d+b.n*self.d,self.d*b.d)
    def __radd__(self,b): return self.__add__(b)
    def __neg__(self): return F(-self.n,self.d)
    def __sub__(self,b): return self+self._coerce(b).__neg__()
    def __rsub__(self,b): return self._coerce(b)+(-self)
    def __mul__(self,b):
        b=self._coerce(b)
        return F(self.n*b.n,self.d*b.d)
    def __rmul__(self,b): return self.__mul__(b)
    def div(self,b):
        b=self._coerce(b)
        return F(self.n*b.d,self.d*b.n)
    def __pow__(self,n):
        if not isinstance(n,int) or n<0: raise ValueError("positive_int_exponent_only")
        return F(pow(self.n,n),pow(self.d,n))
    def _comp(self,b):
        b=self._coerce(b)
        return self.n*b.d-b.n*self.d
    def __eq__(self,b):
        try:return self._comp(b)==0
        except (TypeError,ValueError):return False
    def __lt__(self,b):return self._comp(b)<0
    def __le__(self,b):return self._comp(b)<=0
    def __gt__(self,b):return self._comp(b)>0
    def __ge__(self,b):return self._comp(b)>=0
    def __bool__(self):return self.n!=0
    def __repr__(self):return "F("+str(self.n)+","+str(self.d)+")"


S=10**12
GAMMA=F(94068200,10**6)
EHI=(F(69909586556,10**9), F(69949433884,10**9))
MARGIN=F(9285530088,S)

def need(condition,reason):
    if not condition: raise ValueError(reason)

def mm(a,b):
    return [[sum((a[i][k]*b[k][j] for k in range(len(b))),F(0))
             for j in range(len(b[0]))] for i in range(len(a))]

def t(a):return [list(v) for v in zip(*a)]
def D(v):return [[F(x) if i==j else F(0) for j in range(len(v))]
                for i,x in enumerate(v)]
def op(a,b,sign=1):
    return [[x+sign*y for x,y in zip(u,v)] for u,v in zip(a,b)]
def mul(a,x):return [[x*v for v in row] for row in a]
def col(a,i):return [row[i] for row in a]
def dot(u,v):return sum((x*y for x,y in zip(u,v)),F(0))

def toy():
    # Rational orthogonal similarity gives EXACT known E1=1, E2=2 and Q mass.
    r12=[[F(3,5),F(-4,5),F(0)],[F(4,5),F(3,5),F(0)],[F(0),F(0),F(1)]]
    r23=[[F(1),F(0),F(0)],[F(0),F(5,13),F(-12,13)],
         [F(0),F(12,13),F(5,13)]]
    V=mm(r23,r12)
    need(mm(t(V),V)==D((1,1,1)),"orthogonal_true_basis")
    H=mm(mm(V,D((1,2,9))),t(V))
    A=[row[:2] for row in H[:2]]
    B=[H[2][:2]]
    d=H[2][2]
    need(d>2 and all(B[0]),"nontrivial_two_energy_Q_mass")
    R1,R2=F(1).div(d-1),F(1).div(d-2)
    def schur(e):
        return op(op(A,mul(D((1,1)),e),-1),mul(mm(t(B),B),F(1).div(d-e)),-1)
    s1,s2=schur(F(1)),schur(F(2))
    cross=op(D((1,1)),mul(mm(t(B),B),R1*R2))
    need(cross==op(s1,s2,-1),"Schur_divided_difference_full_Gram")
    O9=D((12,-16,-30))
    O7=D((21,-7,-21))
    def meff(o):
        return op(D((o[0][0],o[1][1])),mul(mm(t(B),B),R1*R2*o[2][2]))
    m9,m7=meff(O9),meff(O7)
    need(m7==op(m9,mul(cross,F(9))),"full_Wilson_Gram_shift")
    v1,v2=col(V,0),col(V,1)
    p1,p2=v1[:2],v2[:2]
    need(mm(s1,[[x] for x in p1])==[[0],[0]] and
         mm(s2,[[x] for x in p2])==[[0],[0]],"actual_Schur_eigendirections")
    need(dot(p2,col(mm(cross,[[x] for x in p1]),0))==0,
         "true_Gram_orthogonality")
    true1=dot(p2,col(mm(m9,[[x] for x in p1]),0))
    true2=dot(p2,col(mm(m7,[[x] for x in p1]),0))
    need(true1==true2!=0 and
         true1==dot(v2,col(mm(O9,[[x] for x in v1]),0)),
         "full_and_Schur_Wilson_true_transition")
    p=[F(1),F(1)];q=[F(2),F(-1)]
    mix=dot(q,col(mm(cross,[[x] for x in p]),0))
    difference=dot(q,col(mm(m7,[[x] for x in p]),0))-dot(q,col(mm(m9,[[x] for x in p]),0))
    need(mix!=0 and difference==9*mix,"nonorthogonal_fixed_trial_shift_must_stay")

def sqrt_lower(x):
    return F(isqrt(x.n*S*S//x.d),S)
def sqrt_upper(x):
    j=isqrt(x.n*S*S//x.d)
    if F(j*j,S*S)<x:j+=1
    return F(j,S)
def budget(n,cap,method):
    g=[GAMMA-e for e in EHI];h=[F(468)-e for e in EHI]
    if method=="cheb":
        rate=[(sqrt_upper(b)-sqrt_lower(a)).div(sqrt_upper(b)+sqrt_lower(a))
              for a,b in zip(g,h)]
        eps=[(2*r**n).div(a) for r,a in zip(rate,g)]
    else:
        rate=[(b-a).div(b+a) for a,b in zip(g,h)]
        eps=[(r**n).div(a) for r,a in zip(rate,g)]
    need(all(0<r<1 for r in rate),"contractive_spectral_envelope")
    return 72*cap*(eps[1].div(g[0])+eps[0].div(g[1])+eps[0]*eps[1])
def ceil_ppt(x):
    return (x.n*S+x.d-1)//x.d
def ternary(k):
    p=[1]
    for j in range(k):
        d=3**j
        factor=[0]*(2*d+1);factor[0]=factor[d]=factor[2*d]=1
        nxt=[0]*(len(p)+len(factor)-1)
        for a,x in enumerate(p):
            for b,y in enumerate(factor):nxt[a+b]+=x*y
        p=nxt
    need(p==[1]*(3**k),"ternary_3power_Geometric_resolvent_identity")
def main():
    original=(14,8,5,6,0,2,-7,-7)
    need(max(abs(2*x-16) for x in original)==30 and
         max(abs(2*x-7) for x in original)==21,
         "original_integer_minimax_shift")
    need(62163774481-25196361952-27389725641-292156800==9285530088,
         "original_source_conditional_signed_margin")
    toy();ternary(4)
    vals=(budget(14,30,"cheb"),budget(14,21,"cheb"),
          budget(15,30,"cheb"),budget(18,30,"cheb"),
          budget(27,30,"cheb"),budget(81,30,"geo"))
    need(vals[0]>MARGIN and vals[1]<MARGIN and vals[2]<MARGIN and
         vals[3]<MARGIN.div(2) and vals[4]<MARGIN.div(400) and vals[5]<MARGIN.div(20),
         "independent_rational_Wilson_filter_enclosure")
    print("Y137_SCHUR_GRAM_CENTER_JUMP|math=PASS|true_eigendirection=PASS"+
          "|frozen_trial_shift_control=PASS|old_O9_norm=30|new_O7_norm=21"+
          "|ternary_3power_identity=PASS|original_full_Q_polynomial=NOT_RUN"+
          "|original_Wilson=FORMAL_HOLD|continuum_4D=OPEN|json=0")
    print("Y137_SCHUR_SHORTCUT_BOUNDS|source_conditional_margin_ppt=9285530088"+
          "|cheb14_old_ppt="+str(ceil_ppt(vals[0]))+
          "|cheb14_new_ppt="+str(ceil_ppt(vals[1]))+
          "|cheb15_old_ppt="+str(ceil_ppt(vals[2]))+
          "|cheb18_old_ppt="+str(ceil_ppt(vals[3]))+
          "|cheb27_old_ppt="+str(ceil_ppt(vals[4]))+
          "|geo81_old_ppt="+str(ceil_ppt(vals[5]))+
          "|source_authentication=SEPARATE|json=0")
if __name__=="__main__":main()
