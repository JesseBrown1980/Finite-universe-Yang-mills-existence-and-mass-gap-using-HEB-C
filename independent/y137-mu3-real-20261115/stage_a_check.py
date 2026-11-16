#!/usr/bin/env python3
"""#137 stage A: the Rust row enumerator against the frozen 128-row audit and the independent Python rule.

Integers only. Two steps, driven by stage_a.sh:

  python3 -I -B stage_a_check.py select SPOOL OUTDIR
      verify the group 0 Q5 spool (length, record count, SHA-256 of #195), take every 3,000th record until 128
      (the #196 audit's selection), write their addresses; write 2,000 generated canonical states; write the
      wide-integer test triples.
  python3 -I -B stage_a_check.py compare OUTDIR
      read the Rust rows and the Rust wide sums; rebuild every row with independent_move_rule.py (GPT-6's
      separately written Python rule) and compare the complete destination-multiplicity maps, orbit weights,
      magnetic numbers and self loops; run the planted tamper controls; compare the wide sums with Python integers.
"""
import hashlib
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "y137-d11-shell5-spill-20261114"))
import independent_move_rule as rule

HEADER = struct.Struct("<Q B H H")
SPOOL_SHA = "3f561c26f3cf5b355ab769ae96e9da8ceaa141186fb5ecb80cc1ec4227e4c589"
SPOOL_COUNT, SPOOL_LENGTH = 435324, 72717336
STEP, SAMPLES, RANDOM_STATES, WIDE_TERMS = 3000, 128, 2000, 1000


def need(ok, why):
    if not ok:
        print("Y137_STAGE_A_REFUSE|reason=" + why + "|json=0", flush=True)
        raise SystemExit(1)


def emit(name, **fields):
    print(name + "|" + "|".join(str(k) + "=" + str(v) for k, v in fields.items()) + "|json=0", flush=True)


def code(key):
    v = 0
    for x in reversed(key):
        v = v * 6 + x
    return v


def decode(v):
    out = []
    for _ in range(13):
        v, r = divmod(v, 6)
        out.append(r)
    return tuple(out)


def lcg(seed):
    return (seed * 6364136223846793005 + 1442695040888963407) % 18446744073709551616


def select(spool, out):
    need(os.path.getsize(spool) == SPOOL_LENGTH, "spool_length")
    h, count, picked = hashlib.sha256(), 0, []
    with open(spool, "rb") as f:
        while True:
            head = f.read(HEADER.size)
            if not head:
                break
            need(len(head) == HEADER.size, "partial_header")
            target, w, n0, n1 = HEADER.unpack(head)
            body = f.read(n0 + n1)
            need(len(body) == n0 + n1, "truncated_record")
            h.update(head)
            h.update(body)
            if count % STEP == 0 and len(picked) < SAMPLES:
                picked.append((target, w))
            count += 1
    need(h.hexdigest() == SPOOL_SHA and count == SPOOL_COUNT, "spool_is_not_the_195_group0_artifact")
    need(len(picked) == SAMPLES, "fewer_than_128_samples")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "audit128.txt"), "w", newline="\n") as f:
        for target, w in picked:
            f.write(str(target) + " " + str(w) + "\n")
    seed, states = 20261115, []
    while len(states) < RANDOM_STATES:
        key = []
        for _ in range(13):
            seed = lcg(seed)
            key.append((seed >> 33) % 6)
        states.append(code(rule.canonical_from_full(rule.expanded_links(tuple(key)))))
    with open(os.path.join(out, "random.txt"), "w", newline="\n") as f:
        for s in states:
            f.write(str(s) + "\n")
    with open(os.path.join(out, "wide.txt"), "w", newline="\n") as f:
        for _ in range(WIDE_TERMS):
            seed = lcg(seed); a = seed
            seed = lcg(seed); a = (a * 281474976710656 + (seed >> 16)) % 5192296858534827628530496329220096      # below 2^112
            seed = lcg(seed); b = seed
            seed = lcg(seed); b = (b * 281474976710656 + (seed >> 16)) % 5192296858534827628530496329220096
            seed = lcg(seed); w = seed % 1099511627776                                                           # below 2^40
            f.write(str(a) + " " + str(b) + " " + str(w) + "\n")
    emit("Y137_STAGE_A_SELECT", spool_sha256=SPOOL_SHA, spool_records=count, audit_rows=SAMPLES, step=STEP,
         first_address=picked[0][0], last_address=picked[-1][0], random_states=RANDOM_STATES, wide_terms=WIDE_TERMS)


def parse_rows(path):
    rows = []
    for line in open(path, encoding="ascii"):
        if not line.startswith("ROW|"):
            continue
        d = dict(p.split("=", 1) for p in line.strip().split("|")[1:-1])
        dest = {}
        for item in d["dest"].split(","):
            c, n = item.split(":")
            need(int(c) not in dest, "duplicate_destination_in_rust_row")
            dest[int(c)] = int(n)
        rows.append((int(d["code"]), int(d["canonical"]), int(d["w"]), int(d["m"]), int(d["moves"]), int(d["self"]), dest))
    return rows


