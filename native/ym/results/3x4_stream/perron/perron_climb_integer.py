# Integer copy of native/ym/results/3x4_stream/perron/perron_climb.py, written by native/scripts/make_integer_pairs.py: 2 divisions moved to qdiv and 4 text pairs. The original stays as evidence.
# Climbs the Perron threshold toward the level in one unattended run. Each stage warm-starts perroncert from the best vector so
# far, and each final row is perroncert's own exact check pass. Thresholds are chosen by an exact-fraction fit of
# 1/(t_cert - t) = a/(lambda1 - t) + b. The fit only chooses the next threshold. It certifies nothing, and a stage that diverges
# costs time only, because the best vector is kept in its own file.
#
# usage: perron_climb.py EXE DEV START_D WORKDIR FIRST_T BUDGET_SECS INNER PASSES [KNOWN_T:EXCESS ...]
#   FIRST_T and KNOWN_T in t_milli (10^-6 J_E at JE=1000), EXCESS = t_cert - t in the same units. json=0.
import os, re, shutil, subprocess, sys, time
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "scripts"))
from intpair import IntPair as F, qdiv

exe, dev, start, work, first_t, budget, inner, passes = sys.argv[1:9]
first_t, budget, passes = int(first_t), int(budget), int(passes)
points = [tuple(int(x) for x in a.split(":")) for a in sys.argv[9:]]
os.makedirs(work, exist_ok=True)
t0 = time.monotonic_ns()
log_path = os.path.join(work, "CLIMB.hbp")
STEP_FLOOR = 2000  # stop when the next step is under 0.002 J_E
MARGIN_STOP = 6000  # stop when the estimated distance to the level is under 0.006 J_E
MAX_SEGMENTS = 5


def say(s):
    print(s, flush=True)
    with open(log_path, "a", newline="\n") as f:
        f.write(s + "\n")


def fields(line):
    return dict(x.split("=", 1) for x in line.strip().split("|")[1:] if "=" in x)


def segment(t, source, out, tag):
    env = dict(os.environ, PERRONCERT_START=source, PERRONCERT_INNER=inner)
    path = os.path.join(work, f"seg-{tag}.out")
    with open(path, "w", newline="\n") as f:
        rc = subprocess.run([exe, "solve", dev, "0", "1000", "9000", str(t), str(passes), out], env=env, stdout=f, stderr=subprocess.STDOUT).returncode
    txt = open(path, encoding="utf-8", errors="replace").read()
    final = [ln for ln in txt.splitlines() if ln.startswith("PERRONCERT|")]
    changes = [int(m) for m in re.findall(r"biggest_change=(\d+)", txt)]
    if rc != 0 or not final:
        return None, changes
    return fields(final[-1]), changes


def estimate(pts):
    """Least level above the top threshold that fits the last three points, by bisection in exact fractions."""
    if len(pts) < 3:
        return None
    (t1, e1), (t2, e2), (t3, e3) = pts[-3:]
    u1, u2, u3 = F(1, e1), F(1, e2), F(1, e3)
    if u3 <= u2 or u2 <= u1:
        return None
    want = qdiv((u3 - u2) , (u2 - u1))

    def ratio(lam):
        a, b, c = F(1, lam - t1), F(1, lam - t2), F(1, lam - t3)
        return qdiv((c - b) , (b - a))

    lo, hi = t3 + 1, t3 + 2_000_000
    if not ratio(hi) < want < ratio(lo):
        return None
    while hi - lo > 100:
        mid = (lo + hi) // 2
        if ratio(mid) > want:
            lo = mid
        else:
            hi = mid
    return lo


best = (None, None, None)  # t_cert, threshold, file
best_row = None
source = start
t = first_t
ceiling = None
stage = 0
say(f"CLIMB_START|first_t={first_t}|budget_secs={budget}|inner={inner}|passes_per_segment={passes}|known={','.join(f'{a}:{b}' for a, b in points)}|json=0")
while True:
    stage += 1
    prev = None
    done = None
    src = source
    out = os.path.join(work, f"d{t}.bin")
    for seg in range(1, MAX_SEGMENTS + 1):
        if time.monotonic_ns() - t0 > budget * 10**9:
            say(f"CLIMB_BUDGET|stage={stage}|t={t}|json=0")
            break
        row, changes = segment(t, src, out, f"{t}-{seg}")
        secs = (time.monotonic_ns() - t0) // 10**9
        if row is None:
            say(f"CLIMB_SEGMENT|stage={stage}|t={t}|seg={seg}|result=solver_stopped|changes={','.join(map(str, changes))}|secs={secs}|json=0")
            done = "over"
            break
        tc = int(row["t_cert_milli"])
        say(f"CLIMB_SEGMENT|stage={stage}|t={t}|seg={seg}|t_cert_milli={tc}|min_row={row['min_row']}|min_mag={row['min_mag']}|d_max={row['d_max']}|d_sha256={row['d_sha256']}|last_change={changes[-1] if changes else 'none'}|secs={secs}|json=0")
        if best[0] is None or tc > best[0]:
            keep = os.path.join(work, "best.bin")
            shutil.copyfile(out, keep + ".tmp")
            os.replace(keep + ".tmp", keep)
            best = (tc, t, keep)
            best_row = row
        growing = len(changes) >= 2 and changes[-1] > changes[-2]
        if tc < t and growing and seg >= 2:
            done = "over"
            break
        if tc >= t and prev is not None and abs(tc - prev) <= 20:
            done = "settled"
            break
        if tc >= t and changes and int(row["d_max"]) // max(changes[-1], 1) > 10**7:
            done = "settled"
            break
        prev = tc
        src = out
    else:
        done = "slow"
    if done is None:
        break
    if done == "settled":
        points.append((t, int(row["t_cert_milli"]) - t))
        source = os.path.join(work, "best.bin")
        lam = estimate(points)
        if lam is None:
            step = max((ceiling - t) // 2, STEP_FLOOR) if ceiling else 50_000
        else:
            say(f"CLIMB_ESTIMATE|level_estimate_milli={lam}|from_points={','.join(f'{a}:{b}' for a, b in points[-3:])}|tag=CONJECTURE|json=0")
            if lam - t < MARGIN_STOP:
                say(f"CLIMB_STOP|reason=within_margin_of_estimate|t={t}|json=0")
                break
            step = (lam - t) * 7 // 10
        if ceiling is not None:
            step = min(step, (ceiling - t) // 2)
        step = step // 1000 * 1000
        if step < STEP_FLOOR:
            say(f"CLIMB_STOP|reason=step_below_floor|t={t}|json=0")
            break
        t += step
    else:
        # The threshold was at or too near the level. Step back halfway toward the last settled threshold.
        ceiling = t if ceiling is None else min(ceiling, t)
        base = points[-1][0]
        source = os.path.join(work, "best.bin") if best[2] else start
        if os.path.exists(out):
            os.remove(out)
        if ceiling - base < 2 * STEP_FLOOR:
            say(f"CLIMB_STOP|reason=bracket_closed|settled={base}|ceiling={ceiling}|json=0")
            break
        t = base + (ceiling - base) // 2 // 1000 * 1000
if best[0] is None:
    say("CLIMB_DONE|result=no_vector|json=0")
    sys.exit(2)
say(f"CLIMB_DONE|best_t_cert_milli={best[0]}|at_threshold={best[1]}|min_row={best_row['min_row']}|min_mag={best_row['min_mag']}|d_max={best_row['d_max']}|d_sha256={best_row['d_sha256']}|secs={(time.monotonic_ns() - t0) // 10**9}|json=0")
