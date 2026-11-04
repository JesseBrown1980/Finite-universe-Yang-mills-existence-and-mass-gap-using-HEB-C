#!/usr/bin/env python3
"""
Writes the integer copies of the scripts that used Python's rationals or a floating-point clock. The originals stay as they ran.

Each copy keeps its source's comments and layout. By syntax tree, with the gate's own path-join rule, every numeric true division
a / b becomes qdiv(a , b): the / token becomes a comma, qdiv( goes in at the start of the expression and ) at its end, and x /= y
becomes x = qdiv(x , y). The fractions import becomes intpair, with a sys.path line so the copy finds native/scripts from where it
sits. Every further edit is a text pair in COPIES below, applied first, and must occur exactly as many times as stated.

The rewrite is checked against a second path: the same divisions and import replaced in the syntax tree must dump the same as the
parsed copy. The copy must then read in no_float_gate.py, with the tracked names of the tree at ROOT, the count its row in
FLOAT-EVIDENCE.txt states, or 0 with no row, and 0 hits in integer_only_audit.py. The row's pin is the gate's own check.

usage: make_integer_pairs.py ROOT --write     Writes every copy under the repository at ROOT.
       make_integer_pairs.py ROOT --check     Regenerates every copy and compares bytes with what is there. Exit 1 on a difference.
       make_integer_pairs.py --selftest       Runs the snippets below. Exit 1 if one is misread.
Needs Python 3.12 or later, whose tokenizer and syntax tree see inside f-strings. Integer only, json=0.
"""
import ast
import io
import os
import subprocess
import sys
import tempfile
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import integer_only_audit  # noqa: E402
import no_float_gate  # noqa: E402

P = "native/ym/results/3x4_stream/perron/"
S = P + "second-seat/"
REDO = S + "integer-redo/"
V = P + "vector/"
A = P + "allpairs/failclosed/review-opus55/attack/"
CHAIN = "the output of make_integer_redo.py"


def spec(digits):
    """A float format spec of the old text, spelled in pieces so that this file holds none itself."""
    return ":" + "." + digits + "f}"


def wall(name, *readings):
    """The pairs that move a wall clock to whole seconds on time.monotonic_ns. A reading is (text up to its format spec, digits, count)."""
    pairs = [(name + " = time.time()", name + " = time.monotonic_ns()", 1)]
    for before, digits, count in readings:
        field, expression = before.split("{")
        new = expression.replace(" - ", "-").replace("time.time()", "time.monotonic_ns()")
        pairs.append((before + spec(digits), field + "{(" + new + ")//10**9}", count))
    return pairs


