#!/usr/bin/env python3
"""Independently rebuild 3x4 S3 strong-r first-gap coefficient from group laws.

Unlike the original shell verifier this uses a HORIZONTAL-FIRST spanning tree,
and independently computes the full characteristic polynomial by Newton
identities over integer matrix traces. No original result rows read; no
fractions, floating point, SciPy or JSON. The all-state remainder is checked
by an independently combined rational numerator inequality.
"""
from collections import Counter
from itertools import permutations
import sys

FAULTS=("drop_electric_move","modify_bridge_edge","change_magnetic_cost")
bad=""
if len(sys.argv)==2 and sys.argv[1].startswith("sabotage="):
    bad=sys.argv[1][9:]
    if bad not in FAULTS:
        raise SystemExit("unknown sabotage")
elif len(sys.argv)!=1:
    raise SystemExit("usage: alternative_tree_3x4_s3.py [sabotage=NAME]")

def require(test, label):
    if not test:
        print("ALTTREE_FAIL|gate="+label+"|json=0",flush=True)
        raise SystemExit(1)

GROUP=tuple(permutations(range(3)))
LOOK={g:i for i,g in enumerate(GROUP)}
PRODUCT=tuple(tuple(LOOK[tuple(GROUP[a][GROUP[b][i]] for i in range(3))]
                    for b in range(6)) for a in range(6))
INV=tuple(next(b for b in range(6) if PRODUCT[a][b]==PRODUCT[b][a]==0)
          for a in range(6))
TR=tuple(a for a in range(1,6) if PRODUCT[a][a]==0)
CONJ=tuple(tuple(PRODUCT[PRODUCT[g][a]][INV[g]] for a in range(6))
           for g in range(6))
CHAR=tuple(sum(int(GROUP[a][i]==i) for i in range(3))-1 for a in range(6))
LX=3
LY=4
SIZE=LX*LY
def site(x,y):
    return (x%LX)*LY+(y%LY)

# Horizontal-first, unlike the original vertical-first audit:
TREE=[(site(x,0),site(x+1,0),site(x,0)) for x in range(LX-1)]
TREE += [(site(x,y),site(x,y+1),SIZE+site(x,y))
         for x in range(LX) for y in range(LY-1)]
TSET={e for u,v,e in TREE}
KEEP=tuple(e for e in range(2*SIZE) if e not in TSET)
require(len(KEEP)==13 and len(TREE)==11 and len(TR)==3,
        "different_spanning_tree_and_generators")

def raw(key):
    links=[0]*24
    for e,a in zip(KEEP,key):links[e]=a
    return links

def canon(links):
    gauge=[0]*SIZE
    for u,v,e in TREE:
        gauge[v]=PRODUCT[gauge[u]][links[e]]
    out=[0]*24
    for x in range(LX):
        for y in range(LY):
            a=site(x,y)
            out[a]=PRODUCT[PRODUCT[gauge[a]][links[a]]][INV[gauge[site(x+1,y)]]]
            out[SIZE+a]=PRODUCT[PRODUCT[gauge[a]][links[SIZE+a]]][INV[gauge[site(x,y+1)]]]
    require(all(out[e]==0 for e in TSET),"gauge_tree_fixed")
    key=tuple(out[e] for e in KEEP)
    return min(tuple(CONJ[g][a] for a in key) for g in range(6))

def weight(key):
    return len({tuple(CONJ[g][a] for a in key) for g in range(6)})

def magnetic(links):
    answer=0
    for x in range(LX):
        for y in range(LY):
            i=site(x,y)
            p=PRODUCT[PRODUCT[PRODUCT[links[i]][links[SIZE+site(x+1,y)]]]
                      [INV[links[site(x,y+1)]]]][INV[links[SIZE+i]]]
            answer+=2-CHAR[p]
    return answer

def neighbors(key,first=False):
    links=raw(key)
    moves=Counter()
    for e in range(24):
        orig=links[e]
        for t in TR:
            if bad=="drop_electric_move" and first and e==0 and t==TR[0]:
                continue
            links[e]=PRODUCT[t][orig]
            moves[canon(links)]+=1
        links[e]=orig
    require(sum(moves.values())==72,"all_seventy_two_link_moves")
    return moves

