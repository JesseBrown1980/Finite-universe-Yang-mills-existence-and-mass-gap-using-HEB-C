"""Fail-closed collector for independent-verifier runs (integer only, json=0).

Protocol: one verifier process per threshold, one output file each. Every gate
below must pass before any count is compared; anything missing, duplicated,
malformed or out of scope is INCONCLUSIVE.

Per file, exactly one INDEP_RUN, one INDEP_BUILD and one INDEP_COUNT:
  RUN    code_sha256 equals the pinned reviewed hash (--code), seed present
  BUILD  L, gauge_orbits, burnside, weight_sum, six_pow_free and flat_states
         equal the pinned scope (--scope), and gauge_orbits = burnside,
         weight_sum = six_pow_free
  COUNT  L and r equal the pinned scope; t_milli is one of the expected
         thresholds; result=COMPUTED; N, hadamard_bits, primes_31bit and
         reshuffle_retries are integers
Across files every expected threshold appears exactly once, and nothing else.
Only then are the counts compared with the expected production counts.

Verdict: AGREE (exit 0), MISMATCH (exit 1), INCONCLUSIVE (exit 2). Any
exception while reading or parsing is INCONCLUSIVE.

usage: python collect.py [--kernel SHA256] --code SHA256 --scope L:r:orbits:weights:flat EXPECT FILE...
       (--kernel pins minor_kernel_sha256 when the Rust kernel produced the counts)
       EXPECT = t_milli:N[,t_milli:N...]
"""

import sys


class Reject(Exception):
    pass


def fields(line):
    out = {}
    for part in line.strip().split("|")[1:]:
        if "=" in part:
            k, v = part.split("=", 1)
            if k in out:
                raise Reject(f"duplicate_field_{k}")
            out[k] = v
    return out


def need(d, key):
    if key not in d:
        raise Reject(f"missing_field_{key}")
    return d[key]


def as_int(d, key):
    v = need(d, key)
    if not (v.isdigit() or (v.startswith("-") and v[1:].isdigit())):
        raise Reject(f"malformed_{key}")
    return int(v)


def parse_args(argv):
    kernel = None
    if len(argv) > 1 and argv[0] == "--kernel":
        kernel, argv = argv[1], argv[2:]
    if len(argv) < 6 or argv[0] != "--code" or argv[2] != "--scope":
        raise Reject("usage")
    code = argv[1]
    sl = argv[3].split(":")
    if len(sl) != 5:
        raise Reject("bad_scope")
    scope = {"L": sl[0], "r": int(sl[1]), "orbits": int(sl[2]), "weights": int(sl[3]), "flat": int(sl[4])}
    expect = {}
    for item in argv[4].split(","):
        t, n = item.split(":")
        if int(t) in expect:
            raise Reject("duplicate_expected_threshold")
        expect[int(t)] = int(n)
    return code, scope, expect, argv[5:], kernel


def check_file(path, code, scope, expect, kernel=None):
    runs, builds, counts = [], [], []
    with open(path) as fh:
        for line in fh:
            tag = line.split("|", 1)[0]
            if tag == "INDEP_RUN":
                runs.append(fields(line))
            elif tag == "INDEP_BUILD":
                builds.append(fields(line))
            elif tag == "INDEP_COUNT":
                counts.append(fields(line))
    if (len(runs), len(builds), len(counts)) != (1, 1, 1):
        raise Reject(f"records_per_file_{len(runs)}_{len(builds)}_{len(counts)}")
    run, build, count = runs[0], builds[0], counts[0]
    if need(run, "code_sha256") != code:
        raise Reject("code_hash_not_pinned_value")
    as_int(run, "seed")
    if "result" in build:
        raise Reject("build_failed")
    if need(build, "L") != scope["L"]:
        raise Reject("build_lattice")
    g, b = as_int(build, "gauge_orbits"), as_int(build, "burnside")
    w, s = as_int(build, "weight_sum"), as_int(build, "six_pow_free")
    if not (g == b == scope["orbits"] and w == s == scope["weights"] and as_int(build, "flat_states") == scope["flat"]):
        raise Reject("build_structure")
    if need(count, "L") != scope["L"] or as_int(count, "r") != scope["r"]:
        raise Reject("count_scope")
    t = as_int(count, "t_milli")
    if t not in expect:
        raise Reject(f"unexpected_threshold_{t}")
    if need(count, "result") != "COMPUTED":
        raise Reject(f"count_not_computed_t{t}")
    for key in ("hadamard_bits", "reshuffle_retries"):
        as_int(count, key)
    pk = [k for k in ("primes_31bit", "primes_62bit") if k in count]
    if len(pk) != 1:
        raise Reject("needs_exactly_one_prime_count_field")
    as_int(count, pk[0])
    count["primes"] = count[pk[0]]
    if kernel is not None and need(run, "minor_kernel_sha256") != kernel:
        raise Reject("minor_kernel_hash_not_pinned_value")
    return t, as_int(count, "N"), count


def main(argv):
    rows = []
    try:
        code, scope, expect, files, kernel = parse_args(argv)
        seen = {}
        for f in files:
            t, n, count = check_file(f, code, scope, expect, kernel)
            if t in seen:
                raise Reject(f"duplicate_threshold_{t}")
            seen[t] = (n, count)
        if set(seen) != set(expect):
            raise Reject("missing_thresholds_" + "_".join(str(t) for t in sorted(set(expect) - set(seen))))
        verdict = "AGREE"
        for t in sorted(expect):
            n, count = seen[t]
            st = "AGREE" if n == expect[t] else "MISMATCH"
            if st == "MISMATCH":
                verdict = "MISMATCH"
            rows.append(
                f"INDEP_CHECK|L={scope['L']}|r={scope['r']}|t_milli={t}|expected={expect[t]}|got={n}"
                f"|hadamard_bits={count['hadamard_bits']}|primes={count['primes']}"
                f"|reshuffle_retries={count['reshuffle_retries']}|status={st}|json=0"
            )
        rows.insert(0, f"INDEP_COLLECT|code_sha256={code}|L={scope['L']}|r={scope['r']}|gauge_orbits={scope['orbits']}"
                       f"|weight_sum={scope['weights']}|flat_states={scope['flat']}|files={len(files)}|gates=PASS|json=0")
    except (Reject, OSError, ValueError, KeyError, IndexError) as e:
        print("\n".join(rows + [f"INDEP_COLLECT|gates=FAIL|reason={str(e).replace(' ', '_') or type(e).__name__}|json=0",
                                "INDEP_VERDICT|INCONCLUSIVE|json=0"]))
        sys.exit(2)
    print("\n".join(rows + [f"INDEP_VERDICT|{verdict}|json=0"]))
    sys.exit(0 if verdict == "AGREE" else 1)


if __name__ == "__main__":
    main(sys.argv[1:])
