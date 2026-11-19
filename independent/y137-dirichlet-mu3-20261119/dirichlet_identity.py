#!/usr/bin/env python3
"""Exact-integer eight-channel Dirichlet identity for original weighted mu3.

Full physical Q signed response V1 on the 3x4 S3 torus, W_i=6*w_i,
D_i=b(72+9*m_i)-z, and detailed-balance weighted electric edges imply:

  mu3_six = V1^T W (D-bC) V1
          = sum_i W_i(b*9*m_i-z) V_i V_i^T
            + b sum_{i<j in Q} W_i c_ij (V_i-V_j)(V_i-V_j)^T
            + b sum_{i in Q,j outside Q} W_i c_ij V_i V_i^T.

The last term includes EVERY exterior supported-to-zero edge (including flats).
The formula is valid for true self loops: they contribute zero to the squared
difference. It does not assume graph symmetry without checking the weighted
reversibility relation W_i c_ij = W_j c_ji.

This module intentionally contains a source-free 8x8 integer control first.
Production full 20.74M original-state recomputation is a separate gate.
"""
import hashlib
import sys

B=1000000000
RAW_DEGREE=72
LANES=8
ENERGIES=(69909875505,69949729820)

class Refuse(Exception):pass

def need(ok,why):
    if not ok:raise Refuse(why)

def zero():
    return [[0]*LANES for _ in range(LANES)]

def outer(acc,a,b,coefficient):
    need(len(a)==LANES and len(b)==LANES and
         isinstance(coefficient,int),"exact_8_flat_source")
    for i in range(LANES):
        for j in range(LANES):
            acc[i][j]+=coefficient*a[i]*b[j]

def encode(m):
    return ";".join(",".join(str(v) for v in row) for row in m)

def check_graph(weights,magnetic,edges,boundary,source):
    n=len(weights)
    need(n>=2 and len(magnetic)==n and len(edges)==n and
         len(boundary)==n and len(source)==n,
         "three_block_graph_shapes")
    need(all(w in (1,2,3,6) for w in weights),
         "physical_orbit_weights")
    need(all(0<=x<=36 for x in magnetic),"magnetic_range")
    need(all(len(v)==LANES and all(type(t) is int for t in v)
             for v in source),"eight_exact_integer_source_lanes")
    for i in range(n):
        adjacency=edges[i]
        need(isinstance(adjacency,dict),"directed_adjacency")
        degree=boundary[i]
        need(type(degree) is int and degree>=0,"nonnegative_boundary")
        for j,count in adjacency.items():
            need(type(j) is int and 0<=j<n and
                 type(count) is int and count>0,
                 "positive_real_directed_edges")
            degree+=count
            need(weights[i]*count==weights[j]*edges[j].get(i,0),
                 "weighted_reciprocal_electric_edge")
        need(degree==RAW_DEGREE,"all_72_raw_moves_with_boundary")
    return n

def direct(weights,magnetic,edges,boundary,source,z):
    n=check_graph(weights,magnetic,edges,boundary,source)
    result=zero()
    for i in range(n):
        acc=[(B*(72+9*magnetic[i])-z)*v for v in source[i]]
        for j,c in edges[i].items():
            for k in range(LANES):
                acc[k]-=B*c*source[j][k]
        outer(result,source[i],acc,6*weights[i])
    need(result==[list(col) for col in zip(*result)],
         "weighted_direct_8x8_not_symmetric")
    return result

def dirichlet(weights,magnetic,edges,boundary,source,z):
    n=check_graph(weights,magnetic,edges,boundary,source)
    result=zero()
    for i in range(n):
        # Original diagonal 72 has been split into supported graph degrees
        # and explicitly accounted for exterior Q boundary to zero.
        outer(result,source[i],source[i],
              6*weights[i]*(B*9*magnetic[i]-z+B*boundary[i]))
    for i in range(n):
        for j,count in edges[i].items():
            if i<j:
                difference=tuple(source[i][k]-source[j][k]
                                 for k in range(LANES))
                outer(result,difference,difference,6*B*weights[i]*count)
    need(result==[list(col) for col in zip(*result)],
         "Dirichlet_8x8_not_symmetric")
    return result

