#!/usr/bin/env python3
"""#137 B8: independent all-integer semantic corruption attacks on Q5 moments.

Toy graph intentionally has genuine diagonal self loop, nontrivial w-balanced
offdiag, exterior degree, two frozen energies, 8 source channels. For production
B8, the immutable real graph Q5 census B3/B4 and original source+Gram hashes
remain separately required; a row/pair match alone cannot authenticate them.
"""
import hashlib
import sys

SAMPLES=(69909875505,69949729820)
B=1000000000
W=(1,2,3)
MAGNETIC=(1,2,3)
# True directed grouped transitions (including a true self loop on 0).
EDGES=((0,0,2),(0,1,2),(0,2,3),(1,0,1),(1,2,3),(2,0,1),(2,1,2))
AMPLITUDES=tuple(tuple(tuple((node+1)*(column+2)+(energy*node)+1
                         for column in range(8))
                    for node in range(3)) for energy in range(2))

class Refuse(Exception):
    pass

def need(ok,why):
    if not ok:
        raise Refuse(why)

def fingerprint(amps):
    data=";".join(",".join(",".join(str(value) for value in vec)
                            for vec in energy) for energy in amps)
    return hashlib.sha256(data.encode("ascii")).hexdigest()

def verify_source(amps,frozen):
    need(fingerprint(amps)==frozen, "B8_altered_source_not_equal_frozen_identity")

def graph(edges,weights):
    directed={}
    for i,j,n in edges:
        need(i in range(3) and j in range(3) and 1<=n<=72,
             "B8_invalid_endpoint_or_multiplicity")
        need((i,j) not in directed,"B8_duplicate_directed_record")
        directed[(i,j)]=n
    for (i,j),n in directed.items():
        if i!=j:
            reverse=directed.get((j,i))
            need(reverse is not None,"B8_missing_weighted_reverse")
            need(weights[i]*n==weights[j]*reverse,
                 "B8_unbalanced_weighted_reverse")
    for i in range(3):
        need(sum(n for (a,_),n in directed.items() if a==i)<=72,
             "B8_interior_degree_exceeds_72")
    return directed

def row_matrix(energy,edges=EDGES,weights=W,amps=AMPLITUDES,deg=72,
               diag_scale=6,offdiag_sign=-1,drop_self=False):
    moves=graph(edges,weights)
    z=SAMPLES[energy]
    matrix=[[0]*8 for _ in range(8)]
    for i in range(3):
        q=amps[energy][i]
        d=B*(deg+9*MAGNETIC[i])-z
        for a in range(8):
            for b in range(8):
                term=d*q[b]
                for j in range(3):
                    c=moves.get((i,j),0)
                    if drop_self and i==j:
                        c=0
                    term+=offdiag_sign*B*c*amps[energy][j][b]
                matrix[a][b]+=diag_scale*weights[i]*B*B*q[a]*term
    return matrix

def pair_matrix(energy,edges=EDGES,weights=W,amps=AMPLITUDES,diag_scale=6):
    directed=graph(edges,weights)
    matrix=[[0]*8 for _ in range(8)]
    for i in range(3):
        q=amps[energy][i]
        d=B*(72+9*MAGNETIC[i])-SAMPLES[energy]
        d-=B*directed.get((i,i),0)
        for a in range(8):
            for b in range(8):
                matrix[a][b]+=diag_scale*weights[i]*B*B*d*q[a]*q[b]
        for j in range(i+1,3):
            c=directed.get((i,j),0)
            need((c>0)==(directed.get((j,i),0)>0),"B8_missing_pair")
            if not c:
                continue
            qj=amps[energy][j]
            flux=weights[i]*c
            for a in range(8):
                for b in range(8):
                    matrix[a][b]-=diag_scale*B*B*B*flux*(q[a]*qj[b]+qj[a]*q[b])
    return matrix

def identical(a,b):
    return all(a[i][j]==b[i][j] for i in range(8) for j in range(8))

def gram(energy,amps=AMPLITUDES):
    return [[sum(6*W[i]*B*B*amps[energy][i][a]*amps[energy][i][b]
                 for i in range(3)) for b in range(8)] for a in range(8)]

