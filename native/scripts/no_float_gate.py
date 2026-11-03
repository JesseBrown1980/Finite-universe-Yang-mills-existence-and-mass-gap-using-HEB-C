#!/usr/bin/env python3
"""
The operator's rule, November 3, 2026: "We can't use float."

Scans every tracked code file for binary floating point and fails on what it finds, apart from what FLOAT-EVIDENCE.txt
lists. Each row there names a file, how many findings it holds and why it stays, so one more float in a listed file
fails as well. A row ending in / covers a whole folder.

Python, by syntax tree: float and complex literals; float(), complex(); random floats; imports of numpy, scipy, mpmath,
decimal, fractions, sympy, pandas, torch, statistics and cmath; math.sqrt and its kin; time.time, perf_counter, monotonic and
process_time; true division, unless a string or Path(...) in its operands marks it as a path join; a power with a negative
constant exponent; format specs and %-formats that print as float.
Rust: f32, f64, to_f32 and its kin, 1f64, 0.5, 2. and 1e9. C, C++, Go: float, double, float32, float64 and the same
literals. JavaScript and HTML: Math.*, parseFloat, toFixed and the same literals.
Native comments and strings are removed first, across lines. Exact rationals in Python are the integer pairs of intpair.py,
divided by name with qdiv. A / on any other exact class counts as a finding, and the list says which those are.

usage: no_float_gate.py [ROOT]      Scans ROOT. Exits 1 on a finding that is not listed, or when a listed count has moved.
       no_float_gate.py --selftest  Runs the snippets below. Exits 1 if one is misread. Integer only, json=0.
"""
import ast
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BAD_IMPORT = {"numpy", "scipy", "mpmath", "decimal", "fractions", "sympy", "pandas", "torch", "statistics", "cmath"}
RANDOM_FLOAT = {"random", "uniform", "gauss", "normalvariate", "betavariate", "expovariate", "triangular"}
MATH_FLOAT = {"sqrt", "exp", "expm1", "log", "log1p", "log2", "log10", "sin", "cos", "tan", "asin", "acos", "atan", "atan2", "sinh", "cosh", "tanh",
              "pow", "hypot", "pi", "e", "tau", "inf", "nan", "fsum", "fmod", "erf", "erfc", "gamma", "lgamma", "dist", "degrees", "radians"}
CLOCK_FLOAT = {"time", "perf_counter", "monotonic", "process_time"}
FLOAT_SPEC = re.compile(r"[eEfFgG%]$")
PERCENT_FLOAT = re.compile(r"(?<!%)%[-+ #0]*\d*(?:\.\d+)?[eEfFgG]")
LITERAL = r"(?<![\w.])\d[\d_]*\.\d|(?<![\w.])\d[\d_]*\.(?![\w.])|(?<![\w.])\d[\d_]*[eE][-+]?\d+\b"
NATIVE = (
    ((".rs",), re.compile(r"\b(f32|f64|to_f32|to_f64|from_f32|from_f64)\b|\d_?f(32|64)\b|" + LITERAL)),
    ((".c", ".h", ".cpp", ".go"), re.compile(r"\b(float|double|float32|float64)\b|" + LITERAL)),
    ((".js", ".mjs", ".ts", ".html"), re.compile(r"\bMath\.\w+|\bparseFloat\b|\btoFixed\b|" + LITERAL)),
)
RAW_STRING = re.compile(r'r(#*)"')
CHAR_LITERAL = re.compile(r"'(\\.[^'\n]*|[^'\\\n])'")


def holds_string(node):
    for n in ast.walk(node):
        if isinstance(n, ast.JoinedStr) or (isinstance(n, ast.Constant) and isinstance(n.value, str)):
            return True
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("Path", "PurePath"):
            return True
    return False


