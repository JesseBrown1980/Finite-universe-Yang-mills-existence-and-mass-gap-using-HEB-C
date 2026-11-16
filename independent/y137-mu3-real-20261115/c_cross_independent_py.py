#!/usr/bin/env python3
"""#137 independent Python 3x4 S3 K3/Q4 electric census for cross-block audit.

Reuses ONLY the historical frozen Python gauge-fixing and source builder,
independent of Stage C's copied B4 Rust operator. Enumerates all actual
155378 K3 + 1985218 Q4 rows in 9 source ranges, 72 raw moves per row.
Classifies each destination into K3, Q4, excluded flat, or exterior candidate
and authenticates original K3→Q4 weighted reverse counts on every Q4 row.

The exterior candidate is NOT silently called Q5; full frozen Q5 source
membership is established separately by Rust full-graph job. The Python
result is a separate exact block-census and cross-flux control, not by itself
a pair-by-pair cross-block proof or any physical μ3.
"""
import hashlib
import os
import sys

ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,os.path.join(ROOT,"independent","y137-real-Q-moment-20261114"))
ARGS=sys.argv[:]
sys.argv=sys.argv[:1]
import mu1_shard as src
sys.argv=ARGS

B=1000000000
Z=(69909875505,69949729820)
K3=155378
Q4=1985218
PARTS=8

class Refuse(Exception):
    pass

def need(ok,why):
    if not ok: raise Refuse(why)

def original():
    ball,ex,inner,flat,width,mask,items=src.build_inputs()
    need(ball["n"]==K3 and ball["nf"]==Q4
         and len(ex["s4"])==Q4 and len(inner)==K3
         and tuple(row[0] for row,_,_,_ in items)==Z,
         "C_PY_wrong_historical_signed_source")
    return ball,ex,inner,flat,items

def per_key(address,weight,key,ball,ex,inner,flat,digest,sums):
    need(src.m.code(key)==address,"C_PY_address_encoding")
    need(src.c.canonical(src.c.from_key(key))==key,"C_PY_not_S3_canonical")
    need(src.c.weight(key)==weight,"C_PY_wrong_orbit_weight")
    m=src.c.magnetic(src.c.from_key(key))
    need(0<=m<=36,"C_PY_invalid_magnetic")
    near=src.c.neighbors(key)
    need(sum(near.values())==72,"C_PY_not_72_raw_moves")
    sums["rows"]+=1
    sums["moves"]+=72
    sums["magnetic_sum"]+=m
    got_inner={}
    digest.update((str(address)+"|"+str(weight)+"|").encode("ascii"))
    for dst,c in sorted(near.items(),key=lambda x:src.m.code(x[0])):
        need(1<=c<=72,"C_PY_invalid_edge_multiplicity")
        target=src.m.code(dst)
        digest.update((str(target)+":"+str(c)+",").encode("ascii"))
        j=inner.get(dst)
        if j is not None:
            sums["to_k3"]+=c
            sums["flux_k3"]+=weight*c
            got_inner[j]=c
        elif target in ex["s4"]:
            sums["to_q4"]+=c
            sums["flux_q4"]+=weight*c
        elif dst in flat:
            sums["to_flat"]+=c
        else:
            # Must be compared to independent full Q5 membership, not assumed.
            sums["to_outside_signed_nonflat"]+=c
        if dst==key:
            sums["selfloop"]+=c
    digest.update(b";")
    return got_inner

def expected_q4_reverse(ball,f):
    result={}
    weight=ball["eW"][f]
    for e in range(ball["es"][f],ball["es"][f+1]):
        weighted=ball["ewc"][e]
        need(weighted%weight==0,"C_PY_original_reverse_weight_division")
        j=ball["esrc"][e]
        result[j]=result.get(j,0)+weighted//weight
    return result

