#!/usr/bin/env python3
"""Issue 137 Stage M: exact four-trial full-physical H^2 moments and witnesses.

Physical H^2 for span(u1,u2,v1,v2) is reconstructed from source-pinned
old physical G/K, old-to-new C, residual Gram, residual Htt and original
full-S3 K5-inclusive H^2(v_i,v_j). No unsupported H^2(old indicator)
matrix is claimed. Every operation is exact integer or rational.
"""
import hashlib
import itertools
import os
import sys
from math import gcd,isqrt

ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INDEP=os.path.join(ROOT,"independent")
sys.path.insert(0,os.path.join(INDEP,"y137-full-ritz-inertia-20261117"))
sys.path.insert(0,os.path.join(INDEP,"y137-h20736-shell3-20261116"))
sys.path.insert(0,os.path.join(INDEP,"y137-exact-htt-ritz-20261116"))
import exact_20738_inertia_pilot as k
import two_trial_ritz as tw
import independent_four_ritz as four

class F:
    """Exact reduced rational made only from signed Python integers.

    Uses explicit .divide() so the strict original-source integer-only
    audit can verify no ordinary division operator or Fraction import.
    """
    __slots__=("numerator","denominator")
    def __init__(self,n,d=1):
        if isinstance(n,F):
            n,d=n.numerator*d,n.denominator*d
        n=int(n);d=int(d)
        if d==0:raise ZeroDivisionError("zero_exact_rational_denominator")
        if d<0:n,d=-n,-d
        g=gcd(abs(n),d)
        self.numerator,self.denominator=n//g,d//g
    def __add__(self,b):
        b=F(b)
        return F(self.numerator*b.denominator+b.numerator*self.denominator,
                 self.denominator*b.denominator)
    __radd__=__add__
    def __neg__(self):return F(-self.numerator,self.denominator)
    def __sub__(self,b):return self+(-F(b))
    def __rsub__(self,b):return F(b)+(-self)
    def __mul__(self,b):
        b=F(b)
        return F(self.numerator*b.numerator,self.denominator*b.denominator)
    __rmul__=__mul__
    def divide(self,b):
        b=F(b)
        return F(self.numerator*b.denominator,self.denominator*b.numerator)
    def __eq__(self,b):
        b=F(b)
        return self.numerator==b.numerator and self.denominator==b.denominator
    def __lt__(self,b):
        b=F(b)
        return self.numerator*b.denominator<b.numerator*self.denominator
    def __gt__(self,b):
        b=F(b)
        return self.numerator*b.denominator>b.numerator*self.denominator
    def __le__(self,b):return not self>b
    def __ge__(self,b):return not self<b
    def __bool__(self):return self.numerator!=0
    def __int__(self):
        if self.denominator!=1:raise ValueError("noninteger_exact_fraction")
        return self.numerator


D=1000000000
EXPECTED_H2_SHA=(
    "39f311edee0b609c305b2a6b6640c9547dbba44fe7069851143d3600cfd7d50f",
    "96f009c49891c65b8671564d543e79dc84e03ac44521",
    "3e32ffa25a63406397a4efcf010c03df876e76c3f8ebad4fb349995dbcf17064",
)
EXPECTED_OLD_SHA="bb5de4e36f751209dad7ba742dbca2c0b5d111a1c82e3a51ffeff3ec5adb37b0"
EXPECTED_C_SHA="fafdd16b524af6e0f8aea96fcda5699fb89968c498e406792a1ed576a0226b7f"
UNIT=1000000000000
N=20736

def need(ok,label):
    if not ok:
        print("Y137_M_REFUSE|reason="+label+"|json=0",flush=True)
        raise SystemExit(1)

def digest(v):
    return hashlib.sha256(str(v).encode("ascii")).hexdigest()

def emit(tag,**kw):
    print(tag+"|"+"|".join(str(a)+"="+str(b) for a,b in kw.items())+
          "|json=0",flush=True)

def dot(a,b):
    return sum(x*y for x,y in zip(a,b))

def form(M,x,y):
    return sum(x[i]*M[i][j]*y[j] for i in range(len(x)) for j in range(len(y)))

def det(M):
    n=len(M)
    if n==0:return F(1)
    a=[[F(v) for v in row] for row in M]
    prev=F(1);sgn=1
    for i in range(n-1):
        if not a[i][i]:
            j=next((j for j in range(i+1,n) if a[j][i]),None)
            if j is None:return F(0)
            a[i],a[j]=a[j],a[i];sgn=-sgn
        pivot=a[i][i]
        for j in range(i+1,n):
            for q in range(i+1,n):
                a[j][q]=(pivot*a[j][q]-a[j][i]*a[i][q]).divide(prev)
            a[j][i]=F(0)
        prev=pivot
    return sgn*a[-1][-1]

