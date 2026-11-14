#!/usr/bin/env python3
"""Graph-free independent audit of accepted-K3 full-Q mu1 and exact n=1 Schur.

Reads eight archived raw hosted source receipts and recomputes both sample
moments from original shard entries. Uses independent exact rational Schur
complement (LDL) to check spectral bounds, not the source's Bareiss minors.
Derives both *improved* degree-one Chebyshev Schur bounds, still conditional
on accepted 94.0682 whole-Q spectral floor and raw source completeness.
"""
import hashlib
from math import gcd
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SHARD_PATH=HERE/"RESULT-MU1-SHARD-EVIDENCE.hbp"
RESULT_PATH=HERE/"RESULT-MU1.hbp"
SOURCE_PATH=ROOT/"independent/y137-shell4-diagonal-cache-20261114/RESULT-MAGNETIC-CACHE.hbp"
SHA={
    "shards":"ab6493016ee3201f61fa54746878ee3890f26f34",
    "result":"86abf9611f8b9df5e03e796e81f513cba826c085",
    "historical":"6454216973b8e59d65174c7cadc4f22c7dcf0354",
}
FLATS=8
SHARDS=8
SHELL4=1985218
MOVES=72
B=1000000000
FLOOR=94068200000
HMAX=468000000000
SAMPLES=(69909875505,69949729820)


def insist(cond,reason):
    if not cond:
        raise SystemExit("Y137_N1_REFUSE|reason="+reason+"|json=0")


def blob(b):
    return hashlib.sha1(b"blob "+str(len(b)).encode()+bytes((0,))+b).hexdigest()


def readp(name,path):
    b=path.read_bytes()
    insist(blob(b)==SHA[name],"source_blob_"+name)
    return b.decode("utf-8").splitlines()


def row(line):
    fields=line.split("|")
    d={}
    for bit in fields[1:]:
        insist("=" in bit,"malformed_receipt")
        k,v=bit.split("=",1)
        insist(k not in d,"duplicate_field")
        d[k]=v
    return fields[0],d


def parse_matrix(value):
    A=[[int(v) for v in r.split(",")] for r in value.split(";")]
    insist(len(A)==FLATS and all(len(r)==FLATS for r in A),"matrix8_shape")
    return A


def matrix_hash(A):
    raw="|".join(str(x) for r in A for x in r).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def mat(a=0):
    return [[a]*FLATS for _ in range(FLATS)]


def sum_mat(a,b):
    return [[a[i][j]+b[i][j] for j in range(FLATS)] for i in range(FLATS)]


def diff(a,b):
    return [[a[i][j]-b[i][j] for j in range(FLATS)] for i in range(FLATS)]


def times(a,n):
    return [[n*x for x in row] for row in a]


def encode(a):
    return ";".join(",".join(str(x) for x in r) for r in a)


