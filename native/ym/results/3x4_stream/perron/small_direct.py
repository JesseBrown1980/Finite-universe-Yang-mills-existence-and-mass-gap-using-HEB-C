# Direct small-lattice test of the whole-space lift, by shellschur counts (separate code from perroncert).
# Predictions, written before this ran, for t just below and just above lambda_1 of the sector's H':
#   S1  whole-space H' count is 0 below and >= 1 above, the same as the sector's.
#   S2  the whole-space count of H itself at t just below lambda_1 is <= 8.
#   S3  perroncert's t_cert <= lambda_1 at every solve threshold.
# Integer arithmetic only. json=0.
import os, subprocess, sys

RD = "D:/ym-3x4-room-run/p0-ball"
LX, LY = sys.argv[1], sys.argv[2]
LO, HI = int(sys.argv[3]), int(sys.argv[4])  # bracket of lambda_1 from the sector bisection
os.chdir(f"{RD}/small/{LX}x{LY}")
JE, JB = "1000", "9000"
log = open(f"SMALL-DIRECT-{LX}x{LY}.hbp", "w", newline="\n")


def say(s):
    print(s, flush=True)
    log.write(s + "\n")
    log.flush()


def fields(line):
    return dict(x.split("=", 1) for x in line.strip().split("|")[1:] if "=" in x)


def count(matrix, t):
    r = subprocess.run([f"{RD}/shellschur.exe", matrix, JE, JB, str(t), "-1", "12", "1000", "400"], capture_output=True, text=True)
    for ln in r.stdout.splitlines():
        if ln.startswith("SHELL_SCHUR|"):
            f = fields(ln)
            return f.get("negative"), f.get("ambiguous"), f.get("core")
    return None, None, None


say(f"S0|L={LX}x{LY}|lambda1_sector_in=[{LO},{HI}]|json=0")
for name, matrix, t in (
    ("sector_Hprime_below", "sector-nf.txt", LO),
    ("sector_Hprime_above", "sector-nf.txt", HI),
    ("whole_Hprime_below", "whole-nf.txt", LO),
    ("whole_Hprime_above", "whole-nf.txt", HI),
    ("whole_H_below", "whole.txt", LO),
    ("sector_H_below", "sector.txt", LO),
):
    neg, amb, core = count(matrix, t)
    say(f"S1S2|{name}|matrix={matrix}|t_milli={t}|negative={neg}|ambiguous={amb}|core={core}|json=0")
for dist in (5_000_000, 2_000_000, 500_000):
    t0 = LO - dist
    out = subprocess.run([f"{RD}/perroncert.exe", "solve", "dev.bin", "0", JE, JB, str(t0), "200"], capture_output=True, text=True).stdout.strip().splitlines()[-1]
    f = fields(out)
    tc = f.get("t_cert_milli")
    below = int(tc is not None and int(tc) <= HI)
    say(f"S3|solve_t_milli={t0}|t_cert_milli={tc}|below_lambda1={below}|shortfall_to_hi={HI - int(tc) if tc else 'NONE'}|flats={f.get('flats')}|min_mag={f.get('min_mag')}|json=0")
say("DONE")