def process_group(group):
    need(0<=group<=PARTS,"C_PY_bad_source_shard")
    ball,ex,inner,flat,items=original()
    mode="K3" if group==PARTS else "Q4"
    sums={k:0 for k in ("rows","moves","to_k3","to_q4",
                       "to_flat","to_outside_signed_nonflat",
                       "flux_k3","flux_q4","selfloop","magnetic_sum")}
    digest=hashlib.sha256()
    if mode=="K3":
        inverse=[None]*K3
        for key,i in inner.items():
            need(0<=i<K3 and inverse[i] is None,"C_PY_bad_K3_inverse")
            inverse[i]=key
        need(all(k is not None for k in inverse),"C_PY_missing_K3_inverse")
        lo,hi=0,K3
        for i,key in enumerate(inverse):
            per_key(src.m.code(key),src.c.weight(key),key,ball,ex,
                    inner,flat,digest,sums)
            if (i+1)%50000==0:
                print("Y137_C_PY_PROGRESS|shell=K3|rows="+str(i+1)+"|json=0",flush=True)
    else:
        lo=Q4*group//PARTS
        hi=Q4*(group+1)//PARTS
        for i in range(lo,hi):
            code=ex["code4"][i]
            key=src.m.decode(code)
            got=per_key(code,ball["eW"][i],key,ball,ex,inner,flat,digest,sums)
            need(got==expected_q4_reverse(ball,i),
                 "C_PY_independent_Q4_original_K3_reverse_edge_mismatch")
            if (i-lo+1)%50000==0:
                print("Y137_C_PY_PROGRESS|shell=Q4|group="+str(group)+
                      "|rows="+str(i-lo+1)+"|json=0",flush=True)
    need(sums["rows"]==hi-lo and sums["moves"]==72*(hi-lo),
         "C_PY_incomplete_source_partition")
    need(sums["to_k3"]+sums["to_q4"]+sums["to_flat"]+
         sums["to_outside_signed_nonflat"]==sums["moves"],
         "C_PY_missing_outside_support_move_classification")
    row=("Y137_C_PY_BLOCK|shell="+mode+"|group="+str(group)+
        "|start="+str(lo)+"|stop="+str(hi)+"|rows="+str(sums["rows"])+
        "|raw_moves="+str(sums["moves"])+
        "|to_K3="+str(sums["to_k3"])+
        "|to_Q4="+str(sums["to_q4"])+
        "|to_flat="+str(sums["to_flat"])+
        "|to_outside_signed_nonflat="+str(sums["to_outside_signed_nonflat"])+
        "|weighted_to_K3="+str(sums["flux_k3"])+
        "|weighted_to_Q4="+str(sums["flux_q4"])+
        "|true_selfloop_moves="+str(sums["selfloop"])+
        "|magnetic_sum="+str(sums["magnetic_sum"])+
        "|all_row_edges_sha256="+digest.hexdigest()+
        "|original_K3_UG_E1="+str(items[0][0][4])+","+
                                 str(items[0][0][5])+
        "|original_K3_UG_E2="+str(items[1][0][4])+","+
                                 str(items[1][0][5])+
        "|original_Q4_K3_reverse=EXACT"+
        "|candidate_Q5_membership=CHECK_FULL_RUST_GRAPH"+
        "|whole_mu3=NOT_COMPUTED|Wilson_weight=HOLD|json=0")
    print(row,flush=True)

def parse(line):
    pieces=line.strip().split("|")
    need(pieces[0]=="Y137_C_PY_BLOCK","C_PY_receipt_type")
    out={}
    for token in pieces[1:]:
        k,sep,v=token.partition("=")
        need(bool(sep) and k not in out,"C_PY_duplicate_receipt_field")
        out[k]=v
    need(out.get("json")=="0","C_PY_receipt_json_marker")
    return out

