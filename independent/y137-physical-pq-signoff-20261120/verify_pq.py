#!/usr/bin/env python3
"""Independent original finite 3x4 S3 physical P/Q boundary and Wilson signoff.

From permutation multiplication, enumerate all 8 flat gauge orbits, all 264
direct P-to-Q boundary orbits, full 72-move electric rows on both sides,
weighted exact adjoint, BstarB=72I and the diagonal 7-winding Wilson action.
Imports none of the historical graph, K3, source, or Wilson modules.
General whole-Q W-adjoint and flat completeness proofs: THEOREM.md.
"""
import hashlib
from itertools import permutations

NX,NY,LINKS=3,4,24
WEIGHTS=(1,3,2,3,3,2,2,2)
WILSON=(14,8,5,6,0,2,-7,-7)
SHIFTED=(12,0,-6,-4,-16,-12,-30,-30)
PERMS=tuple(permutations(range(3)))
POS={p:i for i,p in enumerate(PERMS)}
MUL=tuple(tuple(POS[tuple(a[b[j]] for j in range(3))] for b in PERMS)
          for a in PERMS)
INV=tuple(next(j for j in range(6) if MUL[i][j]==MUL[j][i]==0)
          for i in range(6))
TRANS=tuple(i for i in range(1,6) if MUL[i][i]==0)
CHAR=tuple(sum(int(j==p[j]) for j in range(3))-1 for p in PERMS)

class Hold(Exception):
    pass

def need(ok,why):
    if not ok:raise Hold(why)

def mul(a,b):
    return MUL[a][b]

def pos(x,y):
    return (x%NX)*NY+y%NY

def conj(g,v):
    return mul(mul(g,v),INV[g])

TREE=(tuple((pos(0,y),pos(0,y+1),12+pos(0,y)) for y in range(NY-1))+
      tuple((pos(x,y),pos(x+1,y),pos(x,y))
            for y in range(NY) for x in range(NX-1)))
RETAIN=tuple(e for e in range(LINKS) if e not in
             {edge for a,b,edge in TREE})

def full(key):
    need(len(key)==13,"original_13_link_gauge_fixed_coordinates")
    links=[0]*LINKS
    for j,e in enumerate(RETAIN):links[e]=key[j]
    return links

def canonical(links):
    need(len(links)==24,"original_complete_24_link_state")
    frame=[0]*12
    for a,b,e in TREE:frame[b]=mul(frame[a],links[e])
    residual=[]
    for edge in RETAIN:
        i=edge%12
        x,y=divmod(i,NY)
        j=pos(x+1,y) if edge<12 else pos(x,y+1)
        residual.append(mul(mul(frame[i],links[edge]),INV[frame[j]]))
    return min(tuple(conj(g,v) for v in residual) for g in range(6))

def weight(key):
    return len({tuple(conj(g,v) for v in key) for g in range(6)})

def moves(key):
    u=full(key)
    row={}
    for e in range(LINKS):
        old=u[e]
        for tr in TRANS:
            u[e]=mul(tr,old)
            dest=canonical(u)
            row[dest]=row.get(dest,0)+1
        u[e]=old
    need(sum(row.values())==72,"original_24x3_electric_moves")
    return row

def make_flat(a,b):
    u=[0]*LINKS
    for y in range(NY):u[pos(NX-1,y)]=a
    for x in range(NX):u[12+pos(x,NY-1)]=b
    return canonical(u)

def magnetic(key):
    u=full(key)
    ans=0
    for x in range(NX):
        for y in range(NY):
            i=pos(x,y)
            a=mul(u[i],u[12+pos(x+1,y)])
            a=mul(a,INV[u[pos(x,y+1)]])
            a=mul(a,INV[u[12+i]])
            ans+=3-sum(int(j==PERMS[a][j]) for j in range(3))
    return ans

def wilson(key):
    u=full(key)
    sum_h=sum(CHAR[mul(mul(u[pos(0,y)],u[pos(1,y)]),u[pos(2,y)])]
              for y in range(NY))
    total_v=0
    for x in range(NX):
        value=0
        for y in range(NY):value=mul(value,u[12+pos(x,y)])
        total_v+=CHAR[value]
    result=sum_h+total_v
    need(-7<=result<=14,"original_seven_loop_S3_character_range")
    return result

def adjoint(pq,qp,wp):
    for i,row in pq.items():
        for k,c in row.items():
            need(wp[i]*c==weight(k)*qp[k].get(i,0),
                 "physical_WP_HP_Q_equals_WQ_HQ_P_transpose")

def grams(pq,qp):
    return tuple(tuple(sum(pq[i].get(k,0)*qp[k].get(j,0)
                           for k in qp) for j in range(8)) for i in range(8))

def b_identity(pq,qp):
    matrix=grams(pq,qp)
    need(all(matrix[i][j]==(72 if i==j else 0)
             for i in range(8) for j in range(8)),
         "complete_original_physical_BstarB_72_identity")
    return matrix

def observable(op,o9):
    need(tuple(op)==WILSON,"original_seven_loop_flat_basis")
    need(len(op)==len(o9)==8 and
         all(2*x-16==y for x,y in zip(op,o9)) and tuple(o9)==SHIFTED,
         "original_shifted_Wilson_O9_equals_2O_minus_16I")

def reject(fn):
    try:fn()
    except Hold:return
    raise Hold("altered_physical_operator_accepted")