# (source, destination, text pairs). A source of None takes make_integer_redo.py's output for the file named by the destination.
COPIES = (
    (None, REDO + "c2_acc.py", []),
    (None, REDO + "c2_fuzz.py", []),
    (None, REDO + "c3_random.py", []),
    (None, REDO + "c4b_open.py", []),
    (S + "c1_inertia.py", REDO + "c1_inertia.py", wall("t", ("secs_wall={time.time() - t", "1", 1))),
    (S + "c1_small.py", REDO + "c1_small.py", wall("tick", ("|secs={time.time() - tick", "1", 1), ("secs_wall={time.time() - tick", "1", 1))),
    (S + "c4_grid.py", REDO + "c4_grid.py", wall("t0", ("secs_wall={time.time()-t0", "0", 1))),
    (S + "c5_coupling.py", REDO + "c5_coupling.py", wall("t0", ("secs_wall={time.time()-t0", "0", 1))),
    (S + "c6_count.py", REDO + "c6_count.py", wall("t0", ("secs_wall={time.time()-t0", "1", 1), ("secs_wall={time.time()-t0", "0", 2))),
    (S + "c6_lattice.py", REDO + "c6_lattice.py", wall("t0", ("secs_wall={time.time()-t0", "0", 4)) + [
        ('with open(f"{R}/whole{LX}{LY}.pkl", "wb") as f:', 'with open(sys.argv[3], "wb") as f:', 1),
        ("# usage: c6_lattice.py LX LY\n", "# usage: c6_lattice.py LX LY PKL_OUT\n", 1)]),
    (S + "c6_lift.py", REDO + "c6_lift.py", wall("t0", ("secs_wall={time.time()-t0", "0", 2))),
    (S + "c7_receipts.py", REDO + "c7_receipts.py", [
        ('J = "D:/ym-3x4-room-run/p0-ball/jump34/"', 'J = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..") + os.sep', 1),
        ('J + "pass1.out"', 'J + "PASS1-3x4.out"', 1),
        ('J + "grid1.out"', 'J + "GRID1-3x4.out"', 1),
        ("float(r_) if False else str(r_)", "str(r_)", 1)]),
    (S + "own33_check.py", REDO + "own33_check.py", wall("t0", ("secs_wall={time.time()-t0", "0", 1))),
    (S + "own34_post.py", REDO + "own34_post.py", [
        ('R = "C:/tmp/opus55/ym-two-sided"\n', 'HERE = os.path.dirname(os.path.abspath(__file__))\n', 1),
        ('open(f"{R}/own34.out", newline="")', 'open(os.path.join(HERE, "..", "..", "..", "..", "integer-pairs-2026-11-03", "inputs", "own34.out"), newline="")', 1),
        ('open("D:/ym-3x4-room-run/p0-ball/jump34/pass1.out", newline="")', 'open(os.path.join(HERE, "..", "..", "PASS1-3x4.out"), newline="")', 1)]),
    (P + "perron_climb.py", P + "perron_climb_integer.py", [
        ("t0 = time.monotonic()", "t0 = time.monotonic_ns()", 1),
        ("if time.monotonic() - t0 > budget:", "if time.monotonic_ns() - t0 > budget * 10**9:", 1),
        ("secs = int(time.monotonic() - t0)", "secs = (time.monotonic_ns() - t0) // 10**9", 1),
        ("secs={int(time.monotonic() - t0)}", "secs={(time.monotonic_ns() - t0) // 10**9}", 1)]),
    (P + "hash_store.py", P + "hash_store_integer.py", [
        ("t0 = time.time()", "t0 = time.monotonic_ns()", 1),
        ("secs={int(time.time()-t0)}", "secs={(time.monotonic_ns()-t0)//10**9}", 1)]),
    (V + "product_bound.py", V + "integer-pairs/product_bound.py", []),
    (V + "review-gpt6/cap_check.py", V + "review-gpt6/integer-pairs/cap_check.py", [
        ("# Python integers and fractions, json=0.\n", "# Python integers and exact integer pairs, json=0.\n", 1)]),
    (V + "review-opus55/py_exact_t.py", V + "review-opus55/integer-pairs/py_exact_t.py", [
        ("# Python integers and fractions only, json=0.", "# Python integers and exact integer pairs only, json=0.", 1)]),
    (V + "review-opus55/py_two_numbers.py", V + "review-opus55/integer-pairs/py_two_numbers.py", [
        ("exact rationals, json=0.", "exact integer pairs, json=0.", 1)]),
    (V + "review-opus55/py_verify_low.py", V + "review-opus55/integer-pairs/py_verify_low.py", [
        ("Python integers and fractions, json=0.", "Python integers and exact integer pairs, json=0.", 1)]),
    (A + "brute_windows.py", A + "integer-clock/brute_windows.py", [
        ("t0 = time.time()", "t0 = time.monotonic_ns()", 1),
        ("time.time() - t0", "(time.monotonic_ns() - t0) // 10**9", 2)]),
    (A + "reader_controls.py", A + "integer-clock/reader_controls.py", [
        ("t0 = time.time()", "t0 = time.monotonic_ns()", 1),
        ("time.time() - t0", "(time.monotonic_ns() - t0) // 10**9", 2)]),
    (A + "stars.py", A + "integer-clock/stars.py", [
        ("t0 = time.time()", "t0 = time.monotonic_ns()", 1),
        ("time.time() - t0", "(time.monotonic_ns() - t0) // 10**9", 2)]),
    (A + "stars2.py", A + "integer-clock/stars2.py", [
        ("t0 = time.time()", "t0 = time.monotonic_ns()", 1),
        ("time.time() - t0", "(time.monotonic_ns() - t0) // 10**9", 2)]),
)


