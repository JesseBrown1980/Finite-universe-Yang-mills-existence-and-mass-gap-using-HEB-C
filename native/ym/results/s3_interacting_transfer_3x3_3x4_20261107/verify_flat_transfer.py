#!/usr/bin/env python3
"""3x3 global first-gap transfer from sealed source certificates; 3x4 flat
winding selector. Independent exact S3 permutations; integer-only. The new
checker DOES NOT recompute the full 10M/2.17B spectral inertia.

13 rows frozen in parent commit 550926527cda3ed7024d6bc91e638ce12ab4dc9d.
The global first gap at r=27 follows *conditionally* on the existing
published full-space r=9 and zero-momentum r=27 receipts being valid.
"""
from hashlib import sha1,sha256
from itertools import permutations
from pathlib import Path
import sys

CONTROLS=("wrong_T_count","wrong_r27_gap","incorrect_r243_gap",
          "nonzero_flat_Oalt","wrong_flat_54","untraced_gauge_claim")
fault=""
if len(sys.argv)>2 or (len(sys.argv)==2 and
        (not sys.argv[1].startswith("sabotage=")
         or sys.argv[1][9:] not in CONTROLS)):
    print("usage: verify_flat_transfer.py [sabotage=NAME]")
    sys.exit(2)
if len(sys.argv)==2:
    fault=sys.argv[1][9:]


def check(test, name):
    if not test:
        print("FAILED|check="+name+"|json=0")
        sys.exit(1)


def emit(label,**props):
    print(label+"|"+"|".join(str(k)+"="+str(v) for k,v in props.items())
          +"|json=0",flush=True)


perms=tuple(permutations(range(3)))
index={p:i for i,p in enumerate(perms)}
table=tuple(tuple(index[tuple(perms[a][perms[b][j]] for j in range(3))]
                  for b in range(6)) for a in range(6))
inverse=tuple(next(b for b in range(6)
                   if table[a][b]==table[b][a]==0) for a in range(6))
trans=tuple(a for a in range(6) if table[a][a]==0 and a!=0)
check(len(trans)==3,"S3_transposition_count")


def mul(*args):
    out=0
    for a in args:
        out=table[out][a]
    return out


def character(a):
    return sum(int(perms[a][i]==i) for i in range(3))-1


def conjugate(g,a):
    return mul(g,a,inverse[g])


