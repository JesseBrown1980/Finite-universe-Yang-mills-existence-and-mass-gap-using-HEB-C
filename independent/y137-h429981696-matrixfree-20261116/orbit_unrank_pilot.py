#!/usr/bin/env python3
"""Exact S3^13 / simultaneous conjugation index, 429981696-dimensional basis pilot.

The full 3x4 S3 gauge-orbit set has 2177317873 canonical keys. A finite-state
prefix DP over the SIX fixed conjugation maps counts lex-minimal tuples and
supports arbitrary exact rank/unrank without enumerating 6^13 raw tuples.

Keep the accepted original 20736-dimensional Galerkin basis. Exclude EVERY
canonical orbit in its support (8042 K2 orbit keys plus 20592 selected K3
orbit keys). Append the FIRST 429960960 lex-ranked physical orbit indicators
outside that support. Their W-Gram is diagonal and W-orthogonal to the old
basis, so the entire 429981696-dimensional basis is strictly independent.

The hosted pilot authenticates the original 20736 source, complete excluded
support, selected rank cut, and exact 72-move row evaluations of a deterministic
finite sample across the NEW 429m-dimensional basis. It performs independent
weighted-reverse controls on selected actual edges and computes all sampled
couplings to the original 20736 directions. The FULL 429m-source transition
scan, matrix-free bidirectional matvec, Ritz and Wilson checks are NOT RUN.
"""
import bisect
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ORIGINAL = os.path.join(ROOT, "independent", "finite_s3_3x4_r9_first_gap.py")
PARENT = os.path.join(ROOT, "independent", "y137-h20736-shell3-20261116")
ORIGINAL_BLOB = "91bd1e80cbfcfb76198966aa177d097ecfbe8143"
PARENT_BLOB = "d0d9d3d14d804450a31ed8e98c01a031b9a53596"
FULL = 2177317873
OLD = 20736
TARGET = 429981696
ADDED = TARGET - OLD
SUPPORT = 8042 + 20592
LEN = 13
MASK_FULL = (1 << 6) - 1
ROWS = 512
REVERSE_ROWS = 16


def need(ok, reason):
    if not ok:
        print("Y137_H429M_REFUSE|reason=" + reason + "|json=0", flush=True)
        raise SystemExit(1)


def emit(tag, **parts):
    print(tag + "|" + "|".join(str(k) + "=" + str(v)
          for k, v in parts.items()) + "|json=0", flush=True)


def gitblob(path):
    raw = open(path, "rb").read()
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii")
                        + b"\x00" + raw).hexdigest()


def sha(s):
    return hashlib.sha256(s.encode("ascii")).hexdigest()


def original_conj():
    """Historical tracked S3 group action, not a newly guessed presentation."""
    sys.path.insert(0, os.path.dirname(ORIGINAL))
    old_args = sys.argv[:]
    sys.argv = sys.argv[:1]
    try:
        import finite_s3_3x4_r9_first_gap as c
    finally:
        sys.argv = old_args
    return tuple(tuple(x) for x in c.CONJ)


