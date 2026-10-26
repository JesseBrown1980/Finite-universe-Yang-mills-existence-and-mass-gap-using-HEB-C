"""Fan-in of ymstream residue-class cells (integer only, json=0).

Checks, then sums:
  * every residue class 0..M-1 appears exactly once, all cells share L, JE, JB
    and the threshold list;
  * gauge orbits: the summed count equals Burnside for global conjugation on
    S3^k, (6^k + 3*2^k + 2*3^k)/6;
  * sector dimensions: for every sector the representative count equals the
    character formula  sum_g chi_s(g) Fix(g) / |G|  (two independent routes);
  * flat states, core rows and non-positive diagonals at each threshold are
    summed; row hashes are XOR-combined (order independent).
usage: python stream_fanin.py CELL_FILE...
"""

from __future__ import annotations

import sys


def fields(line: str) -> dict[str, str]:
    return dict(p.split("=", 1) for p in line.strip().split("|")[1:] if "=" in p)


def main(files: list[str]) -> None:
    heads, secs = [], []
    for f in files:
        for line in open(f):
            if line.startswith("YMSTREAM|"):
                heads.append(fields(line))
            elif line.startswith("YMSTREAM_SECTOR|"):
                secs.append(fields(line))
    if not heads or any("error" in h for h in heads):
        raise SystemExit("YMSTREAM_FANIN|error=missing_or_failed_cell|json=0")
    L, je, jb = heads[0]["L"], heads[0]["JE"], heads[0]["JB"]
    mod = int(heads[0]["class"].split("/")[1])
    classes = sorted(int(h["class"].split("/")[0]) for h in heads)
    same = all(h["L"] == L and h["JE"] == je and h["JB"] == jb and int(h["class"].split("/")[1]) == mod for h in heads)
    partition = classes == list(range(mod))
    space = int(heads[0]["space"])
    k = 0
    while 6**k < space:
        k += 1
    burnside = (6**k + 3 * 2**k + 2 * 3**k) // 6
    orbits = sum(int(h["gauge_orbits"]) for h in heads)
    group = int(heads[0]["group"])
    fix = [0] * group
    for h in heads:
        for i, v in enumerate(h["fix"].split(",")):
            fix[i] += int(v)
    tot: dict[str, dict] = {}
    for s in secs:
        t = tot.setdefault(s["sector"], {"reps": 0, "flat": 0, "char": 0, "core": {}, "nonpos": {}, "hash": 0})
        t["reps"] += int(s["reps"])
        t["flat"] += int(s["flat_states"])
        t["char"] += int(s["character_sum"])
        t["hash"] ^= int(s["row_hash"], 16)
        for c in s["core_t:rows:nonpos"].split(","):
            tt, rows, np_ = c.split(":")
            t["core"][tt] = t["core"].get(tt, 0) + int(rows)
            t["nonpos"][tt] = t["nonpos"].get(tt, 0) + int(np_)
    out = [
        f"YMSTREAM_TOTAL|L={L}|JE={je}|JB={jb}|cells={len(heads)}|modulus={mod}|partition={int(partition)}|consistent={int(same)}"
        f"|space={space}|gauge_orbits={orbits}|burnside={burnside}|orbits_match={int(orbits == burnside)}|group={group}|json=0"
    ]
    dims_ok = True
    for name in sorted(tot):
        t = tot[name]
        exact = t["char"] % group == 0 and t["char"] // group == t["reps"]
        dims_ok &= exact
        cores = ",".join(f"{tt}:{t['core'][tt]}:{t['nonpos'][tt]}" for tt in sorted(t["core"], key=int))
        out.append(
            f"YMSTREAM_SECTOR_TOTAL|L={L}|sector={name}|states={t['reps']}|character_formula={t['char']}/{group}"
            f"|dimension_match={int(exact)}|flat_states={t['flat']}|core_t:rows:nonpos={cores}|row_hash={t['hash']:016x}|json=0"
        )
    ok = partition and same and orbits == burnside and dims_ok
    out.append(f"YMSTREAM_FANIN|L={L}|result={'PASS' if ok else 'FAIL'}|json=0")
    print("\n".join(out))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
