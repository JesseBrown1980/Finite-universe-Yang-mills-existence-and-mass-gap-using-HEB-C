# Runs a script with every ** and / replaced by a checked call. Reports per-site exponent ranges.
import ast, sys, runpy, io, os
SITES = {}
def _p(a, b, line):
    s = SITES.setdefault(line, [0, None, None, 0])
    s[0] += 1
    if not (type(a) is int and type(b) is int): s[3] += 1
    elif b < 0: s[3] += 1
    if type(b) is int:
        s[1] = b if s[1] is None else min(s[1], b); s[2] = b if s[2] is None else max(s[2], b)
    r = a ** b
    if type(r) is not int: s[3] += 1
    return r
def _d(a, b, line):
    SITES.setdefault(-line, [0, None, None, 0])[3] += 1
    return a / b
class T(ast.NodeTransformer):
    n = 0
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, (ast.Pow, ast.Div)):
            T.n += isinstance(node.op, ast.Pow)
            f = "_p" if isinstance(node.op, ast.Pow) else "_d"
            return ast.copy_location(ast.Call(ast.Name(f, ast.Load()), [node.left, node.right, ast.Constant(node.lineno)], []), node)
        return node
    def visit_AugAssign(self, node):
        self.generic_visit(node)
        assert not isinstance(node.op, (ast.Pow, ast.Div)), "augmented pow/div at %d" % node.lineno
        return node
path = sys.argv[1]; sys.argv = sys.argv[1:]
tree = ast.fix_missing_locations(T().visit(ast.parse(open(path, encoding="utf-8").read(), path)))
g = {"__name__": "__main__", "__file__": path, "_p": _p, "_d": _d}
code = 0
try:
    exec(compile(tree, path, "exec"), g)
except SystemExit as e:
    code = e.code or 0
bad = sum(v[3] for v in SITES.values())
neg = [k for k, v in SITES.items() if v[1] is not None and v[1] < 0]
sys.stderr.write("POWTRACE|file=%s|static_pow_sites=%d|lines_executed=%d|pow_calls=%d|min_exp=%s|bad=%d|neg_lines=%s|exit=%s|json=0\n" % (
    os.path.basename(path), T.n, len(SITES), sum(v[0] for v in SITES.values()), min([v[1] for v in SITES.values() if v[1] is not None] or [None]), bad, neg or "none", code))
