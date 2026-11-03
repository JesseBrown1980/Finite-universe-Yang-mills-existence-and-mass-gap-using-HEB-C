# Runs a script with every true division checked. A division that gives a float stops the run with exit 3, and at the end a row counts the divisions by the type they gave.
# It answers one question by running: are the / in these scripts exact? The script itself runs unchanged, so its own rows must read the same as without this.
# usage: checked_division.py SCRIPT [ARGS...]    Integer only, json=0.
import ast
import atexit
import operator
import os
import sys

COUNTS = {}


def check(left, right):
    result = operator.truediv(left, right)
    kind = type(result).__name__
    COUNTS[kind] = COUNTS.get(kind, 0) + 1
    if isinstance(result, (float, complex)):
        print("CHECKED_DIVISION_FLOAT|left=%r|right=%r|json=0" % (left, right), file=sys.stderr, flush=True)
        os._exit(3)
    return result


class Rewrite(ast.NodeTransformer):
    def __init__(self):
        self.sites = 0

    def call(self, left, right, like):
        self.sites += 1
        return ast.copy_location(ast.Call(ast.Name("__checked_division__", ast.Load()), [left, right], []), like)

    def visit_BinOp(self, node):
        self.generic_visit(node)
        return self.call(node.left, node.right, node) if isinstance(node.op, ast.Div) else node

    def visit_AugAssign(self, node):
        self.generic_visit(node)
        if not isinstance(node.op, ast.Div):
            return node
        read = ast.parse(ast.unparse(node.target), mode="eval").body
        return ast.copy_location(ast.Assign([node.target], self.call(read, node.value, node)), node)


script = sys.argv[1]
tree = ast.parse(open(script, encoding="utf-8").read())
rewrite = Rewrite()
tree = rewrite.visit(tree)
ast.fix_missing_locations(tree)
sys.argv = sys.argv[1:]
sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
atexit.register(lambda: print("CHECKED_DIVISION|script=%s|sites=%d|by_type=%s|float=%d|json=0" % (os.path.basename(script), rewrite.sites, ",".join("%s:%d" % (k, COUNTS[k]) for k in sorted(COUNTS)), COUNTS.get("float", 0)), flush=True))
namespace = {"__name__": "__main__", "__file__": script, "__checked_division__": check}
exec(compile(tree, script, "exec"), namespace)