def python_findings(text):
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        return ["syntax error at line %s" % e.lineno]
    out = []
    for n in ast.walk(tree):
        line = getattr(n, "lineno", 0)
        if isinstance(n, ast.Constant) and isinstance(n.value, (float, complex)):
            out.append("float literal at line %d" % line)
        elif isinstance(n, ast.Import):
            out += ["import %s at line %d" % (a.name, line) for a in n.names if a.name.split(".")[0] in BAD_IMPORT]
        elif isinstance(n, ast.ImportFrom):
            if n.module and n.module.split(".")[0] in BAD_IMPORT:
                out.append("import %s at line %d" % (n.module, line))
            elif n.module == "time":
                out += ["from time import %s at line %d" % (a.name, line) for a in n.names if a.name in CLOCK_FLOAT]
            elif n.module == "math":
                out += ["from math import %s at line %d" % (a.name, line) for a in n.names if a.name in MATH_FLOAT or a.name == "*"]
        elif isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name) and f.id in ("float", "complex"):
                out.append("%s() at line %d" % (f.id, line))
            elif isinstance(f, ast.Attribute) and f.attr in RANDOM_FLOAT:
                out.append("%s() at line %d" % (f.attr, line))
        elif isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name):
            if n.value.id == "math" and n.attr in MATH_FLOAT:
                out.append("math.%s at line %d" % (n.attr, line))
            elif n.value.id == "time" and n.attr in CLOCK_FLOAT:
                out.append("time.%s at line %d" % (n.attr, line))
        elif isinstance(n, ast.BinOp):
            if isinstance(n.op, ast.Div) and not holds_string(n):
                out.append("true division at line %d" % line)
            elif isinstance(n.op, ast.Pow) and isinstance(n.right, ast.UnaryOp) and isinstance(n.right.op, ast.USub):
                out.append("negative power at line %d" % line)
            elif isinstance(n.op, ast.Mod) and isinstance(n.left, ast.Constant) and isinstance(n.left.value, str) and PERCENT_FLOAT.search(n.left.value):
                out.append("float %%-format at line %d" % line)
        elif isinstance(n, ast.AugAssign) and isinstance(n.op, ast.Div) and not holds_string(n.value):
            out.append("true division at line %d" % line)
        elif isinstance(n, ast.FormattedValue) and n.format_spec is not None:
            spec = "".join(v.value for v in n.format_spec.values if isinstance(v, ast.Constant))
            if FLOAT_SPEC.search(spec):
                out.append("float format at line %d" % line)
    return out


def code_only(text, nested_comments):
    out, i, n = [], 0, len(text)
    while i < n:
        c, two = text[i], text[i:i + 2]
        if two == "//":
            while i < n and text[i] != "\n":
                i += 1
        elif two == "/*":
            depth, i = 1, i + 2
            while i < n and depth:
                if nested_comments and text[i:i + 2] == "/*":
                    depth, i = depth + 1, i + 2
                elif text[i:i + 2] == "*/":
                    depth, i = depth - 1, i + 2
                else:
                    out.append("\n" if text[i] == "\n" else "")
                    i += 1
        elif c == '"':
            i += 1
            while i < n and text[i] != '"':
                i += 2 if text[i] == "\\" else 1
                out.append("\n" if text[i - 1] == "\n" else "")
            i += 1
            out.append('""')
        elif c == "r" and RAW_STRING.match(text, i) and not (i and (text[i - 1].isalnum() or text[i - 1] == "_")):
            m = RAW_STRING.match(text, i)
            end = text.find('"' + m.group(1), m.end())
            end = n if end < 0 else end + 1 + len(m.group(1))
            out.append('""' + "\n" * text.count("\n", i, end))
            i = end
        elif c == "'":
            m = CHAR_LITERAL.match(text, i)
            if m:
                out.append("' '")
                i = m.end()
            else:
                out.append(c)
                i += 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


def native_findings(text, name):
    for exts, pattern in NATIVE:
        if name.endswith(exts):
            code = code_only(text, name.endswith(".rs"))
            return ["line %d" % i for i, line in enumerate(code.split("\n"), 1) if pattern.search(line)]
    return []


def findings(text, name):
    return python_findings(text) if name.endswith(".py") else native_findings(text, name)


def listed():
    folders, files = {}, {}
    for line in open(os.path.join(HERE, "FLOAT-EVIDENCE.txt"), encoding="utf-8"):
        line = line.rstrip("\r\n")
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|", 2)]
        if parts[0].endswith("/"):
            folders[parts[0]] = parts[1]
        else:
            files[parts[0]] = int(parts[1].split("=")[1])
    return folders, files


def scan(root):
    tracked = subprocess.run(["git", "-C", root, "ls-files"], capture_output=True, text=True, check=True).stdout.splitlines()
    folders, files = listed()
    scanned, kept, fails, seen = 0, 0, 0, set()
    extensions = (".py",) + tuple(e for exts, _ in NATIVE for e in exts)
    for path in tracked:
        full = os.path.join(root, path)
        if not path.lower().endswith(extensions) or not os.path.isfile(full):
            continue
        scanned += 1
        found = findings(open(full, encoding="utf-8", errors="replace").read(), path.lower())
        folder = [f for f in folders if path.startswith(f)]
        if folder:
            seen.add(folder[0])
            kept += len(found)
        elif path in files:
            seen.add(path)
            kept += len(found)
            if len(found) != files[path]:
                fails += 1
                print("NO_FLOAT|count_moved=%s|listed=%d|found=%d|first=%s|json=0" % (path, files[path], len(found), found[0] if found else "none"))
        elif found:
            fails += 1
            print("NO_FLOAT|file=%s|first=%s|count=%d|json=0" % (path, found[0], len(found)))
    for gone in sorted((set(folders) | set(files)) - seen):
        fails += 1
        print("NO_FLOAT|listed_and_gone=%s|json=0" % gone)
    print("NO_FLOAT_DONE|code_files=%d|listed_files=%d|listed_folders=%d|listed_findings=%d|failed=%d|json=0" % (scanned, len(files), len(folders), kept, fails))
    return 1 if fails else 0


