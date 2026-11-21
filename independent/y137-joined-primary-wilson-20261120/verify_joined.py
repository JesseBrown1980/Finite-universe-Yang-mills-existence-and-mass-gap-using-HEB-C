#!/usr/bin/env python3
"""Fail-closed archival fan-in for the original 3x4 finite S3 Wilson candidate.

Original source archives are independently pinned in two old GitHub Actions
runs. This does not regenerate full original Q duals from all orbit moves.
The final mathematical verdict must therefore preserve FORMAL_HOLD pending
independent primary dual-producer acceptance.
"""
import copy
import hashlib
import sys
from math import gcd, isqrt
from pathlib import Path
from zipfile import ZipFile

sys.path.insert(0,str(Path(__file__).resolve().parents[1].joinpath("y137-one-shot-schur-gram-wilson-20261120")))
from check_shortcut import F

U=1000000000000
B=1000000000
PS=1000000
W=(1,3,2,3,3,2,2,2)
SAMPLES=(69909875505,69949729820)
WINDOWS=((69909429421,69909586556),(69949264147,69949433884))
SINE0=(2362700330,5047836049)
SINENEW=(2034354058,4260581813)
BASE_Q=(259788930946,254910334285)
MOVE=(949209145,3693022069)
GAPS=(24158613444000000,24118766116000000)
BNORM=8485281374239
PINS={
 "ALL.hbp":"bffa172b395dc1ad47b03907315c57ac0625390abaf6ba484ebc4980dcddce5e",
 "COMMIT.txt":"f1e7fa96cbccca77f16dc177d1d48521778b0caf7aea44a83362ec1274ac7ae5",
 "interval.jsonl":"6624235fdbec9dd84bb4df267d56987b8fc55b667bb4521ffb9d60b9604fa3ac",
 "branch.jsonl":"7d7531a63d5e16355438727717f1528312c30cd4f17a4fb5616c43faa85f9778",
 "samples.jsonl":"e1d83a5c862f7b729b374a605bf934eb646d05c023e56908a6e27d8e5a100bc3",
 "TIGHTENED-WILSON.hbp":"8da7cd060dc366b5699997f803d5731b0b20f11a20222eeb7b6c011fdff12443",
}
def need(q,msg):
    if not q:raise ValueError(msg)
def sha(s):return hashlib.sha256(s).hexdigest()
class Artifact:
    def __init__(self,path):
        self.path=Path(path)
        self.archive=None if self.path.is_dir() else ZipFile(self.path)
    def __enter__(self):return self
    def __exit__(self,*args):
        if self.archive is not None:self.archive.close()
    def read(self,name):
        return self.path.joinpath(name).read_bytes() if self.archive is None else self.archive.read(name)

def get_zip(z,name,pin_name=None):
    raw=z.read(name)
    need(sha(raw)==PINS[pin_name or name],"pinned_artifact_sha_"+name)
    return raw.decode("ascii")
def rational(x):
    t=str(x).split("/")
    need(0<len(t)<=2 and all(k for k in t),"rational_format")
    return F(int(t[0]),int(t[1]) if len(t)==2 else 1)
def rows(s,tag):
    out=[]
    for line in s.splitlines():
        if not line.startswith(tag+"|"):continue
        x={}
        for entry in line.split("|")[1:]:
            k,sep,v=entry.partition("=")
            need(sep and k and k not in x,"malformed_"+tag)
            x[k]=v
        need(x.get("json")=="0","hbp_terminator_"+tag)
        out.append(x)
    return out
def one(s,tag):
    x=rows(s,tag)
    need(len(x)==1,"single_"+tag)
    return x[0]
