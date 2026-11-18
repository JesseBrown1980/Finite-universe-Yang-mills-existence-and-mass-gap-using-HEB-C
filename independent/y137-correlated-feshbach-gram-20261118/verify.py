#!/usr/bin/env python3
"""Independent exact integer replay of original-Q Gram Wilson source receipts.
Does not import producer, checker, or original Hamiltonian Python modules.
Uses separately parsed frozen original O/O2 64-entry hosted HBP sources.
"""
import hashlib
import os
import sys
from math import gcd, isqrt

HERE=os.path.dirname(os.path.abspath(__file__))
INDEP=os.path.dirname(HERE)
UNIT=1000000000000
WF=(1,3,2,3,3,2,2,2)
V1=(1000000000,997935625,996905915,38054797,37920545,2788116,51160,51160)
V2=(111045317,-38181375,-112233220,1000000000,979217930,216249666,4169404,4169404)
C2=os.path.join(INDEP,"y137-centered-source-flat-join-20261117",
                "INPUT-CENTERED-O8-64.hbp")
C0=os.path.join(INDEP,"y137-parallel-flat-projector-contraction-20261117",
                "INPUT-ORIGINAL-O8-64.hbp")
BLOB2="61b9d1359f5cae2d19c3b4827ee942ca7dd085ea"
BLOB0="0d9ba8a202b2f77f2dbeb993af9d3f46a32c3024"
S1=3429010525
S2=9197961975


def need(cond,reason):
    if not cond:raise ValueError(reason)


def rootceil(n):
    need(n>=0,"sqrt_domain")
    s=isqrt(n)
    return s+(s*s!=n)


def ceildiv(a,b):
    need(a>=0 and b>0,"ceil_domain")
    return (a+b-1)//b


def sq_up(n,d):
    return rootceil(ceildiv(n*UNIT*UNIT,d))


def sha(val):
    return hashlib.sha256(str(val).encode("ascii")).hexdigest()


def blob(data):
    z=data.encode("ascii")
    return hashlib.sha1(b"blob "+str(len(z)).encode("ascii")+bytes((0,))+z).hexdigest()


def records(raw,strict_prefix):
    rows=[]
    for line in raw.splitlines():
        if line.startswith(strict_prefix+"|"):
            d={}
            for part in line.split("|")[1:]:
                k,sep,v=part.partition("=")
                need(sep and k and k not in d,"bad_HBP_field")
                d[k]=v
            need(d.pop("json",None)=="0","bad_HBP_end")
            rows.append(d)
    return rows


def src_matrix(path,expected_blob):
    raw=open(path,encoding="ascii").read()
    need(blob(raw)==expected_blob,"hosted_source_blob_changed")
    entries=records(raw,"Y137_O8_ENTRY")
    meta=records(raw,"Y137_O8_MATRIX")
    need(len(entries)==64 and len(meta)==1,"source_64_envelope")
    A=[[0]*8 for _ in range(8)]
    R=[[0]*8 for _ in range(8)]
    seen=set()
    for e in entries:
        i,j=int(e["i"]),int(e["j"])
        need(0<=i<8 and 0<=j<8 and (i,j) not in seen,
             "source_index")
        seen.add((i,j))
        den=int(e["den"])
        need(den in (UNIT*UNIT,2*UNIT*UNIT),"source_den")
        a=int(e["approx_signed_num"])
        rad=int(e["Q_residual_radius_num"])+int(e["energy_band_radius_num"])
        need(rad>=0 and int(e["lower_signed_num"])==a-rad and
             int(e["upper_signed_num"])==a+rad,
             "true_energy_source_interval")
        A[i][j]=a
        R[i][j]=rad
    return A,R,meta[0]


def dot(a,b):
    return sum(WF[i]*a[i]*b[i] for i in range(8))


def action(M,v):
    return [sum(M[i][j]*v[j] for j in range(8)) for i in range(8)]


def shift_chord(s):
    return rootceil(2*UNIT*(UNIT-isqrt(UNIT*UNIT-s*s)))


def int_can(v):
    need(str(int(v))==v,"noncanonical_integer")
    return int(v)