def aggregate(folder):
    allrows=[]
    for group in range(9):
        path=os.path.join(folder,"GROUP-"+str(group)+".hbp")
        lines=open(path,encoding="ascii").read().splitlines()
        data=[parse(t) for t in lines if t.startswith("Y137_C_PY_BLOCK|")]
        need(len(data)==1,"C_PY_missing_or_duplicate_source_group")
        r=data[0]
        need(int(r["group"])==group and
             r["shell"]==("K3" if group==8 else "Q4"),
             "C_PY_invalid_original_group")
        need(int(r["raw_moves"])==int(r["rows"])*72 and
             r["original_Q4_K3_reverse"]=="EXACT",
             "C_PY_group_raw_degree_or_sign_regression")
        allrows.append(r)
    counts=[sum(int(r[k]) for r in allrows) for k in
            ("rows","raw_moves","to_K3","to_Q4",
             "to_flat","to_outside_signed_nonflat")]
    need(counts[0]==K3+Q4 and counts[1]==72*(K3+Q4),
         "C_PY_global_original_K3_Q4_count")
    k3_flux=int(allrows[8]["weighted_to_Q4"])
    q4_reverse=sum(int(r["weighted_to_K3"]) for r in allrows[:8])
    need(k3_flux==q4_reverse,
         "C_PY_K3_Q4_full_weighted_cross_flux_mismatch")
    print("Y137_C_PY_CROSS_VERDICT|K3_Q4_rows="+str(counts[0])+
          "|K3_Q4_raw_moves="+str(counts[1])+
          "|to_K3="+str(counts[2])+"|to_Q4="+str(counts[3])+
          "|to_flat="+str(counts[4])+
          "|to_outside_signed_nonflat="+str(counts[5])+
          "|K3_Q4_weighted_flux="+str(k3_flux)+
          "|Q4_K3_weighted_reverse_flux="+str(q4_reverse)+
          "|all_9_actual_source_groups=PASS"+
          "|full_K3_Q4_flux_balance=PASS"+
          "|independent_Python_S3_generator=PASS"+
          "|exhaustive_pair_by_pair_reciprocity=CHECK_RUST_C_GRAPH"+
          "|Q5_candidate_boundary_membership=CHECK_RUST_C_GRAPH"+
          "|whole_mu3=NOT_COMPUTED|Wilson_weight=HOLD|json=0")

def toy():
    keys=[]
    for raw in (0,1,2,3,4,5,6,8,9,12,17,19,25,32,64,81,99,125):
        k=src.c.canonical(src.c.from_key(src.m.decode(raw)))
        if k not in keys:keys.append(k)
    checked=0
    for key in keys:
        weight=src.c.weight(key)
        near=src.c.neighbors(key)
        need(sum(near.values())==72,"C_PY_toy_raw_degree")
        for dst,c in near.items():
            reverse=src.c.neighbors(dst).get(key,0)
            need(weight*c==src.c.weight(dst)*reverse,
                 "C_PY_toy_group_action_weighted_reciprocity")
            checked+=1
    need(checked>0,"C_PY_no_actual_S3_edges")
    print("Y137_C_PY_TOY|actual_S3_3x4_keys="+str(len(keys))+
          "|actual_weighted_pairs_checked="+str(checked)+
          "|weighted_reverse_identity=PASS"+
          "|real_K3_Q4=NOT_COMPUTED|whole_mu3=NOT_COMPUTED"+
          "|Wilson_weight=HOLD|json=0")

def main(argv):
    try:
        if argv==["toy"]:toy()
        elif len(argv)==2 and argv[0]=="group":process_group(int(argv[1]))
        elif len(argv)==2 and argv[0]=="aggregate":aggregate(argv[1])
        else:raise Refuse("C_PY_usage")
    except (Refuse,ValueError,KeyError,OSError) as e:
        print("Y137_C_PY_REFUSE|reason="+str(e)+"|json=0",flush=True)
        raise SystemExit(1) from None

if __name__=="__main__":
    main(sys.argv[1:])
