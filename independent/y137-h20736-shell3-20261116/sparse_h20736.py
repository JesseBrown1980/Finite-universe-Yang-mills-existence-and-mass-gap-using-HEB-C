#!/usr/bin/env python3
"""#137 authenticated 20,736-dimensional sparse generalized Galerkin matrix.

Exact physical gauge-quotient S3 3x4 r=9. Retain the original verified
144-dimensional basis and append 20,592 shell-3 coordinate orbit indicators.
No dense 20,736x20,736 allocation. Build the exact integer weighted sparse
K and diagonal/block Gram G. The 72-move physical source is enumerated for
EVERY added shell-3 coordinate; exact weighted reciprocal pair checks protect
all selected-to-selected and selected-to-K2 transitions.

This certifies the sparse projected matrix and source support ONLY, not a new
20,736-dimensional Ritz root or a full-space residual/angle/Wilson certificate.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
H144 = os.path.join(ROOT, "independent", "y137-h144-nested-20261116")
H144_CODE = os.path.join(H144, "nested_ritz.py")
H144_CODE_BLOB = "9d2f80f1d062b9b9f01e65ff9a1334e1045a51a3"
RANK = 20736
PARENT = 144
SHELL3_ADDED = RANK-PARENT
SHELL3_CENSUS = 147344
SOURCE_EXTERIOR_EDGES = 500664
UNIT = 1000000000
ORIGINAL_144_RITZ = (
    (69924497998, 69924497999),
    (69963565333, 69963565334),
)


def need(ok, reason):
    if not ok:
        print("Y137_H20736_REFUSE|reason="+reason+"|json=0", flush=True)
        raise SystemExit(1)


def emit(label, **kw):
    print(label + "|" + "|".join(str(k)+"="+str(v) for k,v in kw.items())
          + "|json=0", flush=True)


def sha(s):
    return hashlib.sha256(s.encode("ascii")).hexdigest()


def gitblob(path):
    raw=open(path,"rb").read()
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+
                        b"\x00"+raw).hexdigest()


def canonical_shell3(states, old_ball):
    """Recreate the exact original K2 exterior target ORDER and reciprocity."""
    import finite_s3_3x4_r9_first_gap as c
    where={key:i for i,key in enumerate(states)}
    n2=old_ball["n"]
    es=old_ball["es"]
    ext_keys=[]
    ext_index={}
    original_pairs=[]
    per_target=[]
    for i in range(n2):
        k=states[i+8]
        for dst,cc in c.neighbors(k).items():
            if dst in where:
                continue
            f=ext_index.get(dst)
            if f is None:
                f=len(ext_keys)
                ext_index[dst]=f
                ext_keys.append(dst)
                per_target.append([])
            per_target[f].append((i, old_ball["wq"][i]*cc))
    need(len(ext_keys)==old_ball["nf"]==SHELL3_CENSUS,
         "original_shell3_target_census")
    need(len(old_ball["esrc"])==SOURCE_EXTERIOR_EDGES,
         "original_K2_exterior_raw_record_count")
    for f,key in enumerate(ext_keys):
        need(c.weight(key)==old_ball["eW"][f],
             "original_shell3_weight_and_address_order")
        pair=per_target[f]
        a,b=es[f],es[f+1]
        need(b-a==len(pair),"shell3_edge_count_not_identical")
        for x,(i,wc) in enumerate(pair):
            need(int(old_ball["esrc"][a+x])==i and
                 int(old_ball["ewc"][a+x])==wc,
                 "source_exterior_weighted_edge_sha_mismatch")
    return ext_keys,ext_index,where


def source_score(ball, cols):
    """Exact, deterministic importance score from original 144-source actions."""
    scores=[]
    wq=ball["wq"]
    for f in range(ball["nf"]):
        a,b=ball["es"][f],ball["es"][f+1]
        total=0
        strong=0
        for idx in range(a,b):
            i=int(ball["esrc"][idx])
            flux=int(ball["ewc"][idx])
            total+=flux
            strong+=flux*(abs(cols[2][i])+abs(cols[3][i]))
        scores.append((strong,total,f))
    scores.sort(key=lambda t:(-t[0],-t[1],t[2]))
    return scores[:SHELL3_ADDED]


def original144():
    import nested_ritz as m
    G12,K12=m.load_h12()
    ball,states,cols,actions=m.sources()
    selected,score=m.select(ball,cols,actions)
    G,K=m.expanded_matrices(ball,cols,actions,selected,G12,K12)
    gramrank,_=m.gram_rank(G,selected,cols,ball)
    need(gramrank>0,"original_H144_rank_not_positive")
    groups=m.group_schur(ball,cols,actions,selected)
    brackets=[m.exact_bracket(k,G12,K12,groups) for k in (1,2)]
    need(tuple(brackets)==ORIGINAL_144_RITZ,
         "original_144_Ritz_frozen_mismatch")
    need(len(G)==len(K)==PARENT,"original_144_dim_mismatch")
    return G,K,ball,states,cols,selected,brackets


def selected_row_graph(keys,index,where,chosen,ball):
    """Independent physical 72-move shell3 rows plus all reverse controls."""
    import finite_s3_3x4_r9_first_gap as c
    selidx={f:t for t,f in enumerate(chosen)}
    wE=ball["eW"]
    wq=ball["wq"]
    es=ball["es"]
    orig_rec=ball["esrc"]
    orig_flux=ball["ewc"]
    qN=ball["n"]

    # Exact source K2-to-shell3 edge entries in sparse cross-block.
    qcross=[]
    hdiag=[]
    edge_upper=[]
    all_neighbors=[]
    total_raw=0
    cross_records=0
    selfloop_sum=0
    boundary_events=0
    for t,f in enumerate(chosen):
        key=keys[f]
        wf=wE[f]
        neigh=c.neighbors(key)
        need(sum(neigh.values())==72,"shell3_72_electric_row")
        mag=c.magnetic(c.from_key(key))
        selfc=neigh.get(key,0)
        diag=72+9*mag-selfc
        need(diag>=72 and wf in (1,2,3,6),"shell3_diagonal_or_weight")
        hdiag.append(wf*diag)
        selfloop_sum+=selfc
        q_expected={}
        a,b=es[f],es[f+1]
        for u in range(a,b):
            src=int(orig_rec[u])
            weightflux=int(orig_flux[u])
            q_expected[src]=q_expected.get(src,0)+weightflux
        qfound={}
        local={}
        for dst,count in neigh.items():
            if dst==key:
                continue
            j=where.get(dst)
            if j is not None:
                need(j>=8,"new_shell3_neighbor_reaches_original_flat")
                src=j-8
                qfound[src]=qfound.get(src,0)+wf*count
                continue
            ext=index.get(dst)
            if ext is not None:
                s=selidx.get(ext)
                if s is not None:
                    local[s]=local.get(s,0)+count
                else:
                    boundary_events+=count
            else:
                boundary_events+=count
        need(qfound==q_expected,"K2_shell3_exact_weighted_reverse")
        for src,flux in sorted(qfound.items()):
            qcross.append((src,t,flux))
        cross_records+=len(qfound)
        all_neighbors.append(local)
        total_raw+=sum(neigh.values())
        if t%3000==0:
            emit("Y137_H20736_PROGRESS",selected=t+1,
                 target=SHELL3_ADDED, raw_moves=total_raw)
    for t,row in enumerate(all_neighbors):
        for s,cnt in row.items():
            need(s!=t,"self_loop_double_count")
            need(cnt*wE[chosen[t]]==all_neighbors[s].get(t,0)*wE[chosen[s]],
                 "selected_shell3_weighted_reciprocity")
            if s>t:
                edge_upper.append((t,s,-wE[chosen[t]]*cnt))
    need(total_raw==72*SHELL3_ADDED,"raw_selected_move_count")
    return hdiag,qcross,edge_upper,total_raw,cross_records,selfloop_sum,boundary_events


def emit_sparse(G,K,ball,cols,selected,chosen,hdiag,qcross,edge_upper):
    """Deterministic sparse upper-triangular, integer W-Galerkin representation."""
    base=[]
    for i in range(PARENT):
        for j in range(i,PARENT):
            if G[i][j]:
                base.append(("G",i,j,G[i][j]))
            if K[i][j]:
                base.append(("K",i,j,K[i][j]))
    coord_to_col={src:PARENT-132+k for k,src in enumerate(selected)}
    cross={}
    for src,t,flux in qcross:
        for a in range(4):
            value=-flux*cols[a][src]
            if value:
                cross[(8+a,PARENT+t)]=cross.get((8+a,PARENT+t),0)+value
        col=coord_to_col.get(src)
        if col is not None:
            cross[(col,PARENT+t)]=cross.get((col,PARENT+t),0)-flux
    for (i,j),v in sorted(cross.items()):
        if v:
            base.append(("K",i,j,v))
    for t,dd in enumerate(hdiag):
        need(dd>0,"shell3_diagonal_not_positive")
        w=ball["eW"][chosen[t]]
        base.append(("G",PARENT+t,PARENT+t,w))
        base.append(("K",PARENT+t,PARENT+t,dd))
    for t,s,flux in edge_upper:
        base.append(("K",PARENT+t,PARENT+s,flux))
    base.sort(key=lambda x:(x[0],x[1],x[2]))
    counted=len(base)
    need(all(0<=i<=j<RANK and v for tag,i,j,v in base),
         "sparse_matrix_invalid_entry")
    need(len(set((tag,i,j) for tag,i,j,v in base))==counted,
         "duplicate_sparse_entry")
    digest=hashlib.sha256()
    out=os.path.join(ROOT,"build","y137-h20736")
    os.makedirs(out,exist_ok=True)
    path=os.path.join(out,"H20736-SPARSE-UPPER.tsv")
    with open(path,"w",encoding="ascii") as fd:
        for tag,i,j,v in base:
            line=tag+"\t"+str(i)+"\t"+str(j)+"\t"+str(v)+"\n"
            fd.write(line)
            digest.update(line.encode("ascii"))
    # Weighted full Gram rank follows by W-orthogonality of NEW shell3
    # indicators and original authenticated full-rank H144 Gram.
    need(len(chosen)==SHELL3_ADDED and len(hdiag)==SHELL3_ADDED,
         "shell3_basis_rank_mismatch")
    return counted,digest.hexdigest(),len(cross)


def original_primal_bounds(brackets):
    """Monotonic variational comparison; no new spectral root is asserted."""
    for k,interval in enumerate(brackets):
        need(tuple(interval)==ORIGINAL_144_RITZ[k],
             "inherited_Ritz_interval_mismatch")
    emit("Y137_H20736_VARIATIONAL",
         level1_upper_z_num=brackets[0][1],
         level2_upper_z_num=brackets[1][1],
         energy_den=UNIT,
         proof="INCLUSION_ONLY",
         new_20736_Ritz="NOT_COMPUTED",
         full_space_residual="NOT_COMPUTED",
         Wilson_weight="HOLD")


def main():
    need(gitblob(H144_CODE)==H144_CODE_BLOB,
         "original_H144_code_pin")
    sys.path.insert(0,H144)
    import nested_ritz as m
    G,K,ball,states,cols,selected,brackets=original144()
    # Resolve original original K2 checker through the authenticated H12
    # pinned loader rather than using a new gauge/neighbor implementation.
    sys.path.insert(0,os.path.join(ROOT,"independent",
                                    "y137-12x12-krylov-20261116"))
    import exact_krylov_12 as h12
    h12.source_module()
    keys,index,where=canonical_shell3(states,ball)
    score=source_score(ball,cols)
    chosen=[f for strong,total,f in score]
    need(len(set(chosen))==SHELL3_ADDED,
         "selected_shell3_repeat")
    addresses="\n".join(str(f)+":"+str(keys[f]) for f in chosen)
    emit("Y137_H20736_SOURCE",model="3x4_S3_r9",
         original_H144_code_blob=H144_CODE_BLOB,
         K2_nonflat_source_states=ball["n"],
         shell3_source_states=len(keys),
         new_shell3_indicators=SHELL3_ADDED,
         exact_basis_dimension=RANK,
         source_address_sha256=sha(addresses),
         selection="DESCENDING_EXACT_KRYLOV_FLUX",
         full_Ritz_level2_upper_source="H144")
    diag,qcross,edge_upper,moves,reverse,selfc,boundary=selected_row_graph(
        keys,index,where,chosen,ball)
    entries,digest,cross=emit_sparse(
        G,K,ball,cols,selected,chosen,diag,qcross,edge_upper)
    emit("Y137_H20736_MATRIX",basis_dim=RANK,
         full_dense_entries=RANK*RANK,
         upper_triangle_stored_nonzero=entries,
         sparse_TSV_sha256=digest,
         full_Gram_rank="20736_BY_BLOCK_DIAGONAL_Q_ORBIT_WEIGHTS",
         original_144_principal_block="BYTE_IDENTICAL",
         weighted_H_hermiticity="EXACT_REVERSE_PAIR",
         selected_to_selected_pairs=len(edge_upper),
         selected_K2_shell3_cross_records=reverse,
         nonzero_K2_Krylov_cross_entries=cross,
         raw_new_source_moves=moves,
         self_loops=selfc,
         outside_trial_basis_moves=boundary,
         original_source_full_state_dim="2177317873",
         Ritz20736="NOT_COMPUTED",
         Wilson_weight="HOLD")
    original_primal_bounds(brackets)
    emit("Y137_H20736_VERDICT",
         matrix="EXACT_SPARSE_PHYSICAL_W_GALERKIN",
         dimension=RANK,
         source_consistency="K2_TO_SHELL3_WEIGHTED_REVERSE_PASS",
         full_matrix_dense_export="NOT_REQUIRED",
         Ritz_20736="HOLD",
         full_support_residual="NOT_COMPUTED",
         true_eigenspace_angle="HOLD",
         first_Wilson_weight="HOLD",
         issue_137="OPEN")


if __name__=="__main__":
    if sys.argv[1:]==["real"]:
        main()
    else:
        need(False,"use_real")