def pinned_json(raw):
    """Strict minimal JSON grammar for the audited fixed archived integer records.

    JSON floats, escaped strings, duplicate keys and nonfinite values fail closed.
    The four archived source files contain only plain ASCII strings, integers,
    booleans, lists and dictionaries; no broad JSON implementation is needed.
    """
    s=raw.strip()
    i=0
    def skip():
        nonlocal i
        while i<len(s) and s[i] in " \t\r\n":i+=1
    def string():
        nonlocal i
        need(i<len(s) and s[i]=='"',"quoted_json_string")
        i+=1
        start=i
        while i<len(s) and s[i]!='"':
            need(s[i]!='\\' and ord(s[i])>=32 and ord(s[i])<=126,
                 "escaped_or_nonascii_json_string")
            i+=1
        need(i<len(s),"unterminated_json_string")
        result=s[start:i]
        i+=1
        return result
    def value():
        nonlocal i
        skip()
        need(i<len(s),"incomplete_json")
        ch=s[i]
        if ch=='"':return string()
        if ch=='{':
            i+=1;out={};skip()
            if i<len(s) and s[i]=='}':i+=1;return out
            while True:
                skip();key=string();need(key not in out,"duplicate_json_key")
                skip();need(i<len(s) and s[i]==':',"json_colon");i+=1
                out[key]=value();skip()
                need(i<len(s),"json_object_close")
                if s[i]=='}':i+=1;return out
                need(s[i]==',',"json_object_comma");i+=1
        if ch=='[':
            i+=1;out=[];skip()
            if i<len(s) and s[i]==']':i+=1;return out
            while True:
                out.append(value());skip()
                need(i<len(s),"json_array_close")
                if s[i]==']':i+=1;return out
                need(s[i]==',',"json_array_comma");i+=1
        for word,result in (("true",True),("false",False),("null",None)):
            if s.startswith(word,i):
                i+=len(word)
                return result
        start=i
        if ch=='-':i+=1
        need(i<len(s) and s[i].isdigit(),"integer_json_only")
        need(s[i]!='0' or i+1==len(s) or not s[i+1].isdigit(),"json_no_leading_zero")
        while i<len(s) and s[i].isdigit():i+=1
        need(s[i:i+1] not in (".","e","E","-","+"),"json_float_exponent_rejected")
        return int(s[start:i])
    result=value()
    skip();need(i==len(s),"json_trailing_characters")
    return result

def jrows(s,tag,quantity=2):
    x=[pinned_json(line.partition("|")[2]) for line in s.splitlines()
       if line.startswith(tag+"|")]
    need(len(x)==quantity and all(isinstance(y,dict) for y in x),"json_source_"+tag)
    return x
def ceildiv(n,d):
    need(d>0 and n>=0,"ceildiv_positive")
    return (n+d-1)//d
def ceilroot(n):
    need(n>=0,"negative_root")
    t=isqrt(n)
    return t+(t*t!=n)
def up_root(n,d):
    need(d>0 and n>=0,"sqrt_fraction")
    return ceilroot(ceildiv(n*U*U,d))
def ceil_sine(rho,delta):
    need(rho>=0 and delta>0,"sine_domain")
    t=rho*rho; ratio=t.div(t+delta*delta)
    lo,hi=0,U
    while lo+1<hi:
        mid=(lo+hi)//2
        if F(mid*mid,U*U)<ratio:lo=mid
        else:hi=mid
    need(F(hi*hi,U*U)>=ratio and F((hi-1)*(hi-1),U*U)<ratio,"sine_rounding")
    return hi
def vector(s):
    x=tuple(int(v) for v in s.split(","))
    need(len(x)==8,"eight_flat_vector")
    return x