class CanonicalIndex:
    """Lexicographic minimal representatives under diagonal S3 conjugation.

    A 6-bit mask records group actions already shown strictly larger than the
    candidate prefix. Any as-yet-equal conjugate becoming smaller invalidates
    that prefix. At length 13, all valid prefixes are canonical representatives.
    """
    def __init__(self, conj):
        need(len(conj) == 6 and all(len(v) == 6 for v in conj),
             "non_original_S3_conjugation")
        self.conj = conj
        self.memo = {}
        self.transitions = {}
        for mask in range(64):
            for d in range(6):
                new = mask
                valid = True
                for g in range(6):
                    if mask & (1 << g):
                        continue
                    compared = conj[g][d]
                    if d > compared:
                        valid = False
                        break
                    if d < compared:
                        new |= 1 << g
                self.transitions[(mask, d)] = new if valid else -1
        self.total = self.suffix(0, 0)

    def suffix(self, depth, mask):
        if depth == LEN:
            return 1
        idx = (depth, mask)
        v = self.memo.get(idx)
        if v is not None:
            return v
        v = 0
        for digit in range(6):
            nextmask = self.transitions[(mask, digit)]
            if nextmask >= 0:
                v += self.suffix(depth + 1, nextmask)
        self.memo[idx] = v
        return v

    def rank(self, key):
        need(len(key) == LEN, "wrong_original_physical_key_length")
        value = 0
        mask = 0
        for depth, digit in enumerate(key):
            need(0 <= digit <= 5, "non_S3_link_value")
            for d in range(digit):
                nxt = self.transitions[(mask, d)]
                if nxt >= 0:
                    value += self.suffix(depth + 1, nxt)
            mask = self.transitions[(mask, digit)]
            need(mask >= 0, "orbit_key_not_canonical_lex_minimal")
        need(0 <= value < self.total, "rank_outside_physical_space")
        return value

    def unrank(self, index):
        need(0 <= index < self.total, "unrank_outside_full_physical_space")
        out = []
        mask = 0
        for depth in range(LEN):
            found = False
            for digit in range(6):
                nxt = self.transitions[(mask, digit)]
                if nxt < 0:
                    continue
                n = self.suffix(depth + 1, nxt)
                if index >= n:
                    index -= n
                else:
                    out.append(digit)
                    mask = nxt
                    found = True
                    break
            need(found, "exact_unrank_finite_automaton_failure")
        need(index == 0, "unrank_nonzero_remainder")
        return tuple(out)


class NestedSpace:
    """Original 20,736 weighted basis plus disjoint lex-selected orbit axes."""
    def __init__(self, indexer, old_orbit_ranks):
        self.indexer = indexer
        self.old = tuple(sorted(old_orbit_ranks))
        need(len(self.old) == SUPPORT
             and len(set(self.old)) == SUPPORT,
             "original_20k_physical_support_not_unique")
        need(indexer.total - SUPPORT >= ADDED,
             "not_enough_outside_original_basis_support")
        self.cut = self.ordinal_to_rank(ADDED - 1)

    def ordinal_to_rank(self, ordinal):
        need(0 <= ordinal < ADDED, "new_basis_ordinal_outside")
        lo = ordinal
        hi = ordinal + len(self.old)
        while lo < hi:
            mid = (lo + hi) // 2
            # Number of original canonical orbits not among OLD support through mid.
            allowed = mid + 1 - bisect.bisect_right(self.old, mid)
            if allowed >= ordinal + 1:
                hi = mid
            else:
                lo = mid + 1
        need(lo < self.indexer.total
             and self.coordinate_for_rank(lo) == OLD + ordinal,
             "new_basis_ordinal_rank_inverse_disagreement")
        return lo

    def coordinate_for_rank(self, global_rank):
        need(0 <= global_rank < self.indexer.total,
             "nonphysical_neighbor_orbit_rank")
        at = bisect.bisect_left(self.old, global_rank)
        if at < len(self.old) and self.old[at] == global_rank:
            return -2  # Old trial physical support (not a coordinate axis).
        ordinal = global_rank - at
        return OLD + ordinal if ordinal < ADDED else -1

    def row_key(self, ordinal):
        return self.indexer.unrank(self.ordinal_to_rank(ordinal))


def rebuild_old_basis():
    """Reconstruct original source via pinned H20736, no files invented."""
    need(gitblob(ORIGINAL) == ORIGINAL_BLOB,
         "historical_S3_generator_source_sha")
    need(gitblob(os.path.join(PARENT, "sparse_h20736.py")) == PARENT_BLOB,
         "source_H20736_sha_changed")
    sys.path.insert(0, PARENT)
    import sparse_h20736 as h
    G, K, ball, states, cols, selected132, frozen = h.original144()
    keys3, index3, where = h.canonical_shell3(states, ball)
    scores = h.source_score(ball, cols)
    chosen = [f for strong, total, f in scores]
    need(len(states) == 8042
         and len(keys3) == 147344
         and len(chosen) == 20592
         and len(set(chosen)) == 20592,
         "original_20736_K2_K3_census")
    support = list(states) + [keys3[f] for f in chosen]
    need(len(support) == SUPPORT and len(set(support)) == SUPPORT,
         "original_source_orbit_key_duplicate")
    return support, states, cols, selected132, keys3, index3, chosen


