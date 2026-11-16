#!/usr/bin/env python3
"""Exact full-support Ritz-trial residual on 8 flat + 8,034 K2 Q + 147,344 K3 exterior.

For each nested n=12,24,48,96,144 and first/second projected Ritz level:
construct a nonzero rational trial vector by solving the exact 12x12
Schur system (DK-zG)y=e_p at the frozen upper Ritz endpoint z,
recover all added coordinate coefficients by exact diagonal elimination,
clear every denominator, apply the ORIGINAL Hamiltonian on the full
8+8034+147344 support, and calculate exact normalized ||(H-z/D)u||_W.

The certified squared norm includes the original external weighted-flux
metric as independently defined in the K3 direct_forms acceptance. This
is a certified FULL SUPPORT RESIDUAL for a constructed TRIAL vector,
not a verified true full-space eigenvector angle or Wilson-positive overlap.
"""
import hashlib
import os
import sys
from math import gcd, isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nested_ritz as n

DEN = n.DEN
UNIT = 1000000000000


def need(x, reason):
    n.need(x, reason)


def rat(a, b=1):
    need(b != 0, "invalid_rational_denominator")
    if b < 0:
        a, b = -a, -b
    g = gcd(abs(a), b)
    return (a//g, b//g)


def plus(x, y):
    return rat(x[0]*y[1]+y[0]*x[1], x[1]*y[1])


def negative(x):
    return (-x[0], x[1])


def quotient(x, d):
    return rat(x[0], x[1]*d)


def exact_schur(z, G, K, grouped):
    den = {}
    product = 1
    for d in grouped:
        q = DEN*d-z
        need(q > 0, "nonpositive_coordinate_elimination")
        den[d] = q
        product *= q
    s = [[product*(DEN*K[i][j]-z*G[i][j])
          for j in range(n.DIM_BASE)] for i in range(n.DIM_BASE)]
    for d, (HH, HB, BB) in grouped.items():
        mult = product//den[d]
        for i in range(n.DIM_BASE):
            for j in range(n.DIM_BASE):
                s[i][j] -= mult*(DEN*DEN*HH[i][j]
                                 -DEN*z*HB[i][j]+z*z*BB[i][j])
    need(all(s[i][j] == s[j][i]
             for i in range(n.DIM_BASE) for j in range(n.DIM_BASE)),
         "non_symmetric_exact_Schur")
    return s


def solve_int_symmetric(a, probe):
    """Fraction-free augmented Bareiss solve returning reduced rational coordinates."""
    sz = len(a)
    m = [a[i][:] + [int(i == probe)] for i in range(sz)]
    prev=1
    for k in range(sz-1):
        pivot=m[k][k]
        need(pivot != 0,"exact_Schur_solve_zero_pivot")
        for i in range(k+1,sz):
            for j in range(k+1,sz+1):
                v=pivot*m[i][j]-m[i][k]*m[k][j]
                need(v%prev==0,"exact_Schur_solve_nonintegral")
                m[i][j]=v//prev
            m[i][k]=0
        prev=pivot
    need(m[-1][-2] != 0, "exact_Schur_last_pivot_zero")
    x=[(0,1)]*sz
    for i in range(sz-1,-1,-1):
        rhs=rat(m[i][sz])
        for j in range(i+1,sz):
            if m[i][j]:
                rhs=plus(rhs,negative(rat(m[i][j]*x[j][0],x[j][1])))
        x[i]=quotient(rhs,m[i][i])
    # Direct exact substitution checks the entire original system.
    for i in range(sz):
        lhs=(0,1)
        for j in range(sz):
            if a[i][j]:
                lhs=plus(lhs,rat(a[i][j]*x[j][0],x[j][1]))
        need(lhs==rat(int(i==probe)),
             "independent_full_Schur_resolvent_substitution")
    return x


def lcm(a,b):
    return a//gcd(a,b)*b


def integer_coefficients(z, core, chosen, ball, cols, actions):
    """Reconstruct the full projected vector by eliminating coordinate indicators."""
    allrat=list(core)
    C=ball["C"]
    for i in chosen:
        h=[-(0 if C[i] is None else C[i][p]) for p in range(8)]
        h += [actions[a][i] for a in range(4)]
        b=[0]*8+[cols[a][i] for a in range(4)]
        v=(0,1)
        for a in range(n.DIM_BASE):
            coeff=DEN*h[a]-z*b[a]
            if coeff:
                v=plus(v,rat(coeff*core[a][0],core[a][1]))
        allrat.append(negative(quotient(v,DEN*ball["dbase"][i]-z)))
    den=1
    for a,b in allrat:
        den=lcm(den,b)
    x=[a*(den//b) for a,b in allrat]
    common=0
    for v in x:
        common=gcd(common,abs(v))
    need(common>0,"zero_exact_trial_vector")
    x=[v//common for v in x]
    need(any(x[:8]),"original_flat_probe_lost")
    return x


def full_trial(ball, cols, chosen, x):
    """The exact candidate amplitudes on P and entire K2 Q, all integers."""
    p=x[:8]
    q=[sum(cols[a][i]*x[8+a] for a in range(4))
       for i in range(ball["n"])]
    for k,i in enumerate(chosen):
        q[i]+=x[12+k]
    return p,q


def original_projected_identity(z, G, K, x, p, q, rp, rq, ball):
    """An independently reconstructed full-action expectation equals xT(DK-zG)x."""
    direct=sum(ball["wf"][i]*p[i]*rp[i] for i in range(8))
    direct+=sum(ball["wq"][i]*q[i]*rq[i] for i in range(ball["n"]))
    projected=0
    for a in range(len(x)):
        if x[a]==0:
            continue
        for b in range(len(x)):
            if x[b]:
                projected+=x[a]*(DEN*K[a][b]-z*G[a][b])*x[b]
    need(direct==projected,"full_H_action_vs_projected_H_G_quadratic")
    return direct


def direct_full_residual(z, ball, p, q):
    """Physically weighted (six times) square of full (D H-z) action.

    The original K3 direct_forms audit computes exterior flux S_f=Σ wc x_i,
    and adds (6/w_ext)*S_f²; interior contributes 6*w_i*r_i².
    Therefore this is exactly 6*||(D H-z) phi||_W².
    """
    C=ball["C"]
    wf,wq=ball["wf"],ball["wq"]
    rs,oj,oc=ball["rs"],ball["oj"],ball["oc"]
    rp=[(DEN*72-z)*p[t] for t in range(8)]
    for i,ci in enumerate(C):
        if ci is None or q[i]==0:
            continue
        for t in range(8):
            if ci[t]:
                val=DEN*wq[i]*ci[t]*q[i]
                need(val%wf[t]==0, "original_flat_reverse_weight_noninteger")
                rp[t]-=val//wf[t]
    rq=[]
    for i in range(ball["n"]):
        val=(DEN*ball["dbase"][i]-z)*q[i]
        for j in range(rs[i],rs[i+1]):
            val-=DEN*oc[j]*q[oj[j]]
        ci=C[i]
        if ci is not None:
            val-=DEN*sum(ci[t]*p[t] for t in range(8))
        rq.append(val)
    interior=6*sum(wf[t]*v*v for t,v in enumerate(rp))
    interior+=6*sum(wq[i]*v*v for i,v in enumerate(rq))
    es,esrc,ewc,eW=ball["es"],ball["esrc"],ball["ewc"],ball["eW"]
    outside=0
    nonzero=0
    for f in range(ball["nf"]):
        S=sum(ewc[j]*q[esrc[j]] for j in range(es[f],es[f+1]))
        if S:
            nonzero+=1
            need(6%eW[f]==0,"exterior_orbit_weight_not_six_divisor")
            outside+=(6//eW[f])*S*S
    outside*=DEN*DEN
    norm=sum(wf[i]*v*v for i,v in enumerate(p))
    norm+=sum(wq[i]*v*v for i,v in enumerate(q))
    need(norm>0 and interior>=0 and outside>=0,
         "full_residual_not_nonnegative")
    return norm,interior,outside,nonzero,rp,rq


def upper_sqrt_per_trillion(a,b):
    need(a>=0 and b>0,"bad_normalized_square_bound")
    value=a*UNIT*UNIT//b
    root=isqrt(value)
    if root*root*b<a*UNIT*UNIT:
        root+=1
    return root


def best_rational_trial(dim, level, z, chosen, G, K, ball, cols, actions):
    groups=n.group_schur(ball,cols,actions,chosen)
    schur=exact_schur(z,[row[:12] for row in G[:12]],
                     [row[:12] for row in K[:12]],groups)
    probe=0 if level==1 else 3
    core=solve_int_symmetric(schur,probe)
    x=integer_coefficients(z,core,chosen,ball,cols,actions)
    p,q=full_trial(ball,cols,chosen,x)
    norm,inside,outside,noutside,rp,rq=direct_full_residual(z,ball,p,q)
    quad=original_projected_identity(z,G,K,x,p,q,rp,rq,ball)
    numerator=inside+outside
    denominator=6*DEN*DEN*norm
    unit=upper_sqrt_per_trillion(numerator,denominator)
    need(numerator>0 and unit>0, "residual_must_be_measured")
    n.emit("Y137_H144_FULL_RESIDUAL",dimension=dim,level=level,
           projected_Ritz_sample_z_num=z,energy_den=DEN,
           fixed_rational_probe_flat_index=probe,
           trial_coefficient_count=len(x),
           trial_coeff_bit_max=max(abs(t).bit_length() for t in x),
           physical_support_K2_q=sum(t!=0 for t in q),
           physical_support_exterior_residual=noutside,
           norm_squared_integer_bits=norm.bit_length(),
           exact_full_residual_square_num_sha256=n.sha(str(numerator)),
           exact_full_residual_square_den_sha256=n.sha(str(denominator)),
           exact_residual_upper_per_trillion=unit,
           direct_H_vs_projected_quadratic="EXACT",
           projected_source_rayleigh_numerator_sign=(
              "NEG" if quad<0 else "POS" if quad>0 else "ZERO"),
           K3_exterior_all_rows=ball["nf"],
           full_state_residual="EXACT_FOR_THIS_TRIAL",
           true_eigendirection_distance="NOT_CERTIFIED",
           Wilson_weight="HOLD")
    return unit


def main():
    n.test_small()
    G12,K12=n.load_h12()
    ball,states,cols,actions=n.sources()
    selected,scores=n.select(ball,cols,actions)
    n.emit("Y137_H144_RESIDUAL_SOURCE",
           original_H12_blob=n.H12_RESULT_BLOB,
           selected_Q_orbits=len(selected),
           physical_Q_source_states=ball["n"],
           K3_exterior_states=ball["nf"],
           original_K3_exterior_flux_metric="6_OVER_ORBIT_WEIGHT",
           arithmetic="INTEGER_ONLY",Wilson_weight="HOLD")
    for dim in n.SIZES:
        chosen=selected[:dim-12]
        G,K=n.expanded_matrices(ball,cols,actions,chosen,G12,K12)
        groups=n.group_schur(ball,cols,actions,chosen)
        brackets=[n.exact_bracket(k,G12,K12,groups) for k in (1,2)]
        for level,(_,hi) in enumerate(brackets,1):
            best_rational_trial(dim,level,hi,chosen,G,K,ball,cols,actions)
    n.emit("Y137_H144_RESIDUAL_VERDICT",
           matrix_ladder="12_24_48_96_144",
           full_support_trial_residuals="10_OF_10_EXACT",
           full_support_actions="8_FLAT_8034_Q_147344_EXTERIOR",
           true_eigenspace_angle="HOLD",
           positive_Wilson_first_weight="HOLD",issue_137="OPEN")


if __name__=="__main__":
    if sys.argv[1:]==["real"]:
        main()
    else:
        need(False,"use_real")
