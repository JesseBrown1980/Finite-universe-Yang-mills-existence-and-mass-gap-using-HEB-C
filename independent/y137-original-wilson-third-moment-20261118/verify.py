#!/usr/bin/env python3
"""Independent exact-integer third Wilson moment receipt audit; no source-module imports."""
import hashlib
import sys

CAP = 468
ECAP = 144
SHA2 = "393954283e19f17cecaae35947088d9338c9d81f7dea7d271be9fd46c39487b6"
SHA0 = "8f0c480802baf7cb0bf9c5daf45b461f9ea79d22f38d76c1eb5a056e96a8b21f"
SHA1 = "4194349ffb8a6c1bc9df8b64f4b62417b82c7602183bab011d8755ff54ede1be"
SHA4 = "97931421106792319999229833391980997446903218834601104745693653417924939714715139306386898411302098878398624094108700315899234816"


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def hashint(x):
    return hashlib.sha256(str(x).encode("ascii")).hexdigest()


def parse(lines):
    records={}
    progress=[]
    for s in lines.splitlines():
        name=s.split("|",1)[0]
        if name == "Y137_M3_PROGRESS":
            progress.append(s)
            continue
        need(name in ("Y137_M3_TOY","Y137_M3_SOURCE","Y137_M3_BOUNDS",
                      "Y137_M3_EXACT","Y137_M3_VERDICT"),"unexpected_source_row")
        need(name not in records,"duplicate_receipt")
        fields={}
        for pair in s.split("|")[1:]:
            k,sep,v=pair.partition("=")
            need(sep and k and k not in fields,"bad_field")
            fields[k]=v
        need(fields.pop("json",None)=="0","not_HBP")
        records[name]=fields
    need(all(k in records for k in
             ("Y137_M3_TOY","Y137_M3_SOURCE","Y137_M3_BOUNDS",
              "Y137_M3_VERDICT")),"missing_row")
    return records,progress


def integer(record,key):
    s=record[key]
    need(str(int(s))==s and s[0]!="+" and not s.startswith("-0"),
         "noncanonical_integer_"+key)
    return int(s)