def multiply(a,b):
    n=len(a)
    return [[sum(a[i][k]*b[k][j] for k in range(n))
             for j in range(n)] for i in range(n)]

def characteristic(a):
    # Exact Newton identities for characteristic polynomial of 8x8 16*C1.
    powers=[]
    x=[row[:] for row in a]
    for k in range(1,9):
        powers.append(sum(x[i][i] for i in range(8)))
        x=multiply(x,a)
    poly=[1]
    for k in range(1,9):
        z=sum(poly[k-j]*powers[j-1] for j in range(1,k+1))
        require(z%k==0,"Newton_integer_division")
        poly.append(-(z//k))
    return poly

def main():
    flats=set()
    for a in range(6):
        for b in range(6):
            if PRODUCT[a][b]!=PRODUCT[b][a]:
                continue
            links=[0]*24
            for y in range(LY):links[site(LX-1,y)]=a
            for x in range(LX):links[SIZE+site(x,LY-1)]=b
            require(magnetic(links)==0,"flat_commuting_plaquettes")
            flats.add(canon(links))
    flats=sorted(flats)
    require(len(flats)==8 and sum(weight(k) for k in flats)==18,
            "eight_flat_orbits")
    first={f:neighbors(f,True) for f in flats}
    shell=sorted(set().union(*(set(c) for c in first.values())))
    require(len(shell)==264,"first_shell_264")
    potentials={s:magnetic(raw(s)) for s in shell}
    if bad=="change_magnetic_cost":
        potentials[shell[0]]=3
    require(set(potentials.values())=={4},"first_shell_magnetic_four")
    more={s:neighbors(s) for s in shell}
    wk={k:weight(k) for k in flats}
    ws={k:weight(k) for k in shell}
    for f in flats:
        for s,c in first[f].items():
            require(wk[f]*c==ws[s]*more[s][f],
                    "orbit_weight_reversed_link")
    C0=[[0]*8 for i in range(8)] # 4*C0
    C1=[[0]*8 for i in range(8)] # 16*C1
    for i,f in enumerate(flats):
        for s,c in first[f].items():
            for j,g in enumerate(flats):
                C0[i][j]+=c*more[s][g]
            for v,csv in more[s].items():
                if v not in more:
                    continue
                for j,g in enumerate(flats):
                    C1[i][j]+=c*csv*more[v][g]
    if bad=="modify_bridge_edge":
        C1[0][1]+=1
    require(C0==[[72 if i==j else 0 for j in range(8)]
                  for i in range(8)],"C0_equals_18_identity")
    for i,f in enumerate(flats):
        for j,g in enumerate(flats):
            require(wk[f]*C1[i][j]==wk[g]*C1[j][i],
                    "weighted_C1_adjointness")
    nonzero={(i,j):C1[i][j] for i in range(8) for j in range(8) if C1[i][j]}
    expected={(0,1):72,(1,0):24,(1,2):48,
              (2,1):72,(3,4):24,(4,3):24}
    require(nonzero==expected,"alternative_tree_exact_C1")
    poly=characteristic(C1)
    require(poly==[1,0,-5760,0,2985984,0,0,0,0],
            "independent_characteristic_polynomial")
    for r in (10000,100000):
        d=3*r
        den=r*r*d*d*(d-72)**3
        remainder=5184*d*d+373248*(d-72)**2
        central=3*d*d*(d-72)**3
        lo=central-2*r*r*remainder
        hi=central+2*r*r*remainder
        require(lo>0 and hi>lo,"global_nonflat_remainder_positive")
        if r==100000:
            scale=10**15
            require((lo*scale)//den==271961
                    and (hi*scale+den-1)//den==328039,
                    "rational_outward_rounding")
    print("ALTTREE_3X4|flat=8|shell1=264|flat_weight_sum=18"
          "|tree=HORIZONTAL_FIRST|C0=18I8|weighted_adjoint=PASS"
          "|C1_spectrum=9/2,3/2,0,0,0,0,-3/2,-9/2"
          "|r_ge_10000_gap_positive=YES|json=0")

if __name__=="__main__":
    main()
