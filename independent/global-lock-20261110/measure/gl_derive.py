#!/usr/bin/env python3
"""Derive GL1 and GL3 enclosures from the certified LEVEL rows, then (second stage) compare.

usage: gl_derive.py measure   -> MEASURE-GLOBAL-LOCK.hbp (measured block only) + .sha256
       gl_derive.py compare   -> appends the verdict block to MEASURE-GLOBAL-LOCK.hbp + .sha256

GL1: c_hat(r) = r*(3r - (E9-E8)/J_E).   GL3: W(r) = E8 - E1,  rho = W(r)/W(3r).
All numbers are integer pairs; decimals are rounded outward.  Integer only, json=0.
"""
import hashlib
import sys
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
OUT = HERE / "MEASURE-GLOBAL-LOCK.hbp"
FROZEN = HERE.parents[2] / "docs" / "PREDICTION-GLOBAL-LOCK-20261110.hbp"
GL1_POINTS = (("3x4", 27), ("3x4", 81), ("3x4", 729), ("3x3", 729))
GL3_POINTS = (("3x3", 27), ("3x3", 81), ("3x4", 27), ("3x4", 81))
L_MIN = {"3x3": 3, "3x4": 3}


def fail(label):
    print("FAILED|check=" + label + "|json=0")
    raise SystemExit(1)


def red(n, d):
    g = gcd(n, d)
    return n // g, d // g