def verify(data):
    r,progress=parse(data)
    toy=r["Y137_M3_TOY"]
    need(toy=={"physical_H_cube":"PASS","cross_edge_sign":"PASS",
               "nonnegative_electric":"PASS","planted_wrong_cross":"REJECTED",
               "first_Wilson_weight":"HOLD"},"toy_controls")
    scope=r["Y137_M3_SOURCE"]
    need(set(scope)=={"original_Wilson","flat_K3","shell4",
                      "shell4_nonzero","original_m2_sha256",
                      "original_K3_sha256","field","first_Wilson_weight"},
         "source_fields")
    need(scope["original_Wilson"]=="SEVEN_LOOP_24_LINK" and
         scope["flat_K3"]=="8_AND_155378" and
         scope["field"]=="FULL_ORIGINAL_S3_r9" and
         scope["first_Wilson_weight"]=="HOLD" and
         scope["original_m2_sha256"]==SHA2 and
         scope["original_K3_sha256"]==
             "f3461aa8a50cfa9efb4a1bbdc2d7be44ec1d4a13c80c47fd55fa07de60be28ff" and
         integer(scope,"shell4")==1985218,"source_scope")
    count=integer(scope,"shell4_nonzero")
    need(0<count<=1985218,"shell4_nonzero_scope")
    b=r["Y137_M3_BOUNDS"]
    need(set(b)=={"m0","m1","m2","m0_sha256","m1_sha256","m2_sha256",
                  "shell4_norm2_sha256","m3_core_sha256",
                  "cross4_sha256","mag4_sha256",
                  "shell4_norm2","core","cross","magnetic",
                  "lower","upper","electric_Ceiling",
                  "all_K4_magnetic","all_K4_electric"},"bound_schema")
    m0,m1,m2=[integer(b,k) for k in ("m0","m1","m2")]
    shell,core,cross,mag=[integer(b,k) for k in
                          ("shell4_norm2","core","cross","magnetic")]
    lower,upper=integer(b,"lower"),integer(b,"upper")
    need(m0>0 and m1>0 and 0<m2<=CAP*m1 and m1*m1<=m0*m2,
         "original_H_moment_psd")
    need(hashint(m0)==SHA0==b["m0_sha256"] and
         hashint(m1)==SHA1==b["m1_sha256"] and
         hashint(m2)==SHA2==b["m2_sha256"] and
         str(shell)==SHA4,"accepted_original_m2_receipt_regression")
    need(hashint(shell)==b["shell4_norm2_sha256"] and
         hashint(core)==b["m3_core_sha256"] and
         hashint(cross)==b["cross4_sha256"] and
         hashint(mag)==b["mag4_sha256"],
         "new_source_parts_digest")
    need(0<shell<=m2 and 0<=mag<=324*shell,
         "shell4_magnetic_bound")
    base=core+cross+mag
    need(lower==max(base,0,(m2*m2+m1-1)//m1) and
         upper==min(base+ECAP*shell,CAP*m2) and 0<=lower<=upper,
         "exact_interval_replay")
    need(integer(b,"electric_Ceiling")==ECAP and
         b["all_K4_magnetic"]=="EXACT","K4_electric_bound_theorem")
    v=r["Y137_M3_VERDICT"]
    need(v["source"]=="K3_K4_PHYSICAL" and
         v["first_Wilson_weight"]=="HOLD","physical_scope")
    if "Y137_M3_EXACT" not in r:
        need(not progress and
             b["all_K4_electric"]=="BOUNDED" and
             v=={"source":"K3_K4_PHYSICAL","physical_m3":"RATIONAL_INTERVAL",
                 "full_K4_E":"BOUNDED_PSD_144",
                 "first_Wilson_weight":"HOLD"},"bounded_gate")
        return "INTERVAL"
    x=r["Y137_M3_EXACT"]
    need(set(x)=={"m3","m3_sha256","electric4","electric4_sha256",
                 "full_K4_nonzero","third_T_sha256","exact_H3",
                 "first_Wilson_weight"},"full_fields")
    m3=integer(x,"m3")
    electric=integer(x,"electric4")
    need(0<=electric<=ECAP*shell and m3==base+electric and
         lower<=m3<=upper and m1*m3>=m2*m2 and 0<=m3<=CAP*m2,
         "full_H3_interval_and_Hankel")
    need(hashint(m3)==x["m3_sha256"] and
         hashint(electric)==x["electric4_sha256"] and
         integer(x,"full_K4_nonzero")==count and
         x["exact_H3"]=="PASS" and x["first_Wilson_weight"]=="HOLD",
         "full_source_hash")
    t1=CAP*m0-m1
    t2=CAP*CAP*m0-2*CAP*m1+m2
    t3=CAP*CAP*CAP*m0-3*CAP*CAP*m1+3*CAP*m2-m3
    need(0<=t3<=CAP*t2 and t1*t3>=t2*t2 and
         hashint(t3)==x["third_T_sha256"],"full_filtered_H3")
    need(b["all_K4_electric"]=="RUNNING" and
         v=={"source":"K3_K4_PHYSICAL","physical_m3":"EXACT",
             "full_K4_E":"EXHAUSTIVE_NONZERO_72_MOVES",
             "first_Wilson_weight":"HOLD"},"full_source_scope")
    return "EXACT"


def tamper_controls(data):
    status=verify(data)
    for old,new in (
        ("|first_Wilson_weight=HOLD|","|first_Wilson_weight=PASS|"),
        ("|shell4=1985218|","|shell4=0|"),
        ("|m2_sha256="+SHA2+"|","|m2_sha256=bad|"),
        ("|electric_Ceiling=144|","|electric_Ceiling=468|"),
        ("|lower=","|lower=7"),
    ):
        altered=data.replace(old,new,1)
        need(altered!=data,"bad_tamper_fixture")
        try:
            verify(altered)
        except ValueError:
            pass
        else:
            raise AssertionError("tampered_receipt_was_accepted")
    print("Y137_M3_REPLAY|mode="+status+"|source_m2_PIN=PASS|"
          "tamper_controls=5_REJECTED|first_Wilson_weight=HOLD|json=0")


if __name__=="__main__":
    need(len(sys.argv)==2,"usage_verify_HBP")
    with open(sys.argv[1],encoding="ascii") as f:
        tamper_controls(f.read())