def path_line(dest, indent):
    """The line that lets a copy at dest import from native/scripts."""
    ups = len(dest.split("/")) - 2  # dest's folders below native, the first of which is native itself
    parts = ", ".join(['".."'] * ups + ['"scripts"'])
    return indent + "import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), %s))\n" % parts


class Positions:
    def __init__(self, text):
        self.lines = text.split("\n")
        self.starts = [0]
        for line in self.lines:
            self.starts.append(self.starts[-1] + len(line) + 1)

    def of_tree(self, row, byte_col):
        return self.starts[row - 1] + len(self.lines[row - 1].encode("utf-8")[:byte_col].decode("utf-8"))

    def of_token(self, row, char_col):
        return self.starts[row - 1] + char_col


def is_division(n):
    if isinstance(n, ast.BinOp):
        return isinstance(n.op, ast.Div) and not no_float_gate.is_path_join(n)
    return isinstance(n, ast.AugAssign) and isinstance(n.op, ast.Div) and not no_float_gate.is_path_join(n.value)


def fractions_imports(tree):
    found = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import) and any(a.name.split(".")[0] == "fractions" for a in n.names):
            raise SystemExit("import fractions at line %d: only 'from fractions import Fraction as X' is handled" % n.lineno)
        if isinstance(n, ast.ImportFrom) and n.module == "fractions":
            if len(n.names) != 1 or n.names[0].name != "Fraction" or n.names[0].asname is None:
                raise SystemExit("from fractions at line %d: only 'from fractions import Fraction as X' is handled" % n.lineno)
            found.append(n)
    return found


def rewrite(text, dest):
    """Returns the rewritten text and the number of divisions moved to qdiv."""
    if "\r" in text:
        raise SystemExit("%s: carriage return in the source" % dest)
    tree = ast.parse(text)
    where = Positions(text)
    slashes = []
    for t in tokenize.generate_tokens(io.StringIO(text).readline):
        if t.type == tokenize.OP and t.string in ("/", "/="):
            slashes.append(where.of_token(*t.start))
    edits = []  # (position, characters removed, text put there)
    divisions = 0
    for n in ast.walk(tree):
        if not is_division(n):
            continue
        divisions += 1
        if isinstance(n, ast.BinOp):
            low, high = where.of_tree(n.left.end_lineno, n.left.end_col_offset), where.of_tree(n.right.lineno, n.right.col_offset)
            token = [s for s in slashes if low <= s < high]
            if len(token) != 1:
                raise SystemExit("%s: line %d: %d division tokens between the operands" % (dest, n.lineno, len(token)))
            edits.append((where.of_tree(n.lineno, n.col_offset), 0, "qdiv("))
            edits.append((token[0], 1, ","))
            edits.append((where.of_tree(n.end_lineno, n.end_col_offset), 0, ")"))
        else:
            low, high = where.of_tree(n.target.end_lineno, n.target.end_col_offset), where.of_tree(n.value.lineno, n.value.col_offset)
            token = [s for s in slashes if low <= s < high]
            if len(token) != 1:
                raise SystemExit("%s: line %d: %d /= tokens after the target" % (dest, n.lineno, len(token)))
            target = text[where.of_tree(n.target.lineno, n.target.col_offset):low]
            edits.append((token[0], 2, "= qdiv(%s," % target))
            edits.append((where.of_tree(n.end_lineno, n.end_col_offset), 0, ")"))
    imports = fractions_imports(tree)
    if divisions and not imports:
        raise SystemExit("%s: %d divisions and no fractions import: add it to the text pairs by hand" % (dest, divisions))
    for n in imports:
        start, end = where.of_tree(n.lineno, n.col_offset), where.of_tree(n.end_lineno, n.end_col_offset)
        indent = text[where.starts[n.lineno - 1]:start]
        if indent.strip():
            raise SystemExit("%s: line %d: the fractions import shares its line" % (dest, n.lineno))
        names = "IntPair as %s, qdiv" % n.names[0].asname if divisions else "IntPair as %s" % n.names[0].asname
        edits.append((start, end - start, path_line(dest, indent).lstrip(" ") + indent + "from intpair import " + names))
    out = text
    for position, removed, put in sorted(edits, key=lambda e: e[0], reverse=True):
        out = out[:position] + put + out[position + removed:]
    second_path(text, out, dest, divisions)
    return out, divisions