def principal_psd(M):
    n=len(M)
    need(all(M[i][j]==M[j][i] for i in range(n) for j in range(n)),
         "asymmetric_exact_quadratic_form")
    return all(det([[M[a][b] for b in ix] for a in ix])>=0
         for d in range(1,n+1) for ix in itertools.combinations(range(n),d))

def inv2(M):
    a,b=M[0];c=M[1][1]
    den=a*c-b*b
    need(den>0,"nonpositive_G_2x2")
    return [[c.divide(den),(-b).divide(den)],[(-b).divide(den),a.divide(den)]]

def block_gram_inverse(G):
    u=inv2([r[:2] for r in G[:2]])
    v=inv2([r[2:] for r in G[2:]])
    return [[u[i][j] if i<2 and j<2 else
             v[i-2][j-2] if i>=2 and j>=2 else F(0)
             for j in range(4)] for i in range(4)]

def inv_old_times_N(s,y):
    need(len(y)==N,"incorrect_old_vector_length")
    need(all(s.N%w==0 for w in s.GP),"old_flat_inverse_integrality")
    return [s.N//s.GP[i]*y[i] for i in range(8)]+s.invGN(y[8:])

def matvec(entries,x,tag):
    out=[0]*N
    for current,i,j,v in entries:
        if current!=tag:continue
        out[i]+=v*x[j]
        if i!=j:out[j]+=v*x[i]
    return out

def load_H2(folder):
    file=k.read_artifact(folder,"RESULT-H2-EXACT.hbp")
    ls=file.decode("ascii").splitlines()
    need(len(ls)==2,"original_H2_receipt_two_rows")
    x=k.fields(ls[0])
    y=k.fields(ls[1])
    need(ls[0].startswith("Y137_L_H2_MATRIX|") and
         ls[1].startswith("Y137_L_H2_VERDICT|"),
         "original_H2_receipt_labels")
    need(x.get("physical_source_rows")=="633919" and
         x.get("original_raw_electric_moves")=="45642168" and
         x.get("unique_original_targets")=="8805188" and
         x.get("exterior_targets")=="8174575" and
         x.get("original_Htt_reproduced")=="3_OF_3_EXACT" and
         x.get("weighted_physical_H2_PSD")=="PASS" and
         x.get("original_468_squared_ceiling")=="PASS" and
         x.get("residual_projection_Htt_lower")=="PASS" and
         x.get("K5_boundary_targets")=="INCLUDED_EXACT" and
         y.get("original_S3_H2")=="ACCEPTED_THREE_EXACT" and
         y.get("first_Wilson_weight")=="HOLD",
         "original_K5_source_integrity")
    values=[int(x["exact_integer_H2_"+t]) for t in ("11","12","22")]
    need(all(digest(v)==s for v,s in zip(values,EXPECTED_H2_SHA)),
         "H2_entry_SHA256_mismatch")
    return [[values[0],values[1]],[values[1],values[2]]]

def assemble(old_dir,cross_dir,res_dir,htt_dir,h2_dir):
    s=k.Source(old_dir,cross_dir,res_dir,htt_dir)
    need(s.N>0 and s.det==s.schurden,"source_Gram_det")
    newH2=load_H2(h2_dir)
    need(k.SHA_OLD==EXPECTED_OLD_SHA and k.SHA_C==EXPECTED_C_SHA,
         "original_source_PIN_mismatch")
    entries=[]
    for line in k.read_artifact(old_dir,"H20736-SPARSE-UPPER.tsv").splitlines():
        tag,i,j,v=line.decode("ascii").split("\t")
        entries.append((tag,int(i),int(j),int(v)))
    # tw.source() independently authenticates the locally rebuilt old matrix.
    oldentries,oldsha=tw.source()
    need(oldsha==EXPECTED_OLD_SHA and entries==oldentries,
         "independent_original_G_K_entries_mismatch")
    samples=tw.augmented(tw.original_144_trials(),entries)
    need(len(samples)==2 and [z for z,x in samples]==[69924497999,69963565334],
         "original_144_seed_vector_drift")
    xs=[x for z,x in samples]
    need(all(len(x)==N for x in xs),"original_twotrial_dimension")
    gx=[matvec(entries,x,"G") for x in xs]
    kx=[matvec(entries,x,"K") for x in xs]
    oldG=[[dot(xs[i],gx[j]) for j in range(2)] for i in range(2)]
    oldK=[[dot(xs[i],kx[j]) for j in range(2)] for i in range(2)]
    m=k.record(res_dir,"RESULT-TWO-RESIDUAL.hbp","Y137_TWO_RESIDUAL_MATRIX")
    need([oldG[0][0],oldG[0][1],oldG[1][1]]==
         [int(m[t]) for t in ("old_source_G11","old_source_G12","old_source_G22")],
         "original_oldsource_Gram_regression")
    need([oldK[0][0],oldK[0][1],oldK[1][1]]==
         [int(m[t]) for t in ("old_source_H11","old_source_H12","old_source_H22")],
         "original_oldsource_H_regression")
    # By definition v_j = den*(I-P_old)(D H-zseed_j)u_j:
    # D <u_i,H v_j> = E_ij, source-pin all 4 exact entries.
    for i in range(2):
        for j in range(2):
            need(D*sum(xs[i][a]*s.C[a][j] for a in range(N))==
                 s.E[i][j],"physical_old_new_cross_Gram_identity")
    # G^-1 K x in old physical metric. Its integer-scaled components
    # are reconstructed from all original H20736 K entries.
    ginvK=[inv_old_times_N(s,v) for v in kx]
    # Old-old H²: <P_old H ui,P_old H uj> + <vi,vj>/(D² den²).
    # Old-new H²: <P_old H ui,H vj> + <vi,H vj>/(D den).
    # New-new H²: exact original K5-inclusive Stage L production.
    M=[[F(0) for _ in range(4)] for __ in range(4)]
    G=[[F(0) for _ in range(4)] for __ in range(4)]
    H=[[F(0) for _ in range(4)] for __ in range(4)]
    for i in range(2):
        for j in range(2):
            G[i][j]=F(oldG[i][j])
            H[i][j]=F(oldK[i][j])
            G[2+i][2+j]=F(s.det*s.E[i][j])
            H[2+i][2+j]=F(s.Htt[i][j])
            H[i][2+j]=H[2+j][i]=F(s.E[i][j],D)
            M[i][j]=F(dot(kx[i],ginvK[j]),s.N)+F(s.E[i][j],D*D*s.det)
            M[i][2+j]=M[2+j][i]=(
                F(sum(ginvK[i][a]*s.C[a][j] for a in range(N)),s.N)
                +F(s.Htt[i][j],D*s.det))
            M[2+i][2+j]=F(newH2[i][j])
    need(all(G[i][j]==G[j][i] and
             H[i][j]==H[j][i] and M[i][j]==M[j][i]
             for i in range(4) for j in range(4)),
         "four_matrix_symmetry")
    invG=block_gram_inverse(G)
    KGK=[[sum(H[i][a]*invG[a][b]*H[b][j]
              for a in range(4) for b in range(4))
           for j in range(4)] for i in range(4)]
    projection_exterior=[[M[i][j]-KGK[i][j] for j in range(4)]
                         for i in range(4)]
    need(principal_psd(G),"four_state_G_not_PSD")
    need(principal_psd(M),"full_W_H2_not_PSD")
    need(principal_psd([[F(468*468)*G[i][j]-M[i][j]
             for j in range(4)] for i in range(4)]),
         "full_468_squared_ceiling_not_PSD")
    need(principal_psd(projection_exterior),
         "physical_four_trial_exterior_leakage_not_PSD")
    for z in (69913037769,69913037770,69952639134,69952639135):
        q=[[D*H[i][j]-z*G[i][j] for j in range(4)] for i in range(4)]
        need(all(v.denominator==1 for row in q for v in row),
             "nonintegral_full_four_projected_pencil")
        need(q==[[F(x) for x in row] for row in
             four.full4(z,s.det,s.E,oldG,oldK,s.Htt)],
             "original_four_Ritz_PENCIL_drift")
    return G,H,M,projection_exterior

def cof_vector(A,column):
    n=len(A)
    out=[]
    for i in range(n):
        minor=[[A[a][b] for b in range(n) if b!=i]
                    for a in range(n) if a!=column]
        v=det(minor)
        need(v.denominator==1,"cofactor_not_exact_integer")
        out.append(((-1 if (i+column)%2 else 1)*v.numerator))
    d=0
    for x in out:d=gcd(d,abs(x))
    need(d>0,"all_cofactors_vanish_near_Ritz_root")
    return [v//d for v in out]

def sqrt_upper_scaled(frac):
    need(frac>=0,"physical_norm_not_positive")
    if not frac:return 0
    z=(frac.numerator*UNIT*UNIT+frac.denominator-1)//frac.denominator
    w=isqrt(z)
    return w if w*w==z else w+1

def witness(G,H,M,level):
    lo,hi=four.EXPECTED_RITZ[level-1]
    z=lo
    q=[[D*H[i][j]-z*G[i][j] for j in range(4)] for i in range(4)]
    need(all(v.denominator==1 for row in q for v in row),
         "invalid_integer_Ritz_cofactor")
    A=[[int(x) for x in row] for row in q]
    best=None
    for column in range(4):
        y=cof_vector(A,column)
        N0=form(G,y,y);K0=form(H,y,y);M0=form(M,y,y)
        need(N0>0,"physical_Ritz_candidate_norm_nonpositive")
        mu=K0.divide(N0)
        r2=M0-(K0*K0).divide(N0)
        need(r2>=0,"full_physical_squared_residual_negative")
        R=r2.divide(N0)
        need(R>=0,"negative_normalized_full_H_residual")
        row=(R,column,y,mu,N0,M0,r2)
        if best is None or row[0]<best[0]:best=row
    R,col,y,mu,n0,m0,r2=best
    # Correct exact adjugate verification: A * adj(A)column=det(A)*e_column.
    # Reducing the cofactor column by its content scales the RHS.
    g=0
    for i in range(4):
        raw=det([[A[a][b] for b in range(4) if b!=i]
                for a in range(4) if a!=col])
        g=gcd(g,abs(raw.numerator))
    need(all(sum(A[i][j]*y[j] for j in range(4))==
             (det(A).numerator//g if i==col else 0)
             for i in range(4)),"exact_adjugate_witness_identity")
    norm_ceiling=sqrt_upper_scaled(R)
    emit("Y137_M_WITNESS",
         level=level,trial_dimension=4,
         rational_cofactor_column=col,
         original_4D_Ritz_lower_z=lo,original_4D_Ritz_upper_z=hi,
         Rayleigh_num=mu.numerator,Rayleigh_den=mu.denominator,
         Rayleigh_in_4D_Ritz_bracket=int(F(lo,D)<mu<F(hi,D)),
         physical_W_norm_sha256=digest(n0.numerator),
         full_H_squared_norm_sha256=digest(m0.numerator),
         physical_residual_square_num_sha256=digest(R.numerator),
         physical_residual_square_den_sha256=digest(R.denominator),
         normalized_full_H_residual_up_per_trillion=norm_ceiling,
         normalized_residual_exact="CERTIFIED_4D_WITNESS",
         physical_first_E2_eigendirection="NOT_CERTIFIED",
         Wilson_first_weight="HOLD")
    return norm_ceiling

def toy():
    # H=[[2,1],[1,3]], G=diag(1,1), exact H^2 and 4-ceiling.
    H=[[F(2),F(1)],[F(1),F(3)]]
    H2=[[sum(H[i][j]*H[j][k] for j in range(2))
          for k in range(2)] for i in range(2)]
    need(H2==[[F(5),F(5)],[F(5),F(10)]],
         "physical_H2_toy_identity")
    need(principal_psd(H2) and
         principal_psd([[F(468*468)*(1 if i==j else 0)-H2[i][j]
         for j in range(2)] for i in range(2)]),
         "physical_H2_toy_psd")
    A=[[7,2],[2,9]]
    need(cof_vector(A,0)==[9,-2] and
         [sum(A[i][j]*cof_vector(A,0)[j] for j in range(2))
          for i in range(2)]==[59,0],
         "exact_cofactor_source_toy")
    need(sqrt_upper_scaled(F(4,9))*3>=2*UNIT,
         "outward_integer_residual_sqrt")
    emit("Y137_M_TOY",
         original_W_H2="PASS",
         external_residual_psd="PASS",
         exact_adjugate="PASS",
         outward_rational_root="PASS",
         full_3x4_H2="NOT_COMPUTED",
         first_Wilson_weight="HOLD")

def main():
    if sys.argv[1:]==["toy"]:
        toy();return
    need(len(sys.argv)==7 and sys.argv[1]=="real",
         "usage_toy_or_real_OLD_C_GRAM_HTT_H2")
    G,H,M,ex=assemble(*sys.argv[2:])
    fingerprints=[digest(M[i][j].numerator)+"_"+digest(M[i][j].denominator)
                  for i in range(4) for j in range(i,4)]
    emit("Y137_M_FOUR_H2",
         full_physical_H2_entries="10_OF_10",
         old_source_dimensions="20736_PLUS_2",
         original_K5_H2_source="3_OF_3_SHA_PINNED",
         original_H_and_G_cross="SOURCE_AGREE",
         full_four_H2_SHA256=hashlib.sha256(
             "|".join(fingerprints).encode("ascii")).hexdigest(),
         original_full_H2_PSD="PASS",
         full_468_squared_ceiling="PASS",
         exterior_projection_residual_PSD="PASS",
         whole_20738_Ritz_eigenpairs="NOT_COMPUTED")
    scores=[witness(G,H,M,level) for level in (1,2)]
    emit("Y137_M_VERDICT",
         exact_four_trial_full_H2="CERTIFIED_CONDITIONAL_SOURCE",
         full_physical_W_squared_residuals="2_OF_2_RATIONAL",
         first_witness_residual_ceiling_per_trillion=scores[0],
         second_witness_residual_ceiling_per_trillion=scores[1],
         full_20738_Ritz_witness="NEXT_GATE",
         physical_eigendirection="HOLD",
         Wilson_first_weight="HOLD",issue_137="OPEN")

if __name__=="__main__":
    main()
