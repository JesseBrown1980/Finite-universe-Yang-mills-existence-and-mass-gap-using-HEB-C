#!/usr/bin/env python3
"""Issue 137: source-pinned exact, interval-certified full 20,738 inertia pilot.

Eliminate the 20,728-dimensional old nonflat Q block *with verified error*.
The remaining 10x10 Schur interval includes 8 flat axes and both full
residual directions. No floating point, no dense 20,738x20,738 matrix.

The Q block is positive for z below the accepted whole-Q floor. A Chebyshev
polynomial inverse supplies an integer trial solution X and integer residual R.
The exact inverse quadratic form is between
  F0=2*B^T X-X^T A X  and F0+R^T G_Q^-1 R/a,
where A=D K_QQ-z G_QQ >= a G_QQ. Therefore both 10x10 Schur bounds are
rigorous. Equal integer inertia of the two Schur bounds certifies the full
20,738-dimensional negative inertia at z/D, without numerical eigenvalues.

All source artifacts are immutable original GitHub Actions production ZIPs.
"""
import sys, zipfile, hashlib, itertools, time, os
sys.set_int_max_str_digits(0)
NOLD=20736
NQ=NOLD-8
D=1000000000
CAPD=468*D
FLOORD=94068200000
NTRIAL=10
SHA_OLD='bb5de4e36f751209dad7ba742dbca2c0b5d111a1c82e3a51ffeff3ec5adb37b0'
SHA_C='fafdd16b524af6e0f8aea96fcda5699fb89968c498e406792a1ed576a0226b7f'
SHA_RES='8bac7d83154d9fc6ed5b92b62fd127362dc30b9163c9ce9eeeefdf5bcd46748f'
SHA_HTT='afb43ddde0bea1e70c7e1da7b8120f4878d847ecc52a472429a0ba5499de2752'

def need(x,why):
    if not x:raise AssertionError(why)
def fields(line):
    out={}
    for p in line.strip().split('|')[1:]:
        if '=' in p:
            a,b=p.split('=',1);need(a not in out,'duplicate field');out[a]=b
    return out
def read_artifact(path,filename):
    if os.path.isdir(path):
        with open(os.path.join(path,filename),'rb') as f:return f.read()
    with zipfile.ZipFile(path) as z:return z.read(filename)

def record(zip_path,filename,tag):
    rows=read_artifact(zip_path,filename).decode('ascii').splitlines()
    items=[fields(s) for s in rows if s.startswith(tag+'|')]
    need(len(items)==1,'missing or duplicate '+tag)
    return items[0]
def sha(data):return hashlib.sha256(data).hexdigest()
def det_perm(M):
    size=len(M);acc=0
    for p in itertools.permutations(range(size)):
        sign=-1 if sum(p[i]>p[j] for i in range(size) for j in range(i+1,size))%2 else 1
        v=sign
        for i in range(size):v*=M[i][p[i]]
        acc+=v
    return acc
def adj4(M):
    a=[]
    for i in range(4):
        a.append([((-1 if (i+j)%2 else 1)*det_perm([[M[r][c] for c in range(4) if c!=i] for r in range(4) if r!=j])) for j in range(4)])
    return a

def bareiss_det(M):
    n=len(M)
    if n==0:return 1
    a=[r[:] for r in M];den=1;sgn=1
    for k in range(n-1):
        if a[k][k]==0:
            pivot=next((p for p in range(k+1,n) if a[p][k]),None)
            if pivot is None:return 0
            a[k],a[pivot]=a[pivot],a[k];sgn=-sgn
        x=a[k][k]
        for i in range(k+1,n):
            y=a[i][k]
            for j in range(k+1,n):
                val=a[i][j]*x-y*a[k][j]
                need(val%den==0,'bareiss exact division')
                a[i][j]=val//den
            a[i][k]=0
        den=x
    return sgn*a[-1][-1]

def inertia(M):
    # Independent exact Sylvester leading-minor sign-variation test.
    signs=[1];n=len(M)
    for i in range(1,n+1):
        a=bareiss_det([r[:i] for r in M[:i]])
        if not a:return None
        signs.append(1 if a>0 else -1)
    return sum(signs[i]!=signs[i+1] for i in range(n))

