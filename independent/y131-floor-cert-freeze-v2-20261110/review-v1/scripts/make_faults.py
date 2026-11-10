# Opus 5.5 planted faults on the r = 12, m0 = 7 smoke certificate (excluded r). Integers only.
import sys
src, outdir = sys.argv[1], sys.argv[2]
lines = open(src).read().split("\n")
hdr, rows = lines[0], [l for l in lines[1:] if l.strip()]
def write(name, h, rs):
    open("%s/%s.txt" % (outdir, name), "w").write("\n".join([h] + rs) + "\n")
# F1: double the v of the class with the largest v (a single-entry vector forgery)
vals = [tuple(map(int, l.split())) for l in rows]
imax = max(range(len(vals)), key=lambda i: vals[i][2])
f1 = list(rows)
k, M, v = vals[imax]
f1[imax] = "%d %d %d" % (k, M, 2 * v)
write("F1_one_v_doubled", hdr, f1)
# F2: claimed t raised to 1048641/10000, above the writer's own Ritz upper bound 104.854117 (a false floor)
write("F2_t_above_ritz", hdr.replace("t=1042273/10000", "t=1048641/10000"), rows)
# F3: v values of the two lowest-M classes swapped (keys kept, a misbinding of vector to classes)
order = sorted(range(len(vals)), key=lambda i: (vals[i][1], vals[i][0]))
a, b = order[0], order[1]
f3 = list(rows)
f3[a] = "%d %d %d" % (vals[a][0], vals[a][1], vals[b][2])
f3[b] = "%d %d %d" % (vals[b][0], vals[b][1], vals[a][2])
write("F3_v_swapped_lowM", hdr, f3)
print("FAULTS|F1_row=%d|F3_rows=%d,%d|json=0" % (imax, a, b))