def branch_angle(i,r,b,s,pair):
    z=SAMPLES[i];lo,hi=WINDOWS[i]
    need(r["sample_num"]==z and b["sample"]==z and b["level"]==i+1,"energy_sample")
    need(r["source"]=="PINNED_HISTORICAL_PREMISES" and
         r["Wilson_true_first_weight"]=="FORMAL_HOLD","source_scope")
    need(r["source_weight_metric"]==",".join(map(str,W)) and
         rational(r["physical_S_denominator"])==F(10**33),"Schur_W_and_scale")
    need((rational(r["interval_lo"]),rational(r["interval_hi"]))==
         (F(lo,B),F(hi,B)),"true_energy_windows")
    need(r["source_selected_k"]==4 and
         r["exact_singular_bisection_steps"]==12 and
         r["exact_width_spectral_bisection_steps"]==14,"source_eigenspace_trial")
    need(int(r["source_moved_flat_distance_per_trillion"])==MOVE[i],
         "original_matched_movement")
    gap=F(94068200000-z,B)
    spread=ceildiv(BNORM*MOVE[i]*B,U*(94068200000-z))
    q=F(BASE_Q[i]+spread,U)
    der=F(BNORM,U)*q.div(gap)
    drift=F(max(z-lo,z-hi),B)
    gder=F(72).div(gap*gap)
    need(rational(r["source_Q_norm_upper"])==q and
         rational(r["directional_Q_derivative_upper"])==der,"same_Q_directional")
    need(der<=gder and rational(r["global_Q_drift_comparison"])==gder*drift,
         "global_Q_derivative")
    need(rational(r["projected_Q_drift_upper"])==der*drift and
         rational(r["full_schur_drift_upper"])==(F(1)+gder)*drift,
         "Q_drift_matrix")
    width=rational(r["width_spectral_upper"])
    need(F(0)<width<=rational(r["width_frobenius_upper"])+F(1,U),
         "8x8_matrix_width")
    rho=rational(r["residual_mid_upper"])+rational(r["directional_width_error_upper"])+der*drift
    delta=rational(r["sample_compressed_singular_lower"])-width.div(2)-(F(1)+gder)*drift
    need(rational(r["interval_projected_residual_upper"])==rho and
         rational(r["interval_compressed_singular_lower"])==delta and
         delta>F(0),"true_projector_7x7_gap")
    angle=ceil_sine(rho,delta)
    need(angle==SINENEW[i] and
         rational(r["target_sine"])==F(SINE0[i],U) and
         r["conditional_interval_angle"]=="PASS","true_E_projector_sine")
    need(rho*rho*(F(1)-F(SINE0[i]*SINE0[i],U*U)) <=
         F(SINE0[i]*SINE0[i],U*U)*delta*delta,"angle_sufficiency")
    need(b["conditional_branch"]=="PASS" and
         b["original_fullQ_source"]=="PINNED_PREMISE" and
         len(b["endpoints"])==2,"inertia_source")
    for k,p in enumerate(b["endpoints"]):
        need(p["energy_num"]==(lo,hi)[k] and p["energy_den"]==B and
             p["endpoint_count"]=="PASS" and
             p["nneg_lower"]==p["nneg_upper"]==i+k and
             p["nzero_lower"]==p["nzero_upper"]==0,"true_energy_branch_endpoint")
    v=vector(pair[("original_E1_recenter_v","original_E2_recenter_v")[i]])
    srcsha=pair[("original_E1_recenter_sha256","original_E2_recenter_sha256")[i]]
    need(sha(",".join(map(str,v)).encode("ascii"))==srcsha,"original_matched_witness_SHA")
    need(s["sample_num"]==z and s["selected_fraction_num"]==s["selected_fraction_den"]==4 and
         vector(s["source_matched_direction"])==tuple(4*x for x in v),"same_source_matched_direction")
    return angle
