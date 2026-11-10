#!/usr/bin/env python3
"""Planted-fault tests for the acceptance gates in gl_accept.py.  Integer only, json=0.

Every planted fault must make its gate stop with FAILED|check=<the name fixed below>
and a non-zero exit; every clean input must pass.  The faults are the ones the
independent refuter planted in gl_measure.py (reviews/opus55-gl159-refute-20261110/plant.py):
the same text replacements, applied here to a temporary copy of the current script.

usage:
  gl_accept_plants.py fast WORKDIR
      module-grain plants run live on 3x3 (P2max under-reported, floor raised, one
      M4 -> M>=6 edge dropped), the refuter's filed plant outputs, the electric sign plant
  gl_accept_plants.py levels WORKDIR INDEP_ROWS_3x3_r729
      live level-index plants on 3x3 at r=729, where no on-file anchor exists:
      E7 reported as E8, E10 reported as E9; needs indep_gl.py rows for 3x3 r=729
Rows to stdout; exit 1 if any row is NOT_AS_EXPECTED.
"""
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REVIEW = HERE.parents[2].joinpath("reviews", "opus55-gl159-refute-20261110")
GATE = str(HERE.joinpath("gl_accept.py"))

PLANTS = {
    "clean": [],
    "p2_95": [('    emit("FLOOR_INPUTS", m4_orbits',
               '    p2 = p2 * 95 // 100  # PLANT\n    emit("FLOOR_INPUTS", m4_orbits')],
    "floor105": [("    return lo  # fl = lo / FD", "    return lo * 105 // 100  # PLANT")],
    "drop_edge": [("            v = tuple(self.lat.neighbors(key).items())\n",
                   "            v = tuple(self.lat.neighbors(key).items())\n"
                   "            if not getattr(self, '_dropped', False) and self.m(key) == 4:\n"
                   "                for ii, (xx, cc) in enumerate(v):\n"
                   "                    if self.m(xx) >= 6:\n"
                   "                        v = v[:ii] + v[ii + 1:]\n"
                   "                        self._dropped = True\n"
                   "                        break\n")],
    "e8_as_e7": [('for lvl, j in (("E1", 1), ("E8", 8)):', 'for lvl, j in (("E1", 1), ("E8", 7)):')],
    "e9_as_e10": [("hi9 = bisect_upper(evC, 9,", "hi9 = bisect_upper(evC, 10,"),
                  ("lo9 = bisect_lower(evC, 9,", "lo9 = bisect_lower(evC, 10,")],
}
BAD = [0]


def emit(label, **f):
    print(label + "|" + "|".join(str(k) + "=" + str(v) for k, v in f.items()) + "|json=0", flush=True)


def make(work, name):
    d = Path(work).joinpath("plant-" + name)
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    shutil.copyfile(HERE.joinpath("gl_core.py"), d.joinpath("gl_core.py"))
    text = HERE.joinpath("gl_measure.py").read_text()
    for old, new in PLANTS[name]:
        if text.count(old) != 1:
            emit("PLANT", name=name, result="NOT_AS_EXPECTED", reason="plant_text_found_" + str(text.count(old)) + "_times")
            raise SystemExit(1)
        text = text.replace(old, new)
    d.joinpath("gl_measure.py").write_text(text)
    return d


def first_failed(stdout):
    for ln in stdout.splitlines():
        if ln.startswith("FAILED|check="):
            return ln.split("|")[1][6:]
    return "NONE"


def expect(name, grain, argv, want):
    p = subprocess.run([sys.executable, "-I", "-B", GATE] + [str(v) for v in argv], capture_output=True, text=True)
    got = first_failed(p.stdout)
    ok = got == want and (p.returncode != 0) == (want != "NONE")
    BAD[0] += 0 if ok else 1
    emit("PLANT", name=name, grain=grain, gate=argv[0], expect_check=want, observed_check=got,
         exit_code=p.returncode, stdout_sha256=hashlib.sha256(p.stdout.encode()).hexdigest(),
         result="CAUGHT_BY_NAME" if (ok and want != "NONE") else ("CLEAN_PASSED" if ok else "NOT_AS_EXPECTED"))
    if not ok:
        sys.stdout.write(p.stdout[-3000:])
        sys.stderr.write(p.stderr[-3000:])


