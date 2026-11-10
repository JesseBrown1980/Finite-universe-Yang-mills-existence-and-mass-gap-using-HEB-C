# Runs a script with every ** replaced by a counting call. Each call is counted once in each class it belongs to.
import ast, sys, os
N = {}
def _p(a, b, line):
    s = N.setdefault(line, [0, 0, 0, 0, None])
    s[0] += 1
    if not (type(a) is int and type(b) is int): s[1] += 1
    if type(b) is int:
        if b < 0: s[2] += 1
        s[4] = b if s[4] is None else min(s[4], b)
    r = a ** b
    if type(r) is not int: s[3] += 1
    return r
class T(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Pow):
            return ast.copy_location(ast.Call(ast.Name("_p", ast.Load()), [node.left, node.right, ast.Constant(node.lineno)], []), node)
        return node
    def visit_AugAssign(self, node):
        self.generic_visit(node)
        assert not isinstance(node.op, ast.Pow), "augmented power at %d" % node.lineno
        return node
path = sys.argv[1]; sys.argv = sys.argv[1:]
tree = ast.fix_missing_locations(T().visit(ast.parse(open(path, encoding="utf-8").read(), path)))
code = 0
try:
    exec(compile(tree, path, "exec"), {"__name__": "__main__", "__file__": path, "_p": _p})
except SystemExit as e:
    code = e.code or 0
tot = [sum(v[i] for v in N.values()) for i in range(4)]
mins = [v[4] for v in N.values() if v[4] is not None]
sys.stderr.write("POWTRACE2|file=%s|pow_calls=%d|non_integer_operand_calls=%d|negative_exponent_calls=%d|non_integer_result_calls=%d|min_exp=%s|lines_with_non_integer_result=%s|exit=%s|json=0\n" % (
    os.path.basename(path), tot[0], tot[1], tot[2], tot[3], min(mins) if mins else None, sorted(k for k, v in N.items() if v[3]) or "none", code))