def dec(n, d, places, up):
    s = 1
    for _ in range(places):
        s *= 10
    q = -((-n * s) // d) if up else (n * s) // d
    sign = "-" if q < 0 else ""
    q = abs(q)
    a, b = divmod(q, s)
    return sign + str(a) + "." + str(b).rjust(places, "0")


def frac(n, d):
    n, d = red(n, d)
    return str(n) + "/" + str(d)


def row(label, **f):
    return label + "|" + "|".join(str(k) + "=" + str(v) for k, v in f.items()) + "|json=0"


def levels():
    L = {}
    src = []
    # every certified run is used; enclosures of the same level from different runs are
    # each rigorous, so their intersection is rigorous (lo = max of lows, hi = min of highs)
    for p in sorted(RUNS.glob("levels-*.rows")):
        name = p.name
        raw = p.read_bytes()
        src.append(row("SOURCE_ROWS", file="runs/" + name, sha256=hashlib.sha256(raw).hexdigest(),
                       bytes=len(raw)))
        text = raw.decode()
        if "GL_MEASURE_END|" not in text or "result=PASS" not in text.split("GL_MEASURE_END|")[1]:
            fail("source_run_completed_" + name)
        for s in text.splitlines():
            if s.startswith("LEVEL|"):
                f = dict(it.split("=", 1) for it in s.split("|")[1:] if "=" in it)
                lo = None if f["lo_num"] == "NONE" else int(f["lo_num"])
                hi, d = int(f["hi_num"]), int(f["den"])
                if d != 1000000000000:
                    fail("common_denominator")
                key = (f["lattice"], int(f["r"]), f["level"])
                old = L.get(key)
                if old is not None:
                    olo, ohi, _ = old
                    lo = olo if lo is None else (lo if olo is None else max(lo, olo))
                    hi = min(hi, ohi)
                if lo is not None and lo > hi:
                    fail("certified_enclosures_disjoint")
                L[key] = (lo, hi, d)
    return L, src


def measure():
    L, src = levels()
    rows = [row("MEASURE_GLOBAL_LOCK_BEGIN", stage="measured_block", predict_rows_opened=0,
                method="Haynsworth_inertia_trial_resolvent_Schur_onto_flat_plus_M3_complete_exterior",
                floor="M4_census_rho44_P2max_unconditional", float_used=0)]
    rows += src
    for (lat, r, lvl), (lo, hi, d) in sorted(L.items()):
        rows.append(row("LEVEL_ENCLOSURE", lattice=lat, r=r, level=lvl,
                        lo="NONE" if lo is None else frac(lo, d), hi=frac(hi, d),
                        lo_dec="NONE" if lo is None else dec(lo, d, 12, False), hi_dec=dec(hi, d, 12, True)))
    for lat, r in GL1_POINTS:
        e8 = L.get((lat, r, "E8"))
        e9 = L.get((lat, r, "E9"))
        if e8 is None or e9 is None or e8[0] is None:
            rows.append(row("GL1_MEASURED", lattice=lat, r=r, status="NOT_MEASURED", reason="levels_missing"))
            continue
        d = e8[2]
        dhi = e9[1] - e8[0]                      # Delta upper (numerator over d)
        c_lo = r * (3 * r * d - dhi)             # c_hat lower, over d
        if e9[0] is None:
            rows.append(row("GL1_MEASURED", lattice=lat, r=r, c_hat_lo=frac(c_lo, d), c_hat_hi="NONE",
                            c_hat_lo_dec=dec(c_lo, d, 9, False), c_hat_hi_dec="NONE",
                            delta_hi_dec=dec(dhi, d, 12, True), delta_lo_dec="NONE",
                            sides="ONE_SIDED", reason="E9_lower_side_not_certified_floor_or_residual"))
            continue
        dlo = e9[0] - e8[1]
        c_hi = r * (3 * r * d - dlo)
        rows.append(row("GL1_MEASURED", lattice=lat, r=r, c_hat_lo=frac(c_lo, d), c_hat_hi=frac(c_hi, d),
                        c_hat_lo_dec=dec(c_lo, d, 9, False), c_hat_hi_dec=dec(c_hi, d, 9, True),
                        c_hat_width_dec=dec(c_hi - c_lo, d, 9, True),
                        delta_lo_dec=dec(dlo, d, 12, False), delta_hi_dec=dec(dhi, d, 12, True),
                        delta_width_dec=dec(dhi - dlo, d, 12, True), sides="TWO_SIDED"))
    W = {}
    for lat in ("3x3", "3x4"):
        for r in (27, 81, 243, 729):
            e1 = L.get((lat, r, "E1"))
            e8 = L.get((lat, r, "E8"))
            if e1 is None or e8 is None or e1[0] is None or e8[0] is None:
                continue
            d = e1[2]
            wlo, whi = e8[0] - e1[1], e8[1] - e1[0]
            W[(lat, r)] = (wlo, whi, d)
            rows.append(row("W_MEASURED", lattice=lat, r=r, W_lo=frac(wlo, d), W_hi=frac(whi, d),
                            W_lo_dec=dec(wlo, d, 12, False), W_hi_dec=dec(whi, d, 12, True),
                            W_width_dec=dec(whi - wlo, d, 12, True)))
    for lat, r in GL3_POINTS:
        a, b = W.get((lat, r)), W.get((lat, 3 * r))
        if a is None or b is None or b[0] <= 0 or a[0] <= 0:
            rows.append(row("GL3_MEASURED", lattice=lat, r=r, status="NOT_MEASURED", reason="W_missing_or_nonpositive"))
            continue
        rlo = (a[0], b[1])
        rhi = (a[1], b[0])
        rows.append(row("GL3_MEASURED", lattice=lat, r=r, rho="W(r)/W(3r)", rho_lo=frac(*rlo), rho_hi=frac(*rhi),
                        rho_lo_dec=dec(rlo[0], rlo[1], 6, False), rho_hi_dec=dec(rhi[0], rhi[1], 6, True),
                        L_min=L_MIN[lat]))
    body = "\n".join(rows) + "\n"
    h = hashlib.sha256(body.encode()).hexdigest()
    text = body + row("MEASURE_BLOCK_SHA256", sha256=h, rows=len(rows)) + "\n"
    OUT.write_text(text)
    (HERE / "MEASURE-GLOBAL-LOCK.hbp.sha256").write_text(hashlib.sha256(text.encode()).hexdigest()
                                                          + "  MEASURE-GLOBAL-LOCK.hbp\n")
    print(text, end="")


def parse_frac(s):
    n, d = s.split("/")
    return int(n), int(d)


def le(a, b):  # a <= b for fractions
    return a[0] * b[1] <= b[0] * a[1]


def verdict(lo, hi, plo, phi):
    """lo/hi: enclosure ends (hi may be None = +inf); plo/phi: frozen interval."""
    if hi is not None and le(plo, lo) and le(hi, phi):
        return "MET"
    if (hi is not None and not le(plo, hi)) or not le(lo, phi):
        return "MISS"
    return "NOT_RESOLVED"


def compare():
    text = OUT.read_text()
    lines = text.splitlines()
    if not lines[-1].startswith("MEASURE_BLOCK_SHA256|") or "VERDICT" in text:
        fail("measured_block_present_and_uncompared")
    body = "\n".join(lines[:-1]) + "\n"
    want = lines[-1].split("sha256=")[1].split("|")[0]
    if hashlib.sha256(body.encode()).hexdigest() != want:
        fail("measured_block_hash")
    fz = FROZEN.read_bytes()
    out = [row("COMPARE_BEGIN", measured_block_sha256=want,
               frozen_file="docs/PREDICTION-GLOBAL-LOCK-20261110.hbp",
               frozen_sha256=hashlib.sha256(fz).hexdigest())]
    if hashlib.sha256(fz).hexdigest() != "93350dd41e7d8817647ccefa3d7ac6cf890bf09ef694c0037f1f9681f41ff738":
        fail("frozen_file_hash")
    for s in lines:
        f = dict(it.split("=", 1) for it in s.split("|")[1:] if "=" in it)
        if s.startswith("GL1_MEASURED|"):
            r = int(f["r"])
            plo, phi = (21, 1), (21 * r + 64, r)
            if "c_hat_lo" not in f:
                out.append(row("VERDICT", row="GL1", lattice=f["lattice"], r=r, frozen="[21,21+64/r]",
                               verdict="NOT_MEASURED", reason=f.get("reason", "")))
                continue
            lo = parse_frac(f["c_hat_lo"])
            hi = None if f["c_hat_hi"] == "NONE" else parse_frac(f["c_hat_hi"])
            out.append(row("VERDICT", row="GL1", lattice=f["lattice"], r=r, frozen="[21," + frac(*phi) + "]",
                           measured="[" + f["c_hat_lo_dec"] + "," + f["c_hat_hi_dec"] + "]",
                           verdict=verdict(lo, hi, plo, phi)))
        if s.startswith("GL3_MEASURED|"):
            lm = L_MIN[f["lattice"]]
            p = 1
            for _ in range(lm - 1):
                p *= 3
            plo, phi = (2 * p, 3), (3 * p, 2)
            if "rho_lo" not in f:
                out.append(row("VERDICT", row="GL3", lattice=f["lattice"], r=int(f["r"]), verdict="NOT_MEASURED",
                               reason=f.get("reason", "")))
                continue
            lo, hi = parse_frac(f["rho_lo"]), parse_frac(f["rho_hi"])
            out.append(row("VERDICT", row="GL3", lattice=f["lattice"], r=int(f["r"]),
                           frozen="[" + frac(*plo) + "," + frac(*phi) + "]",
                           measured="[" + f["rho_lo_dec"] + "," + f["rho_hi_dec"] + "]",
                           verdict=verdict(lo, hi, plo, phi)))
    fl = fz.decode().splitlines()
    for gid in ("GL1", "GL3"):
        hit = [s for s in fl if s.startswith("GLOBAL_LOCK_PREDICT|id=" + gid + "|")]
        if len(hit) != 1:
            fail("frozen_row_present_" + gid)
        out.append(row("FROZEN_ROW_BIND", id=gid, row_sha256=hashlib.sha256(hit[0].encode()).hexdigest(),
                       interval_read_after_snapshot=("[21,21+64/r]" if gid == "GL1" else
                                                     "[(2/3)*3^(L_min-1),(3/2)*3^(L_min-1)]")))
    out.append(row("VERDICT", row="GL3", lattice="4x4", r="27,81", verdict="NOT_MEASURED",
                   reason="4x4_not_authorized_in_this_stage_(GPT-6_review_comment_6767187945)"))
    out.append(row("VERDICT", row="GL2", lattice="3x4,4x4,5x5,6x6", r=9, verdict="NOT_MEASURED",
                   reason="GL2_not_authorized_in_this_stage_(GPT-6_review_comment_6767187945)"))
    vb = "\n".join(out) + "\n"
    full = text + vb + row("VERDICT_BLOCK_SHA256", sha256=hashlib.sha256(vb.encode()).hexdigest()) + "\n"
    OUT.write_text(full)
    (HERE / "MEASURE-GLOBAL-LOCK.hbp.sha256").write_text(hashlib.sha256(full.encode()).hexdigest()
                                                          + "  MEASURE-GLOBAL-LOCK.hbp\n")
    print(vb, end="")


if __name__ == "__main__":
    if sys.argv[1:] == ["measure"]:
        measure()
    elif sys.argv[1:] == ["compare"]:
        compare()
    else:
        fail("usage")
