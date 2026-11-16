#!/usr/bin/env python3
"""Centre scan: for each grid, the certified gap at r* (where the electric-side and magnetic-side
first-order formulas meet) and on shells r* -2, -1, +1, +2, plus r = 1/3 for the electric-side formula.
Calls the Rust program; couplings are thirds (RDEN = 3). Integers only.
usage: centre_scan.py PATH_TO_open_grid_BINARY"""
import subprocess
import sys

DEN = 3
GRIDS = (((1, 1), 12), ((2, 1), 13), ((3, 1), 13), ((4, 1), 14), ((5, 1), 14), ((2, 2), 14))  # r* in thirds
S = 1000000000


def emit(label, **f):
    print(label + "|" + "|".join("%s=%s" % kv for kv in f.items()) + "|json=0", flush=True)


def run(exe, a, b, num):
    out = subprocess.run([exe, str(a), str(b), str(num), "2", str(DEN)], capture_output=True).stdout.decode("ascii", "replace")
    row = [line for line in out.splitlines() if line.startswith("GRID_LEVELS|")]
    if not row or "NOT_CERTIFIED" in row[-1]:
        return None
    d = dict(kv.split("=", 1) for kv in row[-1].split("|")[1:] if "=" in kv)
    # levels are those of DEN*H: divide the gap bracket by DEN, outward
    return int(d["gap_lo"]) // DEN, -((-int(d["gap_hi"])) // DEN)


def main():
    exe = sys.argv[1]
    c1 = c2 = c3 = True
    minima = {}
    for (a, b), star in GRIDS:
        gaps = {}
        for num in (1, star - 6, star - 3, star, star + 3, star + 6):
            g = run(exe, a, b, num)
            gaps[num] = g
            emit("CENTRE_POINT", a=a, b=b, r_thirds=num, centre_thirds=star, units="1e-9",
                 gap_lo=g[0] if g else "NOT_CERTIFIED", gap_hi=g[1] if g else "NOT_CERTIFIED")
        if any(v is None for v in gaps.values()):
            emit("CENTRE_GRID", a=a, b=b, status="NOT_CERTIFIED_AT_SOME_POINT")
            c1 = c2 = c3 = False
            continue
        five = {k: v for k, v in gaps.items() if k != 1}
        best = min(five, key=lambda k: five[k][1])
        strictly = all(five[best][1] < v[0] for k, v in five.items() if k != best)
        minima[(a, b)] = five[best]
        electric = (12 * DEN - 1) * S // DEN  # 12 - 1/3
        e_err = max(abs(gaps[1][0] - electric), abs(gaps[1][1] - electric))
        c1 &= abs(best - star) <= 3
        c2 &= e_err <= S // 10
        c3 &= 4 * S <= five[best][0] and five[best][1] <= 8 * S
        emit("CENTRE_GRID", a=a, b=b, centre_thirds=star, smallest_at_thirds=best, smallest_is_strict=int(strictly),
             smallest_gap_lo=five[best][0], smallest_gap_hi=five[best][1],
             electric_formula_at_one_third=electric, certified_gap_at_one_third_lo=gaps[1][0], electric_side_error=e_err)
    ladder = [minima.get((n, 1)) for n in range(1, 6)]
    c4 = all(x is not None for x in ladder) and all(ladder[i + 1][0] <= ladder[i][1] for i in range(4)) \
        and minima.get((2, 2)) is not None and minima[(2, 2)][0] <= minima[(4, 1)][1]
    emit("CENTRE_VERDICT", C1=int(c1), C2=int(c2), C3=int(c3), C4=int(c4))


if __name__ == "__main__":
    main()
