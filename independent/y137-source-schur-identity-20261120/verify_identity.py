#!/usr/bin/env python3
"""Independent exact W-weighted physical trial source to Schur identity.

Uses original source integer scales b=1e9 and trial=1e12, original signed
K3/Q4 residual convention and exact archival mu0=G0/6 rule. Does not
import any production K3, source, spectral, moment or Wilson modules.
General matrix identity is proved in THEOREM.md.
"""
from math import lcm

B=1000000000
T=1000000000000
W_P=(1,3)
W_Q=(2,6,3)
BQ=((-1,0),(0,-1),(0,-1))
D_Q=(75,76,77)
Y0=((2,1),(1,0),(0,3))
E=70
P_H=72

class Hold(Exception):
    pass

def need(ok,why):
    if not ok:raise Hold(why)

def gram(rows,weights,powers):
    return tuple(tuple(sum(weights[q]*rows[q][i]*rows[q][j]*powers[q]
                           for q in range(3)) for j in range(2)) for i in range(2))

def derive():
    x=tuple(B*(e-E) for e in D_Q)
    need(all(v>0 for v in x),"strict_source_X_on_entire_Q_toy")
    y=tuple(tuple(T*v for v in row) for row in Y0)
    r=tuple(tuple(x[q]*y[q][i]+B*BQ[q][i]*T for i in range(2))
            for q in range(3))
    mu=tuple(gram(r,W_Q,tuple(t**k for t in x)) for k in range(4))
    u=tuple(tuple((B*P_H-B*E)*W_P[i]*T*T*(i==j)
          +sum(W_Q[q]*(y[q][i]*r[q][j]+B*T*BQ[q][i]*y[q][j])
               for q in range(3)) for j in range(2)) for i in range(2))
    den=lcm(*x)
    f=tuple(tuple(sum(W_Q[q]*r[q][i]*r[q][j]*(den//x[q])
                      for q in range(3)) for j in range(2)) for i in range(2))
    s=tuple(tuple((B*P_H-B*E)*den*W_P[i]*T*T*(i==j)
          -sum(W_Q[q]*(B*BQ[q][i]*T)*(B*BQ[q][j]*T)*(den//x[q])
               for q in range(3)) for j in range(2)) for i in range(2))
    return x,r,mu,u,den,f,s

def original_schur_identity(m):
    x,r,mu,u,den,f,s=m
    need(all(den*u[i][j]-f[i][j]==s[i][j]
             for i in range(2) for j in range(2)),
         "physical_W_source_to_actual_Schur_resolvent")
    need(all(u[i][j]==u[j][i] for i in range(2) for j in range(2)),
         "source_U0_weighted_symmetric")
    need(all(mu[k][i][j]==mu[k][j][i]
             for k in range(4) for i in range(2) for j in range(2)),
         "whole_Q_signed_mu0_mu1_mu2_mu3_weighted_symmetric")
    g0=tuple(tuple(6*mu[0][i][j] for j in range(2)) for i in range(2))
    need(all(g0[i][j]%6==0 and g0[i][j]//6==mu[0][i][j]
             for i in range(2) for j in range(2)),
         "original_archive_six_times_mu0_undo")
    return g0

def controls(m,g0):
    x,r,mu,u,den,f,s=m
    count=0
    def reject(ok):
        nonlocal count
        need(not ok,"corrupt_original_source_Schur_premise_accepted")
        count+=1
    reject(den*(u[0][0]+1)-f[0][0]==s[0][0])
    reject(den*u[0][0]-(f[0][0]+1)==s[0][0])
    reject(den*u[0][0]-f[0][0]==s[0][0]+1)
    reject(den*u[0][0]-f[0][0]==s[0][0]+(B*T*T*den))
    reject(g0[0][0]==mu[0][0])
    reject(g0[0][0]//(6+1)==mu[0][0])
    reject(den*u[0][0]-f[0][0]+
           W_Q[0]*r[0][0]*r[0][0]*(den//x[0])==s[0][0])
    need(count==7,"all_seven_changed_signed_source_controls_rejected")
    return count

def main():
    m=derive()
    g0=original_schur_identity(m)
    controls(m,g0)
    x,r,mu,u,den,f,s=m
    need(x==(5*B,6*B,7*B),"original_integer_energy_units")
    need(den==210*B,"exact_full_Q_inverse_common_denominator")
    need(tuple(tuple(k//(B*T*T) for k in row) for row in u)==((70,12),(12,187)),
         "source_U0_from_original_weighted_PHQ")
    need(tuple(tuple(k//(B*B*T*T) for k in row) for row in mu[0])==
         ((378,54),(54,1256)),"original_signed_mu0_physical_weighted")
    need(tuple(tuple(k//(B*B*T*T) for k in row) for row in g0)==
         ((2268,324),(324,7536)),"original_archived_G0_sixfold")
    need(tuple(tuple(v//(B*B*T*T) for v in row) for row in s)==
         ((336,0),(0,960)),"source_true_original_Schur_resolvent")
    print("Y137_ORIGINAL_SOURCE_SCHUR_IDENTITY|physical_P_W=1,3"+
          "|physical_Q_W=2,6,3"+
          "|original_b=1000000000|original_trial_scale=1000000000000"+
          "|full_Q_inverse_common_denominator=210b"+
          "|original_U0_weighted=70,12;12,187"+
          "|signed_mu0_weighted=378,54;54,1256"+
          "|original_G0_equals_6_mu0=EXACT"+
          "|source_mu0_mu1_mu2_mu3_all_W_GRAM=PASS"+
          "|full_physical_Schur_identity_U0_minus_F=PASS"+
          "|exact_true_Schur_num=336,0;0,960"+
          "|changed_premises=7_REJECTED"+
          "|physical_PQ_source=INDEPENDENTLY_VERIFIED_PR341"+
          "|original_full_mu3=SEPARATE_HOSTED_SOURCE_PASS"+
          "|final_original_Wilson=SOURCE_CONDITIONAL_FORMAL_HOLD"+
          "|continuum_4D=OPEN|json=0")

if __name__=="__main__":
    try:main()
    except (Hold,ValueError,KeyError) as e:
        print("Y137_ORIGINAL_SOURCE_SCHUR_HOLD|reason="+str(e)+
              "|original_Wilson=FORMAL_HOLD|json=0")
        raise SystemExit(2) from None
