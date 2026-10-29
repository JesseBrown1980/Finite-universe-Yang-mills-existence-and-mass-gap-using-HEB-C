#!/usr/bin/env python3
"""Equivalence of schur_record_compare_stream.py with schur_record_compare.py (v2): both tools
on every synthetic control case, then on any real (shell, room) evidence pairs given, must give
byte-identical stdout and the same exit code. Integer-only, json=0.
Every case is run twice: stream vs v2, and stream --v1 vs the frozen v1 file (`--v1-file`).
usage: schur_record_compare_stream_controls.py --v1-file V1.py [SHELL ROOM ...]
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import schur_record_compare_controls as ctl  # noqa: E402

V2 = os.path.join(HERE, "schur_record_compare.py")
ST = os.path.join(HERE, "schur_record_compare_stream.py")


def run(tool, args):
    r = subprocess.run([sys.executable, tool] + args, capture_output=True, text=True)
    return r.stdout, r.returncode


V1 = None


def check(name, args):
    ok_all = True
    for label, ref, st_args in (("v2", V2, args), ("v1", V1, ["--v1"] + args)):
        o2, c2 = run(ref, args)
        os_, cs = run(ST, st_args)
        ok = o2 == os_ and c2 == cs
        ok_all &= ok
        verdict = o2.strip().splitlines()[-1].split("|")[2] if o2.strip() else "-"
        print("STREAM_EQUIV|case=%s|ref=%s|ref_exit=%d|stream_exit=%d|ref_verdict=%s|stdout_identical=%d|ok=%d|json=0"
              % (name, label, c2, cs, verdict, o2 == os_, ok))
    return ok_all


def main(argv):
    global V1
    if len(argv) < 2 or argv[0] != "--v1-file":
        raise SystemExit("usage: schur_record_compare_stream_controls.py --v1-file V1.py [SHELL ROOM ...]")
    V1, argv = argv[1], argv[2:]
    oks = []
    for name, a, b, _want in ctl.CASES:
        d = tempfile.mkdtemp(prefix="sce_")
        pa, pb = os.path.join(d, "shell.txt"), os.path.join(d, "room.txt")
        open(pa, "w").write(a)
        if b is not None:
            open(pb, "w").write(b)
        oks.append(check(name, [pa, pb]))
        # swapped sides and a shell-side malformation must also match
        oks.append(check(name + "_swapped", [pb, pa]))
    S, C = ctl.SUM, ctl.COL
    many = [(cb, ca, cb * 7 + ca) for cb in (0, 1, 2, 9, 10, 11) for ca in (0, 1, 9, 10)]
    alt = [(cb, ca, h + (1 if (cb, ca) in {(10, 0), (9, 1), (2, 10), (11, 9)} else 0)) for cb, ca, h in many]
    extra = [
        ("many_field_diffs_string_order", ctl.text(many), ctl.text(alt)),
        ("keys_and_fields_differ", ctl.text(many), ctl.text([r for r in alt if r[:2] != (0, 0)] + [(99, 99, 1)])),
        ("summary_and_records_differ", ctl.text(many), ctl.text(alt, ("rooms", 8, 2))),
        ("room_dup_after_mismatches", ctl.text(many), ctl.text(alt) + C % (0, 1, 5) + "\n"),
        ("room_late_summary_dup", ctl.text(many), ctl.text(many) + S % ("x", 9, 1) + "\n"),
        ("only_room_records", ctl.text([]), ctl.text(many)),
        ("only_shell_records", ctl.text(many), ctl.text([])),
        ("extra_field_one_side", ctl.text(many), ctl.text(many).replace("|sweeps=7|", "|sweeps=7|extra=1|", 1)),
        ("value_with_equals", ctl.text(many).replace("|lo=-5|", "|lo=a=b|", 1), ctl.text(many).replace("|lo=-5|", "|lo=a=c|", 1)),
    ]
    for name, a, b in extra:
        d = tempfile.mkdtemp(prefix="sce_")
        pa, pb = os.path.join(d, "shell.txt"), os.path.join(d, "room.txt")
        open(pa, "w").write(a)
        open(pb, "w").write(b)
        oks.append(check(name, [pa, pb]))
        oks.append(check(name + "_swapped", [pb, pa]))
    for i in range(0, len(argv) - 1, 2):
        oks.append(check("real_" + os.path.basename(argv[i]), argv[i:i + 2]))
    n = sum(oks)
    print("STREAM_EQUIV_TOTAL|cases=%d|ok=%d|result=%s|json=0" % (len(oks), n, "PASS" if n == len(oks) else "FAIL"))
    sys.exit(0 if n == len(oks) else 2)


if __name__ == "__main__":
    main(sys.argv[1:])
