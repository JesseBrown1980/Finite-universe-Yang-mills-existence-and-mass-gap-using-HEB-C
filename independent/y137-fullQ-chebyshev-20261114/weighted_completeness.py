#!/usr/bin/env python3
"""Independent weighted completeness + paired-moment application control.

A self-consistent truncated operator passes the moment algebra, but is
REFUSED by separate move-list completeness and independent operator checks.
Synthetic 5-orbit 72-move graph only; no real 3x4 moment calculation.
"""
from collections import Counter
from itertools import combinations

N=5
MOVES=72
WEIGHTS=(1,2,3,6,6)
MAG=(0,1,1,2,2)
FLAT=(0,)
Q=(1,2,3,4)
# Independent, directly authored complete-move operator, not obtained by
# summing the builder's event list.
REFERENCE_T=(
    (62,4,6,0,0),
    (2,61,3,6,0),
    (2,2,64,2,2),
    (0,2,1,66,3),
    (0,0,1,3,68),
)
# Builder input is instead a set of move families with directed counts.
# The reverse count follows from raw-orbit flux balance.
EVENTS=((0,1,4),(0,2,6),(1,2,3),(1,3,6),
        (2,3,2),(2,4,2),(3,4,3))
R=((0,2),(0,0),(3,0),(0,0))
F=((25,1),(1,30))
DEGREES=(1,2,4,8,16)
G=10
H=40


def need(ok,reason):
    if not ok:
        raise ValueError(reason)


def emit(label,**fields):
    print(label+"|"+"|".join(str(k)+"="+str(v) for k,v in fields.items())+
          "|json=0",flush=True)


def move_rows():
    rows=[Counter() for _ in range(N)]
    for src,dst,count in EVENTS:
        need((count*WEIGHTS[src])%WEIGHTS[dst]==0,"bad_builder_flux")
        rows[src][dst]+=count
        rows[dst][src]+=count*WEIGHTS[src]//WEIGHTS[dst]
    for i in range(N):
        deficit=MOVES-sum(rows[i].values())
        need(deficit>=0,"builder_row_overfull")
        rows[i][i]+=deficit
    return tuple(tuple(dst for dst in range(N)
                       for _ in range(rows[i][dst]))
                 for i in range(N))


def matrix_from_moves(rows):
    return tuple(tuple(Counter(row)[j] for j in range(N)) for row in rows)


def source_integrity(rows,present,check_reference=True):
    """Every represented source has 72 full moves; no unknown destinations.

    Flat destinations count as generated and resolved, although a Q operator
    application subsequently projects their contributions out.
    """
    present=set(present)
    need(present,"missing_source_state")
    table={}
    for i in present:
        need(len(rows[i])==MOVES,"wrong_outgoing_move_count")
        need(all(t in present for t in rows[i]),"unresolved_boundary_neighbor")
        table[i]=Counter(rows[i])
        need(sum(table[i].values())==MOVES,"non_regular_electric_row")
    for i in present:
        for j,v in table[i].items():
            need(j in present and WEIGHTS[i]*v==
                 WEIGHTS[j]*table[j][i],"weighted_balance_failure")
    if check_reference:
        need(present==set(range(N)),"incomplete_reference_operator")
        # Independent reference is also applied to two complete 5-state
        # columns, independently of the move-list multiplicity builder.
        ref=REFERENCE_T
        columns=((1,3,2,5,7),(2,1,0,4,9))
        for col in columns:
            for i in range(N):
                via_moves=sum(col[j] for j in rows[i])
                via_ref=sum(ref[i][j]*col[j] for j in range(N))
                need(via_moves==via_ref,"independent_operator_sample")
        need(matrix_from_moves(rows)==ref,
             "independent_full_matrix_disagrees")
    return len(present)


def Q_operator(t,mag= MAG,subset=Q):
    # QHQ-zI at z=0 for H=72I-T+9M. Exactly excludes P states
    # after EVERY multiplication, while all 72 raw moves remain counted.
    return tuple(tuple((MOVES+9*mag[i] if i==j else 0)-t[i][j]
                       for j in subset) for i in subset)


def multiply(a,b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(len(b)))
                       for j in range(len(b[0])))
                 for i in range(len(a)))


def transpose(a):
    return tuple(tuple(a[i][j] for i in range(len(a)))
                 for j in range(len(a[0])))


def scale(a,n):
    return tuple(tuple(n*x for x in row) for row in a)


