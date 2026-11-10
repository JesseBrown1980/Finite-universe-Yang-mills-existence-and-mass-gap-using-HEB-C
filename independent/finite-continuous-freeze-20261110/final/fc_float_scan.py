# FC assembly seat: token scan of python sources for float division, float literals and banned modules.
# Run: python3 -I -B fc_float_scan.py <file> [<file> ...]
import sys
import io
import tokenize

BAN = ("float", "math", "fractions", "decimal", "Fraction", "Decimal")
for path in sys.argv[1:]:
    src = open(path).read()
    bad = []
    for t in tokenize.generate_tokens(io.StringIO(src).readline):
        if t.type == tokenize.OP and t.string in ("/", "/="):
            bad.append("%d:%s" % (t.start[0], t.string))
        if t.type == tokenize.NUMBER and any(c in t.string for c in ".eEjJ") and not t.string.lower().startswith("0x"):
            bad.append("%d:%s" % (t.start[0], t.string))
        if t.type == tokenize.NAME and t.string in BAN:
            bad.append("%d:%s" % (t.start[0], t.string))
    print("FLOAT_SCAN|file=%s|hits=%d|detail=%s|json=0" % (path.split("/")[-1], len(bad), ",".join(bad) or "none"))
