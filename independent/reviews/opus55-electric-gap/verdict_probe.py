#!/usr/bin/env python3
"""Probes on the builder's script, from my clone. Integer only, json=0.
1. For each prediction id with needles: corrupt its value in a copy of the rows, and read the verdict.
2. A spurious root added to P: does factor_witness catch it?
usage: verdict_probe.py INDEPENDENT_DIR
"""
import importlib.util
import os
import sys


def load(independent):
    spec = importlib.util.spec_from_file_location("electric", os.path.join(independent, "electric_spectrum_2x2.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def corrupt(text):
    # Change the last run of digits in the needle, or append a character if there is none.
    chars = list(text)
    for i in range(len(chars) - 1, -1, -1):
        if chars[i].isdigit():
            chars[i] = str((int(chars[i]) + 1) % 10)
            return "".join(chars)
    return text + "X"


def main(argv):
    electric = load(argv[0])
    lines = electric.read_rows(os.path.join(argv[0], "electric_spectrum_2x2.measure"))
    tally = {}
    wrong = []
    for pid, needles in electric.PREDICTION_NEEDLES.items():
        fields = {"id": pid}
        if electric.verdict_for(fields, lines) != "MET":
            print("VERDICT_PROBE|id=%s|baseline_not_MET|json=0" % pid)
            continue
        target = needles[-1]
        changed = []
        for line in lines:
            if all(n in line for n in needles):
                changed.append(line.replace(target, corrupt(target)))
            else:
                changed.append(line)
        verdict = electric.verdict_for(fields, changed)
        tally[verdict] = tally.get(verdict, 0) + 1
        if verdict != "MISS":
            wrong.append(pid)
    print("VERDICT_PROBE|ids=%d|verdicts=%s|ids_where_a_wrong_value_is_not_MISS=%s|json=0"
          % (len(electric.PREDICTION_NEEDLES), sorted(tally.items()), ",".join(wrong)))

    model = electric.load_gpt6_model()
    rows = [dict(row) for row in model["rows"]]
    e = [sorted(row.items()) for row in rows]
    table, _, _, _, _ = electric.character_table(2, 2, electric.CHARACTERS)
    roots = [c for c in sorted(table) if table[c]]
    spurious = roots + [3]
    electric.check_annihilator(e, spurious)
    witness = electric.factor_witness(e, spurious, 3)
    print("SPURIOUS_ROOT_PROBE|roots=%s|check_annihilator=passes|factor_witness_at_3=%s|json=0"
          % (",".join(map(str, spurious)), witness))
    read_back = electric.multiplicities_from_prefix_traces(roots, [sum(1 for _ in rows)] + [0] * 0 + electric.check_annihilator(e, roots)[1:])
    print("PREFIX_PROBE|table=%s|json=0" % electric.table_text(read_back))


if __name__ == "__main__":
    main(sys.argv[1:])
