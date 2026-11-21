#!/usr/bin/env python3
"""Independent frozen main-branch source moment / matrix-localizer integrity.

Four original HBP source files, not scalar proof receipt values, are consumed.
This is matrix-source arithmetic validation, not full 20M-state reenumeration.
"""
import hashlib
from pathlib import Path

SOURCE=(
 ("independent/y137-shell4-diagonal-cache-20261114/RESULT-MAGNETIC-CACHE.hbp",
  "6454216973b8e59d65174c7cadc4f22c7dcf0354","Y137_CACHE_POINT"),
 ("independent/y137-real-Q-moment-20261114/RESULT-MU1.hbp",
  "86abf9611f8b9df5e03e796e81f513cba826c085","Y137_MU1_COMPLETE_POINT"),
 ("independent/y137-d11-shell5-spill-20261114/RESULT-MU2.hbp",
  "31de869725d0e760e650365d4c386b4b2fd722e6","Y137_D11_MU2_POINT"),
 ("independent/y137-mu3-real-20261115/RESULT-WORKER1-C-FULL-SIGNED-MU3-TWO-ENERGY-20261116.hbp",
  "1b7afcda7a6f1afe34cb22afcfc8dccde1196e04","Y137_C_MU3_ACCEPT_MATRIX")
)
SAMPLES=(69909875505,69949729820)
M3_SHA=(
"62787ba280050e598323eddcc67e0cd6234b8e2cfcb7b7bc65e6275fdfae4763",
"481f2c6b96cb7a7b756e15e96eb8734538a2b74fcb309ac2103a3e8f0284644d")
def need(v,msg):
    if not v:raise ValueError(msg)
def git_blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+bytes((0,))+data).hexdigest()
def matrix(s):
    out=[[int(x) for x in row.split(",")] for row in s.split(";")]
    need(len(out)==8 and all(len(r)==8 for r in out),"moment_8x8")
    need(all(out[i][j]==out[j][i] for i in range(8) for j in range(8)),
         "moment_W_symmetric_bilinear")
    return out
def digest(m):
    return hashlib.sha256("|".join(str(x) for row in m for x in row).encode("ascii")).hexdigest()
def parse(root,src):
    file,sha,tag=src
    content=root.joinpath(file).read_bytes()
    need(git_blob(content)==sha,"original_immutable_source_SHA_"+tag)
    records=[]
    for line in content.decode("ascii").splitlines():
        if not line.startswith(tag+"|"):continue
        row={}
        for field in line.split("|")[1:]:
            name,sep,v=field.partition("=")
            need(name and sep and name not in row,"original_HBP_fields")
            row[name]=v
        need(row.get("json")=="0","original_HBP_json0")
        records.append(row)
    need(len(records)==2 and tuple(int(r["sample_num"]) for r in records)==SAMPLES,
         "two_original_matched_source_samples")
    return records
def add(a,b):return [[x+y for x,y in zip(row,other)] for row,other in zip(a,b)]
def sub(a,b):return [[x-y for x,y in zip(row,other)] for row,other in zip(a,b)]
def mul(a,k):return [[k*x for x in row] for row in a]
def block(a,b,c,d):
    return [a[i]+b[i] for i in range(8)]+[c[i]+d[i] for i in range(8)]
def bareiss_PD(x):
    a=[row[:] for row in x]
    n=len(a);old=1
    for k in range(n):
        p=a[k][k]
        need(p>0,"signed_16x16_localizer_strict_PD_at_"+str(k))
        if k==n-1:break
        for i in range(k+1,n):
            left=a[i][k]
            for j in range(k+1,n):
                new=p*a[i][j]-left*a[k][j]
                need(new%old==0,"localizer_fraction_free_divisibility")
                a[i][j]=new//old
            a[i][k]=0
        old=p
    return n
def check_one(i,sources):
    s,m1,m2,m3=(x[i] for x in sources)
    z=SAMPLES[i]
    U=matrix(s["U0"])
    G=matrix(s["G0"])
    need(all(x%6==0 for row in G for x in row),"mu0_sixfold")
    m0=[[x//6 for x in row] for row in G]
    a1=matrix(m1["exact_mu1_8x8"])
    a2=matrix(m2["actual_K3_mu2_8x8"])
    txt=m3["full_whole_Q_mu3_six"]
    need(hashlib.sha256(txt.encode("ascii")).hexdigest()==
         m3["matrix_sha256"]==M3_SHA[i],"original_full_Q_signed_mu3_sha")
    a3raw=matrix(txt)
    need(all(x%6==0 for row in a3raw for x in row),"mu3_sixfold")
    a3=[[x//6 for x in row] for row in a3raw]
    need(digest(U)==s["U_sha256"] and digest(G)==s["G_sha256"] and
         digest(m0)==m1["wholeQ_mu0_sha256"]==m2["actual_K3_mu0_sha256"] and
         digest(a1)==m1["wholeQ_mu1_sha256"]==m2["actual_K3_mu1_sha256"] and
         digest(a2)==m2["actual_K3_mu2_sha256"],"original_8x8_moment_source_cross_SHA")
    lo=94068200000-z
    hi=468000000000-z
    need(hi>lo>0,"whole_Q_Perron_to_original_E_window")
    lower=block(sub(a1,mul(m0,lo)),sub(a2,mul(a1,lo)),
                sub(a2,mul(a1,lo)),sub(a3,mul(a2,lo)))
    upper=block(sub(mul(m0,hi),a1),sub(mul(a1,hi),a2),
                sub(mul(a1,hi),a2),sub(mul(a2,hi),a3))
    need(bareiss_PD(lower)==16 and bareiss_PD(upper)==16,"both_strict_signed_localizers")
    return z
def main():
    root=Path(__file__).resolve().parents[2]
    sources=[parse(root,x) for x in SOURCE]
    for i in range(2):
        z=check_one(i,sources)
        print("Y137_JOINED_MAIN_SOURCE_MOMENT|sample="+str(z)+
              "|8x8_U0_mu0_mu1_mu2_mu3=SHA_PASS"+
              "|original_signed_mu3=SHA_PASS|two_16x16_moment_localizers=STRICT_POSITIVE"+
              "|full_state_Q_moment_source=ARCHIVED_INDEPENDENT_RECONSTRUCTION"+
              "|original_Wilson=FORMAL_HOLD|json=0")
    print("Y137_JOINED_MAIN_MOMENT_VERDICT|original_sources=4_BLOBS_PINNED"+
          "|two_energies=PASS|four_signed_16x16_localizers=STRICT_PD"+
          "|same_Perron_floor=PASS|source_reenumeration=SEPARATE_VERIFIED_RUN"+
          "|original_first_Wilson=FORMAL_HOLD|continuum_4D=OPEN|json=0")
if __name__=="__main__":
    try:main()
    except (ValueError,KeyError,IndexError,ZeroDivisionError) as exc:
        print("Y137_JOINED_SOURCE_REFUSE|reason="+str(exc)+"|json=0")
        raise SystemExit(2)