def seven_controls(wp,pq,qp,op,o9):
    key=next(iter(pq[0]))
    changed=list(wp);changed[0]+=1
    reject(lambda:adjoint(pq,qp,tuple(changed)))
    changed={i:dict(row) for i,row in pq.items()}
    changed[0][key]+=1
    reject(lambda:adjoint(changed,qp,wp))
    changed={k:dict(v) for k,v in qp.items()}
    changed[key][0]+=1
    reject(lambda:adjoint(pq,changed,wp))
    changed={k:dict(v) for k,v in qp.items()}
    changed[key][1]=1
    reject(lambda:b_identity(pq,changed))
    changed=list(o9);changed[0]+=1
    reject(lambda:observable(op,changed))
    changed=list(op);changed[0]+=1
    reject(lambda:observable(changed,o9))
    changed={i:dict(row) for i,row in pq.items()}
    del changed[0][key]
    reject(lambda:b_identity(changed,qp))

def check():
    need(len(PERMS)==6 and TRANS==(1,2,5),"original_S3_three_transpositions")
    need(len(TREE)==11 and len(RETAIN)==13,"periodic_3x4_spanning_tree")
    need(sorted(set(CHAR))==[-1,0,2],"S3_standard_character")
    commuting=[(a,b) for a in range(6) for b in range(6)
               if mul(a,b)==mul(b,a)]
    need(len(commuting)==18,"all_18_commuting_torus_holonomies")
    flats=sorted({make_flat(a,b) for a,b in commuting})
    need(len(flats)==8,"all_eight_magnetic_flat_gauge_orbits")
    wp=tuple(weight(p) for p in flats)
    need(wp==WEIGHTS and sum(wp)==18,
         "original_eight_W_flat_orbit_weights")
    need(all(magnetic(p)==0 for p in flats),
         "all_eight_P_states_magnetic_zero")
    op=tuple(wilson(p) for p in flats)
    o9=tuple(2*x-16 for x in op)
    observable(op,o9)
    flatset=set(flats)
    pq={}
    qset=set()
    for i,p in enumerate(flats):
        row=moves(p)
        need(not any(q in flatset for q in row),
             "H_PP_offdiagonal_or_selfloop_found")
        need(sum(row.values())==72,"H_PP_72I_diagonal")
        pq[i]=row
        qset.update(row)
    need(len(qset)==264 and sum(len(row) for row in pq.values())==264,
         "all_264_distinct_PQ_links_from_first_principles")
    qp={}
    for q in qset:
        row=moves(q)
        qp[q]={i:row.get(p,0) for i,p in enumerate(flats) if row.get(p,0)}
        need(len(qp[q])==1,"nonflat_Q1_unique_P_parent")
        need(magnetic(q)==4,"nonflat_Q1_magnetic_four")
    need({weight(q) for q in qset}=={3,6},
         "Q1_orbit_weights_three_or_six")
    adjoint(pq,qp,wp)
    b_identity(pq,qp)
    need(sum(sum(row.values()) for row in pq.values())==576,
         "all_576_original_flat_raw_move_census")
    seven_controls(wp,pq,qp,op,o9)
    digest=hashlib.sha256()
    for i in range(8):
        for q,c in sorted(pq[i].items()):
            addr=sum(v*6**j for j,v in enumerate(q))
            line=(str(i)+"|"+str(addr)+"|"+str(wp[i])+"|"+
                  str(weight(q))+"|"+str(c)+"|"+str(qp[q][i])+"\n")
            digest.update(line.encode("ascii"))
    expected="8d41471666def3e72caf199cd87f6bfbb94fc06a66c037f1c88156c4d6c78d34"
    need(digest.hexdigest()==expected,"frozen_original_S3_PQ_boundary_digest")
    print("Y137_INDEPENDENT_FULL_PHYSICAL_PQ|lattice=3x4_S3"+
          "|whole_flat_orbits=8|commuting_holonomy_pairs=18"+
          "|original_WP=1,3,2,3,3,2,2,2"+
          "|P_Q_distinct_original_physical_orbits=264"+
          "|P_Q_directed_orbit_edges=264|original_raw_flat_moves=576"+
          "|original_P_P_H=72_I8|physical_weighted_HPQ_HQP_adjoint=PASS"+
          "|original_BstarB=72_I8_EXACT|Q1_magnetic_number=4"+
          "|original_Wilson_P=14,8,5,6,0,2,-7,-7"+
          "|original_shifted_O9_P=12,0,-6,-4,-16,-12,-30,-30"+
          "|original_P_O_Q=ZERO_BY_DIAGONAL_ACTION"+
          "|original_operator_PQ_boundary_SHA256="+digest.hexdigest()+
          "|negative_controls=7_REJECTED"+
          "|global_W_adjoint=COMBINATORIAL_INVOLUTION_PROOF"+
          "|complete_source_to_mu3=SEPARATELY_ACCEPTED"+
          "|original_Wilson=SOURCE_CONDITIONAL_FORMAL_HOLD"+
          "|continuum_4D=OPEN|json=0")

if __name__=="__main__":
    try:check()
    except (Hold,ValueError,KeyError) as err:
        print("Y137_INDEPENDENT_FULL_PHYSICAL_PQ_HOLD|reason="+str(err)+
              "|original_Wilson=FORMAL_HOLD|json=0")
        raise SystemExit(2) from None
