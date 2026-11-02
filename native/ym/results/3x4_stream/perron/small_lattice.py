# Small-lattice controls for perroncert, using shellschur counts (separate code, interval Gauss-Seidel
# and exact integers, nothing shared with perroncert). All arithmetic on thresholds is integer. json=0.
#
# Predictions, written before this ran:
#  S1  lambda_1(H' sector) == lambda_1(H' whole space), to the bisection width. The Perron vector of
#      the whole-space H' is positive and unique, so it lies in the symmetric sector.
#  S2  N_whole(lambda_1) <= 8 and lambda_1 <= E_9(whole space).
#  S3  perroncert's t_cert <= lambda_1, and t_cert is near lambda_1 when t is near it.
#  S4  The whole-space count of flats is 8, the sector count 7, all diagonals 3*nl, no flat couplings.
import os, subprocess, sys

RD = "D:/ym-3x4-room-run/p0-ball"
LX, LY, K = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
W = f"{RD}/small/{LX}x{LY}"
os.makedirs(W, exist_ok=True)
os.chdir(W)
JE, JB = "1000", "9000"
U = 1_000_000  # t_milli per J_E
log = open(f"SMALL-{LX}x{LY}.hbp", "w", newline="\n")


def say(s):
    print(s, flush=True)
    log.write(s + "\n")
    log.flush()


def run(*a):
    return subprocess.run([str(x) for x in a], capture_output=True, text=True)


def fields(line):
    return dict(x.split("=", 1) for x in line.strip().split("|")[1:] if "=" in x)


def without_flats(src, dst):
    with open(src) as f:
        n = int(f.readline())
        w = f.readline().split()
        m = f.readline().split()
        keep = [i for i in range(n) if m[i] != "0"]
        rank = {o: i for i, o in enumerate(keep)}
        lines = []
        for ln in f:
            a, b, z = ln.split()
            a, b = int(a), int(b)
            if a in rank and b in rank:
                lines.append(f"{rank[a]} {rank[b]} {z}\n")
    with open(dst, "w", newline="\n") as f:
        f.write(f"{len(keep)}\n{' '.join(w[i] for i in keep)}\n{' '.join(m[i] for i in keep)}\n")
        f.writelines(lines)
    return n, n - len(keep)


def count(matrix, t):
    r = run(f"{RD}/shellschur.exe", matrix, JE, JB, t, -1, 12, 1000, 400)
    for ln in r.stdout.splitlines():
        if ln.startswith("SHELL_SCHUR|"):
            f = fields(ln)
            if f.get("ambiguous") != "0":
                return None
            return int(f["negative"])
    return None


def bisect_up(matrix, want, lo, hi, width):
    """Smallest t in [lo, hi] (to width) with count(t) > want. Counts rise with t."""
    c = count(matrix, lo)
    assert c is not None and c <= want, ("low end", c)
    # Walk up in steps of 1 J_E to the first decided count above want.
    t = lo
    while True:
        t += U
        assert t <= hi, "no decided count above want"
        c = count(matrix, t)
        if c is None:
            say(f"SMALL_AMBIGUOUS|matrix={matrix}|t_milli={t}|json=0")
            continue
        if c > want:
            hi = t
            break
        lo = t
    while hi - lo > width:
        mid = (lo + hi) // 2
        c = count(matrix, mid)
        if c is None:
            say(f"SMALL_AMBIGUOUS|matrix={matrix}|t_milli={mid}|json=0")
            mid += 1
            c = count(matrix, mid)
            assert c is not None
        if c > want:
            hi = mid
        else:
            lo = mid
    return lo, hi


# build the store and both matrices
if not os.path.exists("dev.bin"):
    say(run(f"{RD}/ymroom.exe", "text", LX, LY, "sector.txt").stdout.strip())
    say(run(f"{RD}/ymroom.exe", "passa", LX, LY, "passa.bin").stdout.strip())
    n_sec = os.path.getsize("passa.bin") // 16
    with open("keys.bin", "wb") as f:
        f.truncate(8 * n_sec)
    open("dev.bin", "wb").close()
    say(run(f"{RD}/ymroom.exe", "build", LX, LY, "passa.bin", "keys.bin", "dev.bin", 0).stdout.strip().splitlines()[-1][:120])
    say(run(f"{RD}/ball.exe", LX, LY, K, "whole.txt").stdout.strip())
n_sec, nf_sec = without_flats("sector.txt", "sector-nf.txt")
n_all, nf_all = without_flats("whole.txt", "whole-nf.txt")
nl = 2 * LX * LY
say(f"SMALL_DIMS|L={LX}x{LY}|nl={nl}|sector_n={n_sec}|sector_flats={nf_sec}|whole_n={n_all}|whole_flats={nf_all}|json=0")
say(run(f"{RD}/flatcomp.exe", "sector.txt").stdout.strip())
say(run(f"{RD}/flatcomp.exe", "whole.txt").stdout.strip())

top = (3 * nl + 40) * U
width = 2000
lo_s, hi_s = bisect_up("sector-nf.txt", 0, (3 * nl - 20) * U, top, width)
say(f"S1_SECTOR|lambda1_in=[{lo_s},{hi_s}]|count_above=1|json=0")
lo_w, hi_w = bisect_up("whole-nf.txt", 0, (3 * nl - 20) * U, top, width)
say(f"S1_WHOLE|lambda1_in=[{lo_w},{hi_w}]|json=0")
s1 = int(lo_s <= hi_w and lo_w <= hi_s)
say(f"S1|sector_and_whole_overlap={s1}|width={width}|json=0")
n_at = count("whole.txt", lo_s)
lo9, hi9 = bisect_up("whole.txt", 8, lo_s - 2 * U, top, width)
say(f"S2|N_whole_at_lambda1={n_at}|E9_whole_in=[{lo9},{hi9}]|lambda1_le_E9={int(lo_s <= hi9)}|json=0")
for dist in (5 * U, 2 * U, U // 2):
    t0 = lo_s - dist
    out = run(f"{RD}/perroncert.exe", "solve", "dev.bin", 0, JE, JB, t0, 200).stdout.strip().splitlines()[-1]
    f = fields(out)
    tc = f.get("t_cert_milli")
    ok = tc is not None and int(tc) <= hi_s
    say(f"S3|solve_t_milli={t0}|t_cert_milli={tc}|below_lambda1={int(ok)}|shortfall={hi_s - int(tc) if tc else 'NONE'}|flats={f.get('flats')}|min_mag={f.get('min_mag')}|json=0")
say("DONE")