class Source:
    def __init__(self,old_zip,cross_zip,residual_zip,htt_zip):
        old=read_artifact(old_zip,'H20736-SPARSE-UPPER.tsv')
        need(sha(old)==SHA_OLD,'original sparse source SHA drift')
        cross=read_artifact(cross_zip,'H20736x2-CROSS-EXACT.tsv')
        need(sha(cross)==SHA_C,'original cross matrix SHA drift')
        self.C=[]
        for idx,line in enumerate(cross.splitlines()):
            i,u,v=map(int,line.split(b'\t'));need(i==idx,'C index drift');self.C.append((u,v))
        need(len(self.C)==NOLD,'C dimension drift')
        need(sha(read_artifact(residual_zip,'RESULT-TWO-RESIDUAL.hbp'))==SHA_RES,'original residual receipt SHA')
        need(sha(read_artifact(htt_zip,'RESULT-HTT-EXACT.hbp'))==SHA_HTT,'original Htt receipt SHA')
        m=record(residual_zip,'RESULT-TWO-RESIDUAL.hbp','Y137_TWO_RESIDUAL_MATRIX')
        h=record(htt_zip,'RESULT-HTT-EXACT.hbp','Y137_HTT_FULL_MATRIX')
        self.schurden=int(m['old_Gram_det_den'])
        self.E=[[int(m['E11_num']),int(m['E12_num'])],[int(m['E12_num']),int(m['E22_num'])]]
        self.Htt=[[int(h['K11']),int(h['K12'])],[int(h['K12']),int(h['K22'])]]
        need(h['common_projected_H_den']==str(self.schurden*self.schurden),'Htt scaling')
        self.W=[0]*NQ;self.Gcore=[[0]*4 for _ in range(4)];self.X=[[0]*132 for _ in range(4)]
        self.Gentries=[];self.Kentries=[]
        self.GP=[0]*8
        self.TG=[[0]*10 for _ in range(10)]
        self.TK=[[0]*10 for _ in range(10)]
        self.B=[[0]*10 for _ in range(NQ)]
        # Symmetric upper-triangle physical source, with T=(P8,V2), Q=(old coordinates 8..20735).
        for line in old.splitlines():
            tag,ii,jj,x=line.split(b'\t');i=int(ii);j=int(jj);v=int(x);need(i<=j,'not upper')
            if tag==b'G':
                if i<8:
                    need(i==j,'G_PQ=0 violated');self.TG[i][i]=v;self.GP[i]=v
                else:
                    a=i-8;b=j-8
                    self.Gentries.append((a,b,v))
                    if a==b and not 0<=a<4:self.W[a]=v
                    elif 0<=a<4 and 0<=b<4:self.Gcore[a][b]=self.Gcore[b][a]=v
                    elif 0<=a<4 and 4<=b<136:self.X[a][b-4]=v
                    else:need(False,'unsupported old Gram sparsity')
            elif tag==b'K':
                if j<8:
                    self.TK[i][j]=self.TK[j][i]=v
                elif i<8:
                    self.B[j-8][i]=D*v
                else:self.Kentries.append((i-8,j-8,v))
            else:need(False,'invalid source tag')
        need(all(self.GP),'eight physical flat weights')
        for i in range(8):
            for j in range(2):self.TK[i][8+j]=self.TK[8+j][i]=self.C[i][j]
        for i in range(2):
            for j in range(2):
                self.TK[8+i][8+j]=self.Htt[i][j]
                self.TG[8+i][8+j]=self.schurden*self.E[i][j]
        for i in range(NQ):
            for j in range(2):self.B[i][8+j]=D*self.C[8+i][j]
        need(all(self.W[i]>0 for i in range(4,NQ)),'Q coordinate weights')
        self.S=[r[:] for r in self.Gcore]
        for a in range(4):
            for b in range(4):
                t=0
                for i in range(132):
                    w=self.W[i+4];need(self.X[b][i]%w==0,'old Gram divisibility')
                    t+=self.X[a][i]*(self.X[b][i]//w)
                self.S[a][b]-=t
        self.det=det_perm(self.S)
        need(self.det==self.schurden and self.det>0,'Q Gram source mismatch')
        need(all(det_perm([r[:i] for r in self.S[:i]])>0 for i in range(1,5)),'old Q Schur Gram not strictly PD')
        self.adj=adj4(self.S)
        need(all(sum(self.S[i][k]*self.adj[k][j] for k in range(4))==(self.det if i==j else 0) for i in range(4) for j in range(4)),'inverse 4x4 identity')
        self.N=6*self.det
        need(self.TG[8][8]>0 and self.TG[8][8]*self.TG[9][9]>self.TG[8][9]**2,'two residual metric')
        need(self.Htt[0][0]>=0 and self.Htt[0][0]*self.Htt[1][1]>=self.Htt[0][1]**2,'Htt PSD')
        hcap=[[468*self.TG[8+i][8+j]-self.Htt[i][j] for j in range(2)] for i in range(2)]
        need(hcap[0][0]>=0 and hcap[0][0]*hcap[1][1]>=hcap[0][1]**2,'Htt ceiling')
        for k in range(8):need(self.TK[k][k]==72*self.TG[k][k],'flat physical 72 diagonal')
        need(len(self.Kentries)>0 and self.Gentries,'missing nonflat blocks')
        # Validate the integer inverse representation independently of its 4x4 construction.
        y=[0]*NQ
        for k,val in ((0,7),(3,-13),(4,5),(12,-9),(135,3),(136,11),(NQ-1,-2)):
            y[k]=val
        gy=self.multG(self.invGN(y))
        need(all(gy[k]==self.N*y[k] for k in range(NQ)),'integer full Q metric inverse identity')
    def multG(self,v):
        out=[0]*NQ
        for a,b,x in self.Gentries:
            out[a]+=x*v[b]
            if a!=b:out[b]+=x*v[a]
        return out
    def multK(self,v):
        out=[0]*NQ
        for a,b,x in self.Kentries:
            out[a]+=x*v[b]
            if a!=b:out[b]+=x*v[a]
        return out
    def invGN(self,y):
        # N*G_Q^-1 action, integer exactly, no rational intermediate.
        tmp=[6*y[j] for j in range(4)]
        for j in range(4):
            for k in range(132):
                tmp[j]-=(6//self.W[k+4])*self.X[j][k]*y[k+4]
        u=[sum(self.adj[j][k]*tmp[k] for k in range(4)) for j in range(4)]
        out=u+[0]*(NQ-4)
        for k in range(132):
            w=self.W[k+4]
            v=self.N*y[k+4]-sum(self.X[j][k]*u[j] for j in range(4))
            need(v%w==0,'N*G_inv not integer K2');out[k+4]=v//w
        for k in range(136,NQ):
            w=self.W[k];need(self.N%w==0,'N*G_inv not integer K3')
            out[k]=(self.N//w)*y[k]
        return out
    def L(self,v,z):
        kg=self.multK(v);gg=self.multG(v)
        return self.invGN([D*kg[i]-z*gg[i] for i in range(NQ)])
    def b(self,j):return self.invGN([self.B[k][j] for k in range(NQ)])
    def T(self,z):return [[D*self.TK[i][j]-z*self.TG[i][j] for j in range(10)] for i in range(10)]


def get_peak_rss_kib():
    # Optional Linux diagnostics only, no platform resource module.
    try:
        with open('/proc/self/status',encoding='ascii') as source:
            for line in source:
                if line.startswith('VmHWM:'):
                    return int(line.split()[1])
    except OSError:
        return 0
    return 0

def dot(a,b):return sum(x*y for x,y in zip(a,b))

def cert(s,z,m):
    start=time.monotonic_ns()
    need(0<=z<FLOORD,'z must lie below accepted whole-Q floor')
    lower=FLOORD-z;upper=CAPD-z
    n=s.N
    c=n*(lower+upper);q=n*(upper-lower);q2=q*q
    b=[s.b(j) for j in range(NTRIAL)]
    pprev=[[0]*NQ for _ in range(10)]
    p=[[2*x for x in bj] for bj in b]
    qprev=[x[:] for x in b]
    qq=[]
    for j in range(10):
        lb=s.L(b[j],z)
        qq.append([c*b[j][k]-2*lb[k] for k in range(NQ)])
    tprev=1;t=c
    if m==0:p=pprev;qq=qprev;t=1
    else:
        for step in range(1,m):
            pn=[];qn=[]
            for j in range(10):
                op=s.L(p[j],z);oq=s.L(qq[j],z)
                pn.append([2*(c*p[j][k]-2*op[k])-q2*pprev[j][k]+4*t*b[j][k] for k in range(NQ)])
                qn.append([2*(c*qq[j][k]-2*oq[k])-q2*qprev[j][k] for k in range(NQ)])
            tn=2*c*t-q2*tprev
            pprev,p=p,pn;qprev,qq=qq,qn;tprev,t=t,tn
    need(t>0,'Chebyshev denominator not positive')
    # Exact Chebyshev residual identity: it is not sufficient to trust a
    # numerically stable polynomial recurrence without checking its source.
    for j in range(10):
        lp=s.L(p[j],z)
        need(all(t*b[j][k]-lp[k]==qq[j][k] for k in range(NQ)),
             'Chebyshev recurrence/residual identity')
    # Matrix B'^T p (nondiagonal is symmetrized after adding p^T G q)
    bp=[[sum(s.B[k][i]*p[j][k] for k in range(NQ)) for j in range(10)] for i in range(10)]
    gq=[s.multG(v) for v in qq]
    pq=[[dot(p[i],gq[j]) for j in range(10)] for i in range(10)]
    qqGram=[[dot(qq[i],gq[j]) for j in range(10)] for i in range(10)]
    scale=lower*n*n*t*t
    top=s.T(z)
    nominal=[[top[i][j]*scale-lower*n*(n*t*bp[i][j]+pq[i][j]) for j in range(10)] for i in range(10)]
    lo=[[nominal[i][j]-qqGram[i][j] for j in range(10)] for i in range(10)]
    need(all(nominal[i][j]==nominal[j][i] for i in range(10) for j in range(10)),'nominal Schur symmetry')
    need(all(qqGram[i][j]==qqGram[j][i] for i in range(10) for j in range(10)),'rigorous error Gram symmetry')
    need(all(lo[i][j]==lo[j][i] for i in range(10) for j in range(10)),'lower Schur symmetry')
    il=inertia(lo);iu=inertia(nominal)
    # A symmetric permutation is a congruence. This independent ordering
    # catches a source-dependent leading-minor inertia implementation drift.
    rev=list(range(9,-1,-1))
    ilrev=inertia([[lo[i][j] for j in rev] for i in rev])
    iurev=inertia([[nominal[i][j] for j in rev] for i in rev])
    need(ilrev is None or ilrev==il,'lower reverse-order inertia disagreement')
    need(iurev is None or iurev==iu,'upper reverse-order inertia disagreement')
    need(il is None or iu is None or il>=iu,'Loewner inertia monotonicity')
    elapsed_ms=(time.monotonic_ns()-start)//1000000
    return dict(z=z,degree=m,low_neg=il,upper_neg=iu,
                interval_certified=(il==iu and il is not None),
                ms=elapsed_ms,rss_kib=get_peak_rss_kib(),
                approx_residual_bits=max(abs(v).bit_length() for x in qq for v in x),
                upper_diag_bits=max(abs(nominal[i][i]).bit_length() for i in range(10)),
                q_shape=NQ,source_old_sha=SHA_OLD,source_c_sha=SHA_C)

def toy():
    # Independent 2x2 positive and indefinite integer inertia controls.
    need(inertia([[3,1],[1,3]])==0,'toy SPD')
    need(inertia([[-3,1],[1,3]])==1,'toy indefinite')
    need(inertia([[-3,1],[1,-3]])==2,'toy negative')
    need(det_perm([[3,1],[1,3]])==8,'toy determinant')
    # Separate scalar Chebyshev/variational-error inequality check.
    # A=3, spectrum enclosed by [2,5], B=7; all exact integers.
    aa=3;bb=7;amin=2;amax=5;cc=amin+amax;qq=amax-amin
    pm,pp=0,2*bb;qm,qp=bb,(cc-2*aa)*bb;tm,tt=1,cc
    for deg in range(1,7):
        need(tt*bb-aa*pp==qp,'toy polynomial residual identity')
        # The exact scalar F=B^2/A lies between the variational trial
        # value F0 and F0+r^2/a. Compare after cross multiplication.
        fnum=2*bb*pp*tt-aa*pp*pp
        need(aa*fnum<=bb*bb*tt*tt,'toy lower inverse quadratic bound')
        need(amin*(bb*bb*tt*tt-aa*fnum)<=aa*qp*qp,'toy upper inverse quadratic bound')
        pn=2*(cc-2*aa)*pp-qq*qq*pm+4*tt*bb
        qn=2*(cc-2*aa)*qp-qq*qq*qm
        tn=2*cc*tt-qq*qq*tm
        pm,pp=pp,pn;qm,qp=qp,qn;tm,tt=tt,tn
    print('Y137_K_PILOT_TOY|exact_integer_inertia=PASS|interval_schur=MATHEMATICALLY_SPECIFIED|full_Ritz=NOT_COMPUTED|Wilson_weight=HOLD|json=0',flush=True)

def main():
    if sys.argv[1:]==['toy']:toy();return
    need(len(sys.argv) in (8,9) and sys.argv[1]=='pilot','usage: toy OR pilot old_dir_or_zip cross_dir_or_zip residual_dir_or_zip htt_dir_or_zip z_num degree [expected_negative]')
    src=Source(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
    z=int(sys.argv[6]);m=int(sys.argv[7]);need(0<=m<=20,'pilot degree 0..20')
    print('Y137_K_SOURCE|old_sha='+SHA_OLD+'|cross_sha='+SHA_C+'|original_nonflat_Q_dim='+str(NQ)+'|flat_plus_new_dim=10|old_schur_det_bits='+str(src.det.bit_length())+'|old_Q_edges='+str(len(src.Kentries))+'|exact_Gram_inverse=PASS|json=0',flush=True)
    c=cert(src,z,m)
    if len(sys.argv)==9:
        expected=int(sys.argv[8])
        need(c['interval_certified'] and c['low_neg']==expected,
             'exact whole-20738 inertia target not certified')
    print('Y137_K_PILOT|'+'|'.join(str(k)+'='+str(v) for k,v in c.items())+'|wholeQ_floor=94068200000_OVER_1E9|full_Ritz='+('NEGATIVE_INERTIA_CERTIFIED' if c['interval_certified'] else 'NOT_CERTIFIED')+'|Wilson_weight=HOLD|json=0',flush=True)

if __name__=='__main__':main()