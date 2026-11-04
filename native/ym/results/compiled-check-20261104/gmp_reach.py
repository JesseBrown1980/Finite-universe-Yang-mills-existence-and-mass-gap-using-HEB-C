# Which members of libgmp.a and libgmpxx.a a verifier's assembly reaches by symbol, and which of those hold a floating-point opcode. Read from nm and objdump on a copy of the distribution's libgmp-dev. Integer only, json=0.
# usage: gmp_reach.py LIB_DIR FILE.s [FILE.s ...]
import collections
import re
import subprocess
import sys

LIBDIR = sys.argv[1]
FILES = sys.argv[2:]
OP = re.compile(r"^\s*[0-9a-f]+:\s+(?:(?:v?(?:add|sub|mul|div|sqrt|min|max|ucomi|comi|cmp[a-z]*)s[sd])|v?cvt\w+|f(?:ld|st|add|sub|mul|div|sqrt|ild|ist|xch|chs|abs|com|ucom)\w*)\b")
defined = {}
undef = collections.defaultdict(set)
fp = collections.Counter()
for lib in ("libgmp.a", "libgmpxx.a"):
    path = LIBDIR + "/" + lib
    member = None
    for line in subprocess.run(["nm", path], capture_output=True, text=True).stdout.splitlines():
        if line.endswith(":") and not line.startswith(" "):
            member = lib + ":" + line[:-1]
            continue
        parts = line.split()
        if len(parts) == 3 and parts[1] in "TtDdRrBbVWGSA":
            defined.setdefault(parts[2], member)
        elif len(parts) == 2 and parts[0] == "U":
            undef[member].add(parts[1])
    member = None
    for line in subprocess.run(["objdump", "-d", "--no-show-raw-insn", path], capture_output=True, text=True).stdout.splitlines():
        m = re.match(r"^(\S+\.o):\s+file format", line)
        if m:
            member = lib + ":" + m.group(1)
        elif member and OP.match(line):
            fp[member] += 1
seen = set()
frontier = []
for f in FILES:
    text = open(f, encoding="utf-8", errors="replace").read()
    called = set(re.findall(r"\bcall\s+(__g\w+|_Z\w*gmp\w*)", text))
    hits = sorted(x.split("@")[0] for x in called)
    print("GMP_CALLED|file=%s|symbols=%d|first=%s|json=0" % (f.rsplit("/", 1)[1], len(hits), ",".join(hits[:12])))
    for s in hits:
        if s in defined:
            frontier.append(defined[s])
while frontier:
    x = frontier.pop()
    if x in seen:
        continue
    seen.add(x)
    for u in undef.get(x, ()):
        if u in defined:
            frontier.append(defined[u])
total = sum(1 for k in defined.values())
hit = sorted((k, fp[k]) for k in seen if fp[k])
print("GMP_REACH|members_in_libs=%d|members_with_fp_ops=%d|members_reached=%d|reached_with_fp_ops=%d|json=0" % (len(set(defined.values())), sum(1 for k in fp if fp[k]), len(seen), len(hit)))
for k, n in hit:
    print("GMP_REACHED_FP|member=%s|fp_ops=%d|json=0" % (k, n))