def fast(work):
    emit("PLANTS_BEGIN", mode="fast", gate_sha256=hashlib.sha256(Path(GATE).read_bytes()).hexdigest(),
         script_sha256=hashlib.sha256(HERE.joinpath("gl_measure.py").read_bytes()).hexdigest())
    expect("electric_clean", "identity", ["electric"], "NONE")
    expect("electric_sign_flipped", "identity", ["electric", "sign=-1"], "accept_electric_link_spectrum_0_3_6")
    for name, want in (("clean", "NONE"),
                       ("p2_95", "accept_P2max_equals_independent_recount"),
                       ("floor105", "accept_floor_at_most_certified_value"),
                       ("drop_edge", "accept_m4_exterior_edges_complete")):
        expect(name, "live_module_3x3", ["module", make(work, name), "3x3"], want)
    pl = REVIEW.joinpath("plant")
    i243 = REVIEW.joinpath("indep", "i-3x3-r243.rows")
    i729 = REVIEW.joinpath("indep", "i-3x3-r729.rows")
    for name, ind, want in (("clean_3x3_r243", i243, "NONE"),
                            ("p2_95_3x3_r243", i243, "accept_P2max_equals_independent_recount"),
                            ("floor105_3x3_r243", i243, "accept_floor_at_most_certified_value"),
                            ("clean_3x3_r729", i729, "NONE"),
                            ("e8_as_e7_3x3_r729", i729, "accept_level_index_E8"),
                            ("e9_as_e10_3x3_r729", i729, "accept_level_index_E9")):
        expect(name, "filed_plant_output", ["receipt", "3x3", pl.joinpath(name + ".rows"), ind], want)
    expect("clean_3x3_r243_against_itself", "filed_plant_output",
           ["replay", pl.joinpath("clean_3x3_r243.rows"), pl.joinpath("clean_3x3_r243.rows")], "NONE")
    expect("drop_edge_3x3_r243", "filed_plant_output",
           ["replay", pl.joinpath("clean_3x3_r243.rows"), pl.joinpath("drop_edge_3x3_r243.rows")],
           "accept_replay_computational_rows_equal")


def levels(work, indep_rows):
    emit("PLANTS_BEGIN", mode="levels", gate_sha256=hashlib.sha256(Path(GATE).read_bytes()).hexdigest(),
         script_sha256=hashlib.sha256(HERE.joinpath("gl_measure.py").read_bytes()).hexdigest(),
         indep_rows_sha256=hashlib.sha256(Path(indep_rows).read_bytes()).hexdigest())
    names = (("clean", "NONE"), ("e8_as_e7", "accept_level_index_E8"), ("e9_as_e10", "accept_level_index_E9"))
    procs = []
    for name, want in names:
        d = make(work, name)
        out = d.joinpath("levels-3x3-r729.rows")
        fh = open(out, "w")
        procs.append((name, want, out, fh, subprocess.Popen(
            [sys.executable, "-I", "-B", str(d.joinpath("gl_measure.py")), "3x3", "729", "kf=1"], stdout=fh)))
    for name, want, out, fh, p in procs:
        rc = p.wait()
        fh.close()
        emit("PLANT_RUN", name=name, lattice="3x3", r=729, own_checks_exit_code=rc,
             own_checks_first_failed=first_failed(out.read_text()),
             rows_sha256=hashlib.sha256(out.read_bytes()).hexdigest())
        expect(name, "live_levels_3x3_r729", ["receipt", "3x3", out, indep_rows], want)


def main():
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "fast":
        fast(a[1])
    elif len(a) == 3 and a[0] == "levels":
        levels(a[1], a[2])
    else:
        emit("FAILED", check="usage")
        raise SystemExit(1)
    emit("PLANTS_END", mode=a[0], not_as_expected=BAD[0], result="PASS" if BAD[0] == 0 else "FAIL")
    raise SystemExit(1 if BAD[0] else 0)


if __name__ == "__main__":
    main()
