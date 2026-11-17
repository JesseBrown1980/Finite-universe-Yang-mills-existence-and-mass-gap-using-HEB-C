#!/usr/bin/env python3
"""Y137 Stage J: exact full old-to-new H20738 coupling C (20736 x 2).

Stacked on authenticated Stage I physical residual support:
  v_j = d (I-P_old) (D H - z_j) u_j, D=10**9, d=det(Schur Gram).
  C_aj = <old_basis_a, H v_j>_W.
Only 28,634 physical rows in the OLD basis support are needed: 8 flat,
8,034 K2 and 20,592 selected K3. Every row evaluates all 72 ORIGINAL
S3 electric moves, in eight reproducible disjoint source shards.

The full coupling is authenticated by the four exact frozen identities
  D u_i^T C_j = E_ij,  i,j in {1,2},
with E the original 2x2 residual-Gram numerator.

Computes neither a full 20738 Ritz root nor Wilson spectral weight.
Integer-only and no floating-point.
"""
import hashlib
import os
import sys

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
HTT=os.path.join(ROOT,"independent","y137-htt-streamed-20261116")
sys.path.insert(0,HTT)
import exact_htt_stream as h
from exact_htt_stream import finite_s3_3x4_r9_first_gap as physical
from exact_htt_stream import residual_projection as proj
from exact_htt_stream import full_trial_residual as old
from exact_htt_stream import D

NOLD=20736
ROWS=28634
SHARDS=8

def need(ok,tag):
    if not ok:
        print("Y137_CROSS_REFUSE|reason="+tag+"|json=0",flush=True)
        raise SystemExit(1)

def emit(tag,**kv):
    print(tag+"|"+"|".join(str(k)+"="+str(v) for k,v in kv.items())+"|json=0",flush=True)

def sha256_file(path):
    hs=hashlib.sha256()
    with open(path,"rb") as fd:
        for part in iter(lambda:fd.read(1<<20),b""):
            hs.update(part)
    return hs.hexdigest()

def old_basis():
    """Physical old rows; Krylov columns contribute on every K2 row."""
    ball,states,cols,s132=old.old_source()
    keys3,unused,unused_where=proj.h20.canonical_shell3(states,ball)
    s3=[f for score,total,f in proj.h20.source_score(ball,cols)]
    need(len(states)==8042 and ball["n"]==8034
         and len(s132)==132 and len(s3)==20592
         and len(set(s132))==132 and len(set(s3))==20592,
         "old_source_census_changed")
    selected={i:12+k for k,i in enumerate(s132)}
    rows=[]
    for i,key in enumerate(states[:8]):
        rows.append((key,i,ball["wf"][i]))
    for i in range(ball["n"]):
        rows.append((states[8+i],selected.get(i,-1),ball["wq"][i]))
    for t,f in enumerate(s3):
        rows.append((keys3[f],144+t,ball["eW"][f]))
    need(len(rows)==ROWS and
         len({key for key,b,w in rows})==ROWS,
         "old_support_not_28634_distinct_orbits")
    sha=hashlib.sha256()
    for key,idx,weight in rows:
        sha.update(bytes(key))
        sha.update(int(idx).to_bytes(4,"big",signed=True))
        sha.update(bytes((weight,)))
    return rows,cols,sha.hexdigest()

def weighted_old_row(key,weight,support):
    """Return (w Hv1, w Hv2) from the original physical H, no surrogate."""
    nei=physical.neighbors(key)
    need(sum(nei.values())==72,"not_72_original_electric_moves")
    magnetic=physical.magnetic(physical.from_key(key))
    need(0<=magnetic<=36,"magnetic_outside_original_plaquette_range")
    diag=72+9*magnetic
    s=support.get(key)
    out=[0,0] if s is None else [diag*s[0],diag*s[1]]
    for dst,count in nei.items():
        amplitudes=support.get(dst)
        if amplitudes is not None:
            out[0]-=count*amplitudes[0]
            out[1]-=count*amplitudes[1]
    return (weight*out[0],weight*out[1]),nei

def negative_controls():
    # A two-orbit weighted-reciprocal toy source:
    # W=(1,2), H diagonal 4, off-diagonal (-2,-1).
    s0,s1=3,5
    left=4*s0-2*s1
    reverse=s0*4+2*s1*(-1)
    need(left==reverse==2,"toy_weighted_reverse_identity")
    forged=s0*4+2*s1*(-2)
    need(forged!=left,"toy_nonreciprocal_edge_not_rejected")
    need(D*7==7*D and D*7!=8*D,"toy_exact_cross_identity")
    emit("Y137_CROSS_TOY",weighted_reverse="PASS",
         forged_reverse="REJECTED",
         frozen_cross_identity="EXACT_INTEGER",
         first_Wilson_weight="HOLD")

