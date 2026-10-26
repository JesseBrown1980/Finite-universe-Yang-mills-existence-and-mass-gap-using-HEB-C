"""Fail-closed collector for independent-verifier runs (integer only, json=0).

Reads INDEP_* records from one or more output files and requires:
  * one INDEP_RUN and one INDEP_BUILD per file, identical code hash and build;
  * gauge_orbits == burnside and weight_sum == six_pow_free;
  * every INDEP_COUNT has result=COMPUTED (any INCONCLUSIVE fails, whatever the
    process exit status was);
  * the computed counts equal the expected production counts.
Verdict: AGREE (exit 0), MISMATCH (exit 1), INCONCLUSIVE (exit 2).
usage: python collect.py EXPECT FILE...      EXPECT = t_milli:N[,t_milli:N...]
"""

import sys


def fields(line):
    return dict(p.split("=", 1) for p in line.strip().split("|")[1:] if "=" in p)


def main(argv):
    expect = {int(a): int(b) for a, b in (x.split(":") for x in argv[0].split(","))}
    runs, builds, counts = [], [], {}
    for f in argv[1:]:
        for line in open(f):
            tag = line.split("|", 1)[0]
            if tag == "INDEP_RUN":
                runs.append(fields(line))
            elif tag == "INDEP_BUILD":
                builds.append(fields(line))
            elif tag == "INDEP_COUNT":
                d = fields(line)
                counts[int(d["t_milli"])] = d
    out = []
    verdict = "AGREE"
    codes = {r["code_sha256"] for r in runs}
    struct_ok = (
        len(runs) == len(argv) - 1
        and len(builds) == len(argv) - 1
        and len(codes) == 1
        and all("result" not in b for b in builds)
        and all(b["gauge_orbits"] == b["burnside"] and b["weight_sum"] == b["six_pow_free"] for b in builds)
        and len({(b["L"], b["gauge_orbits"], b["weight_sum"], b["flat_states"]) for b in builds}) == 1
    )
    if not struct_ok:
        verdict = "INCONCLUSIVE"
    for t, n in sorted(expect.items()):
        d = counts.get(t)
        if d is None or d.get("result") != "COMPUTED":
            verdict = "INCONCLUSIVE"
            out.append(f"INDEP_CHECK|t_milli={t}|expected={n}|got=-|status=INCONCLUSIVE|json=0")
            continue
        got = int(d["N"])
        st = "AGREE" if got == n else "MISMATCH"
        if st == "MISMATCH" and verdict == "AGREE":
            verdict = "MISMATCH"
        out.append(
            f"INDEP_CHECK|t_milli={t}|expected={n}|got={got}|hadamard_bits={d['hadamard_bits']}"
            f"|primes_31bit={d['primes_31bit']}|reshuffle_retries={d['reshuffle_retries']}|status={st}|json=0"
        )
    b = builds[0] if builds else {}
    out.insert(0, f"INDEP_COLLECT|code_sha256={','.join(sorted(codes))}|L={b.get('L', '-')}|gauge_orbits={b.get('gauge_orbits', '-')}"
                  f"|burnside={b.get('burnside', '-')}|weight_sum={b.get('weight_sum', '-')}|structure={'PASS' if struct_ok else 'FAIL'}|json=0")
    out.append(f"INDEP_VERDICT|{verdict}|json=0")
    print("\n".join(out))
    sys.exit({"AGREE": 0, "MISMATCH": 1, "INCONCLUSIVE": 2}[verdict])


if __name__ == "__main__":
    main(sys.argv[1:])
