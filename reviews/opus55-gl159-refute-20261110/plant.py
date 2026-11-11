#!/usr/bin/env python3
"""Make planted-fault copies of the PR's gl_measure.py (the PR's own checks must catch them)."""
import sys, shutil, pathlib
src = pathlib.Path("/root/gl159/repo/independent/global-lock-20261110/measure")
dst = pathlib.Path("/root/gl159/plant")
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)
base = (dst / "gl_measure.py").read_text()
P = {}
# F1: floor claimed 5% higher (tighter) than the Schur-test lemma certifies
P["floor105"] = base.replace("    return lo  # fl = lo / FD", "    return lo * 105 // 100  # PLANT: 5% above the certified floor")
# F1b: input-level fault, P2max under-reported by 5%
P["p2_95"] = base.replace("    emit(\"FLOOR_INPUTS\", m4_orbits", "    p2 = p2 * 95 // 100  # PLANT\n    emit(\"FLOOR_INPUTS\", m4_orbits")
# F2: one exterior edge dropped from the electric neighbour map (first M4 state that has an M>=6 neighbour)
P["drop_edge"] = base.replace(
    "            v = tuple(self.lat.neighbors(key).items())\n",
    "            v = tuple(self.lat.neighbors(key).items())\n"
    "            if not getattr(self, '_dropped', False) and self.m(key) == 4:\n"
    "                for ii, (xx, cc) in enumerate(v):\n"
    "                    if self.m(xx) >= 6:\n"
    "                        v = v[:ii] + v[ii + 1:]\n"
    "                        self._dropped = True\n"
    "                        break\n")
# F3: wrong level index, E8 bisected as the 7th level
P["e8_as_e7"] = base.replace('for lvl, j in (("E1", 1), ("E8", 8)):', 'for lvl, j in (("E1", 1), ("E8", 7)):')
# F3b: E9 bisected as the 10th level
P["e9_as_e10"] = base.replace("hi9 = bisect_upper(evC, 9,", "hi9 = bisect_upper(evC, 10,").replace("lo9 = bisect_lower(evC, 9,", "lo9 = bisect_lower(evC, 10,")
for k, s in P.items():
    assert s != base, k
    (dst / ("gl_measure_" + k + ".py")).write_text(s)
print("planted", ",".join(P))