def physical_toy():
    # Three supported Q rows and an explicit exterior zero sector.
    # The directed S3-like multigraph has exact W-weighted reciprocity,
    # all 72 moves counted at each source, and nonzero boundary flux.
    w=(1,2,3)
    magnetic=(5,7,9)
    edges=({1:2,2:3},{0:1,2:3},{0:1,1:2})
    outside=(67,68,69)
    source1=(
        (3,-5,7,-11,13,-17,19,-23),
        (-29,31,-37,41,-43,47,-53,59),
        (61,-67,71,-73,79,-83,89,-97),
    )
    source2=(
        (-101,103,-107,109,-113,127,-131,137),
        (139,-149,151,-157,163,-167,173,-179),
        (181,191,-193,197,-199,211,-223,227),
    )
    cases=0
    for z,source in zip(ENERGIES,(source1,source2)):
        a=direct(w,magnetic,edges,outside,source,z)
        b=dirichlet(w,magnetic,edges,outside,source,z)
        need(a==b,"two_independent_signed_Mu3_matrices_differ")
        need(all(a[i][j]==a[j][i] for i in range(8) for j in range(8)),
             "matrix_64_entries_weighted_symmetry")
        digest=hashlib.sha256(encode(a).encode("ascii")).hexdigest()
        print("Y137_DIRICHLET_TOY_ENERGY|sample_num="+str(z)+
              "|source_rows=3|exterior_zero_rows=EXPLICIT"+
              "|real_72_degree_each=PASS"+
              "|weighted_reciprocity=PASS|matrix_entries=64"+
              "|row_vs_Dirichlet=EXACT|matrix_sha256="+digest+
              "|original_whole_Q=NOT_RECALCULATED|json=0",flush=True)
        cases+=1

    # Explicit wrong sign, omitted boundary, energy and link controls.
    fails=0
    def reject(f):
        nonlocal fails
        try:
            f()
        except Refuse:
            fails+=1
        else:raise Refuse("forged_exact_Dirichlet_control_accepted")
    # The same original direct matrix must disagree if a source is changed
    # or a physical boundary term is dropped.
    baseline=direct(w,magnetic,edges,outside,source1,ENERGIES[0])
    def force_equal(a,b):
        need(a==b,"intentionally_modified_matrix_rejected")
    def flip_source():
        modified=list(source1)
        modified[1]=tuple(-x for x in source1[1])
        force_equal(baseline,dirichlet(w,magnetic,edges,outside,modified,ENERGIES[0]))
    def lost_boundary():
        modified=dirichlet(w,magnetic,edges,outside,source1,ENERGIES[0])
        # Compare the corrupt no-exterior-energy expression.
        for i in range(len(w)):
            outer(modified,source1[i],source1[i],-6*w[i]*B*outside[i])
        force_equal(baseline,modified)
    def wrong_z():
        force_equal(baseline,dirichlet(w,magnetic,edges,outside,source1,ENERGIES[1]))
    def wrong_factor6():
        force_equal(baseline,[[v//6 for v in row] for row in baseline])
    def bad_flux():
        edges2=({1:1,2:3},{0:1,2:3},{0:1,1:2})
        direct(w,magnetic,edges2,outside,source1,ENERGIES[0])
    def missing_raw_move():
        direct(w,magnetic,edges,(67,68,68),source1,ENERGIES[0])
    def wrong_negative_source():
        modified=list(source1)
        modified[0]=tuple(abs(x) for x in modified[0])
        force_equal(baseline,dirichlet(w,magnetic,edges,outside,modified,ENERGIES[0]))
    def missing_link_pair():
        changed=dirichlet(w,magnetic,edges,outside,source1,ENERGIES[0])
        difference=tuple(source1[0][k]-source1[1][k] for k in range(8))
        outer(changed,difference,difference,-6*B*w[0]*edges[0][1])
        force_equal(baseline,changed)
    for f in (flip_source,lost_boundary,wrong_z,wrong_factor6,
              bad_flux,missing_raw_move,wrong_negative_source,
              missing_link_pair):
        reject(f)
    need(fails==8 and cases==2,"exact_Mu3_toy_control_census")
    print("Y137_DIRICHLET_TOY_VERDICT|two_signed_energies=PASS"+
          "|two_8x8_matrices_128_entries=EXACT"+
          "|weighted_reciprocity=PASS|all_72_raw_moves=PASS"+
          "|zero_source_boundary=EXPLICIT"+
          "|altered_source_boundary_factor_energy_pair_controls=8_REJECTED"+
          "|full_20M_signed_mu3=INDEPENDENT_RECOMPUTATION_OPEN"+
          "|first_Wilson_weight=SOURCE_CONDITIONAL_FORMAL_HOLD"+
          "|continuum_4D=OPEN|json=0",flush=True)

def main():
    try:
        need(sys.argv[1:]==["toy"],"usage_toy")
        physical_toy()
    except (Refuse,KeyError,ValueError,OSError) as exc:
        print("Y137_DIRICHLET_REFUSE|reason="+str(exc)+
              "|first_Wilson_weight=FORMAL_HOLD|json=0",flush=True)
        raise SystemExit(2) from None

if __name__=="__main__":main()