class Structural(ast.NodeTransformer):
    """The same edits made on the syntax tree."""

    def __init__(self, dest, divisions):
        self.dest = dest
        self.divisions = divisions

    def visit_BinOp(self, node):
        self.generic_visit(node)
        if is_division(node):
            return ast.Call(ast.Name("qdiv", ast.Load()), [node.left, node.right], [])
        return node

    def visit_AugAssign(self, node):
        self.generic_visit(node)
        if is_division(node):
            read = ast.parse(ast.unparse(node.target), mode="eval").body
            return ast.Assign([node.target], ast.Call(ast.Name("qdiv", ast.Load()), [read, node.value], []), None)
        return node

    def visit_ImportFrom(self, node):
        if node.module != "fractions":
            return node
        names = "IntPair as %s, qdiv" % node.names[0].asname if self.divisions else "IntPair as %s" % node.names[0].asname
        return ast.parse(path_line(self.dest, "") + "from intpair import " + names + "\n").body


def second_path(text, out, dest, divisions):
    expected = Structural(dest, divisions).visit(ast.parse(text))
    if ast.dump(expected) != ast.dump(ast.parse(out)):
        raise SystemExit("%s: the text rewrite and the syntax-tree rewrite differ" % dest)


def build(source_text, source_name, dest, pairs):
    t = source_text
    for old, new, count in pairs:
        have = t.count(old)
        if have != count:
            raise SystemExit("%s: %r appears %d times, not %d" % (dest, old, have, count))
        t = t.replace(old, new)
    out, divisions = rewrite(t, dest)
    if out != source_text:
        made = "# Integer copy of %s, written by native/scripts/make_integer_pairs.py: %d divisions moved to qdiv and %d text pairs. The original stays as evidence.\n" % (source_name, divisions, len(pairs))
        out = made + out
    return out, divisions


def regenerate(root):
    """Yields (destination, text, divisions, pairs, source name)."""
    _, listed_files, _ = no_float_gate.listed()
    local = no_float_gate.local_modules({row[3] for row in no_float_gate.ls_files(root)})
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([sys.executable, "-I", "-X", "utf8", os.path.join(root, REDO, "make_integer_redo.py"), os.path.join(root, S), tmp], check=True, capture_output=True)
        for source, dest, pairs in COPIES:
            if source is None:
                name = CHAIN + " for " + dest.split("/")[-1]
                text = open(os.path.join(tmp, dest.split("/")[-1]), encoding="utf-8", newline="").read()
            else:
                name = source
                text = open(os.path.join(root, source), encoding="utf-8", newline="").read()
            out, divisions = build(text, name, dest, pairs)
            found = no_float_gate.python_findings(out, local)
            listed_count = listed_files[dest][0] if dest in listed_files else 0
            if len(found) != listed_count:
                raise SystemExit("%s: the gate reads %d findings, its row states %d, first %s" % (dest, len(found), listed_count, found[0] if found else "none"))
            yield dest, out, divisions, pairs, name


def main_tree(root, write):
    differ = 0
    count = 0
    divisions_total = 0
    for dest, out, divisions, pairs, name in regenerate(root):
        full = os.path.join(root, dest)
        count += 1
        divisions_total += divisions
        if write:
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8", newline="") as f:
                f.write(out)
            same = 1
        else:
            have = open(full, encoding="utf-8", newline="").read() if os.path.exists(full) else None
            same = 1 if have == out else 0
            differ += 1 - same
        hits = integer_only_audit.audit(full) if os.path.exists(full) else [(0, "missing")]
        differ += 1 if hits else 0
        print("INTEGER_COPY|file=%s|divisions_to_qdiv=%d|text_pairs=%d|same=%d|audit_hits=%d|json=0" % (dest, divisions, len(pairs), same, len(hits)), flush=True)
    print("INTEGER_COPIES_DONE|copies=%d|divisions_to_qdiv=%d|differ=%d|json=0" % (count, divisions_total, differ), flush=True)
    return 1 if differ else 0