def pilot():
    ordered,support,gram,meta=h.new_scaled_vectors()
    rows,cols,old_sha=old_basis()
    indices=[0,1,7,8,9,8041,8042,8043,ROWS//2,ROWS-2,ROWS-1]
    checks=0
    for pos in indices:
        key,bidx,w=rows[pos]
        weighted,neighbors=weighted_old_row(key,w,support)
        for dst,count in neighbors.items():
            if dst not in support:
                continue
            rev=physical.neighbors(dst).get(key,0)
            need(w*count==support[dst][2]*rev,
                 "original_weighted_reverse_edge_mismatch")
            checks+=1
    need(checks>0,"no_original_source_reverse_checks")
    emit("Y137_CROSS_PILOT",old_rows=len(rows),
         original_moves=len(indices)*72,
         checked_reverse_edges=checks,
         source_support_sha256=meta["scaled_support_SHA256"],
         old_basis_sha256=old_sha,
         old_basis_dim=NOLD,
         full_coupling="NOT_COMPUTED",
         first_Wilson_weight="HOLD")

def shard(slot):
    need(0<=slot<SHARDS,"invalid_slot")
    ordered,support,gram,meta=h.new_scaled_vectors()
    rows,cols,old_sha=old_basis()
    folder=os.path.join(ROOT,"build","y137-cross")
    os.makedirs(folder,exist_ok=True)
    name=os.path.join(folder,"COUPLING-ROWS-"+str(slot)+".tsv")
    count=0
    with open(name,"w",encoding="ascii") as fd:
        for pos in range(slot,len(rows),SHARDS):
            key,idx,w=rows[pos]
            vals,neighbors=weighted_old_row(key,w,support)
            fd.write(str(pos)+"\t"+str(idx)+"\t"+str(vals[0])
                     +"\t"+str(vals[1])+"\n")
            count+=1
    need(count==(ROWS+SHARDS-1-slot)//SHARDS,
         "original_support_slot_partition")
    emit("Y137_CROSS_SHARD",slot=slot,shards=SHARDS,
         old_source_rows=count,raw_electric_moves=72*count,
         total_old_source_rows=ROWS,old_basis_dim=NOLD,
         old_basis_sha256=old_sha,
         source_support_sha256=meta["scaled_support_SHA256"],
         frozen_original_E11_SHA=meta["original_frozen_Gram_E11_SHA"],
         frozen_original_E12_SHA=meta["original_frozen_Gram_E12_SHA"],
         frozen_original_E22_SHA=meta["original_frozen_Gram_E22_SHA"],
         file_sha256=sha256_file(name),
         source_code_sha256=sha256_file(__file__),
         old_to_new_H="SHARD_EXACT",
         Wilson_weight="HOLD")

def parse_receipt(line):
    need(line.startswith("Y137_CROSS_SHARD|"),"invalid_shard_receipt")
    d={}
    for item in line.strip().split("|")[1:]:
        k,sep,v=item.partition("=")
        need(sep and k not in d,"duplicate_shard_receipt_key")
        d[k]=v
    need(d.get("json")=="0","invalid_receipt_trailer")
    return d

def fanin(folder):
    # Rebuild independently the ORIGINAL old-coordinate and Krylov basis,
    # not just a 20,736-entry unchecked array from external artifacts.
    rows,cols,old_sha=old_basis()
    need(len(rows)==ROWS,"old_basis_census_drift")
    values=[[0,0] for ignored in range(NOLD)]
    seen=set()
    source_sha=None
    total=0
    for slot in range(SHARDS):
        local=os.path.join(folder,"slice-"+str(slot))
        path=os.path.join(local,"COUPLING-ROWS-"+str(slot)+".tsv")
        receipt=os.path.join(local,"RESULT-CROSS-"+str(slot)+".hbp")
        need(os.path.isfile(path) and os.path.isfile(receipt),
             "missing_exact_source_shard_"+str(slot))
        lines=open(receipt,encoding="ascii").read().splitlines()
        need(len(lines)==1,"invalid_shard_receipt_line_count")
        q=parse_receipt(lines[0])
        need(int(q["slot"])==slot and int(q["shards"])==SHARDS
             and q["old_basis_sha256"]==old_sha
             and q["old_basis_dim"]==str(NOLD)
             and q["total_old_source_rows"]==str(ROWS)
             and q["Wilson_weight"]=="HOLD",
             "shard_source_census_or_scope_drift")
        if source_sha is None:
            source_sha=q["source_support_sha256"]
        need(q["source_support_sha256"]==source_sha,
             "physical_residual_source_shas_disagree")
        need(q["source_code_sha256"]==sha256_file(__file__),
             "source_code_SHA_across_shards_changed")
        for provenance,expected in (("COMMIT.txt",None),("SOURCE.sha256",None)):
            need(os.path.isfile(os.path.join(local,provenance)),
                 "missing_shard_source_provenance_"+provenance)
        expected_source=open(os.path.join(local,"SOURCE.sha256"),encoding="ascii").read().split()[0]
        need(expected_source==q["source_code_sha256"],
             "shard_source_provenance_checksum_mismatch")
        need(sha256_file(path)==q["file_sha256"],
             "source_shard_file_checksum_mismatch")
        with open(path,encoding="ascii") as fd:
            local_count=0
            for line in fd:
                parts=line.rstrip("\n").split("\t")
                need(len(parts)==4,"invalid_source_row_columns")
                pos,idx,a,b=map(int,parts)
                need(0<=pos<ROWS and pos%SHARDS==slot
                     and pos not in seen,"duplicate_or_wrong_source_row")
                need(idx==rows[pos][1],"source_basis_index_swapped")
                seen.add(pos)
                local_count+=1
                total+=1
                if idx>=0:
                    need(not values[idx][0] and not values[idx][1],
                         "duplicate_coordinate_basis_record")
                    values[idx][0]=a
                    values[idx][1]=b
                # The 4 non-coordinate Krylov old columns overlap all 8034
                # K2 physical coordinates, including selected indicators.
                if 8<=pos<8042:
                    i=pos-8
                    for j in range(4):
                        coeff=cols[j][i]
                        values[8+j][0]+=coeff*a
                        values[8+j][1]+=coeff*b
        need(local_count==int(q["old_source_rows"])
             and int(q["raw_electric_moves"])==72*local_count,
             "shard_electric_row_count_mismatch")
    need(total==ROWS and len(seen)==ROWS
         and seen==set(range(ROWS)),
         "missing_original_support_coordinate")
    den,e=h.frozen_gram()
    need(den>0,"frozen_gram_denominator")
    # Original integer Ritz trial coefficients in the SAME old-basis order.
    entries,old_sparse_sha,trials,ball,states,original_cols,s132,keys3,index3,where,s3,indexer,nested=proj.pinned()
    need(len(trials)==2 and len(trials[0][1])==NOLD
         and len(trials[1][1])==NOLD,
         "frozen_trial_vectors_missing")
    need([t[0] for t in trials]==[69924497999,69963565334],
         "frozen_trial_z_changed")
    need(len(s132)==132 and len(s3)==20592,
         "original_basis_selection_changed")
    # Four independent frozen exact bilinear identities, no rounding:
    # <u_i,H v_j> = <(D H-z_i)u_i, v_j>/D
    #              = <t_i, d t_j>/D = E_num[i,j]/D.
    for i,(z,x) in enumerate(trials):
        for j in range(2):
            actual=D*sum(x[a]*values[a][j] for a in range(NOLD))
            need(actual==e[i][j],
                 "FROZEN_CROSS_GRAM_IDENTITY_FAILED_"+str(i)+str(j))
    out=os.path.join(ROOT,"build","y137-cross-final")
    os.makedirs(out,exist_ok=True)
    path=os.path.join(out,"H20736x2-CROSS-EXACT.tsv")
    with open(path,"w",encoding="ascii") as fd:
        for i,(a,b) in enumerate(values):
            fd.write(str(i)+"\t"+str(a)+"\t"+str(b)+"\n")
    need(sum(1 for a,b in values if a or b)>0,
         "full_cross_block_zeros")
    emit("Y137_CROSS_MATRIX",old_dim=NOLD,new_dim=2,
         exact_entries=NOLD*2,original_source_rows=ROWS,
         original_raw_electric_moves=ROWS*72,
         original_basis_sha256=old_sha,
         residual_physical_source_sha256=source_sha,
         old_sparse_matrix_sha256=old_sparse_sha,
         C_file_sha256=sha256_file(path),
         frozen_Gram_numerator_identities="4_OF_4_PASS",
         old_noncoordinate_Krylov_columns="4_OF_4_INCLUDED",
         Htt="STAGE_I_FROZEN_EXACT",
         full_20738_Ritz="NOT_COMPUTED",
         first_Wilson_weight="HOLD")
    emit("Y137_CROSS_VERDICT",full_old_to_new_H="ACCEPTED_EXACT_20736x2",
         source_shards="8_OF_8",old_to_new_G="ZERO_BY_FROZEN_PROJECTION",
         source_integrity="PASS",issue_137="OPEN",
         first_Wilson_weight="HOLD")

if __name__=="__main__":
    args=sys.argv[1:]
    if args==["toy"]:
        negative_controls()
    elif args==["pilot"]:
        pilot()
    elif len(args)==2 and args[0]=="shard":
        shard(int(args[1]))
    elif len(args)==2 and args[0]=="fanin":
        fanin(args[1])
    else:
        need(False,"usage_toy_pilot_shard_SLOT_fanin_DIR")