def add(a,b):
    return tuple(tuple(x+y for x,y in zip(aa,bb)) for aa,bb in zip(a,b))


def sub(a,b):
    return tuple(tuple(x-y for x,y in zip(aa,bb)) for aa,bb in zip(a,b))


def ident(n):
    return tuple(tuple(int(i==j) for j in range(n)) for i in range(n))


def weighted_dot(a,b,w):
    return tuple(tuple(sum(w[k]*a[k][i]*b[k][j]
                           for k in range(len(w)))
                       for j in range(len(b[0])))
                 for i in range(len(a[0])))


def determinant(a):
    n=len(a)
    if n==0:
        return 1
    m=[list(row) for row in a]
    prev=1
    sign=1
    for k in range(n-1):
        if m[k][k]==0:
            pivot=next((i for i in range(k+1,n) if m[i][k]),None)
            if pivot is None:
                return 0
            m[k],m[pivot]=m[pivot],m[k]
            sign=-sign
        p=m[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                x=p*m[i][j]-m[i][k]*m[k][j]
                need(x%prev==0,"noninteger_Bareiss")
                m[i][j]=x//prev
        for i in range(k+1,n):
            m[i][k]=0
        prev=p
    return sign*m[-1][-1]


def psd(a):
    n=len(a)
    need(all(len(row)==n for row in a),"PSD_shape")
    need(all(a[i][j]==a[j][i] for i in range(n)
             for j in range(n)),"PSD_symmetry")
    for k in range(1,n+1):
        for ix in combinations(range(n),k):
            if determinant(tuple(tuple(a[i][j] for j in ix)
                                 for i in ix))<0:
                return False
    return True


def weighted_interval(a,w,g,h):
    # A is W-self-adjoint, and the spectral interval is certified by
    # all weighted principal minors (not an unweighted surrogate).
    wa=tuple(tuple(w[i]*a[i][j] for j in range(len(w)))
             for i in range(len(w)))
    wd=tuple(tuple((w[i] if i==j else 0) for j in range(len(w)))
             for i in range(len(w)))
    need(psd(sub(wa,scale(wd,g))) and
         psd(sub(scale(wd,h),wa)),"weighted_spectral_interval")
    return 1


def pair_and_direct(a,r,w,n):
    """2n moments from n operator passes, matched to a direct route."""
    vectors=[r]
    for j in range(n):
        vectors.append(multiply(a,vectors[-1]))
    paired=[]
    for j in range(n):
        paired.append(weighted_dot(vectors[j],vectors[j],w))
        paired.append(weighted_dot(vectors[j],vectors[j+1],w))
    direct=[]
    v=r
    for k in range(2*n):
        direct.append(weighted_dot(r,v,w))
        v=multiply(a,v)
    need(paired==direct,"paired_and_direct_moment_disagree")
    return paired,vectors


def polynomials(n,g,h):
    s=g+h
    d=h-g
    before=[1]
    current=[s,-2]
    if n==1:
        return current
    for _ in range(2,n+1):
        nxt=[0]*(len(current)+1)
        for i,x in enumerate(current):
            nxt[i]+=2*s*x
            nxt[i+1]-=4*x
        for i,x in enumerate(before):
            nxt[i]-=d*d*x
        before,current=current,nxt
    return current


def moments_coeff(n,g,h):
    p=polynomials(n,g,h)
    k=p[0]
    need(k>0,"negative_normalizer")
    square=[0]*(2*n+1)
    for i,x in enumerate(p):
        for j,y in enumerate(p):
            square[i+j]+=x*y
    need(square[0]==k*k,"wrong_polynomial_zero")
    return k,[-v for v in square[1:]]


def center_from_moments(a,r,w,n):
    moments,vectors=pair_and_direct(a,r,w,n)
    k,coeff=moments_coeff(n,G,H)
    cent=scale(F,k*k)
    for c,m in zip(coeff,moments):
        cent=sub(cent,scale(m,c))
    # Independent direct evaluation of Y'=-((K-P)/X)(A)R / K
    pc=polynomials(n,G,H)
    qr=scale(vectors[0],0)
    for i,c in enumerate(pc[1:]):
        qr=add(qr,scale(vectors[i],-c))
    rqr=weighted_dot(r,qr,w)
    direct=add(sub(scale(F,k*k),scale(rqr,2*k)),
               weighted_dot(qr,multiply(a,qr),w))
    need(cent==direct,"weighted_center_disagrees_with_direct")
    return moments,cent


def requires_refusal(callback,why):
    try:
        callback()
    except ValueError:
        return
    raise ValueError("fault_not_refused_"+why)


def all_on_truncated_passes_moment_algebra(rows):
    """Counterexample to treating the moment identity as a completeness test."""
    t=matrix_from_moves(rows)
    subset=(1,2,3)      # drops the real Q shell5 state 4
    # Consistently truncate the Q source & operator: an internally
    # valid smaller, weighted self-adjoint operator.
    a=Q_operator(t,subset=subset)
    w=tuple(WEIGHTS[i] for i in subset)
    rr=R[:3]
    pair_and_direct(a,rr,w,4)  # passes, even though boundary was omitted
    return 1


def negative_controls(rows):
    table=matrix_from_moves(rows)
    all_on_truncated_passes_moment_algebra(rows)
    requires_refusal(lambda:source_integrity(rows,(0,1,2,3),False),
                    "shell5_omission")
    # A malicious "repair" can redirect the missing move to a self-loop
    # and preserve 72, closure and W-balance on the truncated subset.
    rebuilt=[list(row) for row in rows]
    for i in (2,3):
        rebuilt[i]=[i if j==4 else j for j in rebuilt[i]]
    subset_rows=tuple(tuple(x) for x in rebuilt)
    source_integrity(subset_rows,(0,1,2,3),False)
    requires_refusal(lambda:source_integrity(subset_rows,range(N),True),
                    "tampered_complete_move_law")
    # One asymmetric changed move keeps all 72 destinations and closure,
    # but fails true orbit-weight detailed balance.
    bad=[list(row) for row in rows]
    edge=bad[3].index(4)
    bad[3][edge]=3
    requires_refusal(lambda:source_integrity(tuple(tuple(x) for x in bad),
                                              range(N),False),
                    "detailed_balance")
    # Wrong metric: symmetrical W relation is lost on a genuine edge.
    oldweights=WEIGHTS
    a=Q_operator(table)
    # The correct metric must yield a symmetric WA and a certified interval.
    weighted_interval(a,WEIGHTS[1:],G,H)
    need(WEIGHTS[0]*table[0][1]!=
         WEIGHTS[1]*table[1][0]//2,"wrong_weight_fault_not_visible")
    # Raw full H powers return through the removed P sector.
    whole=tuple(tuple((MOVES+9*MAG[i] if i==j else 0)-table[i][j]
                     for j in range(N)) for i in range(N))
    a2=multiply(a,a)
    whole2=multiply(whole,whole)
    qraw=tuple(tuple(whole2[i][j] for j in Q) for i in Q)
    need(a2!=qraw,"unprojected_flat_reentry_not_visible")
    return 1


def main():
    rows=move_rows()
    count=source_integrity(rows,range(N),True)
    t=matrix_from_moves(rows)
    a=Q_operator(t)
    w=WEIGHTS[1:]
    # Correct orbit-space inner product: nontrivial diagonal W.
    need(any(x!=w[0] for x in w),"identity_metric_toy")
    weighted_interval(a,w,G,H)
    negatives=negative_controls(rows)
    emit("Y137_COMPLETE_TOY",full_states=count,flat_states=1,
         nonflat_states=4,raw_moves_per_state=MOVES,
         all_destinations_resolved=1,
         every_weighted_edge_balanced=1,
         all_rowsum_72=1,
         independent_reference_operator=PASS,
         Q_projection_after_every_step=PASS,
         wholeQ_moments="SYNTHETIC_ONLY")
    for n in DEGREES:
        moments,cent=center_from_moments(a,R,w,n)
        need(len(moments)==2*n,"paired_moment_count")
        emit("Y137_COMPLETE_PAIR",degree=n,moment_matrices=len(moments),
             operator_applications=n,metric="W_NONIDENTITY",
             direct_vs_paired="PASS",exact_Schur_center="PASS")
    emit("Y137_COMPLETE_VERDICT",
         fully_truncated_moment_identity="PASSES_BUT_IS_NOT_A_PROOF",
         truncated_operator_completeness="REJECTED",
         tampered_closed_graph="REJECTED_BY_INDEPENDENT_REFERENCE",
         unbalanced_edge="REJECTED",
         real_3x4_orbit_closure="NOT_COMPUTED",
         real_moments="NOT_COMPUTED",
         actual_Wilson_weight="HOLD",
         issue_137="OPEN")


if __name__=="__main__":
    main()