def old_row_cross(canonical_key, weight, moves, states, cols,
                  selected132, index3, chosen):
    """All new-to-original 20,736 cross-entries from physical source vectors.

    Original eight flat orbit indicators; four old Q-Krylov columns on K2;
    132 old K2 coordinate orbit indicators; 20,592 old K3 coordinates.
    """
    index2 = {key: i for i, key in enumerate(states)}
    map132 = {f: 12+t for t, f in enumerate(selected132)}
    map3 = {f: 144+t for t, f in enumerate(chosen)}
    cross = {}
    for dst, multiplicity in moves.items():
        original_i = index2.get(dst)
        if original_i is not None:
            if original_i < 8:
                column = original_i
                cross[column] = cross.get(column, 0) - weight * multiplicity
            else:
                q = original_i - 8
                for a in range(4):
                    v = cols[a][q]
                    if v:
                        col = 8 + a
                        cross[col] = cross.get(col, 0) - weight * multiplicity * v
                col = map132.get(q)
                if col is not None:
                    cross[col] = cross.get(col, 0) - weight * multiplicity
            continue
        shell3_idx = index3.get(dst)
        if shell3_idx is not None:
            col = map3.get(shell3_idx)
            if col is not None:
                cross[col] = cross.get(col, 0) - weight * multiplicity
    return sorted((col, v) for col, v in cross.items() if v)