FLOATS = (
    ("x.py", "x = 0.5"), ("x.py", "x = 1e9"), ("x.py", "x = 2j"), ("x.py", "x = float(3)"), ("x.py", "x = 1 / 2"), ("x.py", "a /= b"),
    ("x.py", "x = 2 ** -3"), ("x.py", "import numpy"), ("x.py", "from decimal import Decimal"), ("x.py", "import math\nx = math.sqrt(2)"),
    ("x.py", "from math import sqrt"), ("x.py", "import time\nx = time.time()"), ("x.py", "from time import monotonic"), ("x.py", "x = rng.random()"),
    ("x.py", 'print(f"{a:.2f}")'), ("x.py", 'print("%.3f" % a)'), ("x.py", 'print(f"{a:.1%}")'),
    ("x.py", "import fractions"), ("x.py", "from fractions import Fraction"), ("x.py", "from fractions import Fraction as F"), ("x.py", "def f():\n    from fractions import Fraction as F\n    return F(1, 2)"),
    ("x.rs", "let a: f64 = 1;"), ("x.rs", "let a = 0.5;"), ("x.rs", "let a = 2.;"), ("x.rs", "let a = 1e9;"), ("x.rs", "let a = 1f64;"), ("x.rs", "let a = x.to_f64();"),
    ("x.rs", "fn f<'a>(x: f64, y: &'a u8) {}"), ("x.rs", 'let s = "a\nb"; let c = 0.5;'), ("x.rs", "/* a /* b */ c */ let d = 0.5;"), ("x.rs", 'let s = r#"a"b"#; let c = 0.5;'),
    ("x.c", "double a;"), ("x.go", "var a float64"), ("x.html", "<script>Math.sqrt(2)</script>"), ("x.js", "let a = 1.5;"),
)
CLEAN = (
    ("x.py", "x = a // b"), ("x.py", 'p = root / "shards" / name'), ("x.py", 'p = root / f"{a}.hbp"'), ("x.py", 'p = base / (name + ".matrix")'), ("x.py", 'p = Path(a) / b'),
    ("x.py", "import math\nx = math.isqrt(9)"), ("x.py", "import time\nx = time.time_ns()"), ("x.py", "import time\ntime.sleep(1)"), ("x.py", 'print(f"{a:08x} {b:>9} {c:d}")'),
    ("x.py", 'print("%%-f %d" % a)'), ("x.py", "x = rng.randrange(2)"), ("x.py", "# 0.5 / float\nx = 1"), ("x.py", 's = "0.5 / float"'), ("x.py", "x = 2 ** 3"),
    ("x.py", "from intpair import IntPair as F, qdiv\nx = qdiv(F(1, 2), 3)"), ("x.py", "import time\nx = time.monotonic_ns()"), ("x.py", "# from fractions import Fraction\nx = 1"), ("x.py", 's = "from fractions import Fraction"'),
    ("x.rs", "let a = x.0.1;"), ("x.rs", "for i in 0..5 {}"), ("x.rs", "for i in 0..=5 {}"), ("x.rs", "let a = 0x1e5;"), ("x.rs", "fn f<'a>(x: &'a u8, y: &'a u8) {}"), ("x.rs", "let c = 'f';"),
    ("x.rs", '// f64 0.5\nlet a = 1;'), ("x.rs", 'let s = "HTTP/1.1\nf64 0.5";'), ("x.rs", '/* f64 */ let a = 1;'), ("x.rs", 'let s = r#"a"f64"#;'), ("x.rs", "let a = 1.max(2);"), ("x.rs", "let a = 12_345;"),
    ("x.c", 'int a = 1; /* double */'), ("x.go", 'var a uint64'), ("x.html", '<small>HTTP/1.1 Rust 1.81</small>'.replace("1.81", '"1.81"').replace("1.1", '"1.1"')),
)


def selftest():
    fails = 0
    for name, text in FLOATS:
        if not findings(text, name):
            fails += 1
            print("NO_FLOAT_SELFTEST|missed=%r|json=0" % text)
    for name, text in CLEAN:
        found = findings(text, name)
        if found:
            fails += 1
            print("NO_FLOAT_SELFTEST|flagged=%r|first=%s|json=0" % (text, found[0]))
    print("NO_FLOAT_SELFTEST_DONE|must_flag=%d|must_pass=%d|failed=%d|json=0" % (len(FLOATS), len(CLEAN), fails))
    return 1 if fails else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    sys.exit(scan(sys.argv[1] if len(sys.argv) > 1 else "."))
