#!/usr/bin/env python3
"""#137 Worker-1: streaming authentication of all eight immutable Q5 V1/b spools.

No Q5 operator/moment computation is claimed.  One complete read per group,
bounded memory, strict byte layout, globally disjoint radix-64 source buckets.
Usage:
  source_gate.py selftest
  source_gate.py verify MANIFEST GROUP GROUP.v1 RECEIPT.hbp
  source_gate.py aggregate MANIFEST RECEIPT_DIR FINAL.hbp
"""
import hashlib
import os
import struct
import sys
import tempfile

HEADER = struct.Struct("<Q B H H")
GROUPS = 8
BUCKETS = 64
WIDTH = 82
CHANNELS = 8
MAX_PACKED_BYTES = WIDTH * CHANNELS // 8
MAX_ADDRESS = 6 ** 13
# Independently rederive all six global-conjugation actions and orbit weights
# from the public S3 permutation definition (Stage A Rust convention).
PERMS = ((0, 1, 2), (0, 2, 1), (1, 0, 2),
         (1, 2, 0), (2, 0, 1), (2, 1, 0))
MUL = tuple(tuple(PERMS.index(tuple(a[b[i]] for i in range(3)))
                  for b in PERMS) for a in PERMS)
INV = tuple(PERMS.index(tuple(a.index(i) for i in range(3)))
            for a in PERMS)
CONJ = tuple(tuple(MUL[MUL[a][u]][INV[a]] for u in range(6))
             for a in range(6))
EXPECTED_TARGETS = 18598040
EXPECTED_BYTES = 3140900108
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
WORKFLOW = os.path.join(ROOT, ".github", "workflows",
                        "y137-stage-b-source-gate.yml")


class Refuse(Exception):
    pass


def need(condition, why):
    if not condition:
        raise Refuse(why)


def fields(line, prefix):
    need(line.startswith(prefix + "|"), "missing_" + prefix)
    ans = {}
    for token in line.rstrip("\r\n").split("|")[1:]:
        k, sep, value = token.partition("=")
        need(sep and k not in ans, "invalid_receipt_field")
        ans[k] = value
    need(ans.get("json") == "0", "receipt_json_marker")
    return ans


def manifest(path, expected_targets=EXPECTED_TARGETS, expected_bytes=EXPECTED_BYTES):
    rows = {}
    verdict = None
    with open(path, "rb") as f:
        raw = f.read()
    for line in raw.decode("ascii").splitlines():
        if line.startswith("Y137_D11_V1_ALL_GROUP|"):
            r = fields(line, "Y137_D11_V1_ALL_GROUP")
            g = int(r["group"])
            need(0 <= g < GROUPS and g not in rows, "duplicate_or_invalid_manifest_group")
            need(len(r["sha256"]) == 64, "invalid_manifest_sha")
            rows[g] = r
        elif line.startswith("Y137_D11_V1_ALL_VERDICT|"):
            need(verdict is None, "duplicate_manifest_verdict")
            verdict = fields(line, "Y137_D11_V1_ALL_VERDICT")
    need(set(rows) == set(range(GROUPS)) and verdict is not None,
         "incomplete_original_manifest")
    need(sum(int(r["targets"]) for r in rows.values()) == expected_targets,
         "manifest_target_sum")
    need(sum(int(r["bytes"]) for r in rows.values()) == expected_bytes,
         "manifest_byte_sum")
    need(int(verdict["complete_Q5_support_targets"]) == expected_targets,
         "manifest_verdict_target_count")
    need(int(verdict["spooled_V1_over_b_bytes"]) == expected_bytes,
         "manifest_verdict_byte_count")
    return rows, hashlib.sha256(raw).hexdigest()


def canonical_weight(address):
    digits = []
    for _ in range(13):
        address, digit = divmod(address, 6)
        digits.append(digit)
    need(address == 0, "source_address_out_of_range")
    original = tuple(digits)
    orbit = set()
    for a in range(6):
        conjugate = tuple(CONJ[a][u] for u in original)
        need(conjugate >= original, "noncanonical_source_address")
        orbit.add(conjugate)
    return len(orbit)


