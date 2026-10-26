#!/usr/bin/env python3
"""Spectral certificate for the full 3x3 zero-momentum operator from
shellschur inertia counts plus Krylov-Bogoliubov residual intervals.

Inputs: the sealed GitRAM sector receipt (CLUSTER_LEVEL lines per sector and
coupling) and shellschur logs run with JE=1000, JB=1000*R, so t_milli is the
threshold in micro-units of the physical energy.

Logic (every step an exact integer comparison):
  N(t) = sum over the four C2v sectors of neg(H_s - t). A sector count missing
  at t is taken as 0 only if the same sector has count 0 at some t' >= t
  (inertia is monotone in t).
  Each residual interval [lo, hi] contains at least one eigenvalue.

  Band gap (required): N(t1) = N(tB) = 8 with t1 < tB. Then E1..E8 < t1 and
  E9 >= tB. Every interval with hi < t1 contains one of E1..E8, so
  E8 >= max lo over those; every interval with lo >= t1 contains an
  eigenvalue >= E9, so E9 <= min hi over those.
      E9 - E8 in [tB - t1, min_hi - max_lo].

  Vacuum cluster (optional, reported when the thresholds are present):
    t0 with N(t0) = 0      =>  E1 >= t0;   E1 <= min hi of the cluster.
    ts with N(ts) = 1      =>  E2 >= ts;   E1 < ts, and E2 <= min hi over
                               intervals with lo >= ts.
      cluster width  E8 - E1 in [max(0, max_lo - min_hi), t1 - t0]
      first splitting E2 - E1 in [ts - E1_hi, E2_hi - t0]
Lattice (optional first argument --lattice LXxLY, default 3x3): cluster lines
are read with prefix YM{LX}X{LY}_S{sx}_{sy}_r{R}_, count lines from matrices
named s{LX}{LY}_{sx}_{sy}.matrix, and the 8-vacuum logic is unchanged.
Copied from The-matrix-law-essentials 8fd12e6 python/volume/shell_gap_cert.py;
only the lattice parameter was added.
usage: shell_gap_cert.py [--lattice LXxLY] SEALED_HBP R SHELL_LOG...        json=0
"""
import re
import sys


def main():
    args = sys.argv[1:]
    lx, ly = 3, 3
    if args and args[0] == "--lattice":
        lx, ly = (int(v) for v in args[1].split("x"))
        args = args[2:]
    lat = "%dx%d" % (lx, ly)
    sealed, r, logs = args[0], int(args[1]), args[2:]
    ivs = []
    pat = re.compile(r"YM%dX%d_S(-?1)_(-?1)_r%d_CLUSTER_LEVEL\|k=(\d+)\|.*interval=\[(\d+),(\d+)\]" % (lx, ly, r))
    for line in open(sealed):
        m = pat.match(line)
        if m:
            ivs.append((int(m.group(4)), int(m.group(5)), m.group(1) + "," + m.group(2), int(m.group(3))))
    counts = {}
    for path in logs:
        for line in open(path):
            if "SHELL_SCHUR|" not in line:
                continue
            f = dict(kv.split("=", 1) for kv in line.strip().split("|") if "=" in kv)
            if f.get("result") != "PASS" or f.get("JE") != "1000" or f.get("JB") != str(1000 * r):
                continue
            mt = re.search(r"s%d%d_(-?1)_(-?1)\.matrix" % (lx, ly), f["matrix"])
            counts[(mt.group(1) + "," + mt.group(2), int(f["t_milli"]))] = int(f["negative"])
    sectors = ("1,1", "1,-1", "-1,1", "-1,-1")
    ts_all = sorted({t for (_, t) in counts})

    def n_at(t):
        tot = 0
        for s in sectors:
            if (s, t) in counts:
                tot += counts[(s, t)]
            elif any(counts.get((s, u)) == 0 for u in ts_all if u >= t):
                tot += 0
            else:
                return None
        return tot

    def detail(t):
        return ",".join("%s:%d@%d" % (s, counts.get((s, t), 0), t) for s in sectors)

    good = [t for t in ts_all if n_at(t) == 8]
    if len(good) < 2:
        print("SHELL_GAP_CERT|r=%d|result=FAIL|reason=need_two_thresholds_with_N=8|json=0" % r)
        sys.exit(2)
    t1, tb = good[0], good[-1]
    below = [iv for iv in ivs if iv[1] < t1]
    above = [iv for iv in ivs if iv[0] >= t1]
    straddle = [iv for iv in ivs if iv[0] < t1 <= iv[1]]
    if not below or not above or straddle:
        print("SHELL_GAP_CERT|r=%d|result=FAIL|reason=intervals_straddle_or_missing|json=0" % r)
        sys.exit(2)
    e8_lo = max(iv[0] for iv in below)
    e9_hi = min(iv[1] for iv in above)
    e1_hi = min(iv[1] for iv in below)
    print("SHELL_GAP_CERT|L=%s|r=%d|N(t1)=8|N(tB)=8|t1=%d/1000000|tB=%d/1000000|sector_counts=%s,%s|E8_in=[%d,%d)/1000000|E9_in=[%d,%d]/1000000|gap_E9_minus_E8_in=[%d,%d]/1000000|cluster_intervals_below_t1=%d|cluster_lowest_interval_lo=%d/1000000|result=PASS|json=0"
          % (lat, r, t1, tb, detail(t1), detail(tb), e8_lo, t1, tb, e9_hi, tb - t1, e9_hi - e8_lo, len(below), min(iv[0] for iv in below)))
    zero = [t for t in ts_all if n_at(t) == 0]
    one = [t for t in ts_all if n_at(t) == 1]
    if zero:
        t0 = max(zero)
        if t0 > e1_hi:
            print("SHELL_CLUSTER_CERT|r=%d|result=FAIL|reason=t0_above_an_interval|json=0" % r)
            sys.exit(2)
        out = "SHELL_CLUSTER_CERT|L=%s|r=%d|N(t0)=0|t0=%d/1000000|E1_in=[%d,%d]/1000000|cluster_width_E8_minus_E1_in=[%d,%d]/1000000" % (
            lat, r, t0, t0, e1_hi, max(0, e8_lo - e1_hi), t1 - t0)
        if one:
            ts = max(one)
            if not (e1_hi < ts):
                print("SHELL_CLUSTER_CERT|r=%d|result=FAIL|reason=ts_not_above_first_interval|json=0" % r)
                sys.exit(2)
            e2_hi = min(iv[1] for iv in ivs if iv[0] >= ts)
            out += "|N(ts)=1|ts=%d/1000000|sector_counts_ts=%s|E2_in=[%d,%d]/1000000|first_splitting_E2_minus_E1_in=[%d,%d]/1000000" % (
                ts, detail(ts), ts, e2_hi, ts - e1_hi, e2_hi - t0)
        else:
            out += "|first_splitting=INCONCLUSIVE(no_threshold_with_N=1;intervals_overlap)"
        print(out + "|result=PASS|json=0")


if __name__ == "__main__":
    main()