def pilot():
    ind = CanonicalIndex(original_conj())
    import finite_s3_3x4_r9_first_gap as c
    need(ind.total == FULL
         and FULL == (6**13 + 3 * 2**13 + 2 * 3**13) // 6,
         "original_Burnside_orbit_census_disagreement")
    emit("Y137_H429M_INDEX", total_canonical_orbits=ind.total,
         rank_DFA_cached_states=len(ind.memo),
         original_conjugacy_actions=6,
         canonical_key_length=LEN, Burnside="EXACT_MATCH",
         arithmetic="INTEGER_ONLY",
         physical_lattice="3x4_S3", proposed_dimension=TARGET)
    support, states, cols, selected132, keys3, index3, chosen = rebuild_old_basis()
    global_ranks = []
    for key in support:
        r = ind.rank(key)
        global_ranks.append(r)
    original_support_sha = sha(",".join(str(r) for r in sorted(global_ranks)))
    nested = NestedSpace(ind, global_ranks)
    need(nested.ordinal_to_rank(0) >= 0
         and nested.ordinal_to_rank(ADDED - 1) < FULL,
         "429m_subset_cut_invalid")
    emit("Y137_H429M_SPACE", existing_independent_basis=OLD,
         old_support_unique_orbits=SUPPORT,
         extra_orthogonal_orbit_indicators=ADDED,
         exact_basis_dimension=TARGET,
         full_orbit_count=FULL,
         original_support_rank_sha256=original_support_sha,
         last_selected_global_orbit_rank=nested.cut,
         full_Gram_rank="STRICT_OLD_PLUS_DISJOINT_POSITIVE_ORBITS",
         previous_H20736_nested="PASS",
         full_matrix_free_operator="PARTIAL_NEW_ROW_API")

    # Spread the exact pilot across the new 429m dimension: first/last plus
    # uniformly spaced deterministic source representatives.
    selected = sorted(set(
        [0,1,2,3,ADDED-1,ADDED-2,ADDED-3]
        + [(ADDED-1)*t//(ROWS-1) for t in range(ROWS)]
    ))
    digest = hashlib.sha256()
    total_moves=0
    within_new=0
    to_old=0
    outside=0
    source_selfloops=0
    reverse_checked=0
    k4_and_beyond=0
    sample_orbit_weights={}
    for i, ordinal in enumerate(selected):
        global_rank = nested.ordinal_to_rank(ordinal)
        key = ind.unrank(global_rank)
        need(ind.rank(key) == global_rank
             and c.canonical(c.from_key(key)) == key,
             "original_S3_canonicalization_vs_DFA_mismatch")
        weight = c.weight(key)
        need(weight in (1,2,3,6), "orbit_weight_not_original")
        sample_orbit_weights[weight]=sample_orbit_weights.get(weight,0)+1
        moves = c.neighbors(key)
        need(sum(moves.values()) == 72, "original_physical_72_move_census")
        magnetic = c.magnetic(c.from_key(key))
        selfloops=moves.get(key,0)
        diag = weight*(72+9*magnetic-selfloops)
        need(diag>0, "incorrect_shell_magnetic_diagonal")
        source_selfloops += selfloops
        oldcross = old_row_cross(key, weight, moves,
                                 states, cols, selected132,index3,chosen)
        entries = [("D", OLD+ordinal, diag)]
        for column, value in oldcross:
            need(0<=column<OLD, "original_source_cross_out_of_range")
            entries.append(("P", column, value))
        for neighbor, multiplicity in sorted(moves.items()):
            if neighbor==key:
                continue
            near_rank=ind.rank(neighbor)
            kind=nested.coordinate_for_rank(near_rank)
            if kind==-2:
                to_old+=multiplicity
            elif kind==-1:
                outside+=multiplicity
                k4_and_beyond+=1
            else:
                within_new+=multiplicity
                entries.append(("E",kind,-weight*multiplicity))
                if i<REVERSE_ROWS:
                    reverse=c.neighbors(neighbor)
                    need(weight*multiplicity
                         == c.weight(neighbor)*reverse.get(key,0),
                         "sample_weighted_reciprocity_failure")
                    reverse_checked+=1
        encoded=";".join(tag+":"+str(col)+":"+str(value)
                         for tag,col,value in sorted(entries))
        digest.update((str(ordinal)+"|"+str(global_rank)+"|"+
                       str(weight)+"|"+str(magnetic)+"|"+
                       encoded+"\n").encode("ascii"))
        total_moves += 72
    need(total_moves==72*len(selected), "sample_total_raw_move_mismatch")
    emit("Y137_H429M_PILOT", exact_sampled_new_rows=len(selected),
         total_sample_72_moves=total_moves,
         weights=",".join(str(k)+":"+str(v)
                          for k,v in sorted(sample_orbit_weights.items())),
         sampled_new_to_new_weighted_raw_moves=within_new,
         sampled_new_to_old_support_raw_moves=to_old,
         sampled_outside_trial_basis_raw_moves=outside,
         selfloops=source_selfloops,
         exact_weighted_reverse_edges_checked=reverse_checked,
         original_source_signed_row_digest_sha256=digest.hexdigest(),
         all_rows="NOT_COMPUTED", full_429m_Ritz="NOT_COMPUTED",
         full_429m_residual="NOT_COMPUTED",
         Wilson_weight="HOLD", issue_137="OPEN")
    emit("Y137_H429M_VERDICT", physical_space="S3_3X4",
         exact_total_orbit_unrank="PASS",
         new_basis_dimension=TARGET,
         strict_weighted_Gram_rank="PASS",
         real_original_operator_sampled_rows="PASS",
         new_to_old_cross_exact="PASS",
         full_429m_sweep="NOT_LAUNCHED",
         429b_dimension="EXCEEDS_FINITE_PHYSICAL_SPACE",
         first_Wilson_excitation="HOLD")


def toy():
    ind = CanonicalIndex(original_conj())
    need(ind.total == FULL, "toy_Burnside_vs_DFA")
    critical = (0,1,2,10,429981695,FULL-1,FULL//2)
    for r in critical:
        k = ind.unrank(r)
        need(ind.rank(k) == r
             and k == min(tuple(ind.conj[g][d] for d in k)
                          for g in range(6)), "rank_unrank_toy_invertibility")
    need(ind.rank(tuple([0]*13)) == 0,
         "toy_first_identity_key")
    need(ind.total < 429981696000,
         "literal_429_billion_exceeds_physical_Hilbert_dimension")
    emit("Y137_H429M_TOY", all_orbits=ind.total,
         required_dimension=TARGET,
         rank_unrank_boundaries=len(critical),
         exact_Burnside="PASS",
         lex_minimal_canonical="PASS",
         literal_429_billion="IMPOSSIBLE_AS_INDEPENDENT_FINITE_BASIS",
         sampled_rows="NOT_COMPUTED", Wilson_weight="HOLD")


if __name__ == "__main__":
    if sys.argv[1:]==["toy"]:
        toy()
    elif sys.argv[1:]==["pilot"]:
        pilot()
    else:
        need(False, "usage_toy_or_pilot")
