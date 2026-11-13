R = "/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/"
def patch(rel, pairs):
    p = R + rel
    s = open(p, "rb").read().decode("utf-8")
    assert "\r" not in s
    for old, new in pairs:
        assert s.count(old) == 1, (rel, old[:60], s.count(old))
        s = s.replace(old, new)
    open(p, "wb").write(s.encode("utf-8"))
    print("patched", rel)

patch("work/design/gate_required.sh", [
    ("# Usage: gate_required.sh CERT [--freeze-commit C --prediction FILE --prediction-sha256 H]   (the last three only at r = 9)\n",
     "# Usage: gate_required.sh CERT [--freeze-commit C --prediction FILE --prediction-sha256 H]   (the last three only at r = 9)\n"
     "# V2 (2026-11-10): D is the directory that holds this script (work/design of the package), at any absolute location.\n"),
    ("D=/tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/floor/work/design\n",
     "D=$(cd \"$(dirname \"${BASH_SOURCE[0]}\")\" && pwd -P)\n"),
])
patch("final/tools/r_scan.sh", [
    ("# are named on stderr only; each needs its own DISCLOSE row and a place in the list.\n",
     "# are named on stderr only; each needs its own DISCLOSE row and a place in the list.\n"
     "# V2 (2026-11-10): F is the package root, two levels above this script (final/tools/), at any absolute location.\n"),
    ("F=/tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/floor\n",
     "F=$(cd \"$(dirname \"${BASH_SOURCE[0]}\")/../..\" && pwd -P)\n"),
])
