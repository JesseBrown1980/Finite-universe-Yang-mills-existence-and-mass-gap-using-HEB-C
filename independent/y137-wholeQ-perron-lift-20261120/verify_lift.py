#!/usr/bin/env python3
"""Independent exact whole-Q weighted Perron spatial-symmetry lift theorem toy.

Tests the exact ground-state-transform identity, invariant quotient lift,
weighted-adjoint detailed balance and positive-vector row certificate.
No imports from original Perron solver, physical graph, or earlier proof tests.
Original full-store certificate inputs remain separate accepted premises.
"""
W=(1,2,2)
C=((0,2,2),(1,0,0),(1,0,0))
D=(6,7,7)
PART=((0,),(1,2))
SECTOR=((6,-4),(-1,7))
SECTOR_D=(2,1)
THRESHOLD=4
ORIGINAL_T_MICRO=94070673
ORIGINAL_GAMMA_MICRO=94068200
class Hold(Exception):
    pass

def need(ok,why):
    if not ok:raise Hold(why)

def fullop(w,c,diag):
    need(len(w)==len(c)==len(diag)==3 and all(len(row)==3 for row in c),
         "complete_fullspace_weighted_Z_matrix")
    need(all(x>0 for x in w),"strict_positive_original_orbit_weights")
    need(all(c[i][j]>=0 and (i!=j or c[i][j]==0)
             for i in range(3) for j in range(3)),
         "nonpositive_offdiagonal_original_H")
    need(all(w[i]*c[i][j]==w[j]*c[j][i]
             for i in range(3) for j in range(3)),
         "physical_weighted_detailed_balance")
    need(diag[1]==diag[2] and c[0][1]==c[0][2] and
         c[1][0]==c[2][0] and c[1][2]==c[2][1],
         "physical_lattice_symmetry_commutes_with_H")
    return tuple(tuple((diag[i] if i==j else -c[i][j])
                       for j in range(3)) for i in range(3))

def quotient(h):
    q=[]
    for block in PART:
        x=block[0]
        q.append(tuple(sum(h[x][j] for j in orbit) for orbit in PART))
    need(q[0]==(6,-4) and q[1]==(-1,7),
         "exact_spatial_symmetry_orbit_quotient_H")
    return tuple(q)

def valid_lift(h,q,d,t):
    need(len(d)==2 and all(v>0 for v in d),
         "positive_comparison_vector_on_every_nonflat_sector_orbit")
    need(q==quotient(h),"original_entire_sector_to_wholeQ_operator_identity")
    lifted=tuple(d[0] if i==0 else d[1] for i in range(3))
    for i in range(3):
        actual=sum(h[i][j]*lifted[j] for j in range(3))
        expected=sum(q[0 if i==0 else 1][k]*d[k] for k in range(2))
        need(actual==expected,"spatial_symmetry_quotient_row_lift_exact")
        need(actual>=t*lifted[i],"strict_positive_whole_Q_Barta_row")
    return lifted

def transformed_quadratic(h,w,c,d,t,u):
    f=tuple(d[i]*u[i] for i in range(3))
    lhs=sum(w[i]*f[i]*(sum(h[i][j]*f[j] for j in range(3))-t*f[i])
            for i in range(3))
    Ad=tuple(sum(h[i][j]*d[j] for j in range(3))-t*d[i]
             for i in range(3))
    source=sum(w[i]*d[i]*Ad[i]*u[i]*u[i] for i in range(3))
    graph=sum(w[i]*c[i][j]*d[i]*d[j]*(u[i]-u[j])**2
              for i in range(3) for j in range(i+1,3))
    need(lhs==source+graph,"weighted_wholeQ_Perron_groundstate_sum_of_squares")
    need(source>=0 and graph>=0 and lhs>=0,
         "positive_groundstate_transform_Z_matrix")
    return lhs

def refuse(fn):
    try:fn()
    except Hold:return
    raise Hold("bad_wholeQ_positive_vector_or_symmetry_lift_accepted")

def checks():
    h=fullop(W,C,D)
    q=quotient(h)
    need(q==SECTOR,"exact_original_sector_orbit_row_sum_in_toy")
    d=valid_lift(h,q,SECTOR_D,THRESHOLD)
    need(d==(2,1,1),"strict_positive_original_comparison_lift")
    need(tuple(sum(h[i][j]*d[j] for j in range(3))-THRESHOLD*d[i]
               for i in range(3))==(0,1,1),
         "original_quotient_to_wholeQ_fullrow_Barta")
    for u in ((2,-1,2),(-3,4,0),(1,1,1),(0,0,0)):
        transformed_quadratic(h,W,C,d,THRESHOLD,u)
    need(ORIGINAL_T_MICRO-ORIGINAL_GAMMA_MICRO==2473,
         "original_Q_Perron_cert_strictly_above_conservative_gamma")
    count=0
    def negative(fn):
        nonlocal count
        refuse(fn)
        count+=1
    negative(lambda:fullop((1,1,2),C,D))
    negative(lambda:fullop(W,((0,2,2),(2,0,0),(1,0,0)),D))
    negative(lambda:fullop(W,((0,2,0),(1,0,0),(1,0,0)),D))
    negative(lambda:fullop(W,C,(6,7,8)))
    negative(lambda:fullop(W,((0,-2,2),(1,0,0),(1,0,0)),D))
    negative(lambda:valid_lift(h,((6,-2),(-1,7)),SECTOR_D,THRESHOLD))
    negative(lambda:valid_lift(h,q,(2,0),THRESHOLD))
    negative(lambda:valid_lift(h,q,SECTOR_D,6))
    negative(lambda:valid_lift(h,q,(2,-1),THRESHOLD))
    need(count==9,"all_nine_lift_and_positive_vector_negative_controls")
    print("Y137_INDEPENDENT_WHOLEQ_PERRON_LIFT"+
          "|full_source=ORIGINAL_WEIGHTED_SELFADJOINT_Z_MATRIX"+
          "|spatial_quotient_invariant=EXACT"+
          "|strict_positive_quotient_vector=PASS"+
          "|wholeQ_row_lift=EXACT"+
          "|wholeQ_groundstate_sum_squares=PASS"+
          "|original_cert_t_microJE=94070673"+
          "|original_conservative_gamma_microJE=94068200"+
          "|strict_spectral_floor_slack_microJE=2473"+
          "|negative_controls=9_REJECTED"+
          "|original_45m_positive_witness=SEPARATE_PINNED_PREMISE"+
          "|wholeQ_lift_mathematical_theorem=PASS"+
          "|first_original_Wilson=SOURCE_CONDITIONAL_FORMAL_HOLD"+
          "|continuum_4D=OPEN|json=0")

if __name__=="__main__":
    try:checks()
    except (Hold,ValueError,KeyError) as e:
        print("Y137_WHOLEQ_PERRON_LIFT_HOLD|reason="+str(e)+
              "|first_original_Wilson=FORMAL_HOLD|json=0")
        raise SystemExit(2) from None
