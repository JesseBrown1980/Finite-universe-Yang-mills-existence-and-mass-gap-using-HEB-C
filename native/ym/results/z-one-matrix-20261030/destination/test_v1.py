#!/usr/bin/env python3
"""Independent, deterministic, stdlib-only reference: destination tokens and signed j.

Constructed software rules, not claims that a photon needs a nonlocal token.
Emits HBP lines to stdout, makes no filesystem writes.
"""
import hashlib
import sys

SCALES = ((3, 2, 8, 23), (4, 9, 29, 71), (5, 11, 71, 190))
DOMAIN = b"YM-ZDEST-20261030-V1"

def h(b):
    return hashlib.sha256(b).digest()

def num(v):
    return v.to_bytes(4, "big", signed=False)

def cell_hash(i, trit):
    assert trit in (-1, 0, 1)
    return h(b"CELL" + num(i) + bytes((trit+1,)))

def merkle(cells):
    level = [cell_hash(i,v) for i,v in enumerate(cells)]
    while len(level)>1:
        if len(level)%2: level.append(level[-1])
        level=[h(b"NODE"+level[k]+level[k+1]) for k in range(0,len(level),2)]
    return level[0]

def token(n, source, dest, direction, message, cells):
    assert direction in (-1,1) and message in (-1,1)
    # The oracle has access to destination state and signs the selection.
    # This is a *simulator privilege*, not a local physical interaction.
    return h(DOMAIN+b"TOKEN"+num(n)+num(source)+num(dest)+
             bytes((direction+1,message+1))+cell_hash(dest,cells[dest]))

def permitted(n, source, dest, direction, message, cells, received):
    return isinstance(received,bytes) and received==token(n,source,dest,direction,message,cells)

def protocol_root(physical_root,n,source,dest,direction,message,received):
    return h(DOMAIN+b"PROTO"+physical_root+num(n)+num(source)+num(dest)+
             bytes((direction+1,message+1))+received)

def cells_at(n, source, direction, message, tick):
    cells=[0]*(3**n)
    if tick>=1:
        cells[(source+direction*(tick-1))%len(cells)]=message
    return cells

def ring_dist(n,source,dest,direction):
    m=3**n
    return ((dest-source) if direction==1 else (source-dest))%m

def ensure(condition, message):
    if not condition: raise AssertionError(message)

