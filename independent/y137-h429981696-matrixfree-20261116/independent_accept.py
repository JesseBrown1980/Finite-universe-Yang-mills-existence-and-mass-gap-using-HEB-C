#!/usr/bin/env python3
"""Independent integer receipt acceptance for the pinned 429M orbit-index pilot.

Arithmetic checks on frozen production receipt, including original physical
census, exact nested rank and all sampled 72-move partition totals. This
is not a blind second source enumeration. Source-based independent replays
and complete 429M electric census remain future acceptance gates.
"""
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "orbit_unrank_pilot.py")
RESULT = os.path.join(HERE, "RESULT-H429M-INDEX-PILOT-20261116.hbp")
SOURCE_BLOB = "a23467d5aad5cad968bea1b854d4388878dc5536"
FULL = 2177317873
TARGET = 429981696


def need(ok, reason):
    if not ok:
        print("Y137_H429M_ACCEPT_REFUSE|reason="+reason+"|json=0", flush=True)
        raise SystemExit(1)


def sha_git(path):
    raw = open(path, "rb").read()
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")
                        + b"\x00" + raw).hexdigest()


def parse(line, tag):
    need(line.startswith(tag+"|"), "wrong_receipt_type")
    parts = {}
    for s in line.split("|")[1:]:
        k, eq, v = s.partition("=")
        need(eq and k not in parts, "duplicate_or_malformed_receipt_field")
        parts[k] = v
    need(parts.get("json") == "0", "wrong_receipt_terminator")
    return parts


def verify():
    text = open(RESULT, encoding="ascii").read()
    raw = text.splitlines()
    need(len(raw) == 5, "unexpected_record_count")
    header = parse(raw[0], "Y137_H429M_PROVENANCE")
    index = parse(raw[1], "Y137_H429M_INDEX")
    space = parse(raw[2], "Y137_H429M_SPACE")
    sample = parse(raw[3], "Y137_H429M_PILOT")
    verdict = parse(raw[4], "Y137_H429M_VERDICT")

    need(sha_git(SOURCE) == SOURCE_BLOB ==
         header.get("script_git_blob"), "original_pilot_code_sha_not_frozen")
    need(header.get("S3_source_git_blob")
         == "91bd1e80cbfcfb76198966aa177d097ecfbe8143"
         and header.get("H20736_source_git_blob")
         == "d0d9d3d14d804450a31ed8e98c01a031b9a53596",
         "source_provenance_changed")
    need(int(index["total_canonical_orbits"]) == FULL ==
         (6**13 + 3*2**13 + 2*3**13)//6
         and index["Burnside"] == "EXACT_MATCH"
         and int(index["rank_DFA_cached_states"]) == 48
         and int(index["canonical_key_length"]) == 13,
         "wrong_exact_Burnside_or_finite_state_index")
    need(int(space["existing_independent_basis"]) == 20736
         and int(space["old_support_unique_orbits"]) == 28634
         and int(space["extra_orthogonal_orbit_indicators"]) == TARGET - 20736
         and int(space["exact_basis_dimension"]) == TARGET
         and space["full_Gram_rank"] ==
         "STRICT_OLD_PLUS_DISJOINT_POSITIVE_ORBITS",
         "nested_basis_rank_source_changed")
    need(int(space["last_selected_global_orbit_rank"]) == 429974655,
         "wrong_last_lex_source_rank")
    need(len(space["original_support_rank_sha256"]) == 64,
         "missing_source_support_sha")
    # Lex prefix contains 13,696 previously reserved support-orbit IDs.
    need(int(space["last_selected_global_orbit_rank"])
         - (TARGET - 20736 - 1) == 13696,
         "lex_cut_and_reserved_orbit_count_inconsistent")

    rows = int(sample["exact_sampled_new_rows"])
    moves = int(sample["total_sample_72_moves"])
    a = int(sample["sampled_new_to_new_weighted_raw_moves"])
    b = int(sample["sampled_new_to_old_support_raw_moves"])
    c = int(sample["sampled_outside_trial_basis_raw_moves"])
    selfloops = int(sample["selfloops"])
    need(rows == 517 and moves == 72*rows
         and moves == a+b+c+selfloops
         and a == 31568 and b == 43 and c == 5613
         and selfloops == 0, "pilot_72_move_source_partition_wrong")
    weights = dict((int(w), int(n)) for w,n in
                   (x.split(":") for x in sample["weights"].split(",")))
    need(set(weights).issubset({1,2,3,6})
         and sum(weights.values()) == rows
         and int(sample["exact_weighted_reverse_edges_checked"]) == 1032,
         "pilot_weights_or_reverse_edge_census_wrong")
    need(len(sample["original_source_signed_row_digest_sha256"]) == 64
         and sample["all_rows"] == "NOT_COMPUTED"
         and sample["full_429m_Ritz"] == "NOT_COMPUTED"
         and sample["full_429m_residual"] == "NOT_COMPUTED"
         and sample["Wilson_weight"] == "HOLD",
         "pilot_scope_overclaim")
    need(verdict["strict_weighted_Gram_rank"] == "PASS"
         and verdict["real_original_operator_sampled_rows"] == "PASS"
         and verdict["full_429m_sweep"] == "NOT_LAUNCHED"
         and verdict["first_Wilson_excitation"] == "HOLD",
         "invalid_project_acceptance_scope")

    # Pure integer negative controls. Any 1-move mismatch or 1-basis-
    # dimension inflation must be visible to these same acceptance equations.
    need(moves != a+b+c+selfloops+1, "one_move_forge_accepted")
    need(TARGET != 20736+429960960+1, "one_basis_forge_accepted")
    print("Y137_H429M_ACCEPT|receipt_original=PINNED"
          "|Burnside_independent=PASS"
          "|429981696_nested_basis_arithmetic=PASS"
          "|old_support_disjointness_receipt=PINNED"
          "|517_rows_37224_moves_partition=PASS"
          "|1032_reverse_edge_receipts=PINNED"
          "|negative_mutations=2_OF_2_REJECTED"
          "|full_429m_sweep=NOT_LAUNCHED"
          "|Wilson_weight=HOLD|json=0",flush=True)


if __name__ == "__main__":
    verify()