def all_classes():
    seen=set()
    result=[]
    for a in range(6):
        for b in range(6):
            if table[a][b]!=table[b][a]:
                continue
            idx=6*a+b
            if idx in seen:
                continue
            orbit={6*conjugate(g,a)+conjugate(g,b) for g in range(6)}
            check(len(orbit) in (1,2,3),"commuting_orbit_size")
            check(all(table[x//6][x%6]==table[x%6][x//6]
                      for x in orbit),"commuting_orbit_closed")
            seen.update(orbit)
            result.append((a,b,orbit))
    check(len(result)==8 and len(seen)==18,"eight_magnetic_flat_classes")
    where={pair:i for i,(_,_,o) in enumerate(result) for pair in o}
    swaps=[where[6*b+a] for a,b,_ in result]
    check(all(swaps[swaps[i]]==i for i in range(8)),
          "flat_exchange_involution")
    fixed=sum(int(swaps[i]==i) for i in range(8))
    check(fixed==4,"flat_swap_fixed_count")
    check((8+fixed)//2==6 and (8-fixed)//2==2,
          "flat_axis_parity_split")
    plus=[character(a)+character(b) for a,b,_ in result]
    minus=[character(a)-character(b) for a,b,_ in result]
    check(all(plus[swaps[i]]==plus[i]
              and minus[swaps[i]]==-minus[i] for i in range(8)),
          "flat_plus_minus_parities")
    check(sum(int(x!=0) for x in plus)==7,"flat_square_even_rank")
    check(sum(int(x!=0) for x in minus)==4,"flat_square_odd_rank")
    check(sum(len(o) for _,_,o in result)==18,"flat_orbit_weight_sum")
    emit("TRANSFER_FLAT_ORBITS",classes=8,raw_commuting_pairs=18,
         total_residual_weights=18,axis_swap_fixed=4,
         square_even_dim=6,square_odd_dim=2,
         square_Oplus_flat_rank=7,square_Ominus_flat_rank=4)
    return result,swaps


def place(Lx,Ly,x,y):
    return (x%Lx)*Ly+(y%Ly)


def flat_configuration(Lx,Ly,a,b):
    V=Lx*Ly
    U=[0]*(2*V)
    for y in range(Ly):
        U[place(Lx,Ly,Lx-1,y)]=a
    for x in range(Lx):
        U[V+place(Lx,Ly,x,Ly-1)]=b
    return U


def plaquette(U,Lx,Ly,x,y):
    V=Lx*Ly
    s=place(Lx,Ly,x,y)
    right=place(Lx,Ly,x+1,y)
    up=place(Lx,Ly,x,y+1)
    return mul(U[s],U[V+right],inverse[U[up]],inverse[U[V+s]])


def magnetic(U,Lx,Ly):
    return sum(2-character(plaquette(U,Lx,Ly,x,y))
               for x in range(Lx) for y in range(Ly))


def translation(U,Lx,Ly,dx,dy):
    V=Lx*Ly
    Z=[0]*(2*V)
    for x in range(Lx):
        for y in range(Ly):
            s=place(Lx,Ly,x,y)
            src=place(Lx,Ly,x+dx,y+dy)
            Z[s]=U[src]
            Z[V+s]=U[V+src]
    return Z


def gauge(U,Lx,Ly,h):
    V=Lx*Ly
    Z=[0]*(2*V)
    for x in range(Lx):
        for y in range(Ly):
            s=place(Lx,Ly,x,y)
            Z[s]=mul(h[s],U[s],inverse[h[place(Lx,Ly,x+1,y)]])
            Z[V+s]=mul(h[s],U[V+s],inverse[h[place(Lx,Ly,x,y+1)]])
    return Z


def gauge_related(U,Vlinks,Lx,Ly):
    # Exhaustively search the six possible root-frame choices, with
    # all other vertex frames uniquely propagated along any connected tree.
    V=Lx*Ly
    edges=[]
    for x in range(Lx):
        for y in range(Ly):
            s=place(Lx,Ly,x,y)
            edges.append((s,place(Lx,Ly,x+1,y),s))
            edges.append((s,place(Lx,Ly,x,y+1),V+s))
    for root in range(6):
        frame=[-1]*V
        frame[0]=root
        for _ in range(V):
            updated=False
            for a,b,e in edges:
                if frame[a]!=-1 and frame[b]==-1:
                    frame[b]=mul(inverse[Vlinks[e]],frame[a],U[e])
                    updated=True
                elif frame[b]!=-1 and frame[a]==-1:
                    frame[a]=mul(Vlinks[e],frame[b],inverse[U[e]])
                    updated=True
            if not updated:
                break
        if all(h!=-1 for h in frame) and gauge(U,Lx,Ly,frame)==Vlinks:
            return True
    return False


def winding_values(U,Lx,Ly):
    V=Lx*Ly
    wx=[character(mul(*[U[place(Lx,Ly,x,y)]
                            for x in range(Lx)])) for y in range(Ly)]
    wy=[character(mul(*[U[V+place(Lx,Ly,x,y)]
                            for y in range(Ly)])) for x in range(Lx)]
    return wx,wy


def examine_flat(classes,swaps):
    for Lx,Ly in ((3,3),(3,4)):
        V=Lx*Ly
        flat2flat=0
        gauge_equiv=0
        diag=3*(2*V)
        for j,(a,b,_) in enumerate(classes):
            U=flat_configuration(Lx,Ly,a,b)
            check(magnetic(U,Lx,Ly)==0,
                  "commuting_flat_plaquettes_"+str(V))
            wx,wy=winding_values(U,Lx,Ly)
            check(wx==[character(a)]*Ly
                  and wy==[character(b)]*Lx,"flat_winding_seams")
            if V==9:
                even=3*(character(a)+character(b))
                odd=3*(character(a)-character(b))
                check(even==3*(character(classes[swaps[j]][0])
                                +character(classes[swaps[j]][1]))
                      and odd==-3*(character(classes[swaps[j]][0])
                                   -character(classes[swaps[j]][1])),
                      "flat_exchange_Wilson_selection")
            else:
                alt=sum(wx[y]*(1 if y%2==0 else -1)
                        for y in range(4))
                if fault=="nonzero_flat_Oalt":
                    check(alt!=0,"RED_nonzero_flat_Oalt")
                check(alt==0,"alternating_winding_zero_on_flat")
                xsum=sum(wx)
                ysum=sum(wy)
                check(xsum==4*character(a) and ysum==3*character(b),
                      "rectangular_flat_winding_values")
            for dx,dy in ((1,0),(0,1)):
                shifted=translation(U,Lx,Ly,dx,dy)
                check(gauge_related(U,shifted,Lx,Ly),
                      "flat_translations_gauge_equivalent")
                gauge_equiv+=1
            for e in range(2*V):
                for t in trans:
                    changed=U[:]
                    changed[e]=table[t][changed[e]]
                    check(magnetic(changed,Lx,Ly)>0,
                          "single_link_move_outside_flat")
                    flat2flat+=1
        if fault=="wrong_flat_54" and V==9:
            check(diag==55,"RED_wrong_flat_54")
        check(diag==54 if V==9 else diag==72,
              "flat_electric_compression")
        emit("TRANSFER_FLAT_MATRIX",shape=str(Lx)+"x"+str(Ly),
             flat_orbits=8,magnetic_potential=0,
             flat_compressed_H_diagonal=diag,
             flat_off_diagonal="ZERO_EXACT",
             single_link_changed_nonflat=flat2flat,
             translation_gauge_equivalences=gauge_equiv,
             flat_low_state_translation="MOMENTUM_ZERO")
    osum=[4*character(a) for a,_,_ in classes]
    ysum=[3*character(b) for _,b,_ in classes]
    check(sum(int(v!=0) for v in osum)==6
          and sum(int(v!=0) for v in ysum)==6,
          "rect_winding_nonzero_ranks")
    emit("TRANSFER_RECT_SELECTION",shape="3x4",
         alternating_winding_flat_compression="IDENTICALLY_ZERO",
         horizontal_winding_sum_flat_rank=6,
         vertical_winding_sum_flat_rank=6,
         nonzero_momentum_E1_overlap="NOT_INFERRED_FROM_FLAT",
         first_excitation_sector="OPEN")
    U=[0]*18
    h=[0]*9
    h[0]=trans[0]
    GU=gauge(U,3,3,h)
    check(character(U[0])!=character(GU[0]),
          "bare_link_character_is_not_gauge_invariant")
    if fault=="untraced_gauge_claim":
        check(character(U[0])==character(GU[0]),
              "RED_untraced_gauge_claim")



def verify_original_git_blob(raw,expected,name):
    # The pinned source SHA identifies the exact content used in the
    # original spectral certificates, not merely a forged PASS row.
    blob=b"blob "+str(len(raw)).encode("ascii")+bytes((0,))+raw
    actual=sha1(blob).hexdigest()
    check(actual==expected,"pinned_original_blob_"+name)


def read_lines(root,*parts):
    raw=root.joinpath(*parts).read_bytes()
    return raw,[x.decode("utf-8") for x in raw.splitlines()]


def require_one(lines,prefix):
    matches=[s for s in lines if s.startswith(prefix)]
    check(len(matches)==1,"unique_row_"+prefix.split("|")[0])
    return matches[0]


def entry(line,key):
    bits=line.split("|")
    xs=[v.split("=",1)[1] for v in bits
        if v.startswith(key+"=")]
    check(len(xs)==1,"single_field_"+key)
    return xs[0]


def require_same(test,gate):
    check(test,gate)


def cert_transfer(root):
    folder=("native","ym","results","3x3_full_space")
    cert_bytes,cert=read_lines(root,*folder,"CERTIFY-3X3-FULLSPACE.hbp")
    dim_bytes,dims=read_lines(root,*folder,"DIMENSION-RECONCILIATION.hbp")
    frozen_bytes,frozen=read_lines(root,"native","ym","reference",
                        "ym3x3_frozen_8fd12e6.hbp")
    verify_original_git_blob(
        cert_bytes,"4da4a753639c18d4c63313951be40198f4305c89","fullspace_r9")
    verify_original_git_blob(
        dim_bytes,"fe52a9541f4e1bd74f95989767d80752310a6cfd","dimension")
    verify_original_git_blob(
        frozen_bytes,"bdb52c0e6be7eb39c0b6a44548f30e2c2f0f5e43",
        "T_r27_reference")
    head=require_one(cert,"CERTIFY|root=root|")
    check("t1_milli=52533422|" in head and
          "tF_milli=71900000|" in head,
          "original_full_thresholds")
    row=require_one(cert,"CERTIFY_VERDICT|")
    check("PASS|N_full_t1=8|N_full_tF=8|" in row,
          "original_full_inertia_count")
    green=require_one(cert,"CERTIFY_CORRECTNESS|")
    check("CERTIFIED|depths=0-4|nodes_green=340|" in green,
          "fullspace_green_certificate")
    expected={0:2,1:10,2:32,3:280,4:16}
    for d,num in expected.items():
        lines=[s for s in cert if s.startswith("NNEST|depth="+str(d)+"|")]
        check(len(lines)==num and all("state=CONVERGED|" in s
              for s in lines),"fullspace_sealed_depth_"+str(d))
    for t in (52533422,71900000):
        sector=require_one(cert,"NNEST|depth=1|node=t"+str(t)+".T|")
        full=require_one(cert,"NNEST|depth=0|node=t"+str(t)+"|")
        Tcount=7 if fault=="wrong_T_count" else 8
        if fault=="wrong_T_count":
            check(Tcount==int(entry(sector,"reported")),
                  "RED_wrong_T_count")
        check(int(entry(sector,"reported"))==8 and
              int(entry(full,"reported"))==8,
              "full_matches_zero_momentum_"+str(t))
    tdimension=require_one(dims,"SECTOR_TOTAL|kernel=T|")
    dimension=require_one(dims,"DIMENSION|L=3x3|")
    check("states=1122211|" in tdimension and
          "mobius_dimension=10097891|gauge_orbits=10097891|" in dimension
          and "result=PASS|" in dimension,"sector_dimensions")
    emit("TRANSFER_SOURCE_FULL",at_r=9,
         t1="52.533422",tF="71.900000",
         N_full_t1=8,N_T_t1=8,N_full_tF=8,N_T_tF=8,
         certificate_nodes_green=340,full_dimension=10097891,
         T_dimension=1122211,receipt_sha256=sha256(cert_bytes).hexdigest(),
         source="PINNED_ORIGINAL_CERTIFICATE")
    source=require_one(frozen,"REFERENCE|")
    check("commit=8fd12e6a54354f0b7483e05db56eeec97946a81c|" in source
          and "status=FROZEN|" in source,
          "frozen_zero_momentum_reference")
    flat=[s for s in frozen if s.startswith("FLATCOMP|")]
    check(len(flat)==4 and
          sum(int(entry(s,"flat_states")) for s in flat)==8
          and all("flat_flat_couplings=0|" in s for s in flat),
          "pinned_zero_momentum_eight_flat")
    for s in flat:
        if int(entry(s,"flat_states"))>0:
            check(entry(s,"flat_diag_max")=="54","pinned_flat_54")
    r27=require_one(frozen,"SHELL_CLUSTER_CERT|L=3x3|r=27|")
    check("N(t0)=0|" in r27 and "N(ts)=1|" in r27
          and "sector_counts_ts=1,1:1@" in r27
          and "E1_in=[53493345,53493390]/1000000|" in r27
          and "E2_in=[53495357,53495404]/1000000|" in r27
          and "first_splitting_E2_minus_E1_in=[1967,2059]/1000000|" in r27
          and "result=PASS|" in r27,
          "frozen_T_r27_first_level_bounds")
    if fault=="wrong_r27_gap":
        check(53495357-53493390==1968,"RED_wrong_r27_gap")
    check(53495357-53493390==1967
          and 53495404-53493345==2059,
          "first_gap_outward_interval_difference")
    r27shell=require_one(frozen,"SHELL_GAP_CERT|L=3x3|r=27|")
    check("N(t1)=8|" in r27shell and "N(tB)=8|" in r27shell
          and "result=PASS|" in r27shell,
          "r27_T_full_cluster_certificate")
    r243=require_one(frozen,"SHELL_CLUSTER_CERT|L=3x3|r=243|")
    check("first_splitting=INCONCLUSIVE(" in r243
          and "result=PASS|" in r243,
          "r243_first_gap_still_unknown")
    if fault=="incorrect_r243_gap":
        check("first_splitting_E2_minus_E1_in=" in r243,
              "RED_incorrect_r243_gap")
    emit("TRANSFER_R27_T",r=27,JE=1,
         T_E1_lower_micro=53493345,T_E1_upper_micro=53493390,
         T_E2_lower_micro=53495357,T_E2_upper_micro=53495404,
         T_first_gap_lower_micro=1967,T_first_gap_upper_micro=2059,
         first_state_sector_in_original_reference="1,1",
         exchange_parity_of_global_E1="NOT_IDENTIFIED")
    # Proof:
    # H(r)−H(9)=(r−9)M is positive semidefinite for r>=9.
    # Consequently E9(full,r)>=E9(full,9)>=71.9.
    # The eight exact flat states are translation-zero, and compress H(r)
    # to 54 I_8. Min-max implies E8(T,r)<=54.
    # As 54<71.9<=E9(full,r), the first eight full-space levels lie in T.
    check(54*1000000<71900000,"flat_vs_nonflat_spectral_separator")
    emit("TRANSFER_GLOBAL_THEOREM",lattice="3x3",r_range="r_ge_9",
         E9_full_lower="71.900000",E8_T_upper="54.000000",
         transfer_proof="MINMAX_PLUS_MONOTONE_MAGNETIC",
         low_eight_all_zero_momentum="CERTIFICATE_COMPOSITION_PASS",
         independent_full_space_inertia="NOT_RERUN")
    emit("TRANSFER_GLOBAL_R27_GAP",lattice="3x3",r=27,
         JE=1,E1_global_interval="[53.493345,53.493390]",
         E2_global_interval="[53.495357,53.495404]",
         first_gap_global_interval="[0.001967,0.002059]",
         status="CERTIFICATE_COMPOSITION_PASS",
         new_full_space_eigenanalysis="NOT_RUN",
         underlying_HBP_source="EXISTING_CERTIFICATES")
    emit("TRANSFER_R243_HOLD",lattice="3x3",r=243,
         full_first_eight_zero_momentum="YES",
         first_gap_interval="INCONCLUSIVE",
         new_claim="NONE")


def main():
    root=Path(__file__).resolve().parents[4]
    raw,pred=read_lines(root,"native","ym","results",
           "s3_interacting_transfer_3x3_3x4_20261107","PREDICTION.hbp")
    check(sum(int(s.startswith("PREDICT|id=")) for s in pred)==13,
          "prediction_first_thirteen_rows")
    emit("TRANSFER_BEGIN",gauge_group="S3",
         lattices="3x3,3x4",
         frozen_sha256=sha256(raw).hexdigest(),
         arithmetic="INTEGER_ONLY",new_full_spectrum="NO")
    classes,swaps=all_classes()
    examine_flat(classes,swaps)
    cert_transfer(root)
    emit("TRANSFER_VERIFY",status="PASS",
         composed_global_3x3_first_gap_r27="YES",
         actual_E1_axis_exchange_parity="OPEN",
         actual_E1_winding_overlap="OPEN",
         global_3x4_E1="OPEN",
         electric_JB0_3x3_3x4="SEPARATE_PR129",
         spatial_SU2_continuum="NOT_PROVED",Clay_YM4="OPEN")


if __name__=="__main__":
    main()