SNIPPETS = (
    ("x = a / b\n", "x = qdiv(a , b)\n", 1),
    ("x = a/b\n", "x = qdiv(a,b)\n", 1),
    ("x = (a + b) / (c - d)\n", "x = qdiv((a + b) , (c - d))\n", 1),
    ("x = a / b / c\n", "x = qdiv(qdiv(a , b) , c)\n", 2),
    ("x = a / (b / c)\n", "x = qdiv(a , (qdiv(b , c)))\n", 2),
    ("x = -a / b ** 2 + 1\n", "x = qdiv(-a , b ** 2) + 1\n", 1),
    ("x = (\n    a  # 1 / 2\n    / b\n)\n", "x = (\n    qdiv(a  # 1 / 2\n    , b)\n)\n", 1),
    ('x = f"{a / b}|{c}"\n', 'x = f"{qdiv(a , b)}|{c}"\n', 1),
    ("x /= y + 1\n", "x = qdiv(x, y + 1)\n", 1),
    ("m[i][j] /= p / q\n", "m[i][j] = qdiv(m[i][j], qdiv(p , q))\n", 2),
    ('p = root / "a" / b\n', 'p = root / "a" / b\n', 0),
    ('p = "C:/x" + s  # a / b\n', 'p = "C:/x" + s  # a / b\n', 0),
    ("x = a // b\n", "x = a // b\n", 0),
    ("é = 'é' + é2 / b\n", "é = 'é' + qdiv(é2 , b)\n", 1),
    ('x = d["k"] / b\n', 'x = qdiv(d["k"] , b)\n', 1),
)


def selftest():
    fails = 0
    for before, after, divisions in SNIPPETS:
        head = "from fractions import Fraction as F\n" if divisions else ""
        got, n = rewrite(head + before, "a/b/c/x.py")
        want = (path_line("a/b/c/x.py", "") + "from intpair import IntPair as F, qdiv\n" if divisions else "") + after
        if got != want or n != divisions:
            fails += 1
            print("INTEGER_COPY_SELFTEST|bad=%r|got=%r|json=0" % (before, got), flush=True)
    numbers = {"a": 7, "b": 3, "c": 5, "d": 2, "y": 4, "p": 3, "q": 5, "é2": 7}
    sys.path.insert(0, HERE)
    for before, _, divisions in SNIPPETS[:10]:
        if not divisions:
            continue
        text, _ = rewrite("from fractions import Fraction as F\n" + before, "native/scripts/x.py")
        scope = dict(numbers, x=11, m={0: {0: 9}}, i=0, j=0, __file__=os.path.join(HERE, "x.py"))
        exec(compile(text, "snippet", "exec"), scope)
        result = scope["m"][0][0] if "m[i]" in before else scope["x"]
        if not isinstance(result, str) and type(result.numerator) is not int:
            fails += 1
            print("INTEGER_COPY_SELFTEST|not_exact=%r|json=0" % before, flush=True)
    try:
        build("x = 1\n", "x.py", "x.py", [("y", "z", 1)])
    except SystemExit:
        pass
    else:
        fails += 1
        print("INTEGER_COPY_SELFTEST|a_text_pair_with_the_wrong_count_passed|json=0", flush=True)
    print("INTEGER_COPY_SELFTEST_DONE|snippets=%d|failed=%d|json=0" % (len(SNIPPETS), fails), flush=True)
    return 1 if fails else 0


def main(argv):
    if sys.version_info[:2] < (3, 12):
        raise SystemExit("Python 3.12 or later is needed: earlier syntax trees give no positions inside f-strings")
    if argv == ["--selftest"]:
        return selftest()
    if len(argv) == 2 and argv[1] in ("--write", "--check"):
        return main_tree(argv[0], argv[1] == "--write")
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