def refuse(thunk,name):
    try:
        thunk()
    except Refuse:
        return
    raise Refuse(name+"_NOT_REJECTED")

def selftest():
    original=fingerprint(AMPLITUDES)
    need(original==fingerprint(AMPLITUDES),"B8_source_sha_selftest")
    for energy in range(2):
        x=row_matrix(energy)
        y=pair_matrix(energy)
        need(identical(x,y),"B8_reference_row_pair_disagree")
        need(all(x[a][b]==x[b][a] for a in range(8) for b in range(8)),
             "B8_reference_lost_symmetry")
        need(not identical(row_matrix(energy,deg=7),y),
             "B8_missing_exterior_diagonal_not_detected")
        need(not identical(row_matrix(energy,drop_self=True),y),
             "B8_selfloop_discard_not_detected")
        need(not identical(row_matrix(energy,offdiag_sign=1),y),
             "B8_wrong_electric_sign_not_detected")
        need(not identical(row_matrix(energy,diag_scale=36),y),
             "B8_six_double_applied_not_detected")
        need(not identical(row_matrix(energy),pair_matrix(energy,diag_scale=36)),
             "B8_pair_six_double_applied_not_detected")
    refuse(lambda:graph(EDGES[:-1],W),"B8_missing_reverse")
    refuse(lambda:graph(EDGES+((1,0,1),),W),"B8_duplicate_reverse")
    changed=tuple((i,j,n+1 if (i,j)==(1,0) else n) for i,j,n in EDGES)
    refuse(lambda:graph(changed,W),"B8_weighted_multiplicity")
    refuse(lambda:graph(EDGES,(1,3,3)),"B8_wrong_orbit_weight")
    corrupt=list(AMPLITUDES)
    first=list(corrupt[0])
    row=list(first[1])
    row[0]+=1
    first[1]=tuple(row)
    corrupt[0]=tuple(first)
    corrupt=tuple(corrupt)
    refuse(lambda:verify_source(corrupt,original),"B8_signed_source_amplitude")
    swapped=(AMPLITUDES[1],AMPLITUDES[0])
    refuse(lambda:verify_source(swapped,original),"B8_energy_sample_swap")
    # A single source sign flip leaves mu2 invariant, changes mu3 due to
    # cross terms: Stage C must authenticate the physical Q4 sign separately.
    signed=[list(energy) for energy in AMPLITUDES]
    signed=tuple(tuple(tuple(-u for u in q) if i==1 else q
                       for i,q in enumerate(energy)) for energy in signed)
    for energy in range(2):
        need(gram(energy)==gram(energy,signed),"B8_sign_flip_changes_mu2")
        need(not identical(row_matrix(energy),row_matrix(energy,amps=signed)),
             "B8_missing_signed_mu3_cross_sensitivity")
    # Live production receipt verifier attacks run separately using
    # b6_gram_accept.py attack-toy; string-only hashes do not certify refusal.
    print("Y137_B8_TOY|energies=2|entries_checked=128|reference_row_pair=EXACT"+
          "|magnetic_and_exterior_diagonal=PASS|selfloop_omission=REFUSED"+
          "|wrong_electric_sign=REFUSED|double_factor_six=REFUSED"+
          "|missing_reverse=REFUSED|duplicate_reverse=REFUSED"+
          "|weighted_multiplicity=REFUSED|wrong_orbit_weight=REFUSED"+
          "|tampered_amplitude=REFUSED|sample_swap=REFUSED"+
          "|Q4_sign_flip_mu2_invariant_mu3_changed=PASS"+
          "|forged_PASS_receipt=SEPARATE_B6_VERIFIER_ATTACK|real_Q5_mu3=UNCHANGED"+
          "|signed_Q4_K3=HOLD|Wilson_weight=HOLD|json=0")

if __name__=="__main__":
    try:
        need(sys.argv[1:]==["toy"],"B8_usage")
        selftest()
    except (Refuse,ValueError,KeyError) as e:
        print("Y137_B8_REFUSE|reason="+str(e)+"|json=0",flush=True)
        raise SystemExit(1) from None