def python_row(c):
    key = decode(c)
    counts = rule.neighbor_counts(key)
    return {code(k): n for k, n in counts.items()}, rule.canonical_weight(key), rule.magnetic_of_key(key)


def agree(rust, c):
    ref, w, m = python_row(c)
    return (rust[0] == c and rust[1] == 1 and rust[2] == w and rust[3] == m and rust[4] == 72
            and rust[5] == ref.get(c, 0) and rust[6] == ref)


def compare(out):
    spool_w = [tuple(int(x) for x in line.split()) for line in open(os.path.join(out, "audit128.txt"))]
    audit = parse_rows(os.path.join(out, "audit128.rows"))
    need(len(audit) == SAMPLES and [r[0] for r in audit] == [t for t, _ in spool_w], "audit_rows_out_of_order")
    ok_audit = sum(int(agree(r, r[0])) for r in audit)
    w_ok = sum(int(r[2] == w) for r, (_, w) in zip(audit, spool_w))
    self_loops = sum(r[5] for r in audit)
    moves = sum(r[4] for r in audit)
    emit("Y137_STAGE_A_AUDIT128", rows=len(audit), rows_equal_to_the_python_rule=ok_audit,
         orbit_weight_equal_to_the_spool=w_ok, raw_moves=moves, genuine_self_loop_moves=self_loops,
         frozen_196_audit="128_rows_9216_moves_0_self_loops")
    need(ok_audit == SAMPLES and w_ok == SAMPLES and moves == 9216 and self_loops == 0, "audit128_mismatch")

    rnd = parse_rows(os.path.join(out, "random.rows"))
    need(len(rnd) == RANDOM_STATES, "random_row_count")
    ok_rnd = sum(int(agree(r, r[0])) for r in rnd)
    emit("Y137_STAGE_A_RANDOM", rows=len(rnd), rows_equal_to_the_python_rule=ok_rnd,
         raw_moves=sum(r[4] for r in rnd), genuine_self_loop_moves=sum(r[5] for r in rnd),
         rows_with_a_self_loop=sum(int(r[5] > 0) for r in rnd))
    need(ok_rnd == RANDOM_STATES, "random_rows_mismatch")

    # planted faults: each altered Rust row must be refused by the comparison
    base = audit[0]
    other = next(k for k in base[6] if k != base[0])
    fold = dict(base[6]); fold[other] -= 1; fold[base[0]] = fold.get(base[0], 0) + 1
    fold = {k: v for k, v in fold.items() if v}
    drop = dict(base[6]); drop[other] -= 1
    drop = {k: v for k, v in drop.items() if v}
    moved = dict(base[6]); n = moved.pop(other); moved[other + 6] = moved.get(other + 6, 0) + n
    t_fold = agree(base[:5] + (base[5] + 1, fold), base[0])
    t_drop = agree(base[:4] + (71, base[5], drop), base[0])
    t_moved = agree(base[:6] + (moved,), base[0])
    t_weight = agree(base[:2] + (base[2] % 6 + 1,) + base[3:], base[0])
    emit("Y137_STAGE_A_TAMPER", move_folded_into_a_self_loop_with_72_kept="REFUSED" if not t_fold else "ACCEPTED",
         one_move_omitted="REFUSED" if not t_drop else "ACCEPTED",
         destination_changed="REFUSED" if not t_moved else "ACCEPTED",
         orbit_weight_changed="REFUSED" if not t_weight else "ACCEPTED")
    need(not (t_fold or t_drop or t_moved or t_weight), "a_planted_fault_was_accepted")

    total = 0
    for line in open(os.path.join(out, "wide.txt")):
        a, b, w = (int(x) for x in line.split())
        total += a * b * w
    wide = dict(p.split("=", 1) for p in open(os.path.join(out, "wide.out")).read().strip().split("|")[1:-1])
    w_ok = int(wide["terms"]) == WIDE_TERMS and int(wide["sum"]) == total and int(wide["negated"]) == -total
    emit("Y137_STAGE_A_WIDE", terms=wide["terms"], sum_bits=total.bit_length(), accumulator_bits=320,
         sum_equal_to_python_integers=int(int(wide["sum"]) == total),
         negated_sum_equal=int(int(wide["negated"]) == -total))
    need(w_ok, "wide_integer_mismatch")
    emit("Y137_STAGE_A_VERDICT", audit128="PASS", random_states="PASS", tamper_controls="PASS", wide_integers="PASS",
         real_mu3="NOT_COMPUTED", Wilson_weight="HOLD")


def main():
    if len(sys.argv) == 4 and sys.argv[1] == "select":
        select(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3 and sys.argv[1] == "compare":
        compare(sys.argv[2])
    else:
        need(False, "usage")


if __name__ == "__main__":
    main()