def rational(n,d=1):
    insist(d!=0,"zero_rational_denominator")
    if d<0:
        n=-n
        d=-d
    v=gcd(abs(n),d)
    return (n//v,d//v)


def rsub(x,y):
    return rational(x[0]*y[1]-y[0]*x[1],x[1]*y[1])


def rmul(x,y):
    return rational(x[0]*y[0],x[1]*y[1])


def rdiv(x,y):
    insist(y[0]!=0,"rational_zero_pivot")
    return rational(x[0]*y[1],x[1]*y[0])


def exact_psd(a):
    """Exact integer-pair rational LDL, not source Bareiss minors.

    Each rational is a reduced (numerator,positive denominator) pair.
    A zero pivot requires its entire remaining row to vanish.
    """
    insist(all(a[i][j]==a[j][i] for i in range(FLATS)
               for j in range(FLATS)),"non_symmetric_matrix")
    b=[[rational(x) for x in row] for row in a]
    for k in range(FLATS):
        p=b[k][k]
        if p[0]<0:
            return False
        if p[0]==0:
            if any(b[k][j][0]!=0 for j in range(k+1,FLATS)):
                return False
            continue
        for i in range(k+1,FLATS):
            u=b[i][k]
            for j in range(i,FLATS):
                b[i][j]=rsub(b[i][j],rdiv(rmul(u,b[k][j]),p))
        for i in range(k+1,FLATS):
            b[i][k]=rational(0)
        for i in range(k+1,FLATS):
            for j in range(k+1,i):
                b[i][j]=b[j][i]
    return True

def evidence():
    lines=readp("shards",SHARD_PATH)
    data=[]
    at=0
    for shard in range(SHARDS):
        insist(at<len(lines),"missing_shard")
        tag,h=row(lines[at])
        insist(tag=="BEGIN_PART" and int(h["shard"])==shard,
               "shard_frame_order")
        at+=1
        rows=[]
        while at<len(lines) and not lines[at].startswith("END_PART|"):
            tag,d=row(lines[at])
            insist(tag in ("Y137_MU1_SHARD","Y137_MU1_PART",
                           "Y137_MU1_INNER","Y137_MU1_VERDICT"),
                   "unknown_shard_row")
            rows.append((tag,d))
            at+=1
        insist(at<len(lines),"unterminated_shard")
        end,ed=row(lines[at])
        insist(end=="END_PART" and int(ed["shard"])==shard,
               "bad_shard_end")
        at+=1
        insist(len(rows)==int(h["record_count"])==
               (6 if shard==0 else 4),"shard_row_count")
        headers=[d for tag,d in rows if tag=="Y137_MU1_SHARD"]
        parts=[d for tag,d in rows if tag=="Y137_MU1_PART"]
        inner=[d for tag,d in rows if tag=="Y137_MU1_INNER"]
        verdict=[d for tag,d in rows if tag=="Y137_MU1_VERDICT"]
        insist(len(headers)==len(verdict)==1 and len(parts)==2 and
               len(inner)==(2 if shard==0 else 0),"shard_structure")
        status=headers[0]
        insist(int(status["shard"])==shard and
               int(status["shards"])==SHARDS and
               int(status["start"])==SHELL4*shard//SHARDS and
               int(status["stop"])==SHELL4*(shard+1)//SHARDS and
               int(status["rows"])==int(status["stop"])-int(status["start"])
               and int(status["complete_raw_moves"])==
                   MOVES*int(status["rows"]),
               "missing_or_duplicate_shell4_rows")
        insist(status["all_72_moves_per_row"]=="PASS" and
               verdict[0]["real_mu1_certified"]=="NOT_UNTIL_ALL_SHARDS" and
               verdict[0]["actual_Wilson_weight"]=="HOLD",
               "shard_provenance")
        data.append((status,parts,inner))
    insist(at==len(lines),"extra_untrusted_source_lines")
    insist(sum(int(v[0]["rows"]) for v in data)==SHELL4,
           "total_shell4_mismatch")
    return data


def source_and_result():
    raw=[row(s) for s in readp("historical",SOURCE_PATH)]
    points=[d for t,d in raw if t=="Y137_CACHE_POINT"]
    insist(len(points)==2,"historical_source_count")
    rr=[row(s) for s in readp("result",RESULT_PATH)]
    results=[d for t,d in rr if t=="Y137_MU1_COMPLETE_POINT"]
    insist(len(results)==2 and len(rr)==4 and
           rr[-1][0]=="Y137_MU1_COMPLETE_VERDICT","result_source_count")
    return points,results


def reconstruct(items,source,result,index):
    z=SAMPLES[index]
    insist(int(source["sample_num"])==z and
           int(result["sample_num"])==z,"frozen_energy_mismatch")
    insist(matrix_hash(parse_matrix(source["U0"]))==source["U_sha256"] and
           matrix_hash(parse_matrix(source["G0"]))==source["G_sha256"],
           "historical_U_G_hash_mismatch")
    original_G=parse_matrix(source["G0"])
    G=mat()
    H=mat()
    for n,(_,parts,inner) in enumerate(items):
        p=parts[index]
        insist(int(p["shard"])==n and int(p["sample_num"])==z and
               p["source_U_sha256"]==source["U_sha256"] and
               p["source_G_sha256"]==source["G_sha256"],
               "shard_source_inconsistency")
        G=sum_mat(G,parse_matrix(p["complete_Q4_mu0_six"]))
        H=sum_mat(H,parse_matrix(p["complete_Q4_mu1_six"]))
        if n==0:
            q=inner[index]
            insist(int(q["sample_num"])==z,"inner_energy_mismatch")
            G=sum_mat(G,parse_matrix(q["complete_K3_mu0_six"]))
            H=sum_mat(H,parse_matrix(q["complete_K3_mu1_six"]))
    insist(G==original_G,"reconstructed_mu0_not_original")
    insist(all(x%6==0 for r in G for x in r) and
           all(x%6==0 for r in H for x in r),"W_divisibility")
    mu0=[[x//6 for x in r] for r in G]
    mu1=[[x//6 for x in r] for r in H]
    insist(matrix_hash(mu0)==result["wholeQ_mu0_sha256"] and
           matrix_hash(mu1)==result["wholeQ_mu1_sha256"] and
           encode(mu1)==result["exact_mu1_8x8"],
           "independently_reconstructed_mu1_result_mismatch")
    return mu0,mu1,parse_matrix(source["U0"])


def prove_degree1(z,mu0,mu1,u):
    # A_int = b(QHQ-z), g/h are integer scaled full-Q endpoints.
    g=FLOOR-z
    h=HMAX-z
    s=g+h
    d=h-g
    insist(g>0 and h>g,"source_global_spectral_bounds")
    low=diff(mu1,times(mu0,g))
    high=diff(times(mu0,h),mu1)
    insist(exact_psd(mu0) and exact_psd(low) and exact_psd(high),
           "independent_fraction_LDL_spectral_localizers")

    # n=1 exact Chebyshev:
    # P1(X)=s-2X, K1=s, F0(X)=2,
    # Y1=Y-2b R/s.
    # U1=U-(4b/s²)(s mu0-mu1).
    numerator_reduction=times(diff(times(mu0,s),mu1),4*B)
    insist(exact_psd(numerator_reduction) and
           any(numerator_reduction[i][i]>0 for i in range(FLATS)),
           "strict_degree1_variational_improvement")
    U1_num=diff(times(u,s*s),numerator_reduction)

    # R1 = (s-2A_int)R/s: global full-Q Gram <= (d/s)²mu0.
    # S(z) in [U1-(b/g)(d/s)² mu0, U1].
    # Exact lower has denominator g*s².
    lower_num=diff(times(U1_num,g),times(mu0,B*d*d))
    # Old lower: U-(b/g)mu0. Improvement in the NEW lower:
    #   (4b/s²)(mu1-g mu0), by exact rearrangement.
    gain_lower=times(low,4*B)
    old_lower_num=diff(times(u,g*s*s),times(mu0,B*s*s))
    insist(diff(lower_num,old_lower_num)==times(gain_lower,g),
           "lower_improvement_algebra")
    insist(exact_psd(gain_lower),"lower_bound_not_monotone")
    # Negative controls: a false lower/upper endpoint must be rejected.
    insist(not exact_psd(diff(mu1,times(mu0,h+1))) or
           not exact_psd(diff(times(mu0,g-1),mu1)),
           "fault_control_spectral_endpoint")

    # Directional integer trace improvement: strictly positive.
    sumdiag_upper=sum(numerator_reduction[i][i] for i in range(FLATS))
    sumdiag_lower=sum(gain_lower[i][i] for i in range(FLATS))
    return (s,d,U1_num,lower_num,sha_big(U1_num),sha_big(lower_num),
            sumdiag_upper,sumdiag_lower)


def sha_big(M):
    return matrix_hash(M)


def main():
    shards=evidence()
    src,res=source_and_result()
    out=[]
    for i,z in enumerate(SAMPLES):
        mu0,mu1,u=reconstruct(shards,src[i],res[i],i)
        s,d,u1,low,us,ls,upt,lot=prove_degree1(z,mu0,mu1,u)
        out.append((z,s,d,u1,low,us,ls,upt,lot))
    print("Y137_N1_FREEZE|source=ACTUAL_ACCEPTED_K3_3x4_S3"+
          "|complete_shell4_states=1985218|source_shards=8"+
          "|raw_moves=142935696|two_energy_samples=2"+
          "|original_G_exactly_restored=1"+
          "|PSD_method=INDEPENDENT_INTEGER_PAIR_LDL"+
          "|conditional_floor_num=94068200000"+
          "|whole_Q_upper_num=468000000000"+
          "|first_Wilson_weight=HOLD|json=0",flush=True)
    for z,s,d,u1,lower,sha_u,sha_l,up,low in out:
        print("Y137_N1_POINT|sample_num="+str(z)+
              "|den=1000000000"+
              "|K1_num="+str(s)+
              "|Cheb_spectral_span_num="+str(d)+
              "|new_upper_denom="+str(s*s)+
              "|new_upper_numerator_8x8="+encode(u1)+
              "|new_upper_sha256="+sha_u+
              "|new_lower_denom="+str((FLOOR-z)*s*s)+
              "|new_lower_numerator_8x8="+encode(lower)+
              "|new_lower_sha256="+sha_l+
              "|upper_improvement_trace_numerator="+str(up)+
              "|lower_improvement_trace_numerator="+str(low)+
              "|strict_two_sided_improvement_PSD=1"+
              "|new_corrected_schur_center=EXACT"+
              "|degree7_14_moments=NOT_COMPUTED"+
              "|first_Wilson_weight=HOLD|json=0",flush=True)
    print("Y137_N1_VERDICT|actual_K3_corrected_Schur_degree=1"+
          "|actual_wholeQ_mu0_mu1=EXACT"+
          "|degree1_fullQ_two_sided_sandwich=PASS"+
          "|degree7_corrected_schur=HOLD"+
          "|independent_raw_move_source_review=PENDING"+
          "|actual_Wilson_weight=HOLD|issue_137=OPEN|json=0",
          flush=True)


if __name__=="__main__":
    main()
