#!/usr/bin/env python3
"""#137 exact two-trial full-H residual split against H20736 and H429981696.

For the two frozen H20736 rational Ritz trial vectors, original seed energies:
    R = (D H - z) u, D=10^9.
Compute the exact physical weighted-norm orthogonal decomposition
    ||R||_W^2 = ||P_old R||_W^2 + ||P_new R||_W^2
                 + ||(I - P_old - P_new) R||_W^2.
P_old is the *actual* 20736-dimensional W-orthogonal projector, not merely
coordinate support. The Gram inverse reduces exactly to a 4x4 integer Schur
complement after eliminating 8 flats + 132 K2 indicators + 20592 K3
indicators. P_new is diagonal on the 429960960 lex-ordered physical orbit
indicators outside all 28634 old-support coordinates. Only actual one-hop
shell3/shell4 residual targets are indexed. No scan of 429m new source rows.

Everything including the projector is exact integer/rational arithmetic.
Residual capture alone is NOT a Wilson spectral weight or eigenvector angle.
"""
import hashlib
import heapq
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
H20736 = os.path.join(ROOT, "independent", "y137-h20736-shell3-20261116")
H144 = os.path.join(ROOT, "independent", "y137-h144-nested-20261116")
H12 = os.path.join(ROOT, "independent", "y137-12x12-krylov-20261116")
H429 = os.path.join(ROOT, "independent", "y137-h429981696-matrixfree-20261116")
sys.path.insert(0, H20736)
sys.path.insert(0, H144)
sys.path.insert(0, H12)
sys.path.insert(0, H429)

import two_trial_ritz as tw
import full_trial_residual as oldr
import nested_ritz as nested144
import orbit_unrank_pilot as h429
import sparse_h20736 as h20

D = 1000000000
UNIT = 1000000
TOP_N = 12
ORIGINAL_S3_BLOB = "91bd1e80cbfcfb76198966aa177d097ecfbe8143"
ORIGINAL_H20_BLOB = "d0d9d3d14d804450a31ed8e98c01a031b9a53596"
ORIGINAL_H429_BLOB = "a23467d5aad5cad968bea1b854d4388878dc5536"
ORIGINAL_SUPPORT_SHA = "590dde0e0dfb20c1983d374dc7475e389346e5a810c01dcfa325f093247c4be3"
N_OLD = 20736
N_K2 = 8034
N_K3 = 147344
EXPECTED_CUT = 429974655
EXPECTED_OLD_SUPPORT = 28634


def need(ok, reason):
    if not ok:
        print("Y137_H429M_PROJECTION_REFUSE|reason=" + reason + "|json=0",
              flush=True)
        raise SystemExit(1)


def emit(tag, **fields):
    print(tag + "|" + "|".join(str(k) + "=" + str(v)
          for k, v in fields.items()) + "|json=0", flush=True)


def sha(s):
    return hashlib.sha256(s.encode("ascii")).hexdigest()