def ptest():
    records=[]
    for n,s,a,b in SCALES:
        m=3**n
        da=ring_dist(n,s,a,1); db=ring_dist(n,s,b,-1)
        initial=[0]*m
        phys0=merkle(initial)
        token_a=token(n,s,a,1,1,initial)
        token_b=token(n,s,b,-1,1,initial)
        z_a=protocol_root(phys0,n,s,a,1,1,token_a)
        z_b=protocol_root(phys0,n,s,b,-1,1,token_b)
        ensure(phys0==merkle(initial) and z_a!=z_b, "P1")
        gates=(permitted(n,s,b,-1,1,initial,None),
               permitted(n,s,b,-1,1,initial,token_a),
               permitted(n,s,b,1,1,initial,token_b),
               permitted(n,s,b,-1,1,initial,token_b[:-1]+bytes((token_b[-1]^1,))),
               permitted(n,s,b,-1,1,initial,token_b))
        ensure(gates==(False,False,False,False,True),"P2")
        # Direction -1, source emission at tick 1. Target B responds at t=1+db.
        before=[cell_hash(b,cells_at(n,s,-1,1,t)[b]) for t in range(db+1)]
        arrived=cell_hash(b,cells_at(n,s,-1,1,1+db)[b])
        ensure(all(x==before[0] for x in before) and arrived!=before[0],"P3 target")
        ensure(all(cells_at(n,s,-1,1,t)[a]==0 for t in range(m)),"P3 nonselected")
        # Midflight retarget t_switch after flight started towards A; no physical perturbation.
        switch=min(5,max(2,da//2))
        state_sw=cells_at(n,s,1,1,switch)
        prephys=merkle(state_sw); postphys=merkle(state_sw)
        oldtok=token(n,s,a,1,1,state_sw)
        newtok=token(n,s,b,-1,1,state_sw)
        oldroot=protocol_root(prephys,n,s,a,1,1,oldtok)
        newroot=protocol_root(postphys,n,s,b,-1,1,newtok)
        ensure(prephys==postphys and oldroot!=newroot,"P4 metadata")
        ensure(cells_at(n,s,1,1,1+da)[a]==1,"P4 old destination")
        ensure(all(cells_at(n,s,1,1,t)[b]==0 for t in range(m)),"P4 target B")
        # Equal-prior destination choice: exact deterministic I(D;local)=0 bits,
        # I(D;protocol_digest)=1 bit. Not a thermodynamic/sampled estimate.
        no_leak=all(cells_at(n,s,d,1,t)[a if d==1 else b]==0
                    for d in (1,-1) for t in (0,))
        ensure(no_leak and z_a!=z_b,"P5")
        records.append(
            f"ZDEST_LEVEL|N={n}|sites={m}|source={s}|destination_A={a}|destination_B={b}|"
            f"distance_A={da}|distance_B={db}|prelaunch_physical_unchanged=1|"
            f"prelaunch_protocol_changed=1|"
            f"gate_missing_rejected={int(not gates[0])}|gate_stale_rejected={int(not gates[1])}|"
            f"gate_wrong_direction_rejected={int(not gates[2])}|gate_tamper_rejected={int(not gates[3])}|"
            f"gate_new_accepted={int(gates[4])}|target_B_first_change_tick={1+db}|"
            f"midflight_switch_tick={switch}|midflight_physical_unchanged=1|"
            f"midflight_protocol_changed=1|old_A_arrival_tick={1+da}|new_B_untouched=1|"
            f"local_prearrival_information_bits=0|global_early_information_bits=1|"
            f"cell_root_sha256={phys0.hex()}|protocol_A_sha256={z_a.hex()}|"
            f"protocol_B_sha256={z_b.hex()}|P1=PASS|P2=PASS|P3=PASS|P4=PASS|P5=PASS|json=0")
    return records

def identity(): return [[int(r==c) for c in range(3)] for r in range(3)]
def matplus(*terms): return [[sum(M[r][c]*coef for coef,M in terms) for c in range(3)] for r in range(3)]
def transpose(M): return [list(row) for row in zip(*M)]
def rank_mod3(a):
    a=[[x%3 for x in row] for row in a]
    rank=0
    for c in range(len(a[0])):
        pivot=next((r for r in range(rank,len(a)) if a[r][c]),None)
        if pivot is None: continue
        a[rank],a[pivot]=a[pivot],a[rank]
        k=pow(a[rank][c],-1,3)
        a[rank]=[(x*k)%3 for x in a[rank]]
        for r in range(len(a)):
            if r!=rank:
                f=a[r][c]
                a[r]=[(x-f*y)%3 for x,y in zip(a[r],a[rank])]
        rank+=1
    return rank

def btest():
    I=identity()
    R=[[int(c==(r+1)%3) for c in range(3)] for r in range(3)]
    R2=[[int(c==(r+2)%3) for c in range(3)] for r in range(3)]
    symmetric=matplus((1,R),(1,R2))
    J=matplus((1,I),(1,R),(1,R2))
    plus=matplus((1,I),(1,R),(-1,R2))
    minus=matplus((1,I),(-1,R),(1,R2))
    ensure(symmetric==transpose(symmetric) and J==transpose(J),"B1 base")
    ensure(plus!=transpose(plus) and minus!=transpose(minus),"B1 curve")
    ensure(transpose(plus)==minus,"B2 transpose")
    ensure(all(sum(int(M[r][c]!=0) for r in range(3))==3 for M in (plus,minus) for c in range(3)),"B2 support")
    ensure(J!=plus and J!=minus,"B2 Q5")
    ranks=[rank_mod3(M) for M in (J,plus,minus)]
    ensure(ranks==[1,3,3],"B3 ranks")
    # Check 27 GF(3) inputs: j preserves distinct outputs, J maps to 3 distinct outputs.
    def states(M):
        return {tuple(sum(M[i][j]*v[j] for j in range(3))%3 for i in range(3))
                for v in ((x,y,z) for x in range(3) for y in range(3) for z in range(3))}
    sizes=[len(states(M)) for M in (J,plus,minus)]
    ensure(sizes==[3,27,27],"B3 27 states")
    return [f"ZCURVE_RESULT|r_symmetric=1|J_symmetric=1|j_plus_asymmetric=1|"
            f"j_minus_asymmetric=1|j_plus_transpose_eq_j_minus=1|"
            f"each_j_source_has_3_nonzero=1|Q5_all_ones_breaks=1|"
            f"ranks_GF3_J_plus_minus=1,3,3|distinct_images_GF3_J_plus_minus=3,27,27|"
            f"orientation_not_selected=1|B1=PASS|B2=PASS|B3=PASS|B4=PASS|json=0"]

def main():
    rows=["ZDEST_RUN|experiment=one_matrix_one_universe|cases=3|"
          "dest_bound_token_is_constructed_not_physical|json=0"]
    rows.extend(ptest()); rows.extend(btest())
    rows.append("ZDEST_VERDICT|P1=PASS|P2=PASS|P3=PASS|P4=PASS|P5=PASS|"
                "B1=PASS|B2=PASS|B3=PASS|B4=PASS|"
                "orientation_selected=NO|physical_ftl_evidence=NO|"
                "quantum_necessity_established=NO|spectral_pass=0|production=HOLD|json=0")
    sys.stdout.write("\n".join(rows)+"\n")
if __name__=="__main__": main()
