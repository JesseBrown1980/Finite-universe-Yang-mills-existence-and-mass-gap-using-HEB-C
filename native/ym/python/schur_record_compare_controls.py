#!/usr/bin/env python3
"""Synthetic controls for schur_record_compare.py. Integer-only, json=0.
usage: schur_record_compare_controls.py
"""
import os
import subprocess
import sys
import tempfile

TOOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schur_record_compare.py")
SUM = ("SHELL_SCHUR|matrix=%s|n=288645|JE=1000|JB=9000|t_milli=90000000|shell_max=-1|core=2940|core_edges=5|H=285705|"
       "H_min_margin=1|H_max_offdiag_over_diag_permille_ceil=990|F=10^12|gs_sweeps_max=19|y_width_max=3|negative=37|"
       "positive_core=2894|positive_H=285705|eliminated=2931|ambiguous=%s|result=AMBIGUOUS|ms=%s|json=0")
COL = "SCOL|n=288645|JE=1000|JB=9000|t_milli=90000000|core=2940|core_fp=abc|F=10^12|cb=%s|ca=%s|lo=-5|hi=%s|sweeps=7|ywidth=2|json=0"
SPL = "SHELL_SCHUR_COLS|n=288645|cols=%s|gs_sweeps_max=%s|y_width_max=2|ms=%s|json=0"
RSPL = "SHELL_SCHUR_COLS|n=288645|cols=%s|gs_sweeps_max=%s|y_width_max=2|room_bytes_per_pass=125825024|pass_ms=9,8|payload_merkle=%s|ms=%s|json=0"


def text(cols, summ=("a.txt", 9, 100), spl=()):
    lines = [COL % c for c in cols] + [SPL % m for m in spl]
    if summ:
        lines.append(SUM % summ)
    return "\n".join(lines) + "\n"


BASE_COLS = [(0, 0, 3), (1, 0, 4)]
CASES = [
    ("identical_ambiguous", text(BASE_COLS), text(BASE_COLS, ("rooms", 9, 999)), "AGREE"),
    ("only_matrix_and_ms_differ", text(BASE_COLS, ("x", 9, 1)), text(BASE_COLS, ("y", 9, 2)), "AGREE"),
    ("summary_field_differs", text(BASE_COLS), text(BASE_COLS, ("rooms", 8, 1)), "MISMATCH"),
    ("scol_value_differs", text(BASE_COLS), text([(0, 0, 3), (1, 0, 5)]), "MISMATCH"),
    ("scol_only_one_side", text(BASE_COLS), text([(0, 0, 3)]), "MISMATCH"),
    ("duplicate_scol_key", text(BASE_COLS), text(BASE_COLS + [(1, 0, 4)]), "INCONCLUSIVE"),
    ("duplicate_scol_key_conflicting", text(BASE_COLS), text(BASE_COLS + [(1, 0, 6)]), "INCONCLUSIVE"),
    ("duplicate_summary", text(BASE_COLS), text(BASE_COLS) + SUM % ("a", 9, 1) + "\n", "INCONCLUSIVE"),
    ("scol_without_key", text(BASE_COLS), text(BASE_COLS) + "SCOL|lo=1|hi=2|json=0\n", "INCONCLUSIVE"),
    ("cols_lines_ms_only", text(BASE_COLS, spl=[("0:2", 7, 1), ("2:4", 7, 2)]),
     text(BASE_COLS, spl=[("2:4", 7, 8), ("0:2", 7, 9)]), "AGREE"),
    ("cols_line_value_differs", text(BASE_COLS, spl=[("0:2", 7, 1)]), text(BASE_COLS, spl=[("0:2", 8, 1)]), "MISMATCH"),
    ("cols_line_only_one_side", text(BASE_COLS, spl=[("0:2", 7, 1), ("2:4", 7, 1)]),
     text(BASE_COLS, spl=[("0:2", 7, 1)]), "MISMATCH"),
    ("duplicate_cols_key", text(BASE_COLS, spl=[("0:2", 7, 1)]),
     text(BASE_COLS, spl=[("0:2", 7, 1), ("0:2", 7, 5)]), "INCONCLUSIVE"),
    ("duplicate_cols_key_shell_side", text(BASE_COLS, spl=[("0:2", 7, 1), ("0:2", 9, 1)]),
     text(BASE_COLS, spl=[("0:2", 7, 1)]), "INCONCLUSIVE"),
    ("room_only_fields_on_room_side", text(BASE_COLS, spl=[("0:2", 7, 1), ("2:4", 7, 2)]),
     text(BASE_COLS) + "".join(RSPL % (c, 7, "m1", 5) + "\n" for c in ("0:2", "2:4")), "AGREE"),
    ("room_payload_merkle_inconsistent", text(BASE_COLS, spl=[("0:2", 7, 1), ("2:4", 7, 2)]),
     text(BASE_COLS) + RSPL % ("0:2", 7, "m1", 5) + "\n" + RSPL % ("2:4", 7, "m2", 5) + "\n", "INCONCLUSIVE"),
    ("room_line_value_differs", text(BASE_COLS, spl=[("0:2", 7, 1)]),
     text(BASE_COLS) + RSPL % ("0:2", 8, "m1", 5) + "\n", "MISMATCH"),
    ("cols_line_without_key", text(BASE_COLS), text(BASE_COLS) + "SHELL_SCHUR_COLS|n=1|ms=3|json=0\n", "INCONCLUSIVE"),
    ("no_summary_truncated", text(BASE_COLS), text(BASE_COLS, None), "INCONCLUSIVE"),
    ("failed_execution", text(BASE_COLS), "SHELL_SCHUR|result=FAIL|reason=x|json=0\n", "INCONCLUSIVE"),
    ("missing_file", text(BASE_COLS), None, "INCONCLUSIVE"),
]


def main():
    ok_all = True
    for name, a, b, want in CASES:
        d = tempfile.mkdtemp(prefix="scc_")
        pa, pb = os.path.join(d, "shell.txt"), os.path.join(d, "room.txt")
        open(pa, "w").write(a)
        if b is not None:
            open(pb, "w").write(b)
        r = subprocess.run([sys.executable, TOOL, pa, pb], capture_output=True, text=True)
        got = r.stdout.strip().splitlines()[-1].split("|")[2]
        if want == "AGREE" or want == "MISMATCH":
            # the excluded raw values must be carried in the evidence line
            ok_ev = "|excluded_shell_ms=" in r.stdout and "|excluded_room_ms=" in r.stdout
        else:
            ok_ev = True
        ok = got == want and ok_ev and (r.returncode == 0) == (want == "AGREE")
        ok_all &= ok
        print("SCHUR_COMPARE_CONTROL|case=%s|want=%s|got=%s|ok=%d|json=0" % (name, want, got, ok))
    print("SCHUR_COMPARE_CONTROLS_TOTAL|cases=%d|result=%s|json=0" % (len(CASES), "PASS" if ok_all else "FAIL"))
    sys.exit(0 if ok_all else 2)


if __name__ == "__main__":
    main()