def action(raw,pair,angles):
    inp=one(raw,"Y137_MATCHED_ACTION_INPUT")
    bound=one(raw,"Y137_MATCHED_ACTION_BOUND")
    graph=one(raw,"Y137_MATCHED_ACTION_GRAPH")
    dual=one(raw,"Y137_JOINT_DUAL_AUDIT")
    need(graph=={"original_PQ_edges":"264",
                "matched_E1_forward_independent_flat_row":"PASS",
                "matched_E2_adjoint_independent_flat_row":"PASS",
                "physical_weighted_PQ_adjoint":"PASS",
                "first_original_Wilson_weight":"HOLD","json":"0"},"original_264_PQ_rows")
    need(inp["source_original_flat_W"]==",".join(map(str,W)),"Wilson_same_W")
    v1=vector(pair["original_E1_recenter_v"])
    v2=vector(pair["original_E2_recenter_v"])
    n1=sum(W[i]*v1[i]*v1[i] for i in range(8))
    n2=sum(W[i]*v2[i]*v2[i] for i in range(8))
    need((n1,n2)==(5985138300502958552,6011785104049132129) and
         (int(inp["n1"]),int(inp["n2"]))==(n1,n2),"same_original_flat_norms")
    f=vector(inp["forward_raw"]);a=vector(inp["adjoint_raw"])
    vfw=sum(v2[i]*f[i] for i in range(8))
    vad=sum(v1[i]*a[i] for i in range(8))
    need((int(inp["forward_W_bilinear"]),int(inp["adjoint_W_bilinear"]))==
         (vfw,vad),"source_forward_adjoint_bilinears")
    fn=n2*sum((6//W[i])*f[i]*f[i] for i in range(8))-6*vfw*vfw
    an=n1*sum((6//W[i])*a[i]*a[i] for i in range(8))-6*vad*vad
    need(fn>=0 and an>=0,"source_deflation_Cauchy")
    f0=up_root(fn,6*n2*n1*U*U)
    a0=up_root(an,6*n1*n2*U*U)
    g1,g2,d21,d12=(int(inp[k]) for k in
        ("g1_residual_norm2_scaled","g2_residual_norm2_scaled",
         "d21_residual_norm2_scaled","d12_residual_norm2_scaled"))
    need(min(g1,g2,d21,d12)>=0,"signed_Q_residuals")
    gap1,gap2=GAPS
    need((int(inp["gap1_num"]),int(inp["gap2_num"]))==GAPS and
         (int(inp["e1_window_width_num"]),int(inp["e2_window_width_num"]))==
         (157135,169737),"same_Perron_floor_and_energy_windows")
    e21=ceildiv(ceilroot(d21)*PS,gap2)
    e12=ceildiv(ceilroot(d12)*PS,gap1)
    eq1=ceildiv(30*ceilroot(g1)*B*PS*PS,gap1*gap2)
    eq2=ceildiv(30*ceilroot(g2)*B*PS*PS,gap1*gap2)
    fe=up_root(72*(e21+eq1)*(e21+eq1),n1*U*U)
    ae=up_root(72*(e12+eq2)*(e12+eq2),n2*U*U)
    drift=ceildiv(72*30*B*B*PS*PS*PS*U*
                  (157135*gap2+169737*gap1),gap1*gap1*gap2*gap2)
    fw=f0+fe+drift;adj=a0+ae+drift
    op=30*U+ceildiv(30*72*B*B*PS*PS*U,gap1*gap2)
    comparison={
      "nominal_forward_deflated_per_trillion":f0,
      "nominal_adjoint_deflated_per_trillion":a0,
      "forward_direct_dual_Q_error_per_trillion":fe,
      "adjoint_direct_dual_Q_error_per_trillion":ae,
      "true_energy_matrix_drift_per_trillion":drift,
      "forward_source_action_upper_per_trillion":fw,
      "adjoint_source_action_upper_per_trillion":adj,
      "physical_effective_M9_norm_upper_per_trillion":op,
    }
    for k,v in comparison.items():need(int(bound[k])==v,"raw_Q_action_"+k)
    need(int(dual["fixed_shifted_weight_ppb_floor"])==3864421 and
         int(inp["amp_source_ppb"])==3864421,"original_fixed_sample_signal")
    amp=isqrt(3864421*U*U//B)
    need(amp==62164467342 and int(bound["matched_fixed_amp_lower_per_trillion"])==amp,
         "original_signed_signal")
    def margin(s1,s2):
        signal=amp*isqrt(U*U-s1*s1)*isqrt(U*U-s2*s2)//(U*U)
        p1=ceildiv(s1*adj,U)
        p2=ceildiv(s2*fw,U)
        mixed=ceildiv(s1*s2*op,U*U)
        return signal-p1-p2-mixed,(signal,p1,p2,mixed)
    old,ov=margin(*SINE0)
    need(old==47724563 and int(bound["signed_true_flat_transition_margin_per_trillion"])==old,
         "original_Wilson_451_ppt_source")
    for key,v in zip(("phase_cosine_signal_lower_per_trillion",
      "E1_directional_penalty_per_trillion","E2_directional_penalty_per_trillion",
      "two_angles_penalty_per_trillion"),ov):
        need(int(bound[key])==v,"original_source_action_bound_"+key)
    need(bound["mixed_projector_cosine_upper"]=="ONE_EXACT" and
         bound["actual_first_Wilson_weight"]=="HOLD","frozen_scientific_scope")
    new,nv=margin(*angles)
    need(new==9285530088 and nv==(62163774481,25196361952,27389725641,292156800),
         "new_positive_signed_Wilson_action")
    num=new*new*gap1*gap1*gap2*gap2
    den=4*U*U*(gap1*gap1+72*B*B*PS*PS)*(gap2*gap2+72*B*B*PS*PS)
    ppt=num*U//den
    dg=sha((str(num)+"/"+str(den)).encode("ascii"))
    need(ppt==17074763 and
         dg=="7a8255cfb82207653ef3050b1efba0cedda61a309c3084e6a8a50b42deb7abf0",
         "full_original_O_not_O9_normalized")
    return new,ppt,dg
def forged_controls(ir,br,sm,pair,raw):
    # Independent semantic mutations after the frozen SHA and file-level gates.
    tests=[]
    def add(target,field,replacement,idx=0):
        a,b,c=copy.deepcopy(ir),copy.deepcopy(br),copy.deepcopy(sm)
        p=copy.deepcopy(pair)
        targetobj={"interval":a[idx],"branch":b[idx],"sample":c[idx],"pair":p}[target]
        targetobj[field]=replacement
        tests.append((a,b,c,p,raw))
    add("interval","source_weight_metric","1,1,1,1,1,1,1,1")
    add("interval","interval_lo","0")
    add("interval","interval_projected_residual_upper","1")
    add("interval","interval_compressed_singular_lower","1/10000")
    add("interval","target_sine","1/100000")
    add("interval","source_Q_norm_upper","1")
    add("sample","source_matched_direction","0,0,0,0,0,0,0,0")
    add("pair","original_E2_recenter_v","1,1,1,1,1,1,1,1")
    for field,old,new in [
       ("original_PQ_edges=264","264","263"),
       ("mixed_projector_cosine_upper=ONE_EXACT","ONE_EXACT","LOWER"),
       ("forward_W_bilinear=","=","=77"),
       ("signed_true_flat_transition_margin_per_trillion=47724563","47724563","1")]:
        need(field in raw,"negative_original_fixture_"+field)
        changed=raw.replace(field,field.replace(old,new),1)
        tests.append((copy.deepcopy(ir),copy.deepcopy(br),copy.deepcopy(sm),copy.deepcopy(pair),changed))
    count=0
    for a,b,c,p,act in tests:
        try:
            args=(branch_angle(0,a[0],b[0],c[0],p),
                  branch_angle(1,a[1],b[1],c[1],p))
            action(act,p,args)
        except (ValueError,KeyError,TypeError,IndexError,ZeroDivisionError):
            count+=1
        else:raise ValueError("forged_accepted")
    need(count==12,"adversarial_count")
    return count
def audit(diagnostic,source):
    with Artifact(diagnostic) as a,Artifact(source) as b:
        raw=get_zip(b,"ALL.hbp")
        need(raw==get_zip(a,"original-Wilson/ALL.hbp","ALL.hbp"),
             "two_original_frozen_hosted_artifacts_equal")
        commit=get_zip(b,"COMMIT.txt")
        need(commit.strip()=="abb9d910b343c003d7985a6973211fe71e297803",
             "original_action_producer_commit")
        interval=get_zip(a,"interval.jsonl")
        branch=get_zip(a,"branch.jsonl")
        sample=get_zip(a,"samples.jsonl")
        tightened=get_zip(a,"TIGHTENED-WILSON.hbp")
        ir=jrows(interval,"Y137_SCHUR_INTERVAL_DIRECTIONAL")
        br=jrows(branch,"Y137_ENDPOINT_BRANCH")
        sm=jrows(sample,"Y137_SCHUR_SAMPLE_DIAGNOSTIC")
        pair=one(raw,"Y137_MATCHED_PAIR")
        angles=tuple(branch_angle(i,ir[i],br[i],sm[i],pair) for i in range(2))
        margin,ppt,weightsha=action(raw,pair,angles)
        r=jrows(tightened,"Y137_TIGHTENED_ORIGINAL_WILSON",1)[0]
        need((r["new_E1_projector_sine_per_trillion"],
              r["new_E2_projector_sine_per_trillion"])==angles and
             r["new_signed_O9_margin_lower_per_trillion"]==margin and
             r["new_original_Wilson_squared_weight_ppt_floor"]==ppt and
             r["new_weight_rational_SHA256"]==weightsha and
             r["first_Wilson_formal"]=="HOLD","original_tightened_result_byte_reference")
        tests=forged_controls(ir,br,sm,pair,raw)
    return margin,ppt,tests
def main():
    need(len(sys.argv)==3,"usage: verify_joined.py DIAGNOSTIC_DIR_OR_ZIP ACTION_DIR_OR_ZIP")
    margin,ppt,tests=audit(sys.argv[1],sys.argv[2])
    print("Y137_JOINED_ORIGINAL_WILSON|two_hosted_archives=SHA256_PASS"+
          "|true_E1_E2_branches=2_PASS|true_projector_cones=2_PASS"+
          "|source_correlated_original_W_action=INDEPENDENT_ARITHMETIC_PASS"+
          "|matched_original_Q_scope=SOURCE_PINNED"+
          "|signed_O9_margin_ppt="+str(margin)+"|original_squared_Wilson_weight_ppt="+str(ppt)+
          "|altered_controls="+str(tests)+"_REJECTED"+
          "|full_raw_Q_dual_independent_production=EXTERNAL_ACCEPTANCE_REQUIRED"+
          "|original_finite_Wilson=SOURCE_CONDITIONAL_FORMAL_HOLD|continuum_4D=OPEN|json=0")
if __name__=="__main__":
    try:main()
    except (ValueError,KeyError,TypeError,IndexError,ZeroDivisionError) as exc:
        print("Y137_JOINED_WILSON_REFUSE|reason="+str(exc)+"|json=0")
        raise SystemExit(2)
