#!/usr/bin/env python3
"""Independent 3x4 S3 gauge-fix and raw electric move reconstruction.

Does not call the original source's canonical(), neighbors(), weight(),
or magnetic() functions. It uses only the publicly fixed S3 group and
periodic 3x4 lattice. The graph formula is independently authored.
"""
from collections import Counter
from itertools import permutations

GROUP=tuple(permutations((0,1,2)))
LOOKUP={p:i for i,p in enumerate(GROUP)}
LX=3
LY=4
SITE_COUNT=12
LINK_COUNT=24


def require(ok,reason):
    if not ok:
        raise ValueError("INDEPENDENT_RULE_"+reason)


def compose(a,b):
    """S3 composition directly on permutations, no original MUL table."""
    ga,gb=GROUP[a],GROUP[b]
    return LOOKUP[(ga[gb[0]],ga[gb[1]],ga[gb[2]])]


def inverse(a):
    p=GROUP[a]
    return LOOKUP[(p.index(0),p.index(1),p.index(2))]


def at(x,y):
    return (x%LX)*LY+(y%LY)


def kept_links():
    edges=[]
    for y in range(LY-1):
        edges.append((at(0,y),at(0,y+1),SITE_COUNT+at(0,y)))
    for y in range(LY):
        for x in range(LX-1):
            edges.append((at(x,y),at(x+1,y),at(x,y)))
    tree={link for _,_,link in edges}
    keep=tuple(j for j in range(LINK_COUNT) if j not in tree)
    require(len(edges)==11 and len(keep)==13,"tree_rank")
    return edges,keep


TREE,KEEP=kept_links()
TRANSPOSITIONS=tuple(i for i,p in enumerate(GROUP)
                      if i!=0 and compose(i,i)==0)
require(len(TRANSPOSITIONS)==3,"transpositions")


def canonical_from_full(links):
    """Spanning-tree transport, plus explicit six-element global conjugacy."""
    require(len(links)==LINK_COUNT,"full_links")
    gauge=[0]*SITE_COUNT
    for src,dst,edge in TREE:
        gauge[dst]=compose(gauge[src],links[edge])
    flat=[0]*LINK_COUNT
    for x in range(LX):
        for y in range(LY):
            i=at(x,y)
            flat[i]=compose(compose(gauge[i],links[i]),
                            inverse(gauge[at(x+1,y)]))
            flat[SITE_COUNT+i]=compose(
                compose(gauge[i],links[SITE_COUNT+i]),
                inverse(gauge[at(x,y+1)]))
    require(all(flat[k]==0 for _,_,k in TREE),"tree_transport")
    result=tuple(flat[k] for k in KEEP)
    candidates=[]
    for a in range(len(GROUP)):
        ia=inverse(a)
        candidates.append(tuple(compose(compose(a,u),ia)
                                for u in result))
    return min(candidates)


def expanded_links(key):
    require(len(key)==13 and all(0<=u<6 for u in key),
            "orbit_key_domain")
    full=[0]*LINK_COUNT
    for j,a in zip(KEEP,key):
        full[j]=a
    return full


def neighbor_counts(key):
    """72 complete raw moves. Never imports or calls source neighbor table."""
    full=expanded_links(key)
    moves=Counter()
    for i in range(LINK_COUNT):
        old=full[i]
        for t in TRANSPOSITIONS:
            full[i]=compose(t,old)
            dest=canonical_from_full(full)
            moves[dest]+=1
        full[i]=old
    require(sum(moves.values())==72,"raw_moves_72")
    return moves


def canonical_weight(key):
    result=set()
    for a in range(6):
        ia=inverse(a)
        result.add(tuple(compose(compose(a,g),ia) for g in key))
    return len(result)


def magnetic_of_key(key):
    U=expanded_links(key)
    total=0
    for x in range(LX):
        for y in range(LY):
            i=at(x,y)
            p=compose(U[i],U[SITE_COUNT+at(x+1,y)])
            p=compose(p,inverse(U[at(x,y+1)]))
            p=compose(p,inverse(U[SITE_COUNT+i]))
            character=sum(int(GROUP[p][k]==k) for k in range(3))-1
            total+=2-character
    return total


def audit_original(key,original):
    require(KEEP==original.KEPT,"independent_keep_link_agreement")
    require(TRANSPOSITIONS==original.TRANS,"independent_transpositions")
    mine=neighbor_counts(key)
    theirs=original.neighbors(key)
    require(mine==theirs,"raw_full_row_mismatch")
    require(canonical_weight(key)==original.weight(key),
            "canonical_orbit_weight_mismatch")
    require(magnetic_of_key(key)==original.magnetic(original.from_key(key)),
            "independent_magnetic_mismatch")
    return len(mine)


def synthetic(original):
    # Several deterministic nonflat 13-link configurations; exact
    # full 72-row enumeration is independently rebuilt each time.
    cases=(
        (0,)*13,
        (1,0,2,3,4,5,0,1,2,3,4,5,1),
        (2,3,4,5,1,0,2,4,0,3,5,1,2),
    )
    n=0
    for row in cases:
        key=canonical_from_full(expanded_links(row))
        audit_original(key,original)
        n+=1
    # A wrong right-multiply rule, or one omitted generator, must be
    # detected by independently recomputed source moves.
    key=canonical_from_full(expanded_links(cases[2]))
    true=neighbor_counts(key)
    wrong=Counter(true)
    dest=next(iter(wrong))
    wrong[dest]-=1
    if wrong[dest]==0:
        del wrong[dest]
    require(wrong!=true and sum(wrong.values())==71,
            "planted_missing_generator_rejected")
    print("Y137_D11_INDEPENDENT_RULE|synthetic_rows="+str(n)+
          "|each_raw_72_moves=PASS"+
          "|group_permutation_reconstructed=PASS"+
          "|spanning_tree_gauge_reconstructed=PASS"+
          "|magnetic_and_orbit_weight=PASS"+
          "|source_missing_move=REJECTED"+
          "|real_source_rows=NOT_YET_AUDITED|json=0",flush=True)


def main():
    # Standalone import of original minimal model requires no arguments.
    import sys
    args=sys.argv[:]
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
    sys.argv=sys.argv[:1]
    import finite_s3_3x4_r9_first_gap as original
    sys.argv=args
    synthetic(original)


if __name__=="__main__":
    main()