def reconstruct():
    a2,r2,m2=src_matrix(C2,BLOB2)
    a0,r0,m0=src_matrix(C0,BLOB0)
    for k in ("original_Q_trial_1_U_sha256","original_Q_trial_2_U_sha256",
              "original_Q_trial_1_G_sha256","original_Q_trial_2_G_sha256"):
        need(m2[k]==m0[k],"not_same_Q")
    G=[[0]*8 for _ in range(8)]
    for i in range(8):
        for j in range(8):
            z=2*a0[i][j]-a2[i][j]
            need(z%7==0,"Gram_divisibility")
            G[i][j]=z//7
    sg=action(G,V1)
    ss=action(a2,V1)
    g=[(6//WF[i])*sg[i] for i in range(8)]
    s=[(6//WF[i])*ss[i] for i in range(8)]
    gg=dot(g,g);gs=dot(g,s);ssn=dot(s,s)
    gr=dot(g,V2);sr=dot(s,V2)
    det=gg*ssn-gs*gs
    num=ssn*gr*gr-2*gs*gr*sr+gg*sr*sr
    den=dot(V2,V2)*det
    need(gg>0 and det>0 and 0<=num<=den,"source_two_rank")
    ggcd=gcd(abs(gs),gg)
    opt=(gs//ggcd,gg//ggcd)
    return a2,r2,a0,r0,opt,(num,den),gr,gg


def replay(data):
    a2,r2,a0,r0,opt,geom,rg,gg=reconstruct()
    rows={}
    for line in data.splitlines():
        name=line.split("|",1)[0]
        need(name in ("Y137_GRAM_TOY","Y137_GRAM_SOURCE","Y137_GRAM_GEOMETRY",
                      "Y137_GRAM_CANDIDATE","Y137_GRAM_VERDICT"),
             "unknown_output")
        obj={}
        for x in line.split("|")[1:]:
            k,sep,v=x.partition("=")
            need(sep and k and k not in obj,"bad_output")
            obj[k]=v
        need(obj.pop("json",None)=="0","not_HBP")
        rows.setdefault(name,[]).append(obj)
    for key,amount in (("Y137_GRAM_TOY",1),("Y137_GRAM_SOURCE",1),
                       ("Y137_GRAM_GEOMETRY",1),("Y137_GRAM_CANDIDATE",10),
                       ("Y137_GRAM_VERDICT",1)):
        need(len(rows.get(key,[]))==amount,"receipt_count_"+key)
    toy=rows["Y137_GRAM_TOY"][0]
    need(toy=={"shared_shift":"PASS","weighted_W":"PASS",
               "two_energy_orthogonality":"CONDITIONAL_EXACT",
               "nonnormal_control":"PASS",
               "actual_first_Wilson_weight":"HOLD"},"toy")
    src=rows["Y137_GRAM_SOURCE"][0]
    need(src["original_O2"]=="TWO_ORIGINAL_SEVEN_LOOP_MINUS_SEVEN" and
         src["full_Q"]=="155378_PLUS_1985218_EXTERIOR" and
         src["shared_Q_inverse_hashes"]=="4_OF_4_IDENTICAL" and
         src["original_matrix_SHA2"]==BLOB2 and
         src["original_matrix_SHA0"]==BLOB0 and
         src["gram_source_rank2"]=="EXACT_W_WEIGHTED" and
         int_can(src["sample_dual_weight_ppb"])==4232581 and
         int_can(src["E1_sine_hi_per_trillion"])==S1 and
         int_can(src["E2_sine_hi_per_trillion"])==S2 and
         src["first_Wilson_weight"]=="HOLD","source_receipt")
    geo=rows["Y137_GRAM_GEOMETRY"][0]
    num,den=geom
    need(int_can(geo["orthogonal_optimal_shift_num"])==opt[0] and
         int_can(geo["orthogonal_optimal_shift_den"])==opt[1] and
         int_can(geo["closest_joint_dark_sine_lo_per_trillion"])==
             isqrt(num*UNIT*UNIT//den) and
         int_can(geo["closest_joint_dark_sine_hi_per_trillion"])==
             sq_up(num,den) and
         int_can(geo["Gram_only_angle_hi_per_trillion"])==
             sq_up(rg*rg,dot(V2,V2)*gg) and
         int_can(geo["old_E2_cone_source_only_dark_excluded"])==
             int(num*UNIT*UNIT>S2*S2*den) and
         geo["true_state_dark_excluded"]=="NOT_FROM_NOMINAL_GEOMETRY" and
         geo["actual_first_Wilson_weight"]=="HOLD" and
         geo["source_two_constraint_den_sha256"]==sha(den) and
         geo["source_two_constraint_num_sha256"]==sha(num),
         "two_source_geometry")
    choices=[(0,1),(1,1),(2,1),(5,2),(11,4),(3,1),(13,4),(7,2),(4,1),opt]
    gop=UNIT+ceildiv(72*1000000000000000000*UNIT,
                      (94068200000-69909586556)*(94068200000-69949433884))
    best=None
    for (p,q),entry in zip(choices,rows["Y137_GRAM_CANDIDATE"]):
        need(int_can(entry["c_num"])==p and int_can(entry["c_den"])==q,
             "candidate_order_or_scope")
        d=7*q*UNIT*UNIT
        rsum=[sum(((7*q+p)*a2[i][j]-2*p*a0[i][j])*V1[j]
                  for j in range(8)) for i in range(8)]
        amp=sum(V2[i]*rsum[i] for i in range(8))
        n1,n2=dot(V1,V1),dot(V2,V2)
        alow=abs(amp)*UNIT//(d*rootceil(n1*n2))
        ahi=ceildiv(abs(amp)*UNIT,d*max(1,isqrt(n1*n2)))
        norm=sum((6//WF[i])*rsum[i]*rsum[i] for i in range(8))
        anorm=sq_up(norm,6*d*d*n1)
        radrows=[sum((abs(7*q+p)*r2[i][j]+abs(2*p)*r0[i][j])*
                      abs(V1[j]) for j in range(8)) for i in range(8)]
        ern=sum((6//WF[i])*radrows[i]*radrows[i] for i in range(8))
        error=sq_up(ern,6*d*d*n1)
        op=21*gop+ceildiv(abs(p)*gop,q)
        d1=shift_chord(S1);d2=shift_chord(S2)
        e1=ceildiv(op*d1,UNIT)
        rhs=ceildiv(d2*anorm,UNIT)+ceildiv((UNIT+d2)*(e1+error),UNIT)
        expect={
            "center_amp_lo_per_trillion":alow,
            "center_amp_hi_per_trillion":ahi,
            "source_action_hi_per_trillion":anorm,
            "directional_source_radius_hi_per_trillion":error,
            "ground_projector_error_hi_per_trillion":e1,
            "true_E2_chord_hi_per_trillion":d2,
            "true_E1_chord_hi_per_trillion":d1,
            "physical_op_hi_per_trillion":op,
            "no_dark_rhs_hi_per_trillion":rhs,
            "strict_no_dark_margin_per_trillion":alow-rhs}
        for key,expected in expect.items():
            need(int_can(entry[key])==expected,"candidate_replay_"+key)
        need(entry["source_radius_construction"]==
             "SHARED_Q_CENTRE_INDEPENDENT_RADII" and
             entry["full_original_Wilson_weight"]=="HOLD",
             "conservative_error_scope")
        if best is None or (alow-rhs)>best[0]:
            best=(alow-rhs,p,q)
    v=rows["Y137_GRAM_VERDICT"][0]
    need(int_can(v["candidate_count"])==10 and
         int_can(v["best_shift_num"])==best[1] and
         int_can(v["best_shift_den"])==best[2] and
         int_can(v["strongest_valid_margin_per_trillion"])==best[0] and
         v["original_source_nominal_joint_dark"]==
         ("EXCLUDED" if num*UNIT*UNIT>S2*S2*den else "FEASIBLE") and
         v["source_shared_residual_covariance"]=="REQUIRES_DIRECT_JOINT_DUAL" and
         v["true_E1_projector_action"]=="CONSERVATIVE_OP_BOUND" and
         v["original_first_excitation_Wilson_weight"]==
         ("CANDIDATE_REQUIRE_INDEPENDENT_REVIEW" if best[0]>0 else "HOLD") and
         v["quantitative_original_weight"]=="HOLD" and v["issue_137"]=="OPEN",
         "verdict")
    return best[0]


def tests(data):
    margin=replay(data)
    for old,new in (
        ("|first_Wilson_weight=HOLD|","|first_Wilson_weight=PASS|"),
        ("|E2_sine_hi_per_trillion=9197961975|","|E2_sine_hi_per_trillion=0|"),
        ("|original_matrix_SHA2="+BLOB2+"|","|original_matrix_SHA2=bad|"),
        ("|source_action_hi_per_trillion=","|source_action_hi_per_trillion=999"),
        ("|closest_joint_dark_sine_lo_per_trillion=",
         "|closest_joint_dark_sine_lo_per_trillion=999"),
        ("|quantitative_original_weight=HOLD|","|quantitative_original_weight=PASS|"),
    ):
        modified=data.replace(old,new,1)
        need(modified!=data,"corrupt_control_unmatched")
        try:replay(modified)
        except ValueError:pass
        else:raise AssertionError("tampered_source_replayed")
    print("Y137_GRAM_REPLAY|source_centres=128_ENTRIES|W_orthogonality=PASS|"
          "candidate_count=10|tamper_controls=6_REJECTED|"
          "best_margin="+str(margin)+"|original_Wilson_weight=HOLD|json=0")


if __name__=="__main__":
    need(len(sys.argv)==2,"usage_verify_HBP")
    with open(sys.argv[1],encoding="ascii") as f:tests(f.read())