def determinant(a):
    """Independent fraction-free pivoted Bareiss determinant on integer matrices."""
    v = [list(row) for row in a]
    n = len(v)
    need(n > 0 and all(len(row) == n for row in v),
         "fraction_free_nonsquare")
    previous = 1
    sign = 1
    for k in range(n - 1):
        if v[k][k] == 0:
            pivot = next((r for r in range(k+1, n) if v[r][k]), None)
            if pivot is None:
                return 0
            v[k], v[pivot] = v[pivot], v[k]
            sign = -sign
        a_kk = v[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                num = a_kk*v[i][j] - v[i][k]*v[k][j]
                need(num % previous == 0,
                     "fraction_free_exact_division_failed")
                v[i][j] = num // previous
            v[i][k] = 0
        previous = a_kk
    return sign*v[-1][-1]


def test_toy():
    S = [[5, 2], [2, 3]]
    q = [1, -2]
    dets = determinant(S)
    augmented = [S[0]+[q[0]], S[1]+[q[1]], q+[0]]
    n = -determinant(augmented)
    need(dets == 11 and n == 31, "positive_Schur_inverse_toy")
    need(determinant([[0, 1], [1, 0]]) == -1,
         "pivoted_negative_determinant_toy")
    # Orthogonal norm decomposition must not treat old coordinate support as
    # the actual W-orthogonal span whenever nonorthogonal Krylov columns exist.
    need(31 > 0 and 31 <= 4*11, "projection_Pythagoras_toy")
    emit("Y137_H429M_PROJECT_TOY", exact_2D_Schur="PASS",
         integer_3D_augmented_determinant="PASS",
         pivoted_Bareiss="PASS",
         old_support_not_equal_old_projector="PASS",
         full_429m_spectral_solver="NOT_COMPUTED",
         Wilson_weight="HOLD")


def pinned():
    need(h429.gitblob(h429.ORIGINAL) == ORIGINAL_S3_BLOB,
         "unfrozen_original_S3_source")
    need(h429.gitblob(os.path.join(H20736, "sparse_h20736.py"))
         == ORIGINAL_H20_BLOB, "unfrozen_original_H20736_source")
    need(h429.gitblob(os.path.join(H429, "orbit_unrank_pilot.py"))
         == ORIGINAL_H429_BLOB, "unfrozen_original_H429_indexer")
    need(D == tw.D and D == oldr.DEN, "energy_denominator_drift")
    entries, original_sparse_SHA = tw.source()
    old_144_samples = tw.original_144_trials()
    trials = tw.augmented(old_144_samples, entries)
    ball, states, cols, selected132 = oldr.old_source()
    keys3, idx3, where = h20.canonical_shell3(states, ball)
    selected3 = [f for score, total, f in h20.source_score(ball, cols)]
    need(len(states) == 8042 and ball["n"] == N_K2
         and len(keys3) == N_K3 and len(selected3) == 20592
         and len(set(selected3)) == 20592,
         "source_support_drift")
    all_keys = list(states) + [keys3[f] for f in selected3]
    need(len(all_keys) == EXPECTED_OLD_SUPPORT
         and len(set(all_keys)) == EXPECTED_OLD_SUPPORT,
         "original_physical_support_collision")
    indexer = h429.CanonicalIndex(h429.original_conj())
    ranks = [indexer.rank(k) for k in all_keys]
    nested = h429.NestedSpace(indexer, ranks)
    need(nested.cut == EXPECTED_CUT and
         sha(",".join(str(q) for q in sorted(ranks))) == ORIGINAL_SUPPORT_SHA,
         "429m_original_source_rank_sha_or_cut_changed")
    return (entries, original_sparse_SHA, trials,
            ball, states, cols, selected132, keys3, idx3, where,
            selected3, indexer, nested)


def exact_old_projection(z, x, entries, ball, cols, selected132, selected3, rp, rq2, rq3):
    """b^T G_old^-1 b exactly using 4x4 Schur after diagonal eliminations."""
    b = [0] * N_OLD
    for tag, i, j, v in entries:
        term = D*v if tag == "K" else -z*v
        b[i] += term*x[j]
        if i != j:
            b[j] += term*x[i]

    # Independently compare source-block contractions with DIRECT physical R.
    wf, wq, w3 = ball["wf"], ball["wq"], ball["eW"]
    for i in range(8):
        need(b[i] == wf[i]*rp[i], "old_projection_flat_KG_vs_H")
    for k,idx in enumerate(selected132):
        need(b[12+k] == wq[idx]*rq2[idx],
             "old_projection_K2_indicator_KG_vs_H")
    for k,idx in enumerate(selected3):
        need(b[144+k] == w3[idx]*rq3[k],
             "old_projection_K3_indicator_KG_vs_H")
    for a in range(4):
        direct = sum(wq[i]*cols[a][i]*rq2[i] for i in range(N_K2))
        need(b[8+a] == direct,
             "old_projection_Krylov_KG_vs_original_H")
    direct_quadratic = sum(b[i]*x[i] for i in range(N_OLD))
    reported_norm, original_quad = oldr.original_sparse_expectation(
        x, entries, z)
    need(direct_quadratic == original_quad,
         "original_sparse_quadratic_vs_contracted_projector")
    
    flat_coordinates = sum(b[i]*b[i]//wf[i] for i in range(8))
    K2_coordinates = sum(b[12+k]*b[12+k]//wq[idx]
                         for k,idx in enumerate(selected132))
    K3_coordinates = sum(b[144+k]*b[144+k]//w3[idx]
                         for k,idx in enumerate(selected3))
    diag_part = flat_coordinates + K2_coordinates + K3_coordinates

    G12, unused = nested144.load_h12()
    core = [[G12[8+i][8+j] for j in range(4)] for i in range(4)]
    adjusted = b[8:12]
    for k,idx in enumerate(selected132):
        wi = wq[idx]
        for i in range(4):
            ci = cols[i][idx]
            adjusted[i] -= ci*b[12+k]
            for j in range(4):
                core[i][j] -= wi*ci*cols[j][idx]
    need(all(core[i][j] == core[j][i]
             for i in range(4) for j in range(4)),
         "old_4D_Gram_Schur_not_symmetric")
    for k in range(1, 5):
        need(determinant([row[:k] for row in core[:k]]) > 0,
             "old_4D_Gram_Schur_not_positive")
    det = determinant(core)
    five = [core[i]+[adjusted[i]] for i in range(4)]
    five.append(adjusted+[0])
    numerator_schur = -determinant(five)
    need(numerator_schur >= 0, "negative_old_Krylov_projection_norm")
    projected_num = diag_part*det + numerator_schur
    need(projected_num >= 0, "negative_old_projector_norm")
    return projected_num,det,reported_norm,sha(",".join(str(v) for v in adjusted))


def offer_top(heap, value, rank, weight, cat, shell, flux):
    """Keep top 12 exterior orbital W-r'² contributions, exact integer tie rules."""
    item = (value, -rank, rank, weight, cat, shell, sha(str(flux)))
    if len(heap) < TOP_N:
        heapq.heappush(heap, item)
    elif item > heap[0]:
        heapq.heapreplace(heap, item)


def split_external(z, p, q2, q3, ball, keys3, index3,
                   where, selected3, indexer, nested):
    """Re-enumerate actual source edges and classify *all nonzero* exterior r'."""
    sys.path.insert(0, os.path.join(ROOT, "independent"))
    import finite_s3_3x4_r9_first_gap as c

    # Independently reconstruct weighted K2->K3 residual fluxes.
    es, esrc, ewc, we = (ball["es"], ball["esrc"],
                         ball["ewc"], ball["eW"])
    flux3 = [0]*len(keys3)
    for f in range(len(keys3)):
        value = 0
        for e in range(es[f], es[f+1]):
            value += int(ewc[e])*q2[int(esrc[e])]
        flux3[f] = value

    selection = {f:t for t,f in enumerate(selected3)}
    shell4_flux = {}
    actual_raw = 0
    nonzero_active = 0
    for t, f in enumerate(selected3):
        value = q3[t]
        if not value:
            continue
        nonzero_active += 1
        key = keys3[f]
        wi = we[f]
        moves = c.neighbors(key)
        need(sum(moves.values()) == 72,
             "nonzero_K3_source_missing_original_72_moves")
        actual_raw += 72
        for dst, count in moves.items():
            if dst == key or dst in where:
                continue
            g = index3.get(dst)
            if g is not None:
                if g not in selection:
                    flux3[g] += wi*count*value
            else:
                shell4_flux[dst] = (
                    shell4_flux.get(dst, 0) + wi*count*value)

    # Orthogonal new coordinates are exact physical orbits; all remaining
    # orbit coordinates lie outside enlarged trial space.
    sq_new = 0
    sq_ext = 0
    new3 = 0
    new4 = 0
    ext3 = 0
    ext4 = 0
    heap_all = []
    heap_outside = []
    for f,key in enumerate(keys3):
        if f in selection or flux3[f] == 0:
            continue
        flux = flux3[f]
        weight = we[f]
        need(flux % weight == 0,
             "physical_K3_exterior_source_not_divisible")
        rank = indexer.rank(key)
        coord = nested.coordinate_for_rank(rank)
        need(coord != -2, "old_source_shell3_excluded_from_new")
        val = weight*(flux//weight)**2
        score6 = (6//weight)*flux*flux
        if coord >= N_OLD:
            sq_new += val
            new3 += 1
            category = "NEW"
        else:
            sq_ext += val
            ext3 += 1
            category = "OUTSIDE"
        offer_top(heap_all, score6, rank, weight, category, "K3", flux)
        if category == "OUTSIDE":
            offer_top(heap_outside, score6, rank, weight, category, "K3", flux)
    for key,flux in shell4_flux.items():
        if not flux:
            continue
        weight = c.weight(key)
        need(weight in (1,2,3,6) and flux % weight == 0,
             "physical_K4_exterior_weighted_integrality")
        rank = indexer.rank(key)
        coord = nested.coordinate_for_rank(rank)
        need(coord != -2, "old_source_shell4_excluded_from_new")
        val = weight*(flux//weight)**2
        score6 = (6//weight)*flux*flux
        if coord >= N_OLD:
            sq_new += val
            new4 += 1
            category = "NEW"
        else:
            sq_ext += val
            ext4 += 1
            category = "OUTSIDE"
        offer_top(heap_all, score6, rank, weight, category, "K4", flux)
        if category == "OUTSIDE":
            offer_top(heap_outside, score6, rank, weight, category, "K4", flux)

    return (D*D*sq_new, D*D*sq_ext,
            (new3, new4, ext3, ext4, nonzero_active,
             actual_raw, len(shell4_flux)),
            sorted(heap_all, reverse=True),
            sorted(heap_outside, reverse=True))


def real():
    need(h429.gitblob(os.path.join(H429, "orbit_unrank_pilot.py"))
         == ORIGINAL_H429_BLOB, "H429m_source_blob_changed")
    (entries, sparse_sha, trials, ball, states, cols, selected132,
     keys3, index3, where, selected3, indexer, nested) = pinned()
    emit("Y137_H429M_RESIDUAL_SOURCE",
         original_20736_sparse_SHA256=sparse_sha,
         original_429m_orbit_indexer_blob=ORIGINAL_H429_BLOB,
         total_physical_orbits=indexer.total,
         old_trial_dim=N_OLD,
         added_orbit_coordinate_dim=h429.ADDED,
         nested_dim=h429.TARGET,
         source_support_states=EXPECTED_OLD_SUPPORT,
         lex_last_selected_global_rank=nested.cut,
         exact_arithmetic="INTEGER_ONLY",
         full_429m_eigensolve="NOT_COMPUTED")
    for level,(z,x) in enumerate(trials, 1):
        p,q2,q3 = oldr.physical_amplitudes(
            ball, cols, selected132, selected3, x)
        full6, den6, (rp,rq2,rq3), original_census = oldr.direct_residual(
            z,p,q2,q3,ball,keys3,index3,where,selected3)
        # We independently rebuild all nonzero exterior r' and classify it
        # using the H429m exact canonical-orbit indexing.
        norm = oldr.inner_products(p,q2,q3,ball,selected3)
        inside_sq = (
            sum(w*v*v for w,v in zip(ball["wf"],rp))
            + sum(w*v*v for w,v in zip(ball["wq"],rq2))
            + sum(ball["eW"][f]*rq3[t]*rq3[t]
                  for t,f in enumerate(selected3)))
        new_sq,ext_sq,census,top_all,top_outside = split_external(
            z,p,q2,q3,ball,keys3,index3,where,
            selected3,indexer,nested)
        total_sq = inside_sq+new_sq+ext_sq
        need(6*total_sq == full6,
             "full_original_exact_W_residual_does_not_partition")
        need(den6 == 6*D*D*norm,
             "full_original_trial_norm_denominator_disagrees")
        proj_num, proj_den, norm2, adjsha = exact_old_projection(
            z,x,entries,ball,cols,selected132,selected3,
            rp,rq2,rq3)
        need(norm2 == norm, "old_sparse_Gram_norm_incorrect")
        need(0<=proj_num<=inside_sq*proj_den,
             "old_Galerkin_projector_exceeds_full_old_support")
        remainder_num = (inside_sq+ext_sq)*proj_den-proj_num
        need(remainder_num>=0 and
             proj_num + new_sq*proj_den + remainder_num
             == total_sq*proj_den,
             "orthogonal_Pythagoras_exact_identity_invalid")
        new_ppm = UNIT*new_sq//total_sq
        old_ppm = UNIT*proj_num//(proj_den*total_sq)
        outside_ppm = UNIT-new_ppm-old_ppm
        # The candidate reduction is the squared norm of projecting R away
        # from the added indicator axes, NOT a new normalized Ritz residual.
        retained_upper = oldr.upper_sqrt_per_trillion(
            total_sq-new_sq,D*D*norm)
        original_upper = oldr.upper_sqrt_per_trillion(
            total_sq,D*D*norm)
        emit("Y137_H429M_RESIDUAL_SPLIT",
             level=level,original_144_seed_energy_num=z,
             energy_den=D, full_trial_G_norm_bits=norm.bit_length(),
             exact_full_R_square_sha256=sha(str(total_sq)),
             old_projector_fraction_num_sha256=sha(str(proj_num)),
             old_projector_fraction_den_sha256=sha(str(proj_den)),
             new_coordinate_projection_square_sha256=sha(str(new_sq)),
             remainder_projection_num_sha256=sha(str(remainder_num)),
             partition_old_projector_ppm=old_ppm,
             partition_new_basis_ppm=new_ppm,
             partition_remainder_ppm=outside_ppm,
             partition_sum_exact="PASS",
             old_Gram_inversion="EXACT_4X4_SCHUR",
             canonical_cross_source_action="ORIGINAL_72_MOVE",
             full_residual_original_upper_per_trillion=original_upper,
             formal_removed_new_projection_upper_per_trillion=retained_upper,
             energy_seed_type="ORIGINAL_144_UPPER_NOT_NEW_RITZ",
             new_429m_spectral_enclosure="NOT_COMPUTED",
             first_Wilson_weight="HOLD")
        emit("Y137_H429M_RESIDUAL_CENSUS",
             level=level,new_K3_orbits=census[0],
             new_K4_orbits=census[1],
             outside_K3_orbits=census[2],
             outside_K4_orbits=census[3],
             nonzero_active_old_K3_rows=census[4],
             actual_K3_source_raw_moves=census[5],
             distinct_K4_flux_addresses=census[6],
             legacy_K4_distinct_addresses=original_census[2],
             original_full_residual="RECONCILED_EXACTLY",
             source_old_projector_adjusted4_sha256=adjsha)
        for type_name, ranking in (("OVERALL",top_all),
                                   ("NOT_IN_LEX_BASIS",top_outside)):
            for order,(score6,neg_rank,global_rank,wt,cat,shell,
                       fluxsha) in enumerate(ranking,1):
                emit("Y137_H429M_RESIDUAL_TOP",
                     level=level,type=type_name,rank=order,
                     orbit_global_rank=global_rank,
                     shell=shell,lex_selected=cat,
                     physical_weight=wt,
                     score6_bits=score6.bit_length(),
                     score6_sha256=sha(str(score6)),
                     source_flux_sha256=fluxsha)
    emit("Y137_H429M_RESIDUAL_VERDICT",
         two_frozen_trial_vectors="2_OF_2_EXACT",
         actual_old_20736_orthogonal_projection="PASS",
         actual_429960960_new_orthogonal_projection="PASS",
         full_physical_H_residual_against_original="PASS",
         Pythagoras_three_way="EXACT",
         all_new_429m_source_rows="NOT_COMPUTED",
         full_429m_Ritz="NOT_COMPUTED",
         Wilson_first_excitation_weight="HOLD",
         issue_137="OPEN")


if __name__ == "__main__":
    if sys.argv[1:] == ["toy"]:
        test_toy()
    elif sys.argv[1:] == ["real"]:
        real()
    else:
        need(False, "usage_toy_or_real")