def inspect(group, path, row, check_canonical=True):
    size = os.path.getsize(path)
    need(size == int(row["bytes"]), "group_file_length")
    h = hashlib.sha256()
    n = 0
    last_bucket = group - 8
    last_address = -1
    counts = [0] * 8
    max_length = 0
    with open(path, "rb", buffering=1024 * 1024) as f:
        while True:
            head = f.read(HEADER.size)
            if not head:
                break
            need(len(head) == HEADER.size, "short_record_header")
            code, weight, n0, n1 = HEADER.unpack(head)
            need(0 <= code < MAX_ADDRESS, "address_out_of_range")
            need(weight in (1, 2, 3, 6), "invalid_orbit_weight")
            if check_canonical:
                need(weight == canonical_weight(code),
                     "stored_weight_disagrees_with_independent_S3_orbit")
            need(n0 <= MAX_PACKED_BYTES and n1 <= MAX_PACKED_BYTES,
                 "packed_amplitude_length")
            p0 = f.read(n0)
            p1 = f.read(n1)
            need(len(p0) == n0 and len(p1) == n1, "short_record_amplitude")
            need(not p0 or p0[-1] != 0, "nonminimal_first_packed_amplitude")
            need(not p1 or p1[-1] != 0, "nonminimal_second_packed_amplitude")
            need(int.from_bytes(p0, "little").bit_length() <= WIDTH * CHANNELS,
                 "first_packed_amplitude_overflow")
            need(int.from_bytes(p1, "little").bit_length() <= WIDTH * CHANNELS,
                 "second_packed_amplitude_overflow")
            h.update(head)
            h.update(p0)
            h.update(p1)
            bucket = code % BUCKETS
            need(bucket % GROUPS == group, "address_wrong_group")
            if bucket != last_bucket:
                need(bucket == last_bucket + GROUPS, "bucket_missing_or_out_of_order")
                last_bucket = bucket
                last_address = -1
            need(code > last_address, "bucket_address_nonascending_or_duplicate")
            last_address = code
            counts[(bucket - group) // GROUPS] += 1
            n += 1
            max_length = max(max_length, n0, n1)
    need(last_bucket == group + 7 * GROUPS and all(counts),
         "missing_nonempty_bucket")
    need(n == int(row["targets"]), "group_target_count")
    digest = h.hexdigest()
    need(digest == row["sha256"], "group_sha256")
    return ("Y137_STAGE_B_SOURCE_GROUP|group=" + str(group) +
            "|targets=" + str(n) + "|bytes=" + str(size) +
            "|sha256=" + digest +
            "|bucket_counts=" + ",".join(str(c) for c in counts) +
            "|packed_width=" + str(WIDTH) +
            "|max_packed_bytes=" + str(max_length) +
            "|all_eight_buckets_ordered=PASS|address_partition=PASS" +
            "|packed_vectors=PASS|canonical_and_orbit_weights=" +
            ("PASS" if check_canonical else "NOT_TESTED") + "|json=0\n")


def write_receipt(path, content):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write(content)


def code_provenance():
    with open(__file__, "rb") as f:
        exe_sha = hashlib.sha256(f.read()).hexdigest()
    with open(WORKFLOW, "rb") as f:
        workflow_sha = hashlib.sha256(f.read()).hexdigest()
    sha = os.environ.get("GITHUB_SHA", "LOCAL")
    run = os.environ.get("GITHUB_RUN_ID", "LOCAL")
    need(bool(sha) and bool(run), "missing_executable_provenance")
    return exe_sha, workflow_sha, sha, run


def verify(manifest_path, group, spool_path, receipt_path,
           expected_targets=EXPECTED_TARGETS, expected_bytes=EXPECTED_BYTES,
           check_canonical=True):
    rows, manifest_sha = manifest(manifest_path, expected_targets, expected_bytes)
    need(0 <= group < GROUPS, "invalid_group")
    output = inspect(group, spool_path, rows[group], check_canonical)
    output += "Y137_STAGE_B_GROUP_INPUT|manifest_sha256=" + manifest_sha + "|json=0\n"
    exe, workflow, sha, run = code_provenance()
    output += ("Y137_STAGE_B_GROUP_PROVENANCE|code_sha256=" + exe +
               "|workflow_sha256=" + workflow +
               "|github_sha=" + sha + "|github_run_id=" + run + "|json=0\n")
    write_receipt(receipt_path, output)
    return output


def aggregate(manifest_path, receipt_dir, output_path,
              expected_targets=EXPECTED_TARGETS, expected_bytes=EXPECTED_BYTES,
              require_canonical=True):
    rows, manifest_sha = manifest(manifest_path, expected_targets, expected_bytes)
    targets = 0
    bytes_count = 0
    all_buckets = 0
    exe, workflow, sha, run = code_provenance()
    receipts_hash = hashlib.sha256()
    for g in range(GROUPS):
        receipt_path = os.path.join(receipt_dir, "GROUP-" + str(g) + ".hbp")
        with open(receipt_path, "rb") as f:
            raw_receipt = f.read()
        receipts_hash.update(raw_receipt)
        lines = raw_receipt.decode("ascii").splitlines()
        need(len(lines) == 3, "unexpected_group_receipt_rows")
        r = fields(lines[0], "Y137_STAGE_B_SOURCE_GROUP")
        m = fields(lines[1], "Y137_STAGE_B_GROUP_INPUT")
        p = fields(lines[2], "Y137_STAGE_B_GROUP_PROVENANCE")
        need(p["code_sha256"] == exe and
             p["workflow_sha256"] == workflow and
             p["github_sha"] == sha and p["github_run_id"] == run,
             "forged_or_stale_group_provenance")
        need(int(r["group"]) == g and m["manifest_sha256"] == manifest_sha,
             "group_receipt_provenance")
        need(r["sha256"] == rows[g]["sha256"] and
             int(r["targets"]) == int(rows[g]["targets"]) and
             int(r["bytes"]) == int(rows[g]["bytes"]),
             "group_receipt_source_mismatch")
        need(r["all_eight_buckets_ordered"] == "PASS" and
             r["address_partition"] == "PASS" and
             r["packed_vectors"] == "PASS" and
             (not require_canonical or r["canonical_and_orbit_weights"] == "PASS") and
             int(r["packed_width"]) == WIDTH, "group_receipt_failed_control")
        bucket_counts = [int(x) for x in r["bucket_counts"].split(",")]
        need(len(bucket_counts) == 8 and all(x > 0 for x in bucket_counts) and
             sum(bucket_counts) == int(r["targets"]),
             "group_bucket_count_mismatch")
        targets += int(r["targets"])
        bytes_count += int(r["bytes"])
        all_buckets += len(bucket_counts)
    need(targets == expected_targets and bytes_count == expected_bytes and
         all_buckets == BUCKETS, "aggregate_source_count")
    # Each key has exactly one remainder mod 64. Strict ordering within each
    # bucket establishes global uniqueness without storing all 18.6M keys.
    output = ("Y137_STAGE_B_SOURCE_GATE|authenticated_groups=8" +
              "|unique_radix64_buckets=64|distinct_Q5_addresses=" + str(targets) +
              "|total_source_bytes=" + str(bytes_count) +
              "|source_manifest_sha256=" + manifest_sha +
              "|code_sha256=" + exe + "|workflow_sha256=" + workflow +
              "|github_sha=" + sha + "|github_run_id=" + run +
              "|group_receipts_sha256=" + receipts_hash.hexdigest() +
              "|prediction_B1=PASS|prediction_B2=" +
              ("PASS" if require_canonical else "TOY_ONLY") +
              "|canonical_S3_orbit_weights=" +
              ("PASS" if require_canonical else "NOT_TESTED") +
              "|raw_moves=NOT_COMPUTED|mu3=NOT_COMPUTED" +
              "|Wilson_weight=HOLD|json=0\n")
    write_receipt(output_path, output)
    return output


def selftest():
    def record(code, w=1, p0=b"\x01", p1=b"\x02"):
        return HEADER.pack(code, w, len(p0), len(p1)) + p0 + p1

    def sources(folder, faulty_group=None, fault=None):
        source_rows = []
        total = 0
        for g in range(GROUPS):
            pieces = [record(b) for b in range(g, BUCKETS, GROUPS) for _ in (0,)]
            if g == faulty_group:
                if fault == "duplicate":
                    pieces[1] = pieces[0]
                elif fault == "bucket_order":
                    pieces[0], pieces[1] = pieces[1], pieces[0]
                elif fault == "same_bucket_reverse":
                    # Two distinct addresses with the same mod-64 residue,
                    # deliberately in descending order (rehashed manifest).
                    pieces[0] = record(g + 64)
                    pieces[1] = record(g)
                elif fault == "noncanonical_file":
                    need(g == 0, "toy_noncanonical_group_must_be_zero")
                    bad = None
                    for candidate in range(64, 8192, 64):
                        try:
                            canonical_weight(candidate)
                        except Refuse:
                            bad = candidate
                            break
                    need(bad is not None, "toy_noncanonical_address_missing")
                    pieces[0] = record(bad)
                elif fault == "lane":
                    pieces[0] = record(g, p0=b"\x01" * (MAX_PACKED_BYTES + 1))
                elif fault == "group":
                    pieces[0] = record(g + 1)
            data = b"".join(pieces)
            path = os.path.join(folder, "GROUP-" + str(g) + ".v1")
            with open(path, "wb") as f:
                f.write(data)
            total += len(data)
            source_rows.append("Y137_D11_V1_ALL_GROUP|group=" + str(g) +
                               "|targets=8|bytes=" + str(len(data)) +
                               "|sha256=" + hashlib.sha256(data).hexdigest() +
                               "|json=0")
        source_rows.append("Y137_D11_V1_ALL_VERDICT|complete_Q5_support_targets=64" +
                           "|spooled_V1_over_b_bytes=" + str(total) + "|json=0")
        manifest_path = os.path.join(folder, "sources.hbp")
        write_receipt(manifest_path, "\n".join(source_rows) + "\n")
        return manifest_path, total

    with tempfile.TemporaryDirectory() as d:
        m, total = sources(d)
        receipts = os.path.join(d, "receipts")
        for g in range(GROUPS):
            verify(m, g, os.path.join(d, "GROUP-" + str(g) + ".v1"),
                   os.path.join(receipts, "GROUP-" + str(g) + ".hbp"),
                   64, total, check_canonical=False)
        output = aggregate(m, receipts, os.path.join(d, "all.hbp"), 64, total,
                           require_canonical=False)
        need("prediction_B2=TOY_ONLY" in output, "toy_aggregation_failed")
        refused = 0
        for flaw in ("duplicate", "same_bucket_reverse", "bucket_order", "lane", "group"):
            m, total = sources(d, 2, flaw)
            try:
                verify(m, 2, os.path.join(d, "GROUP-2.v1"),
                       os.path.join(d, "fault.hbp"), 64, total,
                       check_canonical=False)
            except Refuse as exc:
                if flaw in ("duplicate", "same_bucket_reverse"):
                    need(str(exc) == "bucket_address_nonascending_or_duplicate",
                         "wrong_same_bucket_refusal_reason")
                refused += 1
        need(refused == 5, "planted_structural_fault_accepted")
        m, total = sources(d)
        with open(os.path.join(d, "GROUP-2.v1"), "ab") as f:
            f.write(b"\x00")
        try:
            verify(m, 2, os.path.join(d, "GROUP-2.v1"),
                   os.path.join(d, "fault.hbp"), 64, total,
                       check_canonical=False)
        except Refuse:
            refused += 1
        need(refused == 6, "planted_hash_fault_accepted")
        try:
            canonical_weight(2)  # transposition index 2 conjugates to index 1
        except Refuse:
            refused += 1
        need(canonical_weight(1) == 3 and refused == 7,
             "planted_noncanonical_S3_orbit_accepted")
        # Attack the on-disk file, recomputing its manifest hash.
        # Canonicality must fail independently of the SHA verifier.
        m, total = sources(d, 0, "noncanonical_file")
        try:
            verify(m, 0, os.path.join(d, "GROUP-0.v1"),
                   os.path.join(d, "fault.hbp"), 64, total,
                   check_canonical=True)
        except Refuse as exc:
            need(str(exc) == "noncanonical_source_address",
                 "wrong_on_disk_noncanonical_refusal_reason")
            refused += 1
        need(refused == 8, "planted_rehashed_noncanonical_file_accepted")
        # Spoof a PASS receipt while retaining genuine content hashes:
        # aggregate must independently bind it to the current code and job.
        m, total = sources(d)
        for g in range(GROUPS):
            verify(m, g, os.path.join(d, "GROUP-" + str(g) + ".v1"),
                   os.path.join(receipts, "GROUP-" + str(g) + ".hbp"),
                   64, total, check_canonical=False)
        forged_path = os.path.join(receipts, "GROUP-0.hbp")
        with open(forged_path, encoding="ascii") as f:
            legitimate = f.read()
        with open(forged_path, "w", encoding="ascii") as f:
            f.write(legitimate.replace(
                "code_sha256=" + code_provenance()[0],
                "code_sha256=" + "0" * 64))
        try:
            aggregate(m, receipts, os.path.join(d, "forged.hbp"), 64, total,
                      require_canonical=False)
        except Refuse as exc:
            need(str(exc) == "forged_or_stale_group_provenance",
                 "wrong_forged_receipt_refusal_reason")
            refused += 1
        need(refused == 9, "planted_forged_PASS_receipt_accepted")
    return ("Y137_STAGE_B_SOURCE_TOY|groups=8|buckets=64|distinct_keys=64" +
            "|faults_refused=9|B1_B2=TOY_ONLY|real_Q5=NOT_COMPUTED|json=0\n")


def main(argv):
    try:
        if argv == ["selftest"]:
            print(selftest(), end="")
        elif len(argv) == 5 and argv[0] == "verify":
            _, manifest_path, group, spool_path, receipt_path = argv
            print(verify(manifest_path, int(group), spool_path, receipt_path), end="")
        elif len(argv) == 4 and argv[0] == "aggregate":
            _, manifest_path, receipt_dir, output_path = argv
            print(aggregate(manifest_path, receipt_dir, output_path), end="")
        else:
            raise Refuse("usage")
    except (Refuse, ValueError, OSError, UnicodeError, KeyError) as exc:
        print("Y137_STAGE_B_SOURCE_REFUSE|reason=" + str(exc) + "|json=0", flush=True)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main(sys.argv[1:])
