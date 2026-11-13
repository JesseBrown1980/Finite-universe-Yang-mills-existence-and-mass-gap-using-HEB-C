#!/usr/bin/env python3
"""lighthouse_prompt_v2.py -- SIDE TEST. The lighthouse is the prompt; the matrix is the frozen leaf field.

Operator, 2026-11-12: "the lighthouse is something that you use in your matrix ... imagine that the lighthouse
is the prompt and you send it into your matrix."

The matrix stays frozen (Law 15). The beam is what moves: from every centre row it reaches out at three shell
radii r = 1, 2, 3 (Law 36: inner, medium, outer) and asks the trijection question (Laws 1, 21, 48): do the two
rows at distance r and the centre CLOSE, i.e. sum to zero, at ternary level 3, 9, 27 (Law 71.11 ladder)?
Anchor two, the third is determined: a closing triple is one whose third member is the one the other two fix.

Exact integers only. Controls (Law 71.6 / Law 7): the same values with the row order shuffled (27 runs), and
random values of the same bit length (27 runs). Chance rate for independent values is 1/3, 1/9, 1/27.
  python lighthouse_prompt_v2.py <leaf_file> <field: slack|v>
"""
import sys


def mixer(seed):
    st = [seed & 0xFFFFFFFFFFFFFFFF]
    def nxt():
        st[0] = (st[0] + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        z = st[0]
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        return z ^ (z >> 31)
    return nxt


rows = []
for line in open(sys.argv[1]):
    if line.startswith("LEAF|"):
        d = dict(w.split("=", 1) for w in line.strip().split("|")[1:] if "=" in w)
        rows.append((int(d["key"]), int(d["M"]), int(d[sys.argv[2]])))
rows.sort()
vals = [x[2] for x in rows]
n = len(vals)
SHELLS, LEVELS = (1, 2, 3), (3, 9, 27)


def closures(v):
    out = {}
    for r in SHELLS:
        for q in LEVELS:
            c = sum(1 for i in range(r, len(v) - r) if (v[i - r] + v[i] + v[i + r]) % q == 0)
            out[(r, q)] = (c, len(v) - 2 * r)
    return out


real = closures(vals)
print("PROMPT|lighthouse=three_shells_r_1_2_3_from_every_centre_row|matrix=frozen_leaf_field_%s_in_key_order|rows=%d|levels=3_9_27|integer_only=1|json=0" % (sys.argv[2], n))
census = [sum(1 for x in vals if x % 3 == k) for k in range(3)]
print("TRANSLUCENT_FIRST|value_mod_3_census_0_1_2=%d_%d_%d|json=0" % tuple(census))
nulls = {"row_shuffle": [], "random_values_same_bit_length": []}
for k in range(27):
    r = mixer(5000 + k)
    a = list(vals)
    for i in range(n - 1, 0, -1):
        j = r() % (i + 1)
        a[i], a[j] = a[j], a[i]
    nulls["row_shuffle"].append(closures(a))
    r = mixer(6000 + k)
    b = []
    for x in vals:
        bl = max(x.bit_length(), 1)
        b.append((((r() << 64) | r()) & ((1 << bl) - 1)) | (1 << (bl - 1)))
    nulls["random_values_same_bit_length"].append(closures(b))
outside = {k: 0 for k in nulls}
for r_ in SHELLS:
    for q in LEVELS:
        c, tot = real[(r_, q)]
        line = "CLOSE|shell_r=%d|level=%d|closing_triples=%d|of=%d|chance_expected=%d" % (r_, q, c, tot, tot // q)
        for name, runs in nulls.items():
            xs = [u[(r_, q)][0] for u in runs]
            v = "OUTSIDE" if (c < min(xs) or c > max(xs)) else "INSIDE"
            outside[name] += v == "OUTSIDE"
            line += "|%s=%d..%d_%s" % (name, min(xs), max(xs), v)
        print(line + "|json=0")
print("SUMMARY|cells=9|" + "|".join("outside_%s=%d" % kv for kv in outside.items()) + "|json=0")
